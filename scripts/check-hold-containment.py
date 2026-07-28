#!/usr/bin/env python3
"""The hold has to outlast the thing it is holding.

WHAT DANIEL ASKED FOR, which is the only standard this file is written to:
"stopping when i scroll to see the bubbles inflate into the root system ... i
should be able to see it growing when scrolling and it shouldn't be that fast."
Two claims, and they are one claim: the page stops, and the growth happens
inside the stop. A stop that ends before the growth does is not a stop the
reader experiences as one -- it is a pause, and then the drawing leaves.

THE MECHANISM IS ALREADY CHECKED; THE RELATION BETWEEN ITS TWO HALVES IS NOT.
check-hold-ramp.py holds the hold: the reservation, the ramp's from-state, the
window's length, the return to zero -- five facts, all of them internal to the
hold. .lp-flow__seg, .lp-flow__light, .lp-flow__node and .lp-flow__val carry
the build, and check-flow-chain.py holds the chain identity that makes one
front travel the root. Both halves are correct and neither one knows the other
exists. Nothing in scripts/ has ever read the hold's window and the build's
window in the same breath, and so nothing has ever been able to say the thing
the brief actually asks: is the growth inside the stop.

It was not, and #225 has just closed most of the gap. That commit is stage 2
of the hold: --lp-hold 42vh -> 77vh, every head 20 points of cover earlier,
--flow-c widened. Measured in Chromium at 1440 x 900 before and after, stepping
10 px at a time with smooth scrolling disabled (it is on by default in
base.css, and a sampled scrub that does not turn it off measures the easing and
not the page):

                              before #225        after #225
    the flow box stops        370 px             680 px
    the contour draws         530 px             840 px
    drawn while stopped       270 px   50.9 %    580 px   69.0 %
    drawn while travelling    260 px   49.1 %    260 px   31.0 %

The share held went from half to just over two thirds. THE TRAVELLING REMAINDER
DID NOT MOVE AT ALL: 260 px before, 260 px after. Lengthening the hold bought
the build's OPENING -- it now takes its first ink 10 px into the hold rather
than 100 -- and bought the tail nothing, because the two ends are not the same
kind of quantity.

AND THAT IS WHY THE OVERHANG IS A CONSTANT, WHICH IS WHY THIS IS A SCRIPT AND
NOT A MEASUREMENT. Both windows are declared in `cover` percentages of the same
timeline, --lp-flow, whose subject is .lp-flow itself:

    the hold      cover calc(50% - var(--lp-hold))  ->  cover 50%
    the contour   cover (h + l*c)%                  ->  cover (h + (l+u)*c)%

The hold's LENGTH is a px quantity and depends on the viewport, so the hold's
start moves -- and --lp-hold is the one term any lane can pull on. Its END does
not: it is the literal 50%, at every viewport, by construction. The contour's
end is max over the strokes of h + (l+u)*c, a pure number off the shipped
markup -- 65.99, which #225's own note nails there deliberately, because that
is where .lp-frame's relay takes over. So

    the contour closes 15.99 points of cover after the hold has released,
    at every viewport, unconditionally, and no value of --lp-hold can
    shorten that by a single point.

At 1440 x 900 a point of cover is 15.64 px, so those 15.99 points ARE the 260
px that did not move, arrived at from the stylesheet without opening a browser.
That is the finding this file exists to make un-driftable: the last third of
the root cannot be held by lengthening the hold, and the next lane that tries
will move a number this check is already watching.

WHAT IS HELD, and how each number can be made to fail

  1. THE HOLD RELEASES AT COVER 50 %. Both hold ramps -- .lp-flow's and the
     parts that travel with it -- end at the literal `cover 50%`. If a lane
     moves that literal, the arithmetic below is measuring a window that is no
     longer there, and this check would go on passing while meaning nothing.
     So the literal is read, not assumed.

  2. THE BUILD'S CLOSE IS RATCHETED. The last window to close over the whole
     build -- contour, light, junction, numeral -- may not close later than it
     does today. A lane that widens --flow-c, or adds a stroke with a longer
     run, or moves a head constant up, pushes the drawing further past the
     release and fails here.

  3. THE OVERHANG MAY NOT GROW. Contour: 15.99 points. Whole build including
     the light's fade: 17.99 points. Both recorded as ceilings.

  4. THE BUILD STILL STARTS INSIDE THE HOLD. The first window to open is the
     light's, at cover 6.00 %, against the hold's 5.69 % at 1440 x 900 -- a
     margin of 10 px of scroll, which is the tightest number on this page and
     the thing #225 bought. This one IS viewport-dependent and it is the half
     that now works; it is held so that a lane shortening --lp-hold, or moving
     a head back down, cannot quietly take the opening away as well.

THE TARGET IS ZERO AND THE FLOOR IS TODAY. Every number here is a ceiling at
the value that ships, not a value anyone chose. The check passes on the page as
it stands and fails on any change that makes the reader chase the root further
than they already do. It is written this way on purpose: closing the last 15.99
points is not a tuning job -- it needs the contour's landing to come off cover
66, which is where .lp-frame's relay is nailed, so the root and the lectern
have to move together or not at all. Until someone does that, this file is what
stops the number going back up.
"""

import re
import sys
from pathlib import Path

PAGE = Path(__file__).resolve().parent.parent / "design-system/patterns/landing-page.html"

# Ceilings, in points of `cover` on the --lp-flow timeline. Recorded from the
# page as it ships; the target for every one of them is 0.00.
CONTOUR_OVERHANG_MAX = 15.99
BUILD_OVERHANG_MAX = 17.99
BUILD_OPEN_MAX = 6.00  # the first window may not open later than the light's

TOL = 0.005


def fail(msg):
    print(f"check-hold-containment: FAIL: {msg}")
    sys.exit(1)


def main():
    src = PAGE.read_text()

    # --- the release point, read off the cascade rather than assumed ----------
    ranges = re.findall(
        r"animation-range:\s*cover\s+calc\(\s*50%\s*-\s*var\(--lp-hold\)\s*\)\s+cover\s+([\d.]+)%",
        src,
    )
    if not ranges:
        fail("no hold window of the form `cover calc(50% - var(--lp-hold)) cover N%` "
             "found; check-hold-ramp.py's mechanism has moved and this file is stale")
    closes = {float(r) for r in ranges}
    if len(closes) != 1:
        fail(f"the hold's parts release at different points: {sorted(closes)}; "
             "they are one hold and must share one close")
    release = closes.pop()
    if abs(release - 50.0) > TOL:
        fail(f"the hold releases at cover {release}%, not 50%; every ceiling in "
             "this file is stated against 50 and must be re-derived")

    # --- --flow-c, the front's speed in points of cover per unit of --l -------
    m = re.search(r"--flow-c:\s*([\d.]+)", src)
    if not m:
        fail("--flow-c not found; the build's windows cannot be resolved")
    c = float(m.group(1))

    # --- every part's --l / --u off the shipped markup ------------------------
    def parts(cls):
        out = []
        for mm in re.finditer(
            r'class="([^"]*\b' + re.escape(cls) + r'\b[^"]*)"[^>]*style="([^"]*)"', src
        ):
            style = mm.group(2)
            ml = re.search(r"--l:\s*([\d.]+)", style)
            if not ml:
                continue
            mu = re.search(r"--u:\s*([\d.]+)", style)
            out.append((float(ml.group(1)), float(mu.group(1)) if mu else 0.0))
        return out

    seg = parts("lp-flow__seg")
    light = parts("lp-flow__light")
    node = parts("lp-flow__node")
    val = parts("lp-flow__val")
    if not (seg and light and node and val):
        fail(f"the drawing's parts did not parse "
             f"(seg={len(seg)} light={len(light)} node={len(node)} val={len(val)})")

    # The four heads, read off the stylesheet so a retimed lane fails here
    # rather than silently shifting what this check is measuring.
    def head(selector, which):
        block = re.search(
            re.escape(selector) + r"\s*\{(.*?)\}", src, re.S
        )
        if not block:
            fail(f"{selector} not found")
        rng = re.search(r"animation-range:\s*(.*?);", block.group(1), re.S)
        if not rng:
            fail(f"{selector} has no animation-range")
        nums = re.findall(r"\(\s*(\d+)\s*\+", rng.group(1))
        if len(nums) <= which:
            fail(f"{selector}: expected at least {which + 1} window heads, got {nums}")
        return float(nums[which])

    seg_open, seg_close = head(".lp-flow__seg", 0), head(".lp-flow__seg", 1)
    light_open = head(".lp-flow__light", 0)
    light_fade_close = head(".lp-flow__light", 3)
    node_close = head(".lp-flow__node", 1)
    val_close = head(".lp-flow__val", 1)

    # --- resolve every window -------------------------------------------------
    contour_close = max(seg_close + (l + u) * c for l, u in seg)
    contour_open = min(seg_open + l * c for l, _ in seg)
    build_close = max(
        contour_close,
        max(light_fade_close + (l + u) * c for l, u in light),
        max(node_close + l * c for l, _ in node),
        max(val_close + l * c for l, _ in val),
    )
    build_open = min(
        contour_open,
        min(light_open + l * c for l, _ in light),
    )

    contour_overhang = contour_close - release
    build_overhang = build_close - release

    print(f"check-hold-containment: hold releases at cover {release:.2f}%")
    print(f"  build opens   cover {build_open:.2f}%   (ceiling {BUILD_OPEN_MAX:.2f})")
    print(f"  contour opens cover {contour_open:.2f}%")
    print(f"  contour close cover {contour_close:.2f}%  overhang "
          f"{contour_overhang:+.2f} pts (ceiling {CONTOUR_OVERHANG_MAX:.2f}, target 0)")
    print(f"  build close   cover {build_close:.2f}%  overhang "
          f"{build_overhang:+.2f} pts (ceiling {BUILD_OVERHANG_MAX:.2f}, target 0)")

    if build_open > BUILD_OPEN_MAX + TOL:
        fail(f"the build now opens at cover {build_open:.2f}%, later than the "
             f"{BUILD_OPEN_MAX:.2f}% that ships. At 1440 x 900 the hold opens at "
             "cover 25.83 %, so the opening that currently falls inside the hold "
             "would fall outside it: the reader would meet a stopped drawing "
             "doing nothing, and then the growth after it had started moving again")

    if contour_overhang > CONTOUR_OVERHANG_MAX + TOL:
        fail(f"the contour now closes {contour_overhang:.2f} points of cover after "
             f"the hold releases, against {CONTOUR_OVERHANG_MAX:.2f} that ship. "
             "At 1440 x 900 a point of cover is 15.64 px of scroll, so this is "
             f"{(contour_overhang - CONTOUR_OVERHANG_MAX) * 15.64:.0f} px more root "
             "drawn while the drawing slides off the top of the viewport")

    if build_overhang > BUILD_OVERHANG_MAX + TOL:
        fail(f"the build now closes {build_overhang:.2f} points of cover after the "
             f"hold releases, against {BUILD_OVERHANG_MAX:.2f} that ship")

    print(f"check-hold-containment: OK "
          f"({len(seg)} strokes, {len(light)} lights, {len(node)} junctions, "
          f"{len(val)} numerals; {contour_overhang:.2f} pts of contour still "
          "drawn after the hold releases -- target 0)")


if __name__ == "__main__":
    main()
