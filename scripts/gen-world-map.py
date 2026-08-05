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
# BOTH PAGES THAT DRAW THE MAP, AND THE SECOND ONE IS THE ONE THAT SHIPS.
# This listed the prototype alone. The shipping page carries the same six
# generated blocks -- byte-identical, 62 kB of coastline, points, labels and
# legend -- spliced in by hand when the acts moved and never read by the script
# again. So `--check` said "the map is the generator's output" while looking at
# neither of the two files a reader ever loads it from, and the claim this
# generator exists to make was true of the lab and unenforced everywhere else.
# They agree today because nobody has edited one of them yet.
#
# THE SHIPPING PAGE IS expertise.html NOW. The map was act 5 of the landing
# page and is section 04 of the expertise page: same markup, same six blocks,
# under the four fields where the question it answers is the page's own. The
# prototype keeps it as the lab record, which is why this tuple is still two
# entries and not one.
PAGES = (
    ROOT / "design-system" / "prototypes" / "statement-to-process.html",
    ROOT / "design-system" / "patterns" / "expertise.html",
)
# THE CAMERA'S THREE FRAMINGS ARE CSS, AND THE CSS MOVED. Six of the seven
# blocks are markup and live in the pages; the shots block is the ratio and
# three custom properties and went with the acts when they left the prototype's
# <style> for a stylesheet of their own. One generator, three targets, and the
# block itself says which kind it belongs to.
ACTS = ROOT / "design-system" / "assets" / "css" / "acts.css"
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

# THE HOME MARKET, and it is one country. The ISO code is the vendored file's
# own key so a typo is an AssertionError rather than an empty fill.
HOME = "DEU"

# EUROPE, as a window in degrees. It classifies and it frames, which is the
# whole of "Europe first": the second beat's camera is this box, and a country
# lit by a point inside it is drawn one weight above a country lit outside it.
EUROPE = (-25.0, 34.0, 45.0, 72.0)     # lon0, lat0, lon1, lat1

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
assert HOME in LAND, f"{HOME} is not in the vendored geodata"


# THE SECOND BEAT IS DERIVED FROM THE THIRD, which is the point of the review
# note this answers: the markets beat used to name two countries and draw them
# at one weight, so United Kingdom carried the same lime ramp, the same lattice
# and the same country label as the home market, and the eleven other countries
# the next beat puts a point on carried nothing at all.
#
# THE RULE IS THE LAND A LATER POINT STANDS ON. Every asset point is tested
# against the coastlines already vendored here, so adding a point to ASSETS
# lights its country and nothing has to be kept in step by hand.
#
# NINE OF THE TWENTY-SEVEN STAND ON NO LAND, and the count is printed so it
# cannot drift unnoticed. Six are the offshore kind and the copy says so in as
# many words ("Schiffe und Offshore-Plattformen auf See") -- those are correct
# to leave dark. Three are the 110m simplification: a battery point on the
# Mexican gulf coast, which costs nothing because MEX is lit by its two
# siblings, and the two aviation hubs at Dubai and Singapore, which cost the
# drawing ARE. A nearest-coast tolerance would find Dubai at 0.16 degrees --
# and would find MALAYSIA for Singapore at 0.05, a country this page would then
# be making a claim about. So the strict test is the honest one, and this is
# the note that says which country the drawing therefore leaves dark.
def contains(ring, lon, lat):
    inside = False
    for i, (x0, y0) in enumerate(ring):
        x1, y1 = ring[(i + 1) % len(ring)]
        if (y0 > lat) != (y1 > lat) and lon < (x1 - x0) * (lat - y0) / (y1 - y0) + x0:
            inside = not inside
    return inside


def locate(lon, lat):
    """The ISO code of the country a point stands on, or None for open water."""
    for iso in sorted(LAND):
        if any(contains(r, lon, lat) for r in LAND[iso]):
            return iso
    return None


def in_europe(lon, lat):
    return EUROPE[0] <= lon <= EUROPE[2] and EUROPE[1] <= lat <= EUROPE[3]


# NEAR and FAR, in the drawing's own order -- the reader meets them as the
# legend's kinds arrive, so the lists are built in that order and not sorted.
NEAR, FAR = [], []
for _kind, _label, _places in ASSETS:
    for _lon, _lat in _places:
        _iso = locate(_lon, _lat)
        if _iso is None or _iso == HOME or _iso in NEAR or _iso in FAR:
            continue
        (NEAR if in_europe(_lon, _lat) else FAR).append(_iso)

# THE THREE WEIGHTS, and each is one layer more than the one below it. The home
# market carries the ramp, the lattice and the contour; Europe carries the
# lattice and the contour; everywhere else carries the contour. So "Deutschland
# und die ganze Welt" is drawn as a decay and "Europe first" is the middle term
# of it, rather than either being a sentence the picture does not support.
LIT = [HOME] + NEAR + FAR              # a stronger contour than the world's
WEAVE = [HOME] + NEAR                  # the isometric lattice as well
RAMP = [HOME]                          # and the lime ramp on top of that


def ring_path(ring):
    pts = [merc(lon, lat) for lon, lat in ring]
    out = [f"M{num(pts[0][0])} {num(pts[0][1])}"]
    out += [f"L{num(x)} {num(y)}" for x, y in pts[1:]]
    return "".join(out) + "Z"


def country_path(iso):
    return "".join(ring_path(r) for r in LAND[iso])


# THE TIER'S INK IS THE TIER. France is lit by a solar point outside Paris, and
# France's polygon reaches to 54 degrees west, because French Guiana is France
# -- so lighting the country whole put an 8 x 10 px box of the Europe weight on
# the north-east shoulder of South America, with no point on it and nothing to
# explain it. On a drawing whose entire language is "the dark contour is where
# we are", that is a claim about a place, which is the one thing this act has
# ruled out in as many words. The Europe tier therefore draws the rings that
# are IN Europe; the rest of the country falls back to the world's own weight,
# which is what it is. Ring-level and not country-level, because the alternative
# -- lighting only the landmass the point stands on -- would leave Northern
# Ireland dark beside Britain and Tasmania dark beside Australia.
def lit_rings(iso):
    if iso in WEAVE:
        return [r for r in LAND[iso] if all(in_europe(lon, lat) for lon, lat in r)]
    return list(LAND[iso])


def split_rings(iso):
    """(drawn at the country's own weight, drawn at the world's)."""
    lit = lit_rings(iso) if iso in LIT else []
    keep = {id(r) for r in lit}
    return lit, [r for r in LAND[iso] if id(r) not in keep]


def rings_path(rings):
    return "".join(ring_path(r) for r in rings)


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


# THE SECOND SHOT IS EUROPE AND IT IS CLIPPED TO THE WINDOW, which is not a
# nicety. France's polygon reaches to 54 degrees west, because French Guiana is
# France; framed off the raw bounding box the "Europe" shot came out at scale
# 2.37 with the Atlantic and half of South America in it. Clipped to EUROPE it
# is 4.89, which lands the camera exactly between the Germany zoom's 14.25 and
# the world's 1.0 -- three steps back, evenly spaced, which is what the act
# says it does.
def europe_points(iso):
    return [merc(lon, lat) for r in LAND[iso] for lon, lat in r if in_europe(lon, lat)]


SHOTS = [
    ("de",     framing(country_points(HOME))),
    ("europa", framing(sum((europe_points(i) for i in WEAVE), []))),
    ("welt",   (1.0, 0.0, 0.0)),
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
    lit, rest = split_rings(iso)
    if lit:
        emit(f'<path class="map__land map__land--market" d="{rings_path(lit)}"/>')
    if rest:
        emit(f'<path class="map__land" d="{rings_path(rest)}"/>')

block("fill")
for iso in RAMP:
    emit(f'<path class="map__fill" d="{rings_path(lit_rings(iso))}"/>')
for iso in WEAVE:
    emit(f'<path class="map__weave" d="{rings_path(lit_rings(iso))}"/>')

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
# ONE NAME AT THIS STAGE, AND IT IS THE HOME MARKET'S. The second beat used to
# print DEUTSCHLAND and UNITED KINGDOM at the same size in the same ink, which
# is the co-equal reading the review asked to be taken off it. The other eleven
# countries are not given labels in its place: the drawing already says which
# they are by weight, the copy names the regions in prose, and eleven names at
# a Europe framing is a legend, not a map.
x0, y0, x1, y1 = bbox(country_points(HOME))
px, py = place(((x0 + x1) / 2, (y0 + y1) / 2), SHOTS[1][1])
emit(f'<span class="t-label map__tag map__tag--land" style="--s:1;--i:0;'
     f'--x:{num(px)}%;--y:{num(py)}%">Deutschland</span>')

# A KEY, THEN A TALLY, AND ONLY THE KEY CAN CARRY A SWATCH. This block used to
# be six rows each carrying the same lime dot -- six names against one mark, so
# no point on the drawing could be assigned to a line, while the two points the
# map DOES draw differently, the black offices, stood in no row at all. Six
# marks is not the repair: the drawing has one accent, and two of these kinds
# already share a coordinate (Dubai is `see` and `luft` 0.2 degrees apart, and
# so is Singapore), so a per-kind colour would have to put two of them on one
# dot. What the map draws is TWO marks, and those are what the key states. The
# kinds keep their names and their counts as the tally of the second one, in a
# second list under it, without a swatch that would promise a code. The two
# lists carry one class between them: what tells them apart is the swatch in
# the first, which is markup, and a modifier that styled nothing would be a
# name for a difference the stylesheet does not make.
block("legend")
emit('<div class="map__legends">')
emit('  <ul class="map__legend" role="list">')
for i, (mod, label, n) in enumerate((("office", "Standorte", len(OFFICES)),
                                     ("asset", "Anlagen",
                                      sum(len(p) for _, _, p in ASSETS)))):
    emit(f'    <li class="map__key" style="--i:{i}">'
         f'<span class="map__key-dot map__key-dot--{mod}" aria-hidden="true"></span>'
         f'<span class="t-label map__key-name">{label}</span>'
         f'<span class="map__key-n">{n}</span></li>')
emit('  </ul>')
emit('  <ul class="map__legend" role="list">')
for i, (kind, label, places) in enumerate(ASSETS):
    emit(f'    <li class="map__key" style="--k:{kind};--i:{i + 2}">'
         f'<span class="t-label map__key-name">{label}</span>'
         f'<span class="map__key-n">{len(places)}</span></li>')
emit('  </ul>')
emit('</div>')

block("shots")
# THE DRAWING'S OWN RATIO, AND IT IS NOT THE BOX'S. A label carries --x/--y as
# a percentage of the viewBox -- that is what place() computes -- and is
# positioned as a percentage of .map-box. The two are the same number only
# while the box has the viewBox's shape. Above the pin gate it does not: the
# stage gives the map row `minmax(0, 1fr)` of whatever is left after the copy
# and the legend, preserveAspectRatio="xMidYMid meet" fits the drawing inside
# that row and centres it, and every label slides off the point it names by
# half the letterbox. Measured on the shipped page at the Germany framing,
# label anchor minus the point it names, horizontally:
#
#   viewport     box aspect   Konstanz   Berlin   Deutschland   United Kingdom
#    320- 768      1.7943       0.0       0.0        0.0            0.0
#   1024x 800      2.3633     -12.4     +27.0      +39.1          -38.4
#   1280x 900      2.4016     -16.4     +35.8      +51.8          -51.0
#   1440x 900      2.4952     -18.9     +41.3      +59.8          -58.8
#   1920x1080      1.8471      -1.9      +4.2       +6.1           -6.0
#
# It is L * (1 - 2x) with L the half-letterbox, so it is zero at the middle of
# the drawing and worst at its edges, and it flips sign across the centre --
# which is why the four move in different directions and by different amounts
# and none of it reads as one displacement. Below the gate `.map` takes its
# intrinsic height, the box IS the drawing, and the drift is 0.0 at every
# width: the fault only exists where the box is given a height of its own.
#
# So acts.css rebuilds `meet` for the label layer, and it needs one number to
# do it: the ratio the viewBox has. That number is VIEW, which is computed
# here from LAT_TOP/LAT_BOT, so it is emitted here rather than typed there --
# a hand-written 1.7943 beside a computed viewBox is two numbers that have to
# agree with nothing checking that they do.
emit(f'--map-ar: {VIEW[2] / VIEW[3]:.6f};')
for name, (k, tx, ty) in SHOTS:
    emit(f'--cam-{name}: translate({num(tx)}px, {num(ty)}px) scale({num(k)});')


# THE SHOTS BLOCK LIVES IN CSS AND THEREFORE IN CSS COMMENTS. Everything else
# is markup and carries HTML markers; the three camera transforms are custom
# properties and have to sit in a rule. One splice, two comment syntaxes, and
# the block itself decides which — rather than a second script for one block.
CSS_BLOCKS = {"shots"}


def splice(text, css=False):
    total = 0
    for name, lines in BLOCKS.items():
        if (name in CSS_BLOCKS) != css:
            continue
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
        _dark = sum(1 for _, _, ps in ASSETS for p in ps if locate(*p) is None)
        print(f"  assets     {sum(len(p) for _, _, p in ASSETS)} points in "
              f"{len(ASSETS)} kinds; {len(OFFICES)} offices; {_dark} on open water")
        print(f"  lit        {HOME} + ramp | {' '.join(NEAR)} + lattice | "
              f"{' '.join(FAR)} | {len(LIT)} of {len(LAND)} countries")
        for name, lines in BLOCKS.items():
            print(f"\n<!-- {MARK}: {name} -->")
            for l in lines:
                print(l)
            print(f"<!-- {MARK}: end {name} -->")
        return 0

    targets = [(p, False) for p in PAGES] + [(ACTS, True)]
    # What each target owes: the markup blocks go to every page, the css block
    # to the stylesheet. Counted per target rather than in one total, so a page
    # that has lost a marker is named instead of being covered by a page that
    # still has all six.
    want = {False: sum(1 for n in BLOCKS if n not in CSS_BLOCKS),
            True: sum(1 for n in BLOCKS if n in CSS_BLOCKS)}
    missing, stale = [], False
    for target, css in targets:
        text = target.read_text(encoding="utf-8")
        new, n = splice(text, css=css)
        if n != want[css]:
            missing.append(f"{target.relative_to(ROOT)}: {n} of {want[css]} blocks")
        if args.write:
            if new != text:
                target.write_text(new, encoding="utf-8")
                print(f"  wrote {target.relative_to(ROOT)}")
            else:
                print(f"  {target.relative_to(ROOT)} already current")
        elif new != text:
            stale = True
    if missing:
        print("gen-world-map: the markers went stale —")
        for m in missing:
            print(f"  {m}")
        return 1
    if stale:
        print("gen-world-map: the shipped map is not what this script "
              "generates — re-run with --write")
        return 1
    if args.check:
        print(f"gen-world-map: the map is the generator's output "
              f"({sum(len(v) for v in BLOCKS.values())} lines in {len(BLOCKS)} blocks, "
              f"in {len(targets)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
