#!/usr/bin/env python3
"""The website, collected into dist/ for a deploy that needs a directory.

WHY THIS EXISTS. GitHub Pages uploads the repository root and the root is the
document root, which is why build-site.py writes the pages there and why there
has never been a build directory. Cloudflare needs one anyway, for a reason
that has nothing to do with taste: wrangler writes its own state into
.wrangler/ *inside* the assets directory, so pointing it at the repo root
makes it watch the directory it is writing to. `wrangler dev` then reloads
forever — measured, not guessed: 387 reloads in two minutes before this script
existed. .assetsignore does not help; it governs what is uploaded, not what is
watched.

Naming the output also makes the deploy say what the website is. The repo root
holds the generator, seventy-five checks, the routines' briefs, four
screenshots kept for comparison against the Figma drawings and the Worker
itself. An allowlist cannot leak any of them by forgetting a line.

WHAT THE WEBSITE IS. Two things, and the list is derived, not typed:

  the pages   every name build-site.py ships, read from its own SHIP table, so
              a page added there appears here without this file changing
  design-system/   the assets every page loads, and the documentation, which is
              published and linked from the README as a URL

Nothing else at the root is referenced by any shipped page.

    python3 scripts/stage-site.py            # write dist/
    python3 scripts/stage-site.py --check    # fail if dist/ is missing or stale
"""

import argparse
import ast
import filecmp
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"


def ship_names():
    """The shipped page names, read out of build-site.py's SHIP table.

    Read as text rather than imported, because the file's name is not a valid
    identifier. The table is a literal dict, so ast.literal_eval is exact.
    """
    src = (ROOT / "scripts" / "build-site.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "SHIP" for t in node.targets
        ):
            return sorted(ast.literal_eval(node.value).values())
    raise SystemExit("stage-site: no SHIP table in scripts/build-site.py")


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


def stage(check):
    pages = ship_names()
    missing = [p for p in pages if not (ROOT / p).exists()]
    if missing:
        print("stage-site: not built — run `python3 scripts/build-site.py` first.\n"
              "  missing: %s" % ", ".join(missing), file=sys.stderr)
        return 1

    if check:
        if not DIST.is_dir():
            print("stage-site: dist/ does not exist.", file=sys.stderr)
            return 1
        stale = [p for p in pages
                 if not (DIST / p).exists()
                 or not filecmp.cmp(ROOT / p, DIST / p, shallow=False)]
        if not (DIST / "design-system").is_dir():
            stale.append("design-system/")
        if stale:
            print("stage-site: dist/ is stale — %s" % ", ".join(stale), file=sys.stderr)
            return 1

        headers = DIST / "_headers"
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

        print("dist OK — %d pages and the design system, current with the root; "
              "%d directory index%s served."
              % (len(pages), len(directory_routes()),
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

    if site_origin() is not None:
        (DIST / "_headers").write_text(HEADERS, encoding="utf-8")

    total = sum(1 for _ in DIST.rglob("*") if _.is_file())
    print("dist built — %d pages, %d files in all." % (len(pages), total))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="fail if dist/ is missing or stale rather than writing it")
    args = ap.parse_args()
    return stage(args.check)


if __name__ == "__main__":
    sys.exit(main())
