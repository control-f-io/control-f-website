#!/usr/bin/env python3
"""A root leaves from somewhere, and that somewhere is checkable.

The forty-first check, and the last unguarded end of the statement-to-process
illustration on patterns/landing-page.html.

The drawing has exactly two ends that are not junctions with itself. The
fourteen at the foot hand over to the lectern, and check-flow-handover.py holds
that seam on the axis where it is countable. The ONE at the head is the trunk's
departure -- the point the data leaves the void from -- and nothing held it at
all. check-flow-terminals.py permits it by construction:

    # The void: the one point a segment may start from without another segment
    # under it. It is the topmost start, and there must be exactly one.
    tops = sorted({s[0] for s in segs}, key=lambda p: (p[1], p[0]))
    void = tops[0]

That is a definition, not a measurement. Whatever the topmost start happens to
be IS the void as far as that check is concerned, so the trunk could depart from
anywhere on the page -- a hundred units below the ring, in open wash -- and
every existing check would still pass. The relationship to the actual void was
kept the way this seam's other axis was kept for three fixes running: in prose.

AND THE PROSE WAS WRONG. Two places in landing-page.html put the ring at "about
88 flow units" and "a 94 px rim", while the markup that draws it, and the
comment directly above that markup, both say 84:

    the ring at 84 and the nucleus at 11 disassemble under the same rule
    <path ... d="M270.6 150.6A84 84 0 0 1 389.4 150.6"/>

88 x (1280/1200) = 93.87, which is where the 94 came from: one wrong radius,
copied into two conclusions. Measured on the shipped page at device scale 4,
the ring's rim is 89.60 px at 1440 x 900 and at every viewport at the full
measure -- not 94 -- and the conclusions drawn from 94 do not survive the
correction. See the corrected notes in the page.

WHAT IS TRUE, and what this check holds. Both drawings are 1200 units wide over
the same page width wherever the height cap does not bind, so a flow unit and a
statement unit are the same length and the relationship is exact arithmetic:

  1. SHARED BASIS. The statement figure's viewBox and the flow's viewBox are
     the same width. Everything below is arithmetic only because of this.

  2. THE BOX TOP IS THE VOID'S CENTRE. .lp-flow is placed `top: 50%` of the
     figure, so the flow's y 0 sits on the figure's vertical midpoint. That is
     the void's centre only if the ring's cy is exactly half the statement
     viewBox height. 210 of 420. Move the ring off centre and `top: 50%` stops
     meaning what the note says it means, silently.

  3. THE TRUNK IS PLUMB UNDER THE VOID. The departure's x equals the ring's
     centre x, in the shared basis.

  4. THE DEPARTURE IS ON THE RIM. The departure's y -- its drop below the flow
     box top, which is the void's centre -- equals the ring's radius. 84 and 84.
     THIS is why the head of the drawing touches the void at all, and it is a
     coincidence of two numbers in two different SVGs that nothing stated.

Measured on the shipped page, distance from the departure to the rim:

    1024 x  900    -0.00        \
    1280 x  800    -0.00         |
    1280 x  900    -0.00         |  the flow is at the full measure: the two
    1440 x  900    -0.00         |  drawings share a width, and 84 == 84
    1600 x  900    -0.00         |  puts the departure exactly on the rim
    1920 x 1080    -0.00         |
    2560 x 1440    -0.00        /
    1280 x  720    -3.52        \   the stage's height cap binds, the flow
    1366 x  768    -3.80         |  narrows and the figure does not, and the
    1440 x  720    +2.35        /   departure slides 0.225 x (figure - measure)

The three capped rows are NOT what this check holds, and cannot be: the drift is
0.225 x (figure width - measure), the measure is a function of viewport height,
and no file contains it. It is the same over-determination the page's own note
works through -- a box with two degrees of freedom serving three arrivals -- and
moving the departure onto the rim there means changing where the trunk leaves,
which is the drawing's form. That is the craft lane's brief, and the table above
is the measurement it needs. What this check holds is the exact identity the
whole arrangement rests on, so that the day someone edits 84 in either file the
build says so instead of a screenshot saying so eighteen months later.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-void-departure.py
    python3 scripts/check-void-departure.py -v
"""

import argparse
import re
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "design-system" / "patterns" / "landing-page.html"

SVG_RE = re.compile(r'<svg\b[^>]*class="([^"]*)"[^>]*viewBox="([^"]*)"(.*?)</svg>', re.S)
PATH_RE = re.compile(r'<path\b[^>]*class="([^"]*)"[^>]*\bd="([^"]*)"', re.S)
CMD_RE = re.compile(r'([MLVH])\s*(-?[\d.]+)(?:[ ,]+(-?[\d.]+))?')
# M x y A rx ry rot large sweep x2 y2 — the quarter-arcs both rings are cut into.
ARC_RE = re.compile(
    r'M\s*(-?[\d.]+)[ ,]+(-?[\d.]+)\s*A\s*(-?[\d.]+)[ ,]+(-?[\d.]+)'
    r'[ ,]+[-\d.]+[ ,]+[01][ ,]+[01][ ,]+(-?[\d.]+)[ ,]+(-?[\d.]+)'
)

# The ring the trunk leaves from, and the rule that picks it out of the figure:
# the largest arc radius in the statement's drawing. The nucleus is 11, the ring
# is 84; "both rings are drawn as four quarter-arcs split on the diagonals".
STATEMENT = "cf-iso"
FLOW = "lp-flow"
FLOW_SEG = "lp-flow__seg"

# How far an arc endpoint may sit from the radius the arc declares. The split
# points are the diagonals, so they are r/sqrt(2) rounded to one decimal —
# 59.4 for 84 — and land 0.0043 off. This is a rounding gate, not a tolerance
# on the identities below, which are exact.
ROUND_TOL = Fraction(1, 100)


def rational(text):
    return Fraction(text).limit_denominator(10 ** 6)


def parse_path(d):
    segs, cur = [], None
    for cmd, a, b in CMD_RE.findall(d):
        if cmd == "M":
            cur = (rational(a), rational(b))
            continue
        if cmd == "L":
            nxt = (rational(a), rational(b))
        elif cmd == "V":
            nxt = (cur[0], rational(a))
        else:
            nxt = (rational(a), cur[1])
        segs.append((cur, nxt))
        cur = nxt
    return segs


def show(v):
    return str(int(v)) if v.denominator == 1 else f"{float(v):g}"


def find_ring(body):
    """The void: the largest-radius family of quarter-arcs in the statement.

    Centre from the bounding box of the arc endpoints — the four split points
    are on the diagonals, so their box is centred on the ring — and radius from
    the arc's own rx, which is exact where the split points are rounded."""
    arcs = []
    for x1, y1, rx, ry, x2, y2 in ARC_RE.findall(body):
        if rational(rx) != rational(ry):
            continue
        arcs.append((rational(rx), (rational(x1), rational(y1)),
                     (rational(x2), rational(y2))))
    if not arcs:
        return None, []
    radius = max(a[0] for a in arcs)
    family = [a for a in arcs if a[0] == radius]
    pts = [p for a in family for p in a[1:]]
    cx = (min(p[0] for p in pts) + max(p[0] for p in pts)) / 2
    cy = (min(p[1] for p in pts) + max(p[1] for p in pts)) / 2
    return (cx, cy, radius), pts


def main():
    parser = argparse.ArgumentParser(
        description="The trunk departs from the void's rim, and 84 == 84 is why.")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    text = PAGE.read_text(encoding="utf-8")
    statement = flow = None
    for classes, view_box, body in SVG_RE.findall(text):
        names = classes.split()
        if STATEMENT in names and statement is None:
            statement = (view_box, body)
        if FLOW in names and flow is None:
            flow = (view_box, body)

    findings = []
    if statement is None or flow is None:
        missing = ".cf-iso" if statement is None else ".lp-flow"
        print(f"void departure: {missing} is not on the page — the selector went stale")
        return 1

    s_vb, s_body = statement
    f_vb, f_body = flow
    s_w, s_h = rational(s_vb.split()[2]), rational(s_vb.split()[3])
    f_w = rational(f_vb.split()[2])

    ring, pts = find_ring(s_body)
    if ring is None:
        print("void departure: the statement draws no ring — the void is gone")
        return 1
    cx, cy, radius = ring

    segs = []
    for classes, d in PATH_RE.findall(f_body):
        if FLOW_SEG in classes.split():
            segs.extend(parse_path(d))
    if not segs:
        print(f"void departure: .{FLOW} carries no .{FLOW_SEG}")
        return 1
    # The departure, by the same definition check-flow-terminals.py uses.
    dep = sorted({s[0] for s in segs}, key=lambda p: (p[1], p[0]))[0]

    # 0. the split points really are on the ring the arcs declare
    for p in pts:
        off2 = (p[0] - cx) ** 2 + (p[1] - cy) ** 2
        off = abs(Fraction(off2).limit_denominator(10 ** 6) - radius ** 2)
        if off > ROUND_TOL * radius * 2:
            findings.append(
                f"the ring's split point ({show(p[0])}, {show(p[1])}) is not on the "
                f"radius {show(radius)} the arc declares — the void is not a circle")

    # 1. shared basis
    if s_w != f_w:
        findings.append(
            f"the statement's viewBox is {show(s_w)} wide and the flow's is "
            f"{show(f_w)} — a flow unit and a statement unit are no longer the "
            f"same length, and every identity below is arithmetic about nothing")

    # 2. `top: 50%` lands the flow's y 0 on the void's centre
    if cy * 2 != s_h:
        findings.append(
            f"the ring's centre y is {show(cy)} of a {show(s_h)}-unit viewBox, so the "
            f"figure's midpoint is {show(s_h / 2)} — .lp-flow is placed `top: 50%` and "
            f"its y 0 therefore lands {show(abs(cy - s_h / 2))} units off the void's centre")
    if not re.search(r"\.lp-flow,\s*\.lp-flow-data\s*\{[^}]*?\btop:\s*50%", text, re.S):
        findings.append(
            "`top: 50%` is no longer what places .lp-flow on the figure — the flow's "
            "y 0 is not the void's centre any more, and the departure below is "
            "measured from a point the page does not use")

    # 3. plumb under the void
    if dep[0] != cx:
        findings.append(
            f"the trunk departs at x {show(dep[0])} and the void's centre is x "
            f"{show(cx)} — {show(abs(dep[0] - cx))} units off plumb")

    # 4. on the rim
    if dep[1] != radius:
        findings.append(
            f"the trunk departs {show(dep[1])} units below the void's centre and the "
            f"ring's radius is {show(radius)} — the head of the drawing "
            f"{'stops ' + show(radius - dep[1]) + ' units short of' if dep[1] < radius else 'overshoots'}"
            f" the rim it is supposed to leave from. A root leaves from somewhere.")

    if args.verbose:
        print(f"  statement viewBox  {show(s_w)} x {show(s_h)}")
        print(f"  flow viewBox       {show(f_w)} x {show(rational(f_vb.split()[3]))}")
        print(f"  void ring          centre ({show(cx)}, {show(cy)})  radius {show(radius)}")
        print(f"  figure midpoint    {show(s_h / 2)}   (`top: 50%` puts flow y 0 here)")
        print(f"  trunk departure    ({show(dep[0])}, {show(dep[1])})")
        print(f"  drop below centre  {show(dep[1])}  vs rim {show(radius)}")

    if findings:
        print(f"\nvoid departure: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1
    print(f"void departure OK — the trunk leaves x {show(dep[0])} plumb under the void's "
          f"centre and {show(dep[1])} units below it, onto a rim of {show(radius)}, both "
          f"drawings on a {show(s_w)}-unit basis")
    return 0


if __name__ == "__main__":
    sys.exit(main())
