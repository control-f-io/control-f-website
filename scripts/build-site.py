#!/usr/bin/env python3
"""The website at the repository root, generated from design-system/patterns/.

WHAT THIS REPLACED. The root used to hold a different website — nine hand-written
pages against assets/css/main.css, from before the 2026 brand — while the pages
that implement the brand sat one directory down under design-system/patterns/,
reachable only by a reader who already knew they were there. Every visitor to
https://control-f-io.github.io/control-f-website/ got the outgoing generation.
The patterns are the website now, and this is what puts them where the deploy
serves from.

WHY A GENERATOR AND NOT A `git mv`. The pattern pages cannot leave
design-system/patterns/: seventy-five scripts/check-*.py read them from that
path, several of them keyed on it by *string* — check-glass-budget.py's
`PAGE_BUDGET = {"patterns/landing-page.html": 3}`, check-class-provenance.py's
per-page exemption table — and five scheduled routines run against
`design-system/patterns/landing-page.html` hourly and merge their own work. The
patterns are where the system is checked. Moving them would carry the whole
apparatus with them.

WHY A GENERATOR AND NOT A COPY. Because a copy of 8 500 lines of HTML, edited
hourly on one side, is a drift the repository would notice about a week late.
The root pages are output. `--check` holds them to their source, the way
check-spacing-scale.py holds the space-scale table to the shipping CSS, and
deploy.yml runs the generator before it uploads, so what Pages serves is built
from the patterns as they are at that commit even if someone forgets.

THE FOUR EDITS, and nothing else — no minifying, no rewriting, no template.
Each one asserts its own count, so a page that stops matching fails the build
rather than shipping documentation chrome or a dead link:

  ASSETS   `../assets/…` → `design-system/assets/…`. A pattern page sits one
           directory below the assets it loads; a root page sits above them.
           The design system's own README already names
           `/design-system/assets/css/tokens.css` as the integration path — this
           is that path, written relative, because the site is served from
           /control-f-website/ and a leading `/` resolves against the host.
           One copy of every stylesheet, script, font and image: the shipping
           pages and the documentation load the same files.

  HOME     `landing-page.html` → `index.html`, in href and src. The landing page
           is the document a directory index serves, and every nav, footer,
           breadcrumb and search result that points at it has to follow it
           there.

  PREVIEW  Drops the preview.css <link> and the comment above it, which says of
           itself: never ships.

  DSBACK   Drops the `← Design System` nav at the foot of every pattern page.
           It is the way back into the documentation from a specimen. On the
           website it is a link out of the website.

WHAT IT DOES NOT TOUCH. Comments, whitespace, attribute order, the page-local
<style> and <script> blocks — anything the four edits do not name comes through
byte for byte. A diff between a pattern and its shipped page is readable, which
is the whole reason to keep the edits this few.

USAGE

    python3 scripts/build-site.py            # write the root pages
    python3 scripts/build-site.py --check    # fail if any is stale, missing or unowned
    python3 scripts/build-site.py -v         # name every page, not only the changed ones
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = ROOT / "design-system" / "patterns"

# Every pattern ships, under the name the site serves it as. The landing page
# becomes the directory index; everything else keeps the name the pattern pages
# already link to each other by, which is why the HOME edit is the only rename
# this file has to make.
SHIP = {
    "landing-page.html": "index.html",
    "en/landing-page.html": "en/index.html",
    "expertise.html": "expertise.html",
    "ueber-uns.html": "ueber-uns.html",
    "news.html": "news.html",
    "news-thema.html": "news-thema.html",
    "blog-artikel.html": "blog-artikel.html",
    "suche.html": "suche.html",
    "suche-leer.html": "suche-leer.html",
    "karriere.html": "karriere.html",
    "karriere-leer.html": "karriere-leer.html",
    "karriere-stelle.html": "karriere-stelle.html",
    "kontakt.html": "kontakt.html",
    "kontakt-danke.html": "kontakt-danke.html",
    "bewerbung.html": "bewerbung.html",
    "bewerbung-danke.html": "bewerbung-danke.html",
    "datenschutz.html": "datenschutz.html",
    "impressum.html": "impressum.html",
    "404.html": "404.html",
    "en/expertise.html": "en/expertise.html",
    "en/ueber-uns.html": "en/ueber-uns.html",
    "en/news.html": "en/news.html",
    "en/news-thema.html": "en/news-thema.html",
    "en/blog-artikel.html": "en/blog-artikel.html",
    "en/suche.html": "en/suche.html",
    "en/suche-leer.html": "en/suche-leer.html",
    "en/karriere.html": "en/karriere.html",
    "en/karriere-leer.html": "en/karriere-leer.html",
    "en/karriere-stelle.html": "en/karriere-stelle.html",
    "en/kontakt.html": "en/kontakt.html",
    "en/kontakt-danke.html": "en/kontakt-danke.html",
    "en/bewerbung.html": "en/bewerbung.html",
    "en/bewerbung-danke.html": "en/bewerbung-danke.html",
    "en/datenschutz.html": "en/datenschutz.html",
    "en/impressum.html": "en/impressum.html",
    "en/404.html": "en/404.html",
}


# AND THE ARTICLE PAGES, WHICH ARE NOT A TABLE because there is one per post
# and posts arrive without this file being edited. scripts/build-articles.py
# writes `beitrag-<name>.html` from content/news/ in both editions; they ship
# under their own names like every other page. Discovered rather than listed:
# the alternative is a table that has to be edited every time somebody writes a
# post, which is the cost build-news.py was written to remove.
def ship():
    found = dict(SHIP)
    for p in sorted(PATTERNS.glob("beitrag-*.html")):
        found[p.name] = p.name
    for p in sorted((PATTERNS / "en").glob("beitrag-*.html")):
        found["en/" + p.name] = "en/" + p.name
    return found


BANNER = (
    "<!-- GENERATED — DO NOT EDIT THIS FILE.\n"
    "     The website is built from the design system's pattern pages. This page\n"
    "     is design-system/patterns/%s with four edits, all of them\n"
    "     listed in scripts/build-site.py. Change the pattern, then run:\n"
    "\n"
    "         python3 scripts/build-site.py\n"
    "\n"
    "     CI runs `--check` and the deploy regenerates before it uploads, so an\n"
    "     edit made here is lost rather than shipped. -->\n"
)

DOCTYPE = "<!DOCTYPE html>\n"

# TWO DEPTHS, ONE SET OF EDITS. A German pattern sits in patterns/ and reaches
# the assets by `../`; its English twin sits in patterns/en/ and reaches the same
# files by `../../`. Both land one directory apart at the root too — / and /en/ —
# so every path edit is the same edit written for the depth of the page it is
# reading. `up` is that depth, and it is the only thing that differs.
UP = {"": "../", "en/": "../../"}


def assets_re(up):
    """href, src and poster are the three attributes a pattern page names an
    asset in; the paths inside the stylesheets are relative to the stylesheet
    and do not move."""
    return re.compile(r'(href|src|poster)="%s' % re.escape(up + "assets/"))


# HOME. Attribute-anchored, so the prose in a comment that discusses
# landing-page.html by name still discusses the file that exists.
#
# THREE PREFIXES AND NOT ONE, because the landing page is now pointed at from
# three distances. `landing-page.html` is a sibling — the nav and footer of
# every page in its own edition. `en/landing-page.html` is the German landing
# page's language switch, reaching down into the English edition. And
# `../landing-page.html` is the reverse: every English page's switch, and its
# hreflang="de" alternate, reaching back up. All three become index.html at the
# depth they were written at, and a switch that pointed at /en/landing-page.html
# would 404 on the deploy.
HOME = re.compile(r'(href|src)="((?:\.\./|en/)?)landing-page\.html')

# PREVIEW and DSBACK. Both are written once per page, identically, by hand. The
# exact-match requirement is the point: if a page grows a second preview-only
# link, this stops rather than guesses.
def preview_re(up):
    return re.compile(
        r'[ \t]*<!-- Preview only: styles the \.ds-back link into the documentation\. Never\n'
        r'[ \t]*ships — in production the \.ds-back nav is removed and this link with it\. -->\n'
        r'[ \t]*<link rel="stylesheet" href="%scss/preview\.css">\n' % re.escape(up + "assets/")
    )


def dsback_re(up):
    return re.compile(
        r'\n?[ \t]*<nav aria-label="[^"]*"><a class="ds-back" '
        r'href="%s">← Design System</a></nav>\n' % re.escape(up + "index.html")
    )


class BuildError(Exception):
    """An edit did not find what it was written for."""


def transform(text, name):
    """The four edits.

    The two removals go first. Both are written in terms of the page's own `../`
    prefix, and ASSETS rewrites exactly those — run the other way round, the
    preview link is rewritten to a path PREVIEW no longer recognises and the
    documentation chrome ships.
    """
    counts = {}
    up = UP["en/" if name.startswith("en/") else ""]
    # The English edition is served from /en/, one directory below the assets'
    # new home rather than one above it.
    assets_to = "../design-system/assets/" if name.startswith("en/") else "design-system/assets/"

    text, counts["PREVIEW"] = preview_re(up).subn("", text)
    text, counts["DSBACK"] = dsback_re(up).subn("\n", text)
    text, counts["ASSETS"] = assets_re(up).subn(r'\1="%s' % assets_to, text)
    text, counts["HOME"] = HOME.subn(r'\1="\2index.html', text)

    for name_, minimum in (("ASSETS", 1), ("HOME", 1), ("PREVIEW", 1), ("DSBACK", 1)):
        if counts[name_] < minimum:
            raise BuildError(
                "%s: the %s edit matched %d times, expected at least %d — the pattern "
                "page no longer looks the way build-site.py reads it."
                % (name, name_, counts[name_], minimum)
            )
    for name_ in ("PREVIEW", "DSBACK"):
        if counts[name_] > 1:
            raise BuildError(
                "%s: the %s edit matched %d times, expected exactly one."
                % (name, name_, counts[name_])
            )

    if not text.startswith(DOCTYPE):
        raise BuildError("%s: does not begin with %r" % (name, DOCTYPE.strip()))
    # After the doctype and before <html>: the parser is past the point where a
    # comment could change the mode, and the notice is the first thing a reader
    # of the served page sees.
    text = DOCTYPE + (BANNER % name) + text[len(DOCTYPE):]

    if "../assets/" in text or "ds-back" in text or "preview.css" in text:
        raise BuildError("%s: a preview-only reference survived the edits." % name)

    return text


def build():
    """Every pattern, transformed. Returns {root filename: text}."""
    pages = {}
    for src, dest in sorted(ship().items()):
        path = PATTERNS / src
        if not path.exists():
            raise BuildError("design-system/patterns/%s does not exist" % src)
        pages[dest] = transform(path.read_text(encoding="utf-8"), src)
    return pages


def owned_root_html():
    """The .html files this script owns all of: the root, and the English
    edition one directory below it. Nothing else in the tree is a served page —
    design-system/ is documentation and is not walked here."""
    return ({p.name for p in ROOT.glob("*.html")}
            | {"en/" + p.name for p in (ROOT / "en").glob("*.html")})


def main(argv):
    check = "--check" in argv
    verbose = "-v" in argv or "--verbose" in argv

    try:
        pages = build()
    except BuildError as e:
        print("build-site: %s" % e, file=sys.stderr)
        return 2

    stale, missing, written = [], [], []
    for dest, text in sorted(pages.items()):
        path = ROOT / dest
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current == text:
            if verbose:
                print("  ok       %s" % dest)
            continue
        if check:
            (missing if current is None else stale).append(dest)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            written.append(dest)

    unowned = sorted(owned_root_html() - set(pages))

    if check:
        problems = False
        for dest in missing:
            print("MISSING    %s" % dest)
            problems = True
        for dest in stale:
            print("STALE      %s — its pattern has changed" % dest)
            problems = True
        for dest in unowned:
            print("UNOWNED    %s — the root is generated; no page is written by hand there"
                  % dest)
            problems = True
        if problems:
            print("\nrun: python3 scripts/build-site.py", file=sys.stderr)
            return 1
        print("site OK — %d pages at the root, each current with its pattern" % len(pages))
        return 0

    for dest in written:
        print("  written  %s" % dest)
    for dest in unowned:
        print("  UNOWNED  %s — not generated from a pattern; remove it or add it to SHIP"
              % dest)
    print("site built — %d pages, %d changed" % (len(pages), len(written)))
    return 1 if unowned else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
