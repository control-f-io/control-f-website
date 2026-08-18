"""The four expertise objects, v3.

STAGES ARE DEPTH BANDS, BACK TO FRONT — not "big things, then small things".
The build animation reads data-stage, and a stage is a <g>, so everything in
stage 2 paints over everything in stage 1 no matter what order it was written
in. Ordering the stages by depth is therefore the only assignment that is
correct as a drawing AND as a build: the object comes forward out of its own
foundation, and a hairline never surfaces through the mass in front of it.

EVERY ROW RUNS ON A LATTICE AXIS. The fleet's first draft put its units across
the screen, on the (1,-1) diagonal, and its track came out as two long
horizontal rules and a row of vertical ties — the only two directions in the
drawing that are NOT brand angles. Running the same row down +x instead makes
the rails, the ties, the line the units report to and the row itself all
26.57 deg, and gives the machines real depth overlap into the bargain.

A SLOPE IS ALSO A LATTICE DECISION. Four of the fleet's five machines are
shaped by one raked edge each, and in a vertical plane a step (dx, dz) lands on
screen slope 0.5 - dz/dx — so dz/dx of 1, 1.5 and 2.5 give 26.57, 45 and 63.43
deg and nothing else does. Every stem, fin, ramp and boom in here is written
from that table; isolib's profile note derives it.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from isolib import (  # noqa: E402
    p_, line, box, plate, face, poly, quad_t, quad_x, quad_y, seams, slab_x, slab_y,
    disc, hoop, cyl, taper, node, orbit, rotor, trace, light_quad, light_disc,
    assemble, bbox, lime_span_disc, reset, trace_from,
    FACE_TOP, FACE_L, FACE_R, PLATE_TOP, PLATE_L, PLATE_R,
    ACCENT, DARK,
)


def foundation(x, y, dx, dy, h=0.2, inset=0.18, nx=2, ny=1):
    """A plate with a chamfer line and a couple of bay seams. Nothing is drawn
    INTO it — the little hairlines that used to run down into the plate are the
    reason it read as brittle at stage size."""
    out = plate(x, y, 0.0, dx, dy, h)
    out.append(quad_t(x + inset, y + inset, h, dx - 2 * inset, dy - 2 * inset))
    if nx:
        out += seams((x + inset, y + inset, h), (x + dx - inset, y + inset, h),
                     (x + inset, y + dy - inset, h), (x + dx - inset, y + dy - inset, h), nx)
    if ny:
        out += seams((x + inset, y + inset, h), (x + inset, y + dy - inset, h),
                     (x + dx - inset, y + inset, h), (x + dx - inset, y + dy - inset, h), ny)
    return out


def lime_span(a, b, reach=2.6):
    """Gradient endpoints for a lit face. The ramp is lime for its first third
    and neutral by its end, so an element that spans the WHOLE ramp arrives on
    the page mint — which is not what "lime is light" means. Start the ramp at
    the lit face's far corner and run it well past the near one, and the face
    keeps the lime and only turns at its own edge."""
    pa, pb = p_(*a), p_(*b)
    return pa, (pa[0] + (pb[0] - pa[0]) * reach, pa[1] + (pb[1] - pa[1]) * reach)


# ==================================================================== 01
def maschinenbau():
    """A generating set, drawn from the machine and not from the idea of one:
    cooler package with its fan, engine under its air cleaners and its exhaust,
    then the generator on its feet with the terminal box on top and the shaft
    end lit. Rotating assets are the densest telemetry in the portfolio, so this
    is the object that carries the most machined detail.

    NOTHING IS CUT ANY MORE — not the machine, and not the floor either — and
    that is the fourth answer to one report. #404 authored a window and let the
    plate run out of it at both ends, on the rule that a frame is a crop and not
    a bounding box. #405 moved that window a column left, because the cut was
    taking the cooler and a cut may take ground only. #406 gave it 84 more units
    of height, because it was also taking the plate's near corner and meeting
    the right edge there in the one figure this projection never draws, a right
    angle. Each pass fixed what was reported and each next reading was the same
    sentence again: the image is cut off. At that point the doctrine is not
    being misapplied, it is being answered — what the rule promises is a view
    into something larger, and what a 26.57 deg plate corner ending on a
    vertical <svg> edge actually delivers, against a page whose ground is a
    quiet grey lattice, is a drawing that did not fit its box.

    THE FLOOR CAME IN; THE FRAME DID NOT GO OUT, and that direction is forced
    rather than preferred. The figure is laid out at --vb-w / 112 x --field-unit
    so that one lattice cell of the drawing is one cell of the ground it stands
    on, and the column it is laid out in is 573 px at every viewport the pinned
    stage admits, measured — which is 668 viewBox units and no more. The drawing
    as it stood was 728 wide. Let the frame out to hold it and `max-width: 100%`
    binds instead of the calc, the object renders at 85 % of the ground's scale,
    and the one-cell-to-one-cell registration quietly stops being true — the
    reader sees two lattices at two sizes, which is the fault this page's whole
    scale derivation exists to avoid. The machine is 571.8 of those 668 units
    and does not move. The plate was 728 of them, 156 of which was plate lying
    outside the machine's own two extremes; it is 621.6, of which 49.8 is.

    SO THE COMPOSING IS DONE IN WHAT IS DRAWN rather than in what is cut off.
    The plate holds the set with a lip and stops: 0.25 behind the cooler, 0.20
    past the end cover, 0.15 outboard of the skid beams — 9.4 units measured
    across the edge, 8 CSS px at stage size, a lip and not a margin. That is a
    base frame under a generating set, which is what it is, rather than an
    apron. The frame is then the bounding box plus 18, taken before the trace
    (isolib.bbox), and the four edges land where the drawing puts them rather
    than on lattice rows: a cut had to be deliberate to be read as a cut, so
    #404 put all four edges on lattice lines and said so. A crop that cuts
    nothing owes nothing to the lattice.

    THE PAD IS 18 AND THE OTHER THREE TAKE 30, which is the last thing the
    column budget buys and is worth naming rather than leaving to look like a
    slip. At 30 this frame is 681.6 units against a 668-unit column and the
    scale binding above comes straight back. 18 units is 15 CSS px of air at the
    two diamond points and more everywhere else, because those points are
    corners of a rhombus and not sides of a box.

    THE MACHINE IS A TRAIN ON +x, which is 26.57 deg, so the set, its skid
    beams, the floor they run on and the trace that reaches them are all on one
    angle. A row laid across the screen would have put the whole thing on the
    two directions the system does not own — see the note at the top of this
    file.
    """
    reset()
    gid = 'cf-ex-01'
    s0, s1, s2, s3 = [], [], [], []
    BEAM = 0.5                                                 # top of the skid
    AXIS = 1.45                                                # the shaft line
    GR = 0.86                                                  # generator radius

    # ---- 0 · the floor, and the skid the set is bolted down to.
    # A BASE FRAME, NOT AN APRON, and every number in these four lines is the
    # lip it carries rather than the ground it covers — see the docstring. The
    # plate's own screen width is (dx + dy) lattice cells, because its two
    # extreme points are the rhombus corners at (x0, y1) and (x1, y0) and the
    # projection reads (x - y): 8.8 + 2.3 is 11.1 cells, 621.6 units, and that
    # number plus twice the pad is what has to clear 668. Widening it in y is
    # therefore exactly as expensive as lengthening it in x, which is why the
    # lip is spent where it is seen — 0.25 behind the cooler and 0.20 past the
    # end cover, where the plate ends AT the machine and a viewer looks, and
    # 0.15 outboard, where a beam needs an edge under it and not a margin.
    #
    # The machine occupies x -6.6 to 1.75 and y +-1.0 exactly — the cooler
    # package sets the back and both flanks, the end cover sets the front — so
    # there is no slack in here to be found later by measuring again.
    # ny=0: the lengthwise seam ran at y = 0, which is the drum's own axis, so
    # it came out on the drum's lower silhouette — two 26.57 deg lines 0.57 px
    # apart for 95 px, reading as one contour that thickens. The floor keeps its
    # two cross seams and loses the one that had nowhere to be.
    s0 += foundation(-6.85, -1.15, 8.8, 2.3, 0.22, 0.24, 2, 0)
    # THE BEAMS MOVED WITH THE PLATE, outer flange to +-1.0. Left at +-1.10
    # under a plate that now ends at +-1.15 they would have shown 2.8 units of
    # plate outside themselves — 2.4 px, which is the brittle hairline the
    # foundation's own docstring was written about, and not a lip. At +-1.0 they
    # also land directly under the cooler's flanks, which is where a skid beam
    # belongs and is where the load is.
    for yy in (-1.0, 0.62):                                    # the two skid beams
        s0 += box(-6.7, yy, 0.22, 8.5, 0.38, 0.28, FACE_TOP, PLATE_L, PLATE_R)
    s0.append(line(p_(-6.7, 1.0, 0.36), p_(1.8, 1.0, 0.36)))   # the near beam's web

    # ---- 1 · the back band: the cooler package, then the engine.
    # The cooler is the FURTHEST BACK thing here and therefore the highest on
    # screen, not the tallest: at 2:1 an element loses half a unit of screen
    # height for every unit it moves back. Drawn as deep as the engine it left
    # the frame through the top before the air cleaners were anywhere near it.
    s1 += box(-6.6, -1.0, BEAM, 1.35, 2.0, 0.16, FACE_TOP, PLATE_L, PLATE_R)
    s1 += box(-6.5, -0.9, 0.66, 1.15, 1.8, 1.42)               # cooler core
    for i in range(1, 5):                                      # the fin pack, seen
        xx = -6.5 + 1.15 * i / 5.0                             # edge-on. Four across
        s1.append(line(p_(xx, 0.9, 0.7), p_(xx, 0.9, 2.04)))   # the core at 0.23,
                                                               # which is 6.9 px
    s1 += box(-6.6, -1.0, 2.08, 1.35, 2.0, 0.22)               # which is 6.9 px
    # FACE_R, not FACE_L: this disc lies in the plane x = -5.35, so it is a +x
    # face and the register gives +x #F6F6F6. It was painted the +y tone to buy
    # contrast against the near-white face behind it, which is the one thing the
    # dense register says not to do — the contour does the describing.
    s1.append(disc(-5.35, 0.0, 1.4, 0.6, 'x', FACE_R))         # fan shroud
    s1.append(disc(-5.35, 0.0, 1.4, 0.15, 'x', ACCENT))        # fan boss

    s1 += box(-4.2, -0.95, BEAM, 3.25, 1.9, 1.25)              # crankcase
    s1.append(line(p_(-4.2, 0.95, 1.05), p_(-0.95, 0.95, 1.05)))   # crankcase joint
    # BELOW THE JOINT, all three of them. The joint at 1.05 divides a crankcase
    # from a cylinder block, and the cylinder divisions below run from it up. A
    # door at 1.15 therefore sits on the block, where a division line ran
    # straight through it 2.7 px from its own edge.
    s1.append(quad_y(0.95, -4.0, 0.6, 0.5, 0.38, FACE_TOP))    # access door
    s1.append(quad_y(0.95, -3.87, 0.72, 0.2, 0.18, DARK))      # sight glass
    s1.append(quad_y(0.95, -3.1, 0.62, 1.45, 0.2, ACCENT))     # oil gallery

    # dx 2.80 ends the deck at x = -1.25, flush with the valve cover above it.
    # At 2.95 it ended at -1.10, where its front top edge ran tangent to the
    # generator's far rim — two contours half a pixel apart, which is neither a
    # join nor a gap.
    s1 += box(-4.05, -0.95, 1.75, 2.8, 1.9, 0.42)              # head deck
    # THE DIVISIONS BELONG TO THE HEAD, and stop at it. Run down the block as
    # well they turned its whole flank into a five-by-two grid of panels — the
    # brickwork read, one pitch instead of two but still a wall. A crankcase is
    # one casting; what divides is the cylinders above it. The deck is flush
    # with the block in y rather than inset by a tenth, so the division and the
    # block edge below it stay on one line: on a face set back a tenth the same
    # division lands 5.6 px to the left, which at this size is a misprint.
    for i in range(1, 6):
        xx = -4.05 + 2.8 * i / 6.0
        s1.append(line(p_(xx, 0.95, 1.75), p_(xx, 0.95, 2.17)))
    s1 += box(-3.9, -0.5, 2.17, 2.65, 1.0, 0.2)                # valve cover
    for xx in (-3.6, -2.7):                                    # air cleaners
        s1 += cyl(xx, 0.0, 2.37, 'z', 0.7, 0.25)
        s1.append(hoop(xx, 0.0, 2.79, 0.25, 'z'))
    s1 += cyl(-1.5, 0.0, 2.37, 'z', 1.02, 0.155)               # exhaust stack —
    for zz in (2.72, 3.06):                                    # taller and thinner
        s1.append(hoop(-1.5, 0.0, zz, 0.155, 'z'))             # than a cleaner, so
                                                               # it is not a third one

    # ---- 2 · the generator, one drum closed at both ends.
    # ONE CYLINDER, NOT THREE. cyl(far=False) drops the far cap ELLIPSE and
    # keeps the crown band, which still ends in a full half-arc and protrudes
    # 43.93 * r px past the tube's flat cut — 40 px of white, black-outlined
    # crescent lying over whatever the cylinder was supposed to be running into.
    # The object this replaces shipped one over its engine block: exactly the
    # "ellipse nobody could name" the library's own docstring warns about, from
    # the argument the docstring recommends. Butting a second and third cylinder
    # on for the flywheel housing and the end shield buys two more of them plus
    # two 56.31 deg end chords, so the housing and the shield are drawn on the
    # drum's own end face instead, which is what they are.
    for xx in (-0.15, 1.05):                                   # generator feet
        s2 += box(xx, -0.8, BEAM, 0.55, 1.6, 0.16, FACE_TOP, PLATE_L, PLATE_R)
    # cap=FACE_R: the near cap lies in a plane of constant x, so it is a +x face
    # and takes the lit-side tone. cyl() defaults it to FACE_TOP, which is the
    # sky-facing value and is only right for an axis-z cylinder.
    s2 += cyl(-0.95, 0.0, AXIS, 'x', 2.70, GR, far=True, cap_far=FACE_L, cap=FACE_R)
    # A BAND HAS TO HAVE A WIDTH. Two hoops round one drum meet at the
    # silhouette whatever their spacing — that is true of a real band and is
    # not the fault — but at 0.06 apart the lens between them never opened
    # past 3.4 units, so the pair read as one contour that thickens and splits
    # rather than as a flange: the exact artefact the floor's own seam note
    # further up was written about. 0.16 opens it to 9 units at the widest.
    for xx in (-0.70, -0.54):                                  # the drive-end
        s2.append(hoop(xx, 0.0, AXIS, GR, 'x'))                # flange, a band
    # Four ribs at 0.42 rather than 0.62: the drum came in from 3.43 to 2.70 so
    # that the machine ends inside the frame, and a pitch that is not shortened
    # with it runs the last rib to 1.91 — past the end cover at 1.75, which is
    # a rib standing in mid-air off the end of the barrel it belongs to.
    for i in range(4):                                         # cooling ribs
        s2.append(hoop(0.05 + i * 0.42, 0.0, AXIS, GR, 'x'))

    # ---- 3 · the fittings, nearest the reader
    # The pad is sunk to 2.10, not sat at 2.24. A rectangle laid across a drum
    # meets it only along one line: at y = +-0.45 the crown has already fallen
    # to 2.183, so a pad whose underside is at 2.24 rests on its own centre and
    # holds both its corners in the air.
    s3 += box(0.35, -0.45, 2.1, 1.0, 0.9, 0.16)                # terminal-box pad
    s3 += box(0.47, -0.34, 2.26, 0.76, 0.68, 0.38)             # terminal box
    s3.append(quad_t(0.58, -0.23, 2.64, 0.54, 0.46))

    s3.append(disc(1.75, 0.0, AXIS, 0.7, 'x', FACE_R))         # the end cover
    # disc(), not hoop(). hoop() draws the half of a circle that faces the
    # reader, which is right for a rib round the barrel and wrong for a circle
    # lying IN the end face — that one is wholly visible, and drawn as a hoop it
    # is an open crescent with two dangling ends across the focal element.
    s3.append(disc(1.75, 0.0, AXIS, 0.56, 'x'))                # its bolt circle

    # x 1.53 sits between the last rib and the end cover, and clear of the
    # terminal box, which ends at 1.35. At 0.8 the ghost ran parallel to the
    # rib at 1.06 for 43 px and its dashes crossed the box, which stands in
    # front of it — a ghost is drawn over the mass it is inside, so it has to
    # be inside one.
    ghost = [disc(1.53, 0.0, AXIS, 0.5, 'x')]                  # the rotor, x-ray
    orbits = [orbit(-5.35, 0.0, 1.4, 0.38, 'x')]               # the fan, turning

    # lime_span_disc, not lime_span: a lit disc needs its anchor on its own
    # silhouette AND its endpoints written in the frame the rotate() on the
    # ellipse establishes. Measured on the version before it, the lightest pixel
    # of this light sat 68 % of the way DOWN the disc and lime never appeared.
    # The whole derivation is on the function in isolib.py.
    light = light_disc(gid, 1.75, 0.0, AXIS, 0.46, 'x')
    la, lb = lime_span_disc(1.75, 0.0, AXIS, 0.46, 'x')

    # THE CROP IS TAKEN HERE, before the trace, which is the one thing this
    # object still does differently from the other three and the reason
    # isolib.bbox() exists rather than assemble()'s own default: the trace below
    # enters from off-stage, registers both its endpoints, and would otherwise
    # pull the right edge out to hold the half of itself that was drawn to be
    # cut. Everything else about the crop is now the other three objects' —
    # extent plus a pad, no authored window, nothing outside it.
    #
    # THE HEIGHT IS NOT UNDER THE COLUMN'S CONSTRAINT. Only the WIDTH is read
    # against it; the height follows through `height: auto`, and the row is
    # 541 px tall at 1440x900 because the copy card sets it. So the height is
    # simply what the drawing asks for — 464.4 units, 398 px — and no number
    # here is rationing it.
    crop = bbox(18.0)
    # Three nodes, each a place this field's copy names: the shaft end that is
    # lit, the exhaust outlet, the terminals. The fourth marked one air cleaner
    # lid and not the other, which is a scatter rather than a construction.
    nodes = [node(1.75, 0.0, AXIS), node(-1.5, 0.0, 3.39, 3),
             node(0.85, -0.34, 2.64, 3)]
    # The trace runs on the OTHER ground axis. Run down +x with the skid it was
    # parallel to the plate's own chamfer contour and 1.0 unit from it — 0.83
    # CSS px, which is not a signal arriving, it is that contour getting thicker.
    # On +y it crosses the empty quarter above the machine instead and lands on
    # the terminal box, which is where a generator's cables actually leave.
    #
    # AND IT ENTERS THE FRAME rather than starting inside it. A stroke that both
    # begins and ends in open ground reads as a leader line pointing at a part,
    # not as a signal reaching one. So it starts outside the right edge and
    # carries --trace-from = 1 - (the share of it that is off-stage):
    # pathLength normalises against the DRAWN length, and without it the draw
    # spends that share of its range on a line nobody can see.
    # -> foundations/motion.html, "Why the two ends are authored"
    #
    # THE SHARE IS COMPUTED FROM THE CROP, not typed. It was typed once, at
    # 0.918 for an edge at X = 544; the edge then moved to 488 to stop the
    # frame cutting the cooler, and a literal cannot know that. Off-stage went
    # from a twelfth of the line to two fifths of it, and the draw would have
    # spent the first two fifths of the step's scroll on nothing at all.
    #
    # The start is at y = -2.75 and follows the right edge for the same reason:
    # the edge moved again when the plate came in, and a start that does not
    # move with it is a trace that begins inside the frame — a leader line
    # pointing at a part. Both ends stay on the -y axis, so the angle is the
    # one it always was; only the length changes. 521.6 against an edge at
    # 511.6 is the 7 % it was drawn to have.
    ta, tb = (0.85, -2.75, 2.64), (0.85, -0.34, 2.64)
    traces = [trace(ta, tb, frm=trace_from(ta, tb, crop))]
    return assemble(gid, la, lb, [(0, s0), (1, s1), (2, s2), (3, s3)],
                    light, nodes, traces, ghost, orbits, crop=crop)


# ==================================================================== 02
def anlagen():
    """A process unit: column, rack, storage, exchangers. An Anlage is a net of
    assets rather than one asset, so the object is read as a plot plan with
    elevation — everything connected, nothing standing on its own."""
    reset()
    gid = 'cf-ex-02'
    s0, s1, s2, s3 = [], [], [], []

    s0 += foundation(-2.8, -2.4, 5.6, 4.8, 0.2, 0.2, 2, 1)

    # ---- 1 · the column, furthest back and the tallest thing here
    cx, cy, cr = -1.75, -1.2, 0.44
    s1 += cyl(cx, cy, 0.2, 'z', 0.3, 0.6, side=PLATE_R, cap=FACE_TOP)     # skirt
    s1 += cyl(cx, cy, 0.5, 'z', 3.0, cr, cap=None)
    for zz in (1.35, 2.45):                                    # shell courses
        s1.append(hoop(cx, cy, zz, cr, 'z'))
    fx, fy = cx + cr * 0.707, cy + cr * 0.707                  # the front generatrix
    for o in (0.17, -0.17):                                    # ladder stiles
        s1.append(line(p_(fx + o, fy - o, 0.62), p_(fx + o, fy - o, 3.3)))
    for i in range(8):
        zz = 0.78 + i * 0.34
        s1.append(line(p_(fx + 0.17, fy - 0.17, zz), p_(fx - 0.17, fy + 0.17, zz)))
    s1 += taper(cx, cy, 3.5, cr, 0.3, 0.26, FACE_TOP, FACE_R)  # head
    s1 += cyl(cx, cy, 3.76, 'z', 0.18, 0.22, side=FACE_L)      # top nozzle

    # ---- 2 · storage, then the rack that crosses in front of it
    tx, ty = 1.75, -1.4
    s2 += cyl(tx, ty, 0.2, 'z', 1.4, 0.6)                      # vertical tank
    for zz in (0.6, 1.0, 1.4):
        s2.append(hoop(tx, ty, zz, 0.6, 'z'))
    s2 += taper(tx, ty, 1.6, 0.6, 0.32, 0.3, FACE_TOP, FACE_L)
    s2 += cyl(tx, ty, 1.9, 'z', 0.18, 0.13, side=FACE_L)
    s2.append(quad_x(tx + 0.6, ty - 0.18, 0.42, 0.36, 0.34, DARK))   # manway

    for xx in (-0.5, 0.95, 2.4):                               # rack columns
        s2 += box(xx - 0.09, -0.62, 0.2, 0.18, 0.18, 2.0)
        s2.append(quad_x(xx + 0.09, -0.62, 1.9, 0.18, 0.1, ACCENT))
    s2 += box(-0.62, -0.86, 2.2, 3.14, 0.66, 0.14)             # rack beam
    s2 += seams((-0.62, -0.2, 2.2), (2.52, -0.2, 2.2),
                (-0.62, -0.2, 2.34), (2.52, -0.2, 2.34), 5)
    s2 += cyl(-0.62, -0.7, 2.51, 'x', 3.14, 0.17, side=FACE_L)             # process line
    for i in range(4):
        s2.append(hoop(-0.15 + i * 0.72, -0.7, 2.51, 0.17, 'x'))
    s2 += cyl(-0.62, -0.32, 2.45, 'x', 3.14, 0.11, side=FACE_R)            # utility line
    for i in range(4):
        s2.append(hoop(0.05 + i * 0.72, -0.32, 2.45, 0.11, 'x'))

    s2 += box(-2.5, 0.65, 0.2, 1.5, 0.8, 0.18, FACE_TOP, PLATE_L, PLATE_R)  # pump plinth
    s2 += cyl(-2.35, 1.05, 0.62, 'x', 0.72, 0.24, cap=FACE_TOP)             # motor
    for i in range(3):
        s2.append(hoop(-2.19 + i * 0.2, 1.05, 0.62, 0.24, 'x'))
    s2 += cyl(-1.5, 1.05, 0.6, 'x', 0.38, 0.3, cap=FACE_TOP)                # pump
    s2 += cyl(-1.3, 1.05, 0.9, 'z', 0.3, 0.1, side=FACE_L)

    # ---- 3 · the exchangers, nearest the reader
    for yy in (0.6, 1.6):
        for xx in (0.5, 1.8):                                  # saddles
            s3 += box(xx, yy - 0.2, 0.2, 0.3, 0.4, 0.33, FACE_TOP, PLATE_L, PLATE_R)
        s3 += cyl(0.3, yy, 0.85, 'x', 2.1, 0.32, side=FACE_R, cap=FACE_TOP, cap_far=FACE_L)
        for i in range(4):
            s3.append(hoop(0.62 + i * 0.42, yy, 0.85, 0.32, 'x'))
        s3.append(hoop(2.4, yy, 0.85, 0.24, 'x'))
        s3 += cyl(0.72, yy, 1.17, 'z', 0.3, 0.09, side=FACE_L)  # nozzles
        s3 += cyl(2.02, yy, 1.17, 'z', 0.3, 0.09, side=FACE_L)

    ghost = [disc(tx, ty, 1.15, 0.6, 'z'),          # the level in the tank
             disc(cx, cy, 1.9, cr * 0.76, 'z')]     # a tray in the column
    light = light_disc(gid, cx, cy, 3.94, 0.22, 'z')
    la, lb = lime_span((cx - 0.22, cy - 0.22, 3.94), (cx + 0.22, cy + 0.22, 3.94))
    nodes = [node(cx, cy, 3.94), node(tx, ty, 2.08, 3), node(0.95, -0.53, 2.34, 3)]
    traces = [trace((4.0, -1.0, 0.2), (2.8, -1.0, 0.2))]
    return assemble(gid, la, lb, [(0, s0), (1, s1), (2, s2), (3, s3)],
                    light, nodes, traces, ghost)


# ==================================================================== 03
# Where the rotor has stopped. rotor()'s docstring has the argument; this is
# the number it produces. Scanning all 120 distinct positions of a three-blade
# rotor for the one whose WORST blade is furthest from a brand angle leaves
# two, 18 deg and 78, tied at 13.2 / 9.9 / 9.0 deg off — they are the same
# three axes with the blades on opposite ends, and every other position puts
# some blade closer than 9 deg to a horizontal, a 45 or a 63.43 that it is not
# on. 78 is the one that reads: one blade up, one out to the right, one down
# to the left, and none of the three lying along the tower.
ROTOR_PHASE = 78.0


def erneuerbare():
    """Generation, conversion, storage, on one pad — the three things whose
    telemetry only means anything read against each other."""
    reset()
    gid = 'cf-ex-03'
    s0, s1, s2, s3 = [], [], [], []

    s0 += foundation(-2.9, -2.4, 5.8, 4.8, 0.2, 0.2, 2, 1)

    # ---- 1 · the turbine, furthest back
    #
    # THE ROTOR IS ON THE NACELLE'S +x END, AND THAT IS THE WHOLE REASON THREE
    # BLADES CAN BE DRAWN. Two points share a screen position when they differ
    # by a multiple of (1, 1, 1), so in this projection "further along +x" and
    # "nearer the viewer" are the same statement. Hang the rotor off the -x end
    # — which is where a drawing that only had to carry a sweep circle put it —
    # and the rotor plane is behind both masses: measured at the best of the
    # 120 azimuths, one blade of three came out wholly inside the silhouette of
    # the nacelle and the tower, and a three-blade rotor showing two blades is
    # not a wind turbine, it is a mistake. Turned round, every blade is in
    # front of everything it crosses, and the machine is the same machine: an
    # upwind rotor seen from upwind, nacelle behind it, tower behind that.
    wx, wy = -1.95, -1.75
    hx, hz = wx + 0.15, 2.99                                   # the rotor plane
    s1 += cyl(wx, wy, 0.2, 'z', 0.16, 0.36, side=PLATE_R)      # foundation
    s1 += taper(wx, wy, 0.36, 0.19, 0.12, 2.5, None, FACE_R)
    for zz in (1.1, 1.9):
        s1.append(hoop(wx, wy, zz, 0.19 - (zz - 0.36) / 2.5 * 0.07, 'z'))
    # The nacelle is SQUARE in section, 0.26 x 0.26, and that is what lets the
    # spinner be a circle inside a square rather than a circle inside a
    # rectangle. It was 0.26 x 0.24 under a hub of r 0.13: flush with the end
    # face's half-width and 0.01 over its half-height, so the one circle in
    # the drawing that names the machine crossed the edge it sits on, top and
    # bottom, by a hairline nobody could read as anything but a slip. It still
    # covers the tower's top rim whole — the rim is the taper's own arc and a
    # tower has to end under something.
    s1 += box(hx - 0.55, wy - 0.13, 2.86, 0.55, 0.26, 0.26)    # nacelle
    s1 += rotor(hx, wy, hz, 0.09, 0.88, 'x', 3, ROTOR_PHASE)   # blades, over both
    s1.append(disc(hx, wy, hz, 0.11, 'x', FACE_TOP))           # spinner

    # ---- 2 · the transformer bay and the electrolyser, middle
    #
    # THE BAY STANDS 0.45 OFF THE ELECTROLYSER'S PAD AND USED TO STAND 0.3
    # OFF IT, which was 0.3 of plate that arrived on screen as two units. The
    # two pads' facing edges both run along +y and 50.1 x |dx - dz| is the gap
    # between them, so a 0.3 gap between pads whose tops differ by 0.26 is a
    # slit narrower than the contour drawing it: the two masses read as one
    # with a crack in it. Nothing about the bay itself changes — it moves.
    s2 += box(-1.2, -1.55, 0.2, 1.35, 1.05, 0.18, FACE_TOP, PLATE_L, PLATE_R)
    s2 += box(-1.05, -1.4, 0.38, 1.05, 0.75, 0.62)             # transformer
    s2 += seams((-1.05, -0.65, 0.38), (0.0, -0.65, 0.38),      # radiator fins
                (-1.05, -0.65, 1.0), (0.0, -0.65, 1.0), 5)
    # ON THE TANK'S OWN CENTRE LINES, x -0.525 and y -1.025 — which are also
    # the middle radiator fin's. The row used to sit a fortieth of a cell off
    # in both axes at once, so there was 0.05 more tank to one side of the
    # bushings than the other, and the middle bushing missed the middle fin by
    # the same amount.
    for xx in (-0.825, -0.525, -0.225):                        # bushings
        s2 += cyl(xx, -1.025, 1.0, 'z', 0.26, 0.07, side=FACE_L)

    s2 += box(0.6, -1.85, 0.2, 1.9, 0.95, 0.26, FACE_TOP, PLATE_L, PLATE_R)
    for xx in (0.95, 1.55, 2.15):                              # the same, on the pad: -1.375
        s2 += cyl(xx, -1.375, 0.46, 'z', 0.14, 0.31, side=PLATE_R)  # base flange
        s2 += cyl(xx, -1.375, 0.6, 'z', 1.02, 0.26)
        for zz in (0.85, 1.2, 1.55):
            s2.append(hoop(xx, -1.375, zz, 0.26, 'z'))
    s2 += box(0.75, -1.525, 1.62, 1.6, 0.3, 0.16)              # header
    s2 += seams((0.75, -1.225, 1.62), (2.35, -1.225, 1.62),
                (0.75, -1.225, 1.78), (2.35, -1.225, 1.78), 3)

    # ---- 3 · the bank and the array, nearest
    s3 += box(-2.6, 0.9, 0.2, 2.8, 1.1, 1.05)                  # battery container
    s3 += seams((-2.6, 2.0, 0.2), (0.2, 2.0, 0.2),             # door leaves
                (-2.6, 2.0, 1.25), (0.2, 2.0, 1.25), 7)
    # Both cant rails are the container's own 0.12 inset, which is the inset
    # the end frame below is already drawn at. The top one was 1.12 — one
    # hundredth under the frame it turns into at the corner.
    s3.append(line(p_(-2.6, 2.0, 1.13), p_(0.2, 2.0, 1.13)))   # cant rails
    s3.append(line(p_(-2.6, 2.0, 0.32), p_(0.2, 2.0, 0.32)))
    # THE THREE PANELS ARE EACH ONE DOOR LEAF WIDE, edge to edge. The front is
    # eight leaves of 0.35 and the panels were 0.3, which leaves exactly two
    # ways to place one and both of them are wrong: straddling a joint, which
    # is what the first louvre and the lit panel did — the louvre by nearly
    # half a leaf, a vent across a door that cannot open — or centred in a leaf
    # with 0.025 of door showing down each side, which is a pair of parallel
    # lines under two screen pixels apart and reads as a printing fault. A
    # panel that IS the leaf has neither: its two vertical edges are the two
    # seams, drawn on top of them, and only the top and bottom edges are free,
    # where there is 0.155 of door to be clear of.
    leaf = 2.8 / 8.0
    lv = [-2.6 + leaf * k for k in (0, 3, 7)]                  # leaves 1, 4, 8
    s3.append(quad_y(2.0, lv[0], 0.475, leaf, 0.5, DARK))      # louvres
    s3.append(quad_y(2.0, lv[2], 0.475, leaf, 0.5, DARK))
    s3 += seams((-2.6, 0.9, 1.25), (0.2, 0.9, 1.25),
                (-2.6, 2.0, 1.25), (0.2, 2.0, 1.25), 3)
    # One unit of roof plant on each of the outer roof seams, x -1.9 and -0.5,
    # which are symmetric about the container's own centre. The right-hand one
    # used to stand on -0.6, a tenth off a seam and not symmetric either.
    #
    # AND THE UNIT IS 0.7 x 0.5 x 0.14, NOT 0.5 x 0.5 x 0.22, because in this
    # projection a box's height and its setback SUBTRACT. Two lines that run
    # along +y, at x1/z1 and x2/z2, land 50.1 x |dx - dz| screen units apart —
    # so a box 0.25 out from the seam it straddles and 0.22 tall put its top
    # edge 1.5 units from that seam where the seam surfaces, and 0.3 back from
    # the roof's own back edge put its back edge 4 units from it. Both of those
    # are gaps you cannot see and cannot mistake for anything but a doubled
    # line. Wider and flatter, on the roof-plant proportion 01 and 04 already
    # use, the same two gaps are 10.5 and 8.
    for xx in (-2.25, -0.85):                                  # roof plant
        s3 += box(xx, 1.2, 1.25, 0.7, 0.5, 0.14)
    s3.append(quad_x(0.2, 1.02, 0.32, 0.86, 0.81))             # end frame
    s3 += seams((0.2, 1.02, 0.32), (0.2, 1.02, 1.13),
                (0.2, 1.88, 0.32), (0.2, 1.88, 1.13), 2)

    # THE ARRAY IS OFF THE PLATE'S CHAMFER, and it was off it by 0.05 twice —
    # 0.05 PAST the line on +y and 0.05 SHORT of it on +x. Both of those are
    # two parallel edges three screen units apart running the length of the
    # object, which is the one thing a 26.57 deg drawing cannot absorb: a
    # sliver reads as a misprint, not as a gap. It sits on the container's own
    # front line at y 2.0 now, and takes the container's 0.1 margin at the
    # far edge.
    ax, ay = 0.5, 0.5
    s3 += box(ax, ay, 0.2, 2.1, 1.5, 0.14, FACE_TOP, PLATE_L, PLATE_R)   # array
    fx, fy, fw, fh = ax + 0.12, ay + 0.12, 1.86, 1.26          # the panel field
    s3.append(quad_t(fx, fy, 0.34, fw, fh))
    # The shaded string IS a cell of the grid below, rather than a rectangle
    # the same size as one: 1.13 -> 1.59 against a cell of 1.135 -> 1.6.
    s3.append(quad_t(fx + fw / 4, fy, 0.34, fw / 4, fh / 2, ACCENT))
    s3 += seams((fx, fy, 0.34), (fx + fw, fy, 0.34),
                (fx, fy + fh, 0.34), (fx + fw, fy + fh, 0.34), 3)
    s3 += seams((fx, fy, 0.34), (fx, fy + fh, 0.34),
                (fx + fw, fy, 0.34), (fx + fw, fy + fh, 0.34), 1)

    ghost = []
    orbits = [orbit(hx, wy, hz, 0.88, 'x')]                    # the sweep the tips travel
    light = light_quad(gid, [(lv[1], 2.0, 0.475), (lv[1] + leaf, 2.0, 0.475),
                             (lv[1] + leaf, 2.0, 0.975), (lv[1], 2.0, 0.975)])
    la, lb = lime_span((lv[1], 2.0, 0.975), (lv[1] + leaf, 2.0, 0.475))
    nodes = [node(lv[1] + leaf / 2, 2.0, 0.725), node(1.55, -1.375, 1.78, 3),
             node(hx, wy, hz, 3)]
    traces = [trace((-4.3, -0.3, 0.2), (-2.9, -0.3, 0.2))]
    return assemble(gid, la, lb, [(0, s0), (1, s1), (2, s2), (3, s3)],
                    light, nodes, traces, ghost, orbits)


# ==================================================================== 04
# THE ONE BOX, drawn six times and ghosted twice. A fleet is a repetition, and
# the four asset classes this field names — ships, trains, aircraft, mining
# equipment — do not repeat each other; what repeats across them is the load. So
# the container is a function rather than a shape: the same 1.1 x 0.44 x 0.48
# body, the same corrugations, the same door seam, four of them stacked on the
# ship, one on the rail wagon, one on the semi's trailer. It is also the unit
# the reader measures the yard with — every other dimension in this object was
# chosen against it.
#
# 2.5 : 1 : 1.09 is a 20-foot box, exactly. The one proportion in this drawing
# that had to be right is the one everybody has seen ten thousand of.
CT_L, CT_W, CT_H = 1.1, 0.44, 0.48


def container(x, y, z, top=FACE_TOP):
    """A box and five lines. `top=None` leaves the sky face unpainted, for the
    object's one lit element to be laid over."""
    out = box(x, y, z, CT_L, CT_W, CT_H, top, FACE_L, FACE_R)
    # Three corrugations, not seven. At 55 px long the side takes a rib every
    # 14 px and still reads as pressed steel; at seven it is a grey hatch.
    out += seams((x, y + CT_W, z), (x + CT_L, y + CT_W, z),
                 (x, y + CT_W, z + CT_H), (x + CT_L, y + CT_W, z + CT_H), 3)
    out.append(line(p_(x, y + CT_W, z + CT_H * 0.86),
                    p_(x + CT_L, y + CT_W, z + CT_H * 0.86)))     # the top rail
    out.append(line(p_(x + CT_L, y + CT_W / 2, z),
                    p_(x + CT_L, y + CT_W / 2, z + CT_H)))        # the door leaves
    return out


def wheelset(x, y, z, r, axis='y'):
    """A wheel and its hub, on the near flank. Only the near flank: the far one
    is behind the body it carries, and drawing it there puts two grey discs in
    a place the reader cannot see a wheel from.

    `axis` is the plane the disc lies in — 'y' for a machine running down +x,
    'x' for one running down +y. It was hard-coded 'y' once, and the one +y
    machine in the yard inherited it: the aircraft taxied on wheels turned 90
    degrees across its own axis, three casters under a machine whose nose
    points at the reader."""
    return [disc(x, y, z, r, axis, ACCENT), disc(x, y, z, r * 0.34, axis, FACE_TOP)]


def flotten():
    """A yard with one of everything on it: a ship on its blocks, an aircraft,
    a train, a semi and an excavator, and the same container on three of them.

    WHAT THIS REPLACES, because the replacement only makes sense against it.
    The first fleet object was four identical wagons in a row, and it was drawn
    that way from the copy: a fleet is a repetition, so draw one machine four
    times. The trouble is that the machine was nothing — a box, a smaller box,
    a mast — because a shape that has to serve as ship, aircraft, train and
    mining equipment at once ends up serving as none of them, and four copies
    of a shape that means nothing is not four times the meaning. The chips under
    this field's copy name Flugzeuge, Bergbaugerät, Schiffe and Züge. The
    drawing beside them showed none of the four.

    SO THE REPETITION MOVED TO WHERE IT IS TRUE. It is not the assets that
    repeat — an operator's aircraft and its trains are not each other — it is
    the load, the route and the question. The container is drawn six times here,
    four of them in one stack; that is the repetition the copy is about, and it
    is what makes five different machines one fleet rather than five stickers.
    THE LIT BOX IS ONE OF THE FOUR IN THE STACK, which is the only place in the
    drawing where standing out means anything: a lit box on the trailer is the
    only box on the trailer. Surrounded by its own repetitions it says the
    field's own sentence — what shows on one unit can be checked immediately on
    all the others — and the trace comes in off-stage to exactly that box.

    EVERY MACHINE STILL RUNS ON A LATTICE AXIS — the ship, the train, the semi
    and the excavator down +x, the aircraft down +y — so every long edge in the
    drawing is 26.57 deg one way or the other, and screen-horizontal, the
    direction this projection cannot draw, appears nowhere. Vertical appears
    only where a thing is vertical: masts, gear legs, the fin's trailing edge.
    THE RAKES ARE THE CHARACTER LINES and each is one of the three ratios the
    lattice admits: the stem, the crawler's idler ramp and the boom at 45 deg,
    the transom, the sprocket ramp, the stick and the fin's leading edge at
    63.43. A 40-degree boom drawn because it looked right would be off the
    system's angles exactly as a horizontal rule is — and this object shipped a
    61.4 deg bow for one pass, from raising a deck and not re-deriving the stem
    under it.

    THE PLATE IS 5.9 x 4.7 and that is a width decision, not an area one. The
    figure renders at --vb-w / 112 x --field-unit so that one cell of the
    drawing is one cell of the ground it stands on, and the column it is laid
    out in holds about 668 units — maschinenbau()'s docstring derives that
    number. A plate's screen width is (dx + dy) cells, so lengthening it and
    widening it cost exactly the same, and 10.6 cells plus two pads is 653.6.
    That is the same frame 03 takes and it is the whole budget: the five
    machines are sized to the yard, not the yard to the machines.

    THE FOUR CORNERS ARE SPOKEN FOR, which is what keeps a plate this wide from
    reading as an apron with things loose on it: the ship takes the back corner,
    the aircraft the right, the excavator the left and the semi's tractor the
    front, with the train through the middle on the one axis all five share.
    """
    reset()
    gid = 'cf-ex-04'
    s0, s1, s2, s3 = [], [], [], []
    Z = 0.2                                                    # the apron's top

    # ---- 0 · the apron, and the one road in it that has rails
    # No bay seams: five machines and six containers are as much line as this
    # surface can carry, and the track already gives the ground its direction.
    s0 += foundation(-2.95, -2.35, 5.9, 4.7, Z, 0.26, 0, 0)
    for i in range(13):                                        # ties
        xx = -2.78 + i * 0.44
        s0.append(line(p_(xx, -0.16, Z), p_(xx, 0.56, Z)))
    for yy in (0.0, 0.4):                                      # rails, 0.4 gauge
        s0 += box(-2.9, yy, Z, 5.8, 0.06, 0.05, FACE_TOP, PLATE_L, PLATE_R)

    # ---- 1 · the back band: the ship on its blocks, then the train
    # THE SHIP IS ON KEEL BLOCKS, not floating in a plate. Everything else here
    # stands on the apron on its own running gear, and a hull resting straight on
    # concrete is the one thing in the yard that could not have got there.
    #
    # BOTH ENDS ARE RAKED, and that is the whole difference between a ship and a
    # barge with a house on it. THE RAKES ARE THE LATTICE'S, not a shipwright's:
    # the stem rises 0.6 over 0.4 forward (dz = 1.5 dx, 45 deg) and the transom
    # 0.45 over 0.3 aft (dz = -1.5 dx, 63.43 deg), and those two ratios are the
    # only ones near a real sheer that this projection draws on a brand angle.
    # Deepening the hull without re-deriving the stem is exactly how the first
    # pass ended up with a 61.4 deg bow that no rule in the system admits.
    SY, BEAM = -2.35, 1.0
    KEEL, DECK = 0.42, 1.02
    for xx in (-2.5, -1.6, -0.7):
        s1 += box(xx, SY + 0.22, Z, 0.2, 0.78, KEEL - Z, FACE_TOP, PLATE_L, PLATE_R)
    # ONE HULL, THREE FACES. Box-plus-two-slabs drew every join twice: a slab
    # emits construction strips for all its edges, and at the bow the stem's
    # strips, the hull box's own end and the bulwark's outline stacked into a
    # wireframe X that read as a glitch, not a ship. A hull this camera sees is
    # exactly three faces — the near flank carrying BOTH rakes in one polygon,
    # the stem plate (the transom's faces away and is only ever its edge), and
    # one deck rectangle, because both rakes end AT deck level. The small
    # vertical at the transom's foot is the skeg, and it is the one edge the
    # flank polygon adds.
    NF = SY + BEAM                                             # the near flank
    s1.append(face(poly([p_(-2.9, NF, DECK), p_(-2.6, NF, 0.57), p_(-2.6, NF, KEEL),
                         p_(-0.5, NF, KEEL), p_(-0.1, NF, DECK)]), FACE_L))
    s1.append(face(poly([p_(-0.5, SY, KEEL), p_(-0.1, SY, DECK),
                         p_(-0.1, NF, DECK), p_(-0.5, NF, KEEL)]), FACE_R))
    s1.append(quad_t(-2.9, SY, DECK, 2.8, BEAM, FACE_TOP))     # the deck
    # The boot top's forward end lands ON the stem rake at its own height —
    # -0.5 was the keel corner, 0.093 short of any edge, a scratch on plating.
    s1.append(line(p_(-2.6, NF, 0.56), p_(-0.5 + (0.56 - KEEL) / 1.5, NF, 0.56)))
    s1.append(quad_t(-2.8, SY + 0.06, DECK, 2.62, BEAM - 0.12))  # bulwark
    # ONE POSITION, NOT THREE. The stack is drawn here, ghosted a tier higher and
    # lit on one of its boxes, and each of those was a separate literal until two
    # of them drifted: the lime face floated 0.1 to port of the box it was
    # supposed to be the top of, which at this scale is 6 px of light lying on
    # the deck beside the container. A lit face is a face OF something.
    STK_X, STK_Y = -1.85, SY + 0.06
    # THE DECKHOUSE COMES BEFORE THE LOAD, because the load is nearer: emitted
    # after the stack, the accommodation's lit flank and the bridge's window
    # painted themselves ONTO the containers standing in front of them. And the
    # window moved to the bridge's NEAR flank — its front face, where a bridge
    # window belongs at sea, is wholly behind the stack from this camera, so a
    # window there is a window painted on someone else's wall.
    # (FORWARD OF THE TRANSOM, still: a deckhouse on the raked plating hangs in
    # the air by exactly the rake.)
    s1 += box(-2.55, SY + 0.16, DECK, 0.56, 0.68, 0.4)         # accommodation
    s1 += box(-2.47, SY + 0.24, DECK + 0.4, 0.4, 0.52, 0.26)   # bridge
    s1.append(quad_y(SY + 0.76, -2.4, DECK + 0.5, 0.26, 0.13, DARK))
    s1 += box(-2.37, SY + 0.32, DECK + 0.66, 0.18, 0.26, 0.24)  # funnel
    for tier in (DECK, DECK + CT_H):                           # the deck load, 2 x 2
        s1 += container(STK_X, STK_Y, tier)
        s1 += container(STK_X, STK_Y + CT_W, tier)
    # The yard in two arms, split at the mast: one line through would paint its
    # far half over the body it passes behind.
    s1.append(line(p_(-0.62, SY + 0.34, DECK + 0.54), p_(-0.62, SY + 0.46, DECK + 0.54)))
    s1 += box(-0.66, SY + 0.46, DECK, 0.08, 0.08, 0.72)        # mast
    s1.append(line(p_(-0.62, SY + 0.54, DECK + 0.54), p_(-0.62, SY + 0.66, DECK + 0.54)))

    # the train — a loco and one flat wagon, on the rails drawn above
    #
    # THE SOLEBAR CLEARS THE WHEEL, by 0.03 of a unit and no more. The frames sat
    # at 0.52 with a wheel whose crown is 0.55, and a solebar 0.11 nearer than
    # the wheel plane then crosses it: four units of the tyre disappear behind
    # the frame's bottom edge and what is left reads as a washer with a bite out
    # of it, not as a wheel under a wagon. The whole train is 0.06 higher for it.
    # Everything above the solebar moved with it — a hood that stays put while
    # its own frame rises is a hood standing in its underframe.
    RY, RW = 0.2, 0.7                                          # the track's centre
    # Two bogies, not four wheels — and 0.32 within a pair against a 0.30
    # wheel diameter: at the 0.28 it shipped with, each pair's nearer tyre
    # painted across the farther one's rim and the two read as merged. The
    # wagon's four are symmetric about the DECK's centre, -0.05, not about 0.
    for xx in (-2.68, -2.36, -1.5, -1.18, -0.65, -0.33, 0.23, 0.55):
        s1 += wheelset(xx, RY + 0.24, 0.4, 0.15)
    # THE ENDS ARE CLOSED. The loco's front pair sits under its nose (at -2.57
    # the deck ran 0.2 past the tyre), and each open deck end carries a
    # headstock down to the axle line: without one, the end of a frame is a
    # shelf floating 0.33 over the rail that emerges from beneath it — which is
    # exactly where the eye lands, because an edge over daylight is the
    # highest-contrast thing in the region.
    s1 += box(-2.9, RY - 0.3, 0.46, 0.1, 0.6, 0.12)            # loco headstock
    s1 += box(-2.9, RY - RW / 2, 0.58, 1.9, RW, 0.12)          # loco underframe
    s1 += box(-2.8, RY - 0.28, 0.7, 1.15, 0.56, 0.46)          # long hood
    s1 += seams((-2.8, RY + 0.28, 0.7), (-1.65, RY + 0.28, 0.7),
                (-2.8, RY + 0.28, 1.16), (-1.65, RY + 0.28, 1.16), 3)
    s1.append(disc(-2.2, RY, 1.16, 0.17, 'z', ACCENT))         # radiator fan
    s1 += box(-2.66, RY - 0.08, 1.16, 0.14, 0.16, 0.16)        # exhaust
    s1 += box(-1.6, RY - RW / 2, 0.7, 0.6, RW, 0.74)           # cab
    s1.append(quad_x(-1.0, RY - 0.26, 1.12, 0.52, 0.24, DARK))
    s1.append(quad_y(RY + RW / 2, -1.5, 1.12, 0.4, 0.24, DARK))
    for xx in (-0.85, 0.67):                                   # wagon headstocks
        s1 += box(xx, RY - 0.3, 0.46, 0.08, 0.6, 0.12)
    s1 += box(-0.85, RY - 0.32, 0.58, 1.6, 0.64, 0.12)         # the flat wagon
    s1 += container(-0.6, RY - 0.22, 0.7)

    # ---- 2 · the aircraft down the other axis, and the excavator
    #
    # THE ONE MACHINE ON +y, and it is the aircraft because it is the one whose
    # width matters as much as its length: a wing across the row reads as a wing,
    # a wing along it reads as another roof. It also puts the two long machines
    # on the two different lattice axes, which is what stops the yard reading as
    # a shelf.
    #
    # THE NOSE POINTS +y, AT THE YARD, and that is a projection decision before
    # it is a composition one. cyl() closes its FAR end with the true silhouette
    # arc and its near end with a flat cap ellipse, so whichever end faces the
    # reader is the flat one — nose-away, the tail was a barrel end with a fin
    # behind it, and no amount of fin fixed it. Nose-toward, the flat cap IS the
    # nose cap and the arc does the tail cone for free.
    #
    # 5 : 1, NOT 3 : 1. The fuselage was first drawn fat enough to keep a
    # container in, and it swallowed the wing: at r 0.28 the tube is 31 px across
    # against a wing 4 px thick, and this camera then lays the one over the
    # other. The body is a fifth of its own length here and the wing is the
    # biggest surface on the machine, which is the proportion that reads.
    PX, TAIL, FL = 2.0, -2.4, 2.1
    FZ, FR = 0.95, 0.2
    # A STRUT STOPS AT ITS AXLE. Run to the apron like a table leg, it came out
    # below the wheel and past it on both sides, and the gear read as a post with
    # a washer hung on it. From the wheel's centre up, the wheel is the foot.
    # AND THE WHEELS ROLL THE WAY THE MACHINE DOES: this is the yard's one +y
    # machine, so its axles lie along x — wheelset's default served the
    # aircraft three of the train's wheels, casters turned 90 deg across the
    # taxi direction, and nothing else in the drawing looked more wrong.
    # A BARE WHEEL HAS WIDTH. wheelset()'s flat disc serves the train and the
    # semi because their tyres show as dark slivers half behind a solebar; the
    # aircraft's hang in the open on their own struts, and a zero-thickness
    # disc there is a washer leaning on a post — the right plane, no body.
    # Each wheel is a short drum out the strut's near flank, its hub on the
    # near cap, and the strut still ends at the axle.
    def tyre(x0, y, z, w, r):
        out = cyl(x0, y, z, 'x', w, r, side=ACCENT, cap=ACCENT, cap_far=ACCENT)
        out.append(disc(x0 + w, y, z, r * 0.34, 'x', FACE_TOP))
        return out

    for ex in (PX - 0.52, PX + 0.52):                          # main gear
        s2 += box(ex - 0.05, -1.37, 0.33, 0.1, 0.1, 0.49)
        s2 += tyre(ex + 0.05, -1.32, 0.33, 0.1, 0.13)
    s2 += box(PX - 0.05, -0.73, 0.31, 0.1, 0.1, 0.44)          # nose gear
    s2 += tyre(PX + 0.05, -0.68, 0.31, 0.08, 0.11)
    # A LOW WING IS PAINTED FIRST. The tube's crown (z 1.15) rides above the
    # wing's top face (0.9), so along this camera's ray the fuselage is in front
    # of the wing everywhere they cross — emitted after it, the wing sawed the
    # tube into a nose drum and an aft cone with nothing between them. Wing and
    # fairing first, tube over them: the one round body in the drawing stays
    # whole, and the wing is two lit surfaces either side of it.
    s2 += box(PX - 0.3, -1.66, 0.74, 0.6, 0.74, 0.12)          # belly fairing
    s2 += box(0.95, -1.56, 0.82, 2.1, 0.56, 0.08)              # the wing
    s2.append(line(p_(0.95, -1.2, 0.9), p_(3.05, -1.2, 0.9)))
    # THE FAR ENGINE AND ITS SWEEP GO HERE: after the wing they hang over,
    # before the fuselage that passes in front of the sweep's rear arc. The
    # sweep was once emitted before the wing, and the wing — which is BEHIND
    # the propeller disc — erased its forward arc.
    s2 += cyl(PX - 0.52, -1.28, 1.01, 'y', 0.5, 0.11, cap=FACE_L)
    s2 += cyl(PX - 0.52, -0.78, 1.01, 'y', 0.09, 0.045, cap=FACE_L)
    s2.append(orbit(PX - 0.52, -0.76, 1.01, 0.3, 'y'))         # far prop sweep
    # THE NOSE IS STEPPED. One cylinder ends in a cap ellipse the size of its
    # own body, which at this scale is a drum end pointed at the reader whatever
    # is drawn on it; a second radius under it and the same cap is the last few
    # pixels of a cone. The far end gets its cone free from cyl()'s own arc.
    s2 += cyl(PX, TAIL, FZ, 'y', FL - 0.16, FR, cap=FACE_L, cap_far=FACE_L)
    s2 += cyl(PX, TAIL + FL - 0.16, FZ, 'y', 0.16, 0.12, cap=FACE_L)
    # BOTH BANDS SIT ON THE TUBE, and that is arithmetic, not judgement. A flat
    # panel at (dx, dz) off the axis is on the body only while dx^2 + dz^2 < r^2:
    # the window line once lay along the 45 deg generatrix — the seam where the
    # crown tone meets the side — and the cockpit patch was at radius 0.207 on a
    # 0.20 body, i.e. off the aeroplane altogether. Both are at 0.8 r now, and
    # the cockpit stops at y -0.92: nearer the nose it slid behind the near cap
    # (the cap plane is y -0.46) and showed only as a chip on the cap's rim.
    s2.append(quad_x(PX + FR * 0.8, -2.02, FZ, 1.0, 0.07, ACCENT))
    s2.append(quad_x(PX + FR * 0.8, -0.92, FZ, 0.18, 0.09, DARK))
    # ON the wing, tangent to it: axis 1.01 puts the barrel's underside at
    # 0.90, which is the wing's own top face — at 0.94 the tube sank 0.07 into
    # the surface it is mounted on. Only the NEAR engine paints here; the far
    # one went in before the fuselage, with its sweep.
    s2 += cyl(PX + 0.52, -1.28, 1.01, 'y', 0.5, 0.11, cap=FACE_L)
    s2 += cyl(PX + 0.52, -0.78, 1.01, 'y', 0.09, 0.045, cap=FACE_L)
    # The fin's leading edge is dz = -1.5 dy: 63.43 deg, the transom's angle on
    # the other lattice axis. Its trailing edge stands ON the tube's end plane,
    # y -2.4 — at -2.42 it hung 0.02 behind the aeroplane.
    s2 += slab_x(PX - 0.05, 0.1,
                 [(-1.8, 1.12), (-2.24, 1.78), (-2.4, 1.78), (-2.4, 1.12)])
    s2 += box(PX - 0.45, -2.5, 1.78, 0.9, 0.3, 0.06)            # the tailplane

    # the excavator, facing +x with its boom over the empty quarter
    EX, EY = -2.7, 1.25
    # Both ramps rise 0.3 over 0.2 — dz = 1.5 dx — so the front one lands on 45
    # deg and the rear, running the other way, on 63.43. The rear was 0.2 over
    # 0.2 for one pass, which is 56.31 and is nobody's angle: the strip it
    # belongs to is hidden, but the near face still draws its edge.
    TRK = [(0.0, Z), (1.05, Z), (1.25, Z + 0.3), (1.25, Z + 0.5),
           (-0.2, Z + 0.5), (-0.2, Z + 0.3)]
    for yy in (EY, EY + 0.5):                                  # crawler frames
        s2 += slab_y(yy, 0.3, [(EX + a, b) for a, b in TRK])
        s2.append(line(p_(EX - 0.12, yy + 0.3, Z + 0.28), p_(EX + 1.17, yy + 0.3, Z + 0.28)))
        s2 += seams((EX, yy + 0.3, Z), (EX + 1.05, yy + 0.3, Z),
                    (EX, yy + 0.3, Z + 0.28), (EX + 1.05, yy + 0.3, Z + 0.28), 4)
    s2 += box(EX + 0.02, EY - 0.05, 0.7, 1.2, 0.9, 0.1)        # slew platform
    # NO SLEW RING. It was drawn on the platform's top face and the house stands
    # on that face, so all that ever showed was a 14 px arc coming out from
    # behind the cab — a curve with nothing to be the edge of. The bearing is
    # under the house, which is where a bearing is.
    s2 += box(EX + 0.02, EY, 0.8, 0.23, 0.8, 0.4)              # counterweight
    # CAB BEFORE HOOD: the cab sits on the far lane (y to EY+0.44) and the hood
    # on the near one (from EY+0.45), so the hood is in front — emitted after
    # the cab, it laps the cab's lower flank the way a desk hides the wall
    # behind it. The other order painted the cab through the hood.
    s2 += box(EX + 0.45, EY + 0.02, 0.8, 0.44, 0.42, 0.6)      # cab
    s2.append(quad_x(EX + 0.89, EY + 0.06, 0.96, 0.34, 0.36, DARK))
    s2.append(quad_y(EY + 0.44, EX + 0.51, 0.96, 0.32, 0.36, DARK))
    s2 += box(EX + 0.28, EY + 0.45, 0.8, 0.72, 0.4, 0.34)      # engine hood
    s2 += seams((EX + 0.28, EY + 0.85, 0.8), (EX + 1.0, EY + 0.85, 0.8),
                (EX + 0.28, EY + 0.85, 1.14), (EX + 1.0, EY + 0.85, 1.14), 3)
    # The boom rises at dz = 1.5 dx and the stick falls at dz = -1.5 dx: 45 deg
    # up, 63.43 deg down. THE BUCKET IS ON THE GROUND, which is a drawing
    # decision and not a pose one: a bucket in the air is a shape hanging off a
    # line, and a bucket with its cutting edge on the apron is the one thing in
    # the yard that says what the machine does.
    s2 += slab_y(EY + 0.34, 0.16,
                 [(EX + 1.15, 0.8), (EX + 1.6, 1.475), (EX + 1.6, 1.675),
                  (EX + 1.15, 1.0)])
    s2 += slab_y(EY + 0.26, 0.3,                               # the bucket
                 [(EX + 2.04, 0.74), (EX + 2.48, 0.74), (EX + 2.48, 0.44),
                  (EX + 2.24, Z), (EX + 2.04, Z)])
    # THE MOUTH IS WHAT MAKES IT A BUCKET. Closed, the shape is a box with one
    # chamfered corner and it read as exactly that — a crate on the end of a
    # stick. Seen from above a bucket is open, and an opening is what ACCENT is
    # for: an aperture of a few square units, never a face.
    s2.append(quad_t(EX + 2.08, EY + 0.3, 0.74, 0.36, 0.22, ACCENT))
    # THE STICK GOES LAST AND GOES IN. Painted before the bucket, it vanished
    # behind the rim and the machine ended at a crate it never touched; the
    # joint has to be SEEN, so the stick paints over the mouth and its tip
    # stops exactly ON the rim plane at x +2.0833 — a tip that dipped below it
    # projected past the rim onto the bucket's near wall, because the stick's
    # lane and the mouth's near edge share y. Still dz = -1.5 dx, tip to heel.
    s2 += slab_y(EY + 0.32, 0.2,
                 [(EX + 1.55, 1.54), (EX + 2.0833, 0.74), (EX + 2.0833, 0.94),
                  (EX + 1.55, 1.74)])

    # ---- 3 · the semi, nearest the reader
    #
    # THE COUPLING IS A LAP, NOT A GAP. The deck's front rests ON the chassis —
    # bottom flush with the chassis top, 0.12 of overlap — because a trailer
    # rests on its tractor; the shipped version held a 0.02 air gap with the
    # chassis top ABOVE the deck bottom, a trailer nothing could have coupled
    # to. The chassis flank stays 0.02 behind the wheel plane, and the wheels —
    # the near flank itself — are painted last, so no frame edge ever bites a
    # tyre: the train's solebar rule, applied to the road.
    TY = 1.4
    s3 += box(2.2, TY + 0.04, 0.38, 0.74, 0.48, 0.14)          # tractor chassis
    s3 += box(0.58, TY, 0.52, 1.74, 0.58, 0.1)                 # trailer deck
    s3 += container(0.66, TY + 0.07, 0.62)
    # 0.34 within the trailer's pair against a 0.30 tyre — the train's spacing
    # rule; at 0.30 the two tyres are tangent and read as one blob. BEFORE the
    # cab: the cab's near face is 0.04 nearer than the wheel plane, so the front
    # wheel half-hides behind it the way a cabover's wheel sits under its door —
    # painted after the cab, the tyre lay ON the door instead.
    for xx in (0.86, 1.2, 2.28, 2.8):
        s3 += wheelset(xx, TY + 0.54, 0.35, 0.15)
    s3 += box(2.32, TY + 0.02, 0.52, 0.6, 0.56, 0.62)          # cab
    s3.append(quad_x(2.92, TY + 0.07, 0.8, 0.46, 0.24, DARK))
    s3.append(quad_y(TY + 0.58, 2.42, 0.8, 0.32, 0.22, DARK))
    s3.append(line(p_(2.32, TY + 0.58, 0.72), p_(2.92, TY + 0.58, 0.72)))

    # THE CROP IS TAKEN HERE, before the ghost and the trace, for the reason
    # isolib.bbox() exists: a ghost is what is not there yet and a trace comes
    # in from off-stage, so both sit outside what the drawing is OF. Let the
    # frame grow to hold them and the trace no longer enters from anywhere.
    crop = bbox(30.0)

    # A GHOST IS THE NEXT TIER. The stack is four boxes and the fleet is however
    # many the operator runs, so the row that is loaded continues as the row that
    # is not: the same container, twice more, dashed, over the two below it.
    ghost = []
    for yy in (STK_Y, STK_Y + CT_W):
        ghost += box(STK_X, yy, DECK + 2 * CT_H, CT_L, CT_W, CT_H,
                     'none', 'none', 'none')

    # TWO SWEPT CIRCLES, and they are the reason the aircraft is an aircraft.
    # The system's own distinction is that a swept circle is a path something
    # travels rather than a state, which is exactly what a propeller disc is —
    # and at 40 px a drawn blade would be three edges on angles this projection
    # does not own. 03's rotor is the same argument on a different machine.
    # r 0.30, from the clearance and not from taste: the sweep's inboard edge
    # reaches offset - r, and at 0.38 that was 0.14 — inside the 0.20 tube, a
    # propeller striking its own fuselage, with the far arc's dots landing on
    # the nose drum in front of it.
    # Only the NEAR sweep rides the top layer — the far one is drawn into the
    # aircraft's own stage, before the fuselage, which then occludes the arc
    # that passes behind it. A full ellipse over everything put dashed specks
    # on the nose drum standing in front of the far propeller.
    orbits = [orbit(PX + 0.52, -0.76, 1.01, 0.3, 'y')]

    # The lit box is one of the four on the ship and the near one of the upper
    # tier: it is surrounded by its own repetitions, which is the only place in
    # the drawing where "what stands out on one unit" has anything to stand out
    # from.
    LC = (STK_X, STK_Y + CT_W, DECK + 2 * CT_H)
    light = light_quad(gid, [(LC[0], LC[1], LC[2]), (LC[0] + CT_L, LC[1], LC[2]),
                             (LC[0] + CT_L, LC[1] + CT_W, LC[2]),
                             (LC[0], LC[1] + CT_W, LC[2])])
    la, lb = lime_span((LC[0], LC[1], LC[2]),
                       (LC[0] + CT_L, LC[1] + CT_W, LC[2]), 2.2)
    nodes = [node(LC[0] + CT_L / 2, LC[1] + CT_W / 2, LC[2]),
             node(PX, TAIL + FL, FZ, 3), node(EX + 0.67, EY + 0.23, 1.4, 3),
             node(1.21, TY + 0.29, 1.1, 3)]
    # The trace comes in on -y, over the one empty quarter of the sky, and lands
    # on the lit box. It leaves through the TOP of the frame rather than the
    # side — this stack is the highest thing in the yard — which is what
    # isolib.trace_from() exists to measure; the x-only expression 01 uses
    # returned 1.903 here. y = -4.3 puts an eighth of the line off-stage, enough
    # to arrive from somewhere and not enough to spend the step's scroll on a
    # line nobody can see.
    ta = (LC[0] + CT_L / 2, -4.3, LC[2])
    tb = (LC[0] + CT_L / 2, LC[1] + CT_W / 2, LC[2])
    traces = [trace(ta, tb, frm=trace_from(ta, tb, crop))]
    return assemble(gid, la, lb, [(0, s0), (1, s1), (2, s2), (3, s3)],
                    light, nodes, traces, ghost, orbits, crop=crop)


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    for name, fn in (('01-maschinenbau', maschinenbau), ('02-anlagen', anlagen),
                     ('03-erneuerbare', erneuerbare), ('04-flotten', flotten)):
        out = fn()
        open(os.path.join(here, name + '.svg'), 'w').write(out + '\n')
        n = out.count('<path') + out.count('<ellipse') + out.count('<circle') + out.count('<line')
        vb = out[out.index('viewBox="') + 9:]
        print(f'{name}: {n} elements, viewBox {vb[:vb.index(chr(34))]}')
