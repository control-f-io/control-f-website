#!/usr/bin/env python3
"""The two halves of the seam meet on a shared centre, not on a shared width.

check-flow-handover.py proves the statement-to-process seam in VIEWBOX UNITS:
the source lands inside the top rail's span, and the lectern's inner vertical
grows down from the point it lands at. Both are true of the shipped markup and
both were true on the day this was written. Its argument for why units are
enough is one sentence, and that sentence is the thing nothing measured:

    "Both drawings are the same width by construction ... So the two viewBoxes
     share a width basis, and a flow x maps to a frame x by 1000/1200 exactly."

THEY ARE NOT THE SAME WIDTH. The card's row is capped by --pin-measure, which
is a function of the viewport's HEIGHT, and centred in the container. The
drawing is capped by --sp-measure, which is a DIFFERENT function of the
viewport's height — min(100%, (100vh - --act-bar - 8rem - --sp-head-band) *
1.9) against (max(min(45rem, 100vh), 100vh - consent) - 13rem) * 2 — and it was
not centred at all: a grid item with a definite width is START aligned, so the
drawing hung on the container's left edge. Measured on the shipped page at the
commit this check was written against, gate on, consent dismissed, the source's
x against the inner vertical's x, in page pixels:

    viewport      drawing   container   source    vertical   short by
    1024 x  900     911.38    911.38     512.00     512.00      0.00
    1280 x  900    1109.59   1139.22     625.19     640.00     14.81
    1280 x  800     919.59   1139.22     530.19     640.00    109.81
    1280 x  720     767.59   1139.22     454.19     640.00    185.81
    1366 x  768     858.80   1215.75     504.52     683.00    178.48
    1440 x  900    1109.59   1280.02     634.78     720.00     85.22
    1440 x  720     767.59   1280.02     463.78     720.00    256.22
    1600 x  900    1109.59   1280.00     714.80     800.00     85.20
    1920 x 1080    1280.00   1280.00     960.00     960.00      0.00
    2560 x 1440    1280.00   1280.00    1280.00    1280.00      0.00

Three zeros, and they are the three sizes where the height cap does not bind:
1920 and 2560 are tall, and 1024's container is already narrower than the cap.
Every other row is a laptop. At 1440 x 900 — the size the drawing was tuned at
and the size Standing Order 2 was measured at — the trunk resolved into the
source 85 px to the left of the hairline written to continue it, and every
check in this repository passed on that state, this seam's own check included.

It is the same fault .cf-pin__inner's note in components.css records one
element further down the seam: the card narrowed and centred while its index
and its bar stayed flush to the container, "every zero is a viewport where the
height cap does not bind — which is every size anyone checks at". That audit
fixed the three rows it was looking at. Nobody asked what the DRAWING did.

THE WIDTHS DO NOT HAVE TO MATCH. Fitting the drawing to the stage's height is
what keeps the whole of it on screen — check-figure-fits.py holds that — so a
seam that rests on a shared width is a seam that has to choose between fitting
and joining. It does not have to: the source sits at the flow viewBox's exact
horizontal centre and the inner vertical at the frame viewBox's exact
horizontal centre, so if both boxes are centred in the same container the two
land on each other at every viewport, whatever the two measures resolve to.

SO WHAT IS HELD HERE IS THE CENTRE, in four parts, and each one is a way the
arrival can come apart while every other check in the suite still passes:

  1. THE SOURCE IS AT THE FLOW BOX'S MIDDLE. .lp-flow__orb's cx is half the
     flow viewBox's width. Move the source off centre and centring the box
     stops landing it, silently.

  2. THE INNER VERTICAL IS AT THE FRAME BOX'S MIDDLE. The one .lp-frame__line
     vertical that is not an edge stands at half the frame viewBox's width.
     Same sentence from the other side.

  3. THE DRAWING'S BOX IS CENTRED IN ITS AREA. The gated .sp-drawing rule
     declares `justify-self: center`. This is the declaration that was
     missing, and its absence is invisible in the DOM at 1920 x 1080.

  4. THE CARD'S ROW IS CENTRED IN THE SAME CONTAINER. .cf-pin__inner > *
     declares `justify-self: center`. Drop it and the drawing is centred
     against a lectern that is not, which is this finding with the sign
     flipped.

3 and 4 are declarations rather than computed positions because that is what a
file can be read for; the pixels behind them are the table above, taken with a
browser, and the two numbers a browser is needed for — the rendered widths —
are exactly the two this check is written to stop depending on. Both rules must
also be CENTRED BY justify-self and not by auto margins, for the reason
.cf-pin__inner's own note gives: `margin-inline: auto` is (0,1,0) and loses to
base.css's own element margins, so a join settled in the cascade is a join that
comes apart when an unrelated rule is added above it.

WHAT THIS DOES NOT CLAIM. Nothing about the seam's VERTICAL axis — the gap
between the flow box's foot and the frame's top rail, which check-flow-
handover.py's own note measures at 1.58 to 171.58 px across the tiers and hands
to the craft lane as the drawing's form. This holds one axis, and it is the one
that was open at every laptop size and closed by one declaration.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-seam-centre.py
    python3 scripts/check-seam-centre.py -v
"""

import argparse
import re
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = ROOT / "design-system" / "patterns"
PROTOTYPES = ROOT / "design-system" / "prototypes"
ACTS = ROOT / "design-system" / "assets" / "css" / "acts.css"
COMPONENTS = ROOT / "design-system" / "assets" / "css" / "components.css"

SVG_RE = re.compile(r'<svg\b[^>]*class="([^"]*)"[^>]*viewBox="([^"]*)"(.*?)</svg>', re.S)
PATH_RE = re.compile(r'<path\b[^>]*class="([^"]*)"[^>]*\bd="([^"]*)"', re.S)
ORB_RE = re.compile(r'<circle\b[^>]*class="[^"]*lp-flow__orb[^"]*"[^>]*'
                    r'cx="(-?[\d.]+)"\s*cy="(-?[\d.]+)"\s*r="(-?[\d.]+)"')
CMD_RE = re.compile(r"([MLVH])\s*(-?[\d.]+)(?:[ ,]+(-?[\d.]+))?")


def rational(text):
    return Fraction(text).limit_denominator(10 ** 6)


def show(v):
    return str(int(v)) if v.denominator == 1 else f"{float(v):g}"


def strip_comments(css):
    """Blank out comments, keeping newlines so line numbers survive."""
    return re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)), css, flags=re.S)


def parse_path(d):
    """Every segment of one path, as ((x1, y1), (x2, y2)) in exact rationals."""
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


def collect(text, svg_class, path_class):
    for classes, view_box, body in SVG_RE.findall(text):
        if svg_class not in classes.split():
            continue
        vb = [rational(v) for v in view_box.split()]
        segs = []
        for path_classes, d in PATH_RE.findall(body):
            if path_class in path_classes.split():
                segs.extend(parse_path(d))
        return segs, vb, body
    return None, None, None


def blocks(css):
    """Every `prelude { body }` in the sheet, at any nesting depth.

    @media and @supports are transparent here — their contents are ordinary
    rules and the gate the fix lives in is one of them — so the walk descends
    into every block and yields the innermost preludes as well as the outer
    ones. Declarations are only read off preludes that name a selector, so an
    at-rule's own prelude never matches anything asked for.
    """
    css = strip_comments(css)
    out, i, n = [], 0, len(css)
    while i < n:
        if css[i] != "{":
            i += 1
            continue
        head = css[:i]
        cut = max(head.rfind("{"), head.rfind("}"), head.rfind(";"))
        prelude = head[cut + 1:].strip()
        depth, j = 1, i + 1
        while j < n and depth:
            if css[j] == "{":
                depth += 1
            elif css[j] == "}":
                depth -= 1
            j += 1
        out.append((prelude, css[i + 1:j - 1]))
        i += 1
    return out


def declares(css, selector, prop, value):
    """Does a rule whose prelude is exactly `selector` set `prop: value`?

    Exact prelude, not a substring: the point of the check is that THIS rule
    carries the declaration, and a different selector that happens to contain
    the same text is a different rule with a different specificity.
    """
    for prelude, body in blocks(css):
        if prelude != selector:
            continue
        for decl in body.split(";"):
            if ":" not in decl:
                continue
            name, _, val = decl.partition(":")
            val = val.strip()
            if val.endswith("!important"):
                val = val[:-len("!important")].strip()
            if name.strip() == prop and val == value:
                return True
    return False


def check_page(page, verbose):
    text = page.read_text(encoding="utf-8")
    flow, flow_vb, _ = collect(text, "lp-flow", "lp-flow__seg")
    frame, frame_vb, _ = collect(text, "lp-frame", "lp-frame__line")
    if flow is None or frame is None:
        return [], False

    findings = []
    flow_mid = flow_vb[0] + flow_vb[2] / 2
    frame_mid = frame_vb[0] + frame_vb[2] / 2

    # 1. THE SOURCE IS AT THE FLOW BOX'S MIDDLE.
    orb = ORB_RE.search(text)
    if not orb:
        findings.append(
            f"{page.name}: no .lp-flow__orb — the source is the point the seam "
            f"is centred on and there is nothing to centre")
    else:
        ox = rational(orb.group(1))
        if ox != flow_mid:
            findings.append(
                f"{page.name}: the source stands at flow x {show(ox)} and the flow "
                f"viewBox's middle is {show(flow_mid)} — off centre by "
                f"{show(abs(ox - flow_mid))} units. Centring the box no longer "
                f"lands it on the lectern's inner vertical.")

    # 2. THE INNER VERTICAL IS AT THE FRAME BOX'S MIDDLE.
    frame_left, frame_right = frame_vb[0], frame_vb[0] + frame_vb[2]
    frame_top = frame_vb[1]
    verticals = sorted({s[0][0] for s in frame
                        if s[0][0] == s[1][0] and min(s[0][1], s[1][1]) == frame_top})
    inner = [vx for vx in verticals if frame_left < vx < frame_right]
    if not inner:
        findings.append(
            f"{page.name}: the lectern has no vertical between its own sides — "
            f"nothing in the frame continues the drawing")
    for vx in inner:
        if vx != frame_mid:
            findings.append(
                f"{page.name}: the lectern's inner vertical stands at frame x "
                f"{show(vx)} and the frame viewBox's middle is {show(frame_mid)} "
                f"— off centre by {show(abs(vx - frame_mid))} units. The source "
                f"is centred and this is what it has to meet.")

    if verbose:
        print(f"  {page.name}: flow viewBox {show(flow_vb[2])} wide, middle "
              f"{show(flow_mid)}; lectern {show(frame_vb[2])} wide, middle "
              f"{show(frame_mid)}")
        if orb:
            print(f"    source at flow x {show(rational(orb.group(1)))}")
        for vx in inner:
            print(f"    inner vertical at frame x {show(vx)}")

    return findings, True


def check_sheets(verbose):
    """The two declarations that make the two middles land on each other."""
    findings = []
    acts = ACTS.read_text(encoding="utf-8")
    components = COMPONENTS.read_text(encoding="utf-8")

    if not declares(acts, ".sp-drawing", "justify-self", "center"):
        findings.append(
            "acts.css: .sp-drawing does not declare `justify-self: center`. Its "
            "width is min(100%, a function of 100vh), so on every viewport where "
            "the height cap binds — every laptop — the drawing is narrower than "
            "the container, and a grid item with a definite width is START "
            "aligned. The source ends half the shortfall left of the hairline "
            "that continues it: 85.22 px at 1440 x 900, 256.22 at 1440 x 720.")
    if not declares(components, ".cf-pin__inner > *", "justify-self", "center"):
        findings.append(
            "components.css: .cf-pin__inner > * does not declare "
            "`justify-self: center`. The lectern is the other half of the seam's "
            "centre; uncentred, the drawing is aimed at a middle the card no "
            "longer stands on.")
    # Both must be centred by justify-self and not by an auto margin, which is
    # the form the fix took in .cf-pin__inner's note and the form it must keep.
    if declares(acts, ".sp-drawing", "margin-inline", "auto"):
        findings.append(
            "acts.css: .sp-drawing centres itself with `margin-inline: auto`. "
            "That declaration is (0,1,0) and loses to an element margin written "
            "at (0,1,1) — see .cf-pin__inner's note, where exactly that cascade "
            "left one of three rows flush while the other two centred.")

    if verbose and not findings:
        print("  acts.css: .sp-drawing { justify-self: center }")
        print("  components.css: .cf-pin__inner > * { justify-self: center }")
    return findings


def main():
    parser = argparse.ArgumentParser(
        description="The two halves of the seam meet on a shared centre.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="print each viewBox's middle and the two declarations")
    args = parser.parse_args()

    findings, seams = [], 0
    for page in sorted([*PATTERNS.glob("*.html"), *PROTOTYPES.glob("*.html")]):
        f, found = check_page(page, args.verbose)
        findings += f
        seams += 1 if found else 0

    if not seams:
        print("seam centre: no drawing hands over to a frame — the selector went stale")
        return 1

    findings += check_sheets(args.verbose)

    if findings:
        print(f"\nseam centre: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1
    print(f"seam centre OK — {seams} seam(s): the source on the flow box's middle, "
          f"the inner vertical on the frame box's middle, and both boxes centred "
          f"in the container by justify-self")
    return 0


if __name__ == "__main__":
    sys.exit(main())
