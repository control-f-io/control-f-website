#!/usr/bin/env python3
"""A page that ships paints its own icons, before any script runs.

The eighty-fifth check, and one of the few whose subject is what a degraded
tier is left holding rather than what the finished page looks like.

WHAT WENT WRONG. cf-icons.js is the one file that draws the icon set — forty-
five symbols, one place — and every pattern page loads it at the foot of
<body>. It appends the sprite to the document, and until it has, a
<use href="#cf-signal"> whose symbol is not yet there renders NOTHING. Not a
box, not a broken-image mark, not a console line. SVG's own rule: a use
element referencing an id that resolves to nothing has no shadow tree and
paints no pixels. So the failure is silent in every direction a person would
look — the DOM has the element, the layout has its 24 x 24 box, the network
has no 404, and the screenshot has a gap.

Eight of the fourteen pattern pages already inlined the symbols they point at
and were never exposed. Three did not:

    landing-page.html   7 of 8 uses      the act rail's five marks and both jumps
    expertise.html      4 of 5           the Leistungen cards' .cf-icon--xl marks
    news.html           1 of 2           the chevron in the "mehr" link

Measured on the landing page at 1440 x 900 with JavaScript off, the act rail
lifted by :focus-within — which below 96rem is the only way it is ever seen at
all — ink counted inside each control's own box:

                                with JS    without
      .act-rail__jump, top         80          0
      .act-rail__jump, bottom      82          0
      the five act glyphs      79..216         0

The five act rows survive it: they keep a numeral and a title and lose a mark.
The two jumps do not. Their label is a .visually-hidden span, so the glyph is
their whole visible content and each is a 92 x 24 px link that holds a place in
the tab order, takes the focus ring, scrolls the page when activated, and
paints nothing at all.

WHY A SCRIPT AND NOT A REVIEW. The tier this breaks in is the one nobody
reviews in. With the script running — which is every load in a browser anyone
opens the page in to look at it — the sprite is complete before the first
frame a human sees, so the finished page and the holed page are pixel-
identical. The only way to see it is to turn JavaScript off, and the only way
to keep seeing it is to check.

WHAT IS CHECKED, per page under design-system/patterns/:

  every <use> resolves     the fragment each <use href="#id"> names is the id
  in its own document      of a <symbol> in the same file. Not in the icon
                           set, not in a sibling page — in this document,
                           where the browser will look for it.

Scope is patterns/, and deliberately not the whole tree. The pages under
components/ and foundations/ are the documentation, served with docs.css and
preview.css, and foundations/iconography.html BUILDS its <use> elements from
the set at runtime — a page whose subject is the script cannot be asked to
work without it. patterns/ is what ships.

Nothing here is a hand-kept list: the pages are every .html under patterns/,
and the symbols are whatever each one inlines, both found by reading the tree.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = ROOT / "design-system" / "patterns"

HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)

# href or the legacy xlink:href, and only a same-document fragment: a <use>
# pointing at another file is a different construction with a different failure
# mode, and this system has none.
USE = re.compile(r'<use\b[^>]*?\b(?:xlink:)?href="#([^"]+)"', re.I)
SYMBOL = re.compile(r'<symbol\b[^>]*?\bid="([^"]+)"', re.I)


def blank_comments(html: str) -> str:
    """Drop comment CONTENT and keep every newline, so a reported line number is
    the line the reader will find the tag on. Same device as check-a11y.py —
    this tree comments in paragraphs, and the paragraphs quote markup."""
    return HTML_COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), html)


def main():
    if not PATTERNS.is_dir():
        print("check-icon-sprite: design-system/patterns/ is gone. That directory is "
              "what ships; if it has moved, move this check with it.")
        sys.exit(1)

    failures = []
    pages = []

    for path in sorted(PATTERNS.glob("*.html")):
        html = blank_comments(path.read_text(encoding="utf-8", errors="replace"))
        symbols = set(SYMBOL.findall(html))
        rel = path.relative_to(ROOT)

        uses = []
        for m in USE.finditer(html):
            uses.append((m.group(1), html[: m.start()].count("\n") + 1))
        if not uses:
            continue
        pages.append((rel, len(uses), len(symbols)))

        for ident, line in uses:
            if ident in symbols:
                continue
            failures.append(
                f"{rel}:{line}: <use href=\"#{ident}\"> names a symbol this document "
                "does not carry.\n"
                "    cf-icons.js appends the set at the foot of <body>, so this glyph\n"
                "    paints nothing until that script has run — and paints nothing at\n"
                "    all in the tier where it does not. SVG gives a use element with an\n"
                "    unresolvable reference no shadow tree: no box, no fallback, no\n"
                "    console line, and a screenshot that looks like a spacing bug.\n"
                f"    Paste the <symbol id=\"{ident}\"> from cf-icons.js into this page's\n"
                "    <svg class=\"cf-sprite\">, the way #cf-arrow already is.")

    if not pages:
        failures.append(
            "check-icon-sprite: no <use> in any pattern page. Every one of them draws at "
            "least the arrow; if that has changed, rewrite this check with it — do not "
            "delete it.")

    if failures:
        print("check-icon-sprite: an icon that needs a script to exist is an icon the "
              "page cannot promise.\n")
        for f in failures:
            print("  " + f)
        print()
        sys.exit(1)

    total = sum(n for _, n, _ in pages)
    print(f"check-icon-sprite: {total} <use> across {len(pages)} pattern page(s); "
          "every one resolves to a symbol its own document inlines.")
    for rel, n, s in pages:
        print(f"  {rel}  ->  {n} use, {s} symbol inlined")


if __name__ == "__main__":
    main()
