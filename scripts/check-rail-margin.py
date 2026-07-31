#!/usr/bin/env python3
"""The act rail fits the margin it paints in, at every tier it paints at.

The seventy-ninth check, and the second whose subject is the act rail.

WHAT WENT WRONG. The rail is a fixed column of marks in the LEFT MARGIN — five
acts and two jumps, held at --space-6 from the viewport's edge. Open, its row is
four columns and 84 px wide, so it ends at 108. The margin it was put in is
--column-inset, which tokens.css derives as max(--gutter, (100% - --container-max)
/ 2) and which is where every container on the page starts its content. The
rail's own gate was --space-6 and 64rem, neither of which knows what
--column-inset is, and below 1536 px --column-inset is smaller than the rail:

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

AND IT COULD NOT BE FIXED BY MOVING THE RAIL, which is why the first version of
this check held a TIER and not the inset. Flush at the viewport's edge the rail
still ends at 84 against a column starting at 56.31, 70.39 and 80 — it overlaps
at every width below 1424 wherever it is put. Collapsing the glyph column does
not save it either: the row's three --space-3 gaps survive the collapse, so it
is still 68 px against a 56 px margin. The rail did not fit below 96rem, so
below 96rem it did not paint, and this check proved the one tier that was left.

WHAT THAT COST, AND WHY THIS CHECK IS NOW TWO ROWS INSTEAD OF ONE. A rail that
does not paint is not a rail. Between 64rem and 96rem the acts still pin, so a
pointer had 18 000 to 23 000 px of scroll and no position indicator at all —
three of the four commonest desktop widths on the ladder, on the flagship page,
with act-rail.js running and marking the current act correctly into an element
at opacity 0. acts.css said so in as many words and left the design open.

The rail that fits a 56 px margin is the wide rail's FIRST COLUMN: the tick
alone, at --space-4 from the edge, with the four idle ticks drawn as --space-1
stubs so the current one has a scale to be long against, and everything else —
numeral, glyph, title, plate — arriving on :hover and :focus-within exactly as
it does above 96rem. Two resting geometries, one per tier:

    tier        inset       resting extent         ends   inset at   clears
    64–96rem    --space-4   --space-4 (the tick)     32     56.31      24.31
    96rem+      --space-6   84 (four columns)       108    128         20

So the invariant this file holds is no longer "the rail is hidden where it does
not fit". It is THE RAIL FITS WHEREVER IT PAINTS, checked once per tier, and
that is strictly the stronger claim: the old shape proved one row of that table
and exempted the other by making it invisible.

WHAT IS CHECKED. acts.css and tokens.css, comments stripped, because this
file's own prose quotes the declarations it is about.

  THE TIERS      every media context in which .act-rail declares --act-cols is
                 a resting geometry, and the narrowest viewport each one
                 governs is a row of the table. The rail's own gate — the
                 min-width query that gives .act-rail `display: grid` — is the
                 floor for a geometry declared outside any width query. Nothing
                 here is restated: add a third tier to acts.css and a third row
                 appears, with no edit to this file.

  THE EXTENT     the rail's width at rest is resolved from its own declarations
                 rather than assumed: --act-cols, .act-rail__link's gap, and
                 the collapsed --act-glyph for any `auto` column, all resolved
                 through tokens.css, with the cascade evaluated AT THAT TIER's
                 floor width. Plus .act-rail's inset-inline-start, same way.
                 Change any of them and the numbers compared move with them.

  THE MARGIN     --column-inset evaluated at each floor width, out of --gutter's
                 own clamp and --container-max, both read from tokens.css.

  THE VERDICT    in every tier, the rail's right edge clears --column-inset by
                 at least --space-4, the rung below the inset the wide rail
                 stands on.

Reintroduce the bug — drop the narrow tier's --act-cols override, widen it, or
push either inset out — and this fails, naming the tier, the width and the two
numbers that no longer clear.

WHAT THIS DOES NOT CLAIM. Not that the rail is reachable — :focus-within lifts
it at every width and check-focus-reach.py holds that. Not that nothing else
may overlap the rail: act 1's field is full-bleed and its callouts are placed on
the drawing rather than in the column, so they can land under the rail at any
width, and one of them does at 1536. That is the field's placement against a
fixed element, not the column's, and it is a different check than this one.

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
CLEARANCE = "--space-4"   # the rung below the inset the wide rail stands on
RAIL = ".act-rail"
ROW = (".act-rail__link", ".act-rail__jump")


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
    """Top-level `name: value` pairs. Splits on the semicolons outside ()."""
    out = {}
    for d in split_semis(body):
        if ":" in d:
            name, value = d.split(":", 1)
            out[name.strip()] = value.strip()
    return out


def split_semis(s):
    parts, depth, cur = [], 0, ""
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == ";" and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return [p.strip() for p in parts if p.strip()]


def rules(css):
    """Every style rule in source order, with the @media preludes enclosing it.

    A brace walker rather than a regex, because acts.css nests @media inside
    @media — the max-width tier that carries the narrow rail lives inside the
    64rem gate — and an innermost-braces pattern cannot see the outer prelude
    it is qualified by.
    """
    out, stack, i, buf = [], [], 0, ""
    while i < len(css):
        ch = css[i]
        if ch == "{":
            head = buf.strip()
            buf = ""
            if head.startswith("@"):
                stack.append(head)
                out.append(None)          # marker: this brace opened an at-rule
            else:
                depth, j = 1, i + 1
                while j < len(css) and depth:
                    if css[j] == "{":
                        depth += 1
                    elif css[j] == "}":
                        depth -= 1
                    j += 1
                out.append((tuple(stack), head, css[i + 1:j - 1]))
                i = j
                continue
        elif ch == "}":
            buf = ""
            # Pop the at-rule this brace closes; style rules never reach here,
            # their bodies were consumed whole above.
            for k in range(len(out) - 1, -1, -1):
                if out[k] is None:
                    del out[k]
                    if stack:
                        stack.pop()
                    break
            else:
                if stack:
                    stack.pop()
        else:
            buf += ch
        i += 1
    return [r for r in out if r]


FEATURE = re.compile(r"\(\s*(min|max)-width\s*:\s*([\d.]+)(rem|px)\s*\)")


def width_matches(prelude, width):
    """Does this @media prelude admit `width`? Non-width features are ignored."""
    for kind, num, unit in FEATURE.findall(prelude):
        edge = float(num) * (ROOT_FONT if unit == "rem" else 1)
        if kind == "min" and width < edge:
            return False
        if kind == "max" and width > edge:
            return False
    return True


def edges(prelude_stack, gate):
    """Every viewport width at which this media context could start governing.

    Its own min-widths, and — because a `max-width` tier SHADOWS the geometry
    declared outside it — the width just past each of its max-widths, which is
    where the shadowed geometry becomes the resting one. 95.999rem is
    "everything below 96rem"; the edge is the next whole pixel up.
    """
    out = {gate}
    for prelude in prelude_stack:
        for kind, num, unit in FEATURE.findall(prelude):
            edge = float(num) * (ROOT_FONT if unit == "rem" else 1)
            if kind == "min":
                out.add(max(edge, gate))
            else:
                past = float(int(edge) + 1) if edge != int(edge) else edge + 1.0
                out.add(max(past, gate))
    return out


def deref(value, scope, depth=8):
    """Follow a whole-value `var(--x)` to what it names. Track lists stay lists."""
    v = value.strip()
    for _ in range(depth):
        m = re.fullmatch(r"var\(\s*(--[\w-]+)\s*\)", v)
        if not m or m.group(1) not in scope:
            return v
        v = scope[m.group(1)].strip()
    raise ValueError(f"{value!r} points at itself")


def resolve(rs, width, targets):
    """The declarations a bare selector in `targets` carries at `width`."""
    out = {}
    for stack, head, body in rs:
        if not all(width_matches(p, width) for p in stack):
            continue
        if not any(s.strip() in targets for s in head.split(",")):
            continue
        out.update(declarations(body))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print every tier, not only the failures")
    args = ap.parse_args()

    tokens = {}
    for name, value in re.findall(r"(--[\w-]+)\s*:\s*([^;{}]+);",
                                  strip_comments(TOKENS.read_text(encoding="utf-8"))):
        tokens.setdefault(name, value.strip())
    for required in ("--gutter", "--container-max", "--space-3", "--space-4", "--space-6"):
        if required not in tokens:
            return fail(f"tokens.css no longer declares {required} — this check "
                        f"reads the rail's margin out of it")

    rs = rules(strip_comments(ACTS.read_text(encoding="utf-8")))

    # ---- the gate: the min-width the rail becomes a grid at ----------------
    gate = None
    for stack, head, body in rs:
        if RAIL not in [s.strip() for s in head.split(",")]:
            continue
        if not re.search(r"display\s*:\s*grid", body):
            continue
        here = None
        for prelude in stack:
            for kind, num, unit in FEATURE.findall(prelude):
                if kind == "min":
                    e = float(num) * (ROOT_FONT if unit == "rem" else 1)
                    here = e if here is None else max(here, e)
        if here is not None:
            gate = here if gate is None else min(gate, here)
    if gate is None:
        return fail("no min-width media query in acts.css lays .act-rail out as "
                    "a grid, so this check cannot tell which viewports the rail "
                    "exists at — and a rail that exists at every width is one "
                    "that stands in a margin the phone does not have")

    # ---- the tiers: one per resting geometry -------------------------------
    tiers = []
    for stack, head, body in rs:
        if RAIL not in [s.strip() for s in head.split(",")]:
            continue
        if "--act-cols" not in declarations(body):
            continue
        for low in edges(stack, gate):
            if low not in tiers:
                tiers.append(low)
    if not tiers:
        return fail("no rule in acts.css declares --act-cols on .act-rail, so "
                    "the rail's resting width is typed into .act-rail__link's "
                    "grid-template-columns and cannot be resolved per tier. The "
                    "rail has two resting geometries — see the table above — and "
                    "a check that can only see one of them proves the wrong one.")

    rows, worst = [], 0
    for low in sorted(tiers):
        decls = resolve(rs, low, {RAIL})
        row = resolve(rs, low, set(ROW))
        # The rail publishes properties of its own — --act-glyph, --act-cols and
        # the open geometry --act-cols points back at — so a name resolved here
        # may live on .act-rail rather than in tokens.css. The rail's own
        # declarations shadow the tokens for the length of this tier.
        scope = dict(tokens)
        scope.update({k: v for k, v in decls.items() if k.startswith("--")})
        try:
            inset = px(decls["inset-inline-start"], scope)
            glyph = px(decls["--act-glyph"], scope)
            gap = px(row["gap"], scope)
            cols = deref(decls["--act-cols"], scope).split()
        except (KeyError, ValueError) as exc:
            return fail(f"cannot read the rail's own geometry out of acts.css at "
                        f"{low:.0f} px ({exc}); this check sizes the rail from its "
                        f"declarations rather than from a number typed here")

        # the last column is the collapsed title: `auto` over a clipped label,
        # which measures 0 at rest. Any other `auto` is the glyph.
        widths = [glyph if c == "auto" else px(c, scope) for c in cols]
        if len(widths) > 1:
            widths[-1] = 0.0
        extent = sum(widths) + gap * (len(widths) - 1)
        right = inset + extent

        column_inset = px(tokens["--column-inset"], tokens, low) if "--column-inset" in tokens \
            else max(px(tokens["--gutter"], tokens, low),
                     (low - px(tokens["--container-max"], tokens)) / 2)
        clearance = px(tokens[CLEARANCE], tokens)
        have = column_inset - right
        rows.append((low, len(widths), inset, extent, right, column_inset, have))
        if have < clearance:
            return fail(
                f"the rail paints at rest from {low:.0f} px up in {len(widths)} "
                f"column{'s' if len(widths) != 1 else ''}, where the content "
                f"column starts at {column_inset:.2f} px and the rail ends at "
                f"{right:.0f} ({inset:.0f} inset + {extent:.0f} wide). That leaves "
                f"{have:.2f} px between them, short of the {clearance:.0f} px "
                f"({CLEARANCE}) this asks for, so the rail's marks are painted "
                f"inside the acts' own text column. Either narrow that tier's "
                f"--act-cols or drop its inset a rung — moving the rail left does "
                f"not work on its own, see the note in acts.css.")
        worst = have if not worst else min(worst, have)

    if args.verbose:
        print("  tier      cols  inset  extent  ends  --column-inset  clears")
        for low, n, inset, extent, right, ci, have in rows:
            print(f"  {low:>6.0f}    {n:>3}   {inset:>4.0f}  {extent:>6.0f}  "
                  f"{right:>4.0f}  {ci:>13.2f}  {have:>6.2f}")
    print(f"OK  the act rail fits its margin in all {len(rows)} tier"
          f"{'s' if len(rows) != 1 else ''} it paints at — from "
          + ", ".join(f"{low:.0f} px in {n} column{'s' if n != 1 else ''} "
                      f"({have:.2f} px clear)" for low, n, _, _, _, _, have in rows)
          + f" — every one past the {px(tokens[CLEARANCE], tokens):.0f} px floor")
    return 0


if __name__ == "__main__":
    sys.exit(main())
