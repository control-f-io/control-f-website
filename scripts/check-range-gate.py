#!/usr/bin/env python3
"""A scroll-driven block must gate on `animation-range`, not only on `view()`.

Feature-testing `animation-timeline: view()` and then timing the whole
choreography with `animation-range` assumes one implementation ships both. One
does not. Firefox has `animation-timeline: view()` and `view-timeline-name` and
has never had `animation-range` — neither the shorthand nor the two longhands:

    CSS.supports('animation-timeline', 'view()')                -> true
    CSS.supports('animation-range', 'contain 0% contain 100%')  -> false
    CSS.supports('animation-range-start', 'contain 6%')         -> false

So a gate written `@supports (animation-timeline: view())` admits Firefox into
the pinned tier and then hands it 898 animations whose ranges all compute to the
empty string. Every one of them runs over the entire timeline instead of its own
staggered slice, and they run at once. Measured on the landing page before this
check existed: Chromium resolved `contain 6% contain 14%`, `contain 8.4% contain
16.4%`, … per element; Firefox resolved `""` for all 600 animated elements. What
that draws is not a degraded build, it is a different picture — act 1's sensor
field came up as dozens of strokes at wrong angles across the headline, and the
section title rendered as "WAS W:" and "4 SC".

The fallback tier is the designed answer for a browser that cannot run the
choreography, and it is good. The gate simply has to name every feature the
block behind it needs, so a browser missing any one of them takes that tier
instead of a broken half of this one.

THE RULE: an `animation-range` declaration must be inside an `@supports` whose
condition tests `animation-range`. Nesting counts — the condition may be on the
block itself or on any `@supports` enclosing it.

Blocks that gate on `animation-timeline` and carry no `animation-range` are not
touched: they run on the default range in both engines, which is what they want.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SOURCES = sorted((ROOT / "design-system/assets/css").glob("*.css")) + \
          sorted((ROOT / "design-system/patterns").glob("*.html"))


def blank_comments(css):
    """Comments in these files quote CSS at length — including the declarations
    this script looks for. Blanked in place so every line number still holds."""
    return re.sub(r"/\*.*?\*/",
                  lambda m: re.sub(r"[^\n]", " ", m.group(0)), css, flags=re.S)


def blank_preludes(css):
    """Blank the text between `@supports` and its `{`. The gate's own condition
    names `animation-range` — that is the point of it — and must not be read as
    a declaration sitting outside itself."""
    return re.sub(r"@supports[^{]*",
                  lambda m: re.sub(r"[^\n]", " ", m.group(0)), css)


def violations(css):
    """Every `animation-range` declaration with no `animation-range` in the
    condition of any @supports enclosing it, as (line, condition) pairs."""
    css = blank_comments(css)
    scan = blank_preludes(css)      # same length, so indices still line up
    out = []
    stack = []          # (is_supports, condition) per open brace
    i = 0
    while i < len(css):
        ch = css[i]
        if ch == "{":
            head = css[max(0, i - 400):i]
            m = re.search(r"@supports([^{}]*)$", head)
            stack.append((True, m.group(1)) if m else (False, ""))
            i += 1
            continue
        if ch == "}":
            if stack:
                stack.pop()
            i += 1
            continue
        m = re.match(r"animation-range(-start|-end)?\s*:", scan[i:])
        if m and (i == 0 or not re.match(r"[\w-]", scan[i - 1])):
            gated = any(is_s and "animation-range" in cond for is_s, cond in stack)
            if not gated:
                enclosing = " / ".join(c.strip().replace("\n", " ")
                                       for s, c in stack if s) or "(no @supports)"
                out.append((css[:i].count("\n") + 1, enclosing[:90]))
            i += m.end()
            continue
        i += 1
    return out


def main():
    failures = 0
    checked = 0
    for path in SOURCES:
        css = path.read_text(encoding="utf-8")
        if "animation-range" not in css:
            continue
        checked += 1
        for line, cond in violations(css):
            rel = path.relative_to(ROOT)
            print(f"FAIL  {rel}:{line}  animation-range is not gated on "
                  f"animation-range — enclosing @supports: {cond}")
            failures += 1

    if failures:
        print(f"\n{failures} ungated animation-range declaration(s). Add "
              f"`and (animation-range: contain 0% contain 100%)` to the gate, so "
              f"a browser with view timelines but no ranges — Firefox — takes "
              f"the fallback tier instead of a broken pinned one.")
        return 1

    print(f"range gate OK — every animation-range in {checked} file(s) is "
          f"behind an @supports that tests animation-range")
    return 0


if __name__ == "__main__":
    sys.exit(main())
