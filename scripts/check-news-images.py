#!/usr/bin/env python3
"""Hold the pictures in a news post to the plate they are drawn on.

WHERE THEY COME FROM. An admin puts an image block in a Notion page;
scripts/sync-news-notion.py downloads the file into
design-system/assets/img/news/ and writes `![caption](news/<file>)` into the
post; scripts/build-articles.py draws it as a `.cf-prose > figure`. Nobody in
that chain looks at the file. The photograph that leaves a phone is 4 000 px
wide and four megabytes, and every step above will carry it to the reader
without a word.

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

TWO MORE THINGS, both of them the kind that renders correctly and is wrong:

  DANGLING   a post that names a picture the repository does not have. The
             page then ships an <img> pointing at a 404, which looks like a
             broken photograph and reads as a broken site.
  ORPHANED   a file in design-system/assets/img/news/ that no post names.
             Unpublishing a post in Notion removes its text and its pictures
             have to go with it — otherwise the archive shrinks and the
             repository does not.

SCOPE is content/news/ and design-system/assets/img/news/. Pictures anywhere
else in the design system are somebody else's rule: check-image-scale.py holds
the ones drawn in a fixed box, and there is no plate but this one.

    python3 scripts/check-news-images.py
    python3 scripts/check-news-images.py -v    # name every picture and its size

stdlib only, no build step, no dependency. Same python3 that serves the pages.
"""

import argparse
import importlib.util
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
POSTS = ROOT / "content" / "news"
IMG = ROOT / "design-system" / "assets" / "img"
NEWS_IMG = IMG / "news"

# Measured, not chosen. See the header.
PLATE = 1008
MIN_WIDTH = PLATE
MAX_WIDTH = PLATE * 2
MAX_BYTES = 800_000

PICTURE = re.compile(r"!\[(.*?)\]\(([^)\s]+)\)")


def intrinsic(path):
    """check-image-scale.py's header reader, imported rather than copied: it is
    the file that fails on a width/height attribute disagreeing with the file,
    so it is the file that decides what the file's width is."""
    spec = importlib.util.spec_from_file_location(
        "cf_image_scale", pathlib.Path(__file__).with_name("check-image-scale.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.intrinsic(str(path))


def referenced():
    """Every picture named by a post, and which posts name it."""
    out = {}
    if not POSTS.is_dir():
        return out
    for post in sorted(POSTS.glob("*.md")):
        for m in PICTURE.finditer(post.read_text(encoding="utf-8")):
            out.setdefault(m.group(2).strip(), []).append(post.name)
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
                "is %d and twice that is the ceiling.\n    Export it at %d px — "
                "in Notion, replace the image with a smaller export."
                % (path, w, PLATE, MAX_WIDTH))
        if size > MAX_BYTES:
            findings.append(
                "HEAVY     design-system/assets/img/%s is %.1f MB; the budget is "
                "%.0f kB.\n    At %d x %d that is either barely compressed or "
                "larger than the box." % (path, size / 1e6, MAX_BYTES / 1e3, w, h))
        if args.verbose:
            print("  %-52s %5d x %-5d %6.0f kB  %s"
                  % (path, w, h, size / 1e3, where))

    if NEWS_IMG.is_dir():
        for f in sorted(NEWS_IMG.iterdir()):
            if not f.is_file():
                continue
            rel = f.relative_to(IMG).as_posix()
            if rel not in used:
                findings.append(
                    "ORPHANED  design-system/assets/img/%s is named by no post.\n"
                    "    A picture outlives its post only when something forgot "
                    "to remove it — run: python3 scripts/sync-news-notion.py"
                    % rel)

    if findings:
        print("news images: %d finding(s)\n" % len(findings), file=sys.stderr)
        for f in findings:
            print("  " + f, file=sys.stderr)
        return 1

    print("news images: %d picture(s) in %d post(s), every one between %d and "
          "%d px on a %d px plate and under %.0f kB."
          % (len(used), len({p for ps in used.values() for p in ps}),
             MIN_WIDTH, MAX_WIDTH, PLATE, MAX_BYTES / 1e3))
    return 0


if __name__ == "__main__":
    sys.exit(main())
