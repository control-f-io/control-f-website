#!/usr/bin/env python3
"""The caption under a demo tile is one device, and it may not be written twice.

A caption under a sample — mono at --text-xs with the label tracking, one rung
of air off the thing it names, --text-secondary — is the most repeated shape in
the documentation. It was declared TWENTY times: once in docs.css as
`.docs-plate figcaption`, and nineteen more inside the <style> block of the page
that happened to need it, because a container selector in a page's own block is
not a thing another page can name. docs.css said so in a comment and the comment
could not stop the twenty-first.

Twenty copies of one decision drift, and every axis of the drift was invisible
in a screenshot of any single page:

    the rung     the gap between a sample and its caption measured 8, 12, 16,
                 19.14, 26.23 or 37.09 px depending on which page you had open
    the track    three copies had lost --tracking-label, so the same 11 px mono
                 line was set at two different tracks a scroll apart
    the ink      one had drifted to --text-primary; six had drifted to
                 --text-muted once already, which is the one value the device
                 may not take — #919191 at 11 px is 2.97:1 on --grey-050 and
                 3.15:1 on white, against AA's 4.5:1, and 11 px is not large
                 text
    the case     the device uppercases, and uppercase is wrong wherever the
                 caption carries something whose case carries meaning.
                 foundations/field.html captioned its two samples
                 `--FIELD-UNIT: 3REM` and `--FIELD-UNIT: 12REM`, on the page
                 whose entire subject is that token; foundations/geometry.html
                 read `+ SCALEY(.5) = THE TILE`. foundations/motion.html had
                 already found and fixed exactly this on its own copy — "`120
                 ms` rendered `120 MS`, and MS is not a millisecond" — and a
                 fix on one of twenty copies is not a fix.

`.docs-caption` in docs.css is the device now, with `--cased` for the case and
`--flush` for a caption whose container already supplies the gap.

WHAT THIS CHECKS

1.  No documentation page redeclares the device in its own <style> block. The
    test is a SHAPE, not a roster: a rule whose selector names a caption — a
    `figcaption`, or a class reading `-cap` / `__cap` / `caption` — and whose
    body sets both `font-family: var(--font-mono)` and
    `font-size: var(--text-xs)` is the device being written out again, whatever
    it is called. A twenty-first copy under a name nobody has thought of yet
    fails on the day it is written. Local additions are not copies and are
    exactly what a page is still allowed: `text-align`, `max-width`,
    `line-height`, `word-break`, a colour step on a child.

2.  The device's own ink is --text-secondary. It is the one declaration whose
    wrong value is an accessibility failure rather than an inconsistency, and
    it has drifted before.

3.  A modifier never travels without its base. `docs-caption--cased` or
    `docs-caption--flush` on an element carrying no `docs-caption` is a class
    that resolves and does nothing, which is the failure mode a two-part name
    invites and the one check-class-provenance.py cannot see: both halves are
    declared, so both halves resolve.

SCOPE is the documentation surface, which is what the device is: every page
under design-system/foundations/ and design-system/components/, plus
design-system/index.html and design-system/reference.html, plus docs.css.
patterns/ and prototypes/ are deliberately out — a figcaption on a pattern page
is the shipped article caption in components.css, a different component with a
different job, and a check that read it would be claiming otherwise.

stdlib only, no build step, no dependency — the same contract as the checks
beside it.

    python3 scripts/check-docs-caption.py      # check, exit 1 on a finding
    python3 scripts/check-docs-caption.py -v   # print every rule it considered
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
DOCS_CSS = DS / "assets" / "css" / "docs.css"

BASE = "docs-caption"
MODIFIERS = ("docs-caption--cased", "docs-caption--flush")

# The two declarations that together mean "this is the caption device". Either
# one alone is an ordinary mono label — .icon-count, .field-demo p — and is not
# a copy of anything.
MONO = re.compile(r"font-family:\s*var\(\s*--font-mono\s*\)")
XS = re.compile(r"font-size:\s*var\(\s*--text-xs\s*\)")
# A selector that names a caption. `figcaption` as an element, or a class whose
# last segment is a caption: .ill-cap, .wl__cap, .mob-cap, .docs-caption.
CAPTIONISH = re.compile(r"\bfigcaption\b|\.[\w-]*(?:[-_]cap\b|caption)")
STYLE = re.compile(r"<style[^>]*>(.*?)</style>", re.S)
CLASS_ATTR = re.compile(r'class="([^"]*)"')


def pages():
    """The documentation surface, in a stable order."""
    out = []
    for d in ("foundations", "components"):
        out += sorted((DS / d).glob("*.html"))
    out += [DS / "index.html", DS / "reference.html"]
    return [p for p in out if p.exists()]


def rules(css):
    """Every `selector { body }` pair, comments blanked, line numbers kept.

    A brace walker rather than a parser, the shape the checks beside this one
    use: an at-rule's body still holds braces, so it is passed over here and
    the rules inside it are found on their own pass.
    """
    # Blanked to spaces but newline for newline: a comment that spans six lines
    # has to leave six lines behind it or every finding under it names the
    # wrong one.
    css = re.sub(r"/\*.*?\*/",
                 lambda m: re.sub(r"[^\n]", " ", m.group(0)), css, flags=re.S)
    for m in re.finditer(r"\{([^{}]*)\}", css):
        body = m.group(1)
        head = css[: m.start()]
        cut = max(head.rfind("}"), head.rfind("{"), head.rfind(";"))
        selector = head[cut + 1 :].strip()
        if not selector or selector.startswith("@"):
            continue
        yield selector, body, css.count("\n", 0, m.start()) + 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print every caption rule considered, not only findings")
    args = ap.parse_args()

    findings = []
    considered = []

    # 1 — no page redeclares the device.
    for page in pages():
        rel = page.relative_to(ROOT)
        text = page.read_text(encoding="utf-8")
        for block in STYLE.finditer(text):
            # The rule's line inside the block, plus where the block starts, so
            # a finding names a line of the file the reader opens.
            offset = text.count("\n", 0, block.start(1))
            for selector, body, line in rules(block.group(1)):
                if not CAPTIONISH.search(selector):
                    continue
                copied = bool(MONO.search(body)) and bool(XS.search(body))
                considered.append((str(rel), line + offset, selector, copied))
                if copied:
                    findings.append(
                        f"{rel}:{line}  {selector} — writes the caption device out "
                        f"again. Put `{BASE}` on the element and keep only what is "
                        f"local to this page.")

    # 2 — the device's ink.
    css = DOCS_CSS.read_text(encoding="utf-8")
    device = [(s, b, ln) for s, b, ln in rules(css) if s.strip() == f".{BASE}"]
    if not device:
        findings.append(f"{DOCS_CSS.relative_to(ROOT)}  .{BASE} is not declared — "
                        f"the device every documentation page reaches for is gone.")
    else:
        selector, body, line = device[0]
        considered.append((str(DOCS_CSS.relative_to(ROOT)), line, selector, False))
        if "var(--text-secondary)" not in body:
            findings.append(
                f"{DOCS_CSS.relative_to(ROOT)}:{line}  .{BASE} does not take "
                f"--text-secondary. At 11 px --text-muted is 2.97:1 on --grey-050 "
                f"and 11 px is not large text.")

    # 3 — a modifier never travels without its base.
    for page in pages():
        rel = page.relative_to(ROOT)
        text = page.read_text(encoding="utf-8")
        for m in CLASS_ATTR.finditer(text):
            classes = m.group(1).split()
            worn = [c for c in classes if c in MODIFIERS]
            if worn and BASE not in classes:
                line = text.count("\n", 0, m.start()) + 1
                findings.append(
                    f"{rel}:{line}  {' '.join(worn)} without {BASE} — a modifier "
                    f"with no base declares nothing.")

    if args.verbose:
        for path, line, selector, copied in considered:
            mark = "COPY" if copied else "local"
            print(f"  {mark:5}  {path}:{line}  {selector}")
        print()

    if findings:
        print("check-docs-caption: the caption device is written more than once\n")
        for f in findings:
            print(f"  {f}")
        print(f"\n{len(findings)} finding(s).")
        return 1

    print(f"check-docs-caption: one device, {len(considered)} caption rule(s) "
          f"read, none of them a copy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
