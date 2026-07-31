#!/usr/bin/env python3
"""An `infinite` animation on the document clock must be able to stop.

The eighty-eighth check, and the fourth whose subject is what a page COSTS
rather than what it looks like. check-glass-budget.py counts backdrop-filter
because "a third blurred layer renders correctly; it just costs".
check-iso-motion.py holds the scroll timelines to `screen`. This one holds the
other clock, and it is the one with the largest bill attached to it.

A scroll-driven animation is free while nobody scrolls. No scroll, no frame,
no work — that is the whole reason this system reaches for view() first, and
the reason a page with eight hundred of them can sit still and cost nothing.
An animation on the DOCUMENT clock is the exact opposite. `infinite` means for
the life of the tab: on screen, off screen, or fifteen thousand pixels away,
whether the reader is reading, in another window, or has walked off.

WHAT IT COST HERE. patterns/landing-page.html shipped 128 of them — 126
`.sp-stream > b`, the six readings each of act 1's twenty-one sensor labels
cycle through, plus two copy-stream carets. Act 1 is about 2 300 px of a
22 931 px document. Measured at 1440 x 900 under Chromium 1194, page loaded and
then LEFT COMPLETELY ALONE: no scrolling, no pointer, no keyboard, five seconds
of a still page:

    landing 1440, at the top                1351 ms style recalc per 5 000 ms
                                            299 recalcs — one per frame, 60 Hz
                                            4.5 ms per frame
                                            2246 ms total task time     (45 %)
    landing 1440, act 5 on screen             1395 ms — same cost, and act 1 is
      and act 1 fifteen thousand px away        fifteen thousand pixels away
    landing 1440, those 128 cancelled           319 ms            (-76 %)
    landing 1440, prefers-reduced-motion          0 ms
    landing  375                                  0 ms
    patterns/expertise.html 1440                  0 ms
    patterns/kontakt.html   1440                  0 ms

Half the main thread, at every frame, forever, for a readout that is not on the
screen — on the one page in the tree that is also running two scroll-driven
figure systems, a pinned stage and a hero video in those same frames.

AND IT IS NOT A KEYFRAME THAT CAN BE WRITTEN CHEAPER. The property is
`opacity`, which is the cheapest thing in the system and the one the motion
chapter asks for. Substituting ONE `transform` animation on a single empty
4 x 4 px div for all 128 measured 1362 ms in the same five seconds — the same
figure. Nor is it a count: twenty-six shimmering leaves cost 1375 ms and ONE
costs 1150. What the page pays for is producing frames at all; each frame it
produces then walks a 1 623-element document against 840 KB of stylesheet. So
there is no smaller keyframe and no smaller number of elements. The only lever
is time, and the animation has to be able to stop.

THE RULE, in two halves.

  the stylesheet   every rule in the shipping CSS that starts an `infinite`
                   animation on the document clock must have, in the same
                   stylesheet, a rule that pauses it under `[data-idle]`. The
                   pause is matched on the SELECTOR the animation was declared
                   on, so a new perpetual animation enters this check by
                   existing rather than by somebody adding it to a list here —
                   the same argument check-glass-budget.py makes for reading
                   backdrop-filter out of the CSS instead of naming surfaces.

  the page         a page carrying markup that those selectors reach must mark
                   a box with `data-cf-idle` and load assets/js/cf-idle.js. One
                   without the other is a gate with nothing to open it: the
                   attribute alone is never written, and the script alone has
                   nothing to observe.

ON THE DOCUMENT CLOCK means: this position in the `animation-*` lists is not
given a timeline. `animation-timeline` is a LIST in step with `animation`, so a
leaf declaring three animations and `animation-timeline: --sp, --sp, auto` has
two on a view timeline and its third on the document clock — and only the third
is this file's business. The lists are read positionally for that reason, which
is also the fault that shape of declaration has already caused on this page
once: acts.css's own note over .lp-flow__leaf records `auto` being written into
an `animation-range` list, where it is not a keyword, dropping the whole
declaration.

WHAT IS OUT OF SCOPE, and why. An animation that is not `infinite` ends by
itself, and one whose position carries a named or view timeline never ticks
unless the reader scrolls. Neither can hold a page awake. `docs.css` and
`preview.css` do not ship — the boundary check-spacing-scale.py draws — and
neither does the root generation of the site, which is a directory this file
never reads.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-idle-motion.py        # check, exit 1 on drift
    python3 scripts/check-idle-motion.py -v     # show every rule, not only hits
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
CSS = DS / "assets" / "css"

# The stylesheets that ship to control-f.de, and the same four
# check-glass-budget.py reads for the same reason.
SHIPPING_CSS = ("tokens.css", "base.css", "components.css", "acts.css")

# The pages this system publishes. The root generation is not read: it is the
# generation before this one and has its own copies of everything.
PAGE_DIRS = ("patterns", "prototypes", "foundations", "components")

IDLE_SCRIPT = "cf-idle.js"
IDLE_MARK = "data-cf-idle"

# TRANSIENT BY CONSTRUCTION, and the argument is written beside the key rather
# than asserted. The rule above is about an animation that runs for the LIFE OF
# THE TAB. These two cannot: they are the visible half of a state that ends.
#
#   .cf-arrive__ghost      the placeholder an object stands in for before it
#                          has arrived. components.css's own chapter on it —
#                          "ARRIVAL, the state a thing is in before it is here"
#                          — is explicit that the ghost is REPLACED by the
#                          object when the content lands, not faded out over.
#                          A ghost still animating an hour later is a load that
#                          never finished, which is a different fault.
#   .cf-progress__rail     the indeterminate rail, which by definition is on
#                          screen only while something is running and is the
#                          one thing on the page whose whole message is "this
#                          has not stopped yet". Pausing it while it is off
#                          screen would be pausing the only honest report.
#
# Both are also states a page enters, not furniture it ships: neither exists in
# the markup of a page at rest. The landing page carries neither.
TRANSIENT = (".cf-arrive__ghost", ".cf-progress__rail", ".cf-progress--indeterminate")


def strip_comments(text):
    """Blank out /* ... */ so a measurement quoted in prose is never a rule."""
    return re.sub(r"/\*.*?\*/", lambda m: " " * len(m.group(0)), text, flags=re.S)


def declarations(block):
    """The property: value pairs of one declaration block, top level only."""
    out = []
    depth = 0
    buf = ""
    for ch in block:
        if ch in "({[":
            depth += 1
        elif ch in ")}]":
            depth -= 1
        if ch == ";" and depth == 0:
            out.append(buf)
            buf = ""
        else:
            buf += ch
    out.append(buf)
    pairs = []
    for d in out:
        if ":" not in d:
            continue
        prop, _, val = d.partition(":")
        prop = prop.strip().lower()
        if prop:
            pairs.append((prop, val.strip()))
    return pairs


def split_list(value):
    """Split a comma-separated animation-* list, respecting nesting."""
    parts = []
    depth = 0
    buf = ""
    for ch in value:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(buf.strip())
            buf = ""
        else:
            buf += ch
    parts.append(buf.strip())
    return [p for p in parts if p != ""]


def rules(text):
    """Every (selector, block) pair in a stylesheet, at any nesting depth.

    At-rules are walked into rather than skipped: the declarations this check
    is about live inside @media and @supports, which is the whole shape of the
    file — every perpetual animation on this page is inside a no-preference
    gate already, which is why reduced motion measures 0 ms above.
    """
    found = []
    i = 0
    n = len(text)
    while i < n:
        brace = text.find("{", i)
        if brace == -1:
            break
        prelude = text[i:brace].strip()
        # match the block
        depth = 0
        j = brace
        while j < n:
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        block = text[brace + 1:j]
        prelude = prelude.split("}")[-1].strip()
        if prelude.startswith("@"):
            # An at-rule: its body holds rules, not declarations. @keyframes is
            # the exception — its blocks are keyframe selectors, never these.
            if not prelude.lower().startswith("@keyframes"):
                found.extend(rules(block))
        elif prelude:
            found.append((prelude, block))
        i = j + 1
    return found


def perpetual(block):
    """The indices of this rule's animations that never stop by themselves.

    An animation qualifies when its own position says `infinite` and its own
    position in animation-timeline is the document clock — absent, `auto` or
    `initial`. Both lists are read positionally, which is what the property is.
    """
    names = []
    counts = []
    timelines = []
    for prop, val in declarations(block):
        if prop == "animation":
            names = split_list(val)
            counts = ["infinite" if "infinite" in p.split() else "1" for p in names]
        elif prop == "animation-name":
            names = split_list(val)
        elif prop == "animation-iteration-count":
            counts = split_list(val)
        elif prop == "animation-timeline":
            timelines = split_list(val)
    if not names:
        return []
    hits = []
    for i, name in enumerate(names):
        if name.strip().lower() in ("none", "initial", "unset"):
            continue
        count = counts[i] if i < len(counts) else (counts[-1] if counts else "1")
        if "infinite" not in count.lower():
            continue
        tl = timelines[i].strip().lower() if i < len(timelines) else "auto"
        if tl not in ("auto", "initial", "unset", ""):
            continue          # a view / scroll / named timeline: only ticks on scroll
        hits.append(i)
    return hits


def pauses(block):
    """True when this rule can hold an animation still."""
    for prop, val in declarations(block):
        if prop == "animation-play-state" and "paused" in val.lower():
            return True
        if prop == "animation" and "paused" in val.lower():
            return True
        # `animation: none` removes it outright, which also stops the clock.
        if prop in ("animation", "animation-name") and val.strip().lower() == "none":
            return True
    return False


def keys(selector):
    """The class / element keys a selector rests on, for matching a pause to it.

    The rightmost compound is what identifies the thing being animated, and a
    pause is written beside it rather than as a character-for-character copy of
    the selector — the same reason check-print-fixed.py matches on the key
    instead of the whole thing.
    """
    # :is() and :where() are unwrapped rather than dropped: this file's own
    # pause rules are written as one grouped `:is(...)` beside the declaration
    # they answer, and a regex that ate the parentheses ate the classes with
    # them — the pause was there and the check could not see it.
    sel = re.sub(r"::?(?:is|where|not|has)\(", " ", selector)
    sel = re.sub(r"::?[a-z-]+(\([^)]*\))?", " ", sel)
    sel = sel.replace(",", " ").replace("(", " ").replace(")", " ")
    out = set()
    for part in sel.split():
        for cls in re.findall(r"\.([A-Za-z0-9_-]+)", part):
            out.add("." + cls)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    failures = []
    perpetual_keys = set()
    seen = []

    for name in SHIPPING_CSS:
        path = CSS / name
        if not path.exists():
            continue
        text = strip_comments(path.read_text(encoding="utf-8"))
        all_rules = rules(text)
        paused_keys = set()
        for selector, block in all_rules:
            if "[data-idle]" in selector and pauses(block):
                paused_keys |= keys(selector)
        for selector, block in all_rules:
            if "[data-idle]" in selector:
                continue
            hits = perpetual(block)
            if not hits:
                continue
            sel_keys = keys(selector)
            if sel_keys & set(TRANSIENT):
                seen.append((name, selector + "   [transient]", len(hits)))
                continue
            seen.append((name, selector, len(hits)))
            perpetual_keys |= sel_keys
            if not sel_keys:
                failures.append(
                    "%s: `%s` starts a perpetual animation on a selector with no "
                    "class to pause it by." % (name, selector.strip()))
            elif not (sel_keys & paused_keys):
                failures.append(
                    "%s: `%s` starts %d animation(s) on the document clock with "
                    "`infinite`, and nothing under [data-idle] in this stylesheet "
                    "pauses %s. It will run for the life of the tab.\n"
                    "      Add, beside it:  [data-idle] %s { animation-play-state: paused; }"
                    % (name, selector.strip(), len(hits),
                       " or ".join(sorted(sel_keys)), sorted(sel_keys)[0]))

    # The page half. A page whose markup reaches one of those selectors needs
    # both the mark and the script; neither is any use without the other.
    for sub in PAGE_DIRS:
        d = DS / sub
        if not d.is_dir():
            continue
        for page in sorted(d.glob("*.html")):
            html = page.read_text(encoding="utf-8")
            # HTML comments, not CSS ones. Every page that carries this gate
            # also EXPLAINS it in a comment beside the mark, naming the file —
            # so a check that searched the raw text found the script tag in the
            # prose that describes the script tag, and deleting the tag passed.
            # Verified by deleting it: this is the line that makes that fail.
            body = re.sub(r"<!--.*?-->", " ", html, flags=re.S)
            touched = sorted(k for k in perpetual_keys
                             if re.search(r'class="[^"]*\b%s\b' % re.escape(k[1:]), body))
            if not touched:
                continue
            rel = page.relative_to(ROOT)
            has_mark = IDLE_MARK in body
            has_script = IDLE_SCRIPT in body
            if not has_script:
                failures.append(
                    "%s: carries %s, which animate forever on the document clock, "
                    "and does not load assets/js/%s. Nothing will ever write "
                    "data-idle, so the pause rules can never match."
                    % (rel, ", ".join(touched), IDLE_SCRIPT))
            elif not has_mark:
                failures.append(
                    "%s: loads %s and marks no box with %s, so the observer has "
                    "nothing to watch and the animations never stop."
                    % (rel, IDLE_SCRIPT, IDLE_MARK))
            elif args.verbose:
                print("  ok  %s  gates %s" % (rel, ", ".join(touched)))

    if args.verbose:
        print("perpetual animations declared in the shipping stylesheets:")
        for name, selector, n in seen:
            print("  %-16s %-46s %d" % (name, selector.strip()[:46], n))

    if failures:
        print("check-idle-motion: %d problem(s).\n" % len(failures))
        for f in failures:
            print("  " + f)
        print("\nAn animation with `infinite` on the document clock keeps the page "
              "\nproducing frames for the life of the tab. On the landing page that "
              "\nwas measured at 45 % of the main thread with nobody touching it. "
              "\nSee this file's header for the numbers and the two halves of the rule.")
        return 1

    print("check-idle-motion: ok — %d perpetual animation rule(s), every one "
          "reachable by the idle gate." % len(seen))
    return 0


if __name__ == "__main__":
    sys.exit(main())
