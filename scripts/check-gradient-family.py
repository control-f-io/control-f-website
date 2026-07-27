#!/usr/bin/env python3
"""Enforce the light family in every SVG gradient the site ships.

tokens.css states the rule and foundations/colors.html publishes the numbers:

    SVG CANNOT DO THIS, AND EVERY SVG IN THE SYSTEM STILL HAS TO. There is no
    `in oklab` on a <linearGradient>, so a drawing that carries the family's
    ramp carries the oklab path by hand instead: ONE EXTRA STOP AT 19 % OF THE
    LIME LEG, measured from lime, coloured at the oklab path's value there.

That convention held across twenty gradients and then quietly broke on the
one page nobody re-measured. patterns/expertise.html drew four objects on the
NEAR rake (Glas at 0.32) and gave all four the MID rake's waypoint offset
(0.097, which is 19 % of 0.51). The colour that belongs at 19 % of the leg was
painted at 30.3 % of it. Nothing rendered wrong, no reference broke, and the
page looked approximately right -- which is exactly why a convention enforced
by reading is a convention with a half-life.

A rule stated in prose and applied by hand is a rule that drifts. This is the
thing that applies it.

Both the waypoint's POSITION and its COLOUR are recomputed here from the oklab
path rather than compared against a literal, so the script re-derives #DBFC60
and #E6FF66 instead of trusting them. Change the palette and the expected
waypoints move with it; hard-code a stale hex and this fails.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-gradient-family.py          # check, exit 1 on drift
    python3 scripts/check-gradient-family.py -v       # list every gradient
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"

# WHAT IS IN SCOPE, and the two exclusions are the same boundary
# check-spacing-scale.py already draws.
#
#   assets/source/  is the DESIGNER'S OWN MATERIAL. It is the authority this
#                   script enforces against; correcting it would be backwards.
#                   Its exports carry #E0FF02 and Figma's own stop spacing,
#                   and they are supposed to.
#   prototypes/     is unshipped working material carrying raw Figma exports
#                   for the same reason.
EXCLUDE = ("/assets/source/", "/prototypes/")

# The four CHROMATIC core colours, verbatim from tokens.css section 3a. A stop
# that sits within NEAR_MISS of one of these and is not exactly it is a
# near-miss import -- the #E0FF02-for-#E1FF00 class of drift that
# process-card.html and demon-core.html both record having had to correct by
# hand. #E0FF02 sits at dE 0.0035 from lime, well inside the threshold.
#
# THE THREE NEUTRALS ARE DELIBERATELY NOT IN HERE, and the exclusion is the
# rule's own premise rather than a hole in it. Near a saturated colour,
# "almost" means someone pasted an export. Near the neutral axis it means the
# opposite: the page wash's three chromatic stops (#CFCFD2, #E1E4E7, #F3F8F7)
# are the spectrum pulled down to chroma 0.005 precisely SO THAT they land
# within a few levels of neutral -- tokens.css sets that ceiling at "no channel
# may move further from the neutral than the grain does", and #CFCFD2 is 0.0042
# from CF-Grau because it was built to be. Those stops are governed by the
# chroma budget documented there, not by this rule, and flagging them would be
# telling the wash to stop being iridescent.
PALETTE = {
    "#E1FF00": "lime",
    "#C5EBE2": "Glas",
    "#72B0E2": "Sky",
    "#7E7FE1": "Violett",
}
LIME = "#E1FF00"

# 19 % of the leg. A convention rather than an optimum, and the same number
# everywhere so the drawings cannot drift apart from each other -- see the
# tokens.css comment for why the 21 % that is optimal on one leg was not worth
# a second number.
WAYPOINT_T = 0.19

# How close a stop may sit to a palette colour without being it. In oklab dE.
# The desaturated wash (#CFCFD2, #E1E4E7, #F3F8F7) and the 800-band foil sit
# well outside this; #E0FF02 sits at 0.0035.
NEAR_MISS = 0.01

# Position tolerance. Offsets ship at three decimals, so half a unit in the
# last place is the most an honest rounding can cost.
POS_TOL = 0.0006


# --- colour, exactly as tokens.css and colors.html compute it ----------------

def _srgb_to_linear(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(c):
    v = c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055
    return max(0, min(255, round(v * 255)))


def hex_to_linear(h):
    h = h.lstrip("#")
    return [_srgb_to_linear(int(h[i:i + 2], 16)) for i in (0, 2, 4)]


def linear_to_hex(rgb):
    return "#%02X%02X%02X" % tuple(_linear_to_srgb(c) for c in rgb)


def linear_to_oklab(r, g, b):
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = l ** (1 / 3), m ** (1 / 3), s ** (1 / 3)
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def oklab_to_linear(L, a, b):
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)


def oklab(h):
    return linear_to_oklab(*hex_to_linear(h))


def dE(h1, h2):
    a, b = oklab(h1), oklab(h2)
    return sum((a[i] - b[i]) ** 2 for i in range(3)) ** 0.5


def waypoint_colour(start, end, t=WAYPOINT_T):
    """The colour the oklab path from `start` to `end` passes through at t.

    This is the whole reason the waypoint exists: sRGB interpolation between
    two stops takes a visibly different route than `in oklab` does, and SVG has
    no way to ask for the second one. Planting the oklab path's own value as a
    third stop pulls the sRGB chords back onto it.
    """
    a, b = oklab(start), oklab(end)
    return linear_to_hex(oklab_to_linear(*[a[i] + (b[i] - a[i]) * t for i in range(3)]))


# --- parsing ----------------------------------------------------------------

GRADIENT = re.compile(r"<(linear|radial)Gradient\s[^>]*?id=\"([^\"]+)\"(.*?)</\1Gradient>", re.S)
STOP = re.compile(r"<stop\b([^>]*?)/?>")
ATTR = re.compile(r"(\S+)=\"([^\"]*)\"")


def parse_offset(raw):
    raw = raw.strip()
    return float(raw[:-1]) / 100 if raw.endswith("%") else float(raw)


def gradients(text):
    for m in GRADIENT.finditer(text):
        stops = []
        for sm in STOP.finditer(m.group(3)):
            a = dict(ATTR.findall(sm.group(1)))
            if "stop-color" not in a:
                continue
            stops.append((parse_offset(a.get("offset", "0")), a["stop-color"].strip().upper()))
        if stops:
            yield m.group(2), m.group(1), stops


def sources():
    for path in sorted(DS.rglob("*.html")) + sorted(DS.rglob("*.svg")):
        rel = "/" + str(path.relative_to(ROOT)).replace("\\", "/")
        if any(x in rel for x in EXCLUDE):
            continue
        yield path


# --- the two rules ----------------------------------------------------------

def check_near_miss(stops):
    """A stop that is almost a brand colour is a stop that was pasted, not chosen."""
    out = []
    for off, col in stops:
        for hexv, name in PALETTE.items():
            if col != hexv and dE(col, hexv) < NEAR_MISS:
                out.append("stop %s at %g is %s %s off %s %s -- use the brand hex"
                           % (col, off, "dE", round(dE(col, hexv), 4), name, hexv))
    return out


def check_lime_leg(stops):
    """Every leg leaving lime carries its waypoint, at 19 % of the leg.

    The leg is lime to its nearest neighbour that is not itself a waypoint, in
    whichever direction the drawing runs -- the two Glas-to-lime radials and
    the dark wallpaper's lime-to-Weiss leg all run the other way from the
    process cards, and the rule is about the leg, not about stop order.
    """
    out = []
    idx = [i for i, (_, c) in enumerate(stops) if c == LIME]
    if not idx:
        return out
    i = idx[0]
    lime_off = stops[i][0]

    for step in (1, -1):
        j = i + step
        # Skip over anything that is already a waypoint on this leg: it is the
        # stop we are about to look for, not the far end of the leg.
        while 0 <= j < len(stops) and _is_waypoint_colour(stops[j][1], stops, i, step):
            j += step
        if not (0 <= j < len(stops)):
            continue
        end_off, end_col = stops[j]
        if end_col == LIME:
            continue

        want_pos = lime_off + (end_off - lime_off) * WAYPOINT_T
        want_col = waypoint_colour(LIME, end_col)

        got = [s for s in stops if min(lime_off, end_off) <= s[0] <= max(lime_off, end_off)
               and s[1] not in (LIME, end_col)]
        if not got:
            out.append("lime -> %s leg carries no waypoint; expected %s at offset %s"
                       % (end_col, want_col, round(want_pos, 4)))
            continue
        if len(got) > 1:
            out.append("lime -> %s leg carries %d waypoints; the family allows one"
                       % (end_col, len(got)))
            continue
        pos, col = got[0]
        if abs(pos - want_pos) > POS_TOL:
            leg = abs(end_off - lime_off) or 1
            out.append("waypoint %s sits at offset %g -- %.1f %% of the lime -> %s leg, "
                       "not %g %%; expected offset %s"
                       % (col, pos, abs(pos - lime_off) / leg * 100, end_col,
                          WAYPOINT_T * 100, round(want_pos, 4)))
        if col != want_col:
            out.append("waypoint at offset %g is %s; the oklab path from lime to %s "
                       "passes through %s at %g %%"
                       % (pos, col, end_col, want_col, WAYPOINT_T * 100))
    return out


def _is_waypoint_colour(col, stops, lime_i, step):
    """True if `col` is the oklab waypoint for lime toward some other stop here.

    Used only to step past a waypoint while looking for the far end of its own
    leg, so it asks the derived question rather than consulting a list.
    """
    return any(col == waypoint_colour(LIME, c)
               for _, c in stops if c != LIME and c != col)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every gradient checked, not only the failures")
    args = ap.parse_args()

    failures, seen = [], 0
    for path in sources():
        rel = path.relative_to(DS)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for gid, kind, stops in gradients(text):
            seen += 1
            problems = check_near_miss(stops) + check_lime_leg(stops)
            if args.verbose:
                mark = "FAIL" if problems else "ok  "
                print("%s %-42s %s %-16s %s" % (
                    mark, rel, kind[:3], gid,
                    " ".join("%g:%s" % s for s in stops)))
            for p in problems:
                failures.append("%s  %s: %s" % (rel, gid, p))

    if failures:
        print("\nThe light family has drifted in %d place%s:\n"
              % (len(failures), "" if len(failures) == 1 else "s"), file=sys.stderr)
        for f in failures:
            print("  " + f, file=sys.stderr)
        print("\nSee foundations/colors.html#the-arc and the SVG CANNOT DO THIS "
              "block in tokens.css.", file=sys.stderr)
        return 1

    print("%d gradients, one family." % seen)
    return 0


if __name__ == "__main__":
    sys.exit(main())
