#!/usr/bin/env python3
"""The drawing fits the viewport it plays in.

THE FINDING THIS EXISTS FOR. Measured in Chromium at 1440 x 900 on the render
before this file was written, the statement-to-process drawing on
patterns/landing-page.html — the sensor field, the root that grows out of it,
and the stem between them — stood 871.15 px tall. The viewport below the nav is
810.06 px. 1.075. There was no scroll position at which the whole of it was on
screen: every stage of the sequence played with part of itself cut off, at every
viewport the pin gate admits, and the read-out was simply "the lines are messy".

Nothing in the repository could say so. Sixty-four checks held the drawing's
angles, its ratios, its terminals, its crossings, its labels, its seam with the
lectern and its departure from the void — every one of them INSIDE the drawing's
own box, and the box's own size against the screen was the one relationship
none of them had. Four routines worked this figure for months. It was found by
measuring, once, in a browser.

It is not a motion finding and lengthening the hold does not fix it: swept at
42vh, 70vh, 95vh and 120vh of hold, the share of moving scroll with the whole
drawing on screen went 33 %, 33 %, 26 %, 36 %. Noise around a third. The
binding constraint was height.

WHAT IS CHECKED, and it is arithmetic on the files plus one measured table.

The drawing runs from the topmost glow in the field down to the foot of the
root. Both ends are pinned by other checks:

  * the foot lands on the lectern's rail (check-flow-handover.py), which is a
    page-flow position, and
  * the root departs from the void's centre, which is HALF THE FIGURE'S viewBox
    (check-void-departure.py, identity 2: `top: 50%`, cy x 2 == viewBox height).

so the drawing's height decomposes exactly:

    H = s x (V/2 + extent + travel) + Rest

    V       the figure's viewBox height, read from the page
    extent  the field's vertical semi-extent, max(|cy - V/2| + r) over the
            instruments, computed from the page
    travel  --iso-travel, in viewBox units, read from the shipping sheet
    s       px per drawing unit = the figure's rendered width / 1200
    Rest    the figure's foot to the rail, which is page furniture

The first three terms are the drawing's own geometry and are read out of the
files. s and Rest are rendered quantities and are MEASURED — the table below —
for the same reason check-void-departure.py and check-flow-handover.py carry
measured tables: the alternative is deriving the pin stage's centring, the
section rhythm and a container query from source, which is a second renderer.
The decomposition was verified against the browser at all nine viewports and
reproduces the measured height to under a tenth of a pixel.

WHAT THAT BUYS. Any edit to the FIGURE fires this check: a fatter glow at the
field's rim, another row of instruments, a taller viewBox, a void moved off
centre. Those are exactly the edits that produced the finding — the old field's
extent was an outcome of the largest of a hundred and forty-five hand-picked
radii (52.5, two rows from the top) rather than a decision, and the box was
sized to hold it.

WHAT IT CANNOT SEE, stated so it is not mistaken for covered:

  1. Rest goes stale if the page furniture between the statement section and
     the pinned one moves. It is measured, not derived. A change there needs
     this table re-measured, and the run below prints what it used.
  2. Fitting is not the same as being SHOWN whole. Even where the drawing fits,
     it is inside the band for only 1 - 17 % of the scroll it moves through,
     because nothing holds it still while it is there. That is the hold's
     brief, and this check is its precondition, not its substitute.
  3. The consent banner is 144 px of the viewport's foot on a first visit.
     check-consent-clearance.py owns that; the usable band below is the nav's
     only.

THE THREE VIEWPORTS THAT STILL DO NOT FIT are the three short ones, and they
carry their measured ratio as a ceiling rather than 1.00 — a ratchet, so the
work is visible and cannot get worse without the build saying so. They are the
same three rows check-void-departure.py's table already calls out: the stage's
height cap binds, --lp-measure narrows the flow, and the figure does not narrow
with it. At 720 px of viewport the root alone — Rest, from the figure's foot to
the rail — is 386 to 413 px of a 630 px band, so the figure would have to be
under 835 px wide for the drawing to fit, and no rule makes it so. Closing
those three means moving the seam or capping the figure's width, which is a
change to where the lines go and not to their size.

stdlib only, no build step, no dependency — the same contract as the checks
beside it.

    python3 scripts/check-figure-fits.py
    python3 scripts/check-figure-fits.py -v
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
# THE STATEMENT FIGURE LEFT THE LANDING PAGE with the five acts (2026-07-29):
# acts 1 and 2 draw the same argument as a scroll composition, so the static
# band it replaced is gone from the page and lives on in the component that
# publishes it. The drawing did not change; where it ships did.
PAGE = ROOT / "design-system" / "components" / "statement.html"
CSS = ROOT / "design-system" / "assets" / "css" / "components.css"

SENSOR = "cf-stmt-sensor"
CIRCLE_RE = re.compile(
    r'<circle\b[^>]*class="([^"]*)"[^>]*\bcx="([-\d.]+)"[^>]*\bcy="([-\d.]+)"'
    r'[^>]*\br="([-\d.]+)"')
SVG_RE = re.compile(r'<svg\b[^>]*class="([^"]*)"[^>]*viewBox="([^"]*)"(.*?)</svg>', re.S)
TRAVEL_RE = re.compile(r"\.cf-statement\s+\.cf-iso\s*\{[^}]*--iso-travel:\s*([\d.]+)")

# THE MEASURED TABLE. Chromium 141 headless, device scale 1, consent banner
# dismissed, `scroll-behavior: auto` forced so a sampled position is the
# position. Per viewport: the nav band, the figure's rendered width, and Rest —
# the figure's foot to the frame's rail, in page pixels. The drawing's height is
# sampled at every 12 px of scroll through the whole approach and the MAXIMUM is
# taken, because the scene carries an arrival offset and the question is whether
# the reader ever sees the drawing cut, not whether it fits at rest.
#
#   viewport      nav     figure w     Rest     ceiling
MEASURED = [
    ((1024,  720), 89.94,   911.38,  361.53, 1.000),
    ((1280,  720), 89.94,  1139.22,  386.22, 1.084),   # short: see above
    ((1280,  800), 89.94,  1139.22,  386.22, 1.000),
    ((1366,  768), 89.94,  1215.75,  400.56, 1.057),   # short: see above
    ((1440,  720), 89.94,  1280.02,  412.91, 1.184),   # short: see above
    ((1440,  900), 89.94,  1280.02,  412.91, 1.000),
    ((1600,  900), 89.94,  1280.00,  439.56, 1.000),
    ((1920, 1080), 89.94,  1280.00,  536.90, 1.000),
    ((2560, 1440), 89.94,  1280.00,  716.90, 1.000),
]

# The three short rows are held to what they measure today and no worse. Float
# noise only — this is not slack for a regression to hide in.
RATCHET_TOL = 0.002

# The basis both drawings share. → check-void-departure.py, identity 1.
BASIS = 1200.0


def statement_figure(text):
    """The .cf-iso that carries the sensor field: its viewBox and its body."""
    for classes, view_box, body in SVG_RE.findall(text):
        if "cf-iso" in classes.split() and SENSOR in body:
            parts = view_box.split()
            return float(parts[2]), float(parts[3]), body
    return None, None, None


def field_extent(body, void_y):
    """How far the field reaches ABOVE the void, glows included.

    Above, and not `abs` — the drawing's top edge is the topmost glow and its
    bottom edge is the root's foot five hundred pixels lower, so the field's
    downward reach sets nothing and counting it overstates the height. On the
    field this replaced, which was 15.6 units deeper below the void than above
    it, the two readings differ by 16.6 px at 1440 x 900: `abs` says 887.80 and
    the browser says 871.15. Upward reach says 871.15."""
    reach = 0.0
    count = 0
    for classes, _cx, cy, r in CIRCLE_RE.findall(body):
        if SENSOR not in classes.split():
            continue
        count += 1
        reach = max(reach, void_y - float(cy) + float(r))
    return reach, count


def main():
    ap = argparse.ArgumentParser(
        description="The statement-to-process drawing fits the viewport it plays in.")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    text = PAGE.read_text(encoding="utf-8")
    css = CSS.read_text(encoding="utf-8")

    vb_w, vb_h, body = statement_figure(text)
    if body is None:
        print("figure fits: the statement's .cf-iso is not on the page — "
              "the selector went stale")
        return 1
    if vb_w != BASIS:
        print(f"figure fits: the statement figure is {vb_w:g} units wide and every "
              f"number here is on the {BASIS:g}-unit basis the two drawings share")
        return 1

    void_y = vb_h / 2                      # identity 2, held next door
    extent, instruments = field_extent(body, void_y)
    if instruments < 8:
        print("figure fits: the statement draws no sensor field — there is no "
              "extent to measure")
        return 1

    travel = TRAVEL_RE.search(css)
    if not travel:
        print("figure fits: `.cf-statement .cf-iso { --iso-travel }` is not in "
              "components.css — the arrival offset cannot be read")
        return 1
    travel = float(travel.group(1))

    own = void_y + extent + travel         # the drawing's own share, in units

    findings, rows = [], []
    for (w, h), nav, fig_w, rest, ceiling in MEASURED:
        s = fig_w / BASIS
        height = s * own + rest
        usable = h - nav
        ratio = height / usable
        rows.append((w, h, usable, height, ratio, ceiling))
        if ratio > ceiling + RATCHET_TOL:
            over = height - ceiling * usable
            findings.append(
                f"{w} x {h}: the drawing is {height:.2f} px against {usable:.2f} px "
                f"of viewport below the nav — {ratio:.3f} of it, {over:.2f} px over "
                f"the {ceiling:.3f} this row is held to. The reader cannot see the "
                f"whole of it at any scroll position.")

    if args.verbose or findings:
        print(f"  figure viewBox   {vb_w:g} x {vb_h:g}   void at y {void_y:g}")
        print(f"  field            {instruments} instruments, "
              f"vertical semi-extent {extent:.1f} units")
        print(f"  arrival travel   {travel:g} units")
        print(f"  the drawing owns V/2 + extent + travel = {own:.1f} units")
        print()
        print(f"  {'viewport':>12} {'usable':>8} {'drawing':>9} {'ratio':>7} "
              f"{'ceiling':>8}")
        for w, h, usable, height, ratio, ceiling in rows:
            mark = "  <-- over" if ratio > ceiling + RATCHET_TOL else ""
            print(f"  {w:>5} x {h:>4} {usable:8.2f} {height:9.2f} {ratio:7.3f} "
                  f"{ceiling:8.3f}{mark}")
        print()

    if findings:
        print(f"figure fits: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        print("\n  The drawing's height is s x (V/2 + extent + travel) + Rest and the\n"
              "  first three terms are the figure's own. Shrink the field's reach or\n"
              "  the box that holds it — scripts/gen-stmt-field.py owns both — or\n"
              "  re-measure the table here if the page furniture below the figure\n"
              "  has moved.")
        return 1

    worst = max(rows, key=lambda r: r[4] / r[5])
    print(f"figure fits OK — {len(rows)} viewports, the drawing on "
          f"{own:.1f} units of its own; tightest is {worst[0]} x {worst[1]} at "
          f"{worst[4]:.3f} of the {worst[5]:.3f} it is held to")
    return 0


if __name__ == "__main__":
    sys.exit(main())
