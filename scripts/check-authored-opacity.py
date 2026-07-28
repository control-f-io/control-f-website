#!/usr/bin/env python3
"""An authored opacity is only authored if nothing outranks it.

The seventy-second check, and the third at a value that is stated in one place
and overruled from another. check-anchor-position-cascade.py holds the case
where the winner is a later rule at equal specificity; this one holds the case
where the winner is not a rule at all. A CSS animation resolves in the ANIMATION
origin, which sits above the whole author origin, and an SVG presentation
attribute sits at the very BOTTOM of the author origin -- below every selector,
below the element's own style attribute. Between the two there is no contest and
no warning: the keyframe simply is the value, and the number in the markup is
decoration on a tag.

WHAT WAS WRONG, and it had been wrong since the statement first animated.
`@keyframes cf-iso-fade` ended `to { opacity: 1 }`, and `.cf-iso__ghost` and
`.cf-stmt-sensor` both run it with `animation-fill-mode: both` -- which fills
the endpoint outside the range in both directions, so the override was total at
every scroll position rather than only during the fade. Every opacity those two
selectors authored was dead:

    the lattice     opacity=".26"   rendered 1     one element, 3.8x too strong
    the sensors     opacity="0.1" … "0.7"          145 elements, up to 10x

Seven authored intensities across the field, one rendered value. Measured on the
render at 1440 x 900 at scroll 1225, where the field is at its peak: 145
sensors, `[...new Set(computed)]` == `[1]`. The markup's own note says "which
one a sensor gets is its own intensity; radius and opacity do the rest" -- and
the opacity half of that sentence had never reached a pixel, so a field built to
read as instruments of differing strength rendered as 145 identical ones.

WHY NOBODY SAW IT, which is the reason this is a script and not a review note.
A pale glow at 0.3 and the same glow at 1.0 are both "a pale glow"; a dotted
lattice at .26 and the same lattice at 1 are both "a dotted lattice". Nothing
renders wrong. It surfaces only when something has to be READ against it -- the
root's numerals, superimposed on the field -- and then it surfaces as "messy"
rather than as a number. At 1440 x 900 the darkest pixel inside the "12 480"
label's box was luminance 0.0341 against 0.0648 for the numeral's own ink: the
ground was 1.37:1 from the figure standing on it. At the authored .26 that dash
renders 0.339 and the separation is 3.39:1.

THE RULE THIS HOLDS.

    An element may state its own opacity, or it may run a keyframe that sets
    one, and if it does both then the keyframe must read the element's value
    through a custom property. A literal endpoint in a keyframe that reaches an
    element with an opacity of its own is that element's opacity, deleted.

Which is what `to { opacity: var(--iso-rest, 1) }` buys: the fallback keeps the
six parts that rest at full strength saying nothing, and the two that do not say
it once, in the place the value already lived.

ZERO IS NOT AN OVERRIDE. A keyframe endpoint of literal `0` is an act -- a part
leaving, a field collapsing -- not a claim about where a part rests, and
`cf-stmt-scatter` and `cf-stmt-collapse` are exactly that. Only non-zero
literals are findings.

WHAT IT ALSO CATCHES, both directions of the rot:
  - an `opacity` presentation attribute reintroduced on an element whose opacity
    is governed by a custom property (dead the moment it is typed, and it would
    read as the source of truth to the next person);
  - a `--iso-rest` declared on an element that no opacity keyframe reaches, so
    the property is inert.

MATCHING IS BY THE SELECTOR'S RIGHTMOST COMPOUND, and deliberately loose: a
selector's last compound must be made only of classes the element carries. That
over-matches (it ignores ancestors), which for this check is the safe direction
-- it can call an element governed when it is not, and so report a finding that
needs a human, but it cannot miss an element that a keyframe genuinely reaches.

    python3 scripts/check-authored-opacity.py       # check, exit 1 on a finding
    python3 scripts/check-authored-opacity.py -v    # print every pairing
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHIPPING_CSS = [
    ROOT / "design-system" / "assets" / "css" / "tokens.css",
    ROOT / "design-system" / "assets" / "css" / "base.css",
    ROOT / "design-system" / "assets" / "css" / "components.css",
]
SHIPPING_HTML = sorted((ROOT / "design-system").rglob("*.html"))

COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
STYLE_RE = re.compile(r"<style\b[^>]*>(.*?)</style>", re.S | re.I)
KEYFRAMES_RE = re.compile(r"@keyframes\s+([\w-]+)\s*\{")
OPACITY_RE = re.compile(r"(?:^|[;{\s])opacity\s*:\s*([^;}]+)", re.I)
ANIM_NAME_RE = re.compile(r"(?:^|;)\s*animation-name\s*:\s*([^;}]+)", re.I)
ANIM_SHORT_RE = re.compile(r"(?:^|;)\s*animation\s*:\s*([^;}]+)", re.I)
VAR_RE = re.compile(r"^var\(\s*(--[\w-]+)\s*(?:,\s*(.*?)\s*)?\)$", re.S)
TAG_RE = re.compile(r"<(\w[\w-]*)\b([^>]*)>")
CLASS_RE = re.compile(r'class="([^"]*)"')
ATTR_OPACITY_RE = re.compile(r'\bopacity="([^"]*)"')
STYLE_ATTR_RE = re.compile(r'style="([^"]*)"')

# Keyframe timing keywords, so `animation: 2s cf-thing linear` yields the name.
ANIM_KEYWORDS = {
    "none", "normal", "reverse", "alternate", "alternate-reverse", "forwards",
    "backwards", "both", "running", "paused", "infinite", "linear", "ease",
    "ease-in", "ease-out", "ease-in-out", "step-start", "step-end", "auto",
}


def strip_comments(css):
    return COMMENT_RE.sub(" ", css)


def normalise(sel):
    s = " ".join(sel.split())
    return re.sub(r"\s*([>+~])\s*", r" \1 ", s)


def parse_blocks(css):
    """[(selector_list, declarations)] for every real declaration block.

    A hand-rolled brace walker, stdlib only, like every other script here. Only
    blocks whose body has no nested block are returned, which is what a
    declaration block is; @keyframes bodies are collected separately.
    """
    blocks, i, n, buf = [], 0, len(css), []
    while i < n:
        c = css[i]
        if c == "{":
            head = "".join(buf).strip()
            buf = []
            depth, j = 1, i + 1
            while j < n and depth:
                if css[j] == "{":
                    depth += 1
                elif css[j] == "}":
                    depth -= 1
                j += 1
            body = css[i + 1:j - 1]
            if "{" not in body and not head.startswith("@"):
                blocks.append(([normalise(s) for s in head.split(",") if s.strip()], body))
                i = j
                continue
            i += 1
            continue
        if c == "}":
            buf = []
            i += 1
            continue
        buf.append(c)
        i += 1
    return blocks


def parse_keyframes(css):
    """name -> [opacity value, ...] for every keyframe that sets one."""
    out = {}
    for m in KEYFRAMES_RE.finditer(css):
        name, i, depth = m.group(1), m.end(), 1
        while i < len(css) and depth:
            if css[i] == "{":
                depth += 1
            elif css[i] == "}":
                depth -= 1
            i += 1
        vals = [v.strip() for v in OPACITY_RE.findall(css[m.end():i - 1])]
        if vals:
            out[name] = vals
    return out


def animation_names(decls):
    names = []
    for m in ANIM_NAME_RE.finditer(decls):
        names += [t.strip() for t in m.group(1).split(",")]
    for m in ANIM_SHORT_RE.finditer(decls):
        for part in m.group(1).split(","):
            for tok in part.split():
                tok = tok.strip()
                if (tok and tok.lower() not in ANIM_KEYWORDS
                        and not re.match(r"^[-\d.]+m?s$|^[\d.]+$|^\w+\(", tok)):
                    names.append(tok)
    return [n for n in names if n and n.lower() != "none"]


def rightmost_classes(selector):
    """The classes of the selector's last compound, or None if it has none."""
    last = re.split(r"\s+(?:[>+~]\s+)?", selector.strip())[-1]
    if re.search(r"::?[\w-]+\(", last):          # a functional pseudo -- skip
        last = re.sub(r"::?[\w-]+\([^)]*\)", "", last)
    classes = set(re.findall(r"\.([\w-]+)", last))
    return classes or None


def literal_opacity(value):
    """The value as a float when it is a bare number, else None."""
    v = value.strip()
    try:
        return float(v)
    except ValueError:
        return None


def read_var(value):
    """(property, fallback) when the value is a single var(), else (None, None)."""
    m = VAR_RE.match(value.strip())
    return (m.group(1), m.group(2)) if m else (None, None)


def collect_css(verbose_notes):
    """(keyframes, [(classes, keyframe_names)], [(classes, opacity_value)],
        {property names declared by a rule keyed on classes})"""
    keyframes, animated, declared, props = {}, [], [], {}
    sources = [(p.name, p.read_text(encoding="utf-8")) for p in SHIPPING_CSS]
    for p in SHIPPING_HTML:
        for m in STYLE_RE.finditer(p.read_text(encoding="utf-8")):
            sources.append((p.name, m.group(1)))
    for label, raw in sources:
        css = strip_comments(raw)
        keyframes.update(parse_keyframes(css))
        for sels, decls in parse_blocks(css):
            names = animation_names(decls)
            ops = [v.strip() for v in OPACITY_RE.findall(decls)]
            custom = set(re.findall(r"(--[\w-]+)\s*:", decls))
            for sel in sels:
                cls = rightmost_classes(sel)
                if cls is None:
                    continue
                if names:
                    animated.append((cls, names, sel, label))
                for op in ops:
                    declared.append((cls, op, sel, label))
                for c in custom:
                    props.setdefault(c, []).append(cls)
    return keyframes, animated, declared, props


def collect_markup():
    """Every shipping element that states an opacity, by attribute or property."""
    attr, custom = [], []
    for p in SHIPPING_HTML:
        text = p.read_text(encoding="utf-8")
        rel = p.relative_to(ROOT)
        for m in TAG_RE.finditer(text):
            tag, attrs = m.group(1), m.group(2)
            cm = CLASS_RE.search(attrs)
            if not cm:
                continue
            classes = set(cm.group(1).split())
            line = text.count("\n", 0, m.start()) + 1
            om = ATTR_OPACITY_RE.search(attrs)
            if om:
                attr.append((rel, line, tag, classes, om.group(1)))
            sm = STYLE_ATTR_RE.search(attrs)
            if sm:
                for prop in re.findall(r"(--[\w-]+)\s*:", sm.group(1)):
                    custom.append((rel, line, tag, classes, prop))
    return attr, custom


def keyframes_reaching(classes, animated, keyframes):
    """[(keyframe name, values, selector)] for every opacity keyframe that can
    apply to an element carrying `classes`."""
    hits = []
    for cls, names, sel, _label in animated:
        if not cls <= classes:
            continue
        for n in names:
            if n in keyframes:
                hits.append((n, keyframes[n], sel))
    return hits


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    keyframes, animated, declared, props = collect_css([])
    attr_elems, custom_elems = collect_markup()
    findings, pairings, governed = [], [], set()

    def endpoints(values):
        """(non-zero literals, custom properties read) across a keyframe."""
        lits, reads = [], []
        for v in values:
            lit = literal_opacity(v)
            if lit is not None:
                if lit != 0:
                    lits.append(lit)
                continue
            prop, fallback = read_var(v)
            if prop:
                reads.append(prop)
            else:
                lits.append(v)          # a value this check cannot resolve
        return lits, reads

    # 1. Markup that states an opacity as a presentation attribute.
    for rel, line, tag, classes, value in attr_elems:
        for name, values, sel in keyframes_reaching(classes, animated, keyframes):
            lits, reads = endpoints(values)
            pairings.append(f"{rel}:{line} <{tag} opacity=\"{value}\"> ← @keyframes {name}")
            if lits:
                findings.append(
                    f"{rel}:{line}: <{tag} class=\"{' '.join(sorted(classes))}\"> states "
                    f"opacity=\"{value}\", and `{sel}` runs @keyframes {name}, which sets "
                    f"opacity to {', '.join(str(x) for x in lits)}. An animation outranks a "
                    f"presentation attribute, so the authored value never renders. Move it "
                    f"to the custom property the keyframe reads.")
            elif reads:
                findings.append(
                    f"{rel}:{line}: <{tag} class=\"{' '.join(sorted(classes))}\"> states "
                    f"opacity=\"{value}\", but `{sel}`'s opacity is governed by "
                    f"{', '.join(reads)} via @keyframes {name}. The attribute is dead the "
                    f"moment it is typed and reads as the source of truth. Delete it.")

    # 2. CSS that states an opacity on a selector that also animates one.
    for cls, value, sel, label in declared:
        lit = literal_opacity(value)
        prop, _fb = read_var(value)
        if lit is None and prop is None:
            continue
        for name, values, asel in keyframes_reaching(cls, animated, keyframes):
            lits, reads = endpoints(values)
            if prop:
                governed.add(prop)
            pairings.append(f"{label} `{sel}` opacity:{value} ← @keyframes {name}")
            if lits and (lit is None or lit != 0):
                findings.append(
                    f"{label}: `{sel}` declares opacity: {value}, and `{asel}` runs "
                    f"@keyframes {name}, which sets opacity to "
                    f"{', '.join(str(x) for x in lits)}. The animation origin wins, so the "
                    f"declaration never renders. Route the keyframe's endpoint through a "
                    f"custom property instead of a literal.")

    # 3. A resting property declared in markup that nothing reaching this
    #    element reads. The property is only meaningful where a keyframe that
    #    ACTUALLY APPLIES here resolves its endpoint through it -- an element
    #    that runs a different opacity keyframe, or none, states an intensity
    #    that renders as nothing. Deliberately not softened by whether the
    #    property is read somewhere else on the page: somewhere else is the
    #    whole failure this file is about.
    read_anywhere = set()
    for values in keyframes.values():
        for v in values:
            prop, _fb = read_var(v)
            if prop:
                read_anywhere.add(prop)
    for rel, line, tag, classes, prop in custom_elems:
        if prop not in read_anywhere:
            continue
        hits = keyframes_reaching(classes, animated, keyframes)
        if any(prop in endpoints(values)[1] for _n, values, _s in hits):
            continue
        reached = ", ".join(sorted({n for n, _v, _s in hits})) or "no opacity keyframe"
        findings.append(
            f"{rel}:{line}: <{tag} class=\"{' '.join(sorted(classes))}\"> sets {prop}, "
            f"which is what an opacity keyframe reads its endpoint from — but what "
            f"reaches this element is {reached}, and that does not read {prop}. The "
            f"property is inert: the intensity it states renders as nothing.")

    if not pairings:
        print("authored opacity: nothing on the shipping surface both states an "
              "opacity and animates one — the scan went stale")
        return 1

    if args.verbose:
        for p in sorted(set(pairings)):
            print(f"  {p}")
        print(f"  keyframes that set opacity: {', '.join(sorted(keyframes))}")

    if findings:
        print(f"\nauthored opacity: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1

    print(f"authored opacity OK — {len(set(pairings))} element/keyframe pairing(s) across "
          f"{len(attr_elems)} attribute(s) and {len(declared)} declaration(s), and every "
          f"opacity a shipping element states is one the animation origin reads rather "
          f"than replaces")
    return 0


if __name__ == "__main__":
    sys.exit(main())
