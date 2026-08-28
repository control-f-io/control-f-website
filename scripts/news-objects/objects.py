"""Ten news title plates, one per published post in the Notion news archive.

WHAT THEY REPLACED. The archive's ten Titelbilder were stock and generated
photographs — fibre-optic renders, wind farms at golden hour, and one plate that
was the word "AI" set white on black. Three rules of
foundations/illustration.html are against that last one alone: no text inside a
drawing, no colour outside grey and the one lime ramp, no raster.

AND THE FIRST REPLACEMENT WAS TOO LITERAL, which is the more interesting fault
and the reason this file reads the way it does. It drew a battery container with
cell-bay doors, a marking press with uprights and a ram, a substation with
cross-arms and insulator sheds — technical illustration of real equipment, done
correctly and in the wrong language. The four objects that ship are named in the
chapter's own table by their FORM and not by any machine:

    01  Discovery         stacked cuboids telescoping out of frame
    02  Datenfundament    overlapping 63.43 deg plates, each finer than the last
    03  Weniger Ausfälle  a solid of revolution read on its axis
    04  Mehr Leistung     a sphere cut by its equator, three orbits

None of the four is a thing you could buy. "The brand's pictures are technical
drawings of objects that do not exist" is not a licence to invent plausible
plant; it is the instruction to draw the PROPOSITION — a stack, a subdivision, a
body on its axis, a boundary, a detour — and let the copy name the subject. A
louvre is a detail about a cabinet. A trace that stops on a surface is an
argument about a boundary, and it is the same drawing whether the boundary is a
rack or a jurisdiction.

So: stacks, plates, solids of revolution, orbits, subdivisions, the lattice, and
the trace. Nothing that has a supplier.

THREE GREYS, NO MORE. #919191 and #484848 are the dense register's accent and
aperture — the values that let a 95-to-145-element Expertise object keep its
contours. A news plate carries a dozen or two faces and runs in the register the
chapter states first, so the slots and sight glasses the first pass spent them on
are gone with the equipment that justified them.

ONE LIT ELEMENT EACH, and it is the element the eye is meant to land on. The
rake follows what is lit: `near` for a flat face, `mid` for a body turning away,
`far` for a rim.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from isonews import (  # noqa: E402
    iso, P, p_, f, poly, line, face, box, quad_t, quad_x, quad_y, seams,
    disc, hoop, cyl, drum, taper, orbit, node, reset,
    TOP, LIT, SHADE, light_def, lit, lit_top, lit_x, lattice, emit, fit,
    common_size,
)

# The level step. Both ground axes slope 26.57 deg on screen, so a row marched
# along either one loses a unit of drawn height per step — the trap the plot
# fell into, where five columns rising 31 to 100 came out with the tallest drawn
# lower than the shortest. e1 - e2 is (+1, -1): still a lattice move, and the
# only way to go sideways without descending.
LEVEL = (1.0, -1.0)


def stack(x, y, z, base, dz, n, inset, taper_z=1.0):
    """Cuboids on one axis, each inset from the one below. The whole vocabulary
    of object 01 and half of object 02, and the shape a proposition about
    refinement or accumulation takes before it takes any other."""
    out = []
    for i in range(n):
        s = base - 2 * inset * i
        h = dz * (taper_z ** i)
        out += box(x + inset * i, y + inset * i, z, s, s, h, TOP, SHADE, LIT)
        z += h
    return out


def plates(x, y, z, base, th, gap, n, inset):
    """Overlapping plates, each finer than the last — object 02's form. The
    inset is what carries "finer"; the gap is what stops it reading as a solid."""
    out = []
    for i in range(n):
        s = base - 2 * inset * i
        out += box(x + inset * i, y + inset * i, z + i * (th + gap),
                   s, s, th, TOP, SHADE, LIT)
    return out


def axis(a, b):
    """A construction axis: 1-2 in the line-type table, which is what a centre
    line is. Not the 1-4 the lattice takes.

    P and not p_, here and in every ghost below. p_ returns the screen point
    without registering it, which is right for a gradient endpoint and wrong for
    anything drawn: fit() takes the crop from the registered points, so a ghost
    written with p_ is a ghost the frame is free to cut."""
    return f'<path d="{line(P(*a), P(*b))}" stroke-dasharray="2 4"/>'


def gline(a, b):
    return line(P(*a), P(*b))


def gquad(x, y, z, dx, dy):
    """A horizontal square, drawn as reference geometry."""
    return poly([P(x, y, z), P(x + dx, y, z), P(x + dx, y + dy, z), P(x, y + dy, z)])


def gbox(x, y, z, dx, dy, dz):
    """A cuboid drawn entirely as reference geometry — the three visible faces,
    unfilled. A state the object is not in: the branch that is there and is not
    carrying, the bay that is not built."""
    t, l, r = iso.box_faces(x, y, z, dx, dy, dz)
    # One path with three subpaths, not three paths: a dash restarts at every
    # subpath either way, and one element keeps the ghost a single thing in the
    # markup the way it is a single thing in the drawing.
    return t + l + r


def beam(x, y, z, axis_, length, s=0.28):
    """A member on one lattice axis. Every link in this set is one of these
    rather than a trace: with the arrows gone, what connects two bodies has to
    be a thing, and a thing on a lattice axis is the only kind this projection
    draws."""
    dx, dy, dz = (length, s, s) if axis_ == 'x' else \
                 ((s, length, s) if axis_ == 'y' else (s, s, length))
    return box(x, y, z, dx, dy, dz, TOP, SHADE, LIT)


# ==================================================================== 01
def offshore():
    """WindSeeG: a seven-day consultation window governing two decades of build.

    A load-bearing thinness — mass resting on a member far slighter than itself.
    A block, one 0.18 flange, and a telescoping stack standing on the flange;
    the flange is what is lit.

    THE LIT FACE IS THE FLANGE'S TOP AND THE STACK STANDS ON IT. Lighting the
    flank instead — the obvious move for a member with something on top of it —
    gave a 0.34-deep band three units long, which at plate size is a bright
    wedge at one edge and reads as a highlight rather than as a face. The top,
    painted in its own place in the paint order rather than last, comes out as a
    lit rim running out from under four courses of mass: small, unambiguous, and
    the thing everything rests on."""
    reset()
    forms = box(0.35, 0.35, 0.0, 2.3, 2.3, 0.45, TOP, SHADE, LIT)
    forms += box(0.0, 0.0, 0.45, 3.0, 3.0, 0.34, TOP, SHADE, LIT)
    # THE LIT FACE IS EMITTED HERE, INSIDE THE FORM, and that is the whole
    # composition. emit() paints the light last, which is right when the lit
    # face is the topmost thing in the drawing and wrong here: what should be
    # lit is the flange's top, and the stack stands on it. Painted last the ramp
    # would cover the stack; painted in its own place in the paint order the
    # stack occludes its middle and what is left is a lit rim running out from
    # under four courses of mass. One `.cf-iso__light` either way — the budget
    # is one lit element, not one lit element in a particular tag position.
    la, lb, light_face = lit_top('n01', 0.0, 0.0, 0.79, 3.0, 3.0, reach=0.78)
    forms.append(light_face)
    forms += stack(0.35, 0.35, 0.79, 2.3, 0.6, 4, 0.2)
    ghost = [
        axis((1.5, 1.5, 0.0), (1.5, 1.5, 3.9)),
        gbox(1.15, 1.15, 3.19, 0.7, 0.7, 0.6),          # the course not built
        gquad(0.0, 0.0, 0.0, 3.0, 3.0),
    ]
    nd = [node(0.0, 0.0, 0.79, 3), node(3.0, 0.0, 0.79, 3),
          node(3.0, 3.0, 0.79, 3), node(0.35, 0.35, 0.79, 2),
          node(2.65, 2.65, 0.79, 2), node(0.0, 0.0, 0.45, 1)]
    return light_def('n01', 'near', la, lb), forms, None, ghost, (), nd


# ==================================================================== 02
def labelling():
    """The AI Act's labelling duty: a mark that has to travel with the thing.

    A body, and a smaller body registered into its face. The mark is the lit
    element, which is the argument of the piece in the property the system
    spends most carefully: what is required is not a change to the thing but a
    declaration ON it, and a declaration that is not the thing the eye lands on
    has not been made.

    The ghost is the same square in the two positions it is not in — above the
    body, before it is applied, and beside it, where a mark that travels
    separately ends up."""
    reset()
    forms = box(0.15, 0.15, 0.0, 2.7, 2.7, 1.1, TOP, SHADE, LIT)
    forms += box(1.05, 1.05, 1.1, 0.9, 0.9, 0.34, TOP, SHADE, LIT)
    la, lb, light = lit_top('n02', 1.05, 1.05, 1.44, 0.9, 0.9)
    ghost = [
        axis((1.5, 1.5, 1.1), (1.5, 1.5, 2.7)),
        gbox(1.05, 1.05, 2.05, 0.9, 0.9, 0.34),         # before it is applied
        gbox(3.35, 1.05, 0.0, 0.9, 0.9, 0.34),          # the mark that did not travel
        gquad(1.05, 1.05, 1.1, 0.9, 0.9),
    ]
    nd = [node(1.05, 1.05, 1.44, 3), node(1.95, 1.05, 1.44, 3),
          node(1.95, 1.95, 1.44, 3), node(1.05, 1.95, 1.44, 2),
          node(0.15, 0.15, 1.1, 1), node(2.85, 0.15, 1.1, 1)]
    return light_def('n02', 'near', la, lb), forms, light, ghost, (), nd


# ==================================================================== 03
def redispatch():
    """Redispatch: the direct path is closed, and the cost is the detour.

    Two masses on one axis, a third standing in the axis between them, and a
    bridge built over it out of three members — riser, span, riser, each on a
    lattice axis. The ghost is the straight line that would have been taken.

    THE DETOUR IS BUILT AND NOT DRAWN. It was a trace in the first pass, which
    made the most expensive thing in the piece the one element of the drawing
    that is not part of the object. Three billion euros a year is infrastructure;
    infrastructure is form. What is lit is the block at the apex — the money is
    not spent on the constraint, it is spent on going round it."""
    reset()
    forms = box(-0.6, 0.9, 0.0, 1.2, 1.0, 0.9, TOP, SHADE, LIT)
    forms += box(3.0, 0.9, 0.0, 1.2, 1.0, 0.9, TOP, SHADE, LIT)
    forms += box(1.35, 0.75, 0.0, 0.75, 1.3, 1.7, TOP, SHADE, LIT)
    forms += beam(0.3, 1.25, 0.9, 'z', 1.4, 0.3)
    forms += beam(3.3, 1.25, 0.9, 'z', 1.4, 0.3)
    forms += beam(0.3, 1.25, 2.3, 'x', 3.3, 0.3)
    forms += box(1.75, 1.15, 2.6, 0.5, 0.5, 0.36, TOP, SHADE, LIT)
    la, lb, light = lit_top('n03', 1.75, 1.15, 2.96, 0.5, 0.5)
    ghost = [
        axis((-0.6, 1.4, 0.45), (4.2, 1.4, 0.45)),      # the path not taken
        gquad(1.35, 0.75, 1.7, 0.75, 1.3),
    ]
    nd = [node(1.75, 1.15, 2.96, 3), node(2.25, 1.15, 2.96, 3),
          node(2.25, 1.65, 2.96, 3), node(0.3, 1.25, 2.3, 2),
          node(3.6, 1.25, 2.3, 2), node(1.35, 1.4, 0.45, 1)]
    return light_def('n03', 'near', la, lb), forms, light, ghost, (), nd


# ==================================================================== 04
def electrolyser():
    """Hydrogen under a controller: separation, drawn as object 02's form.

    Overlapping plates, each finer than the last, on one axis — the shape a
    proposition about refinement takes, and the only one of these ten that is
    lifted straight out of the four that ship. What is lit is the finest plate,
    because that is what the process is for."""
    reset()
    forms = plates(-0.35, -0.35, 0.0, 3.7, 0.2, 0.14, 6, 0.28)
    la, lb, light = lit_top('n04', 1.05, 1.05, 2.04, 0.5, 0.5)
    ghost = [
        axis((1.5, 1.5, 0.0), (1.5, 1.5, 2.9)),
        gquad(-0.35, -0.35, 0.0, 3.7, 3.7),
        gquad(1.05, 1.05, 1.7, 0.5, 0.5),
    ]
    nd = [node(1.05, 1.05, 2.04, 3), node(1.55, 1.05, 2.04, 3),
          node(1.55, 1.55, 2.04, 3), node(0.49, 0.49, 1.36, 2),
          node(-0.35, -0.35, 0.2, 1), node(3.35, -0.35, 0.2, 1)]
    return light_def('n04', 'near', la, lb), forms, light, ghost, (), nd


# ==================================================================== 05
def cluster():
    """An on-premise cluster, drawn as the boundary it is bought for.

    A closed body, its interior drawn as reference geometry — an x-ray of what
    it holds — with one small body on the skin where the answer leaves, and the
    path that would carry the corpus out with it drawn entirely in ghost,
    because it is a state the object is not in.

    THE GATE IS LIT, NOT THE BODY. The argument is not that the cluster is
    important, it is that exactly one thing crosses the boundary, so the light
    goes on the one part of the object that lets anything through and the mass
    it protects stays grey.

    A rack with louvres is an argument about a rack. A body whose only opening is
    lit, with a dashed run leaving it and stopping, is an argument about a
    boundary — and it is the same drawing whether the boundary is a server room
    or a jurisdiction."""
    reset()
    forms = box(0.0, 0.0, 0.0, 2.9, 2.9, 2.1, TOP, SHADE, LIT)
    forms.append(quad_t(0.28, 0.28, 2.1, 2.34, 2.34))
    forms += box(1.15, 1.15, 2.1, 0.6, 0.6, 0.32, TOP, SHADE, LIT)
    la, lb, light = lit_top('n05', 1.15, 1.15, 2.42, 0.6, 0.6)
    ghost = [
        gquad(0.0, 0.0, 0.7, 2.9, 2.9),                 # what it holds
        gquad(0.0, 0.0, 1.4, 2.9, 2.9),
        gline((0.97, 0.0, 0.0), (0.97, 0.0, 2.1)),
        gline((1.93, 0.0, 0.0), (1.93, 0.0, 2.1)),
        gline((2.9, 0.97, 0.0), (2.9, 0.97, 2.1)),
        gline((2.9, 1.93, 0.0), (2.9, 1.93, 2.1)),
        # the outflow that does not happen: a run on +x, and where it would land
        gbox(2.9, 1.9, 0.9, 1.05, 0.28, 0.28),
        gbox(3.95, 1.62, 0.0, 0.85, 0.85, 0.5),
    ]
    nd = [node(1.15, 1.15, 2.42, 3), node(1.75, 1.15, 2.42, 3),
          node(1.75, 1.75, 2.42, 3), node(2.9, 1.9, 1.18, 2),
          node(0.0, 0.0, 2.1, 1), node(2.9, 0.0, 2.1, 1)]
    return light_def('n05', 'near', la, lb), forms, light, ghost, (), nd


# ==================================================================== 06
def storage():
    """Storage as a flexibility asset: many small arrivals, one body that holds.

    A row of thin plates running into a single tall mass, and the mass is
    graduated so that a height reads as a quantity. The ghost is the level it
    reaches — the object drawn in the state it is not in yet, which is the one
    thing a photograph of a battery container can never show.

    THE ROW IS ON e1 - e2 AND THAT IS NOT A DETAIL. Both ground axes slope
    26.57 deg on screen, so a row marched along either one loses a unit of drawn
    height per step, and members meant to be equal are drawn unequal — the trap
    the plot fell into, where five columns rising 31 to 100 came out with the
    tallest lower than the shortest. (+1, -1) is still a lattice move and it is
    the only one that is level."""
    reset()
    forms = []
    for i in range(3):
        forms += box(0.2 + i * LEVEL[0] * 0.7, 1.8 + i * LEVEL[1] * 0.7, 0.0,
                     0.9, 0.9, 0.2, TOP, SHADE, LIT)
    forms += box(2.8, 0.3, 0.0, 1.6, 1.6, 1.7, TOP, SHADE, LIT)
    for i in (1, 2):
        forms.append(gline((2.8, 1.9, i * 0.55), (4.4, 1.9, i * 0.55)))
        forms.append(gline((4.4, 0.3, i * 0.55), (4.4, 1.9, i * 0.55)))
    la, lb, light = lit_top('n06', 2.8, 0.3, 1.7, 1.6, 1.6)
    ghost = [
        gquad(2.8, 0.3, 2.4, 1.6, 1.6),                 # the level it reaches
        gline((2.8, 0.3, 1.7), (2.8, 0.3, 2.4)),
        gline((4.4, 1.9, 1.7), (4.4, 1.9, 2.4)),
        axis((0.05, 2.15, 0.1), (3.05, -0.85, 0.1)),    # the level line itself
    ]
    nd = [node(2.8, 0.3, 1.7, 3), node(4.4, 0.3, 1.7, 3),
          node(4.4, 1.9, 1.7, 3), node(0.2, 1.8, 0.2, 1),
          node(0.9, 1.1, 0.2, 1), node(1.6, 0.4, 0.2, 2)]
    return light_def('n06', 'near', la, lb), forms, light, ghost, (), nd


# ==================================================================== 07
def verteilnetz():
    """The distribution grid, and the branch that is curtailed.

    A hub with four arms on the lattice's own ground axes, three of them drawn
    and one of them entirely in ghost. That is the distinction the piece is
    about and the one a photograph cannot make: a curtailed feeder is not a
    feeder that is missing, it is a feeder that is there and not being used, and
    a dashed contour is the only element in the system that means exactly
    that."""
    reset()
    forms = box(0.85, 0.85, 0.0, 1.3, 1.3, 1.4, TOP, SHADE, LIT)
    forms += beam(2.15, 1.36, 0.3, 'x', 2.35, 0.32)
    forms += beam(1.36, 2.15, 0.3, 'y', 2.35, 0.32)
    forms += beam(-1.35, 1.36, 0.3, 'x', 2.2, 0.32)
    la, lb, light = lit_top('n07', 0.85, 0.85, 1.4, 1.3, 1.3)
    ghost = [
        gbox(1.36, -1.35, 0.3, 0.32, 2.2, 0.32),        # there, and carrying nothing
        axis((1.5, -1.55, 0.46), (1.5, 4.7, 0.46)),
        gquad(0.85, 0.85, 0.0, 1.3, 1.3),
    ]
    nd = [node(0.85, 0.85, 1.4, 3), node(2.15, 0.85, 1.4, 3),
          node(2.15, 2.15, 1.4, 3), node(4.5, 1.36, 0.62, 2),
          node(1.36, 4.5, 0.62, 2), node(-1.35, 1.36, 0.62, 1)]
    return light_def('n07', 'near', la, lb), forms, light, ghost, (), nd


# ==================================================================== 08
def platforms():
    """Two data platforms, drawn as two ways of building one volume.

    A stack of layers you can count, and a body of revolution you cannot — same
    footprint, same height, nothing else to tell them apart. The ghost is the
    footprint they share, which is the honest answer to a headline that asks
    which is better: what the piece actually answers is what the workload is,
    and both fit it.

    A DRUM AND NOT A FRUSTUM. A taper's generatrix lands on a screen slope of
    0.5 - dz/dx, which is a brand angle for dz/dx of 1, 1.5 and 2.5 and for
    nothing else — so a frustum chosen for its silhouette is a frustum off the
    grid. A cylinder's sides are vertical, its ends are the 2:1 circle, and the
    whole body is on the lattice by construction."""
    reset()
    forms = plates(-0.9, 0.3, 0.0, 1.7, 0.24, 0.06, 6, 0.0)
    forms += drum(2.85, 1.15, 0.0, 0.85, 1.8, top=TOP, side=LIT)
    forms.append(hoop(2.85, 1.15, 0.9, 0.85))
    la, lb, light = lit_top('n08', -0.9, 0.3, 1.8, 1.7, 1.7)
    ghost = [
        axis((-0.05, 1.15, 0.0), (-0.05, 1.15, 2.4)),
        axis((2.85, 1.15, 0.0), (2.85, 1.15, 2.4)),
        gquad(2.0, 0.3, 0.0, 1.7, 1.7),                 # the footprint they share
        gquad(-0.9, 0.3, 1.8, 1.7, 1.7),
    ]
    nd = [node(-0.9, 0.3, 1.8, 3), node(0.8, 0.3, 1.8, 3),
          node(0.8, 2.0, 1.8, 3), node(2.85, 1.15, 1.8, 2),
          node(2.0, 0.3, 0.0, 1), node(3.7, 2.0, 0.0, 1)]
    return light_def('n08', 'near', la, lb), forms, light, ghost, (), nd


# ==================================================================== 09
def maintenance():
    """Predictive maintenance: a body read on its axis before it fails.

    Object 03's form — a solid of revolution, read on the axis — with an orbit
    for the path its surface travels and a second profile ghosted inside it for
    the state it is heading towards. The reading is the whole subject, so the
    drawing is the body, its axis, and the difference between what it is and
    what it is becoming.

    THE LIT ELEMENT IS THE HUB AND NOT THE WHOLE END. A drum's top disc is the
    largest single face here; filled with the ramp it is a lime object rather
    than a lit one. The hub is 0.42 and it is what the axis passes through — the
    light lands where the reading is taken.

    The rake is far, because a body of revolution has no flat side to light:
    card 04 puts lime at 0.9 to 1.0 of a radial ramp for the same reason, and
    lime_span_disc anchors on the ellipse's own vertical extent rather than on a
    bounding-box corner so the lit end reaches lime at all."""
    reset()
    forms = drum(1.5, 1.5, 0.0, 1.5, 2.15, top=TOP, side=LIT)
    forms.append(hoop(1.5, 1.5, 0.72, 1.5))
    forms.append(hoop(1.5, 1.5, 1.44, 1.5))
    forms += drum(1.5, 1.5, 2.15, 0.52, 0.3, top=None, side=LIT)
    la, lb = iso.lime_span_disc(1.5, 1.5, 2.45, 0.52, axis='z', span=2.6)
    light = iso.light_disc('n09', 1.5, 1.5, 2.45, 0.52, axis='z')
    ghost = [
        axis((1.5, 1.5, -0.7), (1.5, 1.5, 3.3)),
        disc(1.5, 1.5, 2.15, 1.07),                     # the profile it is becoming
        gline((0.43, 1.5, 2.15), (0.43, 1.5, 0.18)),
        gline((2.57, 1.5, 2.15), (2.57, 1.5, 0.18)),
    ]
    orb = [orbit(1.5, 1.5, 1.08, 2.15, axis='z')]
    nd = [node(1.5, 1.5, 2.45, 3), node(2.02, 1.5, 2.45, 3),
          node(1.5, 1.5, 2.15, 2), node(0.0, 1.5, 1.44, 1),
          node(1.5, 1.5, 0.0, 1)]
    return light_def('n09', 'far', la, lb), forms, light, ghost, orb, nd


# ==================================================================== 10
def region():
    """A region of connected platforms: three bodies, and what is between them.

    The links are members on the ground axes and nothing else — with the arrows
    gone, what joins two sites has to be a thing, and a thing in this projection
    runs on a lattice axis or it is off the grid. The one ghosted link runs the
    same way, to the site the network has not reached.

    The lit body is the SMALLEST. What the piece argues is that the benefit is
    in the network rather than in the size of any participant, and the property
    this system will not let you spend twice is the light — so it goes on the
    smallest plate, which is the sentence the drawing can make that a caption
    would otherwise have to."""
    reset()
    forms = box(-0.9, 0.1, 0.0, 1.8, 1.8, 0.7, TOP, SHADE, LIT)
    forms += box(2.2, -0.5, 0.0, 1.4, 1.4, 1.25, TOP, SHADE, LIT)
    forms += box(1.5, 2.4, 0.0, 1.1, 1.1, 0.45, TOP, SHADE, LIT)
    forms += beam(0.9, 0.75, 0.32, 'x', 1.3)
    forms += beam(2.35, 0.9, 0.32, 'y', 1.5)
    la, lb, light = lit_top('n10', 1.5, 2.4, 0.45, 1.1, 1.1)
    ghost = [
        gbox(2.6, 2.75, 0.2, 1.3, 0.28, 0.28),          # the link not made
        gbox(3.9, 2.4, 0.0, 1.0, 1.0, 0.4),             # the site not reached
        axis((-0.9, 1.0, 0.35), (4.9, 1.0, 0.35)),
    ]
    nd = [node(1.5, 2.4, 0.45, 3), node(2.6, 2.4, 0.45, 3),
          node(2.6, 3.5, 0.45, 3), node(0.9, 0.9, 0.46, 2),
          node(2.35, 0.9, 0.46, 2), node(-0.9, 0.1, 0.7, 1)]
    return light_def('n10', 'near', la, lb), forms, light, ghost, (), nd


OBJECTS = {
    'sieben-tage-fuer-zwei-jahrzehnte-was-die': (offshore, 'Ein teleskopierender Stapel auf einer einzigen dünnen Platte'),
    'ki-kennzeichnung-was-der-ai-act-jetzt-ve': (labelling, 'Ein Körper mit einer kleineren Marke, in seine Fläche eingesetzt'),
    'drei-milliarden-fuer-ein-netz-das-es-so': (redispatch, 'Eine verstellte Achse und der Umweg darüber'),
    'gastbeitrag-ki-ist-notwendigkeit-fuer-di': (electrolyser, 'Übereinanderliegende Platten, jede feiner als die vorige'),
    'ki-im-netzbetrieb-wie-llm-cluster-gegen': (cluster, 'Ein geschlossener Körper; die Signale enden auf seiner Haut'),
    'batteriespeicher-als-flexibilitaets-asse': (storage, 'Eine ebene Reihe, die in einen einzelnen speichernden Körper läuft'),
    'wie-wir-mit-digitalisierung-im-verteilne': (verteilnetz, 'Ein Knoten mit vier Armen; einer ist da und trägt nichts'),
    'databricks-vs-snowflake-welche-datenplat': (platforms, 'Zwei Bauweisen über einem geteilten Grundriss'),
    'predictive-maintenance-fuer-kommunale-en': (maintenance, 'Ein Rotationskörper auf seiner Achse, mit Orbit und künftigem Profil'),
    'wie-die-bodenseeregion-von-vernetzten-da': (region, 'Drei Körper auf einem Gitter, über Gitterachsen verbunden'),
}


def build(fn, title, size=None):
    """THE CROP IS TAKEN AFTER THE DRAWING, not before it. fit() reads the
    points every primitive registered, pads them and widens the result to 3:2,
    so no part of an object can end up outside its own frame. The lattice is
    generated from that crop afterwards and registers nothing: it is a field,
    and a field is entitled to run off the edge."""
    defs, forms, light, ghost, orbits, nd = fn()
    crop = fit(size=size)
    return emit(title, crop, defs, [forms], light, ghost, orbits, nd,
                underlay=lattice(crop))


# WHAT SHIPS IS A PNG, AND THE VECTOR IS THE SOURCE IT IS MADE FROM.
#
# These were SVG in the store for two rounds, on illustration.html's own
# instruction — "SVG, always ... no raster export" — and the import path was
# opened up to carry them. What that missed is that the archive's editor is
# Notion, and Notion does not render an SVG in a Files property: the Titelbild
# came out broken in the database, so the person choosing the picture could not
# see the picture. A format the CMS cannot display is not a format this pipeline
# can use, whatever the chapter says about contours — and the chapter is written
# about drawings INLINE in a page, where the rule buys a 1 px contour at every
# size. It buys nothing through an <img> the author cannot preview.
#
# So the vector stays the source, under scripts/news-objects/svg/ with a stable
# name, and the export is a 2016 px PNG — two plates wide, which is the ceiling
# check-content-images.py allows and what a dpr-2 screen resolves across the
# 1008 px plate.
#
# THE EXPORT CARRIES A HEAVIER STROKE THAN THE SOURCE, and that is arithmetic
# rather than taste. In a browser the source draws its contours at 1 CSS px at
# any size, because .cf-iso sets vector-effect: non-scaling-stroke. A raster has
# no such thing: it is downscaled by whatever the card is, 2016 -> 380 in the
# grid and 2016 -> 568 in the lead cell, so a contour needs to be about 5 px in
# the file to arrive at 1. At 2016 px from a 572-unit viewBox the scale is 3.52,
# which puts that at 1.4 user units.
#
# The PNG is named by the digest of its own bytes, the way
# scripts/sync-news-notion.py names anything it stores, so the file this writes
# and the file the sync downloads from Notion after the same export is uploaded
# there are the same file and the next sync is a no-op.

SVG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'svg')
IMAGES = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      '..', '..', 'design-system', 'assets', 'img', 'news')

EXPORT_W = 2016          # two plates; check-content-images.py's ceiling
EXPORT_STROKE = 1.4      # see the note above


def for_raster(svg):
    """The source, prepared for a rasteriser: the <style> block dropped and one
    stroke width set on the scene.

    The block is exactly the two declarations a standalone file carries because
    it inherits no stylesheet, and both are wrong for an export. non-scaling-
    stroke would pin every contour to one device pixel of a 2016 px image, which
    is a quarter of a CSS pixel by the time a card has finished with it."""
    out = re.sub(r'<style>.*?</style>', '', svg, flags=re.S)
    return out.replace('<g class="cf-iso__scene" stroke="#000"',
                       '<g class="cf-iso__scene" stroke-width="%s" stroke="#000"'
                       % EXPORT_STROKE)


def rasterise(svg, stem):
    """The source through rsvg-convert, then re-encoded by Pillow.

    THE RE-ENCODE IS NOT AN OPTIMISATION. librsvg's PNG writer and Pillow's
    differ in filter choice and zlib settings, and one of the ten drawings came
    out of librsvg as a byte stream that Notion's edge refused: HTTP 403 from
    Cloudflare, on the file's content and not on the request — the same slot took
    a different picture at 200, and the same picture failed a fresh slot twice.
    Re-encoded to identical pixels it uploads first time.

    A picture the CMS will not accept is a picture that cannot be published, and
    a pipeline that produces one occasionally is worse than one that produces one
    always: this way every export leaves through the same encoder, so a drawing
    either uploads or none of them do. Pillow is already this repository's one
    dependency — scripts/sync-news-notion.py pins it for fit_to_plate.
    """
    import io
    import subprocess
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, stem + '.svg')
        with open(src, 'w', encoding='utf-8') as fh:
            fh.write(for_raster(svg))
        try:
            out = subprocess.run(
                ['rsvg-convert', '-w', str(EXPORT_W), src],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
        except FileNotFoundError:
            raise SystemExit(
                "news-objects: the PNG export needs rsvg-convert.\n"
                "    brew install librsvg\n"
                "    --check does not need it: it compares the SVG sources.")
    from PIL import Image
    im = Image.open(io.BytesIO(out))
    im.load()
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return buf.getvalue()


def emit_all(check=False):
    import hashlib
    bad = 0
    size = common_size([fn for fn, _ in OBJECTS.values()])
    os.makedirs(SVG_DIR, exist_ok=True)
    for stem, (fn, title) in OBJECTS.items():
        svg = build(fn, title, size).encode('utf-8')
        src = os.path.join(SVG_DIR, stem + '.svg')
        same = os.path.exists(src) and open(src, 'rb').read() == svg
        if check:
            bad += not same
            print(("ok   " if same else "DRIFT") + "  " + stem + '.svg')
            continue
        if not same:
            with open(src, 'wb') as fh:
                fh.write(svg)
        png = rasterise(svg.decode('utf-8'), stem)
        name = "%s-%s.png" % (stem[:40].rstrip('-'),
                              hashlib.sha1(png).hexdigest()[:8])
        path = os.path.join(IMAGES, name)
        if not os.path.exists(path) or open(path, 'rb').read() != png:
            with open(path, 'wb') as fh:
                fh.write(png)
        print("%7d B  %s" % (len(png), name))
    return bad


if __name__ == '__main__':
    check = '--check' in sys.argv
    drift = emit_all(check)
    if check and drift:
        print("\n%d drawing(s) differ from what objects.py produces." % drift)
        sys.exit(1)
