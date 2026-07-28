#!/usr/bin/env python3
"""An anchor that does not resolve is not an error. It is a silent relayout.

The fortieth check, and the first about a CSS feature whose failure mode is
that nothing fails. Every other positioning mistake in this repository showed
up as a wrong number in a measurement. `anchor()` does not: when the reference
cannot be resolved, the declaration behaves as `auto` and the element falls back
to its STATIC position -- wherever it happened to sit in flow -- and renders
perfectly, in the wrong place, with no console warning and no layout error.

WHAT IT COST TO LEARN THIS. patterns/landing-page.html places the "Was wir
machen" section header off .lp-flow's box, so that the title's hairline is the
drawing's own horizon rather than a rule in the column beside it. Two separate
resolution failures, both found only by screenshotting:

  1. THE CONTAINING BLOCK. An anchor is only ACCEPTABLE to a positioned element
     whose containing block is the initial containing block, or is an ancestor
     of the anchor. Giving the header's wrapper `position: relative` -- an
     ordinary thing to do, and done to get a sane percentage basis -- made
     .lp-flow unacceptable, and every anchor() in the rule fell back at once.
     The header dropped 250 px to its static position and drew a full-measure
     hairline through the middle of the root.

  2. A NAME THAT IS NEVER DECLARED does exactly the same thing, and a typo in a
     dashed ident is the cheapest way to write one. There is nothing to see:
     the element renders, in flow, as though the rule had not been written.

WHAT IS CHECKED, over the shipping surface -- design-system/**/*.html and the
three stylesheets that ship:

  1. RESOLUTION. Every --name used in anchor() or anchor-size() is declared by
     some `anchor-name:` in the same file or in the shipping stylesheets. This
     is check-class-provenance.py's question asked of a different namespace: a
     reference nothing declares looks exactly like one that resolves.

  2. NO DEAD ANCHORS. Every declared anchor-name is referenced somewhere. An
     anchor-name nobody positions against is a promise about an element's role
     that the next edit will quietly break.

  3. GUARDED. Every rule that uses anchor() or anchor-size() sits inside an
     @supports whose prelude tests the feature. Because the fallback is silent,
     an unguarded use does not degrade -- it MISPLACES. In a browser without
     anchor positioning the element lands at its static position, which is a
     place nobody chose and nobody has looked at.

The three together are the difference between "the anchor moved" (visible on
the next screenshot) and "the anchor stopped existing" (visible on nobody's).

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-anchor-positioning.py       # exit 1 on a finding
    python3 scripts/check-anchor-positioning.py -v    # list every name and use
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
SHIPPING_CSS = ["tokens.css", "base.css", "components.css"]

# A dashed ident. anchor-name also takes `none`, which is not a name.
NAME = r"--[A-Za-z0-9_-]+"
DECL_RE = re.compile(rf"anchor-name\s*:\s*([^;}}]+)")
USE_RE = re.compile(rf"\banchor(?:-size)?\(\s*({NAME})")
# <style> bodies, so page markup and documentation prose are not read as CSS.
STYLE_RE = re.compile(r"<style\b[^>]*>(.*?)</style>", re.S)
COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
SUPPORTS_RE = re.compile(r"@supports\b([^{]*)\{", re.I)


def css_of(path):
    """The CSS in a file: the whole file for .css, the <style> bodies for HTML."""
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".css":
        return text
    return "\n".join(STYLE_RE.findall(text))


def blank(text):
    return re.sub(r"[^\n]", " ", text)


def strip_comments(css):
    """Blank out comments, keeping newlines so line numbers survive."""
    return COMMENT_RE.sub(lambda m: blank(m.group(0)), css)


def mask_preludes(css):
    """Blank out @supports preludes, keeping offsets.

    A feature query names the property and the function it is testing FOR —
    `@supports (anchor-name: --a) and (top: anchor(--a bottom))` — so read
    literally it is both a declaration of --a and an unguarded use of it. It is
    neither: nothing in a prelude paints. The guard walk still reads the real
    text; only the census is masked.
    """
    out = list(css)
    for m in SUPPORTS_RE.finditer(css):
        for i in range(m.start(), m.end()):
            if out[i] != "\n":
                out[i] = " "
    return "".join(out)


def guarding_supports(css, index):
    """The @supports preludes open around a character offset, outermost first.

    A brace walk rather than a parser: this file's CSS is hand-written and
    nests at-rules only, so tracking which @supports preludes are still open at
    a given offset is exactly a stack of braces.
    """
    stack, open_supports = [], []
    i = 0
    while i < index and i < len(css):
        c = css[i]
        if c == "{":
            m = None
            # walk back to the start of this block's prelude
            start = max(css.rfind("}", 0, i), css.rfind("{", 0, i)) + 1
            prelude = css[start:i].strip()
            if prelude.lower().startswith("@supports"):
                m = prelude
            stack.append(m)
            if m:
                open_supports.append(m)
        elif c == "}":
            if stack:
                m = stack.pop()
                if m and open_supports and open_supports[-1] == m:
                    open_supports.pop()
        i += 1
    return open_supports


def line_of(text, index):
    return text.count("\n", 0, index) + 1


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    files = sorted(DS.rglob("*.html"))
    files += [DS / "assets" / "css" / n for n in SHIPPING_CSS]

    declared = {}   # name -> [(file, line)]
    used = {}       # name -> [(file, line, guarded)]
    findings = []

    for path in files:
        if not path.exists():
            continue
        css = strip_comments(css_of(path))
        census = mask_preludes(css)
        rel = path.relative_to(ROOT)

        for m in DECL_RE.finditer(census):
            for name in re.findall(NAME, m.group(1)):
                declared.setdefault(name, []).append((rel, line_of(css, m.start())))

        for m in USE_RE.finditer(census):
            name = m.group(1)
            preludes = guarding_supports(css, m.start())
            guarded = any("anchor" in p.lower() for p in preludes)
            used.setdefault(name, []).append((rel, line_of(css, m.start()), guarded))
            if not guarded:
                findings.append(
                    f"{rel}:{line_of(css, m.start())}  anchor({name}) is not inside an "
                    f"@supports that tests anchor positioning — where it is unsupported "
                    f"it does not degrade, it lands at the static position")

    for name, uses in sorted(used.items()):
        if name not in declared:
            where = ", ".join(f"{f}:{l}" for f, l, _ in uses)
            findings.append(f"{name} is positioned against but never declared "
                            f"as an anchor-name — used at {where}")

    for name, decls in sorted(declared.items()):
        if name not in used:
            where = ", ".join(f"{f}:{l}" for f, l in decls)
            findings.append(f"{name} is declared as an anchor-name and nothing "
                            f"positions against it — declared at {where}")

    if args.verbose:
        print(f"{len(declared)} anchor name(s) declared, {len(used)} referenced")
        for name in sorted(set(declared) | set(used)):
            d = ", ".join(f"{f}:{l}" for f, l in declared.get(name, [])) or "—"
            for f, l, g in used.get(name, []):
                print(f"  {name:<28} declared {d:<44} used {f}:{l} "
                      f"{'guarded' if g else 'UNGUARDED'}")
            if name not in used:
                print(f"  {name:<28} declared {d:<44} used nowhere")

    if findings:
        print(f"\n{len(findings)} finding(s):", file=sys.stderr)
        for f in findings:
            print(f"  {f}", file=sys.stderr)
        return 1

    print(f"anchor positioning: {len(used)} reference(s) resolve, all guarded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
