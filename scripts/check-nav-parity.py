#!/usr/bin/env python3
"""Every pattern page's navigation bar is the same bar, drift-for-drift.

The companion to check-footer-parity.py, and the other half of its argument.
There is no build step and no include: every pattern page carries a
hand-typed copy of the one component that reaches every other page — the
cf-nav bar, its logo, its toggle and its seven links. The footer earned its
parity gate after four of its copies had quietly stopped being the same block
(#293), and the fix's own docstring names the exposure: a block hand-typed once
per page, "edited hourly by twelve routines, is the exact surface this directory
keeps finding forks on". The nav is that surface exactly — the same copies, the
same hourly edits — and it is a more expensive place to fork than the footer,
because below 780 px the bar's seven links are the ONLY way off any page: a copy
that loses a link does not render wrong, it just strands a phone reader one
route short, on one page, invisibly.

WHAT FOUND THIS. A full sweep of every copy, the way the footer was swept. Raw,
they differ three ways; after the two lawful axes below are normalised away they
are CHARACTER-IDENTICAL, every one of them. Clean without a gate is a
coincidence, not a fact — the footer's copies were presumably identical once
too, and what #293 found four of them doing later is what this file exists to
make impossible here. The same sweep drove every
copy in a browser: the toggle opens, Escape closes and restores focus, and the
panel folds identically on every page today — behaviour parity that holds
precisely as long as the markup the script reads stays one block.

THE LAWFUL AXES. Three, fewer than the footer needs — the bar is the same
everywhere by design, which is why anything else is a finding:

  ARIA-CURRENT   moves per page, naturally. Whether each copy marks the
                 RIGHT link the RIGHT way is check-a11y.py's CURRENT rule
                 and is not re-judged here; this file only refuses to call
                 the moving marker a fork.

  LANG-HREF      the language switch points at the SAME page in the other
                 edition — /kontakt offers /en/kontakt, not /en/. That
                 target therefore moves per page for the same reason
                 aria-current does, and for the same reason it is not a
                 fork. Only the href moves: the label, the two language
                 declarations and the aria-label are the bar's and are
                 compared like everything else, so a copy that offers the
                 wrong language, or offers it unlabelled, still fails.

  COMMENTS       datenschutz.html and impressum.html each argue in place
                 why their bar carries no aria-current at all — the page is
                 beside the seven routes, not in them. An argument is not
                 markup and is stripped before comparing, on every page.

THE RULES. Two, on every design-system/patterns/*.html:

  ONE-NAV   the page carries exactly one cf-nav bar. Zero is a page with no
            way anywhere below 780 px; two is two bars fighting for one
            aria-label and one id.

  PARITY    after stripping comments and aria-current and collapsing
            whitespace, every copy is character-identical to the consensus
            of them all. A dissenting copy is named with the first point
            of divergence, majority against dissenter, so whatever the next
            fork is — a link lost, a label rephrased, an attribute dropped —
            it fails here without this file having to predict it.

The consensus and not a canonical file, deliberately. check-footer-parity.py
holds its copies to components/footer.html because that demo mirrors the
shipping footer link-for-link. The nav component's demo does not and should
not: components/navigation.html teaches the component with `#` hrefs and its
own demo ids, chrome abstracted away from any page's reality. Holding the
shipping copies to a teaching abstraction would mean editing the demo every
time a page moved — a coupling the demo's whole shape argues against — so the
copies hold each other. If they ever split with no majority, every variant is
reported and nothing is guessed.

AND THE COUNT IS NOT WRITTEN DOWN HERE ANY MORE. This docstring said
"fifteen" fourteen times, in a tree that had grown to thirty-eight pattern
pages — the register-goes-stale failure this directory is full of gates for,
in the file whose whole subject is copies drifting apart. The number is
reported at the foot of a run, where it is counted.

AND THAT EXCLUSION WAS BLANKET WHERE IT ONLY EVER HAD AN ARGUMENT FOR TWO
AXES. The demo's hrefs and ids are the demo's. HOW MANY ROUTES THERE ARE is
not: it is a fact about the site, the same fact every shipping bar agrees on,
and it had drifted. components/navigation.html carried a five-route bar, a
five-route copy-paste block and a five-entry "site structure" table while every
shipping page carried seven — Expertise and Suche went into every shipping bar
and into neither of the two places that document the bar. Nothing read it,
because this file had excused the whole document rather than the two axes it
had reasons for. Half that page's arguments are arguments about a seven-route
row — the plate is `max-content` wide, the row wraps rather than taking the
document sideways at 200 % text, a DE|EN pair is 72 px the bar does not have at
375 px — and none of them can be seen in a five-route demo.

So there is a third rule, and it compares LABELS ONLY:

  DEMO-ROUTES  components/navigation.html's demo bar, the copy-paste block
               under it, and the "Site structure" table each carry the
               consensus route labels, in the consensus order. Nothing about
               an href, an id or an aria-current is read there — those are the
               demo's own and stay its own. A route added to the site fails
               here until the component's own page says so.

  DEMO-LABEL   that demo bar carries an aria-label. The page's sidebar is a
               second <nav> (assets/js/docs.js writes it, named "Design
               System"), so an unnamed bar leaves two navigation landmarks a
               reader jumping by landmark cannot tell apart — on the page that
               teaches the rule. It was unnamed.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-nav-parity.py       # check, exit 1 on a finding
    python3 scripts/check-nav-parity.py -v    # list every bar audited
"""

import argparse
import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PATTERNS = ROOT / "design-system" / "patterns"
COMPONENT = ROOT / "design-system" / "components" / "navigation.html"

COMMENT = re.compile(r"<!--.*?-->", re.S)
NAV = re.compile(r"<nav\s+class=\"cf-nav\"[^>]*>.*?</nav>", re.S)


def flatten(nav_html):
    """One line: whitespace runs become one space, whitespace between tags
    disappears, so indentation is never a difference."""
    text = re.sub(r"\s+", " ", nav_html).strip()
    text = re.sub(r"> <", "><", text)
    return text


LANG_HREF = re.compile(r"(<a class=\"cf-nav__lang\" href=\")[^\"]*\"")


def normalise(flat):
    """Remove the two lawful markup axes: the moving aria-current marker, and
    the language switch's target, which moves with the page it stands on."""
    flat = re.sub(r"\s+aria-current=\"[^\"]*\"", "", flat)
    return LANG_HREF.sub(r"\1…\"", flat)


LINK = re.compile(r"<a class=\"cf-nav__link\"[^>]*>(.*?)</a>", re.S)
TAG = re.compile(r"<[^>]+>")


def routes(bar_html):
    """The route labels a bar carries, in order. Labels only — an href, an id
    and an aria-current are never read here."""
    return [html.unescape(TAG.sub("", label)).strip()
            for label in LINK.findall(bar_html)]


def demo_code_block(text):
    """The copy-paste <pre> that shows the bar, as ordinary markup.

    The block is syntax-highlighted with <span> elements around escaped
    markup, so the real tags come off first and the escaped ones are then
    unescaped — after which it reads exactly like the demo above it."""
    for block in re.findall(r"<pre class=\"docs-code\">(.*?)</pre>", text, re.S):
        plain = html.unescape(re.sub(r"</?span[^>]*>", "", block))
        if "cf-nav__link" in plain:
            return plain
    return None


STRUCTURE = re.compile(
    r"<section class=\"docs-section\" id=\"structure\">(.*?)</section>", re.S)
ROW_HEAD = re.compile(r"<tr><td>(.*?)</td>", re.S)


def structure_rows(text):
    """The Label column of the "Site structure" table — this page's one claim
    about the site rather than about the component."""
    section = STRUCTURE.search(text)
    if not section:
        return None
    body = re.search(r"<tbody>(.*?)</tbody>", section.group(1), re.S)
    if not body:
        return None
    return [html.unescape(TAG.sub("", cell)).strip()
            for cell in ROW_HEAD.findall(body.group(1))]


def listing(names):
    return ", ".join(names) if names else "(nothing)"


def component_page(consensus, verbose):
    """DEMO-ROUTES and DEMO-LABEL, against the bar the shipping pages agree on."""
    rel = COMPONENT.relative_to(ROOT)
    if not COMPONENT.exists():
        return ["%s\n    DEMO-ROUTES  the component's own page is gone, and it "
                "is what this rule reads. Restore it, or retire the rule."
                % rel]

    raw = COMPONENT.read_text(encoding="utf-8")
    text = COMMENT.sub("", raw)
    findings = []

    found = NAV.findall(text)
    if len(found) != 1:
        return ["%s\n    DEMO-ROUTES  the page carries %d cf-nav bars; the "
                "rule reads exactly one demo" % (rel, len(found))]
    demo = found[0]

    subjects = [("the demo bar", routes(demo)),
                ("the copy-paste block", None),
                ("the Site structure table", structure_rows(text))]
    block = demo_code_block(text)
    subjects[1] = ("the copy-paste block",
                   routes(block) if block is not None else None)

    for what, actual in subjects:
        if actual is None:
            findings.append(
                "%s\n    DEMO-ROUTES  %s is not there to read. It is one of the "
                "three places this page states the site's routes." % (rel, what))
            continue
        if actual != consensus:
            findings.append(
                "%s\n    DEMO-ROUTES  %s lists %d route(s) and the shipping "
                "bars carry %d.\n      shipping  %s\n      this page %s\n"
                "    Labels and order only — the hrefs and the ids on this page are\n"
                "    its own and are not read. A route added to the site has to be\n"
                "    added here too, or the component's page documents a bar the\n"
                "    site stopped shipping."
                % (rel, what, len(actual), len(consensus),
                   listing(consensus), listing(actual)))

    if not re.search(r"aria-label=\"[^\"]+\"", re.match(r"<nav[^>]*>", demo).group(0)):
        findings.append(
            "%s\n    DEMO-LABEL  the demo bar is a <nav> with no aria-label, and\n"
            "    the documentation sidebar on this page is a second one. Two\n"
            "    navigation landmarks with one name between them are two a reader\n"
            "    jumping by landmark cannot tell apart — on the page that teaches\n"
            "    the rule." % rel)

    if verbose:
        print("  %-24s %d demo route(s): %s"
              % (COMPONENT.name, len(routes(demo)), listing(routes(demo))))
    return findings


def divergence(a, b):
    """Where two normalised bars first part, with enough context to read."""
    n = min(len(a), len(b))
    i = 0
    while i < n and a[i] == b[i]:
        i += 1
    lo = max(0, i - 60)
    return ("      consensus  …%s…\n      this copy  …%s…"
            % (a[lo:i + 80], b[lo:i + 80]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    findings = []
    bars = {}  # name -> normalised bar

    pages = sorted(PATTERNS.glob("*.html"))
    for path in pages:
        rel = path.relative_to(ROOT)
        text = COMMENT.sub("", path.read_text(encoding="utf-8"))
        found = NAV.findall(text)
        if len(found) != 1:
            findings.append(
                "%s\n    ONE-NAV  the page carries %d cf-nav bars; every "
                "pattern page carries exactly one"
                % (rel, len(found)))
            continue
        bars[path.name] = normalise(flatten(found[0]))

    groups = {}
    for name, bar in bars.items():
        groups.setdefault(bar, []).append(name)

    ranked = sorted(groups.items(), key=lambda kv: -len(kv[1]))
    split = len(ranked) > 1 and len(ranked[1][1]) == len(ranked[0][1])

    # The component's own page is held to the routes the shipping bars agree
    # on, so
    # it is only asked once there is something to agree on. Labels survive
    # normalise() untouched — it removes aria-current and the language switch's
    # target and nothing else — so the consensus is read straight off it.
    if ranked and not split:
        findings.extend(component_page(routes(ranked[0][0]), args.verbose))

    if len(groups) > 1:
        canon, majority = ranked[0]
        if split:
            # No majority to trust: report the split whole, guess nothing.
            findings.append(
                "design-system/patterns\n    PARITY  the %d bars split "
                "into %d equal camps (%s); no consensus to hold anyone to"
                % (len(bars), len(ranked), "; ".join(
                    ", ".join(sorted(names)) for _, names in ranked)))
        else:
            for bar, names in ranked[1:]:
                for name in sorted(names):
                    findings.append(
                        "design-system/patterns/%s\n    PARITY  this bar is "
                        "not the bar the other %d pages carry — first "
                        "divergence:\n%s"
                        % (name, len(majority), divergence(canon, bar)))

    if args.verbose:
        for name in sorted(bars):
            print("  %-24s %5d chars normalised" % (name, len(bars[name])))
        print("  %d bars, %d distinct after lawful axes" %
              (len(bars), len(groups)))

    if findings:
        print("check-nav-parity: %d finding(s)\n" % len(findings))
        for f in findings:
            print(f)
        return 1
    print("check-nav-parity: %d bars, one block. OK" % len(bars))
    return 0


if __name__ == "__main__":
    sys.exit(main())
