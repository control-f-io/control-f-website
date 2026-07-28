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

  6. THE HOLD OPENS ON THE BUILD'S HEAD, and this stopped being a tuning the
     moment the hold started carrying the pacing. Both tails of the root's
     build are nailed — the contour lands at cover 66 where the frame's relay
     takes over, the light is out at 68 where the lime clearance was swept
     (check-flow-chain.py holds both) — so the ONLY term in the build's length
     that can grow is the hold's own reservation:

         the build, in px of scroll  =  18 points of cover  +  --lp-hold

     Lengthening the hold and slowing the root are therefore the same act, and
     they are only the same act while the build's head sits at the hold's
     OPENING. Let them drift apart and one of two faults appears, both of them
     the thing this page has now been told about twice:

       head before the opening   ink is laid down while the drawing is still
                                 climbing into view, below where anyone is
                                 looking (→ check-build-arrival.py)
       head after the opening    the drawing stands still, finished-looking and
                                 doing nothing, for the difference

     The opening is `cover 50% - --lp-hold`, which needs the cover range to
     resolve into points and therefore needs a viewport. The ratio between the
     two is what is stable: the cover range is `100vh + the flow's own height`
     and the flow's height is built from --lp-measure, which is built from
     100vh, so across the six viewports the gate admits it is 1.704 to 1.800
     viewports (measured; the table is in the rule's own note and in
     check-build-arrival.py). A hold of H vh therefore opens somewhere in
     `50 - H/1.704` to `50 - H/1.800`, and the light's head must be in that
     band. That is a band and not a number because a vh and a percentage of the
     cover range cannot be made equal at every viewport at once — the same
     reason the window's LENGTH is written as a length and not a percentage.

WHAT IT DOES NOT CHECK. Whether the hold is the right length in the sense that
matters to a reader — whether 77vh of standing still is generous or tedious.
That is a judgement made by watching it, recorded in the rule's own note with
the scroll-pixel budget it buys, and it is not an arithmetic anything here can
settle.
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
# THE RAMP IS THREE PHASES NOW, NOT ONE, and this table is the shape of it.
# The old truth was a single from/to ramp — one perfect standstill — and it
# held the wrong moment: the cloud built while the page still scrolled over
# it (Daniel's 2026-07-28 review, three screenshots of a half-covered field),
# and the hold caught only the root. The new ramp keeps the same window and
# the same endpoints and cuts it into:
#   0-45     standstill at +--lp-pan   the cloud builds, clear of the nav
#   45-60    the glide: the pan drains to 0 while the field collapses
#   60-100   standstill at 0           the root grows; ends at translate 0
# Each row: (stop %, coefficient of --lp-hold, pan term present).
# A flat segment is a standstill iff the coefficient advances by exactly the
# segment's share of the window; the glide is standstill-plus-drain.
PHASES = (("0%", -1.00, True),
          ("45%", -0.55, True),
          ("60%", -0.40, False),
          ("100%", 0.0, False))
# ADDED TO the section's own gap, never written over it. `.section` is
# `padding-block: var(--section-gap)` in base.css, so the bare `var(--lp-hold)`
# replaces the top gap instead of extending it — 258 px of reservation against
# 378 px of ramp at 1440 x 900, and a band between the hero and the statement
# that closes by the 120 px difference for the whole approach.
RESERVATION = "calc(var(--section-gap) + var(--lp-hold))"

# Cover range over viewport height at the six viewports the gate admits, so a
# hold in vh can be turned into a band of cover points without a browser. Same
# table as check-build-arrival.py and as the rule's own note; re-measured when
# the flow's height law changes. → invariant 6.
COVER_RANGE_PER_VH = (1.725, 1.747, 1.800, 1.738, 1.772, 1.704)
# The family whose first ink IS the build's head. The light leads the contour by
# six points by construction, so the light is the one that has to meet the hold.
HEAD_RULE = ".lp-flow__light"
# cover 50 % is the centred position, so it is where the hold has to end.
CENTRE_PCT = 50.0
# The band is already 2.4 points wide at 77vh; this only absorbs the
# rounding in the ratio table, not a drift worth a point.
BAND_TOL = 0.05


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

    # --lp-pan is the cloud stop's altitude and must be declared with the hold
    if not re.search(r"--lp-pan\s*:", css):
        findings.append("nothing declares `--lp-pan` — the cloud stop has no "
                        "altitude and the first phase holds at the root's "
                        "position, under the nav, which is the fault the pan "
                        "exists to fix")

    for name, x in ((PLAIN, "0"), (CENTRED, "-50%")):
        stops = keyframe_stops(css, name)
        if stops is None:
            findings.append(f"@keyframes {name} is missing")
            continue
        want = [p for p, _, _ in PHASES]
        if sorted(stops) != sorted(want):
            findings.append(
                f"@keyframes {name} has stops {sorted(stops)} and the ramp is "
                f"the four written-out phases {want} — a missing or extra stop "
                f"is a phase the two ramps no longer agree on, and every held "
                f"part must move in lockstep or the drawing tears")
            continue
        for pct, coef, has_pan in PHASES:
            y = translate_y(stops[pct]) or ""
            yn = norm(y)
            if coef == 0.0:
                ok = yn in ("0", "0px")
                expect = "0"
            else:
                cstr = "-1" if coef == -1.0 else ("%.2f" % coef)
                expect = f"calc({cstr} * var(--lp-hold)" + (" + var(--lp-pan))" if has_pan else ")")
                ok = yn == expect
            if not ok:
                findings.append(
                    f"@keyframes {name} at {pct} is y `{y}`, not `{expect}` — "
                    f"the phase table above is the standstill arithmetic: a "
                    f"coefficient off its share of the window is a stop that "
                    f"drifts on screen, and a pan term where the table has "
                    f"none is a stop at the wrong altitude")
        # 5. the x component is the part's own centring, unchanged
        for stop, _, _ in PHASES:
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

    # ---- 6. the hold opens on the build's head --------------------------
    hold_m = re.search(r"--lp-hold:\s*([\d.]+)vh\s*;", text)
    head_m = None
    for body in declaring(css, HEAD_RULE):
        head_m = re.search(r"animation-range:\s*cover calc\(\(([\d.-]+) \+", body)
        if head_m:
            break
    if hold_m is None:
        findings.append(
            "--lp-hold is no longer a vh length — invariant 6 turns the hold "
            "into cover points through the viewport ratio and cannot without one")
    elif head_m is None:
        findings.append(
            f"`{HEAD_RULE}` has no `cover calc((N + ...` head — that head is what "
            f"the hold's opening has to land on")
    else:
        hold_vh, head = float(hold_m.group(1)), float(head_m.group(1))
        lo = CENTRE_PCT - hold_vh / min(COVER_RANGE_PER_VH)
        hi = CENTRE_PCT - hold_vh / max(COVER_RANGE_PER_VH)
        if not (lo - BAND_TOL <= head <= hi + BAND_TOL):
            findings.append(
                f"a {hold_vh:g}vh hold opens between cover {lo:.2f} and {hi:.2f} across "
                f"the six viewports, and the light's first ink is at cover {head:g} — "
                f"the build's head is {'before' if head < lo else 'after'} the hold's "
                f"opening, so the root "
                f"{'starts growing while the drawing is still climbing into view' if head < lo else 'stands still and finished for the difference'}. "
                f"The hold and the head move together: 18 points of cover plus "
                f"--lp-hold IS the build's length (invariant 6)")

    if findings:
        print(f"hold ramp: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1
    if args.verbose:
        print(f"hold ramp: {len(HELD)} parts, one window {RANGE}")
        print(f"  ramp {FROM_Y} -> 0, reservation var(--lp-hold)")
        if hold_m and head_m:
            print(f"  a {float(hold_m.group(1)):g}vh hold opens cover "
                  f"{CENTRE_PCT - float(hold_m.group(1)) / min(COVER_RANGE_PER_VH):.2f}"
                  f"-{CENTRE_PCT - float(hold_m.group(1)) / max(COVER_RANGE_PER_VH):.2f}; "
                  f"the light's first ink is cover {float(head_m.group(1)):g}")
    print("hold ramp OK — the reservation, the ramp's two ends and the window's "
          "length are one number, so the statement returns to its own layout "
          "exactly and the seam past the hold is the seam that was measured")
    return 0


if __name__ == "__main__":
    sys.exit(main())
