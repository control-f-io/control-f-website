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
    disc, hoop, cyl, cone, wheel, taper, orbit, rotor, light_quad, light_disc,
    light_nodes_quad, light_nodes_disc, lime_span_quad, lime_span_disc,
    assemble, bbox, reset,
    FACE_TOP, FACE_L, FACE_R, PLATE_TOP, PLATE_L, PLATE_R,
    ACCENT, DARK,
)

# THE LIGHT IS A TOP FACE WITH TWO NODES ON IT, and the nodes are nowhere else.
# The reference plates of 2026-09-01 light one face per object — the top of the
# mass the eye is meant to land on — run the whole ramp inside it, lime at the
# back corner to CF-Grau at the near one, and mark exactly two points: where
# the lit face's far edges meet, and where its right edge turns the corner.
# The four objects used to scatter three or four nodes over places the copy
# named (an exhaust outlet, a header, a cab roof), which is a list and not a
# construction. isolib.light_nodes_quad / _disc take the two points off the lit
# element itself, so they cannot drift from it.


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
    apron. The frame is then the bounding box plus 18, taken before the nodes
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
    beams and the floor they run on are all on one angle. A row laid across
    the screen would have put the whole thing on the
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

    # THE CROP IS TAKEN HERE, before the nodes, and isolib.bbox() exists rather
    # than assemble()'s own default so that it can be taken early at all. It
    # was taken here for the trace that used to arrive from off-stage: that
    # line registered both its endpoints and would otherwise have pulled the
    # right edge out to hold the half of itself that was drawn to be cut. The
    # traces came out of all four objects on 2026-08-26 and the call stays
    # where it was, because moving it now would recrop a drawing nobody asked
    # to recompose. Everything else about the crop is the other three objects' —
    # extent plus a pad, no authored window, nothing outside it.
    #
    # THE HEIGHT IS NOT UNDER THE COLUMN'S CONSTRAINT. Only the WIDTH is read
    # against it; the height follows through `height: auto`, and the row is
    # 541 px tall at 1440x900 because the copy card sets it. So the height is
    # simply what the drawing asks for — 464.4 units, 398 px — and no number
    # here is rationing it.
    crop = bbox(18.0)
    # Two nodes, on the lit disc's highest and rightmost points — see the note
    # at the top of this file. There were three, on the shaft end, the exhaust
    # outlet and the terminals: places the copy names, not points the light
    # depends on.
    nodes = light_nodes_disc(1.75, 0.0, AXIS, 0.46, 'x')
    return assemble(gid, la, lb, [(0, s0), (1, s1), (2, s2), (3, s3)],
                    light, nodes, ghost, orbits, crop=crop)


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
    #
    # THE COLUMN'S TOP IS THE LIGHT, and it is a flat head for that reason. The
    # lit element used to be the top nozzle on a tapered head — a disc of r 0.22,
    # 17 units across, the smallest lit element in the four objects and the one
    # thing here the reference plates would not draw: they light the top face
    # of the mass the eye lands on, and here that is the tallest vessel on the
    # plot. The storage tank would have been the other candidate and is not:
    # the rack's near column stands in front of its top from this camera, and
    # the light paints after every form, so a lit tank top would have painted
    # itself over a member that is nearer than it is. Nothing is in front of
    # the column head at z 3.5.
    cx, cy, cr = -1.75, -1.2, 0.44
    s1 += cyl(cx, cy, 0.2, 'z', 0.3, 0.6, side=PLATE_R)        # skirt
    s1 += cyl(cx, cy, 0.5, 'z', 3.0, cr)
    for zz in (1.35, 2.45):                                    # shell courses
        s1.append(hoop(cx, cy, zz, cr, 'z'))
    fx, fy = cx + cr * 0.707, cy + cr * 0.707                  # the front generatrix
    for o in (0.17, -0.17):                                    # ladder stiles
        s1.append(line(p_(fx + o, fy - o, 0.62), p_(fx + o, fy - o, 3.3)))
    for i in range(8):
        zz = 0.78 + i * 0.34
        s1.append(line(p_(fx + 0.17, fy - 0.17, zz), p_(fx - 0.17, fy + 0.17, zz)))

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
    s2 += cyl(-2.35, 1.05, 0.62, 'x', 0.72, 0.24)                           # motor
    for i in range(3):
        s2.append(hoop(-2.19 + i * 0.2, 1.05, 0.62, 0.24, 'x'))
    # ON THE MOTOR'S AXIS AND ON THE PLINTH. A coupled pump shares its motor's
    # shaft line; this one sat 0.02 below it, at 0.60, with a radius of 0.30 —
    # so its underside was at 0.30 against a plinth top of 0.38, the casing
    # sunk 0.08 into the block it stands on, and the two axes missed by a
    # pixel. Same axis, same radius, and the discharge nozzle starts at the
    # crown it now has.
    s2 += cyl(-1.5, 1.05, 0.62, 'x', 0.38, 0.24)                            # pump
    s2 += cyl(-1.3, 1.05, 0.86, 'z', 0.3, 0.1, side=FACE_L)

    # ---- 3 · the exchangers, nearest the reader
    for yy in (0.6, 1.6):
        for xx in (0.5, 1.8):                                  # saddles
            s3 += box(xx, yy - 0.2, 0.2, 0.3, 0.4, 0.33, FACE_TOP, PLATE_L, PLATE_R)
        s3 += cyl(0.3, yy, 0.85, 'x', 2.1, 0.32, side=FACE_R, cap_far=FACE_L)
        for i in range(4):
            s3.append(hoop(0.62 + i * 0.42, yy, 0.85, 0.32, 'x'))
        # disc(), not hoop(): the channel cover's bolt circle lies IN the end
        # face and is wholly visible. maschinenbau() made exactly this
        # correction on its end cover and wrote down why — drawn as a hoop the
        # circle is an open crescent with two dangling ends — and these two
        # kept the hoop.
        s3.append(disc(2.4, yy, 0.85, 0.24, 'x'))
        s3 += cyl(0.72, yy, 1.17, 'z', 0.3, 0.09, side=FACE_L)  # nozzles
        s3 += cyl(2.02, yy, 1.17, 'z', 0.3, 0.09, side=FACE_L)

    ghost = [disc(tx, ty, 1.15, 0.6, 'z'),          # the level in the tank
             disc(cx, cy, 1.9, cr * 0.76, 'z')]     # a tray in the column
    light = light_disc(gid, cx, cy, 3.5, cr, 'z')
    la, lb = lime_span_disc(cx, cy, 3.5, cr, 'z')
    nodes = light_nodes_disc(cx, cy, 3.5, cr, 'z')
    return assemble(gid, la, lb, [(0, s0), (1, s1), (2, s2), (3, s3)],
                    light, nodes, ghost)


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
    # THE ROOF IS THE LIGHT, AND A LIT FACE IS CLEAN. The container's top is
    # the largest sky-facing face on the pad and the one the reference plates
    # would light; it used to carry three roof seams and two units of roof
    # plant, and the light was one door leaf on the +y flank — a vertical face,
    # lit from the side, which is the one thing "the light comes from above"
    # rules out. The seams and the plant come off with the move: a ramp with a
    # box standing in it is a ramp with a hole in it.
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
    # No shaded string any more. It was one cell of the grid below in the
    # accent value, and in a register where the accent IS the shaded side it
    # would be a second thing standing out on a pad that has one light.
    s3 += seams((fx, fy, 0.34), (fx + fw, fy, 0.34),
                (fx, fy + fh, 0.34), (fx + fw, fy + fh, 0.34), 3)
    s3 += seams((fx, fy, 0.34), (fx, fy + fh, 0.34),
                (fx + fw, fy, 0.34), (fx + fw, fy + fh, 0.34), 1)

    ghost = []
    orbits = [orbit(hx, wy, hz, 0.88, 'x')]                    # the sweep the tips travel
    roof = [(-2.6, 0.9, 1.25), (0.2, 0.9, 1.25), (0.2, 2.0, 1.25), (-2.6, 2.0, 1.25)]
    light = light_quad(gid, roof)
    la, lb = lime_span_quad(roof)
    nodes = light_nodes_quad(roof)
    return assemble(gid, la, lb, [(0, s0), (1, s1), (2, s2), (3, s3)],
                    light, nodes, ghost, orbits)


# ==================================================================== 04
# THE ONE BOX, drawn six times and ghosted twice. A fleet is a repetition, and
# the asset classes this field names do not repeat each other; what repeats
# across them is the load. So the container is a function rather than a shape:
# the same 1.1 x 0.44 x 0.48 body, the same corrugations, the same door seam,
# four of them stacked on the ship, one on the rail wagon, one on the semi's
# trailer. It is also the unit the reader measures the yard with — every other
# dimension in this object was chosen against it.
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


def flotten():
    """A yard with one of everything on it: a ship on its blocks, an aircraft,
    a train, a semi and an excavator, and the same container on three of them.
    Redrawn from scratch on 2026-09-01, machine by machine, after the second
    pass at it still read wrong in the details — an aircraft whose parts did
    not line up on its own centre line, wheels that read as washers, a tractor
    on three axles.

    WHAT HOLDS IT TOGETHER is the container, drawn six times: four in one
    stack on the ship, one on the wagon, one on the trailer. That is the
    repetition the copy is about — what shows on one unit can be checked on
    all the others — and it is what makes five different machines one fleet.
    THE LIT BOX IS ONE OF THE FOUR IN THE STACK, the only place in the drawing
    where standing out means anything.

    THE LAYOUT IS FIVE LANES THAT DO NOT CROSS ON SCREEN. Everything runs on a
    lattice axis — ship, train, semi and excavator down +x, the aircraft down
    +y — and each machine has its own patch of apron: the ship on the back
    edge, the aircraft on the right, the train on a short siding through the
    middle, the excavator in the left corner, the semi across the front. The
    siding stops at x 1.4 so the train never runs under the aircraft's nose,
    and starts at -2.55 so the loco never stands where the excavator's boom is
    drawn; both were true of the first yard, whose track crossed the whole
    apron and put its loco behind the boom. Stages are depth bands: 1 ship and
    aircraft, 2 train and excavator, 3 the semi.

    EVERY MACHINE IS SYMMETRIC ABOUT ITS OWN AXIS AND SAYS SO. The aircraft's
    wing, tailplane, engines and undercarriage are placed by +- offsets from
    PX, never by two literals that were once equal; the train's bogies are
    placed about each vehicle's centre; the semi's axles sit where its loads
    are. A drawing at this size has no room for a part that is nearly where
    it should be.

    THE RAKES ARE THE CHARACTER LINES and each is one of the three ratios the
    lattice admits: in a vertical plane a step (dx, dz) lands on screen slope
    0.5 - dz/dx, so dz/dx of 1, 1.5 and 2.5 give 26.57, 45 and 63.43 deg and
    nothing else does. The stem, the crawler's front ramp and the boom are at
    45; the transom, the rear ramp, the stick and the fin's leading edge at
    63.43.

    THE PLATE IS 5.9 x 4.7 and that is a width decision: the figure renders at
    --vb-w / 112 x --field-unit so that one cell of the drawing is one cell of
    the ground, and the column holds about 668 units — maschinenbau() derives
    that number. 10.6 cells plus two pads is 653.6, the whole budget.
    """
    reset()
    gid = 'cf-ex-04'
    s0, s1, s2, s3 = [], [], [], []
    Z = 0.2                                                    # the apron's top

    # ---- 0 · the apron, and a siding through the middle of it
    s0 += foundation(-2.95, -2.35, 5.9, 4.7, Z, 0.26, 0, 0)
    RY = 0.2                                                   # the siding's centre line
    # Ties only where there is track, and track only where there is train:
    # thirteen ties across the whole apron were the busiest thing on it.
    for i in range(9):
        xx = -2.45 + i * 0.44
        s0.append(line(p_(xx, RY - 0.36, Z), p_(xx, RY + 0.36, Z)))
    for yy in (RY - 0.2, RY + 0.2):                            # rails, 0.4 gauge,
        s0 += box(-2.55, yy - 0.03, Z, 3.95, 0.06, 0.05,       # centred on the
                  FACE_TOP, PLATE_L, PLATE_R)                  # gauge lines

    # ---- 1 · the back band: the ship on its blocks, and the aircraft
    #
    # THE SHIP IS ON KEEL BLOCKS, not floating in a plate: everything else here
    # stands on the apron on its own running gear, and a hull resting straight
    # on concrete is the one thing in the yard that could not have got there.
    # Both ends are raked, which is the whole difference between a ship and a
    # barge with a house on it: the stem rises 0.6 over 0.4 (45 deg) and the
    # transom 0.45 over 0.3 (63.43).
    SY, BEAM = -2.3, 1.0
    KEEL, DECK = 0.42, 1.02
    NF = SY + BEAM                                             # the near flank
    for xx in (-2.5, -1.7, -0.9):                              # keel blocks
        s1 += box(xx, SY + 0.22, Z, 0.2, 0.78, KEEL - Z, FACE_TOP, PLATE_L, PLATE_R)
    # ONE HULL, THREE FACES: the near flank carrying both rakes in one polygon,
    # the stem plate, and one deck rectangle, because both rakes end AT deck
    # level. The small vertical at the transom's foot is the skeg.
    s1.append(face(poly([p_(-2.9, NF, DECK), p_(-2.6, NF, 0.57), p_(-2.6, NF, KEEL),
                         p_(-0.7, NF, KEEL), p_(-0.3, NF, DECK)]), FACE_L))
    s1.append(face(poly([p_(-0.7, SY, KEEL), p_(-0.3, SY, DECK),
                         p_(-0.3, NF, DECK), p_(-0.7, NF, KEEL)]), FACE_R))
    s1.append(quad_t(-2.9, SY, DECK, 2.6, BEAM, FACE_TOP))     # the deck
    # The boot top's forward end lands ON the stem rake at its own height.
    s1.append(line(p_(-2.6, NF, 0.56), p_(-0.7 + (0.56 - KEEL) / 1.5, NF, 0.56)))
    s1.append(quad_t(-2.8, SY + 0.06, DECK, 2.42, BEAM - 0.12))  # bulwark
    # The deckhouse comes before the load, because the load is nearer; its
    # window is on the bridge's near flank, the only face of it this camera
    # sees past the stack. Forward of the transom, so it stands on the deck
    # and not on the rake.
    s1 += box(-2.55, SY + 0.16, DECK, 0.56, 0.68, 0.4)         # accommodation
    s1 += box(-2.47, SY + 0.24, DECK + 0.4, 0.4, 0.52, 0.26)   # bridge
    s1.append(quad_y(SY + 0.76, -2.4, DECK + 0.5, 0.26, 0.13, DARK))
    s1 += box(-2.37, SY + 0.32, DECK + 0.66, 0.18, 0.26, 0.24)  # funnel
    STK_X, STK_Y = -1.85, SY + 0.06                            # the stack: 2 x 2
    for tier in (DECK, DECK + CT_H):
        s1 += container(STK_X, STK_Y, tier)
        s1 += container(STK_X, STK_Y + CT_W, tier)
    # The yard in two arms, split at the mast: one line through would paint
    # its far half over the body it passes behind.
    s1.append(line(p_(-0.62, SY + 0.34, DECK + 0.54), p_(-0.62, SY + 0.46, DECK + 0.54)))
    s1 += box(-0.66, SY + 0.46, DECK, 0.08, 0.08, 0.72)        # mast
    s1.append(line(p_(-0.62, SY + 0.54, DECK + 0.54), p_(-0.62, SY + 0.66, DECK + 0.54)))

    # THE AIRCRAFT, down +y with its nose at the yard, and this time drawn the
    # way a turboprop is built: A HIGH WING. A low wing is hidden at the root
    # by the fuselage that bulges over it, so it arrived on screen as two
    # slabs at two heights with nothing between them; a high wing lies OVER
    # the barrel as one slab, its centre line on the fuselage's own, and the
    # engines hang under it either side, both of them wholly visible. A T-TAIL
    # for the same reason: a stabiliser on the cone had its far half behind
    # the barrel, and one on the fin's tip is one slab in the open, centred
    # on the fin. THE FUSELAGE IS A BARREL WITH A CONE AT EACH END
    # (isolib.cone), not a drum with a cap pointed at the reader.
    #
    # THE UNDERCARRIAGE IS TWO LEGS ON THE CENTRE LINE, a wheel either side of
    # each. From this camera a point under the far side of a y-barrel projects
    # INTO the barrel's band — moving it outboard moves it toward the axis on
    # screen, not away — so a wheel under each wing showed one wheel and a
    # chip. Under the belly, both main wheels are 10 units clear of the lower
    # silhouette. The main pair sits just aft of the wing, where an ATR's does,
    # and that is also what keeps it out from under the nacelle on screen; the
    # nose pair sits under the barrel ahead of the wing, in the open.
    PX, TAIL = 1.9, -2.3
    FZ, FR = 0.9, 0.22
    # tail cone -2.3 .. -1.85, barrel -1.85 .. -0.5, nose cone -0.5 .. -0.1.
    # PX + 1.0, the wing tip, is inside the apron's edge at 2.95.
    s1 += wheel(PX - 0.05, -1.65, 0.34, 0.14, 0.1, 'x')        # main pair, far
    s1 += box(PX - 0.05, -1.7, 0.34, 0.1, 0.1, 0.34)           # main leg, axle to belly
    s1 += wheel(PX + 0.15, -1.65, 0.34, 0.14, 0.1, 'x')        # main pair, near
    # ONE NOSE WHEEL, CENTRED ON A FORK. The nose leg carried a pair like the
    # main gear, and at 8 px the two wheels and the leg between them fused
    # into one lump with a bite out of it. A single wheel astride the leg is
    # one clean disc; the leg paints first, so the wheel's face covers its
    # lower half and the leg is seen coming out of the top of the tyre.
    s1 += box(PX - 0.03, -0.43, 0.33, 0.06, 0.06, 0.35)        # nose leg
    s1 += wheel(PX + 0.05, -0.4, 0.33, 0.13, 0.1, 'x')         # nose wheel, astride it
    s1 += cone(PX, TAIL, FZ, 'y', 0.45, 0.06, FR, cap=None)    # tail cone
    # crown=False: the barrel's lit band ends in a seam a quarter-turn right
    # of the top, and neither cone carries one, so the fin on the true top
    # read as standing beside the ridge. One tone, like the cones.
    s1 += cyl(PX, TAIL + 0.45, FZ, 'y', 1.35, FR, cap=FACE_L, cap_far=FACE_L, crown=False)
    s1 += cone(PX, TAIL + 1.8, FZ, 'y', 0.4, FR, 0.05, far=False)   # nose cone
    # The cockpit glazing at 0.8 r, on the body, the one panel on the tube.
    s1.append(quad_x(PX + FR * 0.8, -0.72, FZ + 0.02, 0.18, 0.09, DARK))
    # The fin's leading edge is dz = 1.5 dy, 63.43 deg. Its root at 1.08 is
    # inside the barrel's crown (1.12) and, at its trailing edge on the first
    # section of the tail cone, inside that (1.084). Aft of the wing's
    # trailing edge at -1.5, so the two never share a cell.
    s1 += slab_x(PX - 0.04, 0.08,
                 [(-1.55, 1.08), (-1.83, 1.5), (-1.95, 1.5), (-1.95, 1.08)])
    s1 += box(PX - 0.45, -2.0, 1.5, 0.9, 0.22, 0.05)           # the T-tail, on the fin
    # Nacelles under the wing, far first, each standing 0.1 proud of the
    # leading edge; the wing goes over both, and over the barrel.
    for ex in (PX - 0.55, PX + 0.55):
        s1 += cyl(ex, -1.5, 0.98, 'y', 0.65, 0.12)
        s1 += cyl(ex, -0.85, 0.98, 'y', 0.1, 0.05)             # spinner
    # Seated into the barrel's crown, not resting on it: at 1.08 the slab
    # floated a hair over the body and read as a plank laid across it. And
    # THIN: 0.06 on a 0.5 chord, where 0.1 on 0.55 was an 18 % section that
    # read as a board.
    s1 += box(PX - 1.0, -1.5, 1.06, 2.0, 0.5, 0.06)            # the wing

    # ---- 2 · the middle band: the train on its siding, the excavator in the corner
    #
    # A loco and one flat wagon. THE SOLEBAR CLEARS THE WHEEL by 0.03: frames at
    # 0.58 over a wheel whose crown is 0.55. Two bogies each, 0.32 within a
    # pair against a 0.30 wheel, placed about each vehicle's own centre; and
    # every open end carries a headstock down to the axle line, because the
    # end of a frame over daylight is the highest-contrast thing in the region.
    RW = 0.7
    for xx in (-2.08, -1.76, -1.09, -0.77, -0.18, 0.14, 0.66, 0.98):
        s2 += wheel(xx, RY + 0.24, 0.4, 0.15, 0.06)
    for xx in (-2.3, -0.65):                                   # loco headstocks
        s2 += box(xx, RY - 0.3, 0.46, 0.1, 0.6, 0.12)
    s2 += box(-2.3, RY - RW / 2, 0.58, 1.75, RW, 0.12)         # loco underframe
    s2 += box(-2.2, RY - 0.28, 0.7, 1.05, 0.56, 0.46)          # long hood
    s2 += seams((-2.2, RY + 0.28, 0.7), (-1.15, RY + 0.28, 0.7),
                (-2.2, RY + 0.28, 1.16), (-1.15, RY + 0.28, 1.16), 3)
    s2.append(disc(-1.65, RY, 1.16, 0.17, 'z', ACCENT))        # radiator fan
    s2 += box(-2.08, RY - 0.08, 1.16, 0.14, 0.16, 0.16)        # exhaust
    s2 += box(-1.15, RY - RW / 2, 0.7, 0.55, RW, 0.74)         # cab
    s2.append(quad_x(-0.6, RY - 0.26, 1.12, 0.52, 0.24, DARK))
    s2.append(quad_y(RY + RW / 2, -1.07, 1.12, 0.38, 0.24, DARK))
    for xx in (-0.4, 1.12):                                    # wagon headstocks
        s2 += box(xx, RY - 0.3, 0.46, 0.08, 0.6, 0.12)
    s2 += box(-0.4, RY - 0.32, 0.58, 1.6, 0.64, 0.12)          # the flat wagon
    s2 += container(-0.15, RY - 0.22, 0.7)                     # centred on it

    # THE EXCAVATOR, facing +x with its boom over the empty quarter between
    # the siding's end and the apron's left corner. Both ramps rise 0.3 over
    # 0.2 — dz = 1.5 dx — so the front one lands on 45 deg and the rear,
    # running the other way, on 63.43.
    EX, EY = -2.85, 1.2
    TRK = [(0.0, Z), (1.05, Z), (1.25, Z + 0.3), (1.25, Z + 0.5),
           (-0.2, Z + 0.5), (-0.2, Z + 0.3)]
    for yy in (EY, EY + 0.5):                                  # crawler frames
        s2 += slab_y(yy, 0.3, [(EX + a, b) for a, b in TRK])
        s2.append(line(p_(EX - 0.12, yy + 0.3, Z + 0.28), p_(EX + 1.17, yy + 0.3, Z + 0.28)))
        s2 += seams((EX, yy + 0.3, Z), (EX + 1.05, yy + 0.3, Z),
                    (EX, yy + 0.3, Z + 0.28), (EX + 1.05, yy + 0.3, Z + 0.28), 4)
    s2 += box(EX + 0.02, EY - 0.05, 0.7, 1.2, 0.9, 0.1)        # slew platform
    # ONE HOUSE, ONE CAB, ONE BOOM FOOT: the house is engine and counterweight
    # together with its vents on the near flank, the cab stands at its front
    # corner on the far lane, and the boom sits on a foot beside the cab on
    # the near lane, which is where an excavator carries it.
    s2 += box(EX + 0.05, EY + 0.02, 0.8, 0.75, 0.76, 0.42)     # house
    s2 += seams((EX + 0.05, EY + 0.78, 0.8), (EX + 0.8, EY + 0.78, 0.8),
                (EX + 0.05, EY + 0.78, 1.22), (EX + 0.8, EY + 0.78, 1.22), 3)
    s2 += cyl(EX + 0.25, EY + 0.22, 1.22, 'z', 0.14, 0.05, side=FACE_L)   # exhaust
    s2 += box(EX + 0.78, EY + 0.02, 0.8, 0.42, 0.36, 0.62)     # cab
    s2.append(quad_x(EX + 1.2, EY + 0.06, 0.96, 0.28, 0.38, DARK))
    s2.append(quad_y(EY + 0.38, EX + 0.84, 0.96, 0.3, 0.38, DARK))
    s2 += box(EX + 0.85, EY + 0.42, 0.8, 0.3, 0.28, 0.12)      # boom foot
    # The boom rises at dz = 1.5 dx and the stick falls at dz = -1.5 dx: 45 deg
    # up, 63.43 deg down, 0.22 deep, 0.28 wide — a box section, not a blade.
    # THE BUCKET IS ON THE GROUND: a bucket with its cutting edge on the apron
    # is the one thing in the yard that says what the machine does. The
    # stick's tip lands on the mouth's rim, and paints last so the joint is seen.
    s2 += slab_y(EY + 0.42, 0.28,                              # the boom
                 [(EX + 0.95, 0.92), (EX + 1.45, 1.67), (EX + 1.45, 1.89), (EX + 0.95, 1.14)])
    s2 += slab_y(EY + 0.4, 0.32,                               # the bucket
                 [(EX + 1.98, 0.8), (EX + 2.4, 0.8), (EX + 2.4, 0.5),
                  (EX + 2.2, Z), (EX + 1.98, Z)])
    s2.append(quad_t(EX + 2.02, EY + 0.44, 0.8, 0.34, 0.24, ACCENT))   # the mouth
    s2 += slab_y(EY + 0.46, 0.2,                               # the stick
                 [(EX + 1.37, 1.8), (EX + 2.03, 0.81), (EX + 2.03, 1.01), (EX + 1.37, 2.0)])

    # ---- 3 · the semi, nearest the reader
    #
    # A CAB-OVER ON TWO AXLES pulling a trailer on a tandem: four wheels a
    # side, which is what a semi has, where the last one had five. The steer
    # axle is under the cab's front, half in the arch — the wheel plane is
    # 0.04 behind the cab's near face and the wheel paints before the cab —
    # and the drive axle is under the coupling, where the trailer's weight is.
    # THE COUPLING IS A LAP: the deck's front rests ON the chassis, bottom
    # flush with the chassis top, because a trailer rests on its tractor.
    TY = 1.5
    s3 += box(2.0, TY + 0.08, 0.34, 0.65, 0.42, 0.12)          # tractor chassis
    s3 += box(0.35, TY, 0.46, 1.8, 0.58, 0.1)                  # trailer deck
    s3 += container(0.45, TY + 0.07, 0.56)
    for xx in (0.7, 1.04):                                     # trailer tandem
        s3 += wheel(xx, TY + 0.56, 0.36, 0.16, 0.1)
    for xx in (2.2, 2.52):                                     # drive axle, steer axle
        s3 += wheel(xx, TY + 0.54, 0.36, 0.16, 0.1)
    s3 += box(2.08, TY + 0.02, 0.5, 0.57, 0.56, 0.6)           # cab
    s3 += box(2.12, TY + 0.06, 1.1, 0.45, 0.48, 0.12)          # roof fairing
    s3.append(quad_x(2.65, TY + 0.08, 0.76, 0.44, 0.26, DARK))     # windscreen
    s3.append(quad_y(TY + 0.58, 2.28, 0.76, 0.28, 0.24, DARK))     # door window
    s3.append(line(p_(2.22, TY + 0.58, 0.5), p_(2.22, TY + 0.58, 1.1)))   # door seam
    s3 += box(2.65, TY + 0.04, 0.34, 0.05, 0.52, 0.16)         # bumper

    # THE CROP IS TAKEN HERE, before the ghost: a ghost is what is not there
    # yet, so it sits outside what the drawing is OF, and letting the frame
    # grow to hold it would pad the drawing with the tier that has not been
    # loaded.
    crop = bbox(30.0)

    # A GHOST IS THE NEXT TIER: the same container, twice more, dashed, over
    # the two below it.
    ghost = []
    for yy in (STK_Y, STK_Y + CT_W):
        ghost += box(STK_X, yy, DECK + 2 * CT_H, CT_L, CT_W, CT_H,
                     'none', 'none', 'none')

    # TWO SWEPT CIRCLES, the propellers: a swept circle is a path something
    # travels rather than a state, which is exactly what a propeller disc is.
    # r 0.28 keeps the inboard edge 0.05 clear of the barrel.
    orbits = [orbit(PX - 0.55, -0.8, 0.98, 0.28, 'y'),
              orbit(PX + 0.55, -0.8, 0.98, 0.28, 'y')]

    LC = (STK_X, STK_Y + CT_W, DECK + 2 * CT_H)
    lid = [(LC[0], LC[1], LC[2]), (LC[0] + CT_L, LC[1], LC[2]),
           (LC[0] + CT_L, LC[1] + CT_W, LC[2]), (LC[0], LC[1] + CT_W, LC[2])]
    light = light_quad(gid, lid)
    la, lb = lime_span_quad(lid)
    nodes = light_nodes_quad(lid)
    return assemble(gid, la, lb, [(0, s0), (1, s1), (2, s2), (3, s3)],
                    light, nodes, ghost, orbits, crop=crop)


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    for name, fn in (('01-maschinenbau', maschinenbau), ('02-anlagen', anlagen),
                     ('03-erneuerbare', erneuerbare), ('04-flotten', flotten)):
        out = fn()
        open(os.path.join(here, name + '.svg'), 'w').write(out + '\n')
        n = out.count('<path') + out.count('<ellipse') + out.count('<circle') + out.count('<line')
        vb = out[out.index('viewBox="') + 9:]
        print(f'{name}: {n} elements, viewBox {vb[:vb.index(chr(34))]}')
