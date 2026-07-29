#!/usr/bin/env python3
"""Enforce that a stroke drawn ALONG its own viewBox edge is not cut in half.

A stroke is centred on its path. An <svg> clips at its own viewport by
default. Put those two facts together and a rail written on the boundary of
its viewBox — `M0 0H1000` at y = 0, `M40 130V10` at x = 40 — loses its outer
half to the clip and reaches the screen at half the weight it declares. The
markup is correct, the stylesheet is correct, the stroke-width is correct, and
the line is thin.

It is the failure mode that hides best, because nothing about it looks like a
bug. There is no error, no warning, no missing element and no gap: a rail is
drawn, in the right place, in the right colour. It is simply drawn at half
weight, and half weight of a hairline is still a hairline — until it meets a
stroke of the same declared width that happens to be INTERIOR and therefore
whole, and the junction between them steps.

THE EVIDENCE. patterns/landing-page.html draws the pinned stage's lectern as
five hairlines in a 1000 x 500 viewBox: four on the boundary and one interior
divider at x = 500. Measured in the browser at device scale 8, integrating the
ink across each rail against the section wash, at contain 20 % of the track:

    viewport        top    left   divider   right    base
    1440 x 900     0.513  0.512    1.016    0.483   0.513
    1920 x 1080    0.510  0.504    0.999    0.495   0.492
    1280 x 800     0.508  0.508    1.008    1.006   0.888
    1024 x 768     0.516  0.511    1.002    1.009   0.454

The seams lane measured that independently of the lane that fixed it, at a
different device scale and a different scroll position, and got the same
answer: the divider whole, the four rails halved, and no two of the four the
same. It is not a reading that needs care to reproduce. It is what the
construction does.

Every rail declares 1 px under `vector-effect: non-scaling-stroke`. The
divider — the one stroke that is interior, and the only one the clip cannot
reach — is the only one that arrived at 1. And the four that were clipped did
not even arrive at a consistent half: the clip is snapped to the device grid
and a plate's edges land on a fraction of a pixel at most widths, so the same
frame drew its five rails at three different weights depending on the
viewport. The 2 px light pass was halved by the same clip on the same four
rails, so the ignition read thin as well.

THE SYSTEM ALREADY KNEW, THREE TIMES, IN PROSE. components.css declares
`overflow: visible` on .cf-page-header__figure, on .cf-plot__draw and on
.cf-arrive__object, and exactly one of the three says why:

    /* The viewBox is the drawing's bounding box, so a 1 px non-scaling
       contour at the extremes is half outside it. SVG clips to the viewport
       by default; without this the outermost shell loses half its stroke. */

That comment is the whole rule. It is written on one selector, it governs
every drawing in the tree, and .lp-frame — the one drawing whose ENTIRE
geometry sits on its extremes — was authored without it and shipped a
half-weight lectern until it was measured. Three copies of a declaration kept
by hand, one of them carrying the reason, is the shape this directory exists
for: the workflow's own header says as much about the highlight fill ("Two
copies of a workaround is the shape of a rule that wants a script"). This is
four.

THE RULE. For every <svg> in the design-system tree that carries a viewBox: if
any straight stroked segment inside it has BOTH endpoints on the SAME viewBox
edge — the segment is coincident with the boundary, not merely touching it —
then that <svg> must resolve `overflow: visible`.

"Coincident, not touching" is what keeps this honest, and it is deliberately
NARROWER than the prose rule it enforces. A drawing whose geometry runs OUT of
the frame is a deliberate crop and this system is full of them: the statement
figure's lattice is explicitly "cut by the void", its lines reach x = 0 and
y = 0 at a point and are meant to be cut there, and the isometric objects all
bleed. A segment that merely touches an edge loses a corner nobody can name; a
segment that LIES ALONG one loses exactly half of itself, every time, on every
viewport, by construction. So this counts the case it can prove and leaves the
rest where it already is — an outermost curved shell at the extremes is the
comment on .cf-page-header__figure's business, not this script's, because no
amount of parsing distinguishes it from a crop that was meant.

Only the <svg>'s own resolved overflow is read, because that is the box that
does the clipping: the property is looked for on the element's `style`
attribute, on the page's own <style> block, and on the three shipping
stylesheets, matched by class or by element. An ancestor cannot fix this and
an ancestor cannot cause it.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-edge-stroke-clip.py
    python3 scripts/check-edge-stroke-clip.py -v
"""

import argparse
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
CSS = DS / "assets" / "css"

SHIPPING = ("tokens.css", "base.css", "components.css", "acts.css")

# Every page in the tree, prototypes included — the same boundary
# check-iso-motion.py draws and for the same reason. This is a fact about a
# DRAWING: a rail halved by its own viewport is as halved in a motion study as
# it is on a pattern page.
PAGES = sorted(DS.rglob("*.html"))

COMMENT = re.compile(r"/\*.*?\*/", re.S)
NUMBER = re.compile(r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?")
# Absolute straight-line commands only. Anything else in a `d` puts the path
# out of scope rather than into a finding — see coincident() on why that is
# the safe direction.
PATH_TOKEN = re.compile(r"[A-Za-z]|[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?")
STRAIGHT = set("MLHV")
EPS = 1e-6

# A geometry element only has a stroke if something gives it one. `fill="none"`
# on the <svg> plus a class is the idiom here, so absence of a stroke attribute
# proves nothing — but a `stroke="none"` states it, and a <rect>/<circle> with
# no stroke anywhere is a fill and has no weight to lose.
STROKELESS = re.compile(r'stroke\s*[:=]\s*"?\s*none', re.I)


# --------------------------------------------------------------------------
# geometry
# --------------------------------------------------------------------------

def segments(tag, attrs):
    """Straight segments of one element as [((x1,y1),(x2,y2)), …], user units.

    Returns [] for anything this check will not reason about: a relative or
    curved path, a <rect>, a transform. That is deliberate. The check's job is
    to catch the construction it can prove — a straight rail written on the
    boundary — and a path it cannot read is not evidence of anything.
    """
    if "transform" in attrs:
        return []
    if tag == "line":
        try:
            return [((float(attrs.get("x1", 0)), float(attrs.get("y1", 0))),
                     (float(attrs.get("x2", 0)), float(attrs.get("y2", 0))))]
        except ValueError:
            return []
    if tag != "path":
        return []
    toks = PATH_TOKEN.findall(attrs.get("d", ""))
    out, cur, i = [], None, 0
    while i < len(toks):
        head = toks[i]
        if head.isalpha():
            if head not in STRAIGHT:
                return []           # curve, close, or a relative command
            i += 1
            cmd = head
        elif cur is None:
            return []               # numbers before any command
        else:
            cmd = "M" if not out and cur is None else last
        try:
            if cmd in "ML":
                x, y = float(toks[i]), float(toks[i + 1]); i += 2
            elif cmd == "H":
                x, y = float(toks[i]), cur[1]; i += 1
            else:
                x, y = cur[0], float(toks[i]); i += 1
        except (IndexError, ValueError):
            return []
        if cur is not None and cmd != "M":
            out.append((cur, (x, y)))
        cur = (x, y)
        last = "L" if cmd == "M" else cmd
    return out


def coincident(seg, box):
    """Which viewBox edge this segment LIES ALONG, or None if it merely meets one."""
    (ax, ay), (bx, by) = seg
    x0, y0, w, h = box
    x1, y1 = x0 + w, y0 + h
    if abs(ay - by) < EPS and abs(ax - bx) > EPS:
        if abs(ay - y0) < EPS:
            return "top"
        if abs(ay - y1) < EPS:
            return "bottom"
    if abs(ax - bx) < EPS and abs(ay - by) > EPS:
        if abs(ax - x0) < EPS:
            return "left"
        if abs(ax - x1) < EPS:
            return "right"
    return None


# --------------------------------------------------------------------------
# what the <svg> resolves for overflow
# --------------------------------------------------------------------------

def rules(text):
    """[(selector, body)] with comments blanked, for one stylesheet or block."""
    text = COMMENT.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)
    out = []
    for m in re.finditer(r"([^{}]*)\{([^{}]*)\}", text):
        selector = " ".join(m.group(1).split())
        if "{" not in m.group(1) and selector.startswith("@"):
            continue
        out.append((selector, m.group(2)))
    return out


def declares_visible(body):
    """True if this declaration block releases the clip on both axes.

    `overflow-x` alone cannot: a box with one axis visible and the other not
    computes the visible one back to auto, which still clips. So a split
    declaration has to release both, and the general property releases both by
    itself.
    """
    axes = {}
    for prop, value in re.findall(
            r"(?<![\w-])(overflow(?:-x|-y)?)\s*:\s*([^;{}]+)", body, re.I):
        axes[prop.lower()] = value.strip().lower()
    if axes.get("overflow") == "visible":
        return True
    return axes.get("overflow-x") == "visible" and axes.get("overflow-y") == "visible"


def selector_hits(selector, classes):
    """Does this selector's SUBJECT name the svg by class or by element?

    The subject is the last compound in the selector; anything to its left is
    an ancestor or a sibling, and cannot be the box that clips. `.a .b` has
    subject `.b`; `svg.lp-frame` has subject `svg.lp-frame`.
    """
    for part in selector.split(","):
        part = part.strip()
        if not part:
            continue
        subject = re.split(r"\s+|(?<=[\w\])])\s*>\s*", part)[-1].strip()
        if not subject:
            continue
        names = set(re.findall(r"\.([\w-]+)", subject))
        if names and not names <= classes:
            continue
        if names:
            return True
        if re.fullmatch(r"svg(?::[\w-]+(?:\([^)]*\))?)*", subject, re.I):
            return True
    return False


def resolves_visible(style_attr, classes, sheets, page_blocks):
    if style_attr and declares_visible(style_attr):
        return "style attribute"
    for origin, ruleset in list(page_blocks) + list(sheets):
        for selector, body in ruleset:
            if declares_visible(body) and selector_hits(selector, classes):
                return origin
    return None


# --------------------------------------------------------------------------
# the pass over the tree
# --------------------------------------------------------------------------

class Reader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.svgs = []          # (line, classes, style, viewBox, [(cls, tag, edge)])
        self.stack = []
        self.style_blocks = []
        self._in_style = False

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "style":
            self._in_style = True
            return
        if tag == "svg":
            box = None
            raw = a.get("viewbox", "")
            n = [float(v) for v in NUMBER.findall(raw)]
            if len(n) == 4 and n[2] > 0 and n[3] > 0:
                box = n
            entry = [self.getpos()[0], set(a.get("class", "").split()),
                     a.get("style", ""), raw, []]
            self.stack.append(entry)
            self.svgs.append(entry)
            return
        if not self.stack:
            return
        entry = self.stack[-1]
        raw = entry[3]
        n = [float(v) for v in NUMBER.findall(raw)]
        if len(n) != 4:
            return
        if STROKELESS.search(" ".join("%s=%s" % kv for kv in a.items())):
            return
        for seg in segments(tag, a):
            edge = coincident(seg, n)
            if edge:
                entry[4].append((a.get("class", ""), tag, edge, self.getpos()[0]))

    def handle_startendtag(self, tag, attrs):
        if tag == "svg":
            return
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if tag == "style":
            self._in_style = False
        elif tag == "svg" and self.stack:
            self.stack.pop()

    def handle_data(self, data):
        if self._in_style:
            self.style_blocks.append(data)


def audit():
    sheets = []
    findings, seen = [], []
    for name in SHIPPING:
        path = CSS / name
        if not path.exists():
            findings.append((name, 0, "", "stylesheet is missing"))
            continue
        sheets.append((name, rules(path.read_text(encoding="utf-8"))))

    for page in PAGES:
        reader = Reader()
        reader.feed(page.read_text(encoding="utf-8"))
        page_blocks = [("%s <style>" % page.name, rules(b))
                       for b in reader.style_blocks]
        rel = page.relative_to(ROOT).as_posix()
        for line, classes, style, raw, rails in reader.svgs:
            if not rails:
                continue
            where = resolves_visible(style, classes, sheets, page_blocks)
            label = ("svg." + ".".join(sorted(classes))) if classes else "svg"
            if where:
                seen.append((rel, line, label, len(rails), where))
            else:
                findings.append((
                    rel, line, label,
                    "%d stroke%s lie along the viewBox edge (%s) and this <svg> "
                    "clips: each of them paints at half its declared weight.\n"
                    "    %s"
                    % (len(rails), "" if len(rails) == 1 else "s",
                       ", ".join(sorted({e for _, _, e, _ in rails})),
                       "; ".join("line %d %s.%s on the %s edge"
                                 % (ln, tag, cls or "(no class)", edge)
                                 for cls, tag, edge, ln in rails[:6]))))
    return findings, seen


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every edge-drawn <svg>, not only the failures")
    args = ap.parse_args()

    findings, seen = audit()

    if args.verbose:
        for rel, line, label, count, where in seen:
            print("  %-46s %5d  %-22s %d rail%s  visible via %s"
                  % (rel, line, label, count, "" if count == 1 else "s", where))
        print()

    if findings:
        for rel, line, label, why in findings:
            print("%s:%d  %s\n    %s" % (rel, line, label, why), file=sys.stderr)
        print("\n%d <svg> %s a rail on its own viewBox boundary and clip%s it in "
              "half. Add `overflow: visible` to the <svg>'s own rule — the way "
              ".cf-page-header__figure does in components.css, where the reason "
              "is written out."
              % (len(findings), "draws" if len(findings) == 1 else "draw",
                 "s" if len(findings) == 1 else ""), file=sys.stderr)
        return 1

    rails = sum(count for *_, count, _ in seen)
    print("edge strokes: %d rail%s on a viewBox boundary across %d <svg>, every "
          "one of them unclipped."
          % (rails, "" if rails == 1 else "s", len(seen)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
