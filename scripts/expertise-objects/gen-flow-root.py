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


# ---------------------------------------------- the balanced construction
#
# THE REVIEW OF 2026-07-28 RETIRED THE GROWTH RULE. "remove overlapping
# branches from the tree, make it branch equally": the grown root was chosen
# branch by branch around its own obstacles, so no two limbs matched, three
# terminals landed mid-stroke on their siblings (legal arrivals, but the eye
# reads a T into another branch as overlap), and the right half carried
# twice the ink of the left. The whole drawing is now WRITTEN OUT as one
# symmetric construction — grow(), free(), touches() and the ratio went with
# the asymmetry they existed to manage.
#
# THE LAW. One crown, two mirrored fans, eight equal feet.
#
#   TRUNK      V from the void (600, 84) to the crown (600, 170).
#   CROWN      divides once, into three: the two fans' reaches (F then D,
#              mirrored) and the centre taproot, V straight to the rail —
#              the one arrival the frame's middle vertical is pinned to.
#   REACH      DL/DR 75 out of the crown, then FL/FR 150 to the fan
#              junction: the 45 leaves the trunk, the flattest angle crosses
#              the width. Steep-then-flat and not the reverse, because the
#              flat leg then crosses the interior band x 400-600 — the band
#              check-flow-density.py floors at 10 %, and the flat-first
#              order left it at 9.8 with the same junctions either way.
#   FAN        each junction splits F 75 both ways; each child dives S 150
#              to the rail. 26.57 spreads, 63.43 lands — and S landing on
#              y 620 exactly is what set the crown at 170.
#
# EIGHT FEET at x 0, 150, 300, 450 | 750, 900, 1050, 1200 — every one a
# multiple of 150, mirror-symmetric about the trunk, and the outer pair plus
# the centre taproot are the three arrivals the lectern is pinned to
# (flow 0, 600, 1200 = frame 0, 500, 1000). Nothing lands on another branch:
# every terminal is on the rail, which is what "no overlaps" means here.
#
# ALL FIVE ANGLES remain the vocabulary: V trunk and taproot, F reaches and
# fan spreads, D elbows, S dives — 2 + 6 + 2 + 8 of 18 strokes.

CROWN = F(170)

DIST[(F(600), F(84))] = F(0)
walk(F(600), F(84), [("V", CROWN - 84)])                  # trunk, out of the void
walk(F(600), CROWN, [("V", RAIL - CROWN)])                # centre taproot

for side in (-1, +1):
    fname = "FR" if side > 0 else "FL"
    dname = "DR" if side > 0 else "DL"
    walk(F(600), CROWN, [(dname, F(75)), (fname, F(150))])    # reach + elbow
    jx = F(600 + side * 375)
    for s2 in (-1, +1):
        f2 = "FR" if s2 > 0 else "FL"
        walk(jx, CROWN + 225, [(f2, F(75))])                  # the fan spreads
        cx = jx + s2 * 150
        for s3 in (-1, +1):
            walk(cx, CROWN + 300,
                 [("SR" if s3 > 0 else "SL", F(150))])        # the dive lands

SKELETON = len(segments)

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
print()
for i, (x1, y1, x2, y2, d) in enumerate(segments):
    print(f'<linearGradient id="lp-flow-ax-{i:02d}" href="#lp-flow-ramp" '
          f'gradientUnits="userSpaceOnUse" x1="{num(x2)}" y1="{num(y2)}" '
          f'x2="{num(x1)}" y2="{num(y1)}"/>')

print()
for i, (x1, y1, x2, y2, d) in enumerate(segments):
    o = "0 0" if x2 >= x1 else "100% 0"
    print(f'<path class="lp-flow__light" style="--o:{o};--l:{level(d)};'
          f'--u:{extent(d, x1, y1, x2, y2)}" '
          f'stroke="url(#lp-flow-ax-{i:02d})" d="{data(x1, y1, x2, y2)}"/>')

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
outdeg = Counter((x1, y1) for x1, y1, _, _, _ in segments)
NODE_POINTS = sorted((p for p, n in outdeg.items() if n >= 2),
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

VALUES = [
    # x, y, value -- the offsets are DERIVED below and no longer typed.
    # THEY CONSERVE on the balanced tree: the crown divides the source three
    # ways (12 480 = 5 040 + 2 400 + 5 040 -- the fans match, the taproot
    # carries the middle), the right fan's junction divides its 5 040
    # (2 640 + 2 400), and the outer dive pair divides the 2 640
    # (1 360 + 1 280). All multiples of 80, as every value here has been.
    # The left fan mirrors the right in geometry, not in figures -- naming
    # both fans' subdivisions would spend fourteen numerals on a drawing
    # whose ceiling of marks is what it is; the left stays unquantified
    # below its reach, and unquantified is not wrong.
    (F(600), F(120), 12480),
    (F(425), F(295),  5040),
    (F(600), F(300),  2400),
    (F(775), F(295),  5040),
    (F(1051), F(433), 2640),
    (F(899), F(433),  2400),
    (F(1150), F(520), 1360),
    (F(1100), F(520), 1280),
]


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
for x, y, v in VALUES:
    text = f"{v // 1000}{SEP}{v % 1000:03d}" if v >= 1000 else str(v)
    dx, dy, side, left_gap, gap = offsets(x, y, len(text))
    print(f'<span class="t-label lp-flow__val" style="--x:{num(x)};--y:{num(y)};'
          f'--tx:{dx};--ty:{dy};--l:{level(run_to(x, y))}">{text}</span>')
    print(f'  <!-- {side:>5}: own stroke {CLEARANCE:.2f} px, nearest other '
          f'{gap:.2f} px at the gate floor; the left offers {left_gap:.2f} -->')
