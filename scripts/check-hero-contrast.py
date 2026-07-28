#!/usr/bin/env python3
"""Recompute what the hero's type actually reads against, frame by frame.

The thirty-fourth check, and the second half of a pair. check-hero-scrim.py
holds the scrim's GEOMETRY — that the plateau follows the content column, at
the projection --angle-a implies — and says plainly why it stops there: "a
table measured with a decoder nothing in CI has is exactly the kind that rots
quietly", so it keeps the photometry in a comment and checks the arithmetic
the measurements were taken under. This one carries the photometry, reduced to
the only thing the arithmetic needs, and recomputes the ratios themselves.

WHAT THE GEOMETRY CHECK CANNOT SEE. Its register is widths — correctly, in its
own words: "heights are irrelevant to the reach -- it is a horizontal
displacement projected onto the axis". They are not irrelevant to the ARTWORK.
.cf-hero__media covers with a 1080 px square, so which part of that square
lands under the type is decided by the box's ASPECT, and the box's aspect
moves with the viewport's height as much as with its width. That axis had
never been sampled, and on it the 11 px kicker was failing AA:

      375x740   4.03     800x800   4.25     1024x768  13.25
      375x812   4.03     860x800   4.14     1024x800  13.35
      375x844   4.01     900x800   4.15     1152x800  13.58
      375x896   4.44     768x800   4.37     1280x800  13.67
                         768x1024  8.13     1440x900  14.73

Nine frames under a 4.5:1 floor that the width-only table put at 6.08 and
above. The cliff is 56.25rem, where .cf-hero__action leaves the flow and the
media box goes from 567 px tall to 624: below it the kicker sits low in a
short hero on the square's dark bottom band, above it the hero is tall enough
that the kicker is on the lit middle. --scrim-depth answers it, and this
script is what keeps the answer true.

WHAT THIS KNOWS THAT A SCREENSHOT CANNOT. The failure was 4.03:1 where 4.5:1
was required: about six levels of grey under an 11 px line, on some frames of
a loop and not others, at some viewport heights and not others. It is not
visible, and it is barely photographable — you have to hide the type, hold the
loop still, and already know which frame and which frame size to hold it at.
It is exactly computable, and this computes it.

HOW THE REGISTER IS BUILT, and how to rebuild it. Each `art` triple is the
rendered page with the type set to transparent and .cf-hero__media::after's
background removed, screenshotted at that frame, once per artwork — the poster
plus 24 frames of the loop at 2 fps — keeping the darkest value each sample
point ever took. Sample points are the glyph runs themselves, from
Range.getClientRects(), and a point is dropped if elementFromPoint puts
anything opaque between the type and the artwork, so the pause switch and the
logo plate cannot be mistaken for a dark backdrop. `media` is
.cf-hero__media's own box at that frame, a layout fact this file cannot derive
and therefore records. Same shape as check-contrast.py's register and the
breakpoint register: hand-kept, its value not that it is complete but that
what is on it can never rot silently. Re-measure when the artwork, the poster,
the hero's geometry or the type's size changes; nothing else moves it.

WHY SEVERAL POINTS PER ROW AND NOT THE DARKEST ONE. The worst COMPOSITED pixel
is not the darkest: the scrim's alpha falls along its axis, so a lighter pixel
further out can come off worse than a darker pixel deep in the plateau, and
which of the two binds depends on the depth — the very number a person
retuning this would be changing. So each row carries its points' Pareto
frontier: a point is kept unless another is BOTH darker AND further along the
axis. The composited value rises with the raw pixel and with the alpha, and
the alpha falls monotonically with distance, so the worst pixel for ANY
monotone scrim is on that frontier. The register stays correct across a
retune instead of only describing today's.

Everything else is read out of tokens.css as it ships and recomputed: the
angle, the reach including the column term and the gutter's own clamp, the
depth at both breakpoints, the scrim's colour, and --hero-dissolve, which
masks the ::after along with the artwork it lies on and so thins the scrim
exactly where the hero fades out. Ratios are taken from the RENDERED
INTEGERS, the rounding check-contrast.py documents, because the unquantized
figure is the wrong one to quote.

Floors are WCAG 2.x AA: 3:1 for the headline, large text at every frame here,
and 4.5:1 for the kicker and the rule that is its border-top.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-hero-contrast.py       # check, exit 1 on a failure
    python3 scripts/check-hero-contrast.py -v    # print every computed ratio
"""

import argparse
import math
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOKENS = ROOT / "design-system" / "assets" / "css" / "tokens.css"

# The root font size every rem here resolves against. base.css never changes it
# and check-viewport-zoom.py holds the pages to that.
REM = 16.0

# -- the register -----------------------------------------------------------
# ((viewport w, h), element, floor, .cf-hero__media's box, [(artwork rgb, x, y,
# frame), ...]) with x / y inside the media box. f001..f024 are the loop at
# 2 fps; "poster" is hero-poster.jpg, which is what a browser paints before the
# first frame decodes and the only frame a prefers-reduced-motion reader is
# ever shown -- it is among the failing ones, which is why it is sampled at all.

REGISTER = [
    ((375, 812), ".cf-hero__title", 3.0, (375, 501), [
        ((26, 26, 30), 123, 84, "f012"),
        ((34, 33, 42), 329, 248, "f023"),
    ]),
    ((375, 812), ".cf-hero__kicker", 4.5, (375, 501), [
        ((37, 38, 43), 181, 346, "f005"),
    ]),
    ((375, 896), ".cf-hero__title", 3.0, (375, 562), [
        ((27, 28, 33), 261, 321, "f023"),
        ((35, 36, 41), 329, 354, "f023"),
    ]),
    ((375, 896), ".cf-hero__kicker", 4.5, (375, 562), [
        ((46, 47, 49), 27, 426, "f024"),
        ((53, 52, 62), 39, 432, "f024"),
    ]),
    ((768, 800), ".cf-hero__title", 3.0, (768, 567), [
        ((26, 30, 34), 568, 267, "f023"),
        ((31, 31, 32), 582, 255, "f023"),
        ((31, 32, 37), 596, 251, "f023"),
    ]),
    ((768, 800), ".cf-hero__kicker", 4.5, (768, 567), [
        ((45, 47, 52), 365, 425, "f005"),
    ]),
    ((768, 1024), ".cf-hero__title", 3.0, (768, 791), [
        ((18, 19, 24), 358, 539, "f006"),
        ((31, 32, 37), 589, 499, "f023"),
        ((34, 33, 40), 596, 503, "f023"),
        ((40, 38, 50), 596, 483, "f023"),
        ((41, 41, 53), 596, 475, "f023"),
    ]),
    ((768, 1024), ".cf-hero__kicker", 4.5, (768, 791), [
        ((117, 119, 130), 190, 648, "f024"),
    ]),
    ((900, 800), ".cf-hero__title", 3.0, (900, 567), [
        ((31, 31, 45), 346, 240, "f023"),
        ((34, 38, 42), 634, 275, "f023"),
        ((39, 40, 45), 642, 270, "f023"),
        ((44, 44, 56), 642, 255, "f022"),
    ]),
    ((900, 800), ".cf-hero__kicker", 4.5, (900, 567), [
        ((40, 40, 52), 519, 423, "f023"),
    ]),
    ((1024, 768), ".cf-hero__title", 3.0, (1024, 624), [
        ((28, 29, 34), 649, 387, "f023"),
    ]),
    ((1024, 768), ".cf-hero__kicker", 4.5, (1024, 624), [
        ((182, 187, 191), 183, 560, "f023"),
        ((184, 187, 191), 190, 562, "f023"),
    ]),
    ((1280, 800), ".cf-hero__title", 3.0, (1280, 656), [
        ((31, 31, 49), 399, 449, "f011"),
        ((33, 45, 49), 589, 354, "f011"),
    ]),
    ((1280, 800), ".cf-hero__kicker", 4.5, (1280, 656), [
        ((188, 193, 198), 113, 592, "f010"),
    ]),
    ((1440, 900), ".cf-hero__title", 3.0, (1440, 756), [
        ((34, 33, 42), 448, 519, "f010"),
        ((30, 39, 43), 591, 444, "f011"),
    ]),
    ((1440, 900), ".cf-hero__kicker", 4.5, (1440, 756), [
        ((197, 201, 203), 94, 692, "f010"),
    ]),
]


# -- reading the tokens -----------------------------------------------------

def decl(name, css, scope=None):
    """One custom property's value: brace-balanced, comments stripped."""
    hay = css
    if scope is not None:
        m = re.search(r"@media\s*\(\s*max-width\s*:\s*" + re.escape(scope)
                      + r"\s*\)\s*\{(.*?)\n\}", css, re.S)
        if not m:
            return None
        hay = m.group(1)
    m = re.search(r"^\s*%s\s*:" % re.escape(name), hay, re.M)
    if not m:
        return None
    i, depth, out = m.end(), 0, []
    while i < len(hay):
        ch = hay[i]
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
    """clamp(<rem>, <vw>, <rem>) -- the one shape --gutter uses."""
    m = re.fullmatch(r"clamp\(\s*([\d.]+)rem\s*,\s*([\d.]+)vw\s*,\s*([\d.]+)rem\s*\)",
                     expr.strip())
    if not m:
        raise ValueError("--gutter is no longer clamp(<rem>, <vw>, <rem>): %r" % expr)
    lo = float(m.group(1)) * REM
    mid = float(m.group(2)) / 100.0 * vw
    hi = float(m.group(3)) * REM
    return min(max(lo, mid), hi)


class Scrim(object):
    """--hero-scrim, --scrim-reach, --scrim-depth and --hero-dissolve, resolved."""

    def __init__(self, css):
        self.css = css
        angle = decl("--angle-a", css)
        m = re.fullmatch(r"([\d.]+)deg", (angle or "").strip())
        if not m:
            raise ValueError("--angle-a is not a plain <deg>: %r" % angle)
        self.angle = math.radians(float(m.group(1)))
        self.sin, self.cos = math.sin(self.angle), math.cos(self.angle)

        self.colour = self._colour()
        self.wide, self.narrow, self.threshold = self._depths()
        self.reach_raw = decl("--scrim-reach", css)
        if self.reach_raw is None:
            raise ValueError("--scrim-reach is gone")
        self.gutter_raw = decl("--gutter", css)
        cmax = decl("--container-max", css)
        m = re.fullmatch(r"([\d.]+)rem", (cmax or "").strip())
        if not m:
            raise ValueError("--container-max is not a plain <rem>: %r" % cmax)
        self.container_max = float(m.group(1)) * REM
        self.dissolve = self._dissolve()

    def _colour(self):
        """The scrim's tint, and the assertion that BOTH plateau stops are the
        token and not a literal.

        Worth asserting rather than assuming: with only one of them named, the
        narrow override lifts one end of the plateau and leaves the other, so
        what ships is a ramp from 0.42 to 0.5 while this file goes on modelling
        a flat run -- and reports the flat number. A check that reads half of
        what it checks proves nothing about the other half.
        """
        grad = decl("--hero-scrim", self.css)
        if grad is None:
            raise ValueError("--hero-scrim is gone")
        # the alpha may itself be a var(), so it is matched as "anything that is
        # not a paren, or a whole var(...)" rather than [^)]+, which would stop
        # inside var(--scrim-depth) and compare a truncated string forever after
        stops = re.findall(r"rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,"
                           r"\s*((?:var\([^()]*\)|[^()])+)\)", grad)
        if len(stops) != 3:
            raise ValueError("--hero-scrim has %d rgba() stops, not the 3 this "
                             "register's arithmetic describes" % len(stops))
        alphas = [s[3].strip() for s in stops]
        if alphas[:2] != ["var(--scrim-depth)", "var(--scrim-depth)"]:
            raise ValueError("--hero-scrim's plateau stops are %r, not both "
                             "var(--scrim-depth). A literal at either end turns "
                             "the plateau into a ramp the moment the narrow "
                             "override moves the other, and nothing here would "
                             "notice." % (alphas[:2],))
        if float(alphas[2]) != 0.0:
            raise ValueError("--hero-scrim's last stop is alpha %s, not 0. The "
                             "scrim has to be OUT at twice the reach."
                             % alphas[2])
        tints = {s[:3] for s in stops}
        if len(tints) != 1:
            raise ValueError("--hero-scrim mixes %d tints; it is CF-Grau and "
                             "nothing else" % len(tints))
        if "var(--scrim-reach)" not in grad:
            raise ValueError("--hero-scrim no longer takes its stop positions "
                             "from --scrim-reach, so recomputing the reach here "
                             "would prove nothing about what ships")
        return tuple(int(v) for v in stops[0][:3])

    def _depths(self):
        wide = decl("--scrim-depth", self.css)
        if wide is None:
            raise ValueError("--scrim-depth is gone; --hero-scrim's weight is "
                             "no longer a token this file can read")
        m = re.search(r"@media\s*\(\s*max-width\s*:\s*([\d.]+)rem\s*\)\s*\{"
                      r"[^{]*\{[^}]*--scrim-depth\s*:\s*([\d.]+)", self.css, re.S)
        if not m:
            raise ValueError(
                "nothing deepens --scrim-depth on a narrow hero any more. Below "
                "56.25rem the media box is 567 px tall, cover puts the square "
                "artwork's dark band under the type, and at 0.42 the 11 px "
                "kicker reads 4.03:1 at 375 x 812 against a 4.5:1 floor.")
        return float(wide), float(m.group(2)), float(m.group(1)) * REM

    def _dissolve(self):
        """--hero-dissolve as (fraction of the hero's height, mask alpha).

        The mask is on .cf-hero__media, so it takes the ::after scrim away at
        the same rate it takes the artwork away -- which the token's own note
        says is the point of putting the scrim inside the media box.
        """
        grad = decl("--hero-dissolve", self.css)
        start = decl("--dissolve-start", self.css)
        if grad is None or start is None:
            raise ValueError("--hero-dissolve or --dissolve-start is gone")
        stops = [(0.0, 1.0), (float(start.rstrip("% ")) / 100.0, 1.0)]
        for a, pct in re.findall(r"rgba\(0,\s*0,\s*0,\s*([\d.]+)\)\s*([\d.]+)%",
                                 grad):
            stops.append((float(pct) / 100.0, float(a)))
        stops.append((1.0, 0.0))
        return sorted(stops)

    def depth(self, vw):
        return self.narrow if vw <= self.threshold else self.wide

    def reach(self, vw, w, h):
        """--scrim-reach in pixels for a W x H media box at viewport width vw.

        A percentage stop is a percentage of the GRADIENT LINE, whose length is
        |W sin A| + |H cos A| -- the fact --scrim-reach is written as a min()
        for. The second term is the content column's displacement past
        --container-max, projected onto the axis; see check-hero-scrim.py,
        which is what holds that term's SHAPE. This only evaluates it.
        """
        m = re.search(r"min\(\s*([\d.]+)rem\s*,\s*([\d.]+)%\s*\)", self.reach_raw)
        if not m:
            raise ValueError("--scrim-reach no longer opens with min(<rem>, <%>): "
                             "%r" % self.reach_raw)
        line = abs(w * self.sin) + abs(h * self.cos)
        out = min(float(m.group(1)) * REM, float(m.group(2)) / 100.0 * line)
        shift = re.search(r"([\d.]+)\s*\*\s*max\(\s*0px\s*,\s*\(\s*100vw", self.reach_raw)
        if shift:
            out += float(shift.group(1)) * max(
                0.0, (vw - self.container_max) / 2.0 - clamp_px(self.gutter_raw, vw))
        return out, line

    def mask(self, fy):
        prev = self.dissolve[0]
        for stop, a in self.dissolve[1:]:
            if fy <= stop:
                if stop == prev[0]:
                    return a
                return prev[1] + (fy - prev[0]) / (stop - prev[0]) * (a - prev[1])
            prev = (stop, a)
        return 0.0

    def alpha(self, t, reach, depth, fy):
        if t <= reach:
            a = depth
        elif t >= 2 * reach:
            a = 0.0
        else:
            a = depth * (1.0 - (t - reach) / reach)
        return a * self.mask(fy)


# -- the arithmetic ---------------------------------------------------------

def over(scrim, alpha, art):
    """The scrim composited over one artwork pixel, QUANTIZED to the integers
    that reach the screen -- the rounding check-contrast.py documents."""
    return tuple(round(scrim[i] * alpha + art[i] * (1 - alpha)) for i in range(3))


def luminance(c):
    def channel(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return (0.2126 * channel(c[0]) + 0.7152 * channel(c[1])
            + 0.0722 * channel(c[2]))


def ratio(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = (la, lb) if la > lb else (lb, la)
    return (hi + 0.05) / (lo + 0.05)


BLACK = (0, 0, 0)


def audit(scrim, verbose):
    findings, table = [], []
    for (vw, vh), sel, floor, (mw, mh), points in REGISTER:
        depth = scrim.depth(vw)
        reach, line = scrim.reach(vw, mw, mh)
        worst = None
        for art, x, y, frame in points:
            t = x * scrim.sin + (mh - y) * scrim.cos
            a = scrim.alpha(t, reach, depth, y / float(mh))
            bg = over(scrim.colour, a, art)
            r = ratio(bg, BLACK)
            if worst is None or r < worst[0]:
                worst = (r, bg, art, frame, a)
        table.append((vw, vh, sel, floor, depth, reach, line, worst))
        if worst[0] < floor:
            findings.append(
                "%s at %dx%d renders %.2f:1 against a floor of %.1f:1. The "
                "darkest backdrop the loop puts under it at that frame is "
                "rgb%s (%s), and --scrim-depth %.2f lifts it only to rgb%s. "
                "tokens.css derives the depth from exactly this pixel."
                % (sel, vw, vh, worst[0], floor, worst[2], worst[3], worst[4],
                   worst[1]))
    if verbose:
        print("  --scrim-depth %.2f, and %.2f at or below %.5grem; scrim rgb%s "
              "at %.5gdeg" % (scrim.wide, scrim.narrow, scrim.threshold / REM,
                              scrim.colour, math.degrees(scrim.angle)))
        for vw, vh, sel, floor, depth, reach, line, w in table:
            print("  %4dx%-4d %-18s %6.2f:1  (floor %.1f, depth %.2f, reach %.0f "
                  "of a %.0f px line, rgb%s -> rgb%s on %s at a=%.3f)"
                  % (vw, vh, sel, w[0], floor, depth, reach, line, w[2], w[1],
                     w[3], w[4]))
        print()
    return findings


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print every computed ratio, not only the failures")
    args = ap.parse_args()

    rel = TOKENS.relative_to(ROOT)
    try:
        findings = audit(Scrim(TOKENS.read_text(encoding="utf-8")), args.verbose)
    except ValueError as exc:
        print("%s  %s" % (rel, exc), file=sys.stderr)
        return 1

    if findings:
        for why in findings:
            print(why, file=sys.stderr)
        print("\n%d hero contrast finding%s."
              % (len(findings), "" if len(findings) == 1 else "s"),
              file=sys.stderr)
        return 1

    pts = sum(len(p) for _, _, _, _, p in REGISTER)
    print("hero contrast: %d element/frame pairs over %d measured backdrop "
          "pixels, recomputed from tokens.css, and every floor holds."
          % (len(REGISTER), pts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
