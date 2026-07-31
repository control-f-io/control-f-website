#!/usr/bin/env python3
"""The folded bar's touch floor is one number, and every control in the bar meets it.

WHAT WENT WRONG, AND HOW IT WENT WRONG TWICE. components.css states the touch
convention in prose on .cf-nav__toggle: 2.75rem — 44 px, WCAG 2.5.5, Apple's
HIG — "the primary control on a phone: the only way to reach any other page."
The toggle got that floor, and the note was right about why. But the toggle is
not the control that reaches any other page; it is the control that opens the
six that do. Those six rows kept the bar's desktop metric — 11 px mono inside
--space-2 padding, a 32 px row, six of them 4 px apart — in the disclosure
panel and in the no-script stacked fallback alike, on every pattern page, at
every width below the fold threshold. Measured at 375: toggle 44, each row it
discloses 32.

That is the same fault the toggle's own fix answered, one element deeper, and
it survived precisely because the statement lived in a comment. A comment
binds nothing. The first fix raised one control and wrote the reason beside
it; nothing read the reason back against the control's siblings, so the floor
held for exactly the element it was typed on.

WHAT THIS KNOWS THAT A SCREENSHOT CANNOT. A 32 px row and a 44 px row are both
"a row you can read"; nothing renders wrong, nothing overlaps, no checker of
colour or contrast or overflow has anything to say. The failure only exists at
the width of a fingertip, and the fingertip is not in the screenshot. But the
floor is countable in the file: the folded bar lives in one @media block in
components.css, and the controls inside it either carry the minimum or do not.

THE RULE. In every `@media (max-width: 48.75rem)` block of components.css,
each of the folded bar's control classes — .cf-nav__toggle and .cf-nav__link —
must declare `min-height`, the declared values must all be one number (a floor
stated twice as two numbers is two floors), and that number must be at least
2.75rem (44 px). The threshold literal is read from the file, not restated as
a second copy here beyond the block prelude this check must find; the register
in tokens.css owns the number 48.75rem, and scripts/check-breakpoints.py keeps
that register honest.

Reintroduce the bug — drop min-height from the folded .cf-nav__link rule, or
lower either floor below 2.75rem — and this fails, naming the class and the
value it found.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system/assets/css/components.css"

FOLD_PRELUDE = re.compile(r"@media\s*\(\s*max-width:\s*48\.75rem\s*\)")
CONTROLS = (".cf-nav__toggle", ".cf-nav__link")
FLOOR_REM = 2.75


def strip_comments(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def media_blocks(css: str):
    """Yield the body of every folded-bar @media block, by brace matching."""
    for m in FOLD_PRELUDE.finditer(css):
        i = css.index("{", m.end())
        depth, j = 1, i + 1
        while depth and j < len(css):
            if css[j] == "{":
                depth += 1
            elif css[j] == "}":
                depth -= 1
            j += 1
        yield css[i + 1 : j - 1]


def rules(block: str):
    """(selector, body) pairs at any nesting depth inside a media block."""
    depth, sel_start = 0, 0
    stack = []
    for i, ch in enumerate(block):
        if ch == "{":
            stack.append(block[sel_start:i].strip().split("}")[-1].strip())
            depth += 1
            sel_start = i + 1
        elif ch == "}":
            body_start = sel_start
            depth -= 1
            if stack:
                yield stack.pop(), block[body_start:i]
            sel_start = i + 1


def to_rem(value: str):
    value = value.strip()
    m = re.fullmatch(r"([\d.]+)rem", value)
    if m:
        return float(m.group(1))
    m = re.fullmatch(r"([\d.]+)px", value)
    if m:
        return float(m.group(1)) / 16
    return None


def main() -> int:
    css = strip_comments(CSS.read_text(encoding="utf-8"))
    floors = {}  # control class -> list of (selector, rem value)

    for block in media_blocks(css):
        for sel, body in rules(block):
            for control in CONTROLS:
                if control not in sel:
                    continue
                for decl in re.finditer(r"min-height\s*:\s*([^;}]+)", body):
                    rem = to_rem(decl.group(1))
                    floors.setdefault(control, []).append((sel, decl.group(1).strip(), rem))

    failures = []
    for control in CONTROLS:
        found = floors.get(control, [])
        if not found:
            failures.append(
                f"{control}: no min-height declared in any folded-bar block — "
                f"the rows are back at the type's own 32 px"
            )
            continue
        for sel, raw, rem in found:
            if rem is None:
                failures.append(f"{control}: min-height '{raw}' on '{sel}' is not a length this check can read")
            elif rem < FLOOR_REM:
                failures.append(f"{control}: min-height {raw} on '{sel}' is below the {FLOOR_REM}rem floor")

    stated = {rem for entries in floors.values() for (_, _, rem) in entries if rem is not None}
    if len(stated) > 1:
        failures.append(
            "the floor is stated as more than one number ("
        + ", ".join(f"{v}rem" for v in sorted(stated))
        + ") — a floor stated twice as two numbers is two floors"
        )

    if failures:
        print("check-touch-floor: the folded bar's touch floor does not hold:")
        for f in failures:
            print(f"  - {f}")
        return 1

    n = sum(len(v) for v in floors.values())
    print(
        f"check-touch-floor: OK — {n} min-height declaration(s) across "
        f"{len(floors)} folded-bar control class(es), all at >= {FLOOR_REM}rem, one number"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
