#!/usr/bin/env python3
"""Every page that can be shared carries a share card, and no other page does.

THE RULE, AND IT IS THE PAGE'S OWN. A share card is for a link somebody pastes
on purpose, which is the same set as the pages that want to be found. So:

    a page carries Open Graph metadata
    EXACTLY WHEN it has a <meta name="description"> and is not `noindex`.

Both halves are things the page already says about itself, which is what makes
the rule enforceable rather than a list somebody keeps. It falls the right way
on every edge this site has:

  404.html                 no description. Served with a 404 status; a polished
                           card over a dead address is a lie.
  kontakt-danke.html       noindex, and no description. The page you see after
  bewerbung-danke.html     sending something — a link to it is a link to nothing.
  suche.html               noindex, follow. Their <title> quotes the reader's own
  suche-leer.html          query, and og:title would be a fourth place that text
                           is echoed into — the other three are named in
                           README.md — on the one surface where the escaping is
                           somebody else's crawler's problem.

AND THE COUNT IS NOT REMEMBERED. Two documents state how many plates ship —
foundations/share.html twice and scripts/README.md once — and a hand-kept count
in prose is the thing this repository has watched go stale most often. Both are
re-derived here from build-og-plates.py's own table.

WHAT ELSE IS CHECKED. The block is not merely present, it is IDENTICAL to what
scripts/og_meta.py emits for that page: same fields, same order, same origin,
same locale pair for the edition, og:title and og:description equal to the
page's own <title> and description, and og:url and the canonical link naming
the page's SHIPPED address on the canonical host — og_meta.address() asks
build-site.py, so /blog/<slug>.html and not beitrag-<slug>.html. Thirteen pattern pages carry the block as
authored markup and three generators write it for everything else; this is what
holds those two to each other.

    python3 scripts/check-open-graph.py
    python3 scripts/check-open-graph.py -v
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import og_meta                                                    # noqa: E402

PATTERNS = os.path.join(ROOT, "design-system", "patterns")

# The generated families. A page whose name starts with one of these is that
# route in another instance, and carries that route's plate.
FAMILIES = (("news-thema-", "news-thema"),
            ("stelle-", "karriere-stelle"),
            ("beitrag-", "blog-artikel"))

TITLE = re.compile(r"<title>(.*?)</title>", re.S)
DESC = re.compile(r'<meta name="description" content="([^"]*)">')
ROBOTS = re.compile(r'<meta name="robots" content="([^"]*)"')
OG_LINE = re.compile(r'^\s*(?:<meta (?:property="og:|name="twitter:)|<link rel="canonical").*$', re.M)
COMMENT = re.compile(r"<!--.*?-->", re.S)


def _plates():
    """build-og-plates.py, loaded by path — its name is not an identifier."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "cf_og_plates", os.path.join(HERE, "build-og-plates.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


PLATES = _plates()


def seed_for(stem):
    """The plate a page's route uses, or None if the route ships none."""
    if stem in PLATES.PAGE_SEED:
        return PLATES.PAGE_SEED[stem]
    for prefix, seed in FAMILIES:
        if stem.startswith(prefix):
            return seed
    return None


def pages():
    """Every pattern page, both editions, authored and generated."""
    out = []
    for name in sorted(os.listdir(PATTERNS)):
        if name.endswith(".html"):
            out.append(("de", name[:-5], os.path.join(PATTERNS, name)))
    en = os.path.join(PATTERNS, "en")
    if os.path.isdir(en):
        for name in sorted(os.listdir(en)):
            if name.endswith(".html"):
                out.append(("en", name[:-5], os.path.join(en, name)))
    return out


# Where the number of plates is written in prose, and what it is written as.
COUNTS = (
    ("design-system/foundations/share.html",
     r"The <strong>(\d+)</strong> routes with a description"),
    ("design-system/foundations/share.html",
     r"<strong>(\d+)</strong> marks ship today"),
    ("scripts/README.md",
     r"one 1200 . 630 share plate per route, (\d+) today"),
)


def counted(verbose):
    """Every prose count of the plates, held to build-og-plates.py's table."""
    want = len(set(PLATES.PAGE_SEED.values()))
    out = []
    for rel, pattern in COUNTS:
        src = open(os.path.join(ROOT, rel), "r", encoding="utf-8").read()
        m = re.search(pattern, src)
        if not m:
            out.append("%s no longer states how many plates ship, in the shape "
                       "this check reads (%s)." % (rel, pattern))
        elif int(m.group(1)) != want:
            out.append("%s says %s plates ship and build-og-plates.py builds %d."
                       % (rel, m.group(1), want))
        elif verbose:
            print("  count %-42s %d" % (rel, want))
    return out


def main(argv):
    verbose = "-v" in argv or "--verbose" in argv
    faults = []
    carried = 0

    # Resolved once: the module read is the same for every page.
    seeds = {}

    for edition, stem, path in pages():
        src = open(path, "r", encoding="utf-8").read()
        # The head's own notes talk about these tags in prose; strip comments
        # before deciding what the page declares.
        bare = COMMENT.sub("", src)

        desc_m = DESC.search(bare)
        robots = ROBOTS.search(bare)
        noindex = bool(robots and "noindex" in robots.group(1))
        wants = bool(desc_m) and not noindex

        found = OG_LINE.findall(bare)
        name = "%s/%s.html" % (edition, stem)

        if not wants:
            if found:
                why = "it is noindex" if noindex else "it has no description"
                faults.append("%s carries a share card and should not — %s."
                              % (name, why))
            elif verbose:
                print("  none  %s" % name)
            continue

        if not found:
            faults.append("%s has a description and is indexable, so it is a "
                          "page somebody will paste — and it has no share card."
                          % name)
            continue

        if stem not in seeds:
            seeds[stem] = seed_for(stem)
        seed = seeds[stem]
        if seed is None:
            faults.append("%s wants a share card and no plate is built for its "
                          "route — add it to PAGE_SEED in build-og-plates.py."
                          % name)
            continue

        title = TITLE.search(bare).group(1)
        want = [line for line in og_meta.block(title, desc_m.group(1), seed,
                                               edition, stem + ".html")
                if not line.startswith("<!--") and not line.startswith("     ")]
        got = [line.strip() for line in found]
        if got != want:
            extra = [l for l in got if l not in want]
            missing = [l for l in want if l not in got]
            detail = []
            if missing:
                detail.append("missing " + "; ".join(missing))
            if extra:
                detail.append("unexpected " + "; ".join(extra))
            if not detail:
                detail.append("the fields are in a different order")
            faults.append("%s: %s" % (name, " / ".join(detail)))
            continue

        carried += 1
        if verbose:
            print("  card  %-34s %s.png" % (name, seed))

    faults.extend(counted(verbose))

    if faults:
        print("check-open-graph: %d fault(s).\n" % len(faults),
              file=sys.stderr)
        for f in faults:
            print("  " + f, file=sys.stderr)
        print("\n  The rule: a page carries a share card exactly when it has a "
              "description\n  and is not noindex. "
              "→ design-system/foundations/share.html", file=sys.stderr)
        return 1

    print("open graph OK — %d page(s) carry a share card, every field derived "
          "from the page." % carried)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
