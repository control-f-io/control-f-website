#!/usr/bin/env python3
"""A reservation for furniture must be the sum of the furniture.

acts.css binds act 3's card width to the viewport HEIGHT, because the pinned
stage crops rather than scrolls and a card taller than the stage loses its
bottom edge to the clip:

    --lp-measure: calc((max(...) - <chrome>) * 2)

<chrome> is what the stage's own furniture takes off the top and bottom before
the card gets any: two paddings, two row-gaps, the index's line, the bar's
hairline. For as long as that term was a flat `13rem` nothing read it against
the five declarations it stands for, and it was 1.69rem too large at every root
size — 27.1 px at 16, 55.1 px at 32.

TOO LARGE IS NOT THE SAFE DIRECTION HERE, which is the whole reason this file
exists. The expression multiplies by two, so 27 px of over-reservation is 54 px
of card width; and this card is a column of copy beside a square, so it gets
TALLER as it narrows — check-consent-clearance.py's link 6 states that
inversion in its own words. A reservation written to make the card fit a short
viewport was, at every viewport where it bound, handing back a taller card:

    viewport      card before      card after       plate cut by the clip
    1366 x 768    1120 x 731       1174 x 690       23 px -> 3
    1440 x 720    1024 x 772       1078 x 751       67    -> 57
    1280 x 720    1024 x 772       1078 x 751       67    -> 57

Nothing rendered an error and no gate saw it. check-rem-floor.py measures this
same stage against this same clip and reports "cut 0" at a 16 px root, because
it counts COPY RUNS and the copy is centred in a panel with air under it: what
was outside the clip was the plate's own bottom rail, the one stroke .lp-frame
exists to draw.

WHAT IS CHECKED — two readings of the same claim, plus the shape that makes
both possible: --lp-measure must subtract ONE parenthesised sum, `- (…)) * 2`,
so that the term the card's whole size comes off is something a file can be
held to rather than a constant. A flat `13rem` fails on the shape alone.

  1. THE TERMS. The reservation's calc() is parsed into a multiset of token
     references, and so are the five declarations it reserves for, read from
     the stylesheets where they live rather than restated here:

       .cf-pin__inner   padding-block-start   components.css
       .lp-proc-stage   row-gap, counted twice (three rows, two gaps)
       .cf-pin__inner   padding-block-end
       .cf-pin__index   font-size, times the line-height it inherits
       .cf-pin__bar     height

     The two multisets must be equal. Change a rung in any of the five and the
     reservation stops being their sum, which is the drift that put 13rem
     there and kept it.

  2. THE NUMBER. Both sides are resolved against tokens.css at 16, 20, 24 and
     32 px roots and must agree to within a tenth of a pixel. This is the
     arithmetic behind reading 1, and it is what ties this file to the table
     acts.css publishes over the derivation: 180.95 / 225.94 / 270.93 / 360.90.
     It fails when a term stops being resolvable at all — the reservation the
     card's whole size comes off has to stay readable — and it is the reason
     reading 1 can afford to compare names rather than trusting them.

     It does NOT catch a rung whose token VALUE moves, and that is right
     rather than a gap: both sides name the same token, so --nav-height going
     5.25rem -> 6rem moves the reservation and the padding together and they
     stay equal. That is the whole point of naming them.

WHAT IT DOES NOT CHECK, deliberately

  Whether the card then fits. It does not, below about 871 px of viewport
  height — the card's floor height is 690 px at the container's own measure
  and the furniture is 181 — and the gate admits 720. That is a question about
  where the gate stands, not about whether this term is honest, and it is
  written up as an open finding rather than smuggled in here.

  Any other page's chrome. .lp-proc-stage is the only stage on the site whose
  measure is derived from the block axis; act 4's, one section down, takes a
  flat `min(72rem, 100%)` and is the sibling that never crops.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-pin-reservation.py       # check, exit 1 on a finding
    python3 scripts/check-pin-reservation.py -v    # print what it resolved
"""

import argparse
import pathlib
import re
import sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
TOKENS = DS / "assets/css/tokens.css"
BASE = DS / "assets/css/base.css"
COMPONENTS = DS / "assets/css/components.css"
ACTS = DS / "assets/css/acts.css"

CONSUMER = "--lp-measure"
ROOTS = (16, 20, 24, 32)

# The reservation is the parenthesised subtrahend inside --lp-measure rather
# than a property of its own, and that is not a style choice.
# check-fluid-crossovers.py resolves var() through tokens.css alone, so a
# `- var(--lp-chrome)` naming a property acts.css defines is a var it cannot
# resolve — the declaration goes to that census's "unread" pile and the
# crossover at 576 px tall stops being published. Named, this term costs
# another gate its coverage; inlined, every var() in it resolves and the row
# stands. So the sum stays in place and this file reaches in for it.
SUBTRAHEND = re.compile(r"-\s*(\((?:[^()]|\([^()]*\))*\))\s*\)\s*\*\s*2")

# The five declarations the reservation stands for: (label, sheet, selector,
# property, how many of them the stage has).
FURNITURE = [
    ("the stage's clearance under the nav", COMPONENTS, ".cf-pin__inner",
     "padding-block", 1, "start"),
    ("the stage's foot", COMPONENTS, ".cf-pin__inner", "padding-block", 1,
     "end"),
    ("the gap between the three rows", ACTS, ".lp-proc-stage", "row-gap", 2,
     None),
    ("the index's one line", COMPONENTS, ".cf-pin__index", "font-size", 1,
     "leading"),
    ("the progress hairline", COMPONENTS, ".cf-pin__bar", "height", 1, None),
]

# .cf-pin__index sets a size and no leading, so the line it occupies is that
# size times whatever base.css puts on the document. Read, not assumed.
BODY_LEADING_SEL = "body"


def strip_comments(css):
    """Blank /* ... */ keeping the newlines, so line numbers survive."""
    return re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), css,
                  flags=re.S)


def rules(css):
    """Yield (line, selector, declarations) for every style rule, at any depth.

    A brace walker rather than a parser: this system's CSS nests @supports
    inside @media inside nothing else, and a rule is any block whose prelude
    does not start with @.
    """
    css = strip_comments(css)
    depth, i, start = 0, 0, 0
    stack = []
    while i < len(css):
        c = css[i]
        if c == "{":
            prelude = css[start:i].strip()
            stack.append(prelude)
            depth += 1
            i += 1
            start = i
            continue
        if c == "}":
            body_start = start
            prelude = stack.pop() if stack else ""
            depth -= 1
            if prelude and not prelude.startswith("@"):
                line = css.count("\n", 0, body_start) + 1
                yield line, prelude, css[body_start:i]
            i += 1
            start = i
            continue
        i += 1


def declarations(body):
    """Top-level `prop: value` pairs of a rule body, nested blocks removed."""
    flat, depth = [], 0
    for c in body:
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        elif depth == 0:
            flat.append(c)
    out = []
    for part in "".join(flat).split(";"):
        if ":" not in part:
            continue
        prop, _, value = part.partition(":")
        out.append((prop.strip(), value.strip()))
    return out


def find_declaration(sheet, selector, prop):
    """The last `prop` declared on a rule whose selector names `selector`.

    Last, because these sheets restate a selector to group an argument with
    the rules it is about, and the cascade takes the last one.
    """
    css = sheet.read_text(encoding="utf-8")
    found = None
    for line, sel, body in rules(css):
        names = {s.strip() for s in sel.split(",")}
        if selector not in names:
            continue
        for name, value in declarations(body):
            if name == prop:
                found = (line, " ".join(value.split()))
    return found


# ---- reading tokens -------------------------------------------------------

TOKEN_DEF = re.compile(r"^\s*(--[\w-]+)\s*:\s*([^;{}]+);", re.M)


def token_table():
    """Every `--name: <literal>` in tokens.css, as it is written."""
    css = strip_comments(TOKENS.read_text(encoding="utf-8"))
    return {m.group(1): " ".join(m.group(2).split())
            for m in TOKEN_DEF.finditer(css)}


LENGTH = re.compile(r"^(-?[\d.]+)(rem|px|em)?$")


def resolve(value, tokens, root, seen=()):
    """A token expression to pixels at a given root size, or None.

    Handles exactly what these five declarations and the reservation are made
    of: var() references, `+` sums, `N *` multipliers, a product of two terms,
    parentheses, rem/px lengths and bare numbers (a line-height). Anything
    else returns None and is reported rather than guessed at.
    """
    value = value.strip()
    if value.startswith("calc(") and value.endswith(")"):
        value = value[5:-1].strip()
    while value.startswith("(") and value.endswith(")") and balanced(value[1:-1]):
        value = value[1:-1].strip()

    for op, fn in (("+", lambda a, b: a + b),):
        parts = split_top(value, op)
        if len(parts) > 1:
            out = 0.0
            for part in parts:
                got = resolve(part, tokens, root, seen)
                if got is None:
                    return None
                out = fn(out, got)
            return out

    parts = split_top(value, "*")
    if len(parts) > 1:
        out = 1.0
        for part in parts:
            got = resolve(part, tokens, root, seen)
            if got is None:
                return None
            out *= got
        return out

    m = re.fullmatch(r"var\(\s*(--[\w-]+)\s*\)", value)
    if m:
        name = m.group(1)
        if name in seen or name not in tokens:
            return None
        return resolve(tokens[name], tokens, root, seen + (name,))

    m = LENGTH.fullmatch(value)
    if m:
        n = float(m.group(1))
        unit = m.group(2)
        if unit == "rem" or unit == "em":
            return n * root
        return n
    return None


def balanced(text):
    depth = 0
    for c in text:
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def split_top(value, op):
    """Split on `op` at paren depth zero. `*` never follows a var() name."""
    parts, depth, cur = [], 0, []
    for c in value:
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        if c == op and depth == 0:
            parts.append("".join(cur))
            cur = []
            continue
        cur.append(c)
    parts.append("".join(cur))
    return [p.strip() for p in parts if p.strip()]


# ---- the terms ------------------------------------------------------------

def terms(value):
    """A token expression as a multiset of what it references.

    A sum contributes its parts; `N * x` contributes x N times; a product of
    two var()s contributes the pair, so the index's `size * leading` is one
    term rather than two loose ones.
    """
    value = value.strip()
    if value.startswith("calc(") and value.endswith(")"):
        value = value[5:-1].strip()
    while value.startswith("(") and value.endswith(")") and balanced(value[1:-1]):
        value = value[1:-1].strip()

    parts = split_top(value, "+")
    if len(parts) > 1:
        out = Counter()
        for part in parts:
            out += terms(part)
        return out

    parts = split_top(value, "*")
    if len(parts) > 1:
        names, count = [], 1
        for part in parts:
            m = re.fullmatch(r"var\(\s*(--[\w-]+)\s*\)", part)
            if m:
                names.append(m.group(1))
                continue
            n = LENGTH.fullmatch(part)
            if n and not n.group(2):
                count *= int(float(n.group(1)))
                continue
            return Counter({"?" + part: 1})
        return Counter({" * ".join(sorted(names)): count})

    m = re.fullmatch(r"var\(\s*(--[\w-]+)\s*\)", value)
    if m:
        return Counter({m.group(1): 1})
    return Counter({"?" + value: 1})


def shorthand_side(value, side):
    """`padding-block: A B` -> A or B; a single value is both."""
    parts = split_shorthand(value)
    if len(parts) == 1:
        return parts[0]
    return parts[0] if side == "start" else parts[1]


def split_shorthand(value):
    parts, depth, cur = [], 0, []
    for c in value:
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        if c == " " and depth == 0:
            if cur:
                parts.append("".join(cur))
                cur = []
            continue
        cur.append(c)
    if cur:
        parts.append("".join(cur))
    return parts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    findings, notes = [], []
    tokens = token_table()

    consumer = find_declaration(ACTS, "main", CONSUMER)
    if not consumer:
        print(f"FINDING  {ACTS.relative_to(ROOT)}: no {CONSUMER} on `main`. "
              f"That declaration is act 3's card width and the reservation is "
              f"the term it subtracts; without it there is nothing to read.")
        print("\ncheck-pin-reservation: 1 finding(s).")
        return 1
    res_line, cons_value = consumer
    match = SUBTRAHEND.search(cons_value)
    if not match:
        print(f"FINDING  {ACTS.relative_to(ROOT)}:{res_line}  {CONSUMER} is "
              f"`{cons_value}` and this file cannot find the reservation in "
              f"it. The shape it reads is `- (<sum>)) * 2`: one parenthesised "
              f"subtrahend, so the term the card's whole size comes off is a "
              f"sum something can be held to rather than a constant.")
        print("\ncheck-pin-reservation: 1 finding(s).")
        return 1
    res_value = match.group(1)
    notes.append(f"reservation  {ACTS.relative_to(ROOT)}:{res_line}  {res_value}")

    # ---- 1. the terms -----------------------------------------------------
    want = Counter()
    body_leading = find_declaration(BASE, BODY_LEADING_SEL, "line-height")
    for label, sheet, selector, prop, count, part in FURNITURE:
        got = find_declaration(sheet, selector, prop)
        if not got:
            findings.append(
                f"{sheet.relative_to(ROOT)}: no `{prop}` on `{selector}` — "
                f"{label}. The reservation reserves for it, so it cannot be "
                f"read from anywhere else.")
            continue
        line, value = got
        if part in ("start", "end"):
            value = shorthand_side(value, part)
        piece = terms(value)
        if part == "leading":
            if not body_leading:
                findings.append(
                    f"{BASE.relative_to(ROOT)}: no `line-height` on "
                    f"`{BODY_LEADING_SEL}` — the index sets a size and no "
                    f"leading, so its line is that size times the document's "
                    f"and there is nothing to read it from.")
                continue
            lead = terms(body_leading[1])
            if len(piece) != 1 or len(lead) != 1:
                findings.append(
                    f"{sheet.relative_to(ROOT)}:{line}  the index's line is "
                    f"`{value}` times `{body_leading[1]}` and one of the two "
                    f"is not a single token — this file can only hold a "
                    f"product of two.")
                continue
            names = sorted([next(iter(piece)), next(iter(lead))])
            piece = Counter({" * ".join(names): 1})
        for _ in range(count):
            want += piece
        notes.append(f"  {label}: {sheet.relative_to(ROOT)}:{line}  "
                     f"{prop} -> {value}" + (f"  x{count}" if count > 1 else ""))

    have = terms(res_value)
    if findings:
        pass
    elif have != want:
        over = have - want
        under = want - have
        detail = []
        if over:
            detail.append("reserves for, and nothing declares: "
                          + ", ".join(f"{k} x{v}" for k, v in sorted(over.items())))
        if under:
            detail.append("declared, and the reservation does not carry: "
                          + ", ".join(f"{k} x{v}" for k, v in sorted(under.items())))
        findings.append(
            f"{ACTS.relative_to(ROOT)}:{res_line}  the reservation is not the "
            f"sum of the five declarations it stands for. "
            + "; ".join(detail)
            + ". A reservation larger than its furniture is doubled by the "
              "`* 2` and spent narrowing a card that gets taller as it "
              "narrows; smaller, and the trio rides up under the nav.")

    # ---- 2. the number ----------------------------------------------------
    if not findings:
        for root in ROOTS:
            a = resolve(res_value, tokens, root)
            if a is None:
                findings.append(
                    f"{ACTS.relative_to(ROOT)}:{res_line}  the reservation has a "
                    f"term this file cannot resolve to a length. It is the "
                    f"reservation the card's whole size comes off — it has to "
                    f"stay readable.")
                break
            total = 0.0
            broken = False
            for label, sheet, selector, prop, count, part in FURNITURE:
                line, value = find_declaration(sheet, selector, prop)
                if part in ("start", "end"):
                    value = shorthand_side(value, part)
                b = resolve(value, tokens, root)
                if b is None:
                    findings.append(
                        f"{sheet.relative_to(ROOT)}:{line}  `{prop}: {value}` "
                        f"({label}) is not a length this file can resolve, so "
                        f"the reservation cannot be checked against it.")
                    broken = True
                    break
                if part == "leading":
                    lead = resolve(body_leading[1], tokens, root)
                    if lead is None:
                        findings.append(
                            f"{BASE.relative_to(ROOT)}: `line-height: "
                            f"{body_leading[1]}` is not a number this file can "
                            f"resolve.")
                        broken = True
                        break
                    b *= lead
                total += b * count
            if broken:
                break
            notes.append(f"  root {root}px: reservation {a:.2f} px, "
                         f"furniture {total:.2f} px")
            if abs(a - total) > 0.1:
                findings.append(
                    f"{ACTS.relative_to(ROOT)}:{res_line}  at a {root}px root "
                    f"the reservation resolves to {a:.2f} px and the five "
                    f"declarations it reserves for come to {total:.2f} px — "
                    f"off by {a - total:+.2f}. The names still agree; a value "
                    f"under one of them moved.")

    if args.verbose or findings:
        for n in notes:
            print(n)
    for f in findings:
        print(f"FINDING  {f}")
    if findings:
        print(f"\ncheck-pin-reservation: {len(findings)} finding(s).")
        return 1
    print(f"check-pin-reservation: the pinned stage's height reservation is "
          f"the sum of its {len(FURNITURE)} declarations, at "
          f"{'/'.join(str(r) for r in ROOTS)} px roots.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
