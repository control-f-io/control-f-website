#!/usr/bin/env python3
"""The field converges on the trunk's head, and that meeting is checkable.

WHAT THIS FILE USED TO HOLD, in two earlier truths. First: the trunk departs
from the rim of a drawn void — arcs at radius 84, plumb, on a shared 1200-unit
basis with the statement figure (patterns/landing-page.html, the anchor era).
Then, after the 2026-07-28 rebuild moved the chain to the prototype: the same
identities restated for a statically stacked column — field svg over .sp-root,
symmetric field, departure in the field's quietest fifth.

BOTH ARE GONE, BY REVIEW. The review of 2026-07-28 ("make the grid cover the
whole screen … the gradient dots streaming from the corners into the grid
positions and then pulsing and merging … let not bubble it so close together")
replaced the column-strip field with a full-bleed stage backdrop on its OWN
1600 x 900 basis, and inverted the old quiet-departure claim on purpose: the
field is now HOTTEST at the point the data funnels into, because the merge is
the story. The shared basis is gone too — the two svgs deliberately differ —
so the meeting point cannot be arithmetic between literals any more. It is
measured at runtime: the aim script maps the trunk's head through both screen
matrices and publishes --ux/--uy on the field.

What survives is the drawing's one load-bearing seam, restated:

  1. THE GROUND PRECEDES THE CONTENT. The stage carries the .sp-field svg
     (viewBox 0 0 1600 900, sliced) BEFORE the .container that holds .sp-root
     and the flow — the field is under the drawing it converges on, at every
     tier, including the scriptless one.

  2. EVERY SENSOR SITS ON A LATTICE CROSSING. The two diagonal families cross
     at x == 0 (mod 32), y == 8 (mod 16) — gen-proto-field.py's law — and each
     sensor's --cx/--cy equal its cx/cy, because sp-field-merge computes its
     flight FROM those custom properties: a circle whose attribute and property
     disagree flies from somewhere it is not.

  3. THE FIELD BREATHES. No two sensors stand closer than 200 units — the
     review's "let not bubble it so close together", as a number the supergrid
     guarantees (nearest neighbours hypot(128, 160) = 204.9).

  4. THE AIM IS THE SOURCE'S CENTRE AND THE DEPARTURE IS ITS RIM, one radius
     apart, plumb. This identity used to be "the aim and the departure are the
     same point", and that was true while the source was a point. It is a disc
     now — cx/cy/r on .lp-flow__orb — and the two questions came apart:

       the glows converge on where the light IS      -> the centre
       the root grows from where the light ENDS      -> the rim

     Aiming at the rim would merge twenty-five glows into the edge of a disc
     they are supposed to be filling; departing from the centre ran the
     trunk's first 34 units inside the fill, which is the one place in this
     drawing where a fill covers a contour. So both points are checked, and
     checked AGAINST THE ORB rather than against each other: the aim equals
     (cx, cy), the departure equals (cx, cy + r), and nothing is free to drift
     without the disc drifting with it. Move the trunk and forget the script,
     and the field still merges into open wash — this catches that as before.

  5. THE FALLBACK IS THE FOCUS, AND THE FOCUS IS A CROSSING. sp-field-merge's
     var(--ux, X)/var(--uy, Y) fallbacks equal gen-proto-field.py's FOCUS, so
     a scriptless render still merges into the drawing's neighbourhood, and
     the law's centre stays a point the lattice owns.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-void-departure.py
    python3 scripts/check-void-departure.py -v
"""

import argparse
import math
import re
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "design-system" / "prototypes" / "statement-to-process.html"
GEN = ROOT / "scripts" / "gen-proto-field.py"

SVG_RE = re.compile(r'<svg\b[^>]*class="([^"]*)"[^>]*viewBox="([^"]*)"(.*?)</svg>', re.S)
PATH_RE = re.compile(r'<path\b[^>]*class="([^"]*)"[^>]*\bd="([^"]*)"', re.S)
CMD_RE = re.compile(r'([MLVH])\s*(-?[\d.]+)(?:[ ,]+(-?[\d.]+))?')
# A SENSOR IS TWO ELEMENTS NOW, and the pairing is part of what this checks.
# The group carries the position and the scroll's property ledger; the bead
# inside it carries the geometry and the clock's. Matching them together means
# a bead orphaned from its group, or a group emptied of its bead, is a finding
# rather than a silently uncounted sensor.
SENSOR_RE = re.compile(
    r'<g\b[^>]*class="([^"]*)"[^>]*style="([^"]*)"\s*>\s*'
    r'<circle\b[^>]*\bcx="(-?[\d.]+)"[^>]*\bcy="(-?[\d.]+)"', re.S)
VAR_RE = re.compile(r'--(cx|cy|fx|fy|m|iso-rest):\s*(-?[\d.]+)')

FIELD = "sp-field"
SENSOR = "cf-stmt-sensor"
FLOW = "lp-flow"
FLOW_SEG = "lp-flow__seg"

# The crossings' congruences, and they follow the CELL rather than being
# chosen: gen-proto-field.py draws lines y = c +/- x/2 with c stepping by
# MODULE, so crossings fall at x == 0 (mod MODULE) and y == LINE_C0
# (mod MODULE/2). MODULE is 48 now — the system's 96 x 48 rhombus, the same
# cell .cf-ground tiles — so these are 48 / 24 / 8.
MODULE_X, MODULE_Y, PHASE_Y = 48, 24, 8
MIN_SPACING = 200                          # identity 3's bar
                                           # (nearest pair is now 221.3)


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
        description="The field converges on the trunk's head, and the meeting holds.")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    text = PAGE.read_text(encoding="utf-8")
    field_svg = flow_svg = None
    for classes, view_box, body in SVG_RE.findall(text):
        names = classes.split()
        if FIELD in names and field_svg is None:
            field_svg = (view_box, body)
        if FLOW in names and flow_svg is None:
            flow_svg = (view_box, body)

    findings = []
    if field_svg is None or flow_svg is None:
        missing = ".sp-field" if field_svg is None else ".lp-flow"
        print(f"void departure: {missing} is not on the page — the selector went stale")
        return 1

    # 1. the ground precedes the content, inside the stage
    if not re.search(
            r'<div class="sp-stage">[\s\S]*?<svg class="sp-field"[^>]*'
            r'viewBox="0 0 1600 900"[^>]*preserveAspectRatio="xMidYMid slice"'
            r'[\s\S]*?</svg>\s*<div class="container">[\s\S]*?'
            r'<div class="sp-root">[\s\S]*?lp-flow\b', text):
        findings.append(
            "the stage no longer opens with the full-bleed .sp-field svg "
            "(1600 x 900, sliced) before the container holding .sp-root — "
            "the ground is not under the drawing it converges on")

    # 2 + 3. every sensor on a crossing, with its properties telling the truth,
    #        and no two closer than the supergrid's bar
    sensors = []
    for cls, style, cx, cy in SENSOR_RE.findall(field_svg[1]):
        if SENSOR not in cls.split():
            continue
        v = dict(VAR_RE.findall(style))
        sensors.append((float(cx), float(cy), v))
    if len(sensors) < 8:
        findings.append(
            f"the field carries {len(sensors)} sensors — under any reading of "
            f"'Tausende Sensoren' the ground has gone missing")
    for x, y, v in sensors:
        if x % MODULE_X or (y - PHASE_Y) % MODULE_Y:
            findings.append(
                f"sensor at ({x:g}, {y:g}) is off the lattice crossings "
                f"(x == 0 mod {MODULE_X}, y == {PHASE_Y} mod {MODULE_Y})")
        if float(v.get("cx", "nan")) != x or float(v.get("cy", "nan")) != y:
            findings.append(
                f"sensor at ({x:g}, {y:g}) declares --cx:{v.get('cx')} "
                f"--cy:{v.get('cy')} — sp-field-merge flies it from somewhere "
                f"it is not")
        if not (v.get("m") and 0.0 <= float(v["m"]) <= 1.0):
            findings.append(
                f"sensor at ({x:g}, {y:g}) has no --m in 0..1 — its windows "
                f"in the script resolve to nonsense")
    for i, (x1, y1, _) in enumerate(sensors):
        for x2, y2, _ in sensors[i + 1:]:
            d = math.hypot(x1 - x2, y1 - y2)
            if d < MIN_SPACING:
                findings.append(
                    f"sensors at ({x1:g}, {y1:g}) and ({x2:g}, {y2:g}) stand "
                    f"{d:.1f} units apart — under the {MIN_SPACING}-unit bar the "
                    f"review set ('let not bubble it so close together')")

    # 4. the aim and the departure agree
    segs = []
    for classes, d in PATH_RE.findall(flow_svg[1]):
        if FLOW_SEG in classes.split():
            segs.extend(parse_path(d))
    if not segs:
        print(f"void departure: .{FLOW} carries no .{FLOW_SEG}")
        return 1
    dep = sorted({s[0] for s in segs}, key=lambda p: (p[1], p[0]))[0]
    orb = re.search(r'<circle\b[^>]*class="[^"]*lp-flow__orb[^"]*"[^>]*'
                    r'cx="(-?[\d.]+)"\s*cy="(-?[\d.]+)"\s*r="(-?[\d.]+)"', text)
    aim = re.search(r'new DOMPoint\((-?[\d.]+),\s*(-?[\d.]+)\)', text)
    if not orb:
        findings.append(
            "no .lp-flow__orb with cx/cy/r — the source is what both the aim "
            "and the departure are measured from")
    if not aim:
        findings.append(
            "the aim script no longer maps a DOMPoint — nothing publishes "
            "--ux/--uy and the merge runs on its fallback everywhere")
    if orb and aim:
        cx, cy, r = (rational(orb.group(i)) for i in (1, 2, 3))
        if (rational(aim.group(1)), rational(aim.group(2))) != (cx, cy):
            findings.append(
                f"the aim script maps ({aim.group(1)}, {aim.group(2)}) and the "
                f"source's centre is ({show(cx)}, {show(cy)}) — the glows "
                f"converge on a point the light is not at")
        if dep != (cx, cy + r):
            findings.append(
                f"the flow departs at ({show(dep[0])}, {show(dep[1])}) and the "
                f"source's rim is ({show(cx)}, {show(cy + r)}) — the trunk "
                f"either starts inside the fill or hangs off it")

    # 5. the fallback is the focus, and the focus is a crossing
    fb = re.search(r'var\(--ux,\s*(-?[\d.]+)\)[\s\S]{0,120}?var\(--uy,\s*(-?[\d.]+)\)', text)
    focus = re.search(r'FOCUS\s*=\s*\((-?[\d.]+),\s*(-?[\d.]+)\)', GEN.read_text(encoding="utf-8"))
    if not fb:
        findings.append("sp-field-merge no longer carries --ux/--uy fallbacks — "
                        "a scriptless render merges into nothing at all")
    elif not focus:
        findings.append("gen-proto-field.py no longer states FOCUS — identity 5 "
                        "has nothing to compare against")
    else:
        fx, fy = float(fb.group(1)), float(fb.group(2))
        gx, gy = float(focus.group(1)), float(focus.group(2))
        if (fx, fy) != (gx, gy):
            findings.append(
                f"the merge fallback is ({fx:g}, {fy:g}) and the generator's "
                f"FOCUS is ({gx:g}, {gy:g}) — the scriptless merge and the "
                f"field's law no longer share a centre")
        if fx % MODULE_X or (fy - PHASE_Y) % MODULE_Y:
            findings.append(
                f"the focus ({fx:g}, {fy:g}) is off the lattice crossings — "
                f"the law's centre is a point the lattice does not own")

    if args.verbose:
        dmin = min((math.hypot(a[0] - b[0], a[1] - b[1])
                    for i, a in enumerate(sensors) for b in sensors[i + 1:]),
                   default=float("inf"))
        print(f"  sensors            {len(sensors)}   nearest pair {dmin:.1f} units")
        print(f"  trunk departure    ({show(dep[0])}, {show(dep[1])})")
        print(f"  aim script maps    {aim.group(0) if aim else '—'}")
        print(f"  merge fallback     ({fb.group(1)}, {fb.group(2)})" if fb else "  merge fallback     —")

    if findings:
        print(f"\nvoid departure: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1
    print(f"void departure OK — {len(sensors)} sensors on crossings, none under "
          f"{MIN_SPACING} units apart, aimed at the source's centre and departing "
          f"from its rim ({show(dep[0])}, {show(dep[1])}), with the generator's "
          f"focus as the fallback")
    return 0


if __name__ == "__main__":
    sys.exit(main())
