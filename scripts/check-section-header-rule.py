#!/usr/bin/env python3
"""--flush is a promise about the next element, and nothing kept it.

.cf-section-header draws the hairline that opens every section on every
designed page. Its one modifier, --flush, sets `border-bottom: 0` and
`margin-bottom: 0` on the understanding stated in components.css: "the content
below is a ruled container (process card, accordion, blog grid) and ITS top
border is the rule. The header gives up its own border rather than drawing a
second hairline 1 px away."

Written above a container that does draw one, that is exactly right and saves a
doubled line. Written above anything else it does not move the rule, it DELETES
it — and what ships is a mono label and a counter floating in space with no
hairline under them and no clearance either, because --flush drops the gap too.

WHY A SCRIPT AND NOT A READING, which is the question every check in this
directory has to answer. Three reasons, and the third is the one that decided
it:

  1. The failure renders as a smaller version of the correct thing rather than
     as an error. There is no red box, no overlap, no overflow; the section
     header device is simply missing its device. Every contrast, link, a11y and
     layout check in this directory passes a section drawn that way, because
     nothing about it is wrong except that a line the brand draws everywhere
     else is absent.

  2. It is a two-file fact. The modifier is in the markup and the border it is
     betting on is in the stylesheet, so neither file read alone says anything
     is wrong. components.css was in fact the more confident of the two: the
     comment over .cf-contact read "No top border. The section header above it
     draws that hairline; giving the list one of its own is what --flush exists
     to avoid" — whose first clause is true of a plain header and whose second
     names the modifier that makes the first false. patterns/impressum.html read
     the second clause and wrote --flush. Two correct-sounding halves, one
     missing rule.

  3. The pages it broke are the ones nobody re-opens. Five of the eight sites
     found were karriere-stelle.html's specimen (which the four generated
     stelle-*.html pages inherit verbatim) and the two zero states,
     karriere-leer.html and suche-leer.html — which is the sharpest form of the
     defect in this system: on karriere.html the same header IS flush and IS
     right, because .cf-vacancies brings the edge; the empty state swaps that
     register for .cf-error--inline, which brings none. So the rule was present
     in the state anyone looks at and absent in the state that ships the day
     the register empties.

  It was also visible one section apart and went unseen for that reason:
  karriere-stelle.html drew 04 with no rule and 05 with one, and
  impressum.html drew 03 with no rule between an 01 and an 02 that both draw it.

THE SET IS DERIVED, NOT LISTED, the same standing check-glass-budget.py takes
for what counts as glass and check-gradient-family.py takes for its waypoint. A
container earns the right to stand under a flush header by declaring a top
border of stroke ink in a shipping stylesheet — `border-top: var(--stroke-N)
solid var(--border-*)` — so a sixth ruled register qualifies by existing rather
than by somebody remembering to add it here. Six classes qualify today
(.cf-accordion, .cf-results, .cf-vacancies, .cf-events, .cf-blog-grid,
.cf-table); a list would have gone stale the first time a seventh was written.

Selectors inside @media forced-colors and the other fallback blocks are read
too, and deliberately: a border those blocks restore is a border the reader
sees, and this check is about whether a hairline exists at that edge, never
about which ink draws it.

WHAT IT CHECKS, on every .html under design-system/ except patterns/en/ (a
generated edition; markup comes through byte for byte, so every finding there
would be a duplicate of one found here) and assets/source/ (the designer's own
material):

  pairing    every .cf-section-header--flush is followed, inside its own
             parent, by an element carrying at least one class that draws a top
             border. A flush header with no element after it at all is the same
             finding by a shorter route — it has handed its rule to nothing.

The inverse is NOT checked, and the boundary matters. A plain header standing
over a ruled container draws two hairlines a few pixels apart, which is a
drawing decision — .cf-culture and the news archive each have a reading — and
not the disappearance of one. This script owns the direction where the line
goes missing.

    python3 scripts/check-section-header-rule.py     # the rule
    python3 scripts/check-section-header-rule.py -v  # every flush header, the
                                                     # element under it, and
                                                     # what draws the edge
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = ROOT / "design-system"
CSS = BASE / "assets" / "css"

# patterns/en/ is generated by build-i18n.py, which replaces words and nothing
# else — classes come through unchanged, so a finding there is this finding
# twice. assets/source/ is the designer's material and is not markup we own.
SKIP = {BASE / "patterns" / "en", BASE / "assets" / "source"}

SHEETS = ("tokens.css", "base.css", "components.css", "acts.css", "docs.css")

COMMENT = re.compile(r"<!--.*?-->", re.S)
CSS_COMMENT = re.compile(r"/\*.*?\*/", re.S)

# A rule that paints a hairline along its own top edge. The ink is a token by
# the system's own convention, and forced-colours restores it as CanvasText —
# both count, because both are a line the reader sees.
# border-top, but also the shorthands that contain it: `border` and
# `border-block` both paint the top edge, and .cf-process — the process card,
# the first component this system drew — states its contour as `border`. Reading
# only the longhand credited it with no edge and reported the one flush header
# in the system that has always been right.
RULED = re.compile(
    r"(?P<sel>[^{}]+)\{(?P<body>[^{}]*\bborder(?:-top|-block)?:\s*var\(--stroke-[^;]*;[^{}]*)\}")
COMBINATOR = re.compile(r"\s*[>+~]\s*|\s+")
# The last compound of a selector, and only when it is made of classes. That
# distinction is the whole of the derivation: ".cf-prose figure" draws its
# border on a <figure> and says nothing about .cf-prose, and reading the last
# CLASS rather than the last COMPOUND credited the wrapper with a line only its
# figures have. .cf-prose is running copy and draws no top edge at all — which
# is exactly one of the eight sites this script was written to find.
COMPOUND = re.compile(
    r"^(?P<classes>(?:\.[A-Za-z0-9_-]+)+)(?::[a-zA-Z-]+(?:\([^()]*\))?)*$")
CLASS_IN_SEL = re.compile(r"\.([A-Za-z0-9_-]+)")

FLUSH = re.compile(r'<div\b[^>]*\bclass="[^"]*\bcf-section-header--flush\b[^"]*"[^>]*>')
TAG = re.compile(r"<(?P<close>/?)(?P<name>[a-zA-Z][\w-]*)(?P<attrs>[^>]*?)(?P<self>/?)>")
CLASS_ATTR = re.compile(r'\bclass="([^"]*)"')

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}


def ruled_classes():
    """Every class set whose rule declares a top border of stroke ink.

    Returned as {frozenset(classes): stylesheet}. A set rather than a name
    because a compound states a conjunction: an element draws the rule only if
    it carries all of them.
    """
    found = {}
    for name in SHEETS:
        path = CSS / name
        if not path.exists():
            continue
        source = CSS_COMMENT.sub("", path.read_text(encoding="utf-8"))
        for match in RULED.finditer(source):
            for one in match.group("sel").split(","):
                one = one.strip()
                if not one or one.startswith("@") or "::" in one:
                    continue
                # :is()/:where() hold selector lists of their own; the border
                # they carry is real but which element takes it is not a fact
                # this reading settles, so they are named rather than guessed.
                if ":is(" in one or ":where(" in one or ":not(" in one:
                    continue
                last = COMBINATOR.split(one)[-1]
                compound = COMPOUND.match(last)
                if not compound:
                    continue
                classes = frozenset(CLASS_IN_SEL.findall(compound.group("classes")))
                found.setdefault(classes, name)
    return found


def next_element_after(source, start):
    """The first element opened after `start` that is a sibling of the div
    opened there — that is, the next tag once that div has closed."""
    depth = 0
    pos = start
    while True:
        match = TAG.search(source, pos)
        if not match:
            return None
        pos = match.end()
        name = match.group("name").lower()
        if name in VOID or match.group("self"):
            if depth == 0:
                continue
            continue
        if match.group("close"):
            depth -= 1
            if depth <= 0:
                # The flush div has closed. The next opening tag is its sibling
                # — unless the parent closes first, in which case there is none.
                nxt = TAG.search(source, pos)
                if not nxt or nxt.group("close"):
                    return None
                return nxt
        else:
            depth += 1


# How far down to follow first children. A container's own top edge is also the
# top edge of its first child, and of that child's first child: .subdivide wraps
# .cf-blog-grid, which is what draws. Four is what the deepest wrapper in the
# system needs and is not a number to grow casually — past it, "the element at
# that edge" stops being a phrase about one box.
EDGE_DEPTH = 4


def edge_chain(source, match):
    """The element opened at `match` and the first-child chain under it — every
    box whose top edge coincides with that element's own."""
    pos, current = match.end(), match
    for _ in range(EDGE_DEPTH):
        names = CLASS_ATTR.search(current.group("attrs"))
        yield current, names.group(1).split() if names else []
        if current.group("name").lower() in VOID or current.group("self"):
            return
        child = TAG.search(source, pos)
        if not child or child.group("close"):
            return
        pos, current = child.end(), child


def pages():
    for path in sorted(BASE.rglob("*.html")):
        if any(skip in path.parents for skip in SKIP):
            continue
        yield path


def audit():
    ruled = ruled_classes()
    findings, seen = [], []

    for path in pages():
        rel = path.relative_to(ROOT)
        source = COMMENT.sub("", path.read_text(encoding="utf-8"))

        for match in FLUSH.finditer(source):
            line = source.count("\n", 0, match.start()) + 1
            where = "%s:%d" % (rel, line)
            nxt = next_element_after(source, match.start())
            if nxt is None:
                findings.append((where, None,
                                 "--flush with no element after it inside its parent. "
                                 "The header has given its hairline to nothing."))
                continue
            label, drawn = None, None
            for element, classes in edge_chain(source, nxt):
                carried = set(classes)
                if label is None:
                    label = ".".join(classes) or "<%s>" % element.group("name")
                for wanted, sheet in ruled.items():
                    if wanted <= carried:
                        drawn = (".".join(sorted(wanted)), sheet)
                        break
                if drawn:
                    break
            if drawn:
                seen.append((where, label, ".%s draws it (%s)" % drawn))
            else:
                findings.append((where, label,
                                 "--flush over %s, which draws no top border and "
                                 "has no first child that does. The section opens "
                                 "on no rule at all." % label))

    return findings, seen, ruled


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every flush header, not only the failures")
    args = ap.parse_args()

    findings, seen, ruled = audit()

    if args.verbose:
        print("  ruled containers, derived from %s:" % ", ".join(SHEETS))
        for classes in sorted(ruled, key=lambda c: sorted(c)):
            print("    %-34s %s"
                  % ("".join("." + c for c in sorted(classes)), ruled[classes]))
        print()
        for where, label, note in seen:
            print("  %-52s %-24s %s" % (where[-52:], (label or "")[:24], note))
        print()

    if findings:
        for where, label, why in findings:
            print("%s\n    %s" % (where, why), file=sys.stderr)
        print("\n%d flush section header%s standing over nothing that draws the "
              "rule it gave up. A section drawn that way renders as a label with "
              "no hairline, which is the device minus the device."
              % (len(findings), "" if len(findings) == 1 else "s"), file=sys.stderr)
        return 1

    print("section header rule: %d flush header(s), each under one of %d ruled "
          "containers derived from the shipping stylesheets."
          % (len(seen), len(ruled)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
