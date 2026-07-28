#!/usr/bin/env python3
"""Where one drawing ends, the next one starts — and that is a junction.

check-flow-terminals.py holds the root to "no free ends" INSIDE its own box:
every segment of .lp-flow arrives on the rail, at the void, or on another
segment, in the drawing's own 1200 x 620 units. It cannot see the one join that
is not inside any box — the seam where the flow hands the reader over to the
lectern. The flow's sixteen terminals stop at the bottom of ITS viewBox; the
frame's six hairlines start at the top of THEIRS; the two are separate SVGs, in
separate sections of the page, on separate unit bases, and every previous fix at
this seam has been made by hand against a screenshot.

Three of them, in a row, all in the same place:

    #177  the three taproots landed 129 px past the lectern's corners at
          1440 x 720, because only the card had been told the stage narrows
    #178  the six hairlines stood 1 px inside the border they replaced, so all
          fifteen terminals met their verticals 0.94 px to the side
    #176  the drawing before this one was a bus whose two runs stopped in
          mid-air, 320 px and 32 px above the rail

Each was found by looking, each was fixed correctly, and after each one the
markup went on stating the relationship in prose — "flow x 0, 600 and 1200 are
these x 0, 500 and 1000" — with nothing reading it. Prose is how this seam has
been kept for three fixes, and prose is what was true the last two times it
broke.

WHAT IS CHECKED. Both drawings are the same width by construction: --lp-measure
is declared once on main, .lp-proc-stage passes it to the card as --pin-measure,
and .lp-flow reads it directly. So the two viewBoxes share a width basis, and a
flow x maps to a frame x by 1000/1200 exactly. On that basis:

  1. THE LECTERN IS CLOSED. Every endpoint of every .lp-frame__line lies on
     another .lp-frame__line. Six strokes, twelve endpoints, four corners and
     two T-junctions — a frame with a free corner is the same finding as a root
     with a free end, one element out.

  2. EVERY DROP LANDS ON THE RAIL. Every flow terminal at the foot of the
     drawing (user y = 620) maps into the span of the frame's top rail. A
     terminal that maps outside 0..1000 is a drop falling past the lectern,
     which is exactly what #177 was.

  3. EVERY VERTICAL CONTINUES A DROP. Every frame vertical's top endpoint is a
     point some flow terminal maps onto. This is the claim --a encodes — the
     verticals grow downward "from the points the data reached, in the order it
     reached them" — and it is false the moment a vertical moves or a taproot
     does. Nothing else in the repository asserts it.

WHAT THIS CHECK CANNOT SEE, stated here so it is not mistaken for covered. The
seam has two axes and this check holds one of them. The VERTICAL join — the
flow's box bottom against the frame's top rail — is not countable in any file,
because it is the sum of the statement figure's height, the section rule below
it, the pin section's padding and the stage's own centring, and the last of
those is a function of viewport height by design (see the .lp-proc-stage note:
the trio is centred in the stage, so the card's top slides half a pixel for
every pixel of viewport). Measured at scroll positions before the pin engages,
frame top minus flow bottom:

    1440 x  900     +1.58        the size the drawing was tuned at
    1280 x  768     +6.92
    1280 x  800     +8.17
    1600 x  900    +28.23
    1366 x  768    +34.66
    1280 x  720    +56.52
    1280 x  900    +58.17
    1440 x  720   +107.84
    1024 x  900   +140.14
    1920 x 1080   +171.58        an ordinary desktop

At 1920 x 1080 all sixteen terminals stop in 172 px of empty wash with no rail
under any of them, which is a screenshot of the thing this system says it does
not ship. It is not fixable by moving a box: the flow's height is locked to its
width by aspect-ratio (the ratio is what makes the x arrivals exact — this
parenthesis is the basis of everything above it and was prose in two files
until scripts/check-flow-ratio.py read it against the viewBox), its top is
locked to the void it leaves, and a box with one degree of freedom cannot serve
two arrivals — the same over-determination .lp-flow's own note works through for
the horizontal axis and resolves by keeping the arrival and letting the
departure drift on the void's rim. Bottom-anchoring the box trades the sixteen
free ends at the rail for one free end at the void, 167 px below its rim at
1920 x 1080, which is a different bug and not a fix.

AND EVERY ROW OF THAT TABLE IS A PRE-PIN NUMBER. .lp-frame sits inside
.cf-pin__stage, which is `position: sticky; top: 0`; .lp-flow sits in static
flow one section up. While the stage is still travelling the gap is flat, which
is what the nine rows record. From the scroll position the stage sticks at, the
frame holds against the viewport and the flow does not, so the gap opens at
1.00 px per px of scroll — at 1440 x 900, the one size the table records the
seam as MADE at, 1.58 px becomes 61.70 at 60 px past the pin and 161.70 at
160 px, with the flow's bottom still on screen at viewport y 9.3 throughout.
scripts/check-seam-travel.py holds that second number, derived from the sticky
asymmetry rather than measured, and the .lp-flow note carries both tables.

So the trunk has to absorb it, which is the drawing's FORM: how the route
branches and where it terminates. That belongs to the craft lane, and BOTH
tables are the measurement it needs — the second one constrains the answer,
because a stretch that lands on the rail at one scroll position still comes
apart at 1.00 px per px unless the two sides travel together.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-flow-handover.py
    python3 scripts/check-flow-handover.py -v
"""

import argparse
import re
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = ROOT / "design-system" / "patterns"

SVG_RE = re.compile(r'<svg\b[^>]*class="([^"]*)"[^>]*viewBox="([^"]*)"(.*?)</svg>', re.S)
PATH_RE = re.compile(r'<path\b[^>]*class="([^"]*)"[^>]*\bd="([^"]*)"', re.S)
CMD_RE = re.compile(r"([MLVH])\s*(-?[\d.]+)(?:[ ,]+(-?[\d.]+))?")


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


def on_segment(p, seg):
    """p lies on seg — at either end or partway along it. Exact, no tolerance:
    both drawings are authored in whole units on a shared basis, so a near-miss
    is a hand edit, which is the thing worth catching."""
    (x1, y1), (x2, y2) = seg
    if p == seg[0] or p == seg[1]:
        return True
    if (x2 - x1) * (p[1] - y1) - (y2 - y1) * (p[0] - x1) != 0:
        return False
    return min(x1, x2) <= p[0] <= max(x1, x2) and min(y1, y2) <= p[1] <= max(y1, y2)


def collect(text, svg_class, path_class):
    """Every segment of one drawing, with the width its viewBox is stated on."""
    for classes, view_box, body in SVG_RE.findall(text):
        if svg_class not in classes.split():
            continue
        vb = [rational(v) for v in view_box.split()]
        segs = []
        for path_classes, d in PATH_RE.findall(body):
            if path_class in path_classes.split():
                segs.extend(parse_path(d))
        return segs, vb
    return None, None


def show(v):
    return str(int(v)) if v.denominator == 1 else f"{float(v):g}"


def check_page(page, verbose):
    text = page.read_text(encoding="utf-8")
    flow, flow_vb = collect(text, "lp-flow", "lp-flow__seg")
    frame, frame_vb = collect(text, "lp-frame", "lp-frame__line")
    if flow is None or frame is None:
        return [], False

    findings = []
    # The two boxes are the same width — .lp-flow reads --lp-measure and the
    # card takes it as --pin-measure — so one basis maps the other.
    basis = frame_vb[2] / flow_vb[2]
    rail_y = flow_vb[3]          # the foot of the flow's own box
    frame_top = frame_vb[1]      # the frame's top rail
    frame_left, frame_right = frame_vb[0], frame_vb[0] + frame_vb[2]

    # 1. THE LECTERN IS CLOSED.
    for i, seg in enumerate(frame):
        for end, p in (("start", seg[0]), ("end", seg[1])):
            if any(on_segment(p, o) for j, o in enumerate(frame) if j != i):
                continue
            findings.append(
                f"{page.name}: the lectern's stroke {i} has its {end} at "
                f"({show(p[0])}, {show(p[1])}), which no other hairline passes "
                f"through — a frame with a free corner is a root with a free end."
            )

    # 2. EVERY DROP LANDS ON THE RAIL, mapped onto the frame's basis.
    drops = sorted({s[1][0] for s in flow if s[1][1] == rail_y}
                   | {s[0][0] for s in flow if s[0][1] == rail_y})
    if not drops:
        findings.append(f"{page.name}: no flow terminal reaches y {show(rail_y)} at all")
    landed = []
    for x in drops:
        fx = x * basis
        landed.append(fx)
        if not (frame_left <= fx <= frame_right):
            findings.append(
                f"{page.name}: a drop lands at flow x {show(x)}, which is frame x "
                f"{show(fx)} — outside the top rail's span "
                f"{show(frame_left)}..{show(frame_right)}. It falls past the lectern."
            )

    # 3. EVERY VERTICAL CONTINUES A DROP.
    verticals = sorted({s[0][0] for s in frame
                        if s[0][0] == s[1][0] and min(s[0][1], s[1][1]) == frame_top})
    for vx in verticals:
        if vx not in landed:
            findings.append(
                f"{page.name}: the lectern's vertical at frame x {show(vx)} grows down "
                f"from a point no drop arrives at — the nearest is frame x "
                f"{show(min(landed, key=lambda f: abs(f - vx)))}. "
                f"--a says each vertical continues the drop that lands on it."
            )

    if verbose:
        print(f"  {page.name}: flow {flow_vb[2]} units wide, lectern {frame_vb[2]} — "
              f"basis {show(basis)}")
        print(f"    {len(frame)} hairlines, {len(frame) * 2} endpoints, all on the frame")
        print(f"    {len(drops)} drops at flow y {show(rail_y)}:")
        for x in drops:
            fx = x * basis
            mark = "  <- vertical" if fx in verticals else ""
            print(f"      flow x {show(x):>7}  ->  frame x {show(fx):>7}{mark}")

    return findings, True


def main():
    parser = argparse.ArgumentParser(
        description="Where one drawing ends, the next one starts — and that is a junction.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="print every drop and the frame x it hands over at")
    args = parser.parse_args()

    findings, seams = [], 0
    for page in sorted(PATTERNS.glob("*.html")):
        f, found = check_page(page, args.verbose)
        findings += f
        seams += 1 if found else 0

    if not seams:
        print("flow handover: no drawing hands over to a frame — the selector went stale")
        return 1
    if findings:
        print(f"\nflow handover: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1
    print(f"flow handover OK — {seams} seam(s): every lectern endpoint on the lectern, "
          f"every drop inside the top rail's span, every vertical continuing a drop")
    return 0


if __name__ == "__main__":
    sys.exit(main())
