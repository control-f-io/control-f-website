#!/usr/bin/env python3
"""The website, collected into dist/ for both deploys.

WHY THIS EXISTS. Cloudflare needs a directory holding the website and nothing
else, for a reason that has nothing to do with taste: wrangler writes its own
state into .wrangler/ *inside* the assets directory, so pointing it at the repo
root makes it watch the directory it is writing to. `wrangler dev` then reloads
forever — measured, not guessed: 387 reloads in two minutes before this script
existed. .assetsignore does not help; it governs what is uploaded, not what is
watched.

AND THEN GITHUB PAGES WANTED IT TOO. Pages uploaded the repository root — the
whole tracked checkout minus .git and .github — because the root is the
document root and the pages are written there. That published every file in the
repository: all six generators and every check script, the Worker's source and
wrangler.toml, the content store with its ledgers, the browser-audit frames, and
for a while twelve editor autosaves. Verified by fetching them, not assumed:
/scripts/build-site.py and /worker/index.js answered 200. The Cloudflare copy
never had that problem because it ships this allowlist, so Pages ships it now as
well and the two surfaces are the same bytes by construction.

TWO SURFACES, ONE DIRECTORY. The content is identical; the difference is one
file. `--surface worker` writes dist/_headers, which marks this copy noindex
while some other host is canonical, and `--check` holds the pairing with
SITE_ORIGIN. `--surface pages` does not write it: Pages IS the canonical site,
must be indexable, and does not read _headers anyway. The Worker-only
assertions — that every directory index is a URL run_worker_first names — are
checked for the worker surface only, so a Cloudflare routing question can never
fail the Pages deploy.

Naming the output also makes the deploy say what the website is. The repo root
holds the generator, the checks, the routines' briefs, the content store and
the Worker itself. An allowlist cannot leak any of them by forgetting a line.
(The reference frames that used to sit at the root beside them now live under
docs/design-system-frames/, with the browser audits.)

WHAT THE WEBSITE IS. Four things, and every list is derived, not typed:

  the pages   every name build-site.py ships, ASKED OF THAT FILE rather than
              read out of it, so a page added there appears here without this
              file changing
  design-system/   the assets every page loads, and the documentation, which is
              published and linked from the README as a URL
  sitemap.xml every indexable page on the canonical host — SITE_ORIGIN — with
              its other edition as an hreflang alternate. Written for both
              surfaces from the pages themselves: a page that says noindex is
              left out, and the 404 page is. There is deliberately no
              robots.txt: the site is meant to be read by every crawler,
              index and script there is, and a sitemap says where to look
              without a file that says where not to.
  the old addresses   content/redirects.txt, the Wix site's URLs and where
              each now lives. GitHub Pages cannot answer a 301, so on that
              surface each becomes a stub page under the old path that
              meta-refreshes to the new one and names it canonical; the Worker
              surface gets the same table as Cloudflare's _redirects file.

Nothing else at the root is referenced by any shipped page.

    python3 scripts/stage-site.py                      # write dist/ for the Worker
    python3 scripts/stage-site.py --check              # fail if dist/ is missing or stale
    python3 scripts/stage-site.py --surface pages      # write dist/ for GitHub Pages
    python3 scripts/stage-site.py --surface pages --check
"""

import argparse
import filecmp
import importlib.util
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
REDIRECTS = ROOT / "content" / "redirects.txt"


def ship_names():
    """The shipped page names, asked of build-site.py.

    IT USED TO READ THE `SHIP` LITERAL out of that file with ast.literal_eval,
    which was exact for as long as the table was the whole list. It stopped
    being: build-site.py's ship() adds the generated content pages — one per
    news post with an article, one per opening with an advertisement — because
    those arrive without anybody editing a table, which is the entire point of
    generating them.
    
    So dist/ held the thirty-eight named pages and none of the generated ones,
    and the Worker answered /stelle-data-engineer.html with the 404 page while
    GitHub Pages, which uploads the repository root, served it correctly.
    Measured on the workers.dev deployment before this was fixed.
    
    The function is imported rather than the literal parsed, because a
    generated list cannot be read as a literal at all — and because the answer
    then comes from the one place that decides it.
    """
    spec = importlib.util.spec_from_file_location(
        "cf_build_site", ROOT / "scripts" / "build-site.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return sorted(mod.ship().values())


def directory_routes():
    """Every directory in dist/ that has an index.html, as a URL path.

    wrangler.toml sets html_handling = "none", because every other mode answers
    /kontakt.html with a 307 to /kontakt — which would rewrite the address of
    every page and break the form's POST outright. The cost is that nothing
    maps a directory to its index.html any more, so worker/index.js does it,
    for the directories named in run_worker_first.

    That list is written by hand and this is what stops it falling behind: a
    directory index that appears in dist/ without a route is a URL that used to
    work under GitHub Pages and now 404s, which no other check would see.
    """
    routes = set()
    for index in DIST.rglob("index.html"):
        rel = index.parent.relative_to(DIST).as_posix()
        routes.add("/" if rel == "." else "/%s/" % rel)
    return routes


def configured_routes():
    """The paths run_worker_first names, read out of wrangler.toml as text."""
    src = (ROOT / "wrangler.toml").read_text(encoding="utf-8")
    m = re.search(r"^run_worker_first = \[(.*?)\]", src, re.M | re.S)
    if not m:
        raise SystemExit("stage-site: no run_worker_first in wrangler.toml")
    return set(re.findall(r'"([^"]+)"', m.group(1)))


def site_origin():
    """SITE_ORIGIN from wrangler.toml, or None.

    It is set exactly while some OTHER host is the canonical site — today
    GitHub Pages, which cannot answer the contact form's POST and so sends it
    across to the Worker. Its presence is therefore the same fact as "this
    deployment is the second copy of the website", which is what HEADERS below
    is about.
    """
    src = (ROOT / "wrangler.toml").read_text(encoding="utf-8")
    m = re.search(r'^SITE_ORIGIN = "([^"]+)"', src, re.M)
    return m.group(1) if m else None


def indexable(name):
    """Whether a shipped page wants to be found: not the 404, not noindex."""
    if name in ("404.html", "en/404.html"):
        return False
    src = (ROOT / name).read_text(encoding="utf-8")
    m = re.search(r'<meta name="robots" content="([^"]*)"', src)
    return not (m and "noindex" in m.group(1))


def address(name):
    """A shipped name as the path a reader has: the directory for its index."""
    return name[:-len("index.html")] if name.endswith("index.html") else name


def sitemap(pages, origin):
    """sitemap.xml: every indexable page, each edition naming the other.

    The alternates are derived from the names alone — en/X is X's English
    edition, and build-i18n.py writes exactly that — and a pair is only written
    when both halves are indexable, so a page that is noindex in one edition
    is not advertised as the other's translation. No lastmod: a date derived
    from the deploy would say every page changed on every merge, which is
    worse information than none.
    """
    wanted = [p for p in pages if indexable(p)]
    have = set(wanted)
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
             '        xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for name in wanted:
        de = name[3:] if name.startswith("en/") else name
        en = "en/" + de
        lines.append("  <url>")
        lines.append("    <loc>%s/%s</loc>" % (origin, address(name)))
        if de in have and en in have:
            for lang, other in (("de", de), ("en", en)):
                lines.append('    <xhtml:link rel="alternate" hreflang="%s" href="%s/%s"/>'
                             % (lang, origin, address(other)))
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def redirects():
    """content/redirects.txt as (old path, shipped target) pairs, in file order."""
    rows = []
    for no, line in enumerate(REDIRECTS.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) != 2 or not parts[0].startswith("/"):
            raise SystemExit("stage-site: content/redirects.txt line %d is not "
                             "`/old-path target.html`: %r" % (no, line))
        rows.append((parts[0], parts[1]))
    return rows


def worker_redirects(rows):
    """The table as Cloudflare's _redirects file: one 301 per line.

    A source that is not ASCII is matched on its ASCII prefix and a splat.
    Cloudflare documents neither raw UTF-8 nor percent-encoding for a source,
    and a prefix-and-splat matches whichever of the two a browser sends. The
    prefixes are long enough that nothing else on the old site shares one.
    """
    out = ["# GENERATED by scripts/stage-site.py from content/redirects.txt — edit that file."]
    for src, dst in rows:
        out.append("%s  /%s  301" % (_ascii_prefix(src), address(dst)))
    return "\n".join(out) + "\n"


def _ascii_prefix(src):
    for i, ch in enumerate(src):
        if not ch.isascii():
            return src[:i] + "*"
    return src


STUB = """<!DOCTYPE html>
<!-- GENERATED by scripts/stage-site.py from content/redirects.txt: an address
     the old site had, answered on GitHub Pages — which cannot send a 301 —
     with the one kind of redirect a static file can carry. -->
<html lang="de">
<head>
<meta charset="utf-8">
<title>Umgezogen: %(url)s</title>
<meta http-equiv="refresh" content="0; url=%(url)s">
<link rel="canonical" href="%(url)s">
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
<p>Diese Seite ist umgezogen: <a href="%(url)s">%(url)s</a></p>
</body>
</html>
"""


def stub_path(src, rows, pages):
    """Where GitHub Pages must find the stub so that it answers the old path.

    Pages serves x.html at /x, so /post/slug is post/slug.html. Where the old
    path is a directory — one this site has, like /blog, or one the old site
    had, like /post over its posts — the stub is that directory's index, since
    a file beside a directory of the same name is not what Pages serves for
    the bare path. Decided from the two tables and not from dist/, so the
    answer does not depend on the order the stubs are written in.
    """
    rel = src.lstrip("/")
    below = [p for p in pages] + [other.lstrip("/") for other, _ in rows]
    if any(p.startswith(rel + "/") for p in below):
        return rel + "/index.html"
    return rel + ".html"


def stubs(rows, origin, pages):
    return {stub_path(src, rows, pages): STUB % {"url": "%s/%s" % (origin, address(dst))}
            for src, dst in rows}


def check_redirects(rows, pages):
    """A target that is not a shipped page, or a source that shadows one, is a
    deploy that must not happen: the first sends a reader to the 404 page with
    a 301 in front of it, the second hides a page of this site behind a stub."""
    shipped = set(pages)
    addresses = {address(p) for p in pages}
    faults = []
    seen = set()
    for src, dst in rows:
        if src in seen:
            faults.append("%s is listed twice" % src)
        seen.add(src)
        if dst not in shipped and dst != "/" and dst not in addresses:
            faults.append("%s -> %s, and %s is not a page this site ships" % (src, dst, dst))
        own = src.lstrip("/")
        if own in addresses or own + ".html" in shipped or own + "/" in addresses:
            faults.append("%s is an address this site serves itself — a redirect "
                          "there would shadow the page" % src)
    return faults


# Cloudflare reads _headers out of the assets directory the way Pages does; it
# is configuration and is not served as a file.
#
# WHY: while GitHub Pages is the canonical site, this deployment is a second
# public copy of the same pages, and a search engine that finds both picks the
# winner itself. The reader still reaches this copy — the form's error page is
# served from here — so it has to work; it just must not compete.
#
# It is written from site_origin() rather than typed into the repository so the
# two cannot disagree: at the cutover SITE_ORIGIN goes, this file stops being
# written, and the site becomes indexable in the same commit. --check holds
# that, so neither half can be forgotten.
HEADERS = "/*\n  X-Robots-Tag: noindex\n"


def stage(check, surface):
    worker = surface == "worker"
    pages = ship_names()
    missing = [p for p in pages if not (ROOT / p).exists()]
    if missing:
        print("stage-site: not built — run `python3 scripts/build-site.py` first.\n"
              "  missing: %s" % ", ".join(missing), file=sys.stderr)
        return 1

    origin = site_origin()
    if origin is None:
        print("stage-site: SITE_ORIGIN is gone from wrangler.toml, and the sitemap "
              "and the redirect stubs need the canonical host. See the cutover "
              "notes in that file.", file=sys.stderr)
        return 1
    rows = redirects()
    faults = check_redirects(rows, pages)
    if faults:
        print("stage-site: content/redirects.txt —\n  %s" % "\n  ".join(faults),
              file=sys.stderr)
        return 1

    def derived():
        """The files written from the pages rather than copied: by surface."""
        out = {"sitemap.xml": sitemap(pages, origin)}
        if worker:
            out["_redirects"] = worker_redirects(rows)
        else:
            out.update(stubs(rows, origin, pages))
        return out

    if check:
        if not DIST.is_dir():
            print("stage-site: dist/ does not exist.", file=sys.stderr)
            return 1
        stale = [p for p in pages
                 if not (DIST / p).exists()
                 or not filecmp.cmp(ROOT / p, DIST / p, shallow=False)]
        if not (DIST / "design-system").is_dir():
            stale.append("design-system/")
        for rel, text in derived().items():
            f = DIST / rel
            if not f.exists() or f.read_text(encoding="utf-8") != text:
                stale.append(rel)
        if stale:
            print("stage-site: dist/ is stale — %s" % ", ".join(stale), file=sys.stderr)
            return 1

        headers = DIST / "_headers"
        if not worker:
            # Nothing to pair with SITE_ORIGIN here: Pages is the canonical
            # site. A _headers in this dist/ means it was staged for the Worker,
            # and uploading that one would publish a stray file — and, read the
            # other way round, staging for Pages and deploying it to Cloudflare
            # would drop the noindex that keeps the second copy out of the
            # results. Each workflow stages its own dist/ from scratch, so this
            # only fires when the two are mixed up by hand.
            if headers.exists():
                print("stage-site: dist/_headers is here, so this dist/ was "
                      "staged for the Worker — restage with --surface pages.",
                      file=sys.stderr)
                return 1
            print("dist OK — %d pages, the design system, the sitemap and %d "
                  "redirect stubs, current with the root, staged for GitHub Pages."
                  % (len(pages), len(rows)))
            return 0

        wanted = site_origin() is not None
        if wanted and not headers.exists():
            print("stage-site: SITE_ORIGIN is set, so another host is the "
                  "canonical site, but dist/_headers is missing — this copy "
                  "would compete with it in search results.", file=sys.stderr)
            return 1
        if not wanted and headers.exists():
            print("stage-site: dist/_headers marks this copy noindex, but "
                  "SITE_ORIGIN is gone — if this deployment is now the site, "
                  "that header hides it from search entirely.", file=sys.stderr)
            return 1
        if wanted and headers.read_text(encoding="utf-8") != HEADERS:
            print("stage-site: dist/_headers is not what this script writes.",
                  file=sys.stderr)
            return 1

        served = configured_routes()
        orphans = sorted(r for r in directory_routes() if r not in served)
        if orphans:
            print("stage-site: dist/ has a directory index that nothing serves — %s\n"
                  "  html_handling is \"none\", so a directory is only reachable if\n"
                  "  wrangler.toml's run_worker_first names it and worker/index.js\n"
                  "  lists it in DIRECTORIES. Add it to both, or the URL 404s."
                  % ", ".join(orphans), file=sys.stderr)
            return 1

        print("dist OK — %d pages, the design system, the sitemap and %d "
              "redirects, current with the root; %d directory index%s served."
              % (len(pages), len(rows), len(directory_routes()),
                 "" if len(directory_routes()) == 1 else "es"))
        return 0

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()

    for name in pages:
        # Not every shipped page sits at the root any more: the English edition
        # is sixteen pages under en/, and SHIP names them with that prefix.
        # copy2 does not create the directory it is copying into, so a page in
        # a subdirectory crashed this loop rather than landing in dist/.
        dst = DIST / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, dst)

    # The stylesheets, scripts, fonts and images every page loads, plus the
    # documentation, which ships. One copy, the same one the patterns use.
    shutil.copytree(ROOT / "design-system", DIST / "design-system")

    if worker and site_origin() is not None:
        (DIST / "_headers").write_text(HEADERS, encoding="utf-8")

    for rel, text in derived().items():
        f = DIST / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text, encoding="utf-8")

    total = sum(1 for _ in DIST.rglob("*") if _.is_file())
    print("dist built for %s — %d pages, %d old addresses answered, %d files in all."
          % (surface, len(pages), len(rows), total))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="fail if dist/ is missing or stale rather than writing it")
    ap.add_argument("--surface", choices=("worker", "pages"), default="worker",
                    help="which deploy this dist/ is for (default: worker)")
    args = ap.parse_args()
    return stage(args.check, args.surface)


if __name__ == "__main__":
    sys.exit(main())
