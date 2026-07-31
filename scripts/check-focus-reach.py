#!/usr/bin/env python3
"""The act rail is hidden by paint, not by the tree.

The rail is the contents page for 22 000 px of composition: five fixed links in
the left margin that say which act you are in and jump to any of the others. It
is off screen until the acts are, and the argument for that was written down —
"a rail the reader cannot see is not a rail they should be able to Tab into" —
and implemented as the `hidden` attribute, set and cleared by act-rail.js
alongside the class that fades it.

WHAT WENT WRONG. `hidden` is only ever OFF while the viewport's middle is inside
the acts, and by the time a reader tabbing forward is inside the acts, Tab has
already gone past the rail's place in the document. The two conditions never
overlap, so the rail could not be reached by keyboard in either direction.
Measured in Chromium at 1440 x 900 with consent accepted:

    forward   focus the hero's "Kennenlernen" and press Tab. The rail's five
              links are the next thing in the document, the viewport's middle is
              still in the hero, `hidden` is on. Focus lands on the first FAQ
              summary, scrollY 0 -> 16 585 — five acts skipped in one keypress.
    reverse   focus that same summary and Shift+Tab. Straight back to
              "Kennenlernen" at scrollY 3 923. The rail is live and at opacity 1
              for the whole of that jump and is still not in the sequence.
    paging    PageDown x9 to scrollY 7 083, act 3, rail live. Focus is on
              <body>, so Tab restarts at the document's first stop — scrolling
              does not move the sequential focus starting point — and tabbing on
              from there reaches the hero's toggle, which scrolls back to the
              top and turns `hidden` on again before the rail's turn comes.

Forcing .focus() on a link proved the rail itself was sound: Tab walked 01 -> 05
in order and left into the FAQ. It was only ever the attribute. And nothing
caught it because the rail photographs correctly in every state — a nav that is
present, visible, marked with aria-current and unreachable looks exactly like a
nav that works.

WHAT IS CHECKED. The three files that have to agree, all of them read with CSS
comments stripped because this file's own prose quotes the declarations:

  MARKUP    no consumer page puts `hidden` on .act-rail. The attribute wins over
            every opacity in the stylesheet, so with scripting off it is also the
            difference between the documented degradation — five links that go
            roughly where they say — and no rail at all.

  SCRIPT    act-rail.js never assigns .hidden. It writes one thing for the
            state, and that is the class.

  STYLESHEET  the rule that lifts the rail's opacity names BOTH .is-live and
            :focus-within, so a rail a reader Tabs to shows itself; and there is
            a `pointer-events: none` for the not-live, not-focused state, because
            an invisible fixed column in the left margin must not swallow clicks
            over act 1's full-bleed field. Hidden by paint is only honest if both
            halves are there: opacity alone leaves a click trap, and
            pointer-events alone leaves an invisible focus stop.

WHAT THIS DOES NOT CLAIM. Not where the rail lives, not the gate it is behind,
not the fade's duration, and not that :focus-within is the only way in — a skip
link into the rail would satisfy the same requirement and would need this check
rewritten rather than deleted.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-focus-reach.py
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ACTS = ROOT / "design-system/assets/css/acts.css"
RAIL_JS = ROOT / "design-system/assets/js/act-rail.js"
PAGES = [ROOT / "design-system/patterns/landing-page.html",
         ROOT / "design-system/prototypes/statement-to-process.html"]


def fail(msg):
    print(f"FAIL  {msg}")
    return 1


def strip_css_comments(css):
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def strip_js_comments(js):
    js = re.sub(r"/\*.*?\*/", "", js, flags=re.S)
    return re.sub(r"^\s*//.*$", "", js, flags=re.M)


def rules(css):
    """(prelude terms, body) for every rule in the sheet."""
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        yield [t.strip() for t in m.group(1).split(",")], m.group(2)


def main():
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()
    bad = 0

    # ---- markup ----
    seen = 0
    for page in PAGES:
        html = page.read_text(encoding="utf-8")
        for m in re.finditer(r"<nav\b[^>]*\bclass=\"[^\"]*\bact-rail\b[^\"]*\"[^>]*>", html):
            seen += 1
            if re.search(r"\bhidden\b(?!-)", m.group(0)):
                bad |= fail(f"{page.name} puts `hidden` on .act-rail. The "
                            f"attribute takes the rail out of the tab order at "
                            f"exactly the scroll positions from which Tab has "
                            f"already passed it, which is every one of them, and "
                            f"with scripting off it takes the rail away "
                            f"altogether. Hide it by paint.")
    if not seen:
        bad |= fail("no <nav class=\"act-rail\"> on either consumer page — the "
                    "register is stale")

    # ---- script ----
    js = strip_js_comments(RAIL_JS.read_text(encoding="utf-8"))
    for m in re.finditer(r"(\w+)\.hidden\s*=", js):
        bad |= fail(f"act-rail.js assigns `{m.group(1)}.hidden`. Scroll position "
                    f"decides what the rail LOOKS like, never whether it is in "
                    f"the document — that is the pairing that made the rail "
                    f"unreachable by keyboard in both directions.")

    # ---- stylesheet ----
    css = strip_css_comments(ACTS.read_text(encoding="utf-8"))
    lifts = []          # preludes of rules that set the rail's opacity to 1
    guard = False       # a pointer-events: none behind both negations
    for terms, body in rules(css):
        decls = {d.split(":", 1)[0].strip(): d.split(":", 1)[1].strip()
                 for d in body.split(";") if ":" in d}
        rail_terms = [t for t in terms if t.startswith(".act-rail")
                      and "::" not in t and "__" not in t]
        if not rail_terms:
            continue
        if decls.get("opacity") == "1":
            lifts += rail_terms
        if decls.get("pointer-events") == "none":
            # THE GUARANTEE IS "NEVER DISARMED WHILE PAINTED", NOT ONE SELECTOR
            # SHAPE. :not(:focus-within) is required of every such rule and is
            # not negotiable — it is the half that keeps a rail the reader has
            # Tabbed to from being a dead focus stop. What may vary is how the
            # rule knows the rail is unpainted. Two ways are honest:
            #
            #   BY THE SCROLL   :not(.is-live) as well, which is the pairing the
            #                   sheet shipped with: the rule matches only the
            #                   state the opacity rules leave at 0.
            #   BY ITS OWN HAND opacity: 0 in the SAME rule, which is stricter
            #                   than the first because the hiding and the
            #                   disarming cannot then drift apart — one selector
            #                   does both, so there is no state where one applies
            #                   and the other does not. This is the shape the
            #                   sub-96rem tier takes, where `is-live` still runs
            #                   and deliberately no longer paints.
            #
            # A rule with neither still fails, and so does one that hides on
            # :not(.is-live) alone: that would take the rail away from the reader
            # who Tabbed to it, which is the trap this file exists over.
            has_focus_guard = all(":not(:focus-within)" in t for t in rail_terms)
            knows_unpainted = (all(":not(.is-live)" in t for t in rail_terms)
                               or decls.get("opacity") == "0")
            if has_focus_guard and knows_unpainted:
                guard = True
            else:
                bad |= fail(f"`pointer-events: none` on `{', '.join(rail_terms)}` "
                            f"does not carry :not(:focus-within), or carries it "
                            f"without either :not(.is-live) or an `opacity: 0` of "
                            f"its own, so it would kill the rail in a state the "
                            f"reader can see it in.")

    if not any(".is-live" in t for t in lifts):
        bad |= fail("no rule lifts .act-rail to opacity 1 on .is-live — the "
                    "scroll no longer brings the rail in at all.")
    if not any(":focus-within" in t for t in lifts):
        bad |= fail("no rule lifts .act-rail to opacity 1 on :focus-within. "
                    "Without it the rail is in the tab order and invisible when "
                    "it gets there, which is a focus stop the reader cannot see "
                    "— worse than the trap it replaced.")
    if not guard:
        bad |= fail("nothing sets `pointer-events: none` on .act-rail while it "
                    "is neither live nor focused. An invisible fixed five-row "
                    "column at the left margin swallows every click that lands "
                    "in it, over act 1's full-bleed field and over the hero.")
    if bad:
        return 1

    print(f"OK  the act rail is hidden by paint on {len(PAGES)} pages: no "
          f"`hidden` in markup, no .hidden in act-rail.js, opacity lifted on "
          f"{len(set(lifts))} selectors including :focus-within, and "
          f"pointer-events released only with it")
    return 0


if __name__ == "__main__":
    sys.exit(main())
