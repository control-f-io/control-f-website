#!/usr/bin/env python3
"""A pinned quarter does not open on a still.

check-pin-handover.py holds the far end of a pinned track — the last stage has
no exit, because there is no next stage to hand over to. This is the same rule
read from the other end, and it broke in the same way: quietly, in an ordinary
change, at a position every frame of which renders exactly as authored.

WHAT A QUARTER'S OPENING IS. A .cf-pin track is four quarters of `contain`. Each
quarter's plate crosses in on cf-pin-step, whose range opens three points BEFORE
the quarter and whose keyframes reach the held state at 11 % of that range — so
the plate lands at 25i + 0.41, a little after the quarter's own start. Then the
build begins. Between those two moments nothing else on the page is running: the
previous quarter is finished and gone, the next has not started, and on the FIRST
quarter there is no previous quarter at all — the entry-phase relay that drew the
frame ended at contain 0 by construction, and the stage has just taken the scroll.

So the gap between the plate landing and the first part starting is a stretch in
which the page is pinned AND nothing moves. It is the one place on a scrubbed
page where a still reads as a fault rather than as a hold: the reader is pushing
the wheel, the stage will not move because it is pinned, and the drawing will not
move because its window has not opened. What stands there is a finished empty
rectangle under a lit index.

THE FAILURE THIS IS WRITTEN AGAINST. The landing page's build head is 1.5, and
1.5 is not a free constant: the ghosts open a quarter at 0.5 and the solids
arrive one point later, into geometry that is already standing. All four cards
were given that head, and card 01 has no ghosts — no plan, no trace, eleven forms
— so its quarter opened by waiting a point for something that never comes.
Measured every 4 px at 1440 x 900 over all 235 animated parts of the page,
sampling opacity, both scale axes, fill-opacity and stroke-dashoffset, the summed
change was exactly zero from y 1626 to y 1682: 62 px, contain 0.42 -> 1.50 %.
The same 1.08 points at 1280 x 800 and 1024 x 720, because the gap is a property
of the track and not of the box. The other three quarters carried 0.09 of a
point, which is 5 px and not a still.

WHAT IS CHECKED. For every step of every .cf-pin track, the earliest head among
the part families that step ACTUALLY CONTAINS, against the plate's landing. Two
things make that a check rather than a restatement of the stylesheet:

  THE FAMILIES ARE READ OFF THE MARKUP, not assumed. Card 01's whole fault was
  that a family the head was written around is absent from one card. A check that
  took the ghost window on trust would have read 0.5 and passed.

  THE STAGE IS READ OFF THE MARKUP TOO. A build head is `A + B x stage`, and a
  card whose shallowest part is stage 1 opens 2.2 points later than one with a
  stage 0. Card 03 is exactly that card, and it is inside the ceiling only
  because its ghosts open the quarter ahead of its forms.

THE CEILING IS 0.5 OF A POINT, which is 29 px at 1440 x 900 and 25 px at the
gate floor — under a third of a wheel notch, and below what reads as a stop.
Everything both pages ship now sits at 0.09.

Both pinned tracks that have a build are held. Unsere Werte is not a build — its
stages are text rows on their own timeline with no plate to land — so it has no
opening of this shape and is deliberately absent.

WHAT IS MODELLED AND WHAT IS NOT. This resolves exactly the arithmetic the two
pages use and no more: a range head of the form `contain calc(var(--i) * 25% +
<head> + var(<stage>, 0) * <B>%)`, where <head> is a literal or a custom property
declared in the same gated block. Three forms of custom-property declaration are
understood, because three are what ship — the default on the steps container, the
conditional on `<container> .cf-pin__step:not(:has(.CLASS))` which applies to a
step whose drawing does not contain CLASS, and a per-element stagger narrowed off
the family's own selector, of which the earliest is the opener. Anything else in
a head fails loudly rather than being skipped: a head this cannot read is a head
nobody is holding.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-quarter-opening.py
"""

import argparse
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
COMPONENTS = DS / "assets" / "css" / "components.css"

# Half a point of the track. → the docstring for why this number and not a
# tighter one: it is the width of a still that is still not a stop.
CEILING = 0.5

MOTION = "-> design-system/foundations/motion.html#hold"

VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}

# The register. Every family that can open a quarter, the selector literal that
# times it, which range in that rule's list is the arrival, the class the markup
# has to carry for the family to be present, and how that element states its
# stage. Named rather than sniffed: a rule that renames itself should fail here
# rather than quietly stop being checked.
#
#   (label, selector, range index, markup class, stage source)
#
# The stage source is (custom property in the range, attribute in the markup) or
# None for a family with no stage term. The landing page writes --stage into the
# element's own style; Expertise writes data-stage and maps it to --s in the
# stylesheet. Both come out of the markup the same way.
COMPONENT_FAMILIES = [
    ("trace", ".cf-pin .cf-iso__trace", 0, "cf-iso__trace", None),
    ("nodes", ".cf-pin .cf-iso__node", 0, "cf-iso__node", None),
]

TRACKS = [
    {
        "name": "landing page · Was wir machen",
        "page": DS / "patterns" / "landing-page.html",
        "container": ".lp-proc-steps",
        "families": [
            ("plan", ".lp-proc-steps .cf-iso--build .cf-iso__ghost:not(.cf-iso__orbit)",
             0, "cf-iso__ghost", None),
            ("orbit", ".lp-proc-steps .cf-iso__orbit", 0, "cf-iso__orbit", None),
            ("build", ".lp-proc-steps .cf-iso__form", 0, "cf-iso__form", ("--stage", "--stage")),
            ("light", ".lp-proc-steps .cf-iso__light", 1, "cf-iso__light", ("--stage", "--stage")),
            ("copy", ".lp-proc-steps .cf-process__panel > *", 0, "cf-process__panel", None),
        ],
    },
    {
        "name": "expertise · Wie wir arbeiten",
        "page": DS / "patterns" / "expertise.html",
        "container": ".ex-steps",
        "families": [
            ("plan", ".ex-step .cf-iso__ghost", 0, "cf-iso__ghost", None),
            ("orbit", ".ex-step .cf-iso__orbit", 0, "cf-iso__orbit", None),
            ("build", ".ex-step .cf-iso__form", 0, "cf-iso__form", ("--s", "data-stage")),
            ("light", ".ex-step .cf-iso__light", 0, "cf-iso__light", None),
            ("copy", ".ex-step__copy > *", 0, "ex-step__copy", None),
        ],
    },
]


def strip_comments(css):
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def style_blocks(html):
    return "\n".join(m.group(1) for m in re.finditer(r"<style[^>]*>(.*?)</style>", html, re.S))


def rule_body(css, selector):
    """The declaration block of the LAST rule whose selector list is exactly this.

    Last rather than first: these stylesheets re-time a component by restating
    its selector further down, and the one that ships is the one that wins.
    """
    body = None
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        sels = [s.strip() for s in m.group(1).split(",")]
        if selector in sels:
            body = m.group(2)
    return body


def decl(body, prop):
    """One declaration out of a block, whitespace collapsed."""
    if body is None:
        return None
    out = None
    for m in re.finditer(r"(^|;)\s*" + re.escape(prop) + r"\s*:([^;]*)", body):
        out = " ".join(m.group(2).split())
    return out


def split_ranges(value):
    """An animation-range list, split on the commas that are not inside calc()."""
    out, depth, cur = [], 0, ""
    for ch in value:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    out.append(cur.strip())
    return out


def range_head(value):
    """The head half of one range — everything before the second phase keyword."""
    parts = re.split(r"\b(?=contain|cover|entry|exit)\b", value.strip())
    parts = [p.strip() for p in parts if p.strip()]
    if not parts:
        raise ValueError(f"unreadable range {value!r}")
    return parts[0]


HEAD_RE = re.compile(
    r"^contain\s+calc\(\s*var\(--i\)\s*\*\s*25%"          # the quarter
    r"\s*\+\s*(?P<head>[\d.]+%|var\(\s*--[\w-]+\s*\)\s*\*\s*1%)"   # the head: literal or var
    r"(?:\s*\+\s*var\(\s*(?P<sv>--[\w-]+)\s*(?:,\s*0\s*)?\)"
    r"\s*\*\s*(?P<b>[\d.]+)%)?"                           # optional stage term
    r"\s*\)\s*$"
)
LITERAL_RE = re.compile(r"^([\d.]+)%$")
VARHEAD_RE = re.compile(r"^var\(\s*(--[\w-]+)\s*\)\s*\*\s*1%$")


def parse_head(head, label, selector):
    """-> (constant | ('var', name), stage-var name or None, B)."""
    m = HEAD_RE.match(" ".join(head.split()))
    if not m:
        raise ValueError(f"{label}: cannot read the head of {selector!r}: {head!r}")
    lit = LITERAL_RE.match(m.group("head").strip())
    if lit:
        base = float(lit.group(1))
    else:
        vh = VARHEAD_RE.match(" ".join(m.group("head").split()))
        if not vh:
            raise ValueError(f"{label}: cannot read the head constant of {selector!r}: {head!r}")
        base = ("var", vh.group(1))
    b = float(m.group("b")) if m.group("b") else 0.0
    return base, m.group("sv"), b


# --------------------------------------------------------------------------
# the markup: what each step actually contains
# --------------------------------------------------------------------------
class Steps(HTMLParser):
    """Every .cf-pin__step, and for each the classes and stages under it."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.steps = []
        self._stack = []
        self._depth = 0
        self._open = None   # (depth, record) of the step we are inside

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = set((a.get("class") or "").split())
        if self._open is None and "cf-pin__step" in classes:
            self._open = (self._depth, {"i": self._var(a, "--i"), "classes": set(), "stages": {}})
            self.steps.append(self._open[1])
        if self._open is not None:
            rec = self._open[1]
            rec["classes"] |= classes
            for cls in classes:
                st = self._stage(a)
                if st is not None:
                    rec["stages"].setdefault(cls, []).append(st)
                else:
                    rec["stages"].setdefault(cls, []).append(0.0)
        if tag not in VOID:
            self._depth += 1
            self._stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in VOID or not self._stack:
            return
        self._stack.pop()
        self._depth -= 1
        if self._open is not None and self._depth == self._open[0]:
            self._open = None

    @staticmethod
    def _var(a, name):
        m = re.search(re.escape(name) + r"\s*:\s*([^;\"']+)", a.get("style") or "")
        return m.group(1).strip() if m else None

    @staticmethod
    def _stage(a):
        if "data-stage" in a:
            try:
                return float(a["data-stage"])
            except ValueError:
                return None
        m = re.search(r"--stage\s*:\s*([\d.]+)", a.get("style") or "")
        return float(m.group(1)) if m else None


# --------------------------------------------------------------------------
# the plate's landing
# --------------------------------------------------------------------------
def plate_landing(css):
    """Where cf-pin-step reaches the state it holds, in points of the quarter."""
    body = rule_body(css, ".cf-pin__step")
    rng = decl(body, "animation-range")
    if rng is None:
        raise ValueError(".cf-pin__step has no animation-range")
    head = range_head(split_ranges(rng)[0])
    m = re.match(r"^contain\s+calc\(\s*var\(--i\)\s*\*\s*25%\s*([+-])\s*([\d.]+)%\s*\)$",
                 " ".join(head.split()))
    if not m:
        raise ValueError(f"cannot read .cf-pin__step's head: {head!r}")
    lead = float(m.group(2)) * (1 if m.group(1) == "+" else -1)
    tail = re.search(r"contain\s+calc\(\s*\(\s*var\(--i\)\s*\+\s*1\s*\)\s*\*\s*25%"
                     r"\s*\+\s*([\d.]+)%\s*\)",
                     " ".join(split_ranges(rng)[0].split()))
    if not tail:
        raise ValueError(f"cannot read .cf-pin__step's tail: {rng!r}")
    span = 25.0 + float(tail.group(1)) - lead
    # The first keyframe stop at which the animation is in the state it then
    # holds — for cf-pin-step, `11%, 89% { opacity: 1 }`.
    km = re.search(r"@keyframes\s+cf-pin-step\s*\{", css)
    if not km:
        raise ValueError("no @keyframes cf-pin-step")
    i, depth = km.end(), 1
    while i < len(css) and depth:
        depth += (css[i] == "{") - (css[i] == "}")
        i += 1
    stops = [float(s) for s in re.findall(r"(\d+(?:\.\d+)?)%[^{}]*\{[^{}]*opacity:\s*1",
                                          css[km.end():i - 1])]
    if not stops:
        raise ValueError("cf-pin-step never reaches the held state")
    return lead + span * min(stops) / 100.0


# --------------------------------------------------------------------------
def resolve_head(base, page_css, container, selector, step):
    """A head that is a custom property, resolved for THIS step.

    Three declaration shapes ship and all three are read here:

      on the steps container            the default for every step
      `<container> .cf-pin__step
         :not(:has(.CLASS))`            applies to a step whose drawing does not
                                        contain CLASS — what lets a card with no
                                        plan open its quarter the way a plan would
      on the family's own selector,
         narrowed                       a per-element stagger, as the copy's
                                        lines carry; the step opens at the
                                        earliest of them

    Anything else raises. A head nobody here can read is a head nobody is
    holding, and that is the failure this whole script exists for.
    """
    if not isinstance(base, tuple):
        return base
    name = base[1]
    default, conditional, staggered = None, None, []
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", page_css):
        d = decl(m.group(2), name)
        if d is None:
            continue
        sel = " ".join(m.group(1).split())
        if sel == container:
            default = float(d)
            continue
        cond = re.match(re.escape(container) + r"\s+\.cf-pin__step:not\(:has\(\.([\w-]+)\)\)$", sel)
        if cond:
            if cond.group(1) not in step["classes"]:
                conditional = float(d)
            continue
        if sel.startswith(selector):
            staggered.append(float(d))
            continue
        raise ValueError(f"{name} is declared on a selector this cannot read: {sel!r}")
    if staggered:
        return min(staggered)
    if conditional is not None:
        return conditional
    if default is None:
        raise ValueError(f"{name} is used in a range head and never declared")
    return default


def earliest(track, page_css, comp_css, step):
    """The first thing this step puts on the stage, in points of its quarter."""
    best, who = None, None
    for label, selector, idx, cls, stage_src in track["families"] + COMPONENT_FAMILIES:
        css = comp_css if selector.startswith(".cf-pin ") else page_css
        body = rule_body(css, selector)
        if body is None:
            raise ValueError(f"{track['name']}: no rule for {selector!r}")
        rng = decl(body, "animation-range")
        if rng is None:
            raise ValueError(f"{track['name']}: {selector!r} has no animation-range")
        ranges = split_ranges(rng)
        if idx >= len(ranges):
            raise ValueError(f"{track['name']}: {selector!r} has no range {idx}")
        base, sv, b = parse_head(range_head(ranges[idx]), track["name"], selector)
        if cls not in step["classes"]:
            continue
        head = resolve_head(base, page_css, track["container"], selector, step)
        if stage_src is None:
            stage = 0.0
        elif stage_src[1] is None:
            # A stage carried by the stylesheet rather than the markup — the
            # copy's per-line stagger. The earliest line is the earliest value.
            vals = [float(v) for v in re.findall(
                re.escape(stage_src[0]) + r"\s*:\s*([\d.]+)", page_css)]
            if not vals:
                raise ValueError(f"{track['name']}: {stage_src[0]} is never declared")
            stage = min(vals)
        else:
            stage = min(step["stages"].get(cls, [0.0]))
        h = head + b * stage
        if best is None or h < best:
            best, who = h, label
    return best, who


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    comp_css = strip_comments(COMPONENTS.read_text(encoding="utf-8"))
    landing = plate_landing(comp_css)

    failures, lines, gaps = [], [], []
    for track in TRACKS:
        page = track["page"]
        page_css = strip_comments(style_blocks(page.read_text(encoding="utf-8")))
        parser = Steps()
        parser.feed(page.read_text(encoding="utf-8"))
        if not parser.steps:
            failures.append(f"{track['name']}: no .cf-pin__step in {page.name}")
            continue
        for n, step in enumerate(parser.steps, 1):
            head, who = earliest(track, page_css, comp_css, step)
            if head is None:
                failures.append(
                    f"{track['name']} · step {n:02d} puts nothing on the stage at all")
                continue
            gap = head - landing
            flag = "" if gap <= CEILING else "   OVER"
            lines.append(f"  {track['name']} · step {n:02d}: plate lands {landing:.2f}, "
                         f"{who} opens {head:.2f} — {gap:+.2f} of a point{flag}")
            gaps.append(gap)
            if gap > CEILING:
                failures.append(
                    f"{track['name']} · step {n:02d} (--i:{step['i']}) opens on a still: the plate "
                    f"lands at contain {landing:.2f} % of its quarter and the first part — the "
                    f"{who} — does not start until {head:.2f} %, a gap of {gap:.2f} points against "
                    f"a ceiling of {CEILING}. The stage is pinned there, so nothing moves at all.")

    if args.verbose or failures:
        print("quarter openings, in points of each quarter:")
        for line in lines:
            print(line)
    if failures:
        print("\nA PINNED QUARTER OPENED ON A STILL " + MOTION, file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    print(f"quarter opening OK — {len(gaps)} quarters across {len(TRACKS)} pinned tracks, "
          f"worst gap {max(gaps):+.2f} of a point against a ceiling of {CEILING}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
