#!/usr/bin/env python3
"""Every counter in the landing page's section headers counts what is under it.

The nineteenth check, and the one whose subject is a number a reader can
verify by looking. components/section-header.html calls the header "the
smallest and most important element in the system: it opens every section and
simultaneously says where you are in the document", and publishes four forms
for the counter on its right — a position (01 / 04, decorative, aria-hidden),
a quantity (189 Beiträge), a bare count when the unit follows from the label
(10), and an action. Nothing checked that any of them was true.

Four of the landing page's five were not:

  Was wir machen   01 / 04       a position, frozen, beside a LIVE one
  Partner & Tech.  03 / 06       seven marks stand under it
  Blog             189 Beiträge  eighteen cards stand under it
  Das Team         10            four faces stand under it
  FAQ              6 Fragen      six questions — the only true one

The two position pairs were not section positions either: the page numbers
its own sections 01 to 07 in its source comments, and the two counters that
claim a position claim 01 of 04 and 03 of 06 while sitting at 03 and 04 of
07. And the first of them sits above .cf-pin__index, whose four marks light
one at a time off the track's timeline — the header's frozen 01 is wrong for
three of the four quarters the reader scrubs through. That is the drift
section-header.html's own "In context" note describes for Unsere Werte on
Über uns, and the landing page is where it shipped.

A wrong counter renders exactly like a right one. It is 11 px of mono at the
far end of a hairline; no screenshot, no contrast check and no HTML validator
has an opinion about whether 10 is the number of faces beside it. The only
thing that can hold it is something that counts.

WHAT IT CHECKS. For design-system/patterns/landing-page.html, comments
masked: every .cf-section-header__count is registered below; each registered
counter's leading integer equals the number of its section's own items,
counted from the heading's id to that section's close; the counter's shape is
a count — "N", "N Einheit", or the subset form "N von M" that news.html and
blog-artikel.html already ship — and never a bare position pair, which on
this page has no sequence to be a position in; M is at least N; and none of
them is aria-hidden, because a counter that carries information stays in the
accessibility tree and all five of these now do.

The register is the landing page alone: this is the page the counters were
measured on. patterns/ueber-uns.html carried the same fault (Das Team, 10,
over six faces); it is fixed there by removing the counter rather than by
correcting it to 6 — that page states no headcount at all, on the site
owner's instruction, and the note beside the header records why.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-section-counts.py       # check, exit 1 on a finding
    python3 scripts/check-section-counts.py -v    # list every counter audited
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = ROOT / "design-system" / "patterns" / "landing-page.html"

COMMENT = re.compile(r"<!--.*?-->", re.S)

# The counter forms the system publishes as counts. A position pair — "01 / 04"
# — is deliberately not among them: on this page there is no sequence of four
# or of six for it to be a position in, and the one section that does carry a
# position carries a live one in .cf-pin__index.
COUNT = re.compile(r"^(\d+)(?:\s+von\s+(\d+))?(?:\s+([^\d/]+))?$")

# heading id → (what one item's markup starts with, what to call it)
#
# Each marker is the opening of the section's own repeating element, matched as
# a literal so it cannot drift into a modifier or a child: the process step and
# not the lectern that shares .cf-process, the blog anchor and not its title
# span, the <li> of a logo mark and not the counter above it.
#
# The logo mark's marker used to be a bare "<span>", because the wall held its
# seven marks as seven bare text nodes in a <div>. It is a <ul role="list"> now
# — seven marks under a header that announces seven should be seven list items,
# and a reader who cannot see the wall should be told how many there are — so
# the marker is the item, the same shape the team strip's entry already had,
# and it no longer rests on a tag that carries no class at all.
#
# AND IT IS THE <img>, NOT THE <li>, NOW THAT THE MARKS ARE ARTWORK. It read
# '<li class="t-label">' — the stand-in TEXT's own class — so the day the
# wordmark files landed and the items stopped being labels, the count went to
# zero under a header still announcing seven. That is the marker doing its job:
# it is a literal on purpose, and a literal that no longer matches is a finding
# rather than a silent recount. Pointing it at the <li> alone would have been
# the cheap fix and the wrong one: '<li>' is the emptiest possible marker, and
# the wall is a component whose items have been three different shapes in three
# releases. The <img> is the thing this section is a count OF, it is what the
# header's 7 promises a reader, and — unlike the class the items used to carry
# — it cannot be present without a mark being drawn.
REGISTER = {
    # AND THEY GOT IT BACK. The steps lost cf-pin__step when the pinned chain
    # moved to prototypes/statement-to-process.html (2026-07-28) and the exact
    # form with the closing quote was what kept the lectern plate out of the
    # count. The chain came back with the five acts (2026-07-29), so the four
    # cards are pinned steps again — and cf-pin__step is a better marker than
    # the bare form was, because the plate has never carried it: it is
    # `cf-process lp-proc-plate`, which is how it stays out of the count
    # without anyone relying on a closing quote to do it.
    # KEYED ON THE HEADING'S id, which is `prozess-titel` and not `prozess`.
    # The two were the same string until act 3's address had to leave the
    # heading: .sp-head sits inside .sp-stage, which is sticky from 64rem up,
    # and a fragment aimed into a stuck box lands where the stage puts it
    # rather than where scroll-margin-top asks. `prozess` is now act 3's
    # <section> — the in-flow element the jump addresses — and the heading
    # keeps the name. section_body() below still finds the section through
    # aria-labelledby, so the pairing is unchanged; only the key moved.
    # → scripts/check-sticky-address.py
    "prozess-titel": ('<article class="cf-process cf-pin__step"', "process step"),
    "partner": ('<img src="../assets/img/partner/', "logo mark"),
    # The blog strip and the team grid left the landing page when the five acts
    # arrived (2026-07-29): act 4 IS the team, and the page the review asked for
    # is hero, acts, partners, FAQ, footer. Both components still exist and are
    # still published; they are simply not sections of this page any more.
    # FAQ followed them on 2026-08-04, to patterns/expertise.html, where the
    # questions stand under the page that answers them — the review's "FAQ auch
    # zu Expertise". Its counter travelled with it unchanged and is still the
    # true one ("6 Fragen", six questions); what this register can no longer say
    # is that it is true, because the register is this one page. The rule the
    # loop below enforces — a registered id with no header on the page is a
    # fork — is why the entry goes rather than stays.
}

HEADER = re.compile(
    # The class list, not the class. Act 3's header carries .sp-head__title
    # alongside the label so the rule it lands on can draw with the act; an
    # exact-match attribute selector stopped seeing it the moment it did.
    r'<h2 class="cf-section-header__label[^"]*" id="(?P<id>[^"]+)">.*?'
    r'<span class="cf-section-header__count(?P<cls>[^"]*)"(?P<attrs>[^>]*)>'
    r"(?P<text>[^<]*)</span>",
    re.S,
)


def section_body(text, start, hid=None):
    """The section a header counts for: from its heading to that section's close,
    or from the section that CLAIMS the heading by aria-labelledby.

    A HEADER AND THE THINGS IT COUNTS CAN BE IN TWO SECTIONS. They were in one
    for as long as a section opened with its own <h2>, and the five acts broke
    that: "Was wir machen" is the rule act 2's root LANDS on, so it lives inside
    that act's stage, while the four cards it counts are the section after it.
    The heading is still the section's heading — the cards' <section> says so
    with aria-labelledby — but reading forward from the <h2> stops at the act's
    own </section> and counts nothing.

    So a header that some section claims is counted in the claiming section, and
    a header that opens its own is counted where it stands. Both are the same
    question — how many of the thing is under this heading — asked of the markup
    that actually answers it.
    """
    if hid:
        m = re.search(r'<section\b[^>]*aria-labelledby\s*=\s*"%s"[^>]*>' % re.escape(hid), text)
        if m and not (m.start() < start < text.find("</section>", m.end())):
            start = m.end()
    end = text.find("</section>", start)
    return text[start:end if end != -1 else len(text)]


def audit(verbose):
    raw = PAGE.read_text(encoding="utf-8")
    text = COMMENT.sub("", raw)
    rel = PAGE.relative_to(ROOT)
    findings = []
    seen = set()

    for m in HEADER.finditer(text):
        hid = m.group("id")
        counter = m.group("text").strip()
        line = text[: m.start()].count("\n") + 1
        seen.add(hid)

        if hid not in REGISTER:
            findings.append(
                '%s:%d  "%s" over #%s is not in the register — a section that '
                "ships a number ships it unchecked." % (rel, line, counter, hid))
            continue

        marker, noun = REGISTER[hid]
        items = section_body(text, m.end(), hid).count(marker)

        if "aria-hidden" in m.group("attrs"):
            findings.append(
                '%s:%d  "%s" over #%s is aria-hidden, and it is a quantity — '
                "section-header.html: a counter that carries information stays "
                "in the accessibility tree." % (rel, line, counter, hid))

        shape = COUNT.match(counter)
        if not shape:
            findings.append(
                '%s:%d  "%s" over #%s is not a count. This page\'s counters are '
                '"N", "N Einheit" or "N von M"; a position pair has no sequence '
                "here to be a position in." % (rel, line, counter, hid))
            continue

        shown = int(shape.group(1))
        whole = int(shape.group(2)) if shape.group(2) else None

        if shown != items:
            findings.append(
                '%s:%d  "%s" over #%s says %d, and the section holds %d %s%s.'
                % (rel, line, counter, hid, shown, items, noun,
                   "" if items == 1 else "s"))
        if whole is not None and whole < shown:
            findings.append(
                '%s:%d  "%s" over #%s shows more than the whole it is part of.'
                % (rel, line, counter, hid))

        if verbose:
            print("  %-9s %-14s %d %s%s"
                  % (hid, counter, items, noun, "" if items == 1 else "s"))

    for hid in REGISTER:
        if hid not in seen:
            findings.append(
                "%s  #%s is registered and has no section header on the page — "
                "the register and the page have forked." % (rel, hid))

    return findings, len(seen)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every counter audited and what it counts")
    args = ap.parse_args()

    findings, counters = audit(args.verbose)

    if findings:
        print("\n".join(findings), file=sys.stderr)
        print("\n%d finding%s against the section header's own counter forms "
              "(components/section-header.html)."
              % (len(findings), "" if len(findings) == 1 else "s"),
              file=sys.stderr)
        return 1

    print("section counts: %d counter%s on the landing page, every one equal to "
          "what stands under it, every one announced." % (counters, "" if counters == 1 else "s"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
