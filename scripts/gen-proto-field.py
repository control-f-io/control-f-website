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

  A SENSOR IS A BEAD, AND IT IS DRAWN THE WAY THE SOURCE IS DRAWN. It used to
  be a single soft disc: one radial ramp running to stop-opacity 0 at the rim,
  no contour, resting between 0.2 and 0.6. Nineteen of the twenty-three had
  CF-Grau at their centre and CF-Grau is the page wash, so they rendered as
  smudges the eye could not find — the fault foundations/illustration.html
  states in one line: "an unlit face sits at exactly the page's own colour and
  the object would disappear entirely if the contour were not carrying it".

  So the bead is built like .lp-flow__orb, which is the thing all twenty-three
  of them converge INTO and the only other light in this drawing: a disc
  filled with the family's ramp, BOUNDED by --border-default, and glowing by
  --glow-light rather than by a fade to nothing. The ramp now ends OPAQUE at
  CF-Grau and the contour says where the disc stops; the halo the old stop
  list drew by hand is the drop-shadow pair the token already owns. The
  radius here is therefore the BEAD's, not the glow's — 9..26 where it was
  12..40 — because the reach moved into --glow-r, which is emitted with it.

  AND IT MOVES LIKE THE LIQUID IT IS NAMED FOR. Each bead carries --wp, its
  own wobble period, and --w, its own phase. The period is NOT decoration: a
  drop's surface-tension oscillation goes as r^1.5, so the big beads at the
  focus swing slowly and the small ones at the rim quiver — the field's
  liveliness is its own size distribution read out loud. The phase is a
  deterministic stride through the slot order (i * 9 mod n), so no two beads
  in the shipped field share one and neighbours never breathe in step.

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
GLOW = 1.6                   # --glow-r as a multiple of the bead's radius:
                             # the Glas shadow reaches 1.6r and the lime one
                             # 0.45 of that, so the footprint lands close to
                             # the 40-unit disc the soft version drew
WOB_MIN, WOB_MAX = 1600, 4000   # ms: the wobble period at r 0 and at R_MAX,
                                # interpolated on r^1.5 (see the header)

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
    carries the CLOCK's one verb, the wobble, which owns `scale` off the
    document timeline. Two timelines writing one property on one element is a
    fight the later declaration wins outright; on two elements it is a
    composition, and the bead goes on wobbling while the field flies.
    """
    out = []
    for x, y, r, op, m, fx, fy, ramp, wp, w in field():
        # the modifier is what keeps LIME on a budget. --glow-light is a lime
        # shadow and a Glas one; hung on all twenty-three it put a yellow ring
        # around nineteen beads that carry no lime at all, and the hot/cool
        # ladder the whole law is built on stopped being visible. The four hot
        # beads take the token; the rest take its Glas half.
        hot = " cf-stmt-sensor--hot" if ramp == "hot" else ""
        out.append(
            f'{indent}<g class="cf-stmt-sensor{hot}" '
            f'style="--cx:{num(x)};--cy:{num(y)};--fx:{num(fx)};--fy:{num(fy)}'
            f';--m:{m:g};--iso-rest:{op:g}'
            f';--glow-r:{r * GLOW:.1f}px;--wp:{wp}ms;--w:{w:g}">\n'
            f'{indent}  <circle class="cf-stmt-sensor__bead" '
            f'cx="{num(x)}" cy="{num(y)}" r="{r:.1f}" '
            f'fill="url(#cf-stmt-sensor-{ramp})"/>\n'
            f'{indent}</g>')
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


def splice(text):
    def one(m, maker):
        indent = re.match(r"\s*", m.group(3)).group(0).lstrip("\n")
        return m.group(1) + m.group(2) + maker(indent) + m.group(4)
    text, n1 = LATTICE_RE.subn(lambda m: one(m, lattice_markup), text, count=1)
    text, n2 = SENSORS_RE.subn(lambda m: one(m, field_markup), text, count=1)
    return text, n1 + n2


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
    if n != 2:
        print(f"gen-proto-field: found {n} of 2 blocks — the markers went stale")
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
