#!/usr/bin/env python3
"""A stroke grows out of a point that is already there.

THE FAILURE THIS IS WRITTEN AGAINST is not hypothetical and was not subtle once
it was measured. The flow's forty-one strokes were staggered by depth — every
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

  4. EACH TIER'S SPEED IS SINGLE-SOURCED, AND EVERY FAMILY IS IN BOTH. The root
     is drawn by two tiers now — the pinned stage above (min-width: 64rem) and
     (min-height: 45rem), and the flow tier under it, where the drawing is its
     own timeline subject — and they cannot share a rate. The stage gives the
     act 4 860 px of `contain` at 1440 x 900; the flow tier gives it the 665 px
     the drawing is on screen for at 390 x 844. So there are two rates,
     --flow-c and --flow-cf, each declared exactly once, and every window in a
     tier is written off that tier's own. A typed constant that creeps back
     into one rule is how the family drifts apart; a family whose rule exists
     in one tier and not the other is how a phone quietly stops drawing the
     junctions while every number in the file still looks right.

  5. THE TAILS THE SEAM AND THE LIGHT ARE MEASURED AT, per tier. In the pinned
     stage the contour lands at contain 86.88, where the frame's relay is
     written to take over, and the light's fade ends at 88.88, which is the
     number Standing Order 2's clearance was swept at: the last lit flow stroke
     is 810 to 1650 px of scroll before card 01's lime at contain 11.5 % of its
     quarter, at every viewport the gate admits. That sweep needs a browser and
     this script does not have one — so what it holds is the pair of authored
     numbers the sweep was taken at. Move either and this fails, which is the
     point: the clearance may be re-measured, but it may not be silently
     invalidated. → foundations/colors.html#one-per-screen.

     The flow tier's pair is 84 and 88 of its own window, and what they owe is
     narrower because there is no relay and no card under it: they have to land
     inside the 100 the drawing is on screen for, and the light has to be out
     AFTER its own black rather than before it. Both tiers are held to that
     last one, which is the sentence the whole chain is about — the front
     leads, the contour follows.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-flow-chain.py
"""

import argparse
import re
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANDING = ROOT / "design-system/prototypes/statement-to-process.html"

# ---------------------------------------------------------------- the page CSS
#
# A PAGE RESOLVES ITS LINKED STYLESHEETS AND ITS OWN <style>, IN THAT ORDER, and
# this check has to read what the page resolves rather than what it happens to
# declare inline. The five acts lived in one prototype's <style> block until they
# became assets/css/acts.css — two thousand lines cannot stay page-local once a
# second page wants them — and every check that read only the <style> went blind
# at that moment. Following the page's own <link> tags means the next stylesheet
# needs no edit here at all.
def page_stylesheets(path):
    html = path.read_text(encoding="utf-8")
    out = []
    for m in re.finditer(r'<link[^>]+href="([^"]*assets/css/[^"]+\.css)"', html):
        sheet = (path.parent / m.group(1)).resolve()
        if sheet.exists():
            out.append(sheet.read_text(encoding="utf-8"))
    out += re.findall(r"<style[^>]*>(.*?)</style>", html, re.S)
    return "\n".join(out)



# THE TAILS ARE RECORDED, NOT NAILED, since the 2026-07-28 rebuild. The old
# truth: the contour had to land at cover 66 because the frame's relay took
# over there, and the light had to be out by 68 where the lime clearance was
# swept — one drawing stretched between two sections by an anchor chain. The
# rebuild put acts 1+2 on their own sticky stage; the stage RELEASES before
# the cards' pin begins, so the relay coupling is gone by construction. What
# the tails still owe: they resolve inside the track (< 100), the light leads
# the contour, and these recorded values move only on purpose.
# RE-RECORDED FOR THE BALANCED TREE (2026-07-28, second review). The grown
# root's longest walk was l+u = 3.0805 on c = 13: contour landed 82.05, fade
# ended 84.05. The balanced construction's longest walk is the dive strokes'
# l+u = 3.74, and c came down to 12 so the landing stays inside the act:
# 42 + 3.74 * 12 = 86.88, fade two points of head behind at 88.88 — still
# before the 89 the page's script gives the closing still.
# AND THERE ARE TWO TIERS OF THEM NOW, one rate each. The pinned stage buys
# the root 53 points of a 640vh track; the flow tier under the gate has no
# stage, so the drawing is its own timeline subject and the whole act plays
# across the `contain` window in which the tree is on screen — 665 px at
# 390 x 844 against the stage's 5760. Same algebra, same order, same chain;
# one number for how many points a unit of --l is worth, and it cannot be the
# same number. Both are recorded here, both move only on purpose, and every
# window in a tier has to be written off that tier's own rate.
TIERS = {
    # rate          the tier it drives      contour lands   the light is out
    "--flow-c":  dict(label="the pinned stage", contour=86.88, fade=88.88),
    "--flow-cf": dict(label="the flow tier",    contour=84.00, fade=88.00),
}
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
    """The run from the SOURCE to every stroke's ends, Chebyshev, exact.

    A CONFLUENCE HAS MANY MOUTHS AND ONE SOURCE, and the walk starts at the one
    rather than the many. That is not the direction the strokes grow — the
    review of 2026-07-29 turned the drawing over, so --o names the fringe end
    and every stroke grows inward — but it is the direction the RUN is measured
    in, and the two have to be told apart.

    The drawing's motion claim is that ONE front travels the root at ONE speed
    and the strokes are where it happens to be. There is exactly one quantity
    that can say where a front at one speed has got to, and it is distance from
    a single point. The fringe is nineteen points at nineteen different depths;
    measuring from there gives every route its own clock, and a stroke on a
    short branch would then open at the same instant as one on a long branch
    that is twice as far from the source. So the run is measured from the
    source outward, exactly as it was when the source was at the top, and the
    LEVEL is what got reversed: level = 3 x (SPAN - run) / SPAN, so the deepest
    tip is 0 and the trunk's near end is 3.

    Walking outward means following tips to origins — a stroke's children are
    the strokes whose TIP is its ORIGIN — because the markup still writes every
    stroke trunk end first.
    """
    by_tip = {}
    for s in segs:
        by_tip.setdefault(s["tip"], []).append(s)
    mouths = [s for s in segs
              if not any(q is not s and q["origin"] == s["tip"] for q in segs)]
    if len(mouths) != 1:
        return (f"the root has {len(mouths)} strokes with nothing below them; "
                f"a confluence has one trunk, into the source")
    mouths[0]["run"] = F(0)
    stack = [mouths[0]]
    while stack:
        q = stack.pop()
        q["run_end"] = q["run"] + q["step"]
        for c in by_tip.get(q["origin"], []):
            if c is q or "run" in c:
                continue
            c["run"] = q["run_end"]
            stack.append(c)
    missing = [s["d"] for s in segs if "run" not in s]
    if missing:
        return f"{len(missing)} strokes are not reachable from the source: {missing[:3]}"
    return None


def cover_tail(body, rate, const, l_plus_u):
    """The last `cover`/`contain` position a family's window resolves to."""
    tails = []
    for m in re.finditer(
            r"(?:cover|contain)\s+calc\(\(\s*([\d.]+)\s*\+\s*"
            r"(?:var\(--l\)|\(\s*var\(--l\)\s*\+\s*var\(--u\)\s*\))"
            r"\s*\*\s*var\(" + re.escape(rate) + r"\)\s*\)\s*\*\s*1%\)", body):
        on_u = "--u" in m.group(0)
        tails.append(float(m.group(1)) + const * (l_plus_u if on_u else 0))
    return tails


def rule_bodies(text, selector):
    """Every rule for one selector, in source order — one per tier.

    THIS RETURNED THE LAST ONE UNTIL THERE WAS MORE THAN ONE TIER, which was
    the right reading while the root only drew inside the pin gate: a second
    `.lp-flow__seg { }` in the file was a duplicate, not a tier. The flow tier
    added one deliberately, and a check that reads the last rule would have
    gone on holding the pinned tier's numbers and said nothing at all about
    the four families a phone actually runs.
    """
    return [m.group(1)
            for m in re.finditer(re.escape(selector) + r"\s*\{([^}]*)\}", text)]


def tier_of(body):
    """Which rate a rule's windows are written off, or None."""
    found = [name for name in TIERS if "var(%s)" % name in body]
    return found[0] if len(found) == 1 else None


def main():
    ap = argparse.ArgumentParser(
        description="A stroke grows out of a point that is already there.")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    text = LANDING.read_text(encoding="utf-8") + page_stylesheets(LANDING)
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
    span = max(s["run_end"] for s in segs)

    def level(d):
        """Where the front is when it has SPAN - d still to go."""
        return round(float(3 * F(span - d) / span), 2)

    # A stroke OPENS at its far end from the source — the fringe side, which
    # the front reaches first — and closes at its near end. run_end is the far
    # one, so the two are the other way round from the delta's own reading.
    for s in segs:
        want_l = level(s["run_end"])
        want_u = round(level(s["run"]) - level(s["run_end"]), 2)
        if abs(s["l"] - want_l) > 1e-9:
            findings.append(
                f"{s['d']}: --l is {s['l']}, but its far end stands at run "
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

    # ---- 3a. the trunk is drawn in the drawing, once, as both passes -----
    # The stem tier — a second svg standing in for the trunk when the anchor
    # chain stretched the box — was removed with the chain (2026-07-28). The
    # trunk is the in-drawing pair again: one light and one contour on
    # .lp-flow__trunk, visible, opening the walk.
    trunk = min(segs, key=lambda s: (s["l"], s["u"]))
    trunk_marks = [m for m in STROKE.finditer(text) if "lp-flow__trunk" in m.group(0)]
    if len(trunk_marks) < 1:
        findings.append(
            "no stroke carries .lp-flow__trunk — the drawing has no trunk of its "
            "own and the walk below starts from an arbitrary stroke")

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

    # ---- 4. every tier's speed is single-sourced ------------------------
    rates = {}
    for name in TIERS:
        decls = re.findall(re.escape(name) + r":\s*([\d.]+)\s*;", text)
        if len(decls) != 1:
            findings.append(
                f"{name} is declared {len(decls)} times; {TIERS[name]['label']} "
                f"has one drawing speed")
        rates[name] = float(decls[0]) if decls else 0.0

    # THE READING RIDES THE SAME WINDOW AS THE VALUE, and the two are one rule
    # on the page because they are one behaviour: both are numerals that light
    # where the front reaches the stroke they stand on. They differ in what
    # they SAY -- a value conserves and a reading carries a unit -- which is
    # check-flow-values.py's business, not this file's.
    #
    # AND EACH FAMILY IS WRITTEN ONCE PER TIER. Four families times two tiers
    # is eight rules, and the two things that can go wrong are the same two
    # they have always been: a window staggered on a typed constant instead of
    # on its tier's rate, and a family that quietly stops being drawn in one of
    # the tiers because its rule was edited in the other.
    families = {".lp-flow__seg": "the contour", ".lp-flow__light": "the light",
                ".lp-flow__node": "the junctions",
                ".lp-flow-data :is(.lp-flow__val, .lp-flow__read)": "the numerals"}
    by_tier = {}
    for selector, label in families.items():
        bodies = rule_bodies(text, selector)
        if not bodies:
            findings.append(f"no rule for `{selector}` — the selector went stale")
            continue
        seen = set()
        for body in bodies:
            decl = re.search(r"animation-range:([^;]*);", body)
            if not decl:
                continue                      # a paint-only rule, not a window
            rate = tier_of(decl.group(1))
            if rate is None:
                findings.append(
                    f"`{selector}` has an animation-range written off no tier's "
                    f"rate, or off two of them — every window belongs to exactly "
                    f"one of {', '.join(TIERS)}")
                continue
            seen.add(rate)
            by_tier.setdefault(rate, {})[selector] = body
            typed = {m.group(1)
                     for m in re.finditer(r"var\(--l\)\s*\*\s*([\d.]+)", decl.group(1))}
            for value in sorted(typed):
                findings.append(
                    f"`{selector}` staggers on a typed {value} instead of on "
                    f"{rate} — the four families drift apart one rule at a time")
        for rate in TIERS:
            if rate not in seen:
                findings.append(
                    f"`{selector}` has no window on {rate}: {TIERS[rate]['label']} "
                    f"draws the root without {label}")

    # ---- 5. the tails each tier's measurements were taken at -------------
    lu = max(round(s["l"] + s["u"], 2) for s in segs)
    for rate, spec in TIERS.items():
        const = rates[rate]
        seg_body = by_tier.get(rate, {}).get(".lp-flow__seg", "")
        light_body = by_tier.get(rate, {}).get(".lp-flow__light", "")
        tails = cover_tail(seg_body, rate, const, lu)
        contour = round(max(tails), 2) if tails else None
        tails = cover_tail(light_body, rate, const, lu)
        fade = round(max(tails), 2) if tails else None
        if contour is None or abs(contour - spec["contour"]) > TOL:
            findings.append(
                f"{spec['label']}: the contour's window does not resolve to "
                f"contain {spec['contour']} (it reads {contour}) — in the pinned "
                f"stage that is where the frame's relay is written to take over "
                f"(check-flow-handover.py has the seam), and in the flow tier it "
                f"is what leaves the finished drawing a still before it goes")
        if fade is None or abs(fade - spec["fade"]) > TOL:
            findings.append(
                f"{spec['label']}: the light's fade ends at contain {fade}, not "
                f"{spec['fade']} — that is the number the one-lit-element "
                f"clearance was swept at; re-sweep it before moving it "
                f"(foundations/colors.html#one-per-screen)")
        if contour is not None and fade is not None and fade <= contour:
            findings.append(
                f"{spec['label']}: the light is out at {fade}, on or before the "
                f"contour lands at {contour} — the front has to survive its own "
                f"black")
    # The other end of the clearance is the pinned card's own light, and its
    # rule carries TWO animation-ranges: the fill, which is the lime, and the
    # build the part shares with its stage-mates. Only the first is this
    # number — searching the whole file for the shape finds four other rules'
    # quarters first and reports whichever one it hits.
    #
    # THE FILL'S OPENING IS A FLOOR NOW, NOT A LITERAL. It used to read
    # `contain calc(var(--i) * 25% + 11.5%)`; it is
    # `contain calc(var(--i) * 25% + max(11.5%, <the part's own arrival end>))`
    # since the light stopped being allowed to fill before the plate carrying
    # it had landed — foundations/motion.html#light-last. What this check owns
    # is unchanged and is still true of card 01: its arrival closes at 11.4 of
    # the quarter, so the floor is what it takes and 11.5 is still the number
    # the clearance was swept at. The general inequality between the two ranges
    # is scripts/check-iso-motion.py's; this reads the floor out of the max()
    # and nothing else, so moving the constant still fails here.
    lit = (rule_bodies(text, ".lp-proc-steps .cf-iso__light") or [""])[-1]
    lime = re.search(
        r"animation-range:\s*contain calc\(\s*var\(--i\) \* 25%\s*"
        r"\+\s*(?:max\(\s*)?([\d.]+)%", lit)
    if lime is None or abs(float(lime.group(1)) - CARD_LIME) > TOL:
        findings.append(
            f"card 01's lime no longer opens at contain {CARD_LIME} % of its quarter — "
            f"that is the other end of the same clearance")

    return report(findings, args.verbose, (len(segs), junctions, lu, rates))


def report(findings, verbose, stats):
    if verbose and stats:
        n, j, lu, rates = stats
        print(f"flow chain: {n} strokes, {j} junctions")
        print(f"  deepest terminal at l + u = {lu:.2f}")
        for rate, spec in TIERS.items():
            print(f"  {spec['label']}: {rate} {rates.get(rate)} points per unit of --l, "
                  f"contour lands contain {spec['contour']:.2f} · "
                  f"light out at {spec['fade']:.2f}")
    if findings:
        print(f"flow chain: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1
    if stats:
        print(f"flow chain OK — {stats[1]} junctions, every stroke opening exactly where "
              f"the one that feeds it closes; both tiers' tails on the numbers the seam "
              f"and the light are measured at")
    return 0


if __name__ == "__main__":
    sys.exit(main())
