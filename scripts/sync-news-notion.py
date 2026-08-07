#!/usr/bin/env python3
"""Import the news archive from Notion into content/news/.

WHY A TOKEN AND NOT THE CONNECTOR. Notion is already where this company writes
— the team's names, roles and photographs are a database there, and the website
takes them from it — so an admin adding a post should be able to write it in
Notion too. What cannot do that job is the Notion *connector*: it is attached to
an interactive Claude session, and the things that would run this on a schedule
have no connectors at all. Measured in this environment: a routine's session
comes up with git and nothing else, and the ambient GitHub token answers the API
with 403. So the automated path needs a credential of its own, which is an
integration token, which is why this script asks for one.

    NOTION_TOKEN     an internal integration's secret (ntn_… / secret_…)
    NOTION_NEWS_DB   the news database's id, from its URL

THE DATABASE IT EXPECTS. Five properties, and the names are the German ones the
post files already use so that the two are read the same way:

    Titel      title        the German headline
    Title      rich text    the English headline
    Datum      date         sorts the archive
    Autor      rich text    optional; only the lead card shows it
    Minuten    number       optional; reading time
    Status     select       only "Veröffentlicht" is imported

STATUS IS THE WHOLE POINT OF THE FIELD. Notion is a drafting surface: a post
exists there long before it should exist on the website, and a sync without a
published state publishes the first sentence somebody types. Anything not
"Veröffentlicht" is skipped, and a post that LEAVES that state has its file
removed — unpublishing in Notion has to mean unpublishing on the site, or the
field is decoration.

THIS SCRIPT ONLY WRITES content/news/. It does not touch the pages: build-news.py
lays out the archive from those files, and it is the same layout whether a post
arrived from Notion or from new-post.py. One store, two ways in.

    python3 scripts/sync-news-notion.py              # write content/news/
    python3 scripts/sync-news-notion.py --dry-run    # say what would change
    python3 scripts/sync-news-notion.py --check      # fail if they differ
    python3 scripts/sync-news-notion.py --fixture f  # read a saved response

--fixture is how the transform is tested without a token: save one query
response to a file and run the whole thing against it. The network is four lines
at the bottom of this file; everything above them is what actually needs
checking.

stdlib only, no build step, no dependency. Same python3 that serves the pages.
"""

import argparse
import json
import os
import pathlib
import re
import sys
import unicodedata
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
POSTS = ROOT / "content" / "news"

# 2022-06-28 rather than the newest. It is the version whose
# `/v1/databases/{id}/query` still exists and returns properties in the shape
# below; the 2025 line splits a database into data sources and would make this
# script's one request two. Pinned deliberately — an API version that follows
# "latest" is a script that breaks on somebody else's release day.
API = "https://api.notion.com/v1/databases/%s/query"
VERSION = "2022-06-28"

PUBLISHED = "Veröffentlicht"

# The header this writes, in the order new-post.py writes it, so a file from
# Notion and a file from the command line are the same file.
FIELDS = ("datum", "autor", "minuten", "titel", "title")


def fail(msg):
    print("sync-news: " + msg, file=sys.stderr)
    sys.exit(1)


# --------------------------------------------------------------------------
# Notion's property shapes, each reduced to the one string this needs
# --------------------------------------------------------------------------

def plain(prop):
    """Notion returns rich text as a list of runs; the post files hold a line.

    A run carries its own formatting and href, and none of that survives into a
    card title anyway — the archive sets its own type. So the text is joined and
    the styling dropped, which is the honest reduction rather than a lossy one.
    """
    if prop is None:
        return ""
    kind = prop.get("type")
    if kind in ("title", "rich_text"):
        return "".join(r.get("plain_text", "") for r in prop.get(kind, [])).strip()
    if kind == "date":
        return ((prop.get("date") or {}).get("start") or "")[:10]
    if kind == "number":
        n = prop.get("number")
        return "" if n is None else ("%d" % n if float(n).is_integer() else str(n))
    if kind in ("select", "status"):
        return ((prop.get(kind) or {}).get("name") or "").strip()
    if kind == "people":
        return ", ".join(p.get("name", "") for p in prop.get("people", [])).strip()
    if kind == "formula":
        f = prop.get("formula") or {}
        return str(f.get(f.get("type"), "") or "").strip()
    fail("property type %r is not one this script reads. Add it to plain() "
         "rather than leaving it to be guessed at." % kind)


def slug(title):
    """Identical to new-post.py's, and it has to be: the two write the same
    filenames for the same headline, so a post drafted at the command line and
    then moved into Notion does not arrive as a second file."""
    s = title.lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        s = s.replace(a, b)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s)).strip("-")[:48]


def post_from(page):
    """One Notion row → the fields a post file holds, or a reason it cannot be.

    A row that is published and unusable is a FAILURE and never a skip. A post
    silently dropped from the archive looks exactly like a post nobody wrote,
    and the person who wrote it in Notion has no way to tell the difference.
    """
    props = page.get("properties") or {}
    got = {k: plain(props.get(v)) for k, v in
           (("titel", "Titel"), ("title", "Title"), ("datum", "Datum"),
            ("autor", "Autor"), ("minuten", "Minuten"))}
    status = plain(props.get("Status"))
    url = page.get("url", page.get("id", "?"))

    if status != PUBLISHED:
        return None, None
    for field in ("titel", "title", "datum"):
        if not got[field]:
            fail("%s is %s and has no %s.\n"
                 "    Every published post needs a German title, an English "
                 "title and a date — the site ships in both languages and the "
                 "archive sorts by date." % (url, PUBLISHED, field.capitalize()))
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", got["datum"]):
        fail("%s has Datum %r, which is not a plain date." % (url, got["datum"]))

    name = "%s-%s.md" % (got["datum"], slug(got["titel"]))
    body = "\n".join("%-8s %s" % (f + ":", got[f]) for f in FIELDS if got[f]) + "\n"
    return name, body


# --------------------------------------------------------------------------

def write(wanted, mode):
    """content/news/ made to match what Notion published.

    Removal is half of it. A post pulled out of "Veröffentlicht" has to leave
    the site, or the status field is a label rather than a switch — and only
    files this script recognises as post files are ever removed, so a note left
    in the directory by hand is not swept up with them.
    """
    POSTS.mkdir(parents=True, exist_ok=True)
    have = {p.name: p.read_text(encoding="utf-8") for p in POSTS.glob("*.md")}
    added = sorted(n for n in wanted if n not in have)
    changed = sorted(n for n in wanted if n in have and have[n] != wanted[n])
    removed = sorted(n for n in have if n not in wanted)

    if mode == "write":
        for n in added + changed:
            (POSTS / n).write_text(wanted[n], encoding="utf-8")
        for n in removed:
            (POSTS / n).unlink()
    return added, changed, removed


def fetch(db, token):
    """Every row, following Notion's cursor. Four lines of network."""
    out, cursor = [], None
    while True:
        payload = {"page_size": 100}
        if cursor:
            payload["start_cursor"] = cursor
        req = urllib.request.Request(
            API % db, data=json.dumps(payload).encode(),
            headers={"Authorization": "Bearer " + token,
                     "Notion-Version": VERSION,
                     "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:400]
            hint = ""
            if e.code == 404:
                hint = ("\n    A 404 here is nearly always the database not "
                        "being SHARED with the integration: open it in Notion, "
                        "… → Connections → add the integration.")
            if e.code == 401:
                hint = "\n    NOTION_TOKEN is not a token this workspace knows."
            fail("Notion answered %s for the database query.%s\n    %s"
                 % (e.code, hint, detail))
        except urllib.error.URLError as e:
            fail("cannot reach api.notion.com: %s" % e.reason)
        out += data.get("results", [])
        if not data.get("has_more"):
            return out
        cursor = data.get("next_cursor")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true", help="say what would change")
    g.add_argument("--check", action="store_true",
                   help="exit 1 if content/news/ differs from Notion")
    ap.add_argument("--fixture", metavar="FILE",
                    help="read a saved query response instead of calling Notion")
    ap.add_argument("--force", action="store_true",
                    help="allow a sync that removes most of the archive")
    args = ap.parse_args()

    if args.fixture:
        raw = json.loads(pathlib.Path(args.fixture).read_text(encoding="utf-8"))
        rows = raw.get("results", raw if isinstance(raw, list) else [])
    else:
        token = os.environ.get("NOTION_TOKEN", "").strip()
        db = os.environ.get("NOTION_NEWS_DB", "").strip()
        if not token or not db:
            fail("NOTION_TOKEN and NOTION_NEWS_DB have to be set.\n"
                 "    The token is an internal integration's secret; the id is "
                 "the 32 hex characters in the database's URL.\n"
                 "    Without a token this can still be run against a saved "
                 "response: --fixture FILE.")
        rows = fetch(db, token)

    wanted = {}
    for page in rows:
        name, body = post_from(page)
        if not name:
            continue
        if name in wanted and wanted[name] != body:
            fail("two published posts write the same file, %s. Two headlines "
                 "that differ only in punctuation on one day do this; change "
                 "one of them or move a date." % name)
        wanted[name] = body

    if not wanted:
        fail("no row in that database is %s. Refusing to empty content/news/ "
             "on the strength of a query that found nothing — a wrong database "
             "id and an empty archive look identical from here." % PUBLISHED)

    # A FLOOR UNDER THE DELETIONS, because this is meant to run unattended.
    # Every failure mode that empties the archive looks like a successful sync
    # from in here: a Status renamed in Notion, a filter left on a view, a
    # second database made and shared instead of the first. The query returns
    # rows, they are simply not the rows, and the next build ships an archive
    # with three posts in it. Refusing to remove most of what is there — unless
    # a person says --force on purpose — costs one command in the case where the
    # wipe is genuine and prevents the case where it is not.
    standing = len(list(POSTS.glob("*.md"))) if POSTS.is_dir() else 0
    going = len([n for n in (p.name for p in POSTS.glob("*.md"))
                 if n not in wanted]) if POSTS.is_dir() else 0
    if going > 3 and going * 2 > standing and not args.force:
        fail("this would remove %d of the %d posts in content/news/ and Notion "
             "published %d.\n"
             "    That is what a wrong database id, a renamed Status or a "
             "filtered view looks like from here.\n"
             "    If the archive really is meant to shrink to %d: --force"
             % (going, standing, len(wanted), len(wanted)))

    added, changed, removed = write(
        wanted, "report" if (args.dry_run or args.check) else "write")

    for n in added:
        print("  + %s" % n)
    for n in changed:
        print("  ~ %s" % n)
    for n in removed:
        print("  - %s" % n)

    if args.check:
        if added or changed or removed:
            print("\nsync-news: content/news/ is %d file(s) out of step with "
                  "Notion.\n    run: python3 scripts/sync-news-notion.py"
                  % (len(added) + len(changed) + len(removed)))
            return 1
        print("sync-news: content/news/ matches Notion — %d published post(s)"
              % len(wanted))
        return 0

    verb = "would change" if args.dry_run else "synced"
    print("sync-news: %s — %d published, %d added, %d updated, %d removed"
          % (verb, len(wanted), len(added), len(changed), len(removed)))
    if not args.dry_run and (added or changed or removed):
        print("     then: sh scripts/build-all.sh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
