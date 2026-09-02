#!/usr/bin/env python3
"""The app icon, and the manifest that names it.

WHAT THIS CLOSES. The brand manual's frame chapter defines five frames for the
signet and the web had built two of them. `assets/img/logo/cf-favicon.svg` is
the transparent frame, and `foundations/logo.html` renders the square one as
the nav plate; the App-Icon frame — a black tile with the mark standing on it —
had nowhere to be. The favicon's own header is where the gap is written down
most plainly. It argues the plate OFF the tab strip, and the reason it gives is
that "a filled near-black square with a rounded corner reads as an app icon
rather than as this company's mark". That reasoning is right and it hands the
plate somewhere. Nothing was there to catch it: 138 pages shipped one browser
surface declaration between them, `rel="icon"`, and a reader who kept the site
on a home screen got the platform's own thumbnail of a screenshot.

THE TILE IS SQUARE AND THE PLATFORM ROUNDS IT. The manual draws the App-Icon
frame with a corner radius, and the system's corner rule allows exactly three
rounded things — the logo pill, the nav pill, the avatar. Neither has to give:
iOS, Android and every launcher since have applied their own mask to a
full-bleed square for years, and a maskable icon is required to be full-bleed
with its content inside the centre circle of 80 % diameter. So the artwork keeps
the system's square corner, the platform draws the manual's radius, and the
radius nobody in this repository has to choose is the one the reader's own
launcher is already using for every other icon beside it.

  ground   CF-Schwarz, full bleed. The opaque layer — the second of the six,
           and the only one an icon has room for.
  mark     cf-symbol-black.svg's two paths, unchanged, at 56 % of the tile.
           Scaled that way the mark's own diagonal is 71.7 % of the tile,
           inside the 80 % maskable circle with 8.3 points to spare, which is
           what check-app-icon.py measures rather than assumes.
  light    the light family's ramp across the mark, Lime through Glas to
           Weiss, on the rake --gradient-light is drawn at. The mark is not
           painted lime; it is painted white and lit, which is the difference
           the light chapter is about. One lime moment, and the icon has room
           for exactly one.

WHY THE RAMP ENDS AT WEISS AND NOT AT CF-GRAU. Every ramp in the light family
falls off to the ground it stands on, and on the page that ground is CF-Grau.
Here it is Schwarz, and a mark that falls off to its own ground disappears —
the far end of this ramp has to stay a mark. Weiss is where the falloff stops
instead: the same three-quarters of the family's leg, ending at the brightest
thing the palette has rather than at the dimmest. Lime is 18.5:1 on Schwarz and
Weiss is 21:1, so the mark clears the 3:1 floor for a graphical object at both
ends of the ramp and everywhere between them.

THE MANIFEST IS GENERATED HERE FOR ONE REASON: its theme colour is a number
that already exists. `--wash-stops` opens the page wash at #CFCFD2, the browser
paints its own chrome directly above that, and a `theme_color` typed by hand is
a second copy of a token that moves. It is read out of tokens.css on every run.

THE OUTPUT IS NOT COMMITTED, which is the rule .gitignore already sets for the
share plates and for every generated page on this site. `scripts/build-all.sh`
writes them before either deploy stages, and `--check` re-renders and compares
bytes, so an icon that was edited by hand rather than generated fails rather
than being silently rebuilt.

    python3 scripts/build-app-icons.py            # write them
    python3 scripts/build-app-icons.py --check    # fail if any is stale
    python3 scripts/build-app-icons.py -v         # name every file
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "og-plate"))

import png                                                          # noqa: E402
import raster                                                       # noqa: E402

OUT = os.path.join(REPO, "design-system", "assets", "icon")
SYMBOL = os.path.join(REPO, "design-system", "assets", "img", "logo",
                      "cf-symbol-black.svg")
TOKENS = os.path.join(REPO, "design-system", "assets", "css", "tokens.css")

# apple-touch-icon is 180 because that is what iOS asks for at 3x and it is the
# one size Safari will not derive from another. 192 and 512 are the two the
# manifest specification names outright. Nothing else: a launcher downsamples
# better than this rasteriser would, and every extra size is another file that
# can go stale on its own.
SIZES = (180, 192, 512)

# The mark's width as a fraction of the tile. See the header: this is the
# number the maskable safe zone is measured against, and check-app-icon.py
# re-derives the diagonal from it rather than trusting this comment.
MARK_WIDTH = 0.56

# The light family's ramp, on the leg this tile has room for. The waypoint at
# 19 % of the lime leg is the family's one SVG convention — it is what makes an
# sRGB ramp track the oklab path the family is defined on — and it is the same
# #DBFC60 the six planes on the front door are drawn with.
# → assets/css/tokens.css, scripts/check-gradient-family.py
LIME_LEG = 0.45
RAMP = ((0.0,                  "#E1FF00"),
        (LIME_LEG * 0.19,      "#DBFC60"),
        (LIME_LEG,             "#C5EBE2"),
        (1.0,                  "#FFFFFF"))

# THE SHALLOW ISOMETRIC RAKE, 116.57deg, WHICH IS 26.57 OFF THE HORIZONTAL.
# The page's own --gradient-light is raked at 132.36deg, and that number is the
# designer's, off the Figma spec, kept because it is what the mockups measure.
# It is not a brand angle, and it does not belong on a drawing this small: the
# signet is an isometric object whose own long edges run at 2:1, so lighting it
# along its own axis is one decision instead of two. It is also the only choice
# that survives check-gradient-angle.py, which holds every SVG in the tree to
# the manual's four angles — and the figure on foundations/outside.html is an
# SVG of exactly this drawing.
#
# A CSS gradient angle is measured clockwise from "to top", so the axis runs
# (sin a, -cos a) in a coordinate system whose y counts UP — and this canvas
# counts down, which flips the second sign back. The result points right and
# down: Lime at the mark's leading tip, Weiss past its trailing one.
RAKE_DEG = 116.565051

GROUND = "#000000"

_D = re.compile(r'\sd="([^"]+)"')
_VIEWBOX = re.compile(r'viewBox="([^"]+)"')
_WASH_HEAD = re.compile(r"--wash-stops:\s*(#[0-9A-Fa-f]{6})")


def theme_colour():
    """The first stop of the page wash, which is what the chrome sits above."""
    src = open(TOKENS, "r", encoding="utf-8").read()
    m = _WASH_HEAD.search(src)
    if not m:
        raise ValueError("tokens.css: --wash-stops does not open with a hex")
    return m.group(1).upper()


def symbol():
    """The signet's contours and its viewBox, as one even-odd shape."""
    src = open(SYMBOL, "r", encoding="utf-8").read()
    if "transform=" in src:
        raise ValueError("cf-symbol-black.svg carries a transform")
    vb = [float(v) for v in _VIEWBOX.search(src).group(1).replace(",", " ").split()]
    contours = []
    for d in _D.findall(src):
        contours.extend(raster.path_contours(d))
    return contours, vb


def render(size):
    """One tile: the ground, then the mark, lit."""
    import math

    cv = raster.Canvas(size, size)
    r, g, b = raster.hex_rgb(GROUND)
    cv.px[:] = bytes((r, g, b)) * (size * size)

    contours, vb = symbol()
    vx, vy, vw, vh = vb
    scale = (size * MARK_WIDTH) / vw
    ox = (size - vw * scale) / 2.0 - vx * scale
    oy = (size - vh * scale) / 2.0 - vy * scale
    placed = [[(x * scale + ox, y * scale + oy) for x, y in ring]
              for ring in contours]

    # The ramp's axis. It is laid across the MARK's box rather than the tile's,
    # so every size gets the same slice of the ramp and the 180 and the 512 are
    # the same drawing at two resolutions.
    a = math.radians(RAKE_DEG)
    ux, uy = math.sin(a), -math.cos(a)
    x0 = (size - vw * scale) / 2.0
    y0 = (size - vh * scale) / 2.0
    x1, y1 = x0 + vw * scale, y0 + vh * scale
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    # Half the box's extent along the axis, so the ramp starts and ends exactly
    # at the mark's own corners on that direction and nothing is clamped away.
    half = abs((x1 - x0) / 2.0 * ux) + abs((y1 - y0) / 2.0 * uy)
    light = raster.Gradient((cx - ux * half, cy - uy * half),
                            (cx + ux * half, cy + uy * half), RAMP)
    cv.fill_many(placed, light)
    return cv


def manifest_text():
    """The manifest, as one string, so --check compares it like a rendering.

    Every address in it is relative. There is no CNAME on the Pages deploy, so
    the document root is /control-f-website/ there and / on Cloudflare, and a
    manifest that named either would be right on one host and wrong on the
    other. A relative start_url resolves against the manifest's own address,
    which is three levels below the site root on both.
    """
    theme = theme_colour()
    doc = {
        "name": "Control-F",
        "short_name": "Control-F",
        "lang": "de",
        "dir": "ltr",
        "description": "Daten- und KI-Loesungen, die komplexe Daten in messbare "
                       "Ergebnisse verwandeln.",
        "start_url": "../../../",
        "scope": "../../../",
        # A website, and it says so. display: standalone would take the address
        # bar away from a reader who did not ask for an app, and this manifest
        # is here for the icon and the two colours, not to be installed.
        "display": "browser",
        "theme_color": theme,
        "background_color": theme,
        "icons": [
            {"src": "cf-app-icon-192.png", "sizes": "192x192",
             "type": "image/png", "purpose": "any"},
            {"src": "cf-app-icon-512.png", "sizes": "512x512",
             "type": "image/png", "purpose": "any"},
            {"src": "cf-app-icon-512.png", "sizes": "512x512",
             "type": "image/png", "purpose": "maskable"},
        ],
    }
    return json.dumps(doc, indent=2, ensure_ascii=True) + "\n"


def _settle(path, fresh, check, verbose, stale, written):
    old = None
    if os.path.exists(path):
        old = open(path, "rb").read()
    name = os.path.basename(path)
    if check:
        if old != fresh:
            stale.append(name)
        elif verbose:
            print("  ok    %s" % name)
        return written
    if old == fresh:
        if verbose:
            print("  ok    %s" % name)
        return written
    tmp = path + ".new"
    with open(tmp, "wb") as fh:
        fh.write(fresh)
    os.replace(tmp, path)
    print("  write %s  (%d KB)" % (name, max(1, len(fresh) // 1024)))
    return written + 1


def build(check=False, verbose=False):
    if not check:
        os.makedirs(OUT, exist_ok=True)
    elif not os.path.isdir(OUT):
        print("build-app-icons: design-system/assets/icon/ does not exist —\n"
              "  run `python3 scripts/build-app-icons.py`.", file=sys.stderr)
        return 1

    stale, written = [], 0
    for size in SIZES:
        cv = render(size)
        path = os.path.join(OUT, "cf-app-icon-%d.png" % size)
        tmp = path + ".render"
        png.write_rgb(tmp, cv.w, cv.h, cv.px)
        fresh = open(tmp, "rb").read()
        os.remove(tmp)
        written = _settle(path, fresh, check, verbose, stale, written)

    written = _settle(os.path.join(OUT, "site.webmanifest"),
                      manifest_text().encode("utf-8"),
                      check, verbose, stale, written)

    if check:
        if stale:
            print("build-app-icons: %d file(s) stale or missing — %s\n"
                  "  run `python3 scripts/build-app-icons.py`."
                  % (len(stale), ", ".join(stale)), file=sys.stderr)
            return 1
        print("app icons OK — %d tiles and the manifest, all current."
              % len(SIZES))
        return 0

    print("app icons: %d file(s) written, %d already current."
          % (written, len(SIZES) + 1 - written))
    return 0


def main(argv):
    return build(check="--check" in argv,
                 verbose="-v" in argv or "--verbose" in argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
