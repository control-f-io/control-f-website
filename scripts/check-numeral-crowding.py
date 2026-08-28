#!/usr/bin/env python3
"""No two numerals on the root may collide, and none may leave the drawing.

check-label-clearance.py holds how far a numeral stands
off THE STROKE IT ANNOTATES, and it holds it in pixels for a stated reason —
.lp-flow__val's own note: "A clearance from the stroke stated in the drawing's
units would close up as the box shrinks; these hold 12 px off the line at every
viewport the gate admits." That is true, it is checked, and it is half of a
placement. The other half is the distance from one numeral to the NEXT one, and
nothing held it.

WHY THAT HALF IS THE ONE THAT BREAKS. The clearance off the stroke is a
translate in px and survives any scale. The POSITIONS are proportional —

    left: calc(var(--x) / 1200 * 100%)      .lp-flow__val, acts.css

— and the type is a constant 11 px, stated as a deliberate choice one comment
above: "both are real HTML at the label ramp's 11 px so they do not scale with
the drawing." Both halves of that sentence are right and together they mean the
lattice of points the numerals hang off contracts with the box while the glyph
boxes do not. At 375 the 60 units between two branch points are 16.7 px on
screen and each numeral is 53.7 px wide.

WHAT WAS SHIPPING. The markup states its own clearance eighteen times, and
every one of the eighteen says the same three words: "nearest other 12.42 px AT
THE GATE FLOOR". The placement was solved at one width. The drawing renders at
every width — below 64rem it is a figure in a one-column stage — and there the
same law puts numerals on top of each other. Measured on the shipped page, in
Chromium, counting only pairs whose boxes actually intersect:

    viewport   drawing     intersecting pairs   numerals outside the drawing
     320        280.0 px          16                  3
     375        333.8             11                  2
     414        368.5              7                  2
     480        427.2              6                  1
     640        569.6              2                  1
     768        683.5              0                  1   12.4 bar, 5.2 px out
     900        801.0              0                  0
    1024        911.4              0                  0

Nothing errors, nothing scrolls sideways, and no screenshot of the design
system shows it, because the design system is looked at on a desktop. On a
phone "690 V", "4.2 mm/s" and "51 Hz" print on top of each other and the
drawing's own claim — 8 400 /s, the number act 2's copy names in words — sits
underneath "3 200 /s".

WHAT THIS CHECK DOES. It rebuilds every numeral's box from the markup at an
arbitrary drawing width and asks two questions of the set: does any pair
intersect, and does any box leave the drawing. Both are decided by arithmetic
on --x / --y / --tx / --ty and the type's own metrics, so this needs no browser:

    box width       len(text) x ADVANCE
    box height      --text-xs x --leading-normal
    X, Y            --x / 1200 x W,  --y / 1200 x W
                    (the same divisor on both axes: .lp-flow-data is
                     aspect-ratio 1200/620 inset to the drawing, so its height
                     is W x 620/1200 and --y is read against that)
    left, top       X + --tx, Y + --ty, with -100% resolving to the box's own
                    extent on that axis and -50% to half of it

Verified against the render before it was trusted: the layer box and the svg
box are identical to 0.01 px at 320, 375, 768, 1024 and 1280, and this model
reproduces the browser's own overlap count at every width in the table above.

THE TWO RULES.

  RULE ONE -- THE THRESHOLD IS SUFFICIENT. acts.css renders the annotation only
  above a container width, on .sp-root, which is the drawing's box:

      @container sp-root (min-width: 56rem) {
        .lp-flow-data > * { display: revert; }
      }

  This recomputes the CROWDING FLOOR — the narrowest drawing width at which the
  whole set is clear — and asserts the threshold is at or above it. The floor
  solves to 746 px; 56rem is 896 and clears it by 150, with 11.88 px between the
  nearest pair and 12.50 px to the nearest edge — against the 12.60 px the law
  was solved to at the gate floor's own 911.4. It then checks every width from
  the threshold up to 2000 px, so a threshold that is high enough at its own
  value and wrong above it still fails.

  RULE TWO -- BELOW THE THRESHOLD THE LAYER IS EMPTY. The suppression takes
  every child of .lp-flow-data and exempts none, so there is no arithmetic to
  do down there: nothing is painted, and what is not painted cannot collide or
  leave the plate. What is held instead is that the exemption stays gone, on
  both sides of it — in the stylesheet, a suppression written `> *` and not
  `> :not(...)`; in the markup, no numeral carrying .lp-flow__head, the class
  that named the exempt one.

  Until 2026-08-28 one numeral WAS exempt — 8 400 /s, the value on the trunk,
  the number act 2's copy also names in words — and this rule was the arithmetic
  that kept it on the plate at every width from 200 px up. That arithmetic never
  failed. The picture did: one 11 px numeral hanging off the trunk of a drawing
  whose other seventeen are gone reads as a label nobody finished taking out
  rather than as the drawing's own claim, and it is the only type inside the
  figure at the widths where the figure has the least room for any. The rate
  still reaches a phone — in the paragraph under the drawing, in words, in both
  editions.

WHAT THIS CHECK IS NOT. It says nothing about whether a numeral is placed on
the right side of its own stroke — that is check-flow-label-law.py — or whether
the clearance off the stroke is one number, which is check-label-clearance.py.
The three are only together a placement rule. Nor does it look at .sp-annots,
act 1's twenty-one sensor readings: those are placed by a different law,
against a sliced backdrop in `1cqh` units, and eleven of them sit outside the
viewport at 320. That is a finding and it is not this one.

THE TYPE'S BOX IS THE SYSTEM'S OWN NUMBERS, not four more literals in a
checker: the size is --text-xs, the height is that times --leading-normal, and
the advance is the size times 0.6 em plus --tracking-label, all read out of
tokens.css. One term is not in any file — 0.6 em, the advance of a monospaced
face — so it is the single stated constant here, and it is the one thing in
this check that was verified against a render rather than derived: measured
across all eighteen numerals in Chromium at 11 px, 6.7101 to 6.7125 px per
character, uniform to the fourth decimal and identical at 320 and at 1280,
against the 6.7100 this arithmetic gives. The four-thousandths of a pixel is
why the crowding floor reads 746 here and 747 off the measured maximum; at a
threshold 150 px above it, nothing turns on which.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-numeral-crowding.py
    python3 scripts/check-numeral-crowding.py -v
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system" / "assets" / "css"
PATTERNS = ROOT / "design-system" / "patterns"
PROTOTYPES = ROOT / "design-system" / "prototypes"

DRAWING_CLASS = "lp-flow"
NUMERAL_CLASSES = ("lp-flow__val", "lp-flow__read")
# The class the one exempt numeral used to carry. Nothing declares it any more;
# it is named here so that its return is a finding rather than a silent
# re-exemption.
EXEMPT_CLASS = "lp-flow__head"
LAYER_CLASS = "lp-flow-data"

# A monospaced face advances 0.6 em; .t-label adds --tracking-label on top.
# Measured 6.7101-6.7125 px/char over the eighteen; the maximum is used.
MONO_ADVANCE_EM = 0.6
# The widths this file reasons over. The low end is below any viewport the
# system admits (320 px gives a 280 px drawing); the high end is past --container-max.
SCAN_LO, SCAN_HI = 200, 2000

FIGURE_RE = re.compile(r'<svg\b[^>]*class="([^"]*)"[^>]*viewBox="([^"]*)"', re.S)
SPAN_RE = re.compile(r'<span\b[^>]*class="([^"]*)"[^>]*style="([^"]*)"[^>]*>([^<]*)</span>', re.S)
TOKEN_RE = re.compile(r"^\s*(--[\w-]+)\s*:\s*([^;]+);", re.M)
# The rule that reinstates the suppressed numerals, and the width it asks for.
GUARD_RE = re.compile(
    r"@container\s+sp-root\s*\(\s*min-width\s*:\s*([\d.]+)(rem|px)\s*\)\s*\{"
    r"[^{}]*\.%s\s*>\s*\*\s*\{[^{}]*\}" % LAYER_CLASS, re.S)
# The rule that suppresses them in the first place.
SUPPRESS_RE = re.compile(
    r"\.%s\s*>\s*\*\s*\{[^{}]*display\s*:\s*none" % LAYER_CLASS, re.S)
# A suppression that lets something through: the shape the layer carried until
# 2026-08-28, and the one way the single numeral comes back.
EXEMPT_RE = re.compile(r"\.%s\s*>\s*:not\(" % LAYER_CLASS, re.S)

PLAIN_RE = re.compile(r"^(-?\d+(?:\.\d+)?)px$")
CALC_RE = re.compile(r"^calc\(\s*-100%\s*-\s*(\d+(?:\.\d+)?)px\s*\)$")


def tokens():
    """--text-xs and --leading-normal, so the type's box is the system's own
    numbers and not two more literals in a checker."""
    raw = (CSS / "tokens.css").read_text(encoding="utf-8")
    return {n: v.split("/*")[0].strip() for n, v in TOKEN_RE.findall(raw)}


def px(value, root_px=16.0):
    value = value.strip()
    if value.endswith("rem"):
        return float(value[:-3]) * root_px
    if value.endswith("px"):
        return float(value[:-2])
    return float(value)


def style_vars(style):
    out = {}
    for decl in style.split(";"):
        if ":" in decl and decl.strip().startswith("--"):
            name, _, value = decl.partition(":")
            out[name.strip()] = value.strip()
    return out


def offset(value, extent):
    """One component of the placement offset in px. -100% and -50% resolve
    against the numeral's own extent on that axis, which is what makes a box
    out of a point."""
    text = " ".join(value.split())
    if text == "-50%":
        return -extent / 2
    if text in ("0", "0px", ""):
        return 0.0
    m = PLAIN_RE.match(text)
    if m:
        return float(m.group(1))
    m = CALC_RE.match(text)
    if m:
        return -(extent + float(m.group(1)))
    return None


class Numeral:
    def __init__(self, text, classes, var, advance, line_height):
        self.text = " ".join(text.split()) or "(blank)"
        self.raw = text
        self.classes = classes
        self.exempt = EXEMPT_CLASS in classes
        self.w = len(text) * advance
        self.h = line_height
        self.x = float(var["--x"])
        self.y = float(var["--y"])
        self.tx = var.get("--tx", "0px")
        self.ty = var.get("--ty", "0px")

    def box(self, W, vb_w):
        """(left, top, right, bottom) in the drawing's own pixels at width W."""
        X, Y = self.x / vb_w * W, self.y / vb_w * W
        left = X + offset(self.tx, self.w)
        top = Y + offset(self.ty, self.h)
        return left, top, left + self.w, top + self.h


def faults(numerals, W, vb_w, vb_h):
    """Escapes and intersecting pairs for a set of numerals at width W."""
    H = W * vb_h / vb_w
    boxes = [(n, n.box(W, vb_w)) for n in numerals]
    escapes = []
    for n, (l, t, r, b) in boxes:
        out = []
        if l < 0:
            out.append(f"{-l:.2f} px past the left edge")
        if r > W:
            out.append(f"{r - W:.2f} px past the right edge")
        if t < 0:
            out.append(f"{-t:.2f} px above the top edge")
        if b > H:
            out.append(f"{b - H:.2f} px below the bottom edge")
        if out:
            escapes.append((n, "; ".join(out)))
    pairs = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, c = boxes[i][1], boxes[j][1]
            ox = min(a[2], c[2]) - max(a[0], c[0])
            oy = min(a[3], c[3]) - max(a[1], c[1])
            if ox > 0 and oy > 0:
                pairs.append((boxes[i][0], boxes[j][0], ox, oy))
    return escapes, pairs


def crowding_floor(numerals, vb_w, vb_h):
    """The narrowest drawing width at which the whole set is clear, or None."""
    for W in range(SCAN_LO, SCAN_HI + 1):
        e, p = faults(numerals, float(W), vb_w, vb_h)
        if not e and not p:
            return W
    return None


def guard_threshold(acts, findings):
    """The width acts.css reinstates the full annotation at, in px."""
    if EXEMPT_RE.search(acts):
        findings.append(
            f"acts.css: the suppression on .{LAYER_CLASS} exempts a child — it is "
            f"written `> :not(...)` rather than `> *`. That is the shape the layer "
            f"carried until 2026-08-28, and it puts one numeral back on a phone: "
            f"alone in the layer, on a drawing whose other seventeen are gone.")
    if not SUPPRESS_RE.search(acts):
        findings.append(
            f"acts.css: nothing suppresses .{LAYER_CLASS} > * — the "
            f"drawing renders all its numerals at every width, and below 746 px of "
            f"drawing they intersect. See this file's own table.")
        return None
    m = GUARD_RE.search(acts)
    if not m:
        findings.append(
            f"acts.css: the numerals are suppressed but nothing reinstates them inside "
            f"`@container sp-root (min-width: ...)`, so the drawing carries no "
            f"annotation at any width and the eighteen values are dead markup.")
        return None
    value, unit = m.group(1), m.group(2)
    if unit != "rem":
        findings.append(
            f"acts.css: the numeral threshold is {value}{unit} — every threshold in this "
            f"system is in rem so it tracks the reader's own font size, and this one "
            f"decides whether 11 px type fits. See the breakpoint register in tokens.css.")
    return px(f"{value}{unit}")


def check_page(page, acts, advance, line_height, verbose):
    text = page.read_text(encoding="utf-8")
    m = next((m for m in FIGURE_RE.finditer(text)
              if DRAWING_CLASS in m.group(1).split()), None)
    if m is None:
        return [], 0
    vb = [float(v) for v in m.group(2).replace(",", " ").split()]
    vb_w, vb_h = vb[2], vb[3]

    numerals = []
    for classes, style, body in SPAN_RE.findall(text):
        names = classes.split()
        if not any(c in names for c in NUMERAL_CLASSES):
            continue
        var = style_vars(style)
        if "--x" not in var or "--y" not in var:
            continue
        n = Numeral(body, names, var, advance, line_height)
        if offset(n.tx, n.w) is None or offset(n.ty, n.h) is None:
            return ([f"{page.name}: the numeral {n.text!r} states an offset this check "
                     f"cannot resolve (--tx {n.tx!r}, --ty {n.ty!r}); "
                     f"check-label-clearance.py holds the three legal forms."], 0)
        numerals.append(n)
    if not numerals:
        return [], 0

    findings = []
    threshold = guard_threshold(acts, findings)

    # --- RULE TWO, the markup half: no numeral is exempt --------------------
    exempt = [n for n in numerals if n.exempt]
    if exempt:
        findings.append(
            f"{page.name}: {len(exempt)} numeral(s) carry .{EXEMPT_CLASS} and none may — "
            f"the suppression takes the whole layer now, so below the threshold that "
            f"class names nothing, and above it every numeral renders anyway. "
            f"They are: {', '.join(repr(n.text) for n in exempt)}.")

    if threshold is None:
        return findings, len(numerals)

    # RULE ONE — the threshold is at or above the crowding floor, and stays
    # clear above it.
    floor = crowding_floor(numerals, vb_w, vb_h)
    if floor is None:
        findings.append(
            f"{page.name}: no drawing width between {SCAN_LO} and {SCAN_HI} px renders all "
            f"{len(numerals)} numerals clear of each other — the placement law itself is "
            f"unsatisfiable, not merely solved at one width.")
    else:
        if threshold < floor:
            e, p = faults(numerals, threshold, vb_w, vb_h)
            detail = []
            if p:
                worst = max(p, key=lambda t: t[2] * t[3])
                detail.append(f"{worst[0].text!r} and {worst[1].text!r} intersect by "
                              f"{worst[2]:.2f} x {worst[3]:.2f} px")
            if e:
                detail.append(f"{e[0][0].text!r} is {e[0][1]}")
            findings.append(
                f"{page.name}: the full annotation is reinstated at {threshold:.0f} px of "
                f"drawing and the crowding floor is {floor} px, so between the two there "
                f"are {len(p)} intersecting pairs and {len(e)} numerals off the plate. At "
                f"the threshold itself: " + "; ".join(detail) + ".")
        for W in range(int(threshold), SCAN_HI + 1):
            e, p = faults(numerals, float(W), vb_w, vb_h)
            if e or p:
                findings.append(
                    f"{page.name}: the full annotation is clear at the threshold but not at "
                    f"{W} px of drawing — {len(p)} intersecting pairs, {len(e)} off the "
                    f"plate. A threshold is a floor, not a window.")
                break

    # RULE TWO is above and in guard_threshold: below the threshold nothing is
    # painted, so there is no set here to measure. The widths from SCAN_LO to the
    # threshold are still scanned — by crowding_floor, on the whole set, which is
    # how the floor is found in the first place.

    if verbose:
        print(f"  {page.name}: {len(numerals)} numerals, viewBox {vb_w:g} x {vb_h:g}, "
              f"crowding floor {floor} px, threshold {threshold:.0f} px, "
              f"none exempt below it")
        for W in (280.0, 333.79, 683.5, 911.4, 1109.59):
            e, p = faults(numerals, W, vb_w, vb_h)
            print(f"      W={W:8.2f}  intersecting pairs {len(p):2d}  off the plate {len(e)}")
    return findings, len(numerals)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every drawing and its floor, not only the failures")
    args = ap.parse_args()

    tok = tokens()
    font_px = px(tok.get("--text-xs", "0.6875rem"))
    leading = float(tok.get("--leading-normal", "1.3"))
    tracking = tok.get("--tracking-label", "0.01em")
    tracking_em = float(tracking.replace("em", "")) if tracking.endswith("em") else 0.0
    advance = font_px * (MONO_ADVANCE_EM + tracking_em)
    line_height = font_px * leading

    acts = (CSS / "acts.css").read_text(encoding="utf-8")

    findings, total, drawings = [], 0, 0
    for page in sorted([*PATTERNS.glob("*.html"), *PROTOTYPES.glob("*.html")]):
        f, n = check_page(page, acts, advance, line_height, args.verbose)
        findings.extend(f)
        total += n
        drawings += 1 if n else 0

    if not drawings:
        sys.exit("check-numeral-crowding: no .lp-flow drawing found — the check has "
                 "nothing to hold, which is itself a finding.")

    # A fault in acts.css is one fault, not one per page that loads it.
    findings = list(dict.fromkeys(findings))

    if findings:
        print(f"check-numeral-crowding: {len(findings)} finding(s)\n")
        for f in findings:
            print(f"  - {f}")
        print(f"\n  advance {advance:.4f} px/char, line height {line_height:.2f} px, "
              f"from --text-xs / --leading-normal / --tracking-label.")
        sys.exit(1)

    print(f"check-numeral-crowding: {total} numerals across {drawings} drawing(s) — no pair "
          f"intersects and none leaves the drawing, at every width each is rendered at.")


if __name__ == "__main__":
    main()
