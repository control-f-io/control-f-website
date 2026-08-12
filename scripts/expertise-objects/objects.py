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
    assemble, window, lime_span_disc, reset,
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

    THE FLOOR IS CUT, THE MACHINE IS NOT, and the difference between those two
    sentences is the whole of this composition. The figure is laid out at
    --vb-w / 112 x --field-unit so that one lattice cell of the drawing is one
    cell of the ground it stands on, which means the drawing cannot be made
    bigger by giving it more room: the only way to a bigger machine is to hold
    the frame where it is and let it cut. So the window is authored — isolib's
    window() — rather than taken from the bounding box, and the floor runs out
    of the frame at both ends. The other three objects on this page still take
    the bbox plus 30 units of pad and still read as models on trays; that is
    the next thing to do here, not a difference of intent.
    -> foundations/illustration.html, "The frame is a crop, not a bounding box"

    WHAT THE CUT MAY TAKE IS GROUND, and only ground. The first version of this
    frame put its left edge at X = -72 and the cooler package reaches -105.6:
    34 units of the machine's own back end went off the side, so the fin pack
    ended in a vertical line no edge of the cooler explains and the top face
    lost its far corner. A floor that leaves the frame reads as a floor that
    continues; a MACHINE that leaves it reads as a drawing that did not fit.
    The frame therefore moved one lattice column left, to -128, and the
    generator came in to 1.75 so the other end has the same air the cooler
    now has — 22.4 units against 21.8, which is as near symmetric as a 56-unit
    column and a 0.01-unit drawing lattice can be. The set is a whole object
    standing on ground that is not.

    AND IT MAY ONLY TAKE IT ALONG ONE AXIS. The frame that fixed the left edge
    was 616 x 420 and it still cut the floor at the FRONT as well: the plate's
    near corner sat at screen (460, 526) — inside the frame's right edge, below
    its bottom one — so the bottom edge sliced it off and met the right edge in
    a 90 deg corner of white against the page's grey lattice. A right angle is
    the one figure this projection never draws: every edge in here is 26.57 deg
    or vertical, so the only thing on the page shaped like that corner was the
    <svg> box itself, and the drawing read as an image that had been cropped
    rather than as a view into a hall. Reported twice from the rendered page,
    both times as "the image is cut off".

    So the cut is spent on the two ENDS and nowhere else, which is what the
    note on the floor below always claimed it was. Two changes buy it, and
    neither touches the machine:

      the frame is 616 x 504 — 11 lattice columns by 9, both edges still on
      lattice rows (Y 8 and 512 are s = -13 and 5) — so its bottom edge clears
      the plate's near corner instead of cutting it;

      and the plate stops at x = 2.5 rather than 4.0, with the skid at 2.2
      rather than 3.7. That 1.5 units was bare ground past the end of the
      machine, and it was bare ground pointing at the one corner that had to
      come inside the frame. Trimmed, the plate's two remaining overhangs are
      56 units at each end and the skid's are 16.8 at each end — the cut is
      symmetric, which a cut that is composed can be and a cut that is an
      accident of where the drawing stopped cannot.

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
    # LONG IN x AND NARROW IN y. The frame has to cut the object somewhere, and
    # ground is the right thing to spend on it — but an apron widened in y buys
    # the cut with two empty corners, because +y is the direction that walks
    # down-left and takes the near corner with it. Lengthened along the machine's
    # own axis instead, the same ground is cut at both ends and none of it is
    # dead: it is the strip the set stands on, running on past the view.
    #
    # dx 10.0, NOT 11.5, and the skid 9.4 rather than 10.9 — see the docstring.
    # The machine ends at x = 1.75 and the plate used to run to 4.0, so 1.5 of
    # the 11.5 was ground with nothing on it, carrying the plate's near corner
    # down to screen Y 526 where the frame had to cut it. At 2.5 the corner is
    # at 484 and the frame's own bottom edge, 512, clears it: the same plate,
    # the same machine, the same lattice, and the cut now falls only where the
    # note above says it should. 2.5 also lands the two end overhangs on one
    # number, 56 units each, because -7.5 - 1.5 and 2.5 + 1.5 are +-9.0 and
    # +-4.0 about a frame whose own edges are at +-8 and 3 in (x - y).
    # ny=0: the lengthwise seam ran at y = 0, which is the drum's own axis, so
    # it came out on the drum's lower silhouette — two 26.57 deg lines 0.57 px
    # apart for 95 px, reading as one contour that thickens. The floor keeps its
    # two cross seams and loses the one that had nowhere to be.
    s0 += foundation(-7.5, -1.5, 10.0, 3.0, 0.22, 0.24, 2, 0)
    for yy in (-1.1, 0.72):                                    # the two skid beams
        s0 += box(-7.2, yy, 0.22, 9.4, 0.38, 0.28, FACE_TOP, PLATE_L, PLATE_R)
    s0.append(line(p_(-7.2, 1.1, 0.36), p_(2.2, 1.1, 0.36)))   # the near beam's web

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

    # THE WINDOW IS TAKEN HERE, before the trace: see isolib.window(). All four
    # edges land on lattice lines — (X - 320) / 56 and (Y - 372) / 28 are -8, 3,
    # -13 and 5 — because illustration.html asks the cut to be deliberate and a
    # crop arrived at by nudging an offset until it looked right is not. That is
    # also why the frame is 616 and not 640: 616 is 11 cells, 640 is 11.43, and
    # a width off the lattice cannot put both vertical edges on one. 616 is also
    # the widest frame the figure's own column will take: the width is
    # --vb-w / 112 x --field-unit and 12 cells asks 576 px of a 573 px column,
    # so `max-width: 100%` would bind and the one-cell-to-one-cell registration
    # would quietly stop being true. The machine was brought inside 11 cells
    # rather than the frame let out to 12.
    #
    # THE HEIGHT IS NOT UNDER THAT CONSTRAINT and was being rationed as though
    # it were. Only the WIDTH is read against the column; the height follows it
    # through `height: auto`, and the row it sits in is 541 px tall at 1440x900
    # because the copy card sets it, against 360 px of drawing. 420 therefore
    # bought nothing and cost the front of the floor. At 504 — 18 rows, 9 cells,
    # the figure 528 x 432 in a row that was already 541 — the bottom edge is at
    # Y 512 and the plate's near corner at 484, so the frame stops cutting in a
    # direction it was never meant to cut in. Every other object on this page is
    # taller than this one still.
    fw, fh = 616.0, 504.0                                      # 11 cells x 9
    fx, fy = 320.0 - 56.0 * 8, 372.0 - 28.0 * 13               # the top-left cut
    crop = window(fw, fh, (fx + fw / 2, fy + fh / 2))
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
    # spent the first two fifths of the step's scroll on nothing at all. The
    # start also came in to y = -2.3 so the line is not mostly off-stage in the
    # first place — 496.4 against an edge at 488 is the same 8 % it was drawn
    # to have.
    ta, tb = (0.85, -2.3, 2.64), (0.85, -0.34, 2.64)
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
