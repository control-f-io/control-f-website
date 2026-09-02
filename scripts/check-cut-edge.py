#!/usr/bin/env python3
"""A crop that hides content says so, and it says nothing when it hides none.

foundations/cut.html states the law of the edge: a contour in this system is an
edge or a division and never decoration, and a crop is a third thing that had
no line. The five inline scroll boxes the system ships all drew their crop
exactly like the end of the drawing, which is the one thing it is not.

WHY THIS IS A SCRIPT AND NOT A SCREENSHOT, which is the test everything in this
directory has to pass. Three of the claims under the mark are invisible in a
rendering:

  1. THE ROSTER. Which boxes carry the cut is a fact about the stylesheet, and
     a roster kept by hand goes stale the day somebody writes the sixth scroll
     box -- which renders perfectly, crops silently, and is in no screenshot of
     anything that exists today. So the roster is READ OUT of the shipping
     stylesheets the way the glass budget reads what counts as glass: every
     rule declaring an inline-axis `overflow` of `auto` or `scroll` is a crop,
     and a crop is either in the cut block or carries an argument here.

  2. ONE ELEMENT CHILD. The mark gets its depth from a single-column grid, and
     the content is placed in that same cell explicitly -- because grid
     auto-placement skips a cell an explicitly placed item already holds, so a
     SECOND child would land in row 2, outside the cell the two marks cover.
     The page would still render: a second child simply stacks under a mark
     that stops short of it. Nothing about that reads as a fault.

  3. THE FALLBACK IS NOTHING. The whole argument for `scroll-state()` over the
     background-attachment pair every other system uses is that this mark can
     be ABSENT -- so the base tier must draw no mark at all, and the marks'
     `opacity: 0` must be raised by the container queries and by nothing else.
     A stray `opacity: 1` outside a query would ship a permanent vertical rule
     on every table in the system, and components/table.html bans that rule by
     name. On a browser without the query it would be the ONLY thing drawn.

The block axis is deliberately out of scope, and it is out of scope by
argument rather than by omission. Three boxes scroll vertically -- the phone
nav's open list, the consent panel and .cf-blog-grid--port's column -- and the
first two are panels whose whole height the reader chose to open, not crops of
a drawing. The third is a genuine block-axis cut and wants the same mark on a
different construction. It is named in foundations/cut.html rather than
half-covered here.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system" / "assets" / "css"

# The stylesheets that ship. docs.css is documentation chrome and is not one of
# them -- the same boundary check-grid-tracks.py draws, for the same reason.
SHIPPING = ["tokens.css", "base.css", "components.css", "acts.css"]

# An inline-axis crop that deliberately does not carry the mark, with the
# argument for it. A roster entry is a judgement; the roster itself is not.
EXEMPT = {
    ".cf-prose pre": (
        "A code block's crop is not at the box's edge. It draws its own solid "
        "frame on all four sides and holds --space-4 of padding inside it, so "
        "a mark stretched across the content box would stand 16 px in from the "
        "line the reader reads as the edge -- a rule inside the code rather "
        "than the edge of it. It is the one inline crop in the system whose "
        "port edge and drawn edge are not the same line."
    ),
}

MARK_PROPS = ("::before", "::after")


def strip_comments(text):
    """Blank out /* ... */ so a selector quoted in prose is not read as code."""
    return re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)


def rules(text):
    """(selector, body, offset) for every rule in a stylesheet, at any depth."""
    out = []
    depth_stack = []
    i = 0
    start = 0
    while i < len(text):
        c = text[i]
        if c == "{":
            head = text[start:i].strip()
            depth_stack.append((head, i + 1))
            start = i + 1
        elif c == "}":
            if depth_stack:
                head, body_start = depth_stack.pop()
                out.append((head, text[body_start:i], body_start))
            start = i + 1
        i += 1
    return out


def selectors(head):
    """The selector list of a rule head, or [] for an at-rule."""
    if head.startswith("@"):
        return []
    return [s.strip() for s in head.split(",") if s.strip()]


def main():
    verbose = "-v" in sys.argv
    findings = []
    notes = []

    components = (CSS / "components.css").read_text()
    bare = strip_comments(components)

    # ---------------------------------------------------------------- the block
    gate = "@supports (container-type: scroll-state)"
    if gate not in bare:
        findings.append(f"components.css: the cut block's gate `{gate}` is gone.")
        report(findings, notes, verbose)
        return 1
    gstart = bare.index(gate)
    # the gate's own braces
    depth = 0
    gend = None
    for i in range(bare.index("{", gstart), len(bare)):
        if bare[i] == "{":
            depth += 1
        elif bare[i] == "}":
            depth -= 1
            if depth == 0:
                gend = i
                break
    if gend is None:
        findings.append("components.css: the cut block's @supports gate never closes.")
        report(findings, notes, verbose)
        return 1
    block = bare[gstart:gend]

    # Which boxes the cut governs: every selector in the block that names a
    # container rather than one of its marks.
    cut = set()
    for head, _body, off in rules(block):
        for sel in selectors(head):
            base = sel.split("::")[0].strip()
            base = re.sub(r"\s*>\s*\*$", "", base).strip()
            if base:
                cut.add(base)
    notes.append(f"the cut governs {len(cut)} box(es): {', '.join(sorted(cut))}")

    # ------------------------------------------------------- 1. the roster
    inline_crops = {}
    for name in SHIPPING:
        path = CSS / name
        if not path.exists():
            continue
        text = strip_comments(path.read_text())
        for head, body, off in rules(text):
            if head.startswith("@"):
                continue
            decls = [d.strip() for d in body.split(";")]
            crops = False
            for d in decls:
                m = re.match(r"^overflow(-x|-inline)?\s*:\s*(.+)$", d, re.S)
                if not m:
                    continue
                axis, value = m.group(1), m.group(2).strip()
                value = " ".join(value.split())
                if axis is None:
                    # the shorthand: the first component is the inline axis
                    first = value.split()[0] if value.split() else ""
                    if first in ("auto", "scroll"):
                        crops = True
                elif value in ("auto", "scroll"):
                    crops = True
            if crops:
                line = text.count("\n", 0, off) + 1
                for sel in selectors(head):
                    inline_crops.setdefault(sel, []).append(f"{name}:{line}")

    for sel, where in sorted(inline_crops.items()):
        if sel in cut:
            notes.append(f"  crop {sel} ({', '.join(where)}) -- cut")
        elif sel in EXEMPT:
            notes.append(f"  crop {sel} ({', '.join(where)}) -- exempt: {EXEMPT[sel][:60]}...")
        else:
            findings.append(
                f"{', '.join(where)}: `{sel}` is an inline-axis crop and carries no cut "
                f"mark. Every box that hides a column behind its edge says so, or is "
                f"named in EXEMPT in this script with the argument for why it does not."
            )

    # A roster entry whose crop is gone is how the next stale roster hides.
    for sel in sorted(EXEMPT):
        if sel not in inline_crops:
            findings.append(
                f"EXEMPT names `{sel}`, which is no longer an inline-axis crop in any "
                f"shipping stylesheet. An exemption that outlives its subject is a "
                f"licence nobody is using and the next one hides behind it."
            )
    for sel in sorted(cut):
        if sel not in inline_crops:
            findings.append(
                f"components.css: the cut block governs `{sel}`, which no shipping "
                f"stylesheet declares as an inline-axis crop. A mark on a box that "
                f"cannot scroll is a rule that can never be raised and never removed."
            )

    # ------------------------------------------ 2. one element child, in the markup
    pages = sorted((ROOT / "design-system").rglob("*.html"))
    child_counts = 0
    for page in pages:
        if "/assets/source/" in str(page):
            continue
        html = page.read_text(errors="replace")
        for sel in sorted(cut):
            cls = sel.lstrip(".")
            if not re.match(r"^[a-z][a-z0-9_-]*$", cls):
                continue
            for m in re.finditer(r'<(\w+)([^>]*\bclass="[^"]*\b' + re.escape(cls) + r'\b[^"]*"[^>]*)>', html):
                tag = m.group(1)
                inner, ok = element_body(html, m.end(), tag)
                if not ok:
                    continue
                kids = len(re.findall(r"<([a-zA-Z][\w-]*)[\s/>]", strip_html_comments(inner))) and \
                    count_top_level_children(strip_html_comments(inner))
                child_counts += 1
                if kids != 1:
                    findings.append(
                        f"{page.relative_to(ROOT)}: a `{cls}` holds {kids} element children. "
                        f"The cut's marks cover one grid cell and the content is placed in it "
                        f"explicitly, so a second child auto-places into row 2 -- outside the "
                        f"depth the marks are drawn to, and renders as though nothing were wrong."
                    )
    notes.append(f"{child_counts} instance(s) of a cut box read in the markup")

    # ------------------------------------------------- 3. the fallback is nothing
    for head, body, off in rules(block):
        sels = selectors(head)
        if not sels or not any("::" in s for s in sels):
            continue
        m = re.search(r"\bopacity\s*:\s*([^;]+)", body)
        if not m:
            continue
        value = m.group(1).strip()
        if value != "0" and "@container scroll-state" not in enclosing_at_rules(block, off):
            findings.append(
                f"components.css: a cut mark sets `opacity: {value}` outside a "
                f"`@container scroll-state()` query. The mark's whole argument is that it "
                f"can be absent; raised anywhere else it is a permanent vertical rule on "
                f"every table in the system, and the only thing drawn on a browser without "
                f"the query."
            )

    # ----------------------------------------------- the dash is a line type
    if "repeating-linear-gradient" in block:
        for m in re.finditer(r"repeating-linear-gradient\((.*?)\)\s*;", block, re.S):
            body = " ".join(m.group(1).split())
            stops = re.findall(r"var\(--stroke-1\)|calc\(var\(--stroke-1\) \* 5\)", body)
            if len(stops) < 3:
                findings.append(
                    "components.css: the cut mark's dash is not written off --stroke-1. "
                    "It is the 1-4 rung of the presence ladder -- one unit of ink, four of "
                    "gap, the hairline each -- and a literal there is a fifth line type "
                    "nobody declared. → scripts/check-line-types.py"
                )
                break

    report(findings, notes, verbose)
    return 1 if findings else 0


def strip_html_comments(html):
    return re.sub(r"<!--.*?-->", "", html, flags=re.S)


VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}


def element_body(html, start, tag):
    """The inner HTML of the element whose start tag ended at `start`."""
    depth = 1
    i = start
    pat = re.compile(r"</?" + re.escape(tag) + r"(?=[\s/>])", re.I)
    while depth:
        m = pat.search(html, i)
        if not m:
            return "", False
        if html[m.start() + 1] == "/":
            depth -= 1
            if depth == 0:
                return html[start:m.start()], True
        else:
            end = html.find(">", m.end())
            if end == -1:
                return "", False
            if not html[end - 1] == "/":
                depth += 1
        i = m.end()
    return "", False


def count_top_level_children(inner):
    """Element children at depth 0 of a fragment."""
    n = 0
    depth = 0
    for m in re.finditer(r"<(/?)([a-zA-Z][\w-]*)([^>]*)>", inner):
        closing, name, attrs = m.group(1), m.group(2).lower(), m.group(3)
        selfclose = attrs.rstrip().endswith("/") or name in VOID
        if closing:
            depth -= 1
        else:
            if depth == 0:
                n += 1
            if not selfclose:
                depth += 1
    return n


def enclosing_at_rules(text, offset):
    """The at-rule preludes open at `offset`."""
    stack = []
    i = 0
    start = 0
    while i < offset and i < len(text):
        if text[i] == "{":
            stack.append(text[start:i].strip())
            start = i + 1
        elif text[i] == "}":
            if stack:
                stack.pop()
            start = i + 1
        i += 1
    return " ".join(s for s in stack if s.startswith("@"))


def report(findings, notes, verbose):
    if verbose:
        for n in notes:
            print(n)
    if findings:
        print("check-cut-edge: %d finding(s)" % len(findings))
        for f in findings:
            print("  - " + f)
    else:
        print("check-cut-edge: ok")


if __name__ == "__main__":
    sys.exit(main())
