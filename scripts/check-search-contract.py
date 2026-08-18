#!/usr/bin/env python3
"""The search page, the script that answers it, and the index they agree on.

check-script-contract.py holds the two behaviours every pattern page carries —
the consent flow and the phone navigation — and its argument is that every
failure in that class is SILENT: a data-cf-consent-action spelled `acept` is
rendered, focusable, announced and answered by nobody. /suche is the third
behaviour and it is worse in exactly the same way, because the page it fails on
already looks finished. patterns/suche.html ships six results for "Telemetrie"
with the term in its field and the count in three places. Break one hook in
assets/js/cf-search.js and the page keeps drawing all of that — for every
query, at every address — and the only reader who notices is the one who reads
the results.

WHAT THE PIECES ARE. Three files, and the seams between them are what this
holds:

  patterns/suche.html          the drawing, the hooks, and every sentence the
                               answer is written in, in <template> so that
                               design-system/i18n/en.json still owns the copy
  assets/js/cf-search.js       the arithmetic: match, rank, excerpt, fragment
  assets/search/index-*.json   the answers, built by build-search-index.py out
                               of the pages that actually ship

THE VOCABULARY IS READ FROM THE SCRIPT AND FROM THE INDEX, never typed here —
the same discipline check-script-contract.py states for the consent words. A
hook renamed in the script is enforced under its new name on the next run; a
hook the script stops using stops being required. A kind that appears in the
index (page, post, job, topic, section) must be a word the page can name,
because the script asks for `kind-<that>` and would otherwise draw a result
with no label.

THE RULES. Five.

  HOOKS     every [data-cf-search-*] attribute the script queries for exists on
            a page that loads the script. The script gives up silently when a
            hook is missing — it has to, since it also runs on a page that is
            merely a specimen — so a typo here is a page that quietly stays the
            specimen for ever.
  HEAD      a page that loads cf-search.js loads it from <head>. Same placement
            argument as NAV-HEAD one file over, and the same cost for getting
            it wrong: the attribute on <html> is what components.css hides the
            shipped answer with, and written after the body it is written after
            that answer has been painted.
  KEYS      every string the script asks the page for is in the copy template,
            and every string in the copy template is asked for. Both
            directions: a missing key draws an empty label, and a spare one is
            a sentence in the catalogue, translated into English, that nothing
            renders.
  STATES    the two block states the script can draw — the empty answer and the
            unreachable index — are present as templates and each is the inline
            error block components/error-state.html specifies, with a route
            out. A dead end with no exit is the one thing that chapter forbids.
  INDEX     every record in a built index resolves: the file exists under the
            repository root, and where the record carries an anchor, that id is
            on that page. A result whose link 404s is worse than no result, and
            an anchor that has been renamed lands the reader at the top of a
            page that was supposed to be the answer.

INDEX is skipped, loudly, when the index has not been built — a fresh checkout
has no website in it, and this check refusing to run at a desk is better than
it passing vacantly. In CI the build step runs first, so it always runs there.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-search-contract.py       # check, exit 1 on a finding
    python3 scripts/check-search-contract.py -v    # list what was audited
"""

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
PATTERNS = DS / "patterns"
SCRIPT = DS / "assets" / "js" / "cf-search.js"
INDEX = DS / "assets" / "search"

# Comments and quoted specimens are text; a parser never mistakes them for
# markup, and neither does this.
MASK = re.compile(
    r"<!--.*?-->|<pre\b.*?</pre>|<code\b.*?</code>|<textarea\b.*?</textarea>",
    re.S | re.I,
)


def strip_js_comments(src):
    """Blank out /* */ and // runs so prose about a hook is not a hook."""
    out, i, n, state = [], 0, len(src), None
    while i < n:
        c, nxt = src[i], src[i + 1] if i + 1 < n else ""
        if state is None:
            if c == "/" and nxt == "*":
                state, i = "block", i + 2
                continue
            if c == "/" and nxt == "/":
                state, i = "line", i + 2
                continue
            if c in "'\"":
                state = c
            out.append(c)
        elif state == "block":
            if c == "*" and nxt == "/":
                state, i = None, i + 2
                continue
            out.append("\n" if c == "\n" else " ")
        elif state == "line":
            if c == "\n":
                state = None
                out.append(c)
            else:
                out.append(" ")
        else:
            if c == "\\":
                out.append(" ")
                i += 2
                continue
            if c == state:
                state = None
            out.append(c)
        i += 1
    return "".join(out)


def audit(verbose):
    findings = []
    if not SCRIPT.exists():
        return ["assets/js/cf-search.js is missing — the search page has no answer"]
    js = strip_js_comments(SCRIPT.read_text(encoding="utf-8"))

    # THE CONTRACT, read out of the script. Every attribute it selects on, and
    # every literal string it asks the page's copy table for.
    hooks = sorted(set(re.findall(r"\[(data-cf-search[\w-]*)", js)))
    # Every literal inside a copy(...) call, and the call is not always a bare
    # one: the claim picks its singular in the argument, `copy(n === 1 ?
    # 'claim-one' : 'claim')`, and both halves are keys the page owes.
    keys = set()
    for call in re.findall(r"copy\(([^)]*)\)", js):
        keys |= set(re.findall(r"'([\w-]+)'", call))
    # The one key that is composed rather than written: `copy('kind-' + doc.kind)`.
    # Which kinds exist is the index's fact, not this file's — see below.
    composed = re.findall(r"copy\('([\w-]+-)'\s*\+", js)
    keys -= set(composed)

    # The templates: the one selected by name in the source, plus the block
    # states, which the script reaches by state('empty') / state('error') and
    # therefore names just as plainly.
    tpls = sorted(set(re.findall(r'data-cf-search-tpl="([\w-]+)"', js))
                  | set(re.findall(r"state\('(\w+)'\)", js)))
    states = sorted(set(re.findall(r"state\('(\w+)'\)", js)))
    if not hooks or not keys:
        findings.append(
            "assets/js/cf-search.js\n    CONTRACT  no hooks or no copy keys "
            "found in the script — this check has nothing to hold the page to")
        return findings

    kinds = set()
    built = sorted(INDEX.glob("index-*.json"))
    for path in built:
        for rec in json.loads(path.read_text(encoding="utf-8"))["docs"]:
            kinds.add(rec["kind"])
    for stem in composed:
        keys |= {stem + kind for kind in kinds}

    # THE PAGES THAT SHIP THE BEHAVIOUR. A page that does not load the script is
    # a specimen and is held to nothing here, exactly as a consent fragment on a
    # page without cf-consent.js is an illustration.
    live = []
    for page in sorted(PATTERNS.glob("*.html")):
        src = page.read_text(encoding="utf-8")
        if "cf-search.js" not in MASK.sub(" ", src):
            continue
        live.append(page)
        name = "design-system/patterns/%s" % page.name
        body = MASK.sub(" ", src)
        head = body.split("</head>", 1)[0]

        if "cf-search.js" not in head:
            findings.append(
                "%s\n    HEAD      cf-search.js is loaded after </head>. It "
                "writes data-cf-search on <html>, which is what components.css\n"
                "              hides the shipped result set with — written that "
                "late, every query paints six wrong answers first." % name)

        for hook in hooks:
            if re.search(r"\b%s\b" % re.escape(hook), body):
                continue
            findings.append(
                "%s\n    HOOKS     the script selects on [%s] and this page "
                "carries no such attribute — it will leave the page as the "
                "specimen, silently." % (name, hook))

        for tpl in tpls:
            if 'data-cf-search-tpl="%s"' % tpl not in body:
                findings.append(
                    '%s\n    HOOKS     no <template data-cf-search-tpl="%s">'
                    % (name, tpl))

        # KEYS, both directions.
        copy_tpl = re.search(
            r'<template data-cf-search-tpl="copy">(.*?)</template>', body, re.S)
        if not copy_tpl:
            continue
        present = set(re.findall(r'data-key="([\w-]+)"', copy_tpl.group(1)))
        for key in sorted(keys - present):
            findings.append(
                '%s\n    KEYS      the script asks for copy("%s") and the copy '
                "template has no [data-key] for it — the label draws empty"
                % (name, key))
        for key in sorted(present - keys):
            findings.append(
                '%s\n    KEYS      [data-key="%s"] is a sentence nothing reads. '
                "It is still in en.json and still translated." % (name, key))

        # STATES: each block state is the inline error block, and it has an exit.
        for state in states:
            block = re.search(
                r'<template data-cf-search-tpl="%s">(.*?)</template>' % state,
                body, re.S)
            if not block:
                continue
            if "cf-error--inline" not in block.group(1):
                findings.append(
                    "%s\n    STATES    the %s state is not .cf-error--inline. "
                    "Zero results is not an error page and not a 404 — it is "
                    "the inline block at 200." % (name, state))
            if "<a " not in block.group(1):
                findings.append(
                    "%s\n    STATES    the %s state offers no route out. A dead "
                    "end needs an exit — components/error-state.html's own rule."
                    % (name, state))

    if not live:
        findings.append(
            "design-system/patterns\n    HOOKS     no page loads "
            "cf-search.js — /suche answers nothing")

    # INDEX. Every address in a built index is a page, and every anchor is on it.
    if not built:
        print("check-search-contract: no index built — run "
              "`python3 scripts/build-search-index.py` for the INDEX rule.",
              file=sys.stderr)
    for path in built:
        index = json.loads(path.read_text(encoding="utf-8"))
        ids = {}
        for rec in index["docs"]:
            url, _, anchor = rec["url"].partition("#")
            page = ROOT / url
            if not page.exists():
                findings.append(
                    "%s\n    INDEX     %s is not a page — a result that 404s"
                    % (path.relative_to(ROOT).as_posix(), rec["url"]))
                continue
            if not anchor:
                continue
            if url not in ids:
                ids[url] = set(re.findall(
                    r'\bid="([^"]+)"', page.read_text(encoding="utf-8")))
            if anchor not in ids[url]:
                findings.append(
                    "%s\n    INDEX     %s names an id that is not on the page — "
                    "the reader lands at the top of it"
                    % (path.relative_to(ROOT).as_posix(), rec["url"]))

    if verbose:
        print("  script    %d hooks, %d templates, %d copy keys"
              % (len(hooks), len(tpls), len(keys)))
        print("  pages     %s" % ", ".join(p.name for p in live))
        for path in built:
            index = json.loads(path.read_text(encoding="utf-8"))
            print("  %-14s %d records, %d kinds"
                  % (path.name, len(index["docs"]), len(kinds)))
    return findings


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list the contract and everything held to it")
    args = ap.parse_args()

    findings = audit(args.verbose)
    if findings:
        print("check-search-contract: %d finding(s)\n" % len(findings))
        for f in findings:
            print(f)
        return 1
    print("check-search-contract: the page, the script and the index agree. OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
