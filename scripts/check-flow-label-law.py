#!/usr/bin/env python3
"""Every numeral on the root is placed by one law, not by hand.

The sixty-fifth check, and the third at this drawing's numerals -- the sibling
of check-flow-values.py, which holds what they SAY, and check-label-ramp.py,
which holds the type they say it in. This one holds where they STAND.

WHAT WAS WRONG. --tx/--ty on the eight .lp-flow__val were eight hand-typed
AXIS-ALIGNED pairs: "12px" across and "8px" down, or "-50%", in whatever
combination looked right beside each stroke. A numeral is a horizontal box on a
sloped line, so an axis-aligned offset buys only its own projection onto that
line's normal -- and the eight projections came out anywhere from 7.55 to
14.14 px. Measured on the render at 1440 x 900, nearest corner of the label box
to the stroke it names:

    12 480   11.99      3 840   12.52      3 200   14.13      5 440   12.52
     1 360    7.56       4 080   12.53      2 400   12.54      1 680    7.55

One drawing, one published clearance -- ".lp-flow__val ... these hold 12 px off
the line at every viewport the gate admits" -- and an 87 % spread under it,
with the two tightest 37 % below the number the rule states. None of it visible
in review: a numeral 7.5 px off a line and a numeral 14 px off a line both read
as a numeral near a line. That is the whole failure shape, and it is the one
this repository writes checks for -- true of some elements, false of others,
invisible in a screenshot, and it comes back the first time anyone nudges a
label for entirely good reasons of composition.

THE LAW, and it decides all eight with nothing left over:

    A numeral sits exactly 12 px from the stroke it names, measured
    perpendicular from the numeral's NEAREST CORNER, on that stroke's LEFT --
    and on its right only where the left would bring another stroke inside the
    same 12 px.

PERPENDICULAR is the offset's direction: 12 * (dy, -dx) / |d| for the left,
its negation for the right. NEAREST CORNER is what the anchoring is for -- a
positive component anchors that axis at 0 and a negative one at -100%, so the
box grows into the quadrant the offset points into and no other corner of it is
nearer the line than the anchor corner. A zero component centres (-50%), which
only the vertical trunk uses. On the drawing's four labelled slopes the law
yields four offsets and no fifth, each of magnitude exactly 12:

    vertical  (12, 0)              1:1  (8.485, -8.485)   = 12 / sqrt 2
    1:2       (5.367, -10.733)     2:1  (10.733, -5.367)  = 12 / sqrt 5

THE SIDE IS DERIVED, WHICH IS THE HALF A MAGNITUDE CHECK WOULD MISS. Three of
the eight take the right: 3 200, 1 360 and 1 680, each the steeper of two
strokes leaving one junction, so its left is the inside of the fork and the
fork closes on it. Measured at the gate floor -- 1024, where the drawing's box
is smallest and this 11 px label is therefore largest against the strokes --
left-side box to the nearest stroke it does not name: 1.20, 0.00 and 0.00 px,
two of them literal crossings. The other five clear their left by 24.78 to
45.64 px and stay there. A check that only asserted "|offset| == 12" would pass
a numeral flipped onto the side that crosses a stroke.

WHAT IT DOES NOT PROMISE. The law BARS a side; it does not guarantee the other
one is roomy. 1 680 takes its right at 10.94 px, which is the tightest mark on
this drawing and under the 12 the law names -- a geometry finding about the
63.43deg dive out of (840, 405) running close to its own sibling, not a
placement one. It is recorded, not nudged, and this check reports it as a note
rather than a finding, because moving the label off the law to hide it is
exactly the hand placement the law exists to end.

THE SCALE THIS IS DECIDED AT. Offsets and the label box are in PIXELS; the
strokes are in the drawing's units. The ratio is 0.75948 px/unit at the gate
floor, 0.91333 at 1440, 1.06667 at 1920 -- so the label is largest against the
strokes at the floor, and the floor is the scale a side has to survive. All
three constants below are measured on the render, and the label box used is the
line box rather than the glyphs, which is the conservative end.

    python3 scripts/check-flow-label-law.py       # check, exit 1 on a finding
    python3 scripts/check-flow-label-law.py -v    # print the table
"""

import argparse
import math
import re
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = ROOT / "design-system" / "patterns"

DRAWINGS = {"lp-flow": ("lp-flow__seg", "lp-flow__val")}

CLEARANCE = 12.0        # px, the one number the whole law is
LABEL_ADVANCE = 7.111   # px per character, 11 px Geist Mono at --tracking-label
LABEL_HEIGHT = 14.30    # px, the line box
FLOOR_SCALE = 0.75948   # px per drawing unit at the gate floor, 1024
TOL = 0.001             # px; the offsets ship rounded to three places

FIGURE_RE = re.compile(r'<svg\b[^>]*class="([^"]*)"[^>]*viewBox="([^"]*)"(.*?)</svg>'
                       r'(.*?)(?=<svg\b|</div>\s*<div class="cf-statement__text")', re.S)
PATH_RE = re.compile(r'<path\b[^>]*class="([^"]*)"[^>]*\bd="([^"]*)"', re.S)
SPAN_RE = re.compile(r'<span\b[^>]*class="([^"]*)"[^>]*style="([^"]*)"[^>]*>([^<]*)</span>', re.S)
CMD_RE = re.compile(r'([MLVH])\s*(-?[\d.]+)(?:[ ,]+(-?[\d.]+))?')

# "5.367px" | "calc(-100% - 10.733px)" | "-50%" -- the three shapes the law
# emits, and nothing else is a legal offset. An axis-aligned "8px" is legal
# SYNTAX; it is the value that fails below.
PX_RE = re.compile(r'^(-?[\d.]+)px$')
NEG_RE = re.compile(r'^calc\(-100% - ([\d.]+)px\)$')


def rational(text):
    return Fraction(text.strip()).limit_denominator(10 ** 6)


def parse_path(d):
    segs, cur = [], None
    for cmd, a, b in CMD_RE.findall(d):
        if cmd == "M":
            cur = (rational(a), rational(b))
        elif cmd == "L":
            nxt = (rational(a), rational(b))
            segs.append((cur, nxt))
            cur = nxt
        elif cmd == "V":
            nxt = (cur[0], rational(a))
            segs.append((cur, nxt))
            cur = nxt
        elif cmd == "H":
            nxt = (rational(a), cur[1])
            segs.append((cur, nxt))
            cur = nxt
    return segs


def on_segment(p, seg):
    (x1, y1), (x2, y2) = seg
    if (x2 - x1) * (p[1] - y1) - (y2 - y1) * (p[0] - x1) != 0:
        return False
    return min(x1, x2) <= p[0] <= max(x1, x2) and min(y1, y2) <= p[1] <= max(y1, y2)


def style_vars(style):
    out = {}
    for decl in style.split(";"):
        if ":" in decl and decl.strip().startswith("--"):
            name, _, value = decl.partition(":")
            out[name.strip()] = value.strip()
    return out


def read_offset(text):
    """(px, anchor) for one component, or None if it is not a shape the law emits.

    anchor is 0 for a near edge at the point's own side, -1 for -100%, and
    None for the centred -50%, which is only legal on a zero component.
    """
    if text == "-50%":
        return 0.0, None
    m = PX_RE.match(text)
    if m:
        return float(m.group(1)), 0
    m = NEG_RE.match(text)
    if m:
        return -float(m.group(1)), -1
    return None


def label_box(px, py, sx, sy, chars):
    """The label's box in drawing units, 12 px along (sx, sy) at the gate floor."""
    w = chars * LABEL_ADVANCE / FLOOR_SCALE
    h = LABEL_HEIGHT / FLOOR_SCALE
    off = CLEARANCE / FLOOR_SCALE
    ax, ay = px + off * sx, py + off * sy
    x0 = ax if sx > 0 else (ax - w if sx < 0 else ax - w / 2)
    y0 = ay if sy > 0 else (ay - h if sy < 0 else ay - h / 2)
    return x0, y0, x0 + w, y0 + h


def box_gap(seg, box, samples=400):
    """Least distance in units from a segment to an axis-aligned box, 0 if it crosses."""
    (x1, y1), (x2, y2) = [(float(a), float(b)) for a, b in seg]
    bx0, by0, bx1, by1 = box
    best = float("inf")
    for i in range(samples + 1):
        px = x1 + (x2 - x1) * i / samples
        py = y1 + (y2 - y1) * i / samples
        dx = max(bx0 - px, 0.0, px - bx1)
        dy = max(by0 - py, 0.0, py - by1)
        best = min(best, math.hypot(dx, dy))
    return best


def check_drawing(name, cls, svg_body, tail, verbose):
    seg_cls, val_cls = DRAWINGS[cls]

    segs = []
    for classes, d in PATH_RE.findall(svg_body):
        if seg_cls in classes.split():
            segs.extend(parse_path(d))
    if not segs:
        return [f"{name}: .{cls} carries no .{seg_cls} at all"], 0, []

    findings, notes, checked = [], [], 0
    for classes, style, text in SPAN_RE.findall(tail):
        if val_cls not in classes.split():
            continue
        var = style_vars(style)
        shown = text.strip()
        if "--x" not in var or "--y" not in var:
            findings.append(f"{name}: the value {shown!r} declares no point")
            continue
        p = (rational(var["--x"]), rational(var["--y"]))

        own = [s for s in segs if on_segment(p, s)]
        if len(own) != 1:
            findings.append(
                f"{name}: the value {shown!r} stands at ({p[0]}, {p[1]}), which is on "
                f"{len(own)} segment(s) of the drawing. The law places a numeral against "
                f"THE stroke it names; on none there is nothing to be perpendicular to, "
                f"and on two 'its stroke' is a guess.")
            continue
        (x1, y1), (x2, y2) = own[0]
        dx, dy = float(x2 - x1), float(y2 - y1)
        length = math.hypot(dx, dy)
        left = (dy / length, -dx / length)

        got = [read_offset(var.get("--tx", "")), read_offset(var.get("--ty", ""))]
        if None in got:
            findings.append(
                f"{name}: the value {shown!r} has --tx/--ty "
                f"{var.get('--tx')!r} / {var.get('--ty')!r}, and the law emits only "
                f"'<n>px', 'calc(-100% - <n>px)' and '-50%'. Anything else is a hand "
                f"placement wearing the class.")
            continue
        (ox, ax), (oy, ay) = got

        # which side did it take, and is that the side the law gives it?
        want_side = None
        for side, (sx, sy) in (("left", left), ("right", (-left[0], -left[1]))):
            if (abs(ox - CLEARANCE * sx) <= TOL and abs(oy - CLEARANCE * sy) <= TOL):
                want_side = side
                break
        if want_side is None:
            best = max(
                (abs(ox - CLEARANCE * s[0]) + abs(oy - CLEARANCE * s[1]), n, s)
                for n, s in (("left", left), ("right", (-left[0], -left[1])))
            )
            findings.append(
                f"{name}: the value {shown!r} is offset ({ox:+.3f}, {oy:+.3f}) px from its "
                f"point, which is {math.hypot(ox, oy):.2f} px along "
                f"{math.degrees(math.atan2(oy, ox)):+.1f}deg. Its stroke "
                f"({x1}, {y1}) -> ({x2}, {y2}) runs at "
                f"{math.degrees(math.atan2(dy, dx)):.2f}deg, so the law's two offsets are "
                f"({CLEARANCE * left[0]:+.3f}, {CLEARANCE * left[1]:+.3f}) on the left and "
                f"({-CLEARANCE * left[0]:+.3f}, {-CLEARANCE * left[1]:+.3f}) on the right. "
                f"A numeral is placed 12 px PERPENDICULAR to the stroke it names, not "
                f"12 across and 8 down.")
            continue

        # the anchoring has to put the NEAREST corner at the offset, or "12 px"
        # measures from a corner that is not the near one and the number is a
        # different number.
        for comp, off, anchor, axis in ((ox, ox, ax, "--tx"), (oy, oy, ay, "--ty")):
            want = None if abs(off) <= TOL else (0 if off > 0 else -1)
            if anchor != want:
                findings.append(
                    f"{name}: the value {shown!r} offsets {axis} by {off:+.3f} px and "
                    f"anchors it {'centred' if anchor is None else ('0' if anchor == 0 else '-100%')}. "
                    f"The box has to grow AWAY from the line, so a positive component "
                    f"anchors at 0, a negative one at -100%, and only a zero component "
                    f"centres — otherwise the corner that holds the 12 px is not the "
                    f"nearest corner and the clearance is not 12 px.")

        # the side, against the geometry
        chars = len(shown)
        gaps = {}
        for side, (sx, sy) in (("left", left), ("right", (-left[0], -left[1]))):
            box = label_box(float(p[0]), float(p[1]), sx, sy, chars)
            gaps[side] = min(box_gap(s, box) for s in segs if s != own[0]) * FLOOR_SCALE
        law_side = "left" if gaps["left"] >= CLEARANCE else "right"
        if want_side != law_side:
            findings.append(
                f"{name}: the value {shown!r} takes its stroke's {want_side}, and the law "
                f"gives it the {law_side}. At the gate floor its left box comes within "
                f"{gaps['left']:.2f} px of a stroke it does not name and its right within "
                f"{gaps['right']:.2f} px; the left is taken unless it brings another "
                f"stroke inside the same 12 px.")
        elif gaps[law_side] < CLEARANCE:
            notes.append(
                f"{name}: {shown!r} takes its {law_side} at {gaps[law_side]:.2f} px from the "
                f"nearest stroke it does not name — under the 12 the law states, because "
                f"the law bars a side rather than promising one. Geometry, not placement.")
        if verbose:
            print(f"    {shown:>8}  ({float(p[0]):>5.1f},{float(p[1]):>5.1f})  "
                  f"{math.degrees(math.atan2(dy, dx)):>7.2f}deg  {want_side:>5}  "
                  f"offset ({ox:+7.3f},{oy:+7.3f})  |offset| {math.hypot(ox, oy):6.3f}  "
                  f"other strokes: left {gaps['left']:6.2f}  right {gaps['right']:6.2f}")
        checked += 1

    return findings, checked, notes


def main():
    parser = argparse.ArgumentParser(description="Every numeral is placed by one law.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="print the offset and both side clearances for every numeral")
    args = parser.parse_args()

    findings, notes, values, drawings = [], [], 0, 0
    for page in sorted(PATTERNS.glob("*.html")):
        text = page.read_text(encoding="utf-8")
        for classes, _view_box, svg_body, tail in FIGURE_RE.findall(text):
            for cls in DRAWINGS:
                if cls in classes.split():
                    drawings += 1
                    if args.verbose:
                        print(f"  {page.name} .{cls}:")
                    f, n, note = check_drawing(page.name, cls, svg_body, tail, args.verbose)
                    findings += f
                    notes += note
                    values += n

    if not drawings:
        print("flow label law: no drawing to check — the selector went stale")
        return 1
    if not values and not findings:
        print("flow label law: the drawing carries no numerals — the routes lost their data")
        return 1
    for n in notes:
        print(f"  note: {n}")
    if findings:
        print(f"\nflow label law: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1
    print(f"flow label law OK — {values} numerals across {drawings} drawing(s), every one "
          f"offset exactly {CLEARANCE:g} px perpendicular to the stroke it names, anchored so "
          f"that offset lands on its nearest corner, and on its stroke's left except where "
          f"the left would bring another stroke inside the same {CLEARANCE:g} px")
    return 0


if __name__ == "__main__":
    sys.exit(main())
