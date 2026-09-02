#!/usr/bin/env python3
"""A state written for the pointer has to be written for the keyboard beside it.

Every one of this system's interactive responses is authored as ONE rule with
both triggers in its selector list — the section header's action, the news
card, the vacancy row, the search result:

    .cf-section-header__action:hover,
    .cf-section-header__action:focus-visible { color: var(--text-primary); }

That shape is the claim, and it is a claim about who the response belongs to:
the element being ADDRESSED, not the device that addressed it. Split the two
apart and the rule silently becomes a rule about mice.

WHAT WAS ACTUALLY BROKEN when this was written. Five rules across the four
stylesheets answered `:hover` and nothing else:

    acts.css   .lp-ev-src a          the landing page's evidence sources
    docs.css   .docs-nav__list a     the chapter list, every page
    docs.css   .docs-card            the index's card grid
    docs.css   .docs-plate img       the gallery of the designer's plates

Three of those four are the entire navigation of the documentation, and the
card is the case that shows why the outline ring is not the missing half: a
.docs-card carries no underline, no arrow and no colour change, so the border
and the lift ARE what says it is a link. A keyboard reader got the ring — "this
one" — and none of the sentence after it.

None of this is a WCAG failure and that is the point. base.css draws a visible
ring on every focusable thing in the system, so a checker built around 2.4.7
passes all five: the ring is there, focus is visible, the box is ticked. What
is absent is the response the pointer reader gets, which is a design decision
this system has taken thirty-odd times in one direction and four times in the
other by accident. A gate is how a convention that nothing enforces stops being
observed only where somebody remembered it.

THE RULE. In the four shipping stylesheets, any style rule whose selector list
mentions `:hover` must also mention `:focus-visible` or `:focus-within` — in
that same selector list, not somewhere else in the file. The same-rule form is
deliberate: two adjacent rules with the same declarations satisfy the letter of
"the element has a focus style" and are exactly the arrangement that drifts,
because the next edit lands in one of them.

TWO EXEMPTIONS, both derived rather than listed by name.

  A rule whose every selector is disabled, aria-disabled or aria-busy. Those
  exist to CANCEL a hover response on a control that is not currently a
  control, and a control that is not a control does not want a focus response
  either. .cf-btn--ghost[disabled]:hover is the shape.

  A rule whose every selector ends at a pseudo-element that cannot take focus.
  ::file-selector-button is the one in this tree: it is painted by the input,
  the input is what the reader tabs to, and `::file-selector-button:focus-
  visible` matches nothing at all. Writing it would be worse than the gap.

Both are read off the selector, so a fifth stylesheet or a sixth exemption of
either shape is covered by existing rather than by being added here.

WHAT THIS CANNOT SEE, stated so it is not mistaken for covered. It reads
selectors, not declarations: a rule that names both triggers and gives them
different responses passes, and so does one whose focus response is invisible.
It says nothing about :active, and nothing about whether the ring itself is
adequate — check-a11y.py and base.css hold that. This holds the one part of
the convention that is a fact about the text: both triggers, one rule.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-hover-focus-parity.py
    python3 scripts/check-hover-focus-parity.py -v   # every :hover rule, not only strays
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system" / "assets" / "css"

# The four stylesheets a reader's browser loads. preview.css is 27 lines of
# iframe chrome with no interactive rule in it and tokens.css declares custom
# properties; neither can hold a state.
SHEETS = ["base.css", "components.css", "acts.css", "docs.css"]

COMMENT = re.compile(r"/\*.*?\*/", re.S)

# A selector that is only ever a cancellation: the control is off, so neither
# trigger applies to it.
OFF = re.compile(r"\[(?:disabled|aria-disabled|aria-busy)\b")

# A selector whose subject is a pseudo-element the reader cannot tab to, so
# there is no focus-visible form of it to write. The state pseudo-classes are
# taken off the tail first — the shape in this tree is
# `::file-selector-button:hover`, where the pseudo-element is the subject and
# :hover is what is being said about it.
STATE_TAIL = re.compile(r"(?::(?:hover|active|focus|focus-visible|focus-within))+\s*$")
UNFOCUSABLE = re.compile(r"::[a-z-]+(?:\([^()]*\))?\s*$")


def strip_comments(text):
    """Blank the comments, keeping the newlines so reported line numbers stay
    the file's own. A prose sentence quoting `:hover` is not a rule."""
    return COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def selectors(text):
    """Yield (line, selector-list) for every style rule in the sheet.

    A selector list is what stands between the previous rule's boundary and the
    `{` that opens this one. At-rules are boundaries like any brace, which is
    what keeps `@media (hover: hover)` out of the list it precedes; nesting is
    not used in these sheets, so the flat scan is the whole grammar needed.
    """
    start = 0
    for m in re.finditer(r"[{};]", text):
        if m.group(0) == "{":
            head = text[start:m.start()]
            line = text.count("\n", 0, m.start()) + 1
            sel = " ".join(head.split())
            if sel and not sel.startswith("@"):
                yield line, sel
        start = m.end()


def parts(sel):
    """Split a selector list on the commas that are not inside :is(), :has(),
    :not() or :where(). Those functions carry commas of their own and a naive
    split turns one selector into fragments that are not selectors."""
    out, depth, buf = [], 0, ""
    for ch in sel:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(buf.strip())
            buf = ""
        else:
            buf += ch
    if buf.strip():
        out.append(buf.strip())
    return out


def exempt(sel):
    """True when EVERY selector in the list is one of the two derived shapes.

    Every, not any: a list that pairs a disabled override with a live selector
    is a rule about a live control and owes the focus form like any other.
    """
    ps = parts(sel)
    return bool(ps) and all(
        OFF.search(p) or UNFOCUSABLE.search(STATE_TAIL.sub("", p)) for p in ps)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print every :hover rule read, not only the strays")
    args = ap.parse_args()

    findings, paired, exempted = [], [], []
    for name in SHEETS:
        path = CSS / name
        if not path.is_file():
            print("missing stylesheet: %s" % name)
            return 1
        text = strip_comments(path.read_text(encoding="utf-8"))
        for line, sel in selectors(text):
            if ":hover" not in sel:
                continue
            if ":focus-visible" in sel or ":focus-within" in sel:
                paired.append((name, line, sel))
            elif exempt(sel):
                exempted.append((name, line, sel))
            else:
                findings.append((name, line, sel))

    if args.verbose:
        for label, rows in (("paired", paired), ("exempt", exempted),
                            ("unpaired", findings)):
            print("%s: %d" % (label, len(rows)))
            for name, line, sel in rows:
                print("  %s:%d  %s" % (name, line, sel[:96]))

    if findings:
        print("hover without focus: %d rule(s)\n" % len(findings))
        for name, line, sel in findings:
            print("  design-system/assets/css/%s:%d\n    %s" % (name, line, sel[:110]))
        print("\n  A response written for :hover alone is a response for readers who")
        print("  point. Add the trigger to the SAME selector list — the split form")
        print("  is what drifts:")
        print("\n      .thing:hover,\n      .thing:focus-visible { … }")
        return 1

    print("hover/focus parity: %d rule(s) name both, %d exempt, across %d sheet(s)."
          % (len(paired), len(exempted), len(SHEETS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
