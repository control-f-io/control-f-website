#!/usr/bin/env python3
"""A node marks a junction, and it marks every junction the ladder reaches.

The fifty-ninth check, and the fourth about the statement-to-process root's own
vocabulary. check-flow-terminals.py holds where a stroke may END, and
check-flow-crossings.py holds what it may CROSS and how big a dot may be at the
run it sits at. Between them they had never asked the one question a reader
asks first: WHICH points get a dot at all.

WHAT SHIPPED. Fifteen junctions in the drawing, seven of them marked, and the
eighth mark not on a junction:

    (330, 150)   level 0.22   r 3   junction, marked
    (420, 195)   level 0.51   r 3   junction, marked
    (480, 255)   level 0.71   r 3   BEND -- one in, one out -- marked
    (150, 240)   level 0.81         junction, bare
    (530, 355)   level 1.04         junction, bare
    ( 60, 330)   level 1.11   r 2   junction, marked
    (720, 345)   level 1.50   r 2   junction, marked
    (  0, 450)   level 1.50   r 2   junction, marked
    (600, 495)   level 1.50   r 2   junction, marked
    (270, 480)   level 1.60         junction, bare
    (150, 510)   level 1.70         junction, bare
    (840, 405)   level 1.90         junction, bare  <- the 2 400 / 1 680 split
    (805, 515)   level 2.06         junction, bare
    (970, 470)   level 2.32   r 1   junction, marked
    (907.5, 540) level 2.34         junction, bare
    (1130, 550)  level 2.85         junction, bare

Read down the level column: marking is not a function of the run from the void
and is not a function of anything else either. (480, 255) carries the largest
dot in the drawing at the one marked point where nothing divides -- it is the
middle taproot turning 45 deg into 63.43 deg, a bend. (840, 405) is the split
the numerals 2 400 and 1 680 name, and carries nothing. (970, 470) at 2.32 is
marked while four junctions NEARER the void are not.

WHY THAT IS A BUG AND NOT A TEXTURE. foundations/illustration.html: "a node
marks a point the construction actually depends on. They are not decoration and
not a scatter." check-flow-crossings.py rests its whole case on reading that
sentence backwards -- two lines meeting with nothing on the meeting means THESE
ARE NOT CONNECTED -- and then proves no two strokes cross. That proof buys
nothing if the dot itself is scattered: a reader who has learnt that a dot means
"here it divides" meets eight of them, seven true and one false, over fifteen
divisions. In the one drawing on this page whose subject is data dividing, the
word for dividing was being spent at random.

THE RULE, in three parts, all of them the run from the void:

  1. EVERY NODE IS ON A JUNCTION. The point carries two or more segments
     leaving it. A bend is not a junction; nor is a terminal, nor the void.
  2. EVERY JUNCTION INSIDE THE CUT CARRIES ONE, and the cut is level < 2 --
     the r 3 and r 2 thirds of the ladder. This clause has now been written
     both ways and each was right about the drawing in front of it. The
     balanced construction (2026-07-28, second review: "make it branch
     equally") had SEVEN divisions, every one load-bearing, so the cut came
     out and every division was marked. The root is grown again (2026-07-28,
     third review: "more arms, back to the procedural graph"), it has fifty
     junctions, and a dot on each is not a vocabulary -- it is a texture. So
     the cut is back, and it is the same number the RADIUS is a function of
     rather than a second one: r 3 and r 2 are the bands nearest the subject,
     and those are the divisions the reader is meant to count. Out at level 2
     and beyond the root is thinning to twigs, where the manual's own reason
     for a dot -- "a point the construction depends on" -- stops picking
     anything out, because out there every point does.
  3. AT MOST ELEVEN. foundations/illustration.html: "Eight is a lot for one
     object; twelve is too many", so eleven is the ceiling. On the geometry
     that ships, the cut in (2) selects eight of the fifty; the two agree
     here and this holds them to agreeing. If the root grows a twelfth
     junction inside the cut, that is a decision for a person, not a drift.

A node's --l is checked too: it is the level of the strokes LEAVING its
junction, which is what puts the dot's fade on the same front as the branches
it feeds (check-flow-chain.py owns the front; this owns the number the node
hands it). A dot lighting a beat off its own fork is the #191 failure in
miniature.

The radius ladder itself stays where it is, in check-flow-crossings.py. This
check does not restate it.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-flow-nodes.py       # check, exit 1 on a finding
    python3 scripts/check-flow-nodes.py -v    # print the junction table
"""

import argparse
import re
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = ROOT / "design-system" / "patterns"
# The statement-to-process chain moved to prototypes/ on 2026-07-28;
# these checks follow the drawing, not the folder.
PROTOTYPES = ROOT / "design-system" / "prototypes"

# drawing class -> (segment class, node class)
DRAWINGS = {"lp-flow": ("lp-flow__seg", "lp-flow__node")}

# No cut any more -- every division is marked (docstring, rule 2). The old
# truth was Fraction(2), the r 3 + r 2 bands, retired with the grown fringe.
MARKED_BELOW = None

# foundations/illustration.html: "Eight is a lot for one object; twelve is too
# many." Twelve is too many, so eleven is the most there may be.
MAX_NODES = 11

SVG_RE = re.compile(r'<svg\b[^>]*class="([^"]*)"[^>]*viewBox="([^"]*)"(.*?)</svg>', re.S)
PATH_RE = re.compile(r'<path\b[^>]*class="([^"]*)"[^>]*style="([^"]*)"[^>]*\bd="([^"]*)"',
                     re.S)
NODE_CUT = 1.75  # gen-flow-root.py's NODE_LEVEL -- see (2) above. It came
                 # down from 2.0 when the root grew arms: the level-2 band went
                 # from nine junctions to twelve and the manual's ceiling is
                 # eleven, so the CUT moves rather than the ceiling.

CIRCLE_RE = re.compile(
    r'<circle\b[^>]*class="([^"]*)"[^>]*style="([^"]*)"[^>]*\bcx="([^"]*)"'
    r'[^>]*\bcy="([^"]*)"[^>]*\br="([^"]*)"', re.S)
CMD_RE = re.compile(r'([MLVH])\s*(-?[\d.]+)(?:[ ,]+(-?[\d.]+))?')
L_RE = re.compile(r'--l:\s*(-?[\d.]+)')


def rational(text):
    return Fraction(text).limit_denominator(10 ** 6)


def parse_path(d):
    """The segments of one `d`, as ((x1, y1), (x2, y2)) in drawing units."""
    segs, cur = [], None
    for cmd, a, b in CMD_RE.findall(d):
        if cmd == "M":
            cur = (rational(a), rational(b))
            continue
        if cmd == "L":
            nxt = (rational(a), rational(b))
        elif cmd == "V":
            nxt = (cur[0], rational(a))
        else:
            nxt = (rational(a), cur[1])
        segs.append((cur, nxt))
        cur = nxt
    return segs


def show(v):
    return str(int(v)) if v.denominator == 1 else f"{float(v):g}"


def point(p):
    return f"({show(p[0])}, {show(p[1])})"


def check_drawing(name, cls, body, verbose):
    seg_cls, node_cls = DRAWINGS[cls]
    findings = []

    # ---- the graph: what leaves each point, and at what level ------------
    out_level = {}      # point -> the --l of the strokes leaving it
    out_count = {}      # point -> how many strokes leave it
    seen_points = set()
    for classes, style, d in PATH_RE.findall(body):
        if seg_cls not in classes.split():
            continue
        m = L_RE.search(style)
        level = rational(m.group(1)) if m else None
        for (a, b) in parse_path(d):
            seen_points.add(a)
            seen_points.add(b)
            out_count[a] = out_count.get(a, 0) + 1
            if level is not None:
                # Every stroke leaving a point carries the same --l — that is
                # check-flow-chain.py's rule, not this one's. Take the first.
                out_level.setdefault(a, level)

    junctions = {p: out_level.get(p) for p, n in out_count.items() if n >= 2}

    # ---- the nodes -------------------------------------------------------
    nodes = {}
    for classes, style, cx, cy, r in CIRCLE_RE.findall(body):
        if node_cls not in classes.split():
            continue
        m = L_RE.search(style)
        p = (rational(cx), rational(cy))
        nodes[p] = (rational(m.group(1)) if m else None, int(r))

    # ---- 1. every node is on a junction ----------------------------------
    for p, (level, r) in sorted(nodes.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        n = out_count.get(p, 0)
        if n >= 2:
            continue
        if p not in seen_points:
            what = "is not on the drawing at all"
        elif n == 1:
            what = "is a bend — one stroke in, one out, and nothing divides there"
        else:
            what = "is a terminal — the drawing arrives there and goes no further"
        findings.append(
            f"{name}: the r {r} node at {point(p)} {what}; a node marks a point "
            f"the construction depends on (foundations/illustration.html)")

    # ---- 2. every junction the cut reaches carries one -------------------
    for p, level in sorted(junctions.items(), key=lambda kv: (kv[1] is None, kv[1])):
        if level is not None and level >= NODE_CUT:
            continue
        if level is None:
            findings.append(
                f"{name}: the junction at {point(p)} carries no --l on the strokes "
                f"leaving it, so nothing can say whether it is inside the cut")
            continue
        if p not in nodes:
            findings.append(
                f"{name}: the junction at {point(p)} is at level {show(level)} "
                f"and carries no node — the drawing divides there and does not "
                f"say so")

    # ---- 3. the node's --l is its junction's -----------------------------
    for p, (level, r) in sorted(nodes.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        want = out_level.get(p)
        if want is None or level is None or level == want:
            continue
        findings.append(
            f"{name}: the node at {point(p)} carries --l {show(level)} and the "
            f"strokes leaving it carry {show(want)} — the dot would light off the "
            f"front that feeds it (check-flow-chain.py)")

    # ---- 4. the ceiling --------------------------------------------------
    if len(nodes) > MAX_NODES:
        findings.append(
            f"{name}: {len(nodes)} nodes — the manual's ceiling is {MAX_NODES} "
            f'("eight is a lot for one object; twelve is too many"), so the cut '
            f"and the ceiling have stopped agreeing and a person has to choose")

    if verbose:
        print(f"  {name} .{cls}: {len(junctions)} junctions, {len(nodes)} nodes, "
              f"every division marked")
        rows = sorted(((lv, p) for p, lv in junctions.items()),
                      key=lambda kv: (kv[0] is None, kv[0]))
        for level, p in rows:
            mark = f"r {nodes[p][1]}" if p in nodes else "—"
            print(f"    {point(p):>16}  level {show(level):<5} {mark}")

    return findings, len(junctions), len(nodes)


def main():
    parser = argparse.ArgumentParser(
        description="A node marks a junction, and every junction the ladder reaches.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="print the junction table")
    args = parser.parse_args()

    findings, junctions, nodes, drawings = [], 0, 0, 0
    for page in sorted([*PATTERNS.glob("*.html"), *PROTOTYPES.glob("*.html")]):
        text = page.read_text(encoding="utf-8")
        for classes, _view_box, body in SVG_RE.findall(text):
            for cls in DRAWINGS:
                if cls in classes.split():
                    drawings += 1
                    f, j, n = check_drawing(page.name, cls, body, args.verbose)
                    findings += f
                    junctions += j
                    nodes += n

    if not drawings:
        print("flow nodes: no drawing to check — the selector went stale")
        return 1
    if findings:
        print(f"\nflow nodes: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1
    print(f"flow nodes OK — {nodes} nodes across {drawings} drawing(s), every one on "
          f"a junction, and every one of the {junctions} junctions inside the ladder's "
          f"marked band carries one")
    return 0


if __name__ == "__main__":
    sys.exit(main())
