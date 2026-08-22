#!/usr/bin/env python3
"""The news title plates, held to the projection they claim to be drawn in.

TWO THINGS ARE MEASURED HERE AND NEITHER OF THEM IS VISIBLE.

EVERY STRAIGHT EDGE IS ON A BRAND ANGLE. foundations/illustration.html states
the geometry as a rule and then says why it is a rule and not a preference:
"nothing about a wrong angle announces itself, it just stops registering with
everything else on the page." Its own demonstration is a cube in textbook 30 deg
isometry sitting beside a correct one, five units wrong in the top face and
barely different to look at. A generator can put a segment off the grid in a
single mistyped coordinate, and no screenshot will report it — so the segments
are measured instead.

    26.57 deg   the two ground axes, e1 and e2
    63.43 deg   the other family the manual's plates run on
    45 deg      sanctioned by the chapter's rule list
    90 deg      the vertical
     0 deg      the level step, e1 - e2 — the only way sideways without descending

IT READS THE VECTOR SOURCE AND NOT THE SHIPPED STORE. What ships is a 2016 px
PNG, because Notion will not render an SVG in a Files property and an archive
whose editor cannot see the picture is not edited. The geometry those pixels
came from is still the thing worth holding to the grid, so the gate reads
scripts/news-objects/svg/ — the drawings, before the rasteriser.

NOTHING IS OUTSIDE THE FRAME. The rule that a frame is a crop and not a bounding
box is a rule about composition, and scripts/expertise-objects/objects.py records
what it cost when it was applied literally: three passes on object 01, each
fixing the cut that was reported, each read back as "the image is cut off". These
plates are cropped to their own extent plus a pad, which is a property a script
can hold — every drawn coordinate inside the viewBox, with the lattice exempt
because it is a field rather than part of any object.

Also checked, because they are the other things the chapter states as absolutes:
one lit element per object, no <text> anywhere in a drawing, no colour outside
the three greys and the one lime ramp, and the oklab waypoint at 19 % of each
lime leg.
"""

import math
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCES = ROOT / "scripts" / "news-objects" / "svg"

# The angles a straight edge may take, as absolute screen slopes. A segment and
# its reverse are the same line, so the test folds onto [0, 90).
BRAND = (0.0, 26.565051177077986, 45.0, 63.43494882292201, 90.0)
TOL = 0.05                     # degrees. Coordinates are emitted at 2 dp.

# The three-grey register, plus the ramp, plus black. #919191 and #484848 are
# the DENSE register's accent and aperture and have no business here.
PALETTE = {'#DADADA', '#CFCFCF', '#C4C4C4', '#000', '#000000',
           '#E1FF00', '#DBFC60', '#C5EBE2', 'none'}

NUM = re.compile(r'-?\d*\.?\d+(?:e-?\d+)?')


def segments(d):
    """Every straight segment of a path, as ((x0, y0), (x1, y1)).

    Arc commands are skipped rather than approximated: an `A` is the true
    projected circle of a solid of revolution, which the chapter exempts from
    the lattice — "a sphere, a solid of revolution and a bloom have no vertices
    to snap". What is on the lattice there is the axis, and the axis is a
    straight segment like any other.
    """
    out, cur, start = [], None, None
    for cmd, args in re.findall(r'([MLHVAZmlhvaz])([^MLHVAZmlhvaz]*)', d):
        n = [float(v) for v in NUM.findall(args)]
        up = cmd.upper()
        if up == 'M':
            for i in range(0, len(n) - 1, 2):
                p = (n[i], n[i + 1])
                if i and cur:
                    out.append((cur, p))
                cur = p
                if i == 0:
                    start = p
        elif up == 'L':
            for i in range(0, len(n) - 1, 2):
                p = (n[i], n[i + 1])
                out.append((cur, p))
                cur = p
        elif up == 'H':
            for v in n:
                p = (v, cur[1]); out.append((cur, p)); cur = p
        elif up == 'V':
            for v in n:
                p = (cur[0], v); out.append((cur, p)); cur = p
        elif up == 'A':
            for i in range(0, len(n) - 6, 7):
                cur = (n[i + 5], n[i + 6])          # the endpoint only
        elif up == 'Z':
            if cur and start and cur != start:
                out.append((cur, start))
            cur = start
    return out


def angle(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    if abs(dx) < 1e-9 and abs(dy) < 1e-9:
        return None                                  # a degenerate segment
    return abs(math.degrees(math.atan2(dy, dx))) % 180.0


def fold(t):
    return 180.0 - t if t > 90.0 else t


def coords(svg):
    """Every drawn point, for the frame test. The lattice group is dropped: it
    is a field the crop is entitled to run off the edge of, and it is the only
    thing in the file emitted after the crop is known."""
    body = re.sub(r'<g class="cf-iso__ghost" stroke-dasharray="1 4" fill="none">'
                  r'(?:(?!</g>).)*?</g>', '', svg, count=1, flags=re.S)
    pts = []
    for d in re.findall(r'<path[^>]*\sd="([^"]+)"', body):
        for a, b in segments(d):
            pts += [a, b]
    for tag in re.findall(r'<(?:ellipse|circle)[^>]*>', body):
        g = dict(re.findall(r'(\w+)="([^"]*)"', tag))
        cx, cy = float(g.get('cx', 0)), float(g.get('cy', 0))
        rx = float(g.get('rx', g.get('r', 0)))
        ry = float(g.get('ry', g.get('r', 0)))
        pts += [(cx - rx, cy - ry), (cx + rx, cy + ry)]   # the rotated bound is no larger
    return pts


def main():
    files = sorted(SOURCES.glob('*.svg'))
    if not files:
        print("check-news-objects: no drawings in %s" % SOURCES, file=sys.stderr)
        return 1
    findings = []
    for p in files:
        s = p.read_text(encoding='utf-8')
        vb = [float(v) for v in NUM.findall(re.search(r'viewBox="([^"]+)"', s).group(1))]
        x0, y0, w, h = vb

        # the lattice is the underlay: the FIRST ghost group in the file
        body = re.sub(r'<g class="cf-iso__ghost" stroke-dasharray="1 4" fill="none">'
                      r'(?:(?!</g>).)*?</g>', '', s, count=1, flags=re.S)
        off = []
        for d in re.findall(r'<path[^>]*\sd="([^"]+)"', body):
            for a, b in segments(d):
                t = angle(a, b)
                if t is None:
                    continue
                t = fold(t)
                if min(abs(t - k) for k in BRAND) > TOL:
                    off.append(round(t, 3))
        if off:
            findings.append("%s: %d segment(s) off the lattice — %s"
                            % (p.name, len(off), sorted(set(off))[:6]))

        out = [q for q in coords(s)
               if q[0] < x0 - 0.6 or q[0] > x0 + w + 0.6
               or q[1] < y0 - 0.6 or q[1] > y0 + h + 0.6]
        if out:
            findings.append("%s: %d point(s) outside the frame — the drawing is "
                            "cut by its own crop" % (p.name, len(out)))

        n = s.count('class="cf-iso__light"')
        if n != 1:
            findings.append("%s: %d lit elements; the budget is one per object"
                            % (p.name, n))
        if re.search(r'<text[\s>]', s):
            findings.append("%s: has a <text> element; a drawing carries no type"
                            % p.name)
        stray = set(re.findall(r'(?:fill|stroke|stop-color)="(#[0-9A-Fa-f]{3,6})"',
                               s)) - PALETTE
        if stray:
            findings.append("%s: off-palette %s" % (p.name, sorted(stray)))
        for g in re.findall(r'<(?:linear|radial)Gradient.*?</(?:linear|radial)Gradient>',
                            s, re.S):
            st = re.findall(r'offset="([\d.]+)"[^/]*stop-color="(#\w+)"', g)
            glas = [float(o) for o, c in st if c == '#C5EBE2']
            way = [float(o) for o, c in st if c == '#DBFC60']
            if not glas or not way or abs(way[0] - glas[0] * 0.19) > 1e-4:
                findings.append("%s: the oklab waypoint is not at 19 %% of the "
                                "lime leg" % p.name)

    if findings:
        print("news objects:", file=sys.stderr)
        for f in findings:
            print("    " + f, file=sys.stderr)
        return 1
    print("news objects: %d drawing(s), every edge on a brand angle, nothing "
          "outside its frame, one light each, three greys and the ramp."
          % len(files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
