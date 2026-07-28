#!/usr/bin/env python3
"""A drawing whose ink sits on its viewBox edge has to be FITTED to that edge.

The fifty-ninth, and it is the layer under #204 and #207 rather than a new
subject. check-shared-measure.py holds the WIDTH chain the seam rests on;
check-flow-stem.py holds the trunk that closed it. Both of those, and both of
the seam checks under them, are statements about USER units. This holds the one
transform standing between those units and the page: how the viewBox is fitted
into the box CSS gives it.

WHAT THE SEAM CHECKS ASSUME. check-flow-terminals.py proves every terminal of
.lp-flow ends at user y 620, the foot of its own viewBox, and two of them at
user x 0 and x 1200, its left and right extremes. check-flow-handover.py maps a
flow x onto a frame x by the pure ratio 1000/1200 and proves all fourteen drops
land inside the lectern's top rail. Every one of those is a claim about where
the ink is IN THE DRAWING. Whether the drawing's foot is the box's foot is
`preserveAspectRatio`, and no check has ever read it.

IT IS NOT A HYPOTHETICAL, because this drawing has now been through both of the
answers to it. Until #207 .lp-flow declared no preserveAspectRatio at all, took
the initial `xMidYMid meet`, and was correct only because `aspect-ratio:
1200 / 620` on its box made `meet` the identity — a fact stated in prose in two
files ("the ratio is what keeps the taproots on the corners, since the default
preserveAspectRatio would otherwise letterbox the drawing inside its own box";
"the ratio is what makes the x arrivals exact") and read by nothing. Measured on
that state at 1440 x 900 before the pin, by moving that one declaration and
nothing else:

    aspect-ratio     box h    ink foot   ink off the    worst terminal to the
                                         box's foot     rail it arrives on

    1200 / 620       661.33    1767.27      0.00 px          1.57 px   shipped
    1200 / 680       725.33    1799.27     32.00 px         30.43 px
    1200 / 560       597.33    1703.27      0.00 px         65.57 px

At 1200/680 the fit stays width-limited, so x survives and the whole drawing
lifts 32.00 px off the foot of a box that by then overhangs the lectern by
62.43 px: fourteen strokes stopping 30 px above the rail. At 1200/560 the fit
turns HEIGHT-limited and the damage moves to the axis handover exists for — the
drawing shrinks about its own centre and the two corner taproots land 61.95 px
inside the verticals they are drawn onto (page x 1298.04 against the vertical at
1360.00), while the centre drop, being centred, does not move at all and hides
it. All fifty-five checks of the day passed on both.

#207 then bound the box between the void and the rail, which RELEASES the ratio
on purpose — `aspect-ratio: auto`, `align-self: stretch` — and pins the foot the
other way instead, with `preserveAspectRatio="xMidYMax meet"`. That is a second
correct answer and not a weaker one: the box is now taller than the ratio at
every viewport, so the fit is width-limited, x stays exact, and YMax puts the
drawing's own foot on the box's foot, which is the rail. Both answers are right.
The default sitting between them is not, and the default is what you get by
deleting five characters.

THE RULE, per drawing, from the edges its geometry is asserted against:

  1. preserveAspectRatio IS DECLARED. Never defaulted. A drawing whose ink sits
     on its viewBox extremes may not inherit `xMidYMid meet` from the initial
     value — that is the one fit that leaves slack on both axes and centres the
     drawing in it, and it is the state both of the failures above are.

  2. THE ALIGNMENT PINS THE EDGE THE INK IS ON. .lp-flow's sixteen terminals are
     on the foot, so the Y keyword must be YMax: with slack on the y axis, YMid
     leaves them half of it short and YMin all of it. `none` pins every edge by
     stretching and needs no keyword.

  3. A DECLARED RATIO IS THE VIEWBOX'S. Where a rule declares `aspect-ratio:
     W / H` for the box, W/H must equal the viewBox's exactly, or the fit can
     turn height-limited and x — the axis fourteen arrivals sit on and no
     alignment keyword can rescue — shrinks about the centre. `auto` is exempt
     and is not an oversight: it is #207 releasing the height deliberately,
     having pinned the foot under rule 2.

.lp-frame answers all three at once with preserveAspectRatio="none": its contour
IS the four viewBox extremes and its box is the plate, which is not 2:1, so only
a stretch puts all four edges on the border box they replaced. Take the
attribute off and the lectern letterboxes inside the plate — the mirror of this
finding, so the branch is checked rather than assumed.

The check reads the markup and the page's own <style>, not the generator, for
the reason every check at this seam does: the last four breaks here were all
CSS-side (#177 the stage narrowing, #178 the frame inside its border, #202 and
#204 the measure chain) and the geometry never moved for any of them.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-flow-ratio.py
    python3 scripts/check-flow-ratio.py -v
"""

import argparse
import re
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = ROOT / "design-system" / "patterns"
# The statement-to-process chain moved to prototypes/ on 2026-07-28;
# these checks follow the drawing, not the folder.
PROTOTYPES = ROOT / "design-system" / "prototypes"

STYLE_RE = re.compile(r"<style\b[^>]*>(.*?)</style>", re.S)
COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
SVG_RE = re.compile(r"<svg\b([^>]*)>", re.S)
ATTR_RE = re.compile(r'([\w:-]+)\s*=\s*"([^"]*)"')
RATIO_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)\s*$")
ALIGN_RE = re.compile(r"^(xMin|xMid|xMax)(YMin|YMid|YMax)$")

# class -> (the viewBox edge its terminals are asserted against, why)
#
# "YMax" means the ink is on the foot, so the fit must put the viewBox's bottom
# on the box's bottom. None means every edge is asserted and only `none` serves.
DRAWINGS = {
    "lp-flow": ("YMax",
                "its sixteen terminals all end at user y 620, the foot of its "
                "own viewBox — check-flow-terminals.py"),
    "lp-frame": (None,
                 "its six hairlines ARE the four viewBox extremes, and its box "
                 "is the plate, which is not 2:1 — check-flow-handover.py"),
}


def strip_comments(css):
    return COMMENT_RE.sub(" ", css)


def rules(css):
    """(selector, declaration-block) for every rule, at any nesting depth.

    The same walker check-shared-measure.py uses, and written rather than
    imported for the same reason: a regex cannot tell a declaration inside
    @media from one beside it, and .lp-flow's two answers to rule 3 live in
    two different @supports blocks."""
    css = strip_comments(css)
    out, buf, stack = [], "", []
    for c in css:
        if c == "{":
            stack.append(buf.strip())
            buf = ""
        elif c == "}":
            head = stack.pop() if stack else ""
            if not head.startswith("@"):
                out.append((head, buf))
            buf = ""
        else:
            buf += c
    return out


def declarations(block):
    for decl in block.split(";"):
        if ":" not in decl:
            continue
        prop, _, value = decl.partition(":")
        yield prop.strip(), " ".join(value.split())


def selects(selector, needle):
    return any(needle in part.split(":")[0] for part in selector.split(","))


def parse_ratio(value):
    """`W / H` as an exact Fraction. `auto` and anything with a var() in it come
    back None and are handled by the caller, which treats them differently."""
    m = RATIO_RE.match(value)
    if m:
        return (Fraction(m.group(1)).limit_denominator(10 ** 6) /
                Fraction(m.group(2)).limit_denominator(10 ** 6))
    if re.match(r"^\s*\d+(\.\d+)?\s*$", value):
        return Fraction(value.strip()).limit_denominator(10 ** 6)
    return None


def show(f):
    return f"{f.numerator}/{f.denominator}"


def check_page(page, verbose):
    text = page.read_text(encoding="utf-8")

    page_rules = []
    for block in STYLE_RE.findall(text):
        page_rules += rules(block)

    findings, seen = [], 0
    for attrs_text in SVG_RE.findall(text):
        attrs = dict(ATTR_RE.findall(attrs_text))
        classes = attrs.get("class", "").split()
        for cls, (needs_align, why) in DRAWINGS.items():
            if cls not in classes:
                continue
            seen += 1
            view_box = attrs.get("viewBox")
            if not view_box or len(view_box.split()) != 4:
                findings.append(
                    f"{page.name}: .{cls} carries no readable viewBox "
                    f"({view_box!r}) — the fit this check is about is undefined")
                continue
            _, _, vw, vh = view_box.split()
            vb_ratio = (Fraction(vw).limit_denominator(10 ** 6) /
                        Fraction(vh).limit_denominator(10 ** 6))
            raw = attrs.get("preserveAspectRatio")
            par = " ".join(raw.split()) if raw is not None else None

            # ---- rule 1: declared, never defaulted -----------------------
            if par is None:
                findings.append(
                    f"{page.name}: .{cls} declares no preserveAspectRatio, so it takes "
                    f"the initial `xMidYMid meet` — the one fit that leaves slack on "
                    f"both axes and CENTRES the drawing in it. {why[0].upper()}{why[1:]}, "
                    f"so the fit has to pin those edges rather than centre between them.")
                continue

            words = par.split()
            align = words[0] if words else ""
            meet_or_slice = words[1] if len(words) > 1 else "meet"

            # `none` stretches the viewBox onto the box, so every extreme is a
            # box edge whatever the box's shape. It answers all three rules at
            # once and is the only fit that can, which is why the frame takes it.
            if align == "none":
                if verbose:
                    print(f'  {page.name} .{cls}: viewBox {vw} x {vh}, '
                          f'preserveAspectRatio="none" — the viewBox is stretched '
                          f"onto the box, so every extreme is a box edge at any "
                          f"box size")
                continue

            # ---- rule 2: the alignment pins the asserted edge -------------
            if needs_align is None:
                findings.append(
                    f'{page.name}: .{cls} carries preserveAspectRatio="{par}", and '
                    f"{why}. All four extremes are asserted at once, and a uniform fit "
                    f'can pin at most two of them — only "none" stretches a viewBox onto '
                    f"its box.")
                continue

            m = ALIGN_RE.match(align)
            if not m:
                findings.append(
                    f'{page.name}: .{cls} carries preserveAspectRatio="{par}", whose '
                    f"alignment {align!r} is not one of the nine keywords — this check "
                    f"cannot tell which edge it pins, and neither can a reader.")
                continue
            if meet_or_slice == "slice":
                findings.append(
                    f'{page.name}: .{cls} is fitted `{par}`. `slice` scales to COVER, so '
                    f"the box crops the drawing on the axis it overflows — and {why}, "
                    f"which is ink `slice` is free to cut off.")
                continue
            if m.group(2) != needs_align:
                findings.append(
                    f'{page.name}: .{cls} is fitted `{par}`, and {why}. Under `meet` the '
                    f"drawing is scaled by min(boxW/{vw}, boxH/{vh}); whatever slack that "
                    f"leaves on the y axis, {m.group(2)} puts "
                    f"{'half of it' if m.group(2) == 'YMid' else 'all of it'} between the "
                    f"ink and the edge it is drawn to arrive on. It has to be "
                    f"{needs_align}.")
                continue

            # ---- rule 3: a declared ratio is the viewBox's ----------------
            declared = [(sel, val) for sel, block in page_rules
                        for prop, val in declarations(block)
                        if prop == "aspect-ratio" and selects(sel, f".{cls}")]
            for sel, val in declared:
                if val.strip() == "auto":
                    if verbose:
                        print(f"  {page.name} .{cls}: `aspect-ratio: auto` under "
                              f"{sel.strip()!r} — height released deliberately; the foot "
                              f"is pinned by {needs_align} instead")
                    continue
                ratio = parse_ratio(val)
                if ratio is None:
                    findings.append(
                        f"{page.name}: .{cls} declares `aspect-ratio: {val}` under "
                        f"{sel.strip()!r}, which this check cannot read as an exact "
                        f"ratio. It has to equal the viewBox's {show(vb_ratio)} or the "
                        f"fit can turn height-limited; write it as two numbers.")
                elif ratio != vb_ratio:
                    findings.append(
                        f"{page.name}: .{cls} has a {vw} x {vh} viewBox ({show(vb_ratio)}) "
                        f"and its box declares `aspect-ratio: {val}` ({show(ratio)}) under "
                        f"{sel.strip()!r}. A box SHORTER than its viewBox's ratio makes "
                        f"`meet` height-limited: the drawing shrinks about its own centre "
                        f"and the x arrivals move, which no alignment keyword rescues and "
                        f"check-flow-handover.py cannot see, being written in user units.")
                elif verbose:
                    print(f"  {page.name} .{cls}: `aspect-ratio: {val}` under "
                          f"{sel.strip()!r} = the viewBox's {show(vb_ratio)}")

            if verbose:
                print(f'  {page.name} .{cls}: viewBox {vw} x {vh}, fitted `{par}` — '
                      f"{needs_align} pins the foot the terminals are on, "
                      f"{len(declared)} aspect-ratio declaration(s) read")

    return findings, seen


def main():
    parser = argparse.ArgumentParser(
        description="A drawing whose ink sits on its viewBox edge has to be fitted "
                    "to that edge.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="print each drawing's viewBox, fit and declared ratios")
    args = parser.parse_args()

    findings, seen = [], 0
    for page in sorted([*PATTERNS.glob("*.html"), *PROTOTYPES.glob("*.html")]):
        f, n = check_page(page, args.verbose)
        findings += f
        seen += n

    if not seen:
        print("flow ratio: no drawing to check — the selector went stale")
        return 1
    if findings:
        print(f"\nflow ratio: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1
    print(f"flow ratio OK — {seen} drawing(s), each fitted so the viewBox edges its "
          f"ink sits on are the box edges: stretched, or aligned to the edge the "
          f"terminals arrive on with no ratio contradicting it")
    return 0


if __name__ == "__main__":
    sys.exit(main())
