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

AND NO CROSSINGS, which is the same sentence about the middle of a stroke
rather than its end, and was the half this script did not say. The growth rule
turned a branch away from a WALL and had no idea the rest of the root was
there, so three branches walked through their own siblings -- at (600, 550),
(195, 555) and (653.33, 478.33). In a construction drawing two lines crossing
with nothing on the crossing MEANS "not connected", and none of the three could
carry a node, because a crossing is not a junction. A drawing whose subject is
data merging was denying it three times in its own vocabulary.

So the wall test became a room test, and a branch is now chosen WHOLE: both
legs together, first free pair wins, in the preference order the rule always
had (the side it wants, the other side, then straight down), and a branch with
no free pair is not grown. Leg by leg is not enough -- flipping leg 1 to clear
a crossing is exactly what laid a child branch along its parent's leg 2, which
is one stroke at twice the weight and worse than the crossing it was reached
for. scripts/check-flow-crossings.py asserts the result on the paste.
"""

import math
from collections import Counter
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

CROWN = F(170)         # where the trunk stops being a trunk

# HOW CLOSE TWO STROKES MAY COME, in drawing units, where they are not joined.
# At the gate floor the box renders 1024 units wide, so one drawing unit is
# 0.853 px: 14 units is 12 px of daylight at the smallest the figure gets, and
# 16 px at 1440. Under about 12 the two strokes stop reading as two, and this
# is the number that decides how many arms the box will take -- at 18 the root
# grew 24 limbs and the fringe had room it was not allowed to use.
CLEAR = F(14)

# HOW DEEP A LIMB MAY DIVIDE. Three generations of grow() below a seed; a
# fifth puts more line under the rail's last 60 units than the eye separates
# at 1 px. CLEAR is what actually stops it: a generation with no room simply
# is not grown, so raising the cap adds arms where there is space for them and
# nothing where there is not.
DEPTH = 4

# WHERE A BRANCH DIVIDES ITS REMAINING DROP, cycled by depth and side so no two
# sibling limbs divide at the same height. See grow().
RATIOS = (F(5, 8), F(1, 2), F(5, 9), F(3, 5), F(4, 9))

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


def name_of(kind, side):
    return "V" if kind == "V" else kind + ("R" if side > 0 else "L")


def lands(x, y, name, h):
    """Where a step would actually be drawn: clipped to the rail."""
    dx, dy = STEPS[name]
    nx, ny = x + dx * h, y + dy * h
    if ny > RAIL:
        t = (RAIL - y) / (ny - y)
        nx, ny = x + (nx - x) * t, RAIL
    return nx, ny


def touches(x, y, nx, ny):
    """Does the step (x,y)->(nx,ny) run into something already drawn?

    A ROOT DOES NOT PASS THROUGH ITSELF, and in this system that is not a
    botanical nicety: the drawing's whole vocabulary is construction, where two
    lines crossing without a dot on the crossing means "these are not
    connected". A crossing in a drawing whose entire subject is data merging
    tells the reader, in the drawing's own language, that it does not.

    A step leaves a junction that already carries strokes, and it may END on
    another branch. So the parameter is open at the start and CLOSED at the
    finish: 0 < t < 1 is a crossing, t == 1 is an arrival.

    AND THE PARALLEL CASE IS NOT "no intersection". Two steps leaving the SAME
    junction on the SAME angle have no crossing point to find, because one lies
    along the other: one stroke at twice the weight and a limb missing, which
    is worse than the crossing it was reached for and invisible in a diff. So
    collinearity is tested first and shares no code with the crossing test.
    """
    for x1, y1, x2, y2, _ in segments:
        det = (nx - x) * (y2 - y1) - (ny - y) * (x2 - x1)
        if det == 0:
            if (x1 - x) * (ny - y) - (y1 - y) * (nx - x) != 0:
                continue
            lo, hi = min(y, ny), max(y, ny)
            if min(y1, y2) < hi and max(y1, y2) > lo:
                return True
            continue
        t = ((x1 - x) * (y2 - y1) - (y1 - y) * (x2 - x1)) / det
        u = ((x1 - x) * (ny - y) - (y1 - y) * (nx - x)) / det
        if 0 < t < 1 and 0 <= u <= 1:
            return True
    return False


def free(x, y, name, h, clear=CLEAR):
    """Is this step clear — inside the box, clear of the drawing, and not
    crowding it?

    THE FIRST TWO CLAUSES ARE THE OLD TEST. The third is what the grown root
    was missing and the symmetric one bought by giving up growth: a step that
    crosses nothing can still run a few units off a sibling for its whole
    length, and at 1 px two strokes four units apart are one thick stroke that
    flickers. `touches` answers a topological question; this answers the
    optical one, and a root that fills a box needs both. CLEAR is in drawing
    units and is the floor for the whole construction — see its own note.
    """
    nx, ny = lands(x, y, name, h)
    if not (LEFT <= nx <= RIGHT):
        return False
    if ny <= y:
        return False
    # A ROOT IS A TREE, AND A TREE HAS ONE FEWER JUNCTION THAN IT HAS STROKES.
    # Two limbs are free to grow toward each other and, on a lattice this
    # regular, to arrive at exactly the same point — which is not an arrival,
    # it is a MERGE, and it closes a cycle. The drawing survives it (no free
    # end, no crossing) and the timing does not: a point reached twice inherits
    # the run of whichever limb got there first, so everything below it lights
    # before the other limb has arrived. check-flow-chain.py caught it as
    # "54 junctions for 53 strokes". The rail is the exception and the only
    # one: every foot lands on it, and feet are meant to share it.
    if ny < RAIL and (nx, ny) in DIST:
        return False
    if touches(x, y, nx, ny):
        return False
    return gap_ok(x, y, nx, ny, clear)


def gap_ok(x, y, nx, ny, clear):
    """No point of this step is within `clear` units of a stroke it does not
    share an endpoint with. Sampled, not solved: the segment-to-segment
    distance in exact Fractions needs a square root to compare against a
    length, and sampling at 5-unit steps on a drawing whose shortest stroke is
    30 units is finer than the question. Endpoints are exempted because a
    junction is exactly where two strokes are meant to be at distance zero."""
    ends = {(x, y), (nx, ny)}
    span = max(abs(nx - x), abs(ny - y))
    n = max(2, int(span / 5))
    c2 = clear * clear
    for x1, y1, x2, y2, _ in segments:
        if ends & {(x1, y1), (x2, y2)}:
            continue
        for k in range(n + 1):
            px = x + (nx - x) * F(k, n)
            py = y + (ny - y) * F(k, n)
            if _d2_point_seg(px, py, x1, y1, x2, y2) < c2:
                return False
    return True


def _d2_point_seg(px, py, x1, y1, x2, y2):
    vx, vy = x2 - x1, y2 - y1
    wx, wy = px - x1, py - y1
    vv = vx * vx + vy * vy
    if vv == 0:
        return wx * wx + wy * wy
    t = (wx * vx + wy * vy) / vv
    t = max(F(0), min(F(1), t))
    dx, dy = wx - t * vx, wy - t * vy
    return dx * dx + dy * dy


# ------------------------------------------------------- the pinned skeleton
#
# THE THREE ARRIVALS THE FRAME IS PINNED TO. flow x 0, 600 and 1200 are frame
# x 0, 500 and 1000 — the two elements share a 1200-unit basis — so three of
# the root's feet are not free: they must land exactly on (0, 620), (600, 620)
# and (1200, 620), where the lectern's three verticals stand up. Those chains
# are written out; an exact arrival is a constraint and not an outcome.
#
# The reach leaves the trunk at 45deg and crosses the width at 26.57deg, and
# not the reverse: the flat leg then crosses the interior band x 400-600 that
# check-flow-density.py floors, and steep-first left it under the floor with
# the same junctions either way.

DIST[(F(600), F(84))] = F(0)
walk(F(600), F(84), [("V", CROWN - 84)])                   # trunk, out of the void
# the centre taproot, broken into runs for the same reason the reach is: a
# 450-unit vertical with no junction on it is 450 units of drawing nothing can
# leave from, and the trunk is where a root is busiest.
walk(F(600), CROWN, [("V", F(110)), ("V", F(100)), ("V", F(110)), ("V", F(130))])

for side in (-1, +1):
    d, f = name_of("D", side), name_of("F", side)
    # THE REACH STEPS, IT DOES NOT RULE. Four collinear 26.57deg runs in a row
    # are one straight line 500 units long however many strokes it is written
    # as, and a straight line from the crown to the corner is the one thing a
    # root never does — it read as a drawn ruler with twigs hung off it. So the
    # reach alternates 45 and 26.57 all the way down: the steep leg drops, the
    # flat leg crosses, and the pair repeats. Same two angles the branches use,
    # same arrival — dx -600, dy 450, exactly (0, 620) — and six junctions
    # instead of four, spread over the whole descent instead of bunched in its
    # last third.
    walk(F(600), CROWN, [(d, F(60)), (f, F(90)), (d, F(60)), (f, F(90)),
                         (d, F(60)), (f, F(30)), ("V", F(60))])

SKELETON = len(segments)

# --------------------------------------------------------------- the growth
#
# BACK TO A GROWN ROOT, and the review that retired growth is answered rather
# than reversed. The complaint against the first grown root was true —
# branches chosen one leg at a time around their own obstacles, three terminals
# landing mid-stroke on a sibling, twice the ink on one side — and the answer
# then was to write the whole drawing out as one symmetric construction. That
# fixed the overlaps by removing the thing that made them, and what came out
# was eighteen strokes, nine feet at exactly 150 units apart, and a drawing
# that reads as a diagram of a tree rather than as a root: the fans mirror to
# the unit, so the eye sees a truss.
#
# So the growth is back, with the three faults answered directly:
#
#   CHOSEN WHOLE, NOT LEG BY LEG. A branch commits both legs or neither, in
#   the preference order the rule always had. Flipping leg 1 to clear a
#   crossing is exactly what laid a child along its parent's other leg.
#
#   A CLEARANCE, NOT ONLY A CROSSING TEST. free() now also refuses a step that
#   comes within CLEAR units of a stroke it does not touch. The old rule was
#   topological and let branches run parallel a few units apart, which at 1 px
#   is one thick flickering stroke.
#
#   BALANCED BY CONSTRUCTION, NOT BY SYMMETRY. The seeds are mirrored, so the
#   two halves carry the same number of limbs and the same drop budget; what
#   the growth then does inside each limb is decided by the room it finds, so
#   the two sides match in mass and differ in detail. That is the difference
#   between balance and reflection, and it is the whole of what was wrong with
#   the truss.
#
# IT IS STILL NOT RANDOM. foundations/illustration.html: a construction is the
# same every time it is drawn. There is no RNG here — every choice is a
# function of the geometry and of the seed list below, so re-running prints
# byte-identical paths. The irregularity the reader sees is the irregularity of
# the box, not of a random number.


def grow(x, y, kind, depth, side, budget):
    """One branch: turn a notch, run part of the drop, turn again, meet the
    rail — then the same again from its own junction, on the other side.

    A BRANCH IS SIZED BY THE DROP IT HAS LEFT, not by its parent's length.
    Size it by the parent and a branch leaving high has to fall the rest of the
    way as a vertical, which is a long parallel drop — seven of those was the
    bus this replaced. Size it by the remaining drop and it lands ON the rail
    at an angle and shrinks on its own as it nears it.

    A BRANCH ALTERNATES 45 AND 63.43 and never uses the outer two angles.
    Turning one notch steeper each time ends every branch at 90 and the bottom
    of the drawing comes out a picket fence; one notch flatter puts 26.57 in
    the fringe, and 26.57 crosses twice its own drop, which reads as a net.
    """
    rem = RAIL - y
    if depth > DEPTH or rem < 55 or budget <= 0:
        return
    a = "S" if kind in ("F", "D") else "D"
    b = "D" if a == "S" else "S"
    # WHERE THE BRANCH PUTS ITS OWN JUNCTION, and this is the one number that
    # makes the feet irregular. A single ratio for every branch is what spaced
    # the truss's feet at exactly 150: same ratio, same drop, same run, every
    # time. The ratio is a function of the branch's own depth and side, so
    # sibling limbs divide at different heights, their children inherit
    # different remainders, and the feet come out unevenly spaced without one
    # of them being placed by hand. Still on fives, so the paste stays readable.
    r = RATIOS[(depth + (1 if side > 0 else 0)) % len(RATIOS)]
    h1 = F(5) * round(rem * r / 5)
    h2 = rem - h1
    if h1 <= 0 or h2 <= 0:
        return
    for n1 in (name_of(a, side), name_of(a, -side), "V"):
        if not free(x, y, n1, h1):
            continue
        x1, y1 = lands(x, y, n1, h1)
        s1 = side if n1 == "V" else (1 if n1.endswith("R") else -1)
        if y1 >= RAIL:
            walk(x, y, [(n1, h1)])
            return
        n2 = next((n for n in (name_of(b, s1), name_of(b, -s1), "V")
                   if free(x1, y1, n, h2)), None)
        if n2 is None:
            continue
        walk(x, y, [(n1, h1)])
        walk(x1, y1, [(n2, h2)])
        grow(x1, y1, a, depth + 1, -s1, budget - 1)
        return


# THE SEEDS, mirrored about the trunk: every junction on a reach, plus two on
# the centre taproot. A taproot is bare near the crown and branchy near the
# tip, so the deeper seeds are given more budget — the number of further
# generations they may spawn — and the shallow ones one limb only.
SEEDS = []
for side in (-1, +1):
    # every junction on the reach, with the parent's own kind so the branch
    # alternates off it rather than repeating it. Inward (-side) on the flat
    # junctions and outward on the steep ones, which is what fills the triangle
    # between the reach and the taproot instead of hanging everything below the
    # reach where there is no room left to fall.
    for (dx, dy), kind, out, depth, budget in [
        (( 60,  60), "D", -1, 1, 4),
        ((240, 150), "F", -1, 1, 4),
        ((300, 210), "D", +1, 1, 4),
        ((480, 300), "F", -1, 1, 3),
        ((540, 360), "D", +1, 2, 2),
        ((600, 390), "F", -1, 2, 2),
    ]:
        SEEDS.append((F(600 + side * dx), CROWN + F(dy), kind,
                      depth, out * side, budget))
# and the taproot, alternating the side it puts a limb out on
for dy, side, budget in ((F(110), +1, 4), (F(210), -1, 4), (F(320), +1, 3)):
    SEEDS.append((F(600), CROWN + dy, "V", 1, side, budget))

for jx, jy, pkind, d, side, budget in SEEDS:
    grow(jx, jy, pkind, d, side, budget)

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


free_ends = []
for i, (x1, y1, x2, y2, d) in enumerate(segments):
    # every segment is on one of the five angles
    dx, dy = x2 - x1, y2 - y1
    ok = dx == 0 or dy == 0 or abs(dx / dy) in (F(1, 2), F(1), F(2))
    assert ok, f"segment {i} is off the brand angles: {dx}/{dy}"
    if on_rail(y2):
        continue
    if any(on_segment(x2, y2, s) for j, s in enumerate(segments) if j != i):
        continue
    free_ends.append((i, x2, y2))

# AND NO CROSSINGS, which is the other half of the same sentence. "Every
# terminal arrives" was asserted from the first paste; nothing asserted that
# the strokes BETWEEN the terminals keep out of each other's way, and three
# pairs did not. A crossing with no dot on it says "not connected" in this
# vocabulary, so a drawing of data merging had three points where the reader
# was told, in the drawing's own language, that it does not.
crossings = []
for i in range(len(segments)):
    for j in range(i + 1, len(segments)):
        ax1, ay1, ax2, ay2, _ = segments[i]
        bx1, by1, bx2, by2, _ = segments[j]
        det = (ax2 - ax1) * (by2 - by1) - (ay2 - ay1) * (bx2 - bx1)
        if det == 0:
            continue
        t = ((bx1 - ax1) * (by2 - by1) - (by1 - ay1) * (bx2 - bx1)) / det
        u = ((bx1 - ax1) * (ay2 - ay1) - (by1 - ay1) * (ax2 - ax1)) / det
        if not (0 <= t <= 1 and 0 <= u <= 1):
            continue
        p = (ax1 + t * (ax2 - ax1), ay1 + t * (ay2 - ay1))
        # an END meeting another stroke is the arrival; only the interior of
        # BOTH strokes at once is a crossing
        if p in ((ax1, ay1), (ax2, ay2)) or p in ((bx1, by1), (bx2, by2)):
            continue
        crossings.append((i, j, float(p[0]), float(p[1])))

print(f"{len(segments)} segments ({SKELETON} pinned, {len(segments) - SKELETON} grown)")
print(f"free ends: {len(free_ends)}  {free_ends}")
print(f"crossings: {len(crossings)}  {crossings}")
assert not free_ends, "a root has no free ends"
assert not crossings, "a root does not pass through itself"

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


# HOW FAR THIS STROKE CARRIES THE FRONT, in the same currency as level(): the
# motion lane buys every window with it, so a stroke's window closes on the
# point its children's windows open on. → the .lp-flow__seg note on the page.
#
# THE DIFFERENCE OF THE TWO ROUNDED LEVELS, and not its own rounding of the
# geometry. What ships is two decimal places, so what has to hold in two
# decimal places is `parent --l + parent --u == child --l` -- and a child's run
# IS its parent's run plus the parent's step, so taking both ends through the
# same level() makes the identity exact in the shipped numbers rather than
# merely true of the reals behind them. Rounding each independently is off by a
# hundredth at twenty of the forty-one junctions, which is a whole stroke's
# stagger at the fringe. scripts/check-flow-chain.py holds it.
def extent(d, x1, y1, x2, y2):
    step = max(abs(x2 - x1), abs(y2 - y1))     # Chebyshev, as walk() accumulates
    return num(round(float(level(d + step)) - float(level(d)), 2))


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
# AND A SECOND AXIS FOR THE LEAVES, ON THE SAME RAMP, STRETCHED.
#
# The ramp puts lime at 0, the oklab waypoint at 0.061 and Glas at 0.32, which
# on a route's own axis means the lime leg is the first six per cent of the
# stroke. That is right for a route: the front is a moving tip and what the
# reader sees of the colour is a point of light travelling down a grey line.
#
# It is wrong for a leaf, which is the one stroke that KEEPS its light. Six per
# cent of a 90-unit dive is five screen pixels, so the settled shimmer was a
# speck at the very end of each foot — "cant see the shimmer leaves", which is
# the only test this kind of light has to pass.
#
# So a leaf reads the same stops across a longer axis: three times its own
# length, which puts Glas at the stroke's far end and the waypoint at 18 % of
# it. Nothing about the family changes — same #lp-flow-ramp,
# same four stops, same oklab path, one href — only how much of the leg lands
# on this particular stroke. The lime is at the foot, where the data arrives.
# THREE, NOT 3.125. The reciprocal of the ramp's Glas stop is 1 / 0.32 =
# 3.125, which would land Glas exactly on the stroke's far end. Three lands it
# at 0.333 of the stroke instead — four units further out on the longest leaf,
# which is under a pixel — and it keeps every endpoint on the same rational
# grid the rest of the drawing is built on. 3.125 does not: the coordinates
# come out with four decimals, `num()` prints six significant figures, and the
# rounding put three of the eighteen leaf axes at 63.44 degrees, which is not
# one of the five angles. A stretch that cannot be written exactly is a stretch
# that fails the angle check for arithmetic reasons rather than geometric ones.
LEAF_STRETCH = F(3)

print()
for i, (x1, y1, x2, y2, d) in enumerate(segments):
    print(f'<linearGradient id="lp-flow-ax-{i:02d}" href="#lp-flow-ramp" '
          f'gradientUnits="userSpaceOnUse" x1="{num(x2)}" y1="{num(y2)}" '
          f'x2="{num(x1)}" y2="{num(y1)}"/>')
    if y2 == RAIL:
        ex = x2 + (x1 - x2) * LEAF_STRETCH
        ey = y2 + (y1 - y2) * LEAF_STRETCH
        print(f'<linearGradient id="lp-flow-lf-{i:02d}" href="#lp-flow-ramp" '
              f'gradientUnits="userSpaceOnUse" x1="{num(x2)}" y1="{num(y2)}" '
              f'x2="{num(ex)}" y2="{num(ey)}"/>')

# THE LEAVES ARE THE STROKES THAT LAND ON THE RAIL, and they are marked in the
# markup rather than found in CSS because there is no selector for "ends at
# y 620". They are the only part of the drawing that keeps its light: the rest
# of the root fades to contour behind the front, and the feet go on glimmering
# — see .lp-flow__leaf on the page. A leaf is where the data actually enters,
# so it is the one place a light that never quite goes out is saying something.
print()
for i, (x1, y1, x2, y2, d) in enumerate(segments):
    o = "0 0" if x2 >= x1 else "100% 0"
    leaf = y2 == RAIL
    print(f'<path class="lp-flow__light{" lp-flow__leaf" if leaf else ""}" '
          f'style="--o:{o};--l:{level(d)};'
          f'--u:{extent(d, x1, y1, x2, y2)}" '
          f'stroke="url(#lp-flow-{"lf" if leaf else "ax"}-{i:02d})" '
          f'd="{data(x1, y1, x2, y2)}"/>')

print()
for x1, y1, x2, y2, d in segments:
    o = "0 0" if x2 >= x1 else "100% 0"
    print(f'<path class="lp-flow__seg" style="--o:{o};--l:{level(d)};'
          f'--u:{extent(d, x1, y1, x2, y2)}" d="{data(x1, y1, x2, y2)}"/>')

# THE NODES. r steps down with distance from the subject, which the manual
# states and this drawing can honour literally: the two splits are nearest the
# void and get r 3, the taproots' own branch points r 2, the fringe r 1. Eight,
# because "eight is a lot for one object; twelve is too many" -- so the three
# rail arrivals carry none. They do not need one: the frame's own verticals
# stand up out of them, which is a louder mark than a 2 px dot.
#
# THE RADIUS IS NOT TYPED ANY MORE, and that is the finding. Three of the eight
# stood at exactly the same run from the void -- (720, 345), (0, 450) and
# (600, 495) are all at d 456, level 1.5 -- and carried r 2, r 1 and r 1. Same
# distance, two radii, in a drawing whose only rule for the radius is that it
# steps down WITH distance. A hand-typed ladder cannot help doing this: it is
# read off the picture ("the fringe ones look far away") rather than off the
# number the picture is built from, and the picture moves.
#
# So r is a function of the run, in the drawing's own depth units: level()
# already normalises the run to 0-3, which is three bands of one, and the
# manual's ladder is three deep -- card 01 puts r 3 on the lit face, 2 on the
# stage below it, 1 on the one below that. Nearest third r 3, middle third
# r 2, last third r 1. Held on the shipped markup by check-flow-crossings.py,
# which also has the ladder.
#
# THE POINT LIST WAS STILL TYPED, AND THAT IS THIS FINDING -- the same one, one
# level up. The radius stopped being read off the picture; WHICH POINTS GET A
# DOT never did, and the eight above were read off the picture exactly the way
# the radii had been. Measured on the paste this replaces: the root has fifteen
# junctions and seven of them carried a node, and the eighth node was not on a
# junction at all. (480, 255) is a BEND -- one stroke in, one stroke out, the
# middle taproot changing from 45deg to 63.43deg -- and it carried r 3, the
# largest dot in the drawing, on the one marked point in it where nothing
# divides. Meanwhile (150, 240) and (530, 355), both real splits and both
# NEARER the void than four of the dots that were drawn, carried nothing. The
# one guard on any of it is the assert below, whose message says "is not a
# junction" and whose test is membership in DIST -- and DIST holds every point
# that starts a stroke, bends included. It has never been able to fail.
#
# In this system that is not untidiness. foundations/illustration.html: "a node
# marks a point the construction actually depends on", which is the sentence
# check-flow-crossings.py reads the other way round to prove a crossing with
# nothing on it means NOT CONNECTED. Marking seven of fifteen divisions and one
# non-division spends the drawing's one word for "here it divides" at random,
# in the one drawing whose whole subject is data dividing.
#
# SO THE POINTS ARE DERIVED TOO, from the same number the radius is: every
# junction whose run is in the r 3 or r 2 band, which is level < 2 -- the
# nearest two thirds. The fringe carries none, and does not want one: out there
# the root is thinning to twigs and a dot every few units would read as texture
# rather than as construction.
#
# THE COUNT IS THE COROBORATION, not the rule. The manual says "eight is a lot
# for one object; twelve is too many", so eleven is the most this drawing may
# carry -- and level < 2 selects exactly eleven of the fifteen junctions, with
# the other four at 2.06, 2.32, 2.34 and 2.85. The two cuts agree on this
# geometry; the assert holds the count so they cannot silently stop agreeing
# when the geometry moves. Held on the shipped markup by check-flow-nodes.py.
# LEVEL < 2 SELECTED ELEVEN OF FIFTEEN JUNCTIONS ON THE GROWN ROOT; on the
# balanced construction it selects one of seven, because the fans sit deep on
# purpose. The cut moves to the rule the manual actually states — "a node
# marks a point the construction depends on" — and on a construction this
# regular that is EVERY division: the crown and the six fan junctions, seven
# dots, inside the ceiling with room. The radius keeps the same ladder.
# ON A GROWN ROOT "EVERY DIVISION" IS TOO MANY AGAIN. The symmetric
# construction had seven divisions and could mark all of them; this one has
# nineteen, and a dot on each spends the drawing's one word for "here it
# divides" until it reads as texture rather than as construction. So the cut
# goes back to the one the radius is already a function of: level, the run from
# the void normalised to 0-3, nearest two thirds. That is the same sentence as
# the ladder — r 3 and r 2 are the bands nearest the subject, and those are the
# divisions the reader is meant to count; out at the fringe the root is
# thinning to twigs and a dot every few units is noise. It selects nine of the
# nineteen, inside the manual's ceiling of eleven with room.
NODE_LEVEL = 2.0
outdeg = Counter((x1, y1) for x1, y1, _, _, _ in segments)
NODE_POINTS = sorted((p for p, n in outdeg.items()
                      if n >= 2 and float(level(DIST[p])) < NODE_LEVEL),
                     key=lambda p: (p[1], p[0]))
assert len(NODE_POINTS) <= 11, (
    f"{len(NODE_POINTS)} nodes -- the manual's ceiling is eleven "
    f'("eight is a lot for one object; twelve is too many")')


def radius(l):
    return max(1, 3 - int(l))


print()
for nx, ny in NODE_POINTS:
    assert outdeg[(nx, ny)] >= 2, f"node at ({nx}, {ny}) is not a junction"
    l = level(DIST[(nx, ny)])
    print(f'<circle class="lp-flow__node" style="--l:{l}" '
          f'cx="{num(nx)}" cy="{num(ny)}" r="{radius(float(l))}"/>')

# ------------------------------------------------------------------ the values
#
# WHAT THE ROOT IS CARRYING. The drawing said data moves; it did not say how
# much, and a route with no quantity on it is a pipe rather than a stream.
# Eight values ride the routes -- the source on the trunk, one on each of the
# three taproots where it leaves the crown, the two the right taproot divides
# into, and the two THOSE divide into where the drawing is emptiest.
#
# THEY CONSERVE, and that is the whole reason they are generated rather than
# typed. At any labelled point the value equals the sum of the labelled values
# immediately downstream of it: 12 480 leaves the void and 3 840 + 3 200 +
# 5 440 leave the crown; 5 440 divides into 1 360 + 4 080, and 4 080 into
# 2 400 + 1 680. A number that does not balance is a drawing telling the
# reader something untrue about itself, which is the one thing an illustration
# of data flow cannot afford. Asserted here and again on the shipped markup by
# scripts/check-flow-values.py.
#
# AND EVERY ROUTE OUT IS IN THE SUM, which is the half of "they conserve" that
# balancing alone does not say -- see the assertion under downstream_labelled()
# for the branch this drawing shipped asserting carries zero.
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
# its own taproot crossed that box from 420.5 to 436.5. So the clearance is
# PERPENDICULAR to the stroke, and it is the NEAREST CORNER of the label box
# that holds it: the box then extends into the quadrant the offset points into,
# and every other point of it is further from the line than that corner. Which
# is what makes "12 px" a number rather than a direction of travel.
#
# THE OFFSETS WERE TYPED, AND THAT IS WHY THERE WERE EIGHT OF THEM. dx/dy were
# axis-aligned constants -- 12 px across, 8 px down, -50% -- so the clearance
# they actually bought was whatever the projection of that pair onto the
# stroke's normal happened to come to. Measured on the render at 1440 x 900,
# nearest corner to own stroke:
#
#     12 480   11.99      3 840   12.52      3 200   14.13      5 440   12.52
#      1 360    7.56       4 080   12.53      2 400   12.54      1 680    7.55
#
# One drawing, one stated clearance, and 7.55 to 14.14 px of it -- an 87 %
# spread, with the two tightest 37 % under the number the rule publishes. None
# of it visible: every label looks placed, because a label 7.5 px off a line
# and a label 14 px off a line both look like a label near a line.
#
# THE LAW, and it decides all eight with nothing left over:
#
#     A numeral sits exactly 12 px from the stroke it names, measured
#     perpendicular from the numeral's nearest corner, on that stroke's LEFT --
#     and on its right only where the left would bring another stroke inside
#     the same 12 px.
#
# "Left" is the walker's left going down the stroke: rotate the direction a
# quarter turn to (dy, -dx). On the drawing's four labelled slopes that gives
# four offsets and no fifth, each of magnitude exactly 12:
#
#     vertical      (12, 0)                 1:1   (8.485, -8.485)  = 12/sqrt2
#     1:2 (26.57d)  (5.367, -10.733)        2:1   (10.733, -5.367) = 12/sqrt5
#
# THE RIGHT IS TAKEN THREE TIMES, and never by preference. 3 200, 1 360 and
# 1 680 are each the STEEPER of two strokes leaving one junction, so their left
# is the inside of the fork, and the fork closes on them. Measured at the gate
# floor (1024, where the box is smallest and the 11 px label is therefore
# largest against it), left-side box to nearest stroke it does not name:
# 1.20 px, 0.00 px, 0.00 px -- a crossing, twice literally. On the right they
# get 21.57, 40.17 and 10.94. The other five are clear on the left by 24.78 to
# 45.64 and stay there.
#
# 1 680 IS THE TIGHTEST MARK ON THE DRAWING at 10.94 px, which is under the
# 12 px the law names -- the law bars the left, it does not promise the right.
# It is a geometry finding, not a placement one: the 63.43deg dive out of
# (840, 405) runs close to its own sibling. Recorded here rather than fixed by
# nudging the label off the law.
#
# AND THE CROWN SITS IN THE STATEMENT'S GHOST FIELD. The lattice the statement
# figure scatters overlaps the top of this box: its rules land on flow y 96,
# 128 and 160 (its own 32-unit rows, offset 240 -- measured, not declared).
# The source value is 14 units tall, so it goes in the 32-unit band between 96
# and 128 rather than on a rule. It was on 128 and read as "12.480". The band
# is why 3 840 keeps its left even though its right is 14.35 px roomier: the
# right is up-and-left of (250, 190), which puts the box across y 160.

# The label's own box, measured on the render -- 11 px Geist Mono at
# --tracking-label, so 7.111 px of advance per character and a 14.30 px line
# box, constant at every viewport because the type does not scale with the
# drawing. The line box, not the glyphs, which is the conservative end.
LABEL_ADVANCE = 7.111
LABEL_HEIGHT = 14.30
# px per drawing unit at the gate floor, 1024 x 720 -- the smallest the box
# gets and therefore the largest the label is against the strokes. 0.91333 at
# 1440, 1.06667 at 1920; the floor is the one a side has to survive.
FLOOR_SCALE = 0.75948
CLEARANCE = 12.0

# WHERE THE NUMERALS GO IS DERIVED NOW, LIKE EVERY OTHER MARK ON THIS DRAWING.
# The eight values were a typed list of coordinates, which is the same finding
# the radius and the node points already went through twice: read off the
# picture rather than off the number the picture is built from, and the picture
# moves. It moved — the root is grown again — and eight coordinates that named
# junctions of the truss now name empty wash.
#
# So a value stands on a route LEAVING a marked junction, one quarter of the
# way along it: the junctions are already chosen (NODE_POINTS, the nearest two
# thirds of the ladder), and quarter-way is far enough down the stroke to be
# clear of the dot and near enough to still be reading that stroke rather than
# the next one. Which junctions get quantified is the ceiling again — the
# crown, and the two junctions the crown's own limbs divide at — because the
# manual's ceiling is on marks and a numeral is a mark.
#
# AND THE FIGURES ARE COMPUTED BOTTOM-UP, not typed and then checked. A
# labelled point carries the sum of the labelled points below it, so
# conservation is how the numbers are MADE rather than a property they are
# audited for afterwards: the fringe of the label tree gets a base rate and
# every parent is the sum of its children. There is no arrangement of these
# numbers that does not balance, which is the difference between a check that
# can fail and a construction that cannot.


def own_stroke(px, py):
    """The one segment a value stands on. Two would make "its stroke" a guess."""
    hits = [s for s in segments if on_segment(px, py, s[:4])]
    assert len(hits) == 1, f"the value at ({px}, {py}) rides {len(hits)} routes"
    return hits[0][:4]


def label_box(px, py, sx, sy, chars):
    """The label's box in drawing units, placed 12 px along (sx, sy).

    The anchor corner is the one the offset points AWAY from, so the box grows
    into the same quadrant and no other corner is nearer the line than this
    one. A zero component centres that axis, which only the vertical uses.
    """
    w = chars * LABEL_ADVANCE / FLOOR_SCALE
    h = LABEL_HEIGHT / FLOOR_SCALE
    off = CLEARANCE / FLOOR_SCALE
    ax, ay = float(px) + off * sx, float(py) + off * sy
    x0 = ax if sx > 0 else (ax - w if sx < 0 else ax - w / 2)
    y0 = ay if sy > 0 else (ay - h if sy < 0 else ay - h / 2)
    return x0, y0, x0 + w, y0 + h


def box_gap(seg, box, samples=400):
    """Least distance in units from a segment to an axis-aligned box."""
    x1, y1, x2, y2 = (float(v) for v in seg)
    bx0, by0, bx1, by1 = box
    best = float("inf")
    for i in range(samples + 1):
        px = x1 + (x2 - x1) * i / samples
        py = y1 + (y2 - y1) * i / samples
        dx = max(bx0 - px, 0.0, px - bx1)
        dy = max(by0 - py, 0.0, py - by1)
        best = min(best, math.hypot(dx, dy))
    return best


def offsets(px, py, chars):
    """The two CSS offsets the law produces for a value, and why that side.

    Returns (dx, dy, side, left_gap, taken_gap) -- gaps in px at the gate
    floor, to the nearest stroke the value does NOT name.
    """
    x1, y1, x2, y2 = own_stroke(px, py)
    dx, dy = float(x2 - x1), float(y2 - y1)
    length = math.hypot(dx, dy)
    left = (dy / length, -dx / length)          # the walker's left, (dy, -dx)
    gaps = {}
    for name, (sx, sy) in (("left", left), ("right", (-left[0], -left[1]))):
        box = label_box(px, py, sx, sy, chars)
        gaps[name] = min(box_gap(s[:4], box) for s in segments
                         if s[:4] != (x1, y1, x2, y2)) * FLOOR_SCALE
    side = "left" if gaps["left"] >= CLEARANCE else "right"
    sx, sy = left if side == "left" else (-left[0], -left[1])
    ox, oy = CLEARANCE * sx, CLEARANCE * sy
    return css_offset(ox, "x"), css_offset(oy, "y"), side, gaps["left"], gaps[side]


def css_offset(v, axis):
    """One component of the offset, carrying its own anchoring.

    The anchor is not a taste either: the box has to grow away from the line,
    so a positive component anchors the near edge at 0 and a negative one at
    -100%. A zero component is the vertical's, and centres.
    """
    if abs(v) < 1e-9:
        return "-50%"
    r = round(v, 3)
    return f"{r:g}px" if r > 0 else f"calc(-100% - {abs(r):g}px)"


def run_to(px, py):
    """The run from the void to a point, via the segment it lies on."""
    for x1, y1, x2, y2, d in segments:
        if on_segment(px, py, (x1, y1, x2, y2)):
            return d + max(abs(px - x1), abs(py - y1))
    raise AssertionError(f"the value at ({px}, {py}) rides no route")


def downstream_labelled(px, py, labelled):
    """The labelled points reachable from here, and the routes that reach none.

    Every step of this drawing descends, so downstream is simply larger y and
    the walk cannot loop. A labelled point STOPS its branch -- that is what
    makes the sum below a statement about one generation rather than about the
    whole subtree.

    ESCAPED is the second half of the same walk and the half that was missing:
    the points where the walk simply RAN OUT -- a terminal reached with no
    labelled value anywhere between it and where the walk started. Those are
    the routes the sum does not cover. See the assertion below.
    """
    found, escaped, seen, stack = set(), set(), set(), [(px, py)]
    while stack:
        p = stack.pop()
        onward = 0
        for x1, y1, x2, y2, _ in segments:
            seg = (x1, y1, x2, y2)
            if (x2, y2) == p or not on_segment(p[0], p[1], seg):
                continue
            onward += 1
            below = sorted(l for l in labelled
                           if l[1] > p[1] and on_segment(l[0], l[1], seg))
            q = min(below, key=lambda l: l[1]) if below else (x2, y2)
            if q in labelled:
                found.add(q)
            elif q not in seen:
                seen.add(q)
                stack.append(q)
        if not onward and (p[0], p[1]) != (px, py):
            escaped.add(p)
    return found, escaped


# A SUM IS ONLY A SUM IF EVERY ROUTE OUT IS IN IT. "The value equals the total
# of the labelled values immediately below it" is silent about the routes that
# reach no labelled value at all, and the drawing shipped one: 4 080 stood at
# (860, 415), which is on (840, 405) -> (970, 470) -- one junction PAST the
# split it was naming. (840, 405) also sheds (907.5, 540), a six-stroke branch
# that lands twice on the lectern's rail, and nothing on it is labelled. So
# `5 440 = 1 360 + 4 080` was a claim that those two rail arrivals carry
# nothing. The arithmetic balanced; the sentence was false.
#
# A value labels THE STROKE IT STANDS ON, so a value that names a split has to
# stand on a stroke leaving that split -- not on a stroke two generations down
# with another division in between. The rule below is that stated as something
# a walk can decide: from a labelled point, every route must arrive at a
# labelled point, or the sum below it is not the whole of what left it.
#
# A point with NOTHING labelled below it asserts nothing and escapes nothing --
# the fringe under 3 840 is unquantified, and unquantified is not wrong.
VALUE_JUNCTIONS = 3        # the crown and the first two divisions under it
BASE_RATE = F(80)          # every value is a multiple of it, as they always were


def outgoing(px, py):
    return [s for s in segments if (s[0], s[1]) == (px, py)]


def value_points():
    """A point a quarter of the way down every route out of the quantified
    junctions, in the order the data reaches them."""
    js = sorted(NODE_POINTS, key=lambda p: DIST[p])[:VALUE_JUNCTIONS]
    pts = [(F(600), F(120))]                       # the source, on the trunk
    for jx, jy in js:
        for x1, y1, x2, y2, _ in outgoing(jx, jy):
            pts.append((x1 + (x2 - x1) / 4, y1 + (y2 - y1) / 4))
    return pts


PTS = value_points()


def _sum_below(p, rest):
    kids, _ = downstream_labelled(p[0], p[1], set(PTS))
    return [k for k in kids if k != p]


# The fringe of the label tree first, then every parent as the sum of its
# children — deepest first, so a parent is only ever summed from figures that
# are already fixed. The base rates step down the fringe by one unit of
# BASE_RATE each, which is what keeps the sums from all coming out equal and
# the drawing from claiming a perfectly even split it does not draw.
_v = {}
for i, p in enumerate(sorted(PTS, key=lambda q: -q[1])):
    kids = _sum_below(p, PTS)
    _v[p] = sum(_v[k] for k in kids) if kids else BASE_RATE * (17 + 2 * i)

VALUES = [(x, y, int(_v[(x, y)])) for x, y in PTS]

LABELLED = {(x, y): v for x, y, v, *_ in VALUES}
for (px, py), v in LABELLED.items():
    kids, escaped = downstream_labelled(px, py, set(LABELLED))
    if kids:
        total = sum(LABELLED[k] for k in kids)
        assert total == v, (f"the value at ({px}, {py}) is {v} and the "
                            f"{len(kids)} below it total {total}")
        assert not escaped, (
            f"the value at ({px}, {py}) is {v} and divides into "
            f"{len(kids)} labelled value(s), but {len(escaped)} route(s) "
            f"leaving it reach the rail with nothing labelled on them: "
            f"{sorted(escaped)} — the sum says those carry zero")

SEP = " "   # see the note at the values' own print loop below

# ---------------------------------------------------------------- the readings
#
# WHAT THE ROOT IS CARRYING, AT THE END WHERE IT IS CARRYING IT FROM. The
# values above are one quantity — a data rate — and they divide, which is why
# they are numerals with no unit on them and why every one of them has to add
# up. The statement over this drawing is "Tausende Sensoren erzeugen Daten",
# and until now the drawing answered it with eight counts of nothing in
# particular: the fringe, where the sensors actually are, carried no reading at
# all.
#
# A READING IS NOT A VALUE, and that is the whole reason it is a second class
# rather than eight more .lp-flow__val. A rate divides: the stream that leaves
# a junction is the sum of the streams that leave it, and check-flow-values.py
# holds the drawing to that. A temperature does not. Two 400 °C channels
# merging do not make 800 °C, and a drawing that let its units into the sum
# would be asserting exactly that. So the two carry different classes, the
# check reads only the one that conserves, and the unit is what tells the
# reader which kind of number they are looking at.
#
# WHERE THEY GO: the fringe, one per limb, spread across the width. That is
# where the sensors are in the drawing's own logic — the far end of the root,
# furthest from the void — and it is also the emptiest band of the box, which
# is the one part of this the eye was going to notice first either way.
#
# THE FIGURES ARE PLAUSIBLE PLANT VALUES, not decoration: a bearing at 74 °C, a
# line at 12.4 bar, a drive at 246 kW. They are typed, because a temperature is
# not derivable from a geometry — but the CHOICE of stroke is not, and neither
# is the placement, which goes through the same label law as everything else.
READINGS = [
    "74 \u00b0C", "12.4 bar", "246 kW", "1 480 rpm", "318 K",
    "4.2 mm/s", "96 %", "51 Hz",
]


def label_side_box(px, py, chars, side):
    """The reading's box on one side of its own stroke, plus that side's offset."""
    x1, y1, x2, y2 = own_stroke(px, py)
    dx, dy = float(x2 - x1), float(y2 - y1)
    length = math.hypot(dx, dy)
    left = (dy / length, -dx / length)
    sx, sy = left if side == "left" else (-left[0], -left[1])
    return label_box(px, py, sx, sy, chars), (CLEARANCE * sx, CLEARANCE * sy), (x1, y1, x2, y2)


def boxes_overlap(a, b, pad):
    return not (a[2] + pad < b[0] or b[2] + pad < a[0]
                or a[3] + pad < b[1] or b[3] + pad < a[1])


def place_reading(px, py, chars, placed):
    """The first side that clears everything, or None.

    THE LAW GREW TWO CLAUSES, AND BOTH WERE FOUND ON THE RENDER RATHER THAN IN
    THE FILE. It used to check one thing — is this box 12 px from a stroke it
    does not name — and then take the right side whether or not the right side
    was any better, because there was no third answer. Two consequences shipped:

      A LABEL COLLIDED WITH ANOTHER LABEL. Nothing measured that at all. The
      strokes are what the law was written about, and a numeral is not a
      stroke, so "246 kW" could be placed perfectly against every line in the
      drawing and land on top of "12.4 bar".

      A LABEL LEFT THE DRAWING. The two outermost feet stand ON the walls, at
      x 0 and x 1200, so a numeral on the outside of either one has its box
      entirely outside the box — half of "74 °C" was off the left edge of the
      figure, which is not a clearance failure, it is a label that is not in
      the picture.

    So a side has to clear three things now — the strokes, the labels already
    placed, and the walls — and if neither side does, the answer is None and
    the caller tries a different stroke. A reading that cannot be placed
    legibly is one the drawing does not carry; there are eight of them and
    nineteen feet to choose from.
    """
    for side in ("left", "right"):
        box, off, own = label_side_box(px, py, chars, side)
        if box[0] < 0 or box[2] > 1200 or box[1] < 0 or box[3] > float(RAIL):
            continue
        gap = min(box_gap(s_[:4], box) for s_ in segments if s_[:4] != own) * FLOOR_SCALE
        if gap < CLEARANCE:
            continue
        if any(boxes_overlap(box, b, CLEARANCE / FLOOR_SCALE) for b in placed):
            continue
        return side, off, box, gap
    return None


def value_boxes():
    """The eight rate numerals' boxes, so a reading can keep off them too.

    They are placed first and by a law of their own, so from the reading's
    point of view they are simply furniture that is already in the room. This
    is the clause whose absence put "246 kW" on top of its neighbour: the
    reading law could see every stroke in the drawing and none of the writing.
    """
    out = []
    for x, y, v in VALUES:
        text = f"{v // 1000}{SEP}{v % 1000:03d}" if v >= 1000 else str(v)
        dx, dy, side, _, _ = offsets(x, y, len(text))
        b, _, _ = label_side_box(x, y, len(text), side)
        out.append(b)
    return out


def fringe_readings(texts):
    """One reading per limb, deepest first, spread across the width.

    Deepest first because the fringe is where the sensors are; spread because
    otherwise every reading lands in whichever corner the root is busiest in,
    which is the fringe, which is all of them. A candidate that cannot be
    placed legibly is skipped and the next one tried — see place_reading.
    """
    span = max(len(t) for t in texts) * LABEL_ADVANCE / FLOOR_SCALE * 0.7
    taken, placed, out = [], value_boxes(), []
    for x1, y1, x2, y2, d in sorted(segments, key=lambda s_: -s_[4]):
        if len(out) == len(texts):
            break
        mx = float(x1 + x2) / 2
        if any(abs(mx - t) < span for t in taken):
            continue
        # a third of the way down, which keeps the numeral off both the
        # junction it leaves and the foot it lands on
        px, py = x1 + (x2 - x1) / 3, y1 + (y2 - y1) / 3
        got = place_reading(px, py, len(texts[len(out)]), placed)
        if got is None:
            continue
        side, off, box, gap = got
        taken.append(mx)
        placed.append(box)
        out.append((px, py, side, off, gap))
    return out


PLACED_READINGS = fringe_readings(READINGS)
assert len(PLACED_READINGS) == len(READINGS), (
    f"only {len(PLACED_READINGS)} of {len(READINGS)} readings could be placed "
    f"clear of the strokes, the other labels and the walls")

print()
for (px, py, side, (ox, oy), gap), text in zip(PLACED_READINGS, READINGS):
    print(f'<span class="t-label lp-flow__read" style="--x:{num(px)};--y:{num(py)};'
          f'--tx:{css_offset(ox, "x")};--ty:{css_offset(oy, "y")};'
          f'--l:{level(run_to(px, py))}">{text}</span>')
    print(f'  <!-- {side:>5}: own stroke {CLEARANCE:.2f} px, nearest other '
          f'{gap:.2f} px at the gate floor, clear of every label already set -->')


print()
# A PLAIN SPACE, AND THE THOUSANDS SEPARATOR IS STILL UNBREAKABLE. This emitted
# U+00A0 and the shipped paste carried U+0020, so six of the generator's 125
# lines did not match the markup it is the source of truth for -- invisible on
# the page, and exactly the drift "re-run it and the same lines come out" is a
# claim against. The plain space is the correct one of the two: .lp-flow__val
# sets `white-space: nowrap`, so the break the no-break space was insuring
# against cannot happen, and an insurance that no longer does any work is one
# more thing for a hand edit to get wrong.
for x, y, v in VALUES:
    text = f"{v // 1000}{SEP}{v % 1000:03d}" if v >= 1000 else str(v)
    dx, dy, side, left_gap, gap = offsets(x, y, len(text))
    print(f'<span class="t-label lp-flow__val" style="--x:{num(x)};--y:{num(y)};'
          f'--tx:{dx};--ty:{dy};--l:{level(run_to(x, y))}">{text}</span>')
    print(f'  <!-- {side:>5}: own stroke {CLEARANCE:.2f} px, nearest other '
          f'{gap:.2f} px at the gate floor; the left offers {left_gap:.2f} -->')
