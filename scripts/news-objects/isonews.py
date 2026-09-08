"""The news title plates: the Expertise object library, one register up.

WHY A SECOND HARNESS AND NOT A FLAG ON THE FIRST. The four Expertise objects
carry 95-145 elements each and run in the DENSE register that
foundations/illustration.html sets out for exactly that: near-white faces, the
contour doing all of the describing. A news plate is the other object on that
page — a dozen or two faces — so it runs in the three-grey register the same
chapter states first, #DADADA / #CFCFCF / #C4C4C4, and it stands on CF-Grau,
which is the value of its own shaded face. That is the shape language as a
measurement: an unlit face IS the ground, and only the contour carries it.

AND THEY ARE STANDALONE FILES, WHICH IS THE REAL DIFFERENCE. Every other
illustration in this repository is inline SVG under `.cf-iso`, and inherits
from components.css the thing that makes a 1 px contour survive being scaled:
`vector-effect: non-scaling-stroke`. A file referenced by <img src> inherits
nothing from the page it is drawn on, so this module inlines it in a <style>
the file carries itself. Without it a 600-unit drawing in a 300 px card puts
its contours on screen at half a pixel.

THE FRAME IS 3:2 AND THAT IS NOT A PREFERENCE EITHER. `.cf-blog-card__image` is
`aspect-ratio: 3 / 2; object-fit: cover`, so a plate authored at any other ratio
is a plate the card crops with no say from here. Authored at 3:2 the card shows
what was drawn. 600 x 400 for all ten — "one size per set", so the archive reads
as one system rather than as ten drawings that happen to be adjacent.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "expertise-objects"))

import isolib as iso                                            # noqa: E402
from isolib import (                                            # noqa: E402
    P, p_, f, poly, line, face, box, quad_t, quad_x, quad_y, seams, ladder,
    disc, hoop, cyl, drum, taper, rotor, orbit, node, window, reset,
)

# ---- the three-grey register. illustration.html, "Contour and fill".
TOP = '#DADADA'      # facing the sky
LIT = '#CFCFCF'      # the lit side — CF-Grau itself
SHADE = '#C4C4C4'    # the side away from this object's own lime end
GROUND = '#CFCFCF'   # the plate the object is drawn on == the unlit face

# The two values the register keeps for a slot and an aperture. They are an
# ACCENT WITH A BUDGET, not a fill with a meaning: three or four in a drawing,
# a few square units each, and the moment one covers a face the object has
# fallen back into the first register with worse contrast.
ACCENT = '#919191'
DARK = '#484848'

# cyl()/rotor() read these at call time; their keyword defaults do not.
# A horizontal run takes top + shaded side, a vertical one lit + shaded — the
# pair a box in that orientation would use, so a pipe and the beam it lies on
# are lit by one rule instead of two.
iso._SIDE = {'x': SHADE, 'y': LIT, 'z': LIT}
iso._CROWN = {'x': (45.0, 135.0, TOP), 'y': (-45.0, 45.0, TOP), 'z': (45.0, 135.0, SHADE)}

AR = 3.0 / 2.0               # `.cf-blog-card__image` is aspect-ratio: 3 / 2


def fit(pad=30.0, size=None):
    """The crop: everything drawn, plus `pad`, widened to 3:2.

    AUTHORED WINDOWS ARE WHY THIS IS A FUNCTION. illustration.html says a frame
    is a crop and not a bounding box, and that an object cut by its frame reads
    as a view into something larger — and scripts/expertise-objects/objects.py
    records what happened when that was applied literally: three passes on
    object 01, each fixing the cut that was reported, each read back as the same
    sentence again, "the image is cut off". The rule promises a view into
    something larger; what a 26.57 deg corner ending on a vertical <svg> edge
    delivers, against a page whose ground is a quiet grey lattice, is a drawing
    that did not fit its box. The four Expertise objects are cropped to their
    own extent plus a pad for that reason, and so are these.

    3:2 because the card is, and because a plate authored at any other ratio is
    a plate object-fit: cover crops with no say from here. Widening the tighter
    axis rather than trimming the longer one is what keeps "plus a pad" true:
    the drawing is never the thing that gives way to the ratio.

    Everything the object draws registers a point through P(); the lattice does
    not, because it is a field the frame is entitled to run off the edge of.
    """
    x0, y0, w, h = iso.bbox(pad)
    cx, cy = x0 + w / 2.0, y0 + h / 2.0
    if size is not None:
        # ONE SIZE PER SET. Sized to its own extent, each drawing fills its frame
        # and the ten then render at ten different scales in the same 380 px
        # card — which is what illustration.html's "one size per set" rule is
        # about: the four process objects share a cap "so the four objects read
        # as a sequence rather than four drawings that happen to be adjacent".
        # The common frame is the largest any of them needs, so it still cuts
        # nothing; what varies between plates is how much of it an object fills,
        # which is the honest variable.
        w, h = size
    elif w / h < AR:
        w = h * AR
    else:
        h = w / AR
    return (cx - w / 2.0, cy - h / 2.0, w, h)


def common_size(builders, pad=30.0):
    """The frame every plate in the set shares: the largest extent any of them
    needs, in 3:2. Taken by drawing each one and measuring, so adding an
    eleventh post cannot silently start cropping the other ten."""
    wmax = hmax = 0.0
    for fn in builders:
        fn()
        _, _, w, h = iso.bbox(pad)
        wmax, hmax = max(wmax, w), max(hmax, h)
    if wmax / hmax < AR:
        wmax = hmax * AR
    else:
        hmax = wmax / AR
    return (wmax, hmax)
GLAS = {'near': 0.32, 'mid': 0.51, 'far': 0.64}
WAYPOINT_T = 0.19


def light_def(gid, rake, a, b):
    """The one ramp, at one of the three rakes, with the oklab waypoint DERIVED
    rather than typed — 19 % of the lime leg, measured from lime, and the leg
    ends at Glas, so the offset moves with the rake. 0.061 belongs to the near
    rake and nothing else; a mid-rake ramp carrying it is off the oklab path it
    was added to hold. → foundations/colors.html, scripts/check-gradient-family.py
    """
    g = GLAS[rake]
    return (f'<linearGradient id="{gid}" x1="{f(a[0])}" y1="{f(a[1])}" '
            f'x2="{f(b[0])}" y2="{f(b[1])}" gradientUnits="userSpaceOnUse">'
            f'<stop stop-color="#E1FF00"/>'
            f'<stop offset="{g * WAYPOINT_T:g}" stop-color="#DBFC60"/>'
            f'<stop offset="{g:g}" stop-color="#C5EBE2"/>'
            f'<stop offset="1" stop-color="#CFCFCF"/></linearGradient>')


def lit(gid, pts):
    """The one lit element. Registered, because the crop rule says a frame may
    never cut it."""
    return f'<path class="cf-iso__light" d="{poly([P(*q) for q in pts])}" fill="url(#{gid})"/>'


def lime_span(a, b, reach=2.6):
    """Ramp endpoints for a lit face. The ramp is lime for its first third and
    neutral by its end, so a face spanning the WHOLE ramp arrives mint — which
    is not what "lime is light" means. Start at the face's far corner and run
    well past the near one: the face keeps its lime and turns only at its edge.
    """
    pa, pb = p_(*a), p_(*b)
    return pa, (pa[0] + (pb[0] - pa[0]) * reach, pa[1] + (pb[1] - pa[1]) * reach)


def lattice(crop, step=2.0, opacity=0.32):
    """The ground lattice, both families, across the crop.

    EXACT, AND NOT A MESH. The first version walked screen intercepts and drew
    both families at every lattice unit, which put a line every 28 screen px in
    each direction: at plate size that is not reference geometry, it is a
    texture, and it competed with the contour it is supposed to sit under. A
    family-1 line is the set of points with constant y and runs on VX; a
    family-2 line has constant x and runs on VY. Step 2 halves the density and
    keeps every line on the lattice, because 2u is still a lattice move.

    The 0.32 is the specimen's own stroke-opacity in foundations/illustration.
    html — a ghost is reference geometry, and reference geometry that reads as
    strongly as the object stops being reference."""
    x0, y0, w, h = crop
    U = iso.U
    out = []
    reach = (w + 2 * h) / U + 2

    def span(base, d):
        return line((base[0] - d[0] * reach, base[1] - d[1] * reach),
                    (base[0] + d[0] * reach, base[1] + d[1] * reach))

    n = int(reach) + 2
    for k in range(-n, n + 1):
        t = k * step
        out.append(span(p_(0.0, t, 0.0), (U, U / 2.0)))      # constant y
        out.append(span(p_(t, 0.0, 0.0), (-U, U / 2.0)))     # constant x
    return [f'<g stroke-opacity="{opacity}">'] + out + ['</g>']


def lit_top(gid, x, y, z, dx, dy, reach=0.92):
    """The lit horizontal face, and the ramp that lights it, from the one place
    that knows both — so the gradient can never drift off the face it paints.

    THE RAMP RUNS DOWN THE FACE'S OWN DIAGONAL. Handed an EDGE instead, as the
    first pass handed it, the ramp varies along one axis of a face that extends
    on two: a 2.4 x 0.95 container top came out as a band of flat lime with a
    green edge, which is not a lit face, it is a lime face. Corner to corner the
    ramp spends its lime leg on the face and turns at the near vertex, which is
    what the specimen does and what "lime is a moment, not a surface" means.

    Lime sits at the FAR corner because screen y is OY + (x+y)U/2: the smallest
    y in the quad is (x, y), and the one thing every object in the manual has in
    common is that the lime end is at the smaller y. The light comes from above.
    """
    a = p_(x, y, z)
    b = p_(x + dx, y + dy, z)
    span_b = (a[0] + (b[0] - a[0]) * reach, a[1] + (b[1] - a[1]) * reach)
    pts = [(x, y, z), (x + dx, y, z), (x + dx, y + dy, z), (x, y + dy, z)]
    return a, span_b, lit(gid, pts)


def lit_x(gid, x, y, z, dy, dz, reach=0.92):
    """The lit VERTICAL face at constant x — the +x flank, which is the lit side
    in this library's convention.

    A face does not have to be horizontal to be the one the eye lands on, and
    for a member that is much thinner than what stands on it the top face is not
    even visible: it is under the next course. What such a member shows is its
    flank, and "on a flat face the ramp climbs" is the chapter's own wording for
    the geometry of lighting one.

    Lime goes at the corner with the smallest screen y, which on a vertical face
    is the far-top one — (y, z + dz). Every object in the manual has its lime end
    at the smaller y, because the light comes from above."""
    a = p_(x, y, z + dz)
    b = p_(x, y + dy, z)
    span_b = (a[0] + (b[0] - a[0]) * reach, a[1] + (b[1] - a[1]) * reach)
    pts = [(x, y, z), (x, y + dy, z), (x, y + dy, z + dz), (x, y, z + dz)]
    return a, span_b, lit(gid, pts)


HEAD = """<svg xmlns="http://www.w3.org/2000/svg" class="cf-iso" viewBox="{vb}" \
width="{w}" height="{h}" fill="none" role="img">
<title>{title}</title>
<style><![CDATA[
/* components.css gives .cf-iso this inline; a file referenced by an img
   element inherits no stylesheet, so it carries it itself.
   CDATA because this is XML and not HTML: a bare "<" in a CSS comment opens an
   element the parser then waits for the end of, and the whole file fails to
   load rather than losing the comment. */
.cf-iso path,.cf-iso line,.cf-iso circle,.cf-iso ellipse,.cf-iso polygon\
{{vector-effect:non-scaling-stroke}}
]]></style>
<defs>{defs}</defs>
<rect x="{x0}" y="{y0}" width="{w0}" height="{h0}" fill="{ground}"/>
<g class="cf-iso__scene" stroke="#000" stroke-linejoin="round">"""


def emit(title, crop, defs, forms, light=None, ghost=(), orbits=(),
         nodes=(), underlay=(), out_w=1200):
    """One finished plate. The order is the material order illustration.html
    sets out — reference geometry and contours before light — with the nodes
    last, as the drawing's own annotation.

    Ghost AFTER the form, not before it: a ghost is either an x-ray of what is
    inside a body or a continuation of what the crop cuts off, and both only
    read with the dashes on top of the mass they belong to.
    """
    x0, y0, w, h = crop
    parts = [HEAD.format(vb=f"{f(x0)} {f(y0)} {f(w)} {f(h)}",
                         w=int(out_w), h=int(out_w * h / w),
                         x0=f(x0), y0=f(y0), w0=f(w), h0=f(h),
                         ground=GROUND, title=title, defs=defs)]
    # THE LATTICE GOES UNDER THE GROUND IT IS THE LATTICE OF. Emitted with the
    # rest of the ghost — after the form, where a ghost belongs — it painted the
    # dashes straight over the plate, and every plate in the set carried a mesh
    # across its own top face. Under the form it shows exactly where there is no
    # plate to hide it, which is the horizon and above: reference geometry for
    # the ground that continues past the one the object stands on.
    if underlay:
        parts.append('  <g class="cf-iso__ghost" stroke-dasharray="1 4" fill="none">')
        parts += ['    ' + (g if g.startswith('<') else f'<path d="{g}"/>') for g in underlay]
        parts.append('  </g>')
    for group in forms:
        parts += ['  ' + (p if p.startswith('<') else f'<path d="{p}"/>') for p in group]
    if ghost:
        parts.append('  <g class="cf-iso__ghost" stroke-dasharray="1 4" fill="none">')
        parts += ['    ' + (g if g.startswith('<') else f'<path d="{g}"/>') for g in ghost]
        parts.append('  </g>')
    parts += ['  ' + o for o in orbits]
    if light:
        parts.append('  ' + light)
    parts += ['  ' + n for n in nodes]
    parts += ['</g>', '</svg>', '']
    return '\n'.join(parts)

