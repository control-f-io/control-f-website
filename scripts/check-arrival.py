#!/usr/bin/env python3
"""Where the page puts a reader who asked to go somewhere.

The twenty-second check, and the first whose subject is the scroll itself rather
than anything drawn on it. Two facts, one about every page in patterns/ and one
about a single declaration in base.css, and both of them were false.

THE CLEARANCE. .cf-nav is `position: sticky; top: 0` with a min-height of
--nav-height, so it stands over the first 84 px of every viewport on every
shipping page. A fragment in the URL scrolls its target flush with the top of
that viewport — under the bar, not below it — and scroll-margin-top is the one
thing that moves the landing point down. components/article.html states this in
as many words:

    Headings carry scroll-margin-top for the sticky navigation. Without it an
    anchor lands underneath the bar.

It was kept by exactly one rule, `.cf-prose :is(h2, h3, h4)`, written for the
prose track. Counted, the tree has 58 headings in the document flow that own an
id; 20 of them are prose and were covered. The other 38 were not, and 33 of
those are .cf-section-header__label — which is the <h2> of every section of
every designed page in the system. So on thirteen of the fourteen pattern
pages, every section address in the page pointed under the bar.

And it does not land LOW, it lands GONE. The bar is 84 px and the label's own
box is 16, so the heading a reader has just asked for is entirely inside the
band: measured on the landing page, loading the address with the fragment
already in it, #prozess, #partner, #faq and #blog each put 16 px of 16 behind
the navigation, and #team escaped only because the document had run out of
scroll to give. Which is also why nobody found it: the page is not broken
afterwards, it is merely somewhere else, and the reader who typed the address
assumes they mis-remembered the anchor.

The rule this check holds is the one the prose rule was an instance of: an id
on a heading in the document flow is an ADDRESS, whatever else it is for.
Thirty-eight of the thirty-eight are also aria-labelledby targets naming a
region — that is what most of them were written for — and it changes nothing,
because expertise.html#feld-02 is still a URL a person can be sent. Headings
inside a <dialog> or inside the consent banner are the one structural
exception and are not counted: a modal dialog is not in the page's scroll box
and the banner is fixed to the bottom of the viewport, so neither can be
scrolled to at all.

THE PREFERENCE. base.css line 52 sets `scroll-behavior: smooth` on <html>, and
nothing anywhere took it back for prefers-reduced-motion. Every other moving
thing in the three stylesheets is gated on `no-preference` — every view
timeline, every keyframe, every transition — and this one declaration sat
outside all of it, which made it the only motion on the site that did not ask.

It is also the largest. A smooth scroll from the top of the landing page to the
team strip travels 6030 px, measured; the reader who set the preference got
every pixel. And it fires far more often than the anchors it was written for,
because Chromium scrolls a focused element into view: on a page this tall every
Tab to an off-screen control is one of these journeys. Measured on the landing
page, reading the focused element 45 ms after each Tab: 34 of its 47 stops were
still in flight under the default and 0 of 46 are under `reduce`. Which put the
largest dose of the one unasked motion on the readers navigating by keyboard —
the population the preference exists for.

Neither fact is visible in a screenshot, and that is the whole shape: the
anchor lands somewhere, the scroll arrives somewhere, and a still frame of
either is a correct-looking page.

WHAT THIS CHECK WILL NOT DO. Rule 1 resolves a heading against the shipping
stylesheets with a matcher that understands descendant chains of tag and class
selectors and :is() lists of the same — every selector shape that carries a
scroll-margin-top in this tree. A shape it cannot read is a FINDING and not a
pass, so the check cannot go quiet by being outgrown.

stdlib only, no build step, no dependency — the same contract as the
twenty-one checks beside it.

    python3 scripts/check-arrival.py       # check, exit 1 on a finding
    python3 scripts/check-arrival.py -v    # print every heading and its clearance
"""

import argparse
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system" / "assets" / "css"
PATTERNS = ROOT / "design-system" / "patterns"

# The three that ship, in cascade order — same set as every check beside this.
# acts.css is the fourth that ships: the five-act scroll composition, which
# left one prototype's <style> block when the landing page wanted it too.
# Its own headings are addressable, so this check has to be able to see the
# scroll-margin they carry.
SHIPPING = ("tokens.css", "base.css", "components.css", "acts.css")

COMMENT = re.compile(r"/\*.*?\*/", re.S)
HEADING = re.compile(r"h[1-6]")

# Void elements, so the ancestor stack stays honest without a real parser.
VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
    "param", "source", "track", "wbr",
    # the SVG shapes this tree writes unclosed
    "circle", "ellipse", "line", "path", "polygon", "polyline", "rect", "stop", "use",
}


# --------------------------------------------------------------------------
# Lengths. Enough arithmetic to evaluate what the tree actually writes: a bare
# length, a var() into :root, or a calc() of those added together. Anything
# else is a finding rather than a guess.
# --------------------------------------------------------------------------
LENGTH = re.compile(r"^(-?\d*\.?\d+)(px|rem)$")


def tokens(css):
    """--name: value pairs off :root. Only the root scope; the inverse theme
       redefines colours, never a length this check reads."""
    out = {}
    root = re.search(r":root\s*\{(.*?)\n\}", css, re.S)
    if not root:
        return out
    for name, value in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", root.group(1)):
        out[name] = value.strip()
    return out


def length_px(value, toks, seen=()):
    """A length in px, or None if this expression is not one this check reads."""
    value = value.strip()
    # A bare 0 is a length and needs no unit. Without this the one value that
    # revokes a clearance outright reads as an expression the check cannot
    # parse, which fails the build for the wrong reason and names the wrong
    # fault.
    if re.fullmatch(r"-?0+(?:\.0+)?", value):
        return 0.0
    m = LENGTH.match(value)
    if m:
        n = float(m.group(1))
        return n * 16.0 if m.group(2) == "rem" else n
    m = re.fullmatch(r"var\(\s*(--[\w-]+)\s*\)", value)
    if m:
        name = m.group(1)
        if name in seen or name not in toks:
            return None
        return length_px(toks[name], toks, seen + (name,))
    m = re.fullmatch(r"calc\((.*)\)", value, re.S)
    if m:
        parts = [p.strip() for p in m.group(1).split("+")]
        if len(parts) < 2:
            return None
        total = 0.0
        for part in parts:
            got = length_px(part, toks, seen)
            if got is None:
                return None
            total += got
        return total
    return None


# --------------------------------------------------------------------------
# Selectors. The grammar this check reads, and refuses to guess past:
#
#   selector      := compound (WS compound)*        descendant combinators only
#   compound      := tag? ('.' class | ':is(' list ')')*
#   list          := selector (',' selector)*       flattened
#
# A combinator this does not know (> + ~), an attribute selector, an id, a
# pseudo-class other than :is(), or a pseudo-element makes the rule
# UNREADABLE — reported, never skipped.
# --------------------------------------------------------------------------
COMPOUND_BIT = re.compile(r"\.[-\w]+|^[a-zA-Z][\w-]*")


def expand_is(selector):
    """:is(a, b) c  ->  ['a c', 'b c'], recursively. None if unbalanced."""
    m = re.search(r":is\(", selector)
    if not m:
        return [selector]
    start = m.end()
    depth = 1
    i = start
    while i < len(selector) and depth:
        if selector[i] == "(":
            depth += 1
        elif selector[i] == ")":
            depth -= 1
        i += 1
    if depth:
        return None
    head, inner, tail = selector[:m.start()], selector[start:i - 1], selector[i:]
    out = []
    for alt in split_top(inner):
        got = expand_is(head + alt + tail)
        if got is None:
            return None
        out.extend(got)
    return out


def compound(part):
    """(tag or None, {classes}) for one compound selector, or None if unread."""
    tag = None
    classes = set()
    rest = part
    m = re.match(r"^[a-zA-Z][\w-]*", rest)
    if m:
        tag = m.group(0)
        rest = rest[m.end():]
    while rest:
        m = re.match(r"^\.[-\w]+", rest)
        if not m:
            return None
        classes.add(m.group(0)[1:])
        rest = rest[m.end():]
    if tag is None and not classes:
        return None
    return tag, classes


def parse_selector(selector):
    """[(tag, classes), ...] outermost first, or None if not this grammar."""
    selector = selector.strip()
    if not selector or re.search(r"[>+~\[\]#*]|::|:(?!is\()", selector):
        return None
    parts = selector.split()
    out = []
    for part in parts:
        got = compound(part)
        if got is None:
            return None
        out.append(got)
    return out


def matches(chain, ancestry):
    """Does a parsed selector match this element? `ancestry` is the element's
       own (tag, classes) last, its ancestors before it."""
    if not chain:
        return False
    if not fits(chain[-1], ancestry[-1]):
        return False
    remaining = list(chain[:-1])
    i = len(ancestry) - 2
    while remaining and i >= 0:
        if fits(remaining[-1], ancestry[i]):
            remaining.pop()
        i -= 1
    return not remaining


def fits(want, have):
    tag, classes = want
    htag, hclasses = have
    if tag is not None and tag != htag:
        return False
    return classes <= hclasses


# --------------------------------------------------------------------------
# Reading the stylesheets
# --------------------------------------------------------------------------
def split_top(text, sep=","):
    """Split on `sep` at paren depth 0. A selector list is comma-separated —
       but so is the inside of :is(), and splitting first turned
       `.cf-prose :is(h2, h3, h4)` into three selectors, one of them the bare
       `h3` that then matched three headings it has nothing to do with. The
       list is split at the top level and the :is() expanded after."""
    out, depth, start = [], 0, 0
    for i, ch in enumerate(text):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == sep and depth == 0:
            out.append(text[start:i])
            start = i + 1
    out.append(text[start:])
    return [p.strip() for p in out if p.strip()]


def rules_with(css, prop):
    """[(selector, value)] for every declaration of `prop`, at any nesting."""
    out = []
    body = COMMENT.sub(" ", css)
    for m in re.finditer(r"([^{}@;]+)\{([^{}]*)\}", body):
        selectors, decls = m.group(1).strip(), m.group(2)
        for name, value in re.findall(r"([-\w]+)\s*:\s*([^;]+)", decls):
            if name.strip() == prop:
                for one in split_top(selectors):
                    out.append((one, value.strip()))
    return out


def reduce_blocks(css):
    """The bodies of every @media block whose prelude asks for reduced motion."""
    out = []
    body = COMMENT.sub(" ", css)
    for m in re.finditer(r"@media([^{]*)\{", body):
        if "prefers-reduced-motion" not in m.group(1) or "reduce" not in m.group(1):
            continue
        i, depth = m.end(), 1
        while i < len(body) and depth:
            if body[i] == "{":
                depth += 1
            elif body[i] == "}":
                depth -= 1
            i += 1
        out.append(body[m.end():i - 1])
    return out


# --------------------------------------------------------------------------
# Reading the pages
# --------------------------------------------------------------------------
class Headings(HTMLParser):
    """Every id-bearing heading, with its ancestry and whether it can be
       scrolled to at all."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.found = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = set(a.get("class", "").split())
        self.stack.append((tag, classes, a))
        if HEADING.fullmatch(tag) and a.get("id"):
            unreachable = any(
                t == "dialog" or "data-cf-consent-banner" in attr
                for t, _, attr in self.stack
            )
            self.found.append({
                "id": a["id"],
                "classes": classes,
                "ancestry": [(t, c) for t, c, _ in self.stack],
                "unreachable": unreachable,
            })
        if tag in VOID:
            self.stack.pop()

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                return


# --------------------------------------------------------------------------
# The two rules
# --------------------------------------------------------------------------
def rule_clearance(verbose=False):
    css = {name: (CSS / name).read_text(encoding="utf-8") for name in SHIPPING}
    toks = tokens(css["tokens.css"])
    nav = length_px("var(--nav-height)", toks)
    if nav is None:
        return ["tokens.css: --nav-height is not a length this check can read"], 0

    parsed, unreadable = [], []
    for name in SHIPPING:
        for selector, value in rules_with(css[name], "scroll-margin-top"):
            px = length_px(value, toks)
            if px is None:
                unreadable.append(f"{name}: scroll-margin-top: {value} — not a length this check reads")
                continue
            alts = expand_is(selector)
            if alts is None:
                unreadable.append(f"{name}: unbalanced :is() in `{selector}`")
                continue
            for alt in alts:
                chain = parse_selector(alt)
                if chain is None:
                    unreadable.append(f"{name}: `{alt}` is not a selector shape this check reads")
                    continue
                # (classes, elements) — the two columns of specificity this
                # grammar can produce; there are no ids and no attributes in it.
                spec = (sum(len(c) for _, c in chain),
                        sum(1 for t, _ in chain if t is not None))
                parsed.append((chain, px, spec, len(parsed), f"{name} `{selector}`"))

    findings = list(unreadable)
    counted = 0
    for page in sorted(PATTERNS.glob("*.html")):
        src = page.read_text(encoding="utf-8")
        if "cf-nav" not in src:
            continue          # no sticky bar, nothing to clear
        p = Headings()
        p.feed(src)
        for h in p.found:
            if h["unreachable"]:
                continue
            counted += 1
            # THE CASCADE, NOT THE MAXIMUM. Taking the largest matching value
            # would pass a heading whose clearance a later rule has revoked —
            # which is the shape a regression actually takes: nobody deletes
            # the declaration, somebody adds one further down. So the winner is
            # the browser's: highest specificity, ties broken by order, and the
            # rules were collected in link order across the three stylesheets.
            best, why = 0.0, None
            winner = None
            for chain, px, spec, order, origin in parsed:
                if not matches(chain, h["ancestry"]):
                    continue
                key = (spec, order)
                if winner is None or key > winner:
                    winner, best, why = key, px, origin
            if verbose:
                print(f"  {best:6.0f}px  patterns/{page.name}#{h['id']}"
                      f"  {'.'.join(sorted(h['classes'])) or '(no class)'}"
                      f"  {why or '— nothing'}")
            if best < nav:
                findings.append(
                    f"patterns/{page.name}#{h['id']}: clears {best:.0f}px of a "
                    f"{nav:.0f}px sticky bar — the heading lands behind .cf-nav"
                )
    return findings, counted


def rule_preference():
    findings = []
    for name in SHIPPING:
        css = (CSS / name).read_text(encoding="utf-8")
        smooth = [sel for sel, value in rules_with(css, "scroll-behavior")
                  if value.strip() == "smooth"]
        if not smooth:
            continue
        taken_back = set()
        for block in reduce_blocks(css):
            for sel, value in rules_with(block, "scroll-behavior"):
                if value.strip() != "smooth":
                    taken_back.add(sel)
        for sel in smooth:
            if sel not in taken_back:
                findings.append(
                    f"{name}: `{sel} {{ scroll-behavior: smooth }}` is never taken back "
                    f"under prefers-reduced-motion: reduce"
                )
    return findings


def main():
    parser = argparse.ArgumentParser(description="Anchors clear the bar; the smooth scroll asks first.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="print every counted heading and the clearance it resolves to")
    args = parser.parse_args()

    if args.verbose:
        print("headings in the flow that own an id, and what gives them their clearance:")
    clearance, counted = rule_clearance(args.verbose)
    preference = rule_preference()

    findings = clearance + preference
    if findings:
        print(f"\narrival: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1
    print(f"arrival OK — {counted} addressable headings across patterns/ all clear the sticky bar, "
          f"and every smooth scroll is taken back under reduced motion")
    return 0


if __name__ == "__main__":
    sys.exit(main())
