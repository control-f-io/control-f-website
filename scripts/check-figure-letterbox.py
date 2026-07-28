#!/usr/bin/env python3
"""Hold the cap on a letterboxed figure box to the cap on the drawing inside it.

THE SHAPE. A "letterboxed figure" in this system is a box that states a RATIO
and centres a drawing in it that states its own SIZE CAP:

    .cf-process__figure       { aspect-ratio: 4/3; place-items: center;
                                padding: var(--space-8); ... }
    .cf-process__figure > svg { width: 100%; max-width: 22rem; ... }

Two rules, two authors, and one silent way for them to disagree: the box's
height comes from its width and the ratio, and NOTHING in either rule stops it
once the drawing has stopped growing. Past the crossover the box keeps taking
its share of every pixel the card gains while the object inside it does not
move.

WHAT IT COST. Measured on patterns/landing-page.html's stacked "Was wir machen"
column, dead height beyond the --space-8 the rule asks for:

    viewport 600   panel 532 x 399   drawing 352 x 334     0 px
    viewport 700   panel 621 x 466   drawing 352 x 352    50 px
    viewport 768   panel 682 x 511   drawing 352 x 352    95 px
    viewport 834   panel 740 x 555   drawing 352 x 352   139 px
    viewport 1000  panel 888 x 666   drawing 352 x 352   250 px

At 834 the panel was 63 % of the card's height to show an object covering 30 %
of its area, and the four cards stood 3 678 px between them against 3 125 with
the cap. Nothing about it was broken: no overflow, no clipped drawing, no
failing check. It renders correctly and it is 553 px of nothing on the widest
phone-shaped screen the page has.

THE INVARIANT, and it is an arithmetic one so a script can hold it. The box may
not be taller than the drawing it is there to hold, plus the air the box itself
declares:

    max-block-size == <the svg's max-width> + 2 x <the box's padding> + <border>

Everything is border-box (base.css:49), so the border the box draws is inside
that number: leave it out and the content box lands a pixel under the drawing's
own cap, which is the pixel --trace-weight is derived from (640/352 = 1.00 CSS
px on the contour).

WHY A SCRIPT AND NOT A NOTE. The two rules are 90 lines apart and each is
individually correct. Change 22rem to 24rem on the drawing and the box silently
stops fitting it; change --space-8 to --space-6 in the padding and the box
silently gains 16 px of dead air. Neither edit looks wrong at the line it is
made on, and neither shows in a screenshot at the three widths anybody checks.

SCOPE is the shipping stylesheets — tokens.css, base.css, components.css. A
letterboxed figure is a component, not page furniture; docs.css is documentation
chrome and is out, the same call every check here makes. A rule inside a
@container or @media block is read with its prelude attached, so the two-column
form's `max-block-size: none` is seen for what it is: that form is square BESIDE
the copy and its height is the row's, which is a documented release rather than
a missing cap, and it is listed in RELEASED below with its reason.

stdlib only, no build step, no dependency — the same contract as the
forty-four checks beside it.

    python3 scripts/check-figure-letterbox.py       # check, exit 1 on a finding
    python3 scripts/check-figure-letterbox.py -v    # print every pair found
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system" / "assets" / "css"
SHEETS = ["tokens.css", "base.css", "components.css"]

# The space scale, read rather than restated: a padding written as
# var(--space-8) has to resolve to a length before it can be added to anything.
SPACE_RE = re.compile(r"--space-(\d+):\s*([0-9.]+)rem")
STROKE_RE = re.compile(r"--stroke-(\d+):\s*([0-9.]+)px")

# A selector whose cap is deliberately released, with the reason it is released.
# A release is a design decision that has to be written down; an absent cap is
# the bug this file exists to catch.
RELEASED = {
    "@container (min-width: 56rem) .cf-process__figure":
        "square BESIDE the copy: its right border IS the card's divider, so its "
        "height has to be the row's or the hairline stops short of what it divides",
}


def strip_comments(text):
    """Blank out /* ... */ so a number inside prose is never read as a value."""
    out, i = [], 0
    while True:
        start = text.find("/*", i)
        if start < 0:
            out.append(text[i:])
            return "".join(out)
        out.append(text[i:start])
        end = text.find("*/", start + 2)
        if end < 0:
            return "".join(out)
        # keep newlines so reported line numbers stay true
        out.append("\n" * text.count("\n", start, end + 2))
        i = end + 2


def read_tokens():
    text = (CSS / "tokens.css").read_text(encoding="utf-8")
    space = {f"--space-{n}": float(v) * 16 for n, v in SPACE_RE.findall(text)}
    stroke = {f"--stroke-{n}": float(v) for n, v in STROKE_RE.findall(text)}
    return space, stroke


def to_px(value, space, stroke):
    """Resolve one length — a token, a rem literal or a px literal — to px."""
    value = value.strip()
    m = re.fullmatch(r"var\((--[a-z0-9-]+)(?:,[^)]*)?\)", value)
    if m:
        name = m.group(1)
        if name in space:
            return space[name]
        if name in stroke:
            return stroke[name]
        return None
    m = re.fullmatch(r"([0-9.]+)rem", value)
    if m:
        return float(m.group(1)) * 16
    m = re.fullmatch(r"([0-9.]+)px", value)
    if m:
        return float(m.group(1))
    if value == "0":
        return 0.0
    return None


def calc_px(value, space, stroke):
    """Resolve a calc() of sums and `x 2` products to px. Anything else -> None."""
    value = value.strip()
    m = re.fullmatch(r"calc\((.*)\)", value, re.S)
    if not m:
        return to_px(value, space, stroke)
    total = 0.0
    for term in re.split(r"\s\+\s", m.group(1)):
        term = term.strip()
        factor = 1.0
        mult = re.fullmatch(r"(.*?)\s*\*\s*([0-9.]+)", term)
        if mult:
            term, factor = mult.group(1), float(mult.group(2))
        px = to_px(term, space, stroke)
        if px is None:
            return None
        total += px * factor
    return total


RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}")


def rules_with_prelude(text):
    """Every declaration block, paired with the at-rule preludes enclosing it."""
    out, stack, i, n = [], [], 0, len(text)
    buf_start = 0
    while i < n:
        ch = text[i]
        if ch == "{":
            head = text[buf_start:i].strip()
            # An at-rule with a block opens a scope; anything else is a rule.
            close = find_close(text, i)
            if head.startswith("@"):
                stack.append(head)
                i += 1
                buf_start = i
                continue
            body = text[i + 1:close]
            line = text.count("\n", 0, buf_start) + 1
            out.append((" ".join(stack), head, body, line))
            i = close + 1
            buf_start = i
            continue
        if ch == "}":
            if stack:
                stack.pop()
            i += 1
            buf_start = i
            continue
        i += 1
    return out


def find_close(text, open_idx):
    depth = 0
    for j in range(open_idx, len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return j
    return len(text) - 1


def decls(body):
    out = {}
    for part in body.split(";"):
        if ":" not in part:
            continue
        prop, _, val = part.partition(":")
        out[prop.strip()] = val.strip()
    return out


def selectors(head):
    return [s.strip() for s in head.split(",") if s.strip()]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print every letterboxed figure found")
    args = ap.parse_args()

    space, stroke = read_tokens()
    findings, seen = [], []

    for name in SHEETS:
        path = CSS / name
        text = strip_comments(path.read_text(encoding="utf-8"))
        blocks = rules_with_prelude(text)

        # The drawing's own cap, per selector: `<SEL> > svg { max-width: <L> }`.
        svg_cap = {}
        for prelude, head, body, line in blocks:
            d = decls(body)
            if "max-width" not in d:
                continue
            for sel in selectors(head):
                m = re.fullmatch(r"(.+?)\s*>\s*svg", sel)
                if m:
                    px = to_px(d["max-width"], space, stroke)
                    if px is not None:
                        svg_cap.setdefault(m.group(1).strip(), (d["max-width"], px))

        # A letterboxed figure: states a ratio, centres its content, and has a
        # capped drawing under it.
        for prelude, head, body, line in blocks:
            d = decls(body)
            for sel in selectors(head):
                base = sel.split()[-1] if prelude else sel
                cap = svg_cap.get(sel) or svg_cap.get(base)
                if cap is None:
                    continue
                has_ratio = "aspect-ratio" in d
                if not has_ratio:
                    continue
                key = f"{prelude} {sel}".strip()
                pad = d.get("padding")
                border = None
                for prop in ("border-bottom", "border-right", "border"):
                    if prop in d and d[prop] != "0":
                        border = d[prop].split()[0]
                        break
                mbs = d.get("max-block-size", d.get("max-height"))

                if key in RELEASED:
                    seen.append((name, line, key, "released", RELEASED[key]))
                    continue

                if mbs is None:
                    findings.append(
                        f"{name}:{line}  {key}\n"
                        f"    states aspect-ratio: {d['aspect-ratio']} over a drawing capped at "
                        f"{cap[0]} and no max-block-size.\n"
                        f"    The box grows past its own content: at a width of "
                        f"{cap[1] * 4 / 3:.0f} px it is already taller than the drawing plus its air.\n"
                        f"    Expected max-block-size: calc({cap[0]} + <padding> * 2 + <border>), "
                        f"or an entry in RELEASED with a reason.")
                    continue

                want = cap[1]
                parts = [cap[0]]
                if pad is not None:
                    p = to_px(pad, space, stroke)
                    if p is None:
                        findings.append(f"{name}:{line}  {key}\n"
                                        f"    padding {pad!r} is not a length this check can add up.")
                        continue
                    want += 2 * p
                    parts.append(f"{pad} * 2")
                if border is not None:
                    bpx = to_px(border, space, stroke)
                    if bpx is None:
                        findings.append(f"{name}:{line}  {key}\n"
                                        f"    border width {border!r} is not a length this check can add up.")
                        continue
                    want += bpx
                    parts.append(border)

                got = calc_px(mbs, space, stroke)
                if got is None:
                    findings.append(
                        f"{name}:{line}  {key}\n"
                        f"    max-block-size {mbs!r} is not a sum this check can resolve.\n"
                        f"    Expected calc({' + '.join(parts)}) = {want:.0f} px.")
                elif abs(got - want) > 0.5:
                    findings.append(
                        f"{name}:{line}  {key}\n"
                        f"    max-block-size resolves to {got:.0f} px; the drawing under it caps at "
                        f"{cap[0]} ({cap[1]:.0f} px) and this box declares "
                        f"{'padding ' + pad if pad else 'no padding'}"
                        f"{' and a ' + border + ' border' if border else ''}.\n"
                        f"    Expected calc({' + '.join(parts)}) = {want:.0f} px — "
                        f"{'dead air' if got > want else 'the drawing is clipped'} by "
                        f"{abs(got - want):.0f} px.")
                else:
                    seen.append((name, line, key, f"{got:.0f} px",
                                 f"= {' + '.join(parts)}"))

    if args.verbose or not findings:
        for name, line, key, state, note in seen:
            print(f"{name}:{line}  {key}\n    cap {state}  {note}")

    if findings:
        print(f"figure letterbox: {len(findings)} finding(s)\n")
        for f in findings:
            print("  - " + f + "\n")
        return 1

    print(f"figure letterbox: {len(seen)} letterboxed figure(s), every cap derived.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
