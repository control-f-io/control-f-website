"""The four expertise objects, v3.

STAGES ARE DEPTH BANDS, BACK TO FRONT — not "big things, then small things".
The build animation reads data-stage, and a stage is a <g>, so everything in
stage 2 paints over everything in stage 1 no matter what order it was written
in. Ordering the stages by depth is therefore the only assignment that is
correct as a drawing AND as a build: the object comes forward out of its own
foundation, and a hairline never surfaces through the mass in front of it.

EVERY ROW RUNS ON A LATTICE AXIS. The fleet's first draft put its four units
across the screen, on the (1,-1) diagonal, and its track came out as two long
horizontal rules and a row of vertical ties — the only two directions in the
drawing that are NOT brand angles. Running the same row down +x instead makes
the rails, the ties, the line the units report to and the row itself all
26.57 deg, and gives the four machines real depth overlap into the bargain.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from isolib import (  # noqa: E402
    p_, line, box, plate, quad_t, quad_x, quad_y, seams,
    disc, hoop, cyl, taper, node, orbit, trace, light_quad, light_disc,
    assemble, bbox, lime_span_disc, reset,
    FACE_TOP, FACE_L, FACE_R, PLATE_L, PLATE_R,
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
    xa, xb = p_(*ta)[0], p_(*tb)[0]
    traces = [trace(ta, tb, frm=round(1.0 - (xa - (crop[0] + crop[2])) / (xa - xb), 3))]
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
    s2 += cyl(-0.62, -0.7, 2.51, 'x', 3.14, 0.17, side=FACE_L, cap=None)   # process line
    for i in range(4):
        s2.append(hoop(-0.15 + i * 0.72, -0.7, 2.51, 0.17, 'x'))
    s2 += cyl(-0.62, -0.32, 2.45, 'x', 3.14, 0.11, side=FACE_R, cap=None)  # utility line
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
def erneuerbare():
    """Generation, conversion, storage, on one pad — the three things whose
    telemetry only means anything read against each other. The rotor is drawn
    as a swept circle rather than as blades: it is a future state, and the
    system already has a way of saying that."""
    reset()
    gid = 'cf-ex-03'
    s0, s1, s2, s3 = [], [], [], []

    s0 += foundation(-2.9, -2.4, 5.8, 4.8, 0.2, 0.2, 2, 1)

    # ---- 1 · the turbine, furthest back
    wx, wy = -1.95, -1.75
    s1 += cyl(wx, wy, 0.2, 'z', 0.16, 0.36, side=PLATE_R)      # foundation
    s1 += taper(wx, wy, 0.36, 0.19, 0.12, 2.5, None, FACE_R)
    for zz in (1.1, 1.9):
        s1.append(hoop(wx, wy, zz, 0.19 - (zz - 0.36) / 2.5 * 0.07, 'z'))
    s1 += box(wx - 0.13, wy - 0.13, 2.86, 0.55, 0.26, 0.24)    # nacelle
    s1.append(disc(wx - 0.13, wy, 2.98, 0.13, 'x', FACE_TOP))  # hub, on the sweep's axis

    # ---- 2 · the transformer bay and the electrolyser, middle
    s2 += box(-1.05, -1.55, 0.2, 1.35, 1.05, 0.18, FACE_TOP, PLATE_L, PLATE_R)
    s2 += box(-0.9, -1.4, 0.38, 1.05, 0.75, 0.62)              # transformer
    s2 += seams((-0.9, -0.65, 0.38), (0.15, -0.65, 0.38),      # radiator fins
                (-0.9, -0.65, 1.0), (0.15, -0.65, 1.0), 5)
    for xx in (-0.7, -0.4, -0.1):                              # bushings
        s2 += cyl(xx, -1.05, 1.0, 'z', 0.26, 0.07, side=FACE_L)

    s2 += box(0.6, -1.85, 0.2, 1.9, 0.95, 0.26, FACE_TOP, PLATE_L, PLATE_R)
    for xx in (0.95, 1.55, 2.15):
        s2 += cyl(xx, -1.38, 0.46, 'z', 0.14, 0.31, side=PLATE_R)   # base flange
        s2 += cyl(xx, -1.38, 0.6, 'z', 1.02, 0.26)
        for zz in (0.85, 1.2, 1.55):
            s2.append(hoop(xx, -1.38, zz, 0.26, 'z'))
    s2 += box(0.75, -1.53, 1.62, 1.6, 0.3, 0.16)               # header
    s2 += seams((0.75, -1.23, 1.62), (2.35, -1.23, 1.62),
                (0.75, -1.23, 1.78), (2.35, -1.23, 1.78), 3)

    # ---- 3 · the bank and the array, nearest
    s3 += box(-2.6, 0.9, 0.2, 2.8, 1.1, 1.05)                  # battery container
    s3 += seams((-2.6, 2.0, 0.2), (0.2, 2.0, 0.2),             # door leaves
                (-2.6, 2.0, 1.25), (0.2, 2.0, 1.25), 7)
    s3.append(line(p_(-2.6, 2.0, 1.12), p_(0.2, 2.0, 1.12)))   # cant rail
    s3.append(line(p_(-2.6, 2.0, 0.32), p_(0.2, 2.0, 0.32)))
    s3.append(quad_y(2.0, -2.42, 0.45, 0.3, 0.5, DARK))        # louvres
    s3.append(quad_y(2.0, -0.12, 0.45, 0.3, 0.5, DARK))
    s3 += seams((-2.6, 0.9, 1.25), (0.2, 0.9, 1.25),
                (-2.6, 2.0, 1.25), (0.2, 2.0, 1.25), 3)
    for xx in (-2.15, -0.85):                                  # roof plant
        s3 += box(xx, 1.2, 1.25, 0.5, 0.5, 0.22)
    s3.append(quad_x(0.2, 1.02, 0.32, 0.86, 0.81))             # end frame
    s3 += seams((0.2, 1.02, 0.32), (0.2, 1.02, 1.13),
                (0.2, 1.88, 0.32), (0.2, 1.88, 1.13), 2)

    s3 += box(0.55, 0.75, 0.2, 2.1, 1.5, 0.14, FACE_TOP, PLATE_L, PLATE_R)   # array
    s3.append(quad_t(0.67, 0.87, 0.34, 1.86, 1.26))
    s3.append(quad_t(1.13, 0.87, 0.34, 0.46, 0.63, ACCENT))    # one string, in shade
    s3 += seams((0.67, 0.87, 0.34), (2.53, 0.87, 0.34),
                (0.67, 2.13, 0.34), (2.53, 2.13, 0.34), 3)
    s3 += seams((0.67, 0.87, 0.34), (0.67, 2.13, 0.34),
                (2.53, 0.87, 0.34), (2.53, 2.13, 0.34), 1)

    ghost = []
    orbits = [orbit(wx - 0.13, wy, 2.98, 0.88, 'x')]           # the sweep, turning
    light = light_quad(gid, [(-1.72, 2.0, 0.45), (-1.32, 2.0, 0.45),
                             (-1.32, 2.0, 1.07), (-1.72, 2.0, 1.07)])
    la, lb = lime_span((-1.72, 2.0, 1.07), (-1.32, 2.0, 0.45))
    nodes = [node(-1.52, 2.0, 0.76), node(1.55, -1.38, 1.78, 3), node(wx - 0.13, wy, 2.98, 3)]
    traces = [trace((-4.3, -0.3, 0.2), (-2.9, -0.3, 0.2))]
    return assemble(gid, la, lb, [(0, s0), (1, s1), (2, s2), (3, s3)],
                    light, nodes, traces, ghost, orbits)


# ==================================================================== 04
def flotten():
    """Four identical units on one track, and a fifth at each end that the
    frame does not reach. A fleet is a repetition, so the drawing is one: the
    same machine four times, on the same rails, on the same line. The row runs
    down +x, so the row, the rails, the ties and the line they report to are
    all the same 26.57 deg — and the units overlap, which is what makes four
    of a thing read as depth instead of as a strip of stickers."""
    reset()
    gid = 'cf-ex-04'
    s0, s1, s2, s3 = [], [], [], []
    X = (-2.4, -0.8, 0.8, 2.4)

    s0 += foundation(-3.8, -1.25, 7.6, 2.5, 0.2, 0.2, 0, 1)
    for i in range(13):                                        # ties
        s0.append(line(p_(-3.36 + i * 0.56, -0.72, 0.2), p_(-3.36 + i * 0.56, 0.72, 0.2)))
    for yy in (-0.52, 0.44):                                   # rails
        s0 += box(-3.5, yy, 0.2, 7.0, 0.08, 0.06, FACE_TOP, PLATE_L, PLATE_R)

    # ---- 1 · running gear
    for x in X:
        for d in (-0.36, 0.36):
            s1.append(disc(x + d, 0.48, 0.5, 0.24, 'y', ACCENT))
            s1.append(disc(x + d, 0.48, 0.5, 0.08, 'y', FACE_TOP))
        s1 += box(x - 0.62, -0.42, 0.5, 1.24, 0.84, 0.14, FACE_TOP, PLATE_L, PLATE_R)

    # ---- 2 · the machine
    for x in X:
        s2 += box(x - 0.56, -0.36, 0.64, 1.12, 0.72, 0.66)
        s2 += seams((x - 0.56, 0.36, 0.64), (x + 0.56, 0.36, 0.64),
                    (x - 0.56, 0.36, 1.3), (x + 0.56, 0.36, 1.3), 3)
        s2.append(quad_y(0.36, x - 0.44, 0.92, 0.42, 0.26, DARK))
        s2.append(line(p_(x - 0.56, 0.36, 0.78), p_(x + 0.56, 0.36, 0.78)))
        s2.append(quad_x(x + 0.56, -0.24, 0.8, 0.48, 0.3, FACE_TOP))
        s2.append(quad_x(x + 0.56, -0.14, 0.9, 0.28, 0.14, ACCENT))

    # ---- 3 · roof, mast, and the one that is lit
    for i, x in enumerate(X):
        s3 += box(x - 0.46, -0.3, 1.3, 0.92, 0.6, 0.14,
                  None if i == 2 else FACE_TOP, FACE_L, FACE_R)
        s3.append(quad_t(x - 0.34, -0.2, 1.44, 0.68, 0.4))
        s3 += box(x - 0.05, -0.05, 1.44, 0.1, 0.1, 0.5, FACE_TOP, PLATE_L, PLATE_R)

    ghost = []
    for x in (-3.5, 3.5):
        ghost += box(x - 0.56, -0.36, 0.64, 1.12, 0.72, 0.66, 'none', 'none', 'none')
        ghost += box(x - 0.62, -0.42, 0.5, 1.24, 0.84, 0.14, 'none', 'none', 'none')

    light = light_quad(gid, [(0.34, -0.3, 1.44), (1.26, -0.3, 1.44),
                             (1.26, 0.3, 1.44), (0.34, 0.3, 1.44)])
    la, lb = lime_span((0.34, -0.3, 1.44), (1.26, 0.3, 1.44), 2.2)
    nodes = [node(x, 0.0, 1.94, 4 if x == 0.8 else 3) for x in X]
    traces = [trace((-3.6, 0.0, 1.94), (3.6, 0.0, 1.94))]
    return assemble(gid, la, lb, [(0, s0), (1, s1), (2, s2), (3, s3)],
                    light, nodes, traces, ghost)


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    for name, fn in (('01-maschinenbau', maschinenbau), ('02-anlagen', anlagen),
                     ('03-erneuerbare', erneuerbare), ('04-flotten', flotten)):
        out = fn()
        open(os.path.join(here, name + '.svg'), 'w').write(out + '\n')
        n = out.count('<path') + out.count('<ellipse') + out.count('<circle') + out.count('<line')
        vb = out[out.index('viewBox="') + 9:]
        print(f'{name}: {n} elements, viewBox {vb[:vb.index(chr(34))]}')
