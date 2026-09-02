#!/usr/bin/env python3
"""Every mark on the act rail can be the current one, in every tier.

The rail is five marks and one sentence: "you are in this act". act-rail.js
resolves it by measuring a scroll position for each act and taking the LAST one
the reader has passed --

    y(p) = top + p * span                     span = the track's scroll budget
    current = max { k : scrollY >= y(k) }

-- which is only ever able to name five acts if the five y's are five DIFFERENT
numbers. Two stops on one number is not a near-miss: the earlier of the two can
never win the max, so its mark is lit only by read()'s own `i = 0` default, over
the lead-in before the acts begin, and goes out at the moment the reader arrives.

WHAT WENT WRONG, AND WHY IT WAS INVISIBLE. `span` was `Math.max(0, h - v)` --
the length of `contain`, which is what every fraction in acts.css is quoted
against, and the right span wherever those fractions run. But acts.css declares
`view-timeline-name` and the 640vh height TOGETHER, inside one
@supports (animation-timeline: view()) and one
(min-width: 64rem) and (min-height: 45rem) and (prefers-reduced-motion:
no-preference) gate. Below that gate, under reduced motion, and in a browser
without animation-timeline the tracks are ordinary blocks a little SHORTER than
the window, h - v is zero or a rounding error, and every fraction of it is zero.
Act 2's beat -- contain 36 %, the only fractional one on the page -- landed
exactly on act 1's.

Measured on the shipped page, of the scroll the reader spends inside .sp-track,
how much of it the rail spent naming act 1: 0 px of 901 at 375 x 900, 0 of 842
at 768 x 900, 0 of 783 at 1023 x 900, 4 of 910 at 320 x 900, 32 of 901 at
375 x 812, 56 of 856 at 1280 x 700, and 0 of 714 at 1440 x 900 in both degraded
tiers -- against 1748 of 5760 above the gate, where it was always right. That is
where the composition is reviewed, and it is why this stood: the rail is correct
in the tier it is looked at in and names the wrong act of five in the tier most
of the page is read in.

A screenshot cannot show it. aria-current paints one mark's tick and numeral in
--text-primary; a rail with mark 02 lit is exactly what a rail is supposed to
look like when the reader is in act 2. Nothing in the DOM is missing, nothing
overflows, no console message, and every other gate stayed green.

AND THEN IT WENT WRONG A SECOND TIME, IN ONE ENGINE, FOR THE WHOLE OF THE FIX'S
LIFE. The correction above was written as `getComputedStyle(track)
.viewTimelineName === 'none'`, and there is an engine on which that read is not
a value: Gecko implements no scroll-driven animation, so view-timeline-name is
not on its CSSStyleDeclaration and the read is `undefined`. `undefined ===
'none'` is false, so Firefox -- the one browser whose EVERY tier is a degraded
tier here -- took the has-a-timeline arm at every viewport and got h - v back.
The fix shipped, the gate went green, and the browser it was most needed on was
never on the "after" row.

Measured, Firefox 153 against Chromium 141, the same reading as the table above
-- of the scroll inside .sp-track, how much of it the rail spends naming act 1.
Taken off the two stops rather than off a walk, so it stands two pixels longer
than that table wherever the two overlap; the two are read()'s own slack:

                  Firefox before   Firefox after   Chromium
    1440 x 900      361 of 1902     685 of 1902    1750 of 5760  (timeline)
    1023 x 900      197 of 1448     521 of 1448     509 of 1413
     768 x 900      193 of 1435     517 of 1435     505 of 1402
     375 x 900      198 of 1450     522 of 1450     508 of 1412
     320 x 900      209 of 1481     533 of 1481     520 of 1445
     768 x 1024     148 of 1435     517 of 1435     505 of 1402
     834 x 1194      92 of 1450     522 of 1450     510 of 1417
    1024 x 1366      30 of 1449     522 of 1449    2655 of 8742  (timeline)

h - v shrinks as the window grows, so the collapse this gate exists to prevent
is reached from the tall end instead of the short one: at 1024 x 1366 act 2's
beat stood 30 px past act 1's and act 1 was named over 2 % of its own field.
834 x 1194 is an iPad Air held upright. Chromium's numbers do not move.

So the shape below asks for the value with getPropertyValue(), which returns the
empty string BOTH for a property the engine does not implement and for one that
is not set -- one falsy sentinel for the two ways a track can have no timeline,
where the DOM property has one of them and `undefined` for the other.

WHAT IS CHECKED, on three sides of the one sentence:

  THE PAGE     the five marks' (track, fraction) pairs. Tracks must appear in
               the page in the order the rail lists them, every fraction must be
               in [0, 1) so a beat cannot land inside the NEXT act, and two marks
               on one track must carry strictly increasing fractions. That is
               the declarative half of "five different numbers", and it is the
               half no arithmetic can rescue.

  THE SCRIPT   that the span is chosen per tier rather than assumed: the beat is
               taken against h - v where the track has a view timeline and
               against the track's own h where it does not. Checked as the shape
               of the expression, not as a substring -- and the shape now
               includes HOW the tier is read, because that is where the second
               fault was: getPropertyValue('view-timeline-name'), tested as
               `named && named !== 'none'`, so that an engine with no such
               property lands on the same arm as a track with no timeline.

  THE STYLESHEET  that the premise both branches rest on holds -- for every
               track carrying a FRACTIONAL beat, `view-timeline-name` is
               declared inside a gate (so the `none` branch is the one the
               degraded tiers reach) and the gated height is over 100vh (so
               h - v is positive where the timeline is real, and the contain
               fractions mean what acts.css says they mean).

WHAT THIS DOES NOT CLAIM. Not the 36 % itself -- where act 2 begins is a
decision, and it is the same decision in acts.css and in the rail, which is the
point. Not that the two spans agree: they must not, and the 36 % of a 640vh
track's contain window is 30.3 % of the track while 36 % of a short track's box
is 36.0 % of it. Not the rail's paint, its lead-in, or its is-live band.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-act-beats.py
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
RAIL_JS = DS / "assets/js/act-rail.js"
ACTS_CSS = DS / "assets/css/acts.css"
# Every consumer of act-rail.js. The landing page ships the acts,
# prototypes/statement-to-process.html is the lab they were built in, and
# patterns/ueber-uns.html and patterns/expertise.html index their three and five
# chapters with the same component — every beat at 0 on both, because a chapter
# there begins at a box rather than at a fraction of one. A fifth page adopting
# the rail registers here.
#
# Those two counts read "four and six" until Expertise's map chapter was parked
# and the register was not read again: the rail has always been three rows on
# Über uns and is five on Expertise now. They are quoted rather than derived
# because this list is quoted rather than derived — which is the argument for
# scripts/check-rail-stagger.py finding its pages instead, and for that script
# printing the row count it found on every run.
PAGES = [DS / "patterns/landing-page.html",
         DS / "patterns/ueber-uns.html",
         DS / "patterns/expertise.html",
         DS / "prototypes/statement-to-process.html"]

MARK = re.compile(
    r'data-act-track="([^"]+)"\s+data-act-at="([^"]+)"', re.S)


def fail(msg):
    print(f"FAIL  {msg}")
    return 1


def strip_comments(text, block=("/*", "*/")):
    out, i = [], 0
    while True:
        j = text.find(block[0], i)
        if j < 0:
            out.append(text[i:])
            return "".join(out)
        out.append(text[i:j])
        k = text.find(block[1], j)
        if k < 0:
            return "".join(out)
        i = k + len(block[1])


def marks_of(page):
    """[(selector, fraction)] in the order the rail lists them."""
    html = page.read_text(encoding="utf-8")
    return [(sel, float(at)) for sel, at in MARK.findall(html)], html


def check_page(page):
    bad = 0
    marks, html = marks_of(page)
    if not marks:
        return fail(f"{page.name} declares no act-rail beats — the register is stale")

    # the tracks, in the order they appear in the document
    order = {}
    for sel, _ in marks:
        cls = sel.lstrip(".")
        m = re.search(r'class="[^"]*\b' + re.escape(cls) + r'\b', html)
        if not m:
            bad |= fail(f"{page.name}: mark on {sel}, which is not an element of the page")
            continue
        order.setdefault(sel, m.start())

    seen = []
    for sel, at in marks:
        if sel not in order:
            continue
        if not (0.0 <= at < 1.0):
            bad |= fail(f"{page.name}: beat {at} on {sel} is outside [0, 1) — a "
                        f"fraction of a track that lands outside it names the next act")
        if seen and order[sel] < order[seen[-1][0]]:
            bad |= fail(f"{page.name}: the rail lists {sel} after {seen[-1][0]}, "
                        f"which comes later in the document — the stops cannot be "
                        f"increasing and `last one passed` cannot name five acts")
        if seen and sel == seen[-1][0] and at <= seen[-1][1]:
            bad |= fail(f"{page.name}: two marks on {sel} at {seen[-1][1]} and {at} "
                        f"— on one track the fractions have to increase, or the "
                        f"second stop lands on the first and the first mark can "
                        f"never be the current one")
        seen.append((sel, at))

    fractional = sorted({sel for sel, at in marks if at > 0})
    return bad, fractional


# `at * span` where span is h - v with a timeline and the track's own h without.
# Written as a shape so a rename survives and a collapse does not: the read has
# to be getPropertyValue('view-timeline-name'), the ternary's test has to be that
# value, and its two arms have to be the two different spans.
#
# GETPROPERTYVALUE AND NOT THE DOM PROPERTY, which is the half of the shape this
# gate was missing and the reason it passed over a live fault for as long as it
# has existed. `getComputedStyle(track).viewTimelineName` is the same read in
# every engine that HAS the property and `undefined` in every engine that does
# not -- which is Gecko, the one engine whose every tier is a degraded tier here.
# `undefined === 'none'` is false, so the browser that never has a timeline took
# the has-a-timeline arm and got h - v back, at every viewport. getPropertyValue
# returns the empty string both for a property the engine does not implement and
# for one that is not set, and both mean the same thing to this arithmetic, so
# the absent case cannot fall through the test. Two statements rather than one,
# because a value that has to be read before it can be tested twice is a
# variable; the read is pinned to the same name the ternary then asks about.
#
# AND ONLY THE POSITIVE FORM IS ACCEPTED, `!== 'none'` and not its inverse. The
# guard is a conjunction, so the arm the empty string reaches is the one on the
# FALSE side of it: written `named && named !== 'none' ? h - v : h`, absent lands
# on h with 'none', which is right; written `named && named === 'none' ? h : h -
# v` it lands on h - v with '--sp', which is the fault this whole shape is here
# to prevent, re-spelt. There is one way round for this test and this is it.
SPAN = re.compile(
    r"""(?:var\s+)?(?P<read>\w+)\s*=\s*
        getComputedStyle\(\s*\w+\s*\)\s*
        \.getPropertyValue\(\s*'view-timeline-name'\s*\)\s*;\s*
        (?:var\s+)?(?P<name>\w+)\s*=\s*
        (?P=read)\s*&&\s*(?P=read)\s*!==\s*'none'\s*\?\s*
        (?P<then>[^:]+?)\s*:\s*(?P<else>[^;]+?)\s*;""",
    re.X)


def check_script():
    src = strip_comments(RAIL_JS.read_text(encoding="utf-8"))
    m = SPAN.search(src)
    if not m:
        return fail(
            "act-rail.js does not choose the beat's span off the track's computed "
            "view-timeline-name, read with getPropertyValue and tested for both "
            "'none' and absent. Without that test the only span available is "
            "h - v, which is zero in every tier that has no timeline, and every "
            "fractional beat collapses onto the one before it; and read as a DOM "
            "property instead, the test is undefined in every engine that has no "
            "view-timeline-name at all, which is the same collapse in the one "
            "engine that is always in that tier")
    # The guard is fixed at `named && named !== 'none'` by the pattern above, so
    # the first arm is the has-a-timeline one and the second is every other tier
    # — 'none', and the empty string an engine without the property returns.
    with_tl, no_tl = m.group("then"), m.group("else")
    bad = 0
    if not re.fullmatch(r"\w+\s*-\s*\w+", with_tl.strip()):
        bad |= fail(f"act-rail.js takes the beat against {with_tl.strip()!r} where the "
                    f"track HAS a timeline; it has to be the contain length, "
                    f"height minus viewport, because that is what every fraction "
                    f"in acts.css is quoted against")
    if not re.fullmatch(r"\w+", no_tl.strip()):
        bad |= fail(f"act-rail.js takes the beat against {no_tl.strip()!r} where the "
                    f"track has NO timeline; it has to be the track's own height "
                    f"— the acts are laid out in that box rather than scrubbed "
                    f"across it, and any expression that can reach zero puts two "
                    f"marks on one number")
    if not re.search(re.escape(m.group("name")) + r"\b", src[m.end():]):
        bad |= fail("act-rail.js computes the span and never uses it")
    return bad


GATE = re.compile(r"\(\s*min-width\s*:[^)]*\)|\(\s*min-height\s*:[^)]*\)")


def check_stylesheet(fractional):
    """For each track carrying a fractional beat: its timeline is declared behind
    a gate, and its gated height is over 100vh."""
    css = ACTS_CSS.read_text(encoding="utf-8")
    bad = 0
    for sel in fractional:
        rules = [m for m in re.finditer(
            re.escape(sel) + r"\s*\{([^}]*)\}", css)]
        timed = [m for m in rules if "view-timeline-name" in m.group(1)]
        if not timed:
            bad |= fail(f"{sel} carries a fractional beat and acts.css never gives "
                        f"it a view-timeline-name — there is no tier in which the "
                        f"contain fraction the rail computes is the one the page "
                        f"animates on")
            continue
        for m in timed:
            head = css[:m.start()]
            depth_supports = head.count("@supports") - 0
            # the innermost media query wrapping this rule
            gated = False
            for q in re.finditer(r"@media([^{]*)\{", head):
                if GATE.search(q.group(1)):
                    gated = True
            if not gated:
                bad |= fail(f"{sel}'s view-timeline-name is not behind a "
                            f"min-width/min-height gate. The rail's two spans "
                            f"rest on the timeline existing in exactly one tier; "
                            f"an ungated timeline means the h - v branch runs at "
                            f"widths where the track is shorter than the window "
                            f"and the beat collapses again")
            if not depth_supports:
                bad |= fail(f"{sel}'s view-timeline-name is not behind "
                            f"@supports (animation-timeline: view()) — a browser "
                            f"without it would take the timed branch")
            h = re.search(r"height\s*:\s*([\d.]+)vh", m.group(1))
            if not h:
                bad |= fail(f"{sel} declares a view timeline and no height in vh "
                            f"beside it — the contain length is h - v and nothing "
                            f"here says h is over a viewport")
            elif float(h.group(1)) <= 100:
                bad |= fail(f"{sel} is {h.group(1)}vh with a view timeline: h - v is "
                            f"not positive, so `contain` is empty and every "
                            f"fraction of it is the track's top")
    return bad


def main():
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()
    bad = 0
    fractional = set()
    total = 0
    for page in PAGES:
        r = check_page(page)
        if isinstance(r, int):
            bad |= r
            continue
        b, fr = r
        bad |= b
        fractional |= set(fr)
        total += len(marks_of(page)[0])
    bad |= check_script()
    bad |= check_stylesheet(sorted(fractional))
    if bad:
        return 1
    print(f"OK  {total} act-rail beats on {len(PAGES)} page(s), "
          f"{len(fractional)} of them fractional; strictly increasing as declared, "
          f"and act-rail.js takes each one against the contain length where the "
          f"track has a view timeline and against the track's own box where it "
          f"does not — so no two marks share a stop in any tier")
    return 0


if __name__ == "__main__":
    sys.exit(main())
