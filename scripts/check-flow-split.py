#!/usr/bin/env python3
"""The root branches equally, and equally is arithmetic.

WHAT THIS FILE USED TO HOLD. The grown root sized every free branch by the
drop it had left — h1 = 5 * round(RATIO * rem / 5), h2 = rem − h1 — and this
check recomputed that split from the RATIO parsed out of gen-flow-root.py, in
exact rational arithmetic, on every grown segment; the three pinned taproots
were derived by walking the drawing and exempted, and the skeleton's count
(fifteen) was asserted so the boundary could not drift. It was written against
Daniel's first review of the drawing — "not random but mathematically correct
based on the ratios and winkel in the design system".

THE GROWTH RULE IS BACK, BY REVIEW. 2026-07-28, third review: "more arms,
and actually go back to the procedural generated graph". The symmetric
construction the second review asked for did remove every overlap, and what
it left was eighteen strokes and nine feet at exactly 150 units apart —
a truss. It read as a diagram of a tree rather than as a root, which is the
thing symmetry cannot help doing: reflection is not balance, it is one half
drawn twice.

So the root is grown again, and the three faults the second review named are
answered inside the growth rule instead of by deleting it — a branch commits
both legs or neither, a clearance test refuses a step that merely comes NEAR
another stroke, and a step may not land on a point that already exists, which
is what kept two limbs from merging into a cycle. What "branches equally"
means moves with it, from reflection to the four identities below.

  1. THE TWO HALVES CARRY THE SAME MASS. Equal strokes either side of the
     trunk's line, to within a tenth — that is balance, and it is what the
     mirror was a much stronger claim than. A drawing can satisfy it with two
     halves that look nothing alike, which is the entire point. The tolerance
     is a fraction and not a count on purpose: the growth stops a limb where
     the box runs out of room, and the two sides do not run out at the same
     stroke. One limb of difference is the rule working; five would be a side
     the seeds forgot.

  2. THE FEET ARE UNEVENLY SPACED, AND NO TWO ARE CLOSER THAN THE
     CLEARANCE. The truss's identity was "every 150"; this one's is the
     opposite, and it is not the absence of a law. Sixteen or more arrivals,
     no two within CLEAR units of each other, and at least four distinct
     gaps — a root that lands its feet on a pitch is a comb.

  3. THE THREE PINNED FEET ARE PRESENT. x 0, 600 and 1200 — flow to frame
     0, 500, 1000, the seam check-flow-handover.py holds. Those three are
     the constraint the growth is written around and the one part of the
     old identity 2 that survives it.

  4. THE CROWN DIVIDES ONCE, INTO THREE. Exactly one stroke enters the crown
     and exactly three leave it: the mirrored pair of reaches and the centre
     taproot. Every other junction divides into two. A second trifurcation is
     a redesign, not a drift.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-flow-split.py       # check, exit 1 on a finding
    python3 scripts/check-flow-split.py -v    # print the feet and the crown
"""

import argparse
import re
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "design-system" / "prototypes" / "statement-to-process.html"

WIDTH = Fraction(1200)      # the shared basis; the mirror is x -> WIDTH - x
RAIL = Fraction(620)
PINNED = (Fraction(0), Fraction(600), Fraction(1200))   # identity 3
MIN_FEET = 16              # identity 2: a grown root fills its rail
MIN_GAPS = 4               # identity 2: distinct gaps between feet
CLEAR = Fraction(14)       # identity 2, and gen-flow-root.py's own CLEAR

SVG_RE = re.compile(r'<svg\b[^>]*class="([^"]*)"[^>]*viewBox="([^"]*)"(.*?)</svg>', re.S)
PATH_RE = re.compile(r'<path\b[^>]*class="([^"]*)"[^>]*\bd="([^"]*)"', re.S)
CMD_RE = re.compile(r'([MLVH])\s*(-?[\d.]+)(?:[ ,]+(-?[\d.]+))?')


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


def main():
    parser = argparse.ArgumentParser(
        description="The root branches equally, and equally is arithmetic.")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    text = PAGE.read_text(encoding="utf-8")
    flow = None
    for classes, view_box, body in SVG_RE.findall(text):
        if "lp-flow" in classes.split():
            flow = body
            break
    if flow is None:
        print("flow split: .lp-flow is not on the page — the selector went stale")
        return 1

    segs = []
    for classes, d in PATH_RE.findall(flow):
        if "lp-flow__seg" in classes.split():
            segs.extend(parse_path(d))
    if not segs:
        print("flow split: .lp-flow carries no .lp-flow__seg")
        return 1

    findings = []

    # ---- 1. the two halves carry the same mass ---------------------------
    def side(seg):
        mid = (seg[0][0] + seg[1][0]) / 2
        return 0 if mid < WIDTH / 2 else (1 if mid > WIDTH / 2 else None)

    left = sum(1 for s_ in segs if side(s_) == 0)
    right = sum(1 for s_ in segs if side(s_) == 1)
    if abs(left - right) > max(2, round((left + right) * 0.1)):
        findings.append(
            f"{left} strokes left of the trunk and {right} right of it — the two "
            f"halves are meant to carry the same mass, which is the claim that "
            f"replaced the mirror, not a weaker version of it")

    # ---- 2. the feet are unevenly spaced, and never crowded --------------
    feet = sorted({p[0] for s_ in segs for p in s_ if p[1] == RAIL})
    gaps = [feet[i + 1] - feet[i] for i in range(len(feet) - 1)]
    if len(feet) < MIN_FEET:
        findings.append(
            f"the rail carries {len(feet)} arrivals — a grown root lands at least "
            f"{MIN_FEET}, and below that the drawing is a bus again")
    tight = [(feet[i], feet[i + 1]) for i, g in enumerate(gaps) if g < CLEAR]
    if tight:
        where = ", ".join(f"{show(a)}/{show(b)}" for a, b in tight)
        findings.append(
            f"{len(tight)} pair(s) of feet closer than {show(CLEAR)} units — at "
            f"{where}. Two feet inside the clearance are one thick foot at 1 px")
    if len(set(gaps)) < MIN_GAPS:
        findings.append(
            f"the feet fall on {len(set(gaps))} distinct gap(s) — a root that "
            f"lands its feet on a pitch is a comb, and evenly spaced was the "
            f"truss's identity, not this one's")

    # ---- 3. the three pinned feet are present ----------------------------
    missing = [x for x in PINNED if x not in feet]
    if missing:
        findings.append(
            f"the rail is missing the pinned arrival(s) at x {', '.join(show(x) for x in missing)} "
            f"— the lectern's verticals stand up out of those three "
            f"(check-flow-handover.py)")

    # ---- 4. the crown divides once, into three ---------------------------
    out_count = Counter(s[0] for s in segs)
    in_count = Counter(s[1] for s in segs)
    crowns = [p for p, n in out_count.items() if n >= 3]
    if len(crowns) != 1:
        findings.append(
            f"{len(crowns)} junction(s) shed three or more strokes "
            f"({[(show(x), show(y)) for x, y in crowns]}) — the construction has "
            f"exactly one crown, and a second trifurcation is a redesign")
    else:
        crown = crowns[0]
        if out_count[crown] != 3 or in_count[crown] != 1:
            findings.append(
                f"the crown at ({show(crown[0])}, {show(crown[1])}) takes "
                f"{in_count[crown]} stroke(s) and sheds {out_count[crown]} — the "
                f"trunk enters once and the two reaches and the taproot leave")

    if args.verbose:
        print(f"  {len(segs)} strokes, {len(feet)} feet on the rail")
        print(f"  feet: {', '.join(show(f) for f in feet)}")
        if len(crowns) == 1:
            print(f"  crown at ({show(crowns[0][0])}, {show(crowns[0][1])}): "
                  f"{in_count[crowns[0]]} in, {out_count[crowns[0]]} out")

    if findings:
        print(f"\nflow split: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1
    print(f"flow split OK — {len(segs)} strokes balanced about x {show(WIDTH / 2)} "
          f"({left} left, {right} right), {len(feet)} feet on {len(set(gaps))} "
          f"distinct gaps with none inside {show(CLEAR)} units, the three pinned "
          f"arrivals present, and one crown dividing into three")
    return 0


if __name__ == "__main__":
    sys.exit(main())
