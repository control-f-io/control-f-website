#!/usr/bin/env python3
"""A scrubbed part may not outrun the reader's hand.

Every animation on the landing page is driven by scroll position rather than by
a clock, and foundations/motion.html states what that buys: "the isometric
assembly is driven by scroll range, not by a duration ... how long it takes
depends entirely on how fast you scroll." The reader's hand IS the transport.
So there is a quantity nothing on this page had ever been held to — how far a
part moves for each pixel the page moves — and one animation was thirteen times
over everything else on the page.

WHAT WENT WRONG, AND WHY NOTHING CAUGHT IT. `.cf-statement .cf-iso__ghost` runs
two animations: the assembly's fade on entry and cf-stmt-scatter on exit. Every
list on that rule is restated in full, because animation-name is a replacement
and not an addition — except animation-timing-function, which was not restated,
so the scatter inherited the --ease-out the isometric family sets for all of its
parts. Right for a fade. Wrong for a 439-unit translate in a 168-unit window.

THE ARITHMETIC IS A PURE NUMBER, WHICH IS WHY THIS IS A SCRIPT AND NOT A
MEASUREMENT. Both quantities are in the drawing's own units:

  travel   hypot(--sx, --sy), off the markup, in viewBox units
  window   the range's span as a fraction of `exit`, and the `exit` phase spans
           the subject's OWN HEIGHT — which for this figure is the viewBox's
           height in both of its layouts. Side by side it is `aspect-ratio:
           1200 / 420` and the box meets the viewBox exactly; stacked it is
           5 / 3 with `slice`, and slice scales to cover, so the tighter axis
           is the vertical one and the box is again exactly 420 units tall.

The render scale therefore cancels and the ratio is the same at every viewport.
Then the timing function multiplies it: an eased curve's steepest slope is the
factor by which the rendered state outruns the linear range position, and for
--ease-out — cubic-bezier(0, 0, .2, 1) — that factor is exactly 5, at t = 0,
where a scatter starts. 439.52 / (0.40 x 420) = 2.62, times 5 is 13.08.

Confirmed in Chromium at 1440 x 900, sampling the computed `translate` every
20 px of scroll: 5.8 units of travel per pixel of scroll on that part, which is
under 13.08 only because a 20 px step averages across the start where the curve
is steepest. The same part is 83 % of the way gone by the middle of its own
window. Everything else on the page peaks at 1.14 CSS px per px — card 01's
tallest build part, 155 units over 374 px of the pinned track at 0.55 render
scale.

THE CEILING IS 3, and it is a decision rather than a measurement. A scatter is
the one thing on this page that is allowed to move faster than the hand at all;
at 3 to 1 a 100 px wheel notch throws a part a third of a screen, which is the
edge of reading as a scrub rather than as a cut. Everything the page ships now
sits at or under 2.62 and everything that is not the scatter is under 1.2.

WHAT IS HELD AND WHAT IS NOT. Held: every part that carries an exit vector, in
both files that ship this drawing — the landing page and components/statement
.html, which is the specimen and drifted from the page once already. Not held:
the `cover` and `contain` families, whose phase spans are `vh + h` and
`pinH - vh` and therefore depend on the viewport, so their rate is not a pure
number and a static script cannot state it. They were measured instead, in the
run that wrote this, and the highest of them is the 1.14 above.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-scrub-rate.py
"""

import argparse
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
COMPONENTS = DS / "assets/css/components.css"
TOKENS = DS / "assets/css/tokens.css"

# The rule, the animation on it that moves parts, and the two markup custom
# properties that say how far. Named rather than sniffed: this check is about
# one authored exit, and a rule that renames itself should fail loudly.
SELECTOR = ".cf-statement .cf-iso__ghost"
MOVER = "cf-stmt-scatter"
VECTOR = ("--sx", "--sy")

# Every file that ships the drawing. The specimen is here on purpose — the
# component's own page carried a stale --iso-travel for as long as the value
# lived in one page's stylesheet, and that is the failure this list prevents.
CARRIERS = [
    DS / "patterns/landing-page.html",
    DS / "components/statement.html",
]

CEILING = 3.0


# --------------------------------------------------------------- easing ----

def peak_slope(x1, y1, x2, y2):
    """The steepest dy/dx a cubic-bezier timing function reaches.

    Sampled on the curve's own parameter rather than on t, so no root-finding
    is involved and the s -> 0 limit is approached rather than divided by.
    """
    def dx(s):
        return x1 * (3 - 12 * s + 9 * s * s) + x2 * (6 * s - 9 * s * s) + 3 * s * s

    def dy(s):
        return y1 * (3 - 12 * s + 9 * s * s) + y2 * (6 * s - 9 * s * s) + 3 * s * s

    best = 0.0
    steps = 200000
    for i in range(1, steps):
        s = i / steps
        d = dx(s)
        if d <= 1e-12:
            continue
        best = max(best, dy(s) / d)
    return best


def resolve_timing(value, findings):
    """A timing-function keyword or var(--token), as a peak slope."""
    value = value.strip()
    if value == "linear":
        return 1.0, "linear"
    m = re.fullmatch(r"var\(\s*(--[\w-]+)\s*\)", value)
    if m:
        token = m.group(1)
        text = TOKENS.read_text(encoding="utf-8")
        t = re.search(rf"{re.escape(token)}:\s*cubic-bezier\(([^)]*)\)", text)
        if not t:
            findings.append(f"{token} is not a cubic-bezier in tokens.css")
            return None, value
        try:
            a, b, c, d = (float(v) for v in t.group(1).split(","))
        except ValueError:
            findings.append(f"{token}'s cubic-bezier is not four numbers")
            return None, value
        return peak_slope(a, b, c, d), f"{value} = cubic-bezier({t.group(1).strip()})"
    m = re.fullmatch(r"cubic-bezier\(([^)]*)\)", value)
    if m:
        a, b, c, d = (float(v) for v in m.group(1).split(","))
        return peak_slope(a, b, c, d), value
    findings.append(
        f"`{value}` is a timing function this check cannot resolve — it holds "
        f"linear, cubic-bezier() and var(--token) and nothing else"
    )
    return None, value


# ------------------------------------------------------------------ CSS ----

def rule_body(text, selector):
    """The declaration block of the LAST rule with this exact selector."""
    body = None
    for m in re.finditer(re.escape(selector) + r"\s*\{([^}]*)\}", text):
        body = m.group(1)
    return body


def split_list(decl):
    """Comma-separated animation list, ignoring commas inside brackets."""
    out, depth, cur = [], 0, ""
    for ch in decl:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


def declaration(body, prop):
    m = re.search(rf"(?<![-\w]){re.escape(prop)}:([^;]*);", body)
    return m.group(1) if m else None


# --------------------------------------------------------------- markup ----

VIEWBOX = re.compile(r'<svg[^>]*class="[^"]*\bcf-iso\b[^"]*"[^>]*viewBox="([^"]*)"')


def viewbox_height(html, findings, path):
    m = VIEWBOX.search(html)
    if not m:
        findings.append(f"{path.name}: no <svg class=\"cf-iso\"> with a viewBox")
        return None
    parts = m.group(1).split()
    if len(parts) != 4:
        findings.append(f"{path.name}: the figure's viewBox is not four numbers")
        return None
    return float(parts[3])


def exit_vectors(html):
    """Every part that carries an exit vector, as (sx, sy, scat_in)."""
    out = []
    for style in re.findall(r'style="([^"]*)"', html):
        if VECTOR[0] not in style:
            continue
        sx = re.search(rf"{VECTOR[0]}:\s*(-?[\d.]+)", style)
        sy = re.search(rf"{VECTOR[1]}:\s*(-?[\d.]+)", style)
        if not (sx and sy):
            continue
        lead = re.search(r"--scat-in:\s*([\d.]+)%", style)
        out.append((float(sx.group(1)), float(sy.group(1)),
                    float(lead.group(1)) if lead else None))
    return out


# ---------------------------------------------------------------- check ----

EXIT_SPAN = re.compile(
    r"exit\s+var\(\s*--scat-in\s*,\s*[\d.]+%\s*\)\s+"
    r"exit\s+calc\(\s*var\(\s*--scat-in\s*,\s*[\d.]+%\s*\)\s*\+\s*([\d.]+)%\s*\)"
)


def main():
    ap = argparse.ArgumentParser(
        description="A scrubbed part may not outrun the reader's hand.")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    findings = []
    css = COMPONENTS.read_text(encoding="utf-8")

    body = rule_body(css, SELECTOR)
    if body is None:
        print(f"scrub rate: no rule for `{SELECTOR}` — the selector went stale",
              file=sys.stderr)
        return 1

    names = split_list(declaration(body, "animation-name") or "")
    if MOVER not in names:
        print(f"scrub rate: `{SELECTOR}` no longer runs {MOVER}", file=sys.stderr)
        return 1
    slot = names.index(MOVER)

    # The keyframes have to be the ones this check's arithmetic is about: a
    # translate written off the markup's own vector. If the mechanism moves,
    # the numbers below stop meaning what they say.
    kf = re.search(rf"@keyframes\s+{MOVER}\s*\{{(.*?)\n\}}", css, re.S)
    if not kf or VECTOR[0] not in kf.group(1):
        findings.append(
            f"@keyframes {MOVER} no longer translates by {VECTOR[0]}/{VECTOR[1]} — "
            f"this check's travel term is read off the markup and would be measuring "
            f"nothing"
        )

    ranges = split_list(declaration(body, "animation-range") or "")
    if len(ranges) <= slot:
        findings.append(
            f"`{SELECTOR}`: animation-range has {len(ranges)} entries for "
            f"{len(names)} animations — a short list cycles, so {MOVER} is running "
            f"a window written for something else"
        )
        span = None
    else:
        m = EXIT_SPAN.search(ranges[slot])
        if not m:
            findings.append(
                f"`{SELECTOR}`: {MOVER}'s range is `{ranges[slot].strip()}` — this "
                f"check holds the `exit` form, where the phase spans the subject's "
                f"own height and the rate is a pure number. A `cover` or `contain` "
                f"window would have to be measured at a stated viewport instead"
            )
            span = None
        else:
            span = float(m.group(1)) / 100.0

    tfs = split_list(declaration(body, "animation-timing-function") or "")
    if not tfs:
        # Inherited from the family block above, which is the failure itself.
        findings.append(
            f"`{SELECTOR}` does not restate animation-timing-function, so {MOVER} "
            f"takes whichever curve the isometric family sets for its fades — the "
            f"exact omission that put this exit at 13 px of travel per px of scroll"
        )
        slope, shown = None, "(inherited)"
    else:
        if len(tfs) <= slot:
            findings.append(
                f"`{SELECTOR}`: animation-timing-function has {len(tfs)} entries for "
                f"{len(names)} animations — the list cycles, so {MOVER} is running "
                f"the curve authored for {names[slot % len(tfs)]}"
            )
        slope, shown = resolve_timing(tfs[slot % len(tfs)], findings)

    rates = []
    if span and slope is not None:
        for path in CARRIERS:
            if not path.exists():
                findings.append(f"{path} is in the carrier list and is not there")
                continue
            html = path.read_text(encoding="utf-8")
            vb = viewbox_height(html, findings, path)
            if vb is None:
                continue
            parts = exit_vectors(html)
            if not parts:
                findings.append(f"{path.name}: no part carries {VECTOR[0]}/{VECTOR[1]}")
                continue
            window = span * vb
            for sx, sy, lead in parts:
                travel = math.hypot(sx, sy)
                rates.append((travel / window * slope, travel, window, lead, path.name))

    if args.verbose:
        print(f"scrub rate — travel per pixel of scroll, at the curve's steepest:")
        print(f"  {SELECTOR} · {MOVER}")
        print(f"    timing  {shown}"
              + (f", peak dy/dx {slope:.3f}" if slope is not None else ""))
        if span:
            print(f"    window  {span * 100:g} % of `exit`")
        for r, travel, window, lead, name in sorted(rates, reverse=True):
            lead_s = f"scat-in {lead:g} %" if lead is not None else "no lead"
            print(f"    {r:6.2f} px/px   travel {travel:7.2f}  window {window:6.1f}"
                  f"   {lead_s:14} {name}")

    for r, travel, window, lead, name in rates:
        if r > CEILING:
            findings.append(
                f"{name}: a part travels {travel:.2f} units in a {window:.0f}-unit "
                f"window under a curve whose steepest slope is {slope:.2f}, so it "
                f"moves {r:.2f} px for every px the reader scrolls, over the "
                f"{CEILING:g} ceiling — lengthen the window or take the ease off "
                f"the exit (foundations/motion.html#scrub)"
            )

    if findings:
        for f in findings:
            print(f"scrub rate: {f}", file=sys.stderr)
        return 1

    worst = max((r for r, *_ in rates), default=0.0)
    print(f"scrub rate OK — {len(rates)} exit vectors across {len(CARRIERS)} files, "
          f"none over {CEILING:g} px of travel per px of scroll; worst is {worst:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
