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

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from isolib import (  # noqa: E402
    p_, line, box, plate, quad_t, quad_x, quad_y, seams,
    disc, hoop, cyl, taper, node, orbit, trace, light_quad, light_disc,
    assemble, reset, FACE_TOP, FACE_L, FACE_R, PLATE_L, PLATE_R,
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
    """A generator set on a skid: engine, coupling, generator, switchgear.
    Rotating assets are the densest telemetry in the portfolio, so this is the
    object that carries the most machined detail."""
    reset()
    gid = 'cf-ex-01'
    s0, s1, s2, s3 = [], [], [], []

    # ---- 0 · the skid
    s0 += foundation(-2.7, -1.95, 5.4, 3.9, 0.22, 0.18, 2, 1)
    for yy in (-1.5, 1.14):                                    # sole rails
        s0 += box(-2.4, yy, 0.22, 4.8, 0.36, 0.14, FACE_TOP, PLATE_L, PLATE_R)

    # ---- 1 · the back band: switchgear, then the engine
    s1 += box(1.35, -1.8, 0.22, 1.0, 0.55, 1.3)                # switchgear cabinet
    s1 += seams((1.35, -1.25, 0.28), (1.35, -1.25, 1.46),      # door leaves
                (2.35, -1.25, 0.28), (2.35, -1.25, 1.46), 1)
    s1.append(quad_y(-1.25, 1.45, 1.06, 0.35, 0.3, DARK))      # louvres
    s1.append(quad_y(-1.25, 1.9, 1.06, 0.35, 0.3, DARK))
    s1.append(quad_x(2.35, -1.75, 0.34, 0.45, 0.12, ACCENT))   # terminal slot

    s1 += box(-2.25, -1.2, 0.36, 1.95, 2.4, 1.15)              # engine block
    s1.append(line(p_(-2.25, 1.2, 0.86), p_(-0.3, 1.2, 0.86)))     # crankcase joint
    s1.append(line(p_(-0.3, 1.2, 0.86), p_(-0.3, -1.2, 0.86)))
    s1 += seams((-2.25, 1.2, 0.36), (-0.3, 1.2, 0.36),         # bay divisions
                (-2.25, 1.2, 1.51), (-0.3, 1.2, 1.51), 4)
    s1.append(quad_y(1.2, -2.05, 0.98, 0.4, 0.4, FACE_TOP))    # access door
    s1.append(quad_y(1.2, -1.94, 1.09, 0.18, 0.18, DARK))      # sight glass
    s1.append(quad_y(1.2, -0.95, 0.48, 1.5, 0.22, ACCENT))     # oil gallery

    for i in range(4):                                         # cylinder heads
        s1 += box(-2.1 + i * 0.45, -0.95, 1.51, 0.32, 1.9, 0.3)
        s1.append(line(p_(-2.1 + i * 0.45 + 0.16, -0.95, 1.81),
                       p_(-2.1 + i * 0.45 + 0.16, 0.95, 1.81)))
    s1 += box(-2.15, -0.28, 1.81, 1.78, 0.56, 0.16)            # valve cover
    s1 += cyl(-1.9, 0.0, 1.97, 'z', 0.95, 0.22)                # exhaust riser
    for zz in (2.28, 2.62):
        s1.append(hoop(-1.9, 0.0, zz, 0.22, 'z'))
    s1 += cyl(-1.9, 0.0, 2.92, 'z', 0.12, 0.26, side=FACE_L)   # stack collar

    # ---- 2 · the middle band: coupling and generator
    s2 += box(-0.38, -0.78, 0.36, 0.68, 1.56, 1.7)             # drive-end housing
    s2 += seams((-0.38, 0.78, 0.36), (0.3, 0.78, 0.36),
                (-0.38, 0.78, 2.06), (0.3, 0.78, 2.06), 2)
    s2.append(quad_t(-0.28, -0.68, 2.06, 0.48, 1.36))
    for xx in (0.45, 1.6):                                     # generator pedestals
        s2 += box(xx, -0.75, 0.36, 0.5, 1.5, 0.2, FACE_TOP, PLATE_L, PLATE_R)
    # far=False: this end runs into the housing, so it has no visible cap
    s2 += cyl(0.3, 0.0, 1.28, 'x', 2.0, 0.72, far=False)
    for i in range(7):                                         # cooling ribs
        s2.append(hoop(0.52 + i * 0.24, 0.0, 1.28, 0.72, 'x'))
    # ---- 3 · the fittings, nearest of all
    s3.append(hoop(2.3, 0.0, 1.28, 0.58, 'x'))                 # end flange
    s3 += box(0.95, -0.34, 1.88, 0.7, 0.68, 0.32)              # terminal box
    s3.append(quad_t(1.06, -0.23, 2.2, 0.48, 0.46, ACCENT))

    ghost = [disc(1.3, 0.0, 1.28, 0.46, 'x')]                  # the rotor, x-ray
    light = light_disc(gid, 2.3, 0.0, 1.28, 0.5, 'x')
    la, lb = lime_span((2.3, -0.5, 1.78), (2.3, 0.5, 0.78))
    nodes = [node(2.3, 0.0, 1.28), node(-1.9, 0.0, 3.04, 3), node(1.3, 0.0, 2.2, 3)]
    traces = [trace((-4.0, 1.35, 0.22), (-2.7, 1.35, 0.22))]
    return assemble(gid, la, lb, [(0, s0), (1, s1), (2, s2), (3, s3)],
                    light, nodes, traces, ghost)


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
