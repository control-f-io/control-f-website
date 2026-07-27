#!/usr/bin/env python3
"""The error block's contract holds on every pattern page that renders one.

The seventeenth check, and the first about a component's own stated rules
rather than a stylesheet's. components/error-state.html writes its contract in
prose, three clauses of it countable and none of them enforced:

  1. "its title is never an <h1> — an empty grid interrupts a section, it does
     not retitle the page."  The inline variant sits inside a page that already
     has a title; an <h1> in it forks the document outline, and the page
     renders pixel-identical either way, because the title's size comes from
     the class and not the tag.

  2. "Three to five rows."  The routes list is the way out of a dead end; two
     rows is a coin flip and six is a sitemap. A list that drifts outside the
     band still renders as a list.

  3. "The list does not repeat whatever the primary button already offers — a
     dead end needs exits, not the same exit twice."  On patterns/404.html the
     button is the home page and the home page is not in the list; nothing
     keeps it that way. The clause binds the PRIMARY action alone — the ghost
     beside it may legitimately share a target with a route (404's "Defekten
     Link melden" and its Kontakt route both go to kontakt.html, one as a
     report, one as an exit), so this check reads only the first action.

All three failures photograph as a working page, which is the same shape as
the sixteen checks beside this one: the difference between kept and broken is
a tag name, a count, and a pair of equal strings, and none of them shows in a
screenshot.

WHAT IT CHECKS. For every design-system/patterns/*.html, comments masked:
every .cf-error--inline block's .cf-error__title sits on h2–h6, never h1;
every .cf-error__routes-list carries three to five <li>; and within each
.cf-error block, no .cf-error__route href equals the href of the first link
in that block's .cf-error__actions. The scope is patterns/ alone: the
component page's own demos link to in-page anchors and demonstrate fragments
of the contract one at a time, which is what a demo is for.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-error-contract.py       # check, exit 1 on a finding
    python3 scripts/check-error-contract.py -v    # list every block audited
"""

import argparse
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
PATTERNS = ROOT / "design-system" / "patterns"

COMMENT = re.compile(r"<!--.*?-->", re.S)


class Node:
    __slots__ = ("tag", "classes", "href", "line", "parent", "children")

    def __init__(self, tag, classes, href, line, parent):
        self.tag = tag
        self.classes = classes
        self.href = href
        self.line = line
        self.parent = parent
        self.children = []

    def walk(self):
        yield self
        for child in self.children:
            yield from child.walk()


class Tree(HTMLParser):
    """A minimal element tree: tag, classes, href, line — nothing else."""

    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", frozenset(), None, 0, None)
        self.open = [self.root]

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        node = Node(tag, frozenset((a.get("class") or "").split()),
                    a.get("href"), self.getpos()[0], self.open[-1])
        self.open[-1].children.append(node)
        if tag not in self.VOID:
            self.open.append(node)

    def handle_endtag(self, tag):
        for i in range(len(self.open) - 1, 0, -1):
            if self.open[i].tag == tag:
                del self.open[i:]
                break


def audit(path, verbose):
    findings = []
    tree = Tree()
    tree.feed(COMMENT.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)),
                          path.read_text(encoding="utf-8")))
    rel = path.relative_to(ROOT)

    for node in tree.root.walk():
        if "cf-error--inline" in node.classes:
            for inner in node.walk():
                if "cf-error__title" in inner.classes and inner.tag == "h1":
                    findings.append(
                        "%s:%d\n    INLINE-H1  .cf-error--inline titles itself "
                        "with an <h1> — the inline block interrupts a section, "
                        "it does not retitle the page" % (rel, inner.line))

        if "cf-error__routes-list" in node.classes:
            rows = sum(1 for c in node.children if c.tag == "li")
            if not 3 <= rows <= 5:
                findings.append(
                    "%s:%d\n    ROWS  the routes list carries %d row%s — the "
                    "way out of a dead end is three to five named routes"
                    % (rel, node.line, rows, "" if rows == 1 else "s"))
            if verbose:
                print("  %-40s routes-list at line %-4d %d rows"
                      % (rel, node.line, rows))

        if "cf-error" in node.classes:
            primary = None
            for inner in node.walk():
                if "cf-error__actions" in inner.classes:
                    primary = next((c.href for c in inner.walk()
                                    if c.tag == "a" and c.href), None)
                    break
            if primary:
                for inner in node.walk():
                    if "cf-error__route" in inner.classes and \
                            inner.href == primary:
                        findings.append(
                            "%s:%d\n    REPEAT  the route duplicates the "
                            "primary action's target %r — a dead end needs "
                            "exits, not the same exit twice"
                            % (rel, inner.line, primary))
            if verbose:
                print("  %-40s cf-error at line %-4d primary action: %s"
                      % (rel, node.line, primary or "—"))

    return findings


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every error block and routes list audited")
    args = ap.parse_args()

    findings = []
    blocks = 0
    for path in sorted(PATTERNS.glob("*.html")):
        text = COMMENT.sub("", path.read_text(encoding="utf-8"))
        blocks += text.count("cf-error--inline") + text.count("cf-error--page")
        findings.extend(audit(path, args.verbose))

    if findings:
        print("\n".join(findings), file=sys.stderr)
        print("\n%d finding%s against the error block's own contract "
              "(components/error-state.html)."
              % (len(findings), "" if len(findings) == 1 else "s"),
              file=sys.stderr)
        return 1

    print("error contract: %d error block%s across the pattern pages, every "
          "title below <h1>, every routes list three to five rows, no route "
          "repeating its primary action."
          % (blocks, "" if blocks == 1 else "s"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
