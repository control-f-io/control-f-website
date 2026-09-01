"""Shared isometric drawing library — Control-F expertise objects, v3.

THE PROJECTION.  +x is 26.57 deg down-right, +y is 26.57 deg down-left, +z is
vertical.  Every vertex comes from a lattice coordinate, so every edge lands on
a brand angle by construction.  One lattice cell is 2*U wide and U tall.

THE TONE.  The three-grey register of foundations/illustration.html, "Contour
and fill": #DADADA facing the sky, CF-Grau #CFCFCF on the lit side — which is
also the top of the page wash, so an unlit face sits at the page's own colour
and the contour alone carries it — and #C4C4C4 turned away.  These four objects
shipped for a while in a near-white register of their own, with two dark accent
values for slots and apertures and a paler trio for the foundation, on the
argument that a dense drawing in three mid greys reads as clip art.  The
reference plates the register was re-measured against on 2026-09-01 say
otherwise: the same three values on a CF-Grau ground, the object sunk into the
page rather than lifted off it, one lit top face running the whole ramp from
lime at its back corner to the ground's own grey at its near one, and two
nodes on that face.  So the foundation is the same material as the machine, an
accent is the shaded value and nothing is darker than that, and DETAIL STILL
COMES FROM LINES drawn on the faces rather than from tone.

THE CURVES ARE COMPUTED, NOT APPROXIMATED.  A circle of radius r lying in any
lattice plane projects to an ellipse whose two semi-axes and rotation fall out
of the singular values of the 2x3 projection restricted to that plane.  _ell()
does that once and every drum, hoop, wheel, flange and rotor in the four
objects is exact rather than eyeballed.  The same maths gives the tangent
points where a cylinder's silhouette leaves its end caps, which is what makes
cyl() a real cylinder in any of the three axes instead of a box with a lid.

NOTHING PIERCES THE PLATE.  Everything that stands on the foundation stands on
it — a mast is a slender box, not a line, and a line that would run into the
plate is not drawn.  Hairlines that ended inside the plate are exactly what
read as brittle at stage size.
"""

import math

U = 56.0
H = 56.0
OX, OY = 320.0, 372.0

# ---- the palette: the three-grey register, and nothing off it. ACCENT and
# DARK are kept as names so a slot or an aperture is still declared as one at
# the call site, but both resolve to the shaded value: a recess is a face
# turned away from the light, and the register has no fourth grey to spend.
FACE_TOP = '#DADADA'      # facing the sky
FACE_R = '#CFCFCF'        # the +x face, lit — CF-Grau, the page's own ground
FACE_L = '#C4C4C4'        # the +y face, turned away
PLATE_TOP = FACE_TOP      # a foundation is the same material as what stands on it
PLATE_R = FACE_R
PLATE_L = FACE_L
ACCENT = FACE_L           # a slot, a gap, a recess
DARK = FACE_L             # an aperture

# Screen images of the three unit lattice directions.
VX = (U, U / 2.0)
VY = (-U, U / 2.0)
VZ = (0.0, -H)
# Cyclic pairs: for an axis, the two in-plane directions in an order that puts
# the visible half of a cylinder at theta in [-45, 135] for all three axes.
_PLANE = {'x': (VY, VZ), 'y': (VZ, VX), 'z': (VX, VY)}
_AXIS = {'x': VX, 'y': VY, 'z': VZ}
_STEP = {'x': (1, 0, 0), 'y': (0, 1, 0), 'z': (0, 0, 1)}

_PTS = []


def reset():
    _PTS.clear()


def P(x, y, z=0.0):
    p = (OX + (x - y) * U, OY + (x + y) * U / 2.0 - z * H)
    _PTS.append(p)
    return p


def p_(x, y, z=0.0):
    """P without registering the point — for construction, not for the crop."""
    return (OX + (x - y) * U, OY + (x + y) * U / 2.0 - z * H)


def f(v):
    s = f"{v:.2f}".rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def poly(pts):
    return "M" + " ".join(f"{f(a)} {f(b)}" for a, b in pts) + "Z"


def line(a, b):
    return f"M{f(a[0])} {f(a[1])} {f(b[0])} {f(b[1])}"


def face(d, fill):
    return f'<path d="{d}" fill="{fill}"/>'


# ---------------------------------------------------------------- boxes
def box_faces(x, y, z, dx, dy, dz):
    t = poly([P(x, y, z + dz), P(x + dx, y, z + dz), P(x + dx, y + dy, z + dz), P(x, y + dy, z + dz)])
    l = poly([P(x, y + dy, z + dz), P(x + dx, y + dy, z + dz), P(x + dx, y + dy, z), P(x, y + dy, z)])
    r = poly([P(x + dx, y, z + dz), P(x + dx, y + dy, z + dz), P(x + dx, y + dy, z), P(x + dx, y, z)])
    return t, l, r


def box(x, y, z, dx, dy, dz, top=FACE_TOP, sl=FACE_L, sr=FACE_R):
    """A cuboid, painted back to front. Depth is overlap, never a shadow."""
    t, l, r = box_faces(x, y, z, dx, dy, dz)
    out = []
    if sl:
        out.append(face(l, sl))
    if sr:
        out.append(face(r, sr))
    if top:
        out.append(face(t, top))
    return out


def plate(x, y, z, dx, dy, dz):
    return box(x, y, z, dx, dy, dz, PLATE_TOP, PLATE_L, PLATE_R)


# ---------------------------------------------------------------- panels on a face
def quad_t(x, y, z, dx, dy, fill=None):
    """A rectangle lying on the horizontal plane z."""
    d = poly([P(x, y, z), P(x + dx, y, z), P(x + dx, y + dy, z), P(x, y + dy, z)])
    return face(d, fill) if fill else d


def quad_x(xc, y, z, dy, dz, fill=None):
    """A rectangle on the vertical face at constant x."""
    d = poly([P(xc, y, z), P(xc, y + dy, z), P(xc, y + dy, z + dz), P(xc, y, z + dz)])
    return face(d, fill) if fill else d


def quad_y(yc, x, z, dx, dz, fill=None):
    """A rectangle on the vertical face at constant y."""
    d = poly([P(x, yc, z), P(x + dx, yc, z), P(x + dx, yc, z + dz), P(x, yc, z + dz)])
    return face(d, fill) if fill else d


# ---------------------------------------------------------------- profiles
# A BOX CANNOT SAY "RAKED", and four of the five machines in the fleet object
# are shaped by exactly one sloped edge: a ship's stem, a fin's leading edge, a
# crawler track's idler ramp, a boom. Drawn as boxes they are the same drawing
# five times, which is what the first fleet object was.
#
# THE SLOPES ARE STILL BRAND ANGLES, and that is a constraint on the numbers
# rather than on the primitive. In a vertical plane a step (dx, dz) lands on
# screen slope 0.5 - dz/dx, so dz/dx of 1, 1.5 and 2.5 give 26.57, 45 and 63.43
# degrees and nothing else does — a "natural-looking" 40-degree boom is off the
# system's five angles as surely as a horizontal rule is. Same numbers on the
# +y side, mirrored. Every profile in objects.py is written from that table.
#
# THE STRIPS ARE PAINTED FIRST AND ALL OF THEM. Extruding a profile toward the
# reader, an edge whose outward normal points away from the viewer extrudes INTO
# the near face and is covered by it; one that points toward the viewer extrudes
# clear of it and shows. So there is no visibility test to get wrong: emit every
# edge's strip, then paint the near face over the lot, and what remains is
# exactly the silhouette.
#
# THE TONE IS COMPUTED FROM THE NORMAL, and that is not a convenience. The
# register has three values and they mean three DIRECTIONS — sky, lit, turned
# away — so a sloped strip's tone is a fact about its normal, not a choice at
# the call site. It is also the one thing hand-assignment gets wrong silently:
# a member steeper than the camera's own 45 deg shows its UNDERSIDE and hides
# its top (the top face's normal is (-dz, 0, dx), which turns away exactly when
# dz > dx), so the excavator's boom was written with its top lit and painted its
# underside with the sky tone. Nothing rendered wrong; it just read as tin.
def _tone(n, away):
    """`n` is (across, up) — the strip's outward normal in its own plane."""
    if n[1] > abs(n[0]):
        return FACE_TOP
    return FACE_R if n[0] > 0 else away


def _extrude(pts_a, pts_b, prof, strips, side, away, flip=False):
    # Shoelace on the profile: the sign says which of an edge's two normals
    # points out of the body, and every strip's tone depends on that.
    #
    # BACK STRIPS PAINT FIRST. A strip whose outward normal turns away from the
    # camera lies behind the prism's own visible faces (every profile in here is
    # convex), but strips were emitted in profile order — a back-facing heel cap
    # could land AFTER the visible face beside it and overpaint it. They cannot
    # be skipped: their far edges are the silhouette's far boundary. So they go
    # first, the visible strips and the near face over them. `flip` is for
    # slab_x, whose profile frame negates its first axis.
    s = sum(prof[i][0] * prof[(i + 1) % len(prof)][1] - prof[(i + 1) % len(prof)][0] * prof[i][1]
            for i in range(len(prof)))
    back, front = [], []
    for i in range(len(pts_a)):
        j = (i + 1) % len(pts_a)
        d = poly([pts_a[i], pts_a[j], pts_b[j], pts_b[i]])
        e = (prof[j][0] - prof[i][0], prof[j][1] - prof[i][1])
        nrm = (e[1], -e[0]) if s > 0 else (-e[1], e[0])
        if strips is None:
            tone = _tone(nrm, away)
        else:
            tone = strips[i] if isinstance(strips, (list, tuple)) else strips
        toward = (-nrm[0] if flip else nrm[0]) + nrm[1]
        (front if toward > 1e-9 else back).append(face(d, tone))
    return back + front + [face(poly(pts_b), side)]


def slab_y(y, w, pts, side=FACE_L, strips=None):
    """A profile in the vertical plane at constant y — pts are (x, z) — given a
    thickness w along +y. The near face is the +y one, so it takes the shaded
    tone; the strips take theirs from their own normals."""
    return _extrude([P(x, y, z) for x, z in pts],
                    [P(x, y + w, z) for x, z in pts], pts, strips, side, FACE_L)


def slab_x(x, w, pts, side=FACE_R, strips=None):
    """The same, in the vertical plane at constant x — pts are (y, z) — with the
    thickness on +x, so the near face is the lit one. A strip across this plane
    can only face the sky or one of the two flanks, and +y is the shaded one."""
    return _extrude([P(x, y, z) for y, z in pts],
                    [P(x + w, y, z) for y, z in pts],
                    [(-a, b) for a, b in pts], strips, side, FACE_L, flip=True)


def seams(a, b, c, d, n):
    """n evenly spaced lines across the strip a->b / c->d (lattice triples)."""
    out = []
    for i in range(1, n + 1):
        t = i / (n + 1.0)
        pa = tuple(a[k] + (b[k] - a[k]) * t for k in range(3))
        pb = tuple(c[k] + (d[k] - c[k]) * t for k in range(3))
        out.append(line(p_(*pa), p_(*pb)))
    return out


def ladder(x, y, axis, z0, z1, w, n):
    """Two stiles and n rungs on a vertical plane — the detail that tells a
    reader how big a vessel is. `axis` is the lattice direction it spreads on."""
    s = _STEP[axis]
    a = (x, y, z0)
    b = (x + s[0] * w, y + s[1] * w, z0)
    out = [line(p_(*a), p_(a[0], a[1], z1)), line(p_(*b), p_(b[0], b[1], z1))]
    for i in range(n):
        t = (i + 0.5) / n
        zz = z0 + (z1 - z0) * t
        out.append(line(p_(a[0], a[1], zz), p_(b[0], b[1], zz)))
    return out


# ---------------------------------------------------------------- curves
def _ell(a, b, r):
    """Semi-axes and rotation of the ellipse a unit circle spanned by screen
    vectors a, b projects to, scaled by r. Left singular values of [a b]."""
    ax, ay = a[0] * r, a[1] * r
    bx, by = b[0] * r, b[1] * r
    n11 = ax * ax + bx * bx
    n12 = ax * ay + bx * by
    n22 = ay * ay + by * by
    tr = n11 + n22
    dd = math.sqrt(max((n11 - n22) ** 2 / 4.0 + n12 * n12, 0.0))
    l1, l2 = tr / 2.0 + dd, tr / 2.0 - dd
    rx, ry = math.sqrt(max(l1, 0.0)), math.sqrt(max(l2, 0.0))
    if abs(n12) < 1e-9:
        ang = 0.0 if n11 >= n22 else 90.0
    else:
        ang = math.degrees(math.atan2(l1 - n11, n12))
    return rx, ry, ang


def _ell_tag(c, rx, ry, ang, fill, cls=None, extra=''):
    ct, st = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    hw = math.hypot(rx * ct, ry * st)
    hh = math.hypot(rx * st, ry * ct)
    _PTS.extend([(c[0] - hw, c[1] - hh), (c[0] + hw, c[1] + hh)])
    k = f' class="{cls}"' if cls else ''
    t = f' transform="rotate({f(ang)} {f(c[0])} {f(c[1])})"' if abs(ang) > 1e-6 else ''
    return (f'<ellipse{k} cx="{f(c[0])}" cy="{f(c[1])}" rx="{f(rx)}" ry="{f(ry)}"{t} '
            f'fill="{fill or "none"}"{extra}/>')


def disc(x, y, z, r, axis='z', fill=None, cls=None):
    """A circle of radius r in the plane normal to `axis`, drawn exact."""
    a, b = _PLANE[axis]
    rx, ry, ang = _ell(a, b, r)
    return _ell_tag(p_(x, y, z), rx, ry, ang, fill, cls)


def _on(c, a, b, r, t):
    """The point at parameter t (degrees) of the circle of radius r in the
    plane (a, b), centred on the screen point c."""
    u = math.radians(t)
    return (c[0] + math.cos(u) * a[0] * r + math.sin(u) * b[0] * r,
            c[1] + math.cos(u) * a[1] * r + math.sin(u) * b[1] * r)


def _arc(c, a, b, r, t0, t1):
    """One SVG `A` command for the TRUE arc from t0 to t1 — the ellipse, not a
    chain of chords across it.

    _ell() already gives the projected circle exactly, and disc() has always
    emitted it as an <ellipse>. Every OPEN arc in the library went out as a
    polyline instead: a hoop as fourteen segments, a crown band as eight. At
    the sizes the four objects shipped at that was under a pixel and invisible;
    at the generator drum's radius the band's segments are 22.5 deg apart and
    the sagitta is a full CSS pixel, so the one contour that runs the length of
    the focal element arrives with eight flats in it. The header of this file
    says the curves are computed and not approximated. They are now.

    The sweep flag is DERIVED, not guessed. A point p on the ellipse has
    parameter phi = atan2(p.v / ry, p.u / rx) in the frame rotate(ang)
    establishes, and SVG's sweep = 1 is the direction of increasing phi — so
    taking phi at the two ends and at the parametric midpoint says which way
    round the browser has to go, and how far, for any t0, t1 and any of the
    three lattice planes."""
    rx, ry, ang = _ell(a, b, r)
    ct, st = math.cos(math.radians(ang)), math.sin(math.radians(ang))

    def phi(p):
        dx, dy = p[0] - c[0], p[1] - c[1]
        return math.atan2((-dx * st + dy * ct) / ry, (dx * ct + dy * st) / rx)

    p0, p1 = _on(c, a, b, r, t0), _on(c, a, b, r, t1)
    pm = _on(c, a, b, r, (t0 + t1) / 2.0)
    tau = 2.0 * math.pi
    f0 = phi(p0)
    dpos, dmid = (phi(p1) - f0) % tau, (phi(pm) - f0) % tau
    sweep = 1 if dmid < dpos else 0
    span = dpos if sweep else tau - dpos
    # A HALF-TURN IS NEITHER ARC, and it is the common case: every hoop and
    # every far end is exactly 180 deg. At span == pi both flags draw the same
    # curve, but `span > pi` on a value that is pi to the last ulp is a coin
    # toss decided by the platform's libm — regenerated on another machine,
    # two of the four shipped files came back with eleven flags flipped and
    # nothing changed on screen. The README says the same paths come out every
    # run; the tolerance is what makes that true.
    large = 1 if span > math.pi + 1e-9 else 0
    return p0, p1, f'A{f(rx)} {f(ry)} {f(ang)} {large} {sweep} {f(p1[0])} {f(p1[1])}'


def hoop(x, y, z, r, axis='z', t0=-45.0, t1=135.0):
    """The visible half of a circle wrapped round a cylinder: a rib, a band, a
    weld seam. Only the half that faces the viewer, the way a draughtsman
    would draw it — the far half is inside the body."""
    a, b = _PLANE[axis]
    c = p_(x, y, z)
    p0, p1, arc = _arc(c, a, b, r, t0, t1)
    _PTS.extend([p0, p1])
    return f'M{f(p0[0])} {f(p0[1])}{arc}'


# The default tone of a tube, and the quarter of it that catches the light.
# A cylinder filled in ONE flat tone is a plank with scalloped ends: the pipe
# rack read as a diagonal ramp until the tubes were given their crown. The
# band runs from the silhouette edge to the 45 deg generatrix, which is where
# a cuboid's own two visible faces meet — so a pipe and a beam lying next to
# each other are lit by the same rule.
_SIDE = {'x': FACE_L, 'y': FACE_R, 'z': FACE_R}
_CROWN = {'x': (45.0, 135.0, FACE_TOP), 'y': (-45.0, 45.0, FACE_TOP), 'z': (45.0, 135.0, FACE_L)}
# The near cap is a face in a plane of constant axis, so its tone is the
# register's value for THAT face: sky for a drum, the lit side for a run along
# +x, the shaded side for one along +y. It defaulted to the sky value for all
# three; maschinenbau() corrected it at the call site and said so, while the
# motor, the pump, both exchangers and both pipe runs on anlagen() kept
# sky-toned end faces pointing at the reader. `cap='auto'` reads this table.
_CAP = {'x': FACE_R, 'y': FACE_L, 'z': FACE_TOP}


def _band(c0, c1, a, b, r, t0, t1):
    q0, q1, arc0 = _arc(c0, a, b, r, t0, t1)
    s0, s1, arc1 = _arc(c1, a, b, r, t1, t0)
    _PTS.extend([q0, q1, s0, s1])
    return (f'M{f(q0[0])} {f(q0[1])}{arc0}L{f(s0[0])} {f(s0[1])}{arc1}Z')


def cyl(x, y, z, axis, length, r, side=None, cap='auto', cap_far=None,
        far=True, crown=True):
    """A finite cylinder along one lattice axis: far cap, tube, crown, near cap.
    The tube's edges leave the caps at the tangent points, so the silhouette is
    the true one and not a rectangle with two lids.

    cap='auto' tones the near cap for the plane it lies in (_CAP); None drops
    it, for a cylinder whose end something else is drawn on.

    far=False drops the far cap, for a cylinder that runs into a housing. The
    generator's did not, and its ellipse stood out past the coupling guard as a
    blob nobody could name.

    THE FAR END IS AN ARC, NOT A CHORD, and that is what the sentence above
    was claiming and not doing. The tube was a quadrilateral: two generatrices
    and two straight ends. The NEAR end never showed, because the near cap is
    painted over it — but the far cap is painted UNDER it, so its chord landed
    as a stroked straight line across the end of every cylinder in all four
    objects, the true arc still visible below it. A cylinder standing on
    something read as a lens with a bar across it; the generator drum got a
    56.31 deg line down its drive end that no edge of the machine explains.
    With far=False there is no cap to leave an arc on and no end to draw, so
    the flat cut stays — that IS the cut the housing hides."""
    a, b = _PLANE[axis]
    d = _AXIS[axis]
    s = _STEP[axis]
    if cap == 'auto':
        cap = _CAP[axis]
    c0 = p_(x, y, z)
    c1 = p_(x + s[0] * length, y + s[1] * length, z + s[2] * length)
    # theta where the tube's edge runs parallel to the axis
    ca = a[0] * d[1] - a[1] * d[0]
    cb = b[0] * d[1] - b[1] * d[0]
    th = math.atan2(cb, ca)
    off = []
    for t in (th, th + math.pi):
        off.append((math.cos(t) * a[0] * r + math.sin(t) * b[0] * r,
                    math.cos(t) * a[1] * r + math.sin(t) * b[1] * r))
    rx, ry, ang = _ell(a, b, r)
    base = side or _SIDE[axis]
    corners = [(c0[0] + off[0][0], c0[1] + off[0][1]),
               (c1[0] + off[0][0], c1[1] + off[0][1]),
               (c1[0] + off[1][0], c1[1] + off[1][1]),
               (c0[0] + off[1][0], c0[1] + off[1][1])]
    if far:
        # The far end closes over the half of its cap that is turned AWAY from
        # c1 — the silhouette. Which half that is falls out of the geometry:
        # take the two candidate midpoints and keep the one further from c1.
        td = math.degrees(th)

        def _away(e):
            m = _on(c0, a, b, r, (td + 180.0 + e) / 2.0)
            return math.hypot(m[0] - c1[0], m[1] - c1[1])

        end = max((td + 360.0, td), key=_away)
        _, _, arc = _arc(c0, a, b, r, td + 180.0, end)
        tube = ('M' + " ".join(f"{f(p[0])} {f(p[1])}" for p in corners) + arc + 'Z')
    else:
        tube = poly(corners)
    out = []
    if far:
        out.append(_ell_tag(c0, rx, ry, ang, cap_far or base))
    out.append(face(tube, base))
    if crown and r >= 0.14:
        t0, t1, tone = _CROWN[axis]
        out.append(face(_band(c0, c1, a, b, r, t0, t1), tone if crown is True else crown))
    if cap:
        out.append(_ell_tag(c1, rx, ry, ang, cap))
    return out


def drum(x, y, z, r, h, top=FACE_TOP, side=FACE_R):
    """A vertical cylinder. cyl(axis='z') with the reading order kept."""
    return cyl(x, y, z, 'z', h, r, side=side, cap=top)


def taper(x, y, z, r0, r1, h, top=FACE_TOP, side=FACE_R):
    """A frustum — a wind tower, a stack, a skirt. Same silhouette rule as a
    cylinder, with the tangent offset taken at each end's own radius."""
    a, b = _PLANE['z']
    bot, tp = p_(x, y, z), p_(x, y, z + h)
    rx0, ry0, _ = _ell(a, b, r0)
    rx1, ry1, _ = _ell(a, b, r1)
    body = (f'M{f(tp[0] - rx1)} {f(tp[1])}L{f(bot[0] - rx0)} {f(bot[1])}'
            f'A{f(rx0)} {f(ry0)} 0 0 0 {f(bot[0] + rx0)} {f(bot[1])}'
            f'L{f(tp[0] + rx1)} {f(tp[1])}'
            f'A{f(rx1)} {f(ry1)} 0 0 1 {f(tp[0] - rx1)} {f(tp[1])}Z')
    _PTS.extend([(bot[0] - rx0, bot[1] + ry0), (bot[0] + rx0, bot[1] + ry0),
                 (tp[0] - rx1, tp[1] - ry1), (tp[0] + rx1, tp[1] - ry1)])
    out = [face(body, side)]
    if top:
        out.append(_ell_tag(tp, rx1, ry1, 0.0, top))
    return out


def cone(x, y, z, axis, length, r0, r1, side=None, cap='auto', cap_far=None, far=True):
    """A frustum along one lattice axis: radius r0 at (x, y, z), the far end,
    and r1 at the near end `length` along the axis. taper() is this for the
    vertical axis, where the two silhouette lines are verticals; along +x or
    +y they are the two tangents from the projected APEX to the projected base
    circle, and the same two parameters cut the top circle, because a
    generator is a straight line through the apex and the projection is
    affine. Solved on the ellipse itself: with u(t) = c0 + cos t * a + sin t * b
    the tangent condition (u - q) x u' = 0 reduces to
    cos t * (w x b) - sin t * (w x a) = -(a x b), w = c0 - q, which is one
    cosine. r0 == r1 falls through to cyl().

    THE FAR END IS ALWAYS THE ARC, whether or not the far cap is painted: a
    frustum butted onto a cylinder shares that cylinder's cap, so `far=False`
    drops only the ellipse — a chord across the end would be exactly the bar
    cyl()'s own docstring was written against. An aircraft is the reason this
    exists: a fuselage that ends in a flat cap pointed at the reader is a drum,
    whatever is drawn on it."""
    if abs(r0 - r1) < 1e-9:
        return cyl(x, y, z, axis, length, r0, side=side, cap=cap, cap_far=cap_far,
                   far=far, crown=False)
    a, b = _PLANE[axis]
    s = _STEP[axis]
    if cap == 'auto':
        cap = _CAP[axis]
    base = side or _SIDE[axis]
    c0 = p_(x, y, z)
    c1 = p_(x + s[0] * length, y + s[1] * length, z + s[2] * length)
    k = r0 / (r0 - r1)
    q = (c0[0] + (c1[0] - c0[0]) * k, c0[1] + (c1[1] - c0[1]) * k)

    def x_(p, s_):
        return p[0] * s_[1] - p[1] * s_[0]

    ar, br = (a[0] * r0, a[1] * r0), (b[0] * r0, b[1] * r0)
    w = (c0[0] - q[0], c0[1] - q[1])
    wa, wb, ab = x_(w, ar), x_(w, br), x_(ar, br)
    rr = math.hypot(wa, wb)
    val = max(-1.0, min(1.0, -ab / rr))
    psi = math.atan2(wa, wb)
    t1 = math.degrees(-psi + math.acos(val))
    t2 = math.degrees(-psi - math.acos(val))
    p01, p02 = _on(c0, a, b, r0, t1), _on(c0, a, b, r0, t2)
    p11, p12 = _on(c1, a, b, r1, t1), _on(c1, a, b, r1, t2)

    def _away(e):
        m = _on(c0, a, b, r0, (t2 + e) / 2.0)
        return math.hypot(m[0] - c1[0], m[1] - c1[1])

    end = max((t1, t1 + 360.0, t1 - 360.0), key=_away)
    _, _, arc = _arc(c0, a, b, r0, t2, end)
    tube = ('M' + ' '.join(f'{f(p[0])} {f(p[1])}' for p in (p01, p11, p12, p02)) + arc + 'Z')
    _PTS.extend([p01, p02, p11, p12])
    rx0, ry0, ang0 = _ell(a, b, r0)
    rx1, ry1, ang1 = _ell(a, b, r1)
    out = []
    if far:
        out.append(_ell_tag(c0, rx0, ry0, ang0, cap_far or base))
    out.append(face(tube, base))
    if cap:
        out.append(_ell_tag(c1, rx1, ry1, ang1, cap))
    return out


def wheel(x, y, z, r, w=0.08, axis='y'):
    """A tyre: a short cylinder ending on the near flank — at `y` for axis 'y',
    a machine running down +x; at `x` for axis 'x', one running down +y — with
    its hub on the near cap. A wheel used to be a flat disc, which reads as a
    washer leaning against the body until it has a tread. Only the near flank
    is drawn on a low-slung machine, because its far wheels are behind its own
    frame from this camera; where the body is carried clear of them, as an
    aircraft's is, both are drawn and both show."""
    if axis == 'y':
        out = cyl(x, y - w, z, 'y', w, r)
    else:
        out = cyl(x - w, y, z, 'x', w, r)
    out.append(disc(x, y, z, r * 0.34, axis, FACE_TOP))
    return out


# The half-chord of a blade, as (fraction of span, half-chord in lattice units):
# a narrow root, the shoulder a fifth of the way out, and a tip that is still
# two contours wide at the size these objects ship at. Under about 0.016 the
# fill between the two contours closes up and the tip reads as a hairline.
_BLADE = ((0.0, 0.032), (0.18, 0.06), (1.0, 0.018))


def rotor(x, y, z, r0, r1, axis='x', n=3, phase=0.0, fill=FACE_R, prof=_BLADE):
    """The n blades of a rotor, in the lattice plane normal to `axis`.

    THE PLANE IS ON THE LATTICE. THE AZIMUTH CANNOT BE, and that is a fact
    about the geometry rather than a licence. A radius at parameter t in an
    x-plane projects to the screen slope tan(t) - 0.5, so each of the five
    brand slopes is hit by exactly one t per half-turn — and blades sit
    360/n apart. At most one of three can land on a brand angle, whatever
    `phase` is.

    So what `phase` is for is the failure that actually reads: a NEAR miss. A
    blade four degrees off horizontal looks like a horizontal somebody failed
    to draw; the same blade ten degrees off looks like a rotor that has turned.
    The value objects.py passes was picked by scanning all 120 distinct
    positions — the blade lines repeat every 360/(2n) — for the one whose worst
    blade is furthest from any brand angle, subject to none of the three being
    swallowed by the nacelle and none of them grazing the tower's silhouette
    instead of crossing it.

    The tips land exactly on r1, so an orbit() of the same radius over them is
    the circle they travel and not a second circle that looks like it."""
    a, b = _PLANE[axis]
    c = p_(x, y, z)

    def at(u, v):
        return (c[0] + u * a[0] + v * b[0], c[1] + u * a[1] + v * b[1])

    span = [(r0 + (r1 - r0) * s, w) for s, w in prof]
    out = []
    for i in range(n):
        t = math.radians(phase + i * 360.0 / n)
        ct, st = math.cos(t), math.sin(t)
        pts = [at(rr * ct - w * st, rr * st + w * ct) for rr, w in span]
        pts += [at(rr * ct + w * st, rr * st - w * ct) for rr, w in reversed(span)]
        _PTS.extend(pts)
        out.append(face(poly(pts), fill))
    return out


def orbit(x, y, z, r, axis='z'):
    """A ghost that CIRCULATES. The system's own distinction: a swept circle is
    a path something travels, not a state, and it carries .cf-iso__ghost in
    addition to .cf-iso__orbit rather than instead of it.

    IT IS THE PATH, NOT THE THING. This used to stand IN for the wind turbine's
    rotor, on the argument that three blades would be three edges on angles the
    lattice does not own. The argument is true about the edges and wrong about
    the drawing: a reader who cannot find blades cannot name a wind turbine,
    and being nameable at a glance is the whole job of an object at stage size.
    rotor() draws the blades; this draws the circle their tips travel, which is
    what an orbit was for in the first place."""
    a, b = _PLANE[axis]
    rx, ry, ang = _ell(a, b, r)
    return _ell_tag(p_(x, y, z), rx, ry, ang, None,
                    cls='cf-iso__ghost cf-iso__orbit', extra=' stroke-dasharray="1 4"')


def _node_tag(c, r):
    return (f'<circle class="cf-iso__node" cx="{f(c[0])}" cy="{f(c[1])}" r="{r}" '
            f'fill="#000" stroke="none"/>')


def node(x, y, z, r=3):
    """A construction point at a lattice point. r = 3 is what the illustration
    page gives a node on the lit face; these objects drew theirs at 4."""
    return _node_tag(P(x, y, z), r)


def _extremes(pts):
    """The highest and the rightmost of a set of screen points — the two
    corners the reference plates put a node on: where the lit face's far edges
    meet at the back, and where its right edge turns the corner. Nothing else
    in a plate carries one, so an object's nodes are the light's, not a list
    of things the copy mentions."""
    top = min(pts, key=lambda p: (p[1], p[0]))
    right = max(pts, key=lambda p: (p[0], -p[1]))
    return top, right


def light_nodes_quad(pts, r=3):
    """The two nodes of a lit quad. `pts` are the lattice triples that were
    handed to light_quad()."""
    return [_node_tag(c, r) for c in _extremes([P(*q) for q in pts])]


def light_nodes_disc(x, y, z, r, axis='z', rn=3):
    """The same two points on a lit disc: the highest and the rightmost point
    of the projected circle, found on the curve itself and not on its box."""
    a, b = _PLANE[axis]
    c = p_(x, y, z)
    top, right = _extremes([_on(c, a, b, r, t / 4.0) for t in range(1440)])
    _PTS.extend([top, right])
    return [_node_tag(top, rn), _node_tag(right, rn)]


# THE WAYPOINT IS DERIVED, NOT TYPED. SVG has no `in oklab`, so a gradient that
# carries the family's ramp carries the oklab path by hand: one extra stop at
# 19 % of the LIME LEG, measured from lime. The leg here ends at Glas, so the
# offset is 0.19 x 0.32 and not the 0.097 that belongs to a ramp whose Glas sits
# at 0.51. These four objects shipped once with the wrong one — computing it
# from the two numbers it depends on is the only version that cannot drift
# again. → scripts/check-gradient-family.py, foundations/colors.html#the-arc
GLAS_AT = 0.32
WAYPOINT_T = 0.19
LIGHT_DEF = ('<linearGradient id="{id}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" gradientUnits="userSpaceOnUse">'
             '<stop stop-color="#E1FF00"/><stop offset="' + f'{GLAS_AT * WAYPOINT_T:g}' + '" stop-color="#DBFC60"/>'
             '<stop offset="' + f'{GLAS_AT:g}' + '" stop-color="#C5EBE2"/>'
             '<stop offset="1" stop-color="#CFCFCF"/></linearGradient>')


def light_quad(gid, pts):
    return f'<path class="cf-iso__light" d="{poly([p_(*q) for q in pts])}" fill="url(#{gid})"/>'


def light_disc(gid, x, y, z, r, axis='z'):
    a, b = _PLANE[axis]
    rx, ry, ang = _ell(a, b, r)
    return _ell_tag(p_(x, y, z), rx, ry, ang, f'url(#{gid})', cls='cf-iso__light')


def lime_span_quad(pts):
    """Ramp endpoints for a light_quad(): straight down — 90 deg, a brand
    angle — from the face's highest corner to the level of its lowest. Lime
    sits in the back corner, Glas crosses the face a third of the way down and
    the near corner lands on CF-Grau, which is the ground's own value: that is
    how the reference plates let a lit top read as lit without the whole face
    standing off the page as a mint sticker.

    This replaces a span that ran corner to corner and 2.6 times the face's
    length, on the reasoning that a face which spends the whole ramp arrives
    mint. It does not; it arrives as the plates draw it. The ramp's length is
    the face's own height, so the light and the thing it lights are one
    measurement and a recrop cannot part them."""
    sp = [p_(*q) for q in pts]
    top, _ = _extremes(sp)
    return top, (top[0], max(p[1] for p in sp))


def lime_span_disc(x, y, z, r, axis='z', span=1.0):
    """Ramp endpoints for a light_disc(). Same arguments, and it exists because
    the generic corner-to-corner span is wrong for a disc in two ways at once.

    A TRANSFORM IS NEVER A NO-OP ON A GRADIENT. _ell_tag emits the ellipse
    axis-aligned plus rotate(ang), and a userSpaceOnUse paint server resolves in
    the user space the referencing element's own transform establishes — so
    screen-space endpoints arrive at the browser rotated by ang. On an x-axis
    disc ang is 127.98 deg, which is most of a half-turn: measured by
    rasterising the shipped ellipse and reading the pixels back, the lightest
    pixel of this object's light sat 68 % of the way DOWN the disc. The one rule
    the page states without qualification is that the light comes from above.
    -> foundations/illustration.html, "A transform is never a no-op on a gradient"

    THE ANCHOR IS THE SILHOUETTE, NOT THE BOUNDING BOX. lime_span() takes the
    corner of the lit element's lattice bounding box, which for a lit QUAD is a
    point of the element — the illustration page's own specimen puts t = 0 on
    two of its quad's vertices — and for a DISC is r*sqrt(2) from the centre,
    41 % of a radius outside the thing being lit. #E1FF00 was painted where
    there was nothing to paint on: 0 of 12 830 rendered pixels fell inside the
    lime leg, and the brightest was #DDFD46. Lime is the light; a lit face that
    never reaches lime is not lit.

    So: anchor on the ellipse's own vertical extent, which is exactly attained,
    run straight down (90 deg, a brand angle), and hand both endpoints over in
    the frame the browser will read them in. `span` is the ramp's length in
    disc heights. It shipped at 3.0 — the disc's lower edge on 1/3, so the
    light spent the lime -> Glas leg and stopped there, mint at the rim — and
    is 1.0 now, for the reason lime_span_quad() gives: the whole ramp lies
    inside the lit element and its lower edge lands on CF-Grau."""
    a, b = _PLANE[axis]
    rx, ry, ang = _ell(a, b, r)
    c = p_(x, y, z)
    t = math.radians(ang)
    ct, st = math.cos(t), math.sin(t)
    hh = math.hypot(rx * st, ry * ct)      # the ellipse's exact vertical semi-extent
    # A screen offset of (0, dy) about the centre, written in the pre-rotation
    # frame: R(-ang) . (0, dy) = (dy sin, dy cos).
    def local(dy):
        return (c[0] + dy * st, c[1] + dy * ct)
    return local(-hh), local(-hh + 2.0 * hh * span)


def window(w, h, at=None, ox=0.0, oy=0.0):
    """An AUTHORED crop: w x h on `at` — a screen point, normally p_() of the
    lattice point the drawing is about — or on the centre of what has been drawn
    so far if `at` is None. Nudged by (ox, oy) screen units. Whatever falls
    outside is what the frame cuts, which is the point —
    foundations/illustration.html:

        "The frame is a crop, not a bounding box. An object that fits neatly
        inside its frame with air all round reads as a sticker; one that is cut
        by the frame reads as a view into something larger."

    NO OBJECT IN objects.py CALLS IT ANY MORE, and the rule it serves is still
    the rule — for a plate whose frame is 640 units of a card and whose object is
    positioned inside it by a transform. It is kept for that, and because the
    argument for taking a window rather than a bbox is written here. What the
    four Expertise objects learned is narrower and is written on maschinenbau():
    a figure laid out at --vb-w / 112 x --field-unit cannot buy frame width
    without spending render scale, so the crop that fits the column is the one
    the drawing's own extent asks for, and the composing is done by deciding how
    much ground to draw rather than by deciding how much of it to cut off.

    A bounding-box centre is the wrong anchor as soon as the ground is much
    wider than the machine standing on it, because half of what it averages is
    floor. Name the point the drawing is about instead. And take the window
    BEFORE emitting the trace either way: a trace runs off-stage by design, so
    letting its far end into the point cloud drags the window off the machine
    and pads the frame with the empty half of a line."""
    if at is None:
        xs = [q[0] for q in _PTS]
        ys = [q[1] for q in _PTS]
        at = ((min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0)
    return (at[0] - w / 2.0 + ox, at[1] - h / 2.0 + oy, w, h)


def bbox(pad=30.0):
    """The crop assemble() would take by default — everything registered SO FAR
    plus `pad` on each side — but taken NOW, which is the whole reason it is a
    function of its own.

    "Now" matters in exactly one place and it is the same place window()'s last
    paragraph names: a trace registers its endpoints (see trace()), and an
    object whose trace enters the frame from off-stage has one endpoint outside
    the crop by construction. Let assemble() take the bbox at the end and that
    endpoint is in it, the frame grows to hold a line that was drawn to be cut,
    and --trace-from — which is computed FROM the crop — is computed from a crop
    the trace itself moved. Take it before the trace and both stay honest."""
    xs = [q[0] for q in _PTS]
    ys = [q[1] for q in _PTS]
    return (min(xs) - pad, min(ys) - pad,
            max(xs) - min(xs) + 2 * pad, max(ys) - min(ys) + 2 * pad)


def assemble(gid, la, lb, layers, light, nodes, ghost=(), orbits=(), pad=30.0,
             crop=None):
    """layers: [(stage, [paths])].  `stage` becomes data-stage on the group,
    which is what the page's build animation reads — the object comes up in
    four passes (foundation, masses, structure, detail) rather than all at once.

    --vb-w and --iso-travel are emitted from the same number that produced the
    crop, so a recrop cannot leave the arrival distance behind. See the note in
    foundations/motion.html#travel. That holds for an authored `crop` too: it is
    the one number both are read off, whether it came from the bounding box or
    from window()."""
    x0, y0, w, h = crop if crop is not None else bbox(pad)
    out = [f'<svg class="cf-iso" style="--vb-w:{f(w)}; --iso-travel: {f(w / 40)}" '
           f'viewBox="{f(x0)} {f(y0)} {f(w)} {f(h)}" fill="none" aria-hidden="true">',
           '  <defs>' + LIGHT_DEF.format(id=gid, x1=f(la[0]), y1=f(la[1]), x2=f(lb[0]), y2=f(lb[1])) + '</defs>',
           '  <g class="cf-iso__scene" stroke="#000" stroke-linejoin="round">']
    for stage, parts in layers:
        if not parts:
            continue
        out.append(f'    <g class="cf-iso__form" data-stage="{stage}">')
        out += ['      ' + (p if p.startswith('<') else f'<path d="{p}"/>') for p in parts]
        out.append('    </g>')
    # AFTER the form, not before it. A ghost is either an x-ray of what is
    # inside a body or a continuation of what the crop cuts off, and both only
    # read if the dashes are on top of the mass they belong to.
    if ghost:
        out.append('    <g class="cf-iso__ghost" stroke-dasharray="1 4" fill="none">')
        out += ['      ' + (g if g.startswith('<') else f'<path d="{g}"/>') for g in ghost]
        out.append('    </g>')
    # An orbit sits outside that group: it carries .cf-iso__ghost itself, and
    # nesting it would fade it twice.
    out += ['    ' + o for o in orbits]
    if light:
        out.append('    ' + light)
    out += ['    ' + n for n in nodes]
    out += ['  </g>', '</svg>']
    return '\n'.join(out)
