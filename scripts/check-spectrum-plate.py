#!/usr/bin/env python3
"""The spectrum's authority is a raster plate, and nothing had ever read it.

Every other number in the light family is re-derived by something. The rakes are
renormalised out of the Figma dump and check-gradient-family.py recomputes both
foils' waypoints from the palette rather than trusting their hexes;
check-wash-derivation.py recomputes the page wash's three literals from
--cf-grau and the foil's own geometry. One claim in the family had no arithmetic
under it at all, because its source is not a number — it is a JPEG:

    Lime -> Weiss -> Glas -> Sky -> Violett is the brand's own spectrum: it is
    the order of the column on Farben > Dosierung.

tokens.css says that, foundations/colors.html says it, and the plate it names
sits in the repository at assets/source/manual/colour-dosage.jpg. A sentence
about a picture, with the picture right there and nothing looking at it.

WHAT THE PLATE ACTUALLY DRAWS. There is a narrow ramp column at the right of
that plate, 654 px of it, and it is the brand's spectrum drawn as one
continuous material. Sampled and matched against the palette by OKLab distance:

    stop           position   dEok    what it is
    --cf-weiss        0.00 %  0.0116  the head. WHITE, and it is BEFORE lime
    --cf-lime        21.29 %  0.0050
    --cf-glas        44.41 %  0.0119
    --cf-sky         64.47 %  0.0042  CORE Sky, not sky-300
    --cf-violett     81.16 %  0.0123  CORE Violett, not violett-300
    --violett-900    98.93 %  0.0041  the tail
    Schwarz               --  0.1518  NEVER APPEARS on the column

The last row is the one worth having measured. tokens.css argues the ink foil
must not be "completed" by adding Schwarz at 0 % — "that puts a 0.426 span on a
ramp whose whole claim is a 0.115 one, and it reads as a fade to black" — and
that argument was made from the arithmetic alone. The designer's own plate makes
it too: the column bottoms out in violett-900 and never reaches black. The
system's two foils are the middle of this column, split; the plate draws it
whole, highlight to shadow, and the lit half and the ink half are visibly one
material rather than two ramps asserted to be related.

TWO PLACES THE IMPLEMENTATION DIFFERS, both reported by this script and neither
fixed by it, because a difference between two of the designer's own sources is
a design decision and not a defect:

    THE WHITE IS ON THE OTHER SIDE OF LIME. The plate opens on Weiss and lime is
    its first coloured stop. --spectrum-stops puts Weiss AFTER lime, at
    --spectrum-hot. That placement's authority is the hero artwork rather than
    this plate — "lime at the lit edge, a white hot spot, then cyan, blue and
    violet in the falloff" — so the two sources genuinely disagree and the
    system follows the moving one.

    THE TWO CHROMATIC POSITIONS COME FROM THE RAKES. Renormalised onto the
    family's own axis (lime = 0, Violett = 100) the plate puts Glas at 38.6 %
    and Sky at 72.1 %. --spectrum-stops puts them at --rake-near (32) and
    --rake-far (64), both measured off the process-card Figma dump. Moving them
    to the plate's figures would move --gradient-spectrum, both foils and the
    page wash's three literals at once; it is a brand decision with a page-wide
    blast radius, not a correction to make on the way past.

Sky at 64.47 % of the COLUMN and --rake-far-n at 64 is the coincidence that
makes the second one worth stating out loud: 64 is the plate's number read from
the top of the column, and the family's axis starts at lime.

WHAT IS GATED. The claim the system actually makes -- the ORDER, and that each
stop is a palette value -- plus the two things the plate settles: that the head
is Weiss and that the tail is not Schwarz. The POSITIONS are held to the table
published in foundations/colors.html, so the prose and the plate cannot drift
apart; the palette hexes come out of tokens.css, so moving a palette value
re-measures it against the picture instead of against a copy.

The browser is how a JPEG gets decoded without a dependency: Chromium draws it
to a canvas and hands back pixels, the same way check-text-zoom.py borrows a
layout engine rather than reimplementing one. No playwright, no Chromium, no
run -- CI has both, and CF_REQUIRE_BROWSER makes the skip a failure.

    python3 scripts/check-spectrum-plate.py          # check, exit 1 on drift
    python3 scripts/check-spectrum-plate.py -v       # print the sampled column
"""

import argparse
import http.server
import math
import os
import re
import socketserver
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
TOKENS = DS / "assets" / "css" / "tokens.css"
COLOURS = DS / "foundations" / "colors.html"
PLATE = "design-system/assets/source/manual/colour-dosage.jpg"

BROWSER_CANDIDATES = (
    os.environ.get("CF_BROWSER"),
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    "/opt/pw-browsers/chromium/chrome-linux/chrome",
)

# How close a sampled row has to come to a palette value for that value to count
# as ON the column. The worst of the six is Glas at 0.0119 and the worst thing
# that is NOT on the column is Schwarz at 0.1518, so the ceiling sits an order of
# magnitude below the nearest false positive. JPEG at this size costs about half
# of the budget; the rest is the 8-bit grid.
DE_CEILING = 0.020

# Schwarz has to stay OFF the column by at least this. It measures 0.1518.
DE_FLOOR = 0.080

# How far a published position may sit from the measured one, in points of the
# column. The column is 654 px, so one point is 6.5 px and the tolerance is
# about three pixels of JPEG edge either way.
POSITION_TOLERANCE = 0.5

# The row at 20 % and the row at 80 % of a ramp column are far apart in OKLab;
# in a flat block they are the same colour. Anything under this is not a ramp.
RUN_DE = 0.35

# A ramp changes colour on nearly every row. A staircase of flat blocks changes
# on a handful. This is what tells the plate's gradient column from the grey
# steps beside it, which are wider and would win a widest-run contest.
ROW_CHANGE = 0.9


# --- colour -----------------------------------------------------------------

def _linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def oklab(rgb):
    r, g, b = (_linear(v) for v in rgb)
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = (v ** (1 / 3) if v > 0 else -((-v) ** (1 / 3)) for v in (l, m, s))
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def dE(a, b):
    return math.dist(oklab(a), oklab(b))


def to_rgb(hexv):
    h = hexv.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# --- what the system says ---------------------------------------------------

COMMENT = re.compile(r"/\*.*?\*/", re.S)

# The stop list the docs publish, and the order is part of the claim.
PLATE_ROW = re.compile(
    r"<tr>\s*<td><code>(--[\w-]+)</code></td>\s*<td>([0-9.]+)&nbsp;%</td>", re.S)
PLATE_TABLE = re.compile(
    r'<table class="docs-table" id="plate-column">(.*?)</table>', re.S)


def read_palette(names):
    """The palette hexes, off tokens.css rather than off a copy of them."""
    bare = COMMENT.sub("", TOKENS.read_text(encoding="utf-8"))
    out = {}
    for name in names:
        m = re.search(r"%s\s*:\s*(#[0-9A-Fa-f]{6})\s*;" % re.escape(name), bare)
        if m:
            out[name] = m.group(1).upper()
    return out


def read_published():
    """The stops and positions foundations/colors.html publishes for the plate."""
    m = PLATE_TABLE.search(COLOURS.read_text(encoding="utf-8"))
    if not m:
        return None
    return [(row[0], float(row[1])) for row in PLATE_ROW.findall(m.group(1))]


# --- what the plate says ----------------------------------------------------

READ_IMAGE = """async (url) => {
  const img = new Image();
  img.src = url;
  await img.decode();
  const c = document.createElement('canvas');
  c.width = img.naturalWidth;
  c.height = img.naturalHeight;
  const x = c.getContext('2d', {willReadFrequently: true});
  x.drawImage(img, 0, 0);
  return {w: c.width, h: c.height,
          d: Array.from(x.getImageData(0, 0, c.width, c.height).data)};
}"""


class Quiet(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    def log_message(self, *a):
        pass


def serve():
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer(("127.0.0.1", 0), Quiet)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def launch(ctx):
    try:
        return ctx.chromium.launch()
    except Exception:
        pass
    for candidate in BROWSER_CANDIDATES:
        if candidate and Path(candidate).exists():
            try:
                return ctx.chromium.launch(executable_path=candidate)
            except Exception:
                continue
    return None


def find_column(px, w, h):
    """The ramp column's x range, found rather than hard-coded.

    Two passes, because the obvious one picks the wrong column. Contiguous runs
    of x where the top of the plate and the bottom of it are far apart in OKLab
    catch the gradient column AND the staircase of grey blocks beside it, and
    the staircase is twenty-six times wider. So the runs are then scored on how
    many ROWS change: a ramp changes on nearly every one of them, a stack of
    flat blocks changes on as many rows as it has seams.
    """
    ramped, runs, cur = [], [], None
    for x in range(w):
        ramped.append(dE(px(x, int(h * 0.20)), px(x, int(h * 0.80))) > RUN_DE)
    for x in range(w):
        if ramped[x]:
            cur = (x, x) if cur is None else (cur[0], x)
        elif cur:
            runs.append(cur)
            cur = None
    if cur:
        runs.append(cur)
    runs = [r for r in runs if r[1] - r[0] >= 6]
    if not runs:
        return None

    def changing_rows(run):
        xm = (run[0] + run[1]) // 2
        n, prev = 0, None
        for y in range(int(h * 0.15), int(h * 0.85)):
            c = px(xm, y)
            if prev is not None and math.dist(c, prev) > ROW_CHANGE:
                n += 1
            prev = c
        return n

    best = max(runs, key=changing_rows)
    # Three columns of inset either side: a JPEG puts ringing on a hard vertical
    # edge and the column's neighbours are a black block and the page grey.
    return best[0] + 3, best[1] - 3


def sample(px, x0, x1, h):
    """The column averaged across its width, and its vertical extent.

    Averaging the width is what takes the chroma noise out: the ramp is one
    colour per row by construction, so every pixel across it is a second reading
    of the same value.
    """
    def row(y):
        r = g = b = 0
        for x in range(x0, x1 + 1):
            p = px(x, y)
            r += p[0]
            g += p[1]
            b += p[2]
        n = x1 - x0 + 1
        return (r / n, g / n, b / n)

    lit = [y for y in range(h) if dE(row(y), (207, 207, 207)) > 0.06]
    if not lit:
        return None, None, None
    y0, y1 = min(lit) + 2, max(lit) - 2
    return y0, y1, {y: row(y) for y in range(y0, y1 + 1)}


def position_of(rows, y0, y1, target):
    """Where the column comes closest to a colour, and how close it gets.

    Model-free on purpose. Fitting stop positions needs an interpolation space
    and an endpoint list, and both are guesses about a file nobody here wrote;
    the nearest approach is a fact about the pixels.
    """
    best = min(range(y0, y1 + 1), key=lambda y: dE(rows[y], target))
    return (best - y0) / (y1 - y0) * 100.0, dE(rows[best], target), rows[best]


# --- the run ----------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()
    required = bool(os.environ.get("CF_REQUIRE_BROWSER"))

    published = read_published()
    if not published:
        print("spectrum-plate: foundations/colors.html no longer publishes a "
              "table with id=\"plate-column\", so there is nothing to hold the "
              "plate to. The measurement is the point of this gate; restore the "
              "table or delete the gate.", file=sys.stderr)
        return 1

    names = [name for name, _ in published]
    palette = read_palette(names + ["--cf-schwarz"])
    missing = [n for n in names + ["--cf-schwarz"] if n not in palette]
    if missing:
        print("spectrum-plate: tokens.css does not declare %s as a plain hex, so "
              "the plate cannot be measured against the palette."
              % ", ".join(missing), file=sys.stderr)
        return 1

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        msg = ("spectrum-plate: SKIPPED — playwright is not installed "
               "(pip install playwright).")
        if required:
            print(msg + " CF_REQUIRE_BROWSER is set, so this is a failure.",
                  file=sys.stderr)
            return 1
        print(msg + " The designer's spectrum plate is unread on this machine; "
                    "CI still gates it.")
        return 0

    server = serve()
    port = server.server_address[1]
    try:
        with sync_playwright() as ctx:
            browser = launch(ctx)
            if browser is None:
                msg = ("spectrum-plate: SKIPPED — no Chromium found "
                       "(playwright install chromium, or CF_BROWSER).")
                if required:
                    print(msg + " CF_REQUIRE_BROWSER is set, so this is a failure.",
                          file=sys.stderr)
                    return 1
                print(msg + " The designer's spectrum plate is unread on this "
                            "machine; CI still gates it.")
                return 0
            page = browser.new_page()
            page.goto("http://127.0.0.1:%d/design-system/index.html" % port,
                      wait_until="load")
            image = page.evaluate(READ_IMAGE,
                                  "http://127.0.0.1:%d/%s" % (port, PLATE))
            browser.close()
    finally:
        server.shutdown()

    w, h, data = image["w"], image["h"], image["d"]

    def px(x, y):
        i = (y * w + x) * 4
        return (data[i], data[i + 1], data[i + 2])

    found = find_column(px, w, h)
    if not found:
        print("spectrum-plate: no ramp column found on %s. The plate is the "
              "authority for the spectrum's order; if it has been re-exported, "
              "re-measure rather than loosening the search."
              % PLATE, file=sys.stderr)
        return 1
    x0, x1 = found
    y0, y1, rows = sample(px, x0, x1, h)
    if rows is None:
        print("spectrum-plate: the ramp column at x %d–%d is the page grey end "
              "to end." % (x0, x1), file=sys.stderr)
        return 1

    problems = []
    measured = []
    for name, claimed in published:
        pos, delta, sampled = position_of(rows, y0, y1, to_rgb(palette[name]))
        measured.append((name, claimed, pos, delta, sampled))
        if delta > DE_CEILING:
            problems.append(
                "%s (%s) is not on the plate's column: nearest approach dEok "
                "%.4f at %.2f %%, against a ceiling of %.3f."
                % (name, palette[name], delta, pos, DE_CEILING))
        elif abs(pos - claimed) > POSITION_TOLERANCE:
            problems.append(
                "%s sits at %.2f %% of the plate's column and "
                "foundations/colors.html publishes %.2f %%."
                % (name, pos, claimed))

    order = [pos for _, _, pos, _, _ in measured]
    if order != sorted(order):
        problems.append(
            "the stops do not run down the column in the published order — "
            "measured %s. The ORDER is the claim tokens.css makes about this "
            "plate; everything else is commentary on it."
            % ", ".join("%s %.2f %%" % (n, p) for n, _, p, _, _ in measured))

    black_pos, black_delta, _ = position_of(rows, y0, y1,
                                            to_rgb(palette["--cf-schwarz"]))
    if black_delta < DE_FLOOR:
        problems.append(
            "Schwarz comes within dEok %.4f of the plate's column at %.2f %%, "
            "and the floor is %.3f. tokens.css argues the shadow half must not "
            "be completed with black; that argument rests on this column "
            "bottoming out in violett-900."
            % (black_delta, black_pos, DE_FLOOR))

    if args.verbose:
        print("plate  %s" % PLATE)
        print("column x %d–%d, y %d–%d (%d px)" % (x0, x1, y0, y1, y1 - y0 + 1))
        for name, claimed, pos, delta, sampled in measured:
            print("  %-16s published %6.2f %%   measured %6.2f %%   dEok %.4f   "
                  "plate #%02X%02X%02X"
                  % (name, claimed, pos, delta, *[round(v) for v in sampled]))
        print("  %-16s %27s dEok %.4f   (must stay off the column)"
              % ("--cf-schwarz", "", black_delta))
        lime = next(p for n, _, p, _, _ in measured if n == "--cf-lime")
        vio = next(p for n, _, p, _, _ in measured if n == "--cf-violett")
        print("renormalised onto the family's axis (lime = 0, Violett = 100):")
        for name, _, pos, _, _ in measured:
            if name in ("--cf-lime", "--cf-violett"):
                continue
            print("  %-16s %6.2f %%" % (name, (pos - lime) / (vio - lime) * 100))

    if problems:
        for line in problems:
            print("  " + line, file=sys.stderr)
        print("\n%d claim%s about the designer's spectrum plate that the plate "
              "does not support. The plate is the authority — see "
              "foundations/colors.html#foil and the header of this file for the "
              "two places the implementation differs from it on purpose."
              % (len(problems), "" if len(problems) == 1 else "s"),
              file=sys.stderr)
        return 1

    print("spectrum-plate: %d stops on the designer's own column, in order, "
          "worst dEok %.4f — and Schwarz is %.4f away from it."
          % (len(measured), max(d for _, _, _, d, _ in measured), black_delta))
    return 0


if __name__ == "__main__":
    sys.exit(main())
