#!/usr/bin/env python3
"""Act 1+2's base tier is a page, not a stage.

acts.css is written in two tiers, and its own header says the order is
load-bearing: the base tier first, the gated tier second, so that at equal
specificity source order hands the gated tier the win. What the header does not
say — and what cost this page its whole mobile reading of act 2 — is that a
declaration authored in the base tier is a declaration the base tier SHIPS.

WHAT WENT WRONG. The copy either side of the confluence is two blocks of prose,
a bold lead and a forty-word paragraph each. Inside the pinned stage they are an
overlay: `position: absolute`, 35 % wide, centred on 74 % of a drawing that has
been fitted to the viewport and is 471 px tall. That placement was authored in
the base tier and nothing ever took it back, so every tier that does not pin got
it too — over a drawing that is whatever the flow makes it. Measured on the
shipped landing page, act 1+2's stage:

    375 x 812     .sp-root 334 x 172     column 117 wide, 74 % = 127
    768 x 900     .sp-root 684 x 353     column 239 wide, 74 % = 261
   1023 x 900     .sp-root 527 x 272     column 184 wide, 74 % = 201
   1280 x 900     .sp-root 1109 x 573    reduced motion, the same tier

220 px of reserved copy inside a 172 px box, on top of a drawing carrying
eighteen numerals of its own, all three layers sharing one top edge. Counting
label-rect against prose-rect intersections over seven scroll positions, 375 px
wide: 24 collisions. It is not a crop and not a near miss — four things in one
place, none of them readable — and it was live for every viewport under 64rem,
every viewport under 45rem tall, every reader with prefers-reduced-motion set,
and every browser without animation-timeline.

Nothing caught it because every check on this stage reads the tier that pins.
check-pin-measure.py, check-scroll-reserve.py, check-iso-motion.py and the rest
all resolve windows and ranges inside the @supports block, which is exactly the
tier that was correct. A screenshot of the enhanced tier is clean, and the
degraded tiers are the ones nobody opens.

WHAT IS CHECKED, off acts.css with comments stripped and the act-1+2 @supports
block located by brace count:

  TIER SPLIT   `position: absolute` for .sp-say and .sp-say__col appears in the
               gated region and NOT in the base region. That is the whole
               sentence: the overlay is the pinned stage's, and a tier that does
               not pin gets flow.

  THE NUMERAL LAYER IS THE DRAWING'S BOX   .lp-flow-data carries the drawing's
               own aspect-ratio and does not take a four-sided `inset: 0`. Every
               numeral is placed at a percentage of this box — left is --x/1200,
               top is --y/620 — so a box that grows with anything below the
               drawing drags all eighteen down it. `inset: 0` of .sp-root was
               only ever true while the drawing was the last child.

  THE RATIO IS THE VIEWBOX'S   the ratio in that declaration equals the drawing's
               own viewBox on both consumer pages. Stated rather than assumed:
               if the drawing is ever redrawn on a different basis, the layer
               that labels it moves with it or this fails.

WHAT THIS DOES NOT CLAIM. Not the flow layout the base tier now has — one column
or two, and at which measure, is a decision. Not the 74 % or the 35 % in the
gated tier. Not that the two tiers look alike; they should not.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-fallback-tier.py
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ACTS = ROOT / "design-system/assets/css/acts.css"
# acts.css has one lab and one shipped consumer, and the drawing is in both.
PAGES = [ROOT / "design-system/patterns/landing-page.html",
         ROOT / "design-system/prototypes/statement-to-process.html"]

# The gate the acts' choreography is behind. The first occurrence in the file is
# acts 1 and 2; the second is act 5's own.
GATE = "@supports (animation-timeline: view())"

# The overlay's two selectors, and the property that makes it an overlay.
OVERLAY = (".sp-say", ".sp-say__col")


def fail(msg):
    print(f"FAIL  {msg}")
    return 1


def strip_comments(css):
    """Comments in this file quote CSS at length — including the declarations
    this script looks for. Blanked rather than removed so nothing else shifts."""
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def split_at_gate(css):
    """(base, gated) — everything before the acts' @supports block, and the
    block itself, found by counting braces from its opening one."""
    i = css.find(GATE)
    if i < 0:
        return None, None
    j = css.find("{", i)
    depth = 0
    for k in range(j, len(css)):
        if css[k] == "{":
            depth += 1
        elif css[k] == "}":
            depth -= 1
            if depth == 0:
                return css[:i], css[j:k + 1]
    return None, None


def declares(region, selector, prop, value=None):
    """Does `selector` carry `prop` (at `value`) anywhere in this region?
    Matches the selector as a whole term in a prelude, so .sp-say does not
    answer for .sp-say__col."""
    hits = []
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", region):
        prelude, body = m.group(1), m.group(2)
        terms = [t.strip() for t in prelude.split(",")]
        if not any(t == selector or t.startswith(selector + ":") for t in terms):
            continue
        for d in body.split(";"):
            if ":" not in d:
                continue
            p, v = d.split(":", 1)
            if p.strip() != prop:
                continue
            if value is None or v.strip() == value:
                hits.append(v.strip())
    return hits


def viewbox_ratio(page):
    m = re.search(r'<svg class="lp-flow" viewBox="0 0 (\d+) (\d+)"', page.read_text(encoding="utf-8"))
    return (int(m.group(1)), int(m.group(2))) if m else None


def main():
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()
    css = strip_comments(ACTS.read_text(encoding="utf-8"))
    base, gated = split_at_gate(css)
    if base is None:
        return fail(f"acts.css has no `{GATE}` block — the tier split this "
                    f"check is about does not exist any more")
    bad = 0

    # ---- the tier split ----
    for sel in OVERLAY:
        in_base = declares(base, sel, "position", "absolute")
        in_gate = declares(gated, sel, "position", "absolute")
        if in_base:
            bad |= fail(f"{sel} is `position: absolute` in the BASE tier of "
                        f"acts.css. That is the pinned stage's overlay, and the "
                        f"base tier is read at every viewport under 64rem, under "
                        f"45rem tall, under prefers-reduced-motion, and in every "
                        f"browser without animation-timeline — where the drawing "
                        f"is 172 px tall at 375 and the copy is 220. Flow there.")
        if not in_gate:
            bad |= fail(f"{sel} is never `position: absolute` inside `{GATE}`, "
                        f"so the pinned stage has lost its overlay: the copy "
                        f"would stand under the drawing on the one tier whose "
                        f"whole composition is the two blocks either side of the "
                        f"confluence.")

    # ---- the numeral layer is the drawing's box ----
    ratios = declares(base, ".lp-flow-data", "aspect-ratio")
    insets = declares(base, ".lp-flow-data", "inset")
    if not ratios:
        bad |= fail(".lp-flow-data declares no aspect-ratio. Every numeral on "
                    "the root is placed at a percentage of this layer — left is "
                    "--x/1200, top is --y/620 — so the layer has to be the "
                    "drawing's box and not whatever .sp-root grows to.")
    for v in insets:
        sides = v.split()
        if len(sides) == 1 or (len(sides) == 4 and sides[2] != "auto") or \
           (len(sides) == 2) or (len(sides) == 3 and sides[2] != "auto"):
            bad |= fail(f".lp-flow-data takes `inset: {v}`, which gives it a "
                        f"bottom edge and lets .sp-root's height decide where "
                        f"the eighteen numerals sit. The block edge belongs to "
                        f"the ratio; leave the bottom `auto`.")

    # ---- the ratio is the viewBox's ----
    if ratios:
        m = re.match(r"(\d+)\s*/\s*(\d+)$", ratios[0])
        if not m:
            bad |= fail(f".lp-flow-data's aspect-ratio is `{ratios[0]}` and this "
                        f"check reads a plain w / h — state it as the drawing's "
                        f"viewBox so the two can be compared.")
        else:
            want = (int(m.group(1)), int(m.group(2)))
            for page in PAGES:
                got = viewbox_ratio(page)
                if got is None:
                    bad |= fail(f"{page.name} carries no <svg class=\"lp-flow\" "
                                f"viewBox=…> — the register is stale")
                elif got != want:
                    bad |= fail(f"{page.name}'s drawing is viewBox {got[0]} x "
                                f"{got[1]} and .lp-flow-data's box is "
                                f"{want[0]} / {want[1]}. The layer that labels "
                                f"the drawing is no longer the drawing's box, "
                                f"so every numeral is placed off a height the "
                                f"figure does not have.")
    if bad:
        return 1

    print(f"OK  acts 1+2 in two tiers: {len(OVERLAY)} overlay selectors absolute "
          f"only inside `{GATE}`, flow outside it; .lp-flow-data is the drawing's "
          f"own {ratios[0]} box with no bottom edge, matched against the lp-flow "
          f"viewBox on {len(PAGES)} pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
