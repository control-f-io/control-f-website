#!/usr/bin/env python3
"""Hold the demo-fold band's table to the fold each demo actually answers to.

foundations/layout.html documents a real anomaly in the documentation chrome.
docs.css collapses the sidebar at 900 px, so below 900 a demo gets the whole
viewport and at 901 the 272 px sidebar returns: the docs column goes 852 -> 533
in one pixel of viewport. A container-queried demo can therefore FOLD on the
wide side of that edge and un-fold again further out, which is the one place in
this system where making the window wider makes a component narrower.

The note that describes it was wrong for as long as it existed, and wrong in
the way this directory exists to catch. It demonstrated the band on
components/blog-grid.html, "against its own 44rem (704 px) fold", and reported
five columns at 900, stacked from 901, five again at 1074. That element is
.subdivide--even.subdivide--late, and the whole point of --late is that the
five-column form folds at 56rem instead of 44 — the modifier and the note
landed in the same commit. 896 px is more than the plain demo frame reaches
below a viewport of 1265, so the demo is stacked at 900, stacked at 901 and
stacked at 1074 alike. Three of the table's four state cells named something
the page has never done, and the 1073/1074 edges were derived from a threshold
that does not govern the element.

Nothing rendered wrong. The table simply described a different component from
the one it named, in a chapter whose whole subject is that a threshold has to
be derived from the thing it governs. That is the shape check-spacing-scale.py
was written for one register over, and this is the same move for this one.

WHAT IT CHECKS

  resolved       every .subdivide call site's governing fold is resolved the
                 way the cascade resolves it: the fold rules are parsed out of
                 base.css — the bare one and every modifier-keyed one — and a
                 call site takes the modifier's threshold if it wears the
                 modifier and the bare one otherwise. Nothing here repeats a
                 number the stylesheet declares.
  rows           every row of the band table in foundations/layout.html names
                 a file that exists and carries exactly one .subdivide, and
                 states the fold that call site actually resolves to.
  coverage       the table's set of demos is exactly the set of .subdivide
                 call sites in the documentation tree (foundations/ and
                 components/). A demo added without a row, or a row left
                 behind by a demo that moved, is a finding — the band applies
                 to every framed demo, so the table cannot be a selection.

WHAT IT DOES NOT CHECK

  The pixel columns. Frame widths and band edges are measurements and need a
  browser; they are stated as measurements, with the method, and re-measuring
  them is a browser check's job. What is checkable without one is the part
  that was actually wrong: which fold governs which demo.

  Whether 44 and 56rem are the right numbers — base.css carries that
  measurement. Whether the fold and the blog axis agree on it —
  check-subdivide-fold.py. Whether a five-column call site wears --late —
  check-subdivide-late.py. Whether the thresholds are registered —
  check-breakpoints.py.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-demo-fold-band.py       # check, exit 1 on a finding
    python3 scripts/check-demo-fold-band.py -v    # list every call site
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
BASE = DS / "assets" / "css" / "base.css"
LAYOUT_DOC = DS / "foundations" / "layout.html"

# The directories whose pages are framed demos. patterns/ is the shipping page
# itself — it has no sidebar and no frame, so the band does not reach it.
DOC_DIRS = ("foundations", "components")

# A fold rule: a container query whose body collapses .subdivide__col across
# the whole grid. The selector may carry a modifier prefix.
FOLD = re.compile(
    r"@container\s*\(\s*max-width:\s*([\d.]+)rem\s*\)\s*\{\s*"
    r"(?:\.(subdivide--[a-z0-9-]+)\s+)?\.subdivide__col\s*\{[^}]*grid-column:\s*1\s*/\s*-1",
    re.S,
)

# A real opening tag with a class attribute. Documentation code samples write
# class=&quot;…&quot;, so escaped markup never matches this.
TAG = re.compile(r"<[a-zA-Z][^>]*\bclass=\"([^\"]*)\"[^>]*>")

TABLE = re.compile(r"<table[^>]*\bid=\"fold-band-table\"[^>]*>(.*?)</table>", re.S)
ROW = re.compile(r"<tr>(.*?)</tr>", re.S)
CELL = re.compile(r"<td[^>]*>(.*?)</td>", re.S)
CODE = re.compile(r"<code>(.*?)</code>", re.S)


def comment_stripped(text):
    """CSS with /* … */ blanked in place, so line numbers survive."""
    return re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)), text, flags=re.S)


def folds():
    """{modifier or None: threshold in rem} for every fold rule in base.css."""
    css = comment_stripped(BASE.read_text(encoding="utf-8"))
    out = {}
    for m in FOLD.finditer(css):
        out[m.group(2)] = float(m.group(1))
    return out


def call_sites(rules):
    """(path, line, classes, governing threshold) for every .subdivide."""
    sites = []
    for path in sorted(DS.rglob("*.html")):
        text = path.read_text(encoding="utf-8")
        for m in TAG.finditer(text):
            classes = m.group(1).split()
            if "subdivide" not in classes:
                continue
            line = text.count("\n", 0, m.start()) + 1
            # The cascade's own order: a modifier-keyed fold is written after
            # the bare one and is more specific, so any modifier the element
            # wears wins. Two would resolve by stylesheet order; there is one.
            keyed = [rules[c] for c in classes if c in rules]
            fold = max(keyed) if keyed else rules.get(None)
            sites.append((path, line, classes, fold))
    return sites


def rows():
    """(page text, fold text) for every row of the documented band table."""
    m = TABLE.search(LAYOUT_DOC.read_text(encoding="utf-8"))
    if not m:
        return None
    out = []
    for r in ROW.finditer(m.group(1)):
        cells = CELL.findall(r.group(1))
        if len(cells) < 2:
            continue
        page = CODE.search(cells[0])
        fold = CODE.search(cells[1])
        out.append((page.group(1).strip() if page else None,
                    fold.group(1).strip() if fold else None))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    rules = folds()
    failures = []

    if None not in rules:
        failures.append(
            "base.css no longer carries a bare fold rule for .subdivide__col.\n"
            "    This check resolves every call site's fold from the rules in that\n"
            "    file rather than repeating a number; if the primitive's own fold\n"
            "    moved or was renamed, move the pattern in this file with it."
        )
        return report(failures, [], rules, args)

    sites = call_sites(rules)
    documented = rows()

    if documented is None:
        failures.append(
            "foundations/layout.html no longer carries #fold-band-table.\n"
            "    That table is the band's worked example and the thing this check\n"
            "    holds to the stylesheet. If the chapter moved, move the id with it."
        )
        return report(failures, sites, rules, args)

    # The demos the band can reach: one row each, no more and no fewer.
    demos = {}
    for path, line, classes, fold in sites:
        if path.parent.name not in DOC_DIRS:
            continue
        demos.setdefault(str(path.relative_to(DS)), []).append((line, classes, fold))

    named = [p for p, _ in documented if p]
    for page in sorted(set(named)):
        if page not in demos:
            failures.append(
                "#fold-band-table names %s, which carries no .subdivide.\n"
                "    A row for a demo that is not there is the same fault the table\n"
                "    was written with — a measurement attached to the wrong element."
                % page
            )
    for page in sorted(demos):
        if page not in named:
            failures.append(
                "%s carries a .subdivide and has no row in #fold-band-table.\n"
                "    The band reaches every framed demo, so the table is the set of\n"
                "    them and not a selection: a demo added without a row is a demo\n"
                "    whose fold nobody has resolved."
                % page
            )

    for page, fold_text in documented:
        if page is None or page not in demos:
            continue
        instances = demos[page]
        if len(instances) != 1:
            failures.append(
                "%s carries %d .subdivide call sites and #fold-band-table states one\n"
                "    fold for the page. Name the element, or split the row: the whole\n"
                "    point of this table is that the fold belongs to the element."
                % (page, len(instances))
            )
            continue
        line, classes, fold = instances[0]
        if fold is None:
            continue
        want = "%grem" % fold
        if fold_text != want:
            mods = [c for c in classes if c in rules] or ["none"]
            failures.append(
                "#fold-band-table gives %s a fold of %s; it resolves to %s.\n"
                "    The element at %s:%d wears %s, and base.css folds that at %s.\n"
                "    This is exactly the error the table was written with: the fold is\n"
                "    a property of the element's modifiers, not of the primitive."
                % (page, fold_text or "nothing", want, page, line,
                   ", ".join(mods), want)
            )

    return report(failures, sites, rules, args)


def report(failures, sites, rules, args):
    if args.verbose:
        print("fold rules in base.css")
        for mod, rem in sorted(rules.items(), key=lambda kv: kv[1]):
            print("  %-20s %grem" % (mod or "(bare)", rem))
        print("\nsubdivision call sites")
        for path, line, classes, fold in sites:
            print("  %s:%d   %s   %s"
                  % (path.relative_to(ROOT), line,
                     ("%grem" % fold) if fold else "?",
                     " ".join(c for c in classes if c.startswith("subdivide")) or "-"))
        print()

    if failures:
        print("demo fold band: %d finding(s)\n" % len(failures))
        for f in failures:
            print("  - %s\n" % f)
        return 1

    docs = [s for s in sites if s[0].parent.name in DOC_DIRS]
    print(
        "demo fold band: %d fold rule(s), %d call site(s), %d framed demo(s) "
        "each stated at the fold it resolves to."
        % (len(rules), len(sites), len(docs))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
