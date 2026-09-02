#!/usr/bin/env python3
"""The share plates under design-system/assets/og/, one per route.

WHAT THIS CLOSES. `components/signet.html#launch` and the launch register in
design-system/README.md both said the same thing: the site ships no Open Graph
metadata at all, every link posted into LinkedIn, Slack, Teams or a message
unfurls as a bare address, and for a company whose readers pass its writing to
each other that is the most-seen brand surface there is. The text half of that
was never blocked. The picture half was blocked on one decision — every
consumer of `og:image` requires a raster, this repository has no build
dependencies, and the chapter costed three routes out of it.

THE DECISION IS ROUTE 1: a rasteriser in scripts/, written against the standard
library, owned here forever. Route 2 moved the cost to a Worker and made a
crawler's FIRST fetch a cold render — and LinkedIn caches what it gets on that
first fetch for weeks, so one cold miss is a permanently blank card. Route 3
was twenty plates exported by hand, which stops being true the day an
eleventh post is published. Route 1 costs about six hundred lines and nothing
else: no dependency, no runtime, no drift, and a plate for a route that did not
exist yesterday is one `python3 scripts/build-og-plates.py` away.

  scripts/og-plate/png.py      a PNG writer over zlib and crc32
  scripts/og-plate/raster.py   scanline fill, hairline strokes, one gradient,
                               and the logo's Bezier outlines
  scripts/og-plate/signet.py   the signet's model, ported from cf-signet.js and
                               held to it by scripts/check-signet-parity.py
  scripts/og-plate/plate.py    the plate itself — what stands where, and why

THE PLATES ARE OUTPUT AND GIT DOES NOT CARRY THEM, which is the rule
.gitignore already sets out for every generated page on this site. They are
written by scripts/build-all.sh before either deploy stages, and `--check`
re-renders every one of them and compares bytes, so a plate that was edited by
hand rather than generated fails rather than being silently rebuilt.

    python3 scripts/build-og-plates.py            # write them
    python3 scripts/build-og-plates.py --check    # fail if any is stale
    python3 scripts/build-og-plates.py -v         # name every plate

WHY ONE PLATE PER PATTERN AND NOT PER PAGE. The seed is the pattern's own stem
— `ueber-uns`, `karriere-stelle` — so the German page and its English twin
carry the SAME mark. The mark stands for the thing, not for the language it is
read in, and a reader who has seen one edition's card should recognise the
other's. It is also what makes the seed safe by the signet's own rule: a stem
is a path, and a path is not a string anybody edits for style.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "og-plate"))

import plate                                                      # noqa: E402
import png                                                        # noqa: E402

OUT = os.path.join(ROOT, "design-system", "assets", "og")

# WHICH PAGES GET A PLATE, and it is not all eighteen.
#
# A share plate is for a link somebody pastes on purpose. That is the same set
# as the pages that want to be found, so the rule is the one the pages already
# state about themselves: **a page carries Open Graph metadata exactly when it
# is not `noindex`.** scripts/check-open-graph.py holds it in both directions,
# so a page cannot gain a card without becoming findable and cannot go noindex
# while keeping one.
#
# That leaves out five, each for its own reason and all of them the same
# reason:
#
#   404.html                  served with a 404 status. Nobody shares one, and
#                             a polished card over a dead address is a lie.
#   kontakt-danke.html        noindex. The page you see after sending
#   bewerbung-danke.html      something; a link to it is a link to nothing.
#   suche.html                noindex, follow — and a second argument on top.
#   suche-leer.html           Their <title> quotes the reader's own query
#                             (`6 Treffer für „Telemetrie“`). README.md already
#                             names the three places that query is echoed into
#                             and has to be escaped in; og:title would be a
#                             fourth, on the one surface where the escaping is
#                             done by somebody else's crawler.
#
# THE SEED IS THE ROUTE, NOT THE FILE. karriere-leer.html is /karriere with
# nothing open — the same address in another state — so it carries karriere's
# mark. The mark stands for the thing, and the thing has not changed because
# its list came back empty.
PAGE_SEED = {
    "landing-page":    "landing-page",
    "expertise":       "expertise",
    "ueber-uns":       "ueber-uns",
    "news":            "news",
    "news-thema":      "news-thema",
    "blog-artikel":    "blog-artikel",
    "karriere":        "karriere",
    "karriere-leer":   "karriere",
    "karriere-stelle": "karriere-stelle",
    "kontakt":         "kontakt",
    "bewerbung":       "bewerbung",
    "datenschutz":     "datenschutz",
    "impressum":       "impressum",
}

# One plate per distinct mark, in the order above.
ROUTES = tuple(dict.fromkeys(PAGE_SEED.values()))

# WhatsApp soft-caps around 300 KB and silently downgrades anything above it, so
# a plate that grew past this is a plate that stops unfurling on the one surface
# nobody tests. It is a ceiling on the drawing, not on the encoder: the plates
# render at a twentieth of it today.
MAX_BYTES = 300 * 1024


def render(seed):
    cv = plate.render(seed)
    return cv


def build(check=False, verbose=False):
    if not check:
        os.makedirs(OUT, exist_ok=True)

    stale, written = [], 0
    for seed in ROUTES:
        path = os.path.join(OUT, "%s.png" % seed)
        cv = render(seed)
        tmp = path + ".new"
        size = png.write_rgb(tmp, cv.w, cv.h, cv.px)
        if size > MAX_BYTES:
            os.remove(tmp)
            print("build-og-plates: %s.png is %d KB, over the %d KB ceiling."
                  % (seed, size // 1024, MAX_BYTES // 1024), file=sys.stderr)
            return 1

        fresh = open(tmp, "rb").read()
        old = open(path, "rb").read() if os.path.exists(path) else None
        if check:
            os.remove(tmp)
            if old != fresh:
                stale.append(seed)
            elif verbose:
                print("  ok    %s.png" % seed)
            continue

        if old == fresh:
            os.remove(tmp)
            if verbose:
                print("  ok    %s.png" % seed)
            continue
        os.replace(tmp, path)
        written += 1
        print("  write %s.png  (%d KB)" % (seed, size // 1024))

    if check:
        if stale:
            print("build-og-plates: %d plate(s) stale or missing — %s\n"
                  "  run `python3 scripts/build-og-plates.py`."
                  % (len(stale), ", ".join(stale)), file=sys.stderr)
            return 1
        print("og plates OK — %d routes, 1200 x 630, all current." % len(ROUTES))
        return 0

    print("og plates: %d route(s) written, %d already current."
          % (written, len(ROUTES) - written))
    return 0


def main(argv):
    check = "--check" in argv
    verbose = "-v" in argv or "--verbose" in argv
    return build(check=check, verbose=verbose)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
