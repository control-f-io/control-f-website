#!/usr/bin/env python3
"""The numbers on the root have to add up.

The thirtieth check, and the sibling of check-flow-terminals.py. That one holds
the SHAPE of the statement-to-process illustration -- a root has no free ends.
This one holds what the root is CARRYING.

WHAT IS DRAWN. Eight values ride the routes of .lp-flow on
patterns/landing-page.html: 12 480 on the trunk as it leaves the void, 3 840 /
3 200 / 5 440 on the three taproots as they leave the crown, 1 360 / 4 080
where the right taproot divides, and 2 400 / 1 680 where 4 080 divides again.
They are the drawing's claim that data is moving and not merely that lines
exist.

THE RULE, and it is two sentences now. At any labelled point, the value equals
the sum of the labelled values immediately downstream of it: 3 840 + 3 200 +
5 440 is 12 480; 1 360 + 4 080 is 5 440; 2 400 + 1 680 is 4 080. AND every
route out of that point is in the sum -- no route may run from a labelled point
to an end of the drawing without meeting a labelled value on the way. Points
with no labelled value below them assert nothing -- the fringe below 3 840 is
unquantified, and unquantified is not the same as wrong.

THE SECOND SENTENCE IS THE ONE THIS SHIPPED WITHOUT, and the balance could not
see what it cost. 4 080 stood at (860, 415), which is a point on
(840, 405) -> (970, 470) -- one junction PAST the split it was naming. The
junction at (840, 405) also sheds a branch to (907.5, 540), six strokes that
land twice on the lectern's rail, and nothing on it carried a value. So
`5 440 = 1 360 + 4 080` balanced perfectly while saying that two of the
fourteen arrivals the root hands the lectern are fed by nothing at all: the
arithmetic was right and the sentence was false. A value labels THE STROKE IT
STANDS ON; a value naming a split must stand on a stroke leaving that split.
The walk is the only thing that can tell the difference, because on the page
the label sits a comfortable 45 units from the junction it appears to name and
looks exactly like the correct one.

WHY IT IS WORTH A CHECK AND NOT A COMMENT. A number in a drawing is the one
kind of content that looks equally right whatever it says. Nothing about
"3 900" beside "5 440" reads as broken; it reads as a number. There is no
screenshot, no visual diff and no reviewer who catches a drawing that has
quietly started telling the reader that a stream splits into more than it
carried -- and the first person to retune one of these values by hand, for
entirely good reasons of composition, will break the arithmetic and see
nothing. That is exactly the failure shape the twenty-nine checks beside this
one exist for: true of some elements, false of others, invisible in review.

AND EVERY VALUE RIDES A ROUTE. A numeral at a coordinate that is on no segment
of the drawing is a floating label, which is a different kind of object with a
different grammar -- a callout, which this system draws with a leader line.
Its point must lie ON a segment, exactly; the geometry is generated in exact
rational arithmetic by scripts/expertise-objects/gen-flow-root.py and pasted,
so a near-miss is a hand edit, which is the thing worth catching.

AND THE TYPE. These are read, so they owe what any text on the page wash owes.
foundations/illustration.html#a11y: "The moment a drawing does carry a label,
the label owes the same contrast as any other text on the page wash -- which on
CF-Grau means --text-secondary, never --text-muted." check-contrast.py already
fails the build on --text-muted in a page-local block; what it cannot see is a
numeral that stops carrying .t-label and starts restating the mono ramp by
hand, so that is checked here, where the markup is.

The check reads the shipped markup, not the generator. The generator asserts
the same things about its own output and cannot see a hand edit made
afterwards, which is where every previous drift in this repository has come
from.

    python3 scripts/check-flow-values.py       # check, exit 1 on a finding
    python3 scripts/check-flow-values.py -v    # print the balance at each point
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

# drawing class -> (segment class, value class)
DRAWINGS = {"lp-flow": ("lp-flow__seg", "lp-flow__val")}

# The type a value must carry. .t-label is the brand's mono label whole --
# mono, --text-xs, medium, --tracking-label -- and uppercase is a no-op on
# digits, which is why these can take it rather than copy four of its five
# declarations and get the fifth wrong.
REQUIRED_CLASS = "t-label"

FIGURE_RE = re.compile(r'<svg\b[^>]*class="([^"]*)"[^>]*viewBox="([^"]*)"(.*?)</svg>'
                       r'(.*?)(?=<svg\b|</div>\s*<div class="cf-statement__text")', re.S)
PATH_RE = re.compile(r'<path\b[^>]*class="([^"]*)"[^>]*\bd="([^"]*)"', re.S)
SPAN_RE = re.compile(r'<span\b[^>]*class="([^"]*)"[^>]*style="([^"]*)"[^>]*>([^<]*)</span>', re.S)
CMD_RE = re.compile(r'([MLVH])\s*(-?[\d.]+)(?:[ ,]+(-?[\d.]+))?')


def rational(text):
    return Fraction(text.strip()).limit_denominator(10 ** 6)


def parse_path(d):
    segs, cur = [], None
    for cmd, a, b in CMD_RE.findall(d):
        if cmd == "M":
            cur = (rational(a), rational(b))
        elif cmd == "L":
            nxt = (rational(a), rational(b))
            segs.append((cur, nxt))
            cur = nxt
        elif cmd == "V":
            nxt = (cur[0], rational(a))
            segs.append((cur, nxt))
            cur = nxt
        elif cmd == "H":
            nxt = (rational(a), cur[1])
            segs.append((cur, nxt))
            cur = nxt
    return segs


def on_segment(p, seg):
    (x1, y1), (x2, y2) = seg
    if p in (seg[0], seg[1]):
        return True
    if (x2 - x1) * (p[1] - y1) - (y2 - y1) * (p[0] - x1) != 0:
        return False
    return min(x1, x2) <= p[0] <= max(x1, x2) and min(y1, y2) <= p[1] <= max(y1, y2)


def show(v):
    return str(int(v)) if v.denominator == 1 else f"{float(v):g}"


def style_vars(style):
    out = {}
    for decl in style.split(";"):
        if ":" in decl and decl.strip().startswith("--"):
            name, _, value = decl.partition(":")
            out[name.strip()] = value.strip()
    return out


def downstream(point, labelled, segs):
    """The labelled points reachable from here, and the routes that reach none.

    Every segment of this drawing descends, so downstream is larger y and the
    walk cannot loop. A labelled point STOPS its branch, which is what makes
    the sum a statement about one generation rather than the whole subtree.

    The second return is the half the balance cannot see: the points where the
    walk RAN OUT — an end of the drawing reached with no labelled value
    anywhere between it and where the walk started. Those are the routes the
    sum below does not cover, and a sum that does not cover a route is a claim
    that the route carries zero.
    """
    found, escaped, seen, stack = set(), set(), set(), [point]
    while stack:
        p = stack.pop()
        onward = 0
        for seg in segs:
            if seg[1] == p or not on_segment(p, seg):
                continue
            onward += 1
            below = [q for q in labelled if q[1] > p[1] and on_segment(q, seg)]
            q = min(below, key=lambda v: v[1]) if below else seg[1]
            if q in labelled:
                found.add(q)
            elif q not in seen:
                seen.add(q)
                stack.append(q)
        if not onward and p != point:
            escaped.add(p)
    return found, escaped


def check_drawing(name, cls, svg_body, tail, verbose):
    seg_cls, val_cls = DRAWINGS[cls]

    segs = []
    for classes, d in PATH_RE.findall(svg_body):
        if seg_cls in classes.split():
            segs.extend(parse_path(d))

    values, findings = {}, []
    for classes, style, text in SPAN_RE.findall(tail):
        names = classes.split()
        if val_cls not in names:
            continue
        var = style_vars(style)
        digits = text.replace(" ", "").replace(" ", "").strip()
        if not digits.isdigit():
            findings.append(f"{name}: a .{val_cls} reads {text!r}, which is not a number")
            continue
        if REQUIRED_CLASS not in names:
            findings.append(
                f"{name}: the value {text.strip()!r} does not carry .{REQUIRED_CLASS} — "
                f"the mono label ramp belongs to the utility, not to a page-local copy "
                f"of four of its five declarations (scripts/check-label-ramp.py)")
        if "--x" not in var or "--y" not in var:
            findings.append(f"{name}: the value {text.strip()!r} declares no point")
            continue
        values[(rational(var["--x"]), rational(var["--y"]))] = (int(digits), text.strip())

    if not segs:
        return [f"{name}: .{cls} carries no .{seg_cls} at all"], 0
    if not values:
        return [f"{name}: .{cls} carries no .{val_cls} — the routes lost their data"], 0

    for p, (v, shown) in values.items():
        if not any(on_segment(p, s) for s in segs):
            findings.append(
                f"{name}: the value {shown!r} stands at ({p[0]}, {p[1]}), which is on no "
                f"segment of the drawing. A value rides a route; a value beside one is a "
                f"callout, and a callout is drawn with a leader line.")

    for p, (v, shown) in sorted(values.items(), key=lambda kv: kv[0][1]):
        kids, escaped = downstream(p, set(values), segs)
        if not kids:
            if verbose:
                print(f"    {shown:>8}  at ({show(p[0]):>4}, {show(p[1]):>3})  nothing labelled below it")
            continue
        total = sum(values[k][0] for k in kids)
        parts = " + ".join(values[k][1] for k in sorted(kids, key=lambda q: q[0]))
        if total != v:
            findings.append(
                f"{name}: the value {shown!r} divides into {parts}, which is {total:,} — "
                f"the drawing says a stream splits into {'more' if total > v else 'less'} "
                f"than it carried")
        if escaped:
            where = ", ".join(f"({show(q[0])}, {show(q[1])})"
                              for q in sorted(escaped, key=lambda q: (q[0], q[1])))
            findings.append(
                f"{name}: the value {shown!r} divides into {parts}, and {len(escaped)} "
                f"route(s) leaving it end unlabelled — at {where}. A sum is only a sum "
                f"if every route out of the point is in it; these are not, so the "
                f"drawing is saying those branches carry nothing. A value names the "
                f"stroke it stands on, so a value naming a split has to stand on a "
                f"stroke leaving that split — not two generations down with another "
                f"division in between.")
        elif total == v and verbose:
            print(f"    {shown:>8}  at ({show(p[0]):>4}, {show(p[1]):>3})  = {parts}")

    return findings, len(values)


def main():
    parser = argparse.ArgumentParser(description="The numbers on the root have to add up.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="print the balance at every labelled point")
    args = parser.parse_args()

    findings, values, drawings = [], 0, 0
    for page in sorted([*PATTERNS.glob("*.html"), *PROTOTYPES.glob("*.html")]):
        text = page.read_text(encoding="utf-8")
        for classes, _view_box, svg_body, tail in FIGURE_RE.findall(text):
            for cls in DRAWINGS:
                if cls in classes.split():
                    drawings += 1
                    if args.verbose:
                        print(f"  {page.name} .{cls}:")
                    f, n = check_drawing(page.name, cls, svg_body, tail, args.verbose)
                    findings += f
                    values += n

    if not drawings:
        print("flow values: no drawing to check — the selector went stale")
        return 1
    if findings:
        print(f"\nflow values: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1
    print(f"flow values OK — {values} values across {drawings} drawing(s), every one on a "
          f"route it belongs to, carrying the label ramp, balancing at every junction "
          f"that has labelled values below it, and with no route leaving such a junction "
          f"unlabelled")
    return 0


if __name__ == "__main__":
    sys.exit(main())
