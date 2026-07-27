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


    # --- 6. scroll-driven animation is scoped to `screen` -------------------
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
        "every animation-timeline scoped to screen."
        % assembling
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
