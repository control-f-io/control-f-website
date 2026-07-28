#!/usr/bin/env python3
"""A rule that is drawn has to be drawn on the edge the reader can see.

The sixty-seventh check, and the first whose subject is a pseudo-element's
RELATIONSHIP to the box it draws for. Every other check in this tree reads one
thing and holds it to a number. This one reads two and holds them to each
other, because the fault it exists for is invisible in either half alone: both
the border and the pseudo-element were correct, and they were on opposite edges
of the same box.

WHAT HAPPENED. .lp-proc-head is the landing page's "WAS WIR MACHEN / 4
SCHRITTE" row, and three rules stack a border on it:

    .cf-section-header          border-bottom: 1px solid    the component
    .cf-section-header--flush   border-bottom: 0            gives the rule up
    .lp-proc-head  (page)       border-block-start: 1px     re-hangs it on top

The last of those is deliberate and documented at length: inside the gate the
header is placed on the drawing's own rim, so the rule belongs on the box's TOP
edge, where the root's horizon is. --flush had already zeroed the bottom one --
its whole reason for existing is the sentence in components.css, "The header
gives up its own border rather than drawing a second hairline 1 px away".

Then a later block set out to make that rule GROW rather than arrive finished,
which is the right idea and is the note "THE GROUND LINE DRAWS ITSELF" in the
page. It wrote:

    .lp-proc-head        { border-bottom-color: transparent; }
    .lp-proc-head::after { bottom: -1px; border-bottom: 1px solid ...;
                           animation: lp-frame-draw ... }

Both lines name the block-END edge. The border was on the block-START edge.

So `border-bottom-color: transparent` recoloured a border that --flush had
already set to 0 px wide -- a no-op, and a no-op that LOOKS like the fix --
while the 1 px opaque black border-block-start went on painting, untouched by
any animation, exactly as it had before. And the ::after drew its replacement
28.9 px lower down, at the bottom of the header's box.

Measured on the render at 1440 x 900, scrolling the sequence in 20 px steps:
the block-start border entered the viewport already finished at scroll y 742;
the ::after did not begin to draw until y 1100 and did not land until y 1280.
The reader therefore met the finished rule the change was written to abolish,
358 px before the drawn one started -- and then got a SECOND full-container
hairline growing in below it. Two parallel rules across a drawing that has one
horizon, with the label row trapped between them, at every viewport inside the
gate.

Neither half is wrong on its own. A grep for the border finds a border; a grep
for the animation finds an animation; the page renders; all sixty-five checks
beside this one pass. What is wrong is that they are on different edges, and
the only way to see it is to resolve both and compare.

THE RULE THIS HOLDS. For every pseudo-element in patterns/ that DRAWS a rule --
a ::before or ::after whose ink is a border on one edge and whose animation is
this tree's scale-draw -- three things must be true of the box it draws for:

  1. the edge the pseudo-element borders is the edge the cascade actually gives
     that box a border on;
  2. the pseudo-element is inset to that same edge (a rule drawn at `top` and
     bordered at `bottom` is 28.9 px of silence);
  3. the box does not still PAINT that border. A drawn rule replaces a painted
     one; if the painted one survives, the reader meets it finished and the
     drawing gets two.

And a fourth, which is the tell rather than the fault, and the cheapest thing
here to get wrong:

  4. a `border-<edge>-color: transparent` whose resolved width on that edge is
     0 px is a NEUTRALISATION THAT NEUTRALISES NOTHING. It is what a correct
     fix looks like from a diff, and it is why this one survived review.

WHAT THIS CHECK WILL NOT DO. It resolves borders for a real element in the
markup, against every rule whose selector is a chain of classes that element
carries. A selector shape it cannot read -- a combinator, an id, an attribute,
a pseudo-class -- is a FINDING and not a pass, so the check cannot go quiet by
being outgrown. It assumes horizontal-tb, which is the whole tree, and says so
by failing if a writing-mode ever appears on a box it reads.

stdlib only, no build step, no dependency -- the same contract as the
sixty-six checks beside it.

    python3 scripts/check-head-rule.py       # check, exit 1 on a finding
    python3 scripts/check-head-rule.py -v    # print every drawn rule it resolved
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system" / "assets" / "css"
PATTERNS = ROOT / "design-system" / "patterns"
SHIPPING = ("tokens.css", "base.css", "components.css")

COMMENT = re.compile(r"/\*.*?\*/", re.S)

# The keyframes this tree grows a stroke with. A rule drawn by anything else is
# not a drawn rule as far as this check is concerned -- and if a new one is
# added without being named here the pseudo-element simply is not read, which
# is why rule 4 is written to fire on the neutralisation instead.
DRAW_KEYFRAMES = ("lp-frame-draw", "cf-iso-draw", "cf-pin-draw")

# Logical -> physical, horizontal-tb. The tree is one writing mode; the check
# fails rather than guesses if that ever stops being true.
EDGE = {
    "top": "top", "bottom": "bottom",
    "block-start": "top", "block-end": "bottom",
}
TRANSPARENT = re.compile(r"^(transparent|rgba\([^)]*,\s*0(\.0+)?\s*\))$", re.I)


def strip(css):
    return COMMENT.sub("", css)


# --------------------------------------------------------------------------
# Blocks. The pages nest their rules inside @supports and @media; at-rules
# carry no specificity and no source order of their own, so flattening to
# (order, selector, declarations) is the whole of what the cascade needs here.
# Selector nesting is NOT flattened -- a nested selector is unreadable and is
# reported, because reading it wrong would silently drop a border.
# --------------------------------------------------------------------------
def blocks(css):
    css = strip(css)
    out, stack, buf, i, n = [], [], "", 0, len(css)
    while i < n:
        c = css[i]
        if c == "{":
            stack.append(buf.strip())
            buf = ""
        elif c == "}":
            decls = buf.strip()
            prelude = stack.pop() if stack else ""
            if decls and not prelude.startswith("@"):
                nested = bool(re.search(r"[.#&\[a-zA-Z]", decls.split("{")[0])) and "{" in decls
                out.append((len(out), prelude, decls, nested))
            buf = ""
        else:
            buf += c
        i += 1
    return out


def declarations(text):
    """[(prop, value)] in source order, shorthands left intact."""
    out = []
    for part in text.split(";"):
        if ":" not in part:
            continue
        prop, _, value = part.partition(":")
        prop, value = prop.strip().lower(), value.strip()
        if prop and value and not prop.startswith("--"):
            out.append((prop, value))
    return out


# --------------------------------------------------------------------------
# Selectors. Only what this subject needs: a compound of classes, optionally
# with a ::before / ::after. Anything else is unreadable.
# --------------------------------------------------------------------------
SIMPLE = re.compile(r"^(?:\.[-\w]+)+(::?(?:before|after))?$")


def parse_selector(sel):
    """({classes}, pseudo or None) or None if this check cannot read it."""
    sel = sel.strip()
    m = SIMPLE.match(sel)
    if not m:
        return None
    pseudo = m.group(1)
    body = sel[: -len(pseudo)] if pseudo else sel
    return set(re.findall(r"\.([-\w]+)", body)), (pseudo.lstrip(":") if pseudo else None)


def split_selectors(prelude):
    return [s.strip() for s in prelude.split(",") if s.strip()]


# --------------------------------------------------------------------------
# Borders. Enough of the shorthand grammar to resolve which edges of a box end
# up painting ink, and no more: a width and a colour per physical edge.
# --------------------------------------------------------------------------
WIDTH_WORD = {"thin": 1.0, "medium": 3.0, "thick": 5.0}


def width_px(value, toks, seen=()):
    v = value.strip()
    if re.fullmatch(r"-?0+(?:\.0+)?", v):
        return 0.0
    m = re.fullmatch(r"(-?\d*\.?\d+)(px|rem|em)", v)
    if m:
        n = float(m.group(1))
        return n * 16.0 if m.group(2) in ("rem", "em") else n
    if v.lower() in WIDTH_WORD:
        return WIDTH_WORD[v.lower()]
    m = re.fullmatch(r"var\(\s*(--[\w-]+)\s*\)", v)
    if m:
        name = m.group(1)
        if name in seen or name not in toks:
            return None
        return width_px(toks[name], toks, seen + (name,))
    return None


def tokens(css):
    out = {}
    for m in re.finditer(r":root\s*\{(.*?)\n\}", strip(css), re.S):
        for name, value in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", m.group(1)):
            out[name] = value.strip()
    return out


def apply_border(state, prop, value, toks, note):
    """Fold one declaration into {edge: {'w':px,'c':colour,'from':note}}."""
    m = re.fullmatch(r"border(?:-(top|bottom|block-start|block-end))?"
                     r"(?:-(width|color|style))?", prop)
    if not m:
        return
    edge_name, sub = m.group(1), m.group(2)
    edges = [EDGE[edge_name]] if edge_name else ["top", "bottom"]
    for e in edges:
        cur = state.setdefault(e, {"w": 0.0, "c": None, "from": None, "wfrom": None})
        if sub == "width":
            cur["w"] = width_px(value, toks)
            cur["wfrom"] = note
        elif sub == "color":
            cur["c"] = value
            cur["from"] = note
        elif sub == "style":
            pass
        else:
            # shorthand: `0`, or `<width> <style> <colour>`
            parts = value.split()
            w = width_px(parts[0], toks) if parts else None
            cur["w"] = w if w is not None else 0.0
            cur["wfrom"] = note
            colour = None
            for p in parts[1:]:
                if p not in ("solid", "dashed", "dotted", "none", "hidden"):
                    colour = p if colour is None else colour + " " + p
            if colour:
                cur["c"] = colour
                cur["from"] = note
            elif len(parts) == 1:
                cur["c"] = None


def visible(edge_state):
    w, c = edge_state.get("w"), edge_state.get("c")
    if w is None:
        return None                      # a width this check could not read
    if w <= 0:
        return False
    if c is not None and TRANSPARENT.match(c.strip()):
        return False
    return True


# --------------------------------------------------------------------------
def classes_in(html):
    """Every class set that appears on one element in the markup."""
    return [set(m.split()) for m in re.findall(r'\bclass="([^"]*)"', html)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    shipping = [(p, (CSS / p).read_text(encoding="utf-8")) for p in SHIPPING]
    toks = {}
    for _, text in shipping:
        toks.update(tokens(text))

    findings, unreadable, resolved = [], [], []

    for page in sorted(PATTERNS.glob("*.html")):
        html = page.read_text(encoding="utf-8")
        style = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S))
        if not style.strip():
            continue
        if re.search(r"writing-mode\s*:", strip(style)):
            findings.append(f"{page.name}: a writing-mode is declared; this "
                            f"check maps logical edges assuming horizontal-tb")

        # every rule that ships, in cascade order: stylesheets then the page
        rules = []
        for name, text in shipping:
            for order, prelude, decls, nested in blocks(text):
                rules.append((f"{name}:{order}", prelude, decls, nested))
        for order, prelude, decls, nested in blocks(style):
            rules.append((f"{page.name}:{order}", prelude, decls, nested))

        # 1. find the drawn rules: a ::before/::after with a border and a draw
        drawn = []
        for note, prelude, decls, nested in rules:
            for sel in split_selectors(prelude):
                parsed = parse_selector(sel)
                if parsed is None:
                    continue
                host, pseudo = parsed
                if not pseudo:
                    continue
                ds = declarations(decls)
                anim = " ".join(v for p, v in ds if p.startswith("animation"))
                if not any(k in anim for k in DRAW_KEYFRAMES):
                    continue
                if not any(p.startswith("border") for p, _ in ds):
                    continue
                state, inset = {}, {}
                for p, v in ds:
                    apply_border(state, p, v, toks, note)
                    if p in ("top", "bottom", "inset-block-start", "inset-block-end"):
                        inset[EDGE[p.replace("inset-", "")] if p.startswith("inset-")
                              else p] = v
                edges = [e for e, s in state.items() if visible(s)]
                drawn.append((page.name, note, sel, host, pseudo, edges, sorted(inset)))

        # 2. for each, resolve the host box's own borders
        for pname, note, sel, host, pseudo, pedges, pinsets in drawn:
            elements = [c for c in classes_in(html) if host <= c]
            if not elements:
                unreadable.append(f"{pname}: {sel} matches no element in the markup")
                continue
            for classes in elements[:1]:
                state = {}
                bad_shape = None
                for hnote, prelude, decls, nested in rules:
                    for s in split_selectors(prelude):
                        parsed = parse_selector(s)
                        if parsed is None:
                            if re.search(r"\.(%s)\b" % "|".join(re.escape(c) for c in host), s):
                                bad_shape = s
                            continue
                        hclasses, hpseudo = parsed
                        if hpseudo or not hclasses or not hclasses <= classes:
                            continue
                        if nested:
                            bad_shape = s
                            continue
                        for p, v in declarations(decls):
                            apply_border(state, p, v, toks, hnote)
                if bad_shape:
                    unreadable.append(
                        f"{pname}: a rule for {sel}'s host is written as "
                        f"`{bad_shape}`, a selector shape this check cannot resolve")

                host_edges = {e: s for e, s in state.items()}
                bordered = [e for e, s in host_edges.items() if (s.get("w") or 0) > 0]
                painting = [e for e, s in host_edges.items() if visible(s) is True]

                resolved.append((pname, sel, sorted(bordered), sorted(painting),
                                 sorted(pedges), pinsets, host_edges))

                # rule 3 -- the box still paints a rule the pseudo replaces
                for e in painting:
                    findings.append(
                        f"{pname}: {sel} draws a rule, but its host still PAINTS "
                        f"a border-{e} ({host_edges[e]['w']:g}px "
                        f"{host_edges[e]['c'] or 'currentcolor'}, from "
                        f"{host_edges[e]['wfrom']}). The reader meets that one "
                        f"finished; the drawn one is a second hairline.")

                # rule 1 -- same edge
                if pedges and bordered and set(pedges) != set(bordered):
                    findings.append(
                        f"{pname}: {sel} borders its {'/'.join(sorted(pedges))} "
                        f"edge, but the box it draws for is bordered on its "
                        f"{'/'.join(sorted(bordered))} edge. A drawn rule has to "
                        f"be drawn where the rule is.")

                # rule 2 -- inset to the edge it borders
                if pedges and pinsets and set(pinsets) != set(pedges):
                    findings.append(
                        f"{pname}: {sel} borders {'/'.join(sorted(pedges))} but is "
                        f"inset to {'/'.join(pinsets)}; it draws at the far edge "
                        f"of the box from the rule it replaces.")

                # rule 4 -- the neutralisation that neutralises nothing
                for hnote, prelude, decls, nested in rules:
                    for s in split_selectors(prelude):
                        parsed = parse_selector(s)
                        if parsed is None or parsed[1] or not parsed[0] <= classes:
                            continue
                        for p, v in declarations(decls):
                            m = re.fullmatch(
                                r"border-(top|bottom|block-start|block-end)-color", p)
                            if not m or not TRANSPARENT.match(v.strip()):
                                continue
                            e = EDGE[m.group(1)]
                            if (host_edges.get(e, {}).get("w") or 0) <= 0:
                                findings.append(
                                    f"{pname}: `{s} {{ {p}: {v} }}` ({hnote}) "
                                    f"neutralises a border that is already 0 px "
                                    f"wide on that edge. It reads as the fix and "
                                    f"is a no-op.")

    if args.verbose:
        print(f"{len(resolved)} drawn rule(s) resolved\n")
        for pname, sel, bordered, painting, pedges, pinsets, st in resolved:
            print(f"  {pname}  {sel}")
            print(f"    pseudo borders : {pedges or '-'}   inset to: {pinsets or '-'}")
            print(f"    host bordered  : {bordered or '-'}   still painting: {painting or '-'}")
            for e, s in sorted(st.items()):
                print(f"      {e:<7} width={s['w']} colour={s['c']} ({s['wfrom']})")
            print()

    for u in unreadable:
        print(f"UNREADABLE  {u}")
    for f in findings:
        print(f"FINDING     {f}")

    if findings or unreadable:
        print(f"\n{len(findings)} finding(s), {len(unreadable)} unreadable.")
        return 1
    print(f"OK  {len(resolved)} drawn rule(s): each on the edge its box is "
          f"bordered on, inset to that edge, and no painted rule left behind.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
