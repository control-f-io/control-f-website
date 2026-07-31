#!/usr/bin/env python3
"""Every name a page hands its scripts is a word the script answers.

The system ships two required scripts and both find their work by name.
cf-consent.js reaches for `[data-cf-consent-banner]`, answers five values of
`data-cf-consent-action`, reads two values of `data-cf-consent-category`, and
activates gated tags by `data-cf-consent`. cf-nav.js reaches for
`.cf-nav__toggle` and takes the panel from whatever id `aria-controls` names.
That is the whole wiring of the two behaviours every pattern page has — the
consent flow and the phone navigation — and not one strand of it was read by
any of the ninety checks beside this one.

WHY EVERY FAILURE IN THIS CLASS IS SILENT. A button whose action is spelled
`acept` is not an error to anything: the browser renders it, check-a11y.py
finds its name and its landmark in order, check-aria-vocabulary.py has no
opinion on data-* attributes, and cf-consent.js's dispatch walks its
if/else chain, matches nothing, and returns. The click is answered by
nobody. A category checkbox spelled `Statistik` is drawn, focusable,
checkable, announced — and never read and never written, because the script
compares tokens exactly. And an `aria-controls` pointing at the WRONG id is
the quietest of all: check-a11y.py's ARIA-REF holds that the id exists, not
that it is the panel, so cf-nav.js would wire the toggle to whatever element
the id lands on — aria-expanded announcing a menu open while data-open is
set on an element the stylesheet never watches, the drawn state and the
announced state disagreeing in exactly the way the script's one-writer
`set()` exists to prevent.

WHAT FOUND THIS. A browser sweep of all fifteen pattern pages — every
console message, every network failure, the dialog's focus contract (open
lands on the title, Escape restores the opener), the nav's Escape-and-
restore, a tab walk of every stop, in first-visit and return-visit states —
found the wiring CLEAN in every condition. But every fact that sweep
verified needed a running browser, and CI has no browser: every gate in
.github/workflows/design-system.yml is arithmetic on a file. So the sweep's
findings would hold exactly until the next typo, and twelve routines edit
these pages hourly. This check is the static shadow of that sweep — the
part of "the wiring works" that is countable in a file, held to the same
standard as the ninety checks beside it.

THE VOCABULARY IS READ FROM THE SCRIPTS, NOT COPIED INTO THE CHECK. The
five action words come from cf-consent.js's own dispatch chain and the two
categories from its CATEGORIES literal, so a word added to the script is
admitted here without editing this file, and a word removed starts failing
the pages that still use it. The two nav class names are asserted to appear
in cf-nav.js before they are enforced on any page — if the script renames
its contract, this check fails on the script, loudly, rather than holding
pages to a contract nobody ships any more.

THE RULES. Seven. The first three are vocabulary and hold everywhere in
design-system/ — a misspelled token is wrong in a component demo exactly as
it is wrong on a pattern page, and a token quoted in documentation prose or
a <code> sample is text, which a parser never mistakes for an attribute.

  ACTION      every data-cf-consent-action value is a word the dispatch in
              cf-consent.js answers.
  CATEGORY    every data-cf-consent-category value is in the script's
              CATEGORIES.
  GATE        every <script type="text/plain" data-cf-consent="…"> names a
              category that can ever be granted. A gated tag with an unknown
              category is a script that no decision, ever, will activate.

The four wiring rules hold where the wiring is live: every page under
patterns/, and any page anywhere that loads the script in question — a
documentation page that ships cf-consent.js has shipped the behaviour and
owes the whole contract. A demo fragment on a page that does not load the
script is an illustration, and is held only to the vocabulary.

  PANEL       every .cf-nav__toggle carries aria-controls, and the id it
              names is on the element carrying .cf-nav__list. Existence of
              the id is ARIA-REF's rule; identity is this one — the gap
              between them is a toggle wired to the wrong element with both
              checks green.
  NAV-HEAD    a page with a live .cf-nav__toggle loads cf-nav.js, from
              <head>. The placement is load-bearing, not habit: the script's
              first act is stamping data-cf-nav on <html>, which is what
              lets the stylesheet draw the button at all and keep the no-JS
              fallback (an ordinary stacked list, no dead control) free of a
              flash of open menu. Loaded at the foot of the body, every
              load below 780 px would paint the open list, then collapse it.
  CONSENT     a page with the banner has the whole first layer: accept and
              reject in the banner (the two choices DSGVO requires side by
              side), and — wherever the page offers action="open" — a
              settings dialog carrying save, aria-labelledby (the element
              openDialog gives focus to), and one checkbox per category,
              exactly. A missing box is a choice the reader is never
              offered; an extra one is a control that does nothing. `close`
              is NOT required, and the first draft of this rule learned it
              from the pages: the dialog deliberately ships no close cross
              — "no dismissal that counts as consent", its own chapter says
              — and Escape is the native <dialog>'s, not a button's. The
              word stays in the vocabulary because the script answers it;
              no page is obliged to use it.
  LOADED      a page with the banner loads cf-consent.js. The banner ships
              `hidden` and only the script shows it: markup without the
              script is a consent flow that never asks, and a footer
              "Cookie-Einstellungen" opener that answers no click.

stdlib only, no build step, no browser. html.parser, the same python3 that
serves the pages.

    python3 scripts/check-script-contract.py       # exit 1 on a finding
    python3 scripts/check-script-contract.py -v    # per-file counts
"""

import argparse
import html.parser
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TREE = ROOT / "design-system"
PATTERNS = TREE / "patterns"
JS = TREE / "assets" / "js"

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}


def vocabulary():
    """The contract's words, read from the scripts that answer them."""
    consent = (JS / "cf-consent.js").read_text(encoding="utf-8")
    nav = (JS / "cf-nav.js").read_text(encoding="utf-8")

    actions = set(re.findall(r"action === '([a-z]+)'", consent))
    m = re.search(r"CATEGORIES\s*=\s*\[([^\]]*)\]", consent)
    categories = set(re.findall(r"'([a-z]+)'", m.group(1))) if m else set()

    # The dispatch and the literal are the source of truth; an empty read
    # means the script was restructured and this check must be re-pointed,
    # which is a failure of the check, said as one.
    if not actions or not categories:
        sys.exit("check-script-contract: could not read the action dispatch "
                 "or CATEGORIES from cf-consent.js — re-point vocabulary().")
    for needle in (".cf-nav__toggle", "cf-nav__list"):
        if needle not in nav:
            sys.exit("check-script-contract: %r is no longer in cf-nav.js — "
                     "the nav contract moved; re-point this check." % needle)
    return actions, categories


class Page(html.parser.HTMLParser):
    """One pass, attributes only. Text — prose, <code>, comments — never
    enters a rule, which is what lets the vocabulary rules run on the
    documentation pages that quote the contract."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []            # (tag, is_banner, is_dialog)
        self.in_head = False
        self.ids = {}              # id -> class list
        self.toggles = []          # (line, aria-controls value or None)
        self.head_srcs = []
        self.body_srcs = []
        self.actions = []          # (line, value, container: banner/dialog/page)
        self.categories = []       # (line, value)
        self.gated = []            # (line, value)
        self.banner_line = None
        self.dialog = None         # dict with line, labelledby

    def container(self):
        for tag, b, d in reversed(self.stack):
            if b:
                return "banner"
            if d:
                return "dialog"
        return "page"

    def handle_starttag(self, tag, attrs, self_closing=False):
        a = dict(attrs)
        line = self.getpos()[0]
        classes = (a.get("class") or "").split()

        if tag == "head":
            self.in_head = True
        if tag == "script":
            src = a.get("src")
            if src:
                (self.head_srcs if self.in_head else self.body_srcs).append(src)
            if a.get("type") == "text/plain" and "data-cf-consent" in a:
                self.gated.append((line, a["data-cf-consent"]))

        if "id" in a:
            self.ids.setdefault(a["id"], classes)
        if "cf-nav__toggle" in classes:
            self.toggles.append((line, a.get("aria-controls")))
        if "data-cf-consent-banner" in a:
            self.banner_line = line
        if "data-cf-consent-dialog" in a:
            self.dialog = {"line": line,
                           "labelledby": a.get("aria-labelledby")}

        if "data-cf-consent-action" in a:
            self.actions.append((line, a["data-cf-consent-action"],
                                 self.container()))
        if "data-cf-consent-category" in a:
            self.categories.append((line, a["data-cf-consent-category"]))

        if tag not in VOID and not self_closing:
            self.stack.append((tag,
                               "data-cf-consent-banner" in a,
                               "data-cf-consent-dialog" in a))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs, self_closing=True)

    def handle_endtag(self, tag):
        if tag == "head":
            self.in_head = False
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break


def check(path, actions, categories, verbose):
    page = Page()
    page.feed(path.read_text(encoding="utf-8"))
    rel = path.relative_to(ROOT)
    findings = []

    def say(line, rule, text):
        findings.append("%s:%d  %s  %s" % (rel, line, rule, text))

    # --- vocabulary, everywhere -------------------------------------------
    for line, value, _ in page.actions:
        if value not in actions:
            say(line, "ACTION", "data-cf-consent-action=%r is not a word the "
                "dispatch answers %s" % (value, sorted(actions)))
    for line, value in page.categories:
        if value not in categories:
            say(line, "CATEGORY", "data-cf-consent-category=%r is not in the "
                "script's CATEGORIES %s" % (value, sorted(categories)))
    for line, value in page.gated:
        if value not in categories:
            say(line, "GATE", "gated script names %r, a category no decision "
                "can ever grant" % value)

    # --- wiring, where the wiring is live ---------------------------------
    srcs = page.head_srcs + page.body_srcs
    loads_nav = any(s.endswith("cf-nav.js") for s in srcs)
    loads_consent = any(s.endswith("cf-consent.js") for s in srcs)
    is_pattern = PATTERNS in path.parents

    if page.toggles and (is_pattern or loads_nav):
        for line, controls in page.toggles:
            if controls is None:
                say(line, "PANEL", ".cf-nav__toggle carries no aria-controls; "
                    "cf-nav.js has no panel to wire")
            elif controls in page.ids and "cf-nav__list" not in page.ids[controls]:
                say(line, "PANEL", "aria-controls=%r lands on an element that "
                    "is not .cf-nav__list — the toggle would announce a menu "
                    "the stylesheet never draws" % controls)
            # An id that is absent altogether is ARIA-REF's finding, once.
        if not loads_nav:
            say(page.toggles[0][0], "NAV-HEAD",
                "page has a live .cf-nav__toggle and never loads cf-nav.js")
        elif not any(s.endswith("cf-nav.js") for s in page.head_srcs):
            say(page.toggles[0][0], "NAV-HEAD",
                "cf-nav.js is loaded from the body; the no-flash fallback "
                "needs it in <head> — see the script's own header")

    if page.banner_line is not None and (is_pattern or loads_consent):
        got = {v for _, v, c in page.actions if c == "banner"}
        for need in ("accept", "reject"):
            if need not in got:
                say(page.banner_line, "CONSENT",
                    "banner offers no %r — the first layer must hold both "
                    "choices side by side" % need)
        offers_open = any(v == "open" for _, v, _ in page.actions)
        if offers_open and page.dialog is None:
            say(page.banner_line, "CONSENT",
                'the page offers action="open" and has no settings dialog '
                "to open")
        if page.dialog is not None:
            d = page.dialog
            got = {v for _, v, c in page.actions if c == "dialog"}
            if "save" not in got:
                say(d["line"], "CONSENT", "dialog offers no 'save' — the "
                    "checkboxes decide nothing without it")
            if not d["labelledby"]:
                say(d["line"], "CONSENT", "dialog carries no aria-labelledby; "
                    "openDialog() would leave focus on the first tabbable "
                    "descendant — a link that leaves the page")
            boxed = {v for _, v in page.categories}
            for missing in sorted(categories - boxed):
                say(d["line"], "CONSENT", "no checkbox for %r — a choice the "
                    "reader is never offered" % missing)
        if not loads_consent:
            say(page.banner_line, "LOADED",
                "page ships the banner and never loads cf-consent.js — a "
                "consent flow that never asks")

    if verbose:
        print("%-52s %d toggle(s), %d action(s), %d finding(s)"
              % (rel, len(page.toggles), len(page.actions), len(findings)))
    return findings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    actions, categories = vocabulary()
    findings = []
    for path in sorted(TREE.rglob("*.html")):
        findings += check(path, actions, categories, args.verbose)

    if findings:
        print("check-script-contract: %d finding(s)" % len(findings))
        for f in findings:
            print("  " + f)
        return 1
    print("check-script-contract: every name the pages hand cf-consent.js "
          "and cf-nav.js is one the scripts answer, and the wiring is "
          "complete on every live page.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
