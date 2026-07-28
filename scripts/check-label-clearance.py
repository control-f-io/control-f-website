#!/usr/bin/env python3
"""Copy set on the root holds the clearance the root publishes.

The forty-eighth. check-flow-terminals.py holds the root's SHAPE, and
check-flow-values.py holds what it CARRIES -- it reads --x and --y off each
numeral and asserts the arithmetic balances and that the point rides a segment.
Neither of them looks at the one property that decides whether a numeral is
READABLE where it was put: how far it stands off the line it annotates.

WHAT THE DRAWING PUBLISHES. patterns/landing-page.html, on .lp-flow__val:

    "The offsets are PIXELS, not units. A clearance from the stroke stated in
     the drawing's units would close up as the box shrinks; these hold 12 px
     off the line at every viewport the gate admits."

Twelve pixels, stated once in prose and typed eight times in markup, on eight
sibling spans, by hand. That is the shape of every drift this repository has
had: a fact that is true of some of the elements, false of others, and
invisible in review because a numeral 9 px off a hairline looks exactly like a
numeral 12 px off a hairline until the box shrinks and the 9 becomes 4.

RULE ONE -- THE NUMERALS, AND IT USED TO HOLD THE WRONG QUANTITY. It read --tx
alone and asserted the eight agreed on it. --tx is the HORIZONTAL COMPONENT of
the offset, and a numeral is a horizontal box on a SLOPED line: on the 26.57deg
runs, 12 px across the page is 5.4 px off the stroke. So "the six agree on
12 px" was true of the component and false of the clearance, which came out
between 7.55 and 14.14 px across the eight -- and this check was the reason the
components all read 12 and nobody looked further. A check can hold a number
exactly and still be holding the wrong number.

It holds the offset's MAGNITUDE now: hypot(--tx, --ty), which is the distance
from the numeral's nearest corner to the point it labels, and -- because
check-flow-label-law.py separately holds that the offset is perpendicular to
the stroke -- the distance off the line. Three forms are legal per component,
and they are the same clearance seen from different sides:

    --tx: 5.367px                 the label hangs right of / below the point
    --tx: calc(-100% - 5.367px)   the label hangs left of / above it
    --ty: -50%                    a zero component, centred on that axis

A bare percentage other than -50%, a unitless number, or a length in any other
unit is a clearance that does not survive the box shrinking, which is the exact
failure the note above rules out in its own words.

WHAT THIS CHECK IS NOT. It holds that the eight agree on ONE clearance. It says
nothing about the DIRECTION of the offset or which side of its stroke a numeral
takes -- that is check-flow-label-law.py, and the two are only together a
placement rule. Eight numerals could agree perfectly on 12 px here and all
eight be pointing into the strokes.

RULE TWO -- THE CHROME THAT STANDS INSIDE THE DRAWING. The four step marks of
.cf-pin__index are copy on this same drawing and cannot state an offset,
because they are not placed against it -- they are the pinned stage's own first
row, and the drawing overhangs them. Their clearance is TIME: .lp-flow scrolls
with the page while .lp-frame sticks with the stage, so past the pin the
drawing withdraws from the chrome's row at 1.00 px per px of scroll.

That makes the chrome's arrival window the clearance, and it was written as
`entry 92% entry 100%`. `entry 100%` IS the pin -- the subject's leading edge
reaching the scrollport's start edge is the same instant .cf-pin__stage sticks
-- so the chrome finished arriving at the moment the drawing was still lying
across it. Measured as the minimum distance from any .cf-pin__mark box to any
.lp-flow__seg, in page pixels, at the pin:

    1280 x  800     0.00        mark 01 touched by the leftmost drop
    1440 x  900     0.00        the size the drawing is tuned at
    1600 x  900     0.00
    1366 x  768     2.72
    1280 x  720    24.58        clear
    1280 x  900    26.23        clear
    1440 x  720    75.91        clear
    1024 x  900   108.20        clear
    1920 x 1080   139.64        clear

The five clear rows are clear for the wrong reason -- their flow-to-frame gap
is 26 to 172 px, so the drawing never reaches the chrome at all. The four that
are touched are the four where that seam is TIGHT, 1.57 to 34.66 px. The closer
the drawing comes to landing where it should, the harder it lands on the copy
underneath, which is why this cannot be left to whoever next narrows the gap.

So: chrome that stands inside the drawing's box may not name `entry` in its
arrival range. `entry` ends at the pin by definition, and at the pin the
drawing has not left. It must arrive on `contain`, at a positive offset past
the pin -- a LENGTH, for the same reason the numerals' clearance is a length,
and a rem one, because the marks are type and the row-gap over them is a rem,
so the deficit scales with the reader's root size and the clearance has to
scale with it.

WHAT THIS CHECK CANNOT SEE, stated so it is not mistaken for covered. It holds
that the chrome asks for its clearance in the right currency; it cannot compute
that the amount is enough, because the amount it must beat is the flow-to-frame
gap, and check-flow-handover.py's own note explains at length why that gap is
not countable in any file. The number of record is 42.23 px at 1440 x 900 and
the measurement is in the .lp-proc-index note beside the declaration. This
check makes a hand edit back to `entry` impossible, which is where it went
wrong; it does not make the seams routine unnecessary.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-label-clearance.py
    python3 scripts/check-label-clearance.py -v
"""

import argparse
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = ROOT / "design-system" / "patterns"
TOKENS = ROOT / "design-system" / "assets" / "css" / "tokens.css"

# The copy that rides the routes, and the chrome that stands inside the box.
VALUE_CLASS = "lp-flow__val"
CHROME_SELECTORS = (".lp-proc-index", ".lp-proc-bar")

SPAN_RE = re.compile(r'<span\b[^>]*class="([^"]*)"[^>]*style="([^"]*)"[^>]*>([^<]*)</span>', re.S)

# 5.367px   |   calc(-100% - 5.367px)   |   -50%, the zero component
PLAIN_RE = re.compile(r"^(-?\d+(?:\.\d+)?)px$")
CALC_RE = re.compile(r"^calc\(\s*-100%\s*-\s*(\d+(?:\.\d+)?)px\s*\)$")

# The block that gives the chrome its arrival, and the range it asks for.
RULE_RE = re.compile(
    r"(" + r"\s*,\s*".join(re.escape(s) for s in CHROME_SELECTORS) + r")\s*\{([^}]*)\}", re.S)
RANGE_RE = re.compile(r"animation-range\s*:\s*([^;}]+)", re.S)
LENGTH_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(px|rem|em)\b")
VAR_RE = re.compile(r"var\(\s*(--[\w-]+)\s*\)")
TOKEN_RE = re.compile(r"^\s*(--space-[\w-]+)\s*:\s*([^;]+);", re.M)


def spacing_tokens():
    """The rungs of the space scale, so a range written against the scale reads
    as the length it is. A check that only understood literals would push the
    fix towards a magic number, which is the opposite of the point."""
    if not TOKENS.exists():
        return {}
    return {n: v.split("/*")[0].strip() for n, v in TOKEN_RE.findall(
        TOKENS.read_text(encoding="utf-8"))}


def resolve(text, tokens):
    """One pass of var() substitution over the space scale. The scale is flat —
    a rung is a literal — so one pass is all there is."""
    return VAR_RE.sub(lambda m: tokens.get(m.group(1), m.group(0)), text)


def style_vars(style):
    out = {}
    for decl in style.split(";"):
        if ":" in decl and decl.strip().startswith("--"):
            name, _, value = decl.partition(":")
            out[name.strip()] = value.strip()
    return out


def component_of(value):
    """One component of the offset in px, or None if it is not stated in px.

    -50% is a ZERO component and the only percentage that is: it centres the
    box on that axis, which is what the vertical trunk's numeral needs and
    what a sloped stroke's never does.
    """
    text = " ".join(value.split())
    if text == "-50%":
        return 0.0
    m = PLAIN_RE.match(text)
    if m:
        return abs(float(m.group(1)))
    m = CALC_RE.match(text)
    if m:
        return float(m.group(1))
    return None


def clearance_of(tx, ty):
    """The offset's magnitude — the distance from the nearest corner to the point."""
    a, b = component_of(tx), component_of(ty)
    if a is None or b is None:
        return None
    return round(math.hypot(a, b), 3)


def check_values(page, text, findings, verbose):
    held = {}
    for classes, style, label in SPAN_RE.findall(text):
        if VALUE_CLASS not in classes.split():
            continue
        var = style_vars(style)
        name = " ".join(label.split()) or "(blank)"
        missing = [a for a in ("--tx", "--ty") if a not in var]
        if missing:
            findings.append(
                f"{page.name}: the value {name!r} declares no {' or '.join(missing)} — "
                f"the clearance is the magnitude of BOTH components, so a missing one "
                f"is not a zero, it is an unstated distance, and .lp-flow__val's own "
                f"note publishes the number: 12 px off the line at every viewport the "
                f"gate admits")
            continue
        px = clearance_of(var["--tx"], var["--ty"])
        if px is None:
            findings.append(
                f"{page.name}: the value {name!r} states its offset as "
                f"{var['--tx']!r} / {var['--ty']!r} — not a pair of px lengths. A "
                f"clearance in the drawing's units or in percent closes up as the box "
                f"shrinks, which is the failure .lp-flow__val's note rules out in its "
                f"own words")
            continue
        held.setdefault(px, []).append(name)

    if len(held) > 1:
        spread = "; ".join(f"{px:g} px on {', '.join(sorted(n))}"
                           for px, n in sorted(held.items()))
        findings.append(
            f"{page.name}: the values do not agree on one clearance — {spread}. "
            f"The clearance is hypot(--tx, --ty), not either component: a numeral is "
            f"a horizontal box on a sloped line, so agreeing on --tx alone is how "
            f"eight labels came to hold 7.55 to 14.14 px while every --tx read 12")
    if verbose and held:
        for px, names in sorted(held.items()):
            print(f"    {len(names)} value(s) hold {px:g} px off the line (hypot of --tx, --ty): "
                  f"{', '.join(sorted(names))}")
    return sum(len(n) for n in held.values())


def check_chrome(page, text, findings, verbose, tokens):
    m = RULE_RE.search(text)
    if not m:
        return False
    body = m.group(2)
    rng = RANGE_RE.search(body)
    if not rng:
        findings.append(
            f"{page.name}: {', '.join(CHROME_SELECTORS)} animates with no "
            f"animation-range — the implicit `normal` runs the fade across the "
            f"whole timeline, so the chrome is arriving from the moment the "
            f"section is touched, drawing and all")
        return True
    written = " ".join(rng.group(1).split())
    text_range = resolve(written, tokens)

    if "entry" in text_range:
        findings.append(
            f"{page.name}: the stage's chrome arrives on {text_range!r}. `entry` "
            f"ends at the instant .cf-pin__stage sticks, and at that instant the "
            f"root is still lying across the chrome's row — 0.00 px from mark 01 "
            f"at three of nine viewports. The chrome stands inside the drawing's "
            f"box, so its clearance is time past the pin: it must arrive on "
            f"`contain`, at a positive offset")
        if verbose:
            print(f"    chrome arrival: {written}")
        return True

    if "contain" not in text_range:
        findings.append(
            f"{page.name}: the stage's chrome arrives on {text_range!r}, which "
            f"names neither `entry` nor `contain`. The offset past the pin is "
            f"what the clearance is measured in, so it has to be a contain offset")
        return True

    lengths = LENGTH_RE.findall(text_range)
    if not lengths:
        findings.append(
            f"{page.name}: the stage's chrome arrives on {text_range!r} — a "
            f"contain range with no length in it. A percentage of contain is a "
            f"different number of pixels at every viewport height, and the "
            f"clearance it has to buy is a fixed distance in page pixels")
        return True
    if not any(u in ("rem", "em") for _, u in lengths):
        findings.append(
            f"{page.name}: the stage's chrome arrives on {text_range!r} — a "
            f"contain offset in px only. The marks are type and the row-gap over "
            f"them is a rem, so the deficit this clearance covers grows with the "
            f"reader's root size and the clearance has to grow with it")
        return True
    if all(float(v) == 0 for v, _ in lengths):
        findings.append(
            f"{page.name}: the stage's chrome arrives on {text_range!r} — a zero "
            f"offset is the pin itself, which is the position the drawing has "
            f"not left yet")
        return True

    if verbose:
        px = ", ".join(f"{v} {u}" for v, u in lengths)
        print(f"    chrome arrival: {written}  ->  {text_range}  ({px})")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Copy set on the root holds the clearance the root publishes.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="print every clearance held and the chrome's arrival range")
    args = parser.parse_args()

    tokens = spacing_tokens()
    findings, values, chromes, pages = [], 0, 0, 0
    for page in sorted(PATTERNS.glob("*.html")):
        text = page.read_text(encoding="utf-8")
        if VALUE_CLASS not in text and CHROME_SELECTORS[0] not in text:
            continue
        pages += 1
        if args.verbose:
            print(f"  {page.name}:")
        values += check_values(page, text, findings, args.verbose)
        chromes += 1 if check_chrome(page, text, findings, args.verbose, tokens) else 0

    if not pages:
        print("label clearance: no copy set on a root — the selector went stale")
        return 1
    if findings:
        print(f"\nlabel clearance: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1
    print(f"label clearance OK — {values} value(s) on {pages} page(s) hold one px "
          f"clearance off the line, and {chromes} pinned chrome(s) wait for theirs "
          f"past the pin rather than claiming it at the pin")
    return 0


if __name__ == "__main__":
    sys.exit(main())
