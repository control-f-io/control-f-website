#!/usr/bin/env python3
"""The act rail only paints where the page has a margin to paint it in.

The seventy-ninth check, and the second whose subject is the act rail.

WHAT WENT WRONG. The rail is a fixed column of marks in the LEFT MARGIN — five
acts and two jumps, 84 px wide, held at --space-6 from the viewport's edge, so
it ends at 108. The margin it was put in is --column-inset, which tokens.css
derives as max(--gutter, (100% - --container-max) / 2) and which is where every
container on the page starts its content. The rail's own gate was --space-6 and
64rem, neither of which knows what --column-inset is, and below 1536 px
--column-inset is smaller than the rail:

    width   --column-inset   rail ends   inside the content column by
     1024        56.31          108              51.7
     1280        70.39          108              37.6
     1440        80             108              28
     1536       128             108             -20   the first width that clears

So for the whole of the 64rem-to-96rem band the rail's numerals and glyphs were
painted on top of the page's own first 28 to 52 px of text. Swept in Chromium at
35 scroll stops per width, with getClientRects() over every painted text run in
the viewport, the runs the rail crossed and by how many pixels:

                                          1024   1280   1440   1536
    act 1  .cf-annot__label "S08"            4     20      -      -
    act 1  the field's kPa readings         54     19      -      -
    act 2  .lp-flow__read "12.4 bar"        38      7      -      -
    act 2  .cf-stream__text, act 2's copy   25      7     10      -
    act 3  "Was wir machen", the head       52     38     28      -
    act 4  .sp4-mark "01 / Geschäftsführung" 76     25      -      -
    act 4  the founders' names and copy     76     25      -      -
    act 5  .map-beat__mark, all three        -      -     28      -

Act 4 at 1024 is the one that cannot be argued about: the rail stands in 76 of
the 84 px it occupies over the copy column, so a label, two names and the
paragraph under them are read through five numerals and five glyphs.

AND IT COULD NOT HAVE BEEN FIXED BY MOVING THE RAIL, which is why this check
holds the tier and not the inset. Flush at the viewport's edge the rail still
ends at 84 against a column starting at 56.31, 70.39 and 80 — it overlaps at
every width below 1424 wherever it is put. Collapsing the glyph column at rest
does not save it either: the row's three --space-3 gaps survive the collapse, so
it is still 68 px against a 56 px margin. The rail does not fit below 96rem, so
below 96rem it does not paint.

WHAT IS CHECKED. Both stylesheets, comments stripped, because this file's own
prose quotes the declarations it is about.

  THE FLOOR    acts.css has a rule that stops the rail painting at rest —
               opacity 0 on .act-rail:not(:focus-within) — inside a max-width
               media query. The width just past that max-width is the narrowest
               viewport at which the scroll is allowed to bring the rail in.

  THE EXTENT   the rail's width is read from its own declarations rather than
               assumed: .act-rail__link's grid-template-columns, its gap, and
               the collapsed --act-glyph, all resolved through tokens.css. Plus
               .act-rail's inset-inline-start. Change any of them and the number
               this check compares moves with them.

  THE MARGIN   --column-inset evaluated at the floor width, out of --gutter's
               own clamp and --container-max, both read from tokens.css.

  THE VERDICT  the rail's right edge clears --column-inset by at least
               --space-4, the rung below the inset it already stands on.

WHAT THIS DOES NOT CLAIM. Not that the rail is unreachable below the floor — it
is lifted by :focus-within at every width and check-focus-reach.py holds that.
Not that nothing else may overlap the rail: act 1's field is full-bleed and its
callouts are placed on the drawing rather than in the column, so they can land
under the rail at any width, and one of them does at 1536. That is the field's
placement against a fixed element, not the column's, and it is a different
check than this one.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-rail-margin.py
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ACTS = ROOT / "design-system/assets/css/acts.css"
TOKENS = ROOT / "design-system/assets/css/tokens.css"

ROOT_FONT = 16.0          # base.css never re-roots the rem; --text-* scale off it
CLEARANCE = "--space-4"   # the rung below the rail's own inset


def fail(msg):
    print(f"FAIL  {msg}")
    return 1


def strip_comments(css):
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def px(value, tokens, width=None):
    """A CSS length in px. Handles rem, px, vw, var(), calc(), clamp(), max()."""
    v = value.strip()
    m = re.fullmatch(r"var\(\s*(--[\w-]+)\s*\)", v)
    if m:
        return px(tokens[m.group(1)], tokens, width)
    m = re.fullmatch(r"(clamp|max|min)\((.*)\)", v, flags=re.S)
    if m:
        fn, args = m.group(1), split_args(m.group(2))
        vals = [px(a, tokens, width) for a in args]
        if fn == "clamp":
            return max(vals[0], min(vals[1], vals[2]))
        return (max if fn == "max" else min)(vals)
    m = re.fullmatch(r"calc\((.*)\)", v, flags=re.S)
    if m:
        return calc(m.group(1), tokens, width)
    m = re.fullmatch(r"(-?[\d.]+)(rem|px|vw|%)?", v)
    if not m:
        # Inside max()/min()/clamp() the arithmetic needs no calc() wrapper, so
        # --column-inset's `(100% - var(--container-max)) / 2` arrives bare.
        if "(" in v or re.search(r" [-+*/] |/", v):
            return calc(v, tokens, width)
        raise ValueError(f"cannot resolve length {value!r}")
    n = float(m.group(1))
    unit = m.group(2) or "px"
    if unit == "rem":
        return n * ROOT_FONT
    if unit in ("vw", "%"):
        if width is None:
            raise ValueError(f"{value!r} needs a viewport width")
        return n * width / 100.0
    return n


def split_args(s):
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    out.append(cur)
    return [a.strip() for a in out if a.strip()]


def calc(expr, tokens, width):
    """Only the shapes the sheets actually use: a - b, a / n, a * n, a + b."""
    expr = expr.strip()
    for op in ("+", "-"):
        depth = 0
        for i in range(len(expr) - 1, 0, -1):
            ch = expr[i]
            if ch == ")":
                depth += 1
            elif ch == "(":
                depth -= 1
            elif ch == op and depth == 0 and expr[i - 1] == " ":
                return (calc(expr[:i], tokens, width)
                        + (1 if op == "+" else -1) * calc(expr[i + 1:], tokens, width))
    for op in ("*", "/"):
        depth = 0
        for i in range(len(expr) - 1, 0, -1):
            ch = expr[i]
            if ch == ")":
                depth += 1
            elif ch == "(":
                depth -= 1
            elif ch == op and depth == 0:
                a = calc(expr[:i], tokens, width)
                b = calc(expr[i + 1:], tokens, width)
                return a * b if op == "*" else a / b
    if expr.startswith("(") and expr.endswith(")"):
        return calc(expr[1:-1], tokens, width)
    return px(expr, tokens, width)


def declarations(body):
    return {d.split(":", 1)[0].strip(): d.split(":", 1)[1].strip()
            for d in body.split(";") if ":" in d}


def main():
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()

    tokens = {}
    for name, value in re.findall(r"(--[\w-]+)\s*:\s*([^;{}]+);",
                                  strip_comments(TOKENS.read_text(encoding="utf-8"))):
        tokens.setdefault(name, value.strip())
    for required in ("--gutter", "--container-max", "--space-3", "--space-4", "--space-6"):
        if required not in tokens:
            return fail(f"tokens.css no longer declares {required} — this check "
                        f"reads the rail's margin out of it")

    acts = strip_comments(ACTS.read_text(encoding="utf-8"))

    # ---- the floor: the width just past the max-width that stops the paint ----
    floor = None
    for m in re.finditer(r"@media[^{]*?\(\s*max-width\s*:\s*([\d.]+)(rem|px)\s*\)([^{]*)\{(.*?)\n\s*\}",
                         acts, flags=re.S):
        block = m.group(4)
        if not re.search(r"\.act-rail(?![\w_-])[^{}]*\{[^{}]*opacity\s*:\s*0\s*[;}]", block):
            continue
        w = float(m.group(1)) * (ROOT_FONT if m.group(2) == "rem" else 1)
        floor = w if floor is None else min(floor, w)
    if floor is None:
        return fail("no max-width media query in acts.css sets the rail's "
                    "opacity to 0, so the scroll lifts the rail at every width "
                    "its 64rem gate opens at — including the ones whose "
                    "--column-inset is narrower than the rail, where the marks "
                    "land on the acts' own text. See the table above.")
    # 95.999rem is "everything below 96rem"; the floor is the next width up.
    floor = float(int(floor) + 1) if floor != int(floor) else floor + 1.0

    # ---- the extent: read off the rail's own declarations ----
    rail_decls, link_decls = {}, {}
    for terms, body in ((t.strip(), b) for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", acts)
                        for t in [m.group(1)] for b in [m.group(2)]):
        last = terms.split(",")[-1].strip()
        if last == ".act-rail":
            rail_decls.update(declarations(body))
        if last in (".act-rail__link", ".act-rail__jump"):
            link_decls.update(declarations(body))

    try:
        inset = px(rail_decls["inset-inline-start"], tokens)
        gap = px(link_decls["gap"], tokens)
        glyph = px(rail_decls["--act-glyph"], tokens)
        cols = link_decls["grid-template-columns"].split()
    except (KeyError, ValueError) as exc:
        return fail(f"cannot read the rail's own geometry out of acts.css "
                    f"({exc}); this check sizes the rail from its declarations "
                    f"rather than from a number typed here")

    widths = []
    for c in cols:
        widths.append(glyph if c == "auto" else px(c, tokens))
    # the fourth column is the collapsed title: `auto` over a clipped label,
    # which measures 0 at rest. The third is the glyph.
    widths[-1] = 0.0
    extent = sum(widths) + gap * (len(widths) - 1)
    right = inset + extent

    # ---- the margin at the floor ----
    column_inset = px(tokens["--column-inset"], tokens, floor) if "--column-inset" in tokens \
        else max(px(tokens["--gutter"], tokens, floor),
                 (floor - px(tokens["--container-max"], tokens)) / 2)
    clearance = px(tokens[CLEARANCE], tokens)
    have = column_inset - right

    if have < clearance:
        return fail(
            f"the rail is allowed to paint from {floor:.0f} px up, where the "
            f"content column starts at {column_inset:.2f} px and the rail ends "
            f"at {right:.0f} ({inset:.0f} inset + {extent:.0f} wide). That "
            f"leaves {have:.2f} px between them, short of the {clearance:.0f} px "
            f"({CLEARANCE}) this asks for, so the rail's marks are painted "
            f"inside the acts' own text column. Either raise the width at which "
            f"the rail is lifted or narrow the rail — moving it left does not "
            f"work, see the note in acts.css.")

    print(f"OK  the act rail paints from {floor:.0f} px up, where the content "
          f"column starts at {column_inset:.2f} px and the rail's {extent:.0f} px "
          f"of marks end at {right:.0f} — {have:.2f} px of margin between them, "
          f"clear of the {clearance:.0f} px floor")
    return 0


if __name__ == "__main__":
    sys.exit(main())
