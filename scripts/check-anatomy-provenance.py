#!/usr/bin/env python3
"""A class named in an anatomy table has to be a class something declares.

Every chapter under design-system/components/ and design-system/foundations/
publishes a table whose left column is the component taken apart:
`.cf-annot-set`, `.cf-process__figure`, `.cf-blog-card--media`. Thirty-four
chapters carry one, 351 such mentions between them. It is the densest register
of class names in the repository and it is the one register nothing reads.

check-class-provenance.py holds the other direction and holds it completely:
every class that appears in a `class=` ATTRIBUTE anywhere in the tree is
declared by a stylesheet or by the page's own <style>. That is the direction in
which a stray costs a reader something — markup naming a rule that does not
exist renders unstyled. This direction costs a reader something else, later: a
part renamed in components.css moves its rule, moves the markup that wears it,
and leaves the row that DESCRIBES it naming a class that no longer exists. The
page still renders. The table still looks like a table. The name in it is now
the one thing on the page that cannot be pasted into anything.

WHY IT IS WORTH A GATE RATHER THAN A PROOF-READ. An anatomy row is prose to
every one of the other gates here — a class name inside <code> is text, and the
one script whose subject is class names reads attributes. So the failure has
the shape this directory keeps finding: nothing renders wrong, no check has an
opinion, and the only reader who ever discovers it is the one who trusted the
table enough to copy out of it. A rename is also exactly the edit most likely
to be made by a lane that has never opened the chapter: the rule and the markup
are in two files it is touching, the description is in a third it is not.

THE RULE. In any chapter under components/ or foundations/, a table cell whose
entire content is one or more <code> spans, each holding a CSS selector, names
classes that are declared by one of the shipping stylesheets or by that page's
own <style> block. That is the whole of it.

DELIBERATELY NARROW, on the same argument check-cited-gates.py makes for
reading only script paths. Three restrictions, each because the alternative
would be a check that is nearly right about several things:

  ONLY WHOLE-CODE CELLS.  A cell of prose with a class mentioned inside it is
      a sentence, and a sentence may legitimately name a class that was
      REMOVED — "this used to be .cf-process__plate" is a record, and this
      repository keeps records. A cell that is nothing but code is a
      specification of what to type.
  ONLY CLASSES.  Element names, custom properties, attributes and pseudo
      elements all appear in these cells too. Custom properties have
      check-registered.py; the rest have no single place to be true against.
  WILDCARDS PASS.  `.col-*` in foundations/layout.html is a family, not a
      class, and a check that made the chapter spell out twelve rows to say
      one thing would be making the documentation worse.

WHAT IT DOES NOT CHECK, and the seam is worth naming: that the class named in
a row is the class that draws the part the row describes. Nothing can read that
— it is a claim about meaning. What it can read is that the name resolves, and
a name that resolves is the precondition for the sentence being checkable by a
person at all.
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DESIGN = ROOT / "design-system"
CSS_DIR = DESIGN / "assets" / "css"

# The chapters. Patterns are not read: they are pages, not documentation, and
# their class names are held by check-class-provenance.py as attributes.
CHAPTERS = ["components", "foundations"]

COMMENT = re.compile(r"/\*.*?\*/", re.S)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
STYLE = re.compile(r"<style[^>]*>(.*?)</style>", re.S)
CLASS_IN_CSS = re.compile(r"\.([A-Za-z_][A-Za-z0-9_-]*)")

# A cell that is code and nothing else. The separators allowed between two
# <code> spans in one cell are the ones the chapters actually use to list
# alternatives: whitespace, a comma, a slash, "and", "or".
CODE_CELL = re.compile(
    r"<t[dh]>\s*"
    r"(<code>[^<]*</code>(?:\s*(?:,|/|and|or)?\s*<code>[^<]*</code>)*)"
    r"\s*</t[dh]>",
    re.S,
)
CODE = re.compile(r"<code>([^<]*)</code>")

# A selector we are willing to adjudicate: it starts with a dot, and it is made
# only of class names, combinators and pseudo-classes/elements we can strip.
# Anything else — an attribute selector, an element name, a custom property —
# is left alone.
SELECTOR_OK = re.compile(r"^\.[A-Za-z_][A-Za-z0-9_-]*[A-Za-z0-9_.:>+~\s()#\[\]=\"'-]*$")


def declared_globally():
    """Every class name any shipping or documentation stylesheet declares."""
    names = set()
    for css in sorted(CSS_DIR.glob("*.css")):
        text = COMMENT.sub("", css.read_text(encoding="utf-8"))
        names |= set(CLASS_IN_CSS.findall(text))
    return names


def declared_locally(html):
    """Every class name a page declares in its own <style> blocks."""
    names = set()
    for block in STYLE.findall(html):
        names |= set(CLASS_IN_CSS.findall(COMMENT.sub("", block)))
    return names


def selectors_in(html):
    """Yield (selector, class names) for every whole-code table cell."""
    for cell in CODE_CELL.finditer(html):
        for raw in CODE.findall(cell.group(1)):
            selector = raw.strip()
            if not selector.startswith("."):
                continue
            if "*" in selector:          # a family, not a class
                continue
            if not SELECTOR_OK.match(selector):
                continue
            names = CLASS_IN_CSS.findall(selector)
            if names:
                yield selector, names


def audit():
    globally = declared_globally()
    findings = []
    seen = []

    for chapter in CHAPTERS:
        for page in sorted((DESIGN / chapter).glob("*.html")):
            html = page.read_text(encoding="utf-8")
            locally = declared_locally(html)
            body = HTML_COMMENT.sub("", html)
            for selector, names in selectors_in(body):
                where = page.relative_to(ROOT).as_posix()
                for name in names:
                    if name in globally:
                        seen.append((where, selector, name, "stylesheet"))
                    elif name in locally:
                        seen.append((where, selector, name, "page-local"))
                    else:
                        findings.append((where, selector, name))
    return findings, seen


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every class mention read, not only the strays")
    args = ap.parse_args()

    findings, seen = audit()

    if args.verbose:
        for where, selector, name, source in seen:
            print("  %-44s %-34s %s" % (where[-44:], selector[:34], source))
        print()

    if findings:
        for where, selector, name in findings:
            print("%s\n    %s names .%s, and nothing declares it. An anatomy row "
                  "is a specification of what to type."
                  % (where, selector, name), file=sys.stderr)
        print("\n%d class name%s in a documentation table that no stylesheet "
              "declares. The page renders; the name does not."
              % (len(findings), "" if len(findings) == 1 else "s"), file=sys.stderr)
        return 1

    pages = len({where for where, _, _, _ in seen})
    local = sum(1 for _, _, _, source in seen if source == "page-local")
    print("anatomy provenance: %d class mention%s across %d chapter%s resolve — "
          "%d to a shipping stylesheet, %d to the page's own <style>."
          % (len(seen), "" if len(seen) == 1 else "s",
             pages, "" if pages == 1 else "s",
             len(seen) - local, local))
    return 0


if __name__ == "__main__":
    sys.exit(main())
