#!/usr/bin/env python3
"""A counter lifted off the label ramp has to be an atom, or it breaks in two.

.cf-section-header is two halves on one baseline row: a label at the left end
of a hairline and a count at the right. components.css floors BOTH halves at
`min-width: 0`, and it is right to — its own note tabulates what happens
without the floor, a German compound in either half taking the whole document
sideways at 320:

    .cf-section-header__count   "6 Fragen" -> 42 chars   320 -> 384 px

But `min-width: 0` does not only stop the overflow. It makes both halves
SHRINKABLE, and a flex row shrinks its items in proportion to their
max-content — so the count gives up width while the label still has slack, and
the count is the half with nowhere to give. At the component's own
`--text-xs` that never shows: eleven-pixel mono fits at every width the site
supports, so the shrink is theoretical and the row has one line box.

IT STOPS BEING THEORETICAL THE MOMENT A SECTION RE-RAMPS THE ROW. acts.css
sets both halves of the landing page's "SERVICE OFFERING / 4 SCHRITTE" at
`--text-h2` — three times the size, same row, same floor — and argues it well:
the header is the seam the drawing hands the reader over at, and eleven pixels
of mono there is a footnote where the page needs a heading. Nothing about that
decision is wrong. What it did not carry with it is the consequence: at
--text-h2 the count runs out of room first, and a counter that runs out of room
wraps between the number and the noun it counts.

Measured on the render, count line boxes at the header:

                                     320   360   375   414   480
    patterns/landing-page.html         3     2     2     2     1     "4 Schritte"
    prototypes/statement-to-process     2     2     2     2     2     "In vier Schritten"

Three line boxes at 320 on the landing page: "4" alone on one, "SCHRITTE"
under it, and the count reads as a numeral and a noun rather than as one
answer. It is the only place on that page that says how many steps there are.

WHAT THE FIX HAS TO BE, and why half of it is not enough. Making the count
rigid — `flex: none` — fixes the landing page and BREAKS the other consumer of
the same stylesheet: statement-to-process.html counts "In vier Schritten", six
characters longer, and with the count immovable the label is squeezed under
its own min-content and breaks mid-word — 4 line boxes at 360, 7 at 320, a
170 px header. So rigidity needs a release: `flex-wrap: wrap` on the row, and
when the two halves cannot stand on one line the count drops to its own line
whole, still ending at the rule's right edge. Both declarations or neither;
one alone is a different defect from the one it fixes.

WHAT THIS CHECKS. For every section header in design-system/ whose label or
count is given a font-size off the label ramp (--text-xs, --text-sm — the two
steps check-label-ramp.py holds the rest of the system to), the local classes
that re-ramped it must also declare:

    the count class    flex: none  /  flex: 0 0 auto  /  flex-shrink: 0
    the header class   flex-wrap: wrap

A header still on the ramp is not a finding and never reaches the requirement:
the thirty-odd ordinary section headers across patterns/ set no size of their
own and this script is silent about them.

The classes are READ OUT OF THE MARKUP, not listed here. An element carrying
`cf-section-header__count` names its own local class beside it, and that is
what pairs `sp-head__count` to `sp-head`; a section that re-ramps its header
under some new name is covered the day it is written, without an edit here.

SCOPE is the four shipping stylesheets plus every <style> block on a page in
design-system/ — the same corpus check-label-ramp.py reads, plus acts.css,
because acts.css is where the re-ramping this check exists for is written.

stdlib only, no build step, no dependency — the same contract as the checks
beside it.

    python3 scripts/check-count-atom.py       # check, exit 1 on a finding
    python3 scripts/check-count-atom.py -v    # print every header row it read
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system" / "assets" / "css"
DESIGN_SYSTEM = ROOT / "design-system"

# acts.css is in and check-label-ramp.py's list is not enough here: the
# re-ramping this check reads is written in acts.css and nowhere else.
SHIPPING = ("tokens.css", "base.css", "components.css", "acts.css")

# The label ramp, from check-label-ramp.py. A header half sized at one of
# these is the component as shipped and carries no requirement.
RAMP = ("--text-xs", "--text-sm")

HEADER = "cf-section-header"
LABEL = "cf-section-header__label"
COUNT = "cf-section-header__count"

SIZE = re.compile(r"font-size:\s*([^;}]+)")
TOKEN = re.compile(r"var\(\s*(--[\w-]+)")
# flex: none, flex: 0 0 auto, flex: 0 1 auto is NOT rigid (shrink 1).
RIGID = re.compile(
    r"(?:^|;)\s*(?:"
    r"flex-shrink:\s*0(?:\D|$)"
    r"|flex:\s*none\b"
    r"|flex:\s*0\s+0(?:\s|;|$)"
    r")", re.M)
WRAPS = re.compile(r"(?:^|;)\s*flex-wrap:\s*wrap(?:-reverse)?\b", re.M)
CLASS_IN_SELECTOR = re.compile(r"\.([A-Za-z_][\w-]*)")


def blocks(text):
    """Every `selector { ... }` pair, comments blanked, line numbers kept.

    A brace walker and not a parser, the same shape as the other checks: at-
    rules nest, so a block whose body still contains a brace is passed over
    and its inner blocks are found on their own.
    """
    text = re.sub(r"/\*.*?\*/", lambda m: " " * len(m.group(0)), text, flags=re.S)
    for m in re.finditer(r"\{([^{}]*)\}", text):
        body = m.group(1)
        head = text[:m.start()]
        selector = re.split(r"[{}]", head)[-1]
        selector = selector.rsplit(";", 1)[-1].strip()
        selector = " ".join(selector.split())
        yield selector, body, head.count("\n") + 1


def sources():
    """(label, text) for every file whose rules this check governs."""
    for name in SHIPPING:
        path = CSS / name
        if path.exists():
            yield name, path.read_text(encoding="utf-8")
    for page in sorted(DESIGN_SYSTEM.rglob("*.html")):
        text = page.read_text(encoding="utf-8")
        label = str(page.relative_to(DESIGN_SYSTEM))
        for m in re.finditer(r"<style[^>]*>(.*?)</style>", text, flags=re.S):
            lead = text[:m.start(1)].count("\n")
            yield label, "\n" * lead + m.group(1)


def header_rows():
    """Every section header in the markup, as (page, header, label, count).

    Each of the three is the SET of classes the element carries, so a local
    treatment names itself: the landing page's row yields
    {cf-section-header, sp-head} / {..., sp-head__title} / {..., sp-head__count}.
    A header missing a half is skipped — check-section-counts.py is what reads
    the markup's shape; this one only reads type and flex.
    """
    tag = re.compile(r"<(\w+)[^>]*\bclass=\"([^\"]*)\"[^>]*>")
    for page in sorted(DESIGN_SYSTEM.rglob("*.html")):
        text = page.read_text(encoding="utf-8")
        name = str(page.relative_to(DESIGN_SYSTEM))
        found = [(m.start(), set(m.group(2).split())) for m in tag.finditer(text)]
        for pos, classes in found:
            if HEADER not in classes:
                continue
            lab = cnt = None
            # The two halves are this header's own children: the next label
            # and count in document order before the following header.
            for pos2, c2 in found:
                if pos2 <= pos:
                    continue
                if HEADER in c2:
                    break
                if LABEL in c2 and lab is None:
                    lab = c2
                if COUNT in c2 and cnt is None:
                    cnt = c2
            if lab is None or cnt is None:
                continue
            line = text[:pos].count("\n") + 1
            yield name, line, classes, lab, cnt


def rules_touching(corpus, classes):
    """Rules whose selector names any class in `classes`, with their bodies."""
    for label, selector, body, line in corpus:
        named = set(CLASS_IN_SELECTOR.findall(selector))
        if named & classes:
            yield label, selector, body, line


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print every section header row and the ramp it is on")
    args = ap.parse_args()

    corpus = [(label, sel, body, line)
              for label, text in sources()
              for sel, body, line in blocks(text)]

    findings, read = [], []

    for page, line, hdr, lab, cnt in header_rows():
        # Every size any rule puts on either half of THIS header.
        sizes = []
        for half, classes in (("label", lab), ("count", cnt)):
            for flabel, sel, body, fline in rules_touching(corpus, classes):
                m = SIZE.search(body)
                if not m:
                    continue
                tok = TOKEN.search(m.group(1))
                sizes.append((half, flabel, sel, m.group(1).strip(),
                              tok.group(1) if tok else None))

        off = [s for s in sizes if s[4] not in RAMP]
        read.append((page, line, sorted(hdr), sizes, bool(off)))
        if not off:
            continue

        rigid = [(f, s) for f, s, b, _ in rules_touching(corpus, cnt) if RIGID.search(b)]
        wraps = [(f, s) for f, s, b, _ in rules_touching(corpus, hdr) if WRAPS.search(b)]

        where = "%s:%d" % (page, line)
        ramped = ", ".join("%s at %s (%s %s)" % (h, size, f, s) for h, f, s, size, _ in off)
        if not rigid:
            findings.append(
                "%s: the header's %s — so the count is sized off the label "
                "ramp — and no rule makes `.%s` rigid. A shrinkable count on a "
                "re-ramped row wraps between the number and the noun it counts. "
                "Declare flex: none on it."
                % (where, ramped, sorted(cnt - {COUNT})[0] if cnt - {COUNT} else COUNT))
        if not wraps:
            findings.append(
                "%s: the header's %s, and no rule lets `.%s` wrap. A rigid count "
                "on a row that cannot wrap squeezes the label under its own "
                "min-content and breaks it mid-word instead. Declare "
                "flex-wrap: wrap on the row beside the count's flex: none."
                % (where, ramped, sorted(hdr - {HEADER})[0] if hdr - {HEADER} else HEADER))

    if args.verbose:
        for page, line, hdr, sizes, off in sorted(read):
            mark = "OFF RAMP" if off else "on ramp "
            print("  %s  %-46s %s" % (mark, "%s:%d" % (page, line), " ".join(hdr)))
            for half, flabel, sel, size, tok in sizes:
                print("             %-6s %-30s %s" % (half, size, sel[:60]))
        print("  %d section header row(s) read" % len(read))

    for f in findings:
        print("check-count-atom: %s" % f, file=sys.stderr)

    if findings:
        print("\n%d finding(s)." % len(findings), file=sys.stderr)
        return 1
    ramped = sum(1 for *_, off in read if off)
    print("OK  %d section header row(s): %d on the label ramp, %d re-ramped and "
          "each with a rigid count on a row that may wrap."
          % (len(read), len(read) - ramped, ramped))
    return 0


if __name__ == "__main__":
    sys.exit(main())
