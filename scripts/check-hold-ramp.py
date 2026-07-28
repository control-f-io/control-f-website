#!/usr/bin/env python3
"""A hold that is a displacement is only safe while it cancels exactly.

WHAT THE MECHANISM IS. patterns/landing-page.html holds the statement still
while the root grows out of its void. It cannot do that with `position: sticky`
and this is measured, not assumed: .lp-flow is stretched between two anchors —
the void's centre above, the lectern's rail below — so it is not in the figure's
containing block and does not travel with it, and anchor() does not follow a
sticky ancestor either (at the pin, .lp-frame's top holds at viewport 171.0
while .lp-flow's box keeps travelling and its height holds at 663.91).

What a transform CAN do is move the paint without moving the layout. Forcing
`translate: -50% 250px` onto .lp-flow at 1440 x 900 paints the box 250.0 px
lower and leaves the contour's mean scale at 0.2538 / 0.5413 / 0.8280 at scroll
1000 / 1100 / 1200 — the same four decimal places as without it. anchor() and
view() both read layout boxes. So the hold is:

    .lp-hold          reserves --lp-hold of scroll as padding above the
                      statement, pushing everything from the figure to the
                      lectern down by exactly that
    the six parts     carry a scrubbed `translate` that runs from
                      -(--lp-hold) to 0 across a window exactly --lp-hold px
                      long, ending at cover 50 % of --lp-flow

and the three states that come out of it are the whole safety argument:

    before the window   translate is -(--lp-hold), which cancels the padding
                        exactly. The approach paints where it painted before
                        the hold existed.
    inside it           the two rates are equal and opposite. The statement
                        stands still.
    after it            translate is 0. Every layout box is where it was, the
                        seam .lp-flow's foot makes with the lectern's rail is
                        0.00 px again, and check-flow-handover.py and
                        check-void-departure.py hold numbers that never moved.

WHY THIS FILE EXISTS. The third state is bought by an arithmetic identity
between four values in three different declarations, and there is no rendering
in which a small error in it is visible. Get the reservation and the ramp's
from-state out of step by 20 px and the drawing settles 20 px above the rail
FOREVER, at every scroll position past the hold, at every viewport — a torn
seam that no screenshot of the hold itself would show, because during the hold
the seam is legitimately open. This directory already carries two checks for
that join (handover for x, seam-travel for the asymmetry) and both would stay
green, because neither reads a transform.

THE FIVE THINGS HELD

  1. THE RAMP RETURNS TO ZERO. Both keyframes end at a y of 0. A hold that
     lands anywhere else is a permanent offset on the seam.

  2. THE RAMP STARTS AT MINUS THE RESERVATION. Both keyframes open at
     calc(-1 * var(--lp-hold)) and .lp-hold reserves var(--lp-hold). One
     literal typed in place of the variable in either spot is the 20 px above.

  3. THE WINDOW IS A LENGTH, NOT A PERCENTAGE. The range is
     `cover calc(50% - var(--lp-hold)) cover 50%`. The percentage resolves
     against the cover range and the length does not resolve against anything,
     so the window is --lp-hold px long at every viewport — which is what makes
     the displacement and the scroll cancel to the pixel. Written as two
     percentages it would be a fixed FRACTION of `100vh + the flow's own
     height`, and the flow's height is a stretch between two anchors: a number
     no stylesheet can write and therefore a residual nobody can predict.

  4. THE END OF THE WINDOW IS COVER 50 %. That is the definition of the
     centred position, so the held position is the centre rather than a tuned
     offset — measured at all six viewports the gate admits, the held top edge
     is (viewport - flow height) / 2 to the tenth of a pixel.

  5. A PART THAT IS CENTRED WITH `translate` TAKES THE -c KEYFRAME. `translate`
     is one property and a keyframe replaces all of it, so a part carrying
     `translate: -50% 0` and given the plain ramp jumps half its own width
     sideways — and `both` means from the top of the document, not just during
     the hold.

WHAT IT DOES NOT CHECK. Whether --lp-hold is the RIGHT length. 42vh puts the
window's opening within a point of the light's first ink at all six viewports,
which is a tuning recorded in the rule's own note and re-measured when it moves;
it is not an identity and this file does not pretend it is one.
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "design-system/patterns/landing-page.html"

# The two ramps and who takes which. The -c copy exists only because those four
# parts are centred with `translate` and a keyframe replaces the whole property.
PLAIN = "lp-hold"
CENTRED = "lp-hold-c"
HELD = {
    ".cf-statement__figure .cf-iso": PLAIN,
    ".cf-statement__text": PLAIN,
    ".lp-flow": CENTRED,
    ".lp-flow-data": CENTRED,
    ".lp-flow__stem": CENTRED,
    ".lp-proc-head": CENTRED,
}
RANGE = "cover calc(50% - var(--lp-hold)) cover 50%"
FROM_Y = "calc(-1 * var(--lp-hold))"
# ADDED TO the section's own gap, never written over it. `.section` is
# `padding-block: var(--section-gap)` in base.css, so the bare `var(--lp-hold)`
# replaces the top gap instead of extending it — 258 px of reservation against
# 378 px of ramp at 1440 x 900, and a band between the hero and the statement
# that closes by the 120 px difference for the whole approach.
RESERVATION = "calc(var(--section-gap) + var(--lp-hold))"


def strip_comments(css):
    """Blank out comments, keeping newlines so line numbers survive."""
    return re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)),
                  css, flags=re.S)


def page_style(text):
    m = re.search(r"<style>(.*?)</style>", text, re.S)
    return strip_comments(m.group(1)) if m else ""


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def blocks(css):
    """Every `prelude { body }` in the sheet, at any nesting depth.

    At-rules with blocks are transparent here — @supports and @media wrap
    ordinary rules and this check is about the rules, not the gate. @keyframes
    is read separately because its body is stops, not declarations.
    """
    out, i, n = [], 0, len(css)
    while i < n:
        if css[i] != "{":
            i += 1
            continue
        prelude = css[max(0, css.rfind("}", 0, i) + 1):i]
        prelude = norm(prelude[max(prelude.rfind("{") + 1, 0):])
        depth, j = 1, i + 1
        while j < n and depth:
            depth += {"{": 1, "}": -1}.get(css[j], 0)
            j += 1
        body = css[i + 1:j - 1]
        out.append((prelude, body))
        if prelude.startswith("@") and not prelude.startswith("@keyframes"):
            i += 1          # descend: the inner rules are read on their own
        else:
            i = j
    return out


def keyframe_stops(css, name):
    """{selector: body} for one @keyframes block, or None if it is absent."""
    for prelude, body in blocks(css):
        if re.fullmatch(r"@keyframes\s+" + re.escape(name), prelude):
            return {norm(p): norm(b) for p, b in blocks(body)}
    return None


def declaring(css, selector):
    """Bodies of every ordinary rule whose selector list contains `selector`."""
    out = []
    for prelude, body in blocks(css):
        if prelude.startswith("@") or "{" in body:
            continue
        if selector in [norm(s) for s in prelude.split(",")]:
            out.append(norm(body))
    return out


def translate_y(decl):
    """The y component of a `translate:` declaration, or None."""
    m = re.search(r"(?<![-\w])translate\s*:\s*([^;]+)", decl)
    if not m:
        return None
    # one calc() may contain spaces; split on top-level whitespace only
    parts, depth, cur = [], 0, ""
    for ch in m.group(1).strip():
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch.isspace() and depth == 0:
            if cur:
                parts.append(cur)
            cur = ""
        else:
            cur += ch
    if cur:
        parts.append(cur)
    return parts[1] if len(parts) > 1 else "0"


def translate_x(decl):
    m = re.search(r"(?<![-\w])translate\s*:\s*([^;]+)", decl)
    if not m:
        return None
    return m.group(1).strip().split()[0]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    text = PAGE.read_text(encoding="utf-8")
    css = page_style(text)
    findings = []

    # ---- 1 & 2. the ramp opens at minus the reservation and closes at zero --
    reservations = declaring(css, ".lp-hold")
    if not reservations:
        findings.append("nothing declares `.lp-hold` — the hold reserves no "
                        "scroll, so the ramp displaces the statement by "
                        "--lp-hold and never gives it back")
    for body in reservations:
        m = re.search(r"padding-block-start\s*:\s*([^;]+)", body)
        if m is None or norm(m.group(1)) != RESERVATION:
            findings.append(
                f"`.lp-hold` reserves `{m.group(1).strip() if m else 'nothing'}` "
                f"and not `{RESERVATION}` — the ramp displaces by --lp-hold, so "
                f"anything but --lp-hold ON TOP OF the section's own gap is a "
                f"band between the hero and the statement that closes by the "
                f"difference, through the whole approach, at every viewport")

    for name, x in ((PLAIN, "0"), (CENTRED, "-50%")):
        stops = keyframe_stops(css, name)
        if stops is None:
            findings.append(f"@keyframes {name} is missing")
            continue
        if norm(",".join(sorted(stops))) != "from,to":
            findings.append(
                f"@keyframes {name} is not the two written-out stops the ramp "
                f"needs — an implied end is a value the next edit can move "
                f"without touching this")
            continue
        f, t = translate_y(stops["from"]), translate_y(stops["to"])
        if f is None or norm(f) != FROM_Y:
            findings.append(
                f"@keyframes {name} opens at y `{f}`, not `{FROM_Y}` — the "
                f"approach no longer cancels the reservation and the statement "
                f"paints off its own layout by the difference")
        if t is None or norm(t) not in ("0", "0px"):
            findings.append(
                f"@keyframes {name} closes at y `{t}`, not 0 — a hold that "
                f"lands anywhere else is a permanent offset on the seam "
                f".lp-flow's foot makes with the lectern's rail")
        # 5. the x component is the part's own centring, unchanged
        for stop in ("from", "to"):
            if norm(translate_x(stops[stop]) or "") != x:
                findings.append(
                    f"@keyframes {name}'s `{stop}` sets x `{translate_x(stops[stop])}` "
                    f"and not `{x}` — `translate` is one property, so the stop has "
                    f"to restate the centring or the part jumps half its own width "
                    f"sideways from the top of the document")

    # ---- 3, 4, 5. every held part, on one window, with the right ramp -------
    for selector, ramp in HELD.items():
        bodies = [b for b in declaring(css, selector)
                  if "animation" in b and "lp-hold" in b]
        if not bodies:
            findings.append(
                f"`{selector}` no longer takes the hold — it is one of the six "
                f"parts of the statement, and a part left behind slides across "
                f"the drawing the other five are holding still")
            continue
        for body in bodies:
            m = re.search(r"(?<![-\w])animation\s*:\s*([^;]+)", body)
            if m is None or m.group(1).split()[0] != ramp:
                findings.append(
                    f"`{selector}` takes `{m.group(1).split()[0] if m else None}` "
                    f"where it needs `{ramp}`" +
                    ("" if ramp == PLAIN else
                     " — it is centred with `translate`, and the plain ramp "
                     "would drop the -50%"))
            m = re.search(r"animation-range\s*:\s*([^;]+)", body)
            got = norm(m.group(1)) if m else None
            if got != RANGE:
                findings.append(
                    f"`{selector}` holds over `{got}`, not `{RANGE}` — the six "
                    f"parts have to share one window, and its length has to be "
                    f"the LENGTH --lp-hold rather than a percentage, or the "
                    f"displacement and the scroll stop cancelling")
            m = re.search(r"animation-timeline\s*:\s*([^;]+)", body)
            if m is None or norm(m.group(1)) != "--lp-flow":
                findings.append(
                    f"`{selector}` holds on `{norm(m.group(1)) if m else None}` "
                    f"and not on --lp-flow — cover 50 % of the drawing's own "
                    f"view timeline is the centred position, and it is the only "
                    f"timeline on which that sentence is true")

    # ---- the scope that lets four of the six read the name at all ----------
    if not any(re.search(r"timeline-scope\s*:\s*--lp-flow", b)
               for b in declaring(css, "main")):
        findings.append(
            "`main` no longer scopes --lp-flow — the statement's copy and the "
            "process header are outside .cf-statement__figure, so a narrower "
            "scope resolves a null timeline for them and they do not hold")

    if findings:
        print(f"hold ramp: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1
    if args.verbose:
        print(f"hold ramp: {len(HELD)} parts, one window {RANGE}")
        print(f"  ramp {FROM_Y} -> 0, reservation var(--lp-hold)")
    print("hold ramp OK — the reservation, the ramp's two ends and the window's "
          "length are one number, so the statement returns to its own layout "
          "exactly and the seam past the hold is the seam that was measured")
    return 0


if __name__ == "__main__":
    sys.exit(main())
