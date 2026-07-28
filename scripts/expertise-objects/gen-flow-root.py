#!/usr/bin/env python3
"""Generate the statement-to-process flow as a branching root, on brand angles.

WHY A SCRIPT. The flow used to be a bus and two drops: one split, one
generation, seven parallel verticals. A root is self-similar -- every branch
spawns smaller branches at the same ratio, several generations deep -- and that
is not a shape anyone types by hand and keeps on the brand's five angles. It is
also not a shape that may be random at runtime: foundations/illustration.html
draws construction, and a construction is the same every time it is drawn. So
the geometry is computed HERE, deterministically, and the result is pasted into
patterns/landing-page.html. Re-run it and the same paths come out.

THE FIVE ANGLES (foundations/geometry.html#angles) are the whole vocabulary:
0deg, 26.57deg, 45deg, 63.43deg, 90deg. Every segment is one of them, which is
what keeps a recursive form from becoming an organic squiggle this system has
no words for. A step is named by the angle it leaves at and sized by the
VERTICAL extent it covers, because the drawing's budget is vertical: the whole
root has 536 units of drop to spend and 1200 of width to cross.

  V   90deg      (0, h)
  S   63.43deg   (h/2, h)     steep -- the tip diving
  D   45deg      (h, h)
  F   26.57deg   (2h, h)      flat -- the only angle that crosses width cheaply

THE THREE TAPROOTS ARE PINNED. flow x 0, 600 and 1200 are frame x 0, 500 and
1000 -- the two elements are the same width on the same 1200-unit basis -- so
three of the root's terminals are not free: they must arrive exactly at
(0, 620), (600, 620) and (1200, 620), where the frame's three verticals begin.
Those three chains are written out below rather than generated, because an
exact arrival is a constraint and not an outcome. Note what the constraint
costs: 26.57deg is the flattest angle in the system, so reaching x 1200 from
the trunk cannot be done in less than 425 units of drop. The right taproot is
long because the vocabulary makes it long.

EVERYTHING ELSE IS GROWN, and thins as it goes -- by LENGTH, never by weight.
foundations/illustration.html: "weight does not vary -- depth is carried by
node radius and by overlap, never by drawing". So a generation-3 twig is a
short 1 px line, not a thin one.

NO FREE ENDS. Every terminal arrives: on the rail at y 620, or on another
branch. The script asserts it -- and scripts/check-flow-terminals.py asserts it
again on the shipped markup, which is where it can actually rot.
"""

from fractions import Fraction as F

RAIL = F(620)          # the frame's top rail, in flow units
LEFT, RIGHT = F(0), F(1200)

# ---------------------------------------------------------------- primitives

STEPS = {
    "V":  (F(0), F(1)),
    "SR": (F(1, 2), F(1)),  "SL": (F(-1, 2), F(1)),
    "DR": (F(1), F(1)),     "DL": (F(-1), F(1)),
    "FR": (F(2), F(1)),     "FL": (F(-2), F(1)),
}

# One notch steeper / flatter, staying on the five angles. Used by the growth
# rule: a child leaves its parent by turning exactly one notch, which is the
# discrete equivalent of the constant branch angle a root actually holds.
# A direction is a kind and a side, so that "one notch steeper" and "the other
# way" are two independent moves rather than a lookup with seven holes in it.
KINDS = ["F", "D", "S", "V"]          # flattest to steepest


def turn(kind, notches):
    return KINDS[max(0, min(len(KINDS) - 1, KINDS.index(kind) + notches))]


def name_of(kind, side):
    return "V" if kind == "V" else kind + ("R" if side > 0 else "L")

segments = []   # (x1, y1, x2, y2, dist) -- dist is the run from the void to x1
DIST = {}       # junction -> its run from the void, so a branch inherits it


def walk(x, y, chain):
    """Emit a chain of steps from (x, y); stop early at the rail or a wall."""
    d = DIST[(x, y)]
    for name, h in chain:
        dx, dy = STEPS[name]
        nx, ny = x + dx * h, y + dy * h
        if ny >= RAIL:                      # clip to the rail: it arrives there
            t = (RAIL - y) / (ny - y)
            nx, ny = x + (nx - x) * t, RAIL
        if nx < LEFT or nx > RIGHT:         # a wall is not something to arrive at
            raise SystemExit(f"branch left the box at ({nx}, {ny})")
        segments.append((x, y, nx, ny, d))
        # Chebyshev, not Euclidean: exact in Fractions, monotone along a path,
        # and never more than 12 % off on the five angles. It only has to order
        # the segments, and it orders them the same way.
        d += max(abs(nx - x), abs(ny - y))
        x, y = nx, ny
        DIST.setdefault((x, y), d)
        if ny >= RAIL:
            return x, y, True
    return x, y, False


# ------------------------------------------------------- the pinned skeleton
#
# The trunk leaves the void at 90deg and splits twice, not once: the left
# taproot at y 150, then the middle and right at y 195. Two bifurcations
# instead of one trifurcation, because a root bifurcates.

DIST[(F(330), F(84))] = F(0)
walk(F(330), F(84), [("V", F(66))])                       # trunk, out of the void

# left taproot -> (0, 620): flat, then 45, then steep, then the last drop.
walk(F(330), F(150), [("FL", F(90)), ("DL", F(90)), ("SL", F(120)), ("V", F(170))])
# the right spine, to the second split
walk(F(330), F(150), [("FR", F(45))])
# middle taproot -> (600, 620). Its long steep run is written as two collinear
# steps, and the right taproot's first flat one likewise: a root branches along
# a straight length as well as at its bends, and a junction is where a branch
# can leave from. Neither changes the taproot's path by a unit.
walk(F(420), F(195), [("DR", F(60)), ("SR", F(100)), ("SR", F(140)), ("V", F(125))])
# right taproot -> (1200, 620). 355 of flat and 70 of 45 is the only split of
# the drop budget that lands on 1200 at all; the lengths taper.
#
# ITS LONGEST RUN IS SPLIT TOO, and it is the one the rule above was written
# for and never reached. 125 of drop at 26.57deg is 250 of width -- the single
# longest step in the drawing -- and it crossed the emptiest ground on it with
# no junction anywhere along it, so nothing could leave. Measured on the paste
# it replaces: of the drawing's 4795 units of ink, the 200-unit band at x
# 800-1000 held 6.0 % against 27.5 % in the band at the other wall, and the
# right half held 35.6 % of the whole. A root branches along a straight length;
# a run this long that does not is the bus this drawing replaced, kept alive in
# its emptiest quarter. 60 + 65 puts the junction at (840, 405), which is
# inside that band and leaves 215 of drop under it -- enough for the growth
# rule to size a branch that lands on the rail rather than one more twig.
# The taproot's path is not changed by a unit.
walk(F(420), F(195), [("FR", F(70)), ("FR", F(80)), ("FR", F(60)), ("FR", F(65)),
                      ("FR", F(80)), ("DR", F(70))])

SKELETON = len(segments)

# --------------------------------------------------------------- the growth
#
# Junctions in the lower half only. A taproot is bare near the crown and
# branchy near the tip, and it is also the only way to keep the fringe SHORT:
# a branch leaving at y 300 has 320 units to fall and reads as one more long
# parallel drop, which is the diagram this replaces. Branch points, ratio and
# turn are fixed values, so the fan is the same every run.

RATIO = F(5, 8)        # where a branch puts its own junction, in its drop

# A BRANCH IS SIZED BY THE DROP IT HAS LEFT, not by the length of its parent.
# That is the one rule that makes this a root rather than the bus it replaces.
# Size a branch by its parent and a branch leaving high has to fall the rest of
# the way as a vertical, which is a long parallel drop -- seven of those was
# the old diagram. Size it by the remaining drop and it lands ON the rail at an
# angle, and shrinks on its own as it gets closer: the fringe is fine near the
# rail because there is little left to fall there. Self-similar in the sense
# that matters, which is shape -- the same two turns and the same 5:3 split of
# whatever drop is left.


def grow(x, y, kind, depth, side):
    """One branch: turn a notch, run 5/8 of the drop, turn again, meet the rail.

    Then the same again from its own junction, on the other side. Depth is
    capped at two generations of this; a third puts more line under the rail's
    last 60 units than the eye can separate at 1 px.
    """
    rem = RAIL - y
    if depth > 2 or rem < 60:
        return
    # A BRANCH ALTERNATES 45 AND 63.43, and never uses the outer two angles.
    # Both of those were drawn and thrown away. Turning one notch steeper each
    # time ends every branch at 90, and the bottom of the drawing comes out a
    # picket fence -- the parallel drops this was meant to be rid of. Turning
    # one notch flatter each time puts 26.57 in the fringe, and 26.57 crosses
    # twice its own drop: at 290 units of drop left, a branch 580 wide, which
    # is wider than the taproot it hangs off. It read as a net, not a root.
    # The two middle angles are the only ones that descend without sprawling,
    # and alternating them is a kink rather than a turn -- so a branch stays
    # legible as a branch at 1 px.
    a = "S" if kind in ("F", "D") else "D"
    b = "D" if a == "S" else "S"
    h1 = F(5) * round(rem * RATIO / 5)  # on fives, so the paste stays readable
    h2 = rem - h1
    if not (LEFT <= x + STEPS[name_of(a, side)][0] * h1 <= RIGHT):
        side = -side                    # a wall is not something to arrive at
    x1, y1, _ = walk(x, y, [(name_of(a, side), h1)])
    side2 = side
    if not (LEFT <= x1 + STEPS[name_of(b, side2)][0] * h2 <= RIGHT):
        side2 = -side2                  # the tip curves back rather than out
    if not (LEFT <= x1 + STEPS[name_of(b, side2)][0] * h2 <= RIGHT):
        b = "V"                         # ...and only then falls straight
    walk(x1, y1, [(name_of(b, side2), h2)])
    grow(x1, y1, a, depth + 1, -side)


# The seven junctions that carry a branch, and the step that made each of them:
# lower half only. A taproot is bare near the crown and branchy near the tip.
for jx, jy, pkind, d, side in [
    (F(150), F(240), "F", 1, +1),   # left taproot, its first bend
    (F(60),  F(330), "D", 1, +1),   # left taproot, the 45 junction
    (F(0),   F(450), "S", 2, +1),   # left taproot, the last corner
    (F(530), F(355), "S", 2, +1),   # middle taproot, along the steep run
    (F(600), F(495), "S", 2, -1),   # middle taproot, the last corner
    (F(720), F(345), "F", 1, -1),   # right taproot, its first bend
    (F(840), F(405), "F", 1, +1),   # right taproot, along its longest run
    (F(970), F(470), "F", 1, +1),   # right taproot, second bend
    (F(1130), F(550), "F", 2, -1),  # right taproot, the tip\'s shoulder
]:
    grow(jx, jy, pkind, d, side)

# ---------------------------------------------------------------- assertions

def on_rail(y):
    return y == RAIL


def on_segment(px, py, seg):
    x1, y1, x2, y2 = seg[:4]
    if (px, py) == (x1, y1) or (px, py) == (x2, y2):
        return True
    cross = (x2 - x1) * (py - y1) - (y2 - y1) * (px - x1)
    if cross != 0:
        return False
    return min(x1, x2) <= px <= max(x1, x2) and min(y1, y2) <= py <= max(y1, y2)


free = []
for i, (x1, y1, x2, y2, d) in enumerate(segments):
    # every segment is on one of the five angles
    dx, dy = x2 - x1, y2 - y1
    ok = dx == 0 or dy == 0 or abs(dx / dy) in (F(1, 2), F(1), F(2))
    assert ok, f"segment {i} is off the brand angles: {dx}/{dy}"
    if on_rail(y2):
        continue
    if any(on_segment(x2, y2, s) for j, s in enumerate(segments) if j != i):
        continue
    free.append((i, x2, y2))

print(f"{len(segments)} segments ({SKELETON} pinned, {len(segments) - SKELETON} grown)")
print(f"free ends: {len(free)}  {free}")
assert not free, "a root has no free ends"

# --------------------------------------------------------------------- paste
#
# --l is the segment's RUN FROM THE VOID, not its generation. The stage grows
# what the data has reached, so a twig hanging off the trunk lights before a
# taproot's far tip does, exactly as a root fills out. Normalised to the 0-3
# the old bus already spanned, so the flow's timing envelope -- which the
# motion lane measures and owns -- is the one that was there before.

MAXD = max(d for *_, d in segments)


def num(v):
    v = float(v)
    return str(int(v)) if v == int(v) else f"{v:g}"


def level(d):
    return num(round(float(3 * d / MAXD), 2))


def data(x1, y1, x2, y2):
    if x1 == x2:
        return f"M{num(x1)} {num(y1)}V{num(y2)}"
    if y1 == y2:
        return f"M{num(x1)} {num(y1)}H{num(x2)}"
    return f"M{num(x1)} {num(y1)}L{num(x2)} {num(y2)}"


# THE AXES, one per stroke, each written FAR END -> ORIGIN. The reason is on
# the page: a userSpaceOnUse gradient is resolved in the element\'s own user
# space, so the scale-draw that grows a stroke carries the ramp with it and
# whatever colour sits at the path\'s far end sits at the growing tip at every
# scale. Lime at the tip, CF-Grau trailing into the junction the stroke left.
# Every axis is its own stroke\'s line, so the gradient\'s angle is a brand
# angle without anything typing one.
print()
for i, (x1, y1, x2, y2, d) in enumerate(segments):
    print(f'<linearGradient id="lp-flow-ax-{i:02d}" href="#lp-flow-ramp" '
          f'gradientUnits="userSpaceOnUse" x1="{num(x2)}" y1="{num(y2)}" '
          f'x2="{num(x1)}" y2="{num(y1)}"/>')

print()
for i, (x1, y1, x2, y2, d) in enumerate(segments):
    o = "0 0" if x2 >= x1 else "100% 0"
    print(f'<path class="lp-flow__light" style="--o:{o};--l:{level(d)}" '
          f'stroke="url(#lp-flow-ax-{i:02d})" d="{data(x1, y1, x2, y2)}"/>')

print()
for x1, y1, x2, y2, d in segments:
    o = "0 0" if x2 >= x1 else "100% 0"
    print(f'<path class="lp-flow__seg" style="--o:{o};--l:{level(d)}" d="{data(x1, y1, x2, y2)}"/>')

# THE NODES. r steps down with distance from the subject, which the manual
# states and this drawing can honour literally: the two splits are nearest the
# void and get r 3, the taproots' own branch points r 2, the fringe r 1. Eight,
# because "eight is a lot for one object; twelve is too many" -- so the three
# rail arrivals carry none. They do not need one: the frame's own verticals
# stand up out of them, which is a louder mark than a 2 px dot.
print()
NODES = [
    (F(330), F(150), 3), (F(420), F(195), 3),
    (F(60), F(330), 2), (F(480), F(255), 2), (F(720), F(345), 2),
    (F(0), F(450), 1), (F(970), F(470), 1), (F(600), F(495), 1),
]
for nx, ny, r in NODES:
    assert (nx, ny) in DIST, f"node at ({nx}, {ny}) is not a junction"
    print(f'<circle class="lp-flow__node" style="--l:{level(DIST[(nx, ny)])}" '
          f'cx="{num(nx)}" cy="{num(ny)}" r="{r}"/>')

# ------------------------------------------------------------------ the values
#
# WHAT THE ROOT IS CARRYING. The drawing said data moves; it did not say how
# much, and a route with no quantity on it is a pipe rather than a stream. Six
# values ride the routes -- the source on the trunk, one on each of the three
# taproots where it leaves the crown, and the two the right taproot divides
# into where the drawing is emptiest.
#
# THEY CONSERVE, and that is the whole reason they are generated rather than
# typed. At any labelled point the value equals the sum of the labelled values
# immediately downstream of it: 12 480 leaves the void and 3 840 + 3 200 +
# 5 440 leave the crown; 5 440 divides into 1 360 + 4 080. A number that does
# not balance is a drawing telling the reader something untrue about itself,
# which is the one thing an illustration of data flow cannot afford. Asserted
# here and again on the shipped markup by scripts/check-flow-values.py.
#
# A value is a POINT ON A SEGMENT, never a free coordinate: it rides the route
# it belongs to. The assertion below finds the segment it lies on and takes its
# --l from the run to that point, so a value lights exactly as the data reaches
# it -- one window, the node's, which the motion lane owns.
#
# The offset is in PIXELS, not units. The numerals are real HTML at the label
# ramp's 11 px, so they do not scale with the box; a clearance from the stroke
# expressed in units would close up as the drawing shrinks. dx/dy carry the
# anchoring too -- "-100%" is right-aligned to the point, "-50%" centred.

# WHICH SIDE OF ITS OWN LINE A VALUE SITS ON IS NOT A TASTE. A numeral is a
# horizontal box on a sloped line, so "8 px below the point" is only 8 px of
# clearance at the point: on the 26.57deg runs the line drops 34 px across the
# width of a six-digit label and walks straight back through it. Measured at
# 1440x900 on the first paste -- 4 080 sat at flow y 422-436, x 871-903, and
# its own taproot crossed that box from 420.5 to 436.5. So a value on a line
# heading DOWN-RIGHT sits ABOVE it and one heading DOWN-LEFT sits BELOW it,
# which is the side the line is walking away from; clearance then grows across
# the label instead of closing.
#
# AND THE CROWN SITS IN THE STATEMENT'S GHOST FIELD. The lattice the statement
# figure scatters overlaps the top of this box: its rules land on flow y 96,
# 128 and 160 (its own 32-unit rows, offset 240 -- measured, not declared).
# The source value is 14 units tall, so it goes in the 32-unit band between 96
# and 128 rather than on a rule. It was on 128 and read as "12.480".

VALUES = [
    # x, y, value, dx, dy -- dx/dy are CSS, applied after the % placement
    (F(330), F(112), 12480, "12px",                "-50%"),
    (F(250), F(190),  3840, "12px",                "8px"),
    (F(450), F(225),  3200, "calc(-100% - 12px)",  "8px"),
    (F(500), F(235),  5440, "12px",                "calc(-100% - 8px)"),
    (F(690), F(405),  1360, "calc(-100% - 12px)",  "-50%"),
    (F(860), F(415),  4080, "12px",                "calc(-100% - 8px)"),
]


def run_to(px, py):
    """The run from the void to a point, via the segment it lies on."""
    for x1, y1, x2, y2, d in segments:
        if on_segment(px, py, (x1, y1, x2, y2)):
            return d + max(abs(px - x1), abs(py - y1))
    raise AssertionError(f"the value at ({px}, {py}) rides no route")


def downstream_labelled(px, py, labelled):
    """The labelled points reachable from here without passing another.

    Every step of this drawing descends, so downstream is simply larger y and
    the walk cannot loop. A labelled point STOPS its branch -- that is what
    makes the sum below a statement about one generation rather than about the
    whole subtree.
    """
    found, seen, stack = set(), set(), [(px, py)]
    while stack:
        p = stack.pop()
        for x1, y1, x2, y2, _ in segments:
            seg = (x1, y1, x2, y2)
            if (x2, y2) == p or not on_segment(p[0], p[1], seg):
                continue
            below = sorted(l for l in labelled
                           if l[1] > p[1] and on_segment(l[0], l[1], seg))
            q = min(below, key=lambda l: l[1]) if below else (x2, y2)
            if q in labelled:
                found.add(q)
            elif q not in seen:
                seen.add(q)
                stack.append(q)
    return found


LABELLED = {(x, y): v for x, y, v, *_ in VALUES}
for (px, py), v in LABELLED.items():
    kids = downstream_labelled(px, py, set(LABELLED))
    if kids:
        total = sum(LABELLED[k] for k in kids)
        assert total == v, (f"the value at ({px}, {py}) is {v} and the "
                            f"{len(kids)} below it total {total}")

print()
# A PLAIN SPACE, AND THE THOUSANDS SEPARATOR IS STILL UNBREAKABLE. This emitted
# U+00A0 and the shipped paste carried U+0020, so six of the generator's 125
# lines did not match the markup it is the source of truth for -- invisible on
# the page, and exactly the drift "re-run it and the same lines come out" is a
# claim against. The plain space is the correct one of the two: .lp-flow__val
# sets `white-space: nowrap`, so the break the no-break space was insuring
# against cannot happen, and an insurance that no longer does any work is one
# more thing for a hand edit to get wrong.
SEP = " "
for x, y, v, dx, dy in VALUES:
    text = f"{v // 1000}{SEP}{v % 1000:03d}" if v >= 1000 else str(v)
    print(f'<span class="t-label lp-flow__val" style="--x:{num(x)};--y:{num(y)};'
          f'--tx:{dx};--ty:{dy};--l:{level(run_to(x, y))}">{text}</span>')
