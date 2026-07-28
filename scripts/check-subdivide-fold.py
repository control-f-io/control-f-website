#!/usr/bin/env python3
"""Hold the subdivision's fold and its axis to the same threshold.

The subdivision grid folds in two files. base.css collapses the columns:

    @container (max-width: 44rem) { .subdivide__col { grid-column: 1 / -1; … } }

and components.css hides the timeline that names them:

    @container (max-width: 44rem) { .cf-blog-axis { display: none; } }

Those are one decision written twice. The axis is a .subdivide__row of the same
grid, so it already folds on the same ELEMENT's width — components.css says so
in as many words, and treats that as the end of the matter:

    /* The grid folds itself (see .subdivide in base.css); the axis is one of
       its rows, so it folds on the same element's width by construction. */

Same element is only half of it. It has to be the same NUMBER too, and nothing
held it there. Move one prelude and leave the other and the grid stacks into a
single column while five vertical year ticks stay drawn beneath it — AKTUELL,
2026, 2025, 2024, 2022–2023 — a timeline labelling columns that are not on the
page. It renders; it just lies. That is the failure mode this whole directory
exists for: invisible in a diff, wrong in a render nobody re-took.

The move that surfaced it is .subdivide--late. A fold width is a property of
the COLUMN COUNT, not of the primitive: blog-artikel.html runs the grid at
three and three columns of a 44rem container are 234 px each, which reads; the
landing page runs it at five and five columns of the same container are 141 px.
Measured at the pixel after the fold — a viewport of 792, a container of 705 —
two of that page's twelve tail headlines rendered as a fragment of one word
followed by an ellipsis, because .cf-blog-card--compact is one line with an
ellipsis and its cell held 116 px of text against the 130 px
"Smart-Home-Systeme" needs. So the five-column form opts up to 56rem, and the
axis had to come with it. Adding the second pair by hand is exactly when a
first pair stops being self-evidently in sync.

WHAT IT CHECKS

  pairing        every threshold at which .subdivide__col folds has an
                 identical threshold at which .cf-blog-axis hides, and the
                 reverse — matched on the whole prelude, so a max-width fold
                 cannot be paired with a min-width hide.
  modifiers      the two rules in a pair carry the same modifier prefix. A
                 fold written for .subdivide--late paired with a bare axis
                 hide would hide the axis for every consumer of the
                 primitive, which is a different bug in the same shape.
  registered     every fold threshold is a number the register in tokens.css
                 already carries. This does not restate the register —
                 check-breakpoints.py owns that in both directions — it fails
                 EARLY and with this file's reason, so a fold moved to an
                 unregistered number is reported as a fold, not as a
                 register row somebody forgot.

WHAT IT DOES NOT CHECK

  Whether the number is the right one. That is a measurement, and it lives
  next to the rule in base.css. This file checks that the two copies of
  whatever number was chosen agree.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-subdivide-fold.py       # check, exit 1 on a finding
    python3 scripts/check-subdivide-fold.py -v    # list every pair
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system" / "assets" / "css"

BASE = CSS / "base.css"
COMPONENTS = CSS / "components.css"
TOKENS = CSS / "tokens.css"

# The two selectors that have to fold together. The fold is on the column; the
# hide is on the axis. Each is matched inside a @container block.
FOLD_SEL = ".subdivide__col"
AXIS_SEL = ".cf-blog-axis"

# A @container prelude and the block that follows it. Blocks here are one level
# deep — a rule inside a query — which is all the subdivision uses.
QUERY = re.compile(r"@container\s*([^{]*?)\s*\{(.*?)\n\}", re.S)

# The modifier a selector is scoped to, if any: `.subdivide--late .subdivide__col`
# carries `.subdivide--late`, a bare `.subdivide__col` carries none.
MODIFIER = re.compile(r"(\.subdivide--[a-z-]+)\s")


def blocks(path):
    """Every (prelude, body, line) @container block in a stylesheet."""
    text = path.read_text(encoding="utf-8")
    out = []
    for m in QUERY.finditer(text):
        pre = " ".join(m.group(1).split())
        out.append((pre, m.group(2), text.count("\n", 0, m.start()) + 1))
    return out


def folds(path, selector):
    """(prelude, modifier, line) for each block whose body sets `selector`."""
    found = []
    for pre, body, line in blocks(path):
        for rule in body.split("}"):
            head = rule.split("{")[0]
            if selector not in head:
                continue
            mod = MODIFIER.search(head)
            found.append((pre, mod.group(1) if mod else "", line))
    return found


def registered():
    """Every threshold literal the register in tokens.css lists."""
    text = TOKENS.read_text(encoding="utf-8")
    return set(re.findall(r"(\d+(?:\.\d+)?rem)\s*/\s*\d+", text))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    fold = folds(BASE, FOLD_SEL)
    axis = folds(COMPONENTS, AXIS_SEL)
    failures = []

    if not fold:
        failures.append(
            "base.css declares no %s fold at all.\n"
            "    The subdivision folds to a stack below a threshold; if that rule is\n"
            "    gone, this check is measuring nothing and the axis rules below are\n"
            "    hiding a timeline for a grid that never stacks." % FOLD_SEL
        )

    fold_keys = {(pre, mod) for pre, mod, _ in fold}
    axis_keys = {(pre, mod) for pre, mod, _ in axis}

    for pre, mod, line in sorted(fold, key=lambda f: f[2]):
        if (pre, mod) not in axis_keys:
            failures.append(
                "base.css:%d folds %s%s at `@container %s`, and components.css\n"
                "    hides %s at no such threshold.\n"
                "    The grid would stack into one column with the year ticks still drawn\n"
                "    beneath it — a timeline naming columns that are not on the page. Add\n"
                "    the matching rule in the same commit."
                % (line, (mod + " ") if mod else "", FOLD_SEL, pre, AXIS_SEL)
            )

    for pre, mod, line in sorted(axis, key=lambda f: f[2]):
        if (pre, mod) not in fold_keys:
            failures.append(
                "components.css:%d hides %s%s at `@container %s`, and base.css\n"
                "    folds %s at no such threshold.\n"
                "    The columns would stand while the timeline that names them vanished.\n"
                "    Either the fold moved and this did not, or this is a threshold with\n"
                "    nothing behind it."
                % (line, (mod + " ") if mod else "", AXIS_SEL, pre, FOLD_SEL)
            )

    reg = registered()
    for pre, mod, line in fold:
        for lit in re.findall(r"(\d+(?:\.\d+)?rem)", pre):
            if lit not in reg:
                failures.append(
                    "base.css:%d folds at %s, which the register in tokens.css does not\n"
                    "    carry.\n"
                    "    A fold width is where the system changes shape, so it is a register\n"
                    "    row by definition. Add it to both copies — tokens.css and\n"
                    "    foundations/layout.html — in the same commit, or fold onto a number\n"
                    "    that already exists." % (line, lit)
                )

    if args.verbose:
        print("subdivision fold pairs\n")
        for pre, mod, line in sorted(fold, key=lambda f: f[2]):
            partner = [l for p, m, l in axis if (p, m) == (pre, mod)]
            print(
                "  @container %s   %s\n      base.css:%d %s\n      components.css:%s %s"
                % (
                    pre,
                    mod or "(bare)",
                    line,
                    FOLD_SEL,
                    ",".join(str(p) for p in partner) or "-",
                    AXIS_SEL,
                )
            )
        print()

    if failures:
        print("subdivide fold: %d finding(s)\n" % len(failures))
        for f in failures:
            print("  - %s\n" % f)
        return 1

    print(
        "subdivide fold: %d fold/axis pair(s), preludes identical, "
        "%d threshold(s) all in the register."
        % (len(fold), len({p for p, _, _ in fold}))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
