"""The share plate: one 1200 x 630 raster per route, drawn from that route's own path.

WHAT A SHARE PLATE IS FOR HERE. It is the picture a consumer renders beside the
title when somebody pastes a Control-F address into LinkedIn, Slack, Teams,
Discord or a message. For a company whose readers pass its writing to each
other it is the most-seen brand surface there is, and until this module it was
blank — every link unfurled as a bare address.

THE PLATE CARRIES THE MARK, NOT THE HEADLINE, and that is a decision rather
than a shortcut. Every consumer of `og:image` renders `og:title` as text
immediately beside the image, at the reader's own size, in the reader's own
typeface, wrapped by the reader's own client. A plate that ALSO sets the title
inside the picture publishes the same sentence twice, at a size nobody chose,
hyphenated by nobody — and this site's headlines are German compounds
("Flexibilitäts-Asset", "Verteilnetz") that a 1200 px plate breaks badly and
silently. So the plate does the one thing the text beside it cannot: it says
whose link this is, before a word is read, and it says it differently for every
route. That is what the signet is for, and foundations/share.html argues it at
length.

  the wash        the page's own ground, CF-Grau to white, read off tokens.css
  the lattice     the 2:1 isometric grid the object is built on, run to all
                  four edges — the manual's `grid-isometry` plate as a field
  the ground      one full-bleed hairline; everything on the plate stands on it
  the object      the route's signet, at the lattice's own cell
  the light       the one lit face, the plate's single lime moment
  the logo        the horizontal lockup, standing on the same line

Six layers, and they are the six the manual names: base wash, opaque, frosted
glass (not used here — a plate has nothing to see through), contour, light,
text (the logotype, which is drawn as outlines and is the only "text" a plate
is allowed).

WHY THE LATTICE RUNS OFF THE EDGE AND THE FRAME DOES NOT EXIST. Consumers crop.
X takes 16:9 out of the middle of a 1.91:1 plate; square thumbnails happen. A
drawn frame inset from the edge is the one graphic that looks BROKEN when it is
clipped, so there is none — the lattice and the ground rule are full-bleed and
survive any crop, and the two things that must not be lost, the object and the
logotype, are kept inside the middle 1200 x 470 that every crop in use keeps.
"""

import os
import re
import sys

# The directory is `og-plate`, which is not an importable package name — the
# same shape scripts/news-objects/ and scripts/expertise-objects/ already have,
# and the same answer: put the directory on the path and import the modules.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import raster                                                     # noqa: E402
import signet                                                     # noqa: E402
from raster import Canvas, Gradient, hex_rgb                       # noqa: E402

WIDTH, HEIGHT = 1200, 630

# The ground line. Everything on the plate stands on it, and the band under it
# is the apron the manual gives every object.
GROUND_Y = 545.0

# The object. `SCALE` maps the signet's 120-unit viewBox onto the plate, and it
# is also the lattice's cell size — 36 x 18 viewBox units become 122.4 x 61.2 px
# — so the grid the object stands on is provably the grid it is built from.
SCALE = 4.3
OBJECT_CX = 800.0

# The logotype, lower left. 380 px is set by the minimum size on
# foundations/logo.html — 120 px for the horizontal lockup — held at the
# smallest scale a consumer renders this plate at: a 400 px feed thumbnail is
# a third of the plate's width, and 380 / 3 is 127.
#
# CLEAR SPACE IS DERIVED, NOT PICKED. The chapter builds the lockup on X, "the
# height of one bar of the symbol", and asks for 4X around it. Measured off
# cf-symbol-black.svg the bar is 120 units of the 480-unit frame, so 4X is
# exactly the lockup's own height — which is the gap kept here, from the ground
# rule below it and from the object beside it.
LOGO_LEFT = 112.0
LOGO_WIDTH = 380.0

INK = (0, 0, 0)
LATTICE_ALPHA = 0.13
LATTICE_HORIZON = 130.0    # above this the grid is gone; below it, it fades in
GROUND_ALPHA = 0.55
CONTOUR_ALPHA = 0.9

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOKENS = os.path.join(REPO, "design-system", "assets", "css", "tokens.css")
LOGO = os.path.join(REPO, "design-system", "assets", "img", "logo",
                    "cf-logo-horizontal-black.svg")


# ---------------------------------------------------------------------------
# The wash, re-derived rather than quoted

_VAR = re.compile(r"^\s*(--[a-z0-9-]+):\s*([^;]+);", re.M)


def wash_stops(path=TOKENS):
    """`--wash-stops` from tokens.css, with its two calc() positions resolved.

    The token is written as three hexes and a white, and two of the four
    positions are calc()s over `--spectrum-*-n` and `--rake-near-n` — the wash
    borrows the foil's geometry rather than restating it. Resolving them here
    rather than pasting four numbers is what stops the plate and the page from
    quietly drawing two different grounds the day somebody moves the foil.
    """
    src = open(path, "r", encoding="utf-8").read()
    nums = {}
    for name, value in _VAR.findall(src):
        v = value.strip()
        if re.fullmatch(r"-?\d+(\.\d+)?", v):
            nums[name] = float(v)
    hot = nums["--spectrum-hot-n"]
    cool = nums["--spectrum-cool-n"]
    near = nums["--rake-near-n"]
    span = 100.0 - hot                     # --spectrum-span-n, as tokens.css writes it

    block = re.search(r"--wash-stops:\s*(.*?);", src, re.S).group(1)
    hexes = re.findall(r"#[0-9A-Fa-f]{6}", block)
    if len(hexes) != 3:
        raise ValueError("--wash-stops no longer holds exactly three literals")

    white = re.search(r"--grey-000:\s*(#[0-9A-Fa-f]{6})", src).group(1)
    return [
        (0.0, hexes[0]),
        ((100.0 - (cool - hot) / span * 100.0) / 100.0, hexes[1]),
        ((100.0 - (near - hot) / span * 100.0) / 100.0, hexes[2]),
        (1.0, white),
    ]


# ---------------------------------------------------------------------------
# Layers

def _lattice(cv):
    """The 2:1 isometric grid, run to all four edges.

    Two families of parallel lines at +/-26.57 deg, on the object's own cell, and
    phased so a lattice line passes through the object's centre plot. Nothing
    else on the plate needs to know where the grid is; the object does, and it
    is the reason the two are locked together rather than merely adjacent.
    """
    cell_w, cell_h = signet.W * SCALE, signet.H * SCALE
    # The lattice's origin is the object's own centre plot, so grid and object
    # cannot drift apart when either number moves.
    ox = OBJECT_CX
    oy = GROUND_Y - (114 - signet.CY) * SCALE

    slope = cell_h / cell_w                 # tan(26.57 deg) = 1/2, by construction
    reach = WIDTH * slope + HEIGHT

    def ink(row):
        # The grid fades in downwards, so the plate has a sky and a ground
        # rather than graph paper over both. The horizon is where the tallest
        # tower a seed can raise stops, so no object is ever drawn on nothing.
        if row <= LATTICE_HORIZON:
            return 0.0
        if row >= GROUND_Y:
            return LATTICE_ALPHA
        t = (row - LATTICE_HORIZON) / (GROUND_Y - LATTICE_HORIZON)
        return LATTICE_ALPHA * t * t

    def family(sign):
        # c is the line's intercept at x = ox. Stepping c by one cell height
        # steps the family by one lattice row.
        c = -reach
        while c <= reach:
            y0 = oy + c + sign * slope * (0 - ox)
            y1 = oy + c + sign * slope * (WIDTH - ox)
            if max(y0, y1) >= -2 and min(y0, y1) <= HEIGHT + 2:
                cv.stroke([(0.0, y0), (float(WIDTH), y1)], INK,
                          width=1.0, close=False, alpha=ink)
            c += cell_h * 2                 # every second row: one line per cell

    family(+1)
    family(-1)


def _object(cv, seed):
    """The route's signet, at SCALE, standing with its front plot on GROUND_Y."""
    ox = OBJECT_CX - signet.CX * SCALE
    oy = GROUND_Y - 114 * SCALE             # 114 is the front plot's bottom vertex

    def to_plate(pts):
        return [(ox + px * SCALE, oy + py * SCALE) for px, py in pts]

    grey = {"top": hex_rgb(signet.FACE_TOP),
            "left": hex_rgb(signet.FACE_LEFT),
            "right": hex_rgb(signet.FACE_RIGHT)}

    for face in signet.faces(seed, lit=True):
        kind = face["kind"]
        if kind == "plot":
            # An empty plot is there and nothing stands on it. On screen that
            # outline is dashed; a 1 px dash at this scale reads as a grey line
            # and nothing else, so the plate draws it at half the contour's ink
            # instead. Same distinction, one register down.
            cv.stroke(to_plate(face["points"]), INK, width=1.4,
                      alpha=CONTOUR_ALPHA * 0.5)
        elif kind in grey:
            pts = to_plate(face["points"])
            cv.fill(pts, grey[kind])
            cv.stroke(pts, INK, width=1.6, close=True, alpha=CONTOUR_ALPHA)
        elif kind == "lit":
            pts = to_plate(face["points"])
            p0, p1 = signet.ramp_axis(face["x"], face["top"])
            axis = [(ox + p[0] * SCALE, oy + p[1] * SCALE) for p in (p0, p1)]
            cv.fill(pts, Gradient(axis[0], axis[1], signet.STOPS))
            cv.stroke(pts, INK, width=1.6, close=True, alpha=CONTOUR_ALPHA)
        elif kind == "dot":
            cx, cy, r = face["at"]
            cv.fill(raster.circle(ox + cx * SCALE, oy + cy * SCALE, r * SCALE * 0.62),
                    INK)


def logo_box():
    """Where the lockup lands, and the clear space it keeps. (x, y, w, h, clear)"""
    vb = raster.svg_outlines(LOGO)[1]
    s = LOGO_WIDTH / vb[2]
    h = vb[3] * s
    return LOGO_LEFT, GROUND_Y - h - h, LOGO_WIDTH, h, h


def _logo(cv):
    """The horizontal lockup, lower left, one clear space above the ground rule."""
    contours, vb = raster.svg_outlines(LOGO)
    vw, vh = vb[2], vb[3]
    s = LOGO_WIDTH / vw
    ox = LOGO_LEFT - vb[0] * s
    oy = logo_box()[1] - vb[1] * s
    placed = [[(ox + x * s, oy + y * s) for x, y in c] for c in contours]
    cv.fill_many(placed, INK)


def render(seed):
    """One plate. `seed` is the route's own path — see build-og-plates.py."""
    cv = Canvas(WIDTH, HEIGHT)
    cv.wash(wash_stops())
    _lattice(cv)
    _object(cv, seed)
    cv.stroke([(0.0, GROUND_Y), (float(WIDTH), GROUND_Y)], INK,
              width=1.6, close=False, alpha=GROUND_ALPHA)
    _logo(cv)
    return cv
