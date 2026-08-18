#!/usr/bin/env python3
"""The index /suche answers from, read out of the pages that actually ship.

WHY THIS EXISTS. design-system/components/search.html specifies the search page
down to the encoding of its text fragments and then says of the behaviour: "No
script. The form is a GET, the server renders the answer, and the page is a
page." That is the right design for a site with a server. This site has one
route with a server — the contact form's POST, in worker/ — and everything else
is a static file on GitHub Pages. There is nobody to render the answer. So
suche.html shipped for the section's whole life as a drawing of six results for
one query, and typing anything into its field reloaded the same six.

WHAT REPLACES THE SERVER is this file plus assets/js/cf-search.js, and the split
between them is the same one the component chapter already argues for the
server: the answer is computed where the pages are, and the page only draws it.
The index is built once at build time out of the shipped HTML; the script
fetches it, matches, and renders. Nothing is computed twice and no page is
parsed in a browser.

WHY IT READS THE SHIPPED PAGES AND NOT THE PATTERNS. Because the index carries
addresses, and a pattern's address is not the page's. build-site.py's whole
second edit is the mapping — landing-page.html becomes index.html, a post's
pattern `beitrag-<slug>.html` is served at `/blog/<slug>.html`, an opening at
`/stellen/`, a topic at `/news/thema/` — and re-deriving that mapping here would
be the same table written twice, which is the mistake check-script-gates.py
exists to catch one directory over. So this runs LAST in build-all.sh, after
build-site.py has written the root, and reads what it wrote. A result link is
then the address the reader will actually be at.

    scripts/build-all.sh
      build-news · build-jobs · build-i18n · build-articles · build-stellen
      build-site        writes the root
      build-search-index    <- reads the root

WHAT A RECORD IS, and why it is a section rather than a page. The result list on
suche.html draws four kinds — Seite, Beitrag, Abschnitt, Stelle — and three of
its six specimens are Abschnitt, pointing into the middle of a page with an
anchor. A page-level index cannot produce those: /expertise is 2 000 lines and
eight sections, and answering "Telemetrie" with "Expertise" sends the reader to
the top of it to find the word themselves. So every `<h2>` inside <main> opens a
record, the anchor is the heading's own id (or the id its <section> points at
with aria-labelledby, which is how most of these pages are built), and the text
before the first heading is the page's own record. One page yields one Seite and
as many Abschnitt as it has headings.

TEXT IS KEPT AS RUNS, AND THAT IS THE FRAGMENT'S REQUIREMENT, not tidiness. Each
result link carries a `#:~:text=` fragment quoting its own excerpt, and the
component chapter names the trap: a phrase long enough to span an element
boundary "will stop matching", silently. So the extractor never joins across a
tag. A record's text is the list of maximal runs between tags — one run per text
node — the script searches inside a run and quotes inside the same run, and a
quoted phrase therefore cannot span a <a>, a <strong> or a paragraph break by
construction. Soft hyphens are dropped from the runs for the same reason:
Verbraucher&shy;schlichtungs&shy;stelle reads as one word and matches as three.

WHAT IS NOT INDEXED, each for its own reason rather than by taste:

  noindex        any page whose robots meta says so. The search page and its
                 empty state, the two form confirmations. A result set that
                 links to a result set is a loop, and a Danke page is a
                 response to something the reader did, not an answer to a
                 question they asked.
  SPECIMENS      blog-artikel.html, karriere-stelle.html and news-thema.html
                 ship as themselves and are ALSO the templates the content
                 pages are spliced from, so their text exists twice on the
                 site. Indexing both would answer every query about a post
                 twice, once at an address the reader has no reason to be at.
                 check-reachability.py keeps the same three out of its walk,
                 for the same reason and in the same words.
  404            nothing links to an error, and an error must not be an answer.
  CHROME         everything outside <main>: the nav, the footer, the consent
                 banner and its dialog. They are on every page, so a word in
                 them matches every page, which is the same as matching none.
  .visually-hidden   the twin cf-stream.js writes its streamed copy into. The
                 sentence is already indexed from the visible half, and a
                 fragment quoting the hidden one would scroll to something the
                 reader cannot see.

TWO FILES, ONE PER EDITION, and they are separate rather than one file with a
lang field on every record because the reader is in one edition at a time: a
German query answered with English pages is not a better answer, it is a
different site. cf-search.js picks the file from <html lang>, which is the same
place build-i18n.py writes the edition into.

The output is generated and is not tracked — .gitignore's last stanza and
check-tracked-outputs.py's rules both name it. It lands under
design-system/assets/ because that directory is the one thing besides the pages
that stage-site.py copies whole, so the index reaches both deploys without
either of them learning a new path.

    python3 scripts/build-search-index.py            # write both indexes
    python3 scripts/build-search-index.py --check    # fail if either is stale
    python3 scripts/build-search-index.py -v         # per-page record counts
"""

import argparse
import html
import importlib.util
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "design-system" / "assets" / "search"

# The domain the result's path line names. It is a LABEL — the reader's check on
# a ranking they did not compute — and not the href, which is relative like
# every other address on this site because the site is served from a subpath.
SITE = "control-f.de"

# Ship, but not as an answer. The three specimens carry text that also ships at
# a content address; 404 is where a miss lands; karriere-leer.html is the empty
# register drawn at /karriere and is the one state page with no robots meta of
# its own. Every other exclusion is read out of the page's own meta rather than
# typed here — check-reachability.py keeps the same list for the same reason and
# calls them templates and state pages.
NOT_ANSWERS = {
    "blog-artikel.html",
    "karriere-stelle.html",
    "news-thema.html",
    "404.html",
    "karriere-leer.html",
}

NOINDEX = re.compile(r'<meta\s+name="robots"\s+content="[^"]*noindex', re.I)

# Subtrees that are not prose. <svg> holds geometry, <template> holds the copy
# cf-search.js renders WITH (indexing it would answer every query with the
# search page's own strings), and the toc restates headings that are already
# records of their own.
#
# .cf-article__tail IS PROSE AND IS STILL EXCLUDED, which is the one entry here
# that needed measuring rather than arguing. It is the tag row under every
# article, so every post carries the word "Telemetrie" in it — and because it
# sits after the last <h2>, that word landed in the FAZIT record of eleven
# different posts. Eleven results reading "Digitale Zwillinge — Fazit", excerpt
# "Telemetrie", above the article that is actually about it. A tag is a link to
# a topic page, and the topic page is already a record.
SKIP_TAGS = {"script", "style", "svg", "template", "noscript"}
SKIP_CLASSES = ("visually-hidden", "cf-article__toc", "cf-breadcrumb",
                "cf-article__tail")

# The kind label a record carries, derived from the address it lives at. The
# words themselves are copy and live on the page — cf-search.js reads them out
# of suche.html's <template> — so what travels in the index is the token.
def kind_of(url):
    if url.startswith("blog/") or url.startswith("en/blog/"):
        return "post"
    if url.startswith("stellen/") or url.startswith("en/stellen/"):
        return "job"
    if url.startswith("news/thema/") or url.startswith("en/news/thema/"):
        return "topic"
    return "page"


def ship_names():
    """The shipped page names, asked of build-site.py rather than re-derived.

    stage-site.py does exactly this and its docstring carries the argument:
    ship() adds the generated content pages, which arrive without anybody
    editing a table, so reading the SHIP literal out of the file is exact only
    until the first post is written. Importing the function is the only form of
    the question that stays true.
    """
    spec = importlib.util.spec_from_file_location(
        "build_site", ROOT / "scripts" / "build-site.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # ship() is keyed by the PATTERN's name and valued by the address it ships
    # at. The addresses are what this file is about.
    return sorted(mod.ship().values())


class Extractor(HTMLParser):
    """<main> into (heading, anchor, runs) sections, and nothing else.

    stdlib html.parser rather than a regex, and that is not a preference here:
    the skip rules are about SUBTREES — an <svg> forty lines deep, a
    .visually-hidden <span> wrapping three paragraphs — and a subtree is the one
    shape a regex over HTML cannot see the end of.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0            # nesting depth inside <main>, 0 = outside
        self.skip_until = None    # depth to resume collecting at, or None
        self.sections = []        # [{"heading": str, "anchor": str, "runs": []}]
        self.title = ""
        self.date = ""
        self.labelledby = []      # <section aria-labelledby> stack
        self.capture = None       # "title" | "heading" | "date" | None
        self.buffer = []
        self.current = {"heading": "", "anchor": "", "runs": []}

    # -- helpers ----------------------------------------------------------
    def open_section(self, heading, anchor):
        if self.current["runs"] or self.current["heading"]:
            self.sections.append(self.current)
        self.current = {"heading": heading, "anchor": anchor, "runs": []}

    def finish(self):
        if self.current["runs"] or self.current["heading"]:
            self.sections.append(self.current)
        self.current = {"heading": "", "anchor": "", "runs": []}

    # -- parser -----------------------------------------------------------
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "main":
            self.depth = 1
            return
        if not self.depth:
            return
        self.depth += 1

        if self.skip_until is not None:
            return
        classes = (a.get("class") or "").split()
        if tag in SKIP_TAGS or any(c in classes for c in SKIP_CLASSES):
            self.skip_until = self.depth
            return

        if tag == "section":
            self.labelledby.append(a.get("aria-labelledby", ""))

        if tag == "h1" and "cf-page-header__title" in classes:
            self.capture, self.buffer = "title", []
        elif tag == "h2":
            # The anchor the reader will land on: the heading's own id if it has
            # one, otherwise the id its <section> already points at. Both are
            # real on these pages — an article's h2 carries the id, a route
            # page's <section aria-labelledby> does.
            #
            # A HEADING WITH NEITHER OPENS NOTHING. It has no address, so a
            # record made from it would carry the page's own — two results, one
            # link, and the reader choosing between them for no reason. Its text
            # joins the record it sits in, which is where it already reads.
            anchor = a.get("id") or (self.labelledby[-1] if self.labelledby else "")
            if anchor:
                self.open_section("", anchor)
            self.capture, self.buffer = "heading" if anchor else "run", []
        elif tag == "time" and not self.date:
            self.capture, self.buffer = "date", []

    def handle_endtag(self, tag):
        if tag == "main":
            self.finish()
            self.depth = 0
            return
        if not self.depth:
            return

        if self.skip_until is not None and self.depth <= self.skip_until:
            self.skip_until = None
        elif self.skip_until is None:
            if tag == "section" and self.labelledby:
                self.labelledby.pop()
            if self.capture and tag in ("h1", "h2", "time"):
                text = norm(" ".join(self.buffer))
                if self.capture == "title":
                    self.title = self.title or text
                elif self.capture == "heading":
                    self.current["heading"] = text
                elif self.capture == "date":
                    self.date = text
                elif self.capture == "run" and text:
                    self.current["runs"].append(text)
                self.capture, self.buffer = None, []

        self.depth -= 1

    def handle_data(self, data):
        if not self.depth or self.skip_until is not None:
            return
        if self.capture:
            self.buffer.append(data)
            return
        run = norm(data)
        # A run is worth keeping if it holds a word. `·`, `—` and a bare numeral
        # are drawing; build-i18n.py draws the same line for the same reason.
        if len(run) > 2 and re.search(r"[^\W\d_]{2,}", run, re.U):
            self.current["runs"].append(run)


def norm(text):
    """One run of text as the browser will hold it.

    Whitespace collapsed, because the source wraps its paragraphs and a text
    fragment matches on the rendered form. Soft hyphens dropped, because they
    are invisible on the page and fatal inside a quoted phrase.
    """
    return re.sub(r"\s+", " ", html.unescape(text).replace("­", "")).strip()


def page_records(name, source):
    """One page's records: its own, plus one per heading under <main>."""
    ex = Extractor()
    ex.feed(source)
    ex.close()

    # The h1 is the page's name to the reader. Where a page has none — the
    # landing page's hero carries the wordmark, not a heading — the <title> is
    # the same sentence with the company appended, so the suffix comes off.
    head = re.search(r"<title>(.*?)</title>", source, re.S)
    title = ex.title or re.sub(
        r"\s+[—–|-]\s+Control-F\s*$", "", norm(head.group(1)) if head else name)
    kind = kind_of(name)
    # The address the page is served at, without the .html the reader never
    # types and with the directory index left as the bare directory.
    stem = re.sub(r"(?:^|/)index\.html$", "/", name)
    stem = re.sub(r"\.html$", "", stem).rstrip("/")

    records = []
    for i, sec in enumerate(ex.sections):
        lead = i == 0 and not sec["heading"]
        anchor = "" if lead else sec["anchor"]
        records.append({
            "url": name + (("#" + anchor) if anchor else ""),
            "title": title if lead else "%s — %s" % (title, sec["heading"]),
            "kind": kind if lead else "section",
            "path": "%s/%s%s" % (SITE, stem, ("#" + anchor) if anchor else ""),
            "date": ex.date,
            "runs": sec["runs"],
        })
    # A page whose <main> opens straight into a heading has no lead record, and
    # then nothing in the index carries the page's own address. Give it one.
    if records and records[0]["url"] != name:
        records.insert(0, {
            "url": name, "title": title, "kind": kind,
            "path": "%s/%s" % (SITE, stem), "date": ex.date,
            "runs": [title],
        })
    return [r for r in records if r["runs"]]


def build_index(names, verbose):
    docs = []
    for name in names:
        source = (ROOT / name).read_text(encoding="utf-8")
        if NOINDEX.search(source):
            continue
        records = page_records(name, source)
        docs.extend(records)
        if verbose:
            print("  %-56s %2d records" % (name, len(records)))
    return docs


def write(check, verbose):
    names = [n for n in ship_names()
             if Path(n).name not in NOT_ANSWERS and (ROOT / n).exists()]
    missing = [n for n in ship_names() if not (ROOT / n).exists()]
    if missing:
        print("build-search-index: the root is not built — run "
              "`python3 scripts/build-site.py` first.\n  missing: %s"
              % ", ".join(missing[:4]), file=sys.stderr)
        return 1

    editions = {
        "de": [n for n in names if not n.startswith("en/")],
        "en": [n for n in names if n.startswith("en/")],
    }

    stale = []
    for lang, pages in editions.items():
        if verbose:
            print("%s — %d pages" % (lang, len(pages)))
        index = {"lang": lang, "site": SITE, "docs": build_index(pages, verbose)}
        # sort_keys so the file is byte-stable across runs: --check compares
        # text, and a dict that reordered itself would report every build stale.
        text = json.dumps(index, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":")) + "\n"
        path = OUT / ("index-%s.json" % lang)
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                stale.append(path.relative_to(ROOT).as_posix())
            continue
        OUT.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print("  %-44s %4d records, %d kB"
              % (path.relative_to(ROOT).as_posix(), len(index["docs"]),
                 round(len(text.encode("utf-8")) / 1024)))

    if check:
        if stale:
            print("build-search-index: stale or missing — %s\n"
                  "  Run `python3 scripts/build-search-index.py`."
                  % ", ".join(stale), file=sys.stderr)
            return 1
        print("search index OK — both editions current with the shipped pages.")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="fail if either index is missing or stale")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="name every page and its record count")
    args = ap.parse_args()
    return write(args.check, args.verbose)


if __name__ == "__main__":
    sys.exit(main())
