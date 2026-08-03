#!/usr/bin/env python3
"""Where one drawing ends, the next one starts — and that is a junction.

check-flow-terminals.py holds the root to "no free ends" INSIDE its own box:
every segment of .lp-flow arrives on the fringe, at the source, or on another
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
flow's box bottom against the frame's top rail — WAS not countable in any file,
because in the fallback tier it is the sum of the statement figure's height, the
section rule below it, the pin section's padding and the stage's own centring,
and the last of those is a function of viewport height by design (see the
.lp-proc-stage note: the trio is centred in the stage, so the card's top slides
half a pixel for every pixel of viewport). Measured in that tier at scroll
positions before the pin engages, frame top minus flow bottom — THESE NINE ARE
HISTORY, kept because the fix was argued from them; the current nine are eight
paragraphs down:

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
departure drift on the void's rim. Bottom-anchoring the box ON ITS OWN trades the
sixteen free ends at the rail for one free end at the void, 167 px below its rim
at 1920 x 1080, which is a different bug and not a fix.

THE PARAGRAPH THAT USED TO STAND HERE SAID THAT WAS FIXED, AND IT WAS NOT. It
read: #207 shipped a bottom anchor with .lp-flow__stem crossing the stretch as
a stroke placed in page pixels, "every row of the table above goes to 0.00",
and two named scripts in scripts/ — a seam-anchor one and a seam-travel one —
held the two axes between them. Three claims, none of them true of anything
that has ever been on main. Neither script exists; `git log -S` finds their
names only in this docstring, in the commit that added this file, and they are
deliberately not written out again here, because a name in this position is
what a reader takes for a gate. .lp-flow__stem exists
nowhere in any page or stylesheet either: the stem tier "was removed with the
chain (2026-07-28)", which scripts/check-flow-chain.py records at its own
section 3a, and this file was never told. The removal left the stem's axis
gradient, #lp-flow-ax-stem, declared on both pages and drawn by nothing, which
is the fingerprint a deleted stroke leaves and the thing that made this
findable at all. Nothing on this page has ever crossed the seam.

SO HERE IS THE SEAM AS IT ACTUALLY MEASURES TODAY, and the numbers are worse
than the ones the fix was written against, because the drawing was inverted
after them: the source is now the drawing's FOOT — one orb at flow x 600 — and
its rim is the last ink .lp-flow puts down. The frame's top rail is the first
ink .lp-frame puts down. Measured on the shipped page, consent dismissed, at
the scroll position where the two come closest, frame top minus flow bottom:

    1280 x  720    218.59
    1366 x  768    218.59
    1280 x  800    229.59
    1440 x  900    244.59
    1600 x  900    244.59
    1024 x  768    258.42
    1280 x  900    279.59
    1920 x 1080    334.59
    2560 x 1440    514.59

Every row a pre-pin number, and the closest either side ever gets. Below 64rem
there is no row because there is no frame: the pin's stacked fallback draws no
lectern, so there is no seam to open.

THE OTHER AXIS IS EXACT, which is what makes the vertical read as a fault
rather than as a composition. The orb's centre and the frame's mid vertical
are the same x to 0.02 px at every one of those nine sizes — 719.98 against
720.00 at 1440, 960.00 against 960.00 at 1920 — so the drawing is aimed
straight down the line it does not reach.

AND THE GAP TRAVELS. .lp-frame sits inside .cf-pin__stage, `position: sticky;
top: 0`; .lp-flow sits one section up. While the stage is still travelling the
gap is flat, which is what the nine rows record. From the scroll position the
stage sticks at, the frame holds against the viewport and the flow does not,
so the gap opens at 1.00 px per px of scroll. Measured at 1440 x 900: 244.59
at the closest approach, 263.66 at 20 px past the pin, 543.66 at 300 px,
1443.66 at 1200 px — exactly +1 px per px, three samples, no rounding.

So the trunk has to absorb it, which is the drawing's FORM: how the route
branches and where it terminates. That belongs to the craft lane, and BOTH
tables are the measurement it needs — the second one constrains the answer,
because a stretch that lands on the rail at one scroll position still comes
apart at 1.00 px per px unless the two sides travel together.

AND THE REASON THIS SURVIVED IS THE CITATION, not the geometry. Two scripts
that were never written were named here as the gates for it, and a name is
indistinguishable from a gate to anybody reading rather than running. That is
now countable: scripts/check-cited-gates.py fails when a check names a
sibling check that does not exist.

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
# The statement-to-process chain moved to prototypes/ on 2026-07-28;
# these checks follow the drawing, not the folder.
PROTOTYPES = ROOT / "design-system" / "prototypes"

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
    # THE TWO BOXES ARE NOT THE SAME WIDTH, and this line said they were. The
    # claim was ".lp-flow reads --lp-measure and the card takes it as
    # --pin-measure" — the card does, the drawing never did. It is sized by
    # --sp-measure, its own function of the viewport's height, and measured on
    # the shipped page the two render 1109.59 px and 1280 px at 1440 x 900.
    # What the basis below actually is, therefore, is a map between the two
    # viewBoxes' PROPORTIONS, which is all this file uses it for: every clause
    # here asks where a point sits along its own box, and a proportion answers
    # that whatever the box measures. Where the two boxes land in PAGE pixels
    # is a different question, it was open by 85 px at the size this seam was
    # tuned at, and scripts/check-seam-centre.py is what closed it.
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

    # 2. THE SOURCE LANDS ON THE RAIL, mapped onto the frame's basis.
    #
    # THIS USED TO BE NINETEEN ARRIVALS AND IT IS NOW ONE. The review of
    # 2026-07-29 turned the root into a confluence — "the spheres should
    # collapse into the several endpoints ... and the tree should grow from
    # top to bottom" — so the fringe moved to the top of the flow box and the
    # single trunk resolves onto the bottom. What crosses the seam into the
    # lectern is therefore one thing, the source, and the test is that it
    # crosses at the right x rather than that nineteen of them do.
    #
    # THE ORB IS THE TERMINAL NOW, so it is what gets measured: its centre for
    # the x, its lower rim for the y. A stroke end cannot stand in for it —
    # the trunk stops at the orb's TOP rim, 68 units short of the foot, and
    # the 34 units of light between them are the part of the drawing that
    # actually touches the rule.
    orb = re.search(r'<circle\b[^>]*class="[^"]*lp-flow__orb[^"]*"[^>]*'
                    r'cx="(-?[\d.]+)"\s*cy="(-?[\d.]+)"\s*r="(-?[\d.]+)"', text)
    landed = []
    if not orb:
        findings.append(
            f"{page.name}: no .lp-flow__orb — the source is what lands on the "
            f"rail now, and nothing else in the flow reaches y {show(rail_y)}")
    else:
        ox, oy, orr = (Fraction(orb.group(i)) for i in (1, 2, 3))
        if oy + orr != rail_y:
            findings.append(
                f"{page.name}: the source's lower rim is at flow y "
                f"{show(oy + orr)} and the flow's foot is {show(rail_y)} — the "
                f"drawing either stops above the rule or hangs through it")
        fx = ox * basis
        landed.append(fx)
        if not (frame_left <= fx <= frame_right):
            findings.append(
                f"{page.name}: the source stands at flow x {show(ox)}, which is "
                f"frame x {show(fx)} — outside the top rail's span "
                f"{show(frame_left)}..{show(frame_right)}. It falls past the lectern.")

    # 3. THE LECTERN'S INNER VERTICAL CONTINUES IT.
    #
    # AND ONLY THE INNER ONE, which is the other half of the same change. The
    # three taproots used to arrive at flow x 0, 600 and 1200 and the frame's
    # three verticals stood up out of them; flipped, those three arrivals are
    # at the TOP of the drawing and the only thing at the bottom is the
    # source. The outer two verticals are the lectern's own sides — the box
    # has to have edges whether or not anything lands on them — so what is
    # held here is the one vertical that is a CONTINUATION rather than an
    # edge: the middle one, and it has to be fed.
    verticals = sorted({s[0][0] for s in frame
                        if s[0][0] == s[1][0] and min(s[0][1], s[1][1]) == frame_top})
    inner = [vx for vx in verticals if frame_left < vx < frame_right]
    if not inner:
        findings.append(
            f"{page.name}: the lectern has no vertical between its own sides — "
            f"nothing in the frame continues the drawing")
    for vx in inner:
        if landed and vx not in landed:
            findings.append(
                f"{page.name}: the lectern's vertical at frame x {show(vx)} grows down "
                f"from a point the source does not arrive at — it stands at frame x "
                f"{show(min(landed, key=lambda f: abs(f - vx)))}. "
                f"--a says the inner vertical continues what lands on it.")

    if verbose:
        print(f"  {page.name}: flow {flow_vb[2]} units wide, lectern {frame_vb[2]} — "
              f"basis {show(basis)}")
        print(f"    {len(frame)} hairlines, {len(frame) * 2} endpoints, all on the frame")
        # ONE ARRIVAL, NOT NINETEEN, and this loop was still printing the
        # nineteen. `drops` went out with the confluence rewrite of 2026-07-29
        # — clause 2 above says so in full — and the verbose branch kept the
        # name, so `-v` raised NameError while the plain run exited 0 and CI,
        # which runs it plain, stayed green. A check that cannot be asked to
        # explain itself is a check nobody re-reads.
        print(f"    {len(landed)} arrival(s) at flow y {show(rail_y)}:")
        for fx in landed:
            mark = "  <- inner vertical" if fx in verticals else "  <- on no vertical"
            print(f"      the source  ->  frame x {show(fx):>7}{mark}")

    return findings, True


def main():
    parser = argparse.ArgumentParser(
        description="Where one drawing ends, the next one starts — and that is a junction.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="print every drop and the frame x it hands over at")
    args = parser.parse_args()

    findings, seams = [], 0
    for page in sorted([*PATTERNS.glob("*.html"), *PROTOTYPES.glob("*.html")]):
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
          f"the source inside the top rail's span, and the inner vertical continuing it")
    return 0


if __name__ == "__main__":
    sys.exit(main())
