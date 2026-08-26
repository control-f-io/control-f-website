#!/usr/bin/env python3
"""Write a new post into content/news/, ready to fill in.

    python3 scripts/new-post.py "Wärmepumpen im Winter"
    python3 scripts/new-post.py "Titel" --datum 2026-02-01 --autor "Simon Deussen"

It writes ONE file and prints the two commands that put it on the site. That is
the whole tool: the archive's layout, its counters, its year axis and its
pagination are build-news.py's job, and an admin adding a post should not have
to know that the columns are 1/2/3/6/6 or that the page ships in two languages.

THE FILE IS THE POST, and its shape is deliberately the smallest thing that can
be read by a person and by a script:

    datum:   2026-02-01          required, YYYY-MM-DD. Sorts the archive.
    autor:   Simon Deussen       optional. Only the lead card has room to show it.
    minuten: 4                   optional. Reading time, as the cards state it.
    themen:  Energie, Telemetrie required. One or more names from
                                 content/themen.json — the chips on the archive.
    bild:    news/anlage.jpg     optional. The post's title picture: the card in
                                 the archive is drawn from it. The file lives in
                                 design-system/assets/img/ and the path is
                                 relative to it, exactly as a picture in the
                                 text is written. No caption and no alt text —
                                 the card's link already reads the headline.
    titel:   Wärmepumpen im …    required. German — what the reader sees.
    title:   Heat pumps in …     required. English — the other edition.

    (a blank line ends the header; everything after it is the text)

THE TEXT IS THE POST'S PAGE. A post that has one gets `beitrag-<name>.html` —
scripts/build-articles.py splices it into the reading surface of
blog-artikel.html — and its card in the archive links there. A post with no
text is a listing and stays one: its card is drawn as a <span>, because a card
that opens somebody else's article is worse than a card that opens nothing.

It is written in both languages, in this one file, divided by `--- en ---` on a
line of its own. Paragraphs are separated by a blank line; `## ` is a section
heading, which is what the contents rail on the left is built from; `- ` is a
bulleted list and `1. ` a numbered one; `![Bildunterschrift](news/datei.jpg)`
on its own line is a picture, drawn as a full-width plate with its caption
under it; `**bold**`, `` `code` `` and `[text](page.html)` work inside a
paragraph. That is the whole grammar, and it is the whole grammar on purpose —
it is what Notion's blocks import as, and an article that needs more than it
belongs on the hand-written specimen.

A picture's caption is required, because the `<img>` carries `alt=""` and the
caption is what stands in for the picture for a reader who cannot see it. The
file goes in design-system/assets/img/news/ and has to fit the plate it is
drawn on — scripts/check-content-images.py carries the numbers and the reasons.

WHY THE TOPICS ARE REQUIRED. They are the filter. Each one is a chip on
news.html and a page of its own — news-thema-<slug>.html, one topic's slice of
the archive — and a link under the finished article back into it. A post with no
topic is in the archive and in nobody's filtered view, and no page says so: the
reader who clicks "Energie" is simply not shown it. The vocabulary is closed and
it is content/themen.json — the `Themen` property of the Notion news database,
written out by scripts/sync-news-notion.py — and build-news.py refuses a name
outside it rather than minting a chip nobody drew. A topic the site has genuinely
grown is added in Notion, not here.

WHY BOTH TITLES ARE REQUIRED and not defaulted. Every pattern page ships twice
and build-i18n.py fails on a German string with no English counterpart, on
purpose: the alternative is an English page with one German sentence in the
middle of it. A post is copy, so a post carries both. Writing the German title
into the English field to get past the check would ship exactly the page that
rule exists to prevent — so this tool leaves `title:` empty and build-news.py
refuses to build until it is filled.

stdlib only, no build step, no dependency. Same python3 that serves the pages.
"""

import argparse
import datetime
import importlib.util
import pathlib
import re
import sys
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parents[1]
POSTS = ROOT / "content" / "news"


def topics():
    """The German topic names build-news.py accepts, lowercased.

    Asked of that file rather than repeated in this one, and it is now a
    question with a moving answer: the vocabulary is content/themen.json, which
    scripts/sync-news-notion.py writes out of the `Themen` property of the
    Notion database. build-news.py reads it, so reading build-news.py is reading
    it — and a list of names typed here would be stale the first time somebody
    added a topic in Notion, which is the shape of drift this repository keeps
    writing checks about.
    """
    spec = importlib.util.spec_from_file_location(
        "cf_build_news", ROOT / "scripts" / "build-news.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return set(mod.BY_NAME)


def slug(title):
    """A filename that keeps the title readable and sorts by date first.

    The umlauts are transliterated the way German does it — ä → ae, not a —
    because a slug is read by people looking for a file, and `waermepumpen` is
    the word where `wrmepumpen` is a typo nobody can search for.
    """
    s = title.lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        s = s.replace(a, b)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s)).strip("-")[:48]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("titel", help="the German headline, in quotes")
    ap.add_argument("--title", default="", help="the English headline")
    ap.add_argument("--datum", default=datetime.date.today().isoformat(),
                    help="YYYY-MM-DD (default: today)")
    ap.add_argument("--autor", default="")
    ap.add_argument("--minuten", default="", help="reading time in minutes")
    ap.add_argument("--themen", default="",
                    help="the post's topics, comma separated. The vocabulary "
                         "is content/themen.json; a name outside it is "
                         "rejected here rather than by the build")
    ap.add_argument("--text", action="store_true",
                    help="scaffold the two-language body, so the post gets a page")
    args = ap.parse_args()

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.datum):
        sys.exit("new-post: --datum is %r, not YYYY-MM-DD." % args.datum)

    # A TOPIC NAME IS CHECKED HERE OR IT IS CHECKED BY THE BUILD, and here is
    # where the person who typed it is still looking. The vocabulary is closed
    # and it is content/themen.json — the Notion property written out — so it is
    # read through build-news.py rather than restated, and "Energy" or
    # "Telemetry" is the mistake this catches: an English name on a German field
    # writes a file that scaffolds cleanly and then fails build-news.py with a
    # topic nothing recognises.
    if args.themen:
        known = topics()
        wrong = [t for t in (x.strip() for x in args.themen.split(",")) if t
                 and t.lower() not in known]
        if wrong:
            sys.exit("new-post: %s is not a topic. The vocabulary is %s — "
                     "content/themen.json, which follows the `Themen` property "
                     "in Notion."
                     % (", ".join(repr(w) for w in wrong),
                        ", ".join(sorted(k.title() for k in known))))

    POSTS.mkdir(parents=True, exist_ok=True)
    path = POSTS / ("%s-%s.md" % (args.datum, slug(args.titel)))
    if path.exists():
        sys.exit("new-post: %s already exists. Edit it, or give a different "
                 "title or --datum." % path.relative_to(ROOT))

    lines = ["datum:   " + args.datum]
    if args.autor:
        lines.append("autor:   " + args.autor)
    if args.minuten:
        lines.append("minuten: " + args.minuten)
    lines += ["themen:  " + args.themen,
              "titel:   " + args.titel,
              "title:   " + args.title,
              ""]
    # The scaffold below is a comment about itself: left as it stands, the post
    # is a listing in the archive and nothing more, which is a legitimate state
    # and the one the mock-up's eighteen entries are in. Filled in, the same
    # file is an article page in both editions.
    if args.text:
        lines += ["Der erste Absatz ist der Lead — er steht größer und ist der "
                  "Satz, den das Archiv und die Suche zitieren.",
                  "",
                  "## Erste Zwischenüberschrift",
                  "",
                  "Text.",
                  "",
                  "--- en ---",
                  "",
                  "The first paragraph is the lead — it is set larger and it is "
                  "the sentence the archive and the search results quote.",
                  "",
                  "## First section heading",
                  "",
                  "Text.",
                  ""]
    path.write_text("\n".join(lines), encoding="utf-8")

    print("wrote %s" % path.relative_to(ROOT))
    if not args.themen:
        print("\n  Fill in `themen:` — one or more of Telemetrie, Energie, "
              "Architektur.\n  They are the chips on the archive and the links "
              "under the finished article;\n  the build refuses a post that is "
              "filed under nothing.")
    if not args.title:
        print("\n  Fill in `title:` — the English headline. The build refuses "
              "without it,\n  because the site ships in both languages and a "
              "half-translated page is the\n  one thing the catalogue exists to "
              "prevent.")
    if not args.text:
        print("\n  It has no text, so it is a listing in the archive and has no "
              "page of its own.\n  Write the two-language body into the file — "
              "or start from a scaffold with --text.")
    print("""
  Then:

      python3 scripts/build-news.py     # the archive, its counters and its axis
      python3 scripts/build-i18n.py     # the English edition
      python3 scripts/build-articles.py # the post's own page, both editions
      python3 scripts/build-site.py     # the pages that actually ship

  Or all four, in that order: scripts/build-all.sh""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
