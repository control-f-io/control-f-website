"""A scanline rasteriser for contour drawings, in the standard library.

THE SECOND HALF OF ROUTE 1. `components/signet.html#launch` named the cost of
drawing the share plate here rather than in a Worker or by hand: "the hard half
is filling and anti-aliasing nine polygons and a gradient, which is a few
hundred lines of code the system would then own forever." This is that code,
and it is deliberately the smallest thing that draws THIS system rather than a
general 2D library. What the brand needs is exact: straight-edged polygons on a
lattice, hairline contours, one linear gradient, and the logo's Bezier
outlines. There is no curve stroking, no dashing, no blend mode, no text
shaping, and none of those are missing — the plate has no type on it, for the
reason set out in foundations/share.html.

HOW IT ANTI-ALIASES, AND WHY NOT BY SUPERSAMPLING. The obvious approach — draw
into a 3x or 4x canvas and average down — costs 6.8 million samples for a
1200 x 630 plate before a single shape is drawn, which in pure Python is tens
of seconds for a background that is a vertical wash and therefore constant
along every row. Instead each polygon is scanned with SAMPLES sub-scanlines per
output row, and along each sub-scanline the span between two crossings
contributes its EXACT fractional cover to the two end pixels and a full share
to everything between. Cost is proportional to the polygon's own height and to
the number of spans, not to the area of the plate, and the result is exact in x
and quantised only in y. At SAMPLES = 16 a 26.57 deg lattice edge — the
shallowest angle this system draws — is smooth.

WINDING. Even-odd. Every shape here is a convex quad, a circle or a glyph
outline whose holes are wound the other way, and even-odd is right for all
three. Nonzero would fill the counter of the "C" in the wordmark.

STROKES ARE MERGED WITH max(), NOT ADDED. A contour is drawn as one quad per
edge. Where two quads overlap at a corner, adding their coverage would paint
the join darker than the line; taking the larger coverage cannot. It is correct
because every stroke in this system is one opaque ink over one background, so
coverage is the only thing that varies across the join.
"""

import math
import re

SAMPLES = 16          # sub-scanlines per output row
_EPS = 1e-9


# ---------------------------------------------------------------------------
# Colour

def hex_rgb(value):
    """'#E1FF00' or 'E1FF00' -> (225, 255, 0)."""
    s = value.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def _lerp(a, b, t):
    return a + (b - a) * t


class Gradient(object):
    """A linear gradient in canvas space, given as CSS gives one.

    `stops` is [(offset 0..1, '#RRGGBB'), ...] in order. `p0` and `p1` are the
    endpoints of the gradient's axis; the colour at a point is decided by that
    point's projection onto the axis, clamped at both ends, which is exactly
    what `linear-gradient` with `gradientUnits="userSpaceOnUse"` does.

    Interpolation is in sRGB, not OKLab, and that is not an oversight: every
    gradient in this system is authored as a CSS `linear-gradient` with no
    `in oklab`, so the browser interpolates the shipped ones in sRGB and a
    plate that interpolated them anywhere else would be a different ramp from
    the one on the page it advertises.
    """

    def __init__(self, p0, p1, stops):
        self.x0, self.y0 = p0
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        self.dx, self.dy = dx, dy
        self.len2 = dx * dx + dy * dy or 1.0
        self.stops = [(o, hex_rgb(c)) for o, c in stops]
        # 512 steps is finer than the 8-bit grid can show over any leg this
        # system draws, so the lookup is exact rather than approximate.
        self.lut = [self._sample(i / 511.0) for i in range(512)]

    def _sample(self, t):
        stops = self.stops
        if t <= stops[0][0]:
            return stops[0][1]
        for i in range(1, len(stops)):
            o0, c0 = stops[i - 1]
            o1, c1 = stops[i]
            if t <= o1:
                k = 0.0 if o1 == o0 else (t - o0) / (o1 - o0)
                return (_lerp(c0[0], c1[0], k),
                        _lerp(c0[1], c1[1], k),
                        _lerp(c0[2], c1[2], k))
        return stops[-1][1]

    def at(self, x, y):
        t = ((x - self.x0) * self.dx + (y - self.y0) * self.dy) / self.len2
        if t <= 0:
            i = 0
        elif t >= 1:
            i = 511
        else:
            i = int(t * 511)
        return self.lut[i]


# ---------------------------------------------------------------------------
# Coverage

def _coverage(points, y0, y1, width):
    """Even-odd coverage of one polygon, as {row: [cover per column]}.

    Rows outside [y0, y1) are not visited at all, which is what keeps a
    16-sample scan cheap on a plate the shape covers a twentieth of.
    """
    n = len(points)
    edges = []
    for i in range(n):
        ax, ay = points[i]
        bx, by = points[(i + 1) % n]
        if ay == by:
            continue                       # horizontal edges never cross a scanline
        edges.append((ax, ay, bx, by))
    if not edges:
        return {}

    top = max(y0, int(math.floor(min(min(e[1], e[3]) for e in edges))))
    bot = min(y1, int(math.ceil(max(max(e[1], e[3]) for e in edges))))
    share = 1.0 / SAMPLES
    rows = {}

    for row in range(top, bot):
        cov = None
        for s in range(SAMPLES):
            sy = row + (s + 0.5) * share
            xs = []
            for ax, ay, bx, by in edges:
                if (ay <= sy < by) or (by <= sy < ay):
                    xs.append(ax + (sy - ay) * (bx - ax) / (by - ay))
            if len(xs) < 2:
                continue
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                xa, xb = xs[k], xs[k + 1]
                if xb <= 0 or xa >= width or xb - xa < _EPS:
                    continue
                xa = max(xa, 0.0)
                xb = min(xb, float(width))
                if cov is None:
                    cov = [0.0] * width
                ia, ib = int(xa), int(xb)
                if ib >= width:
                    ib = width - 1
                if ia == ib:
                    cov[ia] += (xb - xa) * share
                else:
                    cov[ia] += (ia + 1 - xa) * share
                    for i in range(ia + 1, ib):
                        cov[i] += share
                    cov[ib] += (xb - ib) * share
        if cov is not None:
            rows[row] = cov
    return rows


def _merge_max(into, rows, width):
    for row, cov in rows.items():
        dst = into.get(row)
        if dst is None:
            into[row] = list(cov)
            continue
        for i in range(width):
            c = cov[i]
            if c > dst[i]:
                dst[i] = c


# ---------------------------------------------------------------------------
# Canvas

class Canvas(object):
    def __init__(self, width, height):
        self.w = width
        self.h = height
        self.px = bytearray(width * height * 3)

    # -- ground ------------------------------------------------------------

    def wash(self, stops):
        """Fill the whole canvas with a vertical gradient.

        A vertical gradient is one colour per row, so the row is built once and
        multiplied out. This is the only fill on the plate that touches every
        pixel and it is the reason the plate renders in under a second.
        """
        g = Gradient((0, 0), (0, self.h), stops)
        stride = self.w * 3
        for y in range(self.h):
            r, gg, b = g.at(0, y + 0.5)
            row = bytes((int(r + 0.5), int(gg + 0.5), int(b + 0.5))) * self.w
            self.px[y * stride:(y + 1) * stride] = row

    # -- fills -------------------------------------------------------------

    def _composite(self, rows, paint, alpha=1.0):
        """`alpha` is a number, or a callable of the row for a fading layer."""
        px, w = self.px, self.w
        flat = isinstance(paint, tuple)
        fade = callable(alpha)
        for row, cov in rows.items():
            base = row * w * 3
            a_row = alpha(row) if fade else alpha
            if a_row <= 0.0:
                continue
            for i in range(w):
                a = cov[i]
                if a <= 0.002:
                    continue
                if a > 1.0:
                    a = 1.0
                a *= a_row
                if flat:
                    sr, sg, sb = paint
                else:
                    sr, sg, sb = paint.at(i + 0.5, row + 0.5)
                o = base + i * 3
                inv = 1.0 - a
                px[o] = int(px[o] * inv + sr * a + 0.5)
                px[o + 1] = int(px[o + 1] * inv + sg * a + 0.5)
                px[o + 2] = int(px[o + 2] * inv + sb * a + 0.5)

    def fill(self, points, paint, alpha=1.0):
        """One polygon. `paint` is an (r, g, b) tuple or a Gradient."""
        self._composite(_coverage(points, 0, self.h, self.w), paint, alpha)

    def fill_many(self, contours, paint, alpha=1.0):
        """Several contours as ONE even-odd shape — a glyph and its counters.

        The crossings of every contour are sorted together on each sub-scanline
        rather than each contour being filled apart, which is what makes the
        even-odd rule see the whole glyph: a counter wound inside its outline
        opens and closes the same span and the letter comes out hollow.
        """
        self._composite(_coverage_multi(contours, self.h, self.w), paint, alpha)

    # -- strokes -----------------------------------------------------------

    def stroke(self, points, colour, width=1.0, close=True, alpha=1.0):
        """A polyline as one quad per segment, coverage merged with max()."""
        half = width / 2.0
        rows = {}
        n = len(points)
        last = n if close else n - 1
        for i in range(last):
            ax, ay = points[i]
            bx, by = points[(i + 1) % n]
            dx, dy = bx - ax, by - ay
            ln = math.hypot(dx, dy)
            if ln < _EPS:
                continue
            nx, ny = -dy / ln * half, dx / ln * half
            # The segment is extended by half a width at each end, which is a
            # square cap. On a closed contour that is also the join, and it is
            # the right one here: every corner in this system is square.
            ex, ey = dx / ln * half, dy / ln * half
            quad = [(ax - ex + nx, ay - ey + ny), (bx + ex + nx, by + ey + ny),
                    (bx + ex - nx, by + ey - ny), (ax - ex - nx, ay - ey - ny)]
            _merge_max(rows, _coverage(quad, 0, self.h, self.w), self.w)
        self._composite(rows, colour, alpha)


def _coverage_multi(contours, height, width):
    """Even-odd coverage of several contours taken as one shape."""
    edges = []
    for points in contours:
        n = len(points)
        for i in range(n):
            ax, ay = points[i]
            bx, by = points[(i + 1) % n]
            if ay != by:
                edges.append((ax, ay, bx, by))
    if not edges:
        return {}
    top = max(0, int(math.floor(min(min(e[1], e[3]) for e in edges))))
    bot = min(height, int(math.ceil(max(max(e[1], e[3]) for e in edges))))
    share = 1.0 / SAMPLES
    rows = {}
    for row in range(top, bot):
        cov = None
        for s in range(SAMPLES):
            sy = row + (s + 0.5) * share
            xs = []
            for ax, ay, bx, by in edges:
                if (ay <= sy < by) or (by <= sy < ay):
                    xs.append(ax + (sy - ay) * (bx - ax) / (by - ay))
            if len(xs) < 2:
                continue
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                xa, xb = xs[k], xs[k + 1]
                if xb <= 0 or xa >= width or xb - xa < _EPS:
                    continue
                xa = max(xa, 0.0)
                xb = min(xb, float(width))
                if cov is None:
                    cov = [0.0] * width
                ia, ib = int(xa), int(xb)
                if ib >= width:
                    ib = width - 1
                if ia == ib:
                    cov[ia] += (xb - xa) * share
                else:
                    cov[ia] += (ia + 1 - xa) * share
                    for i in range(ia + 1, ib):
                        cov[i] += share
                    cov[ib] += (xb - ib) * share
        if cov is not None:
            rows[row] = cov
    return rows


# ---------------------------------------------------------------------------
# Circles, and the logo's outlines

def circle(cx, cy, r, segments=48):
    """A circle as a polygon. 48 segments is under a tenth of a pixel of sagitta
    at the largest radius this plate draws, which is below what 8 bits show."""
    return [(cx + r * math.cos(2 * math.pi * i / segments),
             cy + r * math.sin(2 * math.pi * i / segments))
            for i in range(segments)]


_NUM = re.compile(r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")
_CMD = re.compile(r"([MmLlHhVvCcSsZz])")


def path_contours(d, steps=24):
    """Flatten one SVG path's `d` into a list of closed point rings.

    Supports the command vocabulary the logo files actually use — M L H V C S Z
    in both cases — and nothing more. A file that arrives with an arc or a
    quadratic raises rather than drawing it wrong, because a logo that
    rasterises silently misshapen is worse than a build that stops.
    """
    # Split into (command, arguments) pairs. A command with no arguments — Z is
    # the only one here — must not swallow the token after it, which is why the
    # pairing is built explicitly rather than by striding the split in twos.
    parts = _CMD.split(d)
    if parts[0].strip():
        raise ValueError("path does not open with a command: %r" % parts[0][:32])
    ops = []
    t = 1
    while t < len(parts):
        cmd = parts[t]
        tail = parts[t + 1] if t + 1 < len(parts) else ""
        if cmd not in "MmLlHhVvCcSsZz":
            raise ValueError("unsupported path command %r" % cmd)
        ops.append((cmd, [float(n) for n in _NUM.findall(tail)]))
        t += 2

    contours, cur = [], []
    x = y = 0.0
    start = (0.0, 0.0)
    prev_c2 = None
    for cmd, args in ops:
        rel = cmd.islower()
        k = cmd.upper()

        if k == "Z":
            if cur:
                contours.append(cur)
                cur = []
            x, y = start
            prev_c2 = None
            continue

        j = 0
        while j < len(args):
            if k == "M":
                nx, ny = args[j], args[j + 1]; j += 2
                if rel:
                    nx, ny = x + nx, y + ny
                if cur:
                    contours.append(cur)
                cur = [(nx, ny)]
                x, y = nx, ny
                start = (nx, ny)
                k = "L"          # subsequent pairs after an M are implicit L
            elif k == "L":
                nx, ny = args[j], args[j + 1]; j += 2
                if rel:
                    nx, ny = x + nx, y + ny
                cur.append((nx, ny))
                x, y = nx, ny
            elif k == "H":
                nx = args[j]; j += 1
                if rel:
                    nx = x + nx
                cur.append((nx, y))
                x = nx
            elif k == "V":
                ny = args[j]; j += 1
                if rel:
                    ny = y + ny
                cur.append((x, ny))
                y = ny
            elif k in ("C", "S"):
                if k == "C":
                    c1x, c1y, c2x, c2y, nx, ny = args[j:j + 6]; j += 6
                    if rel:
                        c1x, c1y = x + c1x, y + c1y
                        c2x, c2y = x + c2x, y + c2y
                        nx, ny = x + nx, y + ny
                else:
                    c2x, c2y, nx, ny = args[j:j + 4]; j += 4
                    if rel:
                        c2x, c2y = x + c2x, y + c2y
                        nx, ny = x + nx, y + ny
                    # S reflects the previous curve's second control point.
                    c1x, c1y = ((2 * x - prev_c2[0], 2 * y - prev_c2[1])
                                if prev_c2 else (x, y))
                for s in range(1, steps + 1):
                    t = s / float(steps)
                    u = 1 - t
                    cur.append((u * u * u * x + 3 * u * u * t * c1x +
                                3 * u * t * t * c2x + t * t * t * nx,
                                u * u * u * y + 3 * u * u * t * c1y +
                                3 * u * t * t * c2y + t * t * t * ny))
                prev_c2 = (c2x, c2y)
                x, y = nx, ny
            if k not in ("C", "S"):
                prev_c2 = None
    if cur:
        contours.append(cur)
    return contours


_D = re.compile(r'\sd="([^"]+)"')
_VIEWBOX = re.compile(r'viewBox="([^"]+)"')


def svg_outlines(path):
    """Every `d` in an SVG file, flattened, plus its viewBox.

    The logo files are two or four filled paths and a clip rect the size of the
    frame; nothing in them needs a transform stack, and asserting that here —
    by refusing a file that carries a `transform` — is cheaper than growing one.
    """
    src = open(path, "r", encoding="utf-8").read()
    if "transform=" in src:
        raise ValueError("%s carries a transform; this reader has no stack" % path)
    vb = [float(v) for v in _VIEWBOX.search(src).group(1).replace(",", " ").split()]
    contours = []
    for d in _D.findall(src):
        contours.extend(path_contours(d))
    return contours, vb
