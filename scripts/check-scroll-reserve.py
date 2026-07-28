#!/usr/bin/env python3
"""The scroll port reserves the layer fixed over its bottom edge.

The fifty-second check, and the third whose subject is the scroll itself.
check-arrival.py holds where a reader who asked for an ADDRESS is put;
check-consent-clearance.py holds the banner's height against the HERO. This one
holds the same banner's height against the place a Tab press puts a control.

WHAT WENT WRONG. Chromium scrolls a newly focused off-screen element into view.
check-arrival.py's own docstring already says so — "on a page this tall every
Tab to an off-screen control is one of these journeys" — and it says it while
measuring how LONG the journey takes, under the preference. Nothing ever asked
where the journey ENDS.

It ends against the bottom edge. The alignment is `nearest`, and an element
entered from above is nearest when its bottom meets the viewport's bottom. That
edge is where `[data-cf-consent-banner]` is fixed — `inset: auto 0 0 0` — and
the banner is not a hairline: 144.4 px at 1280 and 1440, 232.9 at 768 and 333.5
at 375, which is 41 % of a 375 x 812 screen. So on the one visit the banner is
shown, a keyboard reader tabbing down the page parked control after control
behind the notice.

Counted on patterns/landing-page.html, first load, nothing dismissed, under
prefers-reduced-motion: reduce so `scroll-behavior` is auto and every stop is
measured at rest rather than mid-flight. A stop is counted only when
document.elementFromPoint at the CONTROL'S OWN CENTRE returns the banner — that
is entirely hidden, which is the wording WCAG 2.2 SC 2.4.11 (Level AA) fails on,
not merely clipped:

    viewport      stops   entirely hidden   of those, mid-page   banner h
    375 x 812      45           30                  19             333.5
    768 x 1024     45           20                  10             232.9
    1280 x 800     50           11                   1             144.4
    1440 x 900     50           11                   1             144.4

"Mid-page" is the column that separates the two faults. A stop mid-page is one
the document could still have scrolled for and did not: that is the scroll
port's half. The rest are in the final viewport, where there is no scroll left
to give at any setting — the footer's ten links, its contact button and its
wordmark — and no amount of scroll padding can move them. Two faults, one
symptom, and fixing either alone leaves the other whole.

WHY NOBODY SAW IT. Every screenshot of this page is a screenshot of the second
visit. The banner is shown once, the decision is stored, and from then on the
page tabs perfectly — which is the state anyone reviewing the page is in by
their second load. The first-visit state is also the state that renders
correctly: the banner is drawn exactly as designed, the focus ring is drawn
exactly as designed, and they are simply drawn in the same 144 to 334 px of
screen. There is no wrong pixel to find.

WHAT IS CHECKED, and all four links break silently:

  1. base.css's `html` rule declares scroll-padding-bottom reading
     var(--cf-consent-height, 0px).

  2. It is on `html` and not on `body`. scroll-padding acts on the scroll
     CONTAINER, and <html> is the scrolling element on every page in this tree.
     Moved to body — which is where a tidy-up would put it, next to the page's
     other page-level padding — it parses, computes, inspects correctly in
     devtools, and does nothing at all.

  3. components.css's `.cf-footer` adds the same term to its own
     padding-block end, and ADDS it: --space-8 has to survive as a term. The
     substitution is the silent one — the footer would measure as reserving the
     banner while having quietly given up its own bottom rhythm on every page
     that has no banner, which is thirteen of the fourteen states this tree
     renders.

  4. The fallback is 0px everywhere the property is read, in every shipping
     stylesheet. This is check-consent-clearance.py's rule 2 and it is restated
     here rather than borrowed, because this check adds two new readers of the
     property and a fallback is per-reader. Any other value reserves scroll and
     height on every page that never shows a banner.

WHAT THIS DOES NOT CLAIM. The top edge is the other half of SC 2.4.11 and is
not held here. Shift+Tab lands a control against the viewport's TOP edge, under
the sticky nav: measured on the same page, 12 stops at 375, 5 at 768 and 1 at
1280 and 1440. That is the same mechanism at the other end, and the fix is
scroll-padding-top on the same rule — but the tree currently buys top clearance
per element, with `scroll-margin-top: calc(var(--nav-height) + var(--space-6))`
on four heading classes, and check-arrival.py holds exactly those. Adding root
padding without retiring that list would double the clearance and land every
anchor 84 px lower than it lands today. The two have to move together, and they
are not this check's subject.

stdlib only, no build step, no dependency — the same contract as the fifty-one
checks beside it.

    python3 scripts/check-scroll-reserve.py       # check, exit 1 on a finding
    python3 scripts/check-scroll-reserve.py -v    # print every value it read
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system" / "assets" / "css"

# The three that ship, in cascade order — same set as every check beside this.
SHIPPING = ("tokens.css", "base.css", "components.css")
PROP = "--cf-consent-height"

failures = []
notes = []


def strip_comments(s):
    return re.sub(r"/\*.*?\*/", "", s, flags=re.S)


def rule_body(text, selector):
    """The declaration block of the first top-level `selector { ... }`, comments
       already gone. None when the tree has stopped writing that rule at all,
       which is a finding and never a skip."""
    m = re.search(r"(?m)^" + re.escape(selector) + r"\s*\{", text)
    if not m:
        return None
    i, depth = m.end(), 1
    while i < len(text) and depth:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    return strip_comments(text[m.end(): i - 1])


def decl(body, prop):
    """The last declaration of `prop` in a block — the one the cascade keeps."""
    found = re.findall(re.escape(prop) + r"\s*:\s*([^;]+);", body)
    return " ".join(found[-1].split()) if found else None


sources = {name: (CSS / name).read_text(encoding="utf-8") for name in SHIPPING}

# ---- 1 & 2 · the scroll port reserves the banner, and it is the scroll port --
base = sources["base.css"]
html_rule = rule_body(base, "html")
if html_rule is None:
    failures.append("base.css: no top-level `html` rule found — the scroll port "
                    "is where scroll-padding has to be declared")
else:
    pad = decl(html_rule, "scroll-padding-bottom") or decl(html_rule, "scroll-padding")
    if pad is None:
        failures.append(
            "base.css html: no scroll-padding-bottom.\n"
            "    Chromium scrolls a newly focused off-screen element to the "
            "viewport's BOTTOM edge, which is where [data-cf-consent-banner] is "
            "fixed. Without this the banner takes 30 of 45 tab stops at 375 x 812 "
            "and 20 of 45 at 768 x 1024 — entirely hidden, WCAG 2.2 SC 2.4.11 (AA)."
        )
    elif PROP not in pad:
        failures.append(
            "base.css html: scroll-padding-bottom does not read the banner's "
            "published height.\n    scroll-padding-bottom: %s\n"
            "    The banner is 144.4 / 232.9 / 333.5 px at the three widths its "
            "copy re-wraps at and moves again with a reader's type size, so the "
            "reservation has to be var(%s, 0px) and never a constant." % (pad, PROP)
        )
    else:
        notes.append("base.css html    scroll-padding-bottom: %s" % pad)

# The silent one: the same declaration on body parses and does nothing.
body_rule = rule_body(base, "body")
if body_rule is not None:
    stray = decl(body_rule, "scroll-padding-bottom") or decl(body_rule, "scroll-padding")
    if stray is not None:
        failures.append(
            "base.css body: scroll-padding-bottom: %s\n"
            "    scroll-padding acts on the scroll CONTAINER and <html> is the "
            "scrolling element on every page in this tree. On body it parses, "
            "computes, reads back correctly in devtools and moves nothing." % stray
        )

# ---- 3 · the last block pays for the last screen --------------------------
components = sources["components.css"]
footer = rule_body(components, ".cf-footer")
if footer is None:
    failures.append("components.css: no top-level `.cf-footer` rule found")
else:
    pb = decl(footer, "padding-block")
    end = None
    if pb is not None:
        # padding-block: <start> <end>; a single value sets both. Split on the
        # top level only — `var(--x, 0px)` and `calc(a + b)` are ONE value each
        # and the space inside them is not a separator. Splitting naively made
        # this read `0px)` as the end value, which is the branch that reports a
        # substitution as an absence: a right answer for the wrong reason, and
        # the next person to read the message would go looking in the wrong file.
        parts, depth, cur = [], 0, ""
        for ch in pb:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            if ch.isspace() and depth == 0:
                if cur:
                    parts.append(cur)
                cur = ""
            else:
                cur += ch
        if cur:
            parts.append(cur)
        end = parts[-1] if parts else None
    if pb is None:
        failures.append(
            "components.css .cf-footer: no padding-block declaration.\n"
            "    scroll-padding cannot move a control in the document's final "
            "viewport — there is no scroll left. The only thing that adds scroll "
            "at the end of a document is height at the end of a document, so the "
            "footer's own bottom padding is where the last screen is paid for."
        )
    elif PROP not in (end or ""):
        failures.append(
            "components.css .cf-footer: the bottom padding does not reserve the "
            "consent banner.\n    padding-block: %s\n"
            "    Without it the footer's ten links, its contact button and its "
            "wordmark stay entirely behind the banner on a first visit: 11 / 10 / "
            "10 / 10 stops at 375 / 768 / 1280 / 1440, at every setting, because "
            "the document has run out of scroll." % pb
        )
    elif "--space-8" not in (end or ""):
        failures.append(
            "components.css .cf-footer: the banner's height REPLACED the footer's "
            "own bottom rhythm instead of adding to it.\n    padding-block: %s\n"
            "    --space-8 has to survive as a term. Substituted, the footer "
            "measures as reserving the banner and has silently given up its own "
            "padding on every page that never shows one." % pb
        )
    else:
        notes.append("components.css .cf-footer    padding-block: %s" % pb)

# ---- 5 · and paper gets the space back ------------------------------------
# The footer's reservation is scroll, and paper has none. --cf-consent-height is
# an INLINE property on <html> written by cf-consent.js, so no stylesheet rule
# can zero it — it has to be revoked at the reader.
#
# Measured under Chromium's print emulation the property reads 0px even without
# the revocation, because hiding the banner resizes it and cf-consent.js's
# ResizeObserver republishes the height. That is a script racing a paint, which
# is why the emulation is not the evidence: the same file says that where there
# is no ResizeObserver the property "degrades to the first measurement" — the
# screen one — and a print snapshot need not wait for an observer callback. The
# correction belongs in the cascade, where it cannot arrive late. Without it a
# first-visit print stamps 144 to 334 px of extra black under the footer, which
# is the fault the print block above it already exists to stop.
print_blocks = re.findall(r"@media\s+print\s*\{(.*?)\n\}", strip_comments(components), re.S)
revoked = any(
    re.search(r"\.cf-footer\s*\{[^}]*padding-block-end\s*:\s*[^;}]+", block)
    for block in print_blocks
)
if not revoked:
    failures.append(
        "components.css @media print: .cf-footer does not give back the banner's "
        "reservation.\n"
        "    The reservation buys the document's last screen of SCROLL, and paper "
        "has none. --cf-consent-height is an inline property on <html>, so hiding "
        "the banner in print leaves it set and no stylesheet rule can zero it — it "
        "has to be revoked at the reader with a padding-block-end inside @media "
        "print. Left in, printing on a first visit stamps 144 to 334 px of extra "
        "black under the footer."
    )
else:
    notes.append("components.css @media print    .cf-footer padding-block-end revoked")

# ---- 4 · the fallback is 0px, at every reader -----------------------------
READ = re.compile(r"var\(\s*" + re.escape(PROP) + r"\s*(?:,\s*([^)]*))?\)")
readers = 0
for name in SHIPPING:
    for i, line in enumerate(strip_comments(sources[name]).splitlines(), 1):
        for m in READ.finditer(line):
            readers += 1
            fallback = (m.group(1) or "").strip()
            if fallback != "0px":
                failures.append(
                    "%s:%d reads %s with fallback %r.\n"
                    "    It must be 0px. The property exists only while the banner "
                    "does, so any other fallback reserves scroll and height on "
                    "every page that never shows one, permanently."
                    % (name, i, PROP, fallback or "(none)")
                )
if readers < 3:
    failures.append(
        "only %d reader(s) of %s across the shipping stylesheets; the "
        "reservation is three: the hero's height cap, the scroll port's bottom "
        "padding and the footer's." % (readers, PROP)
    )

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("-v", "--verbose", action="store_true")
args, _ = parser.parse_known_args()

if failures:
    print("check-scroll-reserve: a control that takes keyboard focus is scrolled "
          "to the viewport's bottom edge, and the consent banner is fixed to it.")
    print()
    for f in failures:
        print("  " + f)
        print()
    sys.exit(1)

print("check-scroll-reserve: the scroll port and the document's last block both "
      "reserve the consent banner; %d reader(s) of %s, every fallback 0px."
      % (readers, PROP))
if args.verbose:
    for n in notes:
        print("  " + n)
