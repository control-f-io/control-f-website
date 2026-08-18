#!/usr/bin/env python3
"""The number a route claims for its register equals the register under it.

Two routes on this site open by answering "how many?" before anything else:
Suche says "6 Treffer für „Telemetrie"" and Karriere says "4 offene Stellen",
each in the page header's meta line, before the list the number is about. The
invariant is stated twice in prose and was enforced nowhere: karriere.html's
own source comment says "Die Zahl in der Meta-Zeile ist die Länge des
Registers weiter unten", and components/vacancy.html's Before-launch note says
"The count and the register come from one list". In production both do come
from one query. In this repository they are two hand-typed places in one file
— and since the empty states shipped, four files, each carrying a number
(0, 0, 4, 6) about a list in another part of the page.

A wrong register claim renders exactly like a right one. Add a fifth vacancy
and the header still says four; delete a search result and the title, the
meta line and the section counter all still say six, in three different
places a single edit does not reach. check-section-counts.py exists for
precisely this fault class and holds the landing page alone, by its own
scope note: "the register is the landing page alone: this is the page the
counters were measured on." The route pages' numbers had no gate.

The empty states add a second clause. A register at zero is not allowed to
render as nothing — suche-leer.html and karriere-leer.html exist to draw
that state as the inline block from components/error-state.html, a 200 with
a next step rather than a heading over a void. So zero and the block imply
each other: a page claiming 0 must show the block, and a page claiming a
filled register must not also show it. Either drift — the block deleted
from an empty page, or an empty page's claim bumped without content —
renders as a page that looks finished and answers wrong.

WHAT IT CHECKS. For the four register routes, comments, <pre>, <code>,
<textarea> AND <template> masked:

<template> IS MASKED FOR THE SAME REASON <pre> IS, and it was added when the
search page grew one. Its content is inert — not in the document, not
rendered, not focusable, not announced — until a script clones it, so a
.cf-error--inline sitting in a template is not the empty state being drawn,
it is the empty state being kept ready. patterns/suche.html now carries two of
them, for the zero-results answer and for an index that never arrived, and
unmasked they made the page look like a register claiming six results while
also rendering the empty block: STATE's exact finding, on a page where both
halves are correct.

  CLAIM   the page-header meta line carries exactly one "N Treffer" /
          "N offene Stellen" span, and N equals the count of register items
          (.cf-result / .cf-vacancy) on the page.
  TITLE   on the Suche pages, where the <title> is the answer, its leading
          "N Treffer" equals the same count.
  COUNTER on the Suche pages, the Treffer section-header counter — the one
          counter on these pages that is information rather than an
          aria-hidden position — equals the same count.
  STATE   the inline empty block (.cf-error--inline) is present exactly when
          the count is zero.

The scope is the four route files alone, deliberately: the landing page's
counters belong to check-section-counts.py, news.html's "189 Beiträge"
counts an archive the page shows one page of (a subset claim, not a register
length), and the component galleries demonstrate fragments out of context,
which is what a gallery is for.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-register-count.py       # check, exit 1 on a finding
    python3 scripts/check-register-count.py -v    # list every claim audited
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PATTERNS = ROOT / "design-system" / "patterns"

# Regions whose contents are documentation, not markup the browser acts on.
MASK = re.compile(
    r"<!--.*?-->|<pre\b.*?</pre>|<code\b.*?</code>|<textarea\b.*?</textarea>"
    r"|<template\b.*?</template>",
    re.S | re.I,
)

# file → (register item class, the claim's unit, whether the <title> and the
# section counter also state the number). The unit string is matched exactly:
# "4 offene Stellen" is a register length, "189 Beiträge" on news.html is not.
PAGES = {
    "suche.html": ("cf-result", "Treffer", True),
    "suche-leer.html": ("cf-result", "Treffer", True),
    "karriere.html": ("cf-vacancy", "offene Stellen", False),
    "karriere-leer.html": ("cf-vacancy", "offene Stellen", False),
}


def class_token(name):
    """Match an element whose class attribute carries `name` as a whole token."""
    return re.compile(r'class="(?:[^"]*\s)?%s(?:\s[^"]*)?"' % re.escape(name))


def audit(name, text, verbose):
    item_class, unit, titled = PAGES[name]
    text = MASK.sub(" ", text)
    findings = []

    items = len(class_token(item_class).findall(text))

    meta = re.search(
        r'<p class="cf-page-header__meta">(.*?)</p>', text, re.S)
    if not meta:
        findings.append("%s: no .cf-page-header__meta line to carry the claim" % name)
        return findings
    # The span may carry attributes and on suche.html it carries two: the hook
    # cf-search.js rewrites the claim through, and role="status", which is what
    # announces the new number to a reader who never left the page. Neither
    # changes what the span says, which is the only thing this rule is about.
    claims = re.findall(r"<span[^>]*>(\d+)\s+%s\b[^<]*</span>" % re.escape(unit),
                        meta.group(1))
    if len(claims) != 1:
        findings.append(
            '%s: expected exactly one "N %s" span in the header meta, found %d'
            % (name, unit, len(claims)))
        return findings
    claimed = int(claims[0])

    if claimed != items:
        findings.append(
            "%s: the header claims %d %s and the page renders %d .%s"
            % (name, claimed, unit, items, item_class))
    if verbose:
        print("  %-22s claim %d, %d ×.%s" % (name, claimed, items, item_class))

    if titled:
        m = re.search(r"<title>(\d+) Treffer", text)
        if not m:
            findings.append('%s: <title> does not open with "N Treffer"' % name)
        elif int(m.group(1)) != items:
            findings.append(
                "%s: <title> says %s Treffer over %d results" % (name, m.group(1), items))
        counters = [
            c for c in re.finditer(
                r'<span class="cf-section-header__count"([^>]*)>(\d+)</span>', text)
            if "aria-hidden" not in c.group(1)
        ]
        if len(counters) != 1:
            findings.append(
                "%s: expected one informational section counter, found %d"
                % (name, len(counters)))
        elif int(counters[0].group(2)) != items:
            findings.append(
                "%s: the Treffer counter says %s over %d results"
                % (name, counters[0].group(2), items))

    empty_block = bool(class_token("cf-error--inline").search(text))
    if claimed == 0 and not empty_block:
        findings.append(
            "%s: a register at zero must draw the inline empty block "
            "(components/error-state.html), not nothing" % name)
    if claimed > 0 and empty_block:
        findings.append(
            "%s: claims a filled register and also renders the inline empty "
            "block — the two states exclude each other" % name)

    return findings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    findings = []
    for name in sorted(PAGES):
        path = PATTERNS / name
        if not path.exists():
            findings.append("design-system/patterns/%s does not exist" % name)
            continue
        findings += audit(name, path.read_text(encoding="utf-8"), args.verbose)

    for f in findings:
        print("REGISTER   %s" % f)
    if findings:
        return 1
    print("register counts OK — %d routes, every claim equals its register" % len(PAGES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
