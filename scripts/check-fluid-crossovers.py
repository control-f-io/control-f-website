#!/usr/bin/env python3
"""Hold the crossover census to the shipping CSS.

foundations/layout.html carries the breakpoint register, and one panel below it
carries the register's own disclaimer:

    "The register is complete about queries, not about behaviour. A min() or
     clamp() against a viewport unit also changes layout at a specific width —
     its arms swap — and none of those appear above, because none of them is a
     query. That distinction is worth stating rather than leaving implicit: a
     register whose argument is completeness has to say which kind it means.
     The three in shipping CSS:"

`check-breakpoints.py` declines that half on purpose, and its header says so:
"A checker that widened the definition would be enforcing a different rule than
the one written down." That is right about the register and it left the panel
under it standing on nothing. "The three in shipping CSS" is a completeness
claim about the whole of a four-file corpus, kept by hand, on the page whose
neighbouring tables are generated precisely because counts kept by hand went
stale four times.

It was wrong when this script first ran: thirty crossovers, not three. The
three it listed were the three somebody had noticed — the consent dialog's two
and the hero's min-height — and the panel excused the rest in one line, "the
token-level clamps are documented already", which is true of two of them and
silent about eleven more.

THE ONE THAT MATTERS IS 941 px. `.cf-plot`'s --plot-u and `.cf-pie`'s --pie-u
both reach their 32 px ceiling there, and 900-1100 is the band where a clamp
middle is least likely to be looked at: past every phone, short of every
desktop frame the design was drawn on. .cf-plot's own comment points straight
at the gap — "this is a crossover, not a threshold, so it is deliberately
absent from the breakpoint register" — while the panel that was supposed to
catch what the register drops had never heard of it.

WHAT IT CHECKS

  live -> table   every crossover in the four shipping stylesheets has a row.
  table -> live   every row still has a declaration behind it, so a crossover
                  that was removed does not linger as a row describing
                  behaviour the system no longer has.
  the stamp       a digest of the rows, so a stale table announces itself.
                  --fix rewrites both.

HOW A CROSSOVER IS FOUND, rather than listed

A declaration's value is parsed into a tree of min()/max() over linear forms in
(px, vw, vh); clamp(a, b, c) is max(a, min(b, c)), var() is resolved through
tokens.css, and addition and scalar multiplication are distributed into the
branches, because min(a, b) + c is min(a + c, b + c) and a negative factor
turns a min into a max. The result is piecewise linear, so the crossovers are
exactly the widths at which the selected leaf changes: found by sweeping the
axis, then solved exactly off the two leaves that swapped. Nothing is compared
against a table of figures — 640, 920 and 974 are re-derived on every run the
same way 941.2 is.

WHAT IT DOES NOT READ, named on every run rather than skipped in silence

  two axes        a declaration whose arms mix vw and vh has no single width
                  at which it swaps; where it swaps is a curve.
  container       an arm in %, cqi or cqw crosses over at a CONTAINER width,
                  which is a different axis from the one this table publishes
                  and is not a fact about the viewport.
  unresolvable    a var() this script cannot resolve — an inherited custom
                  property, a per-page value — or a product of two lengths.

  Unitless clamps are out of scope silently rather than counted: clamp(0,
  var(--v), 1) is a progress value, not a length, and there are twenty-odd of
  them driving the plot, the pie and the gantt. A number has no crossover
  because it has no arms measured in anything.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-fluid-crossovers.py        # check, exit 1 on drift
    python3 scripts/check-fluid-crossovers.py --fix  # rewrite the table + stamp
    python3 scripts/check-fluid-crossovers.py -v     # every declaration read
"""

import argparse
import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system" / "assets" / "css"
LAYOUT = ROOT / "design-system" / "foundations" / "layout.html"

# The same four sheets check-breakpoints.py governs, and for the same reason:
# these are what a reader downloads. docs.css, per-page <style> blocks and
# prototypes/ are outside by the boundary that file's header draws.
SHIPPING = ("tokens.css", "base.css", "components.css", "acts.css")

# The window the census publishes. Below 200 px there is no viewport to speak
# of and above 4000 there is no frame this design was drawn for; both ends are
# far outside every crossover the system actually has, so the window excludes
# nothing today and is stated so that a future one landing outside it is a
# finding rather than a silent absence.
AXIS_LO, AXIS_HI = 200.0, 4000.0

COMMENT = re.compile(r"/\*.*?\*/", re.S)
DECL = re.compile(r"([-a-zA-Z][-a-zA-Z0-9]*)\s*:\s*([^;{}]*[^;{}\s])\s*(?=[;}])")
MATH = re.compile(r"\b(?:min|max|clamp)\s*\(", re.I)
NUM = re.compile(r"(-?\d*\.?\d+)([a-z%]*)", re.I)
FUNC = re.compile(r"(calc|min|max|clamp|var)\s*\(", re.I)

# A rem is the ROOT font size and this script resolves it at the browser
# default, which is what every px gloss on layout.html is quoted at. A reader
# who has raised their default moves every rem arm and therefore moves the
# crossover; that is the point of writing an arm in rem, and it is why the
# table says "at a 16 px default" rather than stating the figure bare.
REM = 16.0

# Absolute units, in px.
ABS = {"px": 1.0, "rem": REM}
# Viewport units this script resolves. The dynamic and small/large variants are
# deliberately absent: dvh changes with the browser's own chrome, so a
# declaration carrying one has no fixed crossover height at all.
VIEWPORT = {"vw": "vw", "vh": "vh"}
# Units that make a declaration somebody else's axis or nobody's arithmetic.
CONTAINER = ("%", "cqw", "cqi", "cqh", "cqb", "cqmin", "cqmax")
# Any viewport-relative unit at all, including the ones this script declines to
# resolve — a dvh arm still swaps somewhere, it just does not swap at one fixed
# height, so a declaration carrying one is unread rather than out of scope.
VIEWPORT_UNIT = re.compile(r"\d\s*(?:s|l|d)?v(?:w|h|i|b|min|max)\b")


class Unresolved(Exception):
    """This script cannot say where — or whether — these arms swap."""


def strip_comments(text):
    """Blank out comments in place, so line numbers survive.

    Load-bearing rather than hygiene, for the same reason it is in
    check-breakpoints.py: tokens.css quotes whole clamp() declarations inside
    its own prose, and read as declarations they would be findings in the file
    that defines the rule.
    """
    return COMMENT.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


def form(c=0.0, vw=0.0, vh=0.0):
    return {"c": c, "vw": vw, "vh": vh}


# A node is one of
#   ("lin", form, source, is_plain_number)
#   ("min" | "max", [node, ...])
# and every tree of them is piecewise linear in each axis.


def combine(a, b, sign):
    """a + b, or a - b. Addition distributes into min() and max()."""
    if a[0] == "lin" and b[0] == "lin":
        joined = {k: a[1][k] + sign * b[1][k] for k in ("c", "vw", "vh")}
        text = "%s %s %s" % (a[2], "+" if sign > 0 else "-", b[2])
        return ("lin", joined, text, a[3] and b[3])
    if a[0] in ("min", "max"):
        return (a[0], [combine(x, b, sign) for x in a[1]])
    # Subtracting a min() gives a max(): the smallest thing taken away leaves
    # the largest thing behind.
    kind = b[0] if sign > 0 else ("max" if b[0] == "min" else "min")
    return (kind, [combine(a, x, sign) for x in b[1]])


def scale(node, k):
    """node * k. A negative factor turns a min() into a max()."""
    if node[0] == "lin":
        return ("lin", {x: node[1][x] * k for x in ("c", "vw", "vh")}, node[2], node[3])
    kind = node[0] if k > 0 else ("max" if node[0] == "min" else "min")
    return (kind, [scale(x, k) for x in node[1]])


def plain(node):
    """True when the node is a bare number — no unit anywhere."""
    return node[0] == "lin" and node[3]


class Parser:
    """calc()-grammar over min(), max(), clamp() and var()."""

    def __init__(self, text, tokens, depth=0):
        self.s = text
        self.i = 0
        self.tokens = tokens
        self.depth = depth

    def parse(self):
        node = self.expr()
        self.skip()
        if self.i < len(self.s):
            raise Unresolved()
        return node

    def skip(self):
        while self.i < len(self.s) and self.s[self.i].isspace():
            self.i += 1

    def expr(self):
        node = self.term()
        while True:
            self.skip()
            if self.i < len(self.s) and self.s[self.i] in "+-":
                op = self.s[self.i]
                self.i += 1
                node = combine(node, self.term(), 1 if op == "+" else -1)
            else:
                return node

    def term(self):
        node = self.factor()
        while True:
            self.skip()
            if self.i >= len(self.s) or self.s[self.i] not in "*/":
                return node
            op = self.s[self.i]
            self.i += 1
            other = self.factor()
            if op == "/":
                if not plain(other) or other[1]["c"] == 0:
                    raise Unresolved()
                node = scale(node, 1.0 / other[1]["c"])
            elif plain(other):
                node = scale(node, other[1]["c"])
            elif plain(node):
                node = scale(other, node[1]["c"])
            else:
                # A length times a length is an area, and CSS does not have
                # one; in practice this is a var() that did not resolve.
                raise Unresolved()

    def factor(self):
        self.skip()
        if self.i >= len(self.s):
            raise Unresolved()
        if self.s[self.i] == "(":
            self.i += 1
            node = self.expr()
            self.skip()
            if self.i < len(self.s) and self.s[self.i] == ")":
                self.i += 1
                return node
            raise Unresolved()
        match = FUNC.match(self.s, self.i)
        if match:
            name = match.group(1).lower()
            self.i = match.end()
            args = self.arguments()
            if name == "calc":
                return self.nested(args[0])
            if name == "var":
                key = args[0].strip()
                if key in self.tokens:
                    return self.nested(self.tokens[key])
                if len(args) > 1 and args[1].strip():
                    return self.nested(args[1])
                raise Unresolved()
            parts = [self.nested(a) for a in args]
            if name == "clamp":
                if len(parts) != 3:
                    raise Unresolved()
                low, value, high = parts
                return ("max", [low, ("min", [value, high])])
            if len(parts) < 2:
                return parts[0]
            return (name, parts)
        match = NUM.match(self.s, self.i)
        if match:
            self.i = match.end()
            value, unit = float(match.group(1)), match.group(2).lower()
            if unit == "":
                return ("lin", form(value), match.group(0), True)
            if unit in ABS:
                return ("lin", form(value * ABS[unit]), match.group(0), False)
            if unit in VIEWPORT:
                return ("lin", form(**{VIEWPORT[unit]: value / 100.0}),
                        match.group(0), False)
            raise Unresolved()
        raise Unresolved()

    def nested(self, text):
        # A token that resolves through another token resolves through this,
        # and a cycle would otherwise be an unbounded recursion rather than a
        # finding.
        if self.depth > 12:
            raise Unresolved()
        return Parser(text, self.tokens, self.depth + 1).parse()

    def arguments(self):
        out, depth, current = [], 0, ""
        while self.i < len(self.s):
            char = self.s[self.i]
            if char == "(":
                depth += 1
            elif char == ")":
                if depth == 0:
                    self.i += 1
                    out.append(current)
                    return out
                depth -= 1
            if char == "," and depth == 0:
                out.append(current)
                current = ""
                self.i += 1
                continue
            current += char
            self.i += 1
        raise Unresolved()


def evaluate(node, width, height):
    """The value, and the leaf that produced it."""
    if node[0] == "lin":
        return node[1]["c"] + node[1]["vw"] * width + node[1]["vh"] * height, node
    values = [evaluate(x, width, height) for x in node[1]]
    pick = min if node[0] == "min" else max
    return pick(values, key=lambda pair: pair[0])


def leaves(node, out=None):
    out = [] if out is None else out
    if node[0] == "lin":
        out.append(node)
    else:
        for child in node[1]:
            leaves(child, out)
    return out


def crossings(node, axis):
    """Every point on `axis` where the selected leaf changes.

    Swept rather than solved pairwise, because which pair is even in contention
    is itself a function of the axis — then solved exactly off the two leaves
    that swapped, so the figure published is arithmetic and not a sample.
    """
    fixed = 900.0
    def at(x):
        return evaluate(node, x, fixed) if axis == "vw" else evaluate(node, fixed, x)

    found, x = [], AXIS_LO
    _, previous = at(x)
    while x < AXIS_HI:
        x = min(x + 1.0, AXIS_HI)
        _, current = at(x)
        if current is not previous:
            a, b = previous[1], current[1]
            if abs(a[axis] - b[axis]) > 1e-12:
                point = (b["c"] - a["c"]) / (a[axis] - b[axis])
                if AXIS_LO <= point <= AXIS_HI:
                    found.append(round(point, 1))
            previous = current
    # A three-arm clamp can switch twice within one sample step at the same
    # point; the census publishes places, not transitions.
    return sorted(set(found))


def token_table():
    """Every custom property tokens.css defines once, at its own value.

    A property defined twice at two values — the fallback blocks at the foot of
    the file redefine a handful — resolves to whichever the cascade picks, so
    this script declines to guess and drops it. Anything reading one becomes an
    unresolvable, named on every run.
    """
    table, seen = {}, {}
    text = strip_comments((CSS / "tokens.css").read_text())
    for match in re.finditer(r"(--[-a-zA-Z0-9]+)\s*:\s*([^;{}]+);", text):
        name, value = match.group(1), " ".join(match.group(2).split())
        if name not in seen:
            seen[name] = value
            table[name] = value
        elif seen[name] is None or seen[name] == value:
            continue
        else:
            seen[name] = None
            table.pop(name, None)
    return table


VAR = re.compile(r"var\(\s*(--[-a-zA-Z0-9]+)\s*(?:,([^()]*(?:\([^()]*\)[^()]*)*))?\)")


def expand(value, tokens, depth=0):
    """Substitute var() textually, so a value can be asked what units it has.

    Only ever used to decide whether a declaration this script failed to parse
    could have had a viewport crossover at all. A declaration whose every arm
    resolves to a constant cannot, and counting it as a gap would make the
    census of what this script cannot read mostly noise.
    """
    if depth > 8 or "var(" not in value:
        return value
    def one(match):
        name, fallback = match.group(1), match.group(2)
        if name in tokens:
            return tokens[name]
        return fallback or ""
    return expand(VAR.sub(one, value), tokens, depth + 1)


def selector_of(text, index):
    """The nearest enclosing rule's prelude, at-rules stepped over."""
    depth, i = 0, index
    while i > 0:
        i -= 1
        char = text[i]
        if char == "}":
            depth += 1
        elif char == "{":
            if depth:
                depth -= 1
                continue
            start = max(text.rfind("}", 0, i), text.rfind("{", 0, i),
                        text.rfind(";", 0, i)) + 1
            prelude = " ".join(text[start:i].split())
            if prelude.startswith("@"):
                continue
            return prelude
    return ":root"


class Reading:
    """One declaration, and what this script could make of it."""

    def __init__(self, sheet, line, selector, prop, value, kind, points=(), axis=""):
        self.sheet = sheet
        self.line = line
        self.selector = selector
        self.prop = prop
        self.value = value
        self.kind = kind        # crossover | two-axes | container | unresolvable
        self.points = list(points)
        self.axis = axis        # vw | vh

    @property
    def where(self):
        return "%s:%d" % (self.sheet, self.line)

    @property
    def declaration(self):
        return "%s: %s" % (self.prop, self.value)

    def key(self):
        return (self.axis, self.points[0] if self.points else 0.0,
                self.selector, self.prop)


def read_all():
    tokens = token_table()
    crossovers, other = [], []
    for sheet in SHIPPING:
        text = strip_comments((CSS / sheet).read_text())
        for match in DECL.finditer(text):
            prop, raw = match.group(1), match.group(2)
            if not MATH.search(raw):
                continue
            value = " ".join(raw.split())
            line = text.count("\n", 0, match.start()) + 1
            selector = selector_of(text, match.start())
            args = (sheet, line, selector, prop, value)

            try:
                node = Parser(value, tokens).parse()
            except (Unresolved, RecursionError):
                # Classify the failure by what the value is actually made of,
                # once every var() it names has been substituted in.
                full = expand(value, tokens).lower()
                if any(u in full for u in CONTAINER):
                    other.append(Reading(*args, kind="container"))
                elif VIEWPORT_UNIT.search(full):
                    other.append(Reading(*args, kind="unresolvable"))
                else:
                    # No arm is measured against the viewport, so there is no
                    # width at which this one swaps: a progress clamp, or a
                    # pair of constants. Out of scope rather than unread.
                    other.append(Reading(*args, kind="no-viewport"))
                continue
            if node[0] == "lin":
                continue
            arms = leaves(node)
            wide = any(leaf[1]["vw"] for leaf in arms)
            tall = any(leaf[1]["vh"] for leaf in arms)
            if not (wide or tall):
                # A unitless clamp: a progress value, not a length.
                continue
            if wide and tall:
                other.append(Reading(*args, kind="two-axes"))
                continue
            axis = "vw" if wide else "vh"
            points = crossings(node, axis)
            if not points:
                # Arms that never swap inside the window: a clamp whose middle
                # arm is dead, which is a fluid value that is not fluid.
                other.append(Reading(*args, kind="inert", axis=axis))
                continue
            crossovers.append(Reading(*args, kind="crossover", points=points, axis=axis))
    crossovers.sort(key=Reading.key)
    other.sort(key=lambda r: (r.kind, r.sheet, r.line))
    return crossovers, other


def figure(x):
    return ("%.1f" % x).rstrip("0").rstrip(".")


def rows_of(crossovers):
    """The table's cells: (selector, declaration, crossover).

    Three columns rather than two, and the split is not cosmetic. docs.css
    holds every first-column <code> on one line — a key broken at one of its
    own hyphens reads as two keys — and the lane that wrote that rule counted
    the result: "0 of 225 tables overflow at 1280". A declaration value is not
    a key; it is 90 characters of calc() that has to be allowed to wrap. So the
    selector takes the first column, where the guarantee belongs, and the value
    takes the second, where it can break.
    """
    rows = []
    for r in crossovers:
        where = "wide" if r.axis == "vw" else "tall"
        points = ", ".join("%s px" % figure(p) for p in r.points)
        rows.append((r.selector, r.declaration, "%s %s" % (points, where)))
    return rows


def stamp_of(rows):
    return hashlib.sha256(repr(rows).encode()).hexdigest()[:8]


TABLE = re.compile(
    r'(<table class="docs-table" id="crossover-census">.*?<tbody>)(.*?)(</tbody>)',
    re.S,
)
STAMP = re.compile(r'(<code id="crossover-stamp">)[0-9a-f]{8}(</code>)')


def published():
    html = LAYOUT.read_text()
    table = TABLE.search(html)
    stamp = STAMP.search(html)
    if not table or not stamp:
        return None, None
    body = table.group(2)
    cells = re.findall(
        r"<tr><td><code>(.*?)</code></td><td><code>(.*?)</code></td>"
        r"<td><strong>(.*?)</strong></td></tr>", body)
    return stamp.group(0)[len(stamp.group(1)):-len(stamp.group(2))], cells


def write(rows, stamp):
    html = LAYOUT.read_text()
    body = "\n" + "\n".join(
        "        <tr><td><code>%s</code></td><td><code>%s</code></td>"
        "<td><strong>%s</strong></td></tr>" % row
        for row in rows
    ) + "\n      "
    html = TABLE.sub(lambda m: m.group(1) + body + m.group(3), html, count=1)
    html = STAMP.sub(lambda m: m.group(1) + stamp + m.group(2), html, count=1)
    LAYOUT.write_text(html)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fix", action="store_true",
                    help="rewrite the census table and its stamp in layout.html")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print every declaration read, not only the findings")
    args = ap.parse_args()

    crossovers, other = read_all()
    rows = rows_of(crossovers)
    stamp = stamp_of(rows)

    if args.verbose:
        print("CROSSOVERS — %d declarations, %d places" % (
            len(crossovers), sum(len(r.points) for r in crossovers)))
        for r in crossovers:
            print("  %-22s %-30s %-22s %s" % (
                r.where, r.selector[:30], r.prop,
                ", ".join("%s px %s" % (figure(p), "wide" if r.axis == "vw" else "tall")
                          for p in r.points)))
        print("\nNOT READ — %d declarations" % len(other))
        for r in other:
            print("  %-13s %-22s %s: %s" % (r.kind, r.where, r.prop, r.value[:52]))
        print()

    if args.fix:
        write(rows, stamp)
        print("layout.html rewritten: %d rows, stamp %s" % (len(rows), stamp))
        return 0

    doc_stamp, doc_rows = published()
    if doc_rows is None:
        print("foundations/layout.html carries no crossover census "
              "(#crossover-census / #crossover-stamp). Run --fix.")
        return 1

    faults = []
    if doc_stamp != stamp:
        faults.append("layout.html publishes stamp %s; the shipping CSS measures %s."
                      % (doc_stamp, stamp))
    have, want = set(doc_rows), set(rows)
    for row in sorted(want - have):
        faults.append("  live, unpublished:   %s %s  ->  %s" % row)
    for row in sorted(have - want):
        faults.append("  published, not live: %s %s  ->  %s" % row)

    if faults:
        print("The crossover census has drifted from the shipping CSS.\n")
        print("\n".join(faults))
        print("\n    python3 scripts/check-fluid-crossovers.py --fix")
        return 1

    print("%d crossovers in %d declarations, all published; %d declarations "
          "named as unread. Stamp %s." % (
              sum(len(r.points) for r in crossovers), len(crossovers),
              len(other), stamp))
    return 0


if __name__ == "__main__":
    sys.exit(main())
