#!/usr/bin/env python3
"""A floating control is not sealed under content it cannot paint over.

The forty-fourth check, and the third whose subject is a keyboard-and-pointer
guarantee rather than a colour or a measurement.

WHAT WENT WRONG. The hero carries one control: the switch that stops the
background loop. It is not a nicety — the loop runs 12 s and repeats forever,
which is precisely the condition WCAG 2.2.2 (level A) requires a mechanism
over, and the note in components.css says so at length. It lived inside
.cf-hero__media, first in the markup so two sibling selectors could reach the
video and the still, and it carried `z-index: 1` of its own.

.cf-hero__media is `position: absolute; z-index: 0`. That is a STACKING
CONTEXT, and a deliberate one — the note over .cf-hero__media::after banks on
it in as many words: the scrim is "below .cf-hero__body's z-index 1 by being
in the media's box at all, so no stacking order has to be stated for the
type". The seal is exactly right for artwork. It does not ask what it is
holding down. Inside that box the switch's `z-index: 1` ranked it against the
video and the scrim and nothing else; against anything OUTSIDE the box the
whole subtree is one layer at 0, under the type's 1, and no number written
inside it could have lifted the control out.

Nothing looked wrong, and that is the whole reason this ran for as long as it
did. The type has no background, so the plate went on being drawn, in full,
in the right place. What was underneath was the hit test. .cf-hero__body is
`width: fit-content`, sized to the LONGEST line the headline sets, so the h1's
box runs the full width of that column on every line — including the trailing
emptiness after the short ones. Wherever that box reaches the plate, the h1
takes the click. Measured with elementFromPoint at the plate's centre and both
of its diagonal corners, on the landing page:

      375 x 812    h1.cf-hero__title   h1.cf-hero__title   h1.cf-hero__title
      414 x 896    label.cf-hero__still        (own)       label.cf-hero__still
      768 x 1024   label.cf-hero__still        (own)       label.cf-hero__still
     1280 x 800    label.cf-hero__still        (own)       label.cf-hero__still
     1440 x 900    label.cf-hero__still        (own)       label.cf-hero__still
     2560 x 1440   label.cf-hero__still        (own)       label.cf-hero__still

375 is where it binds because that is the width at which the hero runs out of
height: min(92vh, 56rem, 100vh - banner) leaves 478.5 px for roughly 473 px of
content, the flex column stops having bottom slack, and the headline climbs to
y 84 — straight through the plate's band at 96–136. From 414 up the hero body
starts at 179 and the two boxes never meet. So the single viewport class on
which this control could not be pressed was the phone, which is also the one
where a reader is most likely to want the loop stopped. The checkbox itself
never broke: focus is not hit-testing, so a keyboard reader could always pause
the loop and a touch reader never could, on the same page, from the same
markup.

WHAT THIS KNOWS THAT A SCREENSHOT CANNOT. Every rendering of the failing state
is pixel-identical to the fixed one. The plate is drawn, the marks are drawn,
the focus ring is drawn, the hover lift still fires because hover is a
different question from a click landing on the label. The only difference is
which element is returned by a hit test at a coordinate — invisible in an
image, invisible in a diff that reads either file alone, and exactly
computable from the two of them together.

WHAT IT CHECKS, and it is the general rule rather than the one instance. For
every interactive control that FLOATS — `position: absolute` or `fixed`, so it
overlaps content instead of reserving room in the flow — work out what
actually ranks for it. If any ancestor establishes a stacking context, the
OUTERMOST one does: the whole subtree beneath it paints as a single layer at
that ancestor's z-index, and no number written on the control can lift it out.
With no such ancestor the control ranks on its own account. Then compare it
against every positioned element that could overlap it, resolved the same way.

Two ways to lose, and the fix here had to answer both:

  outranked   the content's layer sits above the control's. This is the shape
              the switch was in — sealed at 0 inside .cf-hero__media, under a
              headline at 1, with a `z-index: 1` of its own that ranked it
              against the video and nothing else.

  tied        equal z-index, broken by document order. Moving the switch out
              of the media box is only half the fix: out there at `z-index: 1`
              it would tie with .cf-hero__body, and the body comes later in the
              markup, so the headline would take the click all over again.
              Verified in the browser rather than assumed — at 375 x 812 the
              hit test returns h1.cf-hero__title with the pair untied and the
              plate at 2 makes it return the plate. Hence 2, and hence a tie
              counts as a failure here.

The declared overlay layers are exempt, and have to be. tokens.css publishes a
z-scale — --z-sticky 100, --z-nav 200, --z-overlay 300, --z-modal 400 — and an
element on it is meant to cover the page. A hero control being under the
navigation band is the design; being under the headline is the bug. Anything
resolving to 100 or above is therefore not counted as content.

The invariant, stated as the fix satisfies it: the control and the content it
can overlap resolve into the SAME stacking context, and the control outranks
it there. On the landing page that is z-index 2 on .cf-hero__still against 1
on .cf-hero__body, both direct children of .cf-hero, which is `position:
relative; z-index: auto` and so forms no context of its own (`overflow: clip`
does not form one either — only `contain: paint` and friends do, and the list
below knows the difference).

Reintroduce the bug — put the switch back inside .cf-hero__media, or drop its
z-index below the body's — and this fails.
"""

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = [
    ROOT / "design-system/assets/css/tokens.css",
    ROOT / "design-system/assets/css/base.css",
    ROOT / "design-system/assets/css/components.css",
]
PAGE_DIRS = ["design-system/patterns", "design-system/foundations", "design-system/components"]

# An element on the published z-scale is meant to cover the page. See the
# header: under the nav is the design, under the headline is the bug.
OVERLAY_FLOOR = 100

INTERACTIVE = {"a", "button", "summary", "select", "textarea"}

# Properties that make an element a stacking context on their own, with the
# values that do NOT. `overflow` is deliberately absent: it makes a block
# formatting context, never a stacking one, and the hero's `overflow: clip`
# is exactly the near-miss this list has to get right.
CONTEXT_PROPS = {
    "opacity": lambda v: _num(v) is not None and _num(v) < 1,
    "transform": lambda v: v != "none",
    "rotate": lambda v: v != "none",
    "scale": lambda v: v != "none",
    "translate": lambda v: v != "none",
    "filter": lambda v: v != "none",
    "backdrop-filter": lambda v: v != "none",
    "-webkit-backdrop-filter": lambda v: v != "none",
    "perspective": lambda v: v != "none",
    "clip-path": lambda v: v != "none",
    "mask-image": lambda v: v != "none",
    "-webkit-mask-image": lambda v: v != "none",
    "mix-blend-mode": lambda v: v != "normal",
    "isolation": lambda v: v == "isolate",
    "contain": lambda v: any(k in v.split() for k in ("paint", "layout", "strict", "content")),
    "content-visibility": lambda v: v in ("auto", "hidden"),
    "will-change": lambda v: any(
        k.strip() in ("transform", "opacity", "filter", "perspective", "rotate", "scale", "translate")
        for k in v.split(",")
    ),
}


def _num(v):
    try:
        return float(v.strip())
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------- CSS reading

def strip_comments(text):
    return re.sub(r"/\*.*?\*/", "", text, flags=re.S)


def read_tokens():
    """The --z-* scale, so an overlay can be told from content."""
    text = strip_comments((ROOT / "design-system/assets/css/tokens.css").read_text(encoding="utf-8"))
    return {m.group(1): m.group(2).strip() for m in re.finditer(r"(--z-[\w-]+)\s*:\s*([^;]+);", text)}


def top_level_rules(text):
    """(selector, body) for rules outside every at-rule, in source order.

    AT-RULE BODIES ARE SKIPPED, and that is the check's scope rather than a
    shortcut. The invariant is about the page as it ships by default. Read
    flat, the LAST rule for a class wins — and the last rule for
    .cf-hero__still in this stylesheet is the one inside
    @media (prefers-reduced-motion: reduce) that sets `display: none`. Folding
    that in makes the control look absent and the check falls silent on
    exactly the page it exists for. It cost this script one failed
    reintroduction to find out.

    A control genuinely removed under a condition is not a control under that
    condition, so dropping those blocks is also the correct reading. What it
    does give up is a seal or a rank introduced only inside a width query;
    every declaration this check needs is written unconditionally today, and
    a conditional one would be missed rather than misread.
    """
    out, i, n = [], 0, len(text)
    while i < n:
        brace = text.find("{", i)
        if brace == -1:
            break
        prelude = text[i:brace].strip()
        if prelude.startswith("@"):
            # skip the whole at-rule body, however deeply it nests
            depth, j = 1, brace + 1
            while j < n and depth:
                if text[j] == "{":
                    depth += 1
                elif text[j] == "}":
                    depth -= 1
                j += 1
            i = j
            continue
        close = text.find("}", brace)
        if close == -1:
            break
        out.append((prelude, text[brace + 1:close]))
        i = close + 1
    return out


def read_rules():
    """Declarations per simple class selector, later wins.

    Crude on purpose: this check only ever asks about a handful of properties
    on single-class selectors, and every rule it needs is written that way.
    A selector it cannot read simply contributes nothing, which can only make
    the check quieter, never wrong in the direction that matters.
    """
    decls = {}
    for path in CSS:
        text = strip_comments(path.read_text(encoding="utf-8"))
        for sel, body in top_level_rules(text):
            if not sel:
                continue
            for one in sel.split(","):
                one = one.strip()
                m = re.fullmatch(r"\.([\w-]+)", one)
                if not m:
                    continue
                bucket = decls.setdefault(m.group(1), {})
                for prop, val in re.findall(r"([-\w]+)\s*:\s*([^;]+)", body):
                    bucket[prop.strip()] = val.strip()
    return decls


def resolve_z(value, tokens):
    """A z-index literal, or one read through var(--z-*)."""
    if value is None:
        return None
    value = value.strip()
    m = re.fullmatch(r"var\(\s*(--[\w-]+)\s*(?:,[^)]*)?\)", value)
    if m:
        value = tokens.get(m.group(1), "")
    if value == "auto":
        return "auto"
    try:
        return int(float(value))
    except ValueError:
        return None


def props_for(classes, decls):
    """Merged declarations for an element, in stylesheet order per class."""
    out = {}
    for c in classes:
        out.update(decls.get(c, {}))
    return out


def forms_context(props, z):
    """Does this element establish a stacking context, and why."""
    reasons = []
    pos = props.get("position", "static")
    if pos in ("absolute", "relative", "sticky", "fixed") and isinstance(z, int):
        reasons.append(f"position: {pos} with z-index: {z}")
    if pos in ("fixed", "sticky"):
        reasons.append(f"position: {pos}")
    for prop, test in CONTEXT_PROPS.items():
        val = props.get(prop)
        if val is not None and test(val):
            reasons.append(f"{prop}: {val}")
    return reasons


# --------------------------------------------------------------- HTML reading

class Tree(HTMLParser):
    """Just enough DOM: tag, classes, children, parent, document order."""

    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
            "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = {"tag": "#root", "classes": [], "attrs": {}, "kids": [],
                     "parent": None, "order": 0}
        self.stack = [self.root]
        self.n = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.n += 1
        node = {"tag": tag, "classes": (a.get("class") or "").split(),
                "attrs": a, "kids": [], "parent": self.stack[-1], "order": self.n}
        self.stack[-1]["kids"].append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i]["tag"] == tag:
                del self.stack[i:]
                return


def walk(node):
    yield node
    for k in node["kids"]:
        yield from walk(k)


def label(node):
    return node["tag"] + ("." + ".".join(node["classes"]) if node["classes"] else "")


def is_control(node, props):
    if node["tag"] in INTERACTIVE:
        return True
    if node["tag"] == "input" and node["attrs"].get("type") != "hidden":
        return True
    if node["tag"] == "label" and "for" in node["attrs"]:
        return True
    ti = node["attrs"].get("tabindex")
    return ti is not None and ti != "-1"


# ------------------------------------------------------------------ the check

def ranking_element(node, decls, tokens):
    """What actually ranks for this node, and at what z.

    A node inside a stacking context does not rank against the page — its
    OUTERMOST context-forming ancestor does, and the whole subtree paints as
    that one layer. So walk all the way up and keep the last seal found. With
    no seal anywhere the node ranks on its own account, which is the state the
    fix puts the hero's switch into.
    """
    who, why = node, []
    p = node["parent"]
    while p is not None and p["tag"] != "#root":
        pp = props_for(p["classes"], decls)
        reasons = forms_context(pp, resolve_z(pp.get("z-index"), tokens))
        if reasons:
            who, why = p, reasons
        p = p["parent"]
    props = props_for(who["classes"], decls)
    z = resolve_z(props.get("z-index"), tokens)
    return who, (0 if not isinstance(z, int) else z), why


def audit_page(path, decls, tokens):
    tree = Tree()
    tree.feed(path.read_text(encoding="utf-8"))
    findings = []

    for node in walk(tree.root):
        props = props_for(node["classes"], decls)
        if not is_control(node, props):
            continue
        if props.get("position") not in ("absolute", "fixed"):
            continue  # in the flow: it reserves its own room, nothing can sit on it
        if props.get("display") == "none" or props.get("pointer-events") == "none":
            continue  # not hit-testable by design — the hero's own input is one

        z_self = resolve_z(props.get("z-index"), tokens)
        rank_el, rank_z, seal_why = ranking_element(node, decls, tokens)
        if rank_z >= OVERLAY_FLOOR:
            continue  # the control rides a declared overlay layer; it is on top by design

        over = []
        for other in walk(tree.root):
            if other["tag"] == "#root" or other is node:
                continue
            op = props_for(other["classes"], decls)
            if op.get("position", "static") == "static":
                continue
            if op.get("pointer-events") == "none" or op.get("display") == "none":
                continue  # takes no click, so it cannot take this one
            if not isinstance(resolve_z(op.get("z-index"), tokens), int):
                continue
            o_el, o_z, _ = ranking_element(other, decls, tokens)
            if o_el is rank_el:
                continue  # same layer: they rank inside it, not against each other
            if o_z >= OVERLAY_FLOOR:
                continue  # a declared overlay is meant to cover the page
            # Does it rank at or above the control? A tie is a loss for the
            # control: equal z-index is broken by document order, and the
            # content that overlaps it comes later on every page here.
            if o_z < rank_z or (o_z == rank_z and o_el["order"] < rank_el["order"]):
                continue
            # only content that can actually reach it: a shared ancestor near
            # enough that the two boxes are laid out over one another
            if _nearest_shared(other, node) is None:
                continue
            over.append((other, o_z, o_el))

        if over:
            findings.append({
                "control": label(node), "z": z_self,
                "ranks_as": None if rank_el is node else label(rank_el),
                "rank_z": rank_z, "why": seal_why,
                "over": [(label(o), oz, None if oe is o else label(oe)) for o, oz, oe in over],
            })
    return findings


def _ancestors(node):
    out, p = [], node["parent"]
    while p is not None:
        out.append(p)
        p = p["parent"]
    return out


def _nearest_shared(a, b):
    """The common ancestor, if the two are laid out close enough to meet.

    Both boxes have to live under one positioned or sectioning ancestor for
    an overlap to be possible at all. Two controls in different sections of
    a long page cannot reach each other however their z-indices rank.
    """
    anc_a = set(id(x) for x in _ancestors(a))
    p = b
    while p is not None:
        if id(p) in anc_a and p["tag"] not in ("#root", "body", "html"):
            return p
        p = p["parent"]
    return None


def main():
    decls = read_rules()
    tokens = read_tokens()

    pages = []
    for d in PAGE_DIRS:
        pages.extend(sorted((ROOT / d).glob("*.html")))

    failures, checked, floating = [], 0, 0
    for path in pages:
        found = audit_page(path, decls, tokens)
        checked += 1
        for f in found:
            floating += 1
            over = "\n".join(
                f"      {name}  z-index {z}" + (f"  (ranks as {via})" if via else "")
                for name, z, via in f["over"])
            if f["ranks_as"]:
                how = (f"    sealed by  {f['ranks_as']}  ({'; '.join(f['why'])})\n"
                       f"    so it ranks at {f['rank_z']}, not at its own {f['z']}: the seal is a\n"
                       "    stacking context, and the whole subtree under it paints as one\n"
                       "    layer. No number written on the control can lift it out.\n")
            else:
                how = (f"    ranks at {f['rank_z']} on its own account, and loses the tie: equal\n"
                       "    z-index is broken by document order, and the content below comes\n"
                       "    later in the markup.\n")
            failures.append(
                f"{path.relative_to(ROOT)}: {f['control']} is a control that floats "
                "over content, and the content is painted over it.\n"
                f"    control    {f['control']}  z-index {f['z']}\n"
                f"{how}"
                f"    painted over by:\n{over}\n"
                "    Wherever the two boxes meet, the content takes the click and the\n"
                "    control cannot be pressed — while still being drawn, in full, in\n"
                "    the right place, with its hover and its focus ring intact. Give\n"
                "    the control a stacking position it can win from: out of any seal\n"
                "    that content is not also inside, and above that content there.")

    if failures:
        print("check-pointer-reach: a control that cannot be pressed is not a "
              "control, and a screenshot of one looks exactly like a working one.\n")
        for f in failures:
            print("  " + f + "\n")
        sys.exit(1)

    print(f"check-pointer-reach: {checked} page(s) read; every floating control "
          "outranks the content it overlaps — none sealed beneath it, none tied "
          "with it.")


if __name__ == "__main__":
    main()
