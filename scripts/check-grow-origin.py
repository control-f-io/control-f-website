#!/usr/bin/env python3
"""A stroke that grows by scale must grow from the end its markup names.

Nothing on this page is drawn with a dash. Two notes in landing-page.html work
through why — a dashed draw under `vector-effect: non-scaling-stroke` measures
its dash in SCREEN pixels while pathLength normalises in USER units, so every
stroke stops at the render scale and stays there — and both land on the same
replacement: A STRAIGHT STROKE GROWN FROM ONE END IS A SCALE ABOUT THAT END.
`scale: 0 -> 1` under `transform-box: fill-box`, with `transform-origin` naming
which end is the fixed one.

That makes transform-origin carry the whole direction of the draw. It is the
difference between the lectern's top rail spreading OUT of the middle vertical
— the point the flow's trunk lands on — and the same rail growing INTO it from
the far corner. Both render a rail. Only one of them is the relay the page
describes, and no screenshot of any single scroll position tells them apart:
the two are identical at scale 0 and identical again at scale 1.

WHAT WENT WRONG, and it is the reason this file exists. The direction is
authored per stroke, in the markup, as `--o`, and read by one declaration:

    .lp-frame__line { transform-origin: var(--o, 0 0); }      (0,1,0)

Six strokes away, the shared selector for the same elements said:

    .lp-frame path  { transform-origin: 0 0; }                (0,1,1)

which wins by one point, on every one of them, always. Five of the six declare
`--o: 0 0` and were therefore right by coincidence. The sixth — `M0 0H500`, the
rail's left arm, the one stroke in the drawing whose parent junction is not its
own top-left corner — declares `100% 0` and computed `0px 0px`. Measured in
Chromium: every .lp-frame__line resolved `transform-origin: 0px 0px`, and the
arm grew out of the lectern's top-left corner rightward, closing on the trunk's
landing point LAST, for as long as the drawing has existed.

The note directly above that rule had already found the hazard and named the
arithmetic — "an `animation` shorthand here would outweigh the class rules below
((0,1,1) against (0,1,0))" — and then left `transform-origin` standing one line
under the sentence warning about it. Reading a note is not running one.

WHAT IS CHECKED. For every element in the page whose style attribute sets a
`--o`, the declaration that WINS the cascade for `transform-origin` must be the
one that reads that custom property. Not "a rule exists that reads it" — the
broken page had that rule too, and it lost.

So the check resolves the cascade: it parses every rule that declares
transform-origin out of the shipping stylesheets and the page's own <style>,
matches each against the element, and compares specificity then source order.
A rule it cannot evaluate is a FAILURE, not a skip — a selector shape this
matcher does not understand is exactly where the next one of these would hide.

WHAT THIS DOES NOT CLAIM. It does not check that `--o` names the RIGHT end;
which junction a stroke belongs to is the drawing's form, and
check-flow-terminals.py and check-flow-handover.py hold the geometry it grows
into. This holds only that the value the markup states is the value the browser
uses — which is the half that was false.

stdlib only, no build step, no dependency. Same python3 that serves the pages.
"""

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "design-system/prototypes/statement-to-process.html"

# In the order the page loads them: the linked stylesheets first, the page's own
# <style> last. Source order is the tiebreaker at equal specificity, so this
# list IS part of the cascade being resolved.
SHEETS = [
    ROOT / "design-system/assets/css/tokens.css",
    ROOT / "design-system/assets/css/base.css",
    ROOT / "design-system/assets/css/components.css",
    # The five acts, which left one prototype's <style> block when a second
    # page wanted them. It is a shipping stylesheet like the three above and
    # loads after them, so it sits last in the cascade this list resolves.
    ROOT / "design-system/assets/css/acts.css",
]

PROP = "transform-origin"


# --------------------------------------------------------------------------
# CSS: rules that declare transform-origin, with their source order and line.
# --------------------------------------------------------------------------

def strip_comments(css):
    """Blank out comments, keeping newlines so line numbers survive."""
    return re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)), css, flags=re.S)


def rules_declaring(css, prop, origin_label, line_base=1):
    """Every rule whose own declaration block sets `prop`.

    At-rules with blocks (@media, @supports) are transparent to the cascade for
    our purpose — their contents are ordinary rules — so we descend into them.
    @keyframes blocks are not selectors and are skipped whole.
    """
    css = strip_comments(css)
    out = []
    i = 0
    n = len(css)
    stack = []          # open preludes, innermost last
    while i < n:
        c = css[i]
        if c == "{":
            prelude = css[max(0, css.rfind("}", 0, i) + 1):i]
            prelude = prelude[max(prelude.rfind("{") + 1, 0):].strip()
            # find the matching close
            depth, j = 1, i + 1
            while j < n and depth:
                if css[j] == "{":
                    depth += 1
                elif css[j] == "}":
                    depth -= 1
                j += 1
            body = css[i + 1:j - 1]
            if prelude.startswith("@keyframes") or prelude.startswith("@-"):
                i = j
                continue
            if prelude.startswith("@"):
                out.extend(rules_declaring_inner(body, prop, origin_label,
                                                 line_base + css.count("\n", 0, i + 1)))
                i = j
                continue
            # an ordinary rule: does its OWN block (no nested braces here) set prop?
            m = re.search(r"(?<![-\w])%s\s*:([^;}]+)" % re.escape(prop), body)
            if m and "{" not in body:
                out.append({
                    "selectors": prelude,
                    "value": m.group(1).strip(),
                    "source": origin_label,
                    "line": line_base + css.count("\n", 0, i),
                })
            i = j
            continue
        i += 1
    return out


def rules_declaring_inner(css, prop, origin_label, line_base):
    return rules_declaring(css, prop, origin_label, line_base)


# --------------------------------------------------------------------------
# Selectors: specificity, and matching against an element from the markup.
# --------------------------------------------------------------------------

class Unevaluable(Exception):
    pass


COMPOUND = re.compile(
    r"""(?P<type>^[a-zA-Z][\w-]*|^\*)
      | \.(?P<cls>[\w-]+)
      | \#(?P<id>[\w-]+)
      | \[(?P<attr>[^\]]*)\]
      | ::(?P<pel>[\w-]+)
      | :(?P<pcl>[\w-]+)(?P<parens>\((?P<inner>[^()]*)\))?
    """,
    re.X,
)

# Pseudo-classes that do not depend on state or position, and that this matcher
# treats as matching. Anything else is Unevaluable rather than guessed.
STATIC_PSEUDO = {"root"}
FUNCTIONAL = {"is", "where", "not", "matches", "any"}


def split_top(s, sep):
    """Split on `sep` at paren depth 0."""
    parts, depth, cur = [], 0, ""
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == sep and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return [p.strip() for p in parts if p.strip()]


def parse_compound(tok):
    """-> (dict of requirements, specificity triple)."""
    req = {"type": None, "classes": set(), "id": None}
    a = b = c = 0
    pos = 0
    while pos < len(tok):
        m = COMPOUND.match(tok, pos)
        if not m or m.end() == pos:
            raise Unevaluable(tok)
        if m.group("type"):
            if m.group("type") != "*":
                req["type"] = m.group("type").lower()
                c += 1
        elif m.group("cls"):
            req["classes"].add(m.group("cls"))
            b += 1
        elif m.group("id"):
            req["id"] = m.group("id")
            a += 1
        elif m.group("attr") is not None:
            raise Unevaluable(tok)
        elif m.group("pel"):
            c += 1                      # ::after etc. — the origin element still matches
        elif m.group("pcl"):
            name = m.group("pcl")
            if name in FUNCTIONAL:
                inner = m.group("inner")
                if inner is None:
                    raise Unevaluable(tok)
                sub = [parse_compound_list(x) for x in split_top(inner, ",")]
                if name != "where":
                    sa, sb, sc = max((s for _, s in sub), default=(0, 0, 0))
                    a, b, c = a + sa, b + sb, c + sc
                if name in ("is", "matches", "any"):
                    req.setdefault("is", []).append([r for r, _ in sub])
                elif name == "not":
                    req.setdefault("not", []).extend(r for r, _ in sub)
            elif name in STATIC_PSEUDO:
                b += 1
            else:
                raise Unevaluable(tok)
        pos = m.end()
    return req, (a, b, c)


def parse_compound_list(sel):
    """A single compound (no combinators) — used inside :is()/:not()."""
    if re.search(r"[ >+~]", sel.strip()):
        raise Unevaluable(sel)
    return parse_compound(sel.strip())


def parse_selector(sel):
    """-> (list of (combinator, compound-req), specificity)."""
    sel = sel.strip()
    toks = re.split(r"\s*([>+~])\s*|\s+", sel)
    toks = [t for t in toks if t]
    seq, a, b, c = [], 0, 0, 0
    combi = " "
    for t in toks:
        if t in (">", "+", "~"):
            combi = t
            continue
        req, (sa, sb, sc) = parse_compound(t)
        a, b, c = a + sa, b + sb, c + sc
        seq.append((combi, req))
        combi = " "
    if not seq:
        raise Unevaluable(sel)
    return seq, (a, b, c)


def compound_matches(req, el):
    if req.get("type") and req["type"] != el["tag"]:
        return False
    if req.get("id") and req["id"] != el.get("id"):
        return False
    if not req["classes"] <= el["classes"]:
        return False
    for group in req.get("is", []):
        if not any(compound_matches(r, el) for r in group):
            return False
    for r in req.get("not", []):
        if compound_matches(r, el):
            return False
    return True


def selector_matches(seq, el, ancestors):
    """Right-to-left. Only descendant and child combinators are supported;
    a sibling combinator raises rather than guessing."""
    combi, req = seq[-1]
    if not compound_matches(req, el):
        return False
    rest = seq[:-1]
    chain = list(ancestors)
    while rest:
        combi, req = rest[-1]
        if combi == " ":
            hit = None
            for k in range(len(chain) - 1, -1, -1):
                if compound_matches(req, chain[k]):
                    hit = k
                    break
            if hit is None:
                return False
            chain = chain[:hit]
        elif combi == ">":
            if not chain or not compound_matches(req, chain[-1]):
                return False
            chain = chain[:-1]
        else:
            raise Unevaluable(combi)
        rest = rest[:-1]
    return True


# --------------------------------------------------------------------------
# Markup: every element carrying --o, with its ancestor chain.
# --------------------------------------------------------------------------

class Elements(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.found = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        el = {
            "tag": tag.lower(),
            "classes": set((d.get("class") or "").split()),
            "id": d.get("id"),
            "style": d.get("style") or "",
            "line": self.getpos()[0],
        }
        if re.search(r"(?<![-\w])--o\s*:", el["style"]):
            self.found.append((el, list(self.stack), d.get("d") or d.get("cx") or ""))
        if tag.lower() not in self.VOID:
            self.stack.append(el)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag.lower() not in self.VOID and self.stack and self.stack[-1]["tag"] == tag.lower():
            self.stack.pop()

    def handle_endtag(self, tag):
        for k in range(len(self.stack) - 1, -1, -1):
            if self.stack[k]["tag"] == tag.lower():
                del self.stack[k:]
                break


def main():
    findings = []
    html = PAGE.read_text(encoding="utf-8")

    # every transform-origin rule the page can see, in cascade order
    rules = []
    for order, path in enumerate(SHEETS):
        rules += [dict(r, order=order) for r in
                  rules_declaring(path.read_text(encoding="utf-8"), PROP, path.name)]
    for m in re.finditer(r"<style>(.*?)</style>", html, re.S):
        base = html.count("\n", 0, m.start(1)) + 1
        rules += [dict(r, order=len(SHEETS)) for r in
                  rules_declaring(m.group(1), PROP, PAGE.name + " <style>", base)]

    if not rules:
        print("grow origin: no %s declaration found at all — the parser is broken "
              "or the page stopped growing its strokes by scale." % PROP)
        return 1

    # flatten the selector lists, parsing each
    parsed = []
    for r in rules:
        for sel in split_top(r["selectors"], ","):
            try:
                seq, spec = parse_selector(sel)
            except Unevaluable as e:
                findings.append(
                    "%s:%d declares %s on a selector this check cannot evaluate:\n"
                    "        %s\n"
                    "    (the part it choked on: %s)\n"
                    "    A selector shape the cascade resolver does not understand is\n"
                    "    exactly where the next silent override would hide, so this is a\n"
                    "    failure rather than a skip. Teach parse_selector() the shape."
                    % (r["source"], r["line"], PROP, sel.strip(), e))
                continue
            parsed.append(dict(r, sel=sel.strip(), seq=seq, spec=spec))

    els = Elements()
    els.feed(html)
    if not els.found:
        print("grow origin: no element in %s carries a --o. Either the drawings stopped\n"
              "naming the end they grow from, or this check stopped finding them."
              % PAGE.name)
        return 1

    checked = 0
    for el, ancestors, geom in els.found:
        matching = []
        for p in parsed:
            try:
                if selector_matches(p["seq"], el, ancestors):
                    matching.append(p)
            except Unevaluable as e:
                findings.append(
                    "%s:%d uses a combinator this check cannot evaluate (%s) in:\n        %s"
                    % (p["source"], p["line"], e, p["sel"]))
        if not matching:
            findings.append(
                "%s:%d names an end to grow from (--o) and NOTHING reads it:\n"
                "        <%s class=\"%s\"> %s\n"
                "    No rule matching this element declares %s, so the stroke grows about\n"
                "    its own 0 0 whatever the markup says."
                % (PAGE.name, el["line"], el["tag"], " ".join(sorted(el["classes"])),
                   geom[:40], PROP))
            continue
        winner = max(matching, key=lambda p: (p["spec"], p["order"], p["line"]))
        checked += 1
        if "var(--o" in winner["value"].replace(" ", "").replace("var(--o", "var(--o"):
            continue
        readers = [p for p in matching if "var(--o" in p["value"].replace(" ", "")]
        detail = ""
        if readers:
            r0 = max(readers, key=lambda p: (p["spec"], p["order"], p["line"]))
            detail = ("\n    The rule that DOES read it loses the cascade:\n"
                      "        %s:%d  %s  { %s: %s }   specificity %s\n"
                      "    against\n"
                      "        %s:%d  %s  { %s: %s }   specificity %s"
                      % (r0["source"], r0["line"], r0["sel"], PROP, r0["value"], r0["spec"],
                         winner["source"], winner["line"], winner["sel"], PROP,
                         winner["value"], winner["spec"]))
        findings.append(
            "%s:%d declares --o and the browser does not use it:\n"
            "        <%s class=\"%s\"> %s\n"
            "    %s resolves to `%s`, from %s:%d.%s\n"
            "    A stroke grown by scale takes its direction from %s alone, and the two\n"
            "    directions render identically at both ends of the draw.\n"
            "    -> design-system/foundations/motion.html"
            % (PAGE.name, el["line"], el["tag"], " ".join(sorted(el["classes"])),
               geom[:40], PROP, winner["value"], winner["source"], winner["line"],
               detail, PROP))

    if findings:
        print("grow origin: %d finding(s)\n" % len(findings))
        for f in findings:
            print("  - %s\n" % f)
        return 1

    print("grow origin: %d strokes name the end they grow from, and on every one of them\n"
          "the declaration reading --o wins the cascade against %d competing %s rule(s)."
          % (checked, len(parsed), PROP))
    return 0


if __name__ == "__main__":
    sys.exit(main())
