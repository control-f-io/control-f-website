#!/usr/bin/env python3
"""A root does not pass through itself, and the radius steps down with distance.

The forty-third check, and the other half of a sentence check-flow-terminals.py
has been saying on its own since the bus became a root. That check asserts
every terminal ARRIVES -- on the rail, at the void, or on another branch. It
says nothing about what a stroke does BETWEEN its terminals, and three of them
walked straight over another branch.

WHY THAT IS A BUG AND NOT A TEXTURE. This system's drawings are construction
drawings. foundations/illustration.html: "a node marks a point the construction
actually depends on" -- which is the same statement read the other way, that a
line crossing another line with nothing on the crossing means THESE ARE NOT
CONNECTED. The flow's whole subject is data merging and dividing. At three
points it was telling the reader, in its own vocabulary, that two streams
meeting is not a meeting:

  (600.00, 550.00)   the middle taproot's last vertical, crossed by a branch
                     of the RIGHT taproot on its way to the rail
  (195.00, 555.00)   two branches of the left taproot, crossing each other
  (653.33, 478.33)   a middle-taproot branch crossed by a right-taproot branch

None of the three had a node on it, and none could have: a crossing is not a
junction. The reader cannot tell them apart, which is the failure -- the same
one the free ends were, one level down. It was visible in any screenshot of the
section and had never been read as a failure, because at 1 px and 62 % opacity
an X looks like a drawing decision.

THE RULE. For any two segments, an intersection interior to BOTH is a crossing
and fails. An intersection at an ENDPOINT of either is an arrival -- a junction,
a T, a graft where a tip lands mid-branch -- and is exactly what the drawing is
made of. Collinear overlap is not reachable here (the generator only emits a
second stroke along a line to place a junction on it, sharing one endpoint) and
is reported if it ever appears.

AND THE LADDER, in the same sweep, because it is the same mistake in the other
direction: a mark whose size says something the geometry does not.
foundations/illustration.html states the node radius "steps down with distance
from the subject". The subject here is the void the trunk leaves, and every
node already carries its run from the void as --l, normalised 0-3. So the rule
is checkable exactly: r must be a NON-INCREASING function of --l. Two nodes at
the same distance must be the same size, and no node may be larger than one
nearer the void.

It had never held. (720, 345), (0, 450) and (600, 495) all sit at --l 1.5 --
the same run, to the unit -- and carried r 2, r 1 and r 1. Three points at one
distance, two radii, under a rule whose only variable is distance. The radii
were typed; they are now derived in the generator, and this holds the result.

The check reads the markup, not the generator, for the reason every check here
does: the generator asserts its own output and cannot see a hand edit made to
the paste afterwards.
"""

import argparse
import re
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = ROOT / "design-system" / "patterns"

# drawing class -> (segment class, node class)
DRAWINGS = {"lp-flow": ("lp-flow__seg", "lp-flow__node")}

SVG_RE = re.compile(r'<svg\b[^>]*class="([^"]*)"[^>]*viewBox="([^"]*)"(.*?)</svg>', re.S)
PATH_RE = re.compile(r'<path\b[^>]*class="([^"]*)"[^>]*\bd="([^"]*)"', re.S)
CIRCLE_RE = re.compile(
    r'<circle\b[^>]*class="([^"]*)"[^>]*style="([^"]*)"[^>]*\bcx="([^"]*)"'
    r'[^>]*\bcy="([^"]*)"[^>]*\br="([^"]*)"', re.S)
CMD_RE = re.compile(r'([MLVH])\s*(-?[\d.]+)(?:[ ,]+(-?[\d.]+))?')
L_RE = re.compile(r'--l:\s*(-?[\d.]+)')

RADII = {1, 2, 3}


def rational(text):
    return Fraction(text).limit_denominator(10 ** 6)


def parse_path(d):
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
    return str(int(v)) if v.denominator == 1 else f"{float(v):.2f}"


def meeting(a, b):
    """Where two segments meet, and whether that point is interior to both.

    Exact rational arithmetic throughout: the geometry is generated in
    Fractions and pasted, so a point that is 'almost' on a line is a hand edit
    and there is no tolerance to spend on it.
    """
    (ax1, ay1), (ax2, ay2) = a
    (bx1, by1), (bx2, by2) = b
    det = (ax2 - ax1) * (by2 - by1) - (ay2 - ay1) * (bx2 - bx1)
    if det == 0:
        return None, False          # parallel; collinear overlap handled by caller
    t = ((bx1 - ax1) * (by2 - by1) - (by1 - ay1) * (bx2 - bx1)) / det
    u = ((bx1 - ax1) * (ay2 - ay1) - (by1 - ay1) * (ax2 - ax1)) / det
    if not (0 <= t <= 1 and 0 <= u <= 1):
        return None, False
    p = (ax1 + t * (ax2 - ax1), ay1 + t * (ay2 - ay1))
    return p, (0 < t < 1 and 0 < u < 1)


def collinear_overlap(a, b):
    (ax1, ay1), (ax2, ay2) = a
    (bx1, by1), (bx2, by2) = b
    if (ax2 - ax1) * (by2 - by1) - (ay2 - ay1) * (bx2 - bx1) != 0:
        return False
    if (bx1 - ax1) * (ay2 - ay1) - (by1 - ay1) * (ax2 - ax1) != 0:
        return False               # parallel but not on the same line
    def within(p, s):
        (x1, y1), (x2, y2) = s
        return (min(x1, x2) <= p[0] <= max(x1, x2)
                and min(y1, y2) <= p[1] <= max(y1, y2))
    shared = {(ax1, ay1), (ax2, ay2)} & {(bx1, by1), (bx2, by2)}
    inside = [p for p in ((bx1, by1), (bx2, by2)) if within(p, a)]
    inside += [p for p in ((ax1, ay1), (ax2, ay2)) if within(p, b)]
    return len(set(inside) - shared) > 0


def check_drawing(name, cls, body, verbose):
    seg_cls, node_cls = DRAWINGS[cls]
    segs = []
    for classes, d in PATH_RE.findall(body):
        if seg_cls in classes.split():
            segs.extend(parse_path(d))
    nodes = []
    for classes, style, cx, cy, r in CIRCLE_RE.findall(body):
        if node_cls not in classes.split():
            continue
        m = L_RE.search(style)
        nodes.append((rational(cx), rational(cy), int(r),
                      None if m is None else float(m.group(1))))

    findings = []
    if not segs:
        return [f"{name}: .{cls} carries no .{seg_cls} at all"], 0, 0

    crossings = []
    for i in range(len(segs)):
        for j in range(i + 1, len(segs)):
            p, interior = meeting(segs[i], segs[j])
            if interior:
                crossings.append((i, j, p))
            elif collinear_overlap(segs[i], segs[j]):
                findings.append(
                    f"{name}: segments {i} and {j} lie along each other rather than "
                    f"meeting at a point — two strokes on one line is one stroke "
                    f"drawn twice, at twice the weight"
                )
    for i, j, p in crossings:
        (ax1, ay1), (ax2, ay2) = segs[i]
        (bx1, by1), (bx2, by2) = segs[j]
        findings.append(
            f"{name}: segment {i} (M{show(ax1)} {show(ay1)} L{show(ax2)} {show(ay2)}) "
            f"passes through segment {j} (M{show(bx1)} {show(by1)} L{show(bx2)} "
            f"{show(by2)}) at ({show(p[0])}, {show(p[1])}) — a root does not pass "
            f"through itself, and a crossing with nothing on it reads as two "
            f"streams NOT meeting"
        )

    for x, y, r, l in nodes:
        if r not in RADII:
            findings.append(
                f"{name}: the node at ({show(x)}, {show(y)}) is r {r} — "
                f"foundations/illustration.html publishes r 3, 2 and 1 and nothing else"
            )
        if l is None:
            findings.append(
                f"{name}: the node at ({show(x)}, {show(y)}) carries no --l, so its "
                f"distance from the void is unknown and its radius cannot be read"
            )
    ladder = sorted((n for n in nodes if n[3] is not None), key=lambda n: n[3])
    for (x1, y1, r1, l1), (x2, y2, r2, l2) in zip(ladder, ladder[1:]):
        if r2 > r1:
            findings.append(
                f"{name}: the node at ({show(x2)}, {show(y2)}) is r {r2} at --l {l2}, "
                f"further from the void than the r {r1} node at ({show(x1)}, "
                f"{show(y1)}) (--l {l1}) — the radius steps DOWN with distance"
            )
        elif l1 == l2 and r1 != r2:
            findings.append(
                f"{name}: the nodes at ({show(x1)}, {show(y1)}) and ({show(x2)}, "
                f"{show(y2)}) are both --l {l1} — the same run from the void — and "
                f"are r {r1} and r {r2}. One distance, one radius"
            )

    if verbose:
        pairs = len(segs) * (len(segs) - 1) // 2
        print(f"  {name} .{cls}: {len(segs)} segments, {pairs} pairs swept, "
              f"{len(crossings)} crossing(s), {len(nodes)} nodes")
        for x, y, r, l in sorted(nodes, key=lambda n: (n[3] is None, n[3])):
            print(f"    node ({show(x):>7}, {show(y):>5})  --l {l:<5}  r {r}")

    return findings, len(segs), len(nodes)


def main():
    parser = argparse.ArgumentParser(
        description="A root does not pass through itself.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="print the sweep and the node ladder")
    args = parser.parse_args()

    findings, segs, nodes, drawings = [], 0, 0, 0
    for page in sorted(PATTERNS.glob("*.html")):
        text = page.read_text(encoding="utf-8")
        for classes, _view_box, body in SVG_RE.findall(text):
            for cls in DRAWINGS:
                if cls in classes.split():
                    drawings += 1
                    f, s, n = check_drawing(page.name, cls, body, args.verbose)
                    findings += f
                    segs += s
                    nodes += n

    if not drawings:
        print("flow crossings: no drawing to check — the selector went stale")
        return 1
    if findings:
        print(f"\nflow crossings: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1
    pairs = segs * (segs - 1) // 2
    print(f"flow crossings OK — {pairs} segment pairs across {drawings} drawing(s) meet "
          f"only at their ends, and {nodes} node radii step down with the run from the void")
    return 0


if __name__ == "__main__":
    sys.exit(main())
