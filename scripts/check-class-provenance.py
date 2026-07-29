#!/usr/bin/env python3
"""Resolve every class in the markup against the stylesheets that declare it.

A design system's drift is not usually a wrong colour. It is a page that grew
its own copy of something — a class typed into a page-local <style> block under
deadline, a literal where a token exists, a name that reads like a component
and is one page's private fork of it. Each of those renders correctly on the
day it is written. What makes them expensive is that they are invisible: a
class with no rule looks exactly like a class with one, and a page-local
re-implementation looks exactly like the component until the component moves.

So this is a census before it is a gate. It reads every .html under
design-system/, counts every class the markup uses, and asks one question of
each: WHO DECLARES THIS. There are exactly five legitimate answers —

    tokens.css / base.css / components.css   the three that ship
    docs.css                                 documentation chrome, never ships
    preview.css                              pattern-preview chrome, never ships
    the page's own <style> block             page-local, and stated as such
    nobody                                   a finding

— and the fifth is what the exit code is about. A class nothing declares is
either a typo, a rule that was deleted out from under its markup, or a name
that was always decorative; all three are worth knowing about, and none of the
three announces itself in a screenshot.

The gate is five rules:

  1. RESOLUTION. Every class used on the shipping surface resolves to a
     declaration. The one structural exception is a BEM namespace root: a page
     may write `cf-values` when the stylesheets declare `cf-values__list` and
     friends, because the root names the block for the reader even when it
     carries no rule of its own. The allowance is deliberately narrow — it
     needs a declared `X__…` or `X--…` member — so a misspelt component name
     still fails.

  2. NO DOCS CHROME ON A SHIPPING PAGE. docs.css and preview.css never reach
     control-f.de. A page that does not link one of them must not use a class
     only it declares, or the page renders one way in the design system and
     another way in production — the one drift a screenshot of the design
     system can never show, because the design system is where it looks right.

  3. NO PAGE-LOCAL COPY OF PREVIEW CHROME. The first census found .ds-back
     shipping in fourteen page-local copies, byte for byte, with the two under
     prototypes/ already forked to a hardcoded z-index and respelt tokens.
     Those copies are folded into preview.css now, and the only way the fold
     reopens is a page redeclaring a class preview.css owns — so that exact
     move is the finding.

  4. NO LITERAL IN A PAGE-LOCAL BLOCK WHERE A TOKEN EXISTS. check-spacing-
     scale.py holds the three shipping stylesheets to this and says so: page
     -local <style> blocks are "deliberately out of scope". They were out of
     scope of every check in this directory, which made them the one place in
     the tree where a hex could sit unchallenged. Two literal classes are
     checked here: a colour a token already names exactly, and a length in a
     spacing property.

  5. NO INLINE LAYOUT UNDER patterns/. An inline style= may set custom
     properties — that is per-instance data the markup genuinely owns, `--i`,
     `--stage`, `--build-dx` — and nothing else. The scope is patterns/ alone
     and that is a boundary rather than an omission: a pattern page stands in
     for a page of the real site, while a page under foundations/ or
     components/ frequently writes CSS as its own specimen.

--report prints the whole census instead: the resolution table, every
page-local block with what it declares, and the page-local rules that appear
verbatim on more than one page. That last table is the one to read. It is how
the first run of this census found that .ds-back shipped in fourteen copies
and that two of them — the two under prototypes/ — had already forked to a
different z-index and a different token spelling: the entire argument for this
script, written out by the tree itself. Those fourteen are one declaration in
preview.css now and rule 3 keeps them that way; the prototype forks remain, in
the table, where the census can see them.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-class-provenance.py           # check, exit 1 on drift
    python3 scripts/check-class-provenance.py --report  # the full census
"""

import argparse
import collections
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
CSS = DS / "assets" / "css"

# The three that ship to control-f.de, and the two that do not: docs.css is
# the documentation's own chrome, preview.css is the one rule for the .ds-back
# link a pattern page carries back into the documentation — the rule that used
# to ship in fourteen page-local copies.
# acts.css is the fourth: the five-act scroll composition, which left one
# prototype's <style> block when the landing page wanted it too. It ships.
SHIPPING = ("tokens.css", "base.css", "components.css", "acts.css")
DOCS = "docs.css"
PREVIEW = "preview.css"

# prototypes/ are sketches, not the system: they predate most of the tokens,
# they are linked from nowhere the reader walks, and check-spacing-scale.py
# already draws this exact boundary. They are censused by --report and not
# gated, so a literal there is visible without being a build failure.
GATED_DIRS = ("foundations", "components", "patterns")

# Rule 4's scope. A pattern page is a page of the site with the chrome of the
# design system bolted on; a documentation page is allowed to write CSS as the
# thing it is demonstrating.
INLINE_GATED_DIRS = ("patterns",)


# --------------------------------------------------------------------------
# Exemptions. Every entry is a class nothing declares that this run decided not
# to delete, with the reason and — where it is not this routine's to fix — the
# lane it belongs to. The list is meant to stay short and to be read as a list
# of open findings rather than as settled law.
# --------------------------------------------------------------------------
UNRESOLVED_OK = {
    # docs.css declares .docs-rule and .docs-rule--dont and stops there, on
    # purpose: "told apart by their label and by the material underneath —
    # white for do, sunken grey for don't". The do half IS the base, so --do is
    # a name for the reader of the markup and never a rule. 23 pages.
    ("*", "docs-rule--do"): "the default half of a do/don't pair; docs.css styles only --dont",
    # A real grid child of .cf-error--page with no rule of its own, in the
    # markup components/error-state.html publishes. The pattern page is
    # following the component correctly; the component is what is missing a
    # declaration. → components lane.
    ("patterns/404.html", "cf-error__lead"): "structural grid child of .cf-error--page; components.css declares no rule",
    # The class is a label and the grid it names is typed into a style
    # attribute beside it. → foundations lane.
    ("foundations/colors.html", "docs-swatch-row"): "names a grid that is written inline instead; see the inline-style census",
    # class="text-foil h1" — nothing in the tree declares .h1, in any
    # stylesheet or any page-local block. The foil demo asks for a display size
    # it never gets. → foundations lane.
    ("foundations/sight.html", "h1"): "no .h1 exists anywhere in the tree; the foil demo asks for a size nothing gives it",
    # THREE HOOKS THAT ARE READ RATHER THAN DRAWN. Each of these names a
    # position in the markup that a SCRIPT needs and no rule wants: they carry
    # no declarations because there is nothing to declare, and deleting them to
    # satisfy this check would break the thing that reads them.
    #   .lp-proc-index / .lp-proc-bar  check-label-clearance.py's CHROME_SELECTORS
    #                                  — the pinned chrome whose clearance is
    #                                    measured past the pin rather than at it
    #   .sp-field__sensors             gen-proto-field.py's splice target for
    #                                    the field, matched at its own indent
    # They arrived on this page with the five acts. A class with a reader is
    # not an undeclared class, it is a class declared somewhere this check does
    # not look — and the register is where that gets said out loud.
    ("patterns/landing-page.html", "lp-proc-index"): "a hook check-label-clearance.py selects on; no rule wants it",
    ("patterns/landing-page.html", "lp-proc-bar"): "a hook check-label-clearance.py selects on; no rule wants it",
    ("patterns/landing-page.html", "sp-field__sensors"): "gen-proto-field.py's splice target; no rule wants it",
}

# Rule 3 exemptions: a literal in a page-local block that is not a token
# decision. Same spirit as check-spacing-scale.py's ALLOWED.
LITERAL_OK = {
    # The optical descender clearance under a mono label rule, measured against
    # that label's own cap height rather than against the page's rhythm. Not a
    # rung of the scale and not reachable from one.
    ("foundations/found.html", "padding-bottom: 0.85rem"),
}


# --------------------------------------------------------------------------
# CSS and HTML, read with regexes rather than parsed. Every construct these
# have to survive is in this tree and is covered by the tests below the rules.
# --------------------------------------------------------------------------
COMMENT = re.compile(r"/\*.*?\*/", re.S)
STRING = re.compile(r"\"[^\"]*\"|'[^']*'")
URL = re.compile(r"url\([^)]*\)", re.I)
# A class selector. The first character cannot be a digit, which is what keeps
# `.5rem`, `1.17` and `0.85rem` out of the class set without a second pass.
CLASS_SEL = re.compile(r"\.(-?[A-Za-z_][A-Za-z0-9_-]*)")
STYLE_BLOCK = re.compile(r"<style[^>]*>(.*?)</style>", re.S)
SCRIPT_BLOCK = re.compile(r"<script[^>]*>.*?</script>", re.S)
CLASS_ATTR = re.compile(r"class\s*=\s*\"([^\"]*)\"|class\s*=\s*'([^']*)'")
STYLE_ATTR = re.compile(r"style\s*=\s*\"([^\"]*)\"|style\s*=\s*'([^']*)'")
LINK_CSS = re.compile(r"<link[^>]+href=\"([^\"]*\.css)\"")

COLOUR = re.compile(
    r"#[0-9a-fA-F]{3,8}\b|(?<![\w-])rgba?\([^)]*\)|(?<![\w-])hsla?\([^)]*\)"
    r"|(?<![\w-])oklch\([^)]*\)|(?<![\w-])oklab\([^)]*\)"
)
# Straight from check-spacing-scale.py, so the two agree about what spacing is.
SPACING_PROP = re.compile(
    r"\b(?:margin|padding)(?:-(?:block|inline)(?:-(?:start|end))?|-(?:top|right|bottom|left))?"
    r"|\b(?:row-|column-)?gap\b"
)
LENGTH = re.compile(r"(?<![\w.-])(-?\d*\.?\d+)(px|rem)(?![\w-])")
FREE_LENGTH = {"0px", "0rem"}


def scrub(css):
    """Blank comments, strings and url() so only structure and values remain."""
    for pattern in (COMMENT, STRING, URL):
        css = pattern.sub(lambda m: " " * len(m.group(0)), css)
    return css


def declared_classes(css):
    return set(CLASS_SEL.findall(scrub(css)))


def rules(css):
    """(selector, body) for every rule whose body contains no nested rule.

    Depth is tracked so a rule inside @media or @supports is found, and a body
    that itself contains braces — an at-rule prelude — is skipped rather than
    mis-split. Enough to compare two pages' copies of the same declaration.
    """
    css = scrub(css)
    out = []
    depth = 0
    start = 0
    stack = []
    for m in re.finditer(r"[{}]", css):
        if m.group(0) == "{":
            if depth == 0 or True:
                stack.append((css[start:m.start()], m.end(), depth))
            depth += 1
            start = m.end()
        else:
            depth -= 1
            if stack:
                sel, body_start, _ = stack.pop()
                body = css[body_start:m.start()]
                if "{" not in body and "}" not in body:
                    out.append((" ".join(sel.split()), " ".join(body.split())))
            start = m.end()
    return out


def token_colours():
    """Every token whose value is a bare colour, keyed by normalised value."""
    text = scrub((CSS / "tokens.css").read_text())
    by_value = {}
    for m in re.finditer(r"(--[a-z0-9-]+)\s*:\s*([^;}]+)", text):
        value = m.group(2).strip()
        if COLOUR.fullmatch(value):
            by_value.setdefault(normalise_colour(value), m.group(1))
    return by_value


def normalise_colour(value):
    value = "".join(value.split()).lower()
    if re.fullmatch(r"#[0-9a-f]{3}", value):
        value = "#" + "".join(c * 2 for c in value[1:])
    return value


def declarations(body):
    for decl in body.split(";"):
        prop, sep, value = decl.partition(":")
        if sep:
            yield prop.strip(), value.strip()


def pages():
    for path in sorted(DS.rglob("*.html")):
        yield path


def rel(path):
    return path.relative_to(DS).as_posix()


def gated(path):
    return rel(path).split("/")[0] in GATED_DIRS


class Page:
    def __init__(self, path):
        self.path = path
        self.rel = rel(path)
        text = path.read_text()
        self.blocks = STYLE_BLOCK.findall(text)
        markup = STYLE_BLOCK.sub(" ", text)
        markup = SCRIPT_BLOCK.sub(" ", markup)
        self.used = set()
        for a, b in CLASS_ATTR.findall(markup):
            self.used.update((a or b).split())
        self.inline = [a or b for a, b in STYLE_ATTR.findall(markup)]
        self.local = set()
        for block in self.blocks:
            self.local |= declared_classes(block)
        self.stylesheets = {href.rsplit("/", 1)[-1] for href in LINK_CSS.findall(text)}


def load():
    ship = set()
    for name in SHIPPING:
        ship |= declared_classes((CSS / name).read_text())
    docs = declared_classes((CSS / DOCS).read_text())
    preview = declared_classes((CSS / PREVIEW).read_text())
    return ship, docs, preview, [Page(p) for p in pages()]


def namespace_root(name, declared):
    """True when the stylesheets declare a member of this class's BEM family."""
    return any(
        other.startswith(name + "__") or other.startswith(name + "--")
        for other in declared
    )


def exempt(page_rel, name):
    return ("*", name) in UNRESOLVED_OK or (page_rel, name) in UNRESOLVED_OK


# --------------------------------------------------------------------------
# The five rules
# --------------------------------------------------------------------------
def rule_resolution(ship, docs, preview, pages_):
    declared = ship | docs | preview
    findings = []
    for page in pages_:
        if not gated(page.path):
            continue
        for name in sorted(page.used):
            if name in declared or name in page.local:
                continue
            if namespace_root(name, declared):
                continue
            if exempt(page.rel, name):
                continue
            findings.append(f"{page.rel}: class .{name} is declared nowhere")
    return findings


def rule_docs_leak(ship, docs, preview, pages_):
    findings = []
    for sheet, declared in ((DOCS, docs - ship), (PREVIEW, preview - ship - docs)):
        for page in pages_:
            if not gated(page.path) or sheet in page.stylesheets:
                continue
            for name in sorted(page.used & declared):
                if name in page.local or exempt(page.rel, name):
                    continue
                findings.append(
                    f"{page.rel}: uses .{name}, which only {sheet} declares, and does not link {sheet}"
                )
    return findings


def rule_preview_copy(preview, pages_):
    """Preview chrome is declared once. This is the rule the fold rests on:
    .ds-back shipped in fourteen page-local copies, byte for byte, and the two
    under prototypes/ had already forked to a hardcoded z-index and respelt
    tokens by the time the census first counted them. The copies are folded
    into preview.css now, and a page-local redeclaration is how they would
    come back."""
    findings = []
    for page in pages_:
        if not gated(page.path):
            continue
        for name in sorted(page.local & preview):
            findings.append(
                f"{page.rel}: declares .{name} in a page-local block; "
                f"preview chrome is declared once, in {PREVIEW}"
            )
    return findings


def rule_literals(pages_):
    by_value = token_colours()
    findings = []
    for page in pages_:
        if not gated(page.path):
            continue
        for block in page.blocks:
            for selector, body in rules(block):
                for prop, value in declarations(body):
                    if (page.rel, f"{prop}: {value}") in LITERAL_OK:
                        continue
                    for literal in COLOUR.findall(value):
                        token = by_value.get(normalise_colour(literal))
                        if token:
                            findings.append(
                                f"{page.rel}: {selector} {{ {prop}: {value} }} — "
                                f"{literal} is var({token})"
                            )
                    if SPACING_PROP.fullmatch(prop):
                        for number, unit in LENGTH.findall(value):
                            if number + unit in FREE_LENGTH:
                                continue
                            findings.append(
                                f"{page.rel}: {selector} {{ {prop}: {value} }} — "
                                f"{number}{unit} in a spacing property, and the scale has rungs"
                            )
    return findings


def rule_inline(pages_):
    findings = []
    for page in pages_:
        if page.rel.split("/")[0] not in INLINE_GATED_DIRS:
            continue
        for attr in page.inline:
            for prop, value in declarations(attr):
                if prop.startswith("--"):
                    continue
                findings.append(
                    f"{page.rel}: inline style=\"{prop}: {value}\" — "
                    "an inline style may carry custom properties and nothing else"
                )
    return findings


# --------------------------------------------------------------------------
# The census
# --------------------------------------------------------------------------
def report(ship, docs, preview, pages_):
    declared = ship | docs | preview
    print("CLASS PROVENANCE")
    print(f"  {len(list(pages_)):>4} html files under design-system/")
    print(f"  {len(ship):>4} classes declared by the three shipping stylesheets")
    print(f"  {len(docs):>4} declared by docs.css")
    print(f"  {len(preview):>4} declared by preview.css")

    where = collections.Counter()
    unresolved = collections.defaultdict(list)
    for page in pages_:
        for name in page.used:
            if name in ship:
                where["shipping stylesheet"] += 1
            elif name in docs:
                where["docs.css"] += 1
            elif name in preview:
                where["preview.css"] += 1
            elif name in page.local:
                where["the page's own <style>"] += 1
            elif namespace_root(name, declared):
                where["BEM namespace root"] += 1
            else:
                where["nobody"] += 1
                unresolved[name].append(page.rel)
    print("\n  every class use, by who declares it")
    for key, count in where.most_common():
        print(f"    {count:>5}  {key}")

    print(f"\n  declared by nobody ({len(unresolved)} distinct)")
    for name, users in sorted(unresolved.items()):
        mark = "exempt" if all(exempt(u, name) for u in users) else "FINDING"
        print(f"    {mark:>7}  .{name:<18} {len(users)} page(s): {', '.join(sorted(users)[:3])}")

    print("\nPAGE-LOCAL <style> BLOCKS")
    for page in pages_:
        if not page.blocks:
            continue
        decls = sum(len(list(declarations(b))) for block in page.blocks for _, b in rules(block))
        shadow = sorted(page.local & ship)
        print(f"  {page.rel:<44} {len(page.local):>3} classes  {decls:>4} declarations"
              + (f"  shadows {len(shadow)} shipped" if shadow else ""))

    # Only rules that name a class. A keyframe step is a selector too, and
    # `from { opacity: 0 }` matching `from { opacity: 0 }` inside a different
    # @keyframes says nothing about drift.
    seen = collections.defaultdict(list)
    for page in pages_:
        for block in page.blocks:
            for selector, body in rules(block):
                if body.strip() and CLASS_SEL.search(selector):
                    seen[(selector, body)].append(page.rel)

    print("\nTHE SAME NAME ON MORE THAN ONE PAGE — one rule, copied")
    families = collections.defaultdict(list)
    for (selector, body), users in seen.items():
        if len(set(users)) > 1:
            families[selector].append((len(users), users, body))
    for selector in sorted(families):
        copies = families[selector]
        total = sum(c for c, _, _ in copies)
        forked = " — FORKED into %d versions" % len(copies) if len(copies) > 1 else ""
        print(f"  {selector}: {total} copies{forked}")
        for count, users, body in sorted(copies, reverse=True):
            print(f"      {count:>3} x  {', '.join(sorted(users)[:3])}"
                  + (" …" if len(users) > 3 else ""))
            print(f"             {body[:110]}")

    # The other half of the same question, and the half a name-based census
    # cannot see: one rule written twice under two names is a component the
    # system does not have yet, and it reads as two page-local decisions.
    print("\nTHE SAME RULE UNDER MORE THAN ONE NAME — one component, unnamed")
    by_body = collections.defaultdict(set)
    for (selector, body), users in seen.items():
        by_body[body].add((selector, tuple(sorted(users))))
    for body, entries in sorted(by_body.items()):
        names = {selector for selector, _ in entries}
        where = {page for _, users in entries for page in users}
        if len(names) > 1 and len(where) > 1 and len(body) > 40:
            print(f"  {', '.join(sorted(names))}")
            print(f"      on {', '.join(sorted(where))}")
            print(f"      {body[:110]}")

    print("\nINLINE style= UNDER patterns/")
    props = collections.Counter()
    for page in pages_:
        if page.rel.split("/")[0] not in INLINE_GATED_DIRS:
            continue
        for attr in page.inline:
            for prop, _ in declarations(attr):
                props["custom property" if prop.startswith("--") else prop] += 1
    for prop, count in props.most_common():
        print(f"    {count:>5}  {prop}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", action="store_true", help="print the census and exit 0")
    args = parser.parse_args()

    ship, docs, preview, pages_ = load()
    if args.report:
        report(ship, docs, preview, pages_)
        return 0

    checks = (
        ("class resolution", rule_resolution(ship, docs, preview, pages_)),
        ("docs chrome on a shipping page", rule_docs_leak(ship, docs, preview, pages_)),
        ("a page-local copy of preview chrome", rule_preview_copy(preview, pages_)),
        ("literal in a page-local block", rule_literals(pages_)),
        ("inline layout under patterns/", rule_inline(pages_)),
    )
    failed = 0
    for name, findings in checks:
        if findings:
            failed += len(findings)
            print(f"{name}: {len(findings)} finding(s)")
            for finding in findings:
                print(f"  {finding}")
    if failed:
        print(f"\n{failed} finding(s). Run --report for the full census.")
        return 1
    counted = sum(len(p.used) for p in pages_ if gated(p.path))
    print(f"class provenance OK — {counted} class uses on the gated surface, all resolved")
    return 0


if __name__ == "__main__":
    sys.exit(main())
