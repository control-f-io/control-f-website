#!/usr/bin/env python3
"""The two pages that publish a census of the isometric figures, held to the tree.

TWO CHAPTERS COUNT THE SAME FIGURES AND NEITHER OF THEM COUNTED THEM.
foundations/illustration.html#where publishes "Where illustrations go" -- the
whole shipping tree, one row per group, with a frame and a verdict on each.
foundations/motion.html#assembly publishes the other half of the same census:
which of those figures assemble as they are scrolled to, and on whose timeline.
Both are hand-typed tables over a set that four routines add to, and both had
gone stale in the way a hand-typed census always goes stale -- not by saying
something false about a figure it lists, but by not listing one at all.

WHAT WAS FOUND WHEN THE TREE WAS FINALLY COUNTED, and every one of these is a
claim below rather than a paragraph:

  1. THE FOUR EXPERTISE OBJECTS WERE IN NEITHER OF motion.html's TABLES. They
     are the largest drawings in the system -- 93 to 337 elements each, four
     different frames -- they assemble, and they assemble on a mechanism the
     chapter documents nowhere else: patterns/expertise.html re-times them onto
     the track's own --cf-pin, with a data-stage attribute where a
     .cf-iso--build carries --stage. The roster over them read "the eight
     objects ... Seven of the eight objects assemble". Eight was never the
     number of anything: illustration.html was counting fifteen on the same day,
     in seven rows, one of which is the four this one had lost.

  2. THE STATEMENT FIGURE'S FRAME WAS PUBLISHED AS 480 AND THE DRAWING IS 1200
     UNITS WIDE. components.css derives its arrival from exactly that width and
     says so at the declaration -- "This figure is 1200 units wide wherever it
     is used, so it takes 1200/40" -- so the stylesheet and the census disagreed
     by a factor of 2.5 on the one figure the census names first.

  3. AND IT IS NOT ON THE SHIPPING LANDING PAGE AT ALL. The row read "Landing
     page - statement". patterns/landing-page.html carries no .cf-iso statement
     figure: its statement drawing is .lp-flow, act 2's root, 1200 x 620,
     written by scripts/expertise-objects/gen-flow-root.py and outside the
     .cf-iso vocabulary entirely. The 1200-unit .cf-iso figure the row
     describes lives on components/statement.html and in the prototype. A
     census of the shipping tree was counting a figure the shipping tree does
     not have.

WHY THIS IS A SCRIPT. Every one of those three is invisible in a rendering:
each names a figure that is *missing from a table*, and a missing row renders as
a table. They are also invisible to every other check in this directory --
check-iso-motion.py reads the stylesheets and the markup and is right about both,
which is precisely why the drift could sit in the prose for releases. The set is
derivable, so the table is derived: run with --fix and motion.html's roster is
rewritten from the tree, the same standing check-glass-budget.py's census has.

WHAT A FIGURE IS, and the one rule that is not a class name. A figure is an
<svg> under design-system/patterns/ whose class list carries cf-iso -- except
that TWO SUCH SVGS SHARING A PARENT ARE ONE FIGURE, drawn in stacked layers.
patterns/404.html is the case: .cf-construct__work draws the brand-angle rays
over .cf-construct__figure, two elements, one drawing, and the page's own
comment says so where it reaches both with `.cf-annot-fig > svg`. Counting them
as two would put the shipping tree at fifteen figures and thirteen objects and
give the two chapters two different totals to drift apart on.

The four columns of the roster, all of them read rather than written:

  Page       the file. A link, so a missing group is a missing link.
  Figures    how many share the row's signature.
  Frame      the viewBox width. The unit --iso-travel is derived in, and the
             number claim 2 above was wrong about.
  Assembles  whether any layer of the figure carries a cf-iso__ part class.
             The part classes are the assembly -- components.css animates
             nothing else -- so this is the mechanism and not a description
             of it.
  Timeline   view() when the figure rides its own view timeline, --cf-pin when
             an ancestor is a .cf-pin__step and the track scrubs it instead.

THE CLAIMS

  1  motion.html's #assembly-roster is the table this script generates.
  2  The two counts in the paragraph over it -- the total, and how many of them
     assemble -- are the derived numbers, spelled.
  3  illustration.html#where's census totals the same figures: the word in the
     sentence over the table, the row counts under it, and the ordinal in the
     sentence that sends the next page elsewhere.
  4  Every number in that census's Frame column is a frame the tree actually
     draws, and every frame the tree draws is named in it. That is claim 2 of
     the header, in the form that also catches a drawing being re-framed.

Exit 0 when all four hold, 1 otherwise. --fix rewrites claim 1's table.
"""

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = ROOT / "design-system" / "patterns"
MOTION = ROOT / "design-system" / "foundations" / "motion.html"
ILLUSTRATION = ROOT / "design-system" / "foundations" / "illustration.html"

WORDS = {
    1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
    7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven",
    12: "twelve", 13: "thirteen", 14: "fourteen", 15: "fifteen",
    16: "sixteen", 17: "seventeen", 18: "eighteen", 19: "nineteen",
    20: "twenty",
}
ORDINALS = {
    2: "second", 3: "third", 4: "fourth", 5: "fifth", 6: "sixth",
    7: "seventh", 8: "eighth", 9: "ninth", 10: "tenth", 11: "eleventh",
    12: "twelfth", 13: "thirteenth", 14: "fourteenth", 15: "fifteenth",
    16: "sixteenth", 17: "seventeenth", 18: "eighteenth", 19: "nineteenth",
    20: "twentieth",
}


def word(n):
    return WORDS.get(n, str(n))


def ordinal(n):
    return ORDINALS.get(n, "%dth" % n)


def num(x):
    """A frame as the census writes it: 640, not 640.0, and 657.6 kept."""
    return ("%.4f" % x).rstrip("0").rstrip(".")


class Figures(HTMLParser):
    """Every svg.cf-iso in one page, with the stack it hangs from.

    convert_charrefs is left on: nothing here reads text, only attributes, and
    the pages carry entities in their prose that would otherwise arrive split.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []            # [(tag, classes, id)] of open elements
        self.layers = []           # one per svg.cf-iso
        self.depth = None          # stack depth of the svg being read
        self.current = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = a.get("class", "").split()
        if tag == "svg" and "cf-iso" in classes:
            # HTMLParser lower-cases attribute names, so the camel-case SVG
            # attribute arrives as `viewbox`. Reading it under the name the
            # markup writes silently gives every figure a frame of 0.
            box = (a.get("viewbox") or a.get("viewBox") or "").split()
            width = float(box[2]) if len(box) == 4 else 0.0
            # The parent is the element the svg hangs from; two svgs sharing one
            # are one drawing in stacked layers. It is identified by its position
            # in the document rather than by a class, because .cf-annot-fig is
            # one page's answer and the rule is about the tree.
            self.current = {
                "width": width,
                "parent": self.stack[-1][3] if self.stack else -1,
                "pinned": any("cf-pin__step" in c for _, c, _, _ in self.stack),
                "parts": False,
                "order": len(self.layers),
            }
            self.layers.append(self.current)
            self.depth = len(self.stack)
        elif self.current is not None and any(
            c.startswith("cf-iso__") for c in classes
        ):
            self.current["parts"] = True
        if tag not in ("br", "img", "input", "meta", "link", "hr",
                       "source", "use", "path", "circle", "ellipse",
                       "line", "rect", "polygon", "polyline", "stop",
                       "col", "area", "track", "wbr"):
            self.stack.append((tag, classes, a.get("id"), self.getpos()[0]))

    def handle_startendtag(self, tag, attrs):
        a = dict(attrs)
        classes = a.get("class", "").split()
        if self.current is not None and any(
            c.startswith("cf-iso__") for c in classes
        ):
            self.current["parts"] = True

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                if self.depth is not None and i <= self.depth:
                    self.current = None
                    self.depth = None
                del self.stack[i:]
                return


def read_tree():
    """The shipping tree's figures, in document order, layers collapsed."""
    figures = []
    for page in sorted(PATTERNS.glob("*.html")):
        p = Figures()
        p.feed(page.read_text(encoding="utf-8"))
        by_parent = {}
        order = []
        for layer in p.layers:
            key = layer["parent"]
            if key not in by_parent:
                by_parent[key] = {
                    "page": page,
                    "width": layer["width"],
                    "pinned": layer["pinned"],
                    "parts": layer["parts"],
                }
                order.append(key)
            else:
                f = by_parent[key]
                f["width"] = max(f["width"], layer["width"])
                f["parts"] = f["parts"] or layer["parts"]
                f["pinned"] = f["pinned"] or layer["pinned"]
        figures.extend(by_parent[k] for k in order)
    return figures


def rows(figures):
    """One row per (page, frame, assembles, timeline), in document order."""
    out = []
    index = {}
    for f in figures:
        key = (f["page"].name, num(f["width"]), f["parts"], f["pinned"])
        if key in index:
            out[index[key]]["count"] += 1
        else:
            index[key] = len(out)
            out.append({
                "page": f["page"].name,
                "frame": num(f["width"]),
                "assembles": f["parts"],
                "pinned": f["pinned"],
                "count": 1,
            })
    return out


def roster_html(table_rows):
    body = []
    for r in table_rows:
        if not r["assembles"]:
            timeline = "&mdash;"
        elif r["pinned"]:
            # A pin is a breakpoint, not a state: the same markup rides its own
            # view timeline in the stacked tier and is scrubbed off the track's
            # once the section pins. Both are true of the figure, so both are
            # named. → the pinned track, below.
            timeline = ("its own <code>view()</code>, or the track&rsquo;s "
                        "<code>--cf-pin</code> where the section pins")
        else:
            timeline = "its own <code>view()</code>"
        body.append(
            '        <tr><td><a href="../patterns/%s"><code>patterns/%s</code></a></td>'
            "<td>%d</td><td>%s</td><td>%s</td><td>%s</td></tr>"
            % (r["page"], r["page"], r["count"], r["frame"],
               "yes" if r["assembles"] else "no", timeline)
        )
    return (
        '<table class="docs-table" id="assembly-roster">\n'
        "      <thead>\n"
        "        <tr><th>Page</th><th>Figures</th><th>Frame</th>"
        "<th>Assembles</th><th>Timeline</th></tr>\n"
        "      </thead>\n"
        "      <tbody>\n"
        "%s\n"
        "      </tbody>\n"
        "    </table>" % "\n".join(body)
    )


ROSTER = re.compile(
    r'<table class="docs-table" id="assembly-roster">.*?</table>', re.S
)
CELL = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.S)
ROW = re.compile(r"<tr>(.*?)</tr>", re.S)


def text_of(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html)).strip()


def census_rows(html):
    """The rows of illustration.html#where, as (label, frame) pairs."""
    m = re.search(
        r'<h3 id="where">.*?<table class="docs-table">(.*?)</table>', html, re.S
    )
    if not m:
        return None
    out = []
    for row in ROW.finditer(m.group(1)):
        cells = [text_of(c) for c in CELL.findall(row.group(1))]
        if len(cells) == 4 and cells[0] != "Where":
            out.append((cells[0], cells[2]))
    return out


def main():
    fix = "--fix" in sys.argv
    figures = read_tree()
    table_rows = rows(figures)
    total = len(figures)
    assembling = sum(1 for f in figures if f["parts"])
    findings = []

    # ---- claim 1: motion.html's roster is the table generated from the tree.
    motion = MOTION.read_text(encoding="utf-8")
    want = roster_html(table_rows)
    found = ROSTER.search(motion)
    if not found:
        findings.append(
            'foundations/motion.html: no <table id="assembly-roster">. The '
            "roster is generated -- paste the block this script writes."
        )
    elif found.group(0) != want:
        if fix:
            motion = motion[: found.start()] + want + motion[found.end():]
            MOTION.write_text(motion, encoding="utf-8")
            print("  foundations/motion.html  #assembly-roster rewritten "
                  "from the tree")
        else:
            findings.append(
                "foundations/motion.html #assembly-roster is not the tree's "
                "roster. Run: python3 scripts/check-figure-roster.py --fix"
            )

    # ---- claim 2: the counts in the paragraph over it.
    for phrase, why in (
        ("the %s figures" % word(total),
         "the total the roster lists"),
        ("%s of the %s assemble" % (word(assembling).capitalize(), word(total)),
         "how many of them assemble"),
    ):
        if phrase not in motion:
            findings.append(
                'foundations/motion.html: expected "%s" (%s) in the paragraph '
                "over #assembly-roster." % (phrase, why)
            )

    # ---- claims 3 and 4: illustration.html's census.
    ill = ILLUSTRATION.read_text(encoding="utf-8")
    census = census_rows(ill)
    if census is None:
        findings.append(
            "foundations/illustration.html: no census table under #where."
        )
    else:
        counted = 0
        for label, _frame in census:
            m = re.search(r"×\s*(\d+)", label)
            counted += int(m.group(1)) if m else 1
        if counted != total:
            findings.append(
                "foundations/illustration.html #where: the rows count %d "
                "figure(s); the shipping tree draws %d. A whole group is "
                "missing from the census or one it names is gone."
                % (counted, total)
            )
        for phrase, why in (
            ("shipping tree holds %s of them" % word(total), "the total"),
            ("wants a %s object" % ordinal(total + 1),
             "the ordinal of the next one"),
        ):
            if phrase not in ill:
                findings.append(
                    'foundations/illustration.html: expected "%s" (%s).'
                    % (phrase, why)
                )
        drawn = {num(f["width"]) for f in figures}
        named = set()
        for _label, frame in census:
            named.update(re.findall(r"\d+(?:\.\d+)?", frame))
        for f in sorted(named - drawn, key=float):
            findings.append(
                "foundations/illustration.html #where: the Frame column names "
                "%s and no figure in the shipping tree is drawn in it." % f
            )
        for f in sorted(drawn - named, key=float):
            findings.append(
                "foundations/illustration.html #where: the tree draws a figure "
                "in a %s frame and the Frame column never names it." % f
            )

    if findings:
        print("figure roster: %d finding(s)\n" % len(findings))
        for f in findings:
            print("  - %s\n" % f)
        return 1

    print(
        "figure roster: %d figures in the shipping tree, %d of them assembling, "
        "%d roster row(s); the census totals the same figures and every frame "
        "it names is one the tree draws."
        % (total, assembling, len(table_rows))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
