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

    def run_tool(self, check, pages=()):
        buf = io.StringIO()
        code = I.run(list(pages), self.engine, check, out=buf)
        return code, buf.getvalue()


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


if __name__ == "__main__":
    unittest.main()
