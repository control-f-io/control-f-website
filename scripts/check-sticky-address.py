#!/usr/bin/env python3
"""An address the page links to may not stand inside a stuck box.

The companion to check-arrival.py, and the half of that rule it cannot see.

WHAT check-arrival.py HOLDS. Every addressable heading in patterns/ resolves a
scroll-margin-top out of the shipping stylesheets, so a fragment lands below
the sticky nav rather than behind it. It reads DECLARATIONS: the heading has
the clearance or it does not. That is the right register for the fault it was
written for — 38 of 58 addressable headings had no clearance rule at all — and
it is why it passes on the one below.

WHAT IT CANNOT SEE. scroll-margin-top is applied to the target's position in
the scroll container, and for an element inside a `position: sticky` ancestor
that position is the box's UNSTUCK one. The browser scrolls to the target's
flow offset minus the margin; the stage then sticks; and the target paints
wherever the stage has carried it. The declaration is present, correct, and
powerless, and no check that reads declarations can tell the difference.

WHAT IT COST, on patterns/landing-page.html. Act 3's header — "Was wir machen",
the line that introduces the four process cards — is argued into .sp-stage by a
comment in acts.css: the drawing's nineteen drops land on its rule, so it
belongs in the box they land in. .sp-stage is `position: sticky` from 64rem up.
The <h2> in it carried `id="prozess"`, which is what the act rail's "03 Was wir
machen" jump addresses and what a pasted URL addresses. Measured, the top of
the target after the scroll settles, at the four widths this page is held to:

                   375    768   1280   1440
    #vom-sensor…   108    108    108    108
    #prozess       108    108    854    854   <- inside .sp-stage
    #wer-wir-sind  108    108    108    108
    #wo-die-daten  108    108    108    108

108 px is --nav-height plus --space-6, the clearance .act-anchor declares and
the figure its three siblings land on at every width. Act 3 landed 746 px past
it at the two commonest desktop widths — three-quarters of the way down the
viewport, with the previous act's drawing still filling the screen above the
heading the reader asked for.

WHY NOBODY SAW IT. act-rail.js intercepts a click on the rail and scrolls to
its own computed stop, so with JavaScript on and a mouse in hand the rail goes
somewhere sensible and the href is never resolved. The fault is only on the
paths nobody drives: JavaScript off, a fragment pasted into the address bar, a
link from another page. Measured on both, before the fix, at 1280 and 1440:
854 px either way.

THE FIX was not a bigger scroll margin — there is no margin that reaches a
target the stage has moved. The ADDRESS moved to the element that is in the
flow, act 3's own <section>, and the heading kept its text and its job as that
section's accessible name. Two ids, because they are two jobs.

THE RULE THIS HOLDS, and it is deliberately narrower than "no id inside a
sticky box": an id an <a> on the page LINKS TO — `href="#id"` — may not have a
`position: sticky` or `position: fixed` ancestor. An <a> because that is what
a reader is taken to; the same attribute on <use> or a gradient <stop> names a
paint server inside an SVG and moves nobody. A heading id that is
only an aria-labelledby target is not a landing site and is not counted;
`prozess-titel` is exactly that and stays where the drawing needs it. What is
counted is every id the page itself promises to take a reader to.

MEDIA QUERIES ARE NOT CONSULTED, on purpose. .sp-stage is sticky only from
64rem, and that is precisely how this shipped: correct on a phone, wrong on
every desktop. A box that is EVER stuck can never be a reliable landing site,
so a `position: sticky` anywhere in the sheet counts.

WHAT THIS WILL NOT DO. The ancestor matcher reads simple type and class
selectors and descendant chains of them, plus :is()/:where() lists of the same
— every shape that carries a position declaration in this tree. A shape it
cannot read is a FINDING and not a pass, so the check cannot go quiet by being
outgrown. Pseudo-elements are skipped: ::before is not an element an id can be
inside of.

stdlib only, no build step, no dependency — the same contract as the checks
beside it.

    python3 scripts/check-sticky-address.py       # check, exit 1 on a finding
    python3 scripts/check-sticky-address.py -v    # print every address and its ancestry
"""

import argparse
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
SHIPPING = [
    DS / "assets" / "css" / "tokens.css",
    DS / "assets" / "css" / "base.css",
    DS / "assets" / "css" / "components.css",
    DS / "assets" / "css" / "acts.css",
]
# The pages that carry the acts, and therefore the sticky stages.
PAGE_DIRS = [DS / "patterns", DS / "prototypes"]

VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


class Tree(HTMLParser):
    """Enough of a DOM to answer 'what is this element inside of'."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        # id -> [(tag, frozenset(classes)), ...] outermost first, the id's own last
        self.addresses = {}
        self.links = set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = frozenset((a.get("class") or "").split())
        node = (tag, classes)
        if a.get("id"):
            self.addresses[a["id"]] = list(self.stack) + [node]
        if tag == "a":
            href = a.get("href") or ""
            if href.startswith("#") and len(href) > 1:
                self.links.add(href[1:])
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.addresses[a["id"]] = list(self.stack) + [(tag, frozenset())]
        if tag == "a":
            href = a.get("href") or ""
            if href.startswith("#") and len(href) > 1:
                self.links.add(href[1:])

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                return


def strip_comments(css):
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def position_preludes(css):
    """Every rule prelude that declares position: sticky or fixed.

    Nesting is followed by brace count so a rule inside @media or @supports is
    read with its own prelude, which is the one that names the element.
    """
    css = strip_comments(css)
    out = []
    prelude = ""
    stack = []
    for piece in re.split(r"([{}])", css):
        if piece == "{":
            stack.append(prelude.strip())
        elif piece == "}":
            if stack:
                stack.pop()
        else:
            prelude = piece.rsplit(";", 1)[-1].rsplit("}", 1)[-1]
            if stack and re.search(r"position\s*:\s*(sticky|fixed)\b", piece):
                out.append(stack[-1])
    return out


SIMPLE = re.compile(r"^(?P<tag>[a-zA-Z][\w-]*)?(?P<cls>(?:\.[-\w]+)*)$")


def expand_is(sel):
    """:is(a, b) / :where(a, b) -> [a, b], one level, which is all this tree has."""
    m = re.search(r":(?:is|where)\(([^()]*)\)", sel)
    if not m:
        return [sel]
    return [
        (sel[:m.start()] + part.strip() + sel[m.end():]).strip()
        for part in m.group(1).split(",")
    ]


def key_of(prelude):
    """The compound that must match an ANCESTOR: the selector's rightmost part.

    Returns (tag_or_None, frozenset(classes)) or None if the shape is unreadable.
    A pseudo-element target is not an element and returns 'skip'.
    """
    sel = prelude.strip()
    if "::" in sel:
        return "skip"
    sel = re.sub(r":(hover|focus|focus-visible|active|last-child|first-child|"
                 r"checked|not\([^()]*\)|nth-child\([^()]*\))", "", sel)
    last = re.split(r"[\s>+~]+", sel.strip())[-1]
    m = SIMPLE.match(last)
    if not m:
        return None
    tag = m.group("tag")
    cls = frozenset(c for c in m.group("cls").split(".") if c)
    if not tag and not cls:
        return None
    return (tag, cls)


def sticky_keys():
    keys, unreadable = set(), set()
    for path in SHIPPING:
        for prelude in position_preludes(path.read_text(encoding="utf-8")):
            for part in prelude.split(","):
                for sel in expand_is(part):
                    k = key_of(sel)
                    if k == "skip":
                        continue
                    if k is None:
                        unreadable.add((path.name, sel.strip()[:70]))
                    else:
                        keys.add(k)
    return keys, unreadable


def matches(node, key):
    tag, cls = key
    ntag, ncls = node
    if tag and ntag != tag:
        return False
    return cls <= ncls


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    keys, unreadable = sticky_keys()
    findings = []

    for name, sel in sorted(unreadable):
        findings.append(
            "%s: cannot read the selector `%s`, which declares position: "
            "sticky or fixed. Teach key_of() this shape — an unreadable "
            "selector is a hole in the rule, not a pass." % (name, sel))

    pages = sorted(p for d in PAGE_DIRS if d.is_dir() for p in d.glob("*.html"))
    checked = 0
    for page in pages:
        tree = Tree()
        tree.feed(page.read_text(encoding="utf-8"))
        for target in sorted(tree.links):
            chain = tree.addresses.get(target)
            if chain is None:
                continue          # a dangling fragment is check-links.py's
            checked += 1
            stuck = [
                node for node in chain[:-1]
                if any(matches(node, k) for k in keys)
            ]
            if args.verbose:
                where = " > ".join(
                    n[0] + ("." + ".".join(sorted(n[1])) if n[1] else "")
                    for n in chain[-4:])
                print("  %-28s %-22s %s"
                      % ("#" + target, page.name, where))
            if stuck:
                box = stuck[-1]
                findings.append(
                    "%s: #%s is linked to from this page and stands inside "
                    "<%s class=\"%s\">, which the stylesheets give position: "
                    "sticky or fixed. scroll-margin-top is measured against "
                    "that box's UNSTUCK position, so the fragment lands "
                    "wherever the stage has carried it. Move the address to "
                    "an element in the document flow."
                    % (page.name, target, box[0], " ".join(sorted(box[1]))))

    if findings:
        print("sticky-address: %d finding%s"
              % (len(findings), "" if len(findings) == 1 else "s"))
        for f in findings:
            print("  - " + f)
        return 1

    print("sticky-address OK — %d linked addresses across %d pages, none "
          "inside a sticky or fixed box; %d selectors declare one and all "
          "are readable." % (checked, len(pages), len(keys)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
