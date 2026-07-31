#!/usr/bin/env python3
"""No stroke may begin where nothing has arrived.

THE COMPANION TO check-flow-terminals.py, AT THE OTHER END OF TIME. That check
reads a drawing's SETTLED geometry and holds that no terminal stops in empty
space. This one reads the same drawing WHILE IT IS BEING DRAWN and holds the
other half of the same sentence: no stroke may START in empty space either. A
line that ends in mid-air and a line that begins in mid-air are one fault seen
from two ends, and only the first of them had a gate.

.lp-frame is the lectern the four process cards are built in: six strokes that
the page's own note calls a RELAY — "consecutive strokes chain instead of
running abreast", "one line handed on, which is what --o exists to make true".
Each stroke declares three numbers in its style attribute:

    --a   the point of the section's entry phase at which it begins
    --u   its length in the drawing's own units
    --o   the end it grows FROM, as a transform-origin against its own fill-box

and the stylesheet buys its window as --u x .lp-frame's one --relay-rate. So a
stroke is a segment plus a fixed end plus a start time, and the whole relay is
those three numbers repeated six times. Everything this check needs is in the
markup; nothing here needs a browser.

WHAT IT USED TO SAY. Measured off the shipped markup at HEAD, with the rate at
.024 points per unit, tracing the ink forward from the flow's arrival:

    stroke          --a   --o        origin        founded by            at
    M500 0V500       56   0 0        (500, 0)      the flow's handover   56
    M0 500H1000      62   0 0        (0, 500)      NOTHING               --
    M0 0V500         68   0 100%     (0, 500)      the base rail         62*
    M1000 0V500      72   0 100%     (1000, 500)   the base rail         86
    M0 0H500         78   100% 0     (500, 0)      the middle vertical   56
    M500 0H1000      80   0 0        (500, 0)      the middle vertical   56

    * and the base rail is founded by the left vertical, which is founded by
      the base rail. A pair that founds only each other is founded by nothing:
      neither of them is reachable from the point the drawing is handed the
      line at, which is why this check propagates from the source rather than
      asking each stroke about its neighbour.

Three of the six -- the base rail and both side verticals, which is the whole
bottom half of the lectern -- grew out of a corner the relay never reached. The
right vertical was the plainest of them: it began at entry 72 at the bottom-
right corner, and the base rail's tip, travelling 1000 units at .024, did not
arrive at that corner until entry 86, two points after the vertical had already
finished. Rendered at 1440 x 900 and sampled through the entry phase, the base
rail spent 78 px of scroll as a horizontal stroke growing out of empty space at
the bottom-left corner with the middle vertical's foot still 157 px above its
line, and the right vertical 62 px more doing the same at the other corner.

Every check this drawing already had reads it at rest or one stroke at a time:
check-relay-rate.py holds --u to its own path and every window to one rate,
check-grow-origin.py holds --o to the value the browser actually computes,
check-flow-terminals.py holds the settled geometry. None of them looks at two
strokes at the same MOMENT, which is the only time this is visible.

THE RULE. Walk the ink forward from the source:

  * THE SOURCE is the origin of the stroke with the smallest --a. That is the
    one point the drawing is handed the line at from outside itself -- on
    .lp-frame it is (500, 0), the middle vertical's head, which is where the
    flow's trunk lands and what check-flow-handover.py holds. Exactly one
    stroke may be founded there; every other stroke must be founded by ink
    this drawing has already laid.

  * A STROKE INKS ITS OWN LINE OUTWARD FROM ITS ORIGIN. Growing by
    `scale: 0 -> 1` about `--o` under `transform-box: fill-box`, a point d
    units along the stroke from its origin is drawn at --a + d x rate, because
    the window is --u x rate and --u IS the stroke's length. So arrival is
    linear in distance and needs no easing term: the stylesheet's timing
    function is `linear` and check-relay-rate.py holds the window's shape.

  * A STROKE IS FOUNDED when some other stroke has already inked its origin at
    or before its own --a. Not "another stroke passes through it" -- passing
    through it LATER is what the right vertical did.

Relax the arrival times until they stop moving, then report every stroke whose
origin is still unfounded at its own start. Both passes are checked: .lp-frame__
lit is .lp-frame__line's twin and carries the same three numbers, so a fix
applied to one pass and not the other is a half-drawn relay in colour.

WHAT THIS DOES NOT CLAIM. Not that the final drawing closes -- that is
check-flow-terminals.py's and the corner sweep's. Not that --o names the end
the browser uses -- check-grow-origin.py resolves that cascade. Not that the
relay is beautiful, only that at no moment does it show the reader a stroke
hanging off nothing.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-relay-chain.py
    python3 scripts/check-relay-chain.py -v
"""

import argparse
import re
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = [
    ROOT / "design-system" / "patterns" / "landing-page.html",
    ROOT / "design-system" / "prototypes" / "statement-to-process.html",
]
# The rate is one number for the whole relay and it lives with the component.
SHEET = ROOT / "design-system" / "assets" / "css" / "acts.css"

RATE_PROP = "--relay-rate"
PASSES = ("lp-frame__line", "lp-frame__lit")

PATH_RE = re.compile(r"<path\b[^>]*>", re.S)
CLASS_RE = re.compile(r'class="([^"]*)"')
STYLE_RE = re.compile(r'style="([^"]*)"')
D_RE = re.compile(r'\bd="([^"]*)"')
# M x y then exactly one H, V or L — the shape every stroke in this drawing is.
SEG_RE = re.compile(
    r"^\s*M\s*(-?[\d.]+)[\s,]+(-?[\d.]+)\s*"
    r"(?:([HV])\s*(-?[\d.]+)|L\s*(-?[\d.]+)[\s,]+(-?[\d.]+))\s*$"
)
# A transform-origin term this drawing uses: 0, 50%, 100%.
ORIGIN_TERMS = {"0": Fraction(0), "0%": Fraction(0),
                "50%": Fraction(1, 2), "100%": Fraction(1)}


def num(text):
    return Fraction(text).limit_denominator(10 ** 6)


def parse_segment(d):
    """(start, end) of a straight two-point path, or None."""
    m = SEG_RE.match(d)
    if not m:
        return None
    x1, y1 = num(m.group(1)), num(m.group(2))
    if m.group(3) == "H":
        return (x1, y1), (num(m.group(4)), y1)
    if m.group(3) == "V":
        return (x1, y1), (x1, num(m.group(4)))
    return (x1, y1), (num(m.group(5)), num(m.group(6)))


def parse_style(style):
    out = {}
    for part in style.split(";"):
        if ":" in part:
            k, v = part.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def fill_box_origin(seg, o):
    """The point --o names, against the stroke's own fill-box."""
    terms = o.split()
    if len(terms) != 2 or any(t not in ORIGIN_TERMS for t in terms):
        return None
    fx, fy = ORIGIN_TERMS[terms[0]], ORIGIN_TERMS[terms[1]]
    xs = sorted((seg[0][0], seg[1][0]))
    ys = sorted((seg[0][1], seg[1][1]))
    return (xs[0] + fx * (xs[1] - xs[0]), ys[0] + fy * (ys[1] - ys[0]))


def on_segment(p, seg):
    (x1, y1), (x2, y2) = seg
    if (x2 - x1) * (p[1] - y1) - (y2 - y1) * (p[0] - x1) != 0:
        return False
    return (min(x1, x2) <= p[0] <= max(x1, x2)
            and min(y1, y2) <= p[1] <= max(y1, y2))


def distance(a, b):
    """These strokes are axis-aligned, so one term is always zero."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def strokes_of(text, pass_class):
    out = []
    for tag in PATH_RE.findall(text):
        cls = CLASS_RE.search(tag)
        if not cls or pass_class not in cls.group(1).split():
            continue
        style = STYLE_RE.search(tag)
        d = D_RE.search(tag)
        out.append((tag, parse_style(style.group(1)) if style else {},
                    d.group(1) if d else None))
    return out


def check_pass(page, pass_class, rate, verbose):
    findings = []
    parsed = []
    for tag, style, d in strokes_of(page.read_text(encoding="utf-8"), pass_class):
        if d is None or "--a" not in style or "--u" not in style:
            findings.append(f"{page.name}: a .{pass_class} has no `d`, no --a or "
                            f"no --u: {tag[:90]}")
            continue
        seg = parse_segment(d)
        if seg is None:
            findings.append(
                f"{page.name}: `{d}` is not a straight two-point path. This "
                "check walks ink along a line and a shape it cannot walk is "
                "exactly where the next unfounded stroke would hide.")
            continue
        o = style.get("--o", "0 0")
        origin = fill_box_origin(seg, o)
        if origin is None:
            findings.append(f"{page.name}: `{d}` declares --o:{o}, which is not "
                            "a transform-origin this drawing uses (0, 50%, 100%).")
            continue
        parsed.append({"d": d, "seg": seg, "origin": origin,
                       "a": num(style["--a"]), "u": num(style["--u"])})
    if findings or not parsed:
        if not parsed:
            findings.append(f"{page.name}: no .{pass_class} strokes found — "
                            "the selector went stale")
        return findings

    # THE SOURCE, read off the relay rather than typed: the origin of the
    # stroke that starts first. Ties are a relay with two beginnings, which is
    # not one line handed on.
    first = min(s["a"] for s in parsed)
    starters = [s for s in parsed if s["a"] == first]
    if len(starters) > 1:
        findings.append(
            f"{page.name} .{pass_class}: {len(starters)} strokes share the "
            f"earliest --a ({first}) — "
            + ", ".join(s["d"] for s in starters)
            + ". A relay is one line handed on, so exactly one stroke may be "
              "handed it from outside the drawing.")
        return findings
    source = starters[0]

    # Relax arrival times forward from the source until they stop moving.
    INF = None
    lit = {id(source): source["a"]}          # stroke -> the --a it is founded at
    for _ in range(len(parsed) + 1):
        changed = False
        for s in parsed:
            if id(s) in lit:
                continue
            for t in parsed:
                if t is s or id(t) not in lit:
                    continue
                if not on_segment(s["origin"], t["seg"]):
                    continue
                arrival = t["a"] + distance(t["origin"], s["origin"]) * rate
                if arrival <= s["a"]:
                    lit[id(s)] = arrival
                    changed = True
                    break
        if not changed:
            break

    for s in parsed:
        if id(s) in lit:
            continue
        # Say WHY: the nearest thing that does eventually reach the origin.
        late = []
        for t in parsed:
            if t is not s and on_segment(s["origin"], t["seg"]):
                late.append((t["a"] + distance(t["origin"], s["origin"]) * rate,
                             t["d"]))
        late.sort()
        if not late:
            why = "no stroke in the drawing ever reaches that point"
        elif late[0][0] <= s["a"]:
            # Something does reach it in time, and is itself unfounded: a pair
            # that founds only each other is founded by nothing.
            why = (f"the only ink to reach it in time is `{late[0][1]}`, which "
                   f"is unfounded itself — a pair that founds only each other "
                   f"is not reachable from the source")
        else:
            why = (f"the earliest ink to reach it is `{late[0][1]}` at entry "
                   f"{float(late[0][0]):g}, {float(late[0][0] - s['a']):g} "
                   f"points too late")
        findings.append(
            f"{page.name} .{pass_class}: `{s['d']}` begins at entry {s['a']} at "
            f"({s['origin'][0]}, {s['origin'][1]}), where nothing has arrived — "
            f"{why}. A relay is one line handed on.")

    if verbose:
        print(f"  {page.name} .{pass_class}: source ({source['origin'][0]}, "
              f"{source['origin'][1]}) at entry {source['a']}")
        for s in sorted(parsed, key=lambda s: s["a"]):
            f = lit.get(id(s))
            state = (f"founded at entry {float(f):g}" if f is not None
                     else "UNFOUNDED")
            print(f"    {s['d']:<16} --a {float(s['a']):<5g} "
                  f"origin ({float(s['origin'][0]):>6g}, {float(s['origin'][1]):>5g})"
                  f"  ends {float(s['a'] + s['u'] * rate):<5g}  {state}")
    return findings


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print every stroke, its origin and what founds it")
    args = ap.parse_args()

    if not SHEET.exists():
        print(f"relay chain: cannot read {SHEET}")
        return 1
    m = re.search(re.escape(RATE_PROP) + r"\s*:\s*(-?\.?\d+\.?\d*)\s*[;}]",
                  SHEET.read_text(encoding="utf-8"))
    if not m:
        print(f"relay chain: {RATE_PROP} is not declared in {SHEET.name}. "
              "Arrival is distance times the relay's one rate; without it "
              "there is nothing to walk the ink with.")
        return 1
    rate = num(m.group(1))

    findings, checked = [], 0
    for page in PAGES:
        if not page.exists():
            findings.append(f"{page} is missing — this drawing ships in two "
                            "pages and both carry the same relay")
            continue
        text = page.read_text(encoding="utf-8")
        if "lp-frame" not in text:
            continue
        for pass_class in PASSES:
            findings += check_pass(page, pass_class, rate, args.verbose)
            checked += 1

    if not checked:
        print("relay chain: no .lp-frame in either page — the selector went stale")
        return 1
    if findings:
        print(f"\nrelay chain: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1
    print(f"relay chain OK — {checked} pass(es) across {len(PAGES)} page(s), "
          f"every stroke handed the line at a point the relay had already "
          f"reached, at rate {float(rate):g}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
