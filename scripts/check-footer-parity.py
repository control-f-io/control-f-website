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

  THE TEL CTA    kontakt.html documents the rule in place: "Der Footer trägt
                 auf jeder anderen Seite den CTA 'Jetzt Projekt starten' mit
                 dem Link hierher. Auf dieser Seite wäre das ein Link auf
                 sich selbst, also steht hier die andere Hälfte des Angebots:
                 anrufen statt schreiben." kontakt-danke.html argues the same
                 swap for the page after the form. Two contact pages, two
                 documented tel variants, and the rule's own wording — "auf
                 jeder anderen Seite" — is the fence around them.

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
               page except the two contact pages, which must carry the tel
               form (Lieber direkt sprechen? / cf-btn--outline /
               tel:+4917644478596 / the number). A third form anywhere is a
               finding either way.
  2. CURRENT   at most one footer link carries aria-current; it is "page"
               iff the href is the page itself, "true" iff SECTION_OF maps
               the page to that href, and required whenever either rule
               fires — a page in the links list may not leave itself
               unmarked.
  3. DETACHED  cf-footer--detached iff the last <section> inside <main>
               carries section--flush.
  4. PARITY    after normalising the four lawful axes away — aria-current
               removed, the tel CTA rewritten to the regular one on the
               pages allowed to carry it, --detached and the footer's id
               dropped, whitespace collapsed, the docs page's ../patterns/
               hrefs relativised — every copy is CHARACTER-IDENTICAL to the
               component's. Whatever the next fork is, it fails here without
               this file having to predict it.

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

# The two pages whose footer CTA may not link to kontakt.html, because on
# them it would be a link to itself (kontakt) or to the form the reader has
# just sent (kontakt-danke). The rule and its fence are kontakt.html's own
# comment: the tel variant stands "auf dieser Seite", the regular CTA "auf
# jeder anderen Seite".
CONTACT_PAGES = {"kontakt.html", "kontakt-danke.html"}

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

CTA_REGULAR = (
    '<p class="cf-footer__title text-foil">Jetzt Projekt starten!</p>'
    '<a class="cf-btn cf-btn--primary cf-btn--xwide" href="kontakt.html">'
    " Kontakt aufnehmen "
    '<svg class="cf-arrow" aria-hidden="true"><use href="#cf-arrow"></use></svg></a>'
)
CTA_TEL = (
    '<p class="cf-footer__title text-foil">Lieber direkt sprechen?</p>'
    '<a class="cf-btn cf-btn--outline cf-btn--xwide" href="tel:+4917644478596">'
    " +49 176 44478596 "
    '<svg class="cf-arrow" aria-hidden="true"><use href="#cf-arrow"></use></svg></a>'
)


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
    if name in CONTACT_PAGES:
        flat = flat.replace(CTA_TEL, CTA_REGULAR)
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
    has_tel = CTA_TEL in flat
    if name in CONTACT_PAGES:
        if not has_tel:
            findings.append(
                "%s\n    VARIANT  a contact page must carry the tel CTA — the "
                "regular one is a link to itself" % rel)
    else:
        if has_tel:
            findings.append(
                "%s\n    VARIANT  the tel CTA is the contact pages' answer to "
                "a self-link; this page has no self-link to avoid and owes "
                "the reader the road to kontakt.html" % rel)
        elif not has_regular:
            findings.append(
                "%s\n    VARIANT  the CTA is neither the regular form nor the "
                "tel form — a third fork of the footer's one button" % rel)

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
                else "true" if SECTION_OF.get(name) == href
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
            "tel CTA" if has_tel else "regular CTA",
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
          "lawful axes (aria-current, the contact pages' tel CTA, --detached "
          "over a flush last section, the landing page's anchor)."
          % (len(pages) + 1, len(pages)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
