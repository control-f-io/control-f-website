#!/usr/bin/env python3
"""Fail a ruled band that paints one column boundary from both of its sides.

THE SHAPE, and why every other check in this directory walks past it.

A hairline drawn as a border sits INSIDE the box that declares it. So the same
column line in the same grid lands on a different pixel depending on which
neighbour was asked to draw it:

    grid-column: 1; border-right   the LAST pixel of track 1
    grid-column: 2; border-left    the FIRST pixel of track 2

Both are "the rule between the first and second column", both are one stroke
wide, both are the right colour, and they are one pixel apart. On a band whose
picture changes sides row by row — .cf-culture, where a landscape frame takes
the 3fr track and a portrait frame the 2fr one — the figure carries the rule in
both cases, so the rule swaps sides of the line every time the picture does and
the band's one vertical hairline walks down the page in steps.

Nothing already here can see it. check-grid-tracks.py reads track lists and this
is not one. check-figure-letterbox.py and check-figure-fits.py ask whether a
drawing fits its box, and both boxes are exactly right. check-band-inset.py
measures distances from a band's edge to its content, and every distance here is
correct to the tenth of a pixel. The geometry is not wrong; the STROKE is on the
wrong side of a line, which no measurement of a box reports and no screenshot
shows at 1x unless you already know to look.

WHAT IT COST. patterns/ueber-uns.html, the "Wie wir arbeiten" band, at 1440 on a
2x capture: the vertical rule stood at x 847.0 down both wide rows and at x 848.0
down both tall rows — four jogs between the top of the band and the bottom. With
it went a 2 px stagger between the pictures' own facing edges, because in a tall
row the picture began a pixel PAST its border while the wide row's picture ended
a pixel BEFORE the boundary: the wide frame ran to 846.8 and the tall frame
started at 848.8, with the rule somewhere between them depending on the row.

One pixel is not a rounding artefact at this scale. It is the entire stroke, so
the eye does not read a thin line slightly displaced; it reads a broken one. It
is what got reported, in those words: "the pictures are not aligned".

WHAT THIS CHECKS. Every rule in the shipping CSS that does two things at once —
places its box in a NUMBERED grid column and paints a left or right border with
one of the system's stroke tokens — names a boundary and a side:

    column N, border-right  ->  boundary N|N+1, painted from the low side
    column N, border-left   ->  boundary N-1|N, painted from the high side

Grouped by component, a boundary painted from both sides is the finding. The
boundary and the side are both re-derived from the declarations; nothing is
compared against a number typed in here, so a band that changes its track
count, its stroke token or its modifier names cannot drift out of scope.

WHAT PASSES. A boundary painted from one side only, however many rules paint it
that way — which is what .cf-culture does now: the wide row keeps
`border-right` on the figure in track 1, and the tall row's figure reaches back
across the line for the same pixel with a ::before at `right: 100%` instead of
carrying `border-left`. A pseudo-element is invisible to this check by
construction, and that is correct: it paints no border, so it cannot put a
stroke on the wrong side of anything.

Logical sides count as physical ones. Every page in this repo is LTR — the two
editions are German and English — so border-inline-start is border-left here,
and a mixed band that used one of each would otherwise pass by spelling.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-band-rule-continuity.py       # check, exit 1 on a finding
    python3 scripts/check-band-rule-continuity.py -v    # list every painted boundary
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system" / "assets" / "css"

# The three stylesheets that ship to control-f.de — the same boundary
# check-grid-tracks.py and the spacing check draw, and for the same reason.
SHIPPING = ("tokens.css", "base.css", "components.css")

# A numbered placement and nothing else. `grid-column: 1`, `grid-column: 2 /
# span 3` and `grid-column: 1 / -1` all start at a line this check can name;
# `auto`, `span 2` and a bare `-1` do not, and a rule that does not know which
# track it is in cannot be said to paint a particular boundary.
PLACED = re.compile(r"^\s*(\d+)\s*(?:/.*)?$")

# The stroke tokens, so a decorative 4 px band is out of scope and a hairline is
# in it however it is spelled. --stroke-1 and --stroke-2 are the two the system
# has; the pattern takes any of them rather than naming both, so a third does
# not arrive outside this check's reach.
HAIRLINE = re.compile(r"var\(\s*--stroke-\d")

SIDES = {
    "border-left": "left",
    "border-right": "right",
    "border-inline-start": "left",
    "border-inline-end": "right",
}


def blocks(text):
    """Every rule in a stylesheet as (line, selector, body), comments stripped.

    Comments are blanked in place so line numbers survive and so a declaration
    quoted inside a comment — this file's docstring is full of them, and so is
    components.css — is never read as a live one. Nesting is not parsed and does
    not need to be: a rule inside @media, @supports or @container still arrives
    here with its own selector, because the at-rule prelude precedes the OUTER
    brace and carries no declarations of its own.

    Lifted from check-grid-tracks.py rather than shared: these scripts are each
    one file with no imports between them, which is the property that lets any
    of them be read on its own.
    """
    text = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    for m in re.finditer(r"([^{}]*)\{([^{}]*)\}", text):
        raw = m.group(1)
        sel = " ".join(raw.split())
        if not sel or sel.startswith("@"):
            continue
        head = m.start(1) + len(raw) - len(raw.lstrip())
        yield text[:head].count("\n") + 1, sel, m.group(2)


def declarations(body):
    for decl in body.split(";"):
        prop, sep, value = decl.partition(":")
        if sep:
            yield prop.strip(), value.strip()


def component_of(selector):
    """The component a selector belongs to: its first class, less any __element
    or --modifier. `.cf-culture__row--wide > .cf-culture__figure` is
    `.cf-culture`, which is what puts the wide row's rule and the tall row's
    rule in the same group — they are two modifiers of one band, and the band is
    the thing whose hairline has to be continuous."""
    m = re.search(r"\.([A-Za-z][\w-]*)", selector)
    if not m:
        return None
    return "." + re.split(r"__|--", m.group(1))[0]


def painted(sheets):
    """Every (component, boundary) a border paints, and from which side.

    A boundary is named by the grid line between two tracks: column N with a
    right border paints the line N+1 from below it, column N with a left border
    paints the line N from above it. Both are stored against the LINE, so the
    two spellings of one boundary collide the way they do on screen.
    """
    for name, text in sheets:
        for line, sel, body in blocks(text):
            column = None
            strokes = []
            for prop, value in declarations(body):
                if prop == "grid-column":
                    hit = PLACED.match(value)
                    column = int(hit.group(1)) if hit else None
                elif prop in SIDES and HAIRLINE.search(value):
                    strokes.append(SIDES[prop])
            if column is None:
                continue
            for side in strokes:
                gridline = column + 1 if side == "right" else column
                yield {
                    "sheet": name,
                    "line": line,
                    "selector": sel,
                    "component": component_of(sel),
                    "column": column,
                    "side": side,
                    "gridline": gridline,
                }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every painted boundary, not only the failures")
    args = ap.parse_args()

    sheets = [(n, (CSS / n).read_text()) for n in SHIPPING]
    rows = list(painted(sheets))

    boundaries = {}
    for row in rows:
        boundaries.setdefault((row["component"], row["gridline"]), []).append(row)

    failures = []
    for (component, gridline), group in sorted(boundaries.items(), key=lambda kv: str(kv[0])):
        sides = {row["side"] for row in group}
        if len(sides) < 2:
            continue
        where = "\n".join(
            "        %s:%d  %s\n"
            "              grid-column: %d; border-%s  ->  the %s pixel of track %d"
            % (row["sheet"], row["line"], row["selector"], row["column"], row["side"],
               "last" if row["side"] == "right" else "first", row["column"])
            for row in sorted(group, key=lambda r: r["line"])
        )
        failures.append(
            "%s paints the line before column %d from both sides:\n%s\n"
            "      A border sits inside the box that declares it, so these two land one\n"
            "      stroke apart and the band's hairline steps sideways between the rows\n"
            "      that use them. Paint the boundary from ONE side in every row: keep the\n"
            "      border on whichever cell is in track %d, and let the cell on the other\n"
            "      side reach back across the line for it —\n"
            "        position: relative on the cell, then ::before with\n"
            "        position: absolute; inset-block: 0; right: 100%%; width: var(--stroke-1);\n"
            "        background-color: var(--border-strong);\n"
            "      which is what .cf-culture__row--tall > .cf-culture__figure does."
            % (component, gridline, where, gridline - 1)
        )

    if args.verbose:
        print("hairline borders on numbered grid columns, as read out of the shipping CSS:\n")
        if not rows:
            print("  (none)")
        for row in sorted(rows, key=lambda r: (r["sheet"], r["line"])):
            print("  %-16s %-5d %-46s column %d, border-%-5s -> line %d"
                  % (row["sheet"], row["line"], row["selector"][:46],
                     row["column"], row["side"], row["gridline"]))
        print()

    if failures:
        print("band rule continuity: %d finding(s)\n" % len(failures))
        for f in failures:
            print("  - %s\n" % f)
        return 1

    print("band rule continuity: %d hairline border(s) on numbered columns, "
          "%d boundary/boundaries, each painted from one side."
          % (len(rows), len(boundaries)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
