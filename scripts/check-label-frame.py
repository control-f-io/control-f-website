#!/usr/bin/env python3
"""A layer placed in a drawing's coordinates is given the drawing's box.

The seventy-second, and it is about the one join nothing here was watching: the
seam between a drawing and the HTML laid over it.

THE CONSTRUCTION. Twice in this system a set of labels is too much type to put
inside an <svg> -- the camera would scale it, the font would not be the page's,
and a <text> cannot wrap -- so the labels are HTML, absolutely positioned over
the drawing at percentages a generator computed:

    .lp-flow__val, .lp-flow__read   left: calc(var(--x) / 1200 * 100%)
    .map__tag                       left: var(--x)

Both are percentages OF THE POSITIONED ANCESTOR. Both were computed as
percentages OF THE VIEWBOX. That is a silent identity: it holds only while the
ancestor has the viewBox's shape, and nothing in either rule says so.

WHERE IT BROKE. `.map__tags` is `inset: 0` on `.map-box`. Below the pin gate
`.map` is `block-size: auto`, the svg takes its intrinsic height, the box IS
the drawing and the identity holds. Above the gate the stage hands the map row
`minmax(0, 1fr)` of whatever the copy and the legend leave over; the box came
out between 1.85 and 2.50 wide-per-tall against the drawing's 1.7943;
preserveAspectRatio="xMidYMid meet" fitted the drawing inside that and centred
it; and every label sat half a letterbox off the point it named. Measured on
the shipped page, label anchor minus the point it names, horizontally:

    viewport     box aspect   Konstanz   Berlin   Deutschland   United Kingdom
     320- 768      1.7943       0.0       0.0        0.0            0.0
    1024x 800      2.3633     -12.4     +27.0      +39.1          -38.4
    1280x 900      2.4016     -16.4     +35.8      +51.8          -51.0
    1440x 900      2.4952     -18.9     +41.3      +59.8          -58.8
    1920x1080      1.8471      -1.9      +4.2       +6.1           -6.0

It is L * (1 - 2x) with L the half-letterbox: zero at the middle of the
drawing, worst at its edges, sign flipping across the centre. So the four moved
in four directions by four amounts and none of it read as one displacement.
What it looked like on the page was four separate placement mistakes --
KONSTANZ printed through the German border instead of standing beside its dot,
BERLIN forty pixels adrift of the dot it names, DEUTSCHLAND running off the
country's east edge, UNITED KINGDOM sixty pixels west of Britain, out in the
Irish Sea. Nothing overflowed, nothing scrolled sideways, every check passed,
and the one framing where it nearly vanishes (1920, aspect 1.85) is the one a
desktop review is most likely to be done at.

THE OTHER MEMBER WAS ALREADY CORRECT, AND FOR THE OTHER REASON. .lp-flow is
`height: auto` at every tier, so its box is its intrinsic box, its aspect is
the viewBox's at every width measured (1.9355 at 375, 768, 1280, 1440, 1920),
and `meet` has nothing to letterbox. Two members, two answers, one law -- which
is what makes this a rule and not a note about a map.

THE LAW. A layer whose children are placed at percentages of a drawing's
viewBox must resolve those percentages against the box that viewBox actually
paints into. There are exactly two ways to get there and the system uses both:

  UNSIZED  the svg is never given a size across its cross axis, so `meet` has
           no slack and the element's box is the drawing. .lp-flow's answer,
           and the cheaper one -- it costs a declaration and no machinery.
  FRAMED   the svg IS given a box of its own, so the layer is handed `meet`'s
           own result: the largest box of the viewBox's ratio that fits,
           centred in what contains it. .map__tags' answer, and the only one
           available once a pinned stage owns the height.

WHY A SCRIPT. Every declaration involved is individually correct and they are
six hundred lines apart. `.map-box { block-size: 100% }` is right -- the stage
needs the row filled. `.map__tags { inset: 0 }` is right for a layer over a box.
`left: var(--x)` is right for a generated placement. The fault is in no line;
it is in the identity three of them assume between two rectangles, and it is
invisible in a screenshot at any width where the two happen to be close.

stdlib only, no build step, no dependency. Same python3 that serves the pages.
"""

import argparse
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system" / "assets" / "css"
PAGES = ROOT / "design-system"

# THE SHIPPING STYLESHEETS. docs.css and preview.css are documentation chrome
# and never ship -- the same scope every check in this directory takes.
SHEETS = ["tokens.css", "base.css", "components.css", "acts.css"]

# ---------------------------------------------------------------- the registry
#
# ONE ENTRY PER PLACED LAYER, and RULE 0 below holds that there are no others.
# A third drawing that lays HTML over itself does not get to inherit either
# answer by accident: it fails here until somebody writes down which one it
# takes and why.
#
#   placed   the rule that positions a child at a percentage of the layer
#   layer    the positioned ancestor those percentages resolve against
#   svg      the drawing whose viewBox the percentages were computed in
#   answer   UNSIZED or FRAMED, above
#   ratio    FRAMED only: the custom property carrying the viewBox's ratio
#   box      FRAMED only: what the layer is fitted into, and what therefore has
#            to be the size container the two min()s read 100cqh off
FRAMES = [
    dict(placed=".lp-flow__val, .lp-flow__read", layer=".lp-flow-data",
         svg="lp-flow", answer="UNSIZED", ratio=None, box=None),
    # The canopy beads: same drawing, same UNSIZED construction as the
    # numeral layer one entry up — inset to .sp-root with the viewBox's own
    # aspect-ratio, so the percentages resolve against the flow box to the
    # pixel. Only left is driven (--x); the row's top is the canopy constant,
    # which check-canopy-sources.py holds to the leaves' shared far-end y.
    dict(placed=".lp-flow__src", layer=".lp-flow-sources",
         svg="lp-flow", answer="UNSIZED", ratio=None, box=None),
    dict(placed=".map__tag", layer=".map__tags",
         svg="map", answer="FRAMED", ratio="--map-ar", box=".map-box"),
    # THE THIRD MEMBER IS A MATERIAL, NOT A DRAWING, and that is a difference
    # this registry had not had to hold before. .cf-construct__figure is the
    # object half of the construction layer — foundations/construction.html
    # puts the isometric stack in it at 0 0 640 640, foundations/logo.html the
    # symbol at -150 -30 780 600 — so the "one drawing, one coordinate system"
    # clause above cannot apply to it and is not being waived by accident.
    #
    # What replaces it is that NOTHING SHARED IS COMPUTED FROM A VIEWBOX HERE.
    # The other two members divide the drawing's own units down in CSS, which
    # restates one viewBox in the stylesheet and is exactly what RULE 1 holds.
    # This member's placements are authored per instance, as whole percentages
    # on the element — (coordinate − viewBox min) / viewBox extent, done once,
    # in the markup, beside the drawing it belongs to. There is no number in
    # the CSS that a second viewBox could falsify, and RULE 1 is turned into
    # its converse below: a divisor appearing in this rule is the finding.
    #
    # The UNSIZED law is unchanged and is the whole of what still binds it. The
    # percentages are the drawing's only while .cf-construct__figure takes its
    # intrinsic box, and that holds for any viewBox — which is precisely why a
    # material may take this answer and may not take FRAMED, where the ratio is
    # one number in one declaration.
    dict(placed=".cf-construct__label", layer=".cf-construct__plate",
         svg="cf-construct__figure", answer="UNSIZED", ratio=None, box=None,
         per_instance=True),
]

# The signature of a placed child: a percentage of the containing block, driven
# by a generated custom property. Both members match it; RULE 0 is that nothing
# else in the shipping CSS does.
#
# ANCHORED ON THE DECLARATION BOUNDARY AND NOT ON THE LINE, which is the
# difference between holding this file and appearing to. It read `^\s*(left|top)`
# under re.M and the two members both happen to be written one declaration to a
# line, so it passed and looked right — while a rule written on ONE line, which
# is how a third of this stylesheet is written (`.map-box { block-size: 100%;
# container-type: size; }`), matched nothing at all. Caught by adding an
# unregistered placed layer as a one-liner and watching RULE 0 stay quiet.
PLACED = re.compile(r"(?:^|[;{])\s*(?:left|top)\s*:\s*[^;]*var\(\s*--[xy]\s*\)", re.M)

# `left: calc(var(--x) / 1200 * 100%)` -- the drawing's own units, divided down
# to a percentage. The divisor is a viewBox dimension restated in CSS.
DIVISOR = re.compile(r"(left|top)\s*:\s*calc\(\s*var\(\s*--[xy]\s*\)\s*/\s*"
                     r"([\d.]+)\s*\*\s*100%\s*\)")

# THE DRIFT A RATIO MISMATCH BUYS, in CSS px across the full width of the
# drawing. The generator prints the viewBox at two decimals and the ratio at
# six, so the two cannot agree exactly and asking them to would be asking the
# rounding to be a bug. A tenth of a pixel across a thousand is the bound: at
# that the worst-placed label on the map moves by less than the hairline it
# stands next to.
DRIFT_PX = 0.1


def blocks(text):
    """(selector, body, line) for every rule, preludes carried on the selector.

    Comments go first: this repository writes paragraphs inside them and a
    declaration quoted in prose is not a declaration.
    """
    text = re.sub(r"/\*(?:[^*]|\*(?!/))*\*/", lambda m: "\n" * m.group(0).count("\n"), text)
    out, depth, sel_start, i = [], 0, 0, 0
    stack = []
    while i < len(text):
        c = text[i]
        if c == "{":
            head = text[sel_start:i].strip()
            stack.append((head, i + 1))
            depth += 1
            sel_start = i + 1
        elif c == "}":
            if stack:
                head, body_start = stack.pop()
                body = text[body_start:i]
                # a nested rule's body still holds its own children's text; only
                # the declarations directly in it are this rule's.
                own = re.sub(r"\{(?:[^{}]|\{[^{}]*\})*\}", "", body)
                if head and not head.startswith("@"):
                    out.append((head, own, text[:body_start].count("\n") + 1))
            depth -= 1
            sel_start = i + 1
        i += 1
    return out


def viewboxes(cls):
    """Every viewBox carried by an <svg class=... cls ...> in design-system/."""
    found = {}
    pat = re.compile(r'<svg\b[^>]*\bclass="([^"]*)"[^>]*\bviewBox="([^"]*)"'
                     r'|<svg\b[^>]*\bviewBox="([^"]*)"[^>]*\bclass="([^"]*)"')
    for page in sorted(PAGES.rglob("*.html")):
        for m in pat.finditer(page.read_text(encoding="utf-8")):
            classes, vb = (m.group(1), m.group(2)) if m.group(1) else (m.group(4), m.group(3))
            if cls in classes.split():
                nums = [float(v) for v in vb.replace(",", " ").split()]
                if len(nums) == 4:
                    found.setdefault(tuple(nums), []).append(page.relative_to(ROOT))
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    sheets = {n: (CSS / n).read_text(encoding="utf-8") for n in SHEETS}
    rules = [(n, sel, body, line) for n, t in sheets.items() for sel, body, line in blocks(t)]
    all_css = "\n".join(sheets.values())
    failures, rows = [], []

    # WHERE THE CAMERA STARTS EXISTING. Everything above this line in acts.css
    # is the tier that renders without a scroll timeline; everything below it is
    # inside `@supports (animation-timeline: view())`, which is the only place
    # `.map__cam` is ever given a transform. RULE 4 reads it.
    acts = sheets["acts.css"]
    m = re.search(r"@supports \(animation-timeline: view\(\)\)", acts)
    gate_line = acts[:m.start()].count("\n") + 1 if m else 0

    # ------------------------------------------------------------------ RULE 0
    # Every placed layer in the shipping CSS is registered. A drawing that lays
    # HTML over itself is a construction with a law, not a one-off.
    registered = {f["placed"] for f in FRAMES}
    for name, sel, body, line in rules:
        if not PLACED.search(body):
            continue
        norm = " ".join(sel.split())
        if norm not in registered:
            failures.append(
                "%s:%d  %s\n"
                "      places a child at a percentage driven by var(--x)/var(--y) and is\n"
                "      not registered in FRAMES. A layer placed in a drawing's coordinates\n"
                "      resolves those percentages against its POSITIONED ANCESTOR, which is\n"
                "      the drawing's box only while nothing has given the svg a shape of its\n"
                "      own. Register it with the answer it takes — UNSIZED or FRAMED."
                % (name, line, norm))

    # ---------------------------------------------------------- the members
    for f in FRAMES:
        placed, layer, svgcls = f["placed"], f["layer"], f["svg"]
        vbs = viewboxes(svgcls)
        if not vbs:
            failures.append(
                "FRAMES lists .%s, and no <svg class=\"%s\"> in design-system/ carries a\n"
                "      viewBox. The registry names a drawing that is not there."
                % (svgcls, svgcls))
            continue
        if len(vbs) > 1 and not f.get("per_instance"):
            failures.append(
                ".%s carries %d different viewBoxes across the pages that draw it:\n"
                "      %s\n"
                "      One drawing, one coordinate system — the placements below are\n"
                "      percentages of it and cannot be right in two of them at once."
                % (svgcls, len(vbs),
                   "; ".join("%s in %s" % (" ".join(str(n) for n in k),
                                           ", ".join(str(p) for p in v))
                             for k, v in vbs.items())))
            continue
        vb = next(iter(vbs)) if len(vbs) == 1 else None
        ratio = vb[2] / vb[3] if vb else None

        body = next((b for n, s, b, l in rules if " ".join(s.split()) == placed), None)
        line = next((l for n, s, b, l in rules if " ".join(s.split()) == placed), 0)
        if body is None:
            failures.append(
                "FRAMES lists `%s`, and no rule in the shipping stylesheets has that\n"
                "      selector. The registry has gone stale against the CSS."
                % placed)
            continue

        # ------------------------------------------------------------- RULE 1
        # A placement that divides the drawing's own units down to a percentage
        # restates the viewBox in CSS. The two numbers have to agree — and on a
        # member that carries a viewBox per instance there is no ONE number for
        # them to agree with, so the same clause reads the other way: a divisor
        # in a material's rule is a single drawing's dimension imposed on every
        # drawing that will ever use it, and the second one to arrive is placed
        # against the first one's frame with nothing failing.
        if f.get("per_instance") and DIVISOR.search(body):
            failures.append(
                "`%s` is registered per-instance and divides by a viewBox dimension\n"
                "      in CSS. Its drawings do not share a coordinate system: write the\n"
                "      placement as a whole percentage on the element, beside the drawing\n"
                "      it was solved against." % placed)
        for axis, div in DIVISOR.findall(body) if vb else []:
            want = vb[2] if axis == "left" else vb[3]
            if abs(float(div) - want) > 0.005:
                failures.append(
                    "acts.css:%d  %s\n"
                    "      %s divides by %s; .%s's viewBox is %s across that axis.\n"
                    "      The divisor IS the viewBox dimension, written a second time in\n"
                    "      CSS. Change the drawing and every label on it slides, silently."
                    % (line, placed, axis, div, svgcls, want))

        # ------------------------------------------------------------- RULE 2
        lay = [(n, b, l) for n, s, b, l in rules if " ".join(s.split()).endswith(layer)]
        laytext = "\n".join(b for _, b, _ in lay)

        if f["answer"] == "UNSIZED":
            # The svg must never be given a cross-axis size, so `meet` has no
            # slack to centre in and the element's box is the drawing.
            sized = []
            for n, sel, b, l in rules:
                if not re.search(r"(^|[\s,>+~])\.%s([\s,{:]|$)" % re.escape(svgcls),
                                 " ".join(sel.split()) + " "):
                    continue
                for prop, val in re.findall(r"\b(block-size|height)\s*:\s*([^;]+)", b):
                    if val.strip() not in ("auto", "revert", "unset", "initial"):
                        sized.append("%s:%d  %s { %s: %s }"
                                     % (n, l, " ".join(sel.split()), prop, val.strip()))
            if sized:
                failures.append(
                    "`%s` is registered UNSIZED — its percentages are the drawing's\n"
                    "      only while .%s takes its intrinsic box. These give it one:\n"
                    "        %s\n"
                    "      preserveAspectRatio then letterboxes the drawing inside a box of\n"
                    "      another shape and every label slides off the point it names by\n"
                    "      half the slack. Either take the size back off, or move this entry\n"
                    "      to FRAMED and give %s the meet box."
                    % (placed, svgcls, "\n        ".join(sized), layer))
            rows.append((placed, layer, svgcls, "UNSIZED", ratio, "—"))
            continue

        # FRAMED: the layer is handed `meet`'s own result.
        prop = f["ratio"]
        need = {
            "inline-size": r"min\(\s*100cqw\s*,\s*100cqh\s*\*\s*var\(\s*%s\s*\)\s*\)" % prop,
            "block-size": r"min\(\s*100cqh\s*,\s*100cqw\s*/\s*var\(\s*%s\s*\)\s*\)" % prop,
            "margin": r"\bauto\b",
        }
        for p, want in need.items():
            got = re.search(r"\b%s\s*:\s*([^;]+)" % re.escape(p), laytext)
            if not got or not re.search(want, got.group(1)):
                failures.append(
                    "`%s` is registered FRAMED and %s does not carry its `%s`.\n"
                    "      The three together ARE preserveAspectRatio=\"xMidYMid meet\":\n"
                    "        inline-size: min(100cqw, 100cqh * var(%s));\n"
                    "        block-size:  min(100cqh, 100cqw / var(%s));\n"
                    "        margin: auto;\n"
                    "      the two min()s fit the drawing's ratio into whichever axis runs\n"
                    "      out first, and `margin: auto` against the layer's own inset:0\n"
                    "      centres the leftover — which is the xMid/YMid half. Found: %s\n"
                    "      One axis alone is the fault half-fixed: the labels still slide,\n"
                    "      by less, and it reads as placement error rather than as geometry."
                    % (placed, layer, p, prop, prop,
                       got.group(1).strip() if got else "nothing"))

        # The layer can only read the cross axis if the box it fits into is a
        # size container. `size` and not `inline-size`: it is the HEIGHT the
        # width has to be derived from, and inline-size leaves 100cqh with
        # nothing to resolve against.
        box = f["box"]
        cont = [(n, l) for n, s, b, l in rules
                if re.search(r"container-type\s*:\s*size\b", b)
                and re.search(r"(^|[\s,>+~])%s([\s,{:]|$)" % re.escape(box),
                              " ".join(s.split()) + " ")]
        if not cont:
            failures.append(
                "`%s` is FRAMED and nothing declares `container-type: size` on %s,\n"
                "      the box it is fitted into. 100cqh then has no container to resolve\n"
                "      against, both min()s fall over and the layer keeps whatever inset:0\n"
                "      gave it — the fault returns whole, with the machinery for the fix\n"
                "      still sitting in the file. `container-type: inline-size` does not\n"
                "      answer it either: the whole point is deriving the width from the\n"
                "      HEIGHT, and inline-size is the one that withholds the height."
                % (placed, box))

        # ------------------------------------------------------------- RULE 4
        # A FRAMED layer's percentages were solved AT ONE FRAMING of a camera
        # that only exists inside the gate. Outside it the camera computes to
        # `none`, the drawing is whatever it is with no transform, and the
        # placement means nothing -- so the layer renders in the gated tier and
        # nowhere else. Measured at 375 x 812 before this pairing: Konstanz
        # 89 px from its dot, Berlin 37, DEUTSCHLAND 43, UNITED KINGDOM 109,
        # all four painting at once on a framing none of them was placed for.
        base = [b for n, s, b, l in rules
                if " ".join(s.split()) == layer and l < gate_line]
        gated = [b for n, s, b, l in rules
                 if " ".join(s.split()) == layer and l > gate_line]
        hidden = any(re.search(r"\bdisplay\s*:\s*none\b", b) for b in base)
        shown = any(re.search(r"\bdisplay\s*:\s*(revert|block|flow-root)\b", b)
                    for b in gated)
        if not (hidden and shown):
            failures.append(
                "`%s` is placed per-framing and %s %s.\n"
                "      The camera lives inside `@supports (animation-timeline: view())`\n"
                "      and nowhere else; outside it `transform` computes to none and every\n"
                "      --x/--y is a percentage of a framing that never happened. The layer\n"
                "      takes `display: none` in the base tier and `display: revert` inside\n"
                "      the gate — the same pairing .lp-flow-data's readings take, for the\n"
                "      same reason. Found: base %s, gated %s."
                % (placed, layer,
                   "paints in the base tier" if not hidden else "is never revealed inside the gate",
                   "hides it" if hidden else "does NOT hide it",
                   "reveals it" if shown else "does NOT reveal it"))

        # ------------------------------------------------------------- RULE 3
        # The ratio is the viewBox's, not a number that looked right once.
        decl = re.search(r"%s\s*:\s*([\d.]+)\s*;" % re.escape(prop), all_css)
        if not decl:
            failures.append(
                "`%s` is FRAMED on %s and nothing declares it. The layer's two min()s\n"
                "      fall back to nothing and the box goes to zero."
                % (placed, prop))
        else:
            got = float(decl.group(1))
            drift = abs(got - ratio) / ratio * vb[2]
            if drift > DRIFT_PX:
                failures.append(
                    "%s is %s; .%s's viewBox is %s x %s, ratio %.6f.\n"
                    "      That is %.2f px of label drift across the drawing's own width,\n"
                    "      against a bound of %.2f. The ratio is the viewBox's — it comes\n"
                    "      out of the generator beside the camera so it cannot be typed\n"
                    "      independently of the numbers it has to agree with."
                    % (prop, decl.group(1), svgcls, vb[2], vb[3], ratio, drift, DRIFT_PX))
            rows.append((placed, layer, svgcls, "FRAMED",
                         ratio, "%s = %s, %.3f px drift" % (prop, decl.group(1), drift)))

    if args.verbose:
        print("layers placed in a drawing's coordinates:\n")
        for placed, layer, svgcls, answer, ratio, note in rows:
            # A per-instance member has no one ratio to print, and printing a
            # number for it would be the registry asserting the thing its own
            # entry says is not true.
            print("  %-32s over %-22s .%-22s %-8s viewBox ratio %-8s %s"
                  % (placed, layer, svgcls, answer,
                     "per page" if ratio is None else "%.4f" % ratio, note))
        print()

    if failures:
        print("label frame: %d finding(s)\n" % len(failures))
        for f in failures:
            print("  - %s\n" % f)
        return 1

    print("label frame: %d placed layer(s), %d unsized, %d framed; "
          "every placement resolves against the box its drawing paints into."
          % (len(rows),
             sum(1 for r in rows if r[3] == "UNSIZED"),
             sum(1 for r in rows if r[3] == "FRAMED")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
