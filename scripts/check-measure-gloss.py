#!/usr/bin/env python3
"""Enforce that every px gloss of a ch measure is derived from the shipped font.

`ch` is not a character. It is the advance width of the font's "0", and the
zero of Geist — the body face this system ships — is 0.6875em: 11 px at 16 px,
measured as the resolved .cf-prose grid track in Chromium (66ch computed to
726 px; 726 / 66 = 11 exactly, and the figure is a metric of the woff2, not of
any one rasterizer). Helvetica's zero, the first fallback, is 0.556em.

That 24 % gap is how this system carried a documented lie for a year. The
prose-track comment in components.css glossed 66ch as "587 px" — 66 × 8.9,
the FALLBACK font's arithmetic — while every browser with the webfont drew
726 px. Nothing rendered wrong; the page just read at 90 characters a line at
a 768 viewport and 100.5 on datenschutz at 1280, past the top of the 45–90
band tokens.css itself cites, and no screenshot can show a line that is
merely too long. Invisible in a render, countable in a file: the same test
every other check in this directory passes.

WHAT IT CHECKS — the arithmetic must be derived, in every copy:

  the token        --measure-prose in tokens.css is read as the single source
                   of truth for the prose measure's ch value.
  token -> docs    components/article.html states the same ch value, twice —
                   in its type table and in its grid-track note — and
                   components/search.html's excerpt gloss agrees. A docs page
                   quoting a stale value teaches the next reader the bug.
  the px gloss     every "lands at N px" / "comes out at N px" figure written
                   beside the prose measure — components.css's prose-track
                   comment, article.html's note — must equal
                   round(ch × 0.6875 × font-size) for the font size named
                   beside it (32 px for the h2 example, 16 px for the
                   paragraph). A gloss is a convenience, not a second number
                   to keep in sync, so it is derived here rather than trusted.

WHAT IT DOES NOT CHECK, deliberately:

  Other measure tokens. --measure and --measure-tight carry no px glosses in
  their comments today; the rule binds a gloss wherever one is written, and
  extending it is adding the gloss, not widening this script.

  The band itself. Whether 53ch is the RIGHT measure is a design judgement,
  argued in tokens.css with measured characters-per-line; this script only
  guarantees the arithmetic published beside the judgement is the shipped
  font's and that all copies of it agree.

If the body font ever changes, GEIST_CH_EM below is wrong: re-measure the
resolved .cf-prose track in a real browser (document.querySelector('.cf-prose')
→ getComputedStyle(...).gridTemplateColumns, divided by the ch count) and
update the constant in the same commit as the font.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-measure-gloss.py       # check, exit 1 on a finding
    python3 scripts/check-measure-gloss.py -v    # show every figure it derives
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOKENS = ROOT / "design-system" / "assets" / "css" / "tokens.css"
COMPONENTS = ROOT / "design-system" / "assets" / "css" / "components.css"
ARTICLE = ROOT / "design-system" / "components" / "article.html"
SEARCH = ROOT / "design-system" / "components" / "search.html"

# The advance of Geist's "0", in em. Measured, not assumed — see the docstring
# for how, and re-measure before touching it.
GEIST_CH_EM = 0.6875

# The two font sizes the published arithmetic is worked at: the h2 example and
# the prose paragraph.
EXAMPLE_SIZES = (32, 16)


def token_value():
    """--measure-prose's ch value, from tokens.css."""
    text = TOKENS.read_text(encoding="utf-8")
    m = re.search(r"--measure-prose:\s*(\d+(?:\.\d+)?)ch\s*;", text)
    if not m:
        sys.exit("check-measure-gloss: no --measure-prose token in tokens.css")
    return float(m.group(1))


def stated_ch(path, patterns):
    """Every ch figure a doc states for the prose measure, as (line, value)."""
    text = path.read_text(encoding="utf-8")
    found = []
    for pat in patterns:
        for m in re.finditer(pat, text):
            line = text.count("\n", 0, m.start()) + 1
            found.append((line, float(m.group(1))))
    return found


def stated_glosses(path):
    """Every '<N>ch … at F px … <P> px' arithmetic line in a file.

    Matches the shape both copies use — 'Nch declared on an h2 resolves
    against the h2's own 32 px and comes out at 1166 px' / 'lands at 1166 px'
    — and returns (line, ch, font_px, gloss_px) for each.
    """
    text = path.read_text(encoding="utf-8")
    found = []
    pat = re.compile(
        r"(\d+(?:\.\d+)?)ch(?:</code>)?[^.]*?(\d+)\s*px[^.]*?"
        r"(?:comes out at|lands at)\s*(\d+(?:\.\d+)?)\s*px",
        re.S,
    )
    for m in pat.finditer(text):
        line = text.count("\n", 0, m.start()) + 1
        found.append((line, float(m.group(1)), int(m.group(2)), float(m.group(3))))
    # The paragraph half of the worked example quotes no ch of its own — 'the
    # same token at 16 px … comes out at 583 px' — so the token's value is
    # implied and reported as ch=None for the caller to fill in.
    implied = re.compile(
        r"the same token at (\d+)\s*px and\s*"
        r"(?:comes out at|lands at)\s*(\d+(?:\.\d+)?)\s*px",
        re.S,
    )
    for m in implied.finditer(text):
        line = text.count("\n", 0, m.start()) + 1
        found.append((line, None, int(m.group(1)), float(m.group(2))))
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="show every figure derived, not only the failures")
    args = ap.parse_args()

    token = token_value()
    findings = []
    seen = []

    # --- token -> docs: the ch value, everywhere it is quoted --------------
    quotes = (
        (ARTICLE, [r"(\d+(?:\.\d+)?)\s*ch\s*\(<code>--measure-prose</code>\)",
                   r"<code>(\d+(?:\.\d+)?)ch</code>"]),
        (SEARCH, [r"<code>--measure-prose</code>\s*\((\d+(?:\.\d+)?)\s*ch\)"]),
    )
    for path, patterns in quotes:
        stated = stated_ch(path, patterns)
        if not stated:
            findings.append(f"{path.name}: quotes no ch value for the prose "
                            f"measure — the doc and this check have drifted apart")
        for line, value in stated:
            seen.append((path.name, line, f"{value:g}ch stated"))
            if value != token:
                findings.append(
                    f"{path.name}:{line}  states {value:g}ch; tokens.css says "
                    f"--measure-prose is {token:g}ch. Update the doc in the same "
                    f"commit as the token."
                )

    # --- the px gloss: derived, not trusted --------------------------------
    for path in (COMPONENTS, ARTICLE):
        glosses = stated_glosses(path)
        if not glosses:
            findings.append(f"{path.name}: no 'Nch … at F px … lands at P px' "
                            f"arithmetic found — the doc and this check have "
                            f"drifted apart")
        for line, ch, font_px, gloss in glosses:
            stated = ch if ch is not None else token
            expected = round(stated * GEIST_CH_EM * font_px)
            seen.append((path.name, line,
                         f"{stated:g}ch at {font_px} px glossed {gloss:g} px "
                         f"(derived: {expected})"))
            if ch is not None and ch != token:
                findings.append(
                    f"{path.name}:{line}  works the arithmetic with {ch:g}ch; "
                    f"the token is {token:g}ch."
                )
            if font_px not in EXAMPLE_SIZES:
                continue
            if abs(gloss - expected) > 1:
                findings.append(
                    f"{path.name}:{line}  glosses {stated:g}ch at {font_px} px "
                    f"as {gloss:g} px; Geist's zero is {GEIST_CH_EM}em, so it "
                    f"is {expected} px. A gloss computed with the fallback "
                    f"font's zero is how 587 px shipped while 726 px rendered."
                )

    if args.verbose:
        for name, line, note in seen:
            print(f"  {name:24s} {line:5d}  {note}")
        print()

    if findings:
        print(f"check-measure-gloss: {len(findings)} finding"
              f"{'' if len(findings) == 1 else 's'}\n", file=sys.stderr)
        for f in findings:
            print(f"  - {f}", file=sys.stderr)
        print("\nThe unit is not the target: `ch` is the width of the shipped "
              "font's zero.\n  tokens.css § measure has the measurements.",
              file=sys.stderr)
        return 1

    print(f"check-measure-gloss: --measure-prose is {token:g}ch, "
          f"{len(seen)} stated figures, all derived from the shipped font's "
          f"{GEIST_CH_EM}em zero.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
