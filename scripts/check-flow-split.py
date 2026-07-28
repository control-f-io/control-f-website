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

THE GROWTH RULE IS RETIRED, BY REVIEW. 2026-07-28, second review: "remove
overlapping branches from the tree, make it branch equally". The grown root
was chosen limb by limb around its own obstacles, so no two limbs matched and
three terminals landed mid-stroke on their siblings — legal arrivals under
"no free ends", but the eye reads a T into another branch as overlap. The
drawing is now one WRITTEN-OUT symmetric construction (the balanced-
construction section of gen-flow-root.py): trunk to the crown, two mirrored
fans, a centre taproot, eight dives landing on the rail. Nothing is grown, so
there is no ratio to recompute — what "branch equally" means is now stated
here, as the three identities the construction rests on:

  1. THE DRAWING IS ITS OWN MIRROR. For every stroke, the stroke reflected
     about the trunk's line (x -> 1200 − x) is also in the drawing. One
     asymmetric limb anywhere fails twice — once as itself, once as the hole
     where its mirror should be.

  2. THE FEET ARE EQUALLY SPACED. Exactly nine arrivals on the rail, at
     x = 0, 150, 300, …, 1200 — every 150, no gaps, no doubles. The three
     the lectern is pinned to (flow 0, 600, 1200 = frame 0, 500, 1000,
     check-flow-handover.py's seam) are the outermost pair and the centre.

  3. THE CROWN DIVIDES ONCE, INTO THREE. Exactly one stroke enters the crown
     (the trunk out of the void) and exactly three leave it: the mirrored
     pair of reaches and the centre taproot. Every other junction divides
     into exactly two. A construction this regular has no second trifurcation
     to offer — one appearing is a redesign, not a drift.

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
FOOT_PITCH = Fraction(150)  # identity 2: nine feet, every 150

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

    # ---- 1. the drawing is its own mirror --------------------------------
    def norm(seg):
        (x1, y1), (x2, y2) = seg
        return tuple(sorted([(x1, y1), (x2, y2)]))

    have = {norm(s) for s in segs}
    for seg in segs:
        (x1, y1), (x2, y2) = seg
        mirror = norm(((WIDTH - x1, y1), (WIDTH - x2, y2)))
        if mirror not in have:
            findings.append(
                f"the stroke ({show(x1)}, {show(y1)}) -> ({show(x2)}, {show(y2)}) "
                f"has no mirror about x {show(WIDTH / 2)} — the root does not "
                f"branch equally")

    # ---- 2. the feet are equally spaced ----------------------------------
    feet = sorted({p[0] for s in segs for p in s if p[1] == RAIL})
    want = [FOOT_PITCH * k for k in range(int(WIDTH / FOOT_PITCH) + 1)]
    if feet != want:
        findings.append(
            f"the rail carries {len(feet)} arrivals at {[show(f) for f in feet]} — "
            f"the construction lands {len(want)}, every {show(FOOT_PITCH)} units "
            f"from {show(want[0])} to {show(want[-1])}")

    # ---- 3. the crown divides once, into three ---------------------------
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
    print(f"flow split OK — {len(segs)} strokes mirror about x {show(WIDTH / 2)}, "
          f"{len(feet)} feet every {show(FOOT_PITCH)} units across the rail, and "
          f"one crown dividing into three")
    return 0


if __name__ == "__main__":
    sys.exit(main())
