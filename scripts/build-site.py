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

  ASSETS   `../assets/…` → `design-system/assets/…`, with one `../` for every
           directory the shipped page is buried in. A pattern page sits one
           directory below the assets it loads; a root page sits above them, a
           page in /blog/ one further down, a page in /en/news/thema/ three.
           The design system's own README already names
           `/design-system/assets/css/tokens.css` as the integration path — this
           is that path, written relative, because the site is served from
           /control-f-website/ and a leading `/` resolves against the host.
           One copy of every stylesheet, script, font and image: the shipping
           pages and the documentation load the same files.

  LINKS    Every reference to a pattern page becomes the path that page ships
           at, written relative to the page doing the pointing. Two things fall
           out of the one rule. `landing-page.html` → `index.html`, because the
           landing page is the document a directory index serves and every nav,
           footer, breadcrumb and search result that points at it has to follow
           it there. And the content pages move into folders: a pattern named
           `beitrag-wie-stahl-….html` is served at `/blog/wie-stahl-….html`, so
           a card on news.html that says `href="beitrag-wie-stahl-….html"` is
           rewritten to `blog/wie-stahl-….html`, and the same link from
           `/news/thema/energie.html` two directories down is rewritten to
           `../../blog/wie-stahl-….html`. A name the ship table does not know is
           left alone — it is not a page this script ships.

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

import posixpath
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = ROOT / "design-system" / "patterns"

# Every pattern ships, under the name the site serves it as. The landing page
# becomes the directory index; every other page in this table keeps the name the
# pattern pages already link to each other by. The content pages are not in this
# table and do not keep their names — see FOLDER below.
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


# AND THE CONTENT PAGES, WHICH ARE NOT A TABLE because there is one per post,
# one per opening and one per topic, and none of them arrives by editing this
# file. scripts/build-articles.py writes `beitrag-<name>.html` from
# content/news/, scripts/build-stellen.py writes `stelle-<name>.html` from
# content/jobs/, and scripts/build-news.py writes `news-thema-<slug>.html` for
# every topic its posts carry — all in both editions; they ship under their own
# names like every other page. Discovered rather than listed: the alternative is
# a table that has to be edited every time somebody writes a post, advertises a
# job or files the first post under a new topic, which is the cost build-news.py
# and build-jobs.py were written to remove.
# AND THEY SHIP INTO FOLDERS, WHICH THE PATTERNS DO NOT. A pattern directory is
# flat because 118 check scripts read it with a non-recursive glob and several
# name a page by string; a page moved into a subdirectory there would stop being
# checked without anything failing, which is the one outcome worse than an
# untidy directory. So the folder is a property of the address, not of the
# source: `beitrag-wie-stahl-….html` is written flat beside its siblings and
# served at /blog/wie-stahl-…html. The prefix was doing the folder's job — it is
# dropped on the way out, because /blog/beitrag-wie-stahl… says it twice.
FOLDER = (("beitrag-", "blog/"),
          ("stelle-", "stellen/"),
          ("news-thema-", "news/thema/"))


def ship():
    found = dict(SHIP)
    for prefix, folder in FOLDER:
        for p in sorted(PATTERNS.glob(prefix + "*.html")):
            found[p.name] = folder + p.name[len(prefix):]
        for p in sorted((PATTERNS / "en").glob(prefix + "*.html")):
            found["en/" + p.name] = "en/" + folder + p.name[len(prefix):]
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


# LINKS, WHICH USED TO BE HOME AND IS THE SAME EDIT GENERALISED. It was written
# for one rename — `landing-page.html` → `index.html`, because the landing page
# is the document a directory index serves — and every other page kept the name
# its siblings already linked it by, so nothing else had to move. That stopped
# being true when the content pages gained folders: a card on news.html says
# `href="beitrag-wie-stahl-….html"` and the page it means is served at
# /blog/wie-stahl-….html, one directory down and one prefix shorter.
#
# So the rule is now the general one the rename was an instance of: **every
# reference to a pattern page becomes the path that page ships at, written
# relative to the page doing the pointing.** The landing page falls out of it —
# `landing-page.html` is in the table and the table says `index.html`.
#
# Attribute-anchored, so prose in a comment that discusses a page by name still
# discusses the file that exists. THREE PREFIXES, because a pattern page points
# at another from three distances: `X.html` is a sibling in its own edition;
# `en/X.html` is the German page's language switch reaching down into the
# English edition; `../X.html` is the reverse — every English page's switch and
# its hreflang="de" alternate, reaching back up. A name the table does not know
# is left exactly as it was: it is not a page this script ships.
# The tail is `?query` as well as `#fragment`: the topic pages' pagination points
# at `news-thema-telemetrie.html?seite=2`, and a rewrite that only understood
# fragments left those three links pointing at a page that had moved.
LINK = re.compile(r'(href|src|poster)="((?:\.\./|en/)?)([a-z0-9][a-z0-9-]*\.html)((?:[?#][^"]*)?)"')


def links(text, src, table):
    """Every reference to a pattern page, rewritten to where that page ships."""
    edition = "en/" if src.startswith("en/") else ""
    here = posixpath.dirname(table[src])

    def one(m):
        attr, prefix, name, frag = m.groups()
        if prefix == "en/":
            target = "en/" + name
        elif prefix == "../":
            # Only an English page reaches up, and what it reaches is the German
            # edition. A German page has nothing above it to point at.
            target = name
        else:
            target = edition + name
        if target not in table:
            return m.group(0)
        return '%s="%s%s"' % (attr, posixpath.relpath(table[target], here or "."), frag)

    return LINK.subn(one, text)

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


def transform(text, name, table):
    """The four edits.

    The two removals go first. Both are written in terms of the page's own `../`
    prefix, and ASSETS rewrites exactly those — run the other way round, the
    preview link is rewritten to a path PREVIEW no longer recognises and the
    documentation chrome ships.
    """
    counts = {}
    up = UP["en/" if name.startswith("en/") else ""]
    # HOW FAR THE SHIPPED PAGE SITS FROM THE ROOT, which is not a property of the
    # pattern any more. A pattern is at one of two depths; the page it becomes is
    # at one of four — /index.html, /en/index.html or /blog/x.html, and
    # /en/news/thema/x.html two below that. The assets live at the root either
    # way, so the answer is one `../` per directory the page is buried in.
    assets_to = "../" * table[name].count("/") + "design-system/assets/"

    text, counts["PREVIEW"] = preview_re(up).subn("", text)
    text, counts["DSBACK"] = dsback_re(up).subn("\n", text)
    text, counts["ASSETS"] = assets_re(up).subn(r'\1="%s' % assets_to, text)
    text, counts["LINKS"] = links(text, name, table)

    for name_, minimum in (("ASSETS", 1), ("LINKS", 1), ("PREVIEW", 1), ("DSBACK", 1)):
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

    # A content page's pattern name is not an address. If one survives here it is
    # a link to /beitrag-….html, which is a 404 — the file moved to /blog/.
    left = re.search(r'(?:href|src|poster)="(?:\.\./|en/)?'
                     r'((?:beitrag|stelle|news-thema)-[^"]*\.html)"', text)
    if left:
        raise BuildError(
            "%s: %s is a pattern name and not an address — it ships from a "
            "folder now, and links() did not rewrite this one."
            % (name, left.group(1)))

    return text


def build():
    """Every pattern, transformed. Returns {root filename: text}."""
    pages = {}
    table = ship()
    for src, dest in sorted(table.items()):
        path = PATTERNS / src
        if not path.exists():
            raise BuildError("design-system/patterns/%s does not exist" % src)
        pages[dest] = transform(path.read_text(encoding="utf-8"), src, table)
    return pages


def owned_root_html():
    """The .html files this script owns all of: the root, the English edition one
    directory below it, and the content folders in both. Nothing else in the tree
    is a served page — design-system/ is documentation and is not walked here.

    The folders are walked for the same reason the root is: this set is what the
    unowned sweep subtracts the shipped pages from, so a page that stops being
    generated — a post unpublished in Notion, a topic whose last post moved — is
    deleted instead of being served forever. When the content pages moved out of
    the root, an unwalked folder would have meant every one of them looked
    unowned-and-invisible rather than owned."""
    seen = {p.name for p in ROOT.glob("*.html")}
    seen |= {"en/" + p.name for p in (ROOT / "en").glob("*.html")}
    for _, folder in FOLDER:
        for edition in ("", "en/"):
            here = ROOT / (edition + folder)
            if here.is_dir():
                seen |= {edition + folder + p.name for p in here.glob("*.html")}
    return seen


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
        (ROOT / dest).unlink()
        print("  removed  %s" % dest)
    print("site built — %d pages, %d changed" % (len(pages), len(written) + len(unowned)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
