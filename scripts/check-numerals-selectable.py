#!/usr/bin/env python3
"""A numeral layer may be transparent to a pointer. Its numerals may not.

THE FINDING THIS EXISTS FOR. Act 2's root carries its readings as real HTML on
a layer of their own -- .lp-flow-data, `position: absolute; inset: 0 0 auto 0`
over the whole drawing, so that every value can be placed as a percentage of
the drawing's own box. That layer is `pointer-events: none`, and it has to be:
it is 1110 x 573 px of transparent sheet at 1440 x 900, and a sheet that size
taking a click is a sheet that swallows the figure under it.

pointer-events inherits. So the nineteen numerals on the sheet -- "8 400 /s",
"3 200 /s", "74 °C", "12.4 bar" -- inherited it too, and stopped being text
that a reader can do anything with. Measured on the shipped page at 1440 x 900
with the tree built, document.elementFromPoint at each numeral's own centre:

    before   0 of 19 returned the numeral   19 of 19 returned the <svg> under it
    after   19 of 19 returned the numeral    0 of 19 the <svg>

A drag across "1 360 /s" began a selection in whatever was beneath it, and a
double-click on a number selected nothing. Nothing looked wrong, nothing was
logged, and every gate in this directory stayed green: the layer paints
identically whether or not it can be hit, which is why this is a script and not
a review. The site's own argument for these numbers is that they ARE the
information -- acts.css spends a paragraph on why they are --text-secondary and
not --text-muted, "because the numbers can be read" -- and a number that can be
read and not taken is half published.

WHAT IS CHECKED, over every stylesheet in design-system/assets/css:

  For every rule whose selector is a NUMERAL LAYER -- a class ending in
  `-data`, the naming this system uses for "the layer that carries a drawing's
  values" -- that declares `pointer-events: none`, every class of the SAME
  block that declares a `color` must itself declare `pointer-events` at some
  value other than `none`.

  `color` is the test for "this rule carries text" rather than a list of class
  names, because ink is what text costs: a rule that sets a colour on a layer
  of numerals is setting the colour of glyphs. A decorative sibling on the same
  sheet -- a halo, a leader, a tick -- sets stroke or fill or nothing at all
  and is not asked to become hit-testable. That is the line, and it is the same
  one .lp-flow-data's own note draws: the sheet is not the text on it.

WHY NOT A BROADER RULE. "No visible text may compute pointer-events: none" is
the true statement and it needs a browser and a scroll position to evaluate --
this file gets none of either, and a check that cannot run is a comment. The
`-data` layer is where this system puts numerals on drawings, so it is where
the fault can recur: the map's tick labels sit on .map__tags, the sensor field's
readings on their own annotation list, and any future drawing that needs values
over it will reach for the same construction and inherit the same silence. One
layer matches today. The clause is written for the second one.

Exit 1 on any finding. Run with -v for the layers and numerals resolved.
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS_DIR = ROOT / "design-system" / "assets" / "css"

# A class ending in -data: the system's name for a drawing's value layer.
LAYER = re.compile(r"\.([a-z0-9]+(?:-[a-z0-9]+)*-data)\b")
# .block__element — the numerals of a block are its own elements.
ELEMENT = re.compile(r"\.([a-z0-9-]+__[a-z0-9-]+)\b")
DECL = r"(?:^|[;{\s])%s\s*:\s*([^;}]+)"


def rules(css):
    """(selector, body) for every rule with a declaration block.

    Comments are stripped first: this file is nine parts prose to one part CSS
    and a `pointer-events: none` inside a paragraph is not a declaration.
    """
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        sel, body = m.group(1).strip(), m.group(2)
        if not sel or sel.startswith("@"):
            continue
        yield sel, body


def declared(body, prop):
    m = re.search(DECL % prop, body)
    return m.group(1).strip() if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    findings = []
    resolved = []

    for path in sorted(CSS_DIR.glob("*.css")):
        parsed = list(rules(path.read_text(encoding="utf-8")))

        # Which -data layers on this sheet refuse the pointer, and for which block.
        sealed = {}
        for sel, body in parsed:
            if declared(body, "pointer-events") != "none":
                continue
            for layer in LAYER.findall(sel):
                sealed[layer] = layer[: -len("-data")]

        # Every inked element of those blocks has to opt back in.
        for sel, body in parsed:
            ink = declared(body, "color")
            if not ink:
                continue
            names = [n for n in ELEMENT.findall(sel)]
            for name in names:
                block = name.split("__")[0]
                if block not in sealed.values():
                    continue
                layer = block + "-data"
                pe = declared(body, "pointer-events")
                resolved.append((path.name, layer, "." + name, pe or "-", ink))
                if pe is None or pe == "none":
                    findings.append(
                        f"{path.name}: .{name} carries text (color: {ink}) inside "
                        f".{layer}, which is `pointer-events: none`. It inherits "
                        f"that, so the reader cannot select, drag across or copy "
                        f"it. Declare `pointer-events: auto` on the numerals; "
                        f"leave the layer alone."
                    )

    if args.verbose:
        if not resolved:
            print("no numeral layer declares pointer-events: none")
        for f, layer, name, pe, ink in resolved:
            print(f"{f:14s} .{layer:16s} {name:22s} pointer-events: {pe:6s} color: {ink}")
        print()

    for f in findings:
        print(f"FINDING     {f}")
    if findings:
        print(f"\n{len(findings)} finding(s).")
        return 1
    layers = sorted({r[1] for r in resolved})
    print(
        "OK  every numeral on a `pointer-events: none` value layer declares its "
        "own pointer-events and can be selected"
        + (f" ({', '.join('.' + l for l in layers)})" if layers else "")
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
