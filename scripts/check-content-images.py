#!/usr/bin/env python3
"""Hold the pictures in a post or a job advertisement to the plate they are drawn on.

WHERE THEY COME FROM. An admin puts an image block in a Notion page;
scripts/sync-news-notion.py and scripts/sync-jobs-notion.py download the file
into design-system/assets/img/news/ or …/jobs/ and write
`![caption](news/<file>)` into the post; scripts/build-articles.py and
scripts/build-stellen.py draw it as a `.cf-prose > figure`. The photograph
that leaves a phone is 4 000 px wide and four megabytes — and the sync fits
it to this plate the moment it downloads it (fit_to_plate(), Pillow, the one
dependency the workflows install, pinned). So these sanctions are a BACKSTOP,
not the front door: a LARGE or HEAVY finding means a picture got into the
repository by hand, past a sync that would have fitted it at the door.

THE PLATE IS 1008 PX. Measured on blog-artikel.html at 1440, 1920 and 2560 —
`.cf-prose > figure:not(.cf-quote)` is 1008 px at all three, because the
container caps before the viewport does. So the file's job is to fill 1008 px:

    1008  <=  width  <=  2016        (1 x the plate to 2 x it)

The floor is the screen nobody has an excuse for: below 1008 the picture is
upscaled on an ordinary laptop. The ceiling is the retina one — 2 x is what a
dpr-2 display can resolve across a plate this wide, and the 3 x that
scripts/check-image-scale.py allows its fixed boxes is affordable there because
those files are tens of kilobytes; here 3 x is megabytes of pixels almost
nobody resolves.

AND 800 KB, which is what 2016 px of photograph costs at a sensible quality. A
file over it is either barely compressed or larger than the box, and both are
paid for by a reader on a train.

THREE MORE THINGS, all of them the kind that renders correctly and is wrong:

  DANGLING   a post that names a picture the repository does not have. The
             page then ships an <img> pointing at a 404, which looks like a
             broken photograph and reads as a broken site.
  ORPHANED   a file in design-system/assets/img/news/ that no post names.
             Unpublishing a post in Notion removes its text and its pictures
             have to go with it — otherwise the archive shrinks and the
             repository does not.
  BORROWED   a hand-written page naming a picture in one of those two folders.
             The folders are the syncs' output and nothing else writes to
             them: sweep() deletes every file no post still names, so the
             reference is not wrong today and is one unpublished post away
             from being wrong. components/blog-grid.html held the heat-pump
             post's photograph in its demo; the archive came back from Notion
             on 2026-08-20 without that post, the sweep took the file, and
             check-links.py failed the merge of a sync that merges its own
             work. Same shape as the topic pages two specimens named in an
             href — a hand-written reference cannot survive the archive
             changing underneath it. A specimen draws its demo from the
             site's own photography instead: components/vacancy.html does,
             and its component's real pictures live in …/img/jobs/.

SCOPE is content/news/ and content/jobs/, with their two picture folders, and —
for BORROWED alone — every page in design-system/ that a generator did not
write. Both forms of reference count: a picture in the running text,
`![caption](path)`, and a post's title picture, the `bild:` line in its header
that the archive draws its card from.
Pictures anywhere else in the design system are somebody else's rule: check-image-scale.py holds
the ones drawn in a fixed box, and there is no plate but this one.

    python3 scripts/check-content-images.py
    python3 scripts/check-content-images.py -v   # name every picture and its size

stdlib only, no build step, no dependency. Same python3 that serves the pages.
"""

import argparse
import importlib.util
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
STORES = (ROOT / "content" / "news", ROOT / "content" / "jobs")
TREE = ROOT / "design-system"
IMG = TREE / "assets" / "img"
FOLDERS = (IMG / "news", IMG / "jobs")

# Measured, not chosen. See the header.
PLATE = 1008
MIN_WIDTH = PLATE
MAX_WIDTH = PLATE * 2
MAX_BYTES = 800_000

PICTURE = re.compile(r"!\[(.*?)\]\(([^)\s]+)\)")

# AND THE TITLE PICTURE, which is a header field rather than a block. A post
# names the one picture that stands for it — `bild: news/x.jpg`, the Titelbild
# property in Notion — and the archive draws its card from it. It is the same
# file in the same folder under the same rules: named and missing is still
# DANGLING, present and named by nothing is still ORPHANED, and a card is
# 272 px of a five-column grid, which a file sized for the 1008 px plate covers
# at every density. A post may use one picture in both places; it is downloaded
# once, and this counts it once. → scripts/build-news.py
TITLE_PICTURE = re.compile(r"^bild:\s*(\S+)\s*$", re.M)


def intrinsic(path):
    """check-image-scale.py's header reader, imported rather than copied: it is
    the file that fails on a width/height attribute disagreeing with the file,
    so it is the file that decides what the file's width is."""
    spec = importlib.util.spec_from_file_location(
        "cf_image_scale", pathlib.Path(__file__).with_name("check-image-scale.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.intrinsic(str(path))


def reader(_cache={}):
    """check-links.py, imported for the two things it already knows how to do.

    readable() blanks the regions of a page that are prose ABOUT markup —
    components/vacancy.html names …/img/jobs/ inside a <code> and means the
    folder rather than a file — and references() knows which attributes name a
    resource. Reading a page a second way here would be a second opinion about
    what a reference is, and the two would first disagree over exactly those
    two cases.
    """
    if not _cache:
        spec = importlib.util.spec_from_file_location(
            "cf_links", pathlib.Path(__file__).with_name("check-links.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _cache["mod"] = mod
    return _cache["mod"]


# A page a generator wrote says so on its second line, and its references to a
# picture are the store's own — they are rewritten on the next build, which is
# what makes them safe.
GENERATED = "<!-- GENERATED"

# The other half of "a generator wrote it": a region inside a page that is
# otherwise written by hand. news.html and karriere.html each carry a few,
# and the cards inside them name the archive's pictures.
FENCED = re.compile(r"<!-- (news|jobs):[a-z-]+ -->.*?<!-- /\1:[a-z-]+ -->", re.S)

SWEPT = re.compile(r"assets/img/(news|jobs)/")


def blank(text, start, end):
    """Positions and line count kept, so a line number still means something."""
    return text[:start] + re.sub(r"[^\n]", " ", text[start:end]) + text[end:]


def borrowed():
    """Every hand-written reference into a folder the syncs sweep."""
    links = reader()
    out = []
    for path in sorted(TREE.rglob("*.html")):
        raw = path.read_text(encoding="utf-8")
        if GENERATED in raw[:400]:
            continue
        # readable() keeps the file's length and its lines, so a span found in
        # the source blanks the same span in the masked copy.
        text = links.readable(str(path))
        for m in FENCED.finditer(raw):
            text = blank(text, m.start(), m.end())
        for attr, value, line in links.references(str(path), text):
            if SWEPT.search(value):
                out.append(
                    "BORROWED  %s:%d names %s.\n    That folder is a sync's "
                    "own output and is swept against content/ on every run — "
                    "the file goes the hour the post does. Draw the demo from "
                    "the site's own photography instead."
                    % (path.relative_to(ROOT).as_posix(), line, value))
    return out


def referenced():
    """Every picture named by a post or an opening, and which names it."""
    out = {}
    for store in STORES:
        if not store.is_dir():
            continue
        for item in sorted(store.glob("*.md")):
            text = item.read_text(encoding="utf-8")
            # The header ends at the first blank line, and `bild:` is a field of
            # it: a line further down that happens to begin with the word is
            # prose, not a reference.
            head = text.partition("\n\n")[0]
            for m in PICTURE.finditer(text):
                out.setdefault(m.group(2).strip(), []).append(item.name)
            for m in TITLE_PICTURE.finditer(head):
                out.setdefault(m.group(1).strip(), []).append(item.name)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    used = referenced()
    findings = []

    for path, posts in sorted(used.items()):
        f = IMG / path
        where = ", ".join(sorted(set(posts)))
        if not f.exists():
            findings.append(
                "DANGLING  %s names design-system/assets/img/%s, which does not "
                "exist.\n    A page built from it links to a 404." % (where, path))
            continue
        size = f.stat().st_size
        dims = intrinsic(f)
        if not dims:
            findings.append(
                "UNREADABLE  design-system/assets/img/%s: no pixel size in its "
                "header. JPEG, PNG, WebP and GIF are what this reads." % path)
            continue
        w, h = dims
        if w < MIN_WIDTH:
            findings.append(
                "SMALL     design-system/assets/img/%s is %d px wide; the plate "
                "it is drawn on is %d.\n    It is upscaled on an ordinary "
                "laptop before anybody has zoomed in." % (path, w, PLATE))
        if w > MAX_WIDTH:
            findings.append(
                "LARGE     design-system/assets/img/%s is %d px wide; the plate "
                "is %d and twice that is the ceiling.\n    The sync fits "
                "pictures to this window as it imports them — one this wide got "
                "into the repository another way. Re-run the sync for the "
                "store, or replace it in Notion with an export at %d px."
                % (path, w, PLATE, MAX_WIDTH))
        if size > MAX_BYTES:
            findings.append(
                "HEAVY     design-system/assets/img/%s is %.1f MB; the budget is "
                "%.0f kB.\n    The sync re-encodes pictures over the budget as "
                "it imports them — one this heavy got into the repository "
                "another way. Re-run the sync for the store, or replace it in "
                "Notion with a smaller file." % (path, size / 1e6, MAX_BYTES / 1e3))
        if args.verbose:
            print("  %-52s %5d x %-5d %6.0f kB  %s"
                  % (path, w, h, size / 1e3, where))

    for folder in FOLDERS:
        if not folder.is_dir():
            continue
        for f in sorted(folder.iterdir()):
            if not f.is_file():
                continue
            rel = f.relative_to(IMG).as_posix()
            if rel not in used:
                findings.append(
                    "ORPHANED  design-system/assets/img/%s is named by nothing "
                    "in content/.\n    A picture outlives its post only when "
                    "something forgot to remove it — run the sync for that "
                    "store." % rel)

    findings += borrowed()

    if findings:
        print("content images: %d finding(s)\n" % len(findings), file=sys.stderr)
        for f in findings:
            print("  " + f, file=sys.stderr)
        return 1

    print("content images: %d picture(s) in %d file(s), every one between %d and "
          "%d px on a %d px plate and under %.0f kB, and named by nothing a "
          "generator did not write."
          % (len(used), len({p for ps in used.values() for p in ps}),
             MIN_WIDTH, MAX_WIDTH, PLATE, MAX_BYTES / 1e3))
    return 0


if __name__ == "__main__":
    sys.exit(main())
