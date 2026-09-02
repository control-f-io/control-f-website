#!/usr/bin/env python3
"""Refuse a forced-colours rule that fills a box whose paint was a texture.

Forced colours DISCARDS background-image. It does not repaint it, it does not
approximate it, it drops it — and acts.css says so out loud, in the note over
the map legend's own forced-colours block:

    The gradient on --asset goes too: a linear-gradient is a background
    image, forced-colors does not repaint it, and it would have been the one
    swatch here still wearing brand colour.

That sentence is right and it was written in one file. components.css broke it
in another, on a designed page, and the failure is invisible in every screenshot
nobody takes:

    @media (forced-colors: active) {
      .cf-plot--ground .cf-plot__set::before { background: CanvasText; }
    }

`background` is a SHORTHAND. It set background-color to the reader's ink and
reset background-image to none in the same declaration — on a box whose whole
paint was two repeating gradients drawing a hairline lattice, transparent
everywhere between the lines. So the plane did not come back in the reader's
ink. It became a solid slab of it: measured on patterns/landing-page.html's act
4, card 03, at 1440 x 900 with forced colours on a white Canvas, 392 x 56 px of
CanvasText across the whole figure, the four columns standing in a trench and
the shortest of them more than half swallowed.

THE DISTINCTION THIS FILE DRAWS is between an ink and a ground, and it is the
difference between a slab and an erasure.

  ink      CanvasText, ButtonText, LinkText, GrayText, ... A texture's box
           filled with the FOREGROUND is a slab where a drawing used to be.
           That is the finding, and it is what this file refuses.

  ground   Canvas, ButtonFace, Field, ... A texture's box filled with the
           BACKGROUND paints the page over itself. That is erasure, which is
           honest, and it is what .map__key-dot--asset does one line before it
           redraws itself as a CanvasText ring — the correct answer, kept
           passing on purpose.

WHAT A TEXTURE IS. A base rule paints one when its `background` shorthand or
its `background-image` longhand carries a gradient() or a url(), directly or
through a custom property whose own value does — the sheets define 26 such
properties and a rule reaching one is reaching a texture.

THE SUBJECT, NOT THE WHOLE SELECTOR. Rules are matched on their last compound
plus pseudo-element — `.cf-plot--ground .cf-plot__set::before` and
`.cf-plot__set::before` are the same subject — because the forced-colours
answer for a rule is routinely written at a different depth from the rule it
answers. The plot's two were written at the same depth; the next one need not
be.

WHAT IT DOES NOT CHECK, deliberately

  Whether the forced-colours answer is the RIGHT answer. `display: none` is
  what .cf-ground::before takes in base.css and what the plot takes now; a
  border is what .map__key-dot--asset takes. Both are outside this rule.

  A texture arriving from a stylesheet this file does not read. The four
  shipping sheets are the scope, the same four check-gradient-family.py holds.

  prototypes/ and the documentation sheets — docs.css and preview.css never
  ship, and the boundary is the one every other check in this directory draws.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-forced-texture.py       # check, exit 1 on a finding
    python3 scripts/check-forced-texture.py -v    # print what it read
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
SHEETS = [DS / "assets/css/tokens.css", DS / "assets/css/base.css",
          DS / "assets/css/components.css", DS / "assets/css/acts.css"]

# The CSS system colours that are a FOREGROUND. Filling a box with one of these
# is drawing; filling a texture's box with one is a slab.
INKS = {
    "canvastext", "buttontext", "linktext", "visitedtext", "activetext",
    "graytext", "highlighttext", "fieldtext", "marktext", "accentcolortext",
    "selecteditemtext", "buttonborder",
}

# The grounds, kept only so -v can say which side a rule landed on.
GROUNDS = {
    "canvas", "buttonface", "field", "highlight", "mark", "accentcolor",
    "selecteditem",
}

TEXTURE = re.compile(r"\bgradient\(|\burl\(")
VAR = re.compile(r"var\(\s*(--[\w-]+)")
IMPORTANT = re.compile(r"\s*!\s*important\s*$", re.I)


def strip_comments(text):
    """Blank out /* ... */ so a sentence about a colour is never a declaration.

    Newlines are kept so every line number this file reports is the real one.
    """
    out = []
    i = 0
    while i < len(text):
        start = text.find("/*", i)
        if start < 0:
            out.append(text[i:])
            break
        out.append(text[i:start])
        end = text.find("*/", start + 2)
        if end < 0:
            out.append("\n" * text.count("\n", start))
            break
        out.append("\n" * text.count("\n", start, end))
        i = end + 2
    return "".join(out)


def texture_properties(sources):
    """Custom properties whose own value carries a gradient or a url.

    Resolved to a fixed point: a property defined as another property's value
    is a texture when that one is.
    """
    values = {}
    for text in sources:
        for name, value in re.findall(r"(--[\w-]+)\s*:\s*([^;{}]*)", text):
            values.setdefault(name, []).append(value)
    names = set()
    changed = True
    while changed:
        changed = False
        for name, vs in values.items():
            if name in names:
                continue
            for v in vs:
                if TEXTURE.search(v) or any(r in names for r in VAR.findall(v)):
                    names.add(name)
                    changed = True
                    break
    return names


def subject(selector):
    """The last compound of a selector, plus its pseudo-element.

    `.cf-plot--ground .cf-plot__set::before` -> `.cf-plot__set::before`
    """
    s = " ".join(selector.split())
    s = re.sub(r"\s*([>+~])\s*", " ", s)
    last = s.split(" ")[-1] if s else s
    return last.strip()


class Rule:
    __slots__ = ("sheet", "line", "selector", "subject", "decls", "forced")

    def __init__(self, sheet, line, selector, decls, forced):
        self.sheet = sheet
        self.line = line
        self.selector = selector
        self.subject = subject(selector)
        self.decls = decls
        self.forced = forced


def declarations(block):
    out = []
    for part in block.split(";"):
        if ":" not in part:
            continue
        prop, _, value = part.partition(":")
        prop = prop.strip().lower()
        if prop.startswith("--"):
            continue
        out.append((prop, value.strip()))
    return out


def parse(path):
    """Every declaration block in the file, each tagged with the forced-colours
    state of the at-rules it stands inside."""
    text = strip_comments(path.read_text(encoding="utf-8"))
    rules = []
    stack = []          # open at-rule preludes, innermost last
    forced = 0          # depth of enclosing (forced-colors: active)
    i = 0
    n = len(text)
    chunk_start = 0
    while i < n:
        ch = text[i]
        if ch == "{":
            prelude = text[chunk_start:i].strip()
            if prelude.startswith("@"):
                is_forced = "forced-colors" in prelude and "active" in prelude
                stack.append(is_forced)
                if is_forced:
                    forced += 1
                i += 1
                chunk_start = i
                continue
            # a style rule — find its matching close
            depth = 1
            j = i + 1
            while j < n and depth:
                if text[j] == "{":
                    depth += 1
                elif text[j] == "}":
                    depth -= 1
                j += 1
            block = text[i + 1:j - 1]
            line = text.count("\n", 0, chunk_start) + 1
            decls = declarations(block)
            for sel in prelude.split(","):
                sel = sel.strip()
                if sel:
                    rules.append(Rule(path.name, line, sel, decls, forced > 0))
            i = j
            chunk_start = i
            continue
        if ch == "}":
            if stack:
                if stack.pop():
                    forced -= 1
            i += 1
            chunk_start = i
            continue
        i += 1
    return rules


def paints_texture(decls, texture_names):
    for prop, value in decls:
        if prop not in ("background", "background-image"):
            continue
        if TEXTURE.search(value):
            return value
        for ref in VAR.findall(value):
            if ref in texture_names:
                return value
    return None


def fills_with_ink(decls):
    """The forced-colours fill, when it is a bare system foreground.

    The `background` shorthand counts and is the whole point: it resets
    background-image to none in the same declaration.
    """
    for prop, value in decls:
        if prop not in ("background", "background-color"):
            continue
        word = IMPORTANT.sub("", value).strip().lower()
        if word in INKS:
            return value.strip()
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    missing = [p for p in SHEETS if not p.exists()]
    if missing:
        for p in missing:
            print("check-forced-texture: no %s" % p.relative_to(ROOT))
        return 1

    sources = [strip_comments(p.read_text(encoding="utf-8")) for p in SHEETS]
    texture_names = texture_properties(sources)

    rules = []
    for path in SHEETS:
        rules.extend(parse(path))

    base_textures = {}
    for r in rules:
        if r.forced:
            continue
        value = paints_texture(r.decls, texture_names)
        if value:
            base_textures.setdefault(r.subject, []).append((r, value))

    findings = []
    grounds = []
    for r in rules:
        if not r.forced:
            continue
        fill = fills_with_ink(r.decls)
        base = base_textures.get(r.subject)
        if not base:
            if args.verbose:
                for prop, value in r.decls:
                    if prop in ("background", "background-color") and \
                            value.strip().lower() in GROUNDS:
                        grounds.append((r, value.strip()))
            continue
        if fill:
            findings.append((r, fill, base))
        elif args.verbose:
            grounds.append((r, "answered without a fill"))

    if args.verbose:
        print("check-forced-texture: %d rules across %d sheets, "
              "%d texture-bearing custom properties, %d textured subjects."
              % (len(rules), len(SHEETS), len(texture_names),
                 len(base_textures)))
        for r, note in grounds:
            print("  ok  %s:%d  %s  — %s" % (r.sheet, r.line, r.selector, note))

    for r, fill, base in findings:
        print("%s:%d  %s" % (r.sheet, r.line, r.selector))
        print("    forced colours fills this box with `%s`, an ink." % fill)
        for br, bvalue in base:
            print("    its paint is a texture: %s:%d  %s"
                  % (br.sheet, br.line, bvalue[:72]))
        print("    A background image is discarded in forced colours; a system")
        print("    foreground in its place is not the drawing re-inked, it is a")
        print("    slab where the drawing was. Take the box out (display: none,")
        print("    the way base.css takes .cf-ground::before out) or redraw the")
        print("    mark with a border, the way acts.css redraws the map's key.")

    if findings:
        print()
        print("%d forced-colours rule(s) filling a texture's box with an ink."
              % len(findings))
        return 1

    if not args.verbose:
        print("check-forced-texture: %d textured subjects, none of them filled "
              "with an ink under forced colours." % len(base_textures))
    return 0


if __name__ == "__main__":
    sys.exit(main())
