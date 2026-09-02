#!/usr/bin/env python3
"""Hold page-local <style> blocks to the same grid-track floor the sheets keep.

scripts/check-grid-tracks.py states the rule and the reason it exists: `1fr` is
`minmax(auto, 1fr)`, and as a MINIMUM `auto` is the item's automatic minimum
size, so a bare fr track distributes free space OR the widest unbreakable thing
inside it, whichever is larger. One long German compound then widens its own
track past its share and pushes the whole page sideways.

That check reads the three stylesheets that ship, and says so:

    # The three stylesheets that ship to control-f.de. docs.css, per-page
    # <style> blocks and prototypes/ are out of scope — the same boundary the
    # breakpoint register and the spacing check both draw.

The boundary is right for that file and it leaves a hole here. A page-local
block is not documentation: patterns/ ARE the compositions, and the landing
page's own note on .cf-pin__inner records this exact class of miss one property
over — "the floor the pages' own copies never had: page-local blocks are
outside check-grid-tracks.py's scope, so the bare 1fr shipped twice
unchallenged. Folding it here is what surfaced it." Folding is what surfaced it
that time. Nothing would surface the next one.

So this is that check for the blocks the other one cannot reach, and it is the
same rule, read by the same code: it imports floored(), block_of(),
guarded_blocks() and the track-property list from check-grid-tracks.py rather
than restating them, because two definitions of one floor is the shape of bug
this whole directory exists to catch.

TWO TIERS, WHICH IS NOT A SOFTENING

  patterns/           fails. These are the page compositions the site is built
                      from; a track list here reaches a reader.
  foundations/        counted and printed, does not fail. They are documentation
  prototypes/         demos and declared not-yet-system respectively — the same
                      boundary tokens.css draws around its register and
                      check-local-thresholds.py draws around PX DEBT. Recording
                      them is the point: a number nobody prints is a number
                      nobody fixes, and the alternative was leaving them
                      invisible. The count is the one this script prints and is
                      deliberately not restated here — it read "seven" while the
                      run said eight, which is the whole argument for printing
                      it in the first place.

AND ONE RULE THAT IS NOT TIERED, because it does not depend on content.

check-grid-tracks.py's third pass — the AUTO-REPEAT FLOOR — is imported and run
here over the same blocks, at every tier, with no debt list. Its header carries
the argument; the short form is that repeat(auto-fill | auto-fit, minmax(<floor>,
1fr)) derives its own column count from <floor>, so <floor> is the grid's minimum
inline size and a bare length there sets the minimum width of the page. Whether
a bare fr overflows is a fact about what the items hold, which is why that rule
has tiers; whether an auto-repeat floor overflows is a fact about the
declaration, so it does not.

THE HOLE THAT ARGUMENT LEFT WAS IN THIS FILE'S OWN DOCSTRING. It used to read:

    Whether a floor is the RIGHT floor. minmax(15rem, 1fr) inside a scroll
    container is a chosen floor and passes, exactly as it does in the sheets.

That is sound for the floor it names — .cf-team-strip__list's grid-auto-columns
sits in a scroll container and decides how wide the strip scrolls. It was also,
verbatim, the declaration foundations/print.html had written into an auto-repeat
in normal flow, where it took the document 320 -> 371 px at a 20 px root; and
foundations/share.html had minmax(19rem, 1fr) beside it, the copy base.css
quotes by its number as the reason .tiles is a class at all. An example chosen
to show why a rule stops somewhere is the last place a counter-example should be
able to hide, and it hid there for as long as the paragraph existed.

WHAT IT STILL DOES NOT CHECK, deliberately

  Whether a non-auto floor is the RIGHT floor. A chosen minimum on a track in a
  scroll container, or on grid-auto-columns, is a decision about that element
  and cannot reach the page. The rule there is that a floor was chosen, not that
  it is zero.

  docs.css and assets/css/. Out of scope by the boundary at the head of every
  register in this system — assets/css/ because check-grid-tracks.py reads it.

stdlib only, no build step, no dependency. Same python3 that serves the pages.
"""

import argparse
import html.parser
import importlib.util
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system" / "assets" / "css"
PAGES = ROOT / "design-system"

# The tier that fails. Everything else under design-system/ is counted.
STRICT = ("patterns",)


def _sibling(name):
    """Import a hyphenated sibling check by path. One definition of `floored`."""
    spec = importlib.util.spec_from_file_location(
        name.replace("-", "_"), ROOT / "scripts" / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gt = _sibling("check-grid-tracks")


class StyleBlocks(html.parser.HTMLParser):
    """Every <style> block in a page, with the line its content starts on."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []
        self._start = None

    def handle_starttag(self, tag, attrs):
        if tag == "style":
            self._start = self.getpos()[0]

    def handle_data(self, data):
        if self._start is not None:
            self.blocks.append((self._start, data))
            self._start = None

    def handle_endtag(self, tag):
        if tag == "style":
            self._start = None


def style_blocks(path):
    p = StyleBlocks()
    p.feed(path.read_text())
    p.close()
    return p.blocks


def pages():
    for f in sorted(PAGES.rglob("*.html")):
        yield f


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every page-local track list, not only the failures")
    args = ap.parse_args()

    # A page-local track list may be guarded by min-width: 0 written in a
    # shipping sheet — .subdivide is exactly that case — or by one written in
    # the page's own block. Both count, and the component is the unit, the same
    # way check-grid-tracks.py credits it.
    sheets = [(n, (CSS / n).read_text()) for n in gt.SHIPPING]
    local = [(str(f), css) for f in pages() for _, css in style_blocks(f)]
    guarded = gt.guarded_blocks(sheets) | gt.guarded_blocks(local)

    rows = []
    failures = []
    debt = []
    autos = []
    for f in pages():
        tier = f.relative_to(PAGES).parts[0]
        for offset, css in style_blocks(f):
            for line, sel, body in gt.blocks(css):
                for prop, value in gt.declarations(body):
                    if not gt.TRACK_PROP.fullmatch(prop):
                        continue
                    where = "%s:%d" % (f.relative_to(ROOT), offset + line - 1)
                    for floor in gt.auto_repeat_floors(value):
                        folds = gt.auto_floor_folds(floor)
                        autos.append((where, sel, floor, folds))
                        if not folds:
                            # Not tiered. See the docstring: this one is a fact
                            # about the declaration, not about the content.
                            failures.append(
                                gt.auto_floor_finding(where, sel, prop, value, floor))
                    if not gt.FR.search(value):
                        continue
                    block = gt.block_of(sel)
                    ok = gt.floored(value) or block in guarded
                    rows.append((where, sel, prop, value, ok))
                    if ok:
                        continue
                    note = (
                        "%s  %s\n"
                        "      %s: %s\n"
                        "      A bare fr floors at min-content, so the widest unbreakable word in\n"
                        "      this grid sets the track's width and can push the page sideways.\n"
                        "      Give the track a floor — minmax(0, %s) — or give %s's items\n"
                        "      min-width: 0."
                        % (where, sel, prop, value,
                           gt.FR.search(value).group(0), block or "the grid"))
                    if tier in STRICT:
                        failures.append(note)
                    else:
                        debt.append("%s  %s { %s: %s }" % (where, sel, prop, value))

    if args.verbose:
        print("track lists carrying fr, as read out of page-local <style>:\n")
        for where, sel, prop, value, ok in rows:
            print("  %-52s %-30s %s" % (where, sel[:30], "floored" if ok else "UNFLOORED"))
        print()
        print("auto-repeat floors, as read out of page-local <style>:\n")
        for where, sel, floor, folds in autos:
            print("  %-52s %-24s %-24s %s"
                  % (where, sel[:24], floor[:24], "folds" if folds else "HARD FLOOR"))
        print()

    if debt:
        # One line each, not a finding each: outside patterns/ these are
        # recorded rather than raised, and a wall of text reads as a failure.
        print("page-local track debt, counted not failed — %d unfloored track "
              "list(s) outside %s/:" % (len(debt), "/".join(STRICT)))
        for d in debt:
            print("  " + d)
        print()

    if failures:
        print("page-local grid tracks: %d finding(s)\n" % len(failures))
        for f in failures:
            print("  " + f + "\n")
        return 1

    print("page-local grid tracks: %d track list(s) read, %d floored, "
          "0 unfloored under %s/ (%d counted elsewhere);\n"
          "                        %d auto-repeat floor(s), all folding."
          % (len(rows), sum(1 for r in rows if r[4]), "/".join(STRICT), len(debt),
             len(autos)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
