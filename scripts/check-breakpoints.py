#!/usr/bin/env python3
"""Enforce the breakpoint register's own completeness claim.

A threshold cannot be a design token. `var()` is not allowed in the prelude of
`@media` or `@container`, and `@custom-media` needs a build step this system
does not have. So every threshold in this system is a literal typed into a
stylesheet, and the only defence against them multiplying is a register: one
list, added to on purpose.

The register exists. It is written twice — as a comment in tokens.css and as a
table on foundations/layout.html — and it says of itself:

    "This register is only worth having if it is complete, and it has now been
     caught twice. ... If you add a threshold to a shipping stylesheet, add it
     here in the same commit — and if you are fixing this register, grep the
     preludes rather than trusting the previous fix to have been exhaustive."

That paragraph is the whole argument for this file. A register kept by hand has
now been caught out four separate times — 60rem and the height threshold, then
34rem and the 62rem media query, then 51.25rem hiding behind a true statement
about a different file — and each fix was a human grepping preludes and hoping
they had got them all. They had not: at the time this script was written three
live container queries were unregistered, one of them added the same day.

Nothing about that is visible in a screenshot. An unregistered threshold renders
perfectly; it just means the next person to reason about where this system
changes shape is reasoning off a list that is missing a row. That is the same
test the other five checks pass — invisible in a render, countable in a file.

WHAT IT CHECKS — the three copies must agree, in both directions:

  live -> register    every width/height threshold in a prelude in the three
                      shipping stylesheets has a register entry.
  register -> live    every register entry still has a query behind it, so a
                      threshold that was removed does not linger as a row
                      describing behaviour the system no longer has.
  register -> table   the comment in tokens.css and the table on
                      foundations/layout.html list the same thresholds. Two
                      copies of a register are two things that can disagree,
                      and this one has drifted before.
  the rem rule        no px or em width threshold in shipping CSS. A media
                      query's rem resolves against the BROWSER's default font
                      size, so a rem threshold is the only kind that tracks a
                      reader who has asked for larger type. Reverting one to px
                      renders identically at 16 px and silently opts that
                      threshold out of the reader's preference — which is the
                      exact bug the register's rem rule was written after.
  the px gloss        the figure after each slash is what the threshold
                      resolves to at a 16 px default. It is a convenience, not
                      a second number to keep in sync, so it is derived here
                      rather than trusted.

WHAT IT DOES NOT CHECK, deliberately:

  Non-dimensional features. prefers-reduced-motion, forced-colors, print,
  hover and pointer are not thresholds — they do not have a width at which the
  layout changes shape, and putting them in the register would make it a list
  of every query rather than a list of every place the system folds.

  Anything outside the three shipping stylesheets. docs.css, per-page <style>
  blocks and prototypes/ are out of scope by the same boundary check-grid-
  tracks.py and check-spacing-scale.py draw, and the register itself spends a
  section saying why: they ship nowhere, and governing them would make the
  register look like it governed the documentation chrome. The register's SCOPE
  list names what lives out there; this script does not police it.

  Crossovers. A min() or clamp() against a viewport unit also changes layout at
  a specific width, when its arms swap. None is a query, none is in the
  register, and the register says so in as many words. A checker that widened
  the definition would be enforcing a different rule than the one written down.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-breakpoints.py       # check, exit 1 on a finding
    python3 scripts/check-breakpoints.py -v    # list every threshold, not only failures
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system" / "assets" / "css"
LAYOUT = ROOT / "design-system" / "foundations" / "layout.html"

# The three stylesheets that ship to control-f.de.
SHIPPING = ("tokens.css", "base.css", "components.css")

# Features that name a length at which the layout changes shape. Everything
# else in a prelude — prefers-*, forced-colors, print, hover, pointer,
# orientation — is a mode, not a threshold.
DIMENSION = ("width", "height", "inline-size", "block-size")

COMMENT = re.compile(r"/\*.*?\*/", re.S)
PRELUDE = re.compile(r"@(media|container)\b([^{;]*)\{")
# (min-|max-)?(width|height|…) : <number><unit>
FEATURE = re.compile(
    r"\b(?:(min|max)-)?(width|height|inline-size|block-size)\s*:\s*"
    r"(-?\d*\.?\d+)([a-z%]*)",
    re.I,
)
# The range form — `(width >= 40rem)`, `(40rem <= width < 60rem)`. Nothing in
# this system uses it today; it is here so that adopting it does not silently
# opt every new threshold out of this check.
RANGE = re.compile(
    r"(?:(-?\d*\.?\d+)([a-z%]*)\s*[<>]=?\s*)?"
    r"\b(width|height|inline-size|block-size)\b"
    r"(?:\s*[<>]=?\s*(-?\d*\.?\d+)([a-z%]*))?",
    re.I,
)


def strip_comments(text):
    """Blank out comments in place, so line numbers survive.

    This is load-bearing rather than hygiene. The register lives in a comment
    in tokens.css and quotes live and dead queries inside its own prose —
    `@media (max-width: 900px), which collapses`, `@media (min-width: 62rem)`,
    a whole paragraph about a threshold that was removed. Read as declarations
    they would be three phantom findings in the file that defines the rule.
    """
    return COMMENT.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


def line_of(text, index):
    return text.count("\n", 0, index) + 1


class Threshold:
    """One live query: a kind, a dimension, a value, and where it is written."""

    def __init__(self, kind, axis, value, unit, file, line, prelude):
        self.kind = kind          # "container" | "viewport"
        self.axis = axis          # "width" | "height"
        self.value = value        # float, in the unit as written
        self.unit = unit
        self.file = file
        self.line = line
        self.prelude = prelude

    @property
    def key(self):
        return (self.kind, self.axis, round(self.value, 4), self.unit)

    def __str__(self):
        v = f"{self.value:g}{self.unit}"
        axis = "" if self.axis == "width" else f" {self.axis}"
        return f"{v} {self.kind}{axis}"


def live_thresholds():
    """Every threshold actually queried by the three shipping stylesheets."""
    found = []
    for name in SHIPPING:
        path = CSS / name
        raw = path.read_text(encoding="utf-8")
        text = strip_comments(raw)
        for m in PRELUDE.finditer(text):
            at, prelude = m.group(1), m.group(2)
            kind = "container" if at == "container" else "viewport"
            line = line_of(text, m.start())
            seen = set()

            for f in FEATURE.finditer(prelude):
                _, axis, value, unit = f.groups()
                axis = "width" if "width" in axis or "inline" in axis else "height"
                seen.add((axis, float(value), unit))

            for r in RANGE.finditer(prelude):
                lo, lo_u, axis, hi, hi_u = r.groups()
                axis = "width" if "width" in axis.lower() or "inline" in axis.lower() else "height"
                for value, unit in ((lo, lo_u), (hi, hi_u)):
                    if value is not None:
                        seen.add((axis, float(value), unit))

            for axis, value, unit in sorted(seen):
                found.append(
                    Threshold(kind, axis, value, unit, name, line, prelude.strip())
                )
    return found


# ---------------------------------------------------------------------------
# The register, read out of its two copies.
# ---------------------------------------------------------------------------

# `       34rem / 544   .cf-error__route folds …`
# Anchored at the line start and requiring the slash figure, so a bare `34rem`
# inside a description — and there are several — is never read as an entry.
ENTRY = re.compile(r"^\s{5,}(\d+(?:\.\d+)?)rem\s*/\s*(\d+)\s+(\S.*)$")
ROW = re.compile(
    r"<tr><td><code>(\d+(?:\.\d+)?)rem</code>\s*/\s*(\d+)[^<]*</td>"
    r"<td>([^<]*)</td><td>(.*?)</td></tr>",
    re.S,
)


def register_from_tokens():
    """The register as written in tokens.css, as {key: description}."""
    raw = (CSS / "tokens.css").read_text(encoding="utf-8")
    start = raw.find("THE BREAKPOINT REGISTER")
    if start < 0:
        sys.exit("check-breakpoints: no breakpoint register found in tokens.css")
    block = raw[start:raw.find("*/", start)]

    entries, kind = {}, None
    for line in block.splitlines():
        if "CONTAINER thresholds" in line:
            kind = "container"
            continue
        if "VIEWPORT thresholds" in line:
            kind = "viewport"
            continue
        if "SCOPE:" in line:
            break
        m = ENTRY.match(line)
        if not m and kind:
            continue
        if m and kind:
            value, gloss, desc = float(m.group(1)), int(m.group(2)), m.group(3)
            axis = "height" if desc.lstrip().startswith("(height)") else "width"
            entries[(kind, axis, round(value, 4), "rem")] = (gloss, desc.strip())
    return entries


def register_from_layout():
    """The register as written in the table on foundations/layout.html."""
    html = LAYOUT.read_text(encoding="utf-8")
    entries = {}
    for m in ROW.finditer(html):
        value, gloss, kind_cell, desc = m.groups()
        kind_cell = re.sub(r"\s+|&nbsp;", " ", kind_cell).strip().lower()
        if kind_cell.startswith("container"):
            kind = "container"
        elif kind_cell.startswith("viewport"):
            kind = "viewport"
        else:
            continue
        axis = "height" if "height" in kind_cell else "width"
        entries[(kind, axis, round(float(value), 4), "rem")] = (int(gloss), desc)
    return entries


def describe(key):
    kind, axis, value, unit = key
    axis = "" if axis == "width" else f" {axis}"
    return f"{value:g}{unit} {kind}{axis}"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every threshold, not only the failures")
    args = ap.parse_args()

    live = live_thresholds()
    tokens = register_from_tokens()
    layout = register_from_layout()
    findings = []

    # --- the rem rule -----------------------------------------------------
    for t in live:
        if t.unit != "rem":
            findings.append(
                f"{t.file}:{t.line}  {t.value:g}{t.unit or '<no unit>'} is not rem — "
                f"@{'container' if t.kind == 'container' else 'media'} ({t.prelude[:60]}). "
                f"A px threshold renders identically at a 16 px default and does not move "
                f"when the reader asks for larger type."
            )

    # --- live -> register -------------------------------------------------
    by_key = {}
    for t in live:
        by_key.setdefault(t.key, []).append(t)

    for key, group in sorted(by_key.items()):
        if key[3] != "rem":
            continue  # already reported by the rem rule
        if key not in tokens:
            where = ", ".join(f"{t.file}:{t.line}" for t in group)
            findings.append(
                f"{describe(key)} is queried at {where} and is NOT in the register "
                f"in tokens.css. Add it in the same commit as the query."
            )

    # --- register -> live -------------------------------------------------
    for key in sorted(tokens):
        if key not in by_key:
            findings.append(
                f"{describe(key)} is in the register in tokens.css and no shipping "
                f"stylesheet queries it. A row describing behaviour the system no "
                f"longer has is worse than no row."
            )

    # --- register -> table ------------------------------------------------
    for key in sorted(set(tokens) - set(layout)):
        findings.append(
            f"{describe(key)} is in the register in tokens.css and missing from the "
            f"table on foundations/layout.html."
        )
    for key in sorted(set(layout) - set(tokens)):
        findings.append(
            f"{describe(key)} is in the table on foundations/layout.html and missing "
            f"from the register in tokens.css."
        )

    # --- the px gloss -----------------------------------------------------
    for source, name in ((tokens, "tokens.css"), (layout, "foundations/layout.html")):
        for key, (gloss, _) in sorted(source.items()):
            expected = key[2] * 16
            if abs(gloss - expected) > 0.5:
                findings.append(
                    f"{describe(key)} in {name} is glossed as {gloss} px; at a 16 px "
                    f"default it is {expected:g} px."
                )

    # --- report -----------------------------------------------------------
    if args.verbose:
        print(f"{len(by_key)} distinct thresholds across {len(live)} queries "
              f"in {', '.join(SHIPPING)}\n")
        for key, group in sorted(by_key.items()):
            mark = "ok " if key in tokens else "NOT REGISTERED "
            desc = tokens.get(key, (0, ""))[1]
            desc = re.sub(r"\s+", " ", desc)[:58]
            print(f"  {mark:<16}{describe(key):<22}{len(group):>2} "
                  f"{'query' if len(group) == 1 else 'queries'}  {desc}")
        print()

    if findings:
        print(f"check-breakpoints: {len(findings)} finding"
              f"{'' if len(findings) == 1 else 's'}\n")
        for f in findings:
            print(f"  - {f}")
        print("\nThe register is only worth having if it is complete."
              "\n  tokens.css                        THE BREAKPOINT REGISTER"
              "\n  foundations/layout.html           #breakpoints")
        return 1

    print(f"check-breakpoints: {len(by_key)} thresholds, all registered in both "
          f"copies, all in rem.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
