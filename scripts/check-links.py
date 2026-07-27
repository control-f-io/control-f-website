#!/usr/bin/env python3
"""Every reference in design-system/ resolves against the filesystem.

The tenth check, and the first one about the system as a *site* rather than
about a drawing in it.

The site has no build step and no router. `.github/workflows/deploy.yml`
uploads the repository root and GitHub Pages serves it, and because this is a
project page with no CNAME, the document root is not the domain root — it is
`/control-f-website/`. A href of `/expertise` therefore does not mean "the
expertise page". It means `https://control-f-io.github.io/expertise`: one
level above anything this repository publishes, in a namespace it does not
own. It cannot be made to work by adding a page, because there is no page to
add it at.

That is not a hypothetical. Every pattern page carried a primary nav, a
footer and a consent banner written in production routes — the URLs the site
will have the day it moves to control-f.de — and on the host that actually
serves them, all of them were dead. The section that exists to prove the
system can be walked was the one section of the tree you could not walk.

So the rule this script keeps is: inside design-system/, a reference is
relative and it lands on a file. Five failing classes, no severities:

  ABSOLUTE     a leading `/`. Always wrong here, whatever it points at.
  MISSING      a relative path that resolves to nothing on disk.
  FRAGMENT     a `#name` with no element carrying that id on the target page.
  OPENER       target="_blank" without rel="noopener".
  PLACEHOLDER  a bare `#` outside a demo. Inside a demo it is a specimen's
               stand-in route, same as the fragment-only exemption below.
               Outside one it is a decision nobody made: the link renders,
               focuses, and goes nowhere. patterns/blog-artikel.html shipped
               three of these under "Weiterlesen" while news.html pointed
               twenty cards of the same component at the article specimen.
               A route is either written or removed, never parked.
  CURRENT      aria-current that lies. Two ways: `aria-current="page"` on a
               link that leaves the page, and a list-item link to the page
               it stands on with no aria-current at all. The second is the
               class behind "of six pages standing in their own footer only
               one said so" — hand-fixed once, and nothing kept it fixed.
               Only links inside <li> owe the marker: a logo pointing home
               and a prose link to the page it happens to sit on are not
               items in a set, and ARIA asks it only of sets. Ancestor
               markers (`aria-current="true"` on a section parent, the way
               blog-artikel.html marks News) are correct and stay quiet.

What it deliberately does not read:

  - the outgoing generation at the repository root. Those pages are served
    from the document root and their absolute links are correct there. This
    check is scoped to design-system/ on purpose.
  - anything inside <pre>, <code>, <textarea> or an HTML comment. A docs page
    quoting production markup — components/search.html shows a result row
    written the way it will be written on control-f.de — is documentation,
    not a reference. Masking those is why this check can be strict about
    everything left.
  - text fragments (`#:~:text=`). Those address prose, not an id, and the
    search pattern is built on them.
  - off-site schemes: http, https, mailto, tel, data, javascript.
  - a *fragment-only* href inside a .docs-demo block. A component gallery has
    to give its breadcrumb and its pagination somewhere to point, and the
    gallery has no page 7 of 11 to point at; `#seite-7` is the same placeholder
    as the bare `#` this already tolerates. The exemption is deliberately
    narrow — it is fragment-only, and only inside a demo. ABSOLUTE and MISSING
    still apply everywhere, demos included, because those two differ in kind: a
    dead fragment is inert and leaves the reader on the page, while `/kontakt`
    in a demo takes them off the project page to a 404 on another host. That is
    the distinction, and it is why components/footer.html's demo still fails.

One id source is not in the markup at all. Two scripts inject ids at load:
cf-icons.js is the single place an icon is drawn and injects the whole sprite,
and docs.js injects the one `cf-arrow` symbol so documentation pages get the
arrow without the sprite. A page that includes either can point <use> at those
symbols without the ids appearing anywhere in its own source.

So the script reads the ids back out of every file in assets/js/ and credits
them to the pages that load that file — and only to those pages. That per-page
attribution is the whole value of doing it this way rather than allow-listing
`cf-*`: an arrow drawn on a page that includes neither script is a blank box,
and an allow-list would call it fine.


Exit code 0 when every reference resolves, 1 otherwise.
"""

import os
import re
import sys
from html import unescape
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TREE = os.path.join(ROOT, "design-system")

# Attributes that name a resource. `action` is here because a <form> posting
# to a dead route is the same failure with a slower reveal, and 404.html had
# one. `data-src` is here because the lazy-image pattern uses it as an href in
# all but name.
REF_ATTRS = ("href", "src", "action", "poster", "data-src")

# Regions whose contents are prose *about* markup, not markup. Masked before
# any attribute is read. <script> keeps its own src — only the body is masked,
# which is what the (?<=>) does not do, so the tag itself is matched first.
MASKED = ("pre", "code", "textarea", "script", "style")

OFFSITE = re.compile(r"^(?:https?:|mailto:|tel:|data:|javascript:|#\s*$)", re.I)


def mask(text, tag):
    """Blank the body of every <tag>…</tag>, keeping length and line count."""
    def blank(m):
        return m.group(1) + re.sub(r"[^\n]", " ", m.group(2)) + m.group(3)
    return re.sub(
        r"(<%s\b[^>]*>)(.*?)(</%s\s*>)" % (tag, tag),
        blank, text, flags=re.S | re.I,
    )


def readable(path):
    """The file's source with everything unquotable blanked out."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    # Comments first: a commented-out <pre> should not eat live markup after it.
    text = re.sub(r"<!--.*?-->", lambda m: re.sub(r"[^\n]", " ", m.group(0)),
                  text, flags=re.S)
    for tag in MASKED:
        text = mask(text, tag)
    return text


def line_of(text, index):
    return text.count("\n", 0, index) + 1


class SpanFinder(HTMLParser):
    """Line spans covered by a .docs-demo element, and by <li> elements.

    Depth-counted rather than regex-matched, because demos nest divs freely and
    a non-greedy </div> would close the block at the first inner one. Void and
    self-closing tags never open a span, so they cannot unbalance the count.
    An <li> left unclosed still gets its span when the parent list closes,
    because the pop walks everything above the matching tag.
    """

    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.demo_spans = []
        self.li_spans = []
        self.stack = []      # (tag, is_demo, start_line) per open element

    def handle_starttag(self, tag, attrs):
        if tag in self.VOID:
            return
        classes = dict(attrs).get("class") or ""
        is_demo = "docs-demo" in classes.split()
        self.stack.append((tag, is_demo, self.getpos()[0]))

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                end = self.getpos()[0]
                for t, is_demo, start in self.stack[i:]:
                    if is_demo:
                        self.demo_spans.append((start, end))
                    if t == "li":
                        self.li_spans.append((start, end))
                del self.stack[i:]
                return


def spans_in(path, text, _cache={}):
    """(demo lines, li lines) for the page at `path`.

    Keyed by path, never by id(text): id() names a memory address, CPython
    reuses addresses the moment a string is freed, and this walk frees each
    page's text before reading the next. Keyed by id, twenty-three of the
    fifty-six pages inherited a previous page's spans — patterns/404.html
    was credited fifty-two demo lines it does not have, and pagination.html
    kept forty-five of its real hundred-and-thirty-eight. An exemption
    ledger that misattributes is worse than none: it exempts lines nobody
    wrote a demo on."""
    if path not in _cache:
        finder = SpanFinder()
        try:
            finder.feed(text)
        except Exception:
            finder.demo_spans = []
            finder.li_spans = []
        demo, li = set(), set()
        for start, end in finder.demo_spans:
            demo.update(range(start, end + 1))
        for start, end in finder.li_spans:
            li.update(range(start, end + 1))
        _cache[path] = (demo, li)
    return _cache[path]


def script_ids(name, _cache={}):
    """The ids a script injects, read back out of the script itself.

    Both spellings, because cf-icons.js keeps them in an object array
    (id: 'cf-cube') and docs.js writes them into a markup string
    (id="cf-arrow")."""
    if name not in _cache:
        path = os.path.join(TREE, "assets", "js", name)
        try:
            with open(path, encoding="utf-8") as fh:
                src = fh.read()
        except OSError:
            _cache[name] = set()
        else:
            _cache[name] = (set(re.findall(r"\bid:\s*'([^']+)'", src))
                            | set(re.findall(r'\bid=\\?"([^"\\]+)\\?"', src)))
    return _cache[name]


def ids_in(path, _cache={}):
    """Every id a page has once loaded — its own, plus whatever the scripts it
    includes inject. Ids inside <script>/<pre> count: that is where the inlined
    <symbol id> sits on pages that paste the sprite instead of loading it."""
    if path not in _cache:
        try:
            with open(path, encoding="utf-8") as fh:
                src = fh.read()
        except OSError:
            _cache[path] = None
        else:
            found = set(re.findall(r'\bid\s*=\s*"([^"]+)"', src))
            for script in re.findall(r'src\s*=\s*"[^"]*/([^"/]+\.js)"', src):
                found |= script_ids(script)
            _cache[path] = found
    return _cache[path]


def references(path, text):
    """(attr, value, line) for every resource reference on the page.

    srcset is split into its candidates; each is checked like a src.
    """
    attrs = "|".join(REF_ATTRS)
    # (?<![-\w]) and not \b: `data-cf-consent-action="reject"` names a consent
    # category, not a form target, and \b happily matches after the hyphen.
    for m in re.finditer(r'(?<![-\w])(%s)\s*=\s*"([^"]*)"' % attrs, text):
        yield m.group(1), unescape(m.group(2).strip()), line_of(text, m.start())
    for m in re.finditer(r'(?<![-\w])srcset\s*=\s*"([^"]*)"', text):
        line = line_of(text, m.start())
        for candidate in m.group(1).split(","):
            url = candidate.strip().split()[0] if candidate.strip() else ""
            if url:
                yield "srcset", unescape(url), line


def check(path, failures):
    rel = os.path.relpath(path, ROOT)
    text = readable(path)
    here = os.path.dirname(path)

    demo_lines, _ = spans_in(path, text)

    for attr, value, line in references(path, text):
        if re.match(r"^#\s*$", value) and line not in demo_lines:
            failures.append((rel, line, "PLACEHOLDER", attr, value,
                             "bare '#' outside a demo is a route nobody "
                             "decided; write it or remove the link"))
            continue
        if not value or OFFSITE.match(value):
            continue

        if value.startswith("//"):
            failures.append((rel, line, "ABSOLUTE", attr, value,
                             "protocol-relative URL leaves the site"))
            continue

        if value.startswith("/"):
            failures.append((rel, line, "ABSOLUTE", attr, value,
                             "leading / resolves against the domain root, not "
                             "the project page"))
            continue

        target, _, fragment = value.partition("#")
        target = target.split("?")[0]

        if target:
            dest = os.path.normpath(os.path.join(here, target))
            if not os.path.exists(dest):
                failures.append((rel, line, "MISSING", attr, value,
                                 "no file at %s" % os.path.relpath(dest, ROOT)))
                continue
        else:
            dest = path  # same-page fragment

        if not fragment or fragment.startswith(":~:"):
            continue
        if not dest.endswith(".html"):
            continue
        # A form's action addresses the *response*, which this file is not. The
        # contact form posts to kontakt.html#fehler so that a failed submit
        # lands on the error summary without script, and that summary is
        # rendered only in the response — patterns/kontakt.html says so in a
        # comment above the form. The path still has to resolve; the fragment
        # cannot be checked here, because here is the wrong document.
        if attr == "action":
            continue
        # A fragment-only href inside a demo is a specimen's placeholder route.
        if not target and line in demo_lines:
            continue

        known = ids_in(dest)
        if known is not None and fragment not in known:
            failures.append((rel, line, "FRAGMENT", attr, value,
                             "no id=\"%s\" in %s" % (fragment,
                                                     os.path.relpath(dest, ROOT))))


def check_current(path, failures):
    """aria-current tells the truth, both ways.

    A link claiming `aria-current="page"` must resolve to the document it
    stands in — a same-page fragment counts, a link to another file is a
    claim about a page the reader is not on. And a link inside an <li> that
    resolves to its own document, plainly — no query string turning it into
    another logical page, no fragment turning it into a place on this one —
    must carry the marker, because it is an item in a set and the set is
    lying about where the reader is without it. Demos are exempt as ever:
    a nav specimen marks a pretend current page, and that is its job."""
    rel = os.path.relpath(path, ROOT)
    text = readable(path)
    here = os.path.dirname(path)
    demo_lines, li_lines = spans_in(path, text)

    for m in re.finditer(r"<a\b[^>]*>", text, re.I):
        tag = m.group(0)
        line = line_of(text, m.start())
        if line in demo_lines:
            continue
        href = re.search(r'\bhref\s*=\s*"([^"]*)"', tag)
        if not href:
            continue
        value = unescape(href.group(1).strip())
        if not value or value.startswith("/") or OFFSITE.match(value):
            continue
        cur = re.search(r'\baria-current\s*=\s*"([^"]*)"', tag)
        target, _, fragment = value.partition("#")
        target = target.split("?")[0]
        selfdoc = (not target
                   or os.path.normpath(os.path.join(here, target)) == path)
        plain = target and "?" not in value and not fragment

        if cur and cur.group(1) == "page" and not selfdoc:
            failures.append((rel, line, "CURRENT", "href", value,
                             'aria-current="page" on a link that leaves '
                             "the page"))
        elif cur and cur.group(1) == "true" and selfdoc and plain:
            failures.append((rel, line, "CURRENT", "href", value,
                             'aria-current="true" on the page itself; '
                             'ancestors say true, the page says page'))
        elif not cur and selfdoc and plain and line in li_lines:
            failures.append((rel, line, "CURRENT", "href", value,
                             "the page stands in its own list and does "
                             "not say so"))


def check_blank_targets(path, failures):
    """target="_blank" without rel=noopener hands the opener a window handle."""
    rel = os.path.relpath(path, ROOT)
    text = readable(path)
    for m in re.finditer(r"<a\b[^>]*>", text, re.I):
        tag = m.group(0)
        if 'target="_blank"' not in tag.replace(" =", "=").replace("= ", "="):
            continue
        relattr = re.search(r'\brel\s*=\s*"([^"]*)"', tag)
        if not relattr or "noopener" not in relattr.group(1).lower():
            failures.append((rel, line_of(text, m.start()), "OPENER", "target",
                             tag.strip()[:60],
                             'target="_blank" without rel="noopener"'))


def main():
    pages = []
    for dirpath, _, filenames in os.walk(TREE):
        for name in sorted(filenames):
            if name.endswith(".html"):
                pages.append(os.path.join(dirpath, name))
    pages.sort()

    failures = []
    for page in pages:
        check(page, failures)
        check_current(page, failures)
        check_blank_targets(page, failures)

    total = sum(1 for p in pages for _ in references(p, readable(p)))
    print("check-links: %d references across %d pages in design-system/"
          % (total, len(pages)))

    if not failures:
        print("check-links: every reference resolves")
        return 0

    by_kind = {}
    for f in failures:
        by_kind.setdefault(f[2], []).append(f)

    for kind in ("ABSOLUTE", "MISSING", "FRAGMENT", "PLACEHOLDER", "CURRENT",
                 "OPENER"):
        group = by_kind.get(kind)
        if not group:
            continue
        print("\n%s — %d" % (kind, len(group)))
        for rel, line, _, attr, value, why in group:
            print("  %s:%d  %s=\"%s\"\n      %s" % (rel, line, attr, value, why))

    print("\ncheck-links: %d broken reference%s"
          % (len(failures), "" if len(failures) == 1 else "s"))
    return 1


if __name__ == "__main__":
    sys.exit(main())
