#!/usr/bin/env python3
"""A figure that is not painted must lose its animation, not merely pause it.

The one hundred and twenty-second check, and the second whose subject is what a
page costs while it is being SCROLLED rather than while it sits still. Its
sibling check-idle-motion.py holds the other half of the idle contract: every
`infinite` animation on the document clock must have a `[data-idle]` pause rule
beside it, so a figure fifteen thousand pixels away can stop. That check is
right and this one does not touch it.

WHAT IT MISSES, and what this file exists for. `data-idle` is written by an
IntersectionObserver, so its question is geometric: is this box near the
window. On patterns/landing-page.html the marked box is `.sp-track`, which is
not sticky, and it therefore intersects the viewport for the whole of its own
scroll — every position a reader can be at while still inside act 1 or act 2.
The 126 readouts inside it live in `.sp-annots`, which crossfades to opacity 0
partway through that and stays there. The observer never sees the field leave,
because the box it is asked about never leaves. acts.css carried that as an
open fault under `.sp-stream` for as long as it was known.

Measured on the shipped page at 390 x 844, consent answered, Chromium 1194:
the notes are painted over 250 px of scroll and the readouts were ticking over
3 100 px of it. Twelve times the scroll a reader can see them in, across the
first half of the document.

AND THE VERB IS THE WHOLE OF THIS CHECK. Every measurement this system had
about those 126 animations was taken on a STILL page — no scrolling, no
pointer, five seconds of nothing — where a perpetual animation is the thing
MAKING the page produce frames. Pause it and the frame goes away with it:
-74 %, and cf-idle.js's header is right about that.

A page under a finger is producing frames anyway. A paused animation is still
an animation on the element, and the style update that frame — already
scheduled by the scroll — still walks it. Measured through the acts at
390 x 844 with the CPU throttled 4x, one rAF-paced pass of sixty steps, median
of three, with the readouts' resting state as it then was — all six readings
`display: block`:

    as it stood                        517 elements/frame     2 266 ms recalc
    the same 126 merely PAUSED         491                    1 995
    the same 126 with no animation     136                      689

Pausing bought 5 %. Removing bought 74 %. That is the measurement the verb was
chosen on, and it is the one this script holds.

AND IT IS THE ONE A LATER READER WILL NOT REPRODUCE, which is the other reason
this is a script and not a comment. acts.css puts five readings in six back to
`display: none` under the same attribute — six readings with no animation to
show one at a time is a six-deep overprint, and it flashed for a frame on the
way in before that rule existed. That rule also takes 105 of the 126 animated
boxes out of every frame, so on the shipped page `paused` and `none` measure
170 and 160 over the same band. Anybody who measures the substitution today
finds it costs six per cent and concludes it is free. It is not: it is the
resting state carrying the gate, and the two rules are one mechanism written
twice. Somebody writing `paused` under `[data-dark]` gets something that reads
correct, matches the file next door, renders identically and measures almost
the same — which is exactly the shape of failure this repository writes
scripts for.

THE RULE, in four halves.

  the verb         a `[data-dark]` rule that says anything about animation at
                   all must REMOVE it — `animation: none` or
                   `animation-name: none`. `animation-play-state: paused`
                   under `[data-dark]` fails, and the message says why. At
                   least one rule must do the removing, or the gate governs
                   nothing.

                   A `[data-dark]` rule that declares no `animation-*` property
                   is not the verb and is not held to it. The gate has a second
                   rule of exactly that kind beside the first, and it is not a
                   loophole: `display: block` on all six readings exists only
                   so the animation can cycle them, so the state with no
                   animation has to put the other five back down. Restoring a
                   resting state is the other half of removing an animation,
                   not a way around it.

  the writer       assets/js/cf-idle.js must read the mark and write the
                   attribute. Without both, a marked page has a gate with
                   nothing to open it.

  the page         a page carrying `data-cf-paint` must load cf-idle.js, the
                   same pairing check-idle-motion.py holds for `data-cf-idle`.

  both ends        a mark with no `[data-dark]` rule in the shipping CSS is a
                   mark nothing answers; a `[data-dark]` rule with no mark in
                   any page is a rule nothing writes. Either way one end of
                   the contract has been deleted and the other still looks
                   like it works.

WHAT IS OUT OF SCOPE. Whether a figure SHOULD be marked: that is a judgement
about a drawing and this script has no opinion about drawings. It reads the
mark out of the pages the way check-glass-budget.py reads glass out of the
stylesheets — a second paint-gated figure enters this check by existing.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-idle-paint.py        # check, exit 1 on drift
    python3 scripts/check-idle-paint.py -v     # show every rule, not only hits
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
CSS = DS / "assets" / "css"
JS = DS / "assets" / "js"

# The stylesheets that ship to control-f.de — the same four check-glass-budget.py
# and check-idle-motion.py read, for the same reason.
SHIPPING_CSS = ("tokens.css", "base.css", "components.css", "acts.css")

# The pages this system publishes. The root generation is not read: it is
# generated from these and has its own copy of everything.
PAGE_DIRS = ("patterns", "prototypes", "foundations", "components")

IDLE_SCRIPT = "cf-idle.js"
PAINT_MARK = "data-cf-paint"
DARK_ATTR = "data-dark"


def strip_comments(text):
    """Blank out /* ... */ so a measurement quoted in prose is never a rule."""
    return re.sub(r"/\*.*?\*/", lambda m: " " * len(m.group(0)), text, flags=re.S)


def declarations(block):
    """The property: value pairs of one declaration block, top level only."""
    out, depth, buf = [], 0, ""
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
        if prop and not prop.startswith("--"):
            pairs.append((prop, val.strip()))
    return pairs


def rules(text):
    """Every (selector, block) pair in a stylesheet, at any nesting depth.

    At-rules are walked into rather than skipped: every rule this check is
    about lives inside @media and @supports, which is the shape of the file.
    @keyframes is the exception — its blocks are keyframe selectors.
    """
    found = []
    i, n = 0, len(text)
    while i < n:
        brace = text.find("{", i)
        if brace == -1:
            break
        prelude = text[i:brace].strip()
        depth, j = 0, brace
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
            if not prelude.lower().startswith("@keyframes"):
                found.extend(rules(block))
        elif prelude:
            found.append((prelude, block))
        i = j + 1
    return found


def removes(block):
    """True when this rule takes the animation away rather than holding it."""
    for prop, val in declarations(block):
        if prop in ("animation", "animation-name") and val.strip().lower() in (
                "none", "initial", "unset", "revert"):
            return True
    return False


def only_pauses(block):
    """True when this rule holds the animation still and nothing more."""
    if removes(block):
        return False
    for prop, val in declarations(block):
        if prop == "animation-play-state" and "paused" in val.lower():
            return True
        if prop == "animation" and "paused" in val.lower():
            return True
    return False


def pages():
    """Every source page this system publishes, as (relative path, text)."""
    for name in PAGE_DIRS:
        root = DS / name
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.html")):
            yield path.relative_to(ROOT), path.read_text(encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    failures = []
    dark_rules = []
    removing = []

    # ---- the verb ------------------------------------------------------
    for name in SHIPPING_CSS:
        path = CSS / name
        if not path.exists():
            continue
        text = strip_comments(path.read_text(encoding="utf-8"))
        for selector, block in rules(text):
            if f"[{DARK_ATTR}]" not in selector:
                continue
            flat = " ".join(selector.split())
            dark_rules.append((name, flat))
            if removes(block):
                removing.append((name, flat))
                if args.verbose:
                    print(f"  removes  {name}  {flat}")
                continue
            if not any(p.startswith("animation") for p, _ in declarations(block)):
                # Not the verb: a companion rule restoring the resting state the
                # animation was covering for. See THE RULE, "the verb".
                if args.verbose:
                    print(f"  resting  {name}  {flat}")
                continue
            if only_pauses(block):
                failures.append(
                    f"{name}: {flat}\n"
                    f"    pauses where it must remove. A paused animation is "
                    f"still an animation on\n"
                    f"    the element and the scroll's own style update still "
                    f"walks it: measured 5 %\n"
                    f"    against 74 % for `animation-name: none`, before "
                    f"the resting-state rule\n"
                    f"    beside it began hiding most of the elements and "
                    f"making the substitution\n"
                    f"    measure almost free. See this script's header, and "
                    f"acts.css under .sp-stream.")
            else:
                failures.append(
                    f"{name}: {flat}\n"
                    f"    carries [{DARK_ATTR}] and does not remove an "
                    f"animation. The attribute is\n"
                    f"    written for one purpose; a rule that reads it for "
                    f"anything else has no gate\n"
                    f"    behind it and no measurement under it.")

    # ---- the writer ----------------------------------------------------
    script = JS / IDLE_SCRIPT
    if not script.exists():
        failures.append(
            f"assets/js/{IDLE_SCRIPT} is missing — the mark and the stylesheet "
            f"rule have\n    nothing between them.")
    else:
        source = script.read_text(encoding="utf-8")
        body = source.split("*/", 1)[-1]          # past the header's prose
        if PAINT_MARK not in body:
            failures.append(
                f"assets/js/{IDLE_SCRIPT} does not read [{PAINT_MARK}] — the "
                f"mark in the markup\n    is never observed.")
        if DARK_ATTR not in body:
            failures.append(
                f"assets/js/{IDLE_SCRIPT} does not write {DARK_ATTR} — the "
                f"stylesheet rule can\n    never match.")

    # ---- the page, and both ends ---------------------------------------
    marked = []
    for rel, text in pages():
        if PAINT_MARK not in text:
            continue
        marked.append(rel)
        if IDLE_SCRIPT not in text:
            failures.append(
                f"{rel}: marks [{PAINT_MARK}] and does not load "
                f"assets/js/{IDLE_SCRIPT}.\n"
                f"    The attribute is never written and the figure animates "
                f"unwatched.")

    if marked and not removing:
        failures.append(
            f"{len(marked)} page(s) mark [{PAINT_MARK}] and no shipping "
            f"stylesheet removes an\n"
            f"    animation on [{DARK_ATTR}]. The gate opens and closes on "
            f"nothing.")
    if dark_rules and not marked:
        failures.append(
            f"{len(dark_rules)} rule(s) read [{DARK_ATTR}] and no page marks "
            f"[{PAINT_MARK}].\n"
            f"    Nothing writes the attribute, so the rules never match.")

    if failures:
        print("check-idle-paint: the paint gate is not intact\n")
        for f in failures:
            print(f"  {f}\n")
        return 1

    print(f"check-idle-paint: {len(removing)} of {len(dark_rules)} "
          f"[{DARK_ATTR}] rule(s) remove an animation, "
          f"{len(marked)} page(s) marked, {IDLE_SCRIPT} writes it")
    return 0


if __name__ == "__main__":
    sys.exit(main())
