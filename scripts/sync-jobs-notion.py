#!/usr/bin/env python3
"""Import the vacancy register from Notion into content/jobs/.

THE SAME SHAPE AS scripts/sync-news-notion.py, one register over, and it shares
that file's machinery rather than repeating it: the rich-text reader, the block
grammar, the image download, the paging, the error messages. What differs is
the record — an opening has fifteen fields a reader sees where a post has five —
and that difference is the property table below.

    NOTION_TOKEN     an internal integration's secret (ntn_… / secret_…)
    NOTION_JOBS_DB   the Stellen database's id, from its URL

THE DATABASE IT EXPECTS. Everything a reader sees exists twice, because the
site ships twice, and the German name is the one the post files already use:

    Titel / Title            the headline, e.g. "{Data Engineer} (m/w/d)"
    Kennung                  CF-2026-DE-01 — the reference in the subject line
    Bereich / Area           Plattform, Analytik, …
    Anriss / Excerpt         the two lines the register shows under the title
    Standort / Location      the register's four facts, as short labels
    Anstellung / Employment
    Umfang / Hours
    Start / Starts
    Adresse / Address        optional; the long form for the job page
    Vergütung / Salary       optional; the sentence a reader gets
    Gehalt von / Gehalt bis  optional; the numbers the JobPosting block carries
    Beschäftigungsart        optional; FULL_TIME, PART_TIME, … for the same block
    Ausgeschrieben           the date, and datePosted
    Frist                    optional; the closing date, and validThrough
    Status                   only "Veröffentlicht" is imported

THE BRACES IN A TITLE ARE NOT A TYPO. "{Data Engineer} (m/w/d)" is two
languages in one line, and the braces mark the English run so the German page
can wrap it in lang="en" — WCAG 3.1.2, and the rule karriere.html has carried
in a comment since it was written. On the English page they are simply dropped.

AND THE PAGE'S OWN TEXT IS THE ADVERTISEMENT. What is written inside the Notion
page becomes stelle-<name>.html: the paragraphs before the first heading are
"Die Aufgabe", and each `## heading` and its list is one block of "Ihre Arbeit
und was sie voraussetzt". German text, a DIVIDER BLOCK, then the English text —
the same convention the news database uses.

AN OPENING WITH NO TEXT IS NOT AN ERROR. It stays in the register as a listing
whose title links to its own row, which is what karriere.html shipped for three
of its four entries: an opening is worth announcing before its advertisement is
written, and a link to a page that does not exist is the thing that must not
ship.

    python3 scripts/sync-jobs-notion.py              # write content/jobs/
    python3 scripts/sync-jobs-notion.py --dry-run    # say what would change
    python3 scripts/sync-jobs-notion.py --check      # fail if they differ
    python3 scripts/sync-jobs-notion.py --fixture f  # read a saved response

stdlib only, no build step, no dependency. Same python3 that serves the pages.
"""

import argparse
import importlib.util
import json
import os
import pathlib
import re
import sys
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parents[1]
JOBS = ROOT / "content" / "jobs"
# Its own folder, because each sync sweeps the pictures nothing in ITS
# store names any more — see sweep() in sync-news-notion.py.
IMAGES = ROOT / "design-system" / "assets" / "img" / "jobs"

API = "https://api.notion.com/v1/databases/%s/query"
PUBLISHED = "Veröffentlicht"


def load(name):
    spec = importlib.util.spec_from_file_location(
        "cf_" + name.replace("-", "_"),
        pathlib.Path(__file__).with_name(name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


NEWS = load("sync-news-notion")        # plain(), rich(), body_from(), children(), fetch()
fail = NEWS.fail

# Notion property → post field, in the order the file writes them. A pair of
# languages is two properties and two fields, deliberately: one column that
# somebody has to remember to translate is a column that stays German.
FIELDS = (
    ("kennung", "Kennung"), ("bereich", "Bereich"), ("area", "Area"),
    ("titel", "Titel"), ("title", "Title"),
    ("anriss", "Anriss"), ("excerpt", "Excerpt"),
    ("standort", "Standort"), ("location", "Location"),
    ("anstellung", "Anstellung"), ("employment", "Employment"),
    ("umfang", "Umfang"), ("hours", "Hours"),
    ("start", "Start"), ("starts", "Starts"),
    ("adresse", "Adresse"), ("address", "Address"),
    ("verguetung", "Vergütung"), ("salary", "Salary"),
    ("gehalt_von", "Gehalt von"), ("gehalt_bis", "Gehalt bis"),
    ("art", "Beschäftigungsart"),
    ("seit", "Ausgeschrieben"), ("frist", "Frist"),
)
# Without these the register cannot be drawn in both languages at all.
NEEDED = ("kennung", "titel", "title", "anriss", "excerpt", "bereich", "area",
          "standort", "location", "anstellung", "employment", "umfang",
          "hours", "start", "starts", "seit")

WIDTH = max(len(f) for f, _ in FIELDS) + 2


def slug(titel):
    """The filename, the register's anchor and the page's address, from the
    German headline: the braces dropped, the legal formula in parentheses
    dropped, the rest transliterated the way German does it.

        {Solution Engineer} Industrie (m/w/d)  →  solution-engineer-industrie

    Renaming a role in Notion therefore moves its URL, which is the same
    trade-off content/news/ already makes for a headline — and the reason the
    Kennung exists is that it does not move.
    """
    s = re.sub(r"\([^)]*\)", " ", titel.replace("{", " ").replace("}", " ")).lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        s = s.replace(a, b)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s)).strip("-")[:48]


def job_from(page, text=""):
    """One Notion row → the file an opening is, or a reason it cannot be."""
    props = page.get("properties") or {}
    got = {f: NEWS.plain(props.get(p)) for f, p in FIELDS}
    status = NEWS.plain(props.get("Status"))
    url = page.get("url", page.get("id", "?"))

    if status != PUBLISHED:
        return None, None
    for f in NEEDED:
        if not got[f]:
            fail("%s is %s and has no %s.\n"
                 "    An opening is drawn in both languages before anybody can "
                 "read it — the register ships twice." % (url, PUBLISHED, f))
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", got["seit"]):
        fail("%s has Ausgeschrieben %r, which is not a plain date."
             % (url, got["seit"]))
    # Said here as well as in build-jobs.py, because this is where the person
    # who wrote the advertisement is looking. An opening with text gets a page,
    # a page carries a JobPosting block, and a block without validThrough stays
    # in search results after the position is filled.
    if text and not got["frist"]:
        fail("%s has an advertisement and no Frist.\n"
             "    Set a closing date, or leave the page empty and the opening "
             "stays a listing in the register." % url)

    name = "%s.md" % slug(got["titel"])
    body = "\n".join("%-*s%s" % (WIDTH, f + ":", got[f]) for f, _ in FIELDS if got[f])
    return name, body + "\n" + ("\n" + text if text else "")


def write(wanted, mode):
    """content/jobs/ made to match what Notion published.

    Removal is the half that matters most here: a position that has been
    filled is pulled out of Veröffentlicht, and it has to leave the register
    the same hour. An advertisement that outlives the opening costs somebody
    an application.
    """
    JOBS.mkdir(parents=True, exist_ok=True)
    have = {p.name: p.read_text(encoding="utf-8") for p in JOBS.glob("*.md")}
    added = sorted(n for n in wanted if n not in have)
    changed = sorted(n for n in wanted if n in have and have[n] != wanted[n])
    removed = sorted(n for n in have if n not in wanted)
    if mode == "write":
        for n in added + changed:
            (JOBS / n).write_text(wanted[n], encoding="utf-8")
        for n in removed:
            (JOBS / n).unlink()
    return added, changed, removed


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true", help="say what would change")
    g.add_argument("--check", action="store_true",
                   help="exit 1 if content/jobs/ differs from Notion")
    ap.add_argument("--fixture", metavar="FILE",
                    help="read a saved query response instead of calling Notion")
    ap.add_argument("--force", action="store_true",
                    help="allow a sync that empties the register")
    args = ap.parse_args()

    token = ""
    if args.fixture:
        raw = json.loads(pathlib.Path(args.fixture).read_text(encoding="utf-8"))
        rows = raw.get("results", raw if isinstance(raw, list) else [])
    else:
        token = os.environ.get("NOTION_TOKEN", "").strip()
        db = os.environ.get("NOTION_JOBS_DB", "").strip()
        if not token or not db:
            fail("NOTION_TOKEN and NOTION_JOBS_DB have to be set.\n"
                 "    The token is an internal integration's secret; the id is "
                 "the 32 hex characters in the database's URL.\n"
                 "    Without a token this can still be run against a saved "
                 "response: --fixture FILE.")
        rows = NEWS.fetch_rows(API % db, token)

    mode = "report" if (args.dry_run or args.check) else "write"
    wanted, dropped, pictures = {}, {}, {}
    for page in rows:
        name, _ = job_from(page)
        if not name:
            continue
        url = page.get("url", page.get("id", "?"))
        blocks = (page.get("_blocks", []) if args.fixture
                  else NEWS.children(page["id"], token))
        name, body = job_from(page, NEWS.body_from(
            blocks, url, dropped, stem=name[:-3], mode=mode,
            pictures=pictures, into=IMAGES))
        if name in wanted and wanted[name] != body:
            fail("two published openings write the same file, %s. Two titles "
                 "that reduce to the same name do this; change one of them."
                 % name)
        wanted[name] = body

    # NO FLOOR AND NO EMPTY REGISTER. The archive's floor exists because an
    # empty news page is indistinguishable from a broken query; a register with
    # nothing in it is an ordinary state a company is in, and karriere-leer.html
    # is the page written for it. But that page is written by hand, and this
    # script does not put it in place — so an empty result stops here rather
    # than silently leaving karriere.html claiming a register it no longer has.
    if not wanted and not args.force:
        fail("no row in that database is %s.\n"
             "    If the last opening really has been filled: the zero state is "
             "karriere-leer.html, which is written by hand, and this refuses to "
             "leave karriere.html half-emptied on its own. --force to proceed."
             % PUBLISHED)

    added, changed, removed = write(wanted, mode)
    gone = NEWS.sweep(pictures, mode, IMAGES)

    for n in added:
        print("  + %s" % n)
    for n in changed:
        print("  ~ %s" % n)
    for n in removed + gone:
        print("  - %s" % n)
    for kind, where in sorted(dropped.items()):
        print("  ! %s block(s) of type %r have no form on the job page and were "
              "left out: %s" % (len(where), kind, where[0]), file=sys.stderr)

    if args.check:
        if added or changed or removed:
            print("\nsync-jobs: content/jobs/ is %d file(s) out of step with "
                  "Notion.\n    run: python3 scripts/sync-jobs-notion.py"
                  % (len(added) + len(changed) + len(removed)))
            return 1
        print("sync-jobs: content/jobs/ matches Notion — %d open position(s)"
              % len(wanted))
        return 0

    verb = "would change" if args.dry_run else "synced"
    print("sync-jobs: %s — %d open, %d added, %d updated, %d removed"
          % (verb, len(wanted), len(added), len(changed), len(removed)))
    if not args.dry_run and (added or changed or removed):
        print("     then: sh scripts/build-all.sh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
