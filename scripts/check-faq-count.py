#!/usr/bin/env python3
"""The counter above an accordion counts the entries under it.

The one check in this directory written to close a gap another check names in
its own register — so it carries no ordinal of its own. check-section-counts.py
is the nineteenth by CI's sequence and the README numbers a different fifteen;
what matters here is the boundary between the two, not a position in either.
check-section-counts.py holds every
counter on patterns/landing-page.html to what stands beneath it, and its
register carries this entry:

    FAQ followed them on 2026-08-04, to patterns/expertise.html, where the
    questions stand under the page that answers them ... Its counter travelled
    with it unchanged and is still the true one ("6 Fragen", six questions);
    what this register can no longer say is that it is true, because the
    register is this one page.

The register was right that it could no longer say it, and wrong within a month
about the fact. The migrated set on Expertise grew from six questions to eleven
and its counter grew with it; the copy that stayed behind did not. The specimen
on components/accordion.html — the page that teaches this component and links to
Section Header for the rule — shipped `6 Fragen` over four `<details>`, and went
on shipping it for as long as nothing counted.

WHY A SCRIPT AND NOT A READING. Exactly the reason check-section-counts.py
gives for the page it owns: a wrong counter renders as a right one. It is eleven
pixels of mono at the far end of a hairline, it passes every contrast check, it
breaks no layout at any width, and the number it is wrong by is the one thing a
screenshot cannot show you, because the rows it is a count of do not all fit on
the screen at once. It is also the single fact on a FAQ a reader is most likely
to act on before scrolling: six questions is a section you read, thirty is one
you search.

THE BOUNDARY WITH check-section-counts.py, which matters more here than
anywhere, because two scripts asserting one invariant to two standards is the
drift this family exists to stop. That script owns patterns/landing-page.html —
all of it, every counter, by a hand-kept register of what one item's markup
looks like in each of its sections. This one owns one component wherever it
stands, by counting the component's own item class, and it does not read the
landing page at all. If an accordion ever returns there, the register next door
gains an entry and this script keeps skipping the file.

WHAT IT CHECKS, on every .html under design-system/ except patterns/en/ (a
generated edition — every fact in it is kept one directory up) and
patterns/landing-page.html (above):

  pairing    every .cf-accordion has a .cf-section-header__count somewhere
             above it in the document, or it is skipped as uncounted. An
             accordion with no header is a legitimate shape — an FAQ can be
             the whole of a page — and a missing counter is not a wrong one.
  form       the counter is read as a QUANTITY or as a POSITION, and only a
             quantity is a count. The distinction is in the markup and not in
             a list: section-header.html publishes four forms, and the two
             that are positions — "01 / 04" and a bare ordinal — are drawn
             aria-hidden, because a position is furniture for the eye and a
             quantity is information. So: a counter carrying aria-hidden is a
             position and is skipped; one that does not is a quantity and is
             held to the count. patterns/karriere.html's `05` and
             patterns/kontakt.html's `03` are skipped by that rule rather than
             by being named here.
  count      the leading integer of a quantity equals the number of
             `cf-accordion__item` between that accordion and the next one.

The item class is the marker for the same reason the wall's <img> is next door:
it is the thing the number is a count OF. An entry cannot be drawn without it —
components.css hangs the row's own divider on it — so it cannot go the way the
partner wall's `<li class="t-label">` went, where the marker survived a
redesign the count did not.

    python3 scripts/check-faq-count.py       # the rule
    python3 scripts/check-faq-count.py -v    # every accordion found, counted
                                             # or skipped, and why
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = ROOT / "design-system"

# patterns/en/ is generated from the German page beside it and replaces only
# the words; a counter is a number and comes through unchanged. Reading it
# would double every finding and let a fix look like two.
SKIP = {
    BASE / "patterns" / "en",
    BASE / "assets" / "source",
}
# check-section-counts.py owns this file. See THE BOUNDARY above.
SKIP_FILE = BASE / "patterns" / "landing-page.html"

COMMENT = re.compile(r"<!--.*?-->", re.S)

ACCORDION = re.compile(r'class="[^"]*\bcf-accordion\b[^"]*"')
ITEM = re.compile(r'class="[^"]*\bcf-accordion__item\b[^"]*"')
# The counter element, from its opening tag through its text. Kept as one
# match so the aria-hidden that decides the form is read off the same element
# as the number, and not off whatever attribute happens to be nearest.
COUNTER = re.compile(
    r'<(?P<tag>\w+)(?P<attrs>[^>]*\bclass="[^"]*\bcf-section-header__count\b[^"]*"[^>]*)>'
    r'(?P<text>.*?)</(?P=tag)>', re.S)

TAGS = re.compile(r"<[^>]+>")
# A quantity: a leading integer, then anything that is not another number in a
# pair. "4 Fragen", "189 Beiträge", "11 Fragen". A position pair — "01 / 04",
# "1 von 4" — is not a quantity even when it is not marked aria-hidden, and is
# reported as a form finding rather than counted, because a pair above an
# accordion is a counter that has lost track of what it counts.
QUANTITY = re.compile(r"^(\d+)\s*([^\d/]*)$")
PAIR = re.compile(r"^\d+\s*(?:/|von)\s*\d+$")


def pages():
    for path in sorted(BASE.rglob("*.html")):
        if path == SKIP_FILE:
            continue
        if any(skip in path.parents for skip in SKIP):
            continue
        yield path


def text_of(fragment):
    return TAGS.sub("", fragment).replace("&nbsp;", " ").strip()


def audit():
    findings, seen = [], []

    for path in pages():
        rel = path.relative_to(ROOT)
        source = COMMENT.sub("", path.read_text(encoding="utf-8"))

        starts = [m.start() for m in ACCORDION.finditer(source)]
        if not starts:
            continue
        # The span of one accordion is from its own opening to the next one's,
        # or to the end of the document. cf-accordion__item appears nowhere
        # else in the system, so the span needs no closing tag to be exact —
        # and a nesting depth would be a claim about markup this component's
        # own Don't list forbids.
        bounds = list(zip(starts, starts[1:] + [len(source)]))

        for index, (start, end) in enumerate(bounds, 1):
            items = len(ITEM.findall(source[start:end]))
            line = source.count("\n", 0, start) + 1
            where = "%s:%d  accordion %d/%d" % (rel, line, index, len(bounds))

            above = [m for m in COUNTER.finditer(source) if m.start() < start]
            if not above:
                seen.append((where, items, "no counter above it — uncounted, "
                                           "which is a legitimate shape"))
                continue

            counter = above[-1]
            label = text_of(counter.group("text"))
            if "aria-hidden" in counter.group("attrs"):
                seen.append((where, items,
                             'counter "%s" is aria-hidden — a position, not a count' % label))
                continue

            if PAIR.match(label):
                findings.append((where, items,
                                 'counter "%s" is a position pair standing over %d entr%s, '
                                 "and is not marked aria-hidden. A pair is furniture for the "
                                 "eye; a counter a reader is told about has to count."
                                 % (label, items, "y" if items == 1 else "ies")))
                continue

            quantity = QUANTITY.match(label)
            if not quantity:
                findings.append((where, items,
                                 'counter "%s" is neither a quantity nor a position. '
                                 "components/section-header.html publishes the four forms."
                                 % label))
                continue

            claimed = int(quantity.group(1))
            unit = quantity.group(2).strip()
            if claimed != items:
                findings.append((where, items,
                                 'counter says "%s" over %d entr%s. The number above an '
                                 "accordion is a count of the rows under it."
                                 % (label, items, "y" if items == 1 else "ies")))
            else:
                seen.append((where, items,
                             'counter "%s" counts them%s' % (label, "" if unit else " (bare)")))

    return findings, seen


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every accordion found, not only the failures")
    args = ap.parse_args()

    findings, seen = audit()

    if args.verbose:
        for where, items, note in seen:
            print("  %-58s %3d  %s" % (where[-58:], items, note))
        print()

    if findings:
        for where, items, why in findings:
            print("%s\n    %s" % (where, why), file=sys.stderr)
        print("\n%d counter%s that does not count what stands under it. A wrong "
              "counter renders exactly like a right one."
              % (len(findings), "" if len(findings) == 1 else "s"), file=sys.stderr)
        return 1

    counted = sum(1 for _, _, note in seen if note.startswith("counter") and "counts them" in note)
    print("faq counts: %d accordion(s) read, %d counted by a quantity above them, "
          "%d standing under a position or nothing."
          % (len(seen), counted, len(seen) - counted))
    return 0


if __name__ == "__main__":
    sys.exit(main())
