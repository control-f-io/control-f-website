#!/usr/bin/env python3
"""One solution of a grid per component. Everything else on it takes that one.

Three rules in this system draw content on the twelve-column grid, and only one
of them is the grid. .grid is the primitive; .cf-values__frame and
.cf-values__item are the pinned values composition reaching for the page's
column set INSIDE a component, because they are set in an @supports block
against markup that carries no utility class. foundations/layout.html records
that, and records the fix it got: the track list was written out three times
and is a token now, so all three read --grid-tracks and cannot disagree about
the RECIPE.

THAT IS NOT THE SAME GUARANTEE AS LANDING ON THE SAME LINES, and the gap
between the two is where this script lives. A track set is a recipe plus a
gutter. --grid-tracks carries the recipe. The gutter is a separate declaration
in each rule — `gap: var(--grid-gap)`, written twice — and two rules that must
keep resolving two declarations to the same pair of numbers forever, for a
title's right edge to meet a mark's left one, are two rules that will one day
not. Give the frame a gutter of its own and the three bands of the 4 + 4 + 4
come apart with both rules still reading the token they were told to read.

subgrid is the form that cannot come apart: the child adopts the parent's
resolved lines, gutter included, so the grid is solved once and everything
inside it takes that solution. base.css has said so at .subdivide__row since
the blog grid was built — "a track set written in more than one place is a
track set two rules can disagree about" is the system's own sentence — and
.cf-values was the one component left that restated instead.

WHAT THIS KNOWS THAT A SCREENSHOT CANNOT. Nothing was wrong on the day it was
written and nothing is wrong now: measured at 1024, 1280, 1440 and 1920, the
restated grid and the frame's own grid agree on every vertical to within
0.02 px. A restatement is not a defect you can see. It is a defect you can only
see the day somebody changes one of the two halves, at which point the
screenshot that would have caught it is a screenshot of a page that shipped.

THE RULE, derived rather than listed:

  TRACK SET   a custom property is a track set if some rule in the shipping CSS
              states it as the WHOLE of a grid-template-columns value. That is
              --act-cols, --grid-tracks and --subdivide-cols today, and not
              --gantt-key, which is one track inside a two-track list. A fourth
              earns its place by being written that way.
  ONE SOLVER  per component block, at most ONE rule may state a given track set
              without also taking it through subgrid. A second one is two
              solutions of the same arithmetic, and the second is the nested
              one — that is what a component's second grid on its own columns
              is for. Pair it: a `grid-template-columns: subgrid` beside the
              fallback, which is base.css's idiom at .subdivide__row, or the
              selector restated inside @supports (grid-template-columns:
              subgrid), which is .cf-team-grid__item's and the one to reach for
              when more than one declaration moves.

WHY THE BLOCK, AND WHY RULES RATHER THAN SELECTORS. Two grids are only at risk
of disagreeing if one is inside the other, and a stylesheet cannot see nesting.
The block is the closest thing the naming gives: .cf-values__frame and
.cf-values__item are two grids of one component and one of them contains the
other, while .grid and .cf-values__frame are two components and no relation.
Counting RULES rather than selectors is the other half — .act-rail__link and
.act-rail__jump are two siblings that must put their glyphs on one axis, and
acts.css does that the way this script would ask for, in ONE rule reading one
variable, which is a shared declaration rather than two numbers that agree.
A modifier is folded onto what it modifies, so .grid and .grid--early are the
same solver stated twice for two container widths, not two solvers.

THE OTHER DIRECTION IS DELIBERATELY NOT CHECKED. A subgrid may keep a gutter of
its own: .cf-team-grid__item states row-gap: 0 on its subgrid axis on purpose,
because the three interior gaps of that card are not equal and a single row-gap
cannot express them. Whether a subgrid should inherit its parent's gutter has
more than one right answer, so it is a drawing decision, not a disappearance.
This script owns the direction where one grid gets solved twice.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-track-restatement.py       # check, exit 1 on a finding
    python3 scripts/check-track-restatement.py -v    # list every track set and solver
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system" / "assets" / "css"

# The four stylesheets that ship to control-f.de — the same boundary the
# breakpoint register, the spacing scale and the grid-track check all draw.
# docs.css, per-page <style> blocks and prototypes/ are out for the same reason
# they are out there.
SHIPPING = ("tokens.css", "base.css", "components.css", "acts.css")

COLUMNS = re.compile(r"(?<![\w-])grid-template-columns\s*:\s*([^;]+)")
WHOLE_VAR = re.compile(r"^var\(\s*(--[\w-]+)\s*\)$")
# The class a compound selector is about: the last one in it, which is the
# element the rule draws. `.cf-blog-col.subdivide__col` is a .subdivide__col.
CLASS = re.compile(r"\.([\w-]+)")


def blocks(text):
    """Every rule as (line, selector, body), comments stripped in place.

    Comments go first and keep their newlines, so line numbers survive and a
    track list quoted inside one — this file's own header is full of them, and
    so is base.css — is never read as a declaration.

    Nesting is not parsed and does not need to be: a rule inside @media,
    @supports or @container still arrives here with its own selector, because
    the at-rule prelude is what precedes the OUTER brace. A prelude carries no
    declarations, so it contributes a body with no colon and falls out.
    """
    text = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    for m in re.finditer(r"([^{}]*)\{([^{}]*)\}", text):
        sel, body = m.group(1), m.group(2)
        if ":" not in body:
            continue
        yield text.count("\n", 0, m.start(2)) + 1, " ".join(sel.split()), body


def solver_keys(selector):
    """The elements a rule draws, and the blocks they belong to.

    One key per selector in the list, modifiers folded onto what they modify:
    `.grid--early` is `.grid`, `.subdivide--even .subdivide__col` is
    `.subdivide__col`. Returns {block: frozenset(keys)}.
    """
    out = {}
    for one in selector.split(","):
        names = CLASS.findall(one)
        if not names:
            continue
        key = names[-1].split("--")[0]
        if not key:
            continue
        out.setdefault(key.split("__")[0], set()).add(key)
    return {b: frozenset(k) for b, k in out.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    rules = []
    for name in SHIPPING:
        path = CSS / name
        if not path.exists():
            print(f"track restatement: missing {name}", file=sys.stderr)
            return 1
        for line, sel, body in blocks(path.read_text()):
            rules.append((name, line, sel, body))

    # TRACK SET — a custom property stated as the whole of a column track list.
    track_sets = set()
    for _, _, _, body in rules:
        for value in COLUMNS.findall(body):
            m = WHOLE_VAR.match(" ".join(value.split()))
            if m:
                track_sets.add(m.group(1))

    # Every rule that states a track set, and whether it also takes it through
    # subgrid. Keyed by (block, track set, the elements the rule draws), so a
    # modifier and the rule it modifies are one solver and a selector list is
    # one solver, per WHY THE BLOCK above.
    solvers = {}
    for name, line, sel, body in rules:
        values = [" ".join(v.split()) for v in COLUMNS.findall(body)]
        stated = {WHOLE_VAR.match(v).group(1) for v in values if WHOLE_VAR.match(v)}
        stated &= track_sets
        if not stated:
            continue
        paired = "subgrid" in values
        for block, keys in solver_keys(sel).items():
            for var in stated:
                entry = solvers.setdefault((block, var, keys), {"paired": False, "at": []})
                entry["paired"] |= paired
                entry["at"].append(f"{name}:{line}  {sel}")

    # A selector may take the subgrid form in a rule of its own — the
    # @supports idiom — so a solver counts as paired if ANY rule drawing the
    # same elements carries it.
    subgridded = {
        (block, keys)
        for _, _, sel, body in rules
        if any(" ".join(v.split()) == "subgrid" for v in COLUMNS.findall(body))
        for block, keys in solver_keys(sel).items()
    }
    for (block, _, keys), entry in solvers.items():
        entry["paired"] |= (block, keys) in subgridded

    per_block = {}
    for (block, var, keys), entry in solvers.items():
        per_block.setdefault((block, var), []).append((keys, entry))

    findings = []
    for (block, var), members in sorted(per_block.items()):
        loose = [(k, e) for k, e in members if not e["paired"]]
        if len(loose) < 2:
            continue
        where = "\n".join(f"      {at}" for _, e in loose for at in e["at"])
        findings.append(
            f"  - {block} solves {var} in {len(loose)} rules and takes it through\n"
            f"    subgrid in none of them. One of these is inside another, and the two\n"
            f"    agree only for as long as every gutter and every track declaration in\n"
            f"    both keeps resolving the same. Pair the nested one with\n"
            f"    grid-template-columns: subgrid.\n{where}"
        )

    if args.verbose:
        print(f"track sets: {', '.join(sorted(track_sets)) or 'none'}")
        for (block, var), members in sorted(per_block.items()):
            for keys, entry in sorted(members, key=lambda m: sorted(m[0])):
                state = "subgrid" if entry["paired"] else "solves"
                print(f"  {block:<16} {var:<18} {state:<8} {', '.join(sorted(keys))}")

    if findings:
        print(f"track restatement: {len(findings)} finding(s)\n")
        print("\n\n".join(findings))
        return 1

    print(
        f"track restatement: {len(track_sets)} track set(s) across "
        f"{len(per_block)} block(s), one solver each."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
