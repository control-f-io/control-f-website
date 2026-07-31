#!/usr/bin/env python3
"""acts.css is written base tier first, gated tier second. Hold it to that.

The file says it about itself, in its own opening paragraph, and calls the
order load-bearing:

    THE BASE TIER COMES FIRST AND THE GATED TIER SECOND, throughout, and that
    order is load-bearing rather than tidy — see the note above the @supports
    block. At equal specificity the cascade decides on source order, and a base
    rule authored after the gated one wins in both tiers. It has cost two
    defects in this file already.

Two defects, a rule written down twice, and nothing that reads it. A stylesheet
this size is not kept in order by a paragraph asking nicely: the gated block for
acts 1 and 2 is roughly 1,500 lines long, so "before the gate" and "after the
gate" are not places an author can see at once, and every base-tier declaration
authored near the selectors it belongs with lands after it.

WHAT IT IS. acts.css composes in two tiers. The base tier is the page every
reader gets: every viewport under 64rem, every viewport under 45rem tall, every
reader with prefers-reduced-motion set, every browser without animation-timeline
and every printer. The gated tier — inside `@supports (animation-timeline:
view())` — is the pinned, scrubbed composition. Neither is a fallback for the
other; they are two designs, and the gate is which one is in play.

A media query adds no specificity, so `@supports … { .x { margin-top: 12px } }`
and a plain `.x { margin-top: 80px }` weigh exactly the same and the later one
wins — INCLUDING inside the gate, where the gated value was the point. The
author sees a base-tier default and a gated override; the browser sees the base
tier silently overriding the gated tier at every width.

WHAT IS CHECKED. Every (selector, property) pair declared inside a gated block,
against every pair declared at base tier after that block closes. Any pair in
both is reported with both line numbers. Selector terms are compared whole and
verbatim — `.sp-head` does not answer for `.sp-head__title`, and a pair that
differs by so much as a descendant combinator is a different rule with different
specificity, which this check does not model and does not claim to.

@keyframes and @property bodies are blanked before the scan: `from`/`to` are not
selectors, and every act's keyframes are authored beside the gated rules that
run them. Comments are blanked in place rather than deleted, because this file
quotes its own CSS at length and the line numbers have to survive.

WHAT IT DOES NOT CLAIM. Not that a selector may not appear in both tiers — that
is the normal shape, and the base declaration simply has to come first. Not
anything about specificity: a base rule that deliberately outweighs the gated
one is a different decision, and it is not what the file's own paragraph is
about. Not any other stylesheet — components.css and base.css have no gate of
this kind, and the two-tier discipline is this file's.

FOUND BY WALKING INTO IT. This check was written after the fix for the handover
line's missing top margin. `.sp-head` carries `margin-top: var(--space-3)` in
the gated tier and needed a base-tier value; the obvious home for it was beside
the other .sp-head declarations, which sit 1,300 lines further down and 50 lines
after the gate closes. Written there it would have taken the gated 12 px away
from the pinned stage at every width above 1024 and left the rule floating 80 px
off the drawing's feet — the third defect, in the same file, in the change that
was citing the paragraph.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-tier-order.py
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ACTS = ROOT / "design-system/assets/css/acts.css"

# The gate the acts' choreography is behind. acts.css opens two of these — acts
# 1 and 2 take the first, act 5 the second — and both are checked.
GATE = "@supports (animation-timeline: view())"

# Blanked before the scan: their block contents are not selectors, and they are
# authored beside the gated rules that use them.
BLANK_AT = ("keyframes", "property")


def fail(msg):
    print(f"FAIL  {msg}")
    return 1


def blank_comments(css):
    """Comments quote CSS at length in this file — including declarations this
    script looks for. Blanked in place so every line number still holds."""
    return re.sub(r"/\*.*?\*/",
                  lambda m: re.sub(r"[^\n]", " ", m.group(0)), css, flags=re.S)


def blank_at_blocks(css, name):
    """Blank `@name … { … }` whole, newlines kept, braces balanced by count."""
    out = list(css)
    for m in re.finditer(r"@" + name + r"\b[^{]*\{", css):
        depth = 0
        for k in range(m.end() - 1, len(css)):
            if css[k] == "{":
                depth += 1
            elif css[k] == "}":
                depth -= 1
                if depth == 0:
                    for x in range(m.start(), k + 1):
                        if out[x] != "\n":
                            out[x] = " "
                    break
    return "".join(out)


def gate_spans(css):
    """(start, end) of every gated block, end exclusive of nothing — the closing
    brace is included. Found by counting braces from the block's opening one."""
    spans = []
    i = 0
    while True:
        i = css.find(GATE, i)
        if i < 0:
            return spans
        j = css.find("{", i)
        if j < 0:
            return spans
        depth = 0
        for k in range(j, len(css)):
            if css[k] == "{":
                depth += 1
            elif css[k] == "}":
                depth -= 1
                if depth == 0:
                    spans.append((i, k + 1))
                    i = k + 1
                    break
        else:
            return spans


def rules(css, start, end):
    """(term, property, offset) for every declaration in css[start:end].

    A style rule is a prelude with no braces in it followed by a body with none
    either — which is what every rule in this file is once the at-blocks are
    blanked. At-rule preludes are skipped; their inner rules are matched on
    their own pass, which is what nesting a base rule in an @media should be.
    """
    for m in re.finditer(r"([^{}]*)\{([^{}]*)\}", css[start:end]):
        prelude = m.group(1).strip()
        if not prelude or prelude.startswith("@"):
            continue
        terms = [t.strip() for t in prelude.split(",") if t.strip()]
        props = [d.split(":", 1)[0].strip() for d in m.group(2).split(";")
                 if ":" in d]
        for t in terms:
            for p in props:
                if p:
                    yield t, p, start + m.start()


def main():
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()
    raw = ACTS.read_text(encoding="utf-8")
    css = blank_comments(raw)
    for name in BLANK_AT:
        css = blank_at_blocks(css, name)

    def line(pos):
        return css[:pos].count("\n") + 1

    spans = gate_spans(css)
    if not spans:
        return fail(f"acts.css has no `{GATE}` block. The two-tier split this "
                    f"check is about does not exist any more — either the file "
                    f"changed shape or this check is reading the wrong one.")

    # Every pair the gated tier declares, with where it declares it.
    gated = {}
    for a, b in spans:
        for term, prop, pos in rules(css, a, b):
            gated.setdefault((term, prop), []).append(pos)

    # The base tier is everything outside the gated blocks, in order.
    base = []
    prev = 0
    for a, b in spans:
        base.append((prev, a))
        prev = b
    base.append((prev, len(css)))

    bad = 0
    seen = set()
    for s, e in base:
        for term, prop, pos in rules(css, s, e):
            earlier = [g for g in gated.get((term, prop), []) if g < pos]
            if not earlier or (term, prop, pos) in seen:
                continue
            seen.add((term, prop, pos))
            bad |= fail(
                f"acts.css:{line(pos)} — `{term}` declares `{prop}` in the BASE "
                f"tier, after the gated tier declares it at "
                f"{', '.join('acts.css:' + str(line(g)) for g in earlier)}. A "
                f"media or supports query adds no specificity, so this later "
                f"base declaration wins INSIDE the gate as well as outside it, "
                f"and the gated value is dead at every width. Move it above the "
                f"first `{GATE}` block — the file's own opening paragraph asks "
                f"for base tier first, gated tier second, and says the order is "
                f"load-bearing.")

    if bad:
        return bad
    pairs = sum(len(v) for v in gated.values())
    print(f"OK    acts.css: {len(spans)} gated block(s), {pairs} gated "
          f"declaration(s), none of them overridden by a base rule authored "
          f"after them")
    return 0


if __name__ == "__main__":
    sys.exit(main())
