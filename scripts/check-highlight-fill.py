#!/usr/bin/env python3
"""A highlight that states a colour must state a fill.

`-webkit-text-fill-color` is an INHERITED property, and where it is set it
BEATS the `color` of every descendant. `background-clip: text` is drawn by
setting it to `transparent`, so every character under a clipping ancestor
arrives at a highlight already filled transparent. A highlight rule that sets
only `color` therefore paints its plate and no word:

    ::selection      { background: lime; color: black; }   <- a lime slab
    .text-foil       { -webkit-text-fill-color: transparent; }

The system had already met this and answered it the expensive way. .text-foil
and .cf-btn--solid each carried their own ::selection rule restating the global
one plus the missing property, byte for byte -- two clipping contexts, two
copies, and a third would have wanted a third. The FOUND STATE never got its
copy, and that is the rung this brand is named after: measured before this
script existed, .cf-mark--current inside a foil headline and inside a solid
button rendered as an empty lime block, on both designed pages, at every size.

So the rule is stated once on the highlight rather than once per clip zone, and
this is the thing that keeps it stated. Same shape as the other seven checks and
for the same reason: a rule applied by hand is a rule with a half-life.

WHAT COUNTS AS A HIGHLIGHT is a closed list -- CSS has exactly these
constructs for painting over text somebody else coloured -- plus this system's
own element-level rungs of the same drawing, which are `mark` and `.cf-mark*`.
An element rung is not a pseudo-element, but it has the identical problem for
the identical reason, and foundations/found.html draws them as one thing.

WHAT IS EXEMPT, and both exemptions are the rule rather than holes in it:

  `color: inherit`     is a REFUSAL to supply ink, not a failed attempt at it.
                       :where(mark)/.cf-mark takes it on purpose: a match the
                       reader has not arrived at is the running text with a
                       ground line under it, so inside a foil it should be the
                       foil. Only a rung that supplies its own ink can lose it.

  a rule with no color  has nothing to lose either -- ::highlight(cf-found)
                       sets a ground line and a transparent plate and no ink.

The converse is checked too: a fill declared without a colour beside it would
render correctly today and put the two out of step for whoever moves one next.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-highlight-fill.py       # check, exit 1 on drift
    python3 scripts/check-highlight-fill.py -v    # list every rule considered
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"

# The shipping stylesheets. docs.css is documentation chrome and does not ship,
# which is the boundary check-glass-budget.py and check-gradient-family.py both
# already draw.
CSS = ("tokens.css", "base.css", "components.css")

# The closed list. ::selection, ::target-text, ::highlight(), ::spelling-error
# and ::grammar-error are the CSS highlight pseudo-elements; `mark` and
# .cf-mark* are this system's element-level rungs of the same drawing.
HIGHLIGHT = re.compile(
    r"::(selection|target-text|highlight\(|spelling-error|grammar-error)"
    r"|(?<![\w-])mark(?![\w-])"
    # The modifier is matched, not just the base class, and the difference is
    # the whole finding: .cf-mark--current is the ONLY element rung that
    # supplies its own ink, so a pattern ending at a word boundary would skip
    # the one rule this script exists for and pass.
    r"|\.cf-mark[\w-]*"
)

FILL = "-webkit-text-fill-color"

# A colour that is deliberately not a colour. `currentColor` is the same
# refusal spelled differently, and the CSS-wide keywords all resolve to
# whatever the ancestor said, which under a clip is transparent -- by
# inheritance, which is the behaviour being asked for rather than lost to.
NO_INK = {"inherit", "currentcolor", "unset", "revert", "revert-layer"}

COMMENT = re.compile(r"/\*.*?\*/", re.S)
# Selector { declarations }, non-nested. Every rule in these three files is
# flat inside at most one at-rule block, so a non-greedy body that stops at the
# first brace of either kind is exact here.
RULE = re.compile(r"([^{}]+)\{([^{}]*)\}")


def strip_comments(text):
    """Blank the comments and KEEP THE NEWLINES, so offsets still name lines.

    Every comment in these files is a paragraph. Collapsing one to a single
    space shortens the file by everything above the rule being reported, and
    the line number in the finding then points at unrelated code -- which is
    worse than no line number, because it looks like one."""
    return COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def declarations(body):
    """{property: value} for a declaration block, last wins, as CSS does."""
    out = {}
    for decl in body.split(";"):
        if ":" not in decl:
            continue
        prop, _, value = decl.partition(":")
        out[prop.strip().lower()] = value.strip()
    return out


def line_of(text, index):
    return text.count("\n", 0, index) + 1


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every highlight rule considered, not only the failures")
    args = ap.parse_args()

    failures, seen, clip_zones = [], 0, 0

    for name in CSS:
        path = DS / "assets" / "css" / name
        text = path.read_text(encoding="utf-8")
        src = strip_comments(text)

        for m in RULE.finditer(src):
            selector = " ".join(m.group(1).split())
            decls = declarations(m.group(2))

            # Count the clip zones so the summary line means something: this
            # rule only matters because these exist, and how many there are is
            # how much it is holding up.
            if decls.get(FILL, "").lower() == "transparent":
                clip_zones += 1

            # An at-rule prelude (`@media print`) is swept up as a selector by
            # the flat rule pattern. It has no declarations of its own, so it
            # falls out here rather than needing to be named.
            if selector.startswith("@") or not HIGHLIGHT.search(selector):
                continue

            seen += 1
            colour = decls.get("color")
            fill = decls.get(FILL)
            line = line_of(text, m.start())
            problems = []

            if colour is not None and colour.lower() not in NO_INK and fill is None:
                problems.append(
                    "sets color: %s and no %s. Under a background-clip:text "
                    "ancestor the inherited fill is transparent and beats it, so "
                    "this paints its plate and no word. Restate the ink as a fill."
                    % (colour, FILL))
            if fill is not None and colour is None:
                problems.append(
                    "sets %s and no color. It renders today and the two are now "
                    "out of step for whoever moves one next -- a browser without "
                    "the -webkit- property has nothing to fall back to."
                    % FILL)

            if args.verbose:
                print("%s %s:%d  %s" % ("FAIL" if problems else "ok  ", name, line, selector))
            for p in problems:
                failures.append("%s:%d  %s: %s" % (name, line, selector, p))

    if failures:
        print("\n%d highlight rule%s can be erased by a clip:\n"
              % (len(failures), "" if len(failures) == 1 else "s"), file=sys.stderr)
        for f in failures:
            print("  " + f, file=sys.stderr)
        print("\nSee base.css, ::selection, and foundations/found.html.", file=sys.stderr)
        return 1

    print("highlight fill: %d highlight rules, %d clipping contexts, "
          "every ink stated as a fill." % (seen, clip_zones))
    return 0


if __name__ == "__main__":
    sys.exit(main())
