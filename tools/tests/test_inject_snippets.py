"""Tests for tools/inject_snippets.py.

The injector imports tools/snippet_regions.py from an ENGINE checkout, so the tests need
one: set MCRF_ENGINE to a checkout on a branch that has tools/snippet_regions.py. Without
it the suite fails (it does not skip).

    MCRF_ENGINE=/path/to/McRogueFace python3 -m unittest discover -s tools/tests -v
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))
import inject_snippets as I  # noqa: E402

REAL_ENGINE = os.environ.get("MCRF_ENGINE")
if not REAL_ENGINE or not (Path(REAL_ENGINE) / "tools" / "snippet_regions.py").is_file():
    raise SystemExit("set MCRF_ENGINE to an engine checkout that has tools/snippet_regions.py")

SNIP = '''# mcrf: objects=[Frame] verified=0.3.5 status=ok
# Title line
import mcrfpy

# region: helper
def helper():
    return 1
# endregion

scene = mcrfpy.Scene("demo")
'''
PAGE_HEAD = "---\ntitle: t\n---\n\nIntro text.  \n\n"
PAGE_TAIL = "\nOutro with `inline` and trailing spaces   \n"


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.engine = self.tmp / "engine"
        (self.engine / "tests" / "snippets").mkdir(parents=True)
        (self.engine / "tools").mkdir()
        shutil.copy(Path(REAL_ENGINE) / "tools" / "snippet_regions.py", self.engine / "tools")
        (self.engine / "tests" / "snippets" / "007_demo.py").write_text(SNIP)
        self.site = self.tmp / "site"
        (self.site / "cookbook").mkdir(parents=True)
        (self.site / "tools").mkdir()
        self._saved = (I.SITE_ROOT, I.RATCHET_PATH)
        I.SITE_ROOT = self.site
        I.RATCHET_PATH = self.site / "tools" / "ungated_fences.json"
        self.addCleanup(lambda: (setattr(I, "SITE_ROOT", self._saved[0]),
                                 setattr(I, "RATCHET_PATH", self._saved[1])))

    def page(self, name, text, ratchet=None):
        (self.site / "cookbook" / name).write_text(text)
        data = {}
        if I.RATCHET_PATH.exists():
            data = json.loads(I.RATCHET_PATH.read_text())
        data[f"cookbook/{name}"] = 0 if ratchet is None else ratchet
        I.RATCHET_PATH.write_text(json.dumps(data))

    def read(self, name):
        return (self.site / "cookbook" / name).read_text()

    def ratchet(self):
        return json.loads(I.RATCHET_PATH.read_text())

    def run_tool(self, check, pages=(), base=None):
        buf = io.StringIO()
        code = I.run(list(pages), self.engine, check, out=buf, base=base)
        return code, buf.getvalue()

    def git(self, *args):
        p = subprocess.run(["git", "-C", str(self.site), "-c", "user.name=t", "-c", "user.email=t@t.invalid",
                            *args], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        return p.stdout

    def commit_site(self):
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "base")


def fence(body, marker="<!-- snippet: 007_demo -->", indent=""):
    lines = [indent + marker, indent + "```python"] + [(indent + l) if l else l for l in body.split("\n")] \
        + [indent + "```", indent + "<!-- /snippet -->"]
    return "\n".join(lines) + "\n"


class ScanErrors(Base):
    def bad(self, text, needle):
        with self.assertRaises(I.PageError) as cm:
            I.scan(text)
        self.assertTrue(any(needle in m for _, m in cm.exception.problems), cm.exception.problems)

    def test_marker_without_fence(self):
        self.bad("<!-- snippet: 007_demo -->\nprose\n", "not followed by a python fence")

    def test_marker_at_end_of_file(self):
        self.bad("<!-- snippet: 007_demo -->\n", "not followed by a python fence")

    def test_blank_line_between_marker_and_fence(self):
        self.bad("<!-- snippet: 007_demo -->\n\n```python\nx\n```\n<!-- /snippet -->\n",
                 "not followed by a python fence")

    def test_non_python_fence(self):
        self.bad("<!-- snippet: 007_demo -->\n```bash\nx\n```\n<!-- /snippet -->\n", "not python")

    def test_missing_close_marker(self):
        self.bad("<!-- snippet: 007_demo -->\n```python\nx\n```\nprose\n", "/snippet")

    def test_missing_close_marker_at_eof(self):
        self.bad("<!-- snippet: 007_demo -->\n```python\nx\n```\n", "/snippet")

    def test_stray_close_marker(self):
        self.bad("text\n<!-- /snippet -->\n", "without a marked fence")

    def test_nested_markers(self):
        self.bad("<!-- snippet: a -->\n<!-- snippet: b -->\n```python\nx\n```\n<!-- /snippet -->\n",
                 "not followed by a python fence")

    def test_unknown_attribute(self):
        self.bad("<!-- snippet: a lines=3 -->\n```python\nx\n```\n<!-- /snippet -->\n", "unknown marker")

    def test_malformed_marker(self):
        self.bad("<!-- snippet 007_demo -->\n```python\nx\n```\n<!-- /snippet -->\n", "malformed")
        self.bad("<!-- snippet: -->\n```python\nx\n```\n<!-- /snippet -->\n", "names no snippet")

    def test_unclosed_fence(self):
        self.bad("```python\nx = 1\n", "never closed")

    def test_crlf_refused(self):
        self.bad("```python\r\nx\r\n```\r\n", "CR")


class ScanOk(Base):
    def test_markers_inside_other_fence_are_literal(self):
        m, u = I.scan("````markdown\n<!-- snippet: x -->\n```python\ny\n```\n````\n")
        self.assertEqual((m, u), ([], []))

    def test_counts_unmarked_and_indented(self):
        text = "```python\na\n```\n\n- item\n\n  ```python\n  b\n  ```\n\n```bash\nc\n```\n" + fence("z")
        m, u = I.scan(text)
        self.assertEqual(len(m), 1)
        self.assertEqual(u, [1, 7])


class Inject(Base):
    def test_whole_snippet_strips_header_and_region_markers(self):
        self.page("p.md", PAGE_HEAD + fence("old") + PAGE_TAIL)
        code, out = self.run_tool(False)
        self.assertEqual(code, 0, out)
        body = self.read("p.md")
        self.assertIn("# Title line\nimport mcrfpy\n", body)
        self.assertNotIn("mcrf:", body)
        self.assertNotIn("region", body)
        self.assertIn("def helper():\n    return 1\n", body)

    def test_region(self):
        self.page("p.md", fence("old", "<!-- snippet: 007_demo region=helper -->"))
        self.assertEqual(self.run_tool(False)[0], 0)
        self.assertEqual(self.read("p.md"),
                         "<!-- snippet: 007_demo region=helper -->\n```python\n"
                         "def helper():\n    return 1\n```\n<!-- /snippet -->\n")

    def test_number_resolves(self):
        self.page("p.md", fence("old", "<!-- snippet: 007 -->"))
        self.assertEqual(self.run_tool(False)[0], 0)
        self.assertIn("import mcrfpy", self.read("p.md"))

    def test_outside_text_is_byte_identical_and_idempotent(self):
        head = PAGE_HEAD + "```python\nungated = 1\n```\n\n"
        self.page("p.md", head + fence("old") + PAGE_TAIL + "no trailing newline", ratchet=1)
        self.assertEqual(self.run_tool(False)[0], 0)
        got = self.read("p.md")
        self.assertTrue(got.startswith(head + "<!-- snippet: 007_demo -->\n```python\n# Title line"))
        self.assertTrue(got.endswith("```\n<!-- /snippet -->\n" + PAGE_TAIL + "no trailing newline"))
        self.assertEqual(self.run_tool(False)[0], 0)
        self.assertEqual(self.read("p.md"), got)
        self.assertEqual(self.run_tool(True)[0], 0)

    def test_indented_fence_keeps_indent(self):
        self.page("p.md", "- item\n\n" + fence("old", indent="  "))
        self.assertEqual(self.run_tool(False)[0], 0)
        got = self.read("p.md")
        self.assertIn("  ```python\n  # Title line\n  import mcrfpy\n\n  def helper():\n      return 1\n", got)
        self.assertNotIn("\n   \n", got)  # blank lines get no trailing indent
        self.assertEqual(self.run_tool(True)[0], 0)

    def test_malformed_marker_writes_nothing_anywhere(self):
        self.page("a.md", fence("old"))
        self.page("b.md", "<!-- snippet: 007_demo -->\nno fence\n")
        before = self.read("a.md")
        code, out = self.run_tool(False)
        self.assertEqual(code, 1)
        self.assertIn("b.md:1:", out)
        self.assertEqual(self.read("a.md"), before)


class Check(Base):
    def test_clean_page_passes_and_drift_fails(self):
        self.page("p.md", fence("old"))
        self.run_tool(False)
        self.assertEqual(self.run_tool(True)[0], 0)
        (self.engine / "tests" / "snippets" / "007_demo.py").write_text(SNIP + "extra = 1\n")
        code, out = self.run_tool(True)
        self.assertEqual(code, 1)
        self.assertIn("p.md:1: fence differs from snippet 007_demo", out)

    def test_hand_edit_of_fence_fails(self):
        self.page("p.md", fence("old"))
        self.run_tool(False)
        self.page("p.md", self.read("p.md").replace("import mcrfpy", "import mcrfpy  # edited"))
        self.assertEqual(self.run_tool(True)[0], 1)

    def test_missing_snippet_and_region(self):
        self.page("p.md", fence("x", "<!-- snippet: 999_nope -->"))
        code, out = self.run_tool(True)
        self.assertEqual(code, 1)
        self.assertIn("no snippet '999_nope'", out)
        self.page("p.md", fence("x", "<!-- snippet: 007_demo region=missing -->"))
        code, out = self.run_tool(True)
        self.assertEqual(code, 1)
        self.assertIn("no region 'missing'", out)

    def test_malformed_regions_in_engine_snippet(self):
        (self.engine / "tests" / "snippets" / "007_demo.py").write_text("# region: a\nx = 1\n")
        self.page("p.md", fence("x"))
        code, out = self.run_tool(True)
        self.assertEqual(code, 1)
        self.assertIn("malformed regions", out)

    def test_ambiguous_number(self):
        (self.engine / "tests" / "snippets" / "007_other.py").write_text(SNIP)
        self.page("p.md", fence("x", "<!-- snippet: 007 -->"))
        code, out = self.run_tool(True)
        self.assertEqual(code, 1)
        self.assertIn("ambiguous", out)


class Ratchet(Base):
    def test_more_unmarked_than_allowed_fails(self):
        self.page("p.md", "```python\na\n```\n```python\nb\n```\n", ratchet=1)
        code, out = self.run_tool(True)
        self.assertEqual(code, 1)
        self.assertIn("2 unmarked python fences, ratchet allows 1", out)

    def test_missing_page_entry_fails(self):
        self.page("p.md", "text\n")
        self.page("q.md", "text\n")
        data = self.ratchet()
        del data["cookbook/p.md"]
        I.RATCHET_PATH.write_text(json.dumps(data))
        code, out = self.run_tool(True)
        self.assertEqual(code, 1)
        self.assertIn("no entry", out)

    def test_entry_for_vanished_page_fails(self):
        self.page("p.md", "text\n")
        data = self.ratchet()
        data["cookbook/gone.md"] = 3
        I.RATCHET_PATH.write_text(json.dumps(data))
        code, out = self.run_tool(True)
        self.assertEqual(code, 1)
        self.assertIn("gone.md", out)

    def test_stale_high_entry_fails_check_and_is_lowered_by_default_mode(self):
        self.page("p.md", "```python\na\n```\n", ratchet=4)
        code, out = self.run_tool(True)
        self.assertEqual(code, 1)
        self.assertIn("ratchet says 4 but only 1", out)
        self.assertEqual(self.run_tool(False)[0], 0)
        self.assertEqual(self.ratchet()["cookbook/p.md"], 1)
        self.assertEqual(self.run_tool(True)[0], 0)

    def test_default_mode_never_raises_and_writes_nothing(self):
        self.page("p.md", "```python\na\n```\n```python\nb\n```\n", ratchet=1)
        before = I.RATCHET_PATH.read_text()
        code, _ = self.run_tool(False)
        self.assertEqual(code, 1)
        self.assertEqual(I.RATCHET_PATH.read_text(), before)

    def test_marking_a_fence_lowers_the_ratchet(self):
        self.page("p.md", "```python\na\n```\n" + fence("old"), ratchet=2)
        self.assertEqual(self.run_tool(False)[0], 0)
        self.assertEqual(self.ratchet()["cookbook/p.md"], 1)


class FenceClosers(Base):
    def setUp(self):
        super().setUp()
        (self.engine / "tests" / "snippets" / "008_fence.py").write_text(
            "# mcrf: objects=[] verified=1 status=ok\ntext = \"\"\"\nbefore\n```\nafter\n\"\"\"\n"
            "# region: r\nx = 1\n# endregion\n")

    def test_closing_fence_in_snippet_is_refused_and_nothing_is_written(self):
        self.page("p.md", "intro\n" + fence("old", "<!-- snippet: 008_fence -->"), ratchet=0)
        before, rbefore = self.read("p.md"), I.RATCHET_PATH.read_text()
        code, out = self.run_tool(False)
        self.assertEqual(code, 1)
        self.assertIn("008_fence", out)
        self.assertIn("line 3 of the injected text would close", out)
        self.assertEqual(self.read("p.md"), before)
        self.assertEqual(I.RATCHET_PATH.read_text(), rbefore)
        self.assertEqual(self.run_tool(True)[0], 1)

    def test_longer_page_fence_is_accepted(self):
        text = "<!-- snippet: 008_fence -->\n````python\nold\n````\n<!-- /snippet -->\n"
        self.page("p.md", text)
        code, out = self.run_tool(False)
        self.assertEqual(code, 0, out)
        self.assertIn("before\n```\nafter", self.read("p.md"))
        self.assertEqual(self.run_tool(True)[0], 0)

    def test_a_region_without_the_closer_is_fine(self):
        self.page("p.md", fence("old", "<!-- snippet: 008_fence region=r -->"))
        self.assertEqual(self.run_tool(False)[0], 0)

    def test_tilde_fence_is_not_closed_by_backticks(self):
        text = "<!-- snippet: 008_fence -->\n~~~python\nold\n~~~\n<!-- /snippet -->\n"
        self.page("p.md", text)
        self.assertEqual(self.run_tool(False)[0], 0)


class BaseMode(Base):
    PAGE = ("# T\n\nIntro.\n\n```python\nfirst = 1\n```\n\nMiddle.\n\n```bash\nls\n```\n\n"
            "```python\nsecond = 2\n```\n\nEnd.\n")

    def setUp(self):
        super().setUp()
        self.page("p.md", self.PAGE, ratchet=2)
        self.commit_site()

    def write(self, text, ratchet=None):
        (self.site / "cookbook" / "p.md").write_text(text)
        if ratchet is not None:
            I.RATCHET_PATH.write_text(json.dumps({"cookbook/p.md": ratchet}))

    def base(self):
        return self.run_tool(True, base="HEAD")

    def test_unchanged_page_passes(self):
        self.assertEqual(self.base()[0], 0)

    def test_marking_fences_is_the_only_allowed_change(self):
        self.write(self.PAGE.replace("```python\nfirst = 1\n```", fence("x").rstrip("\n")), ratchet=1)
        self.assertEqual(self.run_tool(False)[0], 0)
        code, out = self.base()
        self.assertEqual(code, 0, out)

    def test_python_fence_turned_into_bare_fence_fails(self):
        self.write(self.PAGE.replace("```python\nfirst = 1", "```\nfirst = 1"), ratchet=1)
        self.assertEqual(self.run_tool(True)[0], 0)           # the ratchet alone is fooled...
        code, out = self.base()                               # ...--base is not
        self.assertEqual(code, 1)
        self.assertIn("info string changed", out)

    def test_deleted_fence_fails(self):
        self.write(self.PAGE.replace("```python\nsecond = 2\n```\n", ""), ratchet=1)
        self.assertEqual(self.run_tool(True)[0], 0)
        code, out = self.base()
        self.assertEqual(code, 1)
        self.assertIn("lost", out)

    def test_added_fence_fails(self):
        self.write(self.PAGE + "\n```bash\nx\n```\n")
        code, out = self.base()
        self.assertEqual(code, 1)
        self.assertIn("added", out)

    def test_changed_prose_fails_with_its_line(self):
        self.write(self.PAGE.replace("Middle.", "Middle!"))
        code, out = self.base()
        self.assertEqual(code, 1)
        self.assertIn("p.md:9: text outside marked fences changed", out)

    def test_edited_unmarked_fence_body_fails(self):
        self.write(self.PAGE.replace("first = 1", "first = 100"))
        self.assertEqual(self.base()[0], 1)

    def test_changed_non_python_fence_fails(self):
        self.write(self.PAGE.replace("ls\n", "rm -rf x\n"))
        self.assertEqual(self.base()[0], 1)

    def test_appended_text_fails(self):
        self.write(self.PAGE + "More prose.\n")
        self.assertEqual(self.base()[0], 1)

    def test_page_removed_or_added_fails(self):
        (self.site / "cookbook" / "q.md").write_text("new\n")
        I.RATCHET_PATH.write_text(json.dumps({"cookbook/p.md": 2, "cookbook/q.md": 0}))
        code, out = self.base()
        self.assertEqual(code, 1)
        self.assertIn("q.md: is new since --base", out)
        (self.site / "cookbook" / "q.md").unlink()
        (self.site / "cookbook" / "p.md").unlink()
        (self.site / "cookbook" / "z.md").write_text("z\n")
        I.RATCHET_PATH.write_text(json.dumps({"cookbook/z.md": 0}))
        code, out = self.base()
        self.assertEqual(code, 1)
        self.assertIn("p.md: existed at --base and is gone", out)

    def test_base_requires_check_and_a_real_revision(self):
        with self.assertRaises(SystemExit):
            self.run_tool(False, base="HEAD")
        with self.assertRaises(SystemExit):
            self.run_tool(True, base="no-such-rev")


class BaseModeAlreadyMarked(Base):
    """The base page already carries markers (the situation after the first page batch)."""
    def setUp(self):
        super().setUp()
        self.text = ("# T\n\nIntro.\n\n" + fence("old") + "\nMiddle.\n\n```python\nunconverted = 1\n```\n\nEnd.\n")
        self.page("p.md", self.text, ratchet=1)
        self.assertEqual(self.run_tool(False)[0], 0)
        self.commit_site()

    def base(self):
        return self.run_tool(True, base="HEAD")

    def edit_page(self, fn):
        path = self.site / "cookbook" / "p.md"
        path.write_text(fn(path.read_text()))

    def test_unchanged_marked_page_passes(self):
        code, out = self.base()
        self.assertEqual(code, 0, out)

    def test_engine_snippet_change_alone_passes(self):
        (self.engine / "tests" / "snippets" / "007_demo.py").write_text(SNIP + "extra = 1\n")
        self.assertEqual(self.run_tool(False)[0], 0)           # re-inject
        self.assertIn("extra = 1", self.read("p.md"))
        code, out = self.base()
        self.assertEqual(code, 0, out)

    def test_prose_change_fails(self):
        self.edit_page(lambda t: t.replace("Middle.", "Middle!"))
        code, out = self.base()
        self.assertEqual(code, 1)
        self.assertIn("text outside marked fences changed", out)

    def test_prose_change_fails_even_with_a_legit_reinjection(self):
        (self.engine / "tests" / "snippets" / "007_demo.py").write_text(SNIP + "extra = 1\n")
        self.run_tool(False)
        self.edit_page(lambda t: t.replace("Intro.", "Intro!"))
        self.assertEqual(self.base()[0], 1)

    def test_untagging_a_marked_fence_fails(self):
        self.edit_page(lambda t: t.replace("<!-- snippet: 007_demo -->\n", "").replace("<!-- /snippet -->\n", ""))
        self.assertEqual(self.base()[0], 1)

    def test_turning_a_marked_fence_bare_fails(self):
        self.edit_page(lambda t: t.replace("```python\n# Title", "```\n# Title", 1))
        self.assertEqual(self.base()[0], 1)

    def test_deleting_a_marked_fence_fails(self):
        def drop(t):
            a = t.index("<!-- snippet: 007_demo -->")
            e = "<!-- /snippet -->\n"
            return t[:a] + t[t.index(e) + len(e):]
        self.edit_page(drop)
        self.assertEqual(self.base()[0], 1)

    def test_retargeting_a_marker_fails(self):
        self.edit_page(lambda t: t.replace("snippet: 007_demo -->", "snippet: 007_demo region=helper -->"))
        self.assertEqual(self.base()[0], 1)

    def test_newly_marking_the_other_fence_still_passes(self):
        self.edit_page(lambda t: t.replace("```python\nunconverted = 1\n```\n", fence("x")))
        I.RATCHET_PATH.write_text(json.dumps({"cookbook/p.md": 0}))
        self.assertEqual(self.run_tool(False)[0], 0)
        code, out = self.base()
        self.assertEqual(code, 0, out)


class Guards(Base):
    def test_cr_in_a_page_is_an_error_not_normalised_away(self):
        (self.site / "cookbook").mkdir(exist_ok=True)
        (self.site / "cookbook" / "p.md").write_bytes(b"text\r\n```python\nx\n```\n")
        I.RATCHET_PATH.write_text(json.dumps({"cookbook/p.md": 1}))
        for check in (True, False):
            code, out = self.run_tool(check)
            self.assertEqual(code, 1)
            self.assertIn("CR characters", out)
        self.assertEqual((self.site / "cookbook" / "p.md").read_bytes(), b"text\r\n```python\nx\n```\n")

    def test_empty_page_set_is_an_error(self):
        I.RATCHET_PATH.write_text(json.dumps({"cookbook/gone.md": 0}))
        for check in (True, False):
            code, out = self.run_tool(check)
            self.assertEqual(code, 1)
            self.assertIn("no pages matched", out)

    def test_empty_ratchet_is_an_error(self):
        self.page("p.md", "text\n")
        I.RATCHET_PATH.write_text("{}")
        with self.assertRaises(SystemExit):
            self.run_tool(True)

    def test_missing_ratchet_is_an_error(self):
        self.page("p.md", "text\n")
        I.RATCHET_PATH.unlink()
        with self.assertRaises(SystemExit):
            self.run_tool(True)


if __name__ == "__main__":
    unittest.main()
