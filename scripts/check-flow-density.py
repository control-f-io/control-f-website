#!/usr/bin/env python3
"""A root fills its box. It may thin at the walls; it may not have a hole in it.

The thirty-eighth check, and the second one the statement-to-process root has
needed. check-flow-terminals.py holds every stroke to a brand angle and every
terminal to an arrival — and a drawing can satisfy both of those completely
while being lopsided enough that a reader sees a bus on one side and a thicket
on the other. That is what shipped.

WHAT IT USED TO LOOK LIKE. The root's right taproot crossed from (720, 345) to
(970, 470) in a single step: 250 units of width, the longest stroke in the
drawing, with no junction anywhere along it. gen-flow-root.py grows branches
from junctions, so a run with none on it grows nothing, and the ground it
crossed stayed empty. Measured as stroke length over the box's six 200-unit
bands, on the paste this check was written against:

    x    0- 200   27.5 %          x  600- 800   20.2 %
    x  200- 400   17.0 %          x  800-1000    6.1 %   <-- the run
    x  400- 600   19.9 %          x 1000-1200    9.3 %

An even sixth is 16.7 %. One interior band at 6.1 % is not a drawing that
thins, it is a drawing with a quarter of its width missing, and the fix was one
junction: the run written as 60 + 65 instead of 125, which does not move the
taproot by a unit and which the growth rule then fills.

WHY A CHECK AND NOT A NOTE. Every part of this is invisible to the checks that
already run. The angles were all legal. Every terminal arrived. The generator's
assertions passed. The markup even carried the rule in prose — "a root branches
along a straight length as well as at its bends, and a junction is where a
branch can leave from" — applied to the middle taproot's long run and never to
the longer one beside it. Prose is how this was kept, and prose is what was
true while it was wrong. The same edit is available again to anyone who
lengthens a taproot step to reach a wall, which is exactly what the flattest
angle in the system makes tempting.

THE RULE, and why the walls are exempt. The box is divided into six bands of
200 units. The four INTERIOR bands each carry at least 10 % of the drawing's
total stroke length. The two bands at the walls are not held to it: a root
genuinely thins as it spreads, the taproots arrive at x 0 and x 1200 rather
than passing through them, and the right wall reads 8.7 % today for reasons
that are the drawing's form and not a defect in it. The interior is where a
hole is a hole. The margin is real in both directions — the failure this is
written against sat at 6.1 % and the drawing now reads 12.8 % in the same band,
with 15.8 % the lowest of the four.

Length is measured Euclidean from the `d` the markup ships, sampled along each
segment so a stroke that crosses a band boundary is counted in both bands in
the proportion it actually occupies. Nothing here reads the generator: the
point is to hold the PASTE, which is where a hand edit lands.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-flow-density.py       # check, exit 1 on a finding
    python3 scripts/check-flow-density.py -v    # print the band table
"""

import argparse
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = ROOT / "design-system" / "patterns"

# The drawings this governs, by the segment class that carries their geometry.
DRAWINGS = {"lp-flow": "lp-flow__seg"}

BANDS = 6
FLOOR = 10.0        # per cent of total ink, interior bands only
SAMPLES = 400       # per segment, so a band boundary splits a stroke fairly

SVG_RE = re.compile(r'<svg\b[^>]*class="([^"]*)"[^>]*viewBox="([^"]*)"(.*?)</svg>', re.S)
PATH_RE = re.compile(r'<path\b[^>]*class="([^"]*)"[^>]*\bd="([^"]*)"', re.S)
CMD_RE = re.compile(r"([MLVH])\s*(-?[\d.]+)(?:[ ,]+(-?[\d.]+))?")


def parse_path(d):
    """The four commands this drawing uses, as a list of segments."""
    segs, cur = [], None
    for cmd, a, b in CMD_RE.findall(d):
        if cmd == "M":
            cur = (float(a), float(b))
            continue
        if cmd == "L":
            nxt = (float(a), float(b))
        elif cmd == "V":
            nxt = (cur[0], float(a))
        else:
            nxt = (float(a), cur[1])
        segs.append((cur, nxt))
        cur = nxt
    return segs


def bands_of(segs, width):
    """Stroke length per band, sampled so a crossing stroke splits correctly."""
    edge = width / BANDS
    bins = [0.0] * BANDS
    total = 0.0
    for (x1, y1), (x2, y2) in segs:
        length = math.hypot(x2 - x1, y2 - y1)
        total += length
        for i in range(SAMPLES):
            x = x1 + (x2 - x1) * (i + 0.5) / SAMPLES
            bins[min(BANDS - 1, max(0, int(x // edge)))] += length / SAMPLES
    return bins, total


def check_drawing(name, cls, body, view_box, verbose):
    findings = []
    segs = []
    for classes, d in PATH_RE.findall(body):
        if cls in classes.split():
            segs += parse_path(d)
    if not segs:
        return [f"{name}: .{cls} matched no geometry — the drawing this check "
                f"reads is not in the markup any more, or its class changed"], 0

    width = float(view_box.split()[2])
    bins, total = bands_of(segs, width)
    edge = width / BANDS
    share = [b / total * 100 for b in bins]

    for i in range(1, BANDS - 1):          # interior only; the walls are exempt
        if share[i] < FLOOR:
            findings.append(
                f"{name} .{cls}: the band x {int(i * edge)}-{int((i + 1) * edge)} "
                f"carries {share[i]:.1f} % of the drawing's {total:.0f} units of "
                f"stroke, under the {FLOOR:.0f} % floor for an interior band "
                f"(an even sixth is {100 / BANDS:.1f} %). A root branches along a "
                f"straight length as well as at its bends — a band this empty is "
                f"a run with no junction on it for a branch to leave from"
            )

    if verbose:
        print(f"  {name} .{cls}: {len(segs)} segments, {total:.0f} units of stroke")
        for i, s in enumerate(share):
            wall = "  wall, exempt" if i in (0, BANDS - 1) else ""
            print(f"    x {int(i * edge):>4}-{int((i + 1) * edge):<4} {s:5.1f} % "
                  f"{'#' * int(s / 2)}{wall}")
        left = sum(share[:BANDS // 2])
        print(f"    left {left:.1f} % / right {100 - left:.1f} %")

    return findings, len(segs)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="print the band table for every drawing")
    args = parser.parse_args()

    findings, segs, drawings = [], 0, 0
    for page in sorted(PATTERNS.glob("*.html")):
        text = page.read_text(encoding="utf-8")
        for classes, view_box, body in SVG_RE.findall(text):
            for cls, seg_cls in DRAWINGS.items():
                if cls in classes.split():
                    drawings += 1
                    f, n = check_drawing(page.name, seg_cls, body, view_box,
                                         args.verbose)
                    findings += f
                    segs += n

    if not drawings:
        print("flow density: no drawing matched — this check governs "
              f"{', '.join('.' + c for c in DRAWINGS)} and found none", file=sys.stderr)
        return 1

    if findings:
        print(f"flow density: {len(findings)} finding(s)", file=sys.stderr)
        for f in findings:
            print(f"  {f}", file=sys.stderr)
        return 1

    print(f"flow density OK — {drawings} drawing(s), {segs} segments, every "
          f"interior band over the {FLOOR:.0f} % floor")
    return 0


if __name__ == "__main__":
    sys.exit(main())
