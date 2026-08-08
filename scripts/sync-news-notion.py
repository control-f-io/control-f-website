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

AND THE PAGE'S OWN TEXT IS THE ARTICLE. A row's properties are the record; what
is written inside the page is the piece, and it becomes beitrag-<name>.html —
one reading page per post, which is what the archive's cards link to.
scripts/build-articles.py writes it; this only carries the text over.

    German text, a DIVIDER BLOCK, then the English text.

That is the whole convention, and the divider is a block Notion already has
because the site ships in two languages and a post that exists in one of them
is a German paragraph in the middle of the English archive. A page with no text
at all is fine: the post stays a listing in the archive and gets no page, which
is what the eighteen entries carried over from the mock-up are.

The blocks that survive the trip are the ones the reading surface has a form
for — paragraph, heading, bulleted and numbered list, image, quote and callout
as paragraphs — with bold, code and links inside them. Anything else in the
page (an embed, a table, a video) is DROPPED WITH A WARNING rather than
silently: something that vanishes between Notion and the site is the kind of
loss nobody notices until a reader asks about it.

PICTURES ARE DOWNLOADED, NOT LINKED. A Notion-hosted file URL is signed and
expires within the hour: a page that pointed at one would show the photograph
to whoever built it and a broken image to everybody after. So the file is
fetched into design-system/assets/img/news/ and the post names it there — the
site serves its own assets, which is also the only arrangement its Content
Security Policy allows.

    <name>-<8 hex>.jpg     the post's name, then the file's own digest

The digest is the file's, so the same picture used twice is stored once and a
picture that has not changed does not churn the repository on every sync. A
file nothing names any more is removed, the way an unpublished post's text is.

EVERY PICTURE NEEDS A CAPTION, and it is not decoration: the caption is written
under the figure AND stands in for the picture for a reader who cannot see it
(scripts/build-articles.py writes alt="" for exactly this reason). A picture
with no caption fails the sync rather than shipping as a hole in the page.

The two halves of a post each carry their own image blocks, because each
carries its own caption. Copy the block below the divider and write the caption
in English; the file is downloaded once either way.

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
import hashlib
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
IMAGES = ROOT / "design-system" / "assets" / "img" / "news"

# The extensions the reading page can draw and check-image-scale.py can read a
# size out of. Anything else Notion lets somebody drop in a page — a PDF, an
# HEIC straight off a phone, an SVG — is refused by name rather than written
# into a post that then fails three scripts downstream.
SUFFIX = {"jpg": ".jpg", "jpeg": ".jpg", "png": ".png",
          "webp": ".webp", "gif": ".gif"}
TYPES = {"image/jpeg": ".jpg", "image/png": ".png",
         "image/webp": ".webp", "image/gif": ".gif"}

# 2022-06-28 rather than the newest. It is the version whose
# `/v1/databases/{id}/query` still exists and returns properties in the shape
# below; the 2025 line splits a database into data sources and would make this
# script's one request two. Pinned deliberately — an API version that follows
# "latest" is a script that breaks on somebody else's release day.
API = "https://api.notion.com/v1/databases/%s/query"
BLOCKS = "https://api.notion.com/v1/blocks/%s/children?page_size=100"
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


# The blocks the reading surface has a form for, and what each becomes in a
# post file. heading_1 becomes `##` and not `#`: the page's h1 is its title,
# written by build-articles.py from the Titel property, and a second h1 in the
# body is a second document. Quotes and callouts arrive as paragraphs — the
# specimen's pull quote and note are hand-set forms with a citation and a tag,
# and inventing either from a block that carries neither would be the generator
# making an editorial claim.
BLOCK = {
    "paragraph": "%s",
    "heading_1": "## %s",
    "heading_2": "## %s",
    "heading_3": "### %s",
    "bulleted_list_item": "- %s",
    "numbered_list_item": "1. %s",
    "quote": "%s",
    "callout": "%s",
}


def rich(runs):
    """Notion's rich text → the three inline forms a post file carries.

    Bold, code and links, in that order of nesting, and nothing else. Italic,
    colour and strikethrough have no form in .cf-prose — the stylesheet styles
    bare HTML by element — so carrying them across would mean inventing markup
    the design system does not have.
    """
    out = []
    for r in runs or []:
        t = r.get("plain_text", "")
        if not t.strip():
            out.append(t)
            continue
        ann = r.get("annotations") or {}
        if ann.get("code"):
            t = "`%s`" % t
        if ann.get("bold"):
            t = "**%s**" % t
        href = r.get("href")
        if href:
            t = "[%s](%s)" % (t, href)
        out.append(t)
    return "".join(out).strip()


def fetch_image(src, stem, url, mode):
    """One picture into design-system/assets/img/news/, named for the post and
    its own digest. Returns the path a post file names it by.

    Written only when it is not already there, byte for byte. That is what
    keeps an hourly job from rewriting the same eight photographs every run and
    filling the history with binary that did not change.
    """
    try:
        with urllib.request.urlopen(src, timeout=60) as r:
            data = r.read()
            ctype = (r.headers.get("Content-Type") or "").split(";")[0].strip()
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        fail("%s: cannot download the picture.\n    %s\n    %s"
             % (url, getattr(e, "reason", e), src.split("?")[0]))

    ext = SUFFIX.get(src.split("?")[0].rsplit(".", 1)[-1].lower()) or TYPES.get(ctype)
    if not ext:
        fail("%s has a picture that is neither JPEG, PNG, WebP nor GIF (%s).\n"
             "    The reading page draws those four; anything else has to be "
             "exported before it goes in the page." % (url, ctype or "unknown type"))

    name = "%s-%s%s" % (stem[:40].rstrip("-"),
                        hashlib.sha1(data).hexdigest()[:8], ext)
    path = IMAGES / name
    if mode == "write" and (not path.exists() or path.read_bytes() != data):
        IMAGES.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return "news/" + name, len(data)


def body_from(blocks, url, dropped, stem="bild", mode="write", pictures=None):
    """A Notion page's children → the two-language text of a post file.

    The divider is the language boundary and it is the only structural block
    with a meaning here. More than one is refused rather than guessed at: the
    second could be a section break somebody liked the look of, and choosing
    for them would publish half an article in the wrong language.
    """
    lines, seen_divider = [], 0
    for b in blocks:
        kind = b.get("type")
        if kind == "divider":
            seen_divider += 1
            lines.append("--- en ---")
            continue
        if kind == "image":
            img = b.get("image") or {}
            src = ((img.get("external") or {}).get("url")
                   or (img.get("file") or {}).get("url"))
            caption = rich(img.get("caption"))
            if not src:
                fail("%s has an image block with no file behind it." % url)
            if not caption:
                fail("%s has a picture with no caption.\n"
                     "    The caption is written under the figure and it is "
                     "also what stands in for the picture for a reader who "
                     "cannot see it — nothing else on the page says what is in "
                     "it. Click the image in Notion and add one." % url)
            path, size = fetch_image(src, stem, url, mode)
            if pictures is not None:
                pictures[path] = size
            lines.append("![%s](%s)" % (caption.replace("]", ""), path))
            continue
        form = BLOCK.get(kind)
        if form is None:
            dropped.setdefault(kind, []).append(url)
            continue
        text = rich((b.get(kind) or {}).get("rich_text"))
        if text:
            lines.append(form % text)
    if not lines:
        return ""
    if seen_divider != 1:
        fail("%s has text but %s.\n"
             "    A post is written in both languages on one page: the German "
             "text, a divider block, then the English text.\n"
             "    Type `---` in Notion to make one." % (
                 url, "no divider block" if not seen_divider
                 else "%d divider blocks" % seen_divider))
    return "\n\n".join(lines) + "\n"


def post_from(page, text=""):
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
    if text:
        body += "\n" + text
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


def sweep(pictures, mode):
    """Pictures nothing published names any more.

    The other half of "unpublishing in Notion has to mean unpublishing on the
    site". A post's text is removed when it leaves Veröffentlicht; its
    photographs are in a second directory and would otherwise stay, shipped
    with the site, reachable by anybody who kept the address. Only files under
    design-system/assets/img/news/ are ever touched — that directory is this
    script's output and nothing else writes to it.
    """
    if not IMAGES.is_dir():
        return []
    keep = {p.split("/", 1)[1] for p in pictures}
    gone = sorted(f.name for f in IMAGES.iterdir()
                  if f.is_file() and f.name not in keep)
    if mode == "write":
        for n in gone:
            (IMAGES / n).unlink()
    return ["news/" + n for n in gone]


def budget():
    """check-news-images.py's byte ceiling, read from the file that enforces it."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "cf_news_images", pathlib.Path(__file__).with_name("check-news-images.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.MAX_BYTES


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


def children(page_id, token):
    """One page's blocks, following the cursor. Four more lines of network."""
    out, url = [], BLOCKS % page_id
    while url:
        req = urllib.request.Request(
            url, headers={"Authorization": "Bearer " + token,
                          "Notion-Version": VERSION})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            fail("Notion answered %s for the blocks of %s.\n    %s"
                 % (e.code, page_id, e.read().decode(errors="replace")[:300]))
        except urllib.error.URLError as e:
            fail("cannot reach api.notion.com: %s" % e.reason)
        out += data.get("results", [])
        url = ((BLOCKS % page_id) + "&start_cursor=" + data["next_cursor"]
               if data.get("has_more") else None)
    return out


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

    mode = "report" if (args.dry_run or args.check) else "write"
    wanted, dropped, pictures = {}, {}, {}
    for page in rows:
        # The properties decide whether it is published; the page's own blocks
        # are only fetched for the rows that are, so a database of drafts costs
        # one request rather than one per draft.
        name, _ = post_from(page)
        if not name:
            continue
        url = page.get("url", page.get("id", "?"))
        blocks = (page.get("_blocks", []) if args.fixture
                  else children(page["id"], token))
        # The picture's filename starts with the post's, so `ls` on the image
        # directory reads as the archive does. name is `<date>-<slug>.md`; the
        # date is already in the post's own name and says nothing about a file.
        name, body = post_from(page, body_from(
            blocks, url, dropped, stem=name[11:-3], mode=mode, pictures=pictures))
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

    added, changed, removed = write(wanted, mode)
    gone = sweep(pictures, mode)

    for n in added:
        print("  + %s" % n)
    for n in changed:
        print("  ~ %s" % n)
    for n in removed:
        print("  - %s" % n)
    for n in gone:
        print("  - %s" % n)
    for kind, where in sorted(dropped.items()):
        print("  ! %s block(s) of type %r have no form on the reading page and "
              "were left out: %s" % (len(where), kind, where[0]), file=sys.stderr)

    # The budget is check-news-images.py's and is read from it rather than
    # repeated: that file is the gate, and a warning here that disagreed with
    # the gate would be a second opinion nobody asked for. Said now anyway,
    # because the person who dropped the photograph in is looking at this run
    # and not at the pull request it will fail an hour from now.
    for path, size in sorted(pictures.items()):
        if size > budget():
            print("  ! %s is %.1f MB — over the %.0f kB a picture on the "
                  "reading plate is allowed. check-news-images.py fails on it."
                  % (path, size / 1e6, budget() / 1e3), file=sys.stderr)

    if args.check:
        if added or changed or removed or gone:
            print("\nsync-news: content/news/ is %d file(s) out of step with "
                  "Notion.\n    run: python3 scripts/sync-news-notion.py"
                  % (len(added) + len(changed) + len(removed) + len(gone)))
            return 1
        print("sync-news: content/news/ matches Notion — %d published post(s), "
              "%d picture(s)" % (len(wanted), len(pictures)))
        return 0

    verb = "would change" if args.dry_run else "synced"
    print("sync-news: %s — %d published, %d added, %d updated, %d removed, "
          "%d picture(s)"
          % (verb, len(wanted), len(added), len(changed), len(removed),
             len(pictures)))
    if not args.dry_run and (added or changed or removed or gone):
        print("     then: sh scripts/build-all.sh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
