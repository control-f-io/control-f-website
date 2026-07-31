#!/usr/bin/env python3
"""Every ARIA token on every page must be a word ARIA has.

The eighty-fourth check, and the third that reads what a page tells assistive
technology rather than what it draws. check-a11y.py holds the references — an
aria-labelledby must name an id that exists — and check-markup.py holds the
grammar. Between them is a gap the exact shape of a typo: `aria-labeledby`
(one L, the most common ARIA misspelling there is), `role="navigaton"`,
`aria-expanded="yes"`. Not one of the eighty-three checks beside this one would say
a word about any of them.

WHY THE GAP IS INVISIBLE FROM BOTH SIDES. check-a11y.py's ARIA-REF rule fires
when a correctly named attribute points at a missing id — but it finds the
attribute by its name, so an attribute whose NAME is wrong never enters the
rule at all. Misspell `aria-labelledby` and the reference does not become a
finding; it becomes nothing. The browser is no help from the other side: an
unknown aria-* attribute is not an error, not a warning, not a console line —
it is simply an attribute no accessibility tree ever reads. The element falls
back to whatever name it would have had, the page renders identically, and
the label someone wrote with care is silence. A wrong ARIA attribute is worse
than none, check-a11y.py already holds — this is the gate for the third way
of being wrong: not pointing at the wrong thing, but saying a word that is
not in the language.

WHAT FOUND THIS. A full sweep of all 59 files: every role and every aria-*
in the tree, against the vocabulary. The tree is CLEAN — ten distinct roles,
fifteen distinct aria-* attributes, every token a real one, every enumerated
value in its set, and not one focusable element inside an aria-hidden
subtree. Clean without a gate is a coincidence, not a fact: twelve routines
edit these pages every hour, and check-a11y.py's own CURRENT rule exists
because one unknown token was worth guarding against ("browsers announce an
unknown token as 'true' rather than dropping it"). That rule guards exactly
one of the forty-eight attributes. This is the same rule for the other
forty-seven, and for role.

THE RULES. Four, all of them everywhere in design-system/ — a word that is
not in ARIA's vocabulary is wrong on a documentation page exactly as it is
wrong on a pattern page, and a code sample quoting a wrong token is text,
which a parser never mistakes for an attribute.

  ROLE          every token in a role attribute is a concrete ARIA role.
                Unknown tokens are flagged; so are ARIA's twelve abstract
                roles (role="widget", role="landmark"), which the spec
                forbids in markup — they are the taxonomy's internal nodes,
                and browsers treat them as no role at all.

  ARIA-NAME     every attribute beginning aria- is one ARIA defines. The
                register is ARIA 1.2 plus the 1.3 additions engines already
                ship (aria-description, the braille pair, the -indextext
                pair, role image) — the register trails the platform, not
                the working draft, so a token that would work is never
                flagged for being newer than 1.2.

  ARIA-VALUE    an enumerated attribute carries a value from its set, an
                integer attribute an integer, a number attribute a number.
                aria-expanded="yes" and aria-level="first" are announced by
                nothing and error nowhere; the spec's own rule — treat an
                invalid value as the default — means the state someone
                wrote is silently replaced by the state they did not.
                aria-current's seven tokens are check-a11y.py's CURRENT rule
                already and are not re-judged here; the name is still this
                check's to know.

  HIDDEN-FOCUS  no focusable element inside an aria-hidden="true" subtree,
                unless something real neutralises it: `hidden` or `inert`
                on the subtree or a branch of it (the kontakt honeypot —
                hidden AND aria-hidden AND tabindex="-1" — is the correct
                shape and passes twice over), tabindex="-1" or `disabled`
                on the element itself. aria-hidden removes content from the
                accessibility tree but not from the tab order, so without
                the neutraliser a screen reader's focus lands on an element
                that, for its user, does not exist: focus announces
                nothing, arrows read nothing, and the reader is somewhere
                the page says is nowhere.

WHAT IT DELIBERATELY DOES NOT JUDGE. Whether a role fits its element
(role="button" on an <a> is a decision, not a typo), whether an attribute is
allowed on a role (aria-checked on a heading is wrong, but the matrix for
that is the whole of ARIA and half of it is genuinely contested), and
redundancy (role="list" on <ul> is belt-and-braces this tree wears on
purpose, against the Safari list-delisting behaviour the components document).
A register of words, not a style guide: the check says "that is not a word",
never "that is not the word I would have chosen".

Proven failing on each class reintroduced: a one-L aria-labeledby, a
role="dialogue", a role="landmark", an aria-expanded="yes" and a link inside
an aria-hidden span, seeded across two pages — five findings, five right
line numbers, and the sweep green again the moment they were removed.

stdlib only, no build step, no dependency. html.parser, the same python3
that serves the pages.

    python3 scripts/check-aria-vocabulary.py       # check, exit 1 on a finding
    python3 scripts/check-aria-vocabulary.py -v    # per-file counts too
"""

import argparse
import html.parser
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TREE = ROOT / "design-system"

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}

# ARIA 1.2's concrete roles, plus the 1.3 synonym `image`. `directory` is
# deprecated in 1.2 but still a word; deprecation is a style question and
# this check does not judge style.
ROLES = {
    "alert", "alertdialog", "application", "article", "banner", "blockquote",
    "button", "caption", "cell", "checkbox", "code", "columnheader",
    "combobox", "complementary", "contentinfo", "definition", "deletion",
    "dialog", "directory", "document", "emphasis", "feed", "figure", "form",
    "generic", "grid", "gridcell", "group", "heading", "image", "img",
    "insertion", "link", "list", "listbox", "listitem", "log", "main",
    "marquee", "math", "menu", "menubar", "menuitem", "menuitemcheckbox",
    "menuitemradio", "meter", "navigation", "none", "note", "option",
    "paragraph", "presentation", "progressbar", "radio", "radiogroup",
    "region", "row", "rowgroup", "rowheader", "scrollbar", "search",
    "searchbox", "separator", "slider", "spinbutton", "status", "strong",
    "subscript", "superscript", "switch", "tab", "table", "tablist",
    "tabpanel", "term", "textbox", "time", "timer", "toolbar", "tooltip",
    "tree", "treegrid", "treeitem",
}

# The taxonomy's internal nodes. In markup they are not a weaker claim, they
# are no claim: the spec forbids them and browsers ignore them.
ABSTRACT = {"command", "composite", "input", "landmark", "range", "roletype",
            "section", "sectionhead", "select", "structure", "widget",
            "window"}

# Every attribute ARIA 1.2 defines, plus the 1.3 additions engines ship.
# Attributes with no entry in the value tables below are strings or id
# references — the references are check-a11y.py's ARIA-REF rule and are not
# re-judged here.
NAMES = {
    "aria-activedescendant", "aria-atomic", "aria-autocomplete",
    "aria-braillelabel", "aria-brailleroledescription", "aria-busy",
    "aria-checked", "aria-colcount", "aria-colindex", "aria-colindextext",
    "aria-colspan", "aria-controls", "aria-current", "aria-describedby",
    "aria-description", "aria-details", "aria-disabled", "aria-dropeffect",
    "aria-errormessage", "aria-expanded", "aria-flowto", "aria-grabbed",
    "aria-haspopup", "aria-hidden", "aria-invalid", "aria-keyshortcuts",
    "aria-label", "aria-labelledby", "aria-level", "aria-live", "aria-modal",
    "aria-multiline", "aria-multiselectable", "aria-orientation", "aria-owns",
    "aria-placeholder", "aria-posinset", "aria-pressed", "aria-readonly",
    "aria-relevant", "aria-required", "aria-roledescription", "aria-rowcount",
    "aria-rowindex", "aria-rowindextext", "aria-rowspan", "aria-selected",
    "aria-setsize", "aria-sort", "aria-valuemax", "aria-valuemin",
    "aria-valuenow", "aria-valuetext",
}

# Enumerated sets, straight from the spec's value types. States whose type is
# "true/false/undefined" accept the literal "undefined" — the spec's own word
# for "as if absent". aria-current is deliberately absent; see the header.
ENUM = {
    "aria-atomic": {"true", "false"},
    "aria-busy": {"true", "false"},
    "aria-disabled": {"true", "false"},
    "aria-modal": {"true", "false"},
    "aria-multiline": {"true", "false"},
    "aria-multiselectable": {"true", "false"},
    "aria-readonly": {"true", "false"},
    "aria-required": {"true", "false"},
    "aria-expanded": {"true", "false", "undefined"},
    "aria-selected": {"true", "false", "undefined"},
    "aria-hidden": {"true", "false", "undefined"},
    "aria-grabbed": {"true", "false", "undefined"},
    "aria-checked": {"true", "false", "mixed", "undefined"},
    "aria-pressed": {"true", "false", "mixed", "undefined"},
    "aria-autocomplete": {"inline", "list", "both", "none"},
    "aria-haspopup": {"false", "true", "menu", "listbox", "tree", "grid",
                      "dialog"},
    "aria-invalid": {"grammar", "false", "spelling", "true"},
    "aria-live": {"assertive", "off", "polite"},
    "aria-orientation": {"horizontal", "vertical", "undefined"},
    "aria-sort": {"ascending", "descending", "none", "other"},
}

# Token lists: every space-separated token must be in the set, and an empty
# list says nothing at all, which is not a thing to write.
ENUM_LIST = {
    "aria-relevant": {"additions", "all", "removals", "text"},
    "aria-dropeffect": {"copy", "execute", "link", "move", "none", "popup"},
}

# Integers, with the spec's floors. -1 is the "unknown" the table and set
# attributes are allowed to declare.
INTEGER = {"aria-level": 1, "aria-colcount": -1, "aria-colindex": 1,
           "aria-colspan": 1, "aria-posinset": 1, "aria-rowcount": -1,
           "aria-rowindex": 1, "aria-rowspan": 0, "aria-setsize": -1}

NUMBER = {"aria-valuemax", "aria-valuemin", "aria-valuenow"}

FOCUSABLE_TAGS = {"button", "select", "textarea", "iframe", "summary"}


def neutral(attrs):
    """Does this element take its whole subtree out of reach? `hidden` is
    display: none unless a stylesheet fights it (none here does), `inert`
    is the attribute invented for exactly this."""
    return "hidden" in attrs or "inert" in attrs


def focusable(tag, attrs):
    """Would this element take Tab focus? The static answer only — a
    display or visibility that removes it is CSS's business."""
    if "hidden" in attrs or "disabled" in attrs:
        return False
    tabindex = attrs.get("tabindex", "").strip()
    if tabindex:
        return not tabindex.startswith("-")
    if tag in ("a", "area"):
        return "href" in attrs
    if tag == "input":
        return attrs.get("type", "").lower() != "hidden"
    if tag in ("audio", "video"):
        return "controls" in attrs
    if attrs.get("contenteditable", "false") != "false":
        return True
    return tag in FOCUSABLE_TAGS


class Page(html.parser.HTMLParser):
    """One pass over one file: every role, every aria-*, and the aria-hidden
    subtrees with what stands inside them.

    The stack carries (tag, shadow) where shadow means "focus cannot get in
    here": True below any hidden/inert element. hidden_at carries the line
    and depth of the outermost live aria-hidden="true", or None. A focusable
    element is a finding exactly when hidden_at is set and no shadow lies
    between it and that subtree's root."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.findings = []
        self.roles = 0
        self.arias = 0
        self.hidden_at = None

    def _shadowed(self):
        if self.hidden_at is None:
            return True
        return any(shadow for _, shadow in self.stack[self.hidden_at[1]:])

    def handle_starttag(self, tag, attrlist):
        attrs = {}
        for k, v in attrlist:
            attrs.setdefault(k.lower(), v if v is not None else "")
        line = self.getpos()[0]

        if "role" in attrs:
            self.roles += 1
            for token in attrs["role"].split():
                low = token.lower()
                if low in ABSTRACT:
                    self.findings.append((line, "ROLE",
                        "role=%r on <%s> is an abstract role. The spec "
                        "forbids abstract roles in markup; browsers treat "
                        "them as no role at all." % (token, tag)))
                elif low not in ROLES:
                    self.findings.append((line, "ROLE",
                        "role=%r on <%s> is not an ARIA role. An unknown "
                        "token is ignored without a word — the element keeps "
                        "its implicit role and the claim is never made."
                        % (token, tag)))

        for name, value in sorted(attrs.items()):
            if not name.startswith("aria-"):
                continue
            self.arias += 1
            if name not in NAMES:
                self.findings.append((line, "ARIA-NAME",
                    "%s on <%s> is not an ARIA attribute. No browser reads "
                    "it, no checker that finds attributes by name sees it — "
                    "whatever it was written to say is said to nobody."
                    % (name, tag)))
                continue
            v = value.strip()
            if name in ENUM and v.lower() not in ENUM[name]:
                self.findings.append((line, "ARIA-VALUE",
                    "%s=%r on <%s>: not one of %s. The spec's rule for an "
                    "invalid value is the default value, so this state is "
                    "silently replaced, never announced."
                    % (name, value, tag, "/".join(sorted(ENUM[name])))))
            elif name in ENUM_LIST:
                bad = [t for t in v.split()
                       if t.lower() not in ENUM_LIST[name]]
                if bad or not v.split():
                    self.findings.append((line, "ARIA-VALUE",
                        "%s=%r on <%s>: %s is not among %s."
                        % (name, value, tag,
                           " ".join(repr(t) for t in bad) or "an empty list",
                           "/".join(sorted(ENUM_LIST[name])))))
            elif name in INTEGER:
                if not (re.fullmatch(r"-?\d+", v)
                        and int(v) >= INTEGER[name]):
                    self.findings.append((line, "ARIA-VALUE",
                        "%s=%r on <%s>: an integer of at least %d."
                        % (name, value, tag, INTEGER[name])))
            elif name in NUMBER:
                try:
                    float(v)
                except ValueError:
                    self.findings.append((line, "ARIA-VALUE",
                        "%s=%r on <%s>: a number." % (name, value, tag)))

        # -- HIDDEN-FOCUS --------------------------------------------------
        hides = attrs.get("aria-hidden", "").strip().lower() == "true"
        if (not self._shadowed() and not neutral(attrs)
                and focusable(tag, attrs)):
            self.findings.append((line, "HIDDEN-FOCUS",
                "<%s> is focusable inside the aria-hidden subtree opened on "
                "line %d. Tab still stops here; the accessibility tree says "
                "here does not exist. tabindex=\"-1\", disabled, `hidden` "
                "on the subtree — or unhide it." % (tag, self.hidden_at[0])))
        # An element can be both out of the tree and in the tab order all by
        # itself: <input aria-hidden="true">, <a href aria-hidden="true">.
        if (hides and self.hidden_at is None and not neutral(attrs)
                and focusable(tag, attrs)):
            self.findings.append((line, "HIDDEN-FOCUS",
                "<%s aria-hidden=\"true\"> is itself focusable. Tab stops "
                "on an element the accessibility tree does not have." % tag))
        if tag in VOID:
            return
        self.stack.append((tag, neutral(attrs)))
        if hides and self.hidden_at is None and not neutral(attrs):
            self.hidden_at = (line, len(self.stack) - 1)

    def handle_startendtag(self, tag, attrlist):
        self.handle_starttag(tag, attrlist)
        if tag not in VOID:
            self._close_to(len(self.stack) - 1)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                self._close_to(i)
                return

    def _close_to(self, depth):
        del self.stack[depth:]
        if self.hidden_at is not None and len(self.stack) <= self.hidden_at[1]:
            self.hidden_at = None


def audit():
    findings, seen = [], []
    for path in sorted(TREE.rglob("*.html")):
        page = Page()
        page.feed(path.read_text(encoding="utf-8"))
        page.close()
        rel = path.relative_to(ROOT)
        seen.append((rel, page.roles, page.arias, len(page.findings)))
        for line, rule, why in sorted(page.findings):
            findings.append((rel, line, rule, why))
    return findings, seen


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="per-file counts, not only the failures")
    args = ap.parse_args()

    findings, seen = audit()

    if args.verbose:
        print("  %-56s %6s %6s %6s" % ("file", "roles", "aria", "bad"))
        for rel, roles, arias, bad in seen:
            print("  %-56s %6d %6d %6d" % (str(rel)[-56:], roles, arias, bad))
        print()

    if findings:
        for rel, line, rule, why in findings:
            print("%s:%d  %s\n    %s" % (rel, line, rule, why), file=sys.stderr)
        print("\n%d vocabulary finding%s across %d file%s."
              % (len(findings), "" if len(findings) == 1 else "s",
                 len({f[0] for f in findings}),
                 "" if len({f[0] for f in findings}) == 1 else "s"),
              file=sys.stderr)
        return 1

    print("aria-vocabulary: %d files read, %d role attributes and %d aria-* "
          "attributes checked against the register; every token a word ARIA "
          "has, and no focusable element inside an aria-hidden subtree."
          % (len(seen), sum(s[1] for s in seen), sum(s[2] for s in seen)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
