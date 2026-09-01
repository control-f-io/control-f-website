#!/usr/bin/env python3
"""The fluid half of the responsive record is arithmetic, and arithmetic can be run.

The breakpoint register holds every width at which the system CHANGES SHAPE,
and check-breakpoints.py keeps its three copies honest. But the register
deliberately leaves out the other half of the responsive design: the seven
clamp() tokens that move CONTINUOUSLY with the viewport — four display sizes,
the gutter and the two section gaps. Those are documented too, and the record
is written FOUR times across two pages:

  foundations/mobile.html   "What changes continuously" — a table of each
                            token's floor, ramp, ceiling and the viewport
                            below which the floor binds, then a second table
                            of the five sizes computed at five viewports, and
                            a prose sentence listing the four type-floor
                            crossovers ("359, 360, 361, 367").
  foundations/layout.html   the token table, whose --gutter row restates the
                            clamp() literal and whose --section-gap row
                            restates the "64 → 160 px" span; the
                            vertical-rhythm table, which restates both section
                            gaps' floors and ceilings WITH the widths they
                            bind at; and the "stops growing at" table, which
                            states the ceiling crossover of four tokens to a
                            tenth of a pixel.

None of those copies was read by any check. That is the exact position the
overflow count on mobile.html was in while it went stale four separate times —
its own notes say so — and the fluid record is MORE exposed, not less, because
its numbers look like measurements and are actually derivations. "Floor binds
below 364" is not something somebody saw; it is 20 px = 5.5vw solved for the
viewport. Change the ramp to 5vw and the true answer moves to 400 while the
page keeps saying 364, every screenshot keeps rendering correctly, and the
record is wrong at forty consecutive viewport widths.

WHAT THIS KNOWS THAT A SCREENSHOT CANNOT. A stale derivation renders
perfectly, at every width, in both pages. But every number in all three copies
is computable from tokens.css alone: a clamp(floor, base + k·vw, ceiling)
crosses its floor at (floor − base) / k and its ceiling at (ceiling − base) / k,
and its value at any viewport is one substitution. So this file does not
compare strings against strings — it re-derives every figure from the live
declarations and fails on the first one the stylesheet no longer supports.

THE RULES, all recomputed from tokens.css with CSS comments stripped:

  CAP      a floor written as min(REM, Kvw) — a rem floor capped so it cannot
           outgrow the viewport it is subtracted from at a large text size —
           must be inert at 320 px, the narrowest viewport this record covers
           and the width WCAG 1.4.10 measures reflow at. Every floor figure on
           both pages is derived from the uncapped rem, so a cap that engaged
           above 320 would make all of them wrong below the width it engaged
           at, silently and at every viewport under it. --gutter is the one
           token that carries a cap today.
  TOKENS   the seven declarations parse as clamp() with a rem floor, a rem
           ceiling, and a ramp that is base + k·vw (base may be 0; the section
           gaps' 100vw / N form is k = 100/N; their var() floors and ceilings
           resolve through the --space-* scale).
  FLUID    mobile.html's fluid table: floor px, ramp text, ceiling px per row,
           and the bold "floor binds below" figure equal to the floor
           crossover rounded to the nearest integer.
  SIZES    mobile.html's computed table: all 25 cells within 0.008 px of the
           clamp evaluated at that row's viewport — the print precision is
           two decimals, so anything past half a hundredth is drift, not
           rounding.
  QUAD     the prose list of the four type crossovers equals the four type
           tokens' binds figures, sorted ascending.
  GUTTER   layout.html's --gutter row: the "20 → 80 px" span and the quoted
           clamp() literal, whitespace-insensitively identical to the live
           declaration.
  SPAN     layout.html's token-table --section-gap row: the "64 → 160 px"
           span carries the token's real floor and ceiling.
  RHYTHM   layout.html's vertical-rhythm table: each gap's "floor below F" and
           "ceiling from C" carry the token's real floor/ceiling in px and the
           real crossovers — these two are exact integers today (64·12 = 768),
           so they are held exactly.
  STOPS    layout.html's "stops growing at" table: each ceiling crossover to
           one decimal — 1438.2 for --container-max (the width where
           vw − 2 gutters reaches 1280), 1440.0, 1454.5, 1920.0.

WHAT A FAILURE MEANS. Two different things, and the fix is different:

  The stylesheet moved — a clamp was retuned. Then the record is stale by
  exactly the amount of the retune, and every failing number this prints is
  the new correct value: update all three copies in the same commit, including
  the computed-size table, which is why it is gated to 0.008 px rather than
  re-measured loosely.

  The record moved — somebody edited a documented number without touching the
  stylesheet. Do not "fix" the check; the stylesheet is the source and the
  page is the record, in that order, always.

Reintroduce the bug — retune 4.9vw to 5vw in tokens.css, or set mobile.html's
364 back to 363, or give layout.html's rhythm row a different ceiling width —
and this fails, naming the file, the line and both numbers.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKENS = ROOT / "design-system" / "assets" / "css" / "tokens.css"
MOBILE = ROOT / "design-system" / "foundations" / "mobile.html"
LAYOUT = ROOT / "design-system" / "foundations" / "layout.html"

# The narrowest viewport the fluid record documents, and the width WCAG 1.4.10
# measures reflow at. A cap on a clamp() floor has to be inert at and above it
# or every floor figure on both pages is a derivation the stylesheet no longer
# supports. See the CAP rule in main().
REFLOW_WIDTH = 320.0

failures = []


def fail(path, line, message):
    failures.append(f"{path.relative_to(ROOT)}:{line}  {message}")


def line_of(text, index):
    return text.count("\n", 0, index) + 1


def strip_css_comments(css):
    """Blank out /* ... */ so a declaration quoted in prose cannot match,
    without moving any line numbers."""
    return re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)), css, flags=re.S)


def rem_to_px(value):
    return float(value) * 16.0


class Fluid:
    """clamp(floor, base + k·vw, ceiling), everything in px; k in px per 100vw.

    floor_k is the vw coefficient of a CAP ON THE FLOOR — min(Nrem, Kvw) — or
    None where the floor is a plain rem. A capped floor exists so a rem floor
    cannot grow past the viewport it is subtracted from when the reader raises
    their text size; see --gutter in tokens.css. Every derivation below treats
    the floor as the plain rem figure, which is correct exactly while the cap
    is inert over the documented range — CAP, in the rules, is the check that
    it is.
    """

    def __init__(self, name, floor, base, k, ceiling, floor_k=None):
        self.name, self.floor, self.base, self.k, self.ceiling = name, floor, base, k, ceiling
        self.floor_k = floor_k

    def floor_at(self, vw):
        if self.floor_k is None:
            return self.floor
        return min(self.floor, self.floor_k * vw / 100.0)

    def floor_cap_crossover(self):
        """Viewport below which the cap, not the rem, is the floor."""
        return self.floor * 100.0 / self.floor_k

    def at(self, vw):
        return min(max(self.base + self.k * vw / 100.0, self.floor_at(vw)), self.ceiling)

    def floor_crossover(self):
        return (self.floor - self.base) * 100.0 / self.k

    def ceiling_crossover(self):
        return (self.ceiling - self.base) * 100.0 / self.k

    @property
    def binds_below(self):
        x = self.floor_crossover()
        return int(x + 0.5)


def parse_tokens():
    css = strip_css_comments(TOKENS.read_text(encoding="utf-8"))

    spaces = {}
    for m in re.finditer(r"--space-(\d+):\s*([\d.]+)rem", css):
        spaces[m.group(1)] = rem_to_px(m.group(2))

    tokens = {}

    # The four display sizes: clamp(REM, REM + Kvw, REM).
    for m in re.finditer(
        r"--(text-display-1|text-display-2|text-h1|text-h2):\s*"
        r"clamp\(\s*([\d.]+)rem\s*,\s*([\d.]+)rem\s*\+\s*([\d.]+)vw\s*,\s*([\d.]+)rem\s*\)",
        css,
    ):
        name = m.group(1)
        tokens[name] = Fluid(
            name, rem_to_px(m.group(2)), rem_to_px(m.group(3)), float(m.group(4)), rem_to_px(m.group(5))
        )

    # --gutter, with or without a cap on its floor: clamp(REM, Kvw, REM) or
    # clamp(min(REM, Cvw), Kvw, REM).
    m = re.search(
        r"--gutter:\s*clamp\(\s*(?:min\(\s*([\d.]+)rem\s*,\s*([\d.]+)vw\s*\)|([\d.]+)rem)"
        r"\s*,\s*([\d.]+)vw\s*,\s*([\d.]+)rem\s*\)",
        css,
    )
    if m:
        capped = m.group(1) is not None
        floor = rem_to_px(m.group(1) if capped else m.group(3))
        tokens["gutter"] = Fluid(
            "gutter", floor, 0.0, float(m.group(4)), rem_to_px(m.group(5)),
            floor_k=float(m.group(2)) if capped else None,
        )
        tokens["gutter"].literal = m.group(0).split(":", 1)[1].strip()

    for gap in ("section-gap", "section-gap-sm"):
        m = re.search(
            r"--" + gap + r":\s*clamp\(\s*var\(--space-(\d+)\)\s*,\s*"
            r"calc\(\s*100vw\s*/\s*(\d+)\s*\)\s*,\s*var\(--space-(\d+)\)\s*\)",
            css,
        )
        if m and m.group(1) in spaces and m.group(3) in spaces:
            tokens[gap] = Fluid(gap, spaces[m.group(1)], 0.0, 100.0 / int(m.group(2)), spaces[m.group(3)])
            tokens[gap].divisor = int(m.group(2))

    m = re.search(r"--container-max:\s*([\d.]+)(rem|px)", css)
    if m:
        tokens["container-max"] = rem_to_px(m.group(1)) if m.group(2) == "rem" else float(m.group(1))

    return tokens


def norm(text):
    return re.sub(r"\s+", "", text)


def cells(row_html):
    return [re.sub(r"<[^>]+>", "", c).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", row_html, re.S)]


def token_rows(html, token):
    """Every <tr> whose first cell is exactly <code>--token</code>, with lines.
    A token can be restated in more than one table of the same page — layout.html
    holds --section-gap in its token table AND its rhythm table — so the caller
    picks the copy it is checking by shape rather than trusting document order."""
    rows = []
    for m in re.finditer(r"<tr[^>]*>.*?</tr>", html, re.S):
        row = m.group(0)
        first = re.search(r"<td[^>]*>(.*?)</td>", row, re.S)
        if first and norm(re.sub(r"<[^>]+>", "", first.group(1))) == "--" + token:
            rows.append((row, line_of(html, m.start())))
    return rows


def token_row(html, token, path, where=None):
    for row, line in token_rows(html, token):
        if where is None or where(cells(row)):
            return row, line
    fail(path, 1, f"no table row for --{token}" + (" of the expected shape" if where else ""))
    return None, None


def main():
    tokens = parse_tokens()
    for needed in ("text-display-1", "text-display-2", "text-h1", "text-h2", "gutter", "section-gap", "section-gap-sm"):
        if needed not in tokens:
            fail(TOKENS, 1, f"--{needed} no longer parses as the clamp() shape this record documents")
    if failures:
        report()

    # CAP — a capped floor may not move any documented figure.
    #
    # Every derivation on both pages reads the floor as the plain rem value,
    # which is only correct while the cap is inert at the narrowest viewport
    # the record covers. REFLOW_WIDTH is that viewport and it is also what
    # WCAG 1.4.10 measures at, so a cap that engages above it would be both a
    # stale record and a narrower content column than the guideline assumes.
    # Raising the cap's coefficient is free; lowering it fails here with the
    # width at which the record stops being true.
    for name, tok in tokens.items():
        if getattr(tok, "floor_k", None) is None:
            continue
        engages = tok.floor_cap_crossover()
        if engages > REFLOW_WIDTH + 1e-9:
            fail(
                TOKENS, 1,
                f"--{name}: the cap on its floor engages at {engages:.1f} px, above the "
                f"{REFLOW_WIDTH:g} px reflow width. Every floor figure on mobile.html and "
                f"layout.html is derived from the uncapped {tok.floor:g} px and would be "
                f"wrong from {engages:.1f} px down. Raise the cap to at least "
                f"{tok.floor * 100.0 / REFLOW_WIDTH:g}vw, or re-derive both records.",
            )
    if failures:
        report()

    mobile = MOBILE.read_text(encoding="utf-8")
    layout = LAYOUT.read_text(encoding="utf-8")

    # FLUID — mobile.html's floor / ramp / ceiling / binds table.
    for name in ("gutter", "section-gap", "section-gap-sm", "text-display-1", "text-display-2", "text-h1", "text-h2"):
        tok = tokens[name]
        row, line = token_row(mobile, name, MOBILE)
        if row is None:
            continue
        c = cells(row)
        if len(c) != 5:
            fail(MOBILE, line, f"--{name}: expected 5 cells (token, floor, ramp, ceiling, binds), found {len(c)}")
            continue
        floor_px = float(re.sub(r"[^\d.]", "", c[1]))
        ceil_px = float(re.sub(r"[^\d.]", "", c[3]))
        binds = int(re.sub(r"[^\d]", "", c[4]))
        if abs(floor_px - tok.floor) > 0.004:
            fail(MOBILE, line, f"--{name}: floor documented {floor_px:g} px, tokens.css floors at {tok.floor:g} px")
        if abs(ceil_px - tok.ceiling) > 0.004:
            fail(MOBILE, line, f"--{name}: ceiling documented {ceil_px:g} px, tokens.css caps at {tok.ceiling:g} px")
        if binds != tok.binds_below:
            fail(
                MOBILE, line,
                f"--{name}: 'floor binds below' documented {binds}, the clamp crosses its floor at "
                f"{tok.floor_crossover():.2f} so the figure is {tok.binds_below}",
            )
        if name == "gutter":
            want_ramp = f"{tok.k:g}vw"
        elif hasattr(tok, "divisor"):
            want_ramp = f"100vw/{tok.divisor}"
        else:
            want_ramp = f"{tok.base / 16:g}rem+{tok.k:g}vw"
        if norm(c[2]) != want_ramp:
            fail(MOBILE, line, f"--{name}: ramp documented '{c[2]}', tokens.css ramp is '{want_ramp}'")

    # SIZES — the five-viewport computed table: viewport, d1, d2, h1, h2, gutter.
    order = ["text-display-1", "text-display-2", "text-h1", "text-h2", "gutter"]
    size_rows = 0
    for m in re.finditer(r"<tr[^>]*>.*?</tr>", mobile, re.S):
        c = cells(m.group(0))
        if len(c) == 6 and re.fullmatch(r"\d{3,4}", c[0]) and all(re.fullmatch(r"[\d.]+", x) for x in c[1:]):
            vw = int(c[0])
            size_rows += 1
            for name, printed in zip(order, c[1:]):
                exact = tokens[name].at(vw)
                if abs(float(printed) - exact) > 0.008:
                    fail(
                        MOBILE, line_of(mobile, m.start()),
                        f"--{name} at a {vw} viewport: documented {printed}, tokens.css computes {exact:.2f}",
                    )
    if size_rows < 5:
        fail(MOBILE, 1, f"the computed-size table holds {size_rows} viewport rows where the record promises 5")

    # QUAD — the prose list of the four type-floor crossovers, ascending.
    quad = ", ".join(str(n) for n in sorted(tokens[t].binds_below for t in order[:4]))
    if quad not in re.sub(r"<[^>]+>", "", mobile):
        fail(MOBILE, 1, f"the type-floor sentence no longer lists the four crossovers as '{quad}'")

    # GUTTER — layout.html's token table restates the literal and the span.
    row, line = token_row(layout, "gutter", LAYOUT)
    if row is not None:
        c = cells(row)
        span = re.search(r"([\d.]+)\s*→\s*([\d.]+)\s*px", c[1] if len(c) > 1 else "")
        tok = tokens["gutter"]
        if not span or abs(float(span.group(1)) - tok.floor) > 0.004 or abs(float(span.group(2)) - tok.ceiling) > 0.004:
            fail(LAYOUT, line, f"--gutter: span documented '{c[1] if len(c) > 1 else ''}', tokens.css runs {tok.floor:g} → {tok.ceiling:g} px")
        # One level of nesting, because a capped floor is a min() inside the
        # clamp(). [^)]* stopped at the min()'s own closing paren and reported
        # half a declaration as the whole of it.
        quoted = re.search(r"clamp\((?:[^()]|\([^()]*\))*\)", row)
        if not quoted or norm(quoted.group(0)) != norm(tok.literal):
            fail(LAYOUT, line, f"--gutter: quoted literal '{quoted.group(0) if quoted else '(none)'}' is not tokens.css's '{tok.literal}'")

    # The token table's --section-gap row — the fourth copy, "64 → 160 px".
    row, line = token_row(layout, "section-gap", LAYOUT, where=lambda c: len(c) > 1 and "→" in c[1])
    if row is not None:
        tok = tokens["section-gap"]
        span = re.search(r"([\d.]+)\s*→\s*([\d.]+)\s*px", cells(row)[1])
        if not span or abs(float(span.group(1)) - tok.floor) > 0.004 or abs(float(span.group(2)) - tok.ceiling) > 0.004:
            fail(LAYOUT, line, f"--section-gap: span documented '{cells(row)[1]}', tokens.css runs {tok.floor:g} → {tok.ceiling:g} px")

    # RHYTHM — both gaps' floors and ceilings with the widths they bind at.
    for gap in ("section-gap", "section-gap-sm"):
        tok = tokens[gap]
        row, line = token_row(layout, gap, LAYOUT, where=lambda c: any("below" in x for x in c))
        if row is None:
            continue
        c = cells(row)
        floor_m = re.search(r"([\d.]+)\s+below\s+(\d+)", c[2] if len(c) > 2 else "")
        ceil_m = re.search(r"([\d.]+)\s+from\s+(\d+)", c[3] if len(c) > 3 else "")
        if not floor_m or abs(float(floor_m.group(1)) - tok.floor) > 0.004 or int(floor_m.group(2)) != round(tok.floor_crossover()):
            fail(LAYOUT, line, f"--{gap}: floor documented '{c[2] if len(c) > 2 else ''}', tokens.css floors at {tok.floor:g} below {tok.floor_crossover():g}")
        if not ceil_m or abs(float(ceil_m.group(1)) - tok.ceiling) > 0.004 or int(ceil_m.group(2)) != round(tok.ceiling_crossover()):
            fail(LAYOUT, line, f"--{gap}: ceiling documented '{c[3] if len(c) > 3 else ''}', tokens.css caps at {tok.ceiling:g} from {tok.ceiling_crossover():g}")
        if not hasattr(tok, "divisor") or norm(c[1] if len(c) > 1 else "").find(f"100vw/{tok.divisor}") != 0:
            fail(LAYOUT, line, f"--{gap}: fluid part documented '{c[1] if len(c) > 1 else ''}', tokens.css divides by {getattr(tok, 'divisor', '?')}")

    # STOPS — the ceiling crossovers, to one decimal.
    gutter = tokens["gutter"]
    stops = {
        "section-gap-sm": tokens["section-gap-sm"].ceiling_crossover(),
        "gutter": gutter.ceiling_crossover(),
        "section-gap": tokens["section-gap"].ceiling_crossover(),
    }
    if "container-max" in tokens:
        stops["container-max"] = tokens["container-max"] * 100.0 / (100.0 - 2.0 * gutter.k)
    for name, exact in stops.items():
        pattern = re.compile(
            r"<tr[^>]*><td><code>--" + name + r"</code></td><td><strong>([\d.]+)</strong></td>"
        )
        m = pattern.search(layout)
        if not m:
            # token_row would also find the register table's rows; the stops
            # table is the only one whose second cell is a lone bold number.
            fail(LAYOUT, 1, f"the 'stops growing at' table has no row for --{name}")
            continue
        printed = float(m.group(1))
        if abs(printed - round(exact, 1)) > 0.04:
            fail(
                LAYOUT, line_of(layout, m.start()),
                f"--{name}: 'stops growing at' documented {printed}, tokens.css puts the crossover at {exact:.1f}",
            )

    report()


def report():
    if failures:
        print("fluid record: the documented arithmetic and tokens.css disagree —", file=sys.stderr)
        for f in failures:
            print("  " + f, file=sys.stderr)
        print(
            "\nIf the stylesheet moved, every figure above is the new correct value: update\n"
            "all three copies in the same commit. If only the record moved, restore it —\n"
            "the stylesheet is the source and the page is the record, in that order.",
            file=sys.stderr,
        )
        sys.exit(1)
    print(
        "fluid record: the seven clamp() tokens and all four documented copies agree — "
        "floors, ramps, ceilings, both crossover columns and all 25 computed sizes re-derived from tokens.css."
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
