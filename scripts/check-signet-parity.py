#!/usr/bin/env python3
"""The signet has two implementations. This is what stops them drifting apart.

WHY THERE ARE TWO. `assets/js/cf-signet.js` draws the mark a page prints inline
and mounts into a documentation wall; `scripts/og-plate/signet.py` draws the
same mark into the share plate a crawler fetches, which runs no script at all.
Neither can do the other's job, so there are two — and two implementations of
one model is exactly the drift a design system notices about a year late, when
a page and its own share card have been showing different marks for months.

WHAT IS COMPARED, and it is the whole model:

  the lattice        W, H, STOREY, N, CX, CY, and the 120-unit viewBox
  the multiset       the nine heights, and which one is the peak
  the ramp           all four stops, offsets included — the family's #DBFC60
                     waypoint at 6.1 % is the one a rounding would eat
  the three faces    the greys off the manual's isometric stack
  the arrangement    the marks themselves, for every route that ships a plate
                     and for a set of edge seeds

THE LAST ROW IS THE ONE THAT MATTERS and it needs the JavaScript to run, so it
runs only where `node` is on PATH. Everywhere else the constants above still
hold — and they are what a person edits. A hash or a shuffle is not something
anybody changes by hand without meaning to; a lattice constant is.

    python3 scripts/check-signet-parity.py
    python3 scripts/check-signet-parity.py -v
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "og-plate"))

import signet                                                     # noqa: E402

JS = os.path.join(ROOT, "design-system", "assets", "js", "cf-signet.js")
CSS = os.path.join(ROOT, "design-system", "assets", "css", "components.css")
TOKENS_SRC = open(os.path.join(ROOT, "design-system", "assets", "css",
                               "tokens.css"), "r", encoding="utf-8").read()

# Seeds beyond the shipping routes: the empty string (the hash's own initial
# state), one character, a path, and a German string, because `charCodeAt` and
# `ord` are only guaranteed to agree below U+10000 and this asserts they do.
EDGE_SEEDS = ["", "a", "/", "control-f", "ÄÖÜ-ß", "2026-08-14-sieben-tage"]

BRIDGE = """
global.document = { readyState: 'complete', addEventListener: function () {},
                    querySelectorAll: function () { return []; } };
global.window = global;
require(%s);
JSON.parse(process.argv[2]).forEach(function (s) {
  console.log(JSON.stringify([s, CFSignet.hash(s), CFSignet.heights(s)]));
});
"""


def js_number(src, name):
    m = re.search(r"\b%s\s*=\s*(-?\d+)" % name, src)
    if not m:
        raise SystemExit("check-signet-parity: %s is gone from cf-signet.js" % name)
    return int(m.group(1))


def fail(msg):
    print("check-signet-parity: %s" % msg, file=sys.stderr)
    return 1


def main(argv):
    verbose = "-v" in argv or "--verbose" in argv
    src = open(JS, "r", encoding="utf-8").read()

    # The lattice, declared on one line: var W = 18, H = 9, STOREY = 18, ...
    lattice = {name: js_number(src, name)
               for name in ("W", "H", "STOREY", "N", "CX", "CY")}
    for name, value in lattice.items():
        if getattr(signet, name) != value:
            return fail("%s is %d in cf-signet.js and %d in og-plate/signet.py"
                        % (name, value, getattr(signet, name)))

    vb = re.search(r'viewBox="0 0 (\d+) (\d+)"', src)
    if not vb or int(vb.group(1)) != signet.VIEWBOX or int(vb.group(2)) != signet.VIEWBOX:
        return fail("the viewBox is not %d x %d in cf-signet.js any more"
                    % (signet.VIEWBOX, signet.VIEWBOX))

    heights = re.search(r"var HEIGHTS = \[([^\]]*)\];", src)
    js_heights = [int(v) for v in heights.group(1).split(",")]
    if js_heights != signet.HEIGHTS:
        return fail("the multiset is %s in cf-signet.js and %s here"
                    % (js_heights, signet.HEIGHTS))
    if js_number(src, "PEAK") != signet.PEAK:
        return fail("PEAK disagrees")

    stops = re.findall(r"{ at: '([\d.]+)%',\s*color: '(#[0-9A-Fa-f]{6})' }", src)
    js_stops = [(round(float(o) / 100.0, 6), c.upper()) for o, c in stops]
    py_stops = [(round(o, 6), c.upper()) for o, c in signet.STOPS]
    if js_stops != py_stops:
        return fail("the ramp is %s in cf-signet.js and %s here" % (js_stops, py_stops))

    # The three face greys. The JavaScript does not carry them — on a page they
    # are classes, so they answer to the theme — which puts the light register's
    # values in components.css, and that is what the plate has to match: a share
    # plate has no theme, so it draws what a reader in the light one sees.
    css = open(CSS, "r", encoding="utf-8").read()
    for name, want in (("top", signet.FACE_TOP), ("left", signet.FACE_LEFT),
                       ("right", signet.FACE_RIGHT)):
        m = re.search(r"--signet-face-%s:\s*([^;]+);" % name, css)
        if not m:
            return fail("--signet-face-%s is gone from components.css" % name)
        value = m.group(1).strip()
        if value.startswith("var("):
            token = re.search(r"var\((--[a-z0-9-]+)\)", value).group(1)
            value = re.search(r"%s:\s*(#[0-9A-Fa-f]{6})" % token, TOKENS_SRC).group(1)
        if value.upper() != want.upper():
            return fail("--signet-face-%s is %s in components.css and %s here"
                        % (name, value, want))

    print("signet parity: lattice, multiset, ramp and faces agree.")

    node = shutil.which("node")
    if not node:
        print("  the arrangements were not compared — `node` is not on PATH.")
        return 0

    seeds = list(_routes()) + EDGE_SEEDS

    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False,
                                     encoding="utf-8") as fh:
        fh.write(BRIDGE % json.dumps(JS))
        bridge = fh.name
    try:
        out = subprocess.run([node, bridge, json.dumps(seeds)],
                             capture_output=True, text=True, check=True).stdout
    finally:
        os.unlink(bridge)

    for line in out.splitlines():
        seed, h, hs = json.loads(line)
        if signet.hash32(seed) != h:
            return fail("hash disagrees for seed %r: %s vs %s"
                        % (seed, h, signet.hash32(seed)))
        if signet.heights(seed) != hs:
            return fail("the arrangement disagrees for seed %r: %s vs %s"
                        % (seed, hs, signet.heights(seed)))
        if verbose:
            print("  ok    %-28s %s" % (repr(seed), hs))
    print("  %d arrangements compared against cf-signet.js under node — identical."
          % len(seeds))
    return 0


def _routes():
    """The seeds the plates ship, read out of build-og-plates.py's PAGE_SEED.

    Imported as text rather than as a module because the file's name is not an
    identifier, and because this check has no other reason to render a plate.
    """
    src = open(os.path.join(HERE, "build-og-plates.py"), "r",
               encoding="utf-8").read()
    block = re.search(r"^PAGE_SEED = \{(.*?)^\}", src, re.M | re.S).group(1)
    return sorted(set(re.findall(r':\s*"([^"]+)"', block)))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
