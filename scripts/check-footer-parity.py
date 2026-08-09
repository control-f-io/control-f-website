#!/usr/bin/env python3
"""Every pattern page's footer is the component's footer, drift-for-drift.

There is no build step and no include: fourteen pattern pages each carry a
hand-typed copy of the footer, and components/footer.html carries a fifteenth
as the demo. Fifteen copies of one block, edited hourly by twelve routines, is
the exact surface this directory keeps finding forks on — and the footer had
no gate, because every existing check reads what a footer SAYS (its links, its
contrast, its consent button) and none reads whether the fifteen copies are
still the same block.

They were not. Diffed against the component, the copies varied on six axes.
Four are lawful and each has a rule already written down somewhere:

  ARIA-CURRENT   moves per page, naturally. The convention in the tree is
                 exact: a link gets aria-current="page" when its href IS the
                 page, and aria-current="true" when the page is a child of
                 the section the link names (blog-artikel under News,
                 karriere-stelle under Karriere) — WAI-ARIA's own distinction,
                 kept correctly on all fourteen pages.

  THE CONTACT    kontakt.html documents the rule in place: "Der Footer trägt
  PAGES' CTA     auf jeder anderen Seite den CTA 'Jetzt Projekt starten' mit
                 dem Link hierher. Auf dieser Seite wäre das ein Link auf
                 sich selbst." kontakt-danke.html argues the same swap for the
                 page after the form. Two contact pages, two variants, and the
                 rule's own wording — "auf jeder anderen Seite" — is the fence
                 around them.

                 It used to be one variant for both, and it was a phone
                 number: "die andere Hälfte des Angebots: anrufen statt
                 schreiben". That half is gone — the form is the only way to
                 reach the company now — so the two pages no longer share a
                 CTA and neither offers a channel. Each points at what its own
                 reader can use next: Expertise before writing, Über uns after
                 sending. They are listed per page below, because two pages
                 with two different buttons is exactly the shape this file
                 exists to keep honest.

  --DETACHED     kontakt.html again, same comment: "Der Modifier ist für
                 Seiten, deren letzte Sektion .section--flush ist." Checked
                 against all fourteen pages the rule holds exactly: two flush
                 last sections, two detached footers, zero exceptions.

  AN ID          the landing page's footer is #abschluss, the act rail's last
                 anchor. An anchor is not a fork.

The other two axes were forks, and both photograph as working pages:

  karriere.html carried cf-btn--outline on its "Kontakt aufnehmen" button
  where the component and the other ten regular footers carry
  cf-btn--primary — directly under its own comment claiming the footer
  arrives "unverändert". The site's one conversion CTA, quiet on exactly one
  page, plausibly a copy taken from a contact page with the text put back
  and the modifier forgotten.

  expertise.html carried the contact pages' whole tel variant — title,
  number, outline — on a page that is not a contact page, with no comment,
  in a tree where every deliberate deviation argues itself in place. The
  rule at kontakt.html says every other page links the reader to kontakt;
  expertise was the one page that did not.

WHAT IT CHECKS. For components/footer.html's demo and every
design-system/patterns/*.html, comments stripped:

  1. VARIANT   the CTA is the regular form (Jetzt Projekt starten! /
               cf-btn--primary / kontakt.html / Kontakt aufnehmen) on every
               page except the two contact pages, each of which must carry
               its own, named in CTA_CONTACT. A third form anywhere is a
               finding either way.
  2. CURRENT   at most one footer link carries aria-current; it is "page"
               iff the href is the page itself, "true" iff SECTION_OF maps
               the page to that href, and required whenever either rule
               fires — a page in the links list may not leave itself
               unmarked.
  3. DETACHED  cf-footer--detached iff the last <section> inside <main>
               carries section--flush.
  4. PARITY    after normalising the four lawful axes away — aria-current
               removed, a contact page's own CTA rewritten to the regular
               one on the pages allowed to carry it, --detached and the
               footer's id dropped, whitespace collapsed, the docs page's
               ../patterns/ hrefs relativised — every copy is
               CHARACTER-IDENTICAL to the component's. Whatever the next
               fork is, it fails here without this file having to predict it.
  5. NO CHANNEL no footer carries a tel: or mailto: link. The contact form
               is the only way to reach the company, and the footer is the
               one block that appears on all sixteen pages — an address put
               back here would reopen that door everywhere at once, which is
               how it came to be everywhere in the first place. The address
               the law requires is in the Impressum, which every footer
               links to.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-footer-parity.py       # check, exit 1 on a finding
    python3 scripts/check-footer-parity.py -v    # list every footer audited
"""

import argparse
import difflib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PATTERNS = ROOT / "design-system" / "patterns"
COMPONENT = ROOT / "design-system" / "components" / "footer.html"

COMMENT = re.compile(r"<!--.*?-->", re.S)
FOOTER = re.compile(r"<footer\b[^>]*>.*?</footer>", re.S)

# The pages whose footer CTA may not link to kontakt.html, because on them it
# would be a link to itself (kontakt) or to the form the reader has just sent
# (kontakt-danke), are the keys of CTA_CONTACT below — the same list as the
# CTAs themselves, so the set and the markup cannot fall out of step. The rule
# and its fence are kontakt.html's own comment: the variant stands "auf dieser
# Seite", the regular CTA "auf jeder anderen Seite".

# Pages that are children of a section a footer link names, and therefore
# mark that link aria-current="true" rather than "page".
SECTION_OF = {
    "blog-artikel.html": "news.html",
    "karriere-stelle.html": "karriere.html",
    # Not a child page but the same route in its empty state. In production
    # the reader at an empty /karriere is *on* the page the link names, but
    # in this file-per-state tree the canonical file is a different document,
    # and check-links.py rightly reads aria-current="page" on a link that
    # resolves elsewhere as a lie. The ancestor marker is the one value both
    # models agree on — the same treatment karriere-stelle.html gets.
    "karriere-leer.html": "karriere.html",
    # The same empty-state argument, for the search route: suche-leer.html is
    # /suche with nothing found, and its footer's Suche link resolves to the
    # canonical file.
    "suche-leer.html": "suche.html",
    # And the filtered-state argument, for the news route: news-thema.html is
    # /news with a topic in the query string, and its footer's News link
    # resolves to the canonical file.
    "news-thema.html": "news.html",
}


def section_of(name):
    """Which footer link a page marks as its section, or nothing.

    Every published article is a child of News, and there is one per post:
    scripts/build-articles.py splices content/news/ into blog-artikel.html and
    writes beitrag-<name>.html. A table with a line per post would be a table
    edited by whoever writes one, which is the cost the generator exists to
    remove — and the specimen's own line above is what these pages inherit,
    because the marker is in the footer they are built from.
    """
    if name.startswith("beitrag-"):
        return "news.html"
    if name.startswith("stelle-"):
        return "karriere.html"
    return SECTION_OF.get(name)

CTA_REGULAR = (
    '<p class="cf-footer__title text-foil">Jetzt Projekt starten!</p>'
    '<a class="cf-btn cf-btn--primary cf-btn--xwide" href="kontakt.html">'
    " Kontakt aufnehmen "
    '<svg class="cf-arrow" aria-hidden="true"><use href="#cf-arrow"></use></svg></a>'
)
# One per contact page, because the two pages answer different questions. The
# regular CTA would be a self-link on kontakt and a link back to the form the
# reader just sent on kontakt-danke; what replaces it is not a second channel
# but the next thing worth reading.
CTA_CONTACT = {
    "kontakt.html": (
        '<p class="cf-footer__title text-foil">Erst sehen, was wir bauen?</p>'
        '<a class="cf-btn cf-btn--outline cf-btn--xwide" href="expertise.html">'
        " Expertise "
        '<svg class="cf-arrow" aria-hidden="true"><use href="#cf-arrow"></use></svg></a>'
    ),
    "kontakt-danke.html": (
        '<p class="cf-footer__title text-foil">Wer sich bei Ihnen meldet</p>'
        '<a class="cf-btn cf-btn--outline cf-btn--xwide" href="ueber-uns.html">'
        " Über uns "
        '<svg class="cf-arrow" aria-hidden="true"><use href="#cf-arrow"></use></svg></a>'
    ),
}


def flatten(footer_html, name):
    """Collapse the markup to one line: whitespace runs become one space and
    whitespace between tags disappears, so indentation depth — the docs demo
    sits two wrappers deeper than a page's footer — is not a difference."""
    text = re.sub(r"\s+", " ", footer_html).strip()
    text = re.sub(r"> <", "><", text)
    if name == COMPONENT.name:
        # The docs page sits one directory over: its footer reaches the
        # patterns through ../patterns/, the patterns reach each other bare.
        text = text.replace('href="../patterns/', 'href="')
    return text


def normalise(flat, name):
    """Remove the four lawful axes of variation from a flattened footer."""
    flat = re.sub(r'\s+aria-current="(?:page|true)"', "", flat)
    flat = re.sub(r'(<footer\b[^>]*?)\s+id="[^"]*"', r"\1", flat)
    flat = flat.replace(" cf-footer--detached", "")
    if name in CTA_CONTACT:
        flat = flat.replace(CTA_CONTACT[name], CTA_REGULAR)
    return flat


def audit(path, canon, verbose):
    findings = []
    name = path.name
    rel = path.relative_to(ROOT)
    text = COMMENT.sub("", path.read_text(encoding="utf-8"))

    m = FOOTER.search(text)
    if not m:
        return ["%s\n    FOOTER  the page carries no <footer> at all" % rel]
    flat = flatten(m.group(0), name)

    # 1. VARIANT — which CTA does the page carry, and which may it.
    has_regular = CTA_REGULAR in flat
    if name in CTA_CONTACT:
        if CTA_CONTACT[name] not in flat:
            findings.append(
                "%s\n    VARIANT  a contact page carries its own CTA, because "
                "the regular one would link to itself — and this is not the "
                "one CTA_CONTACT names for this page" % rel)
    else:
        foreign = [p for p, cta in CTA_CONTACT.items() if cta in flat]
        if foreign:
            findings.append(
                "%s\n    VARIANT  this page carries %s's CTA; that variant "
                "exists only because a contact page cannot link to itself, and "
                "this page owes the reader the road to kontakt.html"
                % (rel, foreign[0]))
        elif not has_regular:
            findings.append(
                "%s\n    VARIANT  the CTA is neither the regular form nor the "
                "one this page is allowed — a third fork of the footer's one "
                "button" % rel)

    # 5. NO CHANNEL — the form is the only way to reach the company, and this
    # block is on every page.
    for scheme in ("tel:", "mailto:"):
        if scheme in flat:
            findings.append(
                "%s\n    CHANNEL  the footer carries a %s link. Contact runs "
                "through the form on kontakt.html; the address the law "
                "requires is in the Impressum, which every footer links to."
                % (rel, scheme.rstrip(":")))

    # 2. CURRENT — the marked link is the right link, marked the right way.
    links = re.findall(
        r'<li><a href="([^"]+)"(\s+aria-current="([^"]*)")?>',
        flat)
    marked = [(href, cur) for href, _, cur in links if cur]
    if len(marked) > 1:
        findings.append(
            "%s\n    CURRENT  %d footer links carry aria-current; a reader "
            "is in one place at a time" % (rel, len(marked)))
    for href, _, cur in links:
        want = ("page" if href == name
                else "true" if section_of(name) == href
                else "")
        if (cur or "") != want and name != COMPONENT.name:
            findings.append(
                '%s\n    CURRENT  the %s link carries aria-current="%s" '
                'where the convention asks %s' % (
                    rel, href, cur or "nothing",
                    '"%s"' % want if want else "nothing"))

    # 3. DETACHED — the modifier tracks the last section, both directions.
    if name != COMPONENT.name:
        main = text[:text.find("</main>")]
        sections = re.findall(r"<section\b[^>]*>", main)
        flush = bool(sections) and "section--flush" in sections[-1]
        detached = "cf-footer--detached" in flat
        if flush and not detached:
            findings.append(
                "%s\n    DETACHED  the last section is --flush and brings no "
                "bottom gap; the footer must carry cf-footer--detached "
                "(the rule is kontakt.html's own comment)" % rel)
        if detached and not flush:
            findings.append(
                "%s\n    DETACHED  cf-footer--detached over a last section "
                "that already brings its own gap doubles the air" % rel)

    # 4. PARITY — after the lawful axes, the copies are one block.
    norm = normalise(flat, name)
    if canon is not None and norm != canon:
        diff = "\n".join(
            "      %s" % l for l in difflib.unified_diff(
                canon.split("><"), norm.split("><"),
                "component", str(rel), lineterm="", n=0)
            if not l.startswith(("---", "+++", "@@")))
        findings.append(
            "%s\n    PARITY  the footer differs from the component's beyond "
            "the four lawful axes:\n%s" % (rel, diff))

    if verbose and not findings:
        print("  %-42s %s%s" % (
            rel,
            "own CTA" if name in CTA_CONTACT else "regular CTA",
            ", detached" if "cf-footer--detached" in flat else ""))
    return findings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    canon_flat = flatten(FOOTER.search(
        COMMENT.sub("", COMPONENT.read_text(encoding="utf-8"))).group(0),
        COMPONENT.name)
    canon = normalise(canon_flat, COMPONENT.name)

    # The component is audited too — against its own normalised form for the
    # attribute rules, so the canon cannot quietly become the fork.
    findings = audit(COMPONENT, canon, args.verbose)

    pages = sorted(PATTERNS.glob("*.html"))
    for page in pages:
        findings.extend(audit(page, canon, args.verbose))

    if findings:
        print("footer parity: %d finding%s\n" % (
            len(findings), "" if len(findings) == 1 else "s"))
        print("\n".join(findings))
        return 1

    print("footer parity: %d copies of the footer — the component's and %d "
          "pattern pages' — agree character-for-character outside the four "
          "lawful axes (aria-current, the contact pages' own CTA, --detached "
          "over a flush last section, the landing page's anchor)."
          % (len(pages) + 1, len(pages)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
