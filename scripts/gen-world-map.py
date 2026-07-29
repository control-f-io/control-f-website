#!/usr/bin/env python3
"""Generate Act 5's map: coastlines, the lattice, the fills and every point.

WHY A SCRIPT, and it is the same answer the root and the two fields give. A map
is the largest table of hand-picked numbers a page can carry -- three thousand
coordinates, three camera framings, and a label position per point per framing
-- and the standing brief has asked for the opposite of that in as many words:
"a rule, not a table of hand-picked values". So the geometry is computed HERE,
deterministically, and the result is spliced into the prototype. Re-run it and
the same paths come out; --check says so on every build.

THE SOURCE IS NATURAL EARTH, 110m admin-0, public domain (CC0), vendored at
scripts/data/world-110m.json rather than fetched. A generator that needs the
network is a generator CI cannot run, and "the shipped markup is the script's
output" is a claim that has to hold offline. The vendored file is already
simplified -- Douglas-Peucker at 0.45 degrees for the world and 0.06 for the
two countries this act actually zooms into, rings under a minimum area dropped,
coordinates at two decimals. 161 countries, 3327 points, 48 kB.

THE PROJECTION IS WEB MERCATOR, clipped to latitude -58..78. Not because it is
the honest projection -- it is not, it inflates the high latitudes and this
drawing does not pretend otherwise -- but because it is the one every reader
has already learned, and the act's job is to be recognised in half a second at
three different scales. Antarctica is dropped: Mercator cannot draw it and the
clip would cut it anyway.

THE CAMERA PULLS BACK, one map, three framings. The svg's viewBox IS the world
framing, and each earlier stage is a transform on the map group that fits that
stage's bounding box into the same box. So there is one set of geometry, drawn
once, and Konstanz is the same dot at every scale -- which is the act's whole
argument and cannot be got from three drawings that cross-fade.

WHAT SCALES AND WHAT DOES NOT. Coastlines carry vector-effect: non-scaling-
stroke, so a hairline is a hairline at every framing. Points are drawn as
ZERO-LENGTH paths with a round linecap and the same vector-effect -- an SVG
dot whose radius is a stroke width, and therefore constant while the camera
moves. There is no vector-effect for a fill, which is why a point here is a
stroke and not a <circle>.

THE ASSETS ARE ILLUSTRATIVE AND THE COPY SAYS SO. They are asset TYPES in the
regions those types are found in -- offshore and shipping, mining, solar, rail,
battery, aviation -- and not customer sites. Nothing in this file or on the
page asserts a customer, which is a decision from the review of 2026-07-29 and
the only safe one: a point on a public map that says "customer" is a factual
claim about somebody else's business.
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "scripts" / "data" / "world-110m.json"
PAGE = ROOT / "design-system" / "prototypes" / "statement-to-process.html"
MARK = "gen-world-map"

W = 1000.0                    # the Mercator square's width, in map units
LAT_TOP, LAT_BOT = 78.0, -58.0
PAD = 0.10                    # of the shorter axis, around each framing's box


def merc(lon, lat):
    x = (lon + 180.0) / 360.0 * W
    s = math.sin(math.radians(max(-85.0, min(85.0, lat))))
    y = (0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)) * W
    return x, y


VY0 = merc(0, LAT_TOP)[1]
VY1 = merc(0, LAT_BOT)[1]
VIEW = (0.0, VY0, W, VY1 - VY0)          # the world framing, and the viewBox


def num(v):
    r = round(float(v), 2)
    return f"{int(r)}" if r == int(r) else f"{r:g}"


# ------------------------------------------------------------------ the places
#
# TWO OFFICES, and they are the only points on this map that name a place. Both
# are ours, both are checkable, and the act opens on them because that is where
# the story starts.
OFFICES = [
    ("Konstanz", "Hauptsitz", 9.1770, 47.6603),
    ("Berlin", "Standort", 13.4050, 52.5200),
]

# THE MARKETS, filled at stage 2. Two countries, and the ISO codes are the
# vendored file's own keys so a typo is a KeyError rather than an empty fill.
MARKETS = ["DEU", "GBR"]

# THE ASSETS, illustrative. Each is a TYPE at a place that type is actually
# found -- ore in the Pilbara, not ore in Bavaria -- so the spread reads as the
# world's industry rather than as scatter. No customer is named or implied.
ASSETS = [
    ("see",     "Offshore & Schiff",  [(2.5, 54.5), (5.5, 58.0), (-90.5, 26.5),
                                       (103.9, 1.2), (-43.2, -23.5), (55.2, 25.1)]),
    ("berg",    "Bergbau",            [(118.5, -22.5), (121.5, -30.8), (-69.3, -24.2),
                                       (-70.5, -33.5), (-76.0, -12.0), (27.5, -26.2)]),
    ("solar",   "Solar & Netz",       [(-3.7, 40.4), (12.5, 41.9), (10.5, 51.2),
                                       (2.3, 48.9), (23.7, 38.0)]),
    ("bahn",    "Schiene",            [(-1.5, 52.5), (-2.2, 53.5), (9.2, 48.8)]),
    ("batterie","Batterie & Speicher",[(-100.3, 25.7), (-99.1, 19.4), (-97.5, 22.0)]),
    ("luft",    "Luftfahrt",          [(8.6, 50.0), (55.4, 25.3), (103.99, 1.36),
                                       (-97.0, 32.9)]),
]


# ------------------------------------------------------------------- the shapes
LAND = json.loads(DATA.read_text(encoding="utf-8"))
for iso in MARKETS:
    assert iso in LAND, f"{iso} is not in the vendored geodata"


def ring_path(ring):
    pts = [merc(lon, lat) for lon, lat in ring]
    out = [f"M{num(pts[0][0])} {num(pts[0][1])}"]
    out += [f"L{num(x)} {num(y)}" for x, y in pts[1:]]
    return "".join(out) + "Z"


def country_path(iso):
    return "".join(ring_path(r) for r in LAND[iso])


def bbox(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


def country_points(iso):
    return [merc(lon, lat) for r in LAND[iso] for lon, lat in r]


# -------------------------------------------------------------- the three shots
#
# A FRAMING IS A BOX AND A TRANSFORM. The box is what the stage should hold; the
# transform is what carries the world's coordinates into the viewBox so that box
# fills it. `translate(t) scale(k)` about the origin, so a map point p lands at
# k*p + t and the label positions below are computed with the same two numbers
# rather than measured off a render.
def framing(points, pad=PAD):
    x0, y0, x1, y1 = bbox(points)
    bw, bh = x1 - x0, y1 - y0
    m = pad * min(bw, bh)
    x0, y0, x1, y1 = x0 - m, y0 - m, x1 + m, y1 + m
    k = min(VIEW[2] / (x1 - x0), VIEW[3] / (y1 - y0))
    tx = VIEW[0] + VIEW[2] / 2 - k * (x0 + x1) / 2
    ty = VIEW[1] + VIEW[3] / 2 - k * (y0 + y1) / 2
    return k, tx, ty


SHOTS = [
    ("de",    framing(country_points("DEU"))),
    ("dega",  framing(sum((country_points(i) for i in MARKETS), []))),
    ("welt",  (1.0, 0.0, 0.0)),
]


def place(p, shot):
    """A map point in a framing, as a percentage of the viewBox."""
    k, tx, ty = shot
    x, y = k * p[0] + tx, k * p[1] + ty
    return (x - VIEW[0]) / VIEW[2] * 100.0, (y - VIEW[1]) / VIEW[3] * 100.0


# ------------------------------------------------------------------ the blocks
BLOCKS = {}
_open = None


def block(name):
    global _open
    _open = name
    BLOCKS.setdefault(name, [])


def emit(line):
    BLOCKS[_open].append(line)


# THE OPENING TAG IS GENERATED TOO, because the viewBox IS the world framing
# and the world framing is computed here. A hand-written viewBox beside a
# computed camera is two numbers that have to agree and nothing checking that
# they do — which is the drift every generator in this repo exists against.
block("view")
emit(f'<svg class="map" viewBox="{" ".join(num(v) for v in VIEW)}" '
     f'fill="none" aria-hidden="true">')

block("coast")
for iso in sorted(LAND):
    cls = "map__land map__land--market" if iso in MARKETS else "map__land"
    emit(f'<path class="{cls}" d="{country_path(iso)}"/>')

block("fill")
for iso in MARKETS:
    emit(f'<path class="map__fill" d="{country_path(iso)}"/>')
    emit(f'<path class="map__weave" d="{country_path(iso)}"/>')

block("points")
for name, _role, lon, lat in OFFICES:
    x, y = merc(lon, lat)
    emit(f'<path class="map__dot map__dot--office" d="M{num(x)} {num(y)}h0"/>')
for n, (kind, _label, places) in enumerate(ASSETS):
    for lon, lat in places:
        x, y = merc(lon, lat)
        d = f'M{num(x)} {num(y)}h0'
        emit(f'<path class="map__dot map__dot--ring" style="--n:{n}" d="{d}"/>')
        emit(f'<path class="map__dot map__dot--asset" style="--k:{kind};--n:{n}" d="{d}"/>')

# THE LABELS ARE HTML AND THEY BELONG TO ONE SHOT EACH. The camera holds still
# while a stage is read, so a label placed for that stage's framing is exact for
# as long as it is on screen -- which is the whole reason the camera holds. Each
# carries its position as a percentage of the map box, computed above from the
# same k and t the transform uses.
block("labels")
for i, (name, role, lon, lat) in enumerate(OFFICES):
    px, py = place(merc(lon, lat), SHOTS[0][1])
    emit(f'<span class="t-label map__tag" style="--s:0;--i:{i};'
         f'--x:{num(px)}%;--y:{num(py)}%">{name}<i>{role}</i></span>')
for i, iso in enumerate(MARKETS):
    x0, y0, x1, y1 = bbox(country_points(iso))
    px, py = place(((x0 + x1) / 2, (y0 + y1) / 2), SHOTS[1][1])
    emit(f'<span class="t-label map__tag map__tag--land" style="--s:1;--i:{i};'
         f'--x:{num(px)}%;--y:{num(py)}%">{"Deutschland" if iso == "DEU" else "United Kingdom"}</span>')

block("legend")
for i, (kind, label, places) in enumerate(ASSETS):
    emit(f'<li class="map__key" style="--k:{kind};--i:{i}">'
         f'<span class="map__key-dot" aria-hidden="true"></span>'
         f'<span class="t-label map__key-name">{label}</span>'
         f'<span class="map__key-n">{len(places)}</span></li>')

block("shots")
for name, (k, tx, ty) in SHOTS:
    emit(f'--cam-{name}: translate({num(tx)}px, {num(ty)}px) scale({num(k)});')


# THE SHOTS BLOCK LIVES IN CSS AND THEREFORE IN CSS COMMENTS. Everything else
# is markup and carries HTML markers; the three camera transforms are custom
# properties and have to sit in a rule. One splice, two comment syntaxes, and
# the block itself decides which — rather than a second script for one block.
CSS_BLOCKS = {"shots"}


def splice(text):
    total = 0
    for name, lines in BLOCKS.items():
        o, c = ("/*", "*/") if name in CSS_BLOCKS else ("<!--", "-->")
        pat = re.compile(r"([ \t]*)(" + re.escape(o) + " " + MARK + ": " + name
                         + " " + re.escape(c) + r"\n)"
                         r"((?:.*\n)*?)(\1" + re.escape(o) + " " + MARK + ": end "
                         + name + " " + re.escape(c) + r")")

        def one(m, lines=lines):
            body = "".join(m.group(1) + l + "\n" for l in lines)
            return m.group(1) + m.group(2) + body + m.group(4)

        text, n = pat.subn(one, text, count=1)
        total += n
    return text, total


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    if not (args.write or args.check):
        print(f"  source     {DATA.relative_to(ROOT)}  "
              f"{len(LAND)} countries, {sum(len(r) for rs in LAND.values() for r in rs)} points")
        print(f"  viewBox    {' '.join(num(v) for v in VIEW)}   "
              f"lat {LAT_BOT}..{LAT_TOP}, Web Mercator")
        for name, (k, tx, ty) in SHOTS:
            print(f"  shot {name:<6} scale {k:8.3f}   translate {num(tx):>10} {num(ty):>8}")
        print(f"  assets     {sum(len(p) for _, _, p in ASSETS)} points in "
              f"{len(ASSETS)} kinds; {len(OFFICES)} offices; {len(MARKETS)} markets")
        for name, lines in BLOCKS.items():
            print(f"\n<!-- {MARK}: {name} -->")
            for l in lines:
                print(l)
            print(f"<!-- {MARK}: end {name} -->")
        return 0

    text = PAGE.read_text(encoding="utf-8")
    new, n = splice(text)
    if n != len(BLOCKS):
        print(f"gen-world-map: found {n} of {len(BLOCKS)} blocks — the markers went stale")
        return 1
    if args.write:
        if new != text:
            PAGE.write_text(new, encoding="utf-8")
            print(f"  wrote {PAGE.relative_to(ROOT)}")
        else:
            print(f"  {PAGE.relative_to(ROOT)} already current")
    elif new != text:
        print("gen-world-map: the prototype's map is not what this script "
              "generates — re-run with --write")
        return 1
    if args.check:
        print(f"gen-world-map: the map is the generator's output "
              f"({sum(len(v) for v in BLOCKS.values())} lines in {len(BLOCKS)} blocks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
