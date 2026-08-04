#!/usr/bin/env python3
"""The accessibility facts about a page that can be counted without a browser.

The twelfth check, and the second about the system as a *site*. check-links.py
asks whether a reference lands on a file. This one asks whether the page a
reader is handed can be read by a reader who is not using a mouse and a pair of
working eyes — as far as that question can be answered by a file.

It cannot be answered all the way. Whether a focus ring is visible enough,
whether a tab order follows the reading order, whether an alt text is the right
alt text: those need a browser, a person, or both, and this script does not
pretend to have either. What it does have is the part of accessibility that is
arithmetic — an id is on the page or it is not, a heading level is one more than
the last or it is two more, an <img> carries `alt` or it carries nothing — and
every one of those has the same failure shape as the ten checks beside it: the
page renders exactly the same either way, so nobody sees it, so it stays.

WHAT FOUND THIS. The pattern pages declare `lang="de"`. The landing page's h1
is "Find the answers. Make the decisions. Build the future." — three English
sentences, the site's tagline, the first thing a screen reader announces after
the title, and until this commit it was announced with German phonemes. That is
not an accent; it is a word the listener cannot resolve. WCAG 3.1.2. And it is
not only a speech problem: base.css already treats `lang` as load-bearing
rather than as metadata — its note on `overflow-wrap` says the right answer for
German is `hyphens: auto` "against these pages' lang='de'" — so the same
attribute decides where this line will one day break.

Twenty-four more English runs were on five other pages: the six job titles on
the two team strips and the author line on blog-artikel.html, the two English
service names among four process subtitles and the same two among five <select>
options on kontakt.html, and the English head of three of the four vacancy
titles on karriere.html and of the one on karriere-stelle.html — that last one
in its h1 and in its breadcrumb. Twenty-five marks, not one of them visible in
a screenshot.

WHAT FOUND THE EIGHTH RULE. Twelve pattern pages close with the same six
footer links. Six of those pages are themselves among the six links, and
exactly one of them — karriere.html — told a screen reader "you are here";
the other five said nothing. Meanwhile the two subpages, blog-artikel.html
under News and karriere-stelle.html under Karriere, marked their parent
section aria-current="page": the one token that is a claim about the FILE,
announced on a link that leads away from it. "Current page" on a link you can
follow somewhere else is not orientation, it is misdirection — WAI-ARIA gives
"true" for exactly this case, the current item that is not the current page.
The nav marker in components.css draws both tokens identically, because the
ink means "where you are", not "which file".

WHAT FOUND THE NINTH AND TENTH RULES. The landing page's team section was a
region landmark named by its own heading — and the scroll box inside it is
also a region, named by the same heading, because that is the scroll-box
contract components/team.html states. Two landmarks, one role, one name,
one inside the other: a landmark list offered "Das Team" twice and nothing
to say which of the two is the content. The section's name was the
redundant claim (the component's own demo keeps its surrounding section
unnamed), so the section gave it up. And on all thirteen pages the preview
chrome — the fixed "← Design System" link before </body> — was the one
focusable element on the page that no landmark contained: a reader walking
the page by landmarks would simply never be offered it. It lives in a
labelled <nav> now. Both facts are arithmetic on a file, so both are rules.

THE RULES. Ten, in two scopes.

Everywhere in design-system/, because every one of these is wrong on any page
in any language:

  DUPLICATE-ID    two elements on one page carrying the same id. Everything
                  that points at an id — a label, an aria-labelledby, a
                  fragment, getElementById — silently takes the first.
  ARIA-REF        an aria-labelledby / describedby / controls / owns / details
                  / errormessage / activedescendant naming an id that is not on
                  the page. A wrong ARIA attribute is worse than none: it does
                  not degrade to the element's own text, it replaces it with
                  nothing.
  LABEL-FOR       a <label for> matching no id. The label is then a caption
                  drawn next to a control it has no relationship with, and
                  clicking it does nothing.
  CONTROL-NAME    an <input>/<select>/<textarea> with no accessible name from
                  any of the four sources: a <label for>, a <label> wrapped
                  round it, aria-label, aria-labelledby. Announced as "edit
                  text, blank".
  IMG-ALT         an <img> with no `alt` attribute at all. `alt=""` is a
                  decision — this image is decoration — and passes. A missing
                  attribute is the absence of a decision, and a screen reader
                  falls back to reading the file name.
  CURRENT (i)     an aria-current whose value is not one of the seven tokens
                  the specification has (page, step, location, date, time,
                  true, false). An unknown token is treated as "true" by some
                  browsers and dropped by none, so a typo here changes what is
                  announced rather than failing.

In design-system/patterns/ only, because those files are the only ones in the
tree that are *a page a visitor is given* rather than documentation
about one. The chapters under foundations/ and components/ are written in
English, and they pair an h2 with h4 "Do"/"Don't" headings twenty-six times —
correct for what they are, and not this check's business:

  HEADINGS        exactly one h1, and no level skipped on the way down. The
                  heading levels are the document's table of contents and a
                  skipped level is a missing branch in it.
  DOCUMENT        lang="de" on <html>; exactly one non-empty <title>; exactly
                  one viewport meta, and one that does not forbid zoom.
  FOREIGN         the register below. A text run that IS one of these phrases,
                  entirely, must sit inside an element carrying a non-German
                  lang.
  CURRENT (ii)    three facts about aria-current on links, all arithmetic
                  against the page's own filename. An <a aria-current="page">
                  must point at the file it is on — "current page" on a link
                  that leads elsewhere announces a place the reader is not.
                  An <a aria-current="true"> pointing at its own file has the
                  stronger claim available and must make it. And inside
                  .cf-nav__list and .cf-footer__links — the two lists every
                  page repeats — a link to the page itself must carry
                  aria-current="page", because five siblings saying it and one
                  staying silent is the consistency bug this rule exists for.
                  Links elsewhere on the page are not required to self-mark:
                  a logo, a TOC fragment or a demo may link home unannotated.
  LANDMARK        two landmarks on one page sharing one role and one
                  accessible name — the same aria-labelledby target or the
                  same aria-label text. Landmarks are a table of contents a
                  reader jumps by; two entries that read identically are one
                  destination advertised twice, and the reader finds out
                  which is which by going there. Names here are compared by
                  their source rather than by resolved text: two landmarks
                  naming the same id ARE the same name, and two ids whose
                  text happens to coincide would already be two headings
                  saying the same thing — a different bug, not this one.
  ORPHAN          a focusable element — a link, a button, a control, a
                  tabindex — sitting outside every landmark. Tab reaches
                  it; a reader walking the page by landmarks is never
                  offered it, so the two journeys through one page disagree
                  about what is on it. The skip link is the one deliberate
                  exception: it is the first thing on the page precisely so
                  that it comes before all structure, and it is exempt by
                  its class.

WHY THE FOREIGN RULE IS A REGISTER AND NOT A DETECTOR. Language identification
of a two-word run is guesswork, and this system already knows what a guess in a
checker costs. The register is the same shape as the breakpoint register in
tokens.css: a hand-kept list whose value is not that it is complete but that
what is on it can never come back. Matching is on the WHOLE text run, so
"Data Engineers und AI-Spezialisten" inside a German sentence on ueber-uns.html
is not a match and is not meant to be — an English term absorbed into German
prose is the exception WCAG 3.1.2 states, and marking it would be the same bug
pointing the other way.

One passage the register cannot reach: <title> on landing-page.html is
"Control-F — Find the answers. Make the decisions. Build the future.", one run,
half German and half English. An element carries one lang and a <title> has no
children, so there is nowhere to put the mark. It is left, knowingly.

stdlib only, no build step, no dependency. html.parser, the same python3 that
serves the pages.

    python3 scripts/check-a11y.py       # check, exit 1 on a finding
    python3 scripts/check-a11y.py -v    # per-file counts, not only failures
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

# Void elements never open a scope, so they must not be pushed on the stack.
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}

CONTROLS = {"input", "select", "textarea"}

# A control of these types is not something a reader types into and takes its
# name from its own value or from nothing at all.
UNNAMED_INPUT_TYPES = {"hidden", "submit", "button", "reset", "image"}

ARIA_IDREF = ("aria-labelledby", "aria-describedby", "aria-controls",
              "aria-owns", "aria-details", "aria-errormessage",
              "aria-activedescendant")

# The seven values aria-current has. Anything else is a typo that still
# announces — unknown tokens fall back to "true" rather than to nothing.
CURRENT_TOKENS = {"page", "step", "location", "date", "time", "true", "false"}

# The two lists every pattern page repeats, and the only places a link to the
# page itself is REQUIRED to say so. See CURRENT (ii) in the module docstring.
SELF_MARK_LISTS = {"cf-nav__list", "cf-footer__links"}

# The eight ARIA landmark roles. A <dialog> (or role="dialog") is not a
# landmark but it does contain its content the way one does — the consent
# layer lives in dialogs — so for the ORPHAN rule it counts as shelter.
LANDMARK_ROLES = {"banner", "complementary", "contentinfo", "form", "main",
                  "navigation", "region", "search"}

# Elements whose implicit role is a landmark wherever they stand.
IMPLICIT_LANDMARK = {"nav": "navigation", "main": "main",
                     "aside": "complementary"}

# header/footer are banner/contentinfo ONLY at the top of the document —
# scoped inside any of these they are plain grouping content (HTML AAM).
SCOPES_HEADER_FOOTER = {"article", "aside", "main", "nav", "section"}

# What the ORPHAN rule counts as focusable. tabindex is handled separately.
FOCUSABLE = {"button", "input", "select", "textarea"}

# The FOREIGN register. Each entry is a complete text run, normalised for
# whitespace, that is not German. Add to it when a foreign phrase is added to a
# pattern page and marked; the entry is what stops it arriving unmarked next
# time. Never add a phrase that also occurs inside German prose — see the
# module docstring on why matching is whole-run.
FOREIGN = {
    # landing-page.html, the hero. Three runs, one per <br>.
    "Find the answers.": "en",
    "Make the decisions.": "en",
    "Build the future.": "en",
    # The team strips on landing-page.html and ueber-uns.html, and the author
    # line on blog-artikel.html.
    "Founder": "en",
    "CEO & Managing Partner": "en",
    "Data Engineer": "en",
    "AI Specialist": "en",
    "Platform Engineer": "en",
    "Analytics Engineer": "en",
    # The two English process subtitles on landing-page.html, and the same two
    # as <option> labels on kontakt.html. "Der Einstieg" and "Die Basis" are
    # the other two subtitles and are German.
    "Predictive Maintenance": "en",
    "Asset Performance": "en",
    # The English head of three vacancy titles on karriere.html. The German
    # tail — "Industrie", "(m/w/d)" — is outside the marked span and outside
    # these entries.
    "Machine Learning Engineer": "en",
    "Solution Engineer": "en",
}

VIEWPORT_BLOCKS_ZOOM = re.compile(
    r"user-scalable\s*=\s*(no|0)|maximum-scale\s*=\s*(1|1\.0)(?![\d.])", re.I)


class Page(html.parser.HTMLParser):
    """One pass over one file, collecting what the eight rules need.

    convert_charrefs is on, so `&amp;` in a text run arrives as `&` and the
    register can be written the way the page reads rather than the way it is
    typed.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []              # [(tag, attrs)], open elements
        self.ids = {}                # id -> [line, ...]
        self.aria_refs = []          # (line, tag, attr, idref)
        self.label_for = []          # (line, idref)
        self.labelled = set()        # every id named by a <label for>
        self.controls = []           # (line, tag, attrs, wrapped_in_label)
        self.imgs_no_alt = []        # [line, ...]
        self.headings = []           # (line, level, text)
        self.titles = []             # [text, ...]
        self.viewports = []          # [content, ...]
        self.html_lang = None
        self.foreign = []            # (line, run, lang_in_scope)
        self.currents = []           # (line, tag, value) — every aria-current
        self.links = []              # (line, href, aria-current, in_self_list)
        self.landmarks = []          # (line, tag, role, namekey)
        self.orphans = []            # (line, tag, classes) — focusable, no landmark
        self._in_title = False
        self._title = []
        self._heading = None
        self._heading_text = []

    # -- scope helpers ----------------------------------------------------
    def _lang(self):
        """The innermost lang in scope, or None if nothing declares one."""
        for tag, attrs in reversed(self.stack):
            if attrs.get("lang") is not None:
                return attrs["lang"]
        return None

    def _inside(self, *tags):
        return any(tag in tags for tag, _ in self.stack)

    def _in_self_list(self):
        """Is an ancestor one of the two lists that must self-mark?"""
        for _, attrs in self.stack:
            if SELF_MARK_LISTS & set((attrs.get("class") or "").split()):
                return True
        return False

    def _shelter(self, tag, attrs, ancestors):
        """The landmark role of one element, or "dialog", or None.

        `ancestors` is the open-element stack BELOW this element — needed
        because header/footer are only landmarks at the top of the document,
        and because the caller asks this question both about the element
        itself and about each of its ancestors.
        """
        role = (attrs.get("role") or "").strip().lower()
        if role:
            if role in LANDMARK_ROLES or role == "dialog":
                return role
            return None                     # an explicit role overrides the tag
        if tag == "dialog":
            return "dialog"
        if tag in IMPLICIT_LANDMARK:
            return IMPLICIT_LANDMARK[tag]
        if tag in ("header", "footer"):
            if any(t in SCOPES_HEADER_FOOTER for t, _ in ancestors):
                return None
            return "banner" if tag == "header" else "contentinfo"
        # section and form are landmarks only once they have a name — an
        # unnamed section is generic, which is most sections and correct.
        if tag in ("section", "form"):
            if attrs.get("aria-label") or attrs.get("aria-labelledby"):
                return "region" if tag == "section" else "form"
        return None

    def _namekey(self, attrs):
        """The name of a landmark, by its source. See LANDMARK in the header."""
        if attrs.get("aria-labelledby"):
            return "labelledby:" + " ".join(attrs["aria-labelledby"].split())
        if attrs.get("aria-label"):
            return "label:" + " ".join(attrs["aria-label"].split())
        return ""

    # -- parser callbacks -------------------------------------------------
    def handle_starttag(self, tag, attrlist):
        attrs = {k.lower(): (v if v is not None else "") for k, v in attrlist}
        line = self.getpos()[0]

        if tag == "html":
            self.html_lang = attrs.get("lang")
        if "id" in attrs and attrs["id"]:
            self.ids.setdefault(attrs["id"], []).append(line)
        for attr in ARIA_IDREF:
            if attrs.get(attr):
                for ref in attrs[attr].split():
                    self.aria_refs.append((line, tag, attr, ref))
        if "aria-current" in attrs:
            self.currents.append((line, tag, attrs["aria-current"]))
        if tag == "a" and "href" in attrs:
            self.links.append((line, attrs["href"],
                               attrs.get("aria-current"), self._in_self_list()))
        if tag == "label" and "for" in attrs:
            self.label_for.append((line, attrs["for"]))
            self.labelled.add(attrs["for"])
        if tag in CONTROLS:
            self.controls.append((line, tag, attrs, self._inside("label")))
        if tag == "img" and "alt" not in attrs:
            self.imgs_no_alt.append(line)
        if tag == "meta" and attrs.get("name", "").lower() == "viewport":
            self.viewports.append(attrs.get("content", ""))

        shelter = self._shelter(tag, attrs, self.stack)
        if shelter and shelter != "dialog":
            self.landmarks.append((line, tag, shelter, self._namekey(attrs)))
        focusable = ((tag == "a" and "href" in attrs)
                     or (tag in FOCUSABLE
                         and attrs.get("type", "").lower() != "hidden")
                     or attrs.get("tabindex", "-1") not in ("", "-1"))
        if focusable and not shelter:
            depth = 0
            for t, a in self.stack:
                if self._shelter(t, a, self.stack[:depth]):
                    break
                depth += 1
            else:
                self.orphans.append((line, tag, attrs.get("class", "")))
        if tag == "title" and self._inside("head"):
            self._in_title, self._title = True, []
        if re.fullmatch(r"h[1-6]", tag):
            self._heading, self._heading_text = (line, int(tag[1])), []

        if tag not in VOID:
            self.stack.append((tag, attrs))

    def handle_startendtag(self, tag, attrlist):
        self.handle_starttag(tag, attrlist)
        if tag not in VOID and self.stack and self.stack[-1][0] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag == "title" and self._in_title:
            self._in_title = False
            self.titles.append(" ".join("".join(self._title).split()))
        if re.fullmatch(r"h[1-6]", tag) and self._heading:
            line, level = self._heading
            self.headings.append(
                (line, level, " ".join("".join(self._heading_text).split())))
            self._heading = None
        # Unwind to the matching open tag. Nothing in this tree relies on the
        # parser's error recovery; if a tag is unbalanced the stack simply
        # returns to where it was, which is what a browser does too.
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        if self._in_title:
            self._title.append(data)
        if self._heading:
            self._heading_text.append(data)
        if self._inside("script", "style"):
            return
        run = " ".join(data.split())
        if run in FOREIGN:
            self.foreign.append((self.getpos()[0], run, self._lang()))


def js_ids():
    """Ids that never appear in any page's source because a script injects them.

    Same source and the same reason as check-links.py: cf-icons.js is the one
    place an icon is drawn and injects the whole sprite. Credited to every page
    rather than per-page here, because an aria-* reference to a sprite symbol
    would be a different bug from the one this rule is about and no page makes
    one — this is only here so that if a page ever does, the check says
    something true about it.
    """
    found = set()
    if JS.is_dir():
        for path in sorted(JS.glob("*.js")):
            found.update(re.findall(r"""\bid=["']([^"']+)["']""",
                                    path.read_text(encoding="utf-8")))
    return found


def audit_page(path, page, injected, strict):
    """Findings for one file. `strict` turns on the patterns-only rules."""
    rel = path.relative_to(ROOT)
    out = []

    for name, lines in sorted(page.ids.items()):
        if len(lines) > 1:
            out.append((lines[1], "DUPLICATE-ID",
                        "id=%r is on %d elements (lines %s). Everything that "
                        "points at it takes the first."
                        % (name, len(lines), ", ".join(map(str, lines)))))

    known = set(page.ids) | injected
    for line, tag, attr, ref in page.aria_refs:
        if ref not in known:
            out.append((line, "ARIA-REF",
                        "<%s %s> names id=%r, which is not on this page."
                        % (tag, attr, ref)))

    for line, ref in page.label_for:
        if ref not in page.ids:
            out.append((line, "LABEL-FOR",
                        "<label for=%r> matches no element on this page." % ref))

    for line, tag, attrs, wrapped in page.controls:
        if tag == "input" and attrs.get("type", "").lower() in UNNAMED_INPUT_TYPES:
            continue
        named = (wrapped
                 or (attrs.get("id") and attrs["id"] in page.labelled)
                 or attrs.get("aria-label")
                 or attrs.get("aria-labelledby"))
        if not named:
            out.append((line, "CONTROL-NAME",
                        "<%s name=%r> has no label, no wrapping <label>, and no "
                        "aria-label. It is announced with no name."
                        % (tag, attrs.get("name", ""))))

    for line in page.imgs_no_alt:
        out.append((line, "IMG-ALT",
                    "<img> with no alt attribute. Write alt=\"\" if it is "
                    "decoration — that is a decision; a missing attribute is not."))

    for line, tag, value in page.currents:
        if value not in CURRENT_TOKENS:
            out.append((line, "CURRENT",
                        "<%s aria-current=%r>: not one of the specification's "
                        "seven tokens. Browsers announce an unknown token as "
                        "\"true\" rather than dropping it." % (tag, value)))

    if not strict:
        return out

    # The three link facts of CURRENT (ii), all against this page's own name.
    # A href is "this page" when, stripped of query and fragment, it is empty
    # or the filename itself — "suche.html?q=x" is still suche.html.
    def is_self(href):
        return href.split("#")[0].split("?")[0] in ("", path.name)

    for line, href, current, in_list in page.links:
        if current == "page" and not is_self(href):
            out.append((line, "CURRENT",
                        "<a href=%r aria-current=\"page\"> on %s: \"current "
                        "page\" announced on a link that leads to another "
                        "page. The token for a current section is \"true\"."
                        % (href, path.name)))
        elif current == "true" and is_self(href):
            out.append((line, "CURRENT",
                        "<a href=%r aria-current=\"true\"> IS the current "
                        "page; the stronger claim exists and must be made — "
                        "aria-current=\"page\"." % href))
        elif current is None and in_list and is_self(href):
            out.append((line, "CURRENT",
                        "<a href=%r> links the page it is on from a list "
                        "every page repeats, and does not say so. Its five "
                        "siblings mark theirs: aria-current=\"page\"." % href))

    groups = {}
    for line, tag, role, name in page.landmarks:
        groups.setdefault((role, name), []).append((line, tag))
    for (role, name), where in sorted(groups.items()):
        if len(where) > 1:
            out.append((where[1][0], "LANDMARK",
                        "%d %r landmarks named by %s (lines %s). Two entries "
                        "in the landmark list that read identically are one "
                        "destination advertised twice."
                        % (len(where), role, name or "nothing",
                           ", ".join(str(l) for l, _ in where))))

    for line, tag, classes in page.orphans:
        if "skip-link" in classes.split():
            continue
        out.append((line, "ORPHAN",
                    "<%s class=%r> is focusable and outside every landmark. "
                    "Tab reaches it; landmark navigation never offers it. "
                    "Give it a landmark to live in." % (tag, classes)))

    h1s = [h for h in page.headings if h[1] == 1]
    if len(h1s) != 1:
        out.append((h1s[1][0] if len(h1s) > 1 else 1, "HEADINGS",
                    "%d <h1> on this page; a page has exactly one."
                    % len(h1s)))
    previous = 0
    for line, level, text in page.headings:
        if previous and level > previous + 1:
            out.append((line, "HEADINGS",
                        "h%d follows h%d — level %d is skipped. (%r)"
                        % (level, previous, previous + 1, text[:48])))
        previous = level

    if page.html_lang != "de":
        out.append((1, "DOCUMENT",
                    "<html lang=%r>; every page under patterns/ is German."
                    % page.html_lang))
    if len(page.titles) != 1 or not page.titles[0]:
        out.append((1, "DOCUMENT",
                    "%d non-empty <title> in <head>; a page has exactly one."
                    % len([t for t in page.titles if t])))
    if len(page.viewports) != 1:
        out.append((1, "DOCUMENT",
                    "%d viewport meta; a page has exactly one."
                    % len(page.viewports)))
    else:
        content = page.viewports[0]
        if VIEWPORT_BLOCKS_ZOOM.search(content):
            out.append((1, "DOCUMENT",
                        "viewport %r forbids zoom. WCAG 1.4.4." % content))

    for line, run, lang in page.foreign:
        want = FOREIGN[run]
        if not lang or lang.lower().split("-")[0] == "de":
            out.append((line, "FOREIGN",
                        "%r is %s and the lang in scope is %r. Put lang=%r on "
                        "the element that holds this run and nothing else."
                        % (run, want, lang or "de (inherited)", want)))

    return out

# The English edition under patterns/en/ is generated, not written —
# scripts/build-i18n.py builds it from the German page beside it and changes
# only the words. It carries the same markup, the same classes, the same
# thresholds and the same glass by construction, so every fact this file
# keeps is already kept one directory up; asserting it twice would only mean
# two tables to edit whenever one page changes. `build-i18n.py --check` is
# what holds the mirror to its source. Same argument check-links.py makes
# about the generated pages at the repository root.
GENERATED = "patterns/en/"


def audit():
    injected = js_ids()
    findings, seen = [], []
    for path in sorted(TREE.rglob("*.html")):
        if path.relative_to(TREE).as_posix().startswith(GENERATED):
            continue
        page = Page()
        page.feed(path.read_text(encoding="utf-8"))
        page.close()
        strict = PATTERNS in path.parents
        out = audit_page(path, page, injected, strict)
        seen.append((path.relative_to(ROOT), strict, len(page.ids),
                     len(page.aria_refs), len(page.controls),
                     len(page.headings), len(page.foreign), len(out)))
        for line, rule, why in sorted(out):
            findings.append((path.relative_to(ROOT), line, rule, why))
    return findings, seen


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="per-file counts, not only the failures")
    args = ap.parse_args()

    findings, seen = audit()

    if args.verbose:
        print("  %-52s %-6s %5s %5s %5s %5s %5s"
              % ("file", "scope", "ids", "aria", "ctrl", "head", "foreign"))
        for rel, strict, ids, aria, ctrl, head, foreign, _ in seen:
            print("  %-52s %-6s %5d %5d %5d %5d %5d"
                  % (str(rel)[-52:], "page" if strict else "docs",
                     ids, aria, ctrl, head, foreign))
        print()

    if findings:
        for rel, line, rule, why in findings:
            print("%s:%d  %s\n    %s" % (rel, line, rule, why), file=sys.stderr)
        print("\n%d accessibility finding%s across %d file%s."
              % (len(findings), "" if len(findings) == 1 else "s",
                 len({f[0] for f in findings}),
                 "" if len({f[0] for f in findings}) == 1 else "s"),
              file=sys.stderr)
        return 1

    pages = sum(1 for _, strict, *_ in seen if strict)
    print("a11y: %d files read (%d pattern pages under the full ten rules), "
          "%d ids, %d aria references, %d form controls, %d headings, "
          "%d marked foreign runs on the pattern pages."
          % (len(seen), pages,
             sum(s[2] for s in seen), sum(s[3] for s in seen),
             sum(s[4] for s in seen), sum(s[5] for s in seen),
             sum(s[6] for s in seen if s[1])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
