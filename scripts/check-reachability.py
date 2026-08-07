#!/usr/bin/env python3
"""Every shipped route can be walked to from the site's front door.

check-registered.py holds the documentation's door: every pattern page carries
a .docs-card in the section index, so a reader OF THE DESIGN SYSTEM can arrive
at every page. Since build-site.py started publishing the patterns as the
website itself, that stopped being the whole question. The site's reader never
sees design-system/index.html — for them the only ways into a page are the
hrefs on the pages themselves, and that graph had no gate. It had a hole to
prove it: suche.html shipped to production for the section's whole life
reachable from exactly one place, the 404 page's "Wege von hier" — a search
page you could only find by first asking for a page that does not exist. The
links routine recorded the orphan twice and correctly left the route decision
to the build lane; this check is that decision made durable.

WHAT IT CHECKS. A breadth-first walk over live hrefs — comments, <pre>, <code>
and <textarea> bodies masked — starting at landing-page.html, the document
build-site.py ships as index.html and the address every visitor lands on.
Every pattern page must be walked to. Counting inbound links would not be
enough, and the first draft of this file proved it: the 404 page IS a pattern
page, so its "Wege von hier" gave suche.html an inbound link and the exact
defect this check was born from passed. A walk gets that for free — nothing
links to 404.html, the walk never enters it, and a link that only an error
page carries counts for nothing, which is what it is worth.

Two kinds of page are lawfully un-walked, each named with its reason rather
than skipped:

  SERVER ROUTES   404.html is where the server sends every address that
                  misses. No page links to an error, and none should.

  STATE PAGES     suche-leer.html, karriere-leer.html and kontakt-danke.html
                  are not routes, they are states of routes: the empty result
                  set at /suche, the empty register at /karriere, the response
                  after the form at /kontakt posts. In production the server
                  renders them at the canonical address; in this file-per-state
                  tree they are separate documents nothing should link to.
                  Each one names its canonical file in STATE_OF, and the check
                  requires THAT file to be walked in its place — a state
                  standing in for an orphaned route would be the same hole one
                  file over.

A new page that is neither linked from the walked site nor entered here fails,
which is the point: "a page nothing links to is not shipped" is the build
lane's oldest rule, and this is the half of it check-registered.py could not
run.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-reachability.py       # check, exit 1 on a finding
    python3 scripts/check-reachability.py -v    # list every page's walk depth
"""

import argparse
import collections
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PATTERNS = ROOT / "design-system" / "patterns"

# The front door: build-site.py ships this file as the site's index.html.
ENTRY = "landing-page.html"

# States of canonical routes: the server renders these at the canonical
# address, so no page links to them — instead their canonical file must be
# walked. Adding a state page means adding a line here, deliberately.
STATE_OF = {
    "suche-leer.html": "suche.html",
    "karriere-leer.html": "karriere.html",
    "kontakt-danke.html": "kontakt.html",
    "bewerbung-danke.html": "bewerbung.html",
    # The filtered archive: /news?thema=… is the canonical address, and the
    # chips and tag links that arrive there say so as query strings on the
    # canonical file. A link to the state document would claim a route that
    # does not exist.
    "news-thema.html": "news.html",
}

# Routes the server reaches on its own; linking to them would be the defect.
SERVER_ROUTES = {"404.html"}

# Regions whose contents are documentation, not markup the browser acts on.
MASK = re.compile(
    r"<!--.*?-->|<pre\b.*?</pre>|<code\b.*?</code>|<textarea\b.*?</textarea>",
    re.S | re.I,
)

HREF = re.compile(r"""href\s*=\s*["']([^"']+)["']""", re.I)
OFFSITE = re.compile(r"^[a-z][a-z0-9+.-]*:", re.I)


def blank(m):
    """Replace a masked region with spaces, keeping newlines for line numbers."""
    return re.sub(r"[^\n]", " ", m.group(0))


def outbound(path):
    """Sibling pattern pages a page's live markup links to."""
    text = MASK.sub(blank, path.read_text(encoding="utf-8"))
    targets = []
    for m in HREF.finditer(text):
        value = m.group(1).strip()
        if not value or value.startswith(("/", "#")) or OFFSITE.match(value):
            continue
        target = value.partition("#")[0].partition("?")[0]
        if target and "/" not in target and target != path.name:
            targets.append(target)
    return targets


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every page with its depth in the walk")
    args = ap.parse_args()

    pages = {p.name for p in PATTERNS.glob("*.html")}
    if ENTRY not in pages:
        print("design-system/patterns/%s\n    the walk's entry — the file "
              "build-site.py ships as index.html — does not exist" % ENTRY,
              file=sys.stderr)
        return 1

    links = {name: [t for t in outbound(PATTERNS / name) if t in pages]
             for name in sorted(pages)}

    depth = {ENTRY: 0}
    via = {ENTRY: None}
    queue = collections.deque([ENTRY])
    while queue:
        here = queue.popleft()
        for target in links[here]:
            if target not in depth:
                depth[target] = depth[here] + 1
                via[target] = here
                queue.append(target)

    findings = []
    for name in sorted(pages):
        if name in SERVER_ROUTES:
            if args.verbose:
                print("  %-28s server route, lawfully un-walked" % name)
            continue
        if name in STATE_OF:
            canonical = STATE_OF[name]
            if canonical not in depth:
                findings.append((name, "state of %s, which the walk never "
                                 "reaches either — a state standing in for an "
                                 "orphaned route" % canonical))
            elif args.verbose:
                print("  %-28s state of %s, walked at depth %d" %
                      (name, canonical, depth[canonical]))
            continue
        if name not in depth:
            findings.append((name, "no chain of live hrefs from %s arrives "
                             "here — the page ships, renders, and no reader "
                             "who entered at the front door can walk to it"
                             % ENTRY))
        elif args.verbose:
            step = "the front door" if via[name] is None else "via %s" % via[name]
            print("  %-28s depth %d, %s" % (name, depth[name], step))

    if findings:
        for name, why in findings:
            print("design-system/patterns/%s\n    %s" % (name, why),
                  file=sys.stderr)
        print("\n%d unreachable route%s on the shipped site. Every pattern "
              "page is walked from %s, or entered in STATE_OF / SERVER_ROUTES "
              "with its reason." %
              (len(findings), "" if len(findings) == 1 else "s", ENTRY),
              file=sys.stderr)
        return 1

    walked = sum(1 for n in pages
                 if n not in SERVER_ROUTES and n not in STATE_OF)
    print("reachability: %d pattern pages — %d walked from %s (max depth %d), "
          "%d server-rendered states whose canonical routes are walked, "
          "%d server route%s." %
          (len(pages), walked, ENTRY, max(depth.values()), len(STATE_OF),
           len(SERVER_ROUTES), "" if len(SERVER_ROUTES) == 1 else "s"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
