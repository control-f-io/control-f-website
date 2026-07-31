#!/usr/bin/env python3
"""Generate the prototype's full-screen sensor field, on brand angles.

THE BRIEF THAT FORCED THE SECOND GENERATOR. The statement field this page
carried was the landing page's: a 1200 x 288 strip inside the figure column,
two tight clusters of glows around a void. The review of 2026-07-28 asked for
the opposite composition in three clauses — the grid should cover the whole
screen, the gradient dots should STREAM FROM THE CORNERS into their grid
positions and then pulse and merge, and the glows should stop crowding
("let not bubble it so close together"). That is a different drawing with a
different law, and scripts/gen-stmt-field.py keeps owning the statement
component's copy unchanged.

TWO PAGES, AND THE SECOND ONE SHIPS. This file was written for the prototype
and named for it, and then the five acts were ported to
design-system/patterns/landing-page.html and took the drawing with them —
lattice, sensors and callouts, 220 lines, byte for byte. The port copied the
markup and the sentence that stands over it ("Contents are GENERATED, NOT
TYPED ... --check holds the shipped markup to it") and did not copy the
ownership: PAGE was one path, so --check read the prototype and the shipping
page's field was held to nothing.

Measured on main before this change, by moving one sensor's crossing
(--cx:816 -> 800) and one lattice line (x1 1520 -> 1500) in landing-page.html
and running the whole suite — 105 check-* scripts plus all four generators'
--check: 0 failures. The lab was gated and the page was not, which is the
inversion of what the two files are for. The landing page also carries the
acts' only shipping copy of this drawing, so a hand edit there is a hand edit
to production with the sentence above it still claiming a generator.

PAGES is the list now, which is the shape scripts/gen-stmt-field.py already
uses for the same reason, and both files are spliced and checked in one pass.
The two copies were identical on the day this landed; the point is that they
stay that way by construction rather than by anyone remembering.

THE LAW. One lattice, one supergrid, one focus.

  THE LATTICE is the same 2:1 isometry at the same phase as the statement
  field — lines y = +-x/2 + c and the level step, c and y on the 32-module,
  the whole angle vocabulary the system allows (foundations/geometry.html:
  0, 26.57, 45, 63.43, 90) — drawn edge to edge over a 1600 x 900 box that
  the stage crops with `slice`, so the ground reaches every corner of every
  viewport instead of stopping at a column edge.

  THE SENSORS sit on lattice intersections and nowhere else: crossings of the
  two diagonal families are x == 0 (mod 32), y == 8 (mod 16), and every glow
  is on one. Of those crossings the field takes a SUPERGRID — every eighth
  column (256), every tenth row (160), odd rows shifted half a super-column
  (128) — so nearest neighbours stand hypot(128, 160) = 204.9 units apart,
  4.6x the old field's 44.7. The crowding the review named was the old law's
  bar (glows had to overlap to merge); this field merges at one point at the
  end instead, so the spacing is free to breathe and does.

  THE FOCUS is (800, 264): the crossing that stands over the root trunk's
  head at the design ratio, this drawing's analogue of the void the old field
  shared with the root. Radius, opacity and the ramp fall out of distance to
  it and nothing else — r = 9 + 17 x (1 - d/d_max), opacity 0.68..0.95 on the
  same slope quantised to the hundredth, the hot lime-core ramp above r 21 —
  so the field is hottest where the data will funnel and coolest at the rim.
  The exact merge point is measured at runtime (the trunk lives in another
  svg in the column flow) and published as --ux/--uy on the field; the focus
  is the LAW's stand-in and the var()'s fallback.

  A SENSOR IS TWO ELEMENTS: A HALO AND A BEAD. It used to be one soft disc —
  a radial ramp running to stop-opacity 0 at the rim, no contour, resting
  between 0.2 and 0.6 — and nineteen of the twenty-three had CF-Grau at their
  centre against a CF-Grau page, so they rendered as smudges the eye could not
  find. foundations/illustration.html states that fault in one line: "an unlit
  face sits at exactly the page's own colour and the object would disappear
  entirely if the contour were not carrying it".

  THE BEAD is the body: the family's ramp, a contour, and the drop's own
  outline. Its radius is 9..26 where the old disc's was 12..40, because the
  reach moved out to the halo. Its contour is --border-strong — CF-Schwarz,
  the token .lp-flow__seg strokes with — on the review's instruction that the
  border be "black like the root system", and the ramp runs the brand's whole
  cool half, lime or Glas at the core through Sky at the rim.

  THE HALO is the spill: one static circle at 2.6x the bead, painted with a
  gradient rather than filtered. It was a drop-shadow and could not stay one —
  a filter re-rasterizes when its source changes, and the source became a path
  that changes every frame; the two together cost 25 fps of a 61 fps budget,
  each alone free. Splitting them also keeps the black contour crisp, which a
  Gaussian over it does not.

  AND IT MOVES LIKE THE LIQUID IT IS NAMED FOR. What animates is the bead's
  `d`: a closed six-segment curve whose vertex radii are two travelling
  harmonics, morphing between four states and back to the first. It was a
  two-axis scale, which conserves volume and reads as breathing but can only
  reach ELLIPSES — the review's answer was "even out of the sphere shape".
  Each bead carries --wp, its own period, and --w, its own phase: the period
  from its own radius on the r^1.5 surface-tension law, so the big beads at
  the focus swing slowly and the small ones at the rim quiver, and the phase
  from a stride through the slot order coprime with the count. Each also gets
  its OWN keyframe set, twenty-one of them, because one set with per-bead
  delays is one sphere morphing twenty-one times.

  THE APPROACH: each glow belongs to its nearest box corner and opens the act
  200 units beyond it — outside every crop the slice can produce (the widest
  admitted viewport ratio costs 80 units a side) — so the streams read as
  entering from off-screen at the four corners, not popping at the bezel.
  --fx/--fy is that run, --m the glow's slot (distance to focus over d_max,
  to the tenth): the core seeds first and the field grows outward, and the
  merge later runs back in the same order.

  THE CLAIM'S REACH: no sensor stands in x >= 920, 180 <= y <= 680 — the
  right-column claim's box, the same argument the old #cf-stmt-reach mask
  made, made by placement instead of by masking, because a glow behind the
  claim is contrast debt and a mask over a full-screen field is a window
  sliding across the page.

  THE BAND USED TO START AT 360, AND THAT WAS NOT THE CLAIM'S BOX. It was the
  claim's box AT THE DESIGN RATIO, and the claim does not stay there: the
  field is sliced, so it scales with the viewport, while the text is laid out
  in CSS pixels and moves the other way. Measured at the eleven viewports the
  gate admits, the claim's glyph lines run field y 181..569 and the band
  started 180 units below their top — so the whole upper row of the field sat
  ON the heading. Two beads did it at eight and four viewports of the eleven,
  and neither was visible enough for anyone to notice until the beads became
  bodies. Extending the band to 180 drops exactly those two.

  ONE OVERLAP IS LEFT AND IT IS DELIBERATE. (816, 248) — the largest bead,
  the one that stands at the focus — touches the heading's first line at
  1024 x 720 and nowhere else. Reaching it needs x >= 810, which also takes
  (960, 416) and leaves the field's whole centre-right empty; the drawing
  would lose its anchor at every viewport to fix one. 1024 x 720 is the
  gate's own minimum, where the claim wraps at its widest.

DETERMINISTIC. No randomness, no seed: the output is a function of the
constants below. Re-run it and the same markup comes out.

    python3 scripts/gen-proto-field.py --check     # the shipped markup is ours
    python3 scripts/gen-proto-field.py --write     # regenerate
    python3 scripts/gen-proto-field.py --report    # the parameters and counts
"""

import argparse
import math
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
# The lab and the shipping page, in that order. Both carry the same three
# marked blocks and both are held to this script's output — see the header.
PAGES = [
    ROOT / "design-system" / "prototypes" / "statement-to-process.html",
    ROOT / "design-system" / "patterns" / "landing-page.html",
]

# THE FIELD IS THE SYSTEM'S GROUND, AT THE SYSTEM'S SIZE.
#
# It was not. tokens.css draws .cf-ground — the lattice the Expertise page and
# every other section stands on — as ONE RHOMBUS, 96 x 48 CSS px, the cell
# foundations/illustration.html builds objects out of and both rungs of the
# space scale (--space-24 and --space-12). This field was drawn on a 64 x 32
# cell instead, so the ground under the root was a different lattice from the
# ground everywhere else on the site: measured at 2000 x 1050 it rendered
# 80 x 40 px against .cf-ground's 96 x 48, and being a sliced viewBox it was a
# different size again at every other viewport.
#
# MODULE 48, so the cell is 96 x 48 — the system's rhombus, 2:1, on the same
# two 26.57 deg families. The box is 1600 x 900, so at a 1600 x 900 viewport
# the slice scale is exactly 1 and the field renders the system's ground at
# the system's own pixel size. Away from that reference it scales with the
# stage, which is what a full-bleed backdrop does and what every other unit in
# this drawing does — but it is now a scaled instance of the right lattice
# rather than an unrelated one.
#
# EVERYTHING THE SENSORS SIT ON MOVES WITH IT. Crossings of y = c + x/2 and
# y = c - x/2 with c == LINE_C0 (mod MODULE) fall at x == 0 (mod MODULE) and
# y == LINE_C0 (mod MODULE/2) — so the supergrid, its stagger, the first
# crossing and the focus are all restated on 48 and 24. The stagger has to be
# a whole number of MODULEs, not merely half a super-column, or the odd rows
# leave the lattice: 288 / 2 = 144 = 3 x 48 is why the column is 288 and not
# the 240 that would have been closer to the old 256.
WIDTH, HEIGHT = 1600, 900
MODULE = 48                  # the lattice lines' step: the system's 96 x 48 cell
LINE_C0 = 8                  # c == 8 (mod 48), the statement field's own phase
SUPER_X, SUPER_Y = 288, 168  # the sensors' supergrid, on 48 x 24
STAGGER = 144                # odd rows shift half a super-column — and 3 x 48
X0, Y0 = 96, 80              # first crossing: x == 0 (mod 48), y == 8 (mod 24)
XMAX, YMAX = 1536, 800       # sensors keep a glow's reach inside the frame
FOCUS = (816, 272)           # the trunk's head at the design ratio — a crossing
CLAIM = (920, 180, 680)      # no sensors right of x in this y band —
                             # measured, not assumed: see the header
# AND THE NOTES KEEP OUT OF A BIGGER BOX THAN THE SENSORS DO. The claim's own
# box in field units moves with the viewport — measured across the eleven the
# gate admits it runs x 810..1512, y 181..569 — and the sensors' exclusion is
# the intersection of that with what the composition can afford to lose,
# because dropping a sensor costs the drawing an anchor. A note costs nothing
# to move, so it is held to the UNION instead: no label may land right of 810
# between 181 and 569 at any admitted viewport, which is what stops S02 from
# sitting on "erzeugen Daten" at 1024 x 720.
CLAIM_LABELS = (810, 181, 569)
R_MAX, R_MIN = 26, 9         # the BEAD's radius; the halo is --glow-r below
# THE BODY IS NEARLY OPAQUE, and that is a second thing the soft version could
# not be. At 0.2..0.6 the lattice read straight THROUGH every sensor, which is
# right for a glow and wrong for a bead: a drop of liquid metal occludes what
# is behind it, and a disc you can see the ground through reads as flat no
# matter what its ramp does. The ladder does not weaken — it is carried by the
# radius (9..26, a 3x range), by the ramp, and by --glow-r as well as by this.
OP_MIN, OP_MAX = 0.68, 0.95
REACH = 200                  # how far beyond its corner a stream opens
GLOW = 2.6                   # the HALO's radius as a multiple of the bead's.
                             # It was 1.6 and it was a drop-shadow's reach,
                             # chosen to land the footprint on the 40-unit disc
                             # the soft version drew — which was sizing the new
                             # drawing to the one it replaced. A bead is a
                             # light and a light spills; the review asked for
                             # more of it. Nearest neighbours stand 221 units
                             # apart and the largest halo is 68, so no two
                             # spills meet at any radius this admits.
WOB_MIN, WOB_MAX = 1600, 4000   # ms: the wobble period at r 0 and at R_MAX,
                                # interpolated on r^1.5 (see the header)

# ------------------------------------------------------------- the annotation
#
# EVERY SPHERE IS ANNOTATED, and the callout is components/annotation.html's,
# not a second one invented here: an anchor on the drawing, a leader that is
# ONE LATTICE STEP on a brand angle, and a note standing on its own rule. The
# component takes --annot-x / --annot-y as lengths rather than as percentages,
# so a sliced backdrop can hand it the crossing's own position instead of a
# fraction of a box that is being cropped.
#
# WHICH WAY THE LEADER RUNS IS NOT DECORATION. The manual allows eight — four
# quadrants on two slopes — and the one this picks per sensor is the one whose
# LABEL lands furthest from the claim's box and from the frame, because a
# leader is a line into clear ground and a note over the page's own sentence is
# not an annotation, it is interference. Ties go to the earlier direction in
# the list, so the choice is a function of the geometry like everything else.
ANNOT_DIRS = (("ne", 2, 1), ("nw", 2, 1), ("se", 2, 1), ("sw", 2, 1),
              ("ne steep", 1, 2), ("nw steep", 1, 2),
              ("se steep", 1, 2), ("sw steep", 1, 2))
ANNOT_U = 22                 # the leader's lattice unit, in FIELD units, so
                             # the step is (44, 22) or (22, 44) — the system's
                             # 2:1 cell at a size a 21-note layer can carry
# THE LABEL'S ALLOWANCE IS IN FIELD UNITS AND THE LABEL IS NOT, which is why
# these two numbers are measured at the SMALLEST scale the gate admits rather
# than at the reference. The backdrop scales with the slice and the type does
# not, so a note that is 84 px wide is 84 field units at 1600 x 900 and 105 at
# 1024 x 720 — and the placement law, scoring 92 everywhere, put S05 on S01 and
# S07 on S06 at exactly that viewport. Measured on the shipped labels at
# 1024 x 720 (scale 0.8): widest 84.1 px, tallest 19.3. 84.1 / 0.8 = 105.
ANNOT_W = 105
ANNOT_H = 24
ANNOT_INSET = 48             # how far inside the box a label must stay — one
                             # MODULE. Not tidiness: the backdrop is SLICED, so
                             # the box's own edge is not the screen's. The
                             # widest ratio the gate admits crops 115 units off
                             # the top and bottom, and scoring against 0..900
                             # put the whole top row's notes hard on the bezel
                             # at 2000 x 1050 and off it entirely at 3440. An
                             # inset makes a note near an edge prefer to point
                             # INWARD, which is also what a draughtsman does.
#
# THE READINGS ARE A POOL, NOT A RANDOM NUMBER. The review asked for numbers
# "randomly generated"; what that means in a system whose illustration page
# opens with "a construction is the same every time it is drawn" is that the
# reader should not be able to see the rule, not that the file should differ
# between runs. So each sensor draws a UNIT from the pool by a coprime stride
# and its own MAGNITUDE from a second one, and the same page comes out byte for
# byte every time. The units are the ones the root already annotates with —
# scripts/expertise-objects/gen-flow-root.py's own list — because two
# vocabularies of unit on one page is two instrument sets.
UNITS = (
    ("\u00b0C", 40, 120, 1), ("bar", 2, 26, 1), ("kW", 60, 420, 0),
    ("rpm", 900, 3200, 0), ("K", 280, 360, 0), ("mm/s", 1, 9, 1),
    ("%", 40, 99, 0), ("Hz", 47, 53, 1), ("m\u00b3/h", 8, 90, 0),
    ("V", 380, 720, 0), ("A", 4, 48, 1), ("kPa", 3, 40, 1),
)
STREAM_K = 6                 # how many readings a sensor cycles through
#
CORNERS = ((0, 0), (WIDTH, 0), (0, HEIGHT), (WIDTH, HEIGHT))

# HOW A FIELD UNIT BECOMES A CSS LENGTH. The backdrop is `xMidYMid slice` over
# a stage that is exactly the viewport in the pinned tier — measured at six
# viewports from 1024x720 to 3440x1440, box (0,0) and size (100vw, 100vh)
# every time — so the slice scale is max(100vw/1600, 100vh/900) and the box is
# centred. --sp-u is that scale as a length-per-unit, and a crossing's position
# is the centre plus its own offset in those units. The annotation layer is
# therefore pinned to the drawing at every viewport without a script measuring
# anything, which is what lets the callouts ship in the markup.
# The offset is a NUMBER and --sp-u is the length, in that order: --sp-u is
# already a length (max(1vw/16, 1vh/9)), and `-6.8px * var(--sp-u)` is a length
# times a length, which is not a thing calc() can produce. Chromium does not
# warn — the declaration is simply invalid at computed-value time, the property
# falls back to its initial 50%/... and every callout stacks at left: 0, top: 0
# in the corner. Measured: twenty-one <li> at (0, 0) with the labels hanging
# off the top-left of the viewport.
POS = "calc(50% + {d} * var(--sp-u))"


def num(v):
    v = round(v + 0.0, 1)
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return f"{v:g}"


# ------------------------------------------------------------------- lattice

def clip(p, q):
    (x1, y1), (x2, y2) = p, q
    dx, dy = x2 - x1, y2 - y1
    t0, t1 = 0.0, 1.0
    for pk, qk in ((-dx, x1), (dx, WIDTH - x1), (-dy, y1), (dy, HEIGHT - y1)):
        if pk == 0:
            if qk < 0:
                return None
            continue
        t = qk / pk
        if pk < 0:
            t0 = max(t0, t)
        else:
            t1 = min(t1, t)
    if t0 >= t1 - 1e-12:
        return None
    return ((x1 + t0 * dx, y1 + t0 * dy), (x1 + t1 * dx, y1 + t1 * dy))


def lattice():
    """Down-right family, down-left family, then the level step — the order
    the statement field has always drawn them in."""
    lines = []
    for sign in (+1, -1):
        lo = -WIDTH // 2 - MODULE if sign > 0 else 0
        hi = HEIGHT if sign > 0 else HEIGHT + WIDTH // 2 + MODULE
        c = LINE_C0 + MODULE * math.ceil((lo - LINE_C0) / MODULE)
        while c < hi:
            seg = clip((0.0, float(c)), (float(WIDTH), c + sign * WIDTH / 2))
            if seg:
                lines.append(seg)
            c += MODULE
    y = MODULE // 2
    while y <= HEIGHT - MODULE // 2:
        lines.append(((0.0, float(y)), (float(WIDTH), float(y))))
        y += MODULE
    return lines


# --------------------------------------------------------------------- field

def field():
    fx, fy = FOCUS
    cand = []
    j = 0
    y = Y0
    while y <= YMAX:
        x = X0 + (STAGGER if j % 2 else 0)
        while x <= XMAX:
            if not (x >= CLAIM[0] and CLAIM[1] <= y <= CLAIM[2]):
                cand.append((x, y, math.hypot(x - fx, y - fy)))
            x += SUPER_X
        j += 1
        y += SUPER_Y
    d_max = max(d for _, _, d in cand)
    cand.sort(key=lambda p: (p[2], p[0], p[1]))
    rows = []
    n = len(cand)
    stride = next(k for k in range(9, 9 + n) if math.gcd(k, n) == 1)
    for i, (x, y, d) in enumerate(cand):
        t = 1.0 - d / d_max
        r = R_MIN + (R_MAX - R_MIN) * t
        op = round(OP_MIN + (OP_MAX - OP_MIN) * t, 2)
        m = round(d / d_max, 1)
        cx, cy = min(CORNERS, key=lambda c: math.hypot(c[0] - x, c[1] - y))
        cd = math.hypot(cx - x, cy - y)
        sx = cx + (cx - x) / cd * REACH
        sy = cy + (cy - y) / cd * REACH
        # the two liquid properties, both functions of the bead and neither of
        # a random number: the period from its own radius on the r^1.5 law, the
        # phase from a stride through the slot order that visits every slot
        # exactly once because the stride is chosen coprime with the count.
        wp = int(round(WOB_MIN + (WOB_MAX - WOB_MIN) * (r / R_MAX) ** 1.5))
        w = round((i * stride % n) / n, 3)
        rows.append((x, y, r, op, m, sx - x, sy - y, wp, w))
    return rows


# -------------------------------------------------------------------- markup

def lattice_markup(indent):
    return "\n".join(
        f'{indent}<line x1="{num(p[0])}" y1="{num(p[1])}" '
        f'x2="{num(q[0])}" y2="{num(q[1])}"/>' for p, q in lattice())


def field_markup(indent):
    """A group per sensor: the halo it spills, then the bead itself.

    THE SPLIT IS A PROPERTY LEDGER, not decoration. The group carries the
    scroll's three verbs — arrive, pulse, merge — which own `translate`,
    `scale` and `opacity` between them off the track's timeline. The two
    children carry paint and geometry and nothing else. Nothing in the field
    is driven by a clock any more: the drawing is scrubbed by the reader,
    which is the pinned track's own contract, and the one thing that moves on
    its own is the readout — see annots_markup.
    """
    out = []
    for x, y, r, op, m, fx, fy, wp, w in field():
        out.append(
            f'{indent}<g class="cf-stmt-sensor" '
            f'style="--cx:{num(x)};--cy:{num(y)};--fx:{num(fx)};--fy:{num(fy)}'
            f';--m:{m:g};--iso-rest:{op:g}">\n'
            f'{indent}  <circle class="cf-stmt-sensor__halo" '
            f'cx="{num(x)}" cy="{num(y)}" r="{r * GLOW:.1f}" '
            f'fill="url(#cf-stmt-sensor-halo)"/>\n'
            f'{indent}  <circle class="cf-stmt-sensor__bead" '
            f'cx="{num(x)}" cy="{num(y)}" r="{r:.1f}" '
            f'fill="url(#cf-stmt-sensor-body)"/>\n'
            f'{indent}</g>')
    return "\n".join(out)


# ---------------------------------------------------------------- the readout

def reading(i, k):
    """Sensor i's k-th reading, as text.

    The unit is the sensor's and does not change while it streams — an
    instrument that changes what it MEASURES between frames is not an
    instrument. Only the magnitude moves, which is what a live readout does.
    Both strides are coprime with their pool so every sensor is on a different
    unit until the pool runs out, and the digits do not cycle in step.
    """
    unit, lo, hi, dp = UNITS[(i * 5) % len(UNITS)]
    span = hi - lo
    # A LIVE SENSOR JITTERS AROUND ITS OPERATING POINT; it does not sweep its
    # whole range in six frames. The first pass stepped k linearly and printed
    # 40.0, 49.2, 58.3, 67.5 — an ascending ramp, which reads as a countdown
    # rather than as an instrument. So the sensor's BASE is its own draw from
    # the range and the six readings are a small deviation about it, ordered
    # by a stride coprime with the modulus so consecutive frames are not
    # neighbours in value either.
    # the base is INSET from the range's ends by more than the deviation can
    # reach, so no reading is ever clamped — a clamp prints the same number
    # twice in six frames and a readout that repeats is a readout that has
    # stopped.
    base = lo + span * (0.12 + 0.76 * ((i * 29 % 89) / 88))
    dev = span * 0.08 * (((i * 13 + k * 37) % 97) / 96 * 2 - 1)
    v = base + dev
    text = f"{v:.{dp}f}"
    # the manual's own thin space between thousands — the root's values set
    # "12 480" this way and two conventions for one numeral on one page is one
    # too many.
    whole, _, frac = text.partition(".")
    if len(whole) > 3:
        whole = whole[:-3] + "\u2009" + whole[-3:]
    return whole + ("." + frac if frac else "") + "\u00a0" + unit


def annot_box(x, y, r, name):
    """Where the label lands if the leader runs `name`, and where it starts."""
    quad = name.split()[0]
    sx = -1 if "w" in quad else 1
    sy = -1 if quad[0] == "n" else 1
    mx, my = (1, 2) if "steep" in name else (2, 1)
    lx, ly = x + sx * ANNOT_U * mx, y + sy * ANNOT_U * my
    # the component sets a west-running note by its right edge — --annot-align
    x0 = lx - ANNOT_W if sx < 0 else lx
    return (x0, ly - ANNOT_H, x0 + ANNOT_W, ly), (sx, sy, mx, my)


def _overlap(a, b):
    return (max(0, min(a[2], b[2]) - max(a[0], b[0]))
            * max(0, min(a[3], b[3]) - max(a[1], b[1])))


def place_annots():
    """One direction per sensor, chosen greedily against everything already on
    the drawing — the same shape of law the root's numerals are placed by.

    FOUR CLAUSES, IN ORDER, and the order is the order of harm:

      1. the CLAIM. A note over the page's own sentence is not an annotation,
         it is interference, and it is the one collision a reader cannot work
         around by looking somewhere else.
      2. the FRAME. The backdrop is sliced, so a note that leaves the box is
         not merely tight, it is cropped — and at which viewport depends on
         the ratio, which is how a label goes missing on one machine only.
      3. the OTHER NOTES. Scored against the boxes already placed rather than
         against all of them, so the pass is one sweep and the earlier sensors
         — which are the bigger, nearer ones, because field() sorts by
         distance to the focus — get the clear ground.
      4. the BEADS themselves, halo and all. A note lying across another
         sensor names two things at once.

    Ties fall to the earlier direction in ANNOT_DIRS, so the whole placement
    is a function of the geometry. Scoring all four rather than rejecting on
    any one means there is always an answer: the least bad direction wins even
    when the sensor is boxed in, and no sensor can end up unannotated.
    """
    rows = field()
    discs = [(x - r * GLOW, y - r * GLOW, x + r * GLOW, y + r * GLOW)
             for x, y, r, *_ in rows]
    cx0, cy0, cy1 = CLAIM_LABELS
    claim = (cx0, cy0, WIDTH, cy1)
    placed, out = [], []
    for i, (x, y, r, *_rest) in enumerate(rows):
        best, best_score = None, None
        for k, (name, _mx, _my) in enumerate(ANNOT_DIRS):
            box, _ = annot_box(x, y, r, name)
            outside = (max(0, ANNOT_INSET - box[0])
                       + max(0, box[2] - (WIDTH - ANNOT_INSET))
                       + max(0, ANNOT_INSET - box[1])
                       + max(0, box[3] - (HEIGHT - ANNOT_INSET)))
            score = (_overlap(box, claim),
                     outside,
                     sum(_overlap(box, b) for b in placed),
                     sum(_overlap(box, d) for j, d in enumerate(discs) if j != i),
                     k)
            if best_score is None or score < best_score:
                best, best_score = name, score
        placed.append(annot_box(x, y, r, best)[0])
        out.append(best)
    return out


def annots_markup(indent):
    """One callout per sensor, in components/annotation.html's own component.

    THE ANCHOR IS THE BEAD'S RIM, not its centre. The component draws a small
    lattice cell where it points, and a lattice cell in the middle of a lit
    sphere is a mark on top of the thing it is naming. Offset along the
    leader's own direction by the bead's radius and the cell sits where the
    line leaves the body, which is where a leader attaches on paper.

    ONE NOTE IS LIT AND THE REST ARE CONTOURED, which is the component's rule
    verbatim — "at most one per figure, and only when a figure has a subject".
    This figure has one: the bead at the focus, the one the whole act converges
    on. The others are drawn in contour like every other annotation in the
    system.
    """
    out = []
    rows = field()
    dirs = place_annots()
    for i, (x, y, r, op, m, fx, fy, wp, w) in enumerate(rows):
        name = dirs[i]
        quad = name.split()[0]
        steep = " cf-annot--steep" if "steep" in name else ""
        lit = " cf-annot--lit" if i == 0 else ""
        sx = -1 if "w" in quad else 1
        sy = -1 if quad[0] == "n" else 1
        mx, my = (1, 2) if steep else (2, 1)
        # the rim, along the leader's own slope
        norm = math.hypot(mx, my)
        ax = x + sx * r * mx / norm
        ay = y + sy * r * my / norm
        vals = "".join(
            f'<b style="--sp-slot:{k}">{reading(i, k)}</b>'
            for k in range(STREAM_K))
        out.append(
            f'{indent}<li class="cf-annot cf-annot--{quad}{steep}{lit}" '
            f'style="--annot-x:{POS.format(d=num(ax - WIDTH / 2))};'
            f'--annot-y:{POS.format(d=num(ay - HEIGHT / 2))};'
            f'--sp-period:{wp}ms">\n'
            f'{indent}  <span class="cf-annot__label">S{i + 1:02d}'
            f'<span class="cf-annot__value sp-stream">{vals}</span>'
            f'</span>\n'
            f'{indent}</li>')
    return "\n".join(out)


# THE CLOSING TAG IS MATCHED AT THE OPENING TAG'S OWN INDENT, and that is not
# tidiness. `(.*?)(\n\s*</g>)` was fine while a block held nothing but leaf
# elements; the moment a sensor became a <g> of its own the lazy match stopped
# at the FIRST sensor's `</g>` and every --write spliced the whole field back
# in one sensor deep. It ran clean, wrote a file, and --check failed on its own
# output. Backreferencing the indent means the match can only end on a closing
# tag that closes the block itself, whatever is nested inside it.
#
# EACH BODY IS ANY RUN OF WHOLE LINES INCLUDING NONE, so a block survives being
# emptied. A pattern that needs at least one line between the markers cannot
# regenerate a block somebody has cleared, which is exactly the state a person
# leaves behind when they delete generated output to see what is theirs.
LATTICE_RE = re.compile(
    r'([ \t]*)(<g class="sp-field__lattice"[^>]*>\n)((?:.*\n)*?)(\1</g>)')
SENSORS_RE = re.compile(
    r'([ \t]*)(<g class="sp-field__sensors">\n)((?:.*\n)*?)(\1</g>)')
ANNOTS_RE = re.compile(
    r'([ \t]*)(<ul class="cf-annot-set sp-annots">\n)((?:.*\n)*?)(\1</ul>)')


def splice(text):
    def one(m, maker):
        return (m.group(1) + m.group(2)
                + maker(m.group(1) + "  ") + "\n" + m.group(4))

    def annots(m):
        return (m.group(1) + m.group(2)
                + annots_markup(m.group(1) + "  ") + "\n" + m.group(4))

    text, n1 = LATTICE_RE.subn(lambda m: one(m, lattice_markup), text, count=1)
    text, n2 = SENSORS_RE.subn(lambda m: one(m, field_markup), text, count=1)
    text, n3 = ANNOTS_RE.subn(annots, text, count=1)
    return text, n1 + n2 + n3


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    if args.report or not (args.write or args.check):
        rows = field()
        dmin = min(math.hypot(a[0] - b[0], a[1] - b[1])
                   for i, a in enumerate(rows) for b in rows[i + 1:])
        print(f"  box            {WIDTH} x {HEIGHT}   focus {FOCUS}")
        print(f"  supergrid      {SUPER_X} x {SUPER_Y}, stagger {STAGGER}"
              f" — nearest neighbours {dmin:.1f} units")
        print(f"  sensors        {len(rows)}   "
              f"lattice lines {len(lattice())}")
        print(f"  bead           r {R_MIN}..{R_MAX}  opacity "
              f"{OP_MIN:g}..{OP_MAX:g}  halo {GLOW:g}x")
        dirs = {}
        for name in place_annots():
            dirs[name] = dirs.get(name, 0) + 1
        print(f"  callouts       {len(rows)}  "
              + ", ".join(f"{k} {v}" for k, v in sorted(dirs.items())))
        print(f"  readings       {STREAM_K} per sensor, "
              f"{len({reading(i, k).split(chr(160))[1] for i in range(len(rows)) for k in range(STREAM_K)})}"
              f" distinct units")
        print(f"  stream         {min(r[7] for r in rows)}"
              f"..{max(r[7] for r in rows)} ms, "
              f"{len({r[8] for r in rows})} distinct phases")
        if not (args.write or args.check):
            return 0

    stale = 0
    for page in PAGES:
        rel = page.relative_to(ROOT)
        text = page.read_text(encoding="utf-8")
        new, n = splice(text)
        if n != 3:
            print(f"gen-proto-field: {rel}: found {n} of 3 blocks — "
                  f"the markers went stale")
            return 1
        if args.write:
            if new != text:
                page.write_text(new, encoding="utf-8")
                print(f"  wrote {rel}")
            else:
                print(f"  {rel} already current")
        elif new != text:
            print(f"gen-proto-field: {rel}'s field is not what this script "
                  f"generates — re-run with --write")
            stale += 1
    if stale:
        return 1
    if args.check:
        print(f"gen-proto-field: the field is the generator's output "
              f"in {len(PAGES)} pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
