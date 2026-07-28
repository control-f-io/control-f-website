#!/usr/bin/env python3
"""Generate the statement figure's lattice and its sensor field, on brand angles.

WHY A SCRIPT, and why now. The root beside this drawing has had a generator
since #218 — scripts/expertise-objects/gen-flow-root.py — and the field it
grows out of never did. Its hundred and forty-five glows carried hand-picked
radii: 11.5, 12.8, 13.4, 15.7 … 52.5, one number per circle, no rule anywhere
that produced them and none that could be checked. The standing brief has asked
for the opposite of that in as many words — "not random but mathematically
correct based on the ratios and winkel in the design system", "a rule, not a
table of hand-picked values" — and a table of a hundred and forty-five values IS
the finding.

IT ALSO COST THE PAGE ITS COMPOSITION, which is what forced the issue. The
drawing's height on the page is

    H = s x (V/2 + extent) + Rest + travel

    V       the figure's viewBox height          s     px per drawing unit
    extent  the field's vertical semi-extent     Rest  iso foot -> the frame's rail
    travel  the scene's arrival offset

because the drawing runs from its topmost glow down to the root's foot, the
foot is nailed to the lectern's rail (check-flow-handover.py) and the root
departs from the void's centre, which is V/2 by construction
(check-void-departure.py, identity 2). Rest is page furniture and the root's
own length is fixed at both ends, so V and `extent` are the ONLY two terms the
drawing's own geometry owns — and `extent` was an outcome of the largest
hand-picked radius rather than a decision. Measured in Chromium at 1440 x 900
before this script existed: extent 189.6 units, V 420, H 871.15 px against
810.06 px of viewport below the nav. 1.075. There was no scroll position at
which the whole drawing was on screen, at any viewport the gate admits.

THE LAW. Three constants and no table.

  THE LATTICE is the 2:1 isometry itself: vertices at (330 + 40a, cy + 20b) for
  every a + b even, so nearest neighbours lie at (+-40, +-20) — arctan 0.5,
  26.57 deg, the tilt the whole system is drawn on (foundations/geometry.html).
  Every instrument sits on one; nothing sits between them.

  THE RIM is that same 2:1 as an extent: the field is the ellipse of semi-axes
  2R x R about the void, which in the isometry's own metric — halve x, and the
  lattice becomes square — is simply the disc of radius R. An instrument exists
  at a vertex if it is inside that disc, and nowhere else. So the field has an
  extent of its own instead of four edges cut by the frame, which is what
  #cf-stmt-halo has asked for in prose since the mask was written.

  THE GLOW is one rise times one fall:

      r = r_min + (r_max - r_min) x clamp(2(v - 1), 0, 1) x (1 - |y - cy| / R)

  RISE, in the VOID's own metric: v = hypot(x - 330, y - cy) / 84. 84 is the
  radius the lattice is cut at and the drop the trunk departs by — the one
  number this figure and the root share. A glow is at the floor on the void's
  rim and full weight half a void-radius further out, so the middle is QUIET,
  NOT MISSING: floored, not culled, because an instrument that vanishes is a
  hole with an edge and that is the one thing a field of glows may not have
  (#216). The half is not decoration — over a whole radius the two factors
  fight, and the first render of this law was sixty-nine identical 12-unit
  circles with clear ground between every one of them. Merging needs
  2r > hypot(40, 20) = 44.72, the lattice's own nearest-neighbour distance,
  and that is the bar the rise is set by.

  FALL, in the VERTICAL, and the axis is the whole point. Height is what this
  drawing is short of, so the taper belongs on the axis that costs it: a glow
  on the field's top or bottom row is at the floor, one on the level of the
  void is at full weight however far out it sits. The two horizontal ends need
  no taper — #cf-stmt-reach fades the field to nothing at x 108 and x 648 and
  #cf-stmt-extent fades what is left — while NOTHING masks the vertical, which
  is exactly why the vertical had to be bounded by the geometry.

  WHAT THAT BUYS is the finding, inverted: the field's vertical semi-extent is
  now R plus the floor, a number this file SETS. Under the old table it was an
  outcome — the largest of the hundred and forty-five radii, 52.5, happened to
  sit two rows from the top, and the box was sized to hold it.

  OPACITY AND RAMP follow the radius and nothing else: opacity is r/r_max of
  the field's ceiling, quantised to the tenth the markup has always used, and a
  glow is drawn with the hot ramp once it is at least half of r_max. One
  quantity, three consequences.

THE TWO ENDS STAY PUT. The departure is at (330, cy + 84) — check-void-
departure.py holds that it is plumb under the void and in the field's quietest
fifth, and v = 1 exactly there, so the law puts every instrument around it at
the floor by construction rather than by tuning. --mx/--my is each glow's run
to that point and --m its slot in the collapse, both derived, neither typed.

DETERMINISTIC. No randomness, no seed, no jitter: the output is a function of
the five parameters below and nothing else. Re-run it and the same markup comes
out.

    python3 scripts/gen-stmt-field.py --check     # the shipped markup is ours
    python3 scripts/gen-stmt-field.py --write     # regenerate both copies
    python3 scripts/gen-stmt-field.py --report    # the parameters and what they cost
"""

import argparse
import math
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = [ROOT / "design-system" / "patterns" / "landing-page.html",
         ROOT / "design-system" / "components" / "statement.html"]

# ---------------------------------------------------------------- parameters
#
# BOX      1200 x V. The width is the system's: every .cf-iso is 1200 units
#          wide, which is what makes --iso-travel 30 (viewBox/40) and what makes
#          a flow unit and a statement unit the same length.
# VOID     84, shared with the root: the radius the lattice is cut at and the
#          drop the trunk departs by. Not free — check-void-departure.py.
# RIM      R, the field's semi-extent in the isometry's own (halved-x) metric.
#          THE ONE NUMBER THAT SETS THE DRAWING'S HEIGHT.
# R_MAX    the fullest glow, a shade over the lattice's own nearest-neighbour
#          distance (hypot(40, 20) = 44.72) so the field merges where it crowds.
# R_MIN    the floor in the quiet middle and at the rim.
WIDTH = 1200
BOX_H = 288
VOID = 84
RIM = 140
R_MAX = 52
R_MIN = 12
OPACITY_MAX = 0.6

PITCH_X, PITCH_Y = 40, 20          # the 2:1 lattice
MODULE = 32                        # the lattice lines' own step
LINE_C0 = 8                        # ... and its phase: c == 8 (mod 32)
B_LAST = 424                       # family B stops here: the drawing thins right
CX = 330                           # the void's x, and the departure's


def cy():
    return BOX_H / 2               # identity 2: the box top IS the void's centre


def dep():
    return (CX, cy() + VOID)       # where the root leaves, and where the field goes


def num(v):
    """A coordinate the way this drawing writes them: exact when it is."""
    v = round(v + 0.0, 2)
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return f"{v:g}"


# ------------------------------------------------------------------- lattice
#
# Two 26.57 deg families and the level step — the whole angle vocabulary this
# drawing is allowed. A family is the set of lines y = +-x/2 + c on the module's
# own phase; each is clipped to the box and then cut by the void, because the
# absence has to be legible or the figure has no argument.

def clip_to_box(p, q):
    """The part of the segment p->q inside 0..WIDTH x 0..BOX_H, or None."""
    (x1, y1), (x2, y2) = p, q
    dx, dy = x2 - x1, y2 - y1
    t0, t1 = 0.0, 1.0
    # Liang-Barsky: each edge is one inequality p*t <= q on the parameter.
    for pk, qk in ((-dx, x1), (dx, WIDTH - x1), (-dy, y1), (dy, BOX_H - y1)):
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


def cut_void(p, q):
    """Split the segment where it runs through the void. One piece, or two."""
    (x1, y1), (x2, y2) = p, q
    dx, dy = x2 - x1, y2 - y1
    vx, vy = x1 - CX, y1 - cy()
    a = dx * dx + dy * dy
    b = 2 * (vx * dx + vy * dy)
    c = vx * vx + vy * vy - VOID * VOID
    disc = b * b - 4 * a * c
    if disc <= 0:
        return [(p, q)]
    s = math.sqrt(disc)
    ta, tb = (-b - s) / (2 * a), (-b + s) / (2 * a)
    ta, tb = max(0.0, ta), min(1.0, tb)
    if ta >= tb:
        return [(p, q)]
    at = lambda t: (x1 + t * dx, y1 + t * dy)
    out = []
    if ta > 1e-9:
        out.append((p, at(ta)))
    if tb < 1 - 1e-9:
        out.append((at(tb), q))
    return out


def lattice():
    """Every construction line, in the order the drawing has always carried
    them: the down-right family, the down-left family, then the level step."""
    lines = []
    for sign, lo, hi in ((+1, -WIDTH // 2 - MODULE, BOX_H),
                         (-1, 0, B_LAST + 1)):
        c = LINE_C0 + MODULE * math.ceil((lo - LINE_C0) / MODULE)
        while c < hi:
            # y = sign * x/2 + c, taken right across the box and clipped back
            p, q = (0.0, c), (float(WIDTH), c + sign * WIDTH / 2)
            seg = clip_to_box(p, q)
            if seg:
                lines.extend(cut_void(*seg))
            c += MODULE
    y = MODULE // 2
    while y <= BOX_H - MODULE // 2:
        seg = clip_to_box((0.0, float(y)), (float(WIDTH), float(y)))
        if seg:
            lines.extend(cut_void(*seg))
        y += MODULE
    return lines


# --------------------------------------------------------------------- field

def glow(x, y):
    """The one law: out of the void's rim, dead at the field's, floored.

    RISE is over HALF a void-radius, not a whole one, and that half is the
    difference between a field and a grid of separate rings. Over a whole
    radius the two factors fight — the vertical room between the void's rim
    (84) and the field's (RIM) is barely two lattice rows, so a glow that is
    still climbing where the other factor is already falling never gets past
    the floor, and the first render of this law was 69 identical 12-unit
    circles with clear ground between every one of them. The reference this
    field is drawn from merges where the dots crowd, and merging needs
    2r > hypot(40, 20) = 44.72: the lattice's own nearest-neighbour distance,
    which is the bar the rise is set by.
    """
    v = math.hypot(x - CX, y - cy()) / VOID
    fall = 1.0 - abs(y - cy()) / RIM
    return R_MIN + (R_MAX - R_MIN) * min(1.0, max(0.0, 2 * (v - 1.0))) * fall


def field():
    """Every lattice vertex inside the rim, with its glow, nearest the
    departure first — which is the order the collapse runs in."""
    out = []
    span_a = int(RIM * 2 / PITCH_X) + 2
    span_b = int(RIM / PITCH_Y) + 2
    for a in range(-span_a, span_a + 1):
        for b in range(-span_b, span_b + 1):
            if (a + b) % 2:
                continue
            x, y = CX + a * PITCH_X, cy() + b * PITCH_Y
            if math.hypot(a * PITCH_X / 2, b * PITCH_Y) > RIM + 1e-9:
                continue
            out.append((x, y, glow(x, y)))
    dx, dy = dep()
    out.sort(key=lambda p: (math.hypot(p[0] - dx, p[1] - dy), p[0], p[1]))
    far = max(math.hypot(x - dx, y - dy) for x, y, _ in out)
    rows = []
    for x, y, r in out:
        m = round(math.hypot(x - dx, y - dy) / far, 1)
        op = max(0.1, round(r / R_MAX * OPACITY_MAX, 1))
        ramp = "hot" if r >= R_MAX / 2 else "halo"
        rows.append((x, y, r, op, m, ramp))
    return rows


def extent():
    """What the field costs in each axis, which is the whole reason for the law."""
    rows = field()
    return (max(abs(y - cy()) + r for _, y, r, _, _, _ in rows),
            max(abs(x - CX) + r for x, _, r, _, _, _ in rows))


# -------------------------------------------------------------------- markup

def lattice_markup(indent):
    return "\n".join(
        f'{indent}<line x1="{num(p[0])}" y1="{num(p[1])}" '
        f'x2="{num(q[0])}" y2="{num(q[1])}"/>' for p, q in lattice())


def field_markup(indent):
    dx, dy = dep()
    out = []
    for x, y, r, op, m, ramp in field():
        out.append(
            f'{indent}<circle class="cf-stmt-sensor" '
            f'style="--mx:{num(dx - x)};--my:{num(dy - y)};--m:{m:g}" '
            f'cx="{num(x)}" cy="{num(y)}" r="{r:.1f}" opacity="{op:g}" '
            f'fill="url(#cf-stmt-sensor-{ramp})"/>')
    return "\n".join(out)


GHOST_RE = re.compile(
    r'(<g class="cf-iso__ghost"[^>]*stroke-dasharray="1 4">\n)(.*?)(\n\s*</g>)', re.S)
FIELD_RE = re.compile(r'(<g class="cf-stmt-field">\n)(.*?)(\n\s*</g>)', re.S)


def splice(text):
    def one(m, maker):
        indent = re.match(r"\s*", m.group(2)).group(0).lstrip("\n")
        return m.group(1) + maker(indent) + m.group(3)
    text, n1 = GHOST_RE.subn(lambda m: one(m, lattice_markup), text, count=1)
    text, n2 = FIELD_RE.subn(lambda m: one(m, field_markup), text, count=1)
    return text, n1 + n2


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    if args.report or not (args.write or args.check):
        ev, eh = extent()
        rows = field()
        print(f"  box            1200 x {BOX_H}   void ({CX}, {num(cy())}) r {VOID}")
        print(f"  rim R          {RIM}  (2:1 ellipse, semi-axes {2 * RIM} x {RIM})")
        print(f"  glow           r_max {R_MAX}  r_min {R_MIN}  "
              f"hot at r >= {R_MAX / 2:g}")
        print(f"  instruments    {len(rows)}   lattice lines {len(lattice())}")
        print(f"  extent         {ev:.1f} vertical, {eh:.1f} horizontal "
              f"({eh / ev:.2f} : 1)")
        print(f"  the height     V/2 + extent = {cy() + ev:.1f} units")
        print(f"  void clearance {ev / VOID:.2f} x the void's radius")
        if not (args.write or args.check):
            return 0

    rc = 0
    for page in PAGES:
        text = page.read_text(encoding="utf-8")
        new, n = splice(text)
        if n != 2:
            print(f"gen-stmt-field: {page.name}: found {n} of 2 blocks — "
                  f"the markers went stale")
            rc = 1
            continue
        if args.write:
            if new != text:
                page.write_text(new, encoding="utf-8")
                print(f"  wrote {page.relative_to(ROOT)}")
            else:
                print(f"  {page.relative_to(ROOT)} already current")
        elif new != text:
            print(f"gen-stmt-field: {page.relative_to(ROOT)} is not what this "
                  f"script generates — re-run with --write")
            rc = 1
    if args.check and rc == 0:
        print("gen-stmt-field: both copies are the generator's output")
    return rc


if __name__ == "__main__":
    sys.exit(main())
