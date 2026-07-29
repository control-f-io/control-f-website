#!/usr/bin/env python3
"""A relay is one line handed on, so every leg of it draws at one speed.

.lp-frame is six strokes that chain: the three verticals grow down from the
points the flow's drops land on, the top rail spreads outward from the middle
vertical, and the base closes the rectangle last. Each stroke names its start
in the markup as `--a`, in points of the pin section's `entry` phase, and each
grows by `scale: 0 -> 1` about the end `--o` names. The page's own note calls
this "consecutive strokes chain instead of running abreast", and `--o` exists
to make the chaining legible: a stroke leaves the junction its predecessor
landed on.

WHAT WENT WRONG. The window was a flat twelve points for all six:

    animation-range: entry calc(var(--a) * 1%) entry calc((var(--a) + 12) * 1%);

Five of the six strokes are 500 viewBox units long, so twelve points was right
five times. The sixth is the base rail, `M0 500H1000`, which is 1000 units. It
drew twice the line in the same scroll — exactly 2.00x, at every viewport,
because the ratio is a pure number and not a measurement: 12 points per 500
units against 12 per 1000. Confirmed in Chromium as the tip's own travel, the
quantity check-scrub-rate.py is written in: 5.94 CSS px per px of scroll on the
five, 11.85 on the base at 1440 x 900; 5.94 / 11.87 at 1280 x 800; 5.52 /
10.55 at the gate floor; 4.95 / 9.88 at 1920 x 1080.

Nothing caught it because nothing was looking. check-scrub-rate.py holds the
one part on this page that is ALLOWED to outrun the hand — the statement's
scatter — and says in as many words that it does not hold the `cover` and
`contain` families, because their phase spans depend on the viewport. `entry`
is the third family and it was not held either, and it is the one the frame
draws in.

WHAT IS CHECKED, and both halves matter.

  ONE RATE FOR THE WHOLE RELAY. Each stroke declares `--u`, its length in the
  drawing's own units, and the stylesheet buys the window as `--u` times a
  single constant declared on .lp-frame as `--relay-rate`. So uniformity is
  structural rather than arithmetical — there is one number and every window
  is derived from it — and this check holds the structure: the rule must read
  --u and --relay-rate and must not add any second per-stroke term, because a
  `+ 2` smuggled back into the calc is the flat 12 returning under another
  name.

  --u MUST BE TRUE. A length typed beside a path is a length that can disagree
  with the path, and this file has watched that happen twice already: the rim
  the root leaves from was recorded as 88 units against markup drawing it at
  84 (#189), and the node radii were a hand-typed ladder read off the picture
  rather than off the number the picture is built from (#191). So every `d` is
  parsed and its length recomputed, and a --u that disagrees with its own
  stroke fails.

THE RATE IS IN UNITS, NOT PIXELS, and the difference is real rather than
pedantic. The frame carries preserveAspectRatio="none", so where the plate is
not exactly 2:1 the two axes scale by different factors and a 500-unit vertical
renders 4.5 % longer than a 500-unit horizontal (477 px against 456 at the gate
floor). Uniform in units is what can be authored and what a static script can
hold; the residual anisotropy is a property of the box and belongs to whichever
lane owns the box.

WHAT THIS DOES NOT CLAIM. Not which stroke starts when — `--a` is the relay's
order and its clearances, a judgement about the drawing, held by eye and by the
notes. Not that a stroke's `--o` names the right end; check-grow-origin.py
holds that the value the markup states is the value the browser uses, and
check-flow-handover.py holds the geometry the frame is drawn into. This holds
only that no leg of the relay draws faster than any other, which was false on
one stroke in six for as long as the drawing has existed.

AND THE RELAY MAY NOT RUN PAST THE PIN. `entry 100 %` IS `contain 0 %` — the
moment the stage takes the scroll and the four-card build takes over — so a
window ending past 100 would leave the frame drawing underneath a card that is
already assembling inside it. The last stroke lands exactly on 100 now; this
holds that it cannot go further.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-relay-rate.py
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "design-system/prototypes/statement-to-process.html"

# ---------------------------------------------------------------- the page CSS
#
# A PAGE RESOLVES ITS LINKED STYLESHEETS AND ITS OWN <style>, IN THAT ORDER, and
# this check has to read what the page resolves rather than what it happens to
# declare inline. The five acts lived in one prototype's <style> block until they
# became assets/css/acts.css — two thousand lines cannot stay page-local once a
# second page wants them — and every check that read only the <style> went blind
# at that moment. Following the page's own <link> tags means the next stylesheet
# needs no edit here at all.
def page_stylesheets(path):
    html = path.read_text(encoding="utf-8")
    out = []
    for m in re.finditer(r'<link[^>]+href="([^"]*assets/css/[^"]+\.css)"', html):
        sheet = (path.parent / m.group(1)).resolve()
        if sheet.exists():
            out.append(sheet.read_text(encoding="utf-8"))
    out += re.findall(r"<style[^>]*>(.*?)</style>", html, re.S)
    return "\n".join(out)



LINE_CLASS = "lp-frame__line"
RULE_SELECTOR = ".lp-frame__line"
RATE_PROP = "--relay-rate"

# The relay lives entirely inside `entry`, whose last point is the pin's
# `contain 0` — see the module note.
ENTRY_CEILING = 100.0

# A stroke is authored to a tenth of a point; anything coarser than this is a
# typo rather than a rounding.
TOL = 1e-6


def read(path):
    try:
        return path.read_text(encoding="utf-8") + page_stylesheets(path)
    except OSError as exc:
        sys.exit(f"check-relay-rate: cannot read {path}: {exc}")


def strokes(text):
    """Every .lp-frame__line in the page, with its style vars and its `d`."""
    out = []
    for tag in re.findall(r"<path\b[^>]*>", text):
        if LINE_CLASS not in tag:
            continue
        style = re.search(r'style="([^"]*)"', tag)
        d = re.search(r'\bd="([^"]*)"', tag)
        if not style or not d:
            out.append((tag, None, None))
            continue
        vars_ = {}
        for decl in style.group(1).split(";"):
            if ":" not in decl:
                continue
            k, v = decl.split(":", 1)
            vars_[k.strip()] = v.strip()
        out.append((tag, vars_, d.group(1).strip()))
    return out


def path_length(d):
    """Length of an axis-aligned two-point path, in viewBox units.

    Deliberately narrow. Every stroke in this frame is `M x y` followed by one
    absolute H or V, and a shape this parser does not understand is exactly
    where the next bad --u would hide — so an unrecognised `d` is a failure and
    not a skip. The day the frame grows a diagonal, this is the line that says
    so out loud instead of quietly measuring it wrong.
    """
    m = re.fullmatch(
        r"M\s*(-?[\d.]+)[\s,]+(-?[\d.]+)\s*([HV])\s*(-?[\d.]+)",
        d.strip(),
    )
    if not m:
        return None
    x, y, axis, to = float(m.group(1)), float(m.group(2)), m.group(3), float(m.group(4))
    return abs(to - (x if axis == "H" else y))


def strip_css_comments(text):
    """`/* ... */` out, newlines kept so nothing runs together.

    The scan below reads a rule's selector as everything since the last `{`,
    `}` or `;`, and this file writes long notes between its rules — so a
    comment left in would be read as part of the next selector and the rule
    would simply not be found. That failure mode is worse than a miss: it
    reports "no rule" for a rule that is there.
    """
    return re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)


def rule_body(text, selector):
    """The declarations of the last rule whose selector list contains one.

    Scanned rather than matched with `([^{}]+)\\{([^{}]*)\\}`, which is the
    obvious regex for this and backtracks catastrophically: on a 200 KB page
    every `[^{}]+` that fails to reach a brace is retried at every length, and
    the check simply never returned. Two str.find walks are linear and say the
    same thing. A block whose body contains a `{` is a nested at-rule, not a
    style rule, and is skipped.
    """
    text = strip_css_comments(text)
    body = None
    i = text.find("{")
    while i != -1:
        start = max(text.rfind(c, 0, i) for c in ("{", "}", ";")) + 1
        end = text.find("}", i + 1)
        if end == -1:
            break
        inner = text[i + 1:end]
        if "{" not in inner:
            sels = [s.strip() for s in text[start:i].split(",")]
            if selector in sels:
                body = inner
        i = text.find("{", i + 1)
    return body


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    text = read(PAGE)
    failures = []
    notes = []

    # --- the rate constant -------------------------------------------------
    rate_decl = re.search(
        re.escape(RATE_PROP) + r"\s*:\s*(-?\.?\d+\.?\d*)\s*[;}]",
        strip_css_comments(text),
    )
    if not rate_decl:
        failures.append(
            f"{RATE_PROP} is not declared anywhere in {PAGE.name}. The relay's "
            "window has to come from one number the whole drawing shares; a "
            "per-stroke constant is the flat 12 returning."
        )
        rate = None
    else:
        rate = float(rate_decl.group(1))
        notes.append(f"{RATE_PROP} = {rate:g} points of entry per viewBox unit")

    # --- the rule derives the window from --u and the rate ------------------
    body = rule_body(text, RULE_SELECTOR)
    if body is None:
        failures.append(f"no `{RULE_SELECTOR}` rule found in {PAGE.name}")
    else:
        ranges = re.findall(r"animation-range\s*:([^;]*)", body)
        if not ranges:
            failures.append(f"`{RULE_SELECTOR}` declares no animation-range")
        else:
            decl = " ".join(ranges[-1].split())
            for want in ("var(--u)", f"var({RATE_PROP})", "var(--a)"):
                if want not in decl:
                    failures.append(
                        f"`{RULE_SELECTOR}`'s animation-range does not read "
                        f"{want}: {decl!r}. Every window is the stroke's own "
                        "length times the relay's one rate."
                    )
            # A second additive per-stroke term is how a flat window comes back.
            tail = decl.split("var(--u)", 1)[-1]
            stray = re.search(r"\+\s*(\d+\.?\d*)\b", tail)
            if stray:
                failures.append(
                    f"`{RULE_SELECTOR}`'s window adds a bare {stray.group(1)} "
                    "after the derived term. The window is --u x the rate and "
                    "nothing else, or the strokes stop sharing a speed."
                )
            if not args.quiet:
                notes.append(f"animation-range: {decl}")

    # --- every stroke: --u true, window uniform, relay inside entry ---------
    found = strokes(text)
    if not found:
        failures.append(f"no .{LINE_CLASS} paths found in {PAGE.name}")

    ends = []
    for tag, vars_, d in found:
        if vars_ is None or d is None:
            failures.append(f"a .{LINE_CLASS} has no style or no `d`: {tag}")
            continue
        if "--u" not in vars_ or "--a" not in vars_:
            failures.append(
                f"`{d}` declares {sorted(vars_)} — every stroke needs --a "
                "(where it starts) and --u (how long it is)."
            )
            continue
        declared = float(vars_["--u"])
        actual = path_length(d)
        if actual is None:
            failures.append(
                f"`{d}` is not an axis-aligned two-point path. This check "
                "measures M-then-H/V and nothing else on purpose: a shape it "
                "cannot read is where a wrong --u would hide."
            )
            continue
        if abs(declared - actual) > TOL:
            failures.append(
                f"`{d}` declares --u:{vars_['--u']} and measures {actual:g} "
                "units. A length typed beside a path has to be that path's."
            )
            continue
        if rate is not None:
            a = float(vars_["--a"])
            end = a + declared * rate
            ends.append((d, end))
            if not args.quiet:
                notes.append(
                    f"  {d:<16} --a {a:<5g} --u {declared:<6g} "
                    f"window {declared * rate:>5.1f} pts  "
                    f"entry {a:g} -> {end:g}"
                )

    for d, end in ends:
        if end > ENTRY_CEILING + TOL:
            failures.append(
                f"`{d}` ends at entry {end:g} %, past {ENTRY_CEILING:g}. "
                "entry 100 % is the pin's contain 0 — the frame would still be "
                "drawing under a card that is already building inside it."
            )

    if failures:
        print("check-relay-rate: FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1

    print(f"check-relay-rate: OK — {len(ends)} strokes, one rate")
    if not args.quiet:
        for n in notes:
            print(f"  {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
