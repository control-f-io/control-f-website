#!/usr/bin/env python3
"""A contour that replaces a border stands on that border's box.

The thirtieth check, and the one whose failure is exactly one pixel wide at
every viewport, which is why it survived a lane whose whole job is corners.

THE CONSTRUCTION. A component draws its own edge as a CSS border. A drawing is
then laid over it to take that edge over — because the edge has to be animated,
or relayed, or drawn in an order the border cannot express — and the component
gives its border-color up to `transparent` so the two do not both show. The
drawing is an <svg> positioned `absolute; inset: 0` over the component, with its
strokes written ON its own viewBox extremes so they land where the border was.

That last sentence is the one that is wrong, and nothing about it looks wrong.

WHY. `inset` on an absolutely positioned box resolves against its containing
block's PADDING box. Giving up `border-color` does not give up `border-width`:
the component still reserves it, so its padding box is one border-width inside
its border box on every side. `inset: 0` therefore lands the drawing's box one
border-width INSIDE the box whose border it replaced, and an edge frame's
strokes — centred on its own box edges — stand one border-width inside where
the border stood. The component is the right size, the drawing is the right
shape, the strokes are the right weight, every corner is closed, and the whole
contour is one pixel small.

THE EVIDENCE. patterns/landing-page.html draws the pinned stage's lectern as
six hairlines in a 1000 x 500 viewBox over .lp-proc-plate, which is a
.cf-process and carries `border: var(--stroke-1) solid var(--border-strong)`.
Measured in the browser, DOM boxes at device scale 1:

    viewport      plate border box          frame box            inset
    1440 x 900    x  79.98 .. 1360.00   x  80.98 .. 1359.00    L+1.00 R+1.00
    1920 x 1080   x 320.00 .. 1600.00   x 321.00 .. 1599.00    L+1.00 R+1.00
    1280 x 900    x  70.39 .. 1209.61   x  71.39 .. 1208.61    L+1.00 R+1.00

and the same +1.00 on top and bottom at all three. Reading the ink instead of
the DOM, at device scale 8, six CSS pixels below the frame's top rail: at
1920 x 1080 the left vertical painted centred on x 320.94 with the plate's
border box beginning at 320.00.

WHAT IT COST. The drawing overhead — .lp-flow, the root the data leaves the
void by — is laid out on the same container, so ITS box is the plate's border
box exactly: 320.00 .. 1600.00. Its fifteen terminals are written to land on
the frame's rail, and the markup says so in as many words: "Each vertical
continues the drop that lands on it — flow x 0, 600 and 1200 are these x 0,
500 and 1000". Flow x 0 landed on 320.00 and frame x 0 stood at 320.94. The
middle agreed, because the middle of a box is the middle of a box either way,
and the two ends did not. A drop that continues into a vertical 0.94 px to its
side is the free end this repository already has a standing order about, drawn
at the one width where nobody would think to measure it: its own.

THE RULE. For every <svg> in the design-system tree that is an EDGE FRAME —
every one of its stroked straight segments lies ALONG a viewBox extreme rather
than merely touching one, the same predicate check-edge-stroke-clip.py uses —
and that resolves `position: absolute`: let P be its parent element. If P
resolves a positioning that makes it the containing block, AND P resolves a
non-zero border-width, AND P gives that border's colour up to `transparent`,
then the <svg> must

  * cancel that border-width on all four insets — which places the box;
  * state `width` and `height` as `calc(100% + 2 x border)` — which makes it
    reach; and
  * declare no max-width or max-height that clamps it back.

THE SECOND OF THOSE THREE IS NOT DECORATION. An <svg> is a REPLACED element,
and a replaced element resolves an auto size from its intrinsic ratio before
it resolves one from opposing insets. With the four insets in and no size
stated, this frame came out 1280 x 640 at 1440 x 900: the width followed the
insets, the height came from the viewBox's own 1000 / 500, and `bottom: -1px`
was dropped as over-constrained. Left, right and top moved onto the border box
and the base rail alone stayed 1 px inside it — three sides fixed and one not,
which reads worse than four sides wrong because now the frame is not even a
rectangle concentric with its plate. Both percentages are of the containing
block's padding box, which is the box being escaped, so both add the border
back twice.

The three conditions together are what make this decidable and what keep it
narrow. An overlay inside a component with a VISIBLE border is not covered: it
may well belong inside that border, and this script cannot tell. An overlay
whose parent is not the containing block is not covered: the box it escapes is
somewhere else and no amount of parsing finds it. What is covered is the one
construction where the drawing IS the border — declared as such by the
transparent colour — and there the drawing's box and the border's box are the
same box or the drawing is wrong.

AND max-width, WHICH IS THE HALF OF THE FIX THAT IS EASY TO MISS. base.css
resets `img, svg, video { display: block; max-width: 100% }`, and for an
absolutely positioned box that 100 % is the containing block's padding box —
the very box being escaped. Negative insets alone move the left edge out and
leave the right edge where it was, which is a worse drawing than the one being
fixed: the two verticals then disagree with each other as well as with what
lands on them. Measured, with the insets in and the cap still on: left edge
79.98 (right), right edge 1357.98 (2 px short). So the cap is part of the rule.

The check reads the markup and the stylesheets, not the browser: this is a
fact about declarations, and it is true before anything renders.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-contour-box.py
    python3 scripts/check-contour-box.py -v
"""

import argparse
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
CSS = DS / "assets" / "css"

SHIPPING = ("tokens.css", "base.css", "components.css")
PAGES = sorted(DS.rglob("*.html"))

COMMENT = re.compile(r"/\*.*?\*/", re.S)
NUMBER = re.compile(r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?")
PATH_TOKEN = re.compile(r"[A-Za-z]|[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?")
STRAIGHT = set("MLHV")
EPS = 1e-6
STROKELESS = re.compile(r'stroke\s*[:=]\s*"?\s*none', re.I)

# Positions that make an element the containing block for an absolutely
# positioned descendant. `static` does not.
CONTAINING = {"relative", "absolute", "fixed", "sticky"}
SIDES = ("top", "right", "bottom", "left")


# --------------------------------------------------------------------------
# geometry — the edge-frame predicate, as check-edge-stroke-clip.py draws it
# --------------------------------------------------------------------------

def segments(tag, attrs):
    """Straight segments of one element, user units. [] for anything unreadable."""
    if "transform" in attrs:
        return []
    if tag == "line":
        try:
            return [((float(attrs.get("x1", 0)), float(attrs.get("y1", 0))),
                     (float(attrs.get("x2", 0)), float(attrs.get("y2", 0))))]
        except ValueError:
            return []
    if tag != "path":
        return []
    toks = PATH_TOKEN.findall(attrs.get("d", ""))
    out, cur, i, last = [], None, 0, "L"
    while i < len(toks):
        head = toks[i]
        if head.isalpha():
            if head not in STRAIGHT:
                return []
            i += 1
            cmd = head
        elif cur is None:
            return []
        else:
            cmd = last
        try:
            if cmd in "ML":
                x, y = float(toks[i]), float(toks[i + 1]); i += 2
            elif cmd == "H":
                x, y = float(toks[i]), cur[1]; i += 1
            else:
                x, y = cur[0], float(toks[i]); i += 1
        except (IndexError, ValueError):
            return []
        if cur is not None and cmd != "M":
            out.append((cur, (x, y)))
        cur = (x, y)
        last = "L" if cmd == "M" else cmd
    return out


def coincident(seg, box):
    """Which viewBox edge this segment LIES ALONG, or None if it merely meets one."""
    (ax, ay), (bx, by) = seg
    x0, y0, w, h = box
    x1, y1 = x0 + w, y0 + h
    if abs(ay - by) < EPS and abs(ax - bx) > EPS:
        if abs(ay - y0) < EPS:
            return "top"
        if abs(ay - y1) < EPS:
            return "bottom"
    if abs(ax - bx) < EPS and abs(ay - by) > EPS:
        if abs(ax - x0) < EPS:
            return "left"
        if abs(ax - x1) < EPS:
            return "right"
    return None


# --------------------------------------------------------------------------
# the stylesheets, and what an element resolves
# --------------------------------------------------------------------------

def rules(text):
    """[(selector, body)] with comments blanked."""
    text = COMMENT.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)
    out = []
    for m in re.finditer(r"([^{}]*)\{([^{}]*)\}", text):
        selector = " ".join(m.group(1).split())
        if "{" not in m.group(1) and selector.startswith("@"):
            continue
        out.append((selector, m.group(2)))
    return out


def tokens(sheets):
    """Custom properties declared on :root, as a flat name -> value map."""
    out = {}
    for _, ruleset in sheets:
        for selector, body in ruleset:
            if ":root" not in selector:
                continue
            for name, value in re.findall(r"(--[\w-]+)\s*:\s*([^;{}]+)", body):
                out[name] = value.strip()
    return out


def length(value, vars_, depth=0):
    """Resolve a length to CSS pixels, or None if this script cannot.

    Handles the three forms the tree actually writes: a bare px length, a
    var() reference, and `calc(<term> * <number>)` — which is how a negative
    of a token is spelled. Anything else returns None and puts the element out
    of scope rather than into a finding.
    """
    if value is None or depth > 8:
        return None
    v = value.strip().lower()
    if v in ("0", "none"):
        return 0.0 if v == "0" else None
    m = re.fullmatch(r"calc\((.+)\)", v)
    if m:
        inner = m.group(1)
        parts = re.split(r"\s\*\s", inner)
        if len(parts) == 2:
            a, b = parts
            try:
                factor = float(b)
            except ValueError:
                a, b = b, a
                try:
                    factor = float(b)
                except ValueError:
                    return None
            base = length(a, vars_, depth + 1)
            return None if base is None else base * factor
        return length(inner, vars_, depth + 1)
    m = re.fullmatch(r"var\((--[\w-]+)(?:\s*,\s*([^)]+))?\)", v)
    if m:
        got = vars_.get(m.group(1))
        if got is None:
            return length(m.group(2), vars_, depth + 1) if m.group(2) else None
        return length(got, vars_, depth + 1)
    m = re.fullmatch(r"([-+]?(?:\d*\.\d+|\d+))px", v)
    if m:
        return float(m.group(1))
    return None


def top_level_split(value):
    """Split a declaration into its terms without cutting inside a function.

    `calc(var(--stroke-1) * -1)` is ONE term and str.split() makes it three,
    which is how a shorthand that was read correctly still came out unset.
    """
    out, depth, cur = [], 0, ""
    for ch in value:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch.isspace() and depth == 0:
            if cur:
                out.append(cur)
                cur = ""
            continue
        cur += ch
    if cur:
        out.append(cur)
    return out


# A compound this script can read: an optional tag, any number of classes, and
# any number of :not(...) groups. Attribute selectors, `+`, `~` and pseudo
# elements or other pseudo classes put the whole selector out of reach.
COMPOUND = re.compile(r"^(?:[a-z][\w-]*)?(?:\.[\w-]+|:not\([^()]*\))*$", re.I)


def compound_matches(compound, tag, classes):
    """Does one compound selector match one element?"""
    if not COMPOUND.match(compound):
        return None                      # unreadable — caller drops the rule
    negated = set()
    for group in re.findall(r":not\(([^()]*)\)", compound):
        if not COMPOUND.match(group.strip()):
            return None
        negated |= set(re.findall(r"\.([\w-]+)", group))
    bare = re.sub(r":not\([^()]*\)", "", compound)
    names = set(re.findall(r"\.([\w-]+)", bare))
    head = re.match(r"^([a-z][\w-]*)", bare, re.I)
    if negated & classes:
        return False
    if names and not names <= classes:
        return False
    if head and head.group(1).lower() != tag:
        return False
    if not names and not head:
        return False
    return True


def selector_matches(selector, chain):
    """Does any comma-branch of this selector match the LAST element of `chain`?

    `chain` is the element's ancestor path as [(tag, classes), …, (tag, classes)]
    with the element itself last. Descendant and child combinators are both
    honoured, because ignoring them is how `.cf-process__figure > svg` came to
    decide what an .lp-frame resolves for max-width: the subject is a bare
    `svg`, it matches every <svg> in the tree if the left side is thrown away,
    and the answer it gave was 22rem for an element that is not in a
    .cf-process__figure at all.

    A branch this script cannot parse contributes nothing rather than matching
    everything — the same direction the rest of the file takes when it cannot
    read something.
    """
    tag, classes = chain[-1]
    for part in selector.split(","):
        part = part.strip()
        if not part:
            continue
        # [compound, ">"?, compound, …], right-to-left from the subject
        seq, ok = [], True
        for raw in re.split(r"(>)", part):
            seq.extend(raw.split())
        if not seq:
            continue
        if seq[-1] == ">" or seq[0] == ">":
            continue
        # walk right to left
        i, j = len(seq) - 1, len(chain) - 1
        m = compound_matches(seq[i], chain[j][0], chain[j][1])
        if m is None:
            continue                       # unreadable branch
        if not m:
            continue
        i -= 1
        j -= 1
        matched = True
        while i >= 0 and matched:
            if seq[i] == ">":
                i -= 1
                if i < 0 or j < 0:
                    matched = False
                    break
                r = compound_matches(seq[i], chain[j][0], chain[j][1])
                if r is None:
                    matched = False
                    ok = False
                    break
                matched = r
                i -= 1
                j -= 1
            else:
                found = False
                k = j
                while k >= 0:
                    r = compound_matches(seq[i], chain[k][0], chain[k][1])
                    if r is None:
                        ok = False
                        break
                    if r:
                        found = True
                        j = k - 1
                        break
                    k -= 1
                if not ok:
                    matched = False
                    break
                matched = found
                i -= 1
        if matched and ok:
            return True
    return False


def resolve(prop, chain, style_attr, blocks):
    """Last declaration of `prop` on any rule that matches this element.

    Source order across the page's own <style> after the shipping sheets, which
    is the order the browser reads them in on these pages, and the style
    attribute last of all. Specificity is deliberately NOT weighed: every rule
    that matches is allowed to have the last word in source order, so the
    answer can only be one a real cascade might also give. Shorthands are not
    expanded except where the caller asks for one by name.
    """
    found = None
    pat = re.compile(r"(?<![\w-])" + re.escape(prop) + r"\s*:\s*([^;{}]+)", re.I)
    for _, ruleset in blocks:
        for selector, body in ruleset:
            if not pat.search(body):
                continue
            if not selector_matches(selector, chain):
                continue
            for m in pat.finditer(body):
                found = m.group(1).strip()
    if style_attr:
        for m in pat.finditer(style_attr):
            found = m.group(1).strip()
    return found


def border_width(chain, style_attr, blocks, vars_):
    """The resolved border-width, reading the `border` shorthand too."""
    width = None
    for prop in ("border", "border-width", "border-top-width"):
        got = resolve(prop, chain, style_attr, blocks)
        if got is None:
            continue
        terms = top_level_split(got)
        if prop == "border":
            if got.strip().lower() in ("none", "0"):
                width = 0.0
                continue
            val = length(terms[0], vars_) if terms else None
            if val is not None:
                width = val
        else:
            val = length(terms[0], vars_) if terms else None
            if val is not None:
                width = val
    return width


def gives_up_colour(chain, style_attr, blocks):
    """Does this element declare its border-color transparent?"""
    for prop in ("border-color", "border"):
        got = resolve(prop, chain, style_attr, blocks)
        if got and "transparent" in got.lower():
            return True
    return False


def percent_plus(value, vars_):
    """For `calc(100% + <length>)`, the length in px. None for anything else.

    This is the only spelling that sizes a box to its containing block plus a
    fixed amount, and it is the one an escaping overlay needs: the percentage
    is of the padding box being escaped, so the addend is what puts the far
    edge back on the border box.
    """
    if value is None:
        return None
    m = re.fullmatch(r"calc\(\s*100%\s*\+\s*(.+)\)", value.strip(), re.I)
    if not m:
        return None
    # the addend is a calc sub-expression with no calc() of its own — give it
    # one so the same arithmetic that reads `calc(var(--x) * -1)` reads it too
    return length("calc(%s)" % m.group(1).strip(), vars_)


def insets(chain, style_attr, blocks, vars_):
    """The four resolved insets, reading the `inset` shorthand too."""
    out = {}
    got = resolve("inset", chain, style_attr, blocks)
    if got is not None:
        parts = top_level_split(got)
        # the box shorthand's own expansion: 1, 2, 3 or 4 terms
        order = {1: (0, 0, 0, 0), 2: (0, 1, 0, 1),
                 3: (0, 1, 2, 1), 4: (0, 1, 2, 3)}.get(len(parts))
        if order:
            for s, k in zip(("top", "right", "bottom", "left"), order):
                out[s] = length(parts[k], vars_)
    for s in SIDES:
        one = resolve(s, chain, style_attr, blocks)
        if one is not None:
            out[s] = length(one, vars_)
    return out


# --------------------------------------------------------------------------
# the pass over the tree
# --------------------------------------------------------------------------

class Reader(HTMLParser):
    """Collect every <svg>, its parent element, and its boundary segments."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.svgs = []
        self.open = []          # (tag, classes, style)
        self.stack = []
        self.style_blocks = []
        self._in_style = False

    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "param", "source", "track", "wbr"}

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "style":
            self._in_style = True
            return
        if tag == "svg":
            me = (tag, set(a.get("class", "").split()), a.get("style", ""))
            # the full ancestor path, element last: what a descendant or child
            # combinator has to be walked against
            chain = [(t, c) for t, c, _ in self.open] + [(tag, me[1])]
            parent = self.open[-1] if self.open else None
            parent_chain = [(t, c) for t, c, _ in self.open]
            entry = [self.getpos()[0], set(a.get("class", "").split()),
                     a.get("style", ""), a.get("viewbox", ""), [],
                     parent, chain, parent_chain]
            self.stack.append(entry)
            self.svgs.append(entry)
            self.open.append(me)
            return
        if self.stack:
            entry = self.stack[-1]
            n = [float(v) for v in NUMBER.findall(entry[3])]
            if len(n) == 4:
                blob = " ".join("%s=%s" % kv for kv in a.items())
                if not STROKELESS.search(blob):
                    for seg in segments(tag, a):
                        edge = coincident(seg, n)
                        entry[4].append(edge)
        if tag not in self.VOID:
            self.open.append((tag, set(a.get("class", "").split()), a.get("style", "")))

    def handle_startendtag(self, tag, attrs):
        if tag == "svg":
            return
        depth = len(self.open)
        self.handle_starttag(tag, attrs)
        del self.open[depth:]

    def handle_endtag(self, tag):
        if tag == "style":
            self._in_style = False
            return
        if tag == "svg" and self.stack:
            self.stack.pop()
        for i in range(len(self.open) - 1, -1, -1):
            if self.open[i][0] == tag:
                del self.open[i:]
                break

    def handle_data(self, data):
        if self._in_style:
            self.style_blocks.append(data)


def audit(verbose):
    sheets = []
    findings = []
    for name in SHIPPING:
        path = CSS / name
        if not path.exists():
            print(f"contour box: {name} is missing")
            return 1
        sheets.append((name, rules(path.read_text(encoding="utf-8"))))
    vars_ = tokens(sheets)

    frames = 0
    checked = []
    for page in PAGES:
        reader = Reader()
        reader.feed(page.read_text(encoding="utf-8"))
        blocks = list(sheets) + [("%s <style>" % page.name, rules(b))
                                 for b in reader.style_blocks]
        rel = page.relative_to(ROOT).as_posix()
        for (line, classes, style, raw, edges, parent,
             chain, parent_chain) in reader.svgs:
            # an EDGE FRAME: it draws all FOUR of its viewBox's edges. That is
            # what makes it a border rather than a drawing that happens to
            # touch one — and a border has four sides. Interior geometry is
            # allowed and expected: this frame carries a divider at x = 500,
            # and it is the one stroke of the six the clip could never reach.
            if {e for e in edges if e} != {"top", "right", "bottom", "left"}:
                continue
            frames += 1
            label = ("svg." + ".".join(sorted(classes))) if classes else "svg"
            pos = resolve("position", chain, style, blocks)
            if (pos or "").strip().lower() != "absolute":
                continue
            if parent is None or not parent_chain:
                continue
            ptag, pclasses, pstyle = parent
            ppos = resolve("position", parent_chain, pstyle, blocks)
            if (ppos or "").strip().lower() not in CONTAINING:
                continue
            bw = border_width(parent_chain, pstyle, blocks, vars_)
            if not bw:
                continue
            if not gives_up_colour(parent_chain, pstyle, blocks):
                continue
            plabel = ptag + ("." + ".".join(sorted(pclasses)) if pclasses else "")

            got = insets(chain, style, blocks, vars_)
            bad = []
            for s in SIDES:
                v = got.get(s)
                if v is None or abs(v + bw) > 1e-6:
                    bad.append((s, v))
            if bad:
                sides = ", ".join(
                    f"{s} {'unset' if v is None else format(v, 'g') + 'px'}" for s, v in bad)
                findings.append(
                    f"{rel}:{line}: {label} is an edge frame over {plabel}, which "
                    f"reserves a {bw:g}px border and gives its colour up — so the "
                    f"contour must cancel that width on all four sides, and {sides} "
                    f"does not. Every stroke stands {bw:g}px inside the box whose "
                    f"border it replaced.")
            # AND THE SIZE, STATED. An <svg> is a replaced element, so an auto
            # size resolves from the intrinsic viewBox ratio BEFORE it resolves
            # from opposing insets — the `bottom` is then dropped as
            # over-constrained and the base rail alone stays behind. Insets
            # place the box; only a stated size makes it reach.
            for prop, side in (("width", "right"), ("height", "bottom")):
                got = resolve(prop, chain, style, blocks)
                add = percent_plus(got, vars_)
                if add is None or abs(add - 2 * bw) > 1e-6:
                    findings.append(
                        f"{rel}:{line}: {label} is an edge frame over {plabel} and "
                        f"resolves {prop}: {got or 'unset'}. An <svg> is replaced, so "
                        f"its auto {prop} comes from the viewBox ratio and the "
                        f"{side} inset is dropped as over-constrained — {prop} has to "
                        f"be stated as calc(100% + {2 * bw:g}px), twice the "
                        f"{bw:g}px border, or that one edge stays inside the plate "
                        f"while the other three move out.")

            # A cap only matters if something declares one. Unset is no cap;
            # `none` is a cap explicitly lifted. Anything else clamps the box
            # back to the containing block it was just told to escape.
            for prop in ("max-width", "max-height"):
                cap = resolve(prop, chain, style, blocks)
                if cap is not None and cap.strip().lower() != "none":
                    findings.append(
                        f"{rel}:{line}: {label} escapes {plabel}'s padding box by "
                        f"{bw:g}px but resolves {prop}: {cap.strip()} — for an "
                        f"absolutely positioned box that percentage is of the very "
                        f"box being escaped, so the far edge is held back and the "
                        f"two sides disagree with each other as well as with it.")
            checked.append((rel, line, label, plabel, bw, len(edges)))

    if verbose:
        print(f"  {frames} edge frame(s) in the tree; {len(checked)} over a "
              f"positioned parent that reserves a border and gives up its colour")
        for rel, line, label, plabel, bw, n in checked:
            print(f"    {rel}:{line}  {label} ({n} boundary strokes) over {plabel}, "
                  f"border {bw:g}px")

    if findings:
        print(f"\ncontour box: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f}")
        return 1
    print(f"contour box OK — {frames} edge frame(s) read, {len(checked)} of them "
          f"standing on the border box of the component whose border they replace, "
          f"insets cancelling the reserved width and nothing capping them back")
    return 0


def main():
    p = argparse.ArgumentParser(
        description="A contour that replaces a border stands on that border's box.")
    p.add_argument("-v", "--verbose", action="store_true",
                   help="print every edge frame and the parent it is measured against")
    return audit(p.parse_args().verbose)


if __name__ == "__main__":
    sys.exit(main())
