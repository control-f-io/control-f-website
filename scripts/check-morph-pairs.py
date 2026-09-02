#!/usr/bin/env python3
"""A morph has two halves in two documents, and half a morph is worse than none.

assets/js/cf-morph.js lifts one object out of a page transition: the headline
of the cell a reader clicked in a register travels to the headline of the page
that cell opened. It is the only behaviour in this system that needs TWO
DOCUMENTS TO AGREE, and neither document can see the other — the outgoing page
names its cell in `pageswap`, the incoming page names its header in
`pagereveal`, and the browser pairs them by name, at a moment when the two
pieces of evidence are in two different renderers.

WHAT GOES WRONG, AND WHY IT IS INVISIBLE. Each half is correct on its own. A
register that hands over to a page which does not load the script names a
headline that nothing answers, and a name with no counterpart is not an error
to anything: the browser plays the default exit on it, the navigation
completes, the console stays clean, every other gate here passes, and what
ships is a headline sliding across the incoming page and fading out on top of
it. The reverse — an object page whose home register does not load the script
— is the same fault mirrored, and reads as the page's headline arriving before
the wipe that is supposed to reveal it. Both are one edit away at all times,
because the two halves live in two files that nothing else makes anyone open
together.

And the third fault is the register itself. cf-morph.js finds its cells by
class — `a.cf-blog-card`, `a.cf-vacancy__link` — and a class that gets renamed
in the markup leaves the entry matching nothing. That failure is TOTALLY
silent: no name is written, no transition changes, and the feature simply
stops existing on the pages it was built for.

THE VOCABULARY IS READ FROM THE SCRIPT, NOT COPIED INTO THIS FILE, which is
the same contract check-script-contract.py holds for the consent and nav
wiring. A shape added to SOURCES is checked here without editing this file; a
class renamed in the script is enforced under its new name on the next run.

WHAT IT CHECKS. Five rules, over design-system/patterns/ — the shipping tree,
generated pages included, which is why CI builds before it runs.

  REGISTER  every selector in the script's SOURCES, plus its TARGET and HOME
            selectors, is drawn by at least one shipping page. An entry that
            matches nothing is a rename that took the feature with it.
  SIDE      a page that loads cf-morph.js is one of the two things the script
            answers to: a REGISTER (no breadcrumb) carrying at least one
            registered cell, or an OBJECT (a breadcrumb of two links or more)
            carrying the page header the script names. A page loading it for
            neither reason is paying for a file that can never do anything.
  PAIR      for every registered cell on a register that loads the script, the
            page it opens loads the script too, and that page's breadcrumb
            ends at the register. This is the mutual reference the script
            relies on, asserted from the outside.
  HOME      for every object page that loads the script, the register its
            breadcrumb names loads the script too. The other direction of
            PAIR, and it stops there on purpose: whether that register also
            DRAWS the object is check-links.py's and check-registered.py's
            question, and the two pattern templates — blog-artikel.html,
            karriere-stelle.html — are objects no register draws by design.
  STYLE     the name the script writes is the name base.css styles, in both
            directions. A name styled nowhere is a morph with no animation; a
            rule for a name nothing writes is dead CSS that reads as a shipped
            behaviour.

Run from the repo root. Exit 1 on any finding. -v prints the whole register
and every pair it walked.
"""

import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATTERNS = os.path.join(ROOT, "design-system", "patterns")
SCRIPT = os.path.join(ROOT, "design-system", "assets", "js", "cf-morph.js")
BASE_CSS = os.path.join(ROOT, "design-system", "assets", "css", "base.css")
SCRIPT_FILE = "cf-morph.js"


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


# ---------------------------------------------------------------- the script

def strip_comments(src):
    """/* … */ and // … out of the JavaScript, so prose about a selector is
    never mistaken for the register that names it."""
    src = re.sub(r"/\*.*?\*/", " ", src, flags=re.S)
    return re.sub(r"(?m)^\s*//.*$", " ", src)


def parse_register(src):
    """SOURCES, TARGET, HOME and the name, out of cf-morph.js itself."""
    body = strip_comments(src)

    block = re.search(r"var\s+SOURCES\s*=\s*\[(.*?)\]\s*;", body, re.S)
    if not block:
        return None, "cf-morph.js: no SOURCES register found"
    shapes = []
    for entry in re.findall(r"\{(.*?)\}", block.group(1), re.S):
        shape = {}
        for field, single, double, nul in re.findall(
                r"(\w+)\s*:\s*(?:'([^']*)'|\"([^\"]*)\"|(null))", entry):
            shape[field] = None if nul else (single or double)
        missing = [k for k in ("link", "title") if not shape.get(k)]
        if missing:
            return None, "cf-morph.js: a SOURCES entry has no %s" % ", ".join(missing)
        shapes.append(shape)
    if not shapes:
        return None, "cf-morph.js: SOURCES is empty"

    def literal(name):
        m = re.search(r"var\s+%s\s*=\s*\{(.*?)\}\s*;" % name, body, re.S)
        if not m:
            return None
        out = {}
        for field, single, double in re.findall(r"(\w+)\s*:\s*(?:'([^']*)'|\"([^\"]*)\")",
                                                m.group(1)):
            out[field] = single or double
        return out

    def string(name):
        m = re.search(r"var\s+%s\s*=\s*(?:'([^']*)'|\"([^\"]*)\")\s*;" % name, body)
        return (m.group(1) or m.group(2)) if m else None

    target = literal("TARGET")
    home = string("HOME")
    title_name = string("NAME_TITLE")
    if not target or not target.get("title"):
        return None, "cf-morph.js: no TARGET with a title"
    if not home:
        return None, "cf-morph.js: no HOME selector"
    if not title_name:
        return None, "cf-morph.js: no NAME_TITLE"

    return {"sources": shapes, "target": target, "home": home,
            "name": title_name}, None


SELECTOR = re.compile(r"^([a-z0-9]*)\.([A-Za-z0-9_-]+)$")


def selector(sel):
    """The subset of CSS the register is allowed to be written in: `tag.class`
    or `.class`. Anything else is refused here rather than half-understood —
    a gate that guesses at a selector is a gate that passes a rename."""
    m = SELECTOR.match(sel or "")
    if not m:
        return None
    return (m.group(1) or None, m.group(2))


# ----------------------------------------------------------------- the pages

class Page(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.scripts = []
        self.classes = set()
        self.anchors = []          # (tagname, frozenset(classes), href)
        self.crumbs = []           # href, in document order

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = frozenset((a.get("class") or "").split())
        self.classes |= cls
        if tag == "script" and a.get("src"):
            self.scripts.append(a["src"])
        if tag == "a" and a.get("href"):
            self.anchors.append((tag, cls, a["href"]))


def load(path):
    page = Page()
    page.feed(read(path))
    return page


def resolve(page_path, href):
    """A pattern page's href, as a path under design-system/patterns/ — or None
    if it leaves the tree, which is every case this feature has no opinion on."""
    href = href.split("#")[0].split("?")[0]
    if not href or "//" in href or href.startswith("mailto:") or href.startswith("tel:"):
        return None
    target = os.path.normpath(os.path.join(os.path.dirname(page_path), href))
    if os.path.dirname(target) != PATTERNS:
        return None
    return target


def matches(cls_set, tag, sel):
    parsed = selector(sel)
    if not parsed:
        return False
    want_tag, want_class = parsed
    if want_tag and want_tag != tag:
        return False
    return want_class in cls_set


def main():
    verbose = "-v" in sys.argv or "--verbose" in sys.argv

    register, err = parse_register(read(SCRIPT))
    if err:
        print(err)
        return 1

    bad = [s for shape in register["sources"] for s in
           (shape["link"], shape.get("scope"), shape["title"])
           if s and not selector(s)]
    for s in (register["target"]["title"], register["home"]):
        if not selector(s):
            bad.append(s)
    if bad:
        for s in bad:
            print("  REGISTER  %s is not `tag.class` or `.class`; this gate reads "
                  "no other selector" % s)
        return 1

    files = sorted(f for f in os.listdir(PATTERNS) if f.endswith(".html"))
    pages = {}
    for name in files:
        path = os.path.join(PATTERNS, name)
        pages[path] = load(path)

    findings = []
    seen_classes = set()
    for page in pages.values():
        seen_classes |= page.classes

    # ---- REGISTER
    wanted = []
    for shape in register["sources"]:
        for field in ("link", "scope", "title"):
            if shape.get(field):
                wanted.append((shape["link"], field, shape[field]))
    wanted.append(("TARGET", "title", register["target"]["title"]))
    wanted.append(("HOME", "home", register["home"]))
    for owner, field, sel in wanted:
        cls = selector(sel)[1]
        if cls not in seen_classes:
            findings.append("REGISTER  %s's %s selector %s is drawn by no shipping page"
                            % (owner, field, sel))

    # ---- which pages load it, and what each one is
    def loads(page):
        return any(src.rsplit("/", 1)[-1] == SCRIPT_FILE for src in page.scripts)

    def crumb_links(path, page):
        out = []
        for tag, cls, href in page.anchors:
            if matches(cls, tag, register["home"]):
                out.append(resolve(path, href))
        return out

    def cells(path, page):
        """(destination path, shape) for every registered cell on this page."""
        out = []
        for shape in register["sources"]:
            for tag, cls, href in page.anchors:
                if not matches(cls, tag, shape["link"]):
                    continue
                dest = resolve(path, href)
                if dest:
                    out.append((dest, shape))
        return out

    registers, objects = {}, {}
    for path, page in sorted(pages.items()):
        if not loads(page):
            continue
        crumbs = crumb_links(path, page)
        found = cells(path, page)
        if len(crumbs) >= 2:
            objects[path] = crumbs[-1]
            if not matches(page.classes, None, register["target"]["title"]):
                findings.append("SIDE      %s loads %s and draws no %s to name"
                                % (os.path.basename(path), SCRIPT_FILE,
                                   register["target"]["title"]))
        elif found:
            registers[path] = found
        else:
            findings.append("SIDE      %s loads %s and is neither a register with a "
                            "cell nor an object with a breadcrumb"
                            % (os.path.basename(path), SCRIPT_FILE))

    # ---- PAIR
    walked = []
    for path, found in sorted(registers.items()):
        for dest, shape in found:
            here = os.path.basename(path)
            there = os.path.basename(dest)
            if dest not in pages:
                findings.append("PAIR      %s: the cell opening %s is not a page in this "
                                "tree" % (here, there))
                continue
            if not loads(pages[dest]):
                findings.append("PAIR      %s hands %s over and %s does not load %s — the "
                                "headline leaves and nothing answers"
                                % (here, there, there, SCRIPT_FILE))
                continue
            crumbs = crumb_links(dest, pages[dest])
            if not crumbs or crumbs[-1] != path:
                findings.append("PAIR      %s hands %s over and %s's breadcrumb ends at %s"
                                % (here, there, there,
                                   os.path.basename(crumbs[-1]) if crumbs and crumbs[-1]
                                   else "nothing in this tree"))
                continue
            walked.append((here, there))

    # ---- HOME
    for path, lives in sorted(objects.items()):
        here = os.path.basename(path)
        if lives is None or lives not in pages:
            findings.append("HOME      %s loads %s and its breadcrumb ends outside this "
                            "tree" % (here, SCRIPT_FILE))
            continue
        home_page = pages[lives]
        if not loads(home_page):
            findings.append("HOME      %s answers for a morph and its register %s does not "
                            "load %s" % (here, os.path.basename(lives), SCRIPT_FILE))

    # ---- STYLE
    css = read(BASE_CSS)
    styled = set(re.findall(r"::view-transition-(?:group|old|new)\((cf-morph[A-Za-z0-9_-]*)\)",
                            css))
    if register["name"] not in styled:
        findings.append("STYLE     the script writes view-transition-name %s and base.css "
                        "styles no ::view-transition-*(%s)"
                        % (register["name"], register["name"]))
    for stray in sorted(styled - {register["name"]}):
        findings.append("STYLE     base.css styles ::view-transition-*(%s) and no script "
                        "writes that name" % stray)

    if verbose:
        print("cf-morph.js register")
        for shape in register["sources"]:
            print("  cell    %-22s title %s" % (shape["link"], shape["title"]))
        print("  object  title %s" % register["target"]["title"])
        print("  home    %s" % register["home"])
        print("  name    %s" % register["name"])
        print("\npages loading %s" % SCRIPT_FILE)
        for path in sorted(registers):
            print("  register  %-28s %d cell(s)"
                  % (os.path.basename(path), len(registers[path])))
        for path in sorted(objects):
            print("  object    %-28s home %s"
                  % (os.path.basename(path),
                     os.path.basename(objects[path]) if objects[path] else "—"))
        print("\npairs walked — %d" % len(walked))
        for here, there in walked:
            print("  %s  →  %s" % (here, there))

    if findings:
        print("check-morph-pairs: %d finding(s)\n" % len(findings))
        for line in findings:
            print("  " + line)
        return 1

    print("check-morph-pairs: %d cell shape(s), %d register(s), %d object(s), "
          "%d pair(s) — both halves present"
          % (len(register["sources"]), len(registers), len(objects), len(walked)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
