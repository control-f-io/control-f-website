#!/usr/bin/env python3
"""The hero scrim's plateau follows the content column.

The thirty-fifth check, and the second whose subject is a contrast guarantee.
check-contrast.py recomputes every pair the token file's guarantees rest on and
opens by saying why: "a token is one number in one file, every claim about it
lives in prose somewhere else, and the page after the nudge renders beautifully
on every screen belonging to anyone who would review it." That check cannot see
this pair. Its backdrops are colours; this one is a 12-second H.264 loop, and a
contrast figure taken over it is a figure taken over ONE FRAME unless somebody
decodes all 360.

Somebody did, and the answer was that the published figures were a frame:

    published in tokens.css     headline 4.08–6.26:1 over 375 / 768 / 1280 / 1920
    measured, all 360 frames    3.28 / 3.15 / 3.51 / 3.41 / 2.91 / 1.65
                                at 375 / 768 / 1280 / 1440 / 1920 / 2560

Two of them are under the 3:1 floor WCAG 1.4.3 sets for large text, the sample
at 1920 was wrong by a factor of 2.15, and the frame the sample came from is
frame 61 — hero-poster.jpg, the only frame a browser hands you with the loop
paused, and therefore the only one anyone was ever going to measure.

Everything in that paragraph is history: the artwork was replaced on
2026-08-03 and the poster is cut from frame 1 of the loop that shipped with it
rather than frame 61 of the one before. What survives the swap is the shape of
the fault — a figure taken from the one frame a paused browser will hand you —
and MEASURED_HEADLINE below, which was re-derived against the new render at the
weight it ships at. The reach is unchanged and so is every claim about it: it
is geometry, and geometry does not know which render it is aimed at.

THE FAULT IS GEOMETRY, NOT WEIGHT, and that is why this script exists rather
than a bigger number. --hero-scrim rises along --angle-a from the bottom-left
corner, full strength for --scrim-reach and out at twice it. The reach was a
constant, min(39rem, 62%), and the note that chose it gave its premise in one
sentence: "the column is anchored to the left gutter … so it stays about the
same size while the line grows by 0.894 of every pixel of viewport."

That premise expires at a viewport of 1438.2. Above it .container has hit
--container-max and centres, so the column stops being anchored to the gutter
and slides right by half of every further pixel — the fact --column-inset
exists to carry, in its own words: "the gap between them opens without limit:
80 px at the 1440 frame, 240 at 1920, 560 at 2560." The hero's CTA and its
pause switch already take --column-inset for exactly this. The scrim is the
third full-bleed layer that has to line up with the column and was the one that
did not take it. Projected onto the axis the column's far corner runs past
2 × 624 px — the far END of the falloff, where the scrim is not weak but zero
— and at 2560 the headline measured 1.65:1: the artwork with nothing on it.

WHY A SCRIPT AND NOT THE TABLE. The table above cannot be re-derived by
anything in this repository. Chromium ships no H.264 in the build CI runs, the
bundled ffmpeg demuxes nothing, and reproducing a single row costs a decoder,
360 screenshots and a compositing pass per viewport. A guarantee whose evidence
is that expensive to reproduce is a guarantee that will be quietly invalidated
by a one-line nudge to a token four screens away — which is precisely how the
figures it replaced came to be wrong. So the photometry stays in the comment as
a dated measurement, and what runs on every commit is the ARITHMETIC those
measurements were taken under: the reach still tracks the column, at the
projection the angle actually implies, and the weight has not been lowered
below the value the table was measured at.

WHAT IS CHECKED, all of it read out of tokens.css rather than restated here:

  the weight       --hero-scrim's three stops are alpha, alpha at
                   --scrim-reach, 0 at twice it, one tint throughout, and
                   alpha is not BELOW the value the table was measured at.
                   Raising it only makes every measured figure better;
                   lowering it invalidates every one of them silently.
  the term         --scrim-reach carries the column's displacement,
                   max(0px, (100vw - --container-max) / 2 - --gutter).
  the projection   its coefficient equals sin(--angle-a). Not 0.8944 as a
                   literal: sin is recomputed from the angle token, so
                   re-aiming the scrim and forgetting to re-derive the
                   coefficient is a finding rather than a silent 6 % error.
  the crossover    evaluated at a register of widths, the reach adds nothing
                   at or below the 1440 frame — the composition at 1280 and
                   1440 is the one the hero was drawn on and may not shift —
                   and exactly sin(A) x the column's own displacement above
                   it. The term has to be spelled with var(--container-max)
                   and var(--gutter) and not with the lengths they hold
                   today, which is what the shape above enforces: a reach
                   that copies 80rem out of the layout block goes stale the
                   day the layout block moves, and moves the scrim off the
                   column with nothing in the diff that says so.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-hero-scrim.py       # check, exit 1 on drift
    python3 scripts/check-hero-scrim.py -v    # print the reach at every width
"""

import argparse
import math
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOKENS = ROOT / "design-system" / "assets" / "css" / "tokens.css"

# The weight the table in tokens.css was measured at. A floor, not the value:
# the check reads the live one and only objects to it going DOWN, because every
# measured figure is monotone in it and only one direction can invalidate them.
# 0.42 until 2026-08-03, when the hero artwork was replaced with a different
# render of the same motion and the figures below were re-derived against it.
MEASURED_AT_ALPHA = 0.46

# Viewports the reach is evaluated at. The three below the crossover prove the
# term contributes nothing there; the three above it are where it does the work
# and where the two failures were measured. Heights are irrelevant to the reach
# — it is a horizontal displacement projected onto the axis — so only widths.
REGISTER = [375, 768, 1280, 1440, 1920, 2560]

# The measured worst frame of the loop, per width, after the reach was fixed.
# Documentation, not an assertion: nothing in CI can re-derive it. Printed by
# -v so the figure and the arithmetic that carries it stay in one place.
#
# RE-DERIVED 2026-08-03 against the artwork that shipped that day, at the
# heights check-hero-contrast.py's register already carries — 375 x 812,
# 768 x 800, 1280 x 800, 1440 x 900, and 1920 x 1080 / 2560 x 1440 above them,
# because the ARTWORK under the type depends on the box's aspect and a width
# alone does not name a frame. Every figure is the worst of all 361 (poster
# plus 360), composited the way that register is: --hero-dissolve fading the
# artwork into the page wash, then the scrim at the alpha the point's own
# distance along the axis gives it. The previous set — 3.28 / 3.15 / 3.51 /
# 3.41 / 3.47 / 3.55 — belongs to the render this one replaced.
MEASURED_HEADLINE = {375: 3.83, 768: 3.81, 1280: 3.45,
                     1440: 3.54, 1920: 3.53, 2560: 3.53}
HEADLINE_FLOOR = 3.0

REM = 16.0


def decl(name, css):
    """The value of one custom property on :root, brace-balanced, comments out."""
    m = re.search(r"^\s*%s\s*:" % re.escape(name), css, re.M)
    if not m:
        return None
    i = m.end()
    depth, out = 0, []
    while i < len(css):
        ch = css[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == ";" and depth == 0:
            break
        out.append(ch)
        i += 1
    return re.sub(r"/\*.*?\*/", " ", "".join(out), flags=re.S).strip()


def clamp_px(expr, vw):
    """Evaluate the one clamp() shape the gutter uses: clamp(<rem>, <vw>, <rem>)."""
    m = re.fullmatch(r"clamp\(\s*([\d.]+)rem\s*,\s*([\d.]+)vw\s*,\s*([\d.]+)rem\s*\)",
                     expr.strip())
    if not m:
        return None
    lo, mid, hi = float(m.group(1)) * REM, float(m.group(2)) / 100.0 * vw, float(m.group(3)) * REM
    return min(max(lo, mid), hi)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    css = TOKENS.read_text()
    rel = TOKENS.relative_to(ROOT)
    findings = []

    angle_raw = decl("--angle-a", css)
    cmax_raw = decl("--container-max", css)
    gutter_raw = decl("--gutter", css)
    reach_raw = decl("--scrim-reach", css)
    scrim_raw = decl("--hero-scrim", css)

    for name, raw in (("--angle-a", angle_raw), ("--container-max", cmax_raw),
                      ("--gutter", gutter_raw), ("--scrim-reach", reach_raw),
                      ("--hero-scrim", scrim_raw)):
        if raw is None:
            print("%s: %s is gone. The hero scrim cannot be checked without it."
                  % (rel, name), file=sys.stderr)
            return 1

    angle_deg = float(re.fullmatch(r"([\d.]+)deg", angle_raw.strip()).group(1))
    cmax_px = float(re.fullmatch(r"([\d.]+)rem", cmax_raw.strip()).group(1)) * REM
    sin_a = math.sin(math.radians(angle_deg))

    # Where the container stops growing and starts centring: the width at which
    # (W - --container-max) / 2 and --gutter's own vw arm meet. --column-inset's
    # note calls this crossover exact rather than approximate, so it is solved
    # rather than quoted — 1438.2 with today's tokens.
    vw_arm = re.search(r",\s*([\d.]+)vw\s*,", gutter_raw)
    crossover_px = (cmax_px / 2.0) / (0.5 - float(vw_arm.group(1)) / 100.0) if vw_arm else 0.0

    # ---- the weight -------------------------------------------------------
    # The plateau's alpha is --scrim-depth now and not a literal typed twice —
    # check-hero-contrast.py deepens it at or below 56.25rem, where cover puts
    # the square artwork's dark band under the 11 px kicker. So the stops are
    # resolved through the token before the weight is judged, and the weight is
    # judged at EVERY value the token takes: a floor that only held at the wide
    # value would leave the narrow one free to drop under the measurements.
    depths = [float(v) for v in re.findall(r"--scrim-depth\s*:\s*([\d.]+)", css)]
    if not depths:
        findings.append("--scrim-depth is gone. --hero-scrim's plateau reads its "
                        "alpha from that token, and without it the weight below "
                        "cannot be resolved at all.")
    def resolve(a):
        return depths if a.strip() == "var(--scrim-depth)" else [float(a)]
    stops = re.findall(r"rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,"
                       r"\s*((?:var\([^()]*\)|[^()])+)\)", scrim_raw)
    if len(stops) != 3:
        findings.append("--hero-scrim has %d colour stops, not the 3 this check and the "
                        "note above it describe (full, full at the reach, out at twice it)."
                        % len(stops))
    else:
        tints = {s[:3] for s in stops}
        if len(tints) != 1:
            findings.append("--hero-scrim mixes %d tints. The scrim is CF-Grau and nothing "
                            "else — the note in tokens.css is explicit that white would "
                            "frost it and black would bruise it." % len(tints))
        try:
            resolved = [resolve(s[3]) for s in stops]
        except ValueError:
            resolved = None
        if resolved is None or not depths:
            alphas = None
        else:
            # every combination the media queries can produce; today two
            alphas = [min(resolved[0]), min(resolved[1]), max(resolved[2])]
        if alphas is None:
            findings.append("--hero-scrim's stops no longer resolve to numbers: %r"
                            % [s[3] for s in stops])
        elif alphas[2] != 0.0:
            findings.append("--hero-scrim's last stop is alpha %.3f, not 0. The scrim has to "
                            "be OUT at twice the reach, or it greys the artwork's best "
                            "corner for no reader." % alphas[2])
        if alphas is not None and sorted(resolve(stops[0][3])) != sorted(resolve(stops[1][3])):
            findings.append("--hero-scrim's first two stops are %.3f and %.3f. They are the "
                            "plateau and have to be equal — a ramp starting at the corner "
                            "is not the material this token describes."
                            % (min(resolve(stops[0][3])), min(resolve(stops[1][3]))))
        if alphas is not None and min(resolve(stops[0][3])) < MEASURED_AT_ALPHA - 1e-9:
            findings.append("--hero-scrim is at alpha %.3f, below the %.2f every contrast "
                            "figure in its own note was measured at. Lowering it invalidates "
                            "the whole table silently and nothing in CI can re-derive it: "
                            "the backdrop is 360 frames of H.264 and neither the browser CI "
                            "runs nor the bundled ffmpeg will decode one. Raise it back, or "
                            "re-measure with a decoder and rewrite the table."
                            % (min(resolve(stops[0][3])), MEASURED_AT_ALPHA))

    # ---- the term and its projection --------------------------------------
    shift = re.search(
        r"max\(\s*0px\s*,\s*\(\s*100vw\s*-\s*var\(\s*--container-max\s*\)\s*\)\s*/\s*2"
        r"\s*-\s*var\(\s*--gutter\s*\)\s*\)", reach_raw)
    if not shift:
        findings.append(
            "--scrim-reach no longer carries the column's displacement. Above a viewport of "
            "%.1f the container has hit --container-max and centres, so the text column "
            "slides right by half of every further pixel while a constant reach stays put — "
            "and the headline's far corner projects past twice the plateau, where the scrim "
            "is zero. Measured at 2560 with a constant reach: 1.65:1 against a 3:1 floor. "
            "The term is max(0px, (100vw - var(--container-max)) / 2 - var(--gutter)), "
            "spelled with the tokens and not with the lengths they hold today."
            % crossover_px)
        coeff = None
    else:
        head = reach_raw[:shift.start()]
        m = re.search(r"([\d.]+)\s*\*\s*$", head.strip())
        coeff = float(m.group(1)) if m else None
        if coeff is None:
            findings.append("--scrim-reach adds the column's displacement unprojected. A "
                            "horizontal shift of dx lands sin(--angle-a) = %.4f of itself on "
                            "the gradient line, not all of it." % sin_a)
        elif abs(coeff - sin_a) > 5e-4:
            findings.append("--scrim-reach projects the column's displacement by %.4f, and "
                            "sin(--angle-a) is %.4f at %.2fdeg. The coefficient is not a "
                            "constant — it is the angle, and re-aiming the scrim without "
                            "re-deriving it puts the plateau %.1f%% off the corner it exists "
                            "to cover." % (coeff, sin_a, angle_deg,
                                           abs(coeff - sin_a) / sin_a * 100))

    # ---- the crossover, evaluated -----------------------------------------
    rows = []
    for w in REGISTER:
        g = clamp_px(gutter_raw, w)
        if g is None:
            findings.append("--gutter is no longer the clamp(<rem>, <vw>, <rem>) this check "
                            "evaluates: %r. The reach cannot be re-derived without it."
                            % gutter_raw)
            break
        column_shift = max(0.0, (w - cmax_px) / 2.0 - g)
        added = (coeff or 0.0) * column_shift
        rows.append((w, g, column_shift, added))
        # Below the crossover the term must contribute nothing at all: the whole
        # point of keeping it zero there is that the designed composition at
        # 1280 and 1440 is byte-identical to what it was.
        if w <= 1440 and added > 1.0:
            findings.append("--scrim-reach adds %.1f px at %d, where the column has not "
                            "moved off the gutter yet. Below the crossover the scrim is the "
                            "one the composition was drawn on and may not shift."
                            % (added, w))

    if findings:
        for why in findings:
            print("%s\n    %s\n" % (rel, why), file=sys.stderr)
        print("%d finding%s: the hero scrim no longer holds the geometry its measured "
              "contrast figures were taken under. Those figures cost a decoder and 360 "
              "frames per viewport; nothing here can re-derive them."
              % (len(findings), "" if len(findings) == 1 else "s"), file=sys.stderr)
        return 1

    if args.verbose:
        print("  --angle-a %.2fdeg  sin %.4f   --container-max %.0f px   "
              "alpha %s (--scrim-depth)"
              % (angle_deg, sin_a, cmax_px,
                 "/".join("%.2f" % d for d in sorted(set(depths)))))
        print("  %6s  %8s  %14s  %10s   %s"
              % ("width", "gutter", "column shift", "reach +", "headline, worst of 360"))
        for w, g, cs, added in rows:
            print("  %6d  %8.1f  %14.1f  %10.1f   %5.2f:1  (floor %.1f)"
                  % (w, g, cs, added, MEASURED_HEADLINE[w], HEADLINE_FLOOR))
        print()

    print("hero scrim: plateau follows the column at sin(%.2fdeg) = %.4f, weight %s, "
          "%d widths checked, %.0f px added at 2560 and 0 at the 1440 frame."
          % (angle_deg, sin_a, "/".join("%.2f" % d for d in sorted(set(depths))),
             len(rows), rows[-1][3]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
