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
  it and nothing else — r = 12 + 28 x (1 - d/d_max), opacity 0.2..0.6 on the
  same slope quantised to the tenth, the hot lime-core ramp above r 32 —
  so the field is hottest where the data will funnel and coolest at the rim.
  The exact merge point is measured at runtime (the trunk lives in another
  svg in the column flow) and published as --ux/--uy on the field; the focus
  is the LAW's stand-in and the var()'s fallback.

  THE APPROACH: each glow belongs to its nearest box corner and opens the act
  200 units beyond it — outside every crop the slice can produce (the widest
  admitted viewport ratio costs 80 units a side) — so the streams read as
  entering from off-screen at the four corners, not popping at the bezel.
  --fx/--fy is that run, --m the glow's slot (distance to focus over d_max,
  to the tenth): the core seeds first and the field grows outward, and the
  merge later runs back in the same order.

  THE CLAIM'S REACH: no sensor stands in x >= 920, 360 <= y <= 680 — the
  right-column claim's box at the design ratio with a margin — the same
  argument the old #cf-stmt-reach mask made, made by placement instead of
  by masking, because a glow behind the claim is contrast debt and a mask
  over a full-screen field is a window sliding across the page.

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

WIDTH, HEIGHT = 1600, 900
MODULE = 32                  # the lattice lines' step, and the phase base
LINE_C0 = 8                  # c == 8 (mod 32), the statement field's own phase
SUPER_X, SUPER_Y = 256, 160  # the sensors' supergrid
STAGGER = 128                # odd rows shift half a super-column
X0, Y0 = 64, 88              # first crossing: x == 0 (mod 32), y == 8 (mod 16)
XMAX, YMAX = 1536, 812       # sensors keep a glow's reach inside the frame
FOCUS = (800, 264)           # the trunk's head at the design ratio — a crossing
CLAIM = (920, 360, 680)      # no sensors right of x in this y band
R_MAX, R_MIN = 40, 12
OP_MIN, OP_MAX = 0.2, 0.6
HOT_AT = 32                  # the lime-core ramp starts here
REACH = 200                  # how far beyond its corner a stream opens

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
    for x, y, d in cand:
        t = 1.0 - d / d_max
        r = R_MIN + (R_MAX - R_MIN) * t
        op = round(OP_MIN + (OP_MAX - OP_MIN) * t, 1)
        m = round(d / d_max, 1)
        cx, cy = min(CORNERS, key=lambda c: math.hypot(c[0] - x, c[1] - y))
        cd = math.hypot(cx - x, cy - y)
        sx = cx + (cx - x) / cd * REACH
        sy = cy + (cy - y) / cd * REACH
        ramp = "hot" if r >= HOT_AT else "halo"
        rows.append((x, y, r, op, m, sx - x, sy - y, ramp))
    return rows


# -------------------------------------------------------------------- markup

def lattice_markup(indent):
    return "\n".join(
        f'{indent}<line x1="{num(p[0])}" y1="{num(p[1])}" '
        f'x2="{num(q[0])}" y2="{num(q[1])}"/>' for p, q in lattice())


def field_markup(indent):
    out = []
    for x, y, r, op, m, fx, fy, ramp in field():
        out.append(
            f'{indent}<circle class="cf-stmt-sensor" '
            f'style="--cx:{num(x)};--cy:{num(y)};--fx:{num(fx)};--fy:{num(fy)}'
            f';--m:{m:g};--iso-rest:{op:g}" '
            f'cx="{num(x)}" cy="{num(y)}" r="{r:.1f}" '
            f'fill="url(#cf-stmt-sensor-{ramp})"/>')
    return "\n".join(out)


LATTICE_RE = re.compile(
    r'(<g class="sp-field__lattice"[^>]*>\n)(.*?)(\n\s*</g>)', re.S)
SENSORS_RE = re.compile(
    r'(<g class="sp-field__sensors">\n)(.*?)(\n\s*</g>)', re.S)


def splice(text):
    def one(m, maker):
        indent = re.match(r"\s*", m.group(2)).group(0).lstrip("\n")
        return m.group(1) + maker(indent) + m.group(3)
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
        print(f"  glow           r {R_MIN}..{R_MAX}  opacity "
              f"{OP_MIN:g}..{OP_MAX:g}  hot at r >= {HOT_AT}")
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
