#!/usr/bin/env python3
"""A scaled line figure states its domain three times. Hold the three together.

components/line.html defines .cf-line in two sentences that, read together,
are an equation:

    .cf-line__bounds   "The frame's own extent, in words, above its top edge.
                        The only number in the figure that is not a datum —
                        and required, because the floor is not assumed to be
                        zero."
    --v                "Per point, and per .cf-line__step. Where it sits in
                        the frame, 0 at the floor and 1 at the ceiling."

So for every point and every scale rung in a figure,

    printed value = floor + --v * (ceiling - floor)

and the three places a figure writes that map down — the bounds line, the
scale rungs (`--v` beside a printed number), and every `.cf-line__val` beside
its point's `--v` — must all be the same affine map. Nothing read them
together, and each of the three is edited by a different kind of change: the
bounds line by a re-framing, the rungs by a re-scaling, the values by a
correction to the data.

WHAT THIS WAS WRITTEN FOR. The evidence line on patterns/landing-page.html
prices a 30 GWh plant's electricity. The research note behind it quoted
Eurostat's €0.2264/kWh — the 500-2 000 MWh band — for a plant that burns
30 000 MWh, where the same publication's price is €0.1595/kWh. The lab found
it, and the correction moved the whole figure: the bill from €6.79m to
€4.785m, the frame from €6.0-7.0m to €4.0-5.0m, both rungs, all twelve values
and both captions. It did not move the paragraph above the markup that derives
them, which went on saying "the plant that changes nothing stays at €6.79m ...
6.79 -> 6.45 / 6.39 / 6.32 / 6.26 / 6.20. Frame €6.0-7.0m, --v = (value-6)/1"
on two pages for as long as the corrected figure shipped under it. A comment
is not something a check can hold. The three statements IN THE MARKUP are, and
they are where the same half-finished correction lands next: a `--v` left on
the old frame renders a point in a plausible place with a wrong number beside
it, and no page of this system looks wrong when it happens.

WHY THE POLYLINE IS NOT A FOURTH TERM. `.cf-line__draw` carries the same
series again as `points="x,y ..."` on a 0-100 viewBox, and y is (1 - --v) *
100 — a real fourth statement. It is left out because pairing a polyline with
a set is a guess: a figure may draw two traces and list two sets, or draw one
and list one, and only their document order relates them. A gate whose report
can name the wrong series is worse than no gate on that term.

TOLERANCE IS THE PRINTED PRECISION AND NOTHING WIDER. A value printed to two
decimals may sit half a unit of the last place from what --v says and no
further: "€4,79 Mio." against --v: .785 is exact at the rounding, and
"€4,78 Mio." is a finding. Rungs and bounds are compared the same way.

NUMBER FORMAT IS TAKEN FROM THE EDITION, not guessed from the string. The
German pages write "€4,79 Mio." and the generated English ones "€4.79m" —
"4.500" is four and a half in one and four thousand five hundred in the other,
so the separators are decided by whether the file sits under patterns/en/,
which is exactly how scripts/build-i18n.py decides them.

    python3 scripts/check-line-scale.py        # exit 1 on a finding
    python3 scripts/check-line-scale.py -v     # print every figure it read

Proven failing on the reintroduced defect — the pre-correction value put back
on one point of the shipped figure:

    design-system/patterns/landing-page.html
        figure 1, frame 4.0 - 5.0
        POINT   --v: .367 says 4.367, printed "€6,20 Mio." (6.2)
"""

import argparse
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DESIGN = ROOT / "design-system"

# The English edition is generated into this directory and writes English
# separators; everything else on this site is German. build-i18n.py draws the
# same line in the same place.
EN_DIR = DESIGN / "patterns" / "en"

FIGURE = re.compile(r'<figure class="cf-line"[^>]*>')
BOUNDS = re.compile(r'class="cf-line__bounds"[^>]*>(.*?)</p>', re.S)
STEP = re.compile(r'<li class="cf-line__step"[^>]*style="([^"]*)"[^>]*>(.*?)</li>', re.S)
POINT = re.compile(r'<li class="cf-line__point[^"]*"[^>]*style="([^"]*)"[^>]*>(.*?)</li>', re.S)
VAL = re.compile(r'<span class="cf-line__val">(.*?)</span>', re.S)
VAR_V = re.compile(r'--v:\s*(-?[\d.]+)')

# A run of digits with at most one group separator run around it. Currency
# marks, per cents, "Mio.", "m", "p. a." and the rest are the label, not the
# number.
NUMBER = re.compile(r'-?\d[\d.,\u00a0\u202f ]*\d|-?\d')


def text(fragment):
    """Markup to the string a reader sees, whitespace collapsed."""
    plain = re.sub(r"<[^>]*>", "", fragment)
    return re.sub(r"\s+", " ", html.unescape(plain).replace("\u00a0", " ")).strip()


def parse_number(token, english):
    """One printed number to (value, decimals), or None if it is not one.

    `decimals` is what the figure committed to in print and is the tolerance
    the comparison is allowed: a number set to two places says nothing about
    the third.
    """
    raw = token.strip().replace(" ", "").replace("\u00a0", "").replace("\u202f", "")
    dec, group = (".", ",") if english else (",", ".")
    if raw.count(dec) > 1:
        return None
    whole, _, frac = raw.partition(dec)
    whole = whole.replace(group, "")
    if not re.fullmatch(r"-?\d+", whole) or (frac and not re.fullmatch(r"\d+", frac)):
        return None
    return float(whole + ("." + frac if frac else "")), len(frac)


def numbers_in(label, english):
    return [n for n in (parse_number(t, english) for t in NUMBER.findall(label)) if n]


def close(printed, expected, decimals):
    """Printed to `decimals` places is allowed half of the last place."""
    return abs(printed - expected) <= 0.5 * 10 ** -decimals + 1e-9


def figures(source):
    """Each <figure class="cf-line"> body. They do not nest."""
    for opening in FIGURE.finditer(source):
        end = source.find("</figure>", opening.end())
        if end != -1:
            yield source[opening.end():end]


def check_figure(block, english):
    findings = []
    bounds = BOUNDS.search(block)
    if not bounds:
        return ["BOUNDS  no .cf-line__bounds — the frame's extent is required, "
                "because the floor is not assumed to be zero"], None
    label = text(bounds.group(1))
    ends = numbers_in(label, english)
    if len(ends) < 2:
        return ['BOUNDS  "%s" does not state two ends' % label], None
    (floor, floor_dp), (ceiling, ceiling_dp) = ends[0], ends[1]
    if ceiling == floor:
        return ['BOUNDS  "%s" opens and closes on %g' % (label, floor)], None
    span = ceiling - floor

    def rung_or_point(kind, style, body, printed):
        v = VAR_V.search(style)
        if not v:
            findings.append('%-7s "%s" carries no --v' % (kind, printed))
            return
        expected = floor + float(v.group(1)) * span
        got = numbers_in(printed, english)
        if not got:
            findings.append('%-7s --v: %s is printed "%s", which states no number'
                            % (kind, v.group(1), printed))
            return
        value, decimals = got[0]
        if not close(value, expected, decimals):
            findings.append('%-7s --v: %s says %.6g, printed "%s" (%g)'
                            % (kind, v.group(1), expected, printed, value))

    for style, body in STEP.findall(block):
        rung_or_point("RUNG", style, body, text(body))
    for style, body in POINT.findall(block):
        val = VAL.search(body)
        if val:
            rung_or_point("POINT", style, body, text(val.group(1)))
    return findings, (floor, ceiling)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    reports = []
    read = 0
    for path in sorted(DESIGN.rglob("*.html")):
        source = path.read_text(encoding="utf-8")
        if 'class="cf-line"' not in source:
            continue
        english = EN_DIR in path.parents
        for index, block in enumerate(figures(source), start=1):
            read += 1
            findings, frame = check_figure(block, english)
            if args.verbose:
                where = "frame %g - %g" % frame if frame else "no frame"
                print("  %s figure %d, %s" % (path.relative_to(ROOT), index, where))
            for finding in findings:
                reports.append((path.relative_to(ROOT), index, frame, finding))

    if reports:
        last = None
        for rel, index, frame, finding in reports:
            if rel != last:
                print("\n%s" % rel)
                last = rel
            head = "figure %d" % index
            if frame:
                head += ", frame %g - %g" % frame
            print("    %s" % head)
            print("        %s" % finding)
        print("\ncheck-line-scale: %d figure(s) whose bounds, rungs and values "
              "are not one map." % len({(r, i) for r, i, _, _ in reports}))
        return 1

    print("check-line-scale: %d line figure(s) — every rung and every printed "
          "value is the figure's own bounds and --v, to the place it is set in."
          % read)
    return 0


if __name__ == "__main__":
    sys.exit(main())
