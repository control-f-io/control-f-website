#!/usr/bin/env python3
"""A census is checked by adding it up, and this one added up.

The sixty-eighth check, and the sixth about the statement-to-process root's own
geometry. The five before it hold where the root's strokes go. This one holds
what the page SAYS about where they go — because the drawing states its own
angle distribution, in prose, in the paragraph directly above the paths, and two
of that sentence's four cells were wrong.

    "these forty-two begin at twenty-seven different junctions. Each axis is
     its own stroke's line, which is how the gradient's angle is a brand angle
     without anything here typing one — 16 at 45, 16 at 63.43, 7 at 26.57 and
     3 vertical"

Measured on the paste that sentence sat above: 14 at 45, 16 at 63.43, 7 at 26.57
and 5 vertical. Two cells out by two, in opposite directions, so the total came
to forty-two and the sentence read as arithmetic that works. That is exactly why
it survived however many passes: a reader checks a census by adding it up.

WHAT THE ERROR ACTUALLY SAID. 45deg is not a spare angle in this system — it is
the fringe's other leg, the one a grown branch alternates onto, and 26.57 is the
only angle that crosses width cheaply, which is why the taproots are made of it.
The published census had two of the drawing's 45deg strokes counted as
VERTICALS. In the one place this drawing states how its five angles are spent,
it moved two strokes off the diagonal that carries the fringe and onto the angle
that carries nothing but the last drop to the rail. Daniel's brief asks for a
drawing that is "not random but mathematically correct based on the ratios and
winkel in the design system"; the winkel were correct and their published
account of themselves was not.

AND THE SENTENCE'S REAL CLAIM WAS HELD BY NOTHING AT ALL, which is the larger
half of this. "Each axis is its own stroke's line, which is how the gradient's
angle is a brand angle without anything here typing one" is a geometric
assertion about forty-one linearGradient defs, and the argument offered for it
is "they are emitted by the same generator as the paths". That is the argument
every drift in this repository has been made against — gen-flow-root.py cannot
see a coordinate typed into patterns/landing-page.html afterwards. An axis that
comes adrift from its stroke does not fail any existing check: the ramp still
resolves, the stops are still #lp-flow-ramp's, check-gradient-family.py still
passes, and the stroke simply lights along the wrong line. On a scale-draw that
is invisible in a diff and nearly invisible on the page, because a gradient at a
slightly wrong angle still looks like a gradient.

WHAT IS HELD, and each is a way this can rot:

  1. ONE AXIS PER STROKE. The count of lp-flow-ax-NN defs equals the count of
     .lp-flow__seg paths, and every .lp-flow__light references a distinct one.
     A shared axis is how the frame's strokes are done and is wrong here: the
     frame's five all begin at a coordinate origin and the root's forty-one
     begin at twenty-six different junctions.

  2. THE AXIS IS ITS STROKE'S LINE, FAR END BACK TO ORIGIN. Exactly: the def's
     (x1, y1) is the path's second point and its (x2, y2) is the path's first.
     The direction is not decoration — a userSpaceOnUse gradient resolves in the
     element's own user space, so the scale-draw carries the ramp with it and
     whatever colour sits at the path's far end sits at the growing tip at every
     scale. Reverse one axis and that stroke grows grey-tipped into lime, alone
     among forty-one.

  3. THEREFORE EVERY AXIS IS ON A BRAND ANGLE, recomputed from the def's own
     four numbers rather than inferred from (2), because that is the sentence
     the page publishes: 0, 26.57, 45, 63.43 or 90 degrees
     (foundations/geometry.html#angles).

  4. THE PUBLISHED CENSUS IS THE MEASURED CENSUS. All four cells, the total and
     the junction count, parsed out of the prose and recomputed from the defs.
     Every number the paragraph states, and no number it does not.

WHAT THIS DOES NOT HOLD. It says nothing about which junctions shed a branch —
that set is still nine coordinate pairs typed into gen-flow-root.py, with a
hand-picked depth seed and side each, and the one-sentence rule its comment
gives for them ("junctions in the lower half only") is false of the table in
both directions. See the audit in the pull request this ships with; it is the
next thing in this lane, not this thing.
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

SVG_RE = re.compile(r'<svg\b[^>]*class="([^"]*)"[^>]*>(.*?)</svg>', re.S)
GRAD_RE = re.compile(
    r'<linearGradient\b[^>]*id="(lp-flow-ax-\d+)"[^>]*'
    r'x1="(-?[\d.]+)"\s*y1="(-?[\d.]+)"\s*x2="(-?[\d.]+)"\s*y2="(-?[\d.]+)"'
)
LIGHT_RE = re.compile(
    r'<path\b[^>]*class="[^"]*lp-flow__light[^"]*"[^>]*'
    r'stroke="url\(#(lp-flow-ax-\d+)\)"[^>]*\bd="([^"]*)"'
)
SEG_RE = re.compile(r'<path\b[^>]*class="[^"]*lp-flow__seg[^"]*"[^>]*\bd="([^"]*)"')
D_RE = re.compile(
    r'^M(-?[\d.]+)[ ,](-?[\d.]+)'
    r'(?:L(-?[\d.]+)[ ,](-?[\d.]+)|V(-?[\d.]+)|H(-?[\d.]+))$'
)

# The paragraph's own sentence, anchored on the clause before it so the
# historical quote further down — which states the WRONG census on purpose —
# cannot be the one that matches.
CENSUS_RE = re.compile(
    r"is a brand angle without anything here typing one\s*[—-]\s*"
    r"(\d+)\s*at\s*45,\s*(\d+)\s*at\s*63\.43,\s*"
    r"(\d+)\s*at\s*26\.57\s*and\s*(\d+)\s*vertical"
)
TOTAL_RE = re.compile(r"ONE RAMP,\s*([A-Za-z-]+)\s*AXES")
JUNCTIONS_RE = re.compile(r"these\s+([a-z-]+)\s+begin at\s+([a-z-]+)\s+different junctions")

UNITS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
    "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
    "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
    "eighty": 80, "ninety": 90,
}

# foundations/geometry.html#angles, and the only five this drawing may use.
BRAND = {0.0, 26.57, 45.0, 63.43, 90.0}


def spelled(word):
    """"forty-one" -> 41. Returns None for anything not a plain numeral."""
    total = 0
    for part in word.lower().split("-"):
        if part not in UNITS:
            return None
        total += UNITS[part]
    return total


def endpoints(d):
    """The two ends of a one-command path, exactly, as Fractions."""
    m = D_RE.match(d.strip())
    if not m:
        return None
    x1, y1 = Fraction(m.group(1)), Fraction(m.group(2))
    if m.group(3) is not None:
        return x1, y1, Fraction(m.group(3)), Fraction(m.group(4))
    if m.group(5) is not None:
        return x1, y1, x1, Fraction(m.group(5))
    return x1, y1, Fraction(m.group(6)), y1


def angle(x1, y1, x2, y2):
    dx, dy = abs(x2 - x1), abs(y2 - y1)
    if dx == 0 and dy == 0:
        return None
    if dx == 0:
        return 90.0
    if dy == 0:
        return 0.0
    return round(math.degrees(math.atan(float(dy) / float(dx))), 2)


def flow_svg(text):
    """The .lp-flow drawing's own markup — not .lp-flow__stem, a sibling svg."""
    for cls, body in SVG_RE.findall(text):
        if "lp-flow" in cls.split() :
            return body
    return None


def check(path, verbose):
    name = path.name
    text = path.read_text(encoding="utf-8")
    body = flow_svg(text)
    if body is None:
        return [], None
    findings = []

    axes = {}
    for gid, x1, y1, x2, y2 in GRAD_RE.findall(body):
        axes[gid] = (Fraction(x1), Fraction(y1), Fraction(x2), Fraction(y2))
    segs = [d for d in SEG_RE.findall(body)]
    lights = LIGHT_RE.findall(body)

    # ---- 1. one axis per stroke ------------------------------------------
    if len(axes) != len(segs):
        findings.append(
            f"{name}: {len(segs)} strokes and {len(axes)} axes — the paragraph "
            f"says one axis per stroke, and a shared axis lights two strokes "
            f"along one line")
    if len(lights) != len(segs):
        findings.append(
            f"{name}: {len(segs)} contour strokes but {len(lights)} lit ones "
            f"carry an axis reference")
    seen = {}
    for gid, _ in lights:
        seen[gid] = seen.get(gid, 0) + 1
    for gid, n in sorted(seen.items()):
        if n > 1:
            findings.append(f"{name}: {n} strokes share the axis #{gid}")
    for gid, _ in lights:
        if gid not in axes:
            findings.append(f"{name}: a stroke references #{gid}, which is not defined")

    # ---- 2. the axis is its stroke's line, far end back to origin ---------
    for gid, d in lights:
        if gid not in axes:
            continue
        pts = endpoints(d)
        if pts is None:
            findings.append(f"{name}: the stroke on #{gid} has a `d` this cannot read: {d}")
            continue
        px1, py1, px2, py2 = pts
        want = (px2, py2, px1, py1)
        if axes[gid] != want:
            ax1, ay1, ax2, ay2 = axes[gid]
            reversed_ = axes[gid] == (px1, py1, px2, py2)
            why = ("it runs origin -> far end, so this stroke alone grows "
                   "grey-tipped into lime" if reversed_ else
                   "it is not this stroke's line at all")
            findings.append(
                f"{name}: axis #{gid} is ({ax1}, {ay1}) -> ({ax2}, {ay2}) but its "
                f"stroke is ({px1}, {py1}) -> ({px2}, {py2}); the axis must be the "
                f"stroke far end back to origin — {why}")

    # ---- 3. every axis on a brand angle ----------------------------------
    census = {45.0: 0, 63.43: 0, 26.57: 0, 90.0: 0}
    strays = []
    for gid in sorted(axes):
        a = angle(*axes[gid])
        if a is None or a not in BRAND:
            strays.append((gid, a))
            continue
        census[a] = census.get(a, 0) + 1
    for gid, a in strays:
        findings.append(
            f"{name}: axis #{gid} lies at {a} degrees, which is not one of the five "
            f"foundations/geometry.html publishes (0, 26.57, 45, 63.43, 90)")

    # ---- 4. the published census is the measured census -------------------
    prose = " ".join(text.split())
    junctions = len({endpoints(d)[:2] for d in segs if endpoints(d)})

    m = CENSUS_RE.search(prose)
    if not m:
        findings.append(
            f"{name}: the paragraph above the paths no longer states its angle "
            f"census in the form this reads — restate it or this check is blind")
    else:
        stated = {45.0: int(m.group(1)), 63.43: int(m.group(2)),
                  26.57: int(m.group(3)), 90.0: int(m.group(4))}
        for a in (45.0, 63.43, 26.57, 90.0):
            if stated[a] != census.get(a, 0):
                findings.append(
                    f"{name}: the paragraph says {stated[a]} axes at {a} degrees and "
                    f"there are {census.get(a, 0)} — a typed census is checked by "
                    f"adding it up, so a cell can be wrong while the total is right")

    m = TOTAL_RE.search(prose)
    if not m or spelled(m.group(1)) is None:
        findings.append(f"{name}: 'ONE RAMP, <n> AXES' no longer states a number")
    elif spelled(m.group(1)) != len(axes):
        findings.append(
            f"{name}: the paragraph heads itself 'ONE RAMP, {m.group(1).upper()} AXES' "
            f"and there are {len(axes)}")

    m = JUNCTIONS_RE.search(prose)
    if not m or spelled(m.group(1)) is None or spelled(m.group(2)) is None:
        findings.append(
            f"{name}: 'these <n> begin at <m> different junctions' no longer states "
            f"two numbers")
    else:
        if spelled(m.group(1)) != len(axes):
            findings.append(
                f"{name}: the paragraph says 'these {m.group(1)}' of {len(axes)} axes")
        if spelled(m.group(2)) != junctions:
            findings.append(
                f"{name}: the paragraph says the strokes begin at {m.group(2)} "
                f"different junctions and they begin at {junctions}")

    stats = (len(axes), junctions, census)
    if verbose:
        print(f"  {name} .lp-flow: {len(segs)} strokes, {len(axes)} axes, "
              f"{junctions} distinct junctions")
        for a in (0.0, 26.57, 45.0, 63.43, 90.0):
            if census.get(a):
                print(f"    {census[a]:>3} at {a}")
    return findings, stats


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    findings, stats = [], None
    for path in sorted([*PATTERNS.glob("*.html"), *PROTOTYPES.glob("*.html")]):
        f, s = check(path, args.verbose)
        findings += f
        stats = s or stats

    if findings:
        print(f"flow axes: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1
    if stats is None:
        print("flow axes: .lp-flow carries no axes at all")
        return 1
    n, junctions, census = stats
    print(f"flow axes OK — {n} axes, one per stroke, each its own stroke's line far "
          f"end back to origin, from {junctions} junctions; the published census "
          f"({census[45.0]} at 45, {census[63.43]} at 63.43, {census[26.57]} at 26.57, "
          f"{census[90.0]} vertical) is the measured one")
    return 0


if __name__ == "__main__":
    sys.exit(main())
