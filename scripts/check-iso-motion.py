#!/usr/bin/env python3
"""Enforce the isometric assembly's invariants.

foundations/motion.html and the README both state a set of rules that hold the
illustrations to the designer's drawing, and both admit in prose that nothing
enforces them. The README's own section is called "Redrawing an illustration:
four things that vanish quietly" — four values that a rebuild or a re-export
drops without anything rendering wrong. A rule stated in prose is not a rule
that is enforced, and each of these has already broken at least once:

  --iso-travel     is in viewBox units, so it means a different distance in
                   every frame. Nothing tied the literals to the viewBox they
                   were derived from. Four objects were recropped within an
                   hour of their values being written and arrived from the
                   wrong distance; the statement figure's value was scoped to
                   one page's stylesheet and the second copy of the same
                   drawing missed it entirely.
  --iso-orbit-travel  is in SCREEN pixels under non-scaling-stroke, so it has
                   to be a whole multiple of the dash period or every orbit
                   settles off the phase the source vector drew.
  pathLength="1"   is what makes the line-drawing linear. Without it the dash
                   maths is in path units and the draw finishes early.

The fourth of the README's four is the oklab waypoint, and it is deliberately
NOT here: scripts/check-gradient-family.py already recomputes that waypoint's
offset and its colour from the oklab path, which is strictly the stronger
claim. Two scripts asserting one invariant to two standards is the drift these
scripts exist to stop.

Plus three structural rules the same pages state: an orbit is a ghost that also
turns, so it must carry both classes; an object carries one lime-gradient
element, because lime is light and a second source says the object is lit from
two places; and every scroll-driven block must be scoped to `screen`, because a
paged medium has no scroll and a `both`-filled animation then holds its `from`
keyframe onto the paper.

None of these can be seen in a screenshot. All of them can be counted.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-iso-motion.py
"""

import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
CSS = DS / "assets" / "css"

# Every .cf-iso in the tree, prototypes included. This boundary is deliberately
# wider than check-spacing-scale.py's, and the reason is what is being checked:
# that script measures the SHIPPING stylesheets, so a prototype's own engine is
# out of scope by definition. These are facts about DRAWINGS — a recropped
# viewBox is as wrong in a motion study as it is on a pattern page, and the
# expertise objects exist in both files with the same literals in both.
PAGES = sorted(p for p in DS.rglob("*.html"))

# The token's default, for a drawing on the 640-unit frame.
TRAVEL_DEFAULT = 16.0

# viewBox width / 40 — 2.5 % of the drawing, the ratio the system holds
# constant rather than the number. → foundations/motion.html#travel
TRAVEL_DIVISOR = 40

# Written to two decimals at the call site (17.14, 11.94, 16.42), so compare
# at that precision rather than exactly.
TRAVEL_TOLERANCE = 0.005

# HTML elements that never have an end tag. Without these the ancestor stack
# below unwinds one element too far on the first <meta> in a document.
VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}



class IsoFinder(HTMLParser):
    """Collect every <svg class="cf-iso">, its frame, its own --iso-travel and
    the classes of every element it sits inside.

    The ancestor classes are what makes a CSS-side override resolvable without
    a CSS engine: the two overrides in the system are single-class descendant
    selectors, so "is one of my ancestors carrying this class" is the whole
    cascade this check needs to model.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # [(tag, frozenset(classes))]
        self.figures = []        # dicts, one per .cf-iso svg
        self.open_svg = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = set((a.get("class") or "").split())
        if tag == "svg" and "cf-iso" in classes:
            vb = (a.get("viewBox") or a.get("viewbox") or "").split()
            inline = re.search(r"--iso-travel:\s*([\d.]+)", a.get("style") or "")
            self.open_svg = {
                "line": self.getpos()[0],
                "width": float(vb[2]) if len(vb) == 4 else None,
                "inline_travel": float(inline.group(1)) if inline else None,
                "ancestors": {c for _, cs in self.stack for c in cs},
                "parts": set(),
                "depth": len(self.stack),
            }
            self.figures.append(self.open_svg)
        if self.open_svg is not None:
            self.open_svg["parts"].update(
                c for c in classes if c.startswith("cf-iso__")
            )
        if tag not in VOID:
            self.stack.append((tag, classes))

    def handle_startendtag(self, tag, attrs):
        if self.open_svg is not None:
            a = dict(attrs)
            self.open_svg["parts"].update(
                c for c in (a.get("class") or "").split() if c.startswith("cf-iso__")
            )

    def handle_endtag(self, tag):
        # Tolerant unwind: pop back to the matching open tag if there is one,
        # so a stray or implied close cannot corrupt the ancestor set.
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break
        if tag == "svg":
            self.open_svg = None


def strip_comments(css):
    """Blank comments out in place, keeping their newlines, so every line
    number this script reports is the line number in the file the reader will
    open. Dropping the comment text outright shifts everything after the first
    one — measured on components.css, by about 1,700 lines."""
    return re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), css, flags=re.S)


def travel_overrides():
    """Rules of the form `.some-class .cf-iso { --iso-travel: N }` in the
    shipping CSS, as {class: value}. These are the only shape the system uses,
    and a new shape should be added here deliberately rather than resolved by
    guesswork — a checker that half-understands the cascade is worse than one
    that says it does not."""
    text = strip_comments((CSS / "components.css").read_text())
    return {
        m.group(1): float(m.group(2))
        for m in re.finditer(
            r"\.([\w-]+)\s+\.cf-iso\s*\{[^}]*--iso-travel:\s*([\d.]+)", text
        )
    }


def token(name, text):
    m = re.search(re.escape(name) + r":\s*([^;]+);", strip_comments(text))
    return m.group(1).strip() if m else None


def scroll_blocks_missing_screen():
    """Every at-rule nesting that contains an `animation-timeline` and is not
    scoped to `screen`.

    A paged medium has no scroll, so a view timeline never advances and a
    `both`-filled animation holds its `from` keyframe onto the paper. That has
    cost this system a printed illustration and, separately, the hairline under
    the nav bar. → foundations/motion.html#scroll-driven
    """
    hits = []
    for name in ("base.css", "components.css"):
        text = strip_comments((CSS / name).read_text())
        stack = []          # preludes of the blocks currently open
        frag_start = 0
        line = 1

        def declaration(frag, at_line):
            if not frag.lstrip().startswith("animation-timeline"):
                return
            at_rules = tuple(h for h in stack if h.startswith("@"))
            media = [h for h in at_rules if h.startswith("@media")]
            if not media:
                hits.append((name, at_line, "(no @media at all)", at_rules))
            elif not any("screen" in h for h in media):
                hits.append((name, at_line, " / ".join(media), at_rules))

        for i, ch in enumerate(text):
            if ch == "\n":
                line += 1
            elif ch == "{":
                # The prelude of a block, not a declaration — which is also why
                # `@supports (animation-timeline: view())` is never counted as
                # one: it ends in `{`, and only fragments ending in `;` or `}`
                # reach declaration().
                stack.append(" ".join(text[frag_start:i].split()))
                frag_start = i + 1
            elif ch == "}":
                declaration(text[frag_start:i], line)
                if stack:
                    stack.pop()
                frag_start = i + 1
            elif ch == ";":
                declaration(text[frag_start:i], line)
                frag_start = i + 1

    # One finding per at-rule nesting, not per declaration or per rule: the
    # thing that is wrong is the @media, and the isometric assembly alone puts
    # seven animation-timeline declarations inside one of them.
    seen, out = set(), []
    for name, at_line, media, at_rules in hits:
        if (name, at_rules) in seen:
            continue
        seen.add((name, at_rules))
        out.append((name, at_line, media))
    return out


# --------------------------------------------------------------------------
# pathLength normalisation and non-scaling-stroke may not govern one stroke.
#
# This file already says it, once, about one class:
#
#     "It is the one stroke in an illustration that may not have it: the dash
#      would then be measured in screen pixels while pathLength normalises in
#      user space, and the draw finishes at 45 % of its range."
#
# components.css says it a second time about the Werte grid lines — "carry
# pathLength='1' and are deliberately NOT under .cf-iso" — and motion.html a
# third. Three statements of one rule, and the only thing enforcing any of
# them was a substring search of the .cf-iso__trace TAG, which reads the
# markup's own attribute and nothing else.
#
# The landing page's process frame then broke it from the other side: five
# hairlines carrying pathLength="1", non-scaling-stroke arriving from a CSS
# rule, and no .cf-iso__trace anywhere near it. Measured at 1440 x 900, a
# 1000 x 500 viewBox stretched to 1278 x 639, every stroke stopped at 78.2 %
# of itself and stayed there — the frame the whole pinned stage rests on was
# never a closed rectangle. Nothing in the tree noticed for as long as it
# shipped, because nothing was looking anywhere but at trace tags.
#
# So the rule is checked where it is true — on every normalised stroke in the
# tree, against every route non-scaling-stroke can reach it by: the presentation
# attribute, a style attribute, the shipping stylesheets, and the page's own
# <style> block.
# --------------------------------------------------------------------------

NSS = "non-scaling-stroke"

# Selector shapes this check models. Anything else is reported rather than
# skipped — the same standard travel_overrides() sets: a checker that half
# understands the cascade is worse than one that says it does not.
_COMPOUND = re.compile(
    r"^(?P<tag>[A-Za-z][\w-]*)?"
    r"(?P<rest>(?:\.[\w-]+|:is\([^()]*\)|:not\([^()]*\))*)$"
)
_PIECE = re.compile(r"\.([\w-]+)|:is\(([^()]*)\)|:not\(([^()]*)\)")


def parse_compound(text):
    """One compound selector as (tags, classes, excluded_classes), or None.

    `tags` is the set the element's tag must be in — from a bare tag or from
    an :is() of bare tags — or None for "any". Only the shapes the shipping
    stylesheets and the page blocks actually use are modelled.
    """
    m = _COMPOUND.match(text)
    if not m:
        return None
    tags = {m.group("tag").lower()} if m.group("tag") else None
    classes, excluded, pos = set(), set(), 0
    for piece in _PIECE.finditer(m.group("rest")):
        if piece.start() != pos:
            return None
        pos = piece.end()
        cls, is_args, not_args = piece.groups()
        if cls:
            classes.add(cls)
        elif is_args is not None:
            args = [a.strip() for a in is_args.split(",")]
            if not args or not all(re.fullmatch(r"[A-Za-z][\w-]*", a) for a in args):
                return None          # :is() of anything but bare tags
            args = {a.lower() for a in args}
            tags = args if tags is None else (tags & args)
        else:
            args = [a.strip() for a in not_args.split(",")]
            if not all(a.startswith(".") and re.fullmatch(r"[\w-]+", a[1:]) for a in args):
                return None          # :not() of anything but classes
            excluded.update(a[1:] for a in args)
    if pos != len(m.group("rest")):
        return None
    return tags, classes, excluded


def parse_selector(sel):
    """A descendant-only selector as a list of compounds, or None."""
    sel = sel.strip()
    if not sel or any(c in sel for c in ">+~[]") or "::" in sel:
        return None
    # Split on descendant combinators only — whitespace INSIDE :is(a, b) is
    # not one. Same lesson as the comma split above, one nesting level in.
    parts, depth, start = [], 0, 0
    for i, ch in enumerate(sel):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch.isspace() and depth == 0:
            parts.append(sel[start:i])
            start = i + 1
    parts.append(sel[start:])
    compounds = []
    for part in [p for p in parts if p.strip()]:
        c = parse_compound(part)
        if c is None:
            return None
        compounds.append(c)
    return compounds


def compound_matches(compound, node):
    tags, classes, excluded = compound
    tag, cls = node
    if tags is not None and tag not in tags:
        return False
    return classes <= cls and not (excluded & cls)


def selector_matches(compounds, chain):
    """chain is [(tag, classes)] from the root down to the element itself."""
    if not compound_matches(compounds[-1], chain[-1]):
        return False
    i = len(compounds) - 2
    for node in reversed(chain[:-1]):
        if i < 0:
            break
        if compound_matches(compounds[i], node):
            i -= 1
    return i < 0


def split_selector_list(text):
    """Split on commas that are not inside parentheses. `.cf-iso :is(path,
    line, rect)` is ONE selector, and splitting it naively produced two
    unmodellable halves and a bare `line` that matched every line in the
    tree — this function is the whole reason the first run of this check
    reported 137 findings against a tree with none."""
    out, depth, start = [], 0, 0
    for i, ch in enumerate(text):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == "," and depth == 0:
            out.append(text[start:i])
            start = i + 1
    out.append(text[start:])
    return [s.strip() for s in out if s.strip()]


def nss_rules(text):
    """(selector, compounds_or_None) for every rule declaring non-scaling-stroke.

    The regex matches innermost blocks only — `[^{}]+` cannot cross a brace —
    so an @media or @supports prelude is never mistaken for a selector.
    """
    out = []
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", strip_comments(text)):
        if not re.search(r"vector-effect\s*:\s*" + NSS, m.group(2)):
            continue
        for sel in split_selector_list(m.group(1)):
            if not sel.startswith("@"):
                out.append((sel, parse_selector(sel)))
    return out


class NormalisedFinder(HTMLParser):
    """Every element carrying pathLength, with its ancestor chain."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.hits = []

    def _enter(self, tag, attrs):
        a = dict(attrs)
        node = (tag.lower(), set((a.get("class") or "").split()))
        if a.get("pathLength") or a.get("pathlength"):
            self.hits.append({
                "line": self.getpos()[0],
                "chain": self.stack + [node],
                "inline": NSS in (a.get("vector-effect") or "") + (a.get("style") or ""),
                "cls": " ".join(sorted(node[1])),
            })
        return node

    def handle_starttag(self, tag, attrs):
        node = self._enter(tag, attrs)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self._enter(tag, attrs)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break


def normalised_strokes_under_non_scaling():
    findings, checked = [], 0
    shipping = [
        (name, nss_rules((CSS / name).read_text()))
        for name in ("tokens.css", "base.css", "components.css")
    ]
    for page in PAGES:
        text = page.read_text()
        rel = page.relative_to(ROOT)
        parser = NormalisedFinder()
        parser.feed(text)
        if not parser.hits:
            continue
        rules = list(shipping)
        for block in re.findall(r"<style[^>]*>(.*?)</style>", text, re.S):
            rules.append((str(rel), nss_rules(block)))
        for hit in parser.hits:
            checked += 1
            sources = []
            if hit["inline"]:
                sources.append("its own attribute")
            for origin, rs in rules:
                for sel, compounds in rs:
                    if compounds is None:
                        findings.append(
                            "%s declares vector-effect: %s on `%s`, a selector shape this\n"
                            "    check cannot model. Teach parse_selector() the shape or\n"
                            "    rewrite the rule — an unmodelled selector is an unchecked one."
                            % (origin, NSS, sel)
                        )
                        rs.remove((sel, compounds))
                        continue
                    if selector_matches(compounds, hit["chain"]):
                        sources.append("`%s` in %s" % (sel, origin))
            if sources:
                findings.append(
                    "%s:%d normalises its length with pathLength and is given %s by %s.\n"
                    "    The two cannot both govern one stroke: the dash is measured in SCREEN\n"
                    "    pixels and pathLength normalises in USER units, so the draw comes up\n"
                    "    short by exactly the render scale and stops there — for good, at every\n"
                    "    viewport. The landing page's process frame stopped at 78.2 %% of every\n"
                    "    stroke and its rectangle never closed. Drop one of the two: draw with a\n"
                    "    transform if the weight has to hold, or stroke in user units if the\n"
                    "    dash does. (%s)\n"
                    "    -> design-system/foundations/motion.html"
                    % (rel, hit["line"], NSS, " and ".join(sources),
                       hit["cls"] or "no class")
                )
    return findings, checked


def main():
    findings = []
    overrides = travel_overrides()

    # --- 1. the travel matches the frame -----------------------------------
    assembling = 0
    for page in PAGES:
        parser = IsoFinder()
        parser.feed(page.read_text())
        rel = page.relative_to(ROOT)
        for fig in parser.figures:
            if "cf-iso__scene" not in fig["parts"]:
                continue  # nothing arrives, so the distance is not consumed
            assembling += 1
            if fig["width"] is None:
                findings.append(
                    "%s:%d is a .cf-iso that assembles and has no viewBox. The travel is\n"
                    "    in viewBox units, so without one there is nothing to derive it from."
                    % (rel, fig["line"])
                )
                continue
            actual = fig["inline_travel"]
            source = "inline style"
            if actual is None:
                matched = [
                    (c, v) for c, v in overrides.items() if c in fig["ancestors"]
                ]
                if matched:
                    actual, source = matched[0][1], ".%s .cf-iso" % matched[0][0]
                else:
                    actual, source = TRAVEL_DEFAULT, "the :root default"
            want = fig["width"] / TRAVEL_DIVISOR
            if abs(actual - want) > TRAVEL_TOLERANCE:
                findings.append(
                    "%s:%d travels %g where its %g-unit frame wants %g (viewBox / %d).\n"
                    "    It is resolving from %s. The ratio is what the system holds\n"
                    "    constant, not the number: 2.5 %% of the drawing's own width, so the\n"
                    "    same object at two sizes moves the same amount relative to itself.\n"
                    "    Set --iso-travel on the svg, or key a rule on the component.\n"
                    "    -> design-system/foundations/motion.html#travel"
                    % (rel, fig["line"], actual, fig["width"], want, TRAVEL_DIVISOR, source)
                )

    # --- 2. the orbit settles on the phase the designer drew ----------------
    tokens = (CSS / "tokens.css").read_text()
    orbit = token("--iso-orbit-travel", tokens)
    dash = token("--dash-1-4", tokens)
    if orbit and dash:
        travel = float(re.sub(r"[^\d.]", "", orbit))
        period = sum(float(re.sub(r"[^\d.]", "", p)) for p in dash.split())
        if period and travel % period:
            findings.append(
                "--iso-orbit-travel is %s and the --dash-1-4 period is %gpx, which does not\n"
                "    divide it. Under non-scaling-stroke the offset is in SCREEN pixels, so a\n"
                "    dashed ring only settles on the phase the source vector drew if it stops a\n"
                "    whole number of dashes from where it started. %g leaves every orbit %.2f\n"
                "    of a dash off the drawing, for good — a drift no diff against\n"
                "    assets/source/illustrations/ could ever show.\n"
                "    -> design-system/foundations/motion.html" % (
                    orbit, period, travel, (travel % period) / period,
                )
            )

    # --- 3, 4, 5. per-page drawing rules --------------------------------
    for page in PAGES:
        text = page.read_text()
        rel = page.relative_to(ROOT)

        for m in re.finditer(r"<[a-z]+\b[^>]*\bcf-iso__trace\b[^>]*>", text):
            line = text.count("\n", 0, m.start()) + 1
            if 'pathLength="1"' not in m.group(0):
                findings.append(
                    "%s:%d is a .cf-iso__trace with no pathLength=\"1\". The draw is timed\n"
                    "    against a normalised length of 1; without it the dash maths is in the\n"
                    "    path's own units and the line finishes long before its range does."
                    % (rel, line)
                )
            if "non-scaling-stroke" in m.group(0):
                findings.append(
                    "%s:%d puts non-scaling-stroke back on a trace. It is the one stroke in an\n"
                    "    illustration that may not have it: the dash would then be measured in\n"
                    "    screen pixels while pathLength normalises in user space, and the draw\n"
                    "    finishes at 45 %% of its range. Stroke it at width 2 in user units."
                    % (rel, line)
                )

        for m in re.finditer(r'class="([^"]*\bcf-iso__orbit\b[^"]*)"', text):
            if "cf-iso__ghost" not in m.group(1):
                findings.append(
                    "%s:%d carries .cf-iso__orbit without .cf-iso__ghost. An orbit is a ghost\n"
                    "    that also turns — the shared rule that hands out animation-duration,\n"
                    "    fill-mode and --ease-out names the ghost, so an orbit without it turns\n"
                    "    on defaults and never fades up at all."
                    % (rel, text.count("\n", 0, m.start()) + 1)
                )

        for m in re.finditer(r"<svg\b[^>]*\bcf-iso\b[^>]*>", text):
            end = text.find("</svg>", m.end())
            lights = len(re.findall(r"\bcf-iso__light\b", text[m.end():end]))
            if lights > 1:
                findings.append(
                    "%s:%d has %d .cf-iso__light elements. One lime-gradient element per\n"
                    "    object: lime is light, and a second source in one drawing says the\n"
                    "    object is lit from two places.\n"
                    "    -> design-system/foundations/illustration.html"
                    % (rel, text.count("\n", 0, m.start()) + 1, lights)
                )


    # --- 6. a normalised stroke is not under non-scaling-stroke -------------
    # The rule the trace check above states for one class, checked on every
    # normalised stroke in the tree and against every route the property can
    # arrive by. Deduped against that check by line, so the trace tags it
    # already names keep their own, more specific advice.
    trace_lines = {f.split(" ", 1)[0] for f in findings}
    nss_findings, normalised = normalised_strokes_under_non_scaling()
    for f in nss_findings:
        if f.split(" ", 1)[0] not in trace_lines:
            findings.append(f)

    # --- 7. scroll-driven animation is scoped to `screen` -------------------
    for name, line, media in scroll_blocks_missing_screen():
        findings.append(
            "%s:%d puts an animation-timeline in a block that is not scoped to `screen`:\n"
            "        %s\n"
            "    A paged medium has no scroll, so the timeline never advances and a\n"
            "    both-filled animation holds its `from` keyframe onto the paper.\n"
            "    -> design-system/foundations/motion.html#scroll-driven"
            % (name, line, media)
        )

    if findings:
        print("isometric assembly: %d finding(s)\n" % len(findings))
        for f in findings:
            print("  - %s\n" % f)
        return 1

    print(
        "isometric assembly: %d assembling figures on the 2.5 %% rule, orbit travel a whole\n"
        "number of dashes, every trace normalised, every orbit a ghost, one light per object,\n"
        "%d normalised strokes clear of non-scaling-stroke, every animation-timeline scoped\n"
        "to screen."
        % (assembling, normalised)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
