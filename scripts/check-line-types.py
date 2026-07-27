#!/usr/bin/env python3
"""Hold every dash pattern in the tree to the four sanctioned line types.

The manual plate `Formsprache > Linien` defines four line types and nothing
else: solid, 2-1, 1-2, 1-4. tokens.css realises the three dashed ones as px
pairs, and components.css says in as many words why those px are the whole of
the rule -- .cf-iso puts `vector-effect: non-scaling-stroke` on every contour,
which measures a dasharray in SCREEN pixels, "which is what keeps a ghost's 1-4
dash a 1-4 dash at any size".

  --dash-2-1   4px 2px
  --dash-1-2   2px 4px
  --dash-1-4   1px 4px

The CSS side has honoured that from the beginning: every `stroke-dasharray`
declaration in the shipping stylesheets is a var(). The MARKUP side never has,
because a dasharray in an inline SVG is a presentation attribute -- a literal,
typed next to the path data, usually carried straight over from an export. A
literal cannot resolve a token and nothing has ever compared the two. Counted
before this script existed, the tree shipped eight distinct dash patterns for a
rule that has three:

  1 4    42   --dash-1-4
  2 4    12   --dash-1-2
  1 2    12   the 1-2 ratio at a unit of 1        <- off the rule
  0.5 1   4   the 1-2 ratio at a unit of 0.5      <- user units, allowed
  4 2     3   --dash-2-1
  3 1.5   2   the 2-1 ratio at a unit of 1.5      <- off the rule
  1 0.5   1   the 2-1 ratio at a unit of 0.5      <- user units, allowed
  4 1     1   4:1, which is not a line type       <- off the rule

Six of the strays were on patterns/ueber-uns.html, which is one of the two
designed pages, and the drawing's own comment claimed its dashes were "pinned
to --dash-*". They were not, and no screenshot could have said so: a 3 px dash
period and a 5 px dash period are the same picture at a glance.

TWO CONTEXTS, TWO STANDARDS, and the distinction is the point.

  screen px   The stroke is non-scaling -- the element is inside a .cf-iso, or
              carries vector-effect="non-scaling-stroke" itself or on an
              ancestor. The dasharray is then device pixels no matter what the
              drawing is scaled to, so it must be EXACTLY one of the three
              token values. This is where drift is invisible and expensive.

  user units  The stroke scales with the drawing, so the absolute numbers are a
              property of the frame and not of the rule. Only the RATIO is
              checked. foundations/iconography.html blows a 24-unit icon box up
              13x and draws its keylines at 0.25 units; holding those to `4 2`
              would put a 53 px dash on a diagram of a 24 px glyph.

The .cf-iso__trace is excluded from both, and has to be: components.css exempts
it from non-scaling-stroke on purpose so that pathLength="1" works, and the CSS
then sets `stroke-dasharray: 1` on it -- one dash as long as the whole path,
which is a draw mechanism and not a line type.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-line-types.py
    python3 scripts/check-line-types.py -v     # every pattern, not only strays
"""

import argparse
import pathlib
import re
import sys
from collections import Counter
from fractions import Fraction
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
CSS = DS / "assets" / "css"

# The three dashed types, as the px pairs tokens.css declares them. Solid is a
# fourth type and needs no entry: it is the absence of a dasharray.
TOKENS = {
    "--dash-2-1": (4.0, 2.0),
    "--dash-1-2": (2.0, 4.0),
    "--dash-1-4": (1.0, 4.0),
}

# Same three as bare ratios, for strokes measured in user units.
RATIOS = {Fraction(2, 1): "2-1", Fraction(1, 2): "1-2", Fraction(1, 4): "1-4"}

# The designer's own material is not ours to hold to our rules. process-card
# and ueber-uns both document where an export's pattern was mapped onto the
# four; the export itself stays exactly as it was delivered.
SKIP_DIRS = {"source"}

VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


def parse_dasharray(raw):
    """A dasharray as a list of floats, or None if it is not a number list.

    `none` and `0` are solid and return an empty list. A single value repeats:
    `4` is four on, four off. Commas and whitespace are both separators.
    """
    text = (raw or "").strip().lower()
    if not text or text == "none":
        return []
    parts = [p for p in re.split(r"[\s,]+", text) if p]
    try:
        nums = [float(p) for p in parts]
    except ValueError:
        return None
    if not any(nums):
        return []
    return nums * 2 if len(nums) == 1 else nums


def describe(nums):
    return " ".join(("%g" % n) for n in nums)


def classify(nums, screen_px):
    """(ok, note). `note` names the type when ok and the fault when not."""
    if not nums:
        return True, "solid"
    if len(nums) != 2:
        return False, "%d values -- a line type is one dash and one gap" % len(nums)
    dash, gap = nums
    if dash <= 0 or gap <= 0:
        return False, "a zero-length dash or gap"

    ratio = Fraction(dash).limit_denominator(1000) / Fraction(gap).limit_denominator(1000)
    name = RATIOS.get(ratio)
    if name is None:
        return False, "%s is not one of the four line types (2-1, 1-2, 1-4)" % describe(nums)

    if not screen_px:
        # The frame sets the scale; only the ratio is the rule.
        return True, "%s (user units)" % name

    for token, value in TOKENS.items():
        if (dash, gap) == value:
            return True, "%s / %s" % (name, token)
    unit = min(dash, gap) if name != "1-4" else dash
    return False, ("%s at a unit of %g -- the %s ratio is right and the period is "
                   "not. Non-scaling stroke measures this in device pixels, so it "
                   "must be %s exactly." % (describe(nums), unit, name,
                                            describe(TOKENS["--dash-%s" % name])))


class DashFinder(HTMLParser):
    """Every stroke-dasharray in a document, with whether its stroke scales.

    Non-scaling is inherited in exactly the two ways the tree uses it: the
    `vector-effect` presentation attribute on the element or an ancestor, and
    the `.cf-iso` descendant rule in components.css, which reaches every shape
    in the drawing except `.cf-iso__trace`.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []      # [(tag, non_scaling, in_iso)]
        self.hits = []       # (line, tag, classes, raw, screen_px)

    def _flags(self, attrs):
        inherited_ns = any(ns for _, ns, _ in self.stack)
        inherited_iso = any(iso for _, _, iso in self.stack)
        ns = inherited_ns or attrs.get("vector-effect", "") == "non-scaling-stroke"
        classes = set((attrs.get("class") or "").split())
        iso = inherited_iso or "cf-iso" in classes
        return ns, iso, classes

    def _record(self, tag, attrs):
        ns, iso, classes = self._flags(attrs)
        raw = attrs.get("stroke-dasharray")
        if raw is None:
            m = re.search(r"stroke-dasharray\s*:\s*([^;]+)", attrs.get("style") or "")
            raw = m.group(1) if m else None
        if raw is None:
            return ns, iso
        # The trace is exempt from non-scaling-stroke by name, and its dasharray
        # is the draw mechanism rather than a line type.
        if "cf-iso__trace" in classes:
            return ns, iso
        screen_px = ns or (iso and tag != "svg")
        self.hits.append((self.getpos()[0], tag, classes, raw, screen_px))
        return ns, iso

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        ns, iso = self._record(tag, a)
        if tag not in VOID:
            self.stack.append((tag, ns, iso))

    def handle_startendtag(self, tag, attrs):
        self._record(tag, dict(attrs))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break


def strip_comments(css):
    """Blank comments out in place, keeping their newlines, so every reported
    line number is the line number in the file the reader will open."""
    return re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), css, flags=re.S)


def token_values():
    """The three dash tokens as declared, so a silent edit fails here rather
    than in a screenshot nobody takes."""
    text = strip_comments((CSS / "tokens.css").read_text(encoding="utf-8"))
    out = {}
    for name in TOKENS:
        m = re.search(re.escape(name) + r"\s*:\s*([^;]+);", text)
        out[name] = m.group(1).strip() if m else None
    return out


def css_declarations():
    """Every stroke-dasharray in the shipping stylesheets.

    The rule on this side is simply that the value is a token. The one literal
    the system allows is `1`, which is the pathLength="1" draw -- one dash as
    long as the path -- and it is allowed by value rather than by selector so
    that a second drawing may use the same mechanism.
    """
    out = []
    for name in ("base.css", "components.css", "docs.css"):
        path = CSS / name
        if not path.exists():
            continue
        text = strip_comments(path.read_text(encoding="utf-8"))
        for m in re.finditer(r"stroke-dasharray\s*:\s*([^;}]+)", text):
            value = " ".join(m.group(1).split())
            line = text[:m.start()].count("\n") + 1
            ok = bool(re.fullmatch(r"var\(--(dash|presence)-[\w-]+\)", value)) or value == "1"
            out.append((name, line, value, ok))
    return out


def pages():
    for path in sorted(DS.rglob("*.html")):
        if SKIP_DIRS & set(p.name for p in path.parents):
            continue
        yield path


def audit():
    findings, seen = [], []

    for name, declared in sorted(token_values().items()):
        want = describe(TOKENS[name])
        got = " ".join((declared or "").replace("px", " ").split())
        if declared is None:
            findings.append(("assets/css/tokens.css", 0, name, "token is missing"))
        elif got != want:
            findings.append(("assets/css/tokens.css", 0, name,
                             "declares %r; the plate's ratio at this system's "
                             "unit is %s px" % (declared, want)))

    for name, line, value, ok in css_declarations():
        rel = "assets/css/" + name
        if ok:
            seen.append((rel, line, "css", value, "token"))
        else:
            findings.append((rel, line, "stroke-dasharray",
                             "%r is a literal. The CSS side reaches the tokens; "
                             "use var(--dash-*) or var(--presence-*)." % value))

    for path in pages():
        rel = path.relative_to(DS).as_posix()
        finder = DashFinder()
        finder.feed(path.read_text(encoding="utf-8"))
        for line, tag, classes, raw, screen_px in finder.hits:
            nums = parse_dasharray(raw)
            if nums is None:
                findings.append((rel, line, tag,
                                 "stroke-dasharray=%r is not a number list" % raw))
                continue
            ok, note = classify(nums, screen_px)
            where = "screen px" if screen_px else "user units"
            if ok:
                seen.append((rel, line, tag, describe(nums) or "none", note))
            else:
                findings.append((rel, line, tag, "%s (%s)" % (note, where)))

    return findings, seen


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every dash pattern, not only the strays")
    args = ap.parse_args()

    findings, seen = audit()

    if args.verbose:
        for rel, line, tag, value, note in seen:
            print("  %-42s %5d  %-8s %-8s %s" % (rel[:42], line, tag, value, note))
        print()

    if findings:
        for rel, line, what, why in findings:
            print("%s:%d  %s\n    %s" % (rel, line, what, why), file=sys.stderr)
        print("\n%d dash pattern%s off the four sanctioned line types. Map each one "
              "onto the rung it means -- see the presence ladder in tokens.css."
              % (len(findings), "" if len(findings) == 1 else "s"), file=sys.stderr)
        return 1

    counts = Counter(value for *_, value, _ in seen if value != "none")
    census = ", ".join("%s x%d" % (v, n) for v, n in sorted(counts.items()))
    print("line types: %d dash patterns, all sanctioned (%s)." % (len(seen), census))
    return 0


if __name__ == "__main__":
    sys.exit(main())
