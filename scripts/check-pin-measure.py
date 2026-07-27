#!/usr/bin/env python3
"""Hold the pinned stage's three rows to one measure.

.cf-pin is a stage with three rows: an index of marks at the top, the page's
own content in the middle, a progress hairline at the bottom. The index NAMES
the content and the bar runs UNDER it, so the three are one column — 01 has to
stand over the card's left edge or it is annotating the wash beside it.

Nothing enforced that, and the landing page broke it. Its card is bound to the
viewport HEIGHT rather than to the column —

    max-inline-size: calc((100vh - 13rem) * 2)

— because the card is width/2 high, so binding the width to the height is what
guarantees card, index and bar all fit one screen at every size the gate
admits. Correct, derived in place, and written on the CARD alone. The index and
the bar went on taking the full container:

    viewport      container   card    chrome wider by
    1024 x 900          911    911      0
    1280 x 900         1139   1139      0
    1920 x 1080        1280   1280      0
    1280 x  720        1139   1024    115
    1366 x  768        1216   1120     96
    1512 x  782        1280   1148    132
    1440 x  720        1280   1024    256

Every zero is a viewport where the height cap does not bind, and every one of
them is TALL: 900 and 1080 are the heights a person checks at, and the gate's
own edges — 1024 x 900, 1280 x 720 — put one case on each side, so even a sweep
of the gate saw it once and read it as the other edge's business. Every
non-zero is a laptop. At 1440 x 720 the index stood 128 px to the left of the
frame it numbers.

THE FIX MAKES IT UNREPRESENTABLE rather than merely fixed. The measure is a
custom property, --pin-measure, set on .cf-pin__inner and inherited by all
three rows, and components.css applies it to `.cf-pin__inner > *` in one rule.
A page cannot narrow the card without narrowing the chrome with it, because it
never touches the card's width at all.

So the rule this file enforces is the one that keeps that true:

  one applier       exactly one rule sets an inline-axis size on a child of
                    .cf-pin__inner, it lives in components.css, its selector is
                    the shared one, and it reads var(--pin-measure).
  no second hand    no other rule — in any shipping stylesheet or any
                    page-local <style> — sets width / min-width / max-width or
                    their logical spellings on any element that is a direct
                    child of a .cf-pin__inner in the markup. That is the exact
                    declaration that caused this, and it renders perfectly on
                    every tall viewport.
  set on the stage  a page that sets --pin-measure sets it where all three rows
                    inherit it: on a selector matching the .cf-pin__inner
                    element itself, not on one row.

The children are read from the MARKUP, not from a list here, so a stage that
grows a fourth row is covered the day the row is added.

WHAT IT DOES NOT CHECK, deliberately

  Whether the measure is the right measure. `calc((100vh - 13rem) * 2)` is a
  derivation about one page's card and belongs in that page, next to the card.
  This file only holds the three rows to whatever number the page chose.

  The BLOCK axis. The rows are deliberately different heights — that is what
  `grid-template-rows: auto minmax(0, 1fr) auto` is for.

  prototypes/. Declared not-yet-system by the README and out of scope by the
  same boundary every other check in this directory draws.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-pin-measure.py       # check, exit 1 on a finding
    python3 scripts/check-pin-measure.py -v    # print what it found
"""

import argparse
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
SHEETS = [DS / "assets/css/tokens.css", DS / "assets/css/base.css",
          DS / "assets/css/components.css"]
EXCLUDED_DIRS = ("prototypes",)

STAGE = "cf-pin__inner"
APPLIER = ".cf-pin__inner > *"
MEASURE = "--pin-measure"

# The inline axis, in both spellings. `inline-size` and `width` are the same
# property in a horizontal writing mode, and a stage narrowed by either is
# narrowed the same amount.
INLINE_SIZE = re.compile(
    r"(?<![-\w])(?:min-|max-)?(?:width|inline-size)\s*:", re.I)


def strip_comments(css):
    """Blank /* ... */ keeping the newlines, so line numbers survive."""
    return re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), css,
                  flags=re.S)


def rules(css):
    """Yield (line, selector, declarations) for every style rule, at any depth.

    A brace walker rather than a parser: this system's CSS nests @supports
    inside @media inside nothing else, and a rule is any block whose prelude
    does not start with @.
    """
    css = strip_comments(css)
    depth, i, start = 0, 0, 0
    stack = []
    while i < len(css):
        c = css[i]
        if c == "{":
            prelude = css[start:i].strip()
            stack.append(prelude)
            if not prelude.startswith("@"):
                # find the matching close, counting nested braces
                d, j = 1, i + 1
                while j < len(css) and d:
                    d += (css[j] == "{") - (css[j] == "}")
                    j += 1
                yield css.count("\n", 0, i) + 1, prelude, css[i + 1:j - 1]
            start = i + 1
        elif c == "}":
            if stack:
                stack.pop()
            start = i + 1
        i += 1


PSEUDO_ELEMENT = re.compile(
    r"(::[-\w]+|:(?:before|after|first-line|first-letter))\s*$", re.I)


def key_classes(selector):
    """Classes in the RIGHTMOST compound of each comma-separated selector.

    `.a .b` styles .b; `.b .a` does not style .b. Only the subject matters —
    and a PSEUDO-ELEMENT is its own subject: `.cf-pin__bar::after` is the
    bar's fill hairline, which is 100 % wide of the bar on purpose and has
    nothing to do with the stage's measure. Pseudo-CLASSES are stripped and
    the subject kept: `.lp-proc-steps:hover` is still the row.
    """
    out = set()
    for part in selector.split(","):
        part = part.strip()
        if not part or PSEUDO_ELEMENT.search(part):
            continue
        part = re.sub(r":[-\w]+(\([^)]*\))?", " ", part)
        compound = re.split(r"[\s>+~]+", part.strip())[-1] if part.strip() else ""
        out.update(re.findall(r"\.([-\w]+)", compound))
    return out


VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}


class Stage(HTMLParser):
    """Collect the classes on every direct child of a .cf-pin__inner element.

    A tag STACK rather than a depth counter, and end tags pop until they find
    their own name. Both pages hold inline SVG hundreds of elements deep; one
    unclosed tag under a counter shifts every depth after it, and the first
    version of this read `.cf-iso__scene` — a <g> six levels down — as a row of
    the stage while missing `.cf-pin__bar`, which is one.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []           # (tag, is_stage)
        self.children = set()     # classes on the stage's direct children
        self.stage_classes = set()  # classes on the stage element itself
        self.found = False

    def _open(self, tag, attrs, empty):
        classes = set((dict(attrs).get("class") or "").split())
        if self.stack and self.stack[-1][1]:
            self.children |= classes
        is_stage = STAGE in classes
        if is_stage:
            self.found = True
            self.stage_classes |= classes
        if not (empty or tag in VOID):
            self.stack.append((tag, is_stage))

    def handle_starttag(self, tag, attrs):
        self._open(tag, attrs, empty=False)

    def handle_startendtag(self, tag, attrs):
        self._open(tag, attrs, empty=True)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                return


def pages():
    for f in sorted(DS.rglob("*.html")):
        if any(p in f.parts for p in EXCLUDED_DIRS):
            continue
        yield f


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    findings = []
    notes = []

    # ---- who the rows are, read from the markup -------------------------
    rows, stage_sel, stage_pages = set(), set(), []
    for f in pages():
        p = Stage()
        p.feed(f.read_text(encoding="utf-8"))
        if p.found:
            stage_pages.append(f)
            rows |= p.children
            stage_sel |= p.stage_classes
    rows.discard("")
    if not stage_pages:
        print("check-pin-measure: no .cf-pin__inner in the tree — nothing to hold.")
        return 0
    notes.append(f"stage on {len(stage_pages)} page(s); "
                 f"rows: {', '.join(sorted(rows))}")

    # ---- one applier, and it reads the property -------------------------
    appliers = []
    for sheet in SHEETS:
        for line, sel, decls in rules(sheet.read_text(encoding="utf-8")):
            if " ".join(sel.split()) == APPLIER:
                appliers.append((sheet, line, decls))
    if len(appliers) != 1:
        findings.append(
            f"{len(appliers)} rule(s) match `{APPLIER}` in the shipping "
            f"stylesheets; the measure is applied in exactly one place.")
    else:
        sheet, line, decls = appliers[0]
        if MEASURE not in decls:
            findings.append(
                f"{sheet.relative_to(ROOT)}:{line}  `{APPLIER}` does not read "
                f"var({MEASURE}); the three rows are no longer one measure.")
        else:
            notes.append(f"applier: {sheet.relative_to(ROOT)}:{line}")

    # ---- no second hand on any row --------------------------------------
    sources = [(s, s.read_text(encoding="utf-8")) for s in SHEETS]
    for f in pages():
        text = f.read_text(encoding="utf-8")
        for m in re.finditer(r"<style[^>]*>(.*?)</style>", text, re.S | re.I):
            offset = text.count("\n", 0, m.start(1))
            sources.append((f, "\n" * offset + m.group(1)))

    for src, css in sources:
        for line, sel, decls in rules(css):
            flat = " ".join(sel.split())
            if flat == APPLIER:
                continue
            hit = key_classes(flat) & rows
            if not hit:
                continue
            prop = INLINE_SIZE.search(decls)
            if prop:
                findings.append(
                    f"{src.relative_to(ROOT)}:{line}  `{flat}` sets "
                    f"{prop.group(0).strip()} on a row of the pinned stage "
                    f"({', '.join(sorted(hit))}). The stage's measure is "
                    f"{MEASURE} on .cf-pin__inner — a width written on one row "
                    f"narrows that row alone and leaves the other two "
                    f"annotating empty wash.")

    # ---- and the property is set where all three rows inherit it ---------
    for src, css in sources:
        for line, sel, decls in rules(css):
            if not re.search(re.escape(MEASURE) + r"\s*:", decls):
                continue
            flat = " ".join(sel.split())
            if key_classes(flat) & stage_sel:
                notes.append(f"measure set: {src.relative_to(ROOT)}:{line}  `{flat}`")
            else:
                findings.append(
                    f"{src.relative_to(ROOT)}:{line}  `{flat}` sets {MEASURE} "
                    f"somewhere other than the .cf-pin__inner element "
                    f"({', '.join(sorted(stage_sel))}). Set on a row it is "
                    f"inherited by that row only, which is the bug it exists "
                    f"to prevent.")

    if args.verbose or findings:
        for n in notes:
            print(f"  {n}")
    for f in findings:
        print(f"FINDING  {f}")
    if findings:
        print(f"\ncheck-pin-measure: {len(findings)} finding(s).")
        return 1
    print(f"check-pin-measure: the pinned stage's rows share one measure "
          f"({len(rows)} rows, {len(stage_pages)} page(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
