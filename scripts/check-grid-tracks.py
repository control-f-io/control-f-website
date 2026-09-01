#!/usr/bin/env python3
"""Enforce the intrinsic minimum on every grid track that can be squeezed.

`1fr` is `minmax(auto, 1fr)`, and as a MINIMUM `auto` is the item's automatic
minimum size — which for anything holding text is its min-content width. So a
bare `fr` track does not distribute free space; it distributes free space OR
the widest unbreakable thing inside it, whichever is larger. One long German
compound then widens its own track past its share and pushes the whole page
sideways, at a width nobody tested, with no error anywhere.

The system already knew this. base.css says it on .tiles ("min-width: 0 on the
items is load-bearing, not hygiene") and again on .subdivide ("a bare 1fr floors
at min-content, which is how a single long headline pushes an entire page
sideways"). Both are prose. Nothing ran either, and .cf-progress shipped
`grid-template-columns: 1fr auto` — the one fr track list of thirty-three with
no minimum of any kind, where twenty-eight were floored on the track and four
guarded by min-width: 0 on their items. Measured with a 61-character compound
in its label, the document went 320 -> 469 px at a 320 px viewport.

That is the fifth time a claim in this system was written down, kept by nearly
everything, and broken by exactly one declaration. Hence a script.

THERE ARE TWO CORRECT FIXES AND THIS CHECKS FOR BOTH, because the system uses
both and neither is wrong:

  on the track   minmax(0, 1fr) — the floor is zero, so the track is pure
                 proportion. What .grid, .cf-process, .cf-article and twenty
                 others do.
  on the item    min-width: 0 on the grid items, which sets the automatic
                 minimum size to zero and leaves `auto` nothing to floor at.
                 What .subdivide does, and it has to: its geometric track sets
                 are `4fr 2fr 2fr`, exact halves whose whole point is the ratio,
                 and minmax(0, 4fr) would say the same thing four times.

A track list may also carry a DELIBERATE non-zero floor — .tiles' min(--tile,
100%), .cf-team-strip__list's 15rem inside a scroll container. Those are floors,
so they pass: the rule is that a floor was chosen, not that it is zero.

AND THERE IS A SECOND AXIS TO THIS, which the rule above cannot reach because it
reads track LISTS. A rule that declares `display: grid` and no columns at all
still has a column: an IMPLICIT one, sized `auto`, and `auto` as a minimum is
the same min-content floor a bare `fr` carries. The defect is identical and the
script had nothing to read, so it was invisible — found in the end by sweeping
the pattern pages at a 24 px browser default rather than by anything here.

The system has fourteen grids that leave their column axis implicit and only one
of them could overflow, so this is a CENSUS with one GATE inside it rather than
a rule over all fourteen:

  the gate     a grid whose ROWS are `subgrid` must declare its columns, or
               guard its items. Both halves are load-bearing. A grid whose own
               width is free absorbs a wide track by growing; a subgrid stands
               in a cell whose width its parent has already decided, so the
               track grows straight THROUGH it. That makes overflow certain
               rather than possible, which is what makes it checkable.
               .cf-team-grid__item is the subject: it shipped `display: grid`
               with `grid-template-rows: subgrid` and no column, and took
               patterns/ueber-uns.html 320 -> 359 px wide at a 320 px viewport
               with the browser's default font at 24 px.
  the census   the other thirteen are printed with their guard status and
               counted in the summary, and nothing fails on them. Whether an
               implicit column CAN be squeezed depends on what its children
               hold — an SVG at grid-area 1/1 cannot produce a min-content
               wider than its cell and a paragraph of German can — and that is
               a fact about content, which no amount of reading the stylesheet
               will settle. Naming a roster of thirteen exemptions would be
               asserting thirteen judgements this script cannot make. Counting
               them is the honest half, and the count cannot grow quietly.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-grid-tracks.py       # check, exit 1 on a finding
    python3 scripts/check-grid-tracks.py -v    # list every track list, not only failures
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system" / "assets" / "css"

# The three stylesheets that ship to control-f.de. docs.css, per-page <style>
# blocks and prototypes/ are out of scope — the same boundary the breakpoint
# register and the spacing check both draw, and for the same reason.
SHIPPING = ("tokens.css", "base.css", "components.css")

# Properties that take a track list. The custom properties are here because in
# this system a track list is as likely to be declared into one as written
# inline: --grid-tracks feeds .grid and both .cf-values rules, --subdivide-cols
# feeds .subdivide and every .subdivide__row. A check that only read the real
# properties would miss the place the track set is actually decided.
TRACK_PROP = re.compile(
    r"grid-template-columns|grid-template-rows|grid-auto-columns|grid-auto-rows"
    r"|--grid-tracks|--subdivide-cols|--subdivide-even"
)

FR = re.compile(r"(?<![\w.-])\d*\.?\d+fr(?![\w-])")
MIN_ZERO = re.compile(r"min-(?:width|inline-size)\s*:\s*0(?:px|rem|%)?\s*$")

# The implicit-column pass. `display: grid` with no column track list anywhere in
# the rule leaves the inline axis to one implicit `auto` track.
GRID_DISPLAY = re.compile(r"(?:inline-)?grid")
# Anything that states the inline axis. grid-template and grid are the shorthands
# (`rows / columns`), so either one present means the author said something about
# columns; grid-auto-columns sizes the implicit ones, which is a floor by another
# name — .cf-team-strip__list's minmax(15rem, 1fr) is exactly that.
COLUMN_PROP = re.compile(r"grid-template-columns|grid-template|grid-auto-columns|grid")


def blocks(text):
    """Every rule in a stylesheet as (line, selector, body), comments stripped.

    Comments go first and in place, so line numbers survive and so a track list
    quoted inside a comment — this file's own docstring is full of them, and so
    is base.css — is never read as a declaration.

    Nesting is not parsed. It does not need to be: a rule inside @media,
    @supports or @container still ends up here with its own selector, because
    the at-rule prelude is what precedes the OUTER brace and every inner rule
    has its own. An at-rule prelude carries no declarations, so it contributes a
    body with no colon in it and falls out on its own.
    """
    text = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    for m in re.finditer(r"([^{}]*)\{([^{}]*)\}", text):
        raw = m.group(1)
        sel = " ".join(raw.split())
        if not sel or sel.startswith("@"):
            continue
        # Count to where the SELECTOR starts, not to where the gap before it
        # does. group(1) begins at the previous rule's closing brace, so for the
        # first rule in a file it begins at byte 0 and every blanked comment
        # above it would otherwise be charged to the selector's line.
        head = m.start(1) + len(raw) - len(raw.lstrip())
        yield text[:head].count("\n") + 1, sel, m.group(2)


def declarations(body):
    for decl in body.split(";"):
        prop, sep, value = decl.partition(":")
        if sep:
            yield prop.strip(), value.strip()


def floored(value):
    """Is every fr in this track list inside the max slot of a minmax()?

    Scanned rather than parsed, because minmax() cannot nest inside minmax() and
    repeat() only ever wraps whole tracks — so an fr is floored exactly when the
    nearest unclosed function opening to its left is a minmax(. That holds for
    repeat(auto-fill, minmax(min(...), 1fr)) as well, which a naive
    "value contains minmax" test would pass for the wrong reason and a
    "value starts with minmax" test would fail outright.
    """
    for hit in FR.finditer(value):
        stack = []
        for m in re.finditer(r"([a-z-]*)\(|\)", value[: hit.start()]):
            if m.group(0) == ")":
                if stack:
                    stack.pop()
            else:
                stack.append(m.group(1))
        if not stack or stack[-1] != "minmax":
            return False
    return True


def block_of(selector):
    """The component a selector belongs to: its first class, less any __element
    or --modifier. `.subdivide--3` and `.subdivide__col` are both `.subdivide`,
    which is what lets an item guard on one be credited to a track list on the
    other."""
    m = re.search(r"\.([A-Za-z][\w-]*)", selector)
    if not m:
        return None
    return "." + re.split(r"__|--", m.group(1))[0]


def guarded_blocks(sheets):
    """Every component that declares min-width: 0 somewhere — on itself or on a
    descendant. That is the item-side fix, and it is credited to the whole
    component rather than to one selector because the guard and the track list
    are never on the same rule: .subdivide carries the tracks and
    .subdivide__col carries the guard."""
    found = set()
    for name, text in sheets:
        for _, sel, body in blocks(text):
            for prop, value in declarations(body):
                if MIN_ZERO.fullmatch("%s: %s" % (prop, value)):
                    b = block_of(sel)
                    if b:
                        found.add(b)
    return found


def implicit_column_grids(sheets):
    """Every rule that makes an element a grid and says nothing about its columns.

    Returns (sheet, line, selector, block, subgrid_rows). `subgrid_rows` is the
    gate: a card whose row axis comes from its parent stands in a cell it cannot
    widen, so a min-content floor on its implicit column overflows the page
    rather than the element. Everything else here is the census.
    """
    out = []
    for name, text in sheets:
        for line, sel, body in blocks(text):
            decls = list(declarations(body))
            if not any(p == "display" and GRID_DISPLAY.fullmatch(v) for p, v in decls):
                continue
            if any(COLUMN_PROP.fullmatch(p) for p, _ in decls):
                continue
            subgrid_rows = any(
                p == "grid-template-rows" and v.strip() == "subgrid" for p, v in decls
            )
            out.append((name, line, sel, block_of(sel), subgrid_rows))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every track list, not only the failures")
    args = ap.parse_args()

    sheets = [(n, (CSS / n).read_text()) for n in SHIPPING]
    guarded = guarded_blocks(sheets)

    rows = []
    failures = []
    for name, text in sheets:
        for line, sel, body in blocks(text):
            for prop, value in declarations(body):
                if not TRACK_PROP.fullmatch(prop) or not FR.search(value):
                    continue
                block = block_of(sel)
                ok_track = floored(value)
                ok_item = block in guarded
                rows.append((name, line, sel, prop, value, ok_track, ok_item))
                if ok_track or ok_item:
                    continue
                failures.append(
                    "%s:%d  %s\n"
                    "      %s: %s\n"
                    "      A bare fr floors at min-content, so the widest unbreakable word in\n"
                    "      this grid sets the track's width and can push the page sideways.\n"
                    "      Give the track a floor — minmax(0, %s) — or give %s's items\n"
                    "      min-width: 0, which is what .subdivide does with its geometric sets."
                    % (name, line, sel, prop, value,
                       FR.search(value).group(0), block or "the grid")
                )

    implicit = implicit_column_grids(sheets)
    for name, line, sel, block, subgrid_rows in implicit:
        if not subgrid_rows or block in guarded:
            continue
        failures.append(
            "%s:%d  %s\n"
            "      display: grid with grid-template-rows: subgrid and no column.\n"
            "      The implicit column is `auto`, and `auto` as a minimum is min-content —\n"
            "      the same floor a bare fr carries. This card cannot grow to absorb it:\n"
            "      its row axis is its parent's, so the track grows through the cell and\n"
            "      pushes the page sideways. Declare grid-template-columns: minmax(0, 1fr),\n"
            "      or give %s's items min-width: 0."
            % (name, line, sel, block or "the grid")
        )

    if args.verbose:
        print("grids leaving their column axis implicit:\n")
        for name, line, sel, block, subgrid_rows in implicit:
            print("  %-16s %-5d %-34s %s"
                  % (name, line, sel[:34],
                     "GATED (rows are subgrid)" if subgrid_rows
                     else ("min-width: 0 on items" if block in guarded else "census only")))
        print()
        print("track lists carrying fr, as read out of the shipping CSS:\n")
        for name, line, sel, prop, value, ok_track, ok_item in rows:
            print("  %-16s %-5d %-34s %s"
                  % (name, line, sel[:34],
                     "floored" if ok_track else ("min-width: 0 on items" if ok_item else "UNFLOORED")))
        print("\ncomponents declaring min-width: 0: %s\n" % ", ".join(sorted(guarded)))

    if failures:
        print("grid tracks: %d finding(s)\n" % len(failures))
        for f in failures:
            print("  - %s\n" % f)
        return 1

    print("grid tracks: %d fr track lists, %d floored, %d guarded on the item;\n"
          "             %d implicit columns, %d of them guarded on the item."
          % (len(rows),
             sum(1 for r in rows if r[5]),
             sum(1 for r in rows if not r[5] and r[6]),
             len(implicit),
             sum(1 for i in implicit if i[3] in guarded)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
