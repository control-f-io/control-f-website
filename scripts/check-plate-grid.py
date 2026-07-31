#!/usr/bin/env python3
"""The box a hairline is drawn ON lands on whole pixels.

THE SEAM THIS IS WRITTEN AGAINST. The pinned "Was wir machen" stage gives its
plate's border to a drawing: `.lp-proc-plate` sets `border-color: transparent`
and `.lp-frame` puts six 1 px paths under `vector-effect: non-scaling-stroke`
exactly where that border stood. acts.css records one fix at that seam already
-- the frame's box was the plate's PADDING box, 0.94 px inside the border box,
so the contour stood a pixel off the line it replaced. What nobody then asked is
what the contour PAINTS once it is in the right place, and the answer was
different on different edges of the same rectangle.

`.container` places the plate with two terms that are fractions of the viewport
below --container-max:

    padding-inline: var(--gutter)                       clamp(1.25rem, 5.5vw, 5rem)
    max-width:      calc(var(--container-max) + var(--gutter) * 2)

so the box starts at 5.5vw exactly -- 56.31 px at 1024, 70.39 px at 1280 -- and
a 1 px stroke centred on 70.39 has no whole column to land in. Read off the
render at device scale 1, mid-pinned-run, as the number of pixel columns each
vertical is spread across and the darkest of them against a 225 ground:

    1024 x 768   left 56.31  2px 106.8   mid 512.00  3px 102.8   right  967.69  3px 116.8
    1280 x 800   left 70.39  2px 103.5   mid 640.00  3px 116.4   right 1209.61  3px  92.4
    1440 x 900   left 79.98  2px 100.8   mid 719.99  2px 100.8   right 1360.00  2px 100.4

1440 is what a frame should read as: one line, three times. 1280 is a rectangle
whose middle rail carries a quarter less ink than its right one and whose base
rail is 123.3 against a top rail of 74.8. It is the corner-that-does-not-close
finding one step finer -- the geometry is exact and the ink is not -- and it is
invisible in review for the same reason that one was: nothing about a hairline
announces that it is painting at half strength.

WHY THIS IS A SCRIPT AND NOT A NUMBER IN A COMMENT. The rounding is written as
the CONTAINER'S OWN EXPRESSIONS wrapped in round(), not as literals, so that
`.lp-proc-stage` cannot drift away from the box it is rounding. That only helps
if something reads both sides. base.css is free to change how a container is
placed; when it does, this check fails and the frame's rounding is restated
against the new formula, instead of rounding a term the container no longer
uses -- which would place the stage somewhere the rest of the page is not, and
that is a worse bug than the one being fixed.

WHAT IS CHECKED

  1. base.css's `.container` still places its box with `max-width` and
     `padding-inline`. If it stops, the premise is gone and this fails loudly.
  2. `.lp-proc-stage` declares both properties, and each value is exactly
     `round(<the container's own expression>, <step>)`.
  3. The steps are 2px for max-width and 1px for padding-inline. Two, because
     the max-width is HALVED into the centring margin above --container-max:
     rounded to 1px, a 1439 px box centres on a half again.
  4. The rounding sits in the same at-rule block as `.lp-frame` -- the pinned
     tier. Below the gate the cards keep real 1 px borders, which the browser
     snaps to the grid itself; rounding the stage there would be a layout
     change bought for nothing.

-> design-system/assets/css/acts.css, the note over .lp-proc-stage
-> design-system/foundations/geometry.html
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "design-system" / "assets" / "css" / "base.css"
ACTS = ROOT / "design-system" / "assets" / "css" / "acts.css"

STEPS = {"max-width": "2px", "padding-inline": "1px"}


def strip_comments(css):
    """Blank out /* ... */ keeping length, so offsets stay meaningful."""
    out = list(css)
    for m in re.finditer(r"/\*.*?\*/", css, re.S):
        for i in range(m.start(), m.end()):
            if out[i] != "\n":
                out[i] = " "
    return "".join(out)


def norm(expr):
    """One space between tokens, none inside brackets' edges."""
    e = re.sub(r"\s+", " ", expr.strip())
    e = re.sub(r"\(\s+", "(", e)
    e = re.sub(r"\s+\)", ")", e)
    return e


def blocks(css):
    """Every `prelude { body }` in the sheet, linear scan, as
    (prelude, prelude_offset, body_start, body_end). Nested blocks included."""
    out = []
    stack = []
    mark = 0
    for i, ch in enumerate(css):
        if ch == "{":
            prelude = css[mark:i]
            stack.append((prelude.strip(), mark + (len(prelude) - len(prelude.lstrip())), i + 1))
            mark = i + 1
        elif ch == "}":
            if stack:
                pre, off, start = stack.pop()
                out.append((pre, off, start, i))
            mark = i + 1
        elif ch == ";":
            mark = i + 1
    return out


def rules_for(css, selector, all_blocks=None):
    """Every `selector { ... }` block, as (offset, body)."""
    found = []
    for pre, off, start, end in (all_blocks if all_blocks is not None else blocks(css)):
        if selector in [s.strip() for s in pre.split(",")]:
            found.append((off, css[start:end]))
    return found


def decls(body):
    out = {}
    depth = 0
    buf = ""
    for ch in body:
        if ch in "({[":
            depth += 1
        elif ch in ")}]":
            depth -= 1
        if ch == ";" and depth == 0:
            if ":" in buf:
                k, v = buf.split(":", 1)
                out[k.strip()] = norm(v)
            buf = ""
        else:
            buf += ch
    if ":" in buf and buf.strip():
        k, v = buf.split(":", 1)
        out.setdefault(k.strip(), norm(v))
    return out


def enclosing_block(all_blocks, offset):
    """(start, end) of the innermost block the offset sits inside, or None."""
    best = None
    for _, _, start, end in all_blocks:
        if start < offset < end and (best is None or start > best[0]):
            best = (start, end)
    return best


def main():
    base = strip_comments(BASE.read_text(encoding="utf-8"))
    acts_raw = ACTS.read_text(encoding="utf-8")
    acts = strip_comments(acts_raw)
    findings = []

    base_blocks = blocks(base)
    acts_blocks = blocks(acts)
    container = rules_for(base, ".container", base_blocks)
    if not container:
        print("plate grid: base.css declares no `.container` rule at all.")
        return 1
    cd = {}
    for _, body in container:
        cd.update(decls(body))
    want = {}
    for prop in STEPS:
        if prop not in cd:
            findings.append(
                "base.css `.container` no longer declares `%s`.\n"
                "    .lp-proc-stage rounds the container's own placement terms; if the\n"
                "    container has stopped using this one, the stage is rounding an\n"
                "    expression nothing else reads and the plate is placed off the column.\n"
                "    Restate the rounding against whatever places a container now."
                % prop)
        else:
            want[prop] = cd[prop]

    stage = rules_for(acts, ".lp-proc-stage", acts_blocks)
    if not stage:
        findings.append("acts.css declares no `.lp-proc-stage` rule.")
    sd = {}
    offsets = {}
    for off, body in stage:
        for k, v in decls(body).items():
            sd[k] = v
            offsets[k] = off

    for prop, step in STEPS.items():
        if prop not in want:
            continue
        expected = norm("round(%s, %s)" % (want[prop], step))
        got = sd.get(prop)
        if got is None:
            findings.append(
                "`.lp-proc-stage` does not round `%s`.\n"
                "        expected  %s: %s\n"
                "    Without it the stage's box starts at 5.5vw below --container-max —\n"
                "    56.31 px at 1024, 70.39 px at 1280 — and .lp-frame's six hairlines,\n"
                "    which are drawn ON that box's edges, spread across three pixel\n"
                "    columns on one side of the rectangle and two on the other."
                % (prop, prop, expected))
        elif got != expected:
            findings.append(
                "`.lp-proc-stage` rounds `%s` against something other than the\n"
                "    container's own expression:\n"
                "        found     %s: %s\n"
                "        expected  %s: %s\n"
                "    The rounding is written as the container's terms on purpose: a literal\n"
                "    drifts silently the first time base.css places a container differently."
                % (prop, prop, got, prop, expected))

    # 4. same at-rule block as .lp-frame — the pinned tier.
    frame = rules_for(acts, ".lp-frame", acts_blocks)
    if not frame:
        findings.append("acts.css declares no `.lp-frame` rule; the premise of this check is gone.")
    elif offsets:
        frame_block = enclosing_block(acts_blocks, frame[0][0])
        for prop in STEPS:
            if prop not in offsets:
                continue
            block = enclosing_block(acts_blocks, offsets[prop])
            if not frame_block or not block or block != frame_block:
                findings.append(
                    "`.lp-proc-stage`'s rounded `%s` is not in the same at-rule block as\n"
                    "    `.lp-frame`. The rounding exists for the frame's hairlines and the\n"
                    "    frame only exists in the pinned tier; below the gate the cards keep\n"
                    "    real 1 px borders, which the browser snaps to the grid itself."
                    % prop)

    if findings:
        print("plate grid: %d finding(s)\n" % len(findings))
        for f in findings:
            print("  - %s\n" % f)
        return 1

    print("plate grid: the pinned stage rounds both terms .container places it with —\n"
          "%s\n"
          "so .lp-frame's six hairlines land on whole pixel columns at every width\n"
          "the pin gate admits." % "\n".join("    %s: %s" % (p, sd[p]) for p in STEPS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
