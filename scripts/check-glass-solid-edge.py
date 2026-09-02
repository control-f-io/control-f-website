#!/usr/bin/env python3
"""When glass goes opaque, its edge has to turn over with it.

The hundred-and-forty-seventh check, and it is --surface-sunken's argument
arriving at the one token that never got it.

THE ARGUMENT, WHICH THIS FILE DOES NOT INVENT. tokens.css retired #E7E7E7 as a
panel surface and published the measurement that retired it: the page wash is
`background-attachment: fixed` and `background-size: cover`, so it spans the
VIEWPORT rather than the document and runs its full CF-Grau-to-white range on
every screen, at every scroll position. An absolute grey inside that range is
therefore

    raised at the top of the screen, INVISIBLE at 65 % of it, and sunken below
    that -- one block that changes which way it steps as the reader scrolls
    past it. Nothing renders wrong; the material simply is not one.

--surface-sunken became a veil that day. --surface-glass-solid did not, and
--surface-glass-solid IS #E7E7E7: the same value, on a panel that stands on the
same wash. It cannot become a veil -- it is the opaque stand-in that holds
4.5:1 for bearing glass when the browser cannot blur, and tokens.css names a
translucent tint with the blur switched off as the worst of the three states,
because the artwork behind it then bleeds through sharp. Nothing opaque and
light escapes the wash's range anyway; the wash covers 207 to 255.

SO THE THING THAT HAS TO BE RELATIVE IS THE BOUNDARY. A panel whose fill can
equal the page anywhere on the screen is a panel identified by its edge, and
that edge was --glass-border -- white at 55 %, authored for a frosted sheet
over a backdrop dark enough and busy enough to hold a white line. On an opaque
light plate on the wash it collapses with the fill. Measured on
patterns/expertise.html with the act rail open, the plate 278 px tall in the
left margin, sampling its own border column and the wash six pixels outside it:

                          wash   plate:wash   white rim   --border-default
    1440x900   top row     220      1.090       1.226         1.627
               bottom      233      1.049       1.072         1.861
    1920x1080  top row     221      1.072       1.205         1.655
               bottom      231      1.030       1.092         1.827

The plate is lighter than the page at its top row and darker at its bottom one,
and the rim goes with it rather than surviving it -- 1.07:1 on a panel already
at 1.05:1. At the bottom of its own height the panel had no boundary at all.

WHAT THIS CHECKS, AND WHY IT IS A CHECK. The rule is one sentence:

    wherever the material's blur is off and its surface is opaque, the border
    must step AWAY from the wash's own direction -- a contour that removes
    light under a light plate, a rim that adds it under a dark one.

That is invisible in a screenshot in the way this directory's other scripts
mean it: the fallback tiers are two @media/@supports blocks nobody renders by
accident, the failure is a 1.07:1 line rather than a missing one, and it only
appears at the bottom of a plate tall enough to cross the wash. A later run
adding a fourth tint to those blocks, or turning --glass-border back to white
because the frosted form wants it, gets the same defect back with nothing to
say so.

NOTHING HERE IS A LIST. The wash's range is read off --wash-stops, the tiers
are found by looking for --glass-blur: none rather than by naming @supports and
prefers-reduced-transparency, and the surfaces are whatever those tiers assign
to the glass tints -- the same derivation check-glass-budget.py uses when it
takes every backdrop-filter rule's selectors as the definition of glass. A
fifth tint, a third tier or a fourth theme enters this check by existing.

THE SECOND CLAIM is the same sentence outside those blocks. .act-rail::before
paints --surface-glass-solid as its own background on patterns/expertise.html
unconditionally -- the one plate in the system that ships the no-blur form by
DEFAULT rather than as a fallback -- so it is not inside any tier this script
finds by the first claim, and it had exactly the defect the first claim is
about. Any rule that paints the opaque stand-in and does not declare
backdrop-filter beside it must not take --glass-border either.

Run:  python3 scripts/check-glass-solid-edge.py [-v]
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system" / "assets" / "css"

SHIPPING_CSS = ("tokens.css", "base.css", "components.css", "acts.css")

# The tints the material declares. A tier switches the blur off and reassigns
# these; which of them it reassigns is the tier's business, not this file's.
GLASS_TINTS = ("--surface-glass", "--surface-glass-thin", "--surface-glass-veil")

# The scopes a token can be declared in. Both are page roots; an element inside
# an inverse section resolves against the second, which is why tokens.css
# repeats every fallback in both.
SCOPES = (":root", '[data-theme="inverse"]')


def strip_comments(text):
    return re.sub(r"/\*.*?\*/", "", text, flags=re.S)


def blocks(text):
    """Yield (context, selector, body, line) for every declaration block.

    context is the chain of at-rule preludes the block sits inside, joined
    with " / ", so a rule inside @supports inside @media reports both.
    """
    out = []
    stack = []
    i = 0
    n = len(text)
    start = 0
    while i < n:
        ch = text[i]
        if ch == "{":
            head = text[start:i].strip()
            if head.startswith("@"):
                stack.append((head, i))
                start = i + 1
            else:
                depth = 1
                j = i + 1
                while j < n and depth:
                    if text[j] == "{":
                        depth += 1
                    elif text[j] == "}":
                        depth -= 1
                    j += 1
                body = text[i + 1:j - 1]
                out.append((" / ".join(h for h, _ in stack), head, body,
                            text.count("\n", 0, i) + 1))
                i = j
                start = j
                continue
        elif ch == "}":
            if stack:
                stack.pop()
            start = i + 1
        i += 1
    return out


def declarations(body):
    decls = {}
    depth = 0
    buf = ""
    for ch in body:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
        if ch == ";" and depth == 0:
            if ":" in buf:
                k, v = buf.split(":", 1)
                decls[k.strip()] = v.strip()
            buf = ""
        else:
            buf += ch
    if ":" in buf:
        k, v = buf.split(":", 1)
        decls[k.strip()] = v.strip()
    return decls


HEX = re.compile(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b")
RGBA = re.compile(r"rgba?\(\s*([\d.]+)[\s,]+([\d.]+)[\s,]+([\d.]+)"
                  r"(?:[\s,/]+([\d.]+%?))?\s*\)")


def parse_colour(value):
    """(r, g, b, a) from a hex or rgb()/rgba() literal, or None."""
    m = HEX.search(value)
    if m:
        h = m.group(1)
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 1.0)
    m = RGBA.search(value)
    if m:
        a = m.group(4)
        if a is None:
            alpha = 1.0
        elif a.endswith("%"):
            alpha = float(a[:-1]) / 100.0
        else:
            alpha = float(a)
        return (float(m.group(1)), float(m.group(2)), float(m.group(3)), alpha)
    return None


def luminance(rgb):
    def f(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(rgb[0]) + 0.7152 * f(rgb[1]) + 0.0722 * f(rgb[2])


def ratio(a, b):
    la, lb = luminance(a), luminance(b)
    if la < lb:
        la, lb = lb, la
    return (la + 0.05) / (lb + 0.05)


def over(fg, bg):
    """Composite a possibly translucent colour onto an opaque one."""
    a = fg[3]
    return tuple(fg[i] * a + bg[i] * (1 - a) for i in range(3)) + (1.0,)


def base_scopes(token_rules):
    """The unconditional value of every custom property, per page root.

    The inverse scope INHERITS the light theme's table and overrides part of
    it, which is what an element inside an inverse section actually resolves
    against: --surface-glass-solid is redeclared there, --grey-800 is not, and
    reading the inverse block on its own leaves the second one unresolvable.
    """
    scoped = {s: {} for s in SCOPES}
    for scope in SCOPES:
        for context, selector, body, _ in token_rules:
            if context:
                continue
            head = selector.strip()
            if head == scope or head.startswith(scope + ","):
                for k, v in declarations(body).items():
                    if k.startswith("--"):
                        scoped[scope][k] = v
    for scope in SCOPES[1:]:
        merged = dict(scoped[SCOPES[0]])
        merged.update(scoped[scope])
        scoped[scope] = merged
    return scoped


def resolve(value, table, seen=None):
    """Substitute var() until a literal falls out. Cycles resolve to None."""
    seen = seen or set()
    for _ in range(12):
        m = re.search(r"var\(\s*(--[\w-]+)\s*(?:,([^()]*))?\)", value)
        if not m:
            return value
        name = m.group(1)
        if name in seen or name not in table:
            fallback = (m.group(2) or "").strip()
            if not fallback:
                return None
            value = value[:m.start()] + fallback + value[m.end():]
            continue
        seen = seen | {name}
        value = value[:m.start()] + table[name] + value[m.end():]
    return None


def wash_range(table):
    """The relative luminance the page wash actually covers on a screen.

    Read off --wash-stops rather than restated: the stops are what the wash
    IS, and the positions between them are irrelevant here -- a ramp covers
    every luminance between its endpoints whatever the offsets do. The stop
    list carries calc()s full of commas and parentheses, so the colours are
    picked out one at a time (a hex, or a var() whose root value is a colour)
    instead of by splitting the value.
    """
    stops = table.get("--wash-stops", "")
    if not stops:
        return None
    colours = []
    for token in re.finditer(r"#[0-9a-fA-F]{3,6}\b|rgba?\([^()]*\)"
                             r"|var\(\s*(--[\w-]+)\s*\)", stops):
        name = token.group(1)
        text = table.get(name, "") if name else token.group(0)
        c = parse_colour(text) if text else None
        if c:
            colours.append(c)
    if len(colours) < 2:
        return None
    lums = [luminance(c) for c in colours]
    return min(lums), max(lums), colours


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print every tier and surface examined, not only faults")
    args = ap.parse_args()

    parsed = {}
    for name in SHIPPING_CSS:
        path = CSS / name
        if not path.exists():
            print("missing stylesheet: %s" % path)
            return 1
        parsed[name] = blocks(strip_comments(path.read_text(encoding="utf-8")))

    scoped = base_scopes(parsed["tokens.css"])
    light = scoped[":root"]
    span = wash_range(light)
    if not span:
        print("check-glass-solid-edge: --wash-stops did not resolve to two or "
              "more colours, so the range this check is about cannot be "
              "derived. Fix the token or this script.")
        return 1
    wash_lo, wash_hi, wash_colours = span

    problems = []
    examined = []

    # Claim 1 -- every tier that switches the blur off.
    for name, bs in parsed.items():
        for context, selector, body, line in bs:
            decls = declarations(body)
            if decls.get("--glass-blur", "").strip() != "none":
                continue
            head = selector.strip()
            scope = ":root"
            for s in SCOPES:
                if s in head:
                    scope = s
            table = dict(scoped.get(scope, {}))
            table.update({k: v for k, v in decls.items() if k.startswith("--")})

            border = parse_colour(resolve(table.get("--glass-border", ""),
                                          table) or "")
            for tint in GLASS_TINTS:
                if tint not in decls:
                    continue
                surface = parse_colour(resolve(decls[tint], table) or "")
                if not surface:
                    continue
                if surface[3] < 0.999:
                    # Still translucent: the material has not gone opaque, so
                    # the boundary question this check asks does not arise.
                    examined.append("%s:%d  %s  %s translucent, skipped"
                                    % (name, line, context or head, tint))
                    continue
                if not border:
                    problems.append(
                        "%s:%d  %s\n      %s is opaque here and --glass-border "
                        "does not resolve to a colour, so the plate has no "
                        "boundary this check can read."
                        % (name, line, context or head, tint))
                    continue
                painted = over(border, surface)
                inside = wash_lo <= luminance(surface) <= wash_hi
                lighter = luminance(painted) > luminance(surface)
                want_darker = luminance(surface) > wash_lo
                examined.append(
                    "%s:%d  %-58s %s surface %s  border %s  %s"
                    % (name, line, (context or head)[:58], tint,
                       tuple(round(c) for c in surface[:3]),
                       tuple(round(c) for c in painted[:3]),
                       "inside the wash" if inside else "outside the wash"))
                if want_darker and lighter:
                    problems.append(
                        "%s:%d  %s\n"
                        "      %s is opaque at %s, which the wash reaches, and "
                        "--glass-border paints %s over it -- a LIGHTER line on "
                        "a light plate, %.3f:1 against it.\n"
                        "      The wash runs %s to %s on every screen, so this "
                        "plate is raised at the top of the viewport and sunken "
                        "at the bottom. Its fill cannot be the thing that "
                        "identifies it; its edge has to be, and a light edge on "
                        "a light plate is not one. Take a contour that removes "
                        "light -- --border-default is 24 %% of whatever is "
                        "behind it, a constant ratio at both ends of the wash."
                        % (name, line, context or head, tint,
                           tuple(round(c) for c in surface[:3]),
                           tuple(round(c) for c in painted[:3]),
                           ratio(painted, surface),
                           tuple(round(c) for c in wash_colours[0][:3]),
                           tuple(round(c) for c in wash_colours[-1][:3])))
                if not want_darker and not lighter:
                    problems.append(
                        "%s:%d  %s\n"
                        "      %s is opaque at %s, darker than every colour the "
                        "wash takes, and --glass-border paints %s over it -- a "
                        "darker line on a dark plate, %.3f:1 against it.\n"
                        "      The argument is the same one the right way up: a "
                        "plate below the page's range is bounded by adding "
                        "light, not by removing it."
                        % (name, line, context or head, tint,
                           tuple(round(c) for c in surface[:3]),
                           tuple(round(c) for c in painted[:3]),
                           ratio(painted, surface)))

    # Claim 2 -- the opaque stand-in painted outside any of those tiers.
    plates = 0
    for name, bs in parsed.items():
        if name == "tokens.css":
            continue
        for context, selector, body, line in bs:
            decls = declarations(body)
            fill = " ".join(decls.get(p, "") for p in ("background",
                                                       "background-color"))
            if "--surface-glass-solid" not in fill:
                continue
            plates += 1
            blurred = any("backdrop-filter" in k for k in decls)
            edge = " ".join(decls.get(p, "") for p in ("border", "border-color",
                                                       "border-top", "outline"))
            examined.append("%s:%d  %s  paints the opaque stand-in, %s"
                            % (name, line, selector.strip(),
                               "blurred" if blurred else "no blur"))
            if not blurred and "--glass-border" in edge:
                problems.append(
                    "%s:%d  %s\n"
                    "      paints --surface-glass-solid with no backdrop-filter "
                    "beside it and still takes --glass-border.\n"
                    "      This is the material's opaque form shipping by "
                    "default rather than as a fallback, so it is not inside any "
                    "tier the first claim finds -- and it is an absolute grey on "
                    "the wash bounded by a white line, which is the whole defect "
                    "one rule further out. Give it a contour."
                    % (name, line, selector.strip()))

    if args.verbose:
        for line in examined:
            print("  " + line)

    if problems:
        print("Glass went opaque and its edge did not turn over with it.\n")
        for p in problems:
            print("  " + p + "\n")
        print("tokens.css states the rule this enforces, beside --surface-sunken")
        print("and again in both fallback blocks: a panel that needs a surface")
        print("takes the veil, and a panel that needs a boundary takes a contour.")
        return 1

    print("check-glass-solid-edge: wash %s..%s (relative luminance %.3f..%.3f), "
          "%d opaque glass surface%s across the no-blur tiers, %d plate%s "
          "painting the stand-in outright, every edge stepping away from the "
          "page."
          % (tuple(round(c) for c in wash_colours[0][:3]),
             tuple(round(c) for c in wash_colours[-1][:3]),
             wash_lo, wash_hi,
             len([e for e in examined if "surface (" in e]),
             "" if len([e for e in examined if "surface (" in e]) == 1 else "s",
             plates, "" if plates == 1 else "s"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
