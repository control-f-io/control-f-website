#!/usr/bin/env python3
"""The numeral is lit exactly while the card it names is on the stage.

.cf-pin is three rows: an index that names the card, the card, a bar that runs
under it. The index is four mono numerals and the lit one is the whole of what
it says -- 01 02 03 04 with 02 in --text-primary means "you are looking at the
second of four". It is the only element on the stage that says which.

WHAT WENT WRONG. The mark and the card were timed by two different pairs of
numbers, and nothing made them agree:

    .cf-pin__step  contain 25i - 3 .. 25(i+1) + 3   cf-pin-step  11 %, 89 %
    .cf-pin__mark  contain 25i     .. 25(i+1)       cf-pin-mark  14 %, 86 %

which resolves to a card fully opaque over contain 25i + 0.41 .. 25i + 24.59
and a numeral at --text-primary over 25i + 3.50 .. 25i + 21.50. The numeral
arrived 3.09 points after the card it names and left 3.09 points before it, so
between one mark going dark and the next lighting there was a SEVEN-POINT band
with nothing at --text-primary at all -- centred exactly on the quarter
boundary, where all four numerals read --text-muted to the integer while a card
stood fully opaque behind them.

Swept in Chromium at 20 px, counting a mark as lit within a quarter of the
primary-to-muted range: 17.7 % of the landing page's pinned run and 18.1 % of
the expertise page's had no numeral lit -- 1020 px and 1040 px at 1440 x 900,
in four bands. The worst of the four is not a handover at all: it is the stage
pinning. The reader arrives, the page stops, card 01 is complete, and the index
over it names nothing for 160 px.

Nothing caught it because nothing was comparing the two. Every check on this
stage holds one animation to its own written intent -- check-pin-handover.py the
cards, check-quarter-opening.py the build's head, check-relay-rate.py the frame
-- and this is a relation BETWEEN two of them. A screenshot cannot show it
either: a muted numeral is exactly what a numeral that is not this card's is
supposed to look like, so an index naming nothing photographs as an index.

WHAT IS CHECKED. Both bands are resolved out of components.css -- the range off
the rule, the plateau off the keyframes -- and compared, for every quarter and
for the two `-last` variants that carry the final one. They must be the same
interval. That is stronger than "the mark is lit somewhere in its quarter" and
it is the sentence the stage actually rests on: if the numeral is lit over
exactly the interval its card is opaque, then at every scroll position of the
run the index names what is on the stage, and the two cross over together.

WHAT THIS DOES NOT CLAIM. Not the 11 % and 89 % themselves -- how quickly a card
arrives is a decision, and moving it moves the numeral with it, which is the
point. Not the +/-3 % overlap. Not that some numeral is lit at every position:
at the crossover both are half-way between the two inks for 0.82 of a point,
which is the cards' own crossfade and is a handover rather than a gap.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-pin-name.py
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPONENTS = ROOT / "design-system/assets/css/components.css"
# The landing page gave its pinned stage to prototypes/statement-to-process.html
# on 2026-07-28; the register follows the stages, not the folder.
PAGES = [ROOT / "design-system/prototypes/statement-to-process.html",
         ROOT / "design-system/patterns/expertise.html"]

# how close two resolved bands have to be, in points of `contain`. They are
# computed from literals, so anything but 0 is a disagreement; the epsilon is
# for float arithmetic only.
EPS = 1e-6


def fail(msg):
    print(f"FAIL  {msg}")
    return 1


def rule_body(css, selector):
    m = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", css)
    return m.group(1) if m else None


RANGE = re.compile(
    r"animation-range:\s*"
    r"contain\s+calc\(\s*var\(--i\)\s*\*\s*([\d.]+)%\s*(?:([-+])\s*([\d.]+)%\s*)?\)\s+"
    r"contain\s+calc\(\s*\(\s*var\(--i\)\s*\+\s*1\s*\)\s*\*\s*([\d.]+)%\s*(?:([-+])\s*([\d.]+)%\s*)?\)\s*;"
)


def parse_range(body, what):
    """(quarter, lead, tail): the range is [25i - lead, 25(i+1) + tail]."""
    m = RANGE.search(body)
    if not m:
        return None, f"{what}'s animation-range is not the `--i` quarter form"
    q, s1, v1, q2, s2, v2 = m.groups()
    if q != q2:
        return None, f"{what}'s range uses two different quarter sizes, {q} and {q2}"
    lead = (float(v1) if v1 else 0.0) * (-1 if s1 == "+" else 1)
    tail = (float(v2) if v2 else 0.0) * (1 if s2 == "+" else -1)
    return (float(q), lead, tail), None


def plateau(css, name, prop, value, what):
    """The first and last keyframe offsets that set `prop` to `value`."""
    m = re.search(r"@keyframes\s+" + re.escape(name) + r"\s*\{(.*?)\n\}", css, re.S)
    if not m:
        return None, f"no @keyframes {name}"
    offs = []
    for sel, decls in re.findall(r"([\d%,\s]+)\{([^}]*)\}", m.group(1)):
        if re.search(re.escape(prop) + r"\s*:\s*" + re.escape(value) + r"\s*;", decls):
            offs += [float(o.strip().rstrip("%")) for o in sel.split(",") if o.strip()]
    if not offs:
        return None, f"@keyframes {name} never sets {prop} to {value} ({what})"
    return (min(offs), max(offs)), None


def band(rng, plat, i):
    q, lead, tail = rng
    a = q * i - lead
    z = q * (i + 1) + tail
    lo, hi = plat
    return a + lo / 100 * (z - a), a + hi / 100 * (z - a)


def main():
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()
    css = COMPONENTS.read_text(encoding="utf-8")
    bad = 0

    quarters = None
    for page in PAGES:
        n = len(re.findall(r'class="[^"]*\bcf-pin__step\b', page.read_text(encoding="utf-8")))
        if not n:
            bad |= fail(f"{page.name} has no .cf-pin__step — the register is stale")
        elif quarters is None:
            quarters = n
        elif n != quarters:
            bad |= fail(f"{page.name} has {n} steps against {quarters} — the two "
                        f"pinned stages no longer share a shape")
    if not quarters:
        return 1

    specs = []
    for sel, kf, prop, val, what in [
        (".cf-pin__step", "cf-pin-step", "opacity", "1", "the card on the stage"),
        (".cf-pin__mark", "cf-pin-mark", "color", "var(--text-primary)", "the numeral naming it"),
    ]:
        body = rule_body(css, sel)
        if body is None:
            bad |= fail(f"{sel} has no rule in components.css")
            continue
        if "linear" not in body:
            bad |= fail(f"{sel} is not linear — scroll position IS this state")
        if "both" not in body:
            bad |= fail(f"{sel} is not `both`-filled, so it has no state outside "
                        f"its own quarter")
        rng, err = parse_range(body, sel)
        if err:
            bad |= fail(err)
            continue
        plat, err = plateau(css, kf, prop, val, what)
        if err:
            bad |= fail(err)
            continue
        last, err = plateau(css, kf + "-last", prop, val, what)
        if err:
            bad |= fail(err)
            continue
        specs.append((sel, rng, plat, last, what))

    if len(specs) != 2:
        return 1
    (_, srng, splat, slast, _), (_, mrng, mplat, mlast, _) = specs

    for i in range(quarters):
        s_plat = slast if i == quarters - 1 else splat
        m_plat = mlast if i == quarters - 1 else mplat
        sa, sz = band(srng, s_plat, i)
        ma, mz = band(mrng, m_plat, i)
        if abs(sa - ma) > EPS or abs(sz - mz) > EPS:
            bad |= fail(
                f"quarter {i + 1}: the card is on the stage over contain "
                f"{sa:.2f}..{sz:.2f} % and its numeral is lit over "
                f"{ma:.2f}..{mz:.2f} % — the index would name nothing for "
                f"{abs(ma - sa) + abs(sz - mz):.2f} points of the run"
            )
    if bad:
        return 1

    sa, sz = band(srng, splat, 0)
    print(f"OK  {quarters} quarters on {len(PAGES)} pinned pages; the numeral is at "
          f"--text-primary over exactly the interval its card is opaque "
          f"(quarter 1: contain {sa:.2f}..{sz:.2f} %), off one range and one "
          f"pair of literals")
    return 0


if __name__ == "__main__":
    sys.exit(main())
