#!/usr/bin/env python3
"""The page margin is one number, so a band that re-derives it must use that one.

Almost every section on this site gets its content box from .container, and
base.css states the arithmetic once:

    width: 100%;
    max-width: calc(var(--container-max) + var(--gutter) * 2);
    padding-inline: var(--gutter);

whose content box is exactly `min(100% - 2 * --gutter, --container-max)`.

A FEW BANDS CANNOT USE IT. The acts are full-bleed tracks with sticky stages of
their own — .sp4-set and .map-stage sit outside any .container, because the
thing that has to reach the viewport edge is the drawing behind them and the
thing that has to sit on the page's margin is the copy in front. Those bands
re-derive the content box in place, by writing the same min() out longhand. That
is legitimate and the system does it deliberately.

WHAT IS NOT LEGITIMATE IS WRITING A DIFFERENT NUMBER IN IT, and the failure is
one no ladder sweep and no breakpoint sweep can name, because it has no
threshold in it at all. --gutter is `clamp(1.25rem, 5.5vw, 5rem)`: it ramps with
the viewport from 364 px to 1454 px and pins flat either side. A fixed space
rung is a horizontal line across that ramp, and a line crosses a ramp at exactly
one point. Both bands were `min(100% - 2 * var(--space-6), …)`, and 5.5vw is
24 px at 436 px of viewport — so on the landing page act 4's plates, act 5's
world map, its legend and its three beats of prose stood on the page's own
margin at ONE width and left of it at every other:

    viewport   page margin   band inset   the band stood
     320        20.0          24           4.0 px inside the page
     436        24.0          24           0      — the one width it agreed
     768        42.2          24          18.2 px outside
     834        45.9          24          21.9 px outside
    1024        56.3          24          32.3 px outside
    1328        73.0          24          49.0 px outside  <- worst
    1440        80.0          80           0      — both pinned at the cap

Measured as the left edge of .map__legend against the left edge of the FAQ and
partner headings two sections down the same page. Nothing overflowed, nothing
errored, every registered threshold was kept, and the page's left edge stepped
sideways by up to 49 px between act 3 and act 4 and back again at act 6 — an
amount that changed continuously as the window was dragged, which is why every
fixed-width screenshot in this repository shows it and none of them names it.

It is the shape a page-local re-derivation of a shared measurement always takes.
These rules were authored in prototypes/statement-to-process.html, a lab page
with no .container anywhere in it, where a self-contained inset is the only
thing that CAN be written and 24 px looks like any other choice. They were
ported to patterns/landing-page.html, which has .container on every other
section, and the substitute and the real thing agreed at one width in eleven
hundred.

WHAT THIS CHECKS. Every declaration in the shipping stylesheets whose value
re-derives a content box — `min(100% - 2 * <inset>, …)`, the .container idiom
written longhand — must take its inset from `var(--gutter)`. A rung of the space
scale, a bare length, or any other token is a finding, named with the viewport
at which it agrees with the ramp and the worst disagreement across the range.

ONE SANCTIONED EXCEPTION, and it is registered below by selector rather than
waved through by pattern: .sp4-set inside the pin gate. There the band is not
flowing copy on a page margin at all — it is a composition centred in a 100vh
stage, capped at `66vh * 1.875` so the taller of its two plates fits the stage,
and the cap is what decides its width above 1200 px. It is `margin-inline: auto`
into empty stage, so it has no page margin to miss. The exception carries the
reason with it, and the check requires the reason's own term (the vh cap) still
to be in the declaration — an exception that stops being that composition stops
being exempt.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-band-inset.py       # check, exit 1 on a finding
    python3 scripts/check-band-inset.py -v    # list every band, not only failures
"""

import argparse
import re
import sys
from pathlib import Path

CSS = Path(__file__).resolve().parent.parent / "design-system" / "assets" / "css"
SHIPPING = ["tokens.css", "base.css", "components.css", "acts.css"]

# The .container idiom written longhand: a content box derived by taking two
# insets off the full width. `100%` or `100vw`, any spacing around the operators.
BAND = re.compile(
    r"min\(\s*100(?:%|vw)\s*-\s*2\s*\*\s*([^,]+?)\s*,",
    re.IGNORECASE,
)

# The page margin, and the only inset a re-derived content box may use.
GUTTER = re.compile(r"^var\(\s*--gutter\s*[,)]", re.IGNORECASE)

# Selector -> the term that has to survive in the declaration for the exemption
# to hold. Keyed on the selector text as authored, so a rename re-opens the
# question rather than inheriting the answer.
EXEMPT = {
    ".sp4-set": (
        "vh",
        "the pinned act-4 composition: centred in a 100vh stage and capped at "
        "66vh * 1.875 so the taller plate fits, with no page margin to miss",
    ),
}

# --gutter's own definition, read rather than restated. clamp(min, ramp, max).
CLAMP = re.compile(
    r"--gutter:\s*clamp\(\s*([\d.]+)rem\s*,\s*([\d.]+)vw\s*,\s*([\d.]+)rem\s*\)",
    re.IGNORECASE,
)


def gutter_ramp(tokens_text):
    """The three numbers of --gutter, in px at a 16 px root, out of tokens.css."""
    m = CLAMP.search(tokens_text)
    if not m:
        raise SystemExit(
            "band inset: --gutter is not a clamp(rem, vw, rem) in tokens.css.\n"
            "  This check derives its arithmetic from that declaration rather\n"
            "  than restating it. Update the check with the new shape."
        )
    return float(m.group(1)) * 16, float(m.group(2)), float(m.group(3)) * 16


def agreement(inset_px, lo, vw_pct, hi):
    """Where a FIXED inset agrees with the ramp, and the worst it disagrees.

    Returns (viewport of agreement or None, worst gap in px, viewport of it).
    The ramp is lo below lo/vw_pct*100, vw_pct % of the viewport through the
    middle, hi above hi/vw_pct*100. A constant crosses that at one point.
    """
    ramp_lo = lo / vw_pct * 100          # viewport where the clamp leaves its floor
    ramp_hi = hi / vw_pct * 100          # viewport where it reaches its ceiling
    meet = None
    if lo <= inset_px <= hi:
        meet = round(inset_px / vw_pct * 100, 1)
    # Worst disagreement over the widths this system draws for: 320 to 1920.
    worst, at = 0.0, None
    for vw in range(320, 1921):
        g = min(max(lo, vw * vw_pct / 100), hi)
        d = abs(g - inset_px)
        if d > worst:
            worst, at = d, vw
    return meet, round(worst, 1), at


def blocks(text):
    """(line, selector, body) for every rule, nested preludes included."""
    out = []
    depth_stack = []
    i = 0
    line = 1
    start = 0
    while i < len(text):
        c = text[i]
        if c == "\n":
            line += 1
        elif c == "{":
            sel = text[start:i].strip().splitlines()
            sel = sel[-1].strip() if sel else ""
            depth_stack.append((line, sel, i + 1))
            start = i + 1
        elif c == "}":
            if depth_stack:
                ln, sel, body_start = depth_stack.pop()
                out.append((ln, sel, text[body_start:i]))
            start = i + 1
        i += 1
    return out


def declarations(body):
    """(prop, value) for the declarations directly in this body."""
    flat = re.sub(r"\{[^{}]*\}", "", body)
    for d in flat.split(";"):
        d = d.strip()
        if not d or d.startswith("/*") or ":" not in d:
            continue
        prop, _, value = d.partition(":")
        prop = prop.strip()
        value = " ".join(value.split())
        if prop.startswith("--") or not prop or "\n" in prop:
            continue
        yield prop, value


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every re-derived band, not only the failures")
    args = ap.parse_args()

    sheets = [(n, (CSS / n).read_text()) for n in SHIPPING]
    tokens = dict(sheets)["tokens.css"]
    lo, vw_pct, hi = gutter_ramp(tokens)

    # The space scale, read out of tokens.css, so a rung can be named in px.
    rungs = {m.group(1): float(m.group(2)) * 16
             for m in re.finditer(r"(--space-\d+):\s*([\d.]+)rem", tokens)}

    rows = []
    failures = []
    for name, text in sheets:
        for line, sel, body in blocks(text):
            for prop, value in declarations(body):
                m = BAND.search(value)
                if not m:
                    continue
                inset = m.group(1).strip()
                ok = bool(GUTTER.match(inset))
                key = sel.strip()
                exempt = EXEMPT.get(key)
                if exempt and exempt[0] in value:
                    rows.append((name, line, key, prop, inset, "exempt"))
                    continue
                rows.append((name, line, key, prop, inset,
                             "gutter" if ok else "FIXED"))
                if ok:
                    continue

                # Name the fault in the units the reader will measure it in.
                tok = re.fullmatch(r"var\(\s*(--space-\d+)\s*[,)].*", inset)
                px = rungs.get(tok.group(1)) if tok else None
                if px is None:
                    bare = re.fullmatch(r"([\d.]+)(rem|px)", inset)
                    if bare:
                        px = float(bare.group(1)) * (16 if bare.group(2) == "rem" else 1)
                where = ""
                if px is not None:
                    meet, worst, at = agreement(px, lo, vw_pct, hi)
                    where = (
                        "\n      %g px agrees with the ramp at %s and nowhere else;\n"
                        "      across 320-1920 the ramp stands up to %g px per side from it,\n"
                        "      at a %d px viewport. What the page shows is that gap or the\n"
                        "      part of it --container-max has not already capped away."
                        % (px,
                           ("a %g px viewport" % meet) if meet else "no viewport at all",
                           worst, at)
                    )
                failures.append(
                    "%s:%d  %s\n"
                    "      %s: … min(100%% - 2 * %s, …)\n"
                    "      A band that re-derives .container's content box has to take\n"
                    "      .container's inset. --gutter is clamp(%grem, %gvw, %grem) — a ramp —\n"
                    "      and this is a constant, so the two agree at one viewport at most.%s\n"
                    "      Write min(100%% - 2 * var(--gutter), var(--container-max)), or\n"
                    "      register the selector in EXEMPT with the reason it has no page\n"
                    "      margin to miss."
                    % (name, line, key, prop, inset,
                       lo / 16, vw_pct, hi / 16, where)
                )

    if args.verbose:
        print("re-derived content boxes, as read out of the shipping CSS:\n")
        for name, line, sel, prop, inset, verdict in rows:
            print("  %-16s %-5d %-24s %-28s %s"
                  % (name, line, sel[:24], inset[:28], verdict))
        print("\n--gutter: clamp(%grem, %gvw, %grem) = %g → %g px\n"
              % (lo / 16, vw_pct, hi / 16, lo, hi))
        for sel, (term, why) in EXEMPT.items():
            print("  exempt: %s — %s (holds while `%s` is in the declaration)"
                  % (sel, why, term))
        print()

    if failures:
        print("band inset: %d finding(s)\n" % len(failures))
        for f in failures:
            print("  - %s\n" % f)
        return 1

    print("band inset: %d re-derived content box(es), %d on --gutter, %d exempt."
          % (len(rows),
             sum(1 for r in rows if r[5] == "gutter"),
             sum(1 for r in rows if r[5] == "exempt")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
