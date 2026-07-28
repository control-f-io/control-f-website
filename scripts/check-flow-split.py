#!/usr/bin/env python3
"""A root is self-similar, and self-similar means ONE constant.

The sixty-fifth check, and the fifth about the statement-to-process root's own
geometry. Between them the four that came before hold every question about that
drawing except the one Daniel asked of the shipped page:

    "the lines are messy still — this needs to be not random but
     mathematically correct based on the ratios and winkel in the design system"

THE WINKEL WERE ALREADY HELD. check-flow-terminals.py enumerates all forty-one
segments and holds every one to 0, 26.57, 45, 63.43 or 90 degrees, the five
foundations/geometry.html publishes. Measured on the paste this check was
written against, the count off that set is ZERO, and has been since the drawing
became a root.

THE RATIO WAS NOT HELD BY ANYTHING. gen-flow-root.py declares it once --

    RATIO = F(5, 8)        # where a branch puts its own junction, in its drop

-- and spends it thirteen times, and no file that ships and no script that runs
has ever read it. That is the whole finding. The generator asserts free ends and
crossings and brand angles about its own output; it cannot assert anything about
a coordinate typed into patterns/landing-page.html afterwards, which is where
every drift in this repository has come from, and the split is the one property
of this drawing that a hand edit can destroy while leaving all four of the other
flow checks perfectly green.

MEASURED, and this is not a hypothetical either. Take the branch at (805, 515),
which has 105 units of drop left to the rail, and swap its two legs: 65 then 40
becomes 40 then 65. Both legs keep their brand angle. Both ends still arrive.
The pair's Chebyshev run is unchanged, so every --l in the drawing and the whole
timing envelope are untouched and check-flow-chain.py is satisfied. The branch's
split goes from 0.619 to 0.381 -- a third of the way down its parent instead of
five eighths -- and ALL SIXTY-FOUR checks in the tree pass. That is the state
this closes.

THE RULE, in the drawing's own units. A grown branch leaves a junction at y with
`rem = 620 - y` of drop left to the rail, and spends it in exactly two legs:

    h1 = 5 * round(RATIO * rem / 5)      the first leg, on fives
    h2 = rem - h1                        the second, and it lands on the rail

Fives because the paste has to stay readable, and the rounding is the only slack
in the rule -- so the check does not compare a float to a float. It recomputes
h1 from the RATIO parsed out of the generator, in exact rational arithmetic, and
demands equality.

WHICH SEGMENTS THE RULE APPLIES TO IS DERIVED, NOT LISTED. Sizing a branch by
the drop it has left only makes sense for a branch that is free to land where it
lands. Three of this root's terminals are not free: flow x 0, 600 and 1200 are
frame x 0, 500 and 1000, so the three taproots must arrive exactly on the
lectern's three verticals and their lengths are a consequence of that
constraint, not of any ratio. gen-flow-root.py writes those three chains out by
hand for exactly this reason.

So the SKELETON is the union of the three paths from the void to (0, 620),
(600, 620) and (1200, 620) -- fifteen segments, computed here by walking the
drawing, never listed -- and everything else is GROWN. The rule is asserted on
the grown segments only, and the skeleton's own count is asserted too, because a
skeleton that quietly grew a fourth pinned arrival would move the boundary this
check reasons across.

THAT COUNT WAS SIXTEEN AND IS NOW FIFTEEN, and this assertion is what caught the
change that made it so, which is the assertion working rather than failing. The
right taproot's first flat run was written as two collinear steps, FR 70 then FR
80, to put a junction at (560, 265) for a branch to leave from -- the same
reason the middle taproot's long steep run is broken at (530, 355), which does
shed one. Nothing ever left (560, 265) and nothing can: all four seedings of
grow() decline it for want of room, and a branch there would be the twelfth node
in a drawing whose stated ceiling is eleven. Two collinear strokes drawn end to
end are one stroke, so it was a division that divided nothing -- invisible on
the page, a branch point in the markup. The two steps are one FR 150 now. No
coordinate moved, no --l or --u on any other stroke changed, and the skeleton is
one segment shorter because the drawing has one fewer place where nothing
happens. The three pinned ARRIVALS are still three, which is what this
assertion is really guarding.

AND THE FRINGE ANGLES, in the same sweep, because they are the other half of the
same sentence and are also stated only in a comment:

    A BRANCH ALTERNATES 45 AND 63.43, and never uses the outer two angles.

26.57 degrees crosses twice its own drop, so a branch on it is wider than the
taproot it hangs off and the fringe reads as a net; 0 does not descend at all.
Both are legal segments in check-flow-terminals.py's eyes, which is correct --
the taproots need 26.57, it is the only angle that crosses width cheaply -- and
both are wrong in the fringe. A grown leg may be 45, 63.43, or the 90 the growth
rule falls back to when neither side has room. Nothing else.

AND THE DEPTH, which is the bound the drawing has to state and hold rather than
run to its walls because the recursion had nowhere else to go. grow() caps at
two generations; a third puts more line under the rail's last 60 units than the
eye can separate at 1 px. In legs -- which is what the markup has -- two
generations is THREE: leg 1, leg 2, and the next generation leaving leg 1's own
tip. Four legs is a third generation, and four legs is the finding.

The other bound is the box, and it needs no check here. Every terminal is on the
rail at y 620 or on another branch (check-flow-terminals.py), the walls at x 0
and x 1200 are two of the three pinned arrivals, and check-flow-density.py holds
the ink's distribution across the six 200-unit bands between them. The root
stops where it is told to stop; what was unheld was how far each step inside
that box may go.

WHAT THIS DOES NOT HOLD, and it is worth saying plainly rather than leaving the
next person to discover it. The check proves the drawing turns on ONE constant
and that the constant is the generator's. It does not prove 5/8 is the right
constant -- nothing in tokens.css or foundations/geometry.html derives it, and
the generator's own comment does not attempt to. What the check does give that
argument is a floor: it reports the interval of constants the shipped geometry
actually admits, which on this paste is

    5/8 <= p <= 69/110        [0.625000, 0.627273], 0.23 % wide

with 5/8 sitting exactly on the left edge, held there by the two branches whose
drop is an exact multiple of eight (rem 380 and rem 140, where 5/8 lands on a
half and rounds up). Any replacement for 5/8 outside that band moves at least
one branch, and this check is what will say which.
"""

import argparse
import math
import re
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = ROOT / "design-system" / "patterns"
# The statement-to-process chain moved to prototypes/ on 2026-07-28;
# these checks follow the drawing, not the folder.
PROTOTYPES = ROOT / "design-system" / "prototypes"
GENERATOR = ROOT / "scripts" / "expertise-objects" / "gen-flow-root.py"

# class -> (segment class, the three arrivals the frame's verticals pin)
DRAWINGS = {"lp-flow": ("lp-flow__seg", (0, 600, 1200))}

SVG_RE = re.compile(r'<svg\b[^>]*class="([^"]*)"[^>]*viewBox="([^"]*)"(.*?)</svg>', re.S)
PATH_RE = re.compile(r'<path\b[^>]*class="([^"]*)"[^>]*\bd="([^"]*)"', re.S)
CMD_RE = re.compile(r'([MLVH])\s*(-?[\d.]+)(?:[ ,]+(-?[\d.]+))?')
RATIO_RE = re.compile(r'^RATIO\s*=\s*F\((\d+),\s*(\d+)\)', re.M)

# The two angles a grown leg may leave on, plus the vertical the growth rule
# falls back to when neither side is free. dx/dy, as parse_path yields it.
FRINGE = {Fraction(1): "45", Fraction(0): "90"}
FRINGE_STEEP = Fraction(1, 2)   # 63.43


def rational(text):
    return Fraction(text).limit_denominator(10 ** 6)


def fm(v):
    """A coordinate the way the paste writes it, not as a raw Fraction."""
    v = float(v)
    return str(int(v)) if v == int(v) else f"{v:g}"


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


def angle_of(seg):
    (x1, y1), (x2, y2) = seg
    dx, dy = x2 - x1, y2 - y1
    if dy == 0:
        return "0"
    if dx == 0:
        return "90"
    return f"{math.degrees(math.atan2(abs(dy), abs(dx))):.2f}"


def declared_ratio():
    """The one constant, read out of the generator that spends it."""
    m = RATIO_RE.search(GENERATOR.read_text(encoding="utf-8"))
    if not m:
        return None
    return Fraction(int(m.group(1)), int(m.group(2)))


def split(ratio, rem):
    """Where the branch puts its own junction: RATIO of the drop, on fives."""
    return 5 * round(ratio * rem / 5)


def skeleton_of(segs, rail, pins):
    """The pinned chains, walked out of the drawing rather than listed.

    The three taproots are the paths from the void to the three arrivals the
    lectern's verticals stand up out of. Their lengths answer to that
    constraint, so the ratio has nothing to say about them.
    """
    out_of = {}
    for i, (a, b) in enumerate(segs):
        out_of.setdefault(a, []).append((i, b))
    void = sorted({s[0] for s in segs}, key=lambda p: (p[1], p[0]))[0]

    pinned = set()
    for px in pins:
        target = (Fraction(px), rail)
        stack = [(void, [])]
        seen = {void}
        while stack:
            here, path = stack.pop()
            if here == target:
                pinned.update(path)
                break
            for i, nxt in out_of.get(here, ()):
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append((nxt, path + [i]))
    return pinned, void


def check_drawing(name, cls, body, view_box, ratio, verbose):
    seg_cls, pins = DRAWINGS[cls]
    rail = rational(view_box.split()[3])

    segs = []
    for classes, d in PATH_RE.findall(body):
        if seg_cls in classes.split():
            segs.extend(parse_path(d))
    if not segs:
        return [f"{name}: .{cls} carries no .{seg_cls} at all"], 0, None

    pinned, void = skeleton_of(segs, rail, pins)
    findings = []
    if len(pinned) != 15:
        findings.append(
            f"{name}: the three pinned chains cover {len(pinned)} segments, not the "
            f"15 gen-flow-root.py writes out — the boundary between what the ratio "
            f"governs and what the frame's verticals govern has moved"
        )

    # what leaves each point, so a leg knows whether anything continues it
    out_of = {}
    for i, (a, b) in enumerate(segs):
        out_of.setdefault(a, []).append(i)

    # window of constants the drawing itself admits, narrowed branch by branch
    lo, hi = Fraction(0), Fraction(1)
    rows, checked = [], 0

    for i, (a, b) in enumerate(segs):
        if i in pinned:
            continue
        rem = rail - a[1]
        drop = b[1] - a[1]

        # THE ANGLE, in the fringe's narrower vocabulary
        (x1, y1), (x2, y2) = segs[i]
        dxdy = abs(Fraction(x2 - x1, y2 - y1)) if y2 != y1 else None
        if dxdy is None or (dxdy not in FRINGE and dxdy != FRINGE_STEEP):
            findings.append(
                f"{name}: grown segment {i} leaves ({fm(a[0])}, {fm(a[1])}) at "
                f"{angle_of(segs[i])}deg — a branch alternates 45 and 63.43 and falls "
                f"back to 90; the outer two angles belong to the taproots"
            )

        # WHICH LEG THIS IS, and the classification is not "does it touch the
        # rail". A leg that stops in open wash would answer no to that and be
        # measured against the wrong half of the rule -- and a mid-air stop
        # whose drop happened to match the split would then read as a clean
        # first leg. So a FIRST leg is one something continues from, and
        # anything that continues from nothing is the finding itself.
        if b[1] == rail:
            if drop != rem:
                findings.append(
                    f"{name}: the leg from ({fm(a[0])}, {fm(a[1])}) lands on the rail "
                    f"having spent {fm(drop)} of the {fm(rem)} it had — a branch is two "
                    f"legs and the second one spends what the first left"
                )
            if out_of.get(b):
                findings.append(
                    f"{name}: a stroke grows out of ({fm(b[0])}, {fm(b[1])}), which is on "
                    f"the rail — the drawing hands over there and stops"
                )
        elif not out_of.get(b):
            findings.append(
                f"{name}: the leg from ({fm(a[0])}, {fm(a[1])}) stops at "
                f"({fm(b[0])}, {fm(b[1])}) with {fm(rem - drop)} of drop still under it "
                f"and nothing continuing it — a branch is two legs and the second one "
                f"reaches the rail"
            )
        else:
            want = split(ratio, rem)
            checked += 1
            rows.append((i, a, rem, drop, want))
            if drop != want:
                findings.append(
                    f"{name}: the branch at ({fm(a[0])}, {fm(a[1])}) has {fm(rem)} of "
                    f"drop left and spends {fm(drop)} of it before it turns — "
                    f"{Fraction(drop, rem)} ({float(Fraction(drop, rem)):.4f}) where the "
                    f"one constant gen-flow-root.py turns on gives {fm(want)} "
                    f"({float(Fraction(want, rem)):.4f}). A root is self-similar."
                )
            else:
                # 5*round(p*rem/5) == want pins p to this closed interval
                lo = max(lo, Fraction(2 * want - 5, 2 * rem))
                hi = min(hi, Fraction(2 * want + 5, 2 * rem))

    # THE BOUND, counted in LEGS off the skeleton, because a leg is what the
    # markup has. A generation is two of them, and the cap is two generations.
    depth = {i: (0 if i in pinned else None) for i in range(len(segs))}
    changed = True
    while changed:
        changed = False
        for i, (a, _b) in enumerate(segs):
            if depth[i] is not None:
                continue
            parents = [depth[j] for j, (_c, e) in enumerate(segs)
                       if e == a and depth[j] is not None]
            if parents:
                depth[i] = min(parents) + 1
                changed = True
    orphans = [i for i, d in depth.items() if d is None]
    for i in orphans:
        findings.append(
            f"{name}: grown segment {i} leaves ({fm(segs[i][0][0])}, {fm(segs[i][0][1])}), "
            f"which nothing arrives at — it hangs off no branch of this drawing"
        )
    grown_depth = max((d for i, d in depth.items() if i not in pinned and d), default=0)
    if grown_depth > 3:      # leg 1, leg 2, and the next generation off leg 1
        findings.append(
            f"{name}: the fringe runs {grown_depth} legs deep off the skeleton — "
            f"gen-flow-root.py caps the growth at two generations because a third "
            f"puts more line under the rail's last 60 units than 1 px can separate"
        )

    if verbose:
        print(f"  {name} .{cls}: {len(segs)} segments, {len(pinned)} pinned by the "
              f"frame's verticals, {len(segs) - len(pinned)} grown, void at "
              f"({void[0]}, {void[1]})")
        print(f"    {'#':>3}  {'junction':>16} {'rem':>5} {'h1':>5} {'h1/rem':>8} "
              f"{'want':>5}")
        for i, a, rem, drop, want in rows:
            print(f"    {i:>3}  ({fm(a[0]):>7}, {fm(a[1]):>5}) {fm(rem):>5} {fm(drop):>5} "
                  f"{float(Fraction(drop, rem)):>8.4f} {fm(want):>5}")
        print(f"    the shipped geometry admits {lo} <= p <= {hi}  "
              f"[{float(lo):.6f}, {float(hi):.6f}], {grown_depth} legs deep")

    return findings, checked, (lo, hi)


def main():
    parser = argparse.ArgumentParser(
        description="A root is self-similar, and self-similar means one constant.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="print every grown branch, its drop, and its split")
    args = parser.parse_args()

    ratio = declared_ratio()
    if ratio is None:
        print(f"flow split: no RATIO in {GENERATOR.relative_to(ROOT)} — the one "
              f"constant this check reads has been renamed or removed")
        return 1

    findings, checked, drawings, band = [], 0, 0, None
    for page in sorted([*PATTERNS.glob("*.html"), *PROTOTYPES.glob("*.html")]):
        text = page.read_text(encoding="utf-8")
        for classes, view_box, body in SVG_RE.findall(text):
            for cls in DRAWINGS:
                if cls in classes.split():
                    drawings += 1
                    f, c, b = check_drawing(page.name, cls, body, view_box, ratio,
                                            args.verbose)
                    findings += f
                    checked += c
                    band = b

    if not drawings:
        print("flow split: no drawing to check — the selector went stale")
        return 1
    if findings:
        print(f"\nflow split: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1
    lo, hi = band
    print(f"flow split OK — {checked} grown branches across {drawings} drawing(s), "
          f"every one splitting its remaining drop at {ratio} on fives, every second "
          f"leg spending the rest, every leg on 45, 63.43 or 90, and the geometry "
          f"admitting {lo} <= p <= {hi} with {ratio} on the edge of it")
    return 0


if __name__ == "__main__":
    sys.exit(main())
