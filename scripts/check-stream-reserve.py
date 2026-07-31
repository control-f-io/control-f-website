#!/usr/bin/env python3
"""A box reserved for a typewriter is reserved in the tier that types.

cf-stream.js writes a copy run character by character as the reader scrubs a
pinned track. A box whose text grows line by line reflows everything under it,
so each streamed run is given a floor — min-block-size, sized to the longest
line count the run reaches — and the composition stands still while the
characters land. That is the whole reason the floors exist, and the file that
needs them says so in its own header:

    It refuses to run unless the pinned layout is actually active — no support
    for scroll-driven animations, reduced motion, or a viewport below the
    consumer's own gate all mean the section is in its stacked state, where
    every stage is on screen at once and typing one of them would be nonsense.

So there is exactly one tier in which a streamed box ever reflows, and it is
the tier behind `@supports (animation-timeline: view())`. Everywhere else the
copy is ordinary markup, whole and at rest from the first paint: below the
gate, under prefers-reduced-motion, in a browser without view timelines, and
in print. In those tiers a floor is not holding anything up. It is the height
of a sentence that is not coming, added to a paragraph that is already the
height it wants to be.

WHAT WENT WRONG. acts.css declared all six of its floors on the base rules —
.sp-say__lead/__body, .sp4-say__lead/__body and .map-beat__lead/__body — which
is every tier, for a mechanic that exists in one. Measured as the box's height
minus the same box's natural height with the floor lifted, JavaScript on, at
rest, on patterns/landing-page.html:

                                        320   375   768  1023   1440
      .sp-say__lead   x2  (2.3em)        36    36    36    36     —
      .sp4-say__lead  "Und das ganze
                       Team"  (2.4em)    30    30    30    30     —
      .sp4-say__lead  plate 01            —     —    30    30     —
      .sp4-say__body  x2 (7.4 / 5.2em)    —     —    63    63     —
      .map-beat__body x2  (4.6em)         —     —    54    54     —
      page total                         66    66   213   213      0

1440 is the gate met, where every floor is load-bearing. The rest is padding.
The visible fault was act 4's second plate: "Und das ganze Team" is one line
in a box reserving two, so on a phone that heading stood 30 px clear of the
paragraph it heads while the plate directly above it — a name that wraps to
two lines — had none. One section, two plates, two rhythms, and the thing that
decided which was which was whether a headline happened to wrap.

components.css has the system's only other instance of the device,
.cf-values__title/__body on ueber-uns, and it has been inside its own
@supports block since it was written, with a comment giving this same reason.
So the system already had the rule; acts.css restated it one gate too high.

WHAT IT CHECKS. The streamed runs are read from the markup rather than listed
here — every element carrying data-stream-line under design-system/, by class
— so a new consumer is covered the day it is authored. For each of the four
shipping stylesheets, with comments stripped, every declaration of
min-block-size or min-height on a selector naming one of those classes must sit
inside an @supports prelude that tests animation-timeline. A floor outside it
is a floor charged to every tier for a mechanic only one tier has.

It does not check the VALUES: how many lines a run needs is a judgement about
copy, and the gate is about where the judgement applies, not what it is.
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DS = os.path.join(ROOT, "design-system")
CSS_DIR = os.path.join(DS, "assets", "css")

# The shipping set. docs.css and preview.css are documentation chrome.
SHEETS = ("tokens.css", "base.css", "components.css", "acts.css")

RESERVE = ("min-block-size", "min-height")

# The element that carries the streamed text, and the attribute cf-stream.js
# divides a track by. Only the line runs get a floor; the stage is a container.
STREAM_ATTR = "data-stream-line"


def strip_comments(text):
    return re.sub(r"/\*.*?\*/", "", text, flags=re.S)


def streamed_classes():
    """The classes that mean "this box holds a streamed run", read from markup.

    A class earns the name only if EVERY element wearing it in design-system/
    is streamed, and two different things fall out of that test.

    The shared utilities go first: the streamed elements also carry t-label on
    two of the marks and text-foil on a title, and those are worn by hundreds
    of boxes that never type a character. A floor on .t-label would be a
    decision about a label, not about a typewriter, and this check has nothing
    to say about it.

    So do the component classes a specimen page uses unstreamed —
    .cf-info-card__title streams on four cards in patterns/expertise.html and
    stands still on three in components/info-card.html. A floor there would
    apply to both, so which tier it belongs in is a question about the
    component and not one this check can answer from the markup. Only classes
    that are streamed everywhere they appear have an unambiguous answer, and
    those are the ones it holds. The list is read rather than kept here, so a
    new consumer is covered the day it is authored.
    """
    worn = {}       # class -> how many elements wear it
    typed = {}      # class -> how many of those are streamed
    pages = {}      # class -> the pages it streams on
    for base, _dirs, files in os.walk(DS):
        for fn in sorted(files):
            if not fn.endswith(".html"):
                continue
            path = os.path.join(base, fn)
            with open(path, encoding="utf-8") as fh:
                html = fh.read()
            rel = os.path.relpath(path, DS)
            for tag in re.findall(r"<[a-zA-Z][^>]*?>", html, flags=re.S):
                m = re.search(r'\bclass\s*=\s*"([^"]*)"', tag)
                if not m:
                    continue
                is_stream = STREAM_ATTR in tag
                for cls in m.group(1).split():
                    worn[cls] = worn.get(cls, 0) + 1
                    if is_stream:
                        typed[cls] = typed.get(cls, 0) + 1
                        pages.setdefault(cls, set()).add(rel)
    return {cls: pages[cls] for cls in typed if typed[cls] == worn[cls]}


def rules(css):
    """(at-rule prelude chain, selector, declaration text) for every rule."""
    out = []
    stack = []          # at-rule preludes currently open
    buf = ""
    i = 0
    n = len(css)
    while i < n:
        ch = css[i]
        if ch == "{":
            prelude = buf.strip()
            buf = ""
            if prelude.startswith("@"):
                stack.append(prelude)
                out.append(None)          # marker: this brace opened an at-rule
            else:
                # a rule: consume to its matching close brace
                depth = 1
                j = i + 1
                while j < n and depth:
                    if css[j] == "{":
                        depth += 1
                    elif css[j] == "}":
                        depth -= 1
                    j += 1
                out.append((tuple(stack), prelude, css[i + 1:j - 1]))
                i = j
                continue
        elif ch == "}":
            if stack and out and out[-1] is None:
                pass
            if stack:
                stack.pop()
            buf = ""
        else:
            buf += ch
        i += 1
    return [r for r in out if r]


def gated(chain):
    """Is this at-rule chain behind an @supports test of animation-timeline?"""
    for prelude in chain:
        if prelude.startswith("@supports") and "animation-timeline" in prelude:
            return True
    return False


def main():
    classes = streamed_classes()
    if not classes:
        print("stream reserve: no %s in design-system/ — nothing to hold." % STREAM_ATTR)
        return 1

    findings = []
    census = []
    for sheet in SHEETS:
        path = os.path.join(CSS_DIR, sheet)
        with open(path, encoding="utf-8") as fh:
            css = strip_comments(fh.read())
        held = 0
        for chain, selector, body in rules(css):
            hits = sorted(c for c in classes if re.search(r"\.%s\b" % re.escape(c), selector))
            if not hits:
                continue
            for decl in body.split(";"):
                if ":" not in decl:
                    continue
                prop, value = decl.split(":", 1)
                prop = prop.strip()
                if prop not in RESERVE:
                    continue
                if gated(chain):
                    held += 1
                else:
                    findings.append((sheet, selector.strip(), prop, value.strip(),
                                     ", ".join(hits), chain))
        census.append((sheet, held))

    print("stream reserve: %d streamed class(es) — %s"
          % (len(classes), ", ".join(sorted(classes))))

    if findings:
        print("\nstream reserve: %d finding(s)\n" % len(findings))
        for sheet, selector, prop, value, hits, chain in findings:
            where = " > ".join(chain) if chain else "top level"
            print("  - %s  %s" % (sheet, selector))
            print("        %s: %s;" % (prop, value))
            print("    reserves a box for a streamed run (%s) at %s, which is every"
                  % (hits, where))
            print("    tier — and cf-stream.js runs only behind")
            print("    @supports (animation-timeline: view()). Outside it the copy is")
            print("    whole markup at rest and the floor is dead air.\n")
        return 1

    total = sum(c[1] for c in census)
    print("%d reservation(s), all inside @supports (animation-timeline: view()):"
          % total)
    for sheet, held in census:
        print("  %-16s %d" % (sheet, held))
    return 0


if __name__ == "__main__":
    sys.exit(main())
