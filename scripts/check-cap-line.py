#!/usr/bin/env python3
"""Hold the cap line: every text-box trim in the system says exactly what it trims.

A line of type is not a line. It is a line BOX, and the slot under the
baseline that carries the descenders belongs to it, so a padding measured
from the bottom of that box is the token PLUS a slice of the font that no
token names. Measured on this system — Chromium 141, 1280 px, every
.cf-section-header on all eighteen pattern pages — `padding-bottom:
var(--space-3)` drew 16.94 px of air under 39 labels and 17.63 px under the
fortieth, under a comment that says every section opens on the same axis.
The slot scales with the font size and the leading, and a section header
chooses neither.

`text-box-trim` removes that slot, which is what makes the number in the
stylesheet the number on the screen. It is also the first property in this
system whose CORRECT USE AND ITS WORST MISUSE ARE THE SAME DECLARATION with
one value left off, and every one of those failures renders perfectly:

  1. EDGE STATED IN THE SAME RULE. `text-box-edge` initial is `auto`, and
     `auto` means "whatever this font's own over/under metrics say". The
     display face of this brand is not licensed yet and falls back to Geist
     (design-system/README.md, "Open before launch"), so a drawing left to
     the font's metrics is a drawing that moves on the day the licence
     lands. Trim without an edge is a distance nobody wrote down.

  2. BOTH EDGES, NEVER ONE. `text-box-edge: cap` is legal and means
     `cap text` — the under edge falls back to `text`, which is the font's
     own descent, which is the slot the trim was reached for in order to
     remove. A one-value edge beside `trim-end` therefore trims nothing at
     all and reads, in the file, exactly like the rule that works.

  3. INSIDE AN @supports BRANCH. A trim is never alone: it is paired with
     the padding that replaces the slot it took away (--space-3 became
     --space-4 on .cf-section-header, which is the drawn distance moved onto
     the space scale rather than changed). Outside the branch the trim
     applies where it is supported and the compensation does not, so the two
     halves of one decision come apart and the drawing tightens by the
     descent slot in every browser that understands it. Firefox shipped this
     in 154, Safari in 18.2, Chrome in 133; anything older has to keep
     today's drawing exactly, and the branch is what guarantees that.

  4. THE CENSUS IS THE STYLESHEETS' OWN LIST. foundations/capline.html
     publishes what is trimmed, and that table is generated here — the same
     device foundations/materials.html's glass census and
     foundations/layout.html's space scale use, and for the same reason: a
     list of selectors kept by hand is a list that is right on the day it is
     written. A fifth trimmed selector enters the table by existing.

None of the four is visible in a screenshot of a page that is right, which is
the whole test for what belongs in one of these scripts. Claim 2 is not even
visible in a screenshot of a page that is wrong: `cap` and `cap alphabetic`
are one character apart in the file and one drawing apart on the screen, and
the wrong one is the one that looks like nothing happened.

    python3 scripts/check-cap-line.py          # the four claims
    python3 scripts/check-cap-line.py -v       # every trim, and its context
    python3 scripts/check-cap-line.py --fix    # rewrite the census + stamp
"""

import argparse
import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS_DIR = ROOT / "design-system" / "assets" / "css"

# The same four the glass budget reads, and for the same reason: which
# stylesheets count as shipping was hand-maintained once and acts.css was
# missing from it for as long as acts.css existed.
SHIPPING_CSS = ("tokens.css", "base.css", "components.css", "acts.css")

CHAPTER = ROOT / "design-system" / "foundations" / "capline.html"
CENSUS_ID = "trim-census"

# The one edge pair this system trims to. `cap` is where a capital starts and
# `alphabetic` is the baseline it stands on — which is the same sentence
# foundations/found.html writes about an isometric object: it has no bounding
# box, it has a lattice edge under it.
EDGE = "cap alphabetic"

COMMENT = re.compile(r"/\*.*?\*/", re.S)


def strip_comments(text):
    """Blank out comments, keeping byte offsets so line numbers stay true."""
    return COMMENT.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


def walk_rules(text):
    """Yield (selector, at_rule_stack, declarations, line) for every style rule.

    A hand-rolled walk rather than a dependency: these scripts are stdlib
    only, because a build step is the thing this system does not have.
    """
    src = strip_comments(text)
    stack = []           # preludes of the open blocks, outermost first
    buf = []
    i = 0
    n = len(src)
    line = 1
    prelude_line = 1
    while i < n:
        c = src[i]
        if c == "\n":
            line += 1
            buf.append(c)
            i += 1
            continue
        if c == "{":
            prelude = " ".join("".join(buf).split())
            buf = []
            if prelude.startswith("@") and not prelude.startswith("@media print"):
                stack.append(("at", prelude, prelude_line))
                i += 1
                prelude_line = line
                continue
            if prelude.startswith("@"):
                stack.append(("at", prelude, prelude_line))
                i += 1
                prelude_line = line
                continue
            # A style rule. Read its declarations flat; a nested block inside
            # one is re-entered by the same loop.
            stack.append(("rule", prelude, prelude_line))
            decls = []
            j = i + 1
            depth = 0
            dbuf = []
            while j < n:
                ch = src[j]
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    if depth == 0:
                        break
                    depth -= 1
                elif ch == ";" and depth == 0:
                    decls.append("".join(dbuf).strip())
                    dbuf = []
                    j += 1
                    continue
                dbuf.append(ch)
                j += 1
            tail = "".join(dbuf).strip()
            if tail and ":" in tail:
                decls.append(tail)
            ats = [p for kind, p, _ in stack[:-1] if kind == "at"]
            yield prelude, ats, [d for d in decls if ":" in d], prelude_line
            stack.pop()
            # Past the rule's own closing brace, not into its body. The system
            # writes no nested style rules, so a block inside a declaration
            # list is not a case this has to re-enter.
            line += src.count("\n", i, j + 1)
            i = j + 1
            prelude_line = line
            continue
        if c == "}":
            if stack:
                stack.pop()
            buf = []
            i += 1
            prelude_line = line
            continue
        if c == ";" and not stack:
            buf = []
            i += 1
            prelude_line = line
            continue
        if not buf:
            prelude_line = line
        buf.append(c)
        i += 1


def collect():
    """Every shipping rule that declares text-box-trim, with its context."""
    trims = []
    for name in SHIPPING_CSS:
        path = CSS_DIR / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for selector, ats, decls, line in walk_rules(text):
            props = {}
            for d in decls:
                prop, _, value = d.partition(":")
                props[prop.strip().lower()] = value.strip()
            if "text-box-trim" not in props and "text-box" not in props:
                continue
            trims.append({
                "file": name,
                "line": line,
                "selector": selector,
                "ats": ats,
                "trim": props.get("text-box-trim", props.get("text-box", "")),
                "edge": props.get("text-box-edge", ""),
                "shorthand": "text-box" in props,
            })
    return trims


def supports_branch(ats):
    return any(a.startswith("@supports") and "text-box-trim" in a for a in ats)


def census_rows(trims):
    rows = []
    for t in trims:
        for sel in [s.strip() for s in t["selector"].split(",") if s.strip()]:
            rows.append((sel, t["file"], t["trim"], t["edge"]))
    return sorted(set(rows))


def stamp(rows):
    payload = "\n".join("|".join(r) for r in rows).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:8]


def render_census(rows):
    out = ['<tbody id="%s">' % CENSUS_ID]
    for sel, fname, trim, edge in rows:
        out.append(
            "        <tr><td><code>%s</code></td><td><code>%s</code></td>"
            "<td><code>%s</code></td><td><code>%s</code></td></tr>"
            % (sel, fname, trim, edge)
        )
    out.append("      </tbody>")
    return "\n".join(out)


CENSUS_RE = re.compile(
    r'<tbody id="%s">.*?</tbody>' % CENSUS_ID, re.S)
STAMP_RE = re.compile(r'(<code class="trim-stamp">)([0-9a-f]{8})(</code>)')


def check_chapter(rows, fix):
    """Claim 4 — the chapter's table is this list, and its stamp is this digest."""
    findings = []
    if not CHAPTER.exists():
        return ["the chapter foundations/capline.html is missing, and it is where\n"
                "    the census is published"]
    text = CHAPTER.read_text(encoding="utf-8")
    want_body = render_census(rows)
    want_stamp = stamp(rows)

    n_body = len(CENSUS_RE.findall(text))
    n_stamp = len(STAMP_RE.findall(text))
    if n_body != 1:
        return ['foundations/capline.html carries %d <tbody id="%s"> and must carry '
                "exactly one" % (n_body, CENSUS_ID)]
    if n_stamp < 1:
        return ['foundations/capline.html carries no <code class="trim-stamp">']

    new = CENSUS_RE.sub(lambda _m: want_body, text)
    new = STAMP_RE.sub(lambda m: m.group(1) + want_stamp + m.group(3), new)
    if new != text:
        if fix:
            CHAPTER.write_text(new, encoding="utf-8")
            print("capline.html rewritten: stamp %s, %d row(s)" % (want_stamp, len(rows)))
        else:
            findings.append(
                "foundations/capline.html's census is not the stylesheets' own list.\n"
                "    %d trimmed selector(s), stamp %s.\n"
                "    Run: python3 scripts/check-cap-line.py --fix" % (len(rows), want_stamp))
    return findings


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print every trim and the context it sits in")
    ap.add_argument("--fix", action="store_true",
                    help="rewrite the census and its stamp on capline.html")
    args = ap.parse_args()

    trims = collect()
    findings = []

    for t in trims:
        where = "%s:%d  %s" % (t["file"], t["line"], t["selector"])
        # 1. the edge is stated in the same rule
        if not t["edge"] and not t["shorthand"]:
            findings.append(
                "%s\n    trims without a text-box-edge. The initial is `auto` — the\n"
                "    font's own metrics — and the display face is not licensed yet, so\n"
                "    `auto` is a distance that moves on the day it lands. State `%s`."
                % (where, EDGE))
            continue
        edge = t["edge"] or " ".join(t["trim"].split()[1:])
        # 2. both edges
        parts = edge.split()
        if len(parts) != 2:
            findings.append(
                "%s\n    text-box-edge: %s — one value. The under edge then falls back to\n"
                "    `text`, which IS the descent slot this trim was reached for, so the\n"
                "    rule reads as a trim and draws as none. State `%s`."
                % (where, edge or "(none)", EDGE))
        elif edge != EDGE:
            findings.append(
                "%s\n    text-box-edge: %s. This system trims to `%s` — where a capital\n"
                "    starts and the baseline it stands on. A second pair is a second\n"
                "    drawing wearing the first one's name."
                % (where, edge, EDGE))
        # 3. inside the @supports branch
        if not supports_branch(t["ats"]):
            findings.append(
                "%s\n    is not inside an @supports (text-box-trim: …) block. The trim and\n"
                "    the padding that replaces the slot it removes are one decision; out\n"
                "    here the first half applies where it is supported and the second half\n"
                "    applies everywhere, and the drawing comes apart by the descent slot."
                % where)

    rows = census_rows(trims)
    findings += check_chapter(rows, args.fix)

    if args.verbose:
        print("trimmed rules: %d, selectors: %d, stamp %s" % (len(trims), len(rows), stamp(rows)))
        for t in trims:
            print("  %-16s %-4d %s" % (t["file"], t["line"], t["selector"]))
            print("      trim %-12s edge %-16s @supports %s"
                  % (t["trim"], t["edge"] or "(none)",
                     "yes" if supports_branch(t["ats"]) else "NO"))

    if findings:
        print("cap line: %d finding(s)\n" % len(findings))
        for f in findings:
            print("  - %s\n" % f)
        return 1

    print("cap line: %d trimmed rule(s), %d selector(s), every one at `%s` inside "
          "its @supports branch; capline.html's census is the stylesheets' own list "
          "(stamp %s)." % (len(trims), len(rows), EDGE, stamp(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
