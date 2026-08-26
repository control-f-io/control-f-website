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

WHAT IT GENERATES, and nothing else. Five regions of the page, each fenced by a
pair of comments this script owns:

    news:meta    the page header's two mono lines — the post count and, when
                 there is more than one page, which page this is
    news:themen  the topic filter: the section header and one chip per topic,
                 the chip for the state the reader is in drawn as a <span>
    news:count   the Beiträge header's counter
    news:grid    the columns — the lead, then a year each — and the axis under
                 them. One region, because the track count and the height of
                 the port are properties of the element around both
    news:pages   nothing. The archive does not page any more; the fences stay
                 because the specimen keeps its own drawn pagination between
                 them and because a region this script owns is one it can fill
                 again.

Everything else on that page — the section headers, the comments that explain
the composition — is authored and comes through untouched.

AND THE FILTER, WHICH DID NOT WORK. The chips said `news.html?thema=energie`
and nothing served that: the site is static files, a query string changes
nothing about which file comes back, so clicking "Energie" returned the whole
archive with "Alle" still marked as the current state. The page's own comment
promised "der aktive Zustand erkennbar" and news-thema.html drew that state as
a mock-up with thirty-seven invented posts in it.

So the filter is the URL and the URL is a file. Every post declares its topics
(`themen: Energie, Telemetrie`, from the vocabulary in content/themen.json —
the `Themen` property of the Notion database, written out by the sync), and this
script writes one page per topic — `news-thema-<slug>.html`, the posts of that
topic spliced into the same five regions of news-thema.html, which lives in
design-system/patterns/ beside them.
That specimen is to these pages what blog-artikel.html is to beitrag-*.html:
authored, documented, shipped, and read rather than copied. The chips link to
them. No script runs, no server is asked, and the state survives being shared,
bookmarked and reloaded.

AND EVERY OTHER LINK INTO THOSE PAGES, WHICH IS WHY THIS SCRIPT WRITES ON THREE
PAGES AND NOT ONE. A topic page exists only while a post carries the topic —
that is the paragraph above and it is right — so a link to one written by hand
is a link that 404s the day the last post on that subject is unpublished. Two
authored specimens carried three of them each: the chips on news-thema.html and
the tag list under the text on blog-artikel.html, each naming all three topics
of the vocabulary because all three had posts on the day they were drawn. On
2026-08-20 the archive came back from Notion with two posts on two topics and
the build stopped on `blog-artikel.html: news-thema-telemetrie.html is a pattern
name and not an address` — build-site.py's guard doing its job, on a link
nothing had rewritten because the page it named had not moved: it had stopped
existing. Nobody had touched either specimen; the archive had changed under
them, which is the one edit a hand-written link cannot survive.

So the rule is the one the chips on news.html were already an instance of:
EVERY REFERENCE TO A TOPIC PAGE IN design-system/patterns/ IS WRITTEN HERE,
because this is the only script that knows which of those pages exist. Three
pages, one fenced region each, and a topic that loses its last post loses the
links to it in the same run it loses its page. → specimens()

A COLUMN IS A YEAR, AND THE COLUMN SCROLLS. The ticks under this grid have read
Aktuell / 2026 / 2025 / 2024 / 2022–2023 since it was drawn, and until now they
were labels over whatever eighteen cards happened to land there: the cards were
poured in by count — 1, 2, 3, 6, 6 — and post nineteen went to page two, under a
tick that said the same year as page one's.

Now the tick is the truth. The newest post is the lead; every post after it
stands in the column of its own year; the last column holds every year older
than the four that fit, which is why its tick is a range. Nothing falls off the
page — the grid is a port twice the height it used to draw and each column
scrolls its own year — so the pagination is gone with the pages it counted.

What 1, 2, 3, 6, 6 still says is how a column DRAWS: "von aktuell nach alt und
von ausführlich nach knapp", which is why the lead card carries its author and a
picture and the compact ones carry nothing but a title.

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
PATTERNS = ROOT / "design-system" / "patterns"
PAGE = PATTERNS / "news.html"
# The filtered archive's specimen, and the file every topic page is spliced
# from — the same relationship blog-artikel.html has to beitrag-<name>.html.
THEMA = PATTERNS / "news-thema.html"
# The article specimen, which links into the same pages from under its text: a
# post's topics are its way back into the archive narrowed to them.
# build-articles.py writes that list for every post page it generates, out of
# the post's own topics — which are topics in use by definition, so those links
# cannot dangle. The specimen has no post and its list is the vocabulary, so its
# list is written here. → specimens()
ARTICLE = PATTERNS / "blog-artikel.html"
CATALOGUE = ROOT / "design-system" / "i18n" / "en.json"
# The topic vocabulary, and the reason it is a file rather than a literal is
# below. → vocabulary()
VOCABULARY = ROOT / "content" / "themen.json"

# THE FIVE COLUMNS' RANKS, which is their presentation and no longer their
# length. 1, 2, 3, 6, 6 is what the .cf-blog-col--N classes lay out — the lead
# card with its author, two columns of cards with a text block, two of single
# lines — "von aktuell nach alt und von ausführlich nach knapp". How MANY posts
# stand in a column is the column's year's business now; the rank says how they
# are drawn. → columns()
RANKS = (1, 2, 3, 6, 6)

# A field this script reads. Everything else in a post file is ignored rather
# than rejected, so a later run can add a body without this one having to know.
#
# `themen` is required for the same reason both titles are. A post with no topic
# stands under no chip: it is in the archive, it is in nobody's filtered view,
# and nothing on any page says so — the reader who clicks "Energie" is simply
# not shown it. An optional field would make that the default, and the default
# would be silent.
REQUIRED = ("datum", "titel", "title", "themen")

# WHERE THE GERMAN TEXT ENDS AND THE ENGLISH BEGINS. A post is one file in two
# languages, the same way its two titles are two fields of one record: the site
# ships both editions, and a post that exists in one of them is a page with a
# German paragraph in the middle of the English archive. The divider is what
# Notion's own divider block imports as, so an admin writing there types
# nothing — they draw a line.
DIVIDER = re.compile(r"^ {0,3}-{3,}\s*en\s*-{3,}\s*$", re.M | re.I)

# A PICTURE, written the way every editor writes one: `![caption](path)`. The
# path is relative to design-system/assets/img/, because that is where the file
# is and a post file should not have to know how many `../` a pattern page is
# from its assets — build-articles.py writes that, once, for the page it is on.
# The file itself is in the repository: scripts/sync-news-notion.py downloads
# what Notion holds, since a Notion file URL is signed and expires within the
# hour, and a site that hot-linked one would show a broken image by lunchtime.
PICTURE = re.compile(r"!\[(.*?)\]\(([^)\s]+)\)")

# Where those files live, and the one place they live.
IMAGES = ROOT / "design-system" / "assets" / "img" / "news"

# THE TITLE PICTURE, and it is a field rather than a block. `bild: news/x.jpg`
# names the one picture that stands for the whole post — the card in the archive
# is drawn from it. It is not the first picture of the text: a post can open on
# a diagram that says nothing at thumbnail size, and a post with no text at all
# still has a card to fill. In Notion it is the `Titelbild` property, which is
# how an admin says "this one" without the archive having to guess.
#
# NO CAPTION AND alt="". A picture in the running text carries one, because
# there the caption IS the description and nothing else on the page says what is
# in the image. On a card the picture sits inside the link whose text is the
# headline: a screen reader already reads the post's title, and an alt
# describing the photograph would read the card twice. That is the W3C's own
# "decorative by context", and it is the reason this field is a path and not a
# pair. → design-system/components/blog-grid.html
IMAGE_FIELD = "bild"

REGION = "<!-- news:%s -->"
REGION_END = "<!-- /news:%s -->"

# THE OTHER SCRIPT'S FENCES, and not a second set beside them. The tag list
# under blog-artikel.html's text is `article:tail`, build-articles.py's region
# on every page it writes — this script fills it on the one page that script
# reads instead of writes, which is the specimen. One region, one shape, two
# writers who never meet on the same file. → specimens()
ARTICLE_REGION = ("<!-- article:%s -->", "<!-- /article:%s -->")


def fail(msg):
    print("build-news: " + msg)
    sys.exit(1)


# --------------------------------------------------------------------------
# THE TOPICS, WHICH ARE A VOCABULARY AND NOT FREE TEXT — AND NOT A LITERAL HERE
# --------------------------------------------------------------------------
#
# A post picks a topic from a closed list; it does not invent one. Free text
# would give the archive a chip per spelling — "Telemetrie", "telemetrie",
# "Telemetrik" — and a filter whose controls are typos is worse than none, which
# is the fault this whole file exists to stop making with numbers.
#
# WHAT CHANGED IS WHERE THE LIST IS KEPT. It was three names written into this
# file, and a fourth was deliberately a code edit here — which was right while
# the archive was eighteen cards somebody had drawn, and stopped being right the
# day the archive started arriving from Notion. The names are not this
# generator's: they are the options of the `Themen` multi-select on the news
# database, and adding one there is something an admin does between two posts,
# in the same window they write the post in. With the list in here, that admin
# could invent a topic, tag a post with it, watch the sync carry the tag over
# faithfully — and get a red build on a topic nothing could draw a chip for,
# whose fix was a pull request against a script.
#
# So the vocabulary is content/themen.json, scripts/sync-news-notion.py writes
# that file out of the property, and this reads it. The same store-and-generator
# split content/news/ already is, for the same reason: one place to author, one
# place to lay out, and no third place that has to be edited in step.
#
# FOUR STRINGS PER TOPIC, because a topic is written in four places and two of
# them are English. The slug is the file name and never seen; the German name is
# the chip; the English name is the chip in the other edition; and the English
# PROSE form is the same word inside a sentence, where the catalogue has always
# set it lower case — "Posts by Control-F on telemetry" was written by hand in
# en.json long before anything generated it, and a generator that wrote
# "on Telemetry" would be a second idiom in the same file.


def vocabulary():
    """content/themen.json → the topic records, in the order that file lists them.

    THE ORDER IS THE CHIPS' ORDER, and it is Notion's. A filter is a fixed set
    of controls and a control that moves is a control nobody learns, so the
    chips stand in the vocabulary's order rather than in each post's — and the
    vocabulary's order is the order the options stand in on the property, where
    somebody can drag them into the one they mean.

    TWO ENGLISH FORMS OUT OF ONE STRING. `en` is the word as it stands inside a
    sentence — "8 posts on telemetry" — and the chip is that word with a capital
    first letter. One string rather than two because two would be two fields
    holding the same word, and the day they disagreed the chip and the sentence
    under it would be about different subjects. Derived in this direction and
    not the other: capitalising "telemetry" gives "Telemetry", which is what the
    catalogue has held by hand since before anything generated it, while
    lower-casing a chip gives "ai act" the first time a topic is a proper noun.

    AN EMPTY `en` IS A TOPIC THE VOCABULARY HOLDS AND THE ARCHIVE CANNOT DRAW,
    and it is not an error here. It is the state a topic arrives in from Notion,
    which has nowhere to keep an English name, and a topic no post carries draws
    no chip and needs none. → build(), where it becomes a failure on the day a
    published post carries it, and not before.
    """
    if not VOCABULARY.exists():
        fail("no content/themen.json, so there is no vocabulary to file a post "
             "under.\n"
             "    It is the topic list — one entry per chip on the archive's "
             "filter — and scripts/sync-news-notion.py writes it from the "
             "`Themen` property of the Notion database. It is tracked, so a "
             "checkout has it; `git checkout content/themen.json` brings it "
             "back.")
    try:
        data = json.loads(VOCABULARY.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fail("content/themen.json is not readable as JSON: %s" % e)
    out, seen = [], {}
    for i, rec in enumerate(data.get("themen") or [], 1):
        if not isinstance(rec, dict):
            fail("content/themen.json, entry %d is %r and not a topic. A topic "
                 "is an object: a slug, a German name, and the English word "
                 "beside it." % (i, rec))
        s, de, en = (str(rec.get(k) or "").strip() for k in ("slug", "de", "en"))
        if not de or not s:
            fail("content/themen.json, entry %d has %s. A topic is the German "
                 "name the chip carries and the slug its page is read at, and "
                 "neither is optional."
                 % (i, "no slug" if de else ("no name" if s else "neither")))
        if "," in de:
            # `themen: Energie, Telemetrie` is a comma-separated line, so a name
            # with a comma in it is two topics as far as a post file is
            # concerned. Notion refuses one in an option name for the same
            # reason; this is the guard for the hand edit that Notion cannot see.
            fail("content/themen.json: the topic %r has a comma in it.\n"
                 "    A post lists its topics on one comma-separated line, so "
                 "that name is two topics the moment it is written down." % de)
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", s):
            fail("content/themen.json: %r is not a slug.\n"
                 "    It is a file name — news-thema-%s.html — and an address "
                 "with a capital, an umlaut or a space in it is one that half "
                 "the web serves differently from the other half." % (s, s))
        if s in seen:
            fail("content/themen.json: %r and %r both slug to %r, so both "
                 "topics would be read at one address and one of the two pages "
                 "would be the other's." % (seen[s], de, s))
        seen[s] = de
        out.append((s, de, en[:1].upper() + en[1:], en))
    if not out:
        fail("content/themen.json lists no topic, so no post can be filed and "
             "the archive has no filter to draw.\n"
             "    That is what an emptied `Themen` property in Notion looks "
             "like from here — every post carries a topic, so it is also what "
             "no post being buildable looks like.")
    return tuple(out)


TOPICS = vocabulary()

BY_NAME = {t[1].lower(): t for t in TOPICS}


# --------------------------------------------------------------------------
# the store
# --------------------------------------------------------------------------

def blocks(text, where):
    """A post's text → the blocks it is made of, in order.

    THE SMALLEST GRAMMAR THAT NOTION EMITS, and deliberately no larger. A post
    is written in an editor — Notion for an admin, a text editor for anyone
    else — and every form below is one the editor already has a button for:
    a paragraph, two levels of heading, a bulleted list, a numbered list, a
    picture. Anything richer that an article needs — the isometric figures, the
    plot, the table, the pull quote — lives in blog-artikel.html, which is
    written by hand for exactly that reason and is the specimen the generated
    pages take their furniture from.

    Blocks are separated by a blank line, which is what pressing return twice
    already does.
    """
    out = []
    for chunk in re.split(r"\n\s*\n", text.strip()):
        lines = [ln.strip() for ln in chunk.strip().splitlines() if ln.strip()]
        if not lines:
            continue
        pic = PICTURE.fullmatch(" ".join(lines))
        if pic:
            # THE CAPTION IS NOT OPTIONAL, and the empty-alt below is why. A
            # figure with a caption beside it does not repeat itself into alt
            # text — the W3C figure pattern, and what .cf-prose figcaption is
            # already styled for — so the caption IS the description. Written
            # nowhere, the picture is a hole in the page for anyone who cannot
            # see it, and there is no second field to fall back to.
            path, caption = pic.group(2).strip(), pic.group(1).strip()
            if not caption:
                fail("%s: the picture %s has no caption.\n"
                     "    It is the line under the image and it is also what "
                     "stands in for the image itself — nothing else on the page "
                     "says what is in it." % (where, path))
            out.append(("img", (path, caption)))
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
    # THE PICTURES ARE IN BOTH EDITIONS OR THE READER OF ONE IS SHOWN LESS.
    # Each edition carries its own image block, because each carries its own
    # caption — the caption is the description, and a German sentence under a
    # photograph on the English page is the fault the catalogue exists to
    # prevent. The FILE is shared: the same picture in both halves downloads
    # once and is written once.
    pics_de = [p for k, (p, _) in ((k, v) for k, v in de if k == "img")]
    pics_en = [p for k, (p, _) in ((k, v) for k, v in en if k == "img")]
    if len(pics_de) != len(pics_en):
        fail("%s: %d picture(s) in the German text and %d in the English.\n"
             "    Both editions ship, so a picture belongs in both halves — in "
             "Notion, copy the image block below the divider and write its "
             "caption in English." % (where, len(pics_de), len(pics_en)))
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
            fail("%s has no %s. Every post needs a date, both titles and at "
                 "least one topic." % (path.name, " and no ".join(missing)))
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", post["datum"]):
            fail("%s: datum is %r, not YYYY-MM-DD." % (path.name, post["datum"]))
        post["topics"] = topics(post["themen"], path.name)
        post["bild"] = title_picture(post, path.name)
        out.append(post)
    if not out:
        fail("content/news/ is empty. scripts/new-post.py writes the first post.")
    # Newest first, and the filename breaks a tie so the order is stable rather
    # than filesystem-dependent — two posts on one day must not swap places
    # between two runs of this script.
    out.sort(key=lambda p: (p["datum"], p["file"]), reverse=True)
    return out


def topics(field, where):
    """`themen: Energie, Telemetrie` → the topic records, in the order written.

    The order is the writer's and is kept: the first topic is the one the post
    is most about, and it is the first chip under the article. The chips on the
    archive are in the vocabulary's own order instead, because a filter is a
    fixed set of controls and a control that moves is a control nobody learns.

    An unknown name is a failure and never a skip. A typo'd topic silently drops
    the post out of the one view a reader would look for it in, and the page it
    should have been on renders perfectly without it.
    """
    seen, out = set(), []
    for name in (n.strip() for n in field.split(",")):
        if not name:
            continue
        rec = BY_NAME.get(name.lower())
        if not rec:
            fail("%s: %r is not one of the topics.\n"
                 "    The vocabulary is %s — a post picks from it, the chips on "
                 "news.html are drawn from it, and a name outside it would be a "
                 "chip nobody drew.\n"
                 "    It is content/themen.json, and it is the `Themen` "
                 "property of the Notion database written out: a topic the site "
                 "has genuinely grown is added there, and the next sync brings "
                 "it here."
                 % (where, name, ", ".join(t[1] for t in TOPICS)))
        if rec[0] in seen:
            continue
        seen.add(rec[0])
        out.append(rec)
    if not out:
        fail("%s: themen is empty. Every post carries at least one topic — "
             "without one it stands under no chip and no filtered view lists "
             "it." % where)
    return tuple(out)


def intrinsic(path):
    """A raster file's real pixel size, read from its header.

    scripts/check-image-scale.py owns this — "no decoder, no dependency" — and
    it is imported rather than written again because that file is also the one
    that FAILS on a width/height attribute which disagrees with the file. Two
    readers of a JPEG header would disagree about a progressive scan exactly
    once, and the check would be right and the page would be wrong.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "cf_image_scale", pathlib.Path(__file__).with_name("check-image-scale.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.intrinsic(str(path))


def title_picture(post, where):
    """`bild: news/x.jpg` → (path, width, height), or None.

    THE SIZE IS READ HERE AND WRITTEN ONTO THE CARD. An <img> with no width and
    height reserves no space, so every card below it moves the moment the file
    arrives — the archive is a grid of eighteen of them and the whole page jumps.
    The pair has to be the file's own numbers, which is why it is read out of the
    file rather than typed: scripts/check-image-scale.py fails on a pair that
    disagrees with the header, and it is right to.

    A named file that is not in the repository is a failure and never a card
    without a picture. The page would ship an <img> pointing at a 404, which
    looks like a broken photograph and reads as a broken site — the same finding
    scripts/check-content-images.py calls DANGLING one level down.
    """
    rel = (post.get(IMAGE_FIELD) or "").strip()
    if not rel:
        return None
    path = ROOT / "design-system" / "assets" / "img" / rel
    if not path.is_file():
        fail("%s: bild is %r and design-system/assets/img/%s does not exist.\n"
             "    The path is relative to the image folder, the file belongs in "
             "the repository — scripts/sync-news-notion.py downloads what Notion "
             "holds, because a Notion file URL is signed and expires within the "
             "hour." % (where, rel, rel))
    size = intrinsic(path)
    if not size:
        fail("%s: cannot read the pixel size out of design-system/assets/img/%s. "
             "JPEG, PNG, WebP and GIF are what scripts/check-image-scale.py "
             "reads." % (where, rel))
    return (rel, size[0], size[1])


def with_topic(posts, slug):
    return [p for p in posts if any(t[0] == slug for t in p["topics"])]


def thema_name(slug):
    """The page one topic is read on. `news-thema-<slug>.html`, beside the
    specimen it is spliced from, exactly as `beitrag-<name>.html` is."""
    return "news-thema-%s.html" % slug


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


def columns(page_posts):
    """The posts in their columns: [(rank, posts), …] — the lead, then a year each.

    A COLUMN IS A YEAR, WHICH IS WHAT THE AXIS UNDER IT ALWAYS SAID. The ticks
    have read Aktuell / 2026 / 2025 / 2024 / 2022–2023 since the grid was drawn,
    but the cards above them were poured in by count — one, two, three, six,
    six, eighteen to a page and the rest on page two. The tick was a label over
    whatever eighteen cards happened to land there, and a year that ran long was
    split across two pages under two identical ticks.

    Now the tick is the truth. The newest post is the lead; every post after it
    stands in the column of its own year; and the last column takes every year
    older than the four that fit, which is what makes its tick a range. Nothing
    is left off the page — the column scrolls instead, which is the whole point
    of the port being twice as tall as the tallest column that fits in it.
    → design-system/components/blog-grid.html

    EMPTY COLUMNS ARE NOT DRAWN. A topic is a slice — Architektur is four posts
    across three years — and a fifth column with nothing in it is a grid track
    of nothing under a tick naming an era with no cards over it. grid() sets the
    track count to what is left.
    """
    if not page_posts:
        return []
    rest = page_posts[1:]
    years = []                      # [(year, posts)], newest first
    for p in rest:
        y = p["datum"][:4]
        if not years or years[-1][0] != y:
            years.append((y, []))
        years[-1][1].append(p)
    slots = len(RANKS) - 1          # the columns left after the lead
    buckets = [ps for _y, ps in years[:slots - 1]]
    # THE LAST COLUMN IS EVERYTHING OLDER, and not the fifth year. An archive
    # that started in 2022 has more years than columns from its fourth birthday
    # on, and a column per year would either grow a sixth track — the
    # composition is five — or drop the oldest posts off the page. "2022–2023"
    # is that decision already drawn: the tail is one column and its tick is the
    # range it holds.
    tail = [p for _y, ps in years[slots - 1:] for p in ps]
    if tail:
        buckets.append(tail)
    out = [(RANKS[0], page_posts[:1])]
    out += [(RANKS[i + 1], ps) for i, ps in enumerate(buckets) if ps]
    return out


def grid(page_posts, indent="      "):
    """The subdivision: the card row, the year axis, and the element they sit in.

    ONE REGION AND NOT TWO. The cards and the axis were spliced separately and
    the element around them was authored, which was right while every page drew
    five columns and wrong the moment one drew three: `--late` and the track
    count belong to that element, they are a function of how many columns the
    page actually has, and neither could be written from inside it.

    .subdivide--late is what five columns take — the fold width is a property of
    the column count, base.css carries the measurement — and it is what fewer
    than five must NOT take, which is the same check read backwards.
    → scripts/check-subdivide-late.py
    """
    cols = columns(page_posts)
    if len(cols) >= 5:
        # Five is the primitive's own default count, so it is not written out.
        opens = '<div class="subdivide subdivide--even subdivide--late">'
    else:
        opens = ('<div class="subdivide subdivide--even" style="--subdivide-count:%d">'
                 % len(cols))
    inner = indent + "  "
    return "\n".join([
        indent + opens,
        # --port is the fixed-height scroll port: the archive's grid is twice
        # the height it drew before and each column scrolls its own year. The
        # Weiterlesen grid under an article uses the same .cf-blog-grid and does
        # NOT take it — three cards have nothing to scroll, and a port there
        # would be a fixed height with air under it.
        '%s<div class="cf-blog-grid cf-blog-grid--port subdivide__row">' % inner,
        cards(cols, inner + "  "),
        "%s</div>" % inner,
        '%s<div class="cf-blog-axis subdivide__row" aria-hidden="true">' % inner,
        axis(cols, inner + "  "),
        "%s</div>" % inner,
        indent + "</div>",
    ])


def image(post, width, pad, up="../assets/img/"):
    """The card's title picture, or nothing at all.

    Nothing on a single-line row and nothing for a post that has no picture: a
    card without one is the card this grid has always drawn, and the modifier
    that changes the padding is only worn when there is something to change it
    for. An archive half of whose posts carry a photograph reads as an archive,
    not as a fault — which is why the picture is optional and the layout does
    not reserve a hole for it.

    `loading="lazy"` because eighteen of these stand on one page and five of
    them are below the fold on every viewport this grid opens at; `decoding`
    so a large file cannot hold up the paint of the text beside it.
    """
    if width > 3 or not post.get("bild"):
        return ""
    rel, w, h = post["bild"]
    return ('%s<img class="cf-blog-card__image" src="%s%s" alt=""\n'
            '%s     width="%d" height="%d" loading="lazy" decoding="async">'
            % (pad, up, rel, pad, w, h))


def cards(cols, indent="          "):
    """The columns, in the design's own order and modifiers."""
    lines = []
    for n, take in cols:
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
            # THE PICTURE STOPS WHERE THE ROOM STOPS, which is the same place
            # the byline and the date stop. Columns 1 to 3 are cards with a text
            # block; the last two are single lines 2rem high, and a picture in
            # one of them is a 48 px stamp painted from a file sized for a
            # 1008 px plate — "512,000 source pixels for 3,136 painted ones" is
            # the fault scripts/check-image-scale.py was written for, and it is
            # bytes a reader on a train pays for a thumbnail nobody can read.
            # A second, smaller derivative would fix that; there is no image
            # library in this lane to write one, and inventing a dependency to
            # put a stamp on a one-line row is the wrong trade.
            # → design-system/components/blog-grid.html
            picture = image(p, n, indent + "    ")
            if picture:
                mod += " cf-blog-card--media"
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
            if n == 1 or picture:
                lines.append("%s  %s" % (indent, open_))
                if picture:
                    lines.append(picture)
                lines.append("%s    %s" % (indent, title))
                if meta_html:
                    lines.append("%s    %s" % (indent, meta_html))
                lines.append("%s  %s" % (indent, close))
            else:
                lines.append("%s  %s%s%s%s" % (indent, open_, title, meta_html, close))
        lines.append("%s</div>" % indent)
    return "\n".join(lines)


def axis(cols, indent="          "):
    """One tick per column, naming the era that column holds.

    The newest column is "Aktuell" whatever year it is in — the tick says where
    the reader is in the archive, and the top of an archive is now. Every other
    column is named by the years its own cards carry, which is why a column
    spanning two years reads "2022–2023" on the page today.
    """
    ticks = []
    for k, (n, take) in enumerate(cols):
        years = sorted({p["datum"][:4] for p in take})
        label = "Aktuell" if k == 0 else (
            years[0] if len(years) == 1 else "%s–%s" % (years[0], years[-1]))
        ticks.append('%s<span class="cf-blog-axis__tick">%s</span>' % (indent, label))
    return "\n".join(ticks)


def meta_left(posts, topic=None):
    """The left mono line: what this page holds, and what makes it that.

    "seit YYYY" is the oldest post's year rather than a constant: an archive
    that loses its oldest post stops having started that year. On a filtered
    page the year is replaced by the topic, because the number is no longer the
    archive's age but the slice's size — the page's own note says the two
    editions of that line are the whole difference between the states.

    Singular is written out. "1 Beiträge zum Thema Architektur" is the kind of
    sentence a generator writes and nobody reads back.
    """
    if topic is None:
        return "%d Beiträge seit %s" % (len(posts), min(p["datum"][:4] for p in posts))
    return "%d %s zum Thema %s" % (
        len(posts), "Beitrag" if len(posts) == 1 else "Beiträge", topic[1])


def meta(posts, topic=None, indent="          "):
    """The page header's mono line.

    ONE LINE NOW, WHERE THERE WERE TWO. The right-hand one answered "which page
    am I on", and there are no pages any more: every post stands in its year's
    column and the column scrolls. A reader who wants to know how far the
    archive goes reads the axis under it, which names the years it holds.
    """
    return "%s<span>%s</span>" % (indent, esc(meta_left(posts, topic)))


def head(topic, indent=""):
    """The topic page's <title> and description.

    THE STATE IS IN THE TITLE. suche.html writes its six and suche-leer.html its
    zero into the title for the same reason the page's own note gives: a screen
    reader reads the title first, and "News" alone is the same name for the
    archive and for every slice of it.
    """
    return ('%s<title>Thema %s — News — Control-F</title>\n'
            '%s<meta name="description" content="Beiträge von Control-F zum '
            'Thema %s — der gefilterte Ausschnitt des Archivs, nach Zeit '
            'sortiert.">' % (indent, esc(topic[1]), indent, esc(topic[1])))


def chips(used, active, indent="      "):
    """The topic filter: the section header and one chip per topic.

    THE ACTIVE CHIP IS A <span>. A link to the state the reader is already in
    does nothing, and both pages have said so in their own comments since they
    were drawn — this is the file that finally draws it, on the archive where
    "Alle" is the state and on each topic page where the topic is.

    ONLY TOPICS THAT POSTS CARRY. A chip is a filter, and a filter onto nothing
    is a control that answers with an empty page. The vocabulary can hold a name
    the archive has not used yet; the chips hold the ones it has.

    The count is the number of chips, which is what stands under the header —
    "Alle" included, because it is one of them and the reader counting them
    counts four. → design-system/components/section-header.html
    """
    items = []
    for slug, de, _en, _prose in [(None, "Alle", None, None)] + list(used):
        if slug == active:
            items.append('<li><span class="cf-article__tag" aria-current="page">%s</span></li>'
                         % esc(de))
        else:
            href = "news.html" if slug is None else thema_name(slug)
            items.append('<li><a class="cf-article__tag" href="%s">%s</a></li>'
                         % (href, esc(de)))
    out = ['%s<div class="cf-section-header">' % indent,
           '%s  <h2 class="cf-section-header__label" id="themen">Themen</h2>' % indent,
           '%s  <span class="cf-section-header__count">%d</span>' % (indent, len(items)),
           "%s</div>" % indent,
           '%s<nav aria-label="Nach Thema filtern">' % indent,
           '%s  <ul class="cf-article__tags" role="list">' % indent]
    out += ["%s    %s" % (indent, it) for it in items]
    out += ["%s  </ul>" % indent, "%s</nav>" % indent]
    return "\n".join(out)


def count(shown, total, indent="        "):
    """The Beiträge header's counter: what stands on this page, of what there is.

    Two numbers only while they differ. components/section-header.html publishes
    "a bare count when the unit follows from the label" as its own form, and on
    a single page "18 von 18" is that form with the same number said twice —
    a counter inviting the reader to check an arithmetic that cannot fail.
    """
    text = str(total) if shown == total else "%d von %d" % (shown, total)
    return '%s<span class="cf-section-header__count">%s</span>' % (indent, text)


def splice(html, name, body, where="news.html", fences=(REGION, REGION_END)):
    """Replace one fenced region, keeping the fences.

    A callable body is handed the region's own indentation, which is what a
    block written at the fence's depth needs and what build-articles.py's
    splice() already does with the same fences.
    """
    start, end = fences[0] % name, fences[1] % name
    m = re.search(re.escape(start) + r".*?" + re.escape(end), html, re.S)
    if not m:
        fail("%s has no %s … %s region. The fences are how this script "
             "knows what it owns; restore them." % (where, start, end))
    pad = re.match(r"[ \t]*", html[html.rfind("\n", 0, m.start()) + 1:m.start()]).group(0)
    if callable(body):
        body = body(pad)
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


def derived(posts, total, first_year=None, topic=None):
    """Every string this script writes onto one page, with its English twin.

    THE GENERATOR OWNS THE ENTRIES FOR WHAT THE GENERATOR WRITES, and this is
    the half that only showed up when a nineteenth post was added. The titles
    are copy an admin types, so they belong in the post file. The rest of the
    page's words are *derived* — "19 Beiträge seit 2022", "8 posts on telemetry",
    "Daniel Tremer · 07.08.2026 · 3 min" — and they change with every post that
    lands. Asking a person to add a catalogue entry for each of them would put
    the cost this script exists to remove back on them, one line further down,
    and build-i18n.py would fail the build until they did.

    So they are translated here, mechanically, in the catalogue's own idiom:
    every one of these forms was already in en.json, written by hand, and this
    only keeps writing them.
    """
    pairs = {}
    # THE SAME WALK THE MARKUP MAKES, and not a second description of it: which
    # cards carry a meta line is a property of the column they land in, and
    # columns() is the one place that decides which column a post lands in. Read
    # separately, the two disagreed the first time a year ran long.
    for rank, take in columns(posts):
        for p in take:
            pairs[p["titel"]] = p["title"]
            if rank > 3:
                continue        # a compact card is a title and nothing else
            parts_de, parts_en = [], []
            if rank == 1 and p.get("autor"):
                parts_de.append(p["autor"])
                parts_en.append(p["autor"])      # a name is not translated
            parts_de.append(german(p["datum"]))
            parts_en.append(en_meta(p["datum"]))
            if p.get("minuten"):
                parts_de.append("%s min" % p["minuten"])
                parts_en.append("%s min" % p["minuten"])
            pairs[" · ".join(parts_de)] = " · ".join(parts_en)
    if topic is None:
        pairs["%d Beiträge seit %s" % (total, first_year)] = \
            "%d posts since %s" % (total, first_year)
    else:
        # The topic in a sentence, set the way the catalogue has always set it:
        # the chip is "Telemetry", the sentence is "on telemetry".
        pairs["%d %s zum Thema %s" % (total, "Beitrag" if total == 1 else "Beiträge", topic[1])] = \
            "%d %s on %s" % (total, "post" if total == 1 else "posts", topic[3])
        pairs["Thema %s — News — Control-F" % topic[1]] = \
            "Topic: %s — News — Control-F" % topic[3]
        pairs["Beiträge von Control-F zum Thema %s — der gefilterte Ausschnitt "
              "des Archivs, nach Zeit sortiert." % topic[1]] = \
            "Posts by Control-F on %s — the filtered slice of the archive, " \
            "sorted by date." % topic[3]
    # The counter is a bare number now — every post the archive has stands on
    # the page — and a bare number is not copy: build-i18n.py needs two adjacent
    # letters to call a run translatable. The "18 von 189" form went with the
    # pagination, and so did "Seite 1 von 11".
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


def strings_used_elsewhere(pages_out):
    """Every catalogue key some OTHER German pattern page actually shows.

    build-i18n.py is imported rather than copied: it owns the definition of a
    translatable run — which regions are opaque, which attributes carry copy,
    what counts as a word — and two definitions of that would drift the first
    time one of them learned something.

    THE PAGES THIS SCRIPT WRITES ARE EXCLUDED — news.html and every
    news-thema-<slug>.html. Their strings are exactly what `pairs` holds, and
    the copy on disk is the version being replaced; counting it would make every
    retired string look like one still in use.

    AND THE TWO SPECIMENS ARE READ AS THIS RUN WILL WRITE THEM, which is the
    same sentence pointed at the pages that are only PARTLY this script's.
    news-thema.html and blog-artikel.html are authored, they ship, and most of
    the words in them are their own — so they are counted, not excluded. But one
    region of each is written by this run, and reading the copy on disk counts
    the version being replaced: on 2026-08-20 the tag list under the specimen's
    text still named Energie and Architektur while this run was removing them,
    both entries were kept as "still in use", and build-i18n.py then stopped on
    two catalogue entries that match no string on any page. `pages_out` is what
    is about to be on disk, so it is what is read. → specimens()
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
        if page == PAGE or page.name.startswith("news-thema-"):
            continue
        text = pages_out.get(page)
        if text is None:
            text = page.read_text(encoding="utf-8")
        # missing is collected and dropped: another page's untranslated string
        # is that page's problem, and build-i18n.py reports it by name.
        mod.build(text, page.name,
                  mod.for_page(cat, overrides, page.name), set())
    used = set(mod.USED) - before
    return used


def catalogue(pairs, posts, pages_out, write):
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
    used = strings_used_elsewhere(pages_out)

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

BANNER = (
    "<!-- GENERATED — DO NOT EDIT THIS FILE.\n"
    "     One topic of the news archive, on the filtered surface of\n"
    "     design-system/patterns/news-thema.html. The posts are the ones in\n"
    "     content/news/ that carry `themen: %s`; everything around them is that\n"
    "     page. Change a post or the specimen, then run:\n"
    "\n"
    "         python3 scripts/build-news.py\n"
    "\n"
    "     CI runs `--check`, so an edit made here is lost rather than shipped. -->\n"
)

DOCTYPE = "<!DOCTYPE html>\n"

# The specimen's own name, everywhere it points at itself: the two hreflang
# alternates and the language switch. Matched as an attribute value rather than
# as a string, so the prose above them that discusses news-thema.html by name
# still discusses the file that exists. The optional prefix is the English
# edition's `../` and the German page's `en/`.
SELF = re.compile(r'(href=")((?:\.\./|en/)?)news-thema\.html"')


def render(template, where, posts, page_posts, total, used, topic, pairs):
    """One page of the archive — the whole of it, or one topic's slice.

    ONE FUNCTION FOR BOTH STATES, because they are one page in two states and
    the pages say so themselves: same title, same composition, same columns.
    What differs is four strings and which chip is a <span> — and a second
    function would be the place those four quietly became six.
    """
    doc = template
    if topic is not None:
        # Only the topic page carries a generated head: the archive's title and
        # description are authored, and there is nothing in them that changes
        # when a post lands.
        doc = splice(doc, "head", head(topic), where)
    doc = splice(doc, "meta", meta(page_posts, topic), where)
    doc = splice(doc, "themen", chips(used, topic[0] if topic else None), where)
    doc = splice(doc, "count", count(total, total), where)
    doc = splice(doc, "grid", grid(page_posts), where)
    # NOTHING IN THE PAGINATION REGION, AND NOTHING TO PUT THERE. The archive
    # does not page any more: the columns are years and they scroll, so there is
    # no second page to step to and no "Seite 1 von 11" to state. The fences
    # stay because the specimen keeps its own drawn pagination between them —
    # that page is where the component is documented — and because a region this
    # script owns is a region this script can fill again.
    doc = splice(doc, "pages", "", where)
    pairs.update(derived(
        page_posts, total,
        first_year=min(p["datum"][:4] for p in posts) if topic is None else None,
        topic=topic))
    return doc


# --------------------------------------------------------------------------
# the two specimens, which link into the topic pages by name
# --------------------------------------------------------------------------

# The chip a filtered page draws for the state the reader is already in. It is
# the one place the specimen says which topic it is a specimen of.
CURRENT = re.compile(
    r'<span class="cf-article__tag" aria-current="page">([^<]*)</span>')


def own_topic(html):
    """The topic news-thema.html draws itself in, read off the page.

    THE SPECIMEN ALREADY SAYS WHICH STATE IT IS A SPECIMEN OF, and it says it
    in the chip it draws as a <span> — "ein Link auf den Zustand, in dem man
    schon ist, tut nichts" is that page's own comment and the span is that rule
    drawn. Reading the topic back out of it is what keeps the two from
    disagreeing: somebody redrawing the specimen for another topic changes the
    word they can see, and the chips beside it follow.
    """
    m = CURRENT.search(html)
    name = m.group(1).strip().lower() if m else ""
    if name not in BY_NAME:
        fail("design-system/patterns/news-thema.html draws no current chip for "
             "any of %s.\n"
             "    It is the specimen of one topic's filtered state, and the "
             "<span aria-current=\"page\"> is what names that topic — this "
             "script reads it to write the chips beside it."
             % ", ".join(t[1] for t in TOPICS))
    topic = BY_NAME[name]
    # AND THE SPECIMEN SHIPS, so its chip is a shipped string in both editions
    # even on the day no post carries the topic it draws. build() checks the
    # topics with posts; this is the one that has a chip without them.
    if not topic[3]:
        fail("design-system/patterns/news-thema.html is drawn in %r, and "
             "content/themen.json has no English name for it.\n"
             "    The specimen ships as itself in both editions, so that chip "
             "is a string /en/news-thema.html shows — write the English word "
             "beside the German one, as it stands inside a sentence." % name)
    return topic


def tags(topics, pad):
    """The tag list under an article's text: one link per topic, into the
    archive filtered to it.

    The markup is build-articles.py's tags(), because this is the page that
    script reads to write it — the specimen is the template, and a template
    whose own version of a region is shaped differently from the generated one
    is a difference that only shows up in a diff nobody runs.
    """
    out = ['%s<ul class="cf-article__tags">' % pad]
    for slug, de, _en, _prose in topics:
        out.append('%s  <li><a class="cf-article__tag" href="%s">%s</a></li>'
                   % (pad, thema_name(slug), esc(de)))
    out.append("%s</ul>" % pad)
    return "\n".join(out)


def specimens(thema, used, pairs):
    """The two authored pages that name topic pages, holding them to the topic
    pages that exist. Returns {path: text}.

    ONE REGION EACH AND NOTHING ELSE. Both pages stay what they are — a drawn
    mock-up of the filtered archive with thirty-seven invented posts in it, and
    an article with a specimen's text under a specimen's byline. Neither is
    generated and neither becomes generated here: what is written is the list
    of links out of them, which is the only thing on either page whose
    correctness is a property of content/news/ rather than of the drawing.
    """
    own = own_topic(thema)
    # THE ACTIVE CHIP IS A <span>, so the specimen may name a topic that has no
    # page — and it has to be able to. Which topic it draws is a property of the
    # drawing; which topics have posts is a property of the archive, and the day
    # those disagree the specimen must keep its subject rather than lose its
    # current state. Every chip beside it is a link, and a link cannot.
    shown = tuple(t for t in TOPICS if t in used or t == own)
    # And its word is a string this script writes, so this script owns its
    # entry in the catalogue — including on the day the topic has no posts, when
    # `pairs` alone would not carry it and build-i18n.py would stop on a German
    # word with no English one.
    pairs[own[1]] = own[2]
    out = {THEMA: splice(thema, "themen",
                         lambda pad: chips(shown, own[0], pad), THEMA.name)}

    if not ARTICLE.exists():
        fail("no design-system/patterns/blog-artikel.html to write the tag list "
             "on. It is the article specimen, it ships as itself, and the tags "
             "under its text are links into the topic pages.")
    out[ARTICLE] = splice(ARTICLE.read_text(encoding="utf-8"), "tail",
                          lambda pad: tags(used, pad), ARTICLE.name,
                          fences=ARTICLE_REGION)
    return out


def build():
    """Every page this script writes, and every string it puts on them.

    Returns (posts, {path: text}, pairs).
    """
    posts = read_posts()

    # THE CHIPS ARE THE TOPICS POSTS CARRY, in the vocabulary's order. A topic
    # nothing is filed under gets no chip and no page: the control would answer
    # with an empty archive, and an empty archive under a chip reads as "we have
    # written nothing about this" — which is true, and is not what a filter is
    # for saying.
    used = tuple(t for t in TOPICS if with_topic(posts, t[0]))
    if not used:
        fail("no post carries a topic, so there is no filter to draw.\n"
             "    Every post file has a `themen:` line; the vocabulary is %s."
             % ", ".join(t[1] for t in TOPICS))

    # A TOPIC BEING DRAWN IS A TOPIC THAT NEEDS ITS ENGLISH WORD, and this is
    # the only moment it does. The vocabulary comes from Notion, where a
    # multi-select option is a name, an id and a colour and there is nowhere to
    # put a translation, so a topic invented there arrives with `en` empty —
    # which is fine and invisible until a published post carries it. From that
    # post on the site owes four English strings it does not have: the chip on
    # /en/news.html, the chip under the article, the topic page's title, and the
    # sentence "8 posts on …" under its header. Falling back to the German word
    # would put a German chip and a half-German sentence into the English
    # edition — precisely the page the catalogue exists to prevent — so this
    # stops instead, and says where the word goes.
    untranslated = [t for t in used if not t[3]]
    if untranslated:
        fail("content/themen.json has no English name for %s, and %s.\n"
             "    Notion cannot hold one — a multi-select option is a name and "
             "a colour — so the sync writes the topic with `en` empty and this "
             "is where it is filled in: the word as it stands INSIDE a "
             "sentence, \"telemetry\" beside \"Telemetrie\". The chip is that "
             "word with a capital, so there is only the one to write.\n"
             "    Until then the English archive would carry a German chip and "
             "a description reading \"Posts by Control-F on %s\"."
             % (", ".join(repr(t[1]) for t in untranslated),
                "a published post carries it"
                if len(untranslated) == 1 else "published posts carry them",
                untranslated[0][1]))

    # The chip labels are the generator's now, because the vocabulary is: adding
    # a fourth topic must not mean a red build until somebody also writes its
    # English name into the catalogue by hand.
    pairs = {de: en for _slug, de, en, _prose in used}
    out = {}

    out[PAGE] = render(PAGE.read_text(encoding="utf-8"), PAGE.name,
                       posts, posts, len(posts), used, None, pairs)

    if not THEMA.exists():
        fail("no design-system/patterns/news-thema.html to build the filtered "
             "pages from. It is the specimen of that state, and it is authored.")
    specimen = THEMA.read_text(encoding="utf-8")
    for topic in used:
        name = thema_name(topic[0])
        slice_ = with_topic(posts, topic[0])
        doc = render(specimen, name, posts, slice_, len(slice_), used, topic, pairs)
        doc = SELF.sub(lambda m: '%s%s%s"' % (m.group(1), m.group(2), name), doc)
        if not doc.startswith(DOCTYPE):
            fail("design-system/patterns/news-thema.html does not begin with a "
                 "doctype")
        out[PATTERNS / name] = DOCTYPE + BANNER % topic[1] + doc[len(DOCTYPE):]

    # AND THE PAGES THAT LINK AT THEM FROM OUTSIDE THE ARCHIVE. Last, because
    # both are read above — news-thema.html as the template every page in the
    # loop is spliced from, blog-artikel.html as nothing at all until here.
    out.update(specimens(specimen, used, pairs))
    return posts, out, pairs


def owned_pages():
    """Every topic page on disk, in both editions.

    The English ones are build-i18n.py's output and are removed here anyway: a
    topic that loses its last post loses its German page in this run, and an
    English page whose German source is gone is a page nothing generates and
    nothing can check.
    """
    return sorted(list(PATTERNS.glob("news-thema-*.html"))
                  + list((PATTERNS / "en").glob("news-thema-*.html")))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="fail if a page or the catalogue is stale")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    posts, pages_out, pairs = build()
    missing, stale = catalogue(pairs, posts, pages_out, write=not args.check)
    # The count this reports is the topic pages, which is no longer everything
    # this script writes minus news.html: two authored specimens are written
    # too, and they are not a topic and must not be counted as one. → specimens()
    topics_out = sum(1 for q in pages_out if q.name.startswith("news-thema-"))

    written, drift = [], []
    for path, text in sorted(pages_out.items()):
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current == text:
            continue
        if args.check:
            drift.append("%s %s" % ("MISSING  " if current is None else "STALE    ",
                                    path.relative_to(ROOT)))
        else:
            path.write_text(text, encoding="utf-8")
            written.append(path.relative_to(ROOT))

    # A TOPIC PAGE WHOSE TOPIC IS GONE. The last post filed under a topic can be
    # unpublished, and the page has to go with it — otherwise the site serves a
    # filtered archive with nothing in it at an address the chips no longer name.
    live = {q.name for q in pages_out}
    orphans = [p for p in owned_pages() if p.name not in live]
    for p in orphans:
        if args.check:
            drift.append("ORPHAN    %s — no topic writes it" % p.relative_to(ROOT))
        else:
            p.unlink()

    if args.check:
        if drift:
            fail("the news archive does not match content/news/:\n%s\n"
                 "    run: python3 scripts/build-news.py"
                 % "\n".join("      " + d for d in drift))
        if missing or stale:
            fail("en.json is out of step with the archive: %d string(s) shown "
                 "have no entry and %d retired one(s) are still there.\n%s\n"
                 "    run: python3 scripts/build-news.py"
                 % (len(missing), len(stale),
                    "\n".join(["      + " + t for t in missing]
                              + ["      - " + t for t in stale])))
        print("news OK — %d post(s), %d topic page(s), the archive matches "
              "content/news/" % (len(posts), topics_out))
        return 0

    note = ""
    if missing or stale:
        note = ", catalogue %+d/%-d" % (len(missing), len(stale))
    print("news built — %d post(s), %d topic page(s)%s"
          % (len(posts), topics_out, note))
    for r in written:
        print("  written  %s" % r)
    for p in orphans:
        print("  removed  %s" % p.relative_to(ROOT))
    if args.verbose:
        for rank, take in columns(posts):
            print("  column of %d, rank %d:" % (len(take), rank))
            for p in take:
                print("    %s  %-12s %s"
                      % (p["datum"], ",".join(x[0] for x in p["topics"]), p["titel"]))
    # NOT A SHORTER SEQUENCE TYPED HERE. This line used to name build-i18n.py and
    # build-site.py and stop, which skips build-articles.py — so a post whose text
    # had just changed kept yesterday's reading page, and the miss surfaced as a
    # red --check rather than as anything a person could see. build-all.sh is the
    # one complete statement of the order and is cheap to re-run.
    print("     then: sh scripts/build-all.sh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
