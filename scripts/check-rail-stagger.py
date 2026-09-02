#!/usr/bin/env python3
"""The chapter rail's stagger index is 0 … n-1 with no hole in it.

Every row of an .act-rail carries `style="--i:<k>"`, and acts.css spends that
value on exactly one thing:

    .act-rail__label { transition-delay: calc(var(--i) * 40ms); }

-- the stagger that runs the labels open when the rail is hovered or focused.
So `--i` is not a label, an id or a hint: it is the row's place in a cadence,
and a cadence has no content except its interval.

WHAT WENT WRONG. patterns/expertise.html parked its second chapter -- the world
map -- inside an HTML comment, and renumbered the four rows below it so the
list still read 01 … 05. Their `--i` was deliberately left alone, on the
argument written into that commit that the value "is a 40 ms transition delay
and nothing else". It is, and that is the whole problem: the rail kept 0, 2, 3,
4, 5, so the five labels opened at 0, 80, 120, 160 and 200 ms. One 80 ms step
where the other four are 40 -- the first label lands and the rail waits a whole
extra beat before the rest of it follows. Landing page and Über uns measure 0,
40, 80, 120 and 0, 40, 80, because neither has ever had a row taken out of the
middle.

A SCREENSHOT CANNOT SHOW IT. Both the held state and the open state are
correct; only the 200 ms between them is wrong, and no still frame contains an
interval. Nothing overflows, nothing is missing from the DOM, no console
message, and every other gate stayed green for the week it shipped
(2026-08-26 to 2026-09-02).

WHAT IS CHECKED, on every page that carries a rail:

  THE INDICES  the `--i` values on .act-rail__item, in document order, are
               exactly 0, 1, … n-1. A hole doubles one interval; a repeat puts
               two rows on one beat; a value out of order runs the cadence
               backwards past a row.

  THE NUMERALS the .act-rail__num marks read 01 … 0n in the same order. That is
               the other half a removal has to renumber, and it is the half that
               IS visible -- which is exactly why it got done and the indices
               did not.

  THE PREMISE  acts.css still declares .act-rail__label's transition-delay as a
               multiple of var(--i). If that mechanism is ever replaced, this
               script is holding a rule that no longer exists and says so rather
               than passing.

The pages are found rather than listed: any file under design-system/ carrying
a live .act-rail__item is in scope, so a fifth page adopting the rail is checked
by existing. Markup inside HTML comments and inside <template> is stripped
first -- the map is parked in both of those forms on Expertise, and neither
renders, so neither is a row of the cadence.

patterns/en/ is out of scope for the reason every other check leaves it out:
build-i18n.py copies markup, classes and inline styles through byte for byte
and replaces only words, so the fact is already kept one directory up.
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
ACTS_CSS = DS / "assets/css/acts.css"

ITEM = re.compile(r'<li\b[^>]*\bclass="[^"]*\bact-rail__item\b[^"]*"[^>]*>', re.S)
INDEX = re.compile(r'--i\s*:\s*(-?\d+)')
NUM = re.compile(r'class="[^"]*\bact-rail__num\b[^"]*"[^>]*>\s*([^<]*?)\s*<', re.S)
# `transition-delay: calc(var(--i) * 40ms)` -- the shape, not the number, so a
# retime of the stagger is not a failure and a change of mechanism is.
DELAY = re.compile(
    r'\.act-rail__label\s*\{(?P<body>[^}]*)\}', re.S)
MULTIPLE = re.compile(
    r'transition-delay\s*:\s*calc\(\s*var\(\s*--i\s*\)\s*\*\s*([\d.]+m?s)\s*\)')


def fail(msg):
    print(f"FAIL  {msg}")
    return 1


def render(html):
    """The markup a browser would build a rail out of.

    HTML comments and <template> contents both keep their bytes and draw
    nothing, and the map is parked in one of each. A row that does not render
    is not a beat of the stagger.
    """
    html = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    return re.sub(r"<template\b.*?</template>", "", html, flags=re.S | re.I)


def pages():
    """Every page under design-system/ with a rail on it, patterns/en/ aside."""
    found = []
    for path in sorted(DS.rglob("*.html")):
        if "/en/" in path.as_posix():
            continue
        text = path.read_text(encoding="utf-8")
        if "act-rail__item" not in text:
            continue
        body = render(text)
        if ITEM.search(body):
            found.append((path, body))
    return found


def check_page(path, body):
    name = path.relative_to(ROOT).as_posix()
    bad = 0

    indices = []
    for tag in ITEM.findall(body):
        m = INDEX.search(tag)
        if not m:
            bad |= fail(f"{name}: an .act-rail__item declares no --i, so its label "
                        f"opens on the inherited value — every row it shares that "
                        f"value with arrives on the same beat")
            indices.append(None)
        else:
            indices.append(int(m.group(1)))

    n = len(indices)
    want = list(range(n))
    if None not in indices and indices != want:
        bad |= fail(f"{name}: the rail's --i reads {indices} over {n} rows and has "
                    f"to read {want}. `--i` is the row's place in "
                    f"transition-delay: calc(var(--i) * step) — a hole doubles one "
                    f"interval of the label stagger, a repeat puts two rows on one "
                    f"beat, and neither is visible in a still frame")

    nums = [t for t in NUM.findall(body)]
    if len(nums) != n:
        bad |= fail(f"{name}: {n} rail rows and {len(nums)} .act-rail__num marks — "
                    f"every row says which chapter it is")
    else:
        want_nums = ["%02d" % (k + 1) for k in range(n)]
        if nums != want_nums:
            bad |= fail(f"{name}: the rail's numerals read {nums} and have to read "
                        f"{want_nums} — the visible half of the same list")
    return bad, n


def check_stylesheet():
    """The premise: --i is still what delays a label."""
    css = ACTS_CSS.read_text(encoding="utf-8")
    bodies = [m.group("body") for m in DELAY.finditer(css)]
    steps = [s for body in bodies for s in MULTIPLE.findall(body)]
    if not bodies:
        return fail("acts.css declares no .act-rail__label rule, so this script is "
                    "holding an invariant about a component that is gone"), None
    if not steps:
        return fail("acts.css no longer delays .act-rail__label by a multiple of "
                    "var(--i). That expression is the only thing --i is spent on; "
                    "without it the indices this script orders are ordering "
                    "nothing, and the rule has to be rewritten rather than kept"), None
    if len(set(steps)) > 1:
        return fail(f"acts.css gives .act-rail__label {len(set(steps))} different "
                    f"stagger steps ({', '.join(sorted(set(steps)))}) — the cadence "
                    f"is one interval or it is not a cadence"), None
    return 0, steps[0]


def main():
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()
    bad, step = check_stylesheet()
    found = pages()
    if not found:
        return fail("no page under design-system/ carries an .act-rail__item, so "
                    "the rail this script is written for is not in the tree")
    rows = 0
    for path, body in found:
        b, n = check_page(path, body)
        bad |= b
        rows += n
    if bad:
        return 1
    print(f"OK  {rows} chapter-rail rows on {len(found)} page(s); every --i is "
          f"0 … n-1 in document order and every numeral counts with it, so each "
          f"rail's labels open on one even {step} interval")
    return 0


if __name__ == "__main__":
    sys.exit(main())
