#!/usr/bin/env python3
"""
inject_snippets.py -- make cookbook code fences come FROM the engine's tested snippets.

The engine repo executes every file in tests/snippets/ (make check-snippets). A python
fence typed into a page is executed by nothing, and rots. This tool removes the second
copy: a fence marked like

    <!-- snippet: 076_effect_screen_shake -->
    ```python
    ...whatever is here is overwritten...
    ```
    <!-- /snippet -->

is rewritten from tests/snippets/076_effect_screen_shake.py. To show only a fragment, the
snippet marks it (`# region: shake` ... `# endregion`, tools/snippet_regions.py in the
engine) and the page asks for it:

    <!-- snippet: 076_effect_screen_shake region=shake -->

NAME is the snippet's file stem, or just its number (076). The injected text is the file
minus its `# mcrf:` provenance header and minus region marker comments; a region is
dedented. Text outside marked fences is never touched, byte for byte.

USAGE
    python3 tools/inject_snippets.py [--engine DIR] [PAGE ...]            # rewrite fences
    python3 tools/inject_snippets.py --check [--engine DIR] [PAGE ...]    # verify, write nothing

PAGE defaults to cookbook/*.md (paths relative to this repo). The engine checkout is
--engine, else $MCRF_ENGINE, else the sibling ../McRogueFace that build_library.py also
assumes; it must contain tests/snippets/ and tools/snippet_regions.py.

--check exits non-zero when
  * a marked fence's text differs from what injection would write (drift)
  * a marker is malformed (not followed by a python fence, no closing marker, nested,
    unknown attribute, ...) or names a snippet or region that does not exist
  * a page has MORE unmarked python fences than tools/ungated_fences.json allows, has no
    entry there, or has FEWER (the entry is stale: run the default mode, which lowers it)

--base REV (with --check): relative to REV, a page may only gain markers and have its marked
fences' bodies replaced. A lost or added fence, a changed info string (```python -> ```),
a missing or new page, or any other changed byte is an error. Without it, converting a
fence by turning it into a bare ``` fence, or deleting it, would lower the ratchet for free.

A snippet line that would close the page's fence (``` at the fence's length) is refused
before anything is written; use a longer fence on the page.

THE RATCHET. tools/ungated_fences.json maps each page to the number of python fences that
are not yet backed by an engine snippet. It can only go down: the default mode lowers an
entry to the page's actual count and refuses (writing nothing) if a page has more than its
entry. Convert a fence, run the tool, commit the lower number.

Plain python3, standard library only.
"""

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parent.parent
RATCHET_PATH = SITE_ROOT / "tools" / "ungated_fences.json"
DEFAULT_PAGES = "cookbook/*.md"

MARKER_OPEN_RE = re.compile(r"^\s*<!--\s*snippet:(.*?)-->\s*$")
MARKER_CLOSE_RE = re.compile(r"^\s*<!--\s*/snippet\s*-->\s*$")
MARKER_LIKE_RE = re.compile(r"<!--\s*/?\s*snippet\b", re.IGNORECASE)
FENCE_OPEN_RE = re.compile(r"^(\s*)(`{3,}|~{3,})\s*([^\s`]*)[^`]*$")
FENCE_CLOSE_RE = re.compile(r"^\s*(`{3,}|~{3,})\s*$")
PYTHON_LANGS = {"python", "py", "python3"}
HEADER_RE = re.compile(r"^#\s*mcrf:")
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")


class PageError(Exception):
    """A problem in one page; .problems is a list of (line, message)."""

    def __init__(self, problems):
        self.problems = problems
        super().__init__("; ".join(f"line {n}: {m}" for n, m in problems))


class Marked:
    fence_char = "`"
    fence_len = 3

    def __init__(self, marker_line, open_line, close_line, indent, name, region):
        self.marker_line = marker_line      # 1-based line of <!-- snippet: ... -->
        self.open_line = open_line          # 1-based line of the opening fence
        self.close_line = close_line        # 1-based line of the closing fence
        self.indent = indent
        self.name = name
        self.region = region


def load_regions_module(engine):
    path = engine / "tools" / "snippet_regions.py"
    if not path.is_file():
        sys.exit(f"inject_snippets: {path} not found (is --engine an engine checkout "
                 f"on a branch with region support?)")
    spec = importlib.util.spec_from_file_location("snippet_regions", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def parse_marker(body):
    """`NAME [region=R]` -> (name, region). ValueError on anything else."""
    toks = body.split()
    if not toks:
        raise ValueError("snippet marker names no snippet")
    name = toks[0]
    if not NAME_RE.match(name):
        raise ValueError(f"bad snippet name {name!r}")
    region = None
    for t in toks[1:]:
        if t.startswith("region=") and len(t) > len("region="):
            if region is not None:
                raise ValueError("region given twice")
            region = t[len("region="):]
        else:
            raise ValueError(f"unknown marker attribute {t!r} (only region=NAME)")
    return name, region


def scan(text):
    """Return (marked, unmarked_lines) for a page; raises PageError on malformed markers.

    marked          list of Marked, in page order
    unmarked_lines  1-based opening-fence lines of python fences with no marker
    """
    marked, unmarked, _fences = scan_all(text)
    return marked, unmarked


def scan_all(text):
    """scan() plus every fence of the page, of any language, in order, as dicts:
    open (line), close (line), info (the info string), marked (Marked or None)."""
    if "\r" in text:
        raise PageError([(1, "page has CR characters; inject_snippets supports LF only")])
    lines = text.split("\n")
    problems = []
    marked, unmarked, fences = [], [], []

    pending = None          # (line, name, region) awaiting its fence
    in_fence = None         # (char, length, open_line, indent, lang, marker or None)
    expect_close = None     # Marked awaiting <!-- /snippet -->

    for i, line in enumerate(lines, start=1):
        if in_fence is not None:
            ch, ln, open_line, indent, lang, mk = in_fence
            m = FENCE_CLOSE_RE.match(line)
            if m and m.group(1)[0] == ch and len(m.group(1)) >= ln:
                fences[-1]["close"] = i
                if mk is not None:
                    mk.close_line = i
                    marked.append(mk)
                    expect_close = mk
                in_fence = None
            continue

        if expect_close is not None:
            if MARKER_CLOSE_RE.match(line):
                expect_close = None
                continue
            problems.append((expect_close.marker_line,
                             "marked fence is not followed by '<!-- /snippet -->'"))
            expect_close = None
            # fall through: this line is judged as ordinary text

        if MARKER_CLOSE_RE.match(line):
            problems.append((i, "'<!-- /snippet -->' without a marked fence before it"))
            continue

        mo = MARKER_OPEN_RE.match(line)
        if mo:
            if pending is not None:
                problems.append((pending[0], "marker not followed by a python fence"))
            try:
                name, region = parse_marker(mo.group(1))
            except ValueError as e:
                problems.append((i, str(e)))
                pending = None
                continue
            pending = (i, name, region)
            continue
        if MARKER_LIKE_RE.search(line):
            problems.append((i, "malformed snippet marker (want "
                                "'<!-- snippet: NAME [region=R] -->' on a line of its own)"))
            continue

        fo = FENCE_OPEN_RE.match(line)
        if fo:
            indent, fence, lang = fo.group(1), fo.group(2), fo.group(3).lower()
            is_py = lang in PYTHON_LANGS
            mk = None
            if pending is not None:
                if not is_py:
                    problems.append((pending[0], f"marker is followed by a {lang or 'plain'} "
                                                 f"fence, not python"))
                else:
                    mk = Marked(pending[0], i, None, indent, pending[1], pending[2])
                    mk.fence_char, mk.fence_len = fence[0], len(fence)
                pending = None
            elif is_py:
                unmarked.append(i)
            in_fence = (fence[0], len(fence), i, indent, lang, mk)
            fences.append({"open": i, "close": None, "info": line.strip()[len(fence):].strip(),
                           "marked": mk})
            continue

        if pending is not None:
            # the fence must be on the very next line: no blank line, no prose
            problems.append((pending[0], "marker not followed by a python fence"))
            pending = None

    if in_fence is not None:
        problems.append((in_fence[2], "code fence is never closed"))
    if pending is not None:
        problems.append((pending[0], "marker not followed by a python fence"))
    if expect_close is not None:
        problems.append((expect_close.marker_line,
                         "marked fence is not followed by '<!-- /snippet -->'"))
    if problems:
        raise PageError(sorted(set(problems)))
    return marked, unmarked, fences


class Engine:
    def __init__(self, engine):
        self.root = engine
        self.dir = engine / "tests" / "snippets"
        if not self.dir.is_dir():
            sys.exit(f"inject_snippets: {self.dir} not found (--engine / $MCRF_ENGINE)")
        self.regions = load_regions_module(engine)
        self.files = sorted(p for p in self.dir.glob("[0-9]*.py"))

    def resolve(self, name):
        exact = [p for p in self.files if p.stem == name]
        if exact:
            return exact[0]
        if name.isdigit():
            hits = [p for p in self.files if p.stem.split("_", 1)[0] == name]
            if len(hits) == 1:
                return hits[0]
            if len(hits) > 1:
                raise KeyError(f"snippet number {name} is ambiguous: "
                               f"{', '.join(h.name for h in hits)}")
        raise KeyError(f"no snippet {name!r} in {self.dir}")

    def text_for(self, name, region):
        """The text injection writes for (name, region): a string ending in one newline."""
        path = self.resolve(name)
        src = path.read_text(encoding="utf-8")
        try:
            self.regions.parse(src)
        except self.regions.RegionError as e:
            raise KeyError(f"{path.name} has malformed regions: {e}")
        if region is not None:
            try:
                body = self.regions.region_text(src, region)
            except KeyError as e:
                raise KeyError(f"{path.name}: {e.args[0]}")
        else:
            lines = src.splitlines(keepends=True)
            for k, l in enumerate(lines[:5]):
                if HEADER_RE.match(l):
                    del lines[k]
                    break
            body = self.regions.strip_markers("".join(lines))
        body = body.strip("\n")
        if not body.strip():
            raise KeyError(f"{path.name}" + (f" region {region!r}" if region else "") +
                           " is empty")
        return body + "\n"


def indent_block(body, indent):
    return [(indent + l) if l else l for l in body.split("\n")[:-1]]


def process_page(text, engine):
    """Return (new_text, drift, n_unmarked, unmarked_lines, problems).

    drift     Marked fences whose current body differs from the snippet
    problems  [(line, msg)] for markers naming a missing snippet/region
    """
    marked, unmarked = scan(text)
    lines = text.split("\n")
    problems, drift = [], []
    out = list(lines)
    # Replace from the bottom up so earlier line numbers stay valid.
    for mk in reversed(marked):
        try:
            body = engine.text_for(mk.name, mk.region)
        except KeyError as e:
            problems.append((mk.marker_line, e.args[0]))
            continue
        closer = [k for k, l in enumerate(body.split("\n")[:-1], start=1)
                  if (FENCE_CLOSE_RE.match(l) and FENCE_CLOSE_RE.match(l).group(1)[0] == mk.fence_char
                      and len(FENCE_CLOSE_RE.match(l).group(1)) >= mk.fence_len)]
        if closer:
            problems.append((mk.marker_line,
                             f"snippet {mk.name}" + (f" region={mk.region}" if mk.region else "") +
                             f": line {closer[0]} of the injected text would close the page's "
                             f"{mk.fence_char * mk.fence_len} fence; nothing was written. Use a longer "
                             f"fence on the page (````python) or change the snippet"))
            continue
        want = indent_block(body, mk.indent)
        if lines[mk.open_line:mk.close_line - 1] != want:
            drift.append(mk)
        out[mk.open_line:mk.close_line - 1] = want
    drift.reverse()
    return "\n".join(out), drift, len(unmarked), unmarked, problems


def read_page(path):
    """Read a page WITHOUT newline translation, so a CR in it is seen (and refused)."""
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def write_page(path, text):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def load_ratchet():
    if not RATCHET_PATH.is_file():
        sys.exit(f"inject_snippets: {RATCHET_PATH} missing")
    data = json.loads(read_page(RATCHET_PATH))
    if not data:
        sys.exit(f"inject_snippets: {RATCHET_PATH} is empty; it must list every page")
    if not isinstance(data, dict) or not all(isinstance(v, int) and v >= 0
                                             for v in data.values()):
        sys.exit(f"inject_snippets: {RATCHET_PATH} must map page -> non-negative int")
    return data


def save_ratchet(data):
    write_page(RATCHET_PATH, json.dumps(dict(sorted(data.items())), indent=2) + "\n")


def page_list(pages):
    if pages:
        out = [Path(p) for p in pages]
    else:
        out = sorted(SITE_ROOT.glob(DEFAULT_PAGES))
    rel = []
    for p in out:
        ap = p if p.is_absolute() else (Path.cwd() / p)
        try:
            rel.append(ap.resolve().relative_to(SITE_ROOT).as_posix())
        except ValueError:
            sys.exit(f"inject_snippets: {p} is not inside {SITE_ROOT}")
    return rel


def find_engine(arg):
    cand = arg or os.environ.get("MCRF_ENGINE") or str(SITE_ROOT.parent / "McRogueFace")
    return Path(cand).expanduser().resolve()


def git_show(rev, rel):
    p = subprocess.run(["git", "-C", str(SITE_ROOT), "show", f"{rev}:{rel}"],
                       capture_output=True)
    return p.stdout.decode("utf-8", "surrogateescape") if p.returncode == 0 else None


def base_pages(rev):
    p = subprocess.run(["git", "-C", str(SITE_ROOT), "ls-tree", "-r", "--name-only", rev, "--",
                        os.path.dirname(DEFAULT_PAGES)], capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit(f"inject_snippets: --base {rev!r}: {p.stderr.strip() or 'not a revision'}")
    import fnmatch
    return sorted(n for n in p.stdout.splitlines() if fnmatch.fnmatch(n, DEFAULT_PAGES))


def check_against_base(base_text, cur_text):
    """Problems [(line, msg)] if `cur_text` differs from `base_text` by anything but marking
    fences: a page may only (a) wrap python fences in markers and (b) have those fences'
    bodies replaced. A lost or added fence, a changed info string, or any other changed byte
    is a problem. Line numbers are lines of `cur_text`."""
    try:
        _m, _u, bf = scan_all(base_text)
    except PageError as e:
        return [(n, f"at --base: {m}") for n, m in e.problems]
    try:
        _m, _u, cf = scan_all(cur_text)
    except PageError as e:
        return list(e.problems)
    if len(bf) != len(cf):
        return [(1, f"the page had {len(bf)} code fence(s) at --base and has {len(cf)}: a "
                    f"fence was {'lost' if len(cf) < len(bf) else 'added'}")]
    problems = []
    for k, (b, c) in enumerate(zip(bf, cf), start=1):
        if b["info"] != c["info"]:
            problems.append((c["open"], f"fence {k}: info string changed from {b['info']!r} to {c['info']!r}"))
    if problems:
        return problems
    blines, clines = base_text.split("\n"), cur_text.split("\n")
    drop_b, drop_c = set(), set()
    for b, c in zip(bf, cf):
        mk = c["marked"]
        if mk is None:
            continue
        drop_b.update(range(b["open"] + 1, b["close"]))            # body lines (1-based)
        drop_c.update(range(c["open"] + 1, c["close"]))
        drop_c.add(mk.marker_line)
        drop_c.add(c["close"] + 1)
    keep_b = [(i, l) for i, l in enumerate(blines, start=1) if i not in drop_b]
    keep_c = [(i, l) for i, l in enumerate(clines, start=1) if i not in drop_c]
    for (bi, bl), (ci, cl) in zip(keep_b, keep_c):
        if bl != cl:
            return [(ci, f"text outside marked fences changed (base line {bi}: {bl[:60]!r} -> {cl[:60]!r})")]
    if len(keep_b) != len(keep_c):
        n = min(len(keep_b), len(keep_c))
        ci = keep_c[n][0] if n < len(keep_c) else len(clines)
        return [(ci, "text outside marked fences was added or removed")]
    return []


def run(pages, engine_dir, check, out=sys.stdout, base=None):
    """Core. Returns exit code. Writes pages (and the ratchet) only in default mode and
    only when nothing at all was wrong."""
    engine = Engine(engine_dir)
    ratchet = load_ratchet()
    whole_set = not pages
    rels = page_list(pages)
    errors = []
    if not rels:
        print(f"inject_snippets: no pages matched ({DEFAULT_PAGES}); refusing to report success "
              f"for an empty set", file=out)
        return 1
    if base is not None:
        if not check:
            sys.exit("inject_snippets: --base is a --check option")
        have = set(base_pages(base))
        if whole_set:
            for rel in sorted(have - set(rels)):
                errors.append(f"{rel}: existed at --base and is gone")
            for rel in sorted(set(rels) - have):
                errors.append(f"{rel}: is new since --base (pages may not be added)")
    new_texts = {}
    new_ratchet = dict(ratchet)

    for rel in rels:
        text = read_page(SITE_ROOT / rel)
        if base is not None:
            bt = git_show(base, rel)
            if bt is None:
                if not whole_set:
                    errors.append(f"{rel}: does not exist at --base")
            else:
                errors.extend(f"{rel}:{n}: {m}" for n, m in check_against_base(bt, text))
        try:
            new_text, drift, n_unmarked, unmarked_lines, problems = process_page(text, engine)
        except PageError as e:
            errors.extend(f"{rel}:{n}: {m}" for n, m in e.problems)
            continue
        errors.extend(f"{rel}:{n}: {m}" for n, m in problems)
        if rel not in ratchet:
            errors.append(f"{rel}: no entry in tools/ungated_fences.json "
                          f"(page has {n_unmarked} unmarked python fence(s)); add one")
            continue
        allowed = ratchet[rel]
        if n_unmarked > allowed:
            where = ", ".join(str(n) for n in unmarked_lines)
            errors.append(f"{rel}: {n_unmarked} unmarked python fences, ratchet allows "
                          f"{allowed} (fences at lines {where}); mark the new ones with a "
                          f"snippet instead of adding ungated code")
        elif n_unmarked < allowed:
            if check:
                errors.append(f"{rel}: ratchet says {allowed} but only {n_unmarked} unmarked "
                              f"fence(s) remain; run tools/inject_snippets.py to lower it")
            else:
                new_ratchet[rel] = n_unmarked
        if check:
            errors.extend(f"{rel}:{mk.marker_line}: fence differs from snippet "
                          f"{mk.name}" + (f" region={mk.region}" if mk.region else "")
                          for mk in drift)
        else:
            new_texts[rel] = new_text

    if whole_set:
        for rel in ratchet:
            if rel not in rels:
                errors.append(f"tools/ungated_fences.json: entry for {rel}, which is not a "
                              f"page matched by {DEFAULT_PAGES}")

    if errors:
        for e in errors:
            print(e, file=out)
        print(f"inject_snippets: {len(errors)} problem(s); nothing written", file=out)
        return 1

    if check:
        print(f"inject_snippets --check: {len(rels)} page(s) ok", file=out)
        return 0

    changed = 0
    for rel, nt in new_texts.items():
        path = SITE_ROOT / rel
        if read_page(path) != nt:
            write_page(path, nt)
            changed += 1
            print(f"rewrote {rel}", file=out)
    if new_ratchet != ratchet:
        save_ratchet(new_ratchet)
        lowered = {k: (ratchet[k], v) for k, v in new_ratchet.items() if ratchet[k] != v}
        print(f"lowered ratchet: {lowered}", file=out)
    print(f"inject_snippets: {len(rels)} page(s), {changed} rewritten", file=out)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Inject engine snippets into cookbook pages.",
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    ap.add_argument("pages", nargs="*", help=f"pages (default {DEFAULT_PAGES})")
    ap.add_argument("--check", action="store_true", help="verify only; write nothing")
    ap.add_argument("--engine", help="engine checkout (default $MCRF_ENGINE, else ../McRogueFace)")
    ap.add_argument("--base", metavar="REV",
                    help="with --check: also fail if, relative to REV, a page lost or gained a "
                         "fence, a fence's info string changed, or any byte outside marked fences "
                         "and marker lines changed (the orchestrator's guard against converting "
                         "a fence by deleting it)")
    args = ap.parse_args(argv)
    return run(args.pages, find_engine(args.engine), args.check, base=args.base)


if __name__ == "__main__":
    sys.exit(main())
