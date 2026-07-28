#!/usr/bin/env python3
"""The drawing's foot is the lectern's rail, and one of the words that says so
is `stretch`.

The sixtieth check, and it closes the axis check-flow-handover.py names in its
own docstring as the one it cannot see:

    WHAT THIS CHECK CANNOT SEE, stated here so it is not mistaken for covered.
    The seam has two axes and this check holds one of them. The VERTICAL join --
    the flow's box bottom against the frame's top rail -- is not countable in
    any file, because it is the sum of the statement figure's height, the
    section rule below it, the pin section's padding and the stage's own
    centring [...]

That was true of the FALLBACK, and it is the reason the .lp-flow note carries a
nine-row table of the gap instead of a rule. It stopped being true at #207,
which bound the box between the void and the rail and drove every row of that
table to 0.00. The join is no longer a sum of four layout terms nobody can
name -- it is four declarations in one file, and this is the check that reads
them.

WHAT IS ACTUALLY HOLDING THE SEAM SHUT. Measured on the shipped page by making
each edit and reloading, frame top minus flow bottom, before the pin engages:

                                     1440x900   1920x1080  1280x900  2560x1440
    shipped                             +0.00       +0.00     +0.00      +0.00
    `align-self: stretch` deleted        1.58      171.58     58.17     351.58
    `bottom` anchored to the void      438.91      608.91    447.41     788.91
    `.lp-flow-data` unregistered         0.00        0.00      0.00       0.00
       -- but its eight numerals slide -222.42 / -52.42 / -141.19 / +127.58 px
          off the strokes they are drawn to label

ALL SIXTY CHECKS THEN IN THE TREE PASSED ON EVERY ONE OF THOSE STATES. The middle row is the
sharpest: `bottom: anchor(--lp-void-box bottom)` is a live anchor, declared on a
real element, guarded by the same @supports, resolving perfectly --
check-anchor-positioning.py proves a name resolves, not that it resolves to the
RAIL -- and it puts the foot of the drawing 788.91 px above the line sixteen
terminals are drawn to arrive on.

WHY `stretch` IS THE LOAD-BEARING WORD AND LOOKS LIKE HOUSEKEEPING. An
absolutely positioned REPLACED element with both block insets set and
`height: auto` does not stretch to fill them: it takes its intrinsic height and
drops the bottom inset. An <svg> is replaced. So `bottom: anchor(--lp-rail-box
top)` on its own is a declaration the layout is free to ignore, and it does --
the box falls back to 661.33 px, the ratio's height, at every viewport, and the
whole #207 table comes back. The page's own note records this ("Measured:
without it the box stayed at 662.91 px at 1440 x 900 and the gap was the old
1.58"); nothing read the note.

`block-size: auto` is in the same rule and is NOT asserted here, because it was
measured and it is inert: deleting it moves nothing at any of the four
viewports, `aspect-ratio: auto` having already released the height. A check
that asserted it would be stating a reason that is not the reason.

THE RULE, per page carrying both drawings:

  1. THE RAIL IS NAMEABLE. .lp-frame declares an `anchor-name`. Without it there
     is nothing for the foot to be anchored TO, and the fallback tier -- a real
     rendering, the one every browser without anchor positioning gets -- is all
     there is.

  2. THE FOOT IS THE RAIL, BY NAME. .lp-flow's `bottom` is `anchor(N top)` where
     N is the name .lp-frame declares. Not any anchor: that one. This is the
     link check-anchor-positioning.py is one level too general to make.

  3. THE BOX ACTUALLY STRETCHES. The same rule declares `align-self: stretch`.
     See above for why this is not tidying.

  4. THE NUMERALS TAKE THE SAME FOOT. .lp-flow-data is a sibling of the drawing
     carrying the eight values, placed by percentages of ITS box against the
     drawing's 620 units, so it registers on the drawing only if it takes the
     rail for its foot too -- `top: auto` and the same `bottom` anchor. A value
     labels the stroke it stands on, which is the sentence #200 was opened for.

  5. ALL OF IT UNDER ONE GUARD. Every declaration above sits inside the
     @supports that tests BOTH halves of anchor positioning, so the fallback is
     a deliberate second rendering and not something that happened.

The check reads the page's own <style>, not the browser, for the reason every
check at this seam does: the last five breaks here were all CSS-side and the
geometry never moved for any of them.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-seam-anchor.py
    python3 scripts/check-seam-anchor.py -v
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = ROOT / "design-system" / "patterns"
# The statement-to-process chain moved to prototypes/ on 2026-07-28;
# these checks follow the drawing, not the folder.
PROTOTYPES = ROOT / "design-system" / "prototypes"

STYLE_RE = re.compile(r"<style\b[^>]*>(.*?)</style>", re.S)
COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
NAME = r"--[A-Za-z0-9_-]+"
ANCHOR_RE = re.compile(rf"\banchor\(\s*({NAME})\s+([a-z]+)\s*\)")

# The drawing whose foot is a rail, and the element that draws the rail.
FLOW = "lp-flow"
DATA = "lp-flow-data"
RAIL = "lp-frame"


def rules(css):
    """(at-rule stack, selector, declaration block) for every rule, nested or not.

    The at-rule stack is what this check is about — finding 5 is entirely a
    question of WHICH block a declaration sits in — so unlike the walker in
    check-shared-measure.py this one keeps the @-heads rather than dropping
    them."""
    css = COMMENT_RE.sub(" ", css)
    out, buf, stack = [], "", []
    for c in css:
        if c == "{":
            stack.append(buf.strip())
            buf = ""
        elif c == "}":
            head = stack.pop() if stack else ""
            if not head.startswith("@"):
                out.append(([h for h in stack if h.startswith("@")], head, buf))
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


def selects(selector, cls):
    """The selector names .cls as one of its comma-separated parts."""
    return any(re.search(rf"\.{re.escape(cls)}(?![\w-])", part)
               for part in selector.split(","))


def guarded(at_stack):
    """Inside an @supports testing both halves of anchor positioning — a name
    and a use. Testing only one is the trap check-anchor-positioning.py's own
    note records: Chromium shipped `anchor-name` parsing before `anchor()`
    resolution, so a one-sided query lets a rule in that cannot work."""
    for at in at_stack:
        if not at.startswith("@supports"):
            continue
        if "anchor-name" in at and re.search(r"anchor\(", at):
            return True
    return False


def check_page(page, verbose):
    text = page.read_text(encoding="utf-8")
    if f'class="{FLOW}"' not in text or f'class="{RAIL}"' not in text:
        return [], False

    page_rules = []
    for block in STYLE_RE.findall(text):
        page_rules += rules(block)

    findings = []

    def decls_for(cls, prop):
        return [(at, sel, val) for at, sel, block in page_rules
                if selects(sel, cls)
                for p, val in declarations(block) if p == prop]

    # 1. THE RAIL IS NAMEABLE.
    rail_names = decls_for(RAIL, "anchor-name")
    rail_name = None
    for at, sel, val in rail_names:
        if val != "none":
            rail_name = val
            break
    if rail_name is None:
        findings.append(
            f"{page.name}: .{RAIL} declares no anchor-name, so nothing on the page "
            f"can be positioned against the rail. The drawing's sixteen terminals "
            f"then keep whatever gap the fallback leaves — up to 351.58 px at "
            f"2560 x 1440 — and every other check still passes.")
        return findings, True

    # 2. THE FOOT IS THE RAIL, BY NAME.
    bottoms = decls_for(FLOW, "bottom")
    if not bottoms:
        findings.append(
            f"{page.name}: .{FLOW} never declares `bottom`, so the foot of the "
            f"drawing is wherever its own height leaves it and the seam is the "
            f"nine-row table in the page's own note again, not 0.00.")
    for at, sel, val in bottoms:
        m = ANCHOR_RE.search(val)
        if not m:
            findings.append(
                f"{page.name}: .{FLOW} sets `bottom: {val}` under {sel.strip()!r}, "
                f"which is not an anchor on the rail. The foot of the drawing has "
                f"to BE the rail; a length here is the seam being tuned at one "
                f"viewport, which is the state #207 found and measured.")
            continue
        used, side = m.group(1), m.group(2)
        if used != rail_name or side != "top":
            findings.append(
                f"{page.name}: .{FLOW} sets `bottom: anchor({used} {side})`, but the "
                f"rail is `{rail_name}` and the edge the drops land on is its top. "
                f"A live anchor to the wrong box resolves perfectly and still puts "
                f"the foot 788.91 px off the rail at 2560 x 1440 — measured, with "
                f"every other check green.")
        if not guarded(at):
            findings.append(
                f"{page.name}: .{FLOW}'s rail anchor is not inside an @supports "
                f"testing both an anchor-name and an anchor() use, so the tier that "
                f"cannot resolve it gets this rule anyway.")

    # 3. THE BOX ACTUALLY STRETCHES.
    #    Only the rule that carries the rail anchor can be asked for it: that is
    #    the box being over-constrained, and `stretch` is what resolves it.
    anchored_blocks = [(at, sel, block) for at, sel, block in page_rules
                       if selects(sel, FLOW)
                       for p, v in declarations(block)
                       if p == "bottom" and ANCHOR_RE.search(v)]
    for at, sel, block in anchored_blocks:
        aligns = [v for p, v in declarations(block) if p == "align-self"]
        if "stretch" not in aligns:
            findings.append(
                f"{page.name}: .{FLOW} anchors its `bottom` to the rail under "
                f"{sel.strip()!r} without `align-self: stretch`. An <svg> is a "
                f"REPLACED element, and an absolutely positioned replaced box with "
                f"both block insets set and an auto height does not stretch — it "
                f"takes its intrinsic height and drops the bottom inset. Measured "
                f"on exactly that state: the box holds at 661.33 px and the seam "
                f"reopens to 1.58 px at 1440 x 900, 58.17 at 1280 x 900, 171.58 at "
                f"1920 x 1080 and 351.58 at 2560 x 1440, with every check then in "
                f"the tree passing. Two words, sixteen free ends.")

    # 4. THE NUMERALS TAKE THE SAME FOOT.
    if f'class="{DATA}"' in text:
        data_bottoms = decls_for(DATA, "bottom")
        data_tops = decls_for(DATA, "top")
        landed = [v for _, _, v in data_bottoms
                  if (m := ANCHOR_RE.search(v)) and m.group(1) == rail_name
                  and m.group(2) == "top"]
        if not landed:
            findings.append(
                f"{page.name}: .{DATA} does not take the rail for its foot. Its "
                f"eight values are placed as percentages of its own box against "
                f"the drawing's 620 units, so a box that ends anywhere else slides "
                f"every numeral off the stroke it labels — measured at -222.42 px "
                f"at 1440 x 900 and +127.58 at 2560 x 1440, with the seam itself "
                f"still reading 0.00 and nothing else complaining.")
        elif not any(v == "auto" for _, _, v in data_tops):
            findings.append(
                f"{page.name}: .{DATA} anchors its foot to the rail but never "
                f"releases `top`. Bound at both ends it stretches with the drawing "
                f"and the percentages stop meaning the drawing's own units, which "
                f"is the trap the page's note on this rule works through.")

    if verbose:
        aligns = [v for _, _, b in anchored_blocks
                  for p, v in declarations(b) if p == "align-self"]
        print(f"  {page.name}: rail is {rail_name}; "
              f".{FLOW} bottom {[v for _, _, v in bottoms]}; "
              f"{len(anchored_blocks)} anchored rule(s), align-self {aligns}")

    return findings, True


def main():
    parser = argparse.ArgumentParser(
        description="The drawing's foot is the lectern's rail, by name.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="print the anchor chain each page declares")
    args = parser.parse_args()

    findings, pages = [], 0
    for page in sorted([*PATTERNS.glob("*.html"), *PROTOTYPES.glob("*.html")]):
        f, seen = check_page(page, args.verbose)
        findings += f
        pages += 1 if seen else 0

    if not pages:
        print("seam anchor: no page carries both drawings — the selector went stale")
        return 1
    if findings:
        print(f"\nseam anchor: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1
    print(f"seam anchor OK — on {pages} page(s) the drawing's foot is the rail by "
          f"name, the box is told to stretch to it, and the numerals take the same "
          f"foot, all under one guard")
    return 0


if __name__ == "__main__":
    sys.exit(main())
