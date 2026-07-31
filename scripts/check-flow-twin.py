#!/usr/bin/env python3
"""A lit front and the contour behind it are one line.

The root on patterns/landing-page.html draws every stroke TWICE. .lp-flow__light
carries the family's ramp and goes out behind itself; .lp-flow__seg is the
CF-Schwarz hairline that stays. The settled drawing is the contour it has always
been, and the colour only ever exists while the line is being drawn. Sixty-five
strokes, one hundred and thirty paths, and the pair is a pair only because two
`d` attributes were typed the same way by hand.

THE FRAME HAS THIS EXACT CONSTRUCTION AND IT IS HELD. .lp-frame__lit and
.lp-frame__line are six and six, and check-relay-rate.py pairs them on `d` and
then compares --a, --u and --o across the twins, with the reasoning stated in as
many words:

    "a pair that disagrees is two lines pretending to be one — the light would
     lay a stroke down somewhere the hairline never arrives, or draw at a
     different speed beside it. Nothing renders wrong at either end of the
     window; only the middle is a lie, and only while it is moving."

That paragraph is about the frame's twelve paths. The root's hundred and thirty
are the same sentence, ten times over, and no file read them. This is the check
that does.

WHY NOTHING ELSE CATCHES IT, stated per neighbour so this is not mistaken for a
fifth copy of a rule already held:

  * check-flow-terminals.py reads .lp-flow__seg alone. Every terminal in the
    CONTOUR arrives on the fringe, at the source or on another segment — and a
    light stroke that stops 30 units short of its contour arrives nowhere,
    invisibly, because that pass is not in the census.

  * check-flow-axes.py reads .lp-flow__light and compares each one against the
    ANGLE of the gradient it references. A light that is short of its contour
    but still on the same bearing is exactly as legal as one that is not: the
    axis check would pass a stroke half the length of the hairline under it.

  * check-flow-chain.py reads the four families' RULES — the animation-range
    each is staggered by — and the per-path --l and --u of .lp-flow__seg. The
    light's own --l and --u, typed once per path beside the contour's, are read
    by nothing.

  * check-relay-rate.py pairs the FRAME's two passes and says so; its PASSES
    tuple names lp-frame__line and lp-frame__lit and no root class.

So the light pass's geometry has been held by the generator's good behaviour and
by nothing else, in two pages — patterns/landing-page.html and
prototypes/statement-to-process.html, which carry the same drawing.

WHAT IS HELD, and each is a way one line can become two:

  1. EVERY FRONT HAS A CONTOUR. Each .lp-flow__light `d` is drawn by exactly one
     .lp-flow__seg. A front with no hairline under it leaves colour where the
     settled drawing is black — the stroke lights, travels, fades, and the line
     it drew is not there afterwards.

  2. EVERY CONTOUR HAS A FRONT. Each .lp-flow__seg `d` is drawn by exactly one
     .lp-flow__light. Sixty-four strokes arriving in the ramp and one sliding in
     black is the kind of gap a screenshot of either end of the draw cannot
     show, because at both ends the two passes agree.

  3. NO LINE IS DRAWN TWICE IN ONE PASS. A `d` that appears twice among the
     contours is one hairline stroked twice — the same ink laid on itself, which
     reads as a heavier line at that one edge and as nothing at all in the
     markup. The same for the fronts.

  4. ONE WINDOW PER PAIR. The twins agree on --o, --l and --u. Those three are
     the stroke's own place in the draw — --l is its distance from the void,
     --u what it adds, --o its transform-origin — and they are typed twice, once
     per pass. A pair that disagrees on --l ignites its light before or after
     the hairline it is supposed to be leading; a pair that disagrees on --o
     grows its two halves out of different ends of the same line.

WHAT THIS CHECK IS NOT. It says nothing about whether the geometry is RIGHT —
that is check-flow-terminals.py for where a stroke may end, check-flow-axes.py
for what bearing it may take and check-flow-chain.py for when it may open. It
holds only that the two passes are drawing the SAME line, which is the one thing
none of those three can see.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-flow-twin.py
    python3 scripts/check-flow-twin.py -v
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = ROOT / "design-system" / "patterns"
# The statement-to-process chain moved to prototypes/ on 2026-07-28; this check
# follows the drawing, not the folder — same rule as check-flow-handover.py.
PROTOTYPES = ROOT / "design-system" / "prototypes"

SVG_RE = re.compile(r'<svg\b[^>]*class="([^"]*)"[^>]*>(.*?)</svg>', re.S)
PATH_RE = re.compile(r"<path\b([^>]*?)/?>", re.S)
ATTR_RE = re.compile(r'\b([a-zA-Z-]+)="([^"]*)"')
# --o holds two tokens ("100% 0"), --l and --u single numbers; one pattern reads
# all three because the comparison is textual either way.
VAR_RE = re.compile(r"(--[a-z]+)\s*:\s*([^;]*)")

FRONT = "lp-flow__light"
CONTOUR = "lp-flow__seg"
# The three the markup types once per pass. --a is the frame's word for the same
# thing; the root spells it --l plus --u, and --o is the transform-origin both
# families carry.
WINDOW = ("--o", "--l", "--u")


def paths(body):
    """Every <path> in one drawing as (classes, d, {--var: value})."""
    out = []
    for raw in PATH_RE.findall(body):
        attrs = dict(ATTR_RE.findall(raw))
        d = attrs.get("d")
        if not d:
            continue
        classes = attrs.get("class", "").split()
        variables = {k: v.strip() for k, v in VAR_RE.findall(attrs.get("style", ""))}
        out.append((classes, " ".join(d.split()), variables))
    return out


def check_drawing(name, body, verbose):
    findings = []
    fronts, contours = {}, {}
    front_seen, contour_seen = Counter(), Counter()

    for classes, d, variables in paths(body):
        if FRONT in classes:
            front_seen[d] += 1
            fronts.setdefault(d, variables)
        elif CONTOUR in classes:
            contour_seen[d] += 1
            contours.setdefault(d, variables)

    if not fronts and not contours:
        return findings, 0

    # ---- 3. no line drawn twice in one pass ------------------------------
    for d, n in sorted(front_seen.items()):
        if n > 1:
            findings.append(
                f"{name}: `{d}` is drawn {n} times by .{FRONT} — one front laid "
                f"on itself is a brighter stroke at one edge and an identical "
                f"line in the markup")
    for d, n in sorted(contour_seen.items()):
        if n > 1:
            findings.append(
                f"{name}: `{d}` is drawn {n} times by .{CONTOUR} — the same "
                f"hairline stroked twice reads as a heavier edge and as nothing "
                f"at all in a diff")

    # ---- 1. every front has a contour ------------------------------------
    for d in sorted(set(fronts) - set(contours)):
        findings.append(
            f"{name}: `{d}` is drawn by .{FRONT} and by no .{CONTOUR} — a front "
            f"with no hairline under it leaves colour where the settled drawing "
            f"is black")

    # ---- 2. every contour has a front ------------------------------------
    for d in sorted(set(contours) - set(fronts)):
        findings.append(
            f"{name}: `{d}` has a contour and no front — one stroke sliding in "
            f"black beside sixty-four arriving in the ramp is invisible at both "
            f"ends of the draw")

    # ---- 4. one window per pair ------------------------------------------
    for d in sorted(set(fronts) & set(contours)):
        for key in WINDOW:
            front, contour = fronts[d].get(key), contours[d].get(key)
            if front != contour:
                findings.append(
                    f"{name}: `{d}` declares {key}:{front} on .{FRONT} and "
                    f"{key}:{contour} on its .{CONTOUR} twin — the two passes "
                    f"are one stroke, and only the middle of the window shows "
                    f"the difference")

    if verbose:
        print(f"  {name}: {len(fronts)} fronts, {len(contours)} contours, "
              f"{len(set(fronts) & set(contours))} twinned on d")

    return findings, len(set(fronts) & set(contours))


def main():
    parser = argparse.ArgumentParser(
        description="A lit front and the contour behind it are one line.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="print the census for each drawing")
    args = parser.parse_args()

    findings, twins, drawings = [], 0, 0
    for page in sorted([*PATTERNS.glob("*.html"), *PROTOTYPES.glob("*.html")]):
        text = page.read_text(encoding="utf-8")
        for classes, body in SVG_RE.findall(text):
            if "lp-flow" not in classes.split():
                continue
            found, n = check_drawing(page.name, body, args.verbose)
            if not found and not n:
                continue
            drawings += 1
            findings += found
            twins += n

    if not drawings:
        print("flow twin: no drawing to check — the selector went stale")
        return 1
    if findings:
        print(f"\nflow twin: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1
    print(f"flow twin OK — {twins} strokes across {drawings} drawing(s), every lit "
          f"front on a contour and every contour under a front, none drawn twice, "
          f"and every pair on one window")
    return 0


if __name__ == "__main__":
    sys.exit(main())
