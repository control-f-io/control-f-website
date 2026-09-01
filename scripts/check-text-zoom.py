#!/usr/bin/env python3
"""No page may scroll sideways because the reader enlarged the text.

THE FAULT THIS IS NAMED AFTER, and it is the third of its family.

`rem` means two things, and scripts/check-rem-floor.py is the file that says so:
in a DECLARATION it resolves against the root element's actual font size, which
is the reader's text-size setting, and in a MEDIA QUERY it resolves against the
root's INITIAL font size and never against the reader's. So every threshold in
this system is frozen at a 16 px default while everything the threshold admits
goes on scaling underneath it.

.cf-nav is where that bit. The plate is `width: max-content; max-width: 100%` --
it asks for the one line its contents need and is then cut to the band -- and
`@media (max-width: 48.75rem)` folds it at 780 px at every text size there has
ever been. Above the fold the three children are each `flex: 0 1 auto` with
`min-width: auto`, and a nowrap flex row's automatic minimum is the SUM of its
items, so when the cap bit the row could not shrink and the surplus left the
plate to the right. `overflow: visible`, so it went straight on to the
document's scroll width. Measured on patterns/landing-page.html:

    viewport   root 16    root 20    root 22        root 24        root 32
      900       900 -9     900 -11    911 +60       989 +139      1302 +451
     1024      1024 -9    1024 -11   1024 -12       1024  +28     1308 +341
     1280      1280 -9    1280 -11   1280 -12       1280  -13     1323 +113

The first failure is 900 x 22 px, which is nothing exotic: 900 px is the width
just above the fold, and 22 px sits between Chrome's "Large" (20) and "Very
large" (24). At 1280 x 32 -- WCAG 1.4.4's 200 %, at level AA -- the wordmark was
gone from the plate and the EN switch was cut in half by the right edge of the
screen, on all 38 pattern pages at once. Nothing errored, nothing was clipped by
an ancestor, and every one of the 130-odd other checks stayed green: a document
wider than its viewport is not a fact any of them read.

It is the third time. .cf-progress shipped a bare `1fr` and took a page
320 -> 469 px (scripts/check-grid-tracks.py); .cf-team-grid__item shipped a
subgrid with no column axis and was found "by sweeping the pattern pages at a
24 px browser default rather than by anything here", in that script's own words.
Both of those gates read CSS. This one reads the page, because the fault is a
computed width and neither a track list nor a declaration: the nav's three
children are individually blameless and it is their sum against a cap that is
wrong.

WHAT IS MEASURED, AND WHAT IS GATED. Every design-system/patterns/*.html over
the whole 4 x 6 grid -- root 16, 20, 24 and 32 px against 320, 375, 768, 900,
1024 and 1280 -- must satisfy scrollWidth <= clientWidth on the document
element. 16 px is the default; 20 and 24 are Chrome's "Large" and "Very large";
32 is the 200 % WCAG 1.4.4 asks for at level AA. The page is loaded once and the
grid is walked by resizing, so this costs one navigation per page and not
twenty-four.

The GATE is the rectangle the tree passes today: roots 16-24 against widths
375-1280, 570 cells, and it must stay empty. 900 x 24 px is the cell the nav
above fails -- 989 px of document in 900 px of viewport -- so the fix is what
this gate stands on.

Everything outside that rectangle -- 320 px at any text size, and 200 % at any
width -- is CENSUS, measured on every run, printed with the widest offender in
each cell, and RATCHETED: 45 cells when this was written; on 2026-09-01, with
the built tree's 38 pages, 42 in CI's Chromium and 43 under the Chromium 1194
this repository's sessions carry (one cell sits inside font-metric slack); and
41 under that same Chromium once the pie took its container query, so the
ceiling is 41 -- and the number may fall but not rise. Measure on a BUILT
tree: the 25 generated pattern pages are half the census, and an unbuilt
checkout reads 23 and tempts a ceiling CI cannot meet.
A census that can only be read is the thing this repository's README calls a
stale enumeration; a census with a ratchet on it is a gate that has not closed
yet. The 45 were five faults, none of them that change's; they are six now,
because one of the five was two:

  the folded plate    38 cells, one per page, at 320 x 32. It overflows by
                      22 px, and its own note in components.css records the
                      measurement that made that inevitable -- "At 320 the six
                      things in the folded bar measure 279.9 px against 280 px
                      of content box", a tenth of a pixel of slack, taken at a
                      16 px default. Wrapping the list cannot reach it, because
                      below the fold that list is `display: none` and the panel
                      is out of flow; the fix is a relayout of the folded plate.
  act 4's pie label   landing-page.html, 4 cells: +6 px at 320 x 20, +23 at
                      320 x 24, +59 at 320 x 32, +31 at 375 x 32. FIXED on
                      2026-09-01, and only two of those four cells were ever
                      its own. The prescription in this paragraph is what
                      shipped: .cf-pie is a named container now, and the tier
                      that rides the ring asks `@container cf-pie (min-width:
                      21rem)` on top of its trig @supports — 336 px against the
                      328 the component's own arithmetic (7u + 2 x
                      --pie-label-w) reserves at the u floor. Below it the
                      labels are the ruled list the no-trig tier already drew.
                      320 x 20 and 320 x 24 are now clean, and 320/375 x 32
                      turned out to be a SECOND cause the pie's wider box had
                      been masking, entered below. The container also had to be
                      given a measure — see the note over .cf-pie — because
                      inline-size containment took a figure that had been
                      borrowing its caption's max-content to 0 px.
  act 4's line chart  landing-page.html, 2 cells: +57 px at 320 x 32 and +6 at
                      375 x 32, and until the pie above was fixed both were
                      reported as the pie's — the pie's label was simply the
                      wider box in the same cell. Card 04's .cf-line is what
                      carries them: hiding that one figure and nothing else
                      takes the document from 377 to 342 at 320 x 32 (342 is
                      the folded plate above, on every page) and from 381 to
                      375 at 375 x 32. Its own box is 150 px wide with a
                      scrollWidth of 292, and its readings are absolutely
                      positioned and `white-space: nowrap`: "€4,79 Mio." is
                      144 px at a 32 px root and its right edge stands 12 px
                      past the figure. Same shape as the pie's and a different
                      component — a label written for a figure that is now
                      narrower than the label — and the same question to
                      answer: which tier a figure this size should draw.
  a prose table       blog-artikel.html, 2 cells: +6 px at 320 x 20 and +16 at
                      320 x 24.
  expertise.html      1 cell, +18 px at 375 x 32, on a list item.
  suche-leer.html     1 cell, +5 px at 375 x 32, on an outline button.

The ratchet holds the COUNT and not the causes, so a fix for any of them lowers
it and a further cause cannot hide behind them. That second half is not
hypothetical: the line chart above spent two cells of this list filed under the
pie, because a cell names its WIDEST offender and the pie's label was wider.
The count is what caught it -- four cells were claimed and two came off. Lower
CENSUS_CEILING as it falls; when it reaches zero, fold GATE_WIDTHS and
GATE_ROOTS back into WIDTHS and ROOTS and delete this half of the header.

    python3 scripts/check-text-zoom.py
    python3 scripts/check-text-zoom.py --verbose     every cell, passing or not
"""

import argparse
import http.server
import os
import socketserver
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = ROOT / "design-system" / "patterns"

# The whole grid is measured. The gate is the rectangle inside it that the tree
# passes today; every other cell is census, and the census is ratcheted.
WIDTHS = (320, 375, 768, 900, 1024, 1280)
ROOTS = (16, 20, 24, 32)

# 16 is the default; 20 and 24 are Chrome's "Large" and "Very large".
GATE_WIDTHS = (375, 768, 900, 1024, 1280)
GATE_ROOTS = (16, 20, 24)

# What the census holds. It may fall; it may not rise.
CENSUS_CEILING = 41

BROWSER_CANDIDATES = (
    os.environ.get("CF_BROWSER"),
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    "/opt/pw-browsers/chromium/chrome-linux/chrome",
)

MEASURE = """(() => {
  const d = document.documentElement;
  if (d.scrollWidth <= d.clientWidth) return null;
  let worst = null;
  for (const el of document.querySelectorAll('body *')) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const r = el.getBoundingClientRect();
    if (r.width < 1 && r.height < 1) continue;
    const over = Math.round(r.right - d.clientWidth);
    if (over > 1 && (!worst || over > worst.over)) {
      let name = el.tagName.toLowerCase();
      const cls = el.getAttribute('class');
      if (cls) name += '.' + cls.trim().split(/\\s+/)[0];
      worst = {over: over, sel: name};
    }
  }
  return {sw: d.scrollWidth, cw: d.clientWidth, worst: worst};
})()"""


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    required = bool(os.environ.get("CF_REQUIRE_BROWSER"))

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        msg = "text-zoom: SKIPPED — playwright is not installed (pip install playwright)."
        if required:
            print(msg + " CF_REQUIRE_BROWSER is set, so this is a failure.", file=sys.stderr)
            return 1
        print(msg + " The reader's text size is unguarded on this machine; CI still gates it.")
        return 0

    pages = sorted(PATTERNS.glob("*.html"))
    if not pages:
        print("text-zoom: no pages under %s" % PATTERNS, file=sys.stderr)
        return 1

    server = serve()
    port = server.server_address[1]
    findings = []
    census = []
    cells = 0
    try:
        with sync_playwright() as ctx:
            browser = launch(ctx)
            if browser is None:
                msg = "text-zoom: SKIPPED — no Chromium found (playwright install chromium, or CF_BROWSER)."
                if required:
                    print(msg + " CF_REQUIRE_BROWSER is set, so this is a failure.", file=sys.stderr)
                    return 1
                print(msg + " The reader's text size is unguarded on this machine; CI still gates it.")
                return 0

            context = browser.new_context(viewport={"width": 1280, "height": 900})
            page = context.new_page()
            for path in pages:
                rel = path.relative_to(ROOT).as_posix()
                page.goto("http://127.0.0.1:%d/%s" % (port, rel), wait_until="load")
                page.wait_for_timeout(400)
                for size in ROOTS:
                    page.evaluate("document.documentElement.style.fontSize='%dpx'" % size)
                    for width in WIDTHS:
                        page.set_viewport_size({"width": width, "height": 900})
                        page.wait_for_timeout(80)
                        cells += 1
                        found = page.evaluate(MEASURE)
                        if not found:
                            continue
                        row = (rel, size, width, found)
                        gated = size in GATE_ROOTS and width in GATE_WIDTHS
                        (findings if gated else census).append(row)
                        if args.verbose:
                            print("    %-44s root=%-3d w=%-5d %s"
                                  % (path.name, size, width,
                                     "%d>%d" % (found["sw"], found["cw"]) if found else "ok"))
                page.set_viewport_size({"width": 1280, "height": 900})
            browser.close()
    finally:
        server.shutdown()

    def line(row):
        rel, size, width, found = row
        worst = found.get("worst") or {}
        return ("  %-46s root=%-3d w=%-5d  %d > %d   widest: %s +%s px"
                % (rel.split("/")[-1], size, width, found["sw"], found["cw"],
                   worst.get("sel", "?"), worst.get("over", "?")))

    status = 0
    if findings:
        for row in findings:
            print(line(row), file=sys.stderr)
        print("\n%d cell%s where the document is wider than the viewport because the "
              "reader enlarged the text. A page that scrolls sideways is never a taste "
              "call: give the row a way to reflow (flex-wrap on the run, min-width: 0 on "
              "the items, minmax(0, 1fr) on the track) rather than moving the threshold, "
              "which cannot see the reader's font size anyway."
              % (len(findings), "" if len(findings) == 1 else "s"), file=sys.stderr)
        status = 1

    if len(census) > CENSUS_CEILING:
        for row in census:
            print(line(row), file=sys.stderr)
        print("\ncensus (320 px at any text size, and 200 %% at any width): %d cells, and "
              "the ceiling is %d. These corners are open on purpose and are listed in this "
              "file's header — but the count may only ever get smaller. Lower "
              "CENSUS_CEILING when it does; do not raise it to admit a new one."
              % (len(census), CENSUS_CEILING), file=sys.stderr)
        status = 1

    if status == 0:
        print("text-zoom: %d pages over a %d x %d grid — %d cells measured, and the "
              "%d gated ones carry no document wider than its viewport."
              % (len(pages), len(ROOTS), len(WIDTHS), cells,
                 len(pages) * len(GATE_ROOTS) * len(GATE_WIDTHS)))
        print("  census (320 px at any text size, 200 %% at any width): %d of %d cells "
              "still overflow, ceiling %d. Five causes, all named in the header, none of "
              "them the nav row this gate was written for."
              % (len(census), cells - len(pages) * len(GATE_ROOTS) * len(GATE_WIDTHS),
                 CENSUS_CEILING))
    return status


if __name__ == "__main__":
    sys.exit(main())
