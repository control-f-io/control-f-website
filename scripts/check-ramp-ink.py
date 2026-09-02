#!/usr/bin/env python3
"""The ink on a ramp step is recomputed from the swatch under it.

A step on foundations/colors.html is a rectangle painted the hex it names, with
that name printed on top of it in 10 px mono. So the ink is not a preference:
it is whichever of the two ends of the neutral ramp reads on that particular
hex, and the answer moves the day the hex does.

It was written by hand. Twelve of the thirty-eight steps carried `color:#fff`
inside their style attribute, and eleven of the twelve were right. The twelfth
was Sky 700 — white on #5684A9 is 3.99:1, under the 4.5:1 a 10 px label owes,
where black on the same swatch is 5.27:1 and clears it. It reads as a copy down
the row rather than as a decision: the two steps below it in the same ramp are
genuinely dark and genuinely take white, and this one was given what they had.

WHY NOTHING CAUGHT IT, which is the part worth keeping. check-contrast.py is
the register of the pairs the TOKENS guarantee, and neither end of this pair is
a token: the background is a literal in a style attribute and the ink was
another one beside it. Every other check that reads colour reads a stylesheet,
and this decision was not in one. It is the same boundary README already
records for the grid-track rule — *a rule enforced over stylesheets is not
enforced over `style=` attributes, and the system's own documentation pages are
where those attributes live* — read a second time, on contrast instead of on
tracks. The fix moved the decision into a class, `.docs-ramp__step--dark` in
docs.css, and this script is what stops the class from being applied to the
wrong swatch the next time a ramp is retuned.

WHAT A SCREENSHOT CANNOT DO HERE is the same thing it cannot do for
check-contrast.py, and one step worse. 3.99 against 4.5 is invisible; the
reviewer looking at the ramp sees a legible number on a blue square, because
they are not the reader this floor exists for. And the swatch it fails on is
the one place on the site where a wrong ink is least likely to be reported:
nobody reads a step label, they look at the colour beside it.

WHAT IT CHECKS, over foundations/colors.html — the one page that draws this
component, and the whole of its scope for that reason. A second page drawing a
ramp would be read too; there is no register:

  inline     no step spells its ink in a style attribute. The background is
             the specimen and belongs there; the ink is a decision about the
             specimen and belongs in the class.
  floor      the ink the step actually takes clears 4.5:1 against the hex the
             step declares. WCAG 2.x AA for text, and the label is 10 px, so
             the large-text exception is not available to it.
  better     the ink it takes is the better of the two available. A step that
             clears the floor on the worse ink is still a step whose ink was
             chosen by hand and got the other answer — Violett 500 at 6.01:1
             black against 3.49:1 white is the closest any of them comes, and
             it is not close.

Ratios are computed the way check-contrast.py computes them, from the sRGB
values as painted. Nothing here composites: both ends are opaque.

    python3 scripts/check-ramp-ink.py       # the rule
    python3 scripts/check-ramp-ink.py -v    # every step, its two ratios and
                                            # the ink it takes
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = ROOT / "design-system"

PAGE = BASE / "foundations" / "colors.html"
SHEET = BASE / "assets" / "css" / "docs.css"

# The two inks a step can take, and where each one comes from. Black is
# inherited — .docs-ramp__step declares no colour, so a step takes the page's
# --text-primary, which is --cf-schwarz. White is the modifier's --grey-000.
INK_DEFAULT = ("#000000", "black")
INK_MODIFIER = ("#FFFFFF", "--grey-000")
MODIFIER = "docs-ramp__step--dark"

# 4.5:1, WCAG 2.x AA for text. The label is 0.625rem mono: not large text under
# any definition, so 3:1 is not available to it.
FLOOR = 4.5

STEP = re.compile(
    r'<span class="(?P<cls>docs-ramp__step[^"]*)"'
    r'\s+style="(?P<style>[^"]*)"\s*>(?P<label>[^<]*)</span>'
)
RAMP_NAME = re.compile(r'<span class="docs-ramp__name">([^<]+)</span>')


def channel(value):
    v = value / 255
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def luminance(hexcolour):
    h = hexcolour.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def ratio(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def audit():
    findings = []
    seen = []

    if not PAGE.exists():
        return [("%s" % PAGE.relative_to(ROOT), "the page this check reads does not exist")], seen

    text = PAGE.read_text(encoding="utf-8")
    where = str(PAGE.relative_to(ROOT))

    # The modifier has to be declared by the stylesheet, or the eleven steps
    # carrying it are taking the inherited ink and nobody has noticed.
    sheet = SHEET.read_text(encoding="utf-8") if SHEET.exists() else ""
    if ".%s" % MODIFIER not in sheet:
        findings.append((where, ".%s is on the markup and nothing declares it "
                                "in %s" % (MODIFIER, SHEET.relative_to(ROOT))))

    # Which ramp each step belongs to, for the report. The name always stands
    # before the steps it names.
    marks = [(m.start(), m.group(1)) for m in RAMP_NAME.finditer(text)]

    def ramp_of(pos):
        name = "?"
        for start, n in marks:
            if start < pos:
                name = n
            else:
                break
        return name

    for m in STEP.finditer(text):
        style = m.group("style")
        classes = m.group("cls").split()
        label = m.group("label").strip()
        ramp = ramp_of(m.start())
        at = "%s %s" % (ramp, label)

        bg = re.search(r"background:\s*(#[0-9A-Fa-f]{3,6})", style)
        if not bg:
            findings.append((where, "%s declares no background hex; this check "
                                    "cannot recompute an ink without one" % at))
            continue
        bg = bg.group(1)

        # inline
        ink_inline = re.search(r"(?<!-)\bcolor:\s*([^;]+)", style)
        if ink_inline:
            findings.append((where, "%s spells its ink in the style attribute "
                                    "(color:%s). The background is the specimen and "
                                    "belongs there; the ink is a decision about it "
                                    "and belongs in .%s"
                             % (at, ink_inline.group(1).strip(), MODIFIER)))
            continue

        dark = MODIFIER in classes
        taken, taken_name = INK_MODIFIER if dark else INK_DEFAULT
        other, other_name = INK_DEFAULT if dark else INK_MODIFIER

        r_taken, r_other = ratio(bg, taken), ratio(bg, other)
        seen.append((at, bg, taken_name, r_taken, other_name, r_other))

        # floor
        if r_taken < FLOOR:
            findings.append((where, "%s prints %s on %s at %.2f:1, under the "
                                    "%.1f:1 a 10 px label owes. %s on the same swatch "
                                    "is %.2f:1"
                             % (at, taken_name, bg, r_taken, FLOOR,
                                other_name, r_other)))
            continue

        # better
        if r_other > r_taken:
            findings.append((where, "%s takes %s at %.2f:1 where %s reads %.2f:1 "
                                    "on the same swatch. The ink is whichever of the "
                                    "two the hex answers to, not a preference"
                             % (at, taken_name, r_taken, other_name, r_other)))

    return findings, seen


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every step, its two ratios and the ink it takes")
    args = ap.parse_args()

    findings, seen = audit()

    if args.verbose:
        for at, bg, taken, r_taken, other, r_other in seen:
            print("  %-14s %-8s  %-10s %6.2f:1   (%-10s %6.2f:1)"
                  % (at, bg, taken, r_taken, other, r_other))
        print()

    if findings:
        for where, why in findings:
            print("%s\n    %s" % (where, why), file=sys.stderr)
        print("\n%d ramp step%s whose ink is not the one its own hex answers to. "
              "3.99:1 and 5.27:1 render identically to everybody who is not the "
              "reader the floor exists for."
              % (len(findings), "" if len(findings) == 1 else "s"), file=sys.stderr)
        return 1

    tightest = min((r for _, _, _, r, _, _ in seen), default=0.0)
    dark = sum(1 for _, _, taken, _, _, _ in seen if taken == INK_MODIFIER[1])
    print("ramp ink: %d step(s) across %d ramp(s) — %d on the light ink, %d on "
          "black; every one the better of its two, tightest %.2f:1 against a "
          "%.1f:1 floor."
          % (len(seen), len(RAMP_NAME.findall(PAGE.read_text(encoding='utf-8'))),
             dark, len(seen) - dark, tightest, FLOOR))
    return 0


if __name__ == "__main__":
    sys.exit(main())
