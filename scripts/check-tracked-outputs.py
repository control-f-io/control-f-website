#!/usr/bin/env python3
"""No generated page is tracked in git, and every page build-site.py ships is one.

WHAT THIS REPLACED. Until 2026-08-17 the generated website was committed beside
its sources: 43 pages at the root, 43 under en/, 43 under
design-system/patterns/en/ and 25 generated pattern pages — 154 files, every
logical page existing four times in git, 70 % of all tracked HTML lines being
output. The costs were not theoretical. A one-word copy change rewrote four
files; `grep` for a class or a sentence answered four times over and only one
answer was the source; an hourly Notion import arrived as a ninety-six-file diff
that nobody could read, so nobody read it. `build-site.py --check` and
`build-i18n.py --check` existed to hold those copies to their sources, which is
the right answer to the wrong question — the copies did not need to be honest,
they needed to not be there.

WHY A CHECK AND NOT JUST .gitignore. Because .gitignore does not untrack what is
already tracked, and because the argument for committing output is a good one and
will be made again: somebody will want to read the English edition in a pull
request, or to see what an import changed, and `git add -f` is one flag away. That
is a decision worth making deliberately in a commit message, not by accident in a
hurry. So the rule is mechanical and this file is where it is written down.

THE RULE, both halves. No file matching a generated path is tracked; and every
page build-site.py's SHIP table names is a generated path this file knows about.
The second half is what stops the check going quietly out of date: a new family of
shipped pages — a fourth content type, a second English edition — would otherwise
be committed with nothing objecting, because a check that only knows three
prefixes cannot notice a fourth.

WHAT IS STILL TRACKED AND IS NOT A CONTRADICTION. design-system/patterns/news.html
and karriere.html are authored pages with generated regions inside comment fences;
blog-artikel.html, karriere-stelle.html and news-thema.html are the authored
specimens the generated pages are spliced from, and they ship as themselves too —
two of those three have a generated region as well, the one list of links into
the topic pages, because which of those pages exist is content and not drawing.
design-system/i18n/en.json and the two content/*/.catalogue.json ledgers are
written by generators and tracked on purpose — they are the record of which
strings a build owns, and a build cannot reconstruct them from the pages. The
gate's other half, scripts/build-and-verify.sh, is what holds those to their
sources: it builds and then fails if a tracked file moved.
"""

import argparse
import importlib.util
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

# The generated paths, as predicates over a repository-relative POSIX path. Each
# one mirrors a stanza of .gitignore; the wording of the reason is what a person
# who has just been failed by this needs to read.
RULES = (
    (lambda p: "/" not in p and p.endswith(".html"),
     "a shipped page at the root",
     "build-site.py writes every .html here out of design-system/patterns/, and "
     "deletes any it does not own."),
    (lambda p: p.startswith("en/") and p.endswith(".html"),
     "the English edition of a shipped page",
     "build-site.py writes it from design-system/patterns/en/."),
    (lambda p: any(p.startswith(f) or p.startswith("en/" + f)
                   for f in ("blog/", "stellen/", "news/thema/"))
     and p.endswith(".html"),
     "a content page in the folder it ships from",
     "build-site.py writes it from a flat pattern — patterns/beitrag-<slug>.html "
     "ships at blog/<slug>.html. The folder is a property of the address; the "
     "prefix is the property of the source."),
    (lambda p: p.startswith("design-system/patterns/en/"),
     "an English pattern page",
     "build-i18n.py writes it from the German pattern beside it and "
     "design-system/i18n/en.json."),
    (lambda p: re.fullmatch(r"design-system/patterns/beitrag-.+\.html", p) is not None,
     "a generated reading page",
     "build-articles.py writes one per news post that has text, in both editions."),
    (lambda p: re.fullmatch(r"design-system/patterns/stelle-.+\.html", p) is not None,
     "a generated Stelle page",
     "build-stellen.py writes one per opening that has an advertisement, in both "
     "editions."),
    (lambda p: re.fullmatch(r"design-system/patterns/news-thema-.+\.html", p) is not None,
     "a generated topic page",
     "build-news.py writes one per topic in use. news-thema.html — no slug — is "
     "the authored specimen and is not this."),
    (lambda p: p.startswith("design-system/assets/search/"),
     "a search index",
     "build-search-index.py writes one per edition out of the shipped pages. It "
     "is the only generated file under assets/, and it is generated for the same "
     "reason the pages are: it is derived, and a derived file in git is a copy "
     "that will one day disagree with what it was derived from."),
)


def generated(path):
    """The reason `path` is output, or None if it is a source."""
    for matches, what, why in RULES:
        if matches(path):
            return what, why
    return None


def tracked():
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, check=True,
                         capture_output=True, text=True).stdout
    return [line for line in out.splitlines() if line]


def shipped():
    """The pages build-site.py ships, asked of that file.

    Imported rather than parsed, for the reason stage-site.py gives: ship() adds
    the generated content pages by glob, so the answer is not a literal any more.
    """
    spec = importlib.util.spec_from_file_location(
        "cf_build_site", ROOT / "scripts" / "build-site.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return sorted(mod.ship().values())


def main():
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()

    bad = [(p,) + generated(p) for p in tracked() if generated(p)]
    if bad:
        print("check-tracked-outputs: %d generated file%s tracked in git."
              % (len(bad), "" if len(bad) == 1 else "s"), file=sys.stderr)
        for path, what, why in bad[:12]:
            print("    %s\n        is %s. %s" % (path, what, why),
                  file=sys.stderr)
        if len(bad) > 12:
            print("    … and %d more." % (len(bad) - 12), file=sys.stderr)
        print("\n  Build output does not belong in git — that is what this "
              "repository\n  carried until 2026-08-17, four copies of every page. "
              "Run:\n\n      git rm --cached <path>\n\n  and build it instead: "
              "sh scripts/build-all.sh", file=sys.stderr)
        return 1

    # The other half: a page this repository ships that no rule above calls
    # generated would be committable, and nothing else would notice.
    unclaimed = [p for p in shipped() if not generated(p)]
    if unclaimed:
        print("check-tracked-outputs: build-site.py ships %d page%s that no rule "
              "in this file calls output."
              % (len(unclaimed), "" if len(unclaimed) == 1 else "s"),
              file=sys.stderr)
        for path in unclaimed[:12]:
            print("    %s" % path, file=sys.stderr)
        print("\n  A new family of shipped pages needs a stanza in .gitignore and "
              "a rule\n  in RULES above, or it will be committed with nothing "
              "objecting.", file=sys.stderr)
        return 1

    print("tracked outputs: none — %d shipped pages, all of them built, "
          "%d files tracked." % (len(shipped()), len(tracked())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
