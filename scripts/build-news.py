#!/usr/bin/env python3
"""The news archive, generated from content/news/ instead of typed into the page.

WHAT WAS WRONG WITH TYPING IT. design-system/patterns/news.html carried
eighteen cards as hand-written markup and three counters as literals: "189
Beiträge seit 2022", "18 von 189", "Seite 1 von 11". None of those numbers
counted anything — there was no store of posts anywhere in the repository, so
the page claimed a hundred and seventy-one articles that do not exist, and the
axis under the grid labelled columns of them.

That is the fault check-section-counts.py was written for, one page over: "a
wrong counter renders exactly like a right one". And the cost fell on whoever
had to add a post — four files by hand (the German pattern, its English
edition, and the two generated root pages), five columns whose lengths are
1/2/3/6/6 and change when anything is inserted at the top, three counters, and
a year axis. Adding one post meant editing eighteen cards.

SO A POST IS A FILE AND THE PAGE IS OUTPUT. content/news/ holds one file per
post — the format is in new-post.py, which writes it — and this script lays out
the grid from them. The same argument build-site.py and build-i18n.py already
made for their own outputs: "a copy of 8 500 lines of HTML, edited hourly on one
side, is a drift the repository would notice about a week late."

WHAT IT GENERATES, and nothing else. Four regions of the page, each fenced by a
pair of comments this script owns:

    news:meta    the page header's two mono lines — the post count and, when
                 there is more than one page, which page this is
    news:cards   the five columns, newest first, 1/2/3/6/6
    news:axis    the tick under each column, naming the era it holds
    news:pages   the pagination, or nothing at all when everything fits on one
                 page. A single page has no "1 of 1" to state and no step to
                 take, and the page's own note says a step that does nothing is
                 removed rather than disabled.

Everything else on that page — the topic chips, the section headers, the
comments that explain the composition — is authored and comes through
untouched. The chips are deliberately NOT generated: the filter is server-side
("der Filter IST die URL") and no post declares a topic, so generating them
would mean inventing metadata to fill a control that does not work yet.

THE COLUMNS ARE THE DESIGN'S, NOT AN ARBITRARY CHUNKING. 1 lead, 2, 3, 6, 6 —
eighteen cards, "von aktuell nach alt und von ausführlich nach knapp", which is
why the lead card carries its author and the compact ones carry nothing but a
title. Posts are sorted newest first and poured into that shape in order, so
the newest post is always the lead and the oldest are always compact.

BOTH EDITIONS COME OUT OF ONE FILE. Every post carries `titel` and `title`, and
this script keeps design-system/i18n/en.json in step: the German title is a
string the reader sees, so build-i18n.py fails the build without an entry for
it. Writing the pair here means an admin adds a post in one place and the
English edition follows, which is the whole point of the catalogue being a
catalogue rather than a second page.

    python3 scripts/build-news.py           # write the page from content/news/
    python3 scripts/build-news.py --check    # fail if the page is stale
    python3 scripts/build-news.py -v         # name every post it laid out

After it, run build-i18n.py and build-site.py — or just scripts/build-all.sh,
which is the order they have to run in. --check does not run them; each build
checks its own output.

stdlib only, no build step, no dependency. Same python3 that serves the pages.
"""

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
POSTS = ROOT / "content" / "news"
PAGE = ROOT / "design-system" / "patterns" / "news.html"
CATALOGUE = ROOT / "design-system" / "i18n" / "en.json"

# The design's own shape: one lead, two, three, then two columns of six.
# Eighteen per page, which is what "18 von 189" claimed and what the five
# .cf-blog-col--N classes lay out.
COLUMNS = (1, 2, 3, 6, 6)
PER_PAGE = sum(COLUMNS)

# A field this script reads. Everything else in a post file is ignored rather
# than rejected, so a later run can add a body without this one having to know.
REQUIRED = ("datum", "titel", "title")

# WHERE THE GERMAN TEXT ENDS AND THE ENGLISH BEGINS. A post is one file in two
# languages, the same way its two titles are two fields of one record: the site
# ships both editions, and a post that exists in one of them is a page with a
# German paragraph in the middle of the English archive. The divider is what
# Notion's own divider block imports as, so an admin writing there types
# nothing — they draw a line.
DIVIDER = re.compile(r"^ {0,3}-{3,}\s*en\s*-{3,}\s*$", re.M | re.I)

REGION = "<!-- news:%s -->"
REGION_END = "<!-- /news:%s -->"


def fail(msg):
    print("build-news: " + msg)
    sys.exit(1)


# --------------------------------------------------------------------------
# the store
# --------------------------------------------------------------------------

def blocks(text, where):
    """A post's text → the blocks it is made of, in order.

    THE SMALLEST GRAMMAR THAT NOTION EMITS, and deliberately no larger. A post
    is written in an editor — Notion for an admin, a text editor for anyone
    else — and every form below is one the editor already has a button for:
    a paragraph, two levels of heading, a bulleted list, a numbered list.
    Anything richer that an article needs — the isometric figures, the plot,
    the table, the pull quote — lives in blog-artikel.html, which is written by
    hand for exactly that reason and is the specimen the generated pages take
    their furniture from.

    Blocks are separated by a blank line, which is what pressing return twice
    already does.
    """
    out = []
    for chunk in re.split(r"\n\s*\n", text.strip()):
        lines = [ln.strip() for ln in chunk.strip().splitlines() if ln.strip()]
        if not lines:
            continue
        if lines[0].startswith("### "):
            kind, payload = "h3", lines[0][4:].strip()
        elif lines[0].startswith("## "):
            kind, payload = "h2", lines[0][3:].strip()
        elif lines[0].startswith("- ") or re.match(r"\d+\.\s", lines[0]):
            # A LIST ITEM IS ALLOWED TO BE LONGER THAN A LINE. The marker opens
            # an item and every line after it that carries none belongs to the
            # item above — which is how a wrapped file reads to a person, and
            # the first version of this took a three-line item for a paragraph
            # and set the whole list as running text.
            kind = "ul" if lines[0].startswith("- ") else "ol"
            payload = []
            for ln in lines:
                if ln.startswith("- ") or re.match(r"\d+\.\s", ln):
                    payload.append(re.sub(r"^(?:-|\d+\.)\s*", "", ln))
                elif payload:
                    payload[-1] += " " + ln
        else:
            kind, payload = "p", " ".join(lines)
        if kind in ("h2", "h3") and len(lines) > 1:
            fail("%s: a heading is one line, and this one runs to %d — %r"
                 % (where, len(lines), lines[0]))
        out.append((kind, payload))
    return out


def bodies(text, where):
    """The German and the English text of one post, or (None, None) for neither.

    A POST WITHOUT TEXT IS NOT AN ERROR. content/news/ was seeded from the cards
    of the mock-up, and eighteen of those entries are a headline and a date and
    nothing else. They stay in the archive and they get no page: a card that
    links to somebody else's article is the fault this whole file was written
    to remove, and a page that says "no text yet" under a claim of six minutes'
    reading is the same fault one click further in.
    """
    if not text.strip():
        return None, None
    parts = DIVIDER.split(text)
    if len(parts) != 2:
        fail("%s has text but %s.\n"
             "    A post is written in both languages, in one file: the German "
             "text, a divider line, then the English text.\n"
             "    In Notion that divider is the divider block; in a file it is "
             "`--- en ---` on a line of its own."
             % (where, "no `--- en ---` divider" if len(parts) < 2
                else "%d dividers" % (len(parts) - 1)))
    de, en = (blocks(p, where) for p in parts)
    if not de or not en:
        fail("%s has text on only one side of the divider. Both editions ship."
             % where)
    for side, bs in (("de", de), ("en", en)):
        if bs[0][0] != "p":
            fail("%s: the %s text opens with a %s. The first block is the lead "
                 "paragraph — it is set larger and it is what the archive and "
                 "the search results quote." % (where, side, bs[0][0]))
    heads_de = [k for k, _ in de if k in ("h2", "h3")]
    heads_en = [k for k, _ in en if k in ("h2", "h3")]
    if heads_de != heads_en:
        fail("%s: the two editions are divided differently — German has %s and "
             "English has %s.\n"
             "    The contents rail is built from the headings, so a piece with "
             "four sections in German and three in English is two different "
             "pieces." % (where, heads_de or "none", heads_en or "none"))
    return de, en


def read_posts():
    """Every post in content/news/, newest first.

    A file that cannot be read is a failure and never a skip: a post silently
    dropped from the archive looks exactly like a post nobody wrote.
    """
    if not POSTS.is_dir():
        fail("no content/news/ directory. scripts/new-post.py writes the first one.")
    out = []
    for path in sorted(POSTS.glob("*.md")):
        post = {"file": path.name}
        head, _, body = path.read_text(encoding="utf-8").partition("\n\n")
        for n, line in enumerate(head.splitlines(), 1):
            line = line.rstrip()
            if not line:
                break                      # the header ends at the first blank line
            if ":" not in line:
                fail("%s:%d is not `feld: wert` — %r" % (path.name, n, line))
            k, v = line.split(":", 1)
            post[k.strip()] = v.strip()
        post["text_de"], post["text_en"] = bodies(body, path.name)
        missing = [k for k in REQUIRED if not post.get(k)]
        if missing:
            fail("%s has no %s. Every post needs a date and both titles."
                 % (path.name, " and no ".join(missing)))
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", post["datum"]):
            fail("%s: datum is %r, not YYYY-MM-DD." % (path.name, post["datum"]))
        out.append(post)
    if not out:
        fail("content/news/ is empty. scripts/new-post.py writes the first post.")
    # Newest first, and the filename breaks a tie so the order is stable rather
    # than filesystem-dependent — two posts on one day must not swap places
    # between two runs of this script.
    out.sort(key=lambda p: (p["datum"], p["file"]), reverse=True)
    return out


def german(iso):
    y, m, d = iso.split("-")
    return "%s.%s.%s" % (d, m, y)


def page_name(post):
    """The page a post is read on — `beitrag-<name>.html`, or None.

    The name is the post file's own, without its date and its extension, so the
    URL a reader shares and the file an admin edits carry the same string and
    neither has to be looked up. `beitrag-` and not `blog-` because
    blog-artikel.html is the specimen these pages are built from: one prefix
    means generated, and a page that is not generated is not called one.

    None for a post with no text. scripts/build-articles.py writes a page for
    every post that has one, and this is where both scripts agree on which.
    """
    if not post.get("text_de"):
        return None
    return "beitrag-%s.html" % post["file"][11:-3]


# --------------------------------------------------------------------------
# the regions
# --------------------------------------------------------------------------

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def cards(page_posts, indent="          "):
    """The five columns, in the design's own order and modifiers."""
    lines, i = [], 0
    for n in COLUMNS:
        take = page_posts[i:i + n]
        i += n
        lines.append('%s<div class="cf-blog-col subdivide__col cf-blog-col--%d">' % (indent, n))
        for p in take:
            meta = []
            # The lead is the only card that names its author: it is the one
            # card with room for the line, and the page's composition note
            # calls the columns "von ausführlich nach knapp".
            if n == 1 and p.get("autor"):
                meta.append(esc(p["autor"]))
            if n <= 3:
                meta.append(german(p["datum"]))
                if p.get("minuten"):
                    meta.append("%s min" % p["minuten"])
            mod = {1: " cf-blog-card--lead", 6: " cf-blog-card--compact"}.get(n, "")
            title = '<span class="cf-blog-card__title">%s</span>' % esc(p["titel"])
            meta_html = ('<span class="cf-blog-card__meta">%s</span>'
                         % esc(" · ".join(meta))) if meta else ""
            # A CARD IS A LINK WHEN THERE IS SOMETHING BEHIND IT AND NOT
            # OTHERWISE. Every one of these used to point at blog-artikel.html,
            # so all eighteen headlines opened the same article about digital
            # twins — the card said one thing and the page said another, which
            # is the failure this file exists to stop making with numbers.
            # A post with text gets its own page and links to it; one of the
            # mock-up's text-less entries stays a listing, and .cf-blog-card
            # is written for any element rather than for <a> so the row looks
            # the same either way. → scripts/build-articles.py
            href = page_name(p)
            open_, close = (
                ('<a class="cf-blog-card%s" href="%s">' % (mod, href), "</a>") if href
                else ('<span class="cf-blog-card%s cf-blog-card--listing">' % mod, "</span>"))
            if n == 1:
                lines.append("%s  %s" % (indent, open_))
                lines.append("%s    %s" % (indent, title))
                lines.append("%s    %s" % (indent, meta_html))
                lines.append("%s  %s" % (indent, close))
            else:
                lines.append("%s  %s%s%s%s" % (indent, open_, title, meta_html, close))
        lines.append("%s</div>" % indent)
    return "\n".join(lines)


def axis(page_posts, indent="          "):
    """One tick per column, naming the era that column holds.

    The newest column is "Aktuell" whatever year it is in — the tick says where
    the reader is in the archive, and the top of an archive is now. Every other
    column is named by the years its own cards carry, which is why a column
    spanning two years reads "2022–2023" on the page today.
    """
    ticks, i = [], 0
    for k, n in enumerate(COLUMNS):
        take = page_posts[i:i + n]
        i += n
        if not take:
            continue
        years = sorted({p["datum"][:4] for p in take})
        label = "Aktuell" if k == 0 else (
            years[0] if len(years) == 1 else "%s–%s" % (years[0], years[-1]))
        ticks.append('%s<span class="cf-blog-axis__tick">%s</span>' % (indent, label))
    return "\n".join(ticks)


def meta(posts, pages, indent="          "):
    """The page header's two mono lines.

    "seit YYYY" is the oldest post's year rather than a constant: an archive
    that loses its oldest post stops having started that year. The second line
    only exists when there is more than one page — it answers "which page am I
    on", and on a single page nobody asked.
    """
    lines = ['%s<span>%d Beiträge seit %s</span>'
             % (indent, len(posts), min(p["datum"][:4] for p in posts))]
    if pages > 1:
        lines.append("%s<span>Seite 1 von %d</span>" % (indent, pages))
    return "\n".join(lines)


def page_links(pages):
    """The numbered links after page 1: (number, aria-label, gap before it).

    ONE DESCRIPTION, READ TWICE. The markup below draws these and derived()
    translates them, and when each worked it out for itself they disagreed: at
    two pages the catalogue gained an entry for "Seite 2, letzte Seite" that the
    markup never drew, and an entry nothing draws fails the next build.

    The gap and the last-page label only appear when they say something. At four
    pages or fewer every page is already listed, and an ellipsis standing for
    nothing is a control lying about how far the archive goes.
    """
    near = list(range(2, min(4, pages) + 1))
    out = [(n, "Seite %d" % n, False) for n in near]
    last = max(near or [1])
    if pages > last:
        out.append((pages, "Seite %d, letzte Seite" % pages, pages > last + 1))
    return out


def count(shown, total, indent="        "):
    """The Beiträge header's counter: what stands on this page, of what there is.

    Two numbers only while they differ. components/section-header.html publishes
    "a bare count when the unit follows from the label" as its own form, and on
    a single page "18 von 18" is that form with the same number said twice —
    a counter inviting the reader to check an arithmetic that cannot fail.
    """
    text = str(total) if shown == total else "%d von %d" % (shown, total)
    return '%s<span class="cf-section-header__count">%s</span>' % (indent, text)


def pagination(pages, indent="      "):
    """The design's own shape: 1 2 3 4 … last, then the step, all inside the list.

    Nothing at all on a single page. The page's note about the first page says
    the step is removed rather than disabled — "ein deaktiviertes Ziel antwortet
    nicht, wenn man dort ankommt" — and one page of posts is that argument taken
    to its end: no "Seite 1 von 1" to state and nowhere to step to.

    The gap and the last-page link only appear when they say something. At five
    pages or fewer every page is already listed, and an ellipsis standing for
    nothing is a control that lies about how far the archive goes.
    """
    if pages <= 1:
        return ""
    items = ['<li><span class="cf-pagination__page" aria-current="page">1</span></li>']
    for n, label, gap_before in page_links(pages):
        if gap_before:
            items.append('<li><span class="cf-pagination__gap" aria-hidden="true">…</span></li>')
        items.append('<li><a class="cf-pagination__page" href="news.html?seite=%d" '
                     'aria-label="%s">%d</a></li>' % (n, label, n))
    out = ['%s<nav class="cf-pagination" aria-label="Beiträge, Seiten">' % indent,
           '%s  <p class="cf-pagination__status">Seite 1 von %d</p>' % (indent, pages),
           '%s  <ul class="cf-pagination__list" role="list">' % indent]
    out += ["%s    %s" % (indent, it) for it in items]
    out += ['%s    <li>' % indent,
            '%s      <a class="cf-pagination__step cf-pagination__step--next" '
            'href="news.html?seite=2" rel="next">' % indent,
            "%s        Weiter" % indent,
            '%s        <svg class="cf-icon cf-icon--sm" aria-hidden="true">'
            '<use href="#cf-chevron-right"></use></svg>' % indent,
            "%s      </a>" % indent,
            "%s    </li>" % indent,
            "%s  </ul>" % indent,
            "%s</nav>" % indent]
    return "\n".join(out)


def splice(html, name, body):
    """Replace one fenced region, keeping the fences."""
    start, end = REGION % name, REGION_END % name
    m = re.search(re.escape(start) + r".*?" + re.escape(end), html, re.S)
    if not m:
        fail("news.html has no %s … %s region. The fences are how this script "
             "knows what it owns; restore them." % (start, end))
    pad = re.match(r"[ \t]*", html[html.rfind("\n", 0, m.start()) + 1:m.start()]).group(0)
    inner = "\n%s\n%s" % (body, pad) if body else "\n%s" % pad
    return html[:m.start()] + start + inner + end + html[m.end():]


# --------------------------------------------------------------------------
# the catalogue
# --------------------------------------------------------------------------

# The catalogue's own conventions for the strings this page generates, read off
# the entries that were already in it: a German dotted date becomes `DD Mon
# YYYY`, and the two counters read as sentences.
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def en_meta(iso):
    y, m, d = iso.split("-")
    return "%s %s %s" % (d, MONTHS[int(m) - 1], y)


def derived(posts, total, pages, first_year):
    """Every string this script writes onto the page, with its English twin.

    THE GENERATOR OWNS THE ENTRIES FOR WHAT THE GENERATOR WRITES, and this is
    the half that only showed up when a nineteenth post was added. The titles
    are copy an admin types, so they belong in the post file. The rest of the
    page's words are *derived* — "19 Beiträge seit 2022", "Seite 1 von 2",
    "Daniel Tremer · 07.08.2026 · 3 min" — and they change with every post that
    lands. Asking a person to add a catalogue entry for each of them would put
    the cost this script exists to remove back on them, one line further down,
    and build-i18n.py would fail the build until they did.

    So they are translated here, mechanically, in the catalogue's own idiom:
    every one of these forms was already in en.json, written by hand, and this
    only keeps writing them.
    """
    pairs = {}
    i = 0
    for width in COLUMNS:
        for p in posts[i:i + width]:
            pairs[p["titel"]] = p["title"]
            if width > 3:
                continue        # a compact card is a title and nothing else
            parts_de, parts_en = [], []
            if width == 1 and p.get("autor"):
                parts_de.append(p["autor"])
                parts_en.append(p["autor"])      # a name is not translated
            parts_de.append(german(p["datum"]))
            parts_en.append(en_meta(p["datum"]))
            if p.get("minuten"):
                parts_de.append("%s min" % p["minuten"])
                parts_en.append("%s min" % p["minuten"])
            pairs[" · ".join(parts_de)] = " · ".join(parts_en)
        i += width
    pairs["%d Beiträge seit %s" % (total, first_year)] = \
        "%d posts since %s" % (total, first_year)
    # A bare number is not copy — build-i18n.py needs two adjacent letters to
    # call a run translatable — so only the two-number form needs an entry.
    if len(posts) != total:
        pairs["%d von %d" % (len(posts), total)] = "%d of %d" % (len(posts), total)
    if pages > 1:
        pairs["Seite 1 von %d" % pages] = "Page 1 of %d" % pages
        for n, label, _ in page_links(pages):
            pairs[label] = ("Page %d, last page" % n if "letzte" in label
                            else "Page %d" % n)
    return pairs


# WHAT THIS SCRIPT WROTE LAST TIME, so it knows what it may take back.
#
# The first two versions inferred ownership — by the shape of the key, then by
# whether a post still carried the title — and both were wrong in the same
# direction. Shapes are not ownership: "Seite 1 von 3" is another list's
# pagination and "Beitrag · 01.01.2025" is the article page's byline. And a
# title can only be recognised while its post exists, so DELETING a post left
# its entry behind for the next build to fail on — the one moment the admin most
# needs the tool to keep up.
#
# A ledger says it outright. It is written beside the posts because it is a fact
# about them, it is generated like every other output in this repository, and it
# turns "which of these entries are mine" from a guess into a read.
LEDGER = POSTS / ".catalogue.json"


def strings_used_elsewhere():
    """Every catalogue key some OTHER German pattern page actually shows.

    build-i18n.py is imported rather than copied: it owns the definition of a
    translatable run — which regions are opaque, which attributes carry copy,
    what counts as a word — and two definitions of that would drift the first
    time one of them learned something.

    This page is excluded from the sweep. Its strings are exactly what `pairs`
    holds, and the copy on disk is the version being replaced; counting it would
    make every retired string look like one still in use.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "cf_build_i18n", pathlib.Path(__file__).with_name("build-i18n.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # load_catalogue() returns the flat table AND the per-page overrides, and
    # build() wants the merged view for the page it is given — for_page() is
    # what merges them. Passing the raw table instead makes every lookup miss,
    # which marks nothing as used and would prune the whole catalogue.
    cat, overrides = mod.load_catalogue()
    before = set(mod.USED)
    # ITS LIST OF PAGES AND NOT A GLOB. The article pages are generated in both
    # editions by build-articles.py and build-i18n.py never translates them, so
    # a string that survives only there is unused as far as that file is
    # concerned — and it fails the build on an entry nothing uses. Keeping one
    # alive here would be this script arranging for the next one to fail.
    for page in mod.source_pages():
        if page == PAGE:
            continue
        # missing is collected and dropped: another page's untranslated string
        # is that page's problem, and build-i18n.py reports it by name.
        mod.build(page.read_text(encoding="utf-8"), page.name,
                  mod.for_page(cat, overrides, page.name), set())
    used = set(mod.USED) - before
    return used


def catalogue(pairs, posts, write):
    """Add what the page now shows, remove what it no longer shows.

    BOTH ENDS, and the second one is not tidiness. build-i18n.py fails on an
    entry that matches no string on any page — "an entry nothing asked for is
    nearly always a key typed slightly wrong" — which is right for a catalogue
    people write by hand and impossible for one a generator feeds: every post
    that lands changes the counter, moves a card out of the lead column and
    pushes the oldest post off the last page, and each of those retires a
    string. Left behind, they fail the next build, and the admin this whole
    script exists for gets a red build for adding a post.

    So the pruning is narrow and stated: a key goes only if the page no longer
    shows it AND it is either one of the derived forms above or the German title
    of a post in content/news/. A string that is neither is somebody else's.
    """
    data = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    added = {k: v for k, v in pairs.items() if data.get(k) != v}
    owned = set(json.loads(LEDGER.read_text(encoding="utf-8"))) if LEDGER.exists() else set()

    # AND IT HAS TO BE UNUSED EVERYWHERE, not merely unused here. The first
    # version of this pruned by shape alone and took four entries other pages
    # need with it: "Beitrag · 01.01.2025" is the article page's byline,
    # "Simon Deussen · 01.01.2026 · 4 min" is a card on the landing page, and
    # "Seite 1 von 3" belongs to another paginated list. A news-shaped string is
    # not a news-owned string.
    #
    # ASKED OF build-i18n.py RATHER THAN GUESSED, and the second version of this
    # is why. Searching the pages for the string is the obvious test and it is
    # wrong in both of the ways that matter here: "189 Beiträge seit 2022"
    # survives in news-thema.html only inside an HTML COMMENT, which is not copy
    # and is never translated, and "Seite 3" survives only as a substring of
    # another page's `aria-label="Seite 3, letzte Seite"`. Both would be kept by
    # a grep and both are dead — and a dead entry fails the next build. The
    # extractor that decides what "used" means already exists one file over, so
    # this asks it instead of reimplementing its judgement badly.
    used = strings_used_elsewhere()

    stale = sorted(k for k in owned
                   if k in data and k not in pairs and k not in used)
    if write:
        if added or stale:
            for k in stale:
                del data[k]
            data.update(added)
            CATALOGUE.write_text(
                json.dumps(dict(sorted(data.items())), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8")
        ledger = json.dumps(sorted(pairs), ensure_ascii=False, indent=2) + "\n"
        if not LEDGER.exists() or LEDGER.read_text(encoding="utf-8") != ledger:
            LEDGER.write_text(ledger, encoding="utf-8")
    elif sorted(pairs) != sorted(owned):
        # --check: the ledger is an output too, and a stale one hides exactly
        # the entries the next build would have to clean up.
        stale = sorted(set(owned) ^ set(pairs)) or stale
    return added, stale


# --------------------------------------------------------------------------

def build():
    posts = read_posts()
    pages = (len(posts) + PER_PAGE - 1) // PER_PAGE
    first = posts[:PER_PAGE]
    html = PAGE.read_text(encoding="utf-8")
    html = splice(html, "meta", meta(posts, pages))
    html = splice(html, "count", count(len(first), len(posts)))
    html = splice(html, "cards", cards(first))
    html = splice(html, "axis", axis(first))
    html = splice(html, "pages", pagination(pages))
    return posts, pages, first, html


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="fail if the page or the catalogue is stale")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    posts, pages, first, html = build()
    current = PAGE.read_text(encoding="utf-8")
    missing, stale = catalogue(
        derived(first, len(posts), pages, min(p["datum"][:4] for p in posts)),
        posts, write=not args.check)

    if args.check:
        if html != current:
            fail("design-system/patterns/news.html is stale — content/news/ has "
                 "%d post(s) and the page does not say so.\n"
                 "    run: python3 scripts/build-news.py" % len(posts))
        if missing or stale:
            fail("en.json is out of step with the archive: %d string(s) shown "
                 "have no entry and %d retired one(s) are still there.\n%s\n"
                 "    run: python3 scripts/build-news.py"
                 % (len(missing), len(stale),
                    "\n".join(["      + " + t for t in missing]
                              + ["      - " + t for t in stale])))
        print("news OK — %d post(s), %d page(s), the archive matches content/news/"
              % (len(posts), pages))
        return 0

    if html != current:
        PAGE.write_text(html, encoding="utf-8")
    note = ""
    if missing or stale:
        note = ", catalogue %+d/%-d" % (len(missing), len(stale))
    print("news built — %d post(s) over %d page(s), %d on the first%s"
          % (len(posts), pages, len(first), note))
    if args.verbose:
        for i, p in enumerate(first):
            print("  %2d  %s  %s" % (i + 1, p["datum"], p["titel"]))
        if len(posts) > len(first):
            print("  … %d more on later pages" % (len(posts) - len(first)))
    print("     then: python3 scripts/build-i18n.py && python3 scripts/build-site.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
