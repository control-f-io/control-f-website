#!/usr/bin/env python3
"""Enforce the light family in every gradient the site ships — SVG and CSS.

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

THE OTHER HALF OF THE FAMILY IS IN CSS, and it was unchecked for as long as
this script existed. tokens.css states two more conventions that live nowhere
but in prose, and both are literals somebody has to remember:

    THE ARC. A straight oklab line between two chromatic stops is a chord, so
    every leg chromatic at BOTH ends carries one waypoint at its midpoint,
    coloured at the OKLCH midpoint. #B9E3EB, #B8CCF3, #33494E and #273650 are
    those four, and tokens.css says of them: "Recompute them if either
    endpoint moves; they are literals, like the #DBFC60 waypoint, and they do
    not follow the palette on their own."

    THE PATH. A ramp carrying a lime leg is restated once with `in oklab`,
    because lime -> Glas is the leg where sRGB and oklab actually part
    (dEok 0.04430, against 0.00148 for Glas -> Sky). tokens.css lists the legs
    it deliberately leaves in sRGB; the lime ones are not among them.

That is the same standing #DBFC60 had before this script: a convention applied
by hand, with a half-life. It had already slipped once — .cf-btn--glass drew
Glas into lime on the sRGB path with no oklab branch, the only lime leg in the
system's CSS never put on the family's path, at dEok 0.03866 composited over
CF-Grau, seventy-nine times the divergence of the one leg tokens.css names as
small enough to leave alone.

So the CSS rules are recomputed here too — the arc waypoints from the polar
midpoint of their own leg's ends, never compared against those four hexes.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-gradient-family.py          # check, exit 1 on drift
    python3 scripts/check-gradient-family.py -v       # list every gradient
"""

import argparse
import math
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

# --- the CSS half -----------------------------------------------------------

# The shipping stylesheets. docs.css is documentation chrome and does not ship,
# which is the boundary check-glass-budget.py already draws.
CSS = ("tokens.css", "base.css", "components.css")

# Below this OKLCh chroma a stop has no hue worth arcing through, so a chord
# cannot fall short of anything and no waypoint is owed. It is the CSS side of
# the SVG rule's NO WAYPOINT ON A LEG THAT ENDS IN GREY, written as a number
# because CSS has stops that are nearly grey rather than exactly grey.
#
# The two things it has to separate are both already in the file and both are
# deliberate. --wash-stops runs the foil backwards at chroma 0.005, and
# tokens.css sets that ceiling on purpose so the wash stays inside the grain;
# arcing it would be telling the wash to stop being neutral. Glas 800 is
# 0.0171 and is the LIGHTEST rung of the ink foil, whose whole claim is hue
# travel. Anywhere between the two would do; the midpoint is not a measurement
# and is not pretending to be one.
ARC_CHROMA_FLOOR = 0.010

# A stop carrying alpha is exempt from the arc, and this is the system's own
# argument rather than an exemption list. --glass-edge runs Glas into Sky —
# chromatic at both ends — and tokens.css leaves it in sRGB deliberately, on
# the grounds that "the comparison has to be made composited, because these
# stops carry alpha". What such a stop renders as depends on what is behind
# it, so its declared chroma is not its drawn chroma and the chord it cuts is
# not a fact about the stop list. Opaque stops have no such excuse.
ALPHA_OPAQUE = 0.999


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


# --- parsing, CSS -----------------------------------------------------------

COMMENT = re.compile(r"/\*.*?\*/", re.S)
CUSTOM_PROP = re.compile(r"(--[\w-]+)\s*:\s*([^;}]+)")
GRADIENT_FN = re.compile(r"\b(repeating-)?(linear|radial|conic)-gradient\s*\(")
VAR_REF = re.compile(r"var\(\s*(--[\w-]+)\s*(?:,[^()]*)?\)")
HEX = re.compile(r"#[0-9A-Fa-f]{3,8}\b")
RGB_FN = re.compile(r"\brgba?\(([^()]*)\)")


# The gradient inside `@supports (background: linear-gradient(in oklab, red,
# blue))` is a FEATURE PROBE, not a gradient the site paints, and it appears
# six times. Its two stops are `red` and `blue`, which resolve to nothing and
# would otherwise be the whole of this script's unresolved count — a number
# that has to mean something for the summary line to be worth printing.
SUPPORTS_PRELUDE = re.compile(r"@supports[^{]*\{")


def strip_comments(text):
    return SUPPORTS_PRELUDE.sub("@supports {", COMMENT.sub(" ", text))


def balanced(text, open_at):
    """Return the text inside the parentheses opening at `open_at`."""
    depth, i = 0, open_at
    while i < len(text):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return text[open_at + 1:i], i + 1
        i += 1
    return "", len(text)


def split_top(text):
    """Split on commas that are not inside parentheses."""
    out, depth, cur = [], 0, ""
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    out.append(cur)
    return [s.strip() for s in out if s.strip()]


def custom_props(texts):
    """Every --name: value in the shipping stylesheets, last declaration wins.

    Last-wins is what the cascade does for the one thing this map is used for:
    the @supports branch at the foot of tokens.css restates a token it has
    already declared, and the restated value is the one that ships wherever the
    branch applies. Nothing here depends on specificity, because every ramp in
    the family is declared at :root or on its own single class.
    """
    props = {}
    for text in texts:
        for name, value in CUSTOM_PROP.findall(strip_comments(text)):
            props[name] = value.strip()
    return props


def expand(value, props, depth=0):
    """Substitute var() references until none are left or the nesting is silly."""
    if depth > 8:
        return value
    out = VAR_REF.sub(lambda m: props.get(m.group(1), m.group(0)), value)
    return out if out == value else expand(out, props, depth + 1)


def parse_colour(item):
    """(hex, alpha) for a gradient stop, or None if it cannot be resolved.

    Unresolvable is a REPORTED outcome, not a silent skip — color-mix() and a
    var() that resolves outside these three files both land here, and the
    summary line names how many there were.
    """
    item = item.strip()
    if not item:
        return None
    if item.split()[0] == "transparent":
        return "#000000", 0.0
    m = RGB_FN.search(item)
    if m:
        parts = [p.strip() for p in re.split(r"[,/]", m.group(1)) if p.strip()]
        try:
            rgb = [int(round(float(p.rstrip("%")))) for p in parts[:3]]
        except ValueError:
            return None
        alpha = 1.0
        if len(parts) > 3:
            try:
                alpha = float(parts[3].rstrip("%")) / (100 if "%" in parts[3] else 1)
            except ValueError:
                return None
        return "#%02X%02X%02X" % tuple(max(0, min(255, c)) for c in rgb), alpha
    m = HEX.search(item)
    if m:
        h = m.group(0).upper()
        if len(h) == 4:                      # #RGB
            h = "#" + "".join(c * 2 for c in h[1:])
        if len(h) == 5:                      # #RGBA
            a = int(h[4] * 2, 16) / 255
            return "#" + "".join(c * 2 for c in h[1:4]), a
        if len(h) == 9:                      # #RRGGBBAA
            return h[:7], int(h[7:9], 16) / 255
        if len(h) == 7:
            return h, 1.0
    return None


def css_gradients(text, props):
    """(function name, [(hex, alpha) or None, ...], has_oklab, stop_text)."""
    src = strip_comments(text)
    for m in GRADIENT_FN.finditer(src):
        args, _ = balanced(src, m.end() - 1)
        resolved = expand(args, props)
        items = split_top(resolved)
        if not items:
            continue
        head = items[0]
        # The first argument is a prefix (an angle, a shape, a side-or-corner,
        # an interpolation method) only when it carries no colour of its own.
        prefix = head if parse_colour(head) is None else ""
        stops = items[1:] if prefix else items
        yield (m.group(0)[:-1],
               [parse_colour(s) for s in stops],
               "in oklab" in prefix or "in oklch" in prefix,
               " , ".join(split_top(args)[1:] if prefix else split_top(args)))


# --- the CSS rules ----------------------------------------------------------

def oklch(h):
    L, a, b = oklab(h)
    return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360


def from_oklch(L, C, h):
    r = math.radians(h)
    return linear_to_hex(oklab_to_linear(L, C * math.cos(r), C * math.sin(r)))


def arc_midpoint(start, end):
    """The colour the POLAR path from `start` to `end` passes through halfway.

    L, C and h each interpolated linearly, hue the shorter way — which is what
    `in oklch shorter hue` means and what the waypoint is standing in for. This
    re-derives #B9E3EB, #B8CCF3, #33494E and #273650 rather than trusting them.
    """
    L1, C1, H1 = oklch(start)
    L2, C2, H2 = oklch(end)
    d = (H2 - H1 + 540) % 360 - 180
    return from_oklch((L1 + L2) / 2, (C1 + C2) / 2, (H1 + d / 2) % 360)


def _chromatic(stop):
    return stop is not None and stop[1] >= ALPHA_OPAQUE and oklch(stop[0])[1] >= ARC_CHROMA_FLOOR


def _turns(start, end):
    """True if this leg is one the arc governs: a TURN, not a falloff.

    THE ARC's own premise is that "two stops of similar chroma and different
    hue sit on roughly the same circle about the neutral axis, so the straight
    line between them is a CHORD". Two conditions, and the block only ever
    writes the second one down because the first is invisible on the four legs
    it names — every one of them is inside the foil's narrow band.

    A LEG CARRYING LIME IS NOT ON THAT CIRCLE. Lime is C 0.2201 and Glas is
    C 0.0414: the move between them is radial, not tangential, and the polar
    path through it bows out to #A8FFB6 — a green in no palette, at C 0.1310,
    three times the chroma of the stop it is travelling to. That is the same
    case as the achromatic one and takes the same answer: oklab's straight
    line is already the correct path. It is why the light family is corrected
    with `in oklab` and the SVG waypoint while the spectrum and the two foils
    are corrected with an arc — the family's own INTERPOLATION block says so
    in as many words, "OKLab is rectangular and has no hue to swing. Where a
    hue path is wanted it is written as an explicit stop instead."

    So: lime is the light source and CF-Grau and Weiss are what it falls away
    to, and a leg touching any of the three is a falloff. Everything else in
    the band turns.
    """
    return start != LIME and end != LIME


def check_arc(stops):
    """Every opaque leg that turns carries its own polar midpoint as a waypoint.

    The stops that are already waypoints have to be identified before the legs
    can be, or the rule eats itself: a waypoint read as an endpoint splits its
    own leg in two and demands a waypoint in each half, for ever. A waypoint is
    recognised the same way it is checked — by BEING the polar midpoint of the
    two chromatic stops either side of it — so nothing here consults a list of
    the four hexes that ship.
    """
    out = []
    chrom = [i for i, s in enumerate(stops) if _chromatic(s)]
    if len(chrom) < 2:
        return out

    # RECOGNISING a waypoint is loose and CHECKING it is exact, and the two
    # thresholds answer different questions. Here the question is "is this stop
    # trying to be the midpoint of its neighbours", so that a drifted waypoint
    # is still read as a waypoint and reported as a wrong one rather than
    # reclassified as an endpoint and reported as a chord. NEAR_MISS is the
    # right coarseness for that. The value itself is then compared exactly,
    # below.
    #
    # Left to right, and a waypoint may not follow a waypoint. Without that
    # second condition the middle of a finished ramp reads as its own waypoint:
    # in --foil-stops the polar midpoint of the two waypoints either side of
    # Sky 300 lands within dE 0.01 of Sky 300 itself, which is not a
    # coincidence but the arithmetic of an evenly waypointed ramp. Real
    # waypoints alternate with real stops, so the greedy pass is exact.
    waypoint = set()
    for k in range(1, len(chrom) - 1):
        a, i, b = chrom[k - 1], chrom[k], chrom[k + 1]
        if a in waypoint:
            continue
        if dE(stops[i][0], arc_midpoint(stops[a][0], stops[b][0])) <= NEAR_MISS:
            waypoint.add(i)

    ends = [i for i in chrom if i not in waypoint]
    for a, b in zip(ends, ends[1:]):
        start, end = stops[a][0], stops[b][0]
        between = [stops[i] for i in range(a + 1, b)]
        if start == end or not _turns(start, end):
            continue
        # An achromatic or transparent stop between the two ends means this is
        # not one leg. --spectrum-stops puts Weiss between lime and Glas and
        # .cf-arrive__ghost puts it between Glas and Sky: in both the ramp
        # travels to the hot spot and away from it, two falloffs that each end
        # in an achromatic stop, and THE ARC gives those nothing.
        if any(s is None or s[1] < ALPHA_OPAQUE or oklch(s[0])[1] < ARC_CHROMA_FLOOR
               for s in between):
            continue
        want = arc_midpoint(start, end)
        if not between:
            out.append("%s -> %s is a chord: the leg turns %.1f deg of hue and carries no "
                       "arc waypoint; expected %s at its midpoint"
                       % (start, end, abs((oklch(end)[2] - oklch(start)[2] + 540) % 360 - 180), want))
            continue
        if len(between) > 1:
            out.append("%s -> %s carries %d stops; the arc allows one waypoint"
                       % (start, end, len(between)))
            continue
        got = between[0][0]
        # Exact, the way the SVG rule compares its own recomputed waypoint. A
        # waypoint is a hex literal and arc_midpoint() returns one off the same
        # 8-bit grid, so anything but equality is somebody's rounding or a
        # stale value left behind by an endpoint that moved. NEAR_MISS is the
        # threshold for "was this pasted", which is a different question and
        # ten times too coarse for this one: it passes a waypoint eleven levels
        # off its leg.
        if got != want:
            out.append("arc waypoint on %s -> %s is %s; the polar midpoint of that leg "
                       "is %s (dE %.4f)" % (start, end, got, want, dE(got, want)))
    return out


def check_path(name, stops, has_oklab, twins):
    """A ramp with a lime leg exists somewhere on the oklab path.

    lime -> Glas is dEok 0.04430 between the two paths and lime -> Weiss is
    0.04651; every other leg in the family is under 0.0015, which is why
    tokens.css leaves those in sRGB by name. So this asks the question only of
    lime, and it asks it of the STOP LIST rather than of the declaration: the
    idiom throughout is one ramp restated with a different path, so the sRGB
    declaration and its oklab twin share their stop text exactly.
    """
    if has_oklab:
        return []
    cols = [s[0] for s in stops if s is not None]
    if LIME not in cols:
        return []
    others = [c for c in cols if c != LIME]
    if not others:
        return []
    if twins:
        return []
    return ["carries a lime leg on the sRGB path and is never restated `in oklab` — "
            "the one leg where the two paths part (dEok 0.0443). Compose the stops "
            "as a custom property and swap only the path, the way .material-rake "
            "and .text-foil do."]


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

    # --- the CSS half. One props map across all three files, because the
    #     ramps are declared in tokens.css and consumed in the other two.
    css = [(name, (DS / "assets" / "css" / name).read_text(encoding="utf-8"))
           for name in CSS]
    props = custom_props([t for _, t in css])

    parsed, css_seen, unresolved = [], 0, 0
    for name, text in css:
        for fn, stops, has_oklab, stop_text in css_gradients(text, props):
            css_seen += 1
            unresolved += sum(1 for s in stops if s is None)
            parsed.append((name, fn, stops, has_oklab, stop_text))

    # Which stop lists exist anywhere on the oklab path. Keyed on the stop text
    # itself so a ramp and its twin are the same ramp by construction, which is
    # what the "compose the stops once, swap only the path" idiom guarantees.
    on_oklab = {stop_text for _, _, _, has_oklab, stop_text in parsed if has_oklab}

    for name, fn, stops, has_oklab, stop_text in parsed:
        opaque = [s for s in stops if s is not None and s[1] >= ALPHA_OPAQUE]
        problems = (check_near_miss([(0, s[0]) for s in opaque])
                    + check_arc(stops)
                    + check_path(name, stops, has_oklab, stop_text in on_oklab))
        if args.verbose:
            mark = "FAIL" if problems else "ok  "
            print("%s %-42s css %-16s %s" % (
                mark, "assets/css/" + name, fn + ("+oklab" if has_oklab else ""),
                " ".join(s[0] if s else "?" for s in stops)))
        for p in problems:
            failures.append("assets/css/%s  %s: %s" % (name, fn, p))

    if failures:
        print("\nThe light family has drifted in %d place%s:\n"
              % (len(failures), "" if len(failures) == 1 else "s"), file=sys.stderr)
        for f in failures:
            print("  " + f, file=sys.stderr)
        print("\nSee foundations/colors.html#the-arc and the SVG CANNOT DO THIS "
              "block in tokens.css.", file=sys.stderr)
        return 1

    print("%d SVG gradients and %d CSS gradients, one family." % (seen, css_seen))
    # Named rather than passed over in silence, the way the glass budget names
    # a selector it cannot count: a stop this script cannot read is a stop it
    # is making no claim about, and a rule with a silent hole in it trains
    # people to ignore it.
    if unresolved:
        print("%d CSS stop%s could not be resolved to a colour — a color-mix(), or a "
              "var() declared outside the three stylesheets. No claim is made about "
              "%s." % (unresolved, "" if unresolved == 1 else "s",
                       "it" if unresolved == 1 else "them"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
