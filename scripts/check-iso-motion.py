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

Plus three about WHEN a part arrives, each authored as a number in a style
attribute and each stated in prose by the very stylesheet that reads it:

  --trace-lead
  + --trace-span  may not run past the trace window's own width. The window is
                  27 points of `cover` and the pinned track maps a stroke onto
                  its quarter's 8 points BY that 27, so one stroke over budget
                  is wrong on two timelines at once — it lands inside the
                  construction points' window instead of on the light.
  --stage         may not name a stage that starts after the light does. Stage
                  n arrives over `build_first + n x build_step`; past the last
                  one that opens before the light, a part is still travelling
                  while the lime it carries is coming up.
  a light's fill  cf-iso-light animates fill-opacity and nothing else, so a
                  light that is not a filled element has no arrival at all —
                  and the <svg>'s own fill="none" means it paints nothing
                  either. And where the light DOES arrive, its fill may not
                  open before that arrival closes: lime is light, so an object
                  lit while it is still travelling is lit before it is there.
                  That one is an inequality between the two ranges of a single
                  declaration, swept over every --stage and --build-head the
                  stylesheets themselves declare — see light_handover().

The two constants those first two are measured against are READ OUT OF
components.css rather than restated here — see assembly_windows(). A checker
carrying its own copy of a number goes on passing the day the stylesheet moves
it, which is the drift every script in this directory exists to stop; if the
constant cannot be found, that is itself a finding rather than a fallback.

None of these can be seen in a screenshot. All of them can be counted.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-iso-motion.py
"""

import ast
import html
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

# --trace-from and --trace-to are dash offsets and are authored to two decimals
# (.49, .46, .12), so they are compared at that precision. --trace-lead and
# --trace-span are points of `cover` and are authored to the same (16.33, 8.78).
TRACE_TOLERANCE = 0.01

# A cross product of two directions taken over coordinates in the hundreds, so
# the slack is generous in absolute terms and still nowhere near a real angle:
# the smallest one the system sanctions is 26.57 degrees.
COLLINEAR_TOLERANCE = 1e-6

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


# A selector-keyed travel as a documentation page writes one, after the
# highlighting spans are stripped:
#
#     .cf-statement .cf-iso { --iso-travel: 30; }   /* 1200 / 40 */
#
# The trailing derivation is optional in the pattern and required by nothing —
# a sample that omits it is checked against the stylesheet alone. Where it is
# written it is the stronger claim, because it names the frame the number came
# out of, which is the thing a recrop moves.
DOC_TRAVEL = re.compile(
    r"\.([\w-]+)\s+\.cf-iso\s*\{[^}]*?--iso-travel:\s*([\d.]+)[^}]*\}"
    r"(?:\s*/\*\s*([\d.]+)\s*/\s*([\d.]+)\s*\*/)?"
)
TAGS = re.compile(r"<[^>]+>")


def documented_travels():
    """Every selector-keyed --iso-travel sample written into a docs-code block,
    as (page, line, class, value, frame, divisor).

    THE SAMPLE IS THE PART NOTHING WAS READING. travel_overrides() above holds
    the stylesheet to the drawings, and did so while the page that teaches the
    rule printed a different number over a frame the tree has never had —
    `.cf-statement .cf-iso { --iso-travel: 12 }` on "the statement figure is 480
    units", against a shipped 30 on a 1200-unit drawing. Both halves were wrong
    and they were consistent with each other, so the sample read as a quotation
    of a rule it contradicted, and the inversion mattered: a BIGGER frame on the
    same token travels a SMALLER fraction, so the example taught the correction
    backwards.

    The spans are stripped rather than parsed. docs-code is highlighted by
    wrapping literals in <span class="val">, which puts markup between the
    property and its value, and the entities that survive that (&lt;, &gt;,
    &amp;) are unescaped before matching so a sample reads as the CSS it
    depicts."""
    out = []
    for page in PAGES:
        text = page.read_text()
        for block in re.finditer(r'<pre class="docs-code">(.*?)</pre>', text, re.S):
            plain = html.unescape(TAGS.sub("", block.group(1)))
            for m in DOC_TRAVEL.finditer(plain):
                out.append((
                    page.relative_to(ROOT),
                    text.count("\n", 0, block.start()) + 1,
                    m.group(1),
                    float(m.group(2)),
                    float(m.group(3)) if m.group(3) else None,
                    float(m.group(4)) if m.group(4) else None,
                ))
    return out


def token(name, text):
    m = re.search(re.escape(name) + r":\s*([^;]+);", strip_comments(text))
    return m.group(1).strip() if m else None


def rule_bodies(text, selector):
    """The declarations of every rule whose selector list is exactly `selector`.

    Anchored on the WHOLE prelude, normalised for whitespace, rather than on a
    substring: `.cf-iso__light` must never pick up
    `.cf-iso--build .cf-iso__light`, whose window is a different number for a
    different reason. Several rules share a selector here — `.cf-iso__trace`
    has three — so this returns all of them and the caller picks by the
    declaration it is after.
    """
    return [
        m.group(2)
        for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", text)
        if " ".join(m.group(1).split()) == selector
    ]


def _number(pattern, bodies):
    """The first number `pattern` finds across `bodies`, or None — and the
    caller reports the None rather than falling back to a literal of its own.
    A gate derived from a constant this script could not find is a gate that
    silently stops meaning anything."""
    for body in bodies:
        m = re.search(pattern, body)
        if m:
            return float(m.group(1))
    return None


def assembly_windows():
    """The three numbers the assembly's timing is written against, read out of
    components.css rather than restated here.

    A checker carrying its own copy of a constant goes on passing the day the
    stylesheet moves, which is the whole failure this directory exists to
    prevent. So the two gates below are DERIVED:

      trace_open   cover % at which the trace window opens.
      trace_span   the default --trace-span, which is also the full width of
                   that window. A led stroke has to fit inside it, and now has
                   to twice: components.css maps the same lead onto the pinned
                   track's 8 points by exactly this ratio.
      build_first  cover % at which stage 0 starts arriving.
      build_step   how much later each subsequent stage starts.
      light_start  cover % at which the lime begins coming up.
    """
    text = strip_comments((CSS / "components.css").read_text())
    trace = rule_bodies(text, ".cf-iso__trace")
    build = rule_bodies(text, ".cf-iso--build .cf-iso__form")
    light = rule_bodies(text, ".cf-iso__light")
    return {
        "trace_open": _number(
            r"animation-range:\s*cover\s*calc\(\s*([\d.]+)%", trace),
        "trace_span": _number(r"--trace-span:\s*([\d.]+)%", trace),
        "build_first": _number(
            r"animation-range:\s*cover\s*calc\(\s*([\d.]+)%", build),
        "build_step": _number(
            r"var\(--stage,\s*0\)\s*\*\s*([\d.]+)%", build),
        "light_start": _number(
            r"animation-range:\s*cover\s*([\d.]+)%", light),
    }


# ---------------------------------------------------------------------------
# THE LIGHT IS THE LAST THING TO ARRIVE, AND THAT IS AN INEQUALITY BETWEEN TWO
# RANGES OF ONE DECLARATION.
#
# `.cf-iso--build .cf-iso__light` and `.lp-proc-steps .cf-iso__light` each
# carry TWO animations on one `animation-range` — the part's arrival and the
# lime's fill — and the whole of what the brand asks of them is that the second
# opens no earlier than the first closes. Lime is light: an object lit while it
# is still travelling is lit before it is there.
#
# Nothing held that, and it was false on two of the four objects at once. The
# fill's opening was a literal (30 on the base assembly, 11.5 on the pinned
# track) and the arrival's closing is an expression over --stage and, since the
# build's head became a variable, over --build-head as well. A literal only
# stays later than an expression while nobody moves the expression, and both
# cards whose lime plate sits on stage 2 — 01's telescope crown, 04's equator —
# had already moved past it.
#
# WHY THIS IS EVALUATED RATHER THAN PATTERN-MATCHED. The two rules state the
# same inequality in two different algebras: `22% + var(--stage,0) * 7%` on one
# timeline, `(var(--build-head) + 6.5 + var(--stage,0) * 2.2) * 1%` on the
# other, the second folded differently again in the arrival it has to beat. A
# textual comparison would fail on the folding and a hand-copied number would
# be the drift this whole directory exists to stop. So the ranges are read out
# of the stylesheets, the variables are swept over the values the stylesheets
# themselves declare, and the two are compared as numbers.
#
# --i is not swept. It shifts a card's whole quarter and appears on both sides
# of the comparison with the same coefficient, so it cancels; it is pinned at 0
# and the check is the same check for every card.

RANGE_NAMES = ("cover", "contain", "entry-crossing", "exit-crossing", "entry", "exit")

# The two rules that carry an arrival and a fill on one declaration. Each is
# (stylesheet, selector) — no third exists, and a fourth arriving without a row
# here is what the count in the summary line is for.
LIGHT_RULES = (
    ("components.css", ".cf-iso--build .cf-iso__light"),
    ("acts.css", ".lp-proc-steps .cf-iso__light"),
)

# ---------------------------------------------------------------------------
# AN ORBIT FADES WITH THE PLAN AND SETTLES WITH THE OBJECT.
#
# foundations/motion.html states the orbit in one sentence — it turns as the
# object assembles and settles when everything else does — and an orbit carries
# .cf-iso__ghost precisely so that it fades up with the rest of the dashed
# geometry. Both halves of that are relations between THREE rules that live in
# two stylesheets, so neither half can be seen from inside any one of them, and
# both were false at once:
#
#   components.css   the base build retimes every ghost to the plan's window
#                    and excludes the orbit, to stop a single-value range
#                    clobbering the turn. The exclusion also handed the FADE
#                    back to `cover 20% cover 40%`, a window measured against
#                    an object that arrives whole. On card 04 — the only built
#                    object in the system with orbits, and they are its only
#                    dashed geometry — the plan's window ran empty and the
#                    rings faded up over a finished sphere.
#   acts.css         the pinned track ended the turn at 12 of a quarter whose
#                    light lands at 15 and whose nodes close the reveal at
#                    15.5, so the ring stopped four tenths of a point before
#                    the lime under it began to come up.
#
# Each is a number that looks free from where it is written and is not: the
# fade's two ends belong to the sibling ghosts' rule and the turn's end to the
# construction points' rule, one of which is in the other stylesheet. So all
# four are read rather than restated, and compared as numbers for the same
# reason light_handover() evaluates rather than matches — the two timelines
# state the same windows in different algebras.
#
#   (stylesheet, orbit selector, plan selector, node stylesheet, node selector)
ORBIT_RULES = (
    ("components.css", ".cf-iso--build .cf-iso__orbit",
     ".cf-iso--build .cf-iso__ghost:not(.cf-iso__orbit)",
     "components.css", ".cf-iso__node"),
    ("acts.css", ".lp-proc-steps .cf-iso__orbit",
     ".lp-proc-steps .cf-iso--build .cf-iso__ghost:not(.cf-iso__orbit)",
     "components.css", ".cf-pin .cf-iso__node"),
)

_VAR = re.compile(r"var\(\s*(--[\w-]+)\s*(?:,\s*([^()]*?)\s*)?\)")


def split_top_level(text, sep=","):
    """Split on `sep`, ignoring separators inside parentheses."""
    parts, depth, start = [], 0, 0
    for i, ch in enumerate(text):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == sep and depth == 0:
            parts.append(text[start:i])
            start = i + 1
    parts.append(text[start:])
    return [p.strip() for p in parts]


def split_range(text):
    """One `animation-range` entry into its start and end values.

    A range is `<name> <value> <name> <value>`, and the values are calc()
    expressions that may themselves contain the word `cover` nowhere but may
    contain commas and parentheses everywhere. So the split is on a range NAME
    seen at paren depth 0, which is the only place one can appear.
    """
    parts, depth, start = [], 0, 0
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif depth == 0:
            for name in RANGE_NAMES:
                if text.startswith(name, i) and (i == 0 or text[i - 1].isspace()):
                    if i > start:
                        parts.append(text[start:i].strip())
                    start = i
                    i += len(name) - 1
                    break
        i += 1
    parts.append(text[start:].strip())
    return [p for p in parts if p]


def eval_calc(expr, values):
    """A CSS calc() expression as a number of percentage points.

    Every term in these two declarations is either a percentage or a plain
    number, and the two are never multiplied together, so the unit can be
    dropped and the arithmetic done in points. `var()` is resolved from
    `values`, falling back to the declaration's own default where it has one —
    a name with neither is a finding, not a zero.
    """
    def sub(m):
        name, default = m.group(1), m.group(2)
        if name in values:
            return "(%s)" % values[name]
        if default is not None and default != "":
            return "(%s)" % default
        raise KeyError(name)

    text = _VAR.sub(sub, expr)
    while _VAR.search(text):                      # var() nested in a default
        text = _VAR.sub(sub, text)
    for name in RANGE_NAMES:
        text = re.sub(r"\b%s\b" % name, "", text)
    text = re.sub(r"\bcalc\b", "", text).replace("%", "")
    return _arith(ast.parse(text.strip(), mode="eval").body)


_BINOPS = {ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b,
           ast.Mult: lambda a, b: a * b, ast.Div: lambda a, b: a / b}


def _arith(node):
    """Numbers, + - * /, unary minus, and max()/min(). Nothing else — the
    expressions are CSS math and an `eval` over a stylesheet is not."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        v = _arith(node.operand)
        return v if isinstance(node.op, ast.UAdd) else -v
    if isinstance(node, ast.BinOp) and type(node.op) in _BINOPS:
        return _BINOPS[type(node.op)](_arith(node.left), _arith(node.right))
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id in ("max", "min") and not node.keywords):
        return (max if node.func.id == "max" else min)(
            *[_arith(a) for a in node.args])
    raise ValueError(ast.dump(node))


def light_handover(max_stage):
    """Every (--stage, --build-head) a light can be authored at, on both
    timelines, with the fill opening no earlier than the arrival closes."""
    findings = []
    stages = range(0, (max_stage if max_stage is not None else 3) + 1)

    for filename, selector in LIGHT_RULES:
        text = strip_comments((CSS / filename).read_text())
        bodies = [b for b in rule_bodies(text, selector) if "animation-range" in b]
        if not bodies:
            findings.append(
                "%s no longer carries an animation-range on `%s`, so the rule that\n"
                "    the lime opens where the plate lands is not being checked on this\n"
                "    timeline. Point LIGHT_RULES at the rule that carries it now."
                % (filename, selector))
            continue

        value = re.search(r"animation-range:\s*([^;]+);", bodies[0]).group(1)
        ranges = [split_range(r) for r in split_top_level(value)]
        if len(ranges) != 2 or any(len(r) != 2 for r in ranges):
            findings.append(
                "%s's `%s` no longer states exactly two ranges — the fill's and the\n"
                "    arrival's — so which one opens first cannot be read. Found %d."
                % (filename, selector, len(ranges)))
            continue

        # Declaration order follows animation-name: cf-iso-light, cf-iso-build.
        fill_start, arrival_end = ranges[0][0], ranges[1][1]

        # The heads a card can be given, off the stylesheet that gives them.
        heads = sorted({float(h) for h in re.findall(
            r"--build-head:\s*([\d.]+)", text)}) or [0.0]

        for head in heads:
            for stage in stages:
                env = {"--i": "0", "--stage": str(stage),
                       "--build-head": repr(head)}
                try:
                    opens, lands = (eval_calc(fill_start, env),
                                    eval_calc(arrival_end, env))
                except (KeyError, SyntaxError, ValueError) as exc:
                    findings.append(
                        "%s's `%s` states a range this check cannot evaluate (%s: %s).\n"
                        "    Either the expression grew a function _arith() does not know\n"
                        "    or a var() lost its fallback."
                        % (filename, selector, type(exc).__name__, exc))
                    break
                if opens < lands - 1e-9:
                    findings.append(
                        "%s's `%s` opens the lime at %g %% and the plate carrying it is\n"
                        "    still arriving until %g %% — at --stage:%d, --build-head:%g.\n"
                        "    Lime is light and it is the last thing to arrive: for %g points\n"
                        "    of range the object is lit before it is there. Open the fill at\n"
                        "    the later of the constant and the part's own arrival end.\n"
                        "    → foundations/motion.html#light-last"
                        % (filename, selector, opens, lands, stage, head,
                           lands - opens))
            else:
                continue
            break
    return findings


def _one_range(filename, selector, text, want):
    """The `animation-range` of `selector`, split into `want` ranges of two
    values each — or a finding saying which of those it is not."""
    bodies = [b for b in rule_bodies(text, selector) if "animation-range" in b]
    if not bodies:
        return None, (
            "%s no longer carries an animation-range on `%s`. ORBIT_RULES names\n"
            "    the rules this gate reads; point it at the rule that carries it now."
            % (filename, selector))
    value = re.search(r"animation-range:\s*([^;]+);", bodies[-1]).group(1)
    ranges = [split_range(r) for r in split_top_level(value)]
    if len(ranges) != want or any(len(r) != 2 for r in ranges):
        return None, (
            "%s's `%s` no longer states exactly %d range(s) of two values, so the\n"
            "    orbit's fade and turn cannot be told apart. Found %d."
            % (filename, selector, want, len(ranges)))
    return ranges, None


def orbit_handover():
    """An orbit's fade is its sibling ghosts' window; its turn opens with that
    fade and closes where the construction points settle."""
    findings = []
    cache = {}

    def sheet(name):
        if name not in cache:
            cache[name] = strip_comments((CSS / name).read_text())
        return cache[name]

    for filename, orbit_sel, plan_sel, node_file, node_sel in ORBIT_RULES:
        text = sheet(filename)
        orbit, bad = _one_range(filename, orbit_sel, text, 2)
        if bad:
            findings.append(bad)
            continue
        plan, bad = _one_range(filename, plan_sel, text, 1)
        if bad:
            findings.append(bad)
            continue
        nodes, bad = _one_range(node_file, node_sel, sheet(node_file), 1)
        if bad:
            findings.append(bad)
            continue

        # Declaration order follows animation-name: cf-iso-fade, cf-iso-orbit.
        (fade_open, fade_shut), (turn_open, turn_shut) = orbit
        env = {"--i": "0"}
        try:
            values = [eval_calc(e, env) for e in
                      (fade_open, fade_shut, turn_open, turn_shut,
                       plan[0][0], plan[0][1], nodes[0][1])]
        except (KeyError, SyntaxError, ValueError) as exc:
            findings.append(
                "%s's `%s` states a range this check cannot evaluate (%s: %s)."
                % (filename, orbit_sel, type(exc).__name__, exc))
            continue
        fo, fs, to, ts, po, ps, ne = values

        if (fo, fs) != (po, ps):
            findings.append(
                "%s's `%s` fades up over %g–%g %% while the ghosts beside it use\n"
                "    %g–%g %%. An orbit carries .cf-iso__ghost so that it arrives WITH\n"
                "    the dashed geometry: on a built object the plan is what the solids\n"
                "    arrive into, and an orbit timed after them is that drawing told\n"
                "    backwards. State the plan's own two ends.\n"
                "    → foundations/motion.html#build"
                % (filename, orbit_sel, fo, fs, po, ps))
        if to != fo:
            findings.append(
                "%s's `%s` begins turning at %g %% and begins fading up at %g %%.\n"
                "    The ring is drawn as motion; it may not appear already still, nor\n"
                "    move before it is visible. Open both on the same point."
                % (filename, orbit_sel, to, fo))
        if abs(ts - ne) > 1e-9:
            findings.append(
                "%s's `%s` settles at %g %% and `%s` settles the construction points\n"
                "    at %g %%. The rule is that an orbit turns while the object assembles\n"
                "    and settles when everything else does — %g points either way is a\n"
                "    ring that stops while its object is still arriving, or goes on\n"
                "    turning after the object is finished. Read the node window's end.\n"
                "    → foundations/motion.html#build"
                % (filename, orbit_sel, ts, node_sel, ne, abs(ts - ne)))
    return findings


def style_number(tag, name, default):
    """A custom property's value off an element's style attribute, in points."""
    m = re.search(re.escape(name) + r":\s*(-?[\d.]+)", tag)
    return float(m.group(1)) if m else default


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


def clip_segment(x1, y1, x2, y2, box):
    """Liang-Barsky. The (t_enter, t_exit) of a segment inside a crop rectangle,
    as fractions of the segment's own length, or None if it never enters.

    This is what pathLength cannot tell anybody: it normalises against the DRAWN
    length, and the drawn length includes everything the crop throws away.
    """
    x0, y0, x3, y3 = box
    dx, dy = x2 - x1, y2 - y1
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, x1 - x0), (dx, x3 - x1), (-dy, y1 - y0), (dy, y3 - y1)):
        if p == 0:
            if q < 0:
                return None
        else:
            r = q / p
            if p < 0:
                if r > t1:
                    return None
                t0 = max(t0, r)
            else:
                if r < t0:
                    return None
                t1 = min(t1, r)
    return (t0, t1)


def line_traces(block):
    """Every <line class="cf-iso__trace"> in one .cf-iso, measured against the
    crop that actually applies to it, or None if the frame cannot be resolved.

    ONLY A <line> IS MEASURED HERE, and that is a boundary rather than an
    omission. The visible extent of a straight segment inside a rectangular crop
    is arithmetic; the visible extent of a <path> is the path maths pathLength
    exists so that nobody has to do. Card 03's five traces are paths, and the
    lead rule in main() is what governs them.
    """
    vb = re.search(r'viewBox="\s*([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s*"', block)
    if not vb:
        return None
    vx, vy, vw, vh = (float(g) for g in vb.groups())
    # The drawing sits inside one translated group; the crop is the viewport,
    # expressed back in the drawing's own coordinates. More than one distinct
    # translate and there is no single answer to "where is the edge", which is
    # reported rather than guessed at.
    trs = set(re.findall(r'transform="translate\(\s*([-\d.]+)[\s,]+([-\d.]+)\s*\)"', block))
    if len(trs) > 1:
        return None
    tx, ty = (float(v) for v in (trs.pop() if trs else ("0", "0")))
    box = (vx - tx, vy - ty, vx + vw - tx, vy + vh - ty)

    out = []
    for m in re.finditer(r"<line\b[^>]*\bcf-iso__trace\b[^>]*>", block):
        tag = m.group(0)
        pts = []
        for name in ("x1", "y1", "x2", "y2"):
            g = re.search(name + r'="\s*(-?[\d.]+)\s*"', tag)
            if not g:
                break
            pts.append(float(g.group(1)))
        if len(pts) != 4:
            continue
        cut = clip_segment(*pts, box)
        if cut is None:
            continue
        out.append({"tag": tag, "offset": m.start(), "pts": pts, "cut": cut})
    return out


def split_journeys(page_text, rel, window):
    """Two rules about a straight trace, both re-derived from the drawing.

    1. THE TWO ENDS OF THE DRAW ARE WHERE THE CROP IS. --trace-from is
       1 - (the fraction already behind the trace when it enters) and
       --trace-to is (the fraction still to run when it leaves). Both are
       stated in prose in components.css and both were, until this gate,
       arithmetic somebody did once by hand beside a drawing that is free to
       move underneath it. A recrop changes the answer and nothing renders
       wrong: the line simply draws part of itself off-stage again.

    2. A SIGNAL SPLIT BY ITS OWN OBJECT IS STILL ONE SIGNAL. Where a trace
       enters an object on one side and leaves it on the other, the drawing is
       two strokes and the event is one journey across the frame — so the two
       strokes take the window in proportion to the length each of them draws,
       in the order they are travelled, and the range between them is the width
       of the object they are passing through. Drawn on one window each, they
       are two lines growing at once in opposite directions: the exit draws
       itself before anything has arrived.

    WHAT IS DELIBERATELY NOT A JOURNEY. Two traces on the same line pointing at
    each other are two signals, not one split in half, and two whose visible
    extents overlap are not sequential halves of anything. Both are left alone
    rather than reported, and the direction test is why the ordering below can
    be a single scalar along one axis.
    """
    findings = []
    measured = 0
    for sm in re.finditer(r"<svg\b[^>]*\bcf-iso\b.*?</svg>", page_text, re.S):
        block = sm.group(0)
        if "cf-iso__trace" not in block:
            continue
        traces = line_traces(block)
        line_of = lambda off: page_text.count("\n", 0, sm.start() + off) + 1
        if traces is None:
            if re.search(r"<line\b[^>]*\bcf-iso__trace\b", block):
                findings.append(
                    "%s:%d is a .cf-iso carrying a straight trace whose crop cannot be\n"
                    "    resolved — no viewBox, or more than one translate inside it. The two\n"
                    "    ends of a draw ARE the crop, so where the edge is has to have one\n"
                    "    answer.\n"
                    "    -> design-system/foundations/motion.html#journey"
                    % (rel, page_text.count("\n", 0, sm.start()) + 1)
                )
            continue

        for t in traces:
            measured += 1
            for prop, want in (("--trace-from", 1 - t["cut"][0]),
                               ("--trace-to", 1 - t["cut"][1])):
                got = style_number(t["tag"], prop, 1.0 if prop == "--trace-from" else 0.0)
                if abs(got - want) > TRACE_TOLERANCE:
                    findings.append(
                        "%s:%d authors %s: %g where the drawing gives %.4f. The line runs\n"
                        "    from (%g, %g) to (%g, %g) and is inside its crop from %.4f to\n"
                        "    %.4f of its own length, so %.4f of the range is spent on a line\n"
                        "    nobody can see — or taken off one they can. pathLength normalises\n"
                        "    the DRAWN length, not the visible one, so a recrop moves this\n"
                        "    number and leaves the markup reading correctly.\n"
                        "    -> design-system/foundations/motion.html#crop"
                        % (rel, line_of(t["offset"]), prop, got, want,
                           t["pts"][0], t["pts"][1], t["pts"][2], t["pts"][3],
                           t["cut"][0], t["cut"][1], abs(got - want))
                    )

        # Collinear, same-way, non-overlapping traces are one journey.
        groups = []
        for t in traces:
            x1, y1, x2, y2 = t["pts"]
            dx, dy = x2 - x1, y2 - y1
            length = (dx * dx + dy * dy) ** 0.5
            if not length:
                continue
            t["u"] = (dx / length, dy / length)
            t0, t1 = t["cut"]
            t["a"] = (x1 + dx * t0, y1 + dy * t0)   # where it starts drawing
            t["b"] = (x1 + dx * t1, y1 + dy * t1)   # where it stops
            for g in groups:
                h = g[0]
                ux, uy = h["u"]
                same_way = t["u"][0] * ux + t["u"][1] * uy > 0
                on_line = abs((x1 - h["pts"][0]) * uy - (y1 - h["pts"][1]) * ux)
                parallel = abs(t["u"][0] * uy - t["u"][1] * ux)
                if same_way and parallel < COLLINEAR_TOLERANCE and on_line < 1e-3:
                    g.append(t)
                    break
            else:
                groups.append([t])

        for g in groups:
            if len(g) < 2:
                continue
            ux, uy = g[0]["u"]
            for t in g:
                t["s0"] = t["a"][0] * ux + t["a"][1] * uy
                t["s1"] = t["b"][0] * ux + t["b"][1] * uy
            g.sort(key=lambda t: t["s0"])
            if any(g[i]["s1"] > g[i + 1]["s0"] + 1e-6 for i in range(len(g) - 1)):
                continue  # overlapping, so not sequential halves of one thing
            start, end = g[0]["s0"], g[-1]["s1"]
            total = end - start
            if total <= 0:
                continue
            for t in g:
                want_lead = window * (t["s0"] - start) / total
                want_span = window * (t["s1"] - t["s0"]) / total
                lead = style_number(t["tag"], "--trace-lead", 0.0)
                span = style_number(t["tag"], "--trace-span", window)
                if (abs(lead - want_lead) > TRACE_TOLERANCE
                        or abs(span - want_span) > TRACE_TOLERANCE):
                    findings.append(
                        "%s:%d is one stroke of a signal drawn in %d, crossing %g units of\n"
                        "    frame in all. This stroke starts %g units along and draws %g of\n"
                        "    them, so its share of the %g-point window is lead %.2f and span\n"
                        "    %.2f; it authors lead %g and span %g. The strokes are one journey\n"
                        "    and the window is shared out by length: each takes the share its\n"
                        "    own drawn length is, in the order it is reached, and the range\n"
                        "    between two of them is the width of the object the signal is\n"
                        "    passing through. On a window each they are lines growing at once\n"
                        "    in different places, and the way out of the object draws itself\n"
                        "    before anything has arrived at it.\n"
                        "    -> design-system/foundations/motion.html#journey"
                        % (rel, line_of(t["offset"]), len(g), total,
                           t["s0"] - start, t["s1"] - t["s0"], window,
                           want_lead, want_span, lead, span)
                    )
    return findings, measured


def main():
    findings = []
    overrides = travel_overrides()

    # --- 1. the travel matches the frame -----------------------------------
    assembling = 0
    # The frames each override actually governs, recorded by the same
    # resolution the loop below already does rather than by a second reading of
    # the cascade. Rule 8 needs it to check a sample's `/* W / 40 */`.
    governs = {}
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
                    governs.setdefault(matched[0][0], set()).add(fig["width"])
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

    # --- 2b. and it turns for as long as the object is arriving -------------
    findings += orbit_handover()

    # --- 3, 4, 5. per-page drawing rules --------------------------------
    #
    # THE ASSEMBLY'S TIMING INVARIANTS ARE IN HERE TOO, and they are the three
    # things components.css and motion.html state in prose about WHEN a part
    # arrives, none of which anything read until now. Each is a number in a
    # style attribute, each is invisible in a screenshot, and each has a
    # failure that renders perfectly:
    #
    #   lead + span   A trace's window is authored per stroke so that a signal
    #                 drawn as several strokes arrives along its own direction
    #                 of travel. components.css says "Keep lead + span <= 27 %
    #                 and the last stroke still lands on the light", and the
    #                 pinned re-timing now maps the same two properties onto
    #                 the quarter's 8 points BY that 27. Past it, the last
    #                 stroke draws into the nodes' window instead of onto it —
    #                 on both timelines, for one number authored once.
    #                 Five of the eight authored traces sit exactly on 27.
    #   --stage       Stage n starts at build_first + n x build_step. The rule
    #                 is that every stage starts before the light comes up —
    #                 "Four stages fit before the light comes up at 30 %" — so
    #                 a part one stage past the last is still travelling when
    #                 the lime it carries begins to light, and still moving
    #                 when the construction nodes settle.
    #   a light's fill  cf-iso-light animates fill-opacity and nothing else.
    #                 A light drawn as a stroke therefore has NO arrival at
    #                 all: it is simply there from the first frame, and the
    #                 beat the whole assembly is timed to end on is missing
    #                 with nothing rendering wrong. The <svg> carries
    #                 fill="none", so an unfilled light paints nothing either.
    #
    # The two constants come from assembly_windows(), which reads them off the
    # stylesheet — see its docstring for why they are not literals here.
    win = assembly_windows()
    missing = [k for k, v in win.items() if v is None]
    if missing:
        findings.append(
            "components.css no longer states %s where this check reads it, so the\n"
            "    assembly's timing gates below cannot be derived and are not being\n"
            "    applied. Point assembly_windows() at the rule that carries them now —\n"
            "    a gate whose constant went missing is worse than no gate, because it\n"
            "    goes on passing." % ", ".join(sorted(missing))
        )
        max_stage = None
    else:
        # The last stage that still STARTS before the light does. 5 + 7n < 30
        # gives 3 — four stages, 0 through 3, which is what motion.html says.
        max_stage = 0
        while win["build_first"] + (max_stage + 1) * win["build_step"] < win["light_start"]:
            max_stage += 1

    # The lime opens where the plate carrying it lands, on both timelines.
    handover = light_handover(max_stage)
    findings.extend(handover)

    led = staged = lit = 0

    for page in PAGES:
        text = page.read_text()
        rel = page.relative_to(ROOT)

        for m in re.finditer(r"<[a-z]+\b[^>]*\bcf-iso__trace\b[^>]*>", text):
            line = text.count("\n", 0, m.start()) + 1
            if win["trace_span"] is not None:
                led += 1
                lead = style_number(m.group(0), "--trace-lead", 0.0)
                span = style_number(m.group(0), "--trace-span", win["trace_span"])
                # A lead only ever DELAYS a stroke and a span is time spent
                # drawing, so the floor on each is not pedantry. It is what
                # scripts/check-quarter-opening.py stands on: that script reads
                # this rule's head past the lead term on the ground that the
                # earliest stroke on a step is the one with no lead, which is
                # true exactly while a lead cannot be negative.
                if lead < 0 or span <= 0:
                    findings.append(
                        "%s:%d authors --trace-lead:%g and --trace-span:%g. A lead is how far\n"
                        "    INTO the window a stroke starts and a span is how much of the\n"
                        "    window it spends drawing, so the first cannot be negative and the\n"
                        "    second cannot be zero or less. A negative lead also moves the head\n"
                        "    of the pinned rule earlier, which is the one thing\n"
                        "    scripts/check-quarter-opening.py reads it past.\n"
                        "    -> design-system/foundations/motion.html#trace"
                        % (rel, line, lead, span)
                    )
                elif lead + span > win["trace_span"] + 1e-9:
                    findings.append(
                        "%s:%d is led %g into a %g-point window and then draws for %g, so it\n"
                        "    finishes at %g where the window itself closes at %g. A trace's\n"
                        "    window is the whole of `cover %g%% -> %g%%`, and the pinned track\n"
                        "    maps a stroke onto its quarter's 8 points by that same %g — so a\n"
                        "    stroke over budget lands inside the nodes' window on BOTH\n"
                        "    timelines rather than on the light at the end of its own.\n"
                        "    Shorten the span or start the stroke earlier.\n"
                        "    -> design-system/foundations/motion.html#trace"
                        % (rel, line, lead, win["trace_span"], span,
                           lead + span, win["trace_span"],
                           win["trace_open"], win["trace_open"] + win["trace_span"],
                           win["trace_span"])
                    )
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

        # A part one stage past the last one that starts before the light.
        if max_stage is not None:
            for m in re.finditer(r"--stage:\s*(\d+)", text):
                staged += 1
                stage = int(m.group(1))
                if stage > max_stage:
                    findings.append(
                        "%s:%d authors --stage:%d, and the last stage that starts before the\n"
                        "    light comes up is %d. Stage n starts at cover %g%% + n x %g%%, so\n"
                        "    this part only begins moving at %g%% — after the lime has started\n"
                        "    coming up at %g%%, and it is still travelling when the construction\n"
                        "    points settle. Stage order is construction order: fold the part\n"
                        "    into an existing stage rather than adding one past the light.\n"
                        "    -> design-system/foundations/motion.html#build"
                        % (rel, text.count("\n", 0, m.start()) + 1, stage, max_stage,
                           win["build_first"], win["build_step"],
                           win["build_first"] + stage * win["build_step"],
                           win["light_start"])
                    )

        # A light that is not a filled element has no arrival at all.
        for m in re.finditer(r"<[a-z]+\b[^>]*\bcf-iso__light\b[^>]*>", text):
            lit += 1
            fill = re.search(r'\bfill="([^"]*)"', m.group(0))
            if fill is None or fill.group(1).strip() in ("", "none"):
                findings.append(
                    "%s:%d is a .cf-iso__light with %s. cf-iso-light animates fill-opacity\n"
                    "    and nothing else, so a light that is not filled never arrives — it is\n"
                    "    simply there from the first frame, and the beat the whole assembly is\n"
                    "    timed to end on is missing with nothing rendering wrong. The <svg>\n"
                    "    carries fill=\"none\", so it paints nothing at all either. Lime is\n"
                    "    light: give it the gradient as a fill.\n"
                    "    -> design-system/foundations/illustration.html"
                    % (rel, text.count("\n", 0, m.start()) + 1,
                       "no fill" if fill is None else 'fill="%s"' % fill.group(1))
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


    # --- 5b. a straight trace's two ends, and a signal split by its object --
    # The lead gate above asks only whether a stroke fits its window. These two
    # ask what the window and the two dash offsets should BE, derived from the
    # drawing rather than compared against a literal — which is the one thing
    # that survives a recrop. See split_journeys().
    straight = 0
    if win["trace_span"] is not None:
        for page in PAGES:
            f, n = split_journeys(page.read_text(), page.relative_to(ROOT),
                                  win["trace_span"])
            findings.extend(f)
            straight += n

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

    # --- 8. a documented travel is the shipped travel ----------------------
    # Rule 1 holds the stylesheet to the drawings. This holds the pages that
    # TEACH that rule to the stylesheet, which is the one direction a checker
    # reading only CSS can never see: the sample is prose, it renders whatever
    # it says, and a number in it that has gone stale reads exactly like a
    # number that has not.
    documented = 0
    for rel, line, cls, value, frame, divisor in documented_travels():
        shipped = overrides.get(cls)
        if shipped is None:
            findings.append(
                "%s:%d prints `.%s .cf-iso { --iso-travel: %g }` as a sample, and\n"
                "    components.css declares no such rule. A sample is a quotation, not a\n"
                "    second declaration — key it on the component the stylesheet keys, or\n"
                "    the page teaches a selector no drawing matches.\n"
                "    -> design-system/foundations/motion.html#travel"
                % (rel, line, cls, value)
            )
            continue
        documented += 1
        if abs(shipped - value) > TRAVEL_TOLERANCE:
            findings.append(
                "%s:%d prints --iso-travel: %g for .%s where components.css ships %g.\n"
                "    The page that teaches the 2.5 %% rule is quoting a value the system does\n"
                "    not hold, and nothing renders wrong either way — the sample is text.\n"
                "    -> design-system/foundations/motion.html#travel"
                % (rel, line, value, cls, shipped)
            )
        if frame is None:
            continue
        seen = governs.get(cls, set())
        if divisor != TRAVEL_DIVISOR:
            findings.append(
                "%s:%d derives .%s's travel as %g / %g. The divisor is %d — 2.5 %% of the\n"
                "    drawing — and it is the ratio the system holds constant, not the number.\n"
                "    -> design-system/foundations/motion.html#travel"
                % (rel, line, cls, frame, divisor, TRAVEL_DIVISOR)
            )
        elif seen and any(abs(w - frame) > TRAVEL_TOLERANCE for w in seen):
            findings.append(
                "%s:%d derives .%s's travel from a %g-unit frame; the drawings that rule\n"
                "    governs are %s units wide. A recrop moves the frame and leaves the\n"
                "    arithmetic beside it reading correctly about a drawing that is gone.\n"
                "    -> design-system/foundations/motion.html#travel"
                % (rel, line, cls, frame,
                   " and ".join("%g" % w for w in sorted(seen)))
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
        "to screen.\n"
        "                    timing: %d traces inside the %g-point window, %d stages at or\n"
        "under %d, %d lights filled, %d light declarations opening their fill no earlier\n"
        "than the plate carrying it lands, %d orbit declarations fading with their plan and\n"
        "settling with their construction points.\n"
        "                    %d straight traces starting and stopping at their own crop,\n"
        "every split signal sharing one window by length.\n"
        "                    %d documented travels quoting the stylesheet they teach."
        % (assembling, normalised, led, win["trace_span"], staged, max_stage, lit,
           len(LIGHT_RULES), len(ORBIT_RULES), straight, documented)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
