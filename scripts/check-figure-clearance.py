#!/usr/bin/env python3
"""The object hanging off the page rule clears the bar above it.

THE FINDING THIS EXISTS FOR. Measured in Chromium at 1440 x 900 on the render
before this file was written, the Uber uns page header's isometric object — the
demon core, .cf-page-header__figure — had its box start at y 63.9 while the nav
bar's box ended at 89.95. Twenty-six pixels of the drawing, the crown of the
inner shell and of the wide one behind it, sat UNDER the glass sheet: blurred by
--glass-blur and cut across by the lit rim .cf-nav::after paints along the bar's
bottom edge. The one thing the drawing is composed around is that it reaches as
far above its axis as below it, and a quarter of the upper reach veiled is the
one way to break that read.

Nothing in the repository could say so, and the stylesheet said the opposite. Of
the two directions the figure reaches, components.css reserved room for one:

    padding-bottom: calc(var(--cf-figure-reach) - ... + var(--space-16));

and where the top should have been there was a sentence — "Upward the object is
free to overflow: it passes behind a transparent nav bar, clear of both pills,
which is what the mockup does too." The nav bar has not been transparent since
it became glass, and the mockup does not do this either: on ueber-uns.jpg the
nav plates run y 16..49 inside equal air, so the bar's box ends at 65, and the
drawing's topmost mark is at y 75. Ten pixels of clearance at a 1200 frame.

A prose claim about a neighbour is exactly the kind of thing that goes stale
without anything rendering wrong on the page that made the claim. The bar grew;
the header never re-read it.

WHAT IS CHECKED. The header's vertical arithmetic above the rule, at every
integer viewport width from the figure's own gate to 2560, resolved out of the
sheets rather than assumed:

    clearance = padding-top + title + rule gap + half the rule - reach

  padding-top   .cf-page-header:has(.cf-page-header__figure), or the
                padding-block it inherits from .cf-page-header
  title         .cf-page-header__title's font-size x its unitless line-height,
                one line — see WHAT THIS CANNOT SEE
  rule gap      .cf-page-header__rule's margin-top
  half the rule the figure is centred on the rule's CENTRE, `top: 50%` of a box
                --stroke-1 high, so half a stroke of the reach is paid by the
                rule itself
  reach         half the figure's rendered height: its width as a fraction of
                the content column, times the viewBox's own aspect ratio, read
                out of the SVG in patterns/ueber-uns.html

and the requirement is `clearance >= --space-3`, the mockup's ten-at-1200
rounded onto the scale, which is twelve at 1440.

THE REACH IS DERIVED, NOT READ. --cf-figure-reach ships as the literal 0.1672,
and this check recomputes that coefficient from the figure's width percentage
and the viewBox in the markup and holds the two to each other. A taller viewBox
or a wider figure therefore fires here even though the coefficient in the CSS
still resolves to a perfectly good number — which is the failure the 0.1672
would otherwise wait for someone to notice.

The figure's placement identity is checked too: `top: 50%` and a -50%
translate on .cf-page-header__figure inside .cf-page-header__rule. Every line of
the arithmetic above assumes the axis is the rule; if the figure is ever
positioned off something else, this check is measuring nothing and says so
rather than passing.

BOTH SCROLLBAR WORLDS. The reach is a percentage of the header's own box and
the gutter is 5.5vw, and those two disagree by the scrollbar: a classic
15 px bar leaves 100 % at 1425 while 100vw is still 1440. Both are real — a
trackpad Mac overlays its scrollbar, a Windows desktop does not — so the sweep
runs at 0 and at 15 and both have to hold.

WHAT THIS CANNOT SEE, stated so it is not mistaken for covered:

  * that the title is one line. It is, at every width the figure paints at —
    "Uber uns" is eight characters against a column of 800 px and up — but the
    check takes the line box on faith and a longer title would silently make
    every number here too small. The measured table below is the guard: it is
    reproduced from the same arithmetic, so a title that grew a line would
    break the reproduction before it broke the sweep.
  * the nav bar's height. It does not need it. The bar is `position: sticky`
    and in flow, so the header's top edge IS the bar's bottom edge at rest, and
    the clearance above is measured inside the header's own box. What the bar
    does on scroll — pass over the drawing — is the point of a sticky bar.
  * anything below the rule. That end was already paid for and is unchanged.

stdlib only, no build step, no dependency — the same contract as the checks
beside it.

    python3 scripts/check-figure-clearance.py       # check, exit 1 on a finding
    python3 scripts/check-figure-clearance.py -v    # print the sweep's floor
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system/assets/css"
TOKENS = CSS / "tokens.css"
COMPONENTS = CSS / "components.css"
PAGE = ROOT / "design-system/patterns/ueber-uns.html"

ROOT_FONT = 16.0            # base.css never re-roots the rem
CLEARANCE = "--space-3"     # the mockup's ten pixels at 1200, on the scale
SWEEP_TOP = 2560            # the widest frame the register admits
SCROLLBARS = (0.0, 15.0)    # overlay, and Chromium's classic bar

HEADER = ".cf-page-header"
FIGURE = ".cf-page-header__figure"
TITLE = ".cf-page-header__title"
RULE = ".cf-page-header__rule"
GATED = f"{HEADER}:has({FIGURE})"

# Chromium 1440 x 900 and its neighbours, measured on the render this check was
# written against, with a 15 px classic scrollbar. `top` is the figure's box
# top; `nav` is the bar's box bottom, which is the header's box top.
#   {viewport: (nav bottom, figure top)}
MEASURED = {
    901: (89.945, 144.156),
    1165: (89.945, 104.871),
    1280: (89.945, 102.437),
    1440: (89.945, 102.437),
    1920: (89.945, 102.445),
}
TOLERANCE = 0.10            # px; the browser rounds line boxes to 1/64


def fail(msg):
    print(f"FAIL  {msg}")
    return 1


def strip_comments(css):
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


# --------------------------------------------------------------------------
# Lengths. The same evaluator shape as check-rail-margin.py, and only the
# grammar these sheets actually use.
# --------------------------------------------------------------------------
def px(value, tokens, width, layout):
    v = value.strip()
    m = re.fullmatch(r"var\(\s*(--[\w-]+)\s*\)", v)
    if m:
        if m.group(1) not in tokens:
            raise ValueError(f"unknown token {m.group(1)}")
        return px(tokens[m.group(1)], tokens, width, layout)
    m = re.fullmatch(r"(clamp|max|min)\((.*)\)", v, flags=re.S)
    if m:
        fn, vals = m.group(1), [px(a, tokens, width, layout)
                                for a in split_args(m.group(2))]
        if fn == "clamp":
            return max(vals[0], min(vals[1], vals[2]))
        return (max if fn == "max" else min)(vals)
    m = re.fullmatch(r"calc\((.*)\)", v, flags=re.S)
    if m:
        return calc(m.group(1), tokens, width, layout)
    m = re.fullmatch(r"(-?[\d.]+)(rem|px|vw|%)?", v)
    if not m:
        if "(" in v or re.search(r" [-+*/] ", v):
            return calc(v, tokens, width, layout)
        raise ValueError(f"cannot resolve length {value!r}")
    n, unit = float(m.group(1)), (m.group(2) or "px")
    if unit == "rem":
        return n * ROOT_FONT
    if unit == "vw":
        return n * width / 100.0
    if unit == "%":
        # The header is full-bleed, so its own 100 % is the layout viewport —
        # which the scrollbar takes off and vw does not. That difference is the
        # reason `layout` is threaded through at all.
        return n * layout / 100.0
    return n


def split_args(s):
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    out.append(cur)
    return [a.strip() for a in out if a.strip()]


def calc(expr, tokens, width, layout):
    expr = expr.strip()
    for op in ("+", "-"):
        depth = 0
        for i in range(len(expr) - 1, 0, -1):
            ch = expr[i]
            if ch == ")":
                depth += 1
            elif ch == "(":
                depth -= 1
            elif ch == op and depth == 0 and expr[i - 1] == " ":
                sign = 1 if op == "+" else -1
                return (calc(expr[:i], tokens, width, layout)
                        + sign * calc(expr[i + 1:], tokens, width, layout))
    for op in ("*", "/"):
        depth = 0
        for i in range(len(expr) - 1, 0, -1):
            ch = expr[i]
            if ch == ")":
                depth += 1
            elif ch == "(":
                depth -= 1
            elif ch == op and depth == 0:
                a = calc(expr[:i], tokens, width, layout)
                b = calc(expr[i + 1:], tokens, width, layout)
                return a * b if op == "*" else a / b
    if expr.startswith("(") and expr.endswith(")"):
        return calc(expr[1:-1], tokens, width, layout)
    return px(expr, tokens, width, layout)


# --------------------------------------------------------------------------
# Rules. A brace walker, because the figure's gate is an @media and the
# declarations inside it shadow the resting ones.
# --------------------------------------------------------------------------
def rules(css):
    out, stack, i, buf = [], [], 0, ""
    while i < len(css):
        ch = css[i]
        if ch == "{":
            head, buf = buf.strip(), ""
            if head.startswith("@"):
                stack.append(head)
                out.append(None)
            else:
                depth, j = 1, i + 1
                while j < len(css) and depth:
                    if css[j] == "{":
                        depth += 1
                    elif css[j] == "}":
                        depth -= 1
                    j += 1
                out.append((tuple(stack), head, css[i + 1:j - 1]))
                i = j
                continue
        elif ch == "}":
            buf = ""
            for k in range(len(out) - 1, -1, -1):
                if out[k] is None:
                    del out[k]
                    if stack:
                        stack.pop()
                    break
            else:
                if stack:
                    stack.pop()
        else:
            buf += ch
        i += 1
    return [r for r in out if r]


FEATURE = re.compile(r"\(\s*(min|max)-width\s*:\s*([\d.]+)(rem|px)\s*\)")

# A prelude this check cannot evaluate, and must not silently treat as active.
#
# width_matches() reads exactly one media feature — the viewport width — and
# returned True for every prelude that did not name one. That is right for
# `@media screen`, which is the render this whole file is about, and wrong for
# every prelude that describes a DIFFERENT render: `@media print` is the sheet,
# `(forced-colors: active)` is Windows high contrast, `(prefers-reduced-motion)`
# is a preference. A declaration inside one of those was folded into the screen
# cascade as though it were unconditional.
#
# WHAT FOUND IT. Adding a forced-colours redraw of .cf-page-header__rule — the
# hairline is painted with `background`, which forced colours discards, so it
# is drawn again as a border there and its box goes `height: 0`. Nothing about
# the screen render moved by a hundredth of a pixel, and all five rows of the
# measured table failed by exactly 0.499 px: half a stroke, which is the half
# of the rule's own height the figure is centred on. The check was reading a
# high-contrast declaration as the screen's.
#
# So the rule is stated the way the rest of this directory states one: a
# prelude naming a render this check does not model is not matched, rather
# than assumed. Width preludes are unchanged, `screen and (min-width: …)`
# included — `screen` IS the render being read.
OTHER_RENDER = re.compile(r"\bprint\b|forced-colors|prefers-")


def width_matches(prelude, width):
    if OTHER_RENDER.search(prelude):
        return False
    for kind, num, unit in FEATURE.findall(prelude):
        edge = float(num) * (ROOT_FONT if unit == "rem" else 1)
        if kind == "min" and width < edge:
            return False
        if kind == "max" and width > edge:
            return False
    return True


def split_semis(s):
    parts, depth, cur = [], 0, ""
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == ";" and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return [p.strip() for p in parts if p.strip()]


def declarations(body):
    out = {}
    for d in split_semis(body):
        if ":" in d:
            name, value = d.split(":", 1)
            out[name.strip()] = value.strip()
    return out


def resolve(rs, width, selectors):
    """Every declaration a selector in `selectors` carries at `width`.

    Source order only. The rules this reads are all single compounds at the
    same specificity or in specificity order down the file, which is the state
    the sheet is in and which the caller's own selector list asserts.
    """
    out = {}
    for stack, head, body in rs:
        if not all(width_matches(p, width) for p in stack):
            continue
        if not any(s.strip() in selectors for s in head.split(",")):
            continue
        out.update(declarations(body))
    return out


def selector_present(rs, selector):
    return any(selector in [s.strip() for s in head.split(",")]
               for _, head, _ in rs)


# --------------------------------------------------------------------------
# The drawing's own box.
# --------------------------------------------------------------------------
def view_box():
    markup = PAGE.read_text(encoding="utf-8")
    m = re.search(r'<svg[^>]*class="[^"]*cf-page-header__figure[^"]*"[^>]*>', markup)
    if not m:
        return None, "patterns/ueber-uns.html carries no .cf-page-header__figure svg"
    vb = re.search(r'viewBox="([-\d.\s]+)"', m.group(0))
    if not vb:
        return None, "the figure svg carries no viewBox"
    nums = [float(n) for n in vb.group(1).split()]
    if len(nums) != 4:
        return None, f"viewBox is not four numbers: {vb.group(1)!r}"
    return (nums[2], nums[3]), None


def gate(rs):
    """The widest viewport at which the figure is switched off."""
    for stack, head, body in rs:
        if FIGURE not in head or declarations(body).get("display") != "none":
            continue
        for prelude in stack:
            for kind, num, unit in FEATURE.findall(prelude):
                if kind == "max":
                    return float(num) * (ROOT_FONT if unit == "rem" else 1)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    tokens_css = strip_comments(TOKENS.read_text(encoding="utf-8"))
    tokens = {}
    for _, head, body in rules(tokens_css):
        if ":root" in head:
            tokens.update({k: v for k, v in declarations(body).items()
                           if k.startswith("--")})

    rs = rules(strip_comments(COMPONENTS.read_text(encoding="utf-8")))
    findings = []

    box, err = view_box()
    if err:
        return fail(err)
    vb_w, vb_h = box

    off = gate(rs)
    if off is None:
        return fail(f"nothing switches {FIGURE} off; the sweep has no floor")

    # The placement identity. Every number below is measured from the rule, so
    # the figure has to be hung on the rule and centred on it.
    fig = resolve(rs, off + 1, {FIGURE, f"{HEADER} {FIGURE}"})
    if fig.get("top") != "50%":
        findings.append(f"{FIGURE} is not `top: 50%` of the rule "
                        f"(top: {fig.get('top')!r}); its axis is not the page line")
    if not re.fullmatch(r"0 -50%", fig.get("translate", "")):
        findings.append(f"{FIGURE} is not pulled back by half its own height "
                        f"(translate: {fig.get('translate')!r})")
    if not selector_present(rs, RULE):
        findings.append(f"{RULE} carries no rule of its own")
    width_pct = fig.get("width", "")
    m = re.fullmatch(r"([\d.]+)%", width_pct)
    if not m:
        return fail(f"{FIGURE}'s width is {width_pct!r}, not a percentage of "
                    f"the column this check can read")
    fig_pct = float(m.group(1)) / 100.0

    # The reach coefficient, derived from the drawing and held against the one
    # the sheet ships.
    derived = fig_pct * (vb_h / vb_w) / 2.0
    reach_decl = resolve(rs, off + 1, {GATED}).get("--cf-figure-reach", "")
    m = re.search(r"([\d.]+)\s*\*", reach_decl)
    if not m:
        return fail(f"--cf-figure-reach is {reach_decl!r}; no coefficient to read")
    shipped = float(m.group(1))
    if abs(shipped - derived) > 5e-5:
        findings.append(
            f"--cf-figure-reach ships {shipped:.5f}; the drawing's own box "
            f"({fig_pct:.5%} of the column, viewBox {vb_w:g} x {vb_h:g}) makes it "
            f"{derived:.5f}. The reserved room no longer matches the figure.")

    def clearance(w, sb):
        """The figure's box top, below the header's own top edge, at width w."""
        layout = w - sb
        head = resolve(rs, w, {HEADER, GATED})
        title = resolve(rs, w, {TITLE})
        rule = resolve(rs, w, {RULE})
        # --cf-figure-reach is declared on the header, not in :root, and every
        # percentage in it resolves against the header's own box — which is the
        # layout viewport, the header being full-bleed.
        scope = dict(tokens, **{k: v for k, v in head.items()
                                if k.startswith("--")})
        pad = head.get("padding-top") or head["padding-block"].split()[0]
        lh = title["line-height"]
        m = re.fullmatch(r"var\(\s*(--[\w-]+)\s*\)", lh)
        lh = float(scope[m.group(1)] if m else lh)
        return (px(pad, scope, w, layout)
                + px(title["font-size"], scope, w, layout) * lh
                + px(rule["margin-top"], scope, w, layout)
                + px(rule["height"], scope, w, layout) / 2.0
                - px("var(--cf-figure-reach)", scope, w, layout))

    floor = px(tokens[CLEARANCE], tokens, 1440.0, 1440.0)
    worst = min(((clearance(w, sb), w, sb)
                 for sb in SCROLLBARS
                 for w in range(int(off) + 1, SWEEP_TOP + 1)),
                key=lambda t: t[0])

    if worst[0] < floor - 1e-6:
        clear, w, sb = worst
        under = (f" {-clear:.2f} px of the drawing is under the glass."
                 if clear < 0 else "")
        findings.append(
            f"the figure clears the bar above it by {clear:.2f} px at a {w} px "
            f"viewport (scrollbar {sb:g}); {CLEARANCE} is {floor:g}.{under}")

    # The measured table, reproduced. It is what keeps the arithmetic above
    # honest about the browser — a title that grew a line, a rule that stopped
    # being one stroke, an @media that shadowed the padding.
    for w, (nav_bottom, fig_top) in sorted(MEASURED.items()):
        predicted = nav_bottom + clearance(w, 15.0)
        if abs(predicted - fig_top) > TOLERANCE:
            findings.append(
                f"the arithmetic does not reproduce the browser at {w} px: "
                f"figure top predicted {predicted:.3f}, measured {fig_top:.3f}. "
                f"Either the sheet moved under the table or the header no longer "
                f"stacks the way this check reads it.")

    if findings:
        print(f"figure clearance: {len(findings)} finding(s)\n")
        for f in findings:
            print(f"  - {f}")
        return 1

    clear, w, sb = worst
    print(f"figure clearance: floor {clear:.2f} px at {w:g} (scrollbar {sb:g}), "
          f"{CLEARANCE} is {floor:g}; reach {shipped:.5f} matches the "
          f"{vb_w:g} x {vb_h:g} viewBox; {len(MEASURED)} measured widths reproduced.")
    if args.verbose:
        for w in sorted(MEASURED):
            print(f"  {w:>5} px  measured figure top {MEASURED[w][1]:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
