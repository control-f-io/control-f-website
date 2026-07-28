#!/usr/bin/env python3
"""A stroke grows out of a point that is already there.

THE FAILURE THIS IS WRITTEN AGAINST is not hypothetical and was not subtle once
it was measured. The flow's forty-two strokes were staggered by depth — every
window `a + c·l` over a FLAT WIDTH of seventeen points, from the 240-unit
taproot to the 25-unit twig — so the gap between a stroke and its child was c
times the parent's own extent, 0.75 to 3.95 points, against seventeen points of
drawing. Every one of the forty-one junctions therefore ignited its child while
the parent was between 4.4 % and 23.2 % drawn, mean 12.1 %, with no easing to
soften it because this family scrubs linear. On the render at 1440 x 900: at
y 754 the trunk was a 4 px stub under the void and the fork it feeds was already
carrying ink 130 px below it, two arms hanging in the wash joined to nothing.

In a construction drawing that is a claim, not a nicety. check-flow-crossings.py
exists because two lines meeting with nothing on the meeting means NOT CONNECTED
— and a stroke leaving a point its own parent has not reached is the same
sentence in the time axis, made forty-one times, in the one drawing whose whole
subject is data merging. #190 and #191 are the same finding about the frame.

THE CURE IS THE ONE #201 APPLIED TO THE FRAME: the window is bought by the
stroke's own run. --l is the distance from the void to where a stroke starts, in
the drawing's own units over its longest such distance, times three; --u is what
that stroke adds to it. Every window is `head + l·c` to `head + (l + u)·c`, so a
stroke's window CLOSES on the point its children's windows OPEN on — by
arithmetic, not by tuning. One front travels the root and the strokes are where
it happens to be.

WHAT IS HELD HERE, and each of the five is a way the arithmetic can rot:

  1. --u IS THE GEOMETRY IT CLAIMS. Walked off the shipped `d`, Chebyshev, the
     way gen-flow-root.py accumulates it. Measure the run Euclidean instead and
     the chain drifts 41 % on every 45° stroke while every number in the file
     still looks right.

  2. THE CHAIN CLOSES, exactly, in the two decimal places that ship: parent --l
     + parent --u == child --l at all forty-one junctions. It is exact because
     the generator emits --u as the DIFFERENCE OF TWO ROUNDED LEVELS rather than
     as its own rounding of the geometry; round the two ends independently and
     twenty of the forty-one are a hundredth out, which is a whole fringe
     stroke's stagger.

  3. THE TWO PASSES AGREE. The light and the contour are one drawing drawn
     twice; a --u that moved on one of them is a head that outruns its own black
     on one route and lags on another.

  4. THE SPEED IS SINGLE-SOURCED. Every `cover` window on the flow's four
     families is written off --flow-c, which is declared exactly once. A typed
     constant that creeps back into one rule is how the family drifts apart.

  5. THE TWO TAILS THE SEAM AND THE LIGHT ARE MEASURED AT. The contour lands at
     cover 66, where the frame's relay is written to take over, and the light's
     fade ends at 68, which is the number Standing Order 2's clearance was swept
     at: the last lit flow stroke is 810 to 1650 px of scroll before card 01's
     lime at contain 11.5 % of its quarter, at every viewport the gate admits.
     That sweep needs a browser and this script does not have one — so what it
     holds is the pair of authored numbers the sweep was taken at. Move either
     and this fails, which is the point: the clearance may be re-measured, but it
     may not be silently invalidated. → foundations/colors.html#one-per-screen.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-flow-chain.py
"""

import argparse
import re
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANDING = ROOT / "design-system/patterns/landing-page.html"

# The two tails every measured number at this seam was taken at.
CONTOUR_LANDS = 66.0        # the frame's relay takes over here
FADE_ENDS = 68.0            # the light is out here, and the lime sweep says so
CARD_LIME = 11.5            # contain %, card 01's fill-opacity leaving 0
TOL = 0.02                  # two decimal places, plus the rounding under them

# The class list is open-ended because #206 put a second class on the trunk:
# .lp-flow__trunk, the in-drawing copy that the tall-box tier hides in favour of
# .lp-flow__stem. Anchoring on a closing quote would drop that stroke from every
# count below — and it is the one stroke the whole walk starts from.
STROKE = re.compile(
    r'class="lp-flow__(seg|light)([^"]*)" style="--o:([^;]+);--l:([\d.]+);--u:([\d.]+)"'
    r'[^>]*?\sd="([^"]+)"')

# THE STEM IS THE TRUNK, DRAWN IN A BOX THAT IS NOT THE DRAWING'S. #206 moved
# the trunk out of the <svg> wherever the flow's box is taller than its own
# units, into a 12 x 100 sliver with preserveAspectRatio="none" — "the same one
# stroke as .lp-flow__trunk above and never drawn at the same time as it". Its
# geometry is therefore not on the root's coordinate system and cannot be walked
# with it, but its TIMING has to be the trunk's exactly, or the two tiers open
# the drawing at different moments. That is what is checked instead.
STEM_D = "M6 0V100"
PATH_D = re.compile(r"M([\d.]+) ([\d.]+)(?:([HVL])([\d.]+)(?: ([\d.]+))?)$")


def endpoints(d):
    m = PATH_D.match(d)
    if m is None:
        return None
    x0, y0 = F(m.group(1)), F(m.group(2))
    cmd = m.group(3)
    if cmd == "V":
        return x0, y0, x0, F(m.group(4))
    if cmd == "H":
        return x0, y0, F(m.group(4)), y0
    return x0, y0, F(m.group(4)), F(m.group(5))


def read(text, kind):
    """Every stroke of one pass, with the end it grows from worked out."""
    out = []
    for m in STROKE.finditer(text):
        if m.group(1) != kind:
            continue
        o, l, u, d = m.group(3), float(m.group(4)), float(m.group(5)), m.group(6)
        if d == STEM_D:
            continue                       # not on the root's units; held below
        pts = endpoints(d)
        if pts is None:
            return None, f"a .lp-flow__{kind} has a `d` this check cannot read: {d!r}"
        x0, y0, x1, y1 = pts
        xs, ys = sorted((x0, x1)), sorted((y0, y1))
        # --o is a transform-origin in the path's own fill-box, so it names a
        # CORNER of the bounding box and not an endpoint of the `d`. On a
        # straight stroke the two coincide; reading it as "the first point" is
        # wrong for exactly the half of them written right-to-left.
        parts = o.split()
        ox = xs[0] if parts[0] == "0" else xs[1]
        oy = ys[0] if parts[1] == "0" else ys[1]
        origin = (ox, oy)
        tip = (x1, y1) if (x0, y0) == origin else (x0, y0)
        out.append(dict(l=l, u=u, d=d, origin=origin, tip=tip,
                        step=max(abs(x1 - x0), abs(y1 - y0))))
    return out, None


def walk(segs):
    """The run from the void to every stroke's start, Chebyshev, exact."""
    by_origin = {}
    for s in segs:
        by_origin.setdefault(s["origin"], []).append(s)
    roots = [s for s in segs
             if not any(q is not s and q["tip"] == s["origin"] for q in segs)]
    if len(roots) != 1:
        return f"the root has {len(roots)} strokes with no parent; a root has one trunk"
    roots[0]["run"] = F(0)
    stack = [roots[0]]
    while stack:
        q = stack.pop()
        q["run_end"] = q["run"] + q["step"]
        for c in by_origin.get(q["tip"], []):
            if c is q or "run" in c:
                continue
            c["run"] = q["run_end"]
            stack.append(c)
    missing = [s["d"] for s in segs if "run" not in s]
    if missing:
        return f"{len(missing)} strokes are not reachable from the trunk: {missing[:3]}"
    return None


def cover_tail(body, const, l_plus_u):
    """The last `cover` position a family's window resolves to."""
    tails = []
    for m in re.finditer(
            r"cover\s+calc\(\(\s*([\d.]+)\s*\+\s*"
            r"(?:var\(--l\)|\(\s*var\(--l\)\s*\+\s*var\(--u\)\s*\))"
            r"\s*\*\s*var\(--flow-c\)\s*\)\s*\*\s*1%\)", body):
        on_u = "--u" in m.group(0)
        tails.append(float(m.group(1)) + const * (l_plus_u if on_u else 0))
    return tails


def rule_body(text, selector):
    body = None
    for m in re.finditer(re.escape(selector) + r"\s*\{([^}]*)\}", text):
        body = m.group(1)
    return body


def main():
    ap = argparse.ArgumentParser(
        description="A stroke grows out of a point that is already there.")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    text = LANDING.read_text(encoding="utf-8")
    findings = []

    segs, err = read(text, "seg")
    lights, err2 = read(text, "light")
    for e in (err, err2):
        if e:
            findings.append(e)
    if findings or not segs:
        if not segs and not findings:
            findings.append("no .lp-flow__seg carries both --l and --u — the pair went stale")
        return report(findings, args.verbose, None)

    # ---- 1. --u is the geometry it claims -------------------------------
    err = walk(segs)
    if err:
        findings.append(err)
        return report(findings, args.verbose, None)
    maxd = max(s["run"] for s in segs)

    def level(d):
        return round(float(3 * F(d) / maxd), 2)

    for s in segs:
        want_l, want_u = level(s["run"]), round(level(s["run_end"]) - level(s["run"]), 2)
        if abs(s["l"] - want_l) > 1e-9:
            findings.append(
                f"{s['d']}: --l is {s['l']}, but its run from the void is "
                f"{s['run']} of {maxd}, which is {want_l}")
        if abs(s["u"] - want_u) > 1e-9:
            findings.append(
                f"{s['d']}: --u is {s['u']}, but the stroke's own run is "
                f"{s['step']} units, which is {want_u} of the drawing's depth")

    # ---- 2. the chain closes --------------------------------------------
    junctions = 0
    for c in segs:
        for p in segs:
            if p is c or p["tip"] != c["origin"]:
                continue
            junctions += 1
            if abs((p["l"] + p["u"]) - c["l"]) > 1e-9:
                findings.append(
                    f"{c['d']} opens at l {c['l']} but {p['d']} closes at "
                    f"{p['l'] + p['u']:.2f} — the branch grows out of a point the "
                    f"stroke that feeds it has not reached")
    if junctions != len(segs) - 1:
        findings.append(
            f"{junctions} junctions for {len(segs)} strokes; a tree has one fewer "
            f"junction than it has strokes")

    # ---- 3a. the stem opens the drawing at the trunk's moment -----------
    trunk = min(segs, key=lambda s: (s["l"], s["u"]))
    stems = [(m.group(1), float(m.group(4)), float(m.group(5)))
             for m in STROKE.finditer(text) if m.group(6) == STEM_D]
    if len(stems) != 2:
        findings.append(
            f"{len(stems)} strokes on .lp-flow__stem, not the light-then-contour "
            f"pair the tall-box tier draws the trunk as")
    for kind, l, u in stems:
        if (l, u) != (trunk["l"], trunk["u"]):
            findings.append(
                f"the stem's {kind} runs l {l} u {u} and the trunk it stands in for "
                f"runs l {trunk['l']} u {trunk['u']} — the two tiers would open the "
                f"drawing at different moments")

    # ---- 3. the two passes agree ----------------------------------------
    seg_by_d = {s["d"]: s for s in segs}
    if len(lights) != len(segs):
        findings.append(f"{len(lights)} light strokes against {len(segs)} contours — "
                        f"one drawing, drawn twice")
    for g in lights:
        s = seg_by_d.get(g["d"])
        if s is None:
            findings.append(f"the light draws {g['d']}, which no contour draws")
        elif (g["l"], g["u"]) != (s["l"], s["u"]):
            findings.append(
                f"{g['d']}: the light runs l {g['l']} u {g['u']} and the contour "
                f"l {s['l']} u {s['u']} — the head would outrun its own black on "
                f"one route and lag on another")

    # ---- 4. the speed is single-sourced ---------------------------------
    decls = re.findall(r"--flow-c:\s*([\d.]+)\s*;", text)
    if len(decls) != 1:
        findings.append(
            f"--flow-c is declared {len(decls)} times; the root has one drawing speed")
        const = float(decls[0]) if decls else 0.0
    else:
        const = float(decls[0])

    families = {".lp-flow__seg": "the contour", ".lp-flow__light": "the light",
                ".lp-flow__node": "the junctions", ".lp-flow__val": "the numerals"}
    for selector, label in families.items():
        body = rule_body(text, selector)
        if body is None:
            findings.append(f"no rule for `{selector}` — the selector went stale")
            continue
        decl = re.search(r"animation-range:([^;]*);", body)
        if not decl:
            findings.append(f"`{selector}` has no animation-range")
            continue
        typed = {m.group(1) for m in re.finditer(r"var\(--l\)\s*\*\s*([\d.]+)", decl.group(1))}
        for value in sorted(typed):
            findings.append(
                f"`{selector}` staggers on a typed {value} instead of on "
                f"--flow-c — the four families drift apart one rule at a time")

    # ---- 5. the two tails the measurements were taken at -----------------
    lu = max(round(s["l"] + s["u"], 2) for s in segs)
    seg_body = rule_body(text, ".lp-flow__seg") or ""
    light_body = rule_body(text, ".lp-flow__light") or ""
    tails = cover_tail(seg_body, const, lu)
    contour = round(max(tails), 2) if tails else None
    tails = cover_tail(light_body, const, lu)
    fade = round(max(tails), 2) if tails else None
    if contour is None or abs(contour - CONTOUR_LANDS) > TOL:
        findings.append(
            f"the contour's window does not resolve to cover {CONTOUR_LANDS} "
            f"(it reads {contour}) — the frame's "
            f"relay is written to take over there (check-flow-handover.py has the seam)")
    if fade is None or abs(fade - FADE_ENDS) > TOL:
        findings.append(
            f"the light's fade ends at cover {fade}, not {FADE_ENDS} — that is the "
            f"number the one-lit-element clearance was swept at; re-sweep it before "
            f"moving it (foundations/colors.html#one-per-screen)")
    # The other end of the clearance is the pinned card's own light, and its
    # rule carries TWO animation-ranges: the fill, which is the lime, and the
    # build the part shares with its stage-mates. Only the first is this
    # number — searching the whole file for the shape finds four other rules'
    # quarters first and reports whichever one it hits.
    lit = rule_body(text, ".lp-proc-steps .cf-iso__light") or ""
    lime = re.search(r"animation-range:\s*contain calc\(var\(--i\) \* 25% \+ ([\d.]+)%\)", lit)
    if lime is None or abs(float(lime.group(1)) - CARD_LIME) > TOL:
        findings.append(
            f"card 01's lime no longer opens at contain {CARD_LIME} % of its quarter — "
            f"that is the other end of the same clearance")

    return report(findings, args.verbose,
                  (len(segs), junctions, const, lu, contour, fade))


def report(findings, verbose, stats):
    if verbose and stats:
        n, j, c, lu, contour, fade = stats
        print(f"flow chain: {n} strokes, {j} junctions, --flow-c {c} points per unit of --l")
        print(f"  deepest terminal at l + u = {lu:.2f}")
        print(f"  contour lands cover {contour:.2f} · light's fade ends cover {fade:.2f}")
    if findings:
        print(f"flow chain: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1
    if stats:
        print(f"flow chain OK — {stats[1]} junctions, every stroke opening exactly where "
              f"the one that feeds it closes; both tails on the numbers the seam and the "
              f"light are measured at")
    return 0


if __name__ == "__main__":
    sys.exit(main())
