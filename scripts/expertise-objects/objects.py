"""The four Expertise objects, in the brand's near-white illustration register.

Keep silhouettes legible before adding detail. Stages are depth bands, back
to front; each drawing has one lit top face and four symmetric nodes on that face.
Run this file to regenerate the SVG assets, authored pages and browser gallery.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from isolib import (  # noqa: E402
    p_, line, box, plate, face, poly, quad_t, quad_x, quad_y, seams, slab_x, slab_y,
    disc, hoop, cyl, cone, wheel, taper, orbit, rotor, light_quad, light_disc,
    light_nodes_quad, light_nodes_disc, lime_span_quad, lime_span_disc,
    assemble, bbox, reset, pipe_network, place,
    FACE_TOP, FACE_L, FACE_R, PLATE_L, PLATE_R,
    ACCENT, DARK,
)


def maschinenbau():
    """An open generating set: radiator, exposed engine, alternator, shared skid.

    Keep the 18-unit margin: at the page's lattice scale a wider crop would
    exceed the pinned column and shrink the machine relative to its ground.
    """
    reset()
    gid = 'cf-ex-01'
    s0, s1, s2, s3 = [], [], [], []
    BEAM = 0.5                                                 # top of the skid
    AXIS = 1.45                                                # the shaft line
    GR = 0.86                                                  # generator radius

    s0 += plate(-6.85, -1.15, 0, 8.8, 2.3, 0.22)
    for yy in (-1.0, 0.62):                                    # the two skid beams
        s0 += box(-6.7, yy, 0.22, 8.5, 0.38, 0.28, FACE_TOP, PLATE_L, PLATE_R)
    for xx in (-6.2, -4.8, -0.25, 1.25):                      # skid attachment points
        s0.append(disc(xx, 1.0, 0.36, 0.055, 'y', ACCENT))

    # The radiator is the tallest component, as in the mtu reference. Its
    # fan faces the engine; both coolant runs physically enter the two units.
    s1 += box(-6.6, -1.0, BEAM, 1.35, 2.0, 0.16, FACE_TOP, PLATE_L, PLATE_R)
    s1 += box(-6.5, -0.9, 0.66, 1.15, 1.8, 3.05)              # radiator core
    s1.append(quad_y(0.9, -6.39, 0.86, 0.93, 2.62, FACE_L))
    s1 += seams((-6.39, 0.9, 0.86), (-5.46, 0.9, 0.86),
                (-6.39, 0.9, 3.48), (-5.46, 0.9, 3.48), 5)
    for zz in (1.51, 2.17, 2.83):                              # core cross rails
        s1.append(line(p_(-6.39, 0.9, zz), p_(-5.46, 0.9, zz)))
    s1 += box(-6.6, -1.0, 3.71, 1.35, 2.0, 0.16)               # top tank
    s1.append(disc(-5.35, 0.0, 1.9, 0.82, 'x', FACE_R))
    s1 += rotor(-5.35, 0.0, 1.9, 0.14, 0.68, 'x', 5, 36)
    s1.append(disc(-5.35, 0.0, 1.9, 0.14, 'x', ACCENT))
    s1 += pipe_network(gid + '-coolant', [
        [(-5.35, -0.62, 2.95), (-4.57, -0.62, 2.95), (-4.57, -0.62, 2.05)],
        [(-5.35, -0.62, 0.97), (-4.66, -0.62, 0.97)],
    ], r=0.09, bend=0.2)

    s1 += box(-4.85, -0.95, BEAM, 3.9, 1.9, 1.2)              # crankcase
    s1.append(line(p_(-4.85, 0.95, 1.04), p_(-0.95, 0.95, 1.04)))
    for xx in (-4.57, -3.52, -2.47):                           # access covers
        s1.append(quad_y(0.95, xx, 0.66, 0.7, 0.25, FACE_TOP))
    s1.append(quad_y(0.95, -1.5, 0.68, 0.24, 0.19, DARK))
    s1 += box(-4.78, -0.95, 1.7, 3.7, 1.9, 0.18)              # cylinder deck

    # Repeated covers and six short branches give the exposed engine its
    # rhythm. The low collector joins every branch instead of floating beside it.
    exhaust = [[(-4.7, 1.08, 1.52), (-1.22, 1.08, 1.52)]]
    for i in range(6):
        xx = -4.7 + i * 0.6
        s1 += box(xx, -0.83, 1.88, 0.48, 1.66, 0.46)
        s1.append(quad_y(0.83, xx + 0.14, 2.03, 0.2, 0.16, FACE_R))
        exhaust.append([(xx + 0.24, 0.83, 2.11), (xx + 0.24, 1.08, 2.11),
                        (xx + 0.24, 1.08, 1.52)])
    s1 += pipe_network(gid + '-exhaust', exhaust, r=(0.1,) + (0.07,) * 6, bend=0.15)
    for xx in (-4.15, -2.35):
        s1.append(hoop(xx, 1.08, 1.52, 0.1, 'x'))

    # Three equally spaced upright intake canisters on a common inlet rail.
    intake = [[(-4.45, 0.0, 2.45), (-1.25, 0.0, 2.45)]]
    intake += [[(xx, 0.0, 2.45), (xx, 0.0, 2.76)] for xx in (-4.15, -2.98, -1.81)]
    s1 += pipe_network(gid + '-intake', intake, r=0.09)
    for xx in (-4.15, -2.98, -1.81):
        s1 += cyl(xx, 0.0, 2.75, 'z', 0.58, 0.25)
        for zz in (2.83, 3.25):
            s1.append(hoop(xx, 0.0, zz, 0.25, 'z'))

    for xx in (-0.15, 1.05):                                   # generator feet
        s2 += box(xx, -0.8, BEAM, 0.55, 1.6, 0.16, FACE_TOP, PLATE_L, PLATE_R)
    s2 += cyl(-0.95, 0.0, AXIS, 'x', 2.70, GR, far=True, cap_far=FACE_L, cap=FACE_R)
    for xx in (-0.70, -0.54):                                  # the drive-end
        s2.append(hoop(xx, 0.0, AXIS, GR, 'x'))                # flange, a band
    for xx in (0.15, 1.35):                                   # housing seams
        s2.append(hoop(xx, 0.0, AXIS, GR, 'x'))

    s2 += box(-0.5, 0.66, BEAM, 0.58, 0.4, 1.65)              # control cabinet
    s2.append(quad_y(1.06, -0.43, 1.29, 0.44, 0.44, FACE_TOP))
    s2.append(quad_y(1.06, -0.37, 1.48, 0.32, 0.17, DARK))
    for xx in (-0.33, -0.13):
        s2.append(disc(xx, 1.06, 1.39, 0.025, 'y', ACCENT))
    s2.append(disc(-0.21, 1.06, 1.08, 0.05, 'y', ACCENT))

    s3 += box(0.35, -0.45, 2.1, 1.0, 0.9, 0.16)                # terminal-box pad
    s3 += box(0.47, -0.38, 2.26, 0.76, 0.76, 0.38)             # terminal box

    s3.append(disc(1.75, 0.0, AXIS, 0.7, 'x', FACE_R))         # the end cover
    s3.append(disc(1.75, 0.0, AXIS, 0.24, 'x', FACE_L))        # bearing housing

    # Six equally spaced fasteners around the bearing housing.
    for i in range(6):
        angle = math.tau * i / 6
        s3.append(disc(1.75, 0.5 * math.cos(angle), AXIS + 0.5 * math.sin(angle),
                       0.035, 'x', ACCENT))

    # The square terminal lid remains the one lit top face, with four
    # symmetric corner nodes supplied by the shared drawing library.
    roof = [(0.47, -0.38, 2.64), (1.23, -0.38, 2.64),
            (1.23, 0.38, 2.64), (0.47, 0.38, 2.64)]
    light = light_quad(gid, roof)
    la, lb = lime_span_quad(roof)
    crop = bbox(18)
    return assemble(gid, la, lb, [(0, s0), (1, s1), (2, s2), (3, s3)],
                    light, light_nodes_quad(roof), crop=crop)


def anlagen():
    """A reference-grounded process unit with a tower, tank and paired coolers.

    The plant is a composed illustration, not a particular process design.
    Every visible support touches its equipment; the common feed has real tees.
    """
    reset()
    gid = 'cf-ex-02'
    s0, s1, s2, s3 = [], [], [], []

    s0 += plate(-2.8, -2.4, 0, 5.6, 4.8, 0.2)

    cx, cy, cr = -1.75, -1.2, 0.44
    s1 += cyl(cx, cy, 0.2, 'z', 0.14, 0.6, side=PLATE_R)      # ring foundation
    s1 += cyl(cx, cy, 0.34, 'z', 0.3, 0.5, side=FACE_L)       # supporting skirt
    s1 += cyl(cx, cy, 0.64, 'z', 2.68, cr)
    for zz in (1.33, 2.3, 3.27):                               # shell courses
        s1.append(hoop(cx, cy, zz, cr, 'z'))

    # A shouldered crown and a shallow flanged access lid replace the drum top.
    # Its circular lid remains the single illuminated face of the whole plant.
    s1 += taper(cx, cy, 3.32, cr, 0.3, 0.2, FACE_TOP, FACE_R)
    s1 += cyl(cx, cy, 3.52, 'z', 0.1, 0.3)
    s1 += cyl(cx, cy, 3.62, 'z', 0.08, 0.36)
    s1 += cyl(cx + 0.39, cy, 1.86, 'x', 0.18, 0.15)           # shell manway
    s1.append(disc(cx + 0.57, cy, 1.86, 0.11, 'x', FACE_TOP))
    for i in range(4):
        a = math.tau * i / 4
        s1.append(disc(cx + 0.57, cy + 0.125 * math.cos(a),
                       1.86 + 0.125 * math.sin(a), 0.018, 'x', ACCENT))

    # An attached access ladder gives the column scale without a dense cage.
    for xx in (cx - 0.2, cx + 0.2):
        s1 += box(xx - 0.018, cy + 0.47, 0.34, 0.036, 0.036, 2.84)
        for zz in (0.91, 2.61):
            s1.append(line(p_(xx, cy + 0.39, zz), p_(xx, cy + 0.49, zz)))
    for i in range(9):
        zz = 0.5 + i * 0.3
        s1.append(line(p_(cx - 0.2, cy + 0.506, zz), p_(cx + 0.2, cy + 0.506, zz)))

    tx, ty = 1.75, -1.4
    s2 += cyl(tx, ty, 0.2, 'z', 0.13, 0.7, side=PLATE_R)      # tank ring foundation
    s2 += cyl(tx, ty, 0.33, 'z', 1.29, 0.62)
    for zz in (0.76, 1.19):
        s2.append(hoop(tx, ty, zz, 0.62, 'z'))
    s2 += taper(tx, ty, 1.62, 0.62, 0.24, 0.18, FACE_TOP, FACE_R)
    s2 += cyl(tx, ty, 1.8, 'z', 0.12, 0.13)                   # top connection
    s2 += cyl(tx, ty, 1.92, 'z', 0.05, 0.18)                  # connection flange
    s2 += cyl(tx + 0.55, ty, 0.8, 'x', 0.16, 0.16)
    s2.append(disc(tx + 0.71, ty, 0.8, 0.11, 'x', FACE_TOP))
    for yy in (ty - 0.06, ty + 0.06):                         # manway handle
        s2.append(line(p_(tx + 0.71, yy, 0.75), p_(tx + 0.71, yy, 0.85)))
    for xx in (tx - 0.15, tx + 0.15):                         # tank access ladder
        s2.append(line(p_(xx, ty + 0.65, 0.33), p_(xx, ty + 0.65, 1.62)))
    for i in range(5):
        zz = 0.48 + i * 0.24
        s2.append(line(p_(tx - 0.15, ty + 0.65, zz), p_(tx + 0.15, ty + 0.65, zz)))
    for zz in (0.48, 1.44):
        s2.append(line(p_(tx, ty + 0.62, zz), p_(tx, ty + 0.65, zz)))

    for xx in (-0.5, 0.95, 2.4):                               # rack columns
        s2 += box(xx - 0.16, -0.69, 0.2, 0.32, 0.32, 0.1, FACE_TOP, PLATE_L, PLATE_R)
        s2 += box(xx - 0.09, -0.62, 0.2, 0.18, 0.18, 2.0)
        s2.append(quad_x(xx + 0.09, -0.62, 1.9, 0.18, 0.1, ACCENT))
    s2 += box(-0.62, -0.86, 2.2, 3.14, 0.66, 0.14)             # rack beam

    # Two saddles support the header, which turns down into the tank instead
    # of ending in a redundant capped stub beyond the connection.
    for xx in (-0.22, 0.98):
        s2 += box(xx - 0.1, -0.83, 2.34, 0.2, 0.26, 0.06)

    # Long-coupled motor and centrifugal pump on one baseplate, following the
    # distinct motor / coupling / volute / axial-inlet silhouette in the photo.
    s2 += box(-2.5, 0.65, 0.2, 1.68, 0.8, 0.18, FACE_TOP, PLATE_L, PLATE_R)
    for xx in (-2.26, -1.85, -1.35):                           # motor and pump feet
        s2 += box(xx, 0.86, 0.38, 0.22, 0.4, 0.16, FACE_TOP, PLATE_L, PLATE_R)
    s2 += cyl(-2.38, 1.05, 0.76, 'x', 0.72, 0.23)
    for a in (0, 45, 90):                                     # longitudinal motor fins
        yy = 1.05 + 0.23 * math.cos(math.radians(a))
        zz = 0.76 + 0.23 * math.sin(math.radians(a))
        s2.append(line(p_(-2.32, yy, zz), p_(-1.74, yy, zz)))
    s2 += box(-2.23, 0.875, 0.94, 0.39, 0.35, 0.23)           # terminal/controller box
    s2.append(quad_y(1.225, -2.16, 1.0, 0.25, 0.1, DARK))
    s2 += cyl(-1.66, 1.05, 0.76, 'x', 0.23, 0.11)             # coupling guard
    s2 += cyl(-1.43, 1.05, 0.76, 'x', 0.3, 0.31)              # volute casing
    s2.append(disc(-1.13, 1.05, 0.76, 0.25, 'x', FACE_R))
    s2 += cyl(-1.13, 1.05, 0.76, 'x', 0.17, 0.11)             # axial suction
    s2 += cyl(-0.96, 1.05, 0.76, 'x', 0.04, 0.17)
    s2.append(disc(-0.92, 1.05, 0.76, 0.08, 'x', DARK))
    s2 += cyl(-1.3, 1.05, 1.0, 'z', 0.42, 0.1)               # vertical discharge
    s2 += cyl(-1.3, 1.05, 1.36, 'z', 0.06, 0.16)

    for yy in (0.6, 1.6):
        for xx in (0.57, 1.78):                               # paired saddle supports
            s3 += box(xx - 0.08, yy - 0.27, 0.2, 0.32, 0.54, 0.09, FACE_TOP, PLATE_L, PLATE_R)
            s3 += box(xx, yy - 0.22, 0.29, 0.16, 0.44, 0.36)
        s3 += cyl(0.3, yy, 0.85, 'x', 1.96, 0.32, cap_far=FACE_L)
        for xx in (0.65, 1.86):                               # saddle straps
            s3.append(hoop(xx, yy, 0.85, 0.32, 'x'))
        s3 += cyl(2.26, yy, 0.85, 'x', 0.16, 0.36)             # removable channel head
        s3 += cyl(2.42, yy, 0.85, 'x', 0.06, 0.4)              # bolted end flange
        s3.append(disc(2.48, yy, 0.85, 0.24, 'x', FACE_R))
        for i in range(6):                                    # equal bolt circle
            a = math.tau * i / 6
            s3.append(disc(2.48, yy + 0.315 * math.cos(a),
                           0.85 + 0.315 * math.sin(a), 0.028, 'x', ACCENT))
        s3 += cyl(2.48, yy, 0.85, 'x', 0.11, 0.08)             # end drain/connection
        for xx in (0.70, 2.00):                               # flanged shell connections
            s3 += cyl(xx, yy, 1.1, 'z', 0.32, 0.09)
            s3 += cyl(xx, yy, 1.36, 'z', 0.06, 0.15)
        s3.append(disc(2.0, yy, 1.42, 0.07, 'z', DARK))

    # Paint connected routes as one network: the small feed joins the header
    # without a cap seam, and each flange has room for a rounded elbow.
    s3 += pipe_network(gid + '-pipes', [
        [(cx + cr, cy, 2.51), (-0.62, cy, 2.51),
         (-0.62, -0.7, 2.51), (tx, -0.7, 2.51),
         (tx, ty, 2.51), (tx, ty, 1.97)],
        [(0.7, -0.7, 2.51), (0.7, -0.02, 2.51),
         (0.7, -0.02, 1.67), (0.7, 1.6, 1.67), (0.7, 1.6, 1.42)],
        [(0.7, 0.6, 1.42), (0.7, 0.6, 1.67)],
        [(-1.3, 1.05, 1.42), (-1.3, 1.05, 1.67), (0.7, 1.05, 1.67)],
    ], r=(0.11, 0.075, 0.075, 0.075), bend=0.22)
    # Visible weld seams follow the pipe surface. A complete collar here
    # left detached crescents behind the elbow at the tower connection.
    s3.append(hoop(-1.07, cy, 2.51, 0.11, 'x'))
    for xx in (0.05, 1.15):
        s3.append(hoop(xx, -0.7, 2.51, 0.11, 'x'))

    ghost = []
    light = light_disc(gid, cx, cy, 3.7, 0.36, 'z')
    la, lb = lime_span_disc(cx, cy, 3.7, 0.36, 'z')
    nodes = light_nodes_disc(cx, cy, 3.7, 0.36, 'z')
    return assemble(gid, la, lb, [(0, s0), (1, s1), (2, s2), (3, s3)],
                    light, nodes, ghost)


ROTOR_PHASE = 78.0


def erneuerbare():
    """A renewable asset portfolio, grounded in manufacturer imagery.

    The assets use independent illustrative scales; this is not a plant layout.
    See references-renewables.md for the observed construction of each asset.
    """
    reset()
    gid = 'cf-ex-03'
    s0, s1, s2, s3 = [], [], [], []

    s0 += plate(-2.9, -2.4, 0, 5.8, 4.8, 0.2)

    wx, wy = -1.95, -1.75
    hx, hz = wx + 0.15, 2.99                                   # the rotor plane
    s1 += cyl(wx, wy, 0.2, 'z', 0.16, 0.36, side=PLATE_R)      # foundation
    s1 += taper(wx, wy, 0.36, 0.19, 0.12, 2.5, None, FACE_R)
    for zz in (1.1, 1.9):
        s1.append(hoop(wx, wy, zz, 0.19 - (zz - 0.36) / 2.5 * 0.07, 'z'))
    # Vestas reference: a long panelled nacelle behind the hub, a tapered
    # tubular tower and three evenly spaced aerofoil blades.
    s1 += box(hx - 0.66, wy - 0.17, 2.84, 0.66, 0.34, 0.3)
    s1.append(quad_y(wy + 0.17, hx - 0.55, 2.9, 0.29, 0.15, FACE_TOP))
    s1 += seams((hx - 0.22, wy + 0.17, 2.89), (hx - 0.05, wy + 0.17, 2.89),
                (hx - 0.22, wy + 0.17, 3.07), (hx - 0.05, wy + 0.17, 3.07), 2)
    s1 += cyl(hx - 0.57, wy, 3.14, 'z', 0.13, 0.025, side=ACCENT)
    s1 += rotor(hx, wy, hz, 0.09, 0.88, 'x', 3, ROTOR_PHASE)
    s1 += cone(hx, wy, hz, 'x', 0.12, 0.13, 0.035, cap=FACE_TOP)
    s1.append(quad_x(wx + 0.15, wy - 0.06, 0.42, 0.12, 0.3, FACE_L))

    # A shared rearward origin keeps the complete transformer and its plinth
    # clear of the elevated solar table in the isometric projection.
    tx, ty = -1.2, -2.15
    s2 += box(tx, ty, 0.2, 1.35, 1.05, 0.18, FACE_TOP, PLATE_L, PLATE_R)
    s2 += box(tx + 0.15, ty + 0.15, 0.38, 1.05, 0.65, 0.62)   # transformer tank
    s2 += box(tx + 0.1, ty + 0.1, 1.0, 1.15, 0.75, 0.07)      # bolted tank lid
    # Hitachi reference: the radiator is a projecting bank, not lines drawn
    # directly on the tank. Short upper/lower headers connect its five fins.
    for xx in (0.22, 0.41, 0.6, 0.79, 0.98):
        s2 += box(tx + xx, ty + 0.8, 0.47, 0.065, 0.18, 0.43, FACE_TOP, FACE_L, FACE_R)
    for zz in (0.47, 0.9):
        s2 += cyl(tx + 0.2, ty + 0.92, zz, 'x', 0.88, 0.04)
    for xx in (0.375, 0.675, 0.975):                         # three ribbed bushings
        s2 += cyl(tx + xx, ty + 0.47, 1.07, 'z', 0.26, 0.045, side=FACE_L)
        for zz in (1.14, 1.23):
            s2.append(disc(tx + xx, ty + 0.47, zz, 0.075, 'z', FACE_TOP))
    s2.append(disc(tx + 1.2, ty + 0.47, 0.83, 0.075, 'x', FACE_TOP))
    s2.append(line(p_(tx + 1.2, ty + 0.47, 0.83), p_(tx + 1.2, ty + 0.5, 0.87)))

    # Nel A485 reference: a horizontal filter-press cell stack and a pair
    # of gas separators share an open steel skid. These are not storage bottles.
    ex, ey = 0.6, -1.75
    s2 += box(ex, ey - 0.3, 0.2, 2.05, 0.96, 0.12, FACE_TOP, PLATE_L, PLATE_R)
    for yy in (ey - 0.2, ey + 0.48):
        s2 += box(ex + 0.04, yy, 0.32, 1.97, 0.09, 0.1)
    for xx in (ex + 0.18, ex + 1.63):
        s2 += box(xx, ey - 0.14, 0.42, 0.2, 0.74, 0.18)
    for yy in (ey - 0.02, ey + 0.38):                         # separator pair at rear
        s2 += cyl(ex + 0.3, yy, 0.6, 'z', 0.82, 0.17)
        s2 += taper(ex + 0.3, yy, 1.42, 0.17, 0.11, 0.1)
        s2 += cyl(ex + 0.3, yy, 1.52, 'z', 0.09, 0.045)
        s2 += cyl(ex + 0.3, yy, 0.72, 'x', 0.28, 0.045)
    s2 += cyl(ex + 0.48, ey + 0.18, 0.88, 'x', 0.09, 0.32, side=FACE_L)
    s2 += cyl(ex + 0.57, ey + 0.18, 0.88, 'x', 1.2, 0.28, side=FACE_R)
    for i in range(6):                                      # condensed cell-plate rhythm
        s2.append(hoop(ex + 0.61 + i * 0.2, ey + 0.18, 0.88, 0.28, 'x'))
    # The two exposed tie rods enter the compression plate from behind.
    # Paint the opaque end plate afterwards so their concealed ends cannot
    # appear as stray lines across its face or beyond the outer rim.
    for yy, zz in ((ey + 0.18, 1.16), (ey + 0.46, 0.88)):
        s2.append(line(p_(ex + 0.57, yy, zz), p_(ex + 1.79, yy, zz)))
    s2 += cyl(ex + 1.77, ey + 0.18, 0.88, 'x', 0.09, 0.32, side=FACE_L)
    for dy, dz in ((0.0, 0.28), (0.28, 0.0), (0.0, -0.28), (-0.28, 0.0)):
        s2.append(disc(ex + 1.86, ey + 0.18 + dy, 0.88 + dz, 0.022, 'x', ACCENT))
    s2.append(disc(ex + 1.86, ey + 0.18, 0.88, 0.14, 'x', FACE_L))
    s2.append(disc(ex + 1.86, ey + 0.18, 0.88, 0.075, 'x', DARK))

    s3 += box(-2.6, 0.9, 0.2, 2.8, 1.1, 1.05)                  # battery container
    # PowerTitan reference: closed flush service doors, a dark plinth and a
    # narrow ventilation band. The former three large windows were misleading.
    s3.append(quad_y(2.0, -2.6, 0.2, 2.8, 0.09, ACCENT))
    s3.append(quad_x(0.2, 0.9, 0.2, 1.1, 0.09, ACCENT))
    s3.append(quad_y(2.0, -2.51, 1.11, 2.62, 0.06, ACCENT))
    s3 += seams((-2.6, 2.0, 0.2), (0.2, 2.0, 0.2),
                (-2.6, 2.0, 1.25), (0.2, 2.0, 1.25), 2)
    for i in range(3):
        xx = -2.6 + (2.8 / 3) * i
        s3.append(quad_y(2.0, xx + 0.73, 0.65, 0.035, 0.15, DARK))
        for zz in (0.45, 0.94):
            s3.append(quad_y(2.0, xx + 0.06, zz, 0.05, 0.06, FACE_R))
    s3.append(quad_x(0.2, 1.12, 0.46, 0.66, 0.52, FACE_L))
    for zz in (0.59, 0.72, 0.85):
        s3.append(line(p_(0.2, 1.22, zz), p_(0.2, 1.68, zz)))

    ax, ay = 0.5, 0.5
    # Schletter FS Duo: slender paired posts and continuous rails beneath
    # an inclined module table, with open air between the supports.
    for xx in (ax + 0.24, ax + 1.74):
        s3 += box(xx, ay + 0.12, 0.2, 0.12, 0.12, 0.86)
        s3 += box(xx, ay + 1.28, 0.2, 0.12, 0.12, 0.28)
        s3.append(line(p_(xx + 0.12, ay + 0.24, 0.48),
                       p_(xx + 0.12, ay + 0.82, 0.77)))
    s3 += box(ax + 0.12, ay + 0.12, 1.0, 1.86, 0.12, 0.06)
    s3 += box(ax + 0.12, ay + 1.28, 0.42, 1.86, 0.12, 0.06)
    s3 += slab_x(ax, 2.1, [(ay, 1.12), (ay + 1.5, 0.37),
                           (ay + 1.5, 0.45), (ay, 1.2)])
    for xx in (ax + 0.525, ax + 1.05, ax + 1.575):
        s3.append(line(p_(xx, ay, 1.2), p_(xx, ay + 1.5, 0.45)))
    for offset in (0.5, 1.0):
        z = 1.2 - offset * 0.5
        s3.append(line(p_(ax, ay + offset, z), p_(ax + 2.1, ay + offset, z)))
    # A fine, symmetric half-cell split inside each of the four module columns.
    for xx in (ax + 0.2625, ax + 0.7875, ax + 1.3125, ax + 1.8375):
        s3.append(line(p_(xx, ay + 0.04, 1.18), p_(xx, ay + 1.46, 0.47)))

    ghost = []
    orbits = [orbit(hx, wy, hz, 0.88, 'x')]                    # the sweep the tips travel
    roof = [(-2.6, 0.9, 1.25), (0.2, 0.9, 1.25), (0.2, 2.0, 1.25), (-2.6, 2.0, 1.25)]
    light = light_quad(gid, roof)
    la, lb = lime_span_quad(roof)
    nodes = light_nodes_quad(roof)
    return assemble(gid, la, lb, [(0, s0), (1, s1), (2, s2), (3, s3)],
                    light, nodes, ghost, orbits)


CT_L, CT_W, CT_H = 1.1, 0.44, 0.48


def container(x, y, z, top=FACE_TOP, length=CT_L):
    """A box and five lines. `top=None` leaves the sky face unpainted, for the
    object's one lit element to be laid over."""
    out = box(x, y, z, length, CT_W, CT_H, top, FACE_L, FACE_R)
    # Three corrugations, not seven. At 55 px long the side takes a rib every
    # 14 px and still reads as pressed steel; at seven it is a grey hatch.
    out += seams((x, y + CT_W, z), (x + length, y + CT_W, z),
                 (x, y + CT_W, z + CT_H), (x + length, y + CT_W, z + CT_H), 3)
    out.append(line(p_(x, y + CT_W, z + CT_H * 0.86),
                    p_(x + length, y + CT_W, z + CT_H * 0.86)))   # the top rail
    out.append(line(p_(x + length, y + CT_W / 2, z),
                    p_(x + length, y + CT_W / 2, z + CT_H)))     # the door leaves
    return out


def fleet_semi(x, y):
    """MAN-style low cab, two tractor axles and an articulated container chassis."""
    out = []
    TY = y
    TYRE_R, AXLE_Z = 0.14, 0.34                             # every tyre rests at z=.2
    TYRE_FACE, TYRE_W = TY + 0.595, 0.065

    def semi_tyre(xx):
        # Dark rubber surrounds one small light metal rim. A narrow tread and
        # an unstroked hub keep the wheel from becoming three bright washers.
        tyre = cyl(xx, TYRE_FACE - TYRE_W, AXLE_Z, 'y', TYRE_W, TYRE_R,
                   side=DARK, cap=DARK, cap_far=DARK, crown=False)
        tyre.append(disc(xx, TYRE_FACE, AXLE_Z, 0.064, 'y', FACE_R))
        tyre.append(disc(xx, TYRE_FACE, AXLE_Z, 0.018, 'y', ACCENT)
                    .replace('/>', ' stroke="none"/>'))
        return tyre

    out += box(1.62 + x, TY + 0.08, 0.34, 1.03, 0.42, 0.12)
    out += cyl(1.87 + x, TY + 0.29, 0.46, 'z', 0.04, 0.15,
               side=ACCENT, cap=ACCENT, crown=False)          # fifth-wheel coupling
    for xx in (0.58, 0.98, 1.38):                            # attached suspension seats
        out += box(xx + x - 0.045, TY + 0.46, 0.4, 0.09, 0.1, 0.11)
    out += box(0.35 + x, TY, 0.5, 1.68, 0.58, 0.09)
    out += container(0.43 + x, TY + 0.07, 0.59, length=1.45)
    # Three separate trailer tyres have .12 clear gaps. The tractor's drive
    # axle stays behind the cab; its steering axle has a real front overhang.
    for xx in (0.58, 0.98, 1.38, 1.87, 2.42):
        out += semi_tyre(xx + x)

    cab = box(2.08 + x, TY + 0.02, 0.44, 0.57, 0.56, 0.66)
    # Cut the near cab face around the steering tyre, with clearance between
    # rubber and the wheel arch. Its open bottom reveals the tyre drawn behind.
    arch_r = 0.165
    angle = math.degrees(math.acos((0.44 - AXLE_Z) / arch_r))
    arch = hoop(2.42 + x, TY + 0.58, AXLE_Z, arch_r, 'y', -angle, angle)
    rear = p_(2.08 + x, TY + 0.58, 0.44)
    front = p_(2.65 + x, TY + 0.58, 0.44)
    front_top = p_(2.65 + x, TY + 0.58, 1.1)
    rear_top = p_(2.08 + x, TY + 0.58, 1.1)
    side = (f'M{rear[0]:.2f} {rear[1]:.2f}' + 'L' + arch[1:]
            + ''.join(f'L{pt[0]:.2f} {pt[1]:.2f}' for pt in (front, front_top, rear_top)) + 'Z')
    cab[0] = face(side, FACE_L)
    out += cab
    out.append(quad_x(2.65 + x, TY + 0.08, 0.76, 0.44, 0.26, DARK))
    out.append(quad_y(TY + 0.58, 2.28 + x, 0.76, 0.28, 0.24, DARK))
    out.append(line(p_(2.22 + x, TY + 0.58, 0.5), p_(2.22 + x, TY + 0.58, 1.1)))
    out.append(quad_x(2.65 + x, TY + 0.19, 0.56, 0.22, 0.12, DARK))  # grille
    for yy in (TY + 0.08, TY + 0.42):                           # paired headlamps
        out.append(quad_x(2.65 + x, yy, 0.55, 0.08, 0.07, FACE_TOP))
    out.append(line(p_(2.27 + x, TY + 0.58, 0.66), p_(2.38 + x, TY + 0.58, 0.66)))
    out += box(2.65 + x, TY + 0.04, 0.34, 0.05, 0.52, 0.16)
    return out


def fleet_excavator(x, y):
    """Tracked excavator: paired crawlers, glazed cab, articulated digging arm."""
    out = []
    Z = 0.2
    for yy in (y, y + 0.5):
        out += slab_y(yy, 0.3, [(x, Z), (x + 1.05, Z),
                               (x + 1.25, Z + 0.3), (x + 1.25, Z + 0.5),
                               (x - 0.2, Z + 0.5), (x - 0.2, Z + 0.3)])
        out.append(line(p_(x - 0.1, yy + 0.3, Z + 0.25),
                        p_(x + 1.15, yy + 0.3, Z + 0.25)))
        for xx in (x + 0.06, x + 0.4, x + 0.74, x + 1.08):
            out.append(disc(xx, yy + 0.3, Z + 0.25, 0.11, 'y', FACE_R))
    out += box(x + 0.02, y - 0.05, 0.7, 1.2, 0.9, 0.1)       # slew deck
    out += box(x + 0.05, y + 0.02, 0.8, 0.75, 0.76, 0.42)    # counterweight
    out += seams((x + 0.13, y + 0.78, 0.9), (x + 0.63, y + 0.78, 0.9),
                 (x + 0.13, y + 0.78, 1.12), (x + 0.63, y + 0.78, 1.12), 3)
    out += box(x + 0.78, y + 0.02, 0.8, 0.42, 0.36, 0.62)    # operator's cab
    out.append(quad_x(x + 1.2, y + 0.07, 0.96, 0.26, 0.38, DARK))
    out.append(quad_y(y + 0.38, x + 0.84, 0.96, 0.29, 0.38, DARK))
    out.append(line(p_(x + 0.85, y + 0.38, 0.86), p_(x + 0.96, y + 0.38, 0.86)))
    out += box(x + 0.85, y + 0.42, 0.8, 0.3, 0.28, 0.12)     # boom foot
    out += slab_y(y + 0.42, 0.28, [(x + 0.95, 0.92), (x + 1.45, 1.67),
                                  (x + 1.45, 1.89), (x + 0.95, 1.14)])
    # A digging bucket has a rounded heel and a forward cutting lip, not a
    # flat lid. The shell wraps across the two side cheeks; the visible mouth
    # is open ahead of the stick, with three teeth along its cutting edge.
    by0, by1 = y + 0.35, y + 0.79

    def bp(dx, yy, zz):
        a, b = p_(x + dx, yy, zz)
        return f'{a:.2f} {b:.2f}'

    def bucket_cheek(yy):
        return (f'M{bp(1.82, yy, 0.8)}'
                f'C{bp(1.59, yy, 0.72)} {bp(1.54, yy, 0.46)} {bp(1.71, yy, 0.3)}'
                f'Q{bp(1.93, yy, 0.13)} {bp(2.36, yy, 0.28)}'
                f'L{bp(2.40, yy, 0.34)}Z')

    out.append(face(bucket_cheek(by0), FACE_R))
    shell = (f'M{bp(1.82, by0, 0.8)}'
             f'C{bp(1.59, by0, 0.72)} {bp(1.54, by0, 0.46)} {bp(1.71, by0, 0.3)}'
             f'Q{bp(1.93, by0, 0.13)} {bp(2.36, by0, 0.28)}'
             f'L{bp(2.36, by1, 0.28)}'
             f'Q{bp(1.93, by1, 0.13)} {bp(1.71, by1, 0.3)}'
             f'C{bp(1.54, by1, 0.46)} {bp(1.59, by1, 0.72)} {bp(1.82, by1, 0.8)}Z')
    out.append(face(shell, FACE_R))
    out.append(face(poly([p_(x + 1.82, by0, 0.8), p_(x + 1.82, by1, 0.8),
                          p_(x + 2.40, by1, 0.34), p_(x + 2.40, by0, 0.34)]), ACCENT))
    out.append(face(bucket_cheek(by1), FACE_L))
    for yy in (y + 0.39, y + 0.54, y + 0.69):
        out += slab_y(yy, 0.065, [(x + 2.29, 0.36), (x + 2.50, 0.25),
                                  (x + 2.32, 0.28)])
    out += slab_y(y + 0.46, 0.2, [(x + 1.37, 1.8), (x + 2.03, 0.81),
                                 (x + 2.03, 1.01), (x + 1.37, 2.0)])
    # The coupling ears overlap the stick's foot and share one hinge axis.
    for yy in (y + 0.39, y + 0.67):
        out += slab_y(yy, 0.06, [(x + 1.79, 0.74), (x + 1.96, 0.88),
                                 (x + 2.0, 0.99), (x + 2.13, 0.99),
                                 (x + 2.07, 0.65)])
        out.append(disc(x + 2.04, yy + 0.06, 0.9, 0.045, 'y', ACCENT))
    # Connected hydraulic ram and pivot pins, confined to the arm silhouette.
    out.append(line(p_(x + 1.01, y + 0.71, 1.03), p_(x + 1.41, y + 0.71, 1.63)))
    for xx, zz in ((x + 1.01, 1.03), (x + 1.41, 1.83)):
        out.append(disc(xx, y + 0.71, zz, 0.05, 'y', ACCENT))
    return out


def fleet_aircraft():
    """A compact Airbus-inspired jet, placed as one ground-anchored asset."""
    gid = "cf-ex-04"
    out = []
    # Airbus A320neo references: slender round fuselage, swept low wings,
    # conventional tail and twin underwing turbofans. Coordinates are shared
    # across paired components so the airframe stays symmetric in the lattice.
    PX, FZ, FR = 1.82, 0.67, 0.185

    def wing(sign, span, root_le, root_te, tip_le, tip_te, z0, zt):
        pts = [(PX, root_le, z0), (PX + sign * span, tip_le, zt),
               (PX + sign * span, tip_te, zt), (PX, root_te, z0)]
        out = []
        for i, a in enumerate(pts):
            b = pts[(i + 1) % len(pts)]
            out.append(face(poly([p_(*a), p_(*b), p_(b[0], b[1], b[2] - 0.018),
                                  p_(a[0], a[1], a[2] - 0.018)]), FACE_L))
        out.append(face(poly([p_(*pt) for pt in pts]), FACE_TOP))
        return out

    def jet_engine(sign):
        ex = PX + sign * 0.62
        # A short swept pylon enters the wing and the nacelle crown. The
        # intake sits just ahead of the local leading edge, not beside the nose.
        out = slab_x(ex - 0.022, 0.044,
                     [(-1.12, 0.48), (-1.24, 0.62), (-1.14, 0.62), (-1.02, 0.48)])
        out += cone(ex, -1.19, 0.38, 'y', 0.08, 0.065, 0.112, cap=None)
        out += cyl(ex, -1.11, 0.38, 'y', 0.25, 0.112, crown=False, far=False)
        out.append(disc(ex, -0.86, 0.38, 0.089, 'y', DARK))
        out.append(disc(ex, -0.86, 0.38, 0.024, 'y', ACCENT))
        return out

    for gx in (PX - 0.23, PX + 0.23):
        out += box(gx - 0.015, -1.15, 0.26, 0.03, 0.035, 0.295)
        out += wheel(gx + 0.012, -1.13, 0.26, 0.06, 0.045, 'x')
    out += box(PX - 0.014, -0.11, 0.245, 0.028, 0.035, 0.29)
    out += wheel(PX + 0.012, -0.09, 0.245, 0.045, 0.04, 'x')

    # The fuselage is painted over both low wing roots and tail roots. Their
    # concealed attachment edges must not run across the cabin like a board.
    for sign in (-1, 1):
        out += jet_engine(sign)
        out += wing(sign, 1.08, -0.77, -1.34, -1.38, -1.54, 0.57, 0.63)
        out.append(face(poly([p_(PX + sign * 1.08, -1.38, 0.63),
                              p_(PX + sign * 1.11, -1.45, 0.78),
                              p_(PX + sign * 1.11, -1.55, 0.78),
                              p_(PX + sign * 1.08, -1.54, 0.63)]), FACE_R))
        out += wing(sign, 0.41, -1.89, -2.18, -2.11, -2.24, 0.71, 0.74)

    # One continuous loft silhouette avoids visible cylinder/cone joints.
    # Each circular station supplies both the shell and its window positions.
    stations = [(-2.35, 0.018, 0.70), (-2.16, 0.09, 0.68),
                (-1.87, FR, FZ), (-0.30, FR, FZ)]
    for i in range(1, 17):
        t = i / 16
        stations.append((-0.30 + 0.42 * t, FR * math.sqrt(1 - t * t),
                         FZ - 0.045 * t * t))

    def skin(yy, angle):
        for a, b in zip(stations, stations[1:]):
            if a[0] <= yy <= b[0]:
                t = (yy - a[0]) / (b[0] - a[0])
                radius = a[1] + t * (b[1] - a[1])
                zz = a[2] + t * (b[2] - a[2])
                theta = math.radians(angle)
                return p_(PX + radius * math.sin(theta), yy,
                          zz + radius * math.cos(theta))
        raise ValueError('Aircraft surface coordinate is outside the fuselage')

    points = sorted(set(skin(yy, i * 5) for yy, _, _ in stations for i in range(72)))

    def turn(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    hull = []
    for ordered in (points, points[::-1]):
        half = []
        for pt in ordered:
            while len(half) >= 2 and turn(half[-2], half[-1], pt) <= 0:
                half.pop()
            half.append(pt)
        hull.extend(half[:-1])
    shell = poly(hull)
    out.append(face(shell, FACE_L))
    cockpit_clip = f'{gid}-cockpit'
    out.append(f'<clipPath id="{cockpit_clip}">' + face(shell, FACE_TOP) + '</clipPath>')
    out.append(f'<g clip-path="url(#{cockpit_clip})">')
    # Continuous, unstroked skin sectors describe a round body with a white
    # crown and a shaded flank. There are no false longitudinal panel seams.
    crown = [skin(yy, -45) for yy, _, _ in stations]
    crown += [skin(yy, 45) for yy, _, _ in reversed(stations)]
    out.append(face(poly(crown), FACE_TOP).replace('/>', ' stroke="none"/>'))
    # Short front panes wrap onto the rounded shoulder, with one compact side
    # pane behind them; all glazing stays inside the shared airframe skin.
    def glazed_window(params):
        # A silhouette clip alone also shows glass from the BACK of a curved
        # nose. Clip in surface coordinates against the viewing direction so
        # a hidden far corner cannot fold forward into an upright dark spike.
        def visibility(q):
            yy, theta = q[0], math.radians(q[1])
            for a, b in zip(stations, stations[1:]):
                if a[0] <= yy <= b[0]:
                    dr = (b[1] - a[1]) / (b[0] - a[0])
                    dz = (b[2] - a[2]) / (b[0] - a[0])
                    return math.sin(theta) + (1 - dz) * math.cos(theta) - dr - 0.10
            raise ValueError('Window outside aircraft skin')

        clipped = []
        for a, b in zip(params[-1:] + params[:-1], params):
            va, vb = visibility(a), visibility(b)
            if (va >= 0) != (vb >= 0):
                lo, hi = 0.0, 1.0
                for _ in range(30):
                    t = (lo + hi) / 2
                    q = tuple(x + (y - x) * t for x, y in zip(a, b))
                    if (visibility(q) >= 0) == (va >= 0):
                        lo = t
                    else:
                        hi = t
                clipped.append(tuple(x + (y - x) * (lo + hi) / 2 for x, y in zip(a, b)))
            if vb >= 0:
                clipped.append(b)
        return face(poly([skin(*q) for q in clipped]), DARK) if len(clipped) >= 3 else ''

    for sign in (-1, 1):
        out.append(glazed_window([(-0.025, sign * 6), (-0.19, sign * 50),
                                 (-0.145, sign * 69), (0.015, sign * 7)]))
    out.append(face(poly([skin(-0.31, 52), skin(-0.205, 52),
                          skin(-0.16, 70), skin(-0.30, 70)]), DARK))
    for i in range(9):
        yy = -1.66 + i * 0.14
        window = [skin(yy + 0.022 * math.cos(a), 72 + 9 * math.sin(a))
                  for a in (math.tau * j / 12 for j in range(12))]
        out.append(face(poly(window), DARK).replace('/>', ' stroke="none"/>'))
    out.append('</g>')
    out.append(face(shell, 'none'))
    # Unlike the low tailplanes, the vertical fin rises from the visible crown.
    # Its lower contour follows the loft instead of being swallowed by it.
    out += slab_x(PX - 0.018, 0.036,
                 [(-1.83, 0.855), (-2.10, 1.12), (-2.24, 1.12),
                  (-2.24, 0.75), (-2.16, 0.77), (-1.87, 0.855)])

    return out


def flotten():
    """Ship afloat beside the apron; aircraft, rail, truck and tracked excavator."""
    reset()
    gid = 'cf-ex-04'
    s0, s1, s2, s3 = [], [], [], []
    Z = 0.2                                                    # the apron's top

    s0 += plate(-2.95, -2.35, 0, 6.2, 5.1, Z)
    # Recessed water occupies the harbour corner of the shared site. The
    # ship ends at this waterline; there is no exposed keel or dry-dock cradle.
    WATER = Z + 0.01
    s0.append(quad_t(-2.95, -2.35, WATER, 2.9, 1.7, '#C5EBE2')
              .replace('/>', ' fill-opacity="0.45"/>'))
    # Small paired ripples on the water plane. Curves distinguish water from
    # the straight contours of the quay. The water uses the brand's Glas tint.
    for xx in (-2.65, -1.85, -1.05):
        for yy in (-1.09, -0.81):
            pts = [p_(xx + dx, yy + dy, WATER) for dx, dy in
                   ((0, 0), (0.12, -0.09), (0.22, 0.09), (0.34, 0))]
            s0.append('M%s %s C%s %s %s %s %s %s' % tuple(v for pt in pts for v in pt))
    RY = 0.25                                                  # clear water, road and aircraft silhouettes
    for i in range(9):
        xx = -2.45 + i * 0.44
        s0.append(line(p_(xx, RY - 0.36, Z), p_(xx, RY + 0.36, Z)))
    for yy in (RY - 0.2, RY + 0.2):                            # rails, 0.4 gauge,
        s0 += box(-2.55, yy - 0.03, Z, 3.95, 0.06, 0.05,       # centred on the
                  FACE_TOP, PLATE_L, PLATE_R)                  # gauge lines

    SY, BEAM = -2.3, 1.0
    KEEL, DECK = WATER, 0.8
    NF = SY + BEAM                                             # the near flank
    s1.append(face(poly([p_(-2.9, NF, DECK), p_(-2.6, NF, KEEL),
                         p_(-0.7, NF, KEEL), p_(-0.3, NF, DECK)]), FACE_L))
    s1.append(face(poly([p_(-0.7, SY, KEEL), p_(-0.3, SY, DECK),
                         p_(-0.3, NF, DECK), p_(-0.7, NF, KEEL)]), FACE_R))
    s1.append(quad_t(-2.9, SY, DECK, 2.6, BEAM, FACE_TOP))     # the deck
    s1.append(line(p_(-2.72, NF, 0.5), p_(-0.51, NF, 0.5)))
    s1.append(quad_t(-2.8, SY + 0.06, DECK, 2.42, BEAM - 0.12))  # bulwark
    s1 += box(-2.55, SY + 0.16, DECK, 0.56, 0.68, 0.4)         # accommodation
    s1 += box(-2.47, SY + 0.24, DECK + 0.4, 0.4, 0.52, 0.26)   # bridge
    s1.append(quad_y(SY + 0.76, -2.4, DECK + 0.5, 0.26, 0.13, DARK))
    s1 += box(-2.37, SY + 0.32, DECK + 0.66, 0.18, 0.26, 0.24)  # funnel
    STK_X, STK_Y = -1.85, SY + 0.06                            # the stack: 2 x 2
    for tier in (DECK, DECK + CT_H):
        s1 += container(STK_X, STK_Y, tier)
        s1 += container(STK_X, STK_Y + CT_W, tier)
    s1.append(line(p_(-0.62, SY + 0.34, DECK + 0.54), p_(-0.62, SY + 0.46, DECK + 0.54)))
    s1 += box(-0.66, SY + 0.46, DECK, 0.08, 0.08, 0.72)        # mast
    s1.append(line(p_(-0.62, SY + 0.54, DECK + 0.54), p_(-0.62, SY + 0.66, DECK + 0.54)))

    s1 += place(fleet_aircraft, origin=(2.0, -0.65, Z), scale=1.25,
                offset=(0.1, 0.04, 0))

    RW = 0.7
    # G6-style shunter: three evenly spaced axles and a central cab between
    # two low hoods. The intermodal wagon retains its two two-axle bogies.
    for xx in (-2.08, -1.45, -0.82, -0.18, 0.14, 0.66, 0.98):
        s2 += wheel(xx, RY + 0.24, 0.4, 0.15, 0.06)
    for xx in (-2.3, -0.65):                                   # loco headstocks
        s2 += box(xx, RY - 0.3, 0.46, 0.1, 0.6, 0.12)
    s2 += box(-2.3, RY - RW / 2, 0.58, 1.75, RW, 0.12)         # loco underframe
    s2 += box(-2.2, RY - 0.26, 0.7, 0.64, 0.52, 0.42)        # engine hood
    s2.append(line(p_(-1.85, RY + 0.26, 0.72), p_(-1.85, RY + 0.26, 1.09)))
    s2.append(quad_y(RY + 0.26, -2.13, 0.93, 0.18, 0.14, ACCENT))
    s2 += box(-1.56, RY - RW / 2, 0.7, 0.56, RW, 0.74)        # central cab
    s2 += box(-1.6, RY - 0.39, 1.44, 0.64, 0.78, 0.04)       # thin roof overhang
    s2.append(quad_x(-1.0, RY - 0.26, 1.12, 0.52, 0.24, DARK))
    s2.append(quad_y(RY + RW / 2, -1.48, 1.12, 0.4, 0.24, DARK))
    s2.append(line(p_(-1.27, RY + RW / 2, 1.12), p_(-1.27, RY + RW / 2, 1.36)))
    s2.append(quad_y(RY + RW / 2, -1.47, 0.77, 0.24, 0.27))   # access door
    s2 += box(-1.0, RY - 0.26, 0.7, 0.35, 0.52, 0.37)        # shorter front hood
    s2.append(quad_x(-0.65, RY - 0.17, 0.85, 0.34, 0.13, ACCENT))
    for xx in (-1.54, -1.1):
        s2 += box(xx, RY - 0.1, 1.48, 0.055, 0.07, 0.16)    # roof equipment
    for xa, xb in ((-2.24, -1.69), (-0.93, -0.62)):
        for xx in (xa, xb):
            s2 += box(xx, RY + 0.32, 0.7, 0.025, 0.025, 0.19)
        s2.append(line(p_(xa, RY + 0.345, 0.89), p_(xb + 0.025, RY + 0.345, 0.89)))
    for yy in (RY - 0.22, RY + 0.22):                         # paired buffer heads
        s2 += cyl(-0.58, yy, 0.53, 'x', 0.12, 0.045, cap=ACCENT)
    for xx in (-0.4, 1.12):                                    # wagon headstocks
        s2 += box(xx, RY - 0.3, 0.46, 0.08, 0.6, 0.12)
    s2 += box(-0.4, RY - 0.32, 0.58, 1.6, 0.64, 0.12)          # the flat wagon
    s2 += box(-0.52, RY - 0.035, 0.49, 0.18, 0.07, 0.06)      # coupled vehicles
    for xa in (-0.22, 0.62):
        s2 += box(xa, RY + 0.24, 0.45, 0.4, 0.07, 0.06)      # bogie side frame
    s2 += container(-0.15, RY - 0.22, 0.7)                     # centred on it

    # Enlarge about the ground plane, then shift right to preserve a visible
    # gap from the rails and excavator bucket without enlarging the apron.
    s3 += fleet_excavator(-2.75, 1.25)
    s3 += place(lambda: fleet_semi(0.3, 1.9), origin=(3.0, 1.9, Z), scale=1.18,
                offset=(0.22, -0.19, 0))

    crop = bbox(30.0)

    ghost = []

    orbits = []

    LC = (STK_X, STK_Y + CT_W, DECK + 2 * CT_H)
    lid = [(LC[0], LC[1], LC[2]), (LC[0] + CT_L, LC[1], LC[2]),
           (LC[0] + CT_L, LC[1] + CT_W, LC[2]), (LC[0], LC[1] + CT_W, LC[2])]
    light = light_quad(gid, lid)
    la, lb = lime_span_quad(lid)
    nodes = light_nodes_quad(lid)
    return assemble(gid, la, lb, [(0, s0), (1, s1), (2, s2), (3, s3)],
                    light, nodes, ghost, orbits, crop=crop)



OBJECTS = (('01-maschinenbau', maschinenbau), ('02-anlagen', anlagen),
           ('03-erneuerbare', erneuerbare), ('04-flotten', flotten))


def validate_symmetry(svg):
    """Keep the four highlight nodes equal and centrally symmetric."""
    import xml.etree.ElementTree as ET

    root = ET.fromstring(svg)
    nodes = root.findall('.//{http://www.w3.org/2000/svg}circle[@class="cf-iso__node"]')
    if len(nodes) != 4 or len({node.get('r') for node in nodes}) != 1:
        raise ValueError('Each highlight needs four equally sized corner nodes')
    for axis in ('cx', 'cy'):
        values = [float(node.get(axis)) for node in nodes]
        if abs(values[0] + values[2] - values[1] - values[3]) > 0.025:
            raise ValueError('Opposing highlight nodes must share one centre')


def main():
    """Generate assets and keep the authored pages and browser gallery in sync."""
    import argparse
    import re
    from pathlib import Path

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail if assets or page drawings are stale')
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    root = here.parent.parent
    drawings = [fn() for _, fn in OBJECTS]
    for drawing in drawings:
        validate_symmetry(drawing)
    outputs = {here / (name + '.svg'): svg + '\n'
               for (name, _), svg in zip(OBJECTS, drawings)}
    for path in (root / 'design-system/patterns/expertise.html',
                 root / 'design-system/prototypes/expertise-scroll.html',
                 here / 'preview.html'):
        page = str(path.relative_to(root))
        source = path.read_text()
        seen = set()

        def replace(match):
            if not re.search(r'id="cf-ex-0[1-4]"', match[0]):
                return match[0]
            index = int(re.search(r'id="cf-ex-0([1-4])"', match[0])[1]) - 1
            if index in seen:
                raise ValueError(f"{page}: duplicate expertise drawing {index + 1}")
            seen.add(index)
            return drawings[index].replace('\n', '\n                ')

        outputs[path] = re.sub(r'<svg\b[^>]*>.*?</svg>', replace, source, flags=re.S)
        if seen != {0, 1, 2, 3}:
            raise ValueError(f'{page}: expected four distinct expertise drawings, found {seen}')
    stale = [p for p, content in outputs.items() if not p.exists() or p.read_text() != content]
    if args.check:
        for path in stale:
            print(f'STALE {path.relative_to(root)}')
        return bool(stale)
    for path in stale:
        path.write_text(outputs[path])
    for (name, _), svg in zip(OBJECTS, drawings):
        count = len(re.findall(r'<(?:path|ellipse|circle)\b', svg))
        print(f'{name}: {count} elements')
    return False


if __name__ == '__main__':
    raise SystemExit(main())
