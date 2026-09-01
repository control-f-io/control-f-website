#!/usr/bin/env python3
"""One plane is lit, and the stack is a stack.

The one hundred and twenty-seventh check, and the first whose subject is the
front door. `design-system/index.html` opens on the six material layers drawn
as one isometric object -- six 2:1 rhombi, one per layer, and exactly one of
them carrying the light family at any moment. The drawing is bound to the list
beside it with :has(), by `data-layer`, and there is no script anywhere in it.

WHY THIS IS COUNTED RATHER THAN LOOKED AT. Every way this block can break
renders as a stack of rhombi:

  a `data-layer` typo          the row's :has() rule matches nothing, so that
                               layer is the one you cannot light. Five of six
                               work, and nobody points at all six.
  a missing --cy row           the plane falls back to `--cy` unset, which
                               makes its transform invalid and puts it at the
                               frame's origin -- on top of layer 6, where it
                               reads as one plane drawn twice.
  an uneven --cy step          the pile is 84 units apart in five gaps and 70
                               in the sixth. It looks like a stack. It is a
                               stack with one seam in it.
  paint order reversed         correct until a plane is lit, and then the base
                               wash's fill covers the five layers standing in
                               front of it. → index.html, the note on the
                               planes
  a second --lit: 1 rule       two planes lit at once, which is the one rule
                               this brand states about lime and the only one
                               a screenshot of the DEFAULT state cannot show,
                               because the default is a single hover away.

None of the five is visible in the state a reviewer opens the page in, and
four of them need a pointer in one specific place to surface at all.

WHAT IT ASSERTS.

  1. The figure declares exactly the layers 1..6, each once, as
     `.docs-stack__plane[data-layer=N]`.
  2. The list declares exactly the same set as `.docs-stack__row[data-layer=N]`.
     Neither side may carry a layer the other does not: a plane with no row is
     a plane nothing can light, a row with no plane is a row that lights
     nothing.
  3. The figure's document order is ascending -- 1 painted first, 6 last --
     because in isometry higher is nearer and SVG paints last on top.
  4. docs.css gives every layer a `--cy` and no layer two, and the six sit on
     one constant step.
  5. docs.css gives every layer exactly one `--lit: 1` rule, and the default
     rule names a layer that exists.

WHAT IT DELIBERATELY DOES NOT ASSERT. The rhombus itself -- that its edges are
26.57 deg -- is geometry every other drawing in the tree carries too, and
holding one figure to it here would be a rule with a scope of one. The
recession's 0.55 is a measured contrast floor and is argued where it is
written; a number with a paragraph next to it does not also need a script.
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "design-system" / "index.html"
SHEET = ROOT / "design-system" / "assets" / "css" / "docs.css"

LAYERS = [1, 2, 3, 4, 5, 6]

PLANE = re.compile(r'class="docs-stack__plane"\s+data-layer="(\d+)"')
ROW = re.compile(r'class="docs-stack__row"\s+data-layer="(\d+)"')
CY = re.compile(r'\.docs-stack__plane\[data-layer="(\d+)"\]\s*\{\s*--cy:\s*(-?[\d.]+)\s*;?\s*\}')
# `.*?` and not `[^)]*`: the selector's condition carries its own parentheses
# — `:is(:hover, :focus-within)` — so a class that stops at the first `)` stops
# in the middle of the thing it is reading. Non-greedy, and the anchor after it
# is what decides where the selector ends.
LIT = re.compile(
    r'\.docs-stack:has\(\.docs-stack__row\[data-layer="(\d+)"\].*?\)\s*'
    r'\.docs-stack__plane\[data-layer="(\d+)"\]\s*\{\s*--lit:\s*1',
    re.S,
)
DEFAULT_LIT = re.compile(
    r'\.docs-stack:not\(:has\(.*?\)\)\s*'
    r'\.docs-stack__plane\[data-layer="(\d+)"\]\s*\{\s*--lit:\s*1',
    re.S,
)


def audit():
    findings = []
    page = PAGE.read_text(encoding="utf-8")
    sheet = SHEET.read_text(encoding="utf-8")

    planes = [int(n) for n in PLANE.findall(page)]
    rows = [int(n) for n in ROW.findall(page)]
    cys = {int(n): float(v) for n, v in CY.findall(sheet)}

    # 1 + 2 — both sides carry exactly the six layers, each once.
    for name, got in (("plane", planes), ("row", rows)):
        if sorted(got) != LAYERS:
            findings.append((
                "design-system/index.html",
                "the %ss declare %s" % (name, sorted(got) or "nothing"),
                "expected one of each of %s. A layer on one side and not the "
                "other is a plane nothing lights or a row that lights nothing."
                % LAYERS,
            ))

    # 3 — paint order. Ascending, so 6 is painted last and occludes 5.
    if planes and planes != sorted(planes):
        findings.append((
            "design-system/index.html",
            "the planes are painted in the order %s" % planes,
            "paint order must ascend 1 -> 6: higher is nearer in isometry and "
            "SVG paints last on top. Reversed, a lit base wash covers the five "
            "layers in front of it.",
        ))

    # 4 — every layer placed, on one step.
    if sorted(cys) != LAYERS:
        findings.append((
            "design-system/assets/css/docs.css",
            "--cy is declared for %s" % (sorted(cys) or "nothing"),
            "every plane needs one, and only one. A plane with no --cy has an "
            "invalid transform and stands at the frame's origin.",
        ))
    else:
        steps = {round(cys[n] - cys[n + 1], 4) for n in LAYERS[:-1]}
        if len(steps) != 1:
            findings.append((
                "design-system/assets/css/docs.css",
                "the planes sit %s units apart" % sorted(steps),
                "one step, or the pile has a seam in it. The step is the "
                "drawing's only spacing decision and it is made once.",
            ))
        elif steps and next(iter(steps)) <= 0:
            findings.append((
                "design-system/assets/css/docs.css",
                "the step is %s" % next(iter(steps)),
                "layer 6 stands above layer 1, so --cy must fall as the layer "
                "number rises.",
            ))

    # 5 — one route to each layer's light, and a default that exists.
    lit = [(int(a), int(b)) for a, b in LIT.findall(sheet)]
    crossed = [pair for pair in lit if pair[0] != pair[1]]
    if crossed:
        findings.append((
            "design-system/assets/css/docs.css",
            "a row lights another layer's plane: %s" % crossed,
            "row N lights plane N. Anything else is a drawing that answers the "
            "wrong question and looks entirely correct doing it.",
        ))
    reached = sorted({a for a, _ in lit})
    if reached != LAYERS:
        findings.append((
            "design-system/assets/css/docs.css",
            "rows can light %s" % (reached or "nothing"),
            "every layer needs exactly one rule, or it is the layer that does "
            "not answer a pointer.",
        ))
    if len(lit) != len(LAYERS):
        findings.append((
            "design-system/assets/css/docs.css",
            "%d hover rules for %d layers" % (len(lit), len(LAYERS)),
            "one each. Two rules for one layer is two planes lit the moment "
            "the second one's condition also holds.",
        ))

    default = [int(n) for n in DEFAULT_LIT.findall(sheet)]
    if len(default) != 1:
        findings.append((
            "design-system/assets/css/docs.css",
            "%d default-lit rules" % len(default),
            "exactly one. No default is a stack with no lime in it; two is two "
            "lit planes before the reader has done anything at all.",
        ))
    elif default[0] not in LAYERS:
        findings.append((
            "design-system/assets/css/docs.css",
            "the default lights layer %d" % default[0],
            "which no plane draws.",
        ))

    return findings, planes, rows, cys, lit, default


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print the stack: every plane, its place and its route to the light")
    args = ap.parse_args()

    findings, planes, rows, cys, lit, default = audit()

    if args.verbose:
        print("  %-6s %-8s %-8s %-8s %s" % ("layer", "painted", "--cy", "row", "lit by"))
        for n in sorted(cys) or LAYERS:
            print("  %-6d %-8s %-8s %-8s %s" % (
                n,
                planes.index(n) + 1 if n in planes else "-",
                cys.get(n, "-"),
                "yes" if n in rows else "-",
                "row %d%s" % (n, "  (default)" if default[:1] == [n] else "")
                if (n, n) in lit else "nothing",
            ))
        print()

    if findings:
        for where, what, why in findings:
            print("%s  %s\n    %s" % (where, what, why), file=sys.stderr)
        print("\n%d finding%s on the front door's stack. -> design-system/README.md, "
              "\"The front door is the stack\""
              % (len(findings), "" if len(findings) == 1 else "s"), file=sys.stderr)
        return 1

    step = round(cys[LAYERS[0]] - cys[LAYERS[1]], 4)
    print("stack: %d planes, %g units apart, one lit at a time, layer %d by default."
          % (len(planes), step, default[0]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
