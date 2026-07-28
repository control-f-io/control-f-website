#!/usr/bin/env python3
"""One stroke, drawn in two places, has to agree with itself.

THE STROKE. patterns/landing-page.html grows a root out of the statement's void
and hands it to the lectern's frame. The foot of that root is sixteen terminals
on the frame's top rail, and for as long as the drawing existed they landed on
the rail at 1440 x 900 and at no other viewport -- 58.17 px of empty wash at
1280 x 900, 171.58 at 1920 x 1080. The .lp-flow note carries the whole table and
the reason: the box's height is locked to its width by aspect-ratio, its top is
locked to the void the trunk leaves, and the rail is a third arrival with no
degree of freedom left to reach it.

The fix the note asks for is in the drawing's form. The box is bound at BOTH
ends -- the void's centre and the rail -- the 1200 x 620 viewBox renders on its
foot under `preserveAspectRatio="xMidYMax meet"`, and everything the box gained
in height is between the void's rim and the crown, where the trunk is the only
stroke. So the trunk leaves the drawing and becomes .lp-flow__stem, a stroke
placed in page pixels off the flow box's own metrics.

WHAT THAT COSTS, AND WHAT THIS CHECKS. The trunk is now authored twice: once as
`M330 84V150` inside the viewBox, for the tier without anchor positioning, and
once as three CSS insets, for the tier with it. Every number in the second copy
is read off the first:

    top     84 / 1200     the departure's y, in the drawing's units
    bottom  470 / 1200    620 - 150, the crown's height above the box's foot
    left    270 / 1200    600 - 330, the departure's x left of the box's centre

Nothing renders wrong when one of them drifts. The two copies are never drawn at
the same time -- exactly one is display: none -- so a stem placed 20 units below
the rim is a correct-looking drawing on the tier that ships it and an unchanged
one on the tier that does not, and the difference between them is not visible in
any screenshot of either. That is the same standing the drawing's OTHER
duplicated number had before check-flow-values.py, and it has the same half-life.

FOUR THINGS, then, all of them countable in the one file:

  1. THE THREE INSETS ARE THE TRUNK'S OWN GEOMETRY. Read the viewBox, read the
     .lp-flow__trunk path, derive 84, 470 and 270, and require the CSS to state
     those and no others -- over the same 1200 denominator, which is the
     drawing's width and the only basis on which a page pixel and a drawing unit
     convert.

  2. THE HEADER'S RIM IS THE SAME 84. "Was wir machen" stands on the drawing's
     horizon, which is the rim, which is where the trunk departs. That term used
     to be `anchor-size(height) * 536 / 620` -- correct while the box WAS the
     drawing, and 536/620 of the stretch too low the moment it was not. It is
     the departure's y over the width now, and it is the same number the stem
     leaves from or the rule is not the horizon.

  3. EXACTLY ONE TRUNK IS DRAWN. .lp-flow__stem is display: none outside the
     @supports block and display: block inside it; .lp-flow__trunk is display:
     none inside it. Miss either half and the page draws one trunk twice -- one
     stroke at two weights and two lengths, from the same point.

  4. THE STEM COMES AFTER THE DRAWING IN THE MARKUP, and this is the one that
     was found by rendering rather than by reading. An anchor is only acceptable
     to an element it PRECEDES in tree order. Authored before .lp-flow the stem
     lost all three insets at once -- not one of them, all three, silently, with
     no invalid value anywhere -- and fell back to its static position: measured
     at 1024 x 720, a 37 px stub at the container's left edge with the crown 250
     px away and nothing above it. A stroke that vanishes when it is moved up
     the file is a stroke whose position in the file is load-bearing.

    python3 scripts/check-flow-stem.py
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "design-system" / "prototypes" / "statement-to-process.html"

FLOW_SVG_RE = re.compile(r'<svg class="lp-flow"[^>]*viewBox="([^"]*)"[^>]*>')
PAR_RE = re.compile(r'<svg class="lp-flow"[^>]*preserveAspectRatio="([^"]*)"')
TRUNK_RE = re.compile(r'<path class="[^"]*\blp-flow__trunk\b[^"]*"[^>]*\bd="M'
                      r'(-?[\d.]+) (-?[\d.]+)V(-?[\d.]+)"')

# `anchor-size(--lp-flow-box width) * N / D`, whitespace-insensitive.
TERM_RE = re.compile(r"anchor-size\(--lp-flow-box width\)\s*\*\s*"
                     r"(-?[\d.]+)\s*/\s*(-?[\d.]+)")

# The required preserveAspectRatio. `meet` on its own would letterbox the
# drawing in the middle of a taller box and put no terminal on the rail; YMax is
# what stands it on the box's foot.
PAR = "xMidYMax meet"


def num(text):
    v = float(text)
    return int(v) if v == int(v) else v


def blocks(src):
    """(offset, selector list, declarations) for every innermost CSS rule.

    Scanned rather than matched. `([^{}]+)\\{([^{}]*)\\}` reads the same rules
    and takes 74 seconds on this page: the markup after the last <style> is
    forty thousand brace-free characters, and a greedy [^{}]+ that must be
    followed by a brace backtracks over all of them from every start position.
    A check nobody will wait for is a check that gets dropped from the workflow.
    """
    out = []
    # comments blanked rather than removed, so every offset below is still an
    # offset into the file the reader is looking at
    flat = re.sub(r"/\*.*?\*/", lambda m: " " * len(m.group(0)), src, flags=re.S)
    for m in re.finditer(r"<style[^>]*>(.*?)</style>", flat, re.S):
        style, at = m.group(1), m.start(1)
        depth, start, opens = 0, 0, []
        for i, ch in enumerate(style):
            if ch == "{":
                if depth == 0:
                    start = i
                opens.append(i)
                depth += 1
            elif ch == "}" and depth:
                depth -= 1
                open_at = opens.pop()
                body = style[open_at + 1:i]
                if "{" in body:
                    continue                      # an at-rule, not a rule
                head = style[:open_at].rsplit("}", 1)[-1].rsplit("{", 1)[-1]
                out.append((at + open_at,
                            [" ".join(s.split()) for s in head.split(",")], body))
    return out


def rule(src, selector, prop=None):
    """The declaration block of the rule whose selector list has this.

    With `prop`, the LAST block that declares it — which is the one that wins
    the cascade, and the only right answer once a selector legitimately appears
    more than once in a file. .lp-proc-head now does: its base `position` has to
    stand ABOVE the @supports that anchors it, or it outvotes the `absolute` an
    anchor needs (→ scripts/check-anchor-position-cascade.py). "The first rule
    with this selector" would read that one-liner and find no `top` at all.
    """
    found = (None, None)
    for at, sels, body in blocks(src):
        if selector not in sels:
            continue
        if prop is None:
            return body, at
        if declared(body, prop) is not None:
            found = (body, at)
    return found


def declared(block, prop):
    m = re.search(r"(?<![\w-])%s\s*:\s*([^;]+)" % re.escape(prop), block or "")
    return " ".join(m.group(1).split()) if m else None


def main():
    src = PAGE.read_text(encoding="utf-8")
    findings = []

    box = FLOW_SVG_RE.search(src)
    trunk = TRUNK_RE.search(src)
    if not box or not trunk:
        print("flow stem: the drawing or its trunk is not in %s" % PAGE.name)
        return 1
    vb = [num(v) for v in box.group(1).split()]
    tx, ty, crown = (num(g) for g in trunk.groups())
    width, height = vb[2], vb[3]

    # 1. the three insets, derived from the drawing rather than read off the CSS
    want = {"top": (ty, "the departure's y below the box top"),
            "bottom": (height - crown, "the crown's height above the box's foot"),
            "left": (width / 2 - tx, "the departure left of the box's centre")}

    par = PAR_RE.search(src)
    if not par or par.group(1) != PAR:
        findings.append(
            'the drawing declares preserveAspectRatio="%s", not "%s".\n'
            "    The box is taller than %g x %g wherever the seam used to be open, and\n"
            "    only YMax stands the viewBox on its foot. Any other alignment centres\n"
            "    or raises the drawing and none of the %g rail terminals arrives."
            % (par.group(1) if par else "(none)", PAR, width, height, height))

    supports = src.find("@supports (anchor-name: --lp-flow-box)")
    stems = [(at, body) for at, sels, body in blocks(src) if ".lp-flow__stem" in sels]
    inside = [b for at, b in stems if at > supports]
    if not stems or not inside:
        print("flow stem: no .lp-flow__stem rule inside the @supports block in %s"
              % PAGE.name)
        return 1
    stem_block = inside[0]

    checked = 0
    for prop, (expect, what) in sorted(want.items()):
        value = declared(stem_block, prop)
        if value is None:
            findings.append(".lp-flow__stem declares no `%s`." % prop)
            continue
        terms = TERM_RE.findall(value)
        if len(terms) != 1:
            findings.append(
                ".lp-flow__stem's `%s` reads --lp-flow-box's width %d time(s):\n"
                "        %s: %s\n"
                "    It is one term -- %s -- over the drawing's own width."
                % (prop, len(terms), prop, value, what))
            continue
        n, d = (num(t) for t in terms[0])
        if d != width:
            findings.append(
                ".lp-flow__stem's `%s` converts over %g, not the drawing's %g:\n"
                "        %s: %s\n"
                "    A page pixel is the box's width over the viewBox's width. Any other\n"
                "    denominator is a second, unstated basis." % (prop, d, width, prop, value))
            continue
        if n != expect:
            findings.append(
                ".lp-flow__stem's `%s` is %g/%g of the width and the drawing says %g/%g:\n"
                "        %s: %s\n"
                "    %s, from viewBox %s and the trunk's M%g %gV%g.\n"
                "    Neither tier renders wrong on its own; they disagree."
                % (prop, n, d, expect, width, prop, value, what.capitalize(),
                   box.group(1), tx, ty, crown))
            continue
        checked += 1

    # 2. the header's rim is the trunk's departure
    head_block, _ = rule(src, ".lp-proc-head", "top")
    head_top = declared(head_block, "top")
    head_terms = TERM_RE.findall(head_top or "")
    if len(head_terms) != 1 or [num(t) for t in head_terms[0]] != [ty, width]:
        findings.append(
            ".lp-proc-head's rim term is %s, and the trunk departs at %g/%g of the\n"
            "    width. The section title stands on the drawing's horizon and the horizon\n"
            "    is where the trunk leaves the void; two numbers is two horizons.\n"
            "        top: %s"
            % (("%g/%g" % (num(head_terms[0][0]), num(head_terms[0][1])))
               if len(head_terms) == 1 else "not one width term",
               ty, width, head_top))

    # 3. exactly one trunk is drawn
    base = [b for at, b in stems if at < supports]
    if not base or declared(base[0], "display") != "none":
        findings.append(
            "no .lp-flow__stem rule before the @supports block hides the stem.\n"
            "    Without anchor positioning the stem has no insets to stand on and the\n"
            "    drawing's own trunk is the one that ships; an unhidden stem falls back\n"
            "    to its static position and draws a second stroke beside it.")
    for sel, want_display in ((".lp-flow__stem", "block"), (".lp-flow__trunk", "none")):
        inner = [(at, body) for at, sels, body in blocks(src)
                 if sel in sels and at > supports]
        if not inner or declared(inner[0][1], "display") != want_display:
            findings.append(
                "inside the @supports block %s is not `display: %s`.\n"
                "    One trunk is drawn per tier. Miss a half and the page draws the same\n"
                "    stroke twice, at two lengths, from the same point." % (sel, want_display))

    # 4. the stem is authored after the drawing it anchors to
    stem_el = src.find('<svg class="lp-flow__stem"')
    flow_el = src.find('<svg class="lp-flow"')
    if stem_el < flow_el:
        findings.append(
            "the stem's markup is before .lp-flow's (offset %d against %d).\n"
            "    An anchor is only acceptable to an element it precedes in tree order.\n"
            "    Authored first the stem loses all three insets at once, with no invalid\n"
            "    value anywhere, and falls back to its static position."
            % (stem_el, flow_el))

    if findings:
        print("flow stem: %d finding(s)\n" % len(findings))
        for f in findings:
            print("  - %s\n" % f)
        return 1

    print("flow stem: the trunk is drawn twice and the two copies agree. Its three\n"
          "insets are %g, %g and %g over the drawing's %g, all derived from viewBox\n"
          '"%s" and the trunk\'s own M%g %gV%g; the section title\'s rim is the same\n'
          "%g; exactly one copy is drawn per tier; and the stem is authored after the\n"
          "drawing it anchors to."
          % (want["top"][0], want["bottom"][0], want["left"][0], width,
             box.group(1), tx, ty, crown, ty))
    return 0


if __name__ == "__main__":
    sys.exit(main())
