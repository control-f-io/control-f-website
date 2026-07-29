#!/usr/bin/env python3
"""Generate the prototype's full-screen sensor field, on brand angles.

THE BRIEF THAT FORCED THE SECOND GENERATOR. The statement field this page
carried was the landing page's: a 1200 x 288 strip inside the figure column,
two tight clusters of glows around a void. The review of 2026-07-28 asked for
the opposite composition in three clauses — the grid should cover the whole
screen, the gradient dots should STREAM FROM THE CORNERS into their grid
positions and then pulse and merge, and the glows should stop crowding
("let not bubble it so close together"). That is a different drawing with a
different law, and scripts/gen-stmt-field.py keeps owning the landing/statement
copies unchanged; this file owns only
design-system/prototypes/statement-to-process.html.

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
PAGE = ROOT / "design-system" / "prototypes" / "statement-to-process.html"

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
R_MAX, R_MIN = 26, 9         # the BEAD's radius; the halo is --glow-r below
# THE BODY IS NEARLY OPAQUE, and that is a second thing the soft version could
# not be. At 0.2..0.6 the lattice read straight THROUGH every sensor, which is
# right for a glow and wrong for a bead: a drop of liquid metal occludes what
# is behind it, and a disc you can see the ground through reads as flat no
# matter what its ramp does. The ladder does not weaken — it is carried by the
# radius (9..26, a 3x range), by the ramp, and by --glow-r as well as by this.
OP_MIN, OP_MAX = 0.68, 0.95
HOT_AT = 21                  # the lime-core ramp starts here
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

# ---------------------------------------------------------------- the outline
#
# A DROP IS NOT AN ELLIPSE. The first wobble scaled a <circle> on two axes,
# which conserves volume and reads as breathing but can only ever produce an
# ellipse — the review's answer was "even out of the sphere shape". So the bead
# is a closed curve through N vertices whose radii are a sum of two travelling
# harmonics, and the animation morphs the `d` property between four states of
# it. At 100 % the phase has advanced by a full turn, so the loop closes
# exactly rather than snapping.
#
# THE HARMONIC ORDERS ARE NOT FREE. Sampling cos(L * theta) at N evenly spaced
# vertices ALIASES: order N-1 comes back as order 1, and an order-1 term on a
# closed curve is not a deformation at all, it is a TRANSLATION — the blob
# would swim off its own lattice crossing while claiming to wobble in place.
# With N = 6 the safe orders are 2, 3 and 4, and the three pairs of them are
# the three shape families below. Order 5 is the one that would have moved it.
#
# STILL NOT RANDOM. Every radius is a function of the bead's index, its own
# radius and the keyframe number — see the module header. Re-running prints
# byte-identical paths.
BLOB_N = 6                   # vertices; 6 admits orders 2..4 without aliasing
BLOB_K = 4                   # keyframe states; the fifth is the first again
BLOB_FAMILIES = ((2, 3), (2, 4), (3, 4))   # the two harmonic orders per bead
BLOB_A1, BLOB_A2 = 0.10, 0.05              # their amplitudes, as fractions of r

CORNERS = ((0, 0), (WIDTH, 0), (0, HEIGHT), (WIDTH, HEIGHT))


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


# ---------------------------------------------------------------- the outline

def blob(cx, cy, r, i, k):
    """One state of one bead's outline, as a closed six-segment cubic path.

    The vertices are Catmull-Rom knots turned into Beziers by the uniform
    construction (the tangent at a knot is a sixth of the chord across it), so
    the curve passes THROUGH every radius rather than near it and the shape is
    the arithmetic rather than an approximation of it.

    EVERY STATE HAS THE SAME COMMAND LIST — one M, six Cs, one Z — because
    interpolating `d` requires it: mismatched structure makes the browser fall
    back to a discrete swap and the drop would jump between shapes instead of
    flowing between them.
    """
    l1, l2 = BLOB_FAMILIES[i % len(BLOB_FAMILIES)]
    # the bead's own place in the turn, so no two blobs are the same blob at a
    # different moment; the same coprime stride the period and phase use.
    psi = 2 * math.pi * (k / BLOB_K + (i * 7 % 23) / 23)
    pts = []
    for j in range(BLOB_N):
        th = 2 * math.pi * j / BLOB_N
        rad = r * (1 + BLOB_A1 * math.cos(l1 * th + psi)
                     + BLOB_A2 * math.cos(l2 * th - psi))
        pts.append((cx + rad * math.cos(th), cy + rad * math.sin(th)))

    def at(n):
        return pts[n % BLOB_N]

    out = [f"M{num(pts[0][0])} {num(pts[0][1])}"]
    for j in range(BLOB_N):
        p0, p1, p2, p3 = at(j - 1), at(j), at(j + 1), at(j + 2)
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        out.append(f"C{num(c1[0])} {num(c1[1])} {num(c2[0])} {num(c2[1])} "
                   f"{num(p2[0])} {num(p2[1])}")
    return "".join(out) + "Z"


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
        ramp = "hot" if r >= HOT_AT else "cool"
        # the two liquid properties, both functions of the bead and neither of
        # a random number: the period from its own radius on the r^1.5 law, the
        # phase from a stride through the slot order that visits every slot
        # exactly once because the stride is chosen coprime with the count.
        wp = int(round(WOB_MIN + (WOB_MAX - WOB_MIN) * (r / R_MAX) ** 1.5))
        w = round((i * stride % n) / n, 3)
        rows.append((x, y, r, op, m, sx - x, sy - y, ramp, wp, w))
    return rows


# -------------------------------------------------------------------- markup

def lattice_markup(indent):
    return "\n".join(
        f'{indent}<line x1="{num(p[0])}" y1="{num(p[1])}" '
        f'x2="{num(q[0])}" y2="{num(q[1])}"/>' for p, q in lattice())


def field_markup(indent):
    """A group per sensor, one bead inside it.

    THE SPLIT IS A PROPERTY LEDGER, not decoration. The group carries the
    SCROLL's three verbs — arrive, pulse, merge — which own `translate`,
    `scale` and `opacity` between them off the track's timeline. The bead
    carries the CLOCK's one verb, the morph, which owns `d` off the document
    timeline. Two timelines writing one property on one element is a fight the
    later declaration wins outright; on two elements — and now on two
    different properties as well — it is a composition, and the bead goes on
    morphing while the field flies.
    """
    out = []
    for i, (x, y, r, op, m, fx, fy, ramp, wp, w) in enumerate(field()):
        # the modifier is what keeps LIME on a budget. --glow-light is a lime
        # shadow and a Glas one; hung on all twenty-one it put a yellow ring
        # around seventeen beads that carry no lime at all, and the hot/cool
        # ladder the whole law is built on stopped being visible. The four hot
        # beads take the token; the rest take its Glas half.
        hot = " cf-stmt-sensor--hot" if ramp == "hot" else ""
        out.append(
            f'{indent}<g class="cf-stmt-sensor{hot}" '
            f'style="--cx:{num(x)};--cy:{num(y)};--fx:{num(fx)};--fy:{num(fy)}'
            f';--m:{m:g};--iso-rest:{op:g}'
            f';--wp:{wp}ms;--w:{w:g}">\n'
            # THE HALO IS PAINTED, NOT FILTERED, AND THAT IS A FRAME BUDGET.
            # A drop-shadow re-rasterizes whenever its SOURCE changes, and once
            # the source was a path morphing every frame the two together cost
            # 25 fps of a 61 fps budget — measured, each alone free:
            #   morph + filter 25   filter only 61   morph only 61   neither 61
            # So the spill moved onto its own static circle, which never
            # changes shape and so never re-rasterizes, and the bead that DOES
            # change carries no filter at all. It is also the better drawing:
            # a Gaussian of a black contour smears the contour, and this
            # leaves it crisp.
            f'{indent}  <circle class="cf-stmt-sensor__halo" '
            f'cx="{num(x)}" cy="{num(y)}" r="{r * GLOW:.1f}" '
            f'fill="url(#cf-stmt-sensor-halo-{ramp})"/>\n'
            # data-, not cx/cy: a <path> has no cx, and an attribute a renderer
            # ignores is exactly the kind of decoration on a tag that
            # check-authored-opacity.py was written about. The crossing is
            # still stated on the element that draws it, because
            # check-void-departure.py holds the group's --cx/--cy against it.
            f'{indent}  <path class="cf-stmt-sensor__bead sp-bead-{i}" '
            f'data-cx="{num(x)}" data-cy="{num(y)}" data-r="{r:.1f}" '
            f'd="{blob(x, y, r, i, 0)}" '
            f'fill="url(#cf-stmt-sensor-{ramp})"/>\n'
            f'{indent}</g>')
    return "\n".join(out)


def shapes_markup(indent):
    """One keyframe set per bead, and the rule that hangs it on that bead.

    TWENTY-ONE SETS RATHER THAN ONE, because the review asked for each sphere
    to morph individually and a single set with per-bead delays is one sphere
    morphing twenty-one times. Every bead's outline is generated from its own
    radius, its own shape family and its own place in the turn, so no two are
    the same curve at a different moment.

    The `d` in the MARKUP is state 0, so a browser that animates nothing —
    print, reduced motion, no CSS animation at all — still gets a drop rather
    than an empty <path>. The keyframes only take it round.
    """
    out = []
    for i, (x, y, r, *_rest) in enumerate(field()):
        states = [blob(x, y, r, i, k) for k in range(BLOB_K)] + [blob(x, y, r, i, 0)]
        out.append(f"{indent}.sp-bead-{i} {{ animation-name: sp-bead-{i}; }}")
        out.append(f"{indent}@keyframes sp-bead-{i} {{")
        for s, d in enumerate(states):
            pct = round(100 * s / BLOB_K)
            out.append(f'{indent}  {pct}% {{ d: path("{d}"); }}')
        out.append(f"{indent}}}")
    return "\n".join(out)


# THE CLOSING TAG IS MATCHED AT THE OPENING TAG'S OWN INDENT, and that is not
# tidiness. `(.*?)(\n\s*</g>)` was fine while a block held nothing but leaf
# elements; the moment a sensor became a <g> of its own the lazy match stopped
# at the FIRST sensor's `</g>` and every --write spliced the whole field back
# in one sensor deep. It ran clean, wrote a file, and --check failed on its own
# output. Backreferencing the indent means the match can only end on a `</g>`
# that closes the block itself, whatever is nested inside it.
LATTICE_RE = re.compile(
    r'([ \t]*)(<g class="sp-field__lattice"[^>]*>\n)(.*?)(\n\1</g>)', re.S)
SENSORS_RE = re.compile(
    r'([ \t]*)(<g class="sp-field__sensors">\n)(.*?)(\n\1</g>)', re.S)
# The third block is CSS rather than markup, so it is fenced by comments
# instead of by a tag. Same shape: an opener, a body this script owns entirely,
# and a closer that is never inside what it encloses.
# THE MARKER IS A COMPLETE COMMENT, opened and closed on its own line, and
# that is not a formatting choice. The first version carried its explanation
# inside the opener and never wrote the `*/`, so the FIRST `*/` in the file
# closed it — the one at the end of the CLOSING marker. Everything this script
# generated was inside one comment. It parsed, it shipped, --check passed
# (the text was there, byte for byte), and nothing animated: `animationName`
# read `none` on all twenty-one beads. The prose lives above the marker now.
#
# The body is matched as ANY RUN OF WHOLE LINES INCLUDING NONE, so the block
# survives being emptied. A pattern that needs at least one line between the
# markers cannot regenerate a block somebody has cleared, which is exactly the
# state a person leaves behind when they delete generated output to see what
# is theirs.
SHAPES_RE = re.compile(
    r"([ \t]*)(/\* == generated: the beads' outlines == \*/\n)"
    r"((?:.*\n)*?)(\1/\* == end generated == \*/)")


def splice(text):
    def one(m, maker):
        indent = re.match(r"\s*", m.group(3)).group(0).lstrip("\n")
        return m.group(1) + m.group(2) + maker(indent) + m.group(4)

    def shapes(m):
        return (m.group(1) + m.group(2)
                + shapes_markup(m.group(1)) + "\n" + m.group(4))

    text, n1 = LATTICE_RE.subn(lambda m: one(m, lattice_markup), text, count=1)
    text, n2 = SENSORS_RE.subn(lambda m: one(m, field_markup), text, count=1)
    text, n3 = SHAPES_RE.subn(shapes, text, count=1)
    return text, n1 + n2 + n3


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    if args.report or not (args.write or args.check):
        rows = field()
        hot = sum(1 for r in rows if r[7] == "hot")
        dmin = min(math.hypot(a[0] - b[0], a[1] - b[1])
                   for i, a in enumerate(rows) for b in rows[i + 1:])
        print(f"  box            {WIDTH} x {HEIGHT}   focus {FOCUS}")
        print(f"  supergrid      {SUPER_X} x {SUPER_Y}, stagger {STAGGER}"
              f" — nearest neighbours {dmin:.1f} units")
        print(f"  sensors        {len(rows)}  ({hot} hot)   "
              f"lattice lines {len(lattice())}")
        print(f"  bead           r {R_MIN}..{R_MAX}  opacity "
              f"{OP_MIN:g}..{OP_MAX:g}  hot at r >= {HOT_AT}")
        print(f"  wobble         {min(r[8] for r in rows)}"
              f"..{max(r[8] for r in rows)} ms, "
              f"{len({r[9] for r in rows})} distinct phases")
        if not (args.write or args.check):
            return 0

    text = PAGE.read_text(encoding="utf-8")
    new, n = splice(text)
    if n != 3:
        print(f"gen-proto-field: found {n} of 3 blocks — the markers went stale")
        return 1
    if args.write:
        if new != text:
            PAGE.write_text(new, encoding="utf-8")
            print(f"  wrote {PAGE.relative_to(ROOT)}")
        else:
            print(f"  {PAGE.relative_to(ROOT)} already current")
    elif new != text:
        print("gen-proto-field: the prototype's field is not what this script "
              "generates — re-run with --write")
        return 1
    if args.check:
        print("gen-proto-field: the field is the generator's output")
    return 0


if __name__ == "__main__":
    sys.exit(main())
