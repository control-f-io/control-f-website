#!/usr/bin/env python3
"""A focus ring drawn over artwork has an edge no frame can take away.

check-focus-ring.py holds the ring's REACH — that every element which takes
focus gets the system's indicator rather than the user agent's. This holds the
half that check cannot see: whether the indicator, once drawn, is visible.

WHY REACH IS NOT ENOUGH. base.css draws one ring:

    outline: var(--stroke-2) solid var(--focus-ring);
    outline-offset: 2px;

The offset is 2 px, so the ring occupies 2-4 px OUTSIDE the border box. Both of
its edges are therefore against whatever is behind the ELEMENT — never against
the element's own plate, which the offset has just stepped over. On a page whose
surfaces the stylesheet owns that is fine: the wash is a known colour and the
ring's outer edge is a computable ratio, which is what check-contrast.py's
register carries.

The landing page's hero is not a surface the stylesheet owns. It is a video, its
poster is a full-bleed abstract, and its dominant hue is this brand's own lime —
so a lime ring over it is the one colour guaranteed to disappear, and a black
ring over its light passages is the other. components.css derives this in full
over .cf-btn--glass: neither single colour can hold, because black clears 3:1
only where the backdrop is darker than L 0.100 and lime only where it is lighter
than L 0.258, and no sampling of frames closes a gap that is a property of the
artwork rather than of any one frame.

THE ANSWER THE SYSTEM SETTLED ON is a two-tone ring: the outline in one colour
and an inner ring, drawn with box-shadow, filling the offset in the other. The
boundary BETWEEN them is internal to the indicator. It is not on the artwork, no
frame reaches it, and it is the edge that carries the indicator when the outer
one washes out. .cf-btn--glass has carried that construction and its derivation
since it was written.

WHAT WAS MEASURED, AND WHY THIS IS A SCRIPT. Three of the four indicators over
that hero had only the outline. Worst edge of eight sampled per control, against
the poster, at four widths — the floor is 3:1, WCAG 1.4.11:

    .cf-logo                  1.24  1.32  1.28  1.40
    .cf-nav__toggle           1.28  1.06     -     -
    .cf-hero__still           1.18  1.15  1.00  1.01
    .cf-btn--glass           18.51 18.51 18.51 18.51   <- the one with the ring

The 1.00 is not a rounding. At 1280 the pause control's plate sits over the
artwork's lime passage and the ring is rgb(225,255,0) against rgb(225,254,99):
the indicator and the backdrop are the same colour, on the one control WCAG
2.2.2 requires this page to provide.

Every one of those rendered correctly. A screenshot of the focused control shows
a ring — it is there, it is 2 px, it is the system's colour. Nothing in the
markup, the diff, or the review says which pixels are underneath it. That is the
failure shape this directory exists for, and it is worse than most: the reader
it fails is a keyboard reader on the flagship page's primary navigation, and
they are never in the review.

WHAT IS COUNTED. Two things, and the second is what keeps the first honest.

  THE REGISTER, below: every focus indicator in the tree that is drawn over a
  surface the stylesheets do not control. For each, this check proves the rule
  still exists, still declares an inner ring, and that the two tones still clear
  3:1 against each other in the theme scope the element renders in. Same shape
  as check-contrast.py's register and check-a11y.py's FOREIGN list, and for the
  reason check-contrast.py states: the value of a hand-kept list is not that it
  is complete, it is that what is on it can never rot silently.

  THE SWEEP: any :focus-visible rule in the shipping stylesheets that takes the
  outline off var(--focus-ring) onto a fixed colour has done so BECAUSE the
  surface under it is not the system's surface. That is the whole reason such a
  rule is ever written. So every one of them has to be in the register — either
  with an inner ring, or with a line saying which controlled surface it sits on.
  A new one appearing anywhere fails until somebody says which it is.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS_DIR = ROOT / "design-system" / "assets" / "css"
TOKENS = CSS_DIR / "tokens.css"
SHIPPING = ["tokens.css", "base.css", "components.css", "acts.css"]

FLOOR = 3.0          # WCAG 1.4.11 / 2.4.11, non-text contrast

# -- the register -----------------------------------------------------------
# (selector, scope, what is behind it, why it needs an internal edge)
#
# scope is the theme the element renders under, because --focus-ring flips to
# lime at [data-theme="inverse"] and the two tones must clear 3:1 as painted.

REGISTER = [
    (".cf-btn--glass:focus-visible", "root",
     "the hero video, at outline-offset outside the glass plate",
     "components.css derives this one at length: the plate's contrast floor "
     "does not extend past the border box, and the ring starts 2 px past it."),
    (".cf-nav :focus-visible", "root",
     "the hero video, for any control the bar's plate does not carry",
     "every control is inside .cf-nav__bar's black plate today and every ring "
     "in the bar falls on black at 18.51:1; the rule stays two-tone because "
     ".cf-logo and .cf-nav__toggle measured 1.06-1.40:1 against the artwork "
     "the day they stood on it, and a plate that is re-cut or made glass "
     "hands that back."),
    (".cf-hero__still-toggle:focus-visible ~ .cf-hero__still", "inverse",
     "the hero video, on the WCAG 2.2.2 pause control",
     "the label carries data-theme=\"inverse\", so --focus-ring resolves to "
     "lime — over an artwork whose dominant hue is lime."),
]

# A rule may be in the register WITHOUT an inner ring only if it is named here,
# with the controlled surface it sits on. Empty on purpose: every indicator over
# artwork in this tree is two-tone today, and an entry added here is a claim
# that a surface is owned, which is a claim somebody has to write down.
ON_A_CONTROLLED_SURFACE = {}


# -- reading the stylesheets ------------------------------------------------

def strip_comments(css):
    """Drop comment CONTENT but keep every newline, so a reported line number is
    the line the reader will find the declaration on. Same reason
    check-focus-ring.py blanks rather than strips: this tree comments in
    paragraphs, and removing them outright moves every citation by hundreds of
    lines."""
    return re.sub(r"/\*.*?\*/",
                  lambda m: "\n" * m.group(0).count("\n"), css, flags=re.S)


def declarations(css):
    """Custom properties under :root and [data-theme="inverse"].

    The same brace walker check-contrast.py uses, and for the same reason: only
    declarations directly under those two preludes count, because a token
    re-declared inside @media or @supports is a conditional value and this check
    may not credit a guarantee that only holds under a condition.
    """
    css = strip_comments(css)
    scopes = {"root": {}, "inverse": {}}
    stack = []
    prelude = ""
    for piece in re.split(r"([{}])", css):
        if piece == "{":
            stack.append(prelude.strip())
        elif piece == "}":
            if stack:
                stack.pop()
        else:
            prelude = piece.rsplit(";", 1)[-1]
            if len(stack) != 1:
                continue
            scope = {":root": "root",
                     '[data-theme="inverse"]': "inverse"}.get(stack[0])
            if not scope:
                continue
            for name, value in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", piece):
                scopes[scope][name] = value.strip()
    return scopes


class Palette:
    def __init__(self, scopes):
        self.scopes = scopes

    def raw(self, name, scope):
        if scope == "inverse" and name in self.scopes["inverse"]:
            return self.scopes["inverse"][name]
        if name in self.scopes["root"]:
            return self.scopes["root"][name]
        raise KeyError("%s is not declared in tokens.css" % name)

    def color(self, spec, scope):
        spec = spec.strip()
        m = re.fullmatch(r"var\(\s*(--[\w-]+)\s*\)", spec)
        if m:
            return self.color(self.raw(m.group(1), scope), scope)
        m = re.fullmatch(r"#([0-9a-fA-F]{6})", spec)
        if m:
            h = m.group(1)
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
        m = re.fullmatch(r"#([0-9a-fA-F]{3})", spec)
        if m:
            h = m.group(1)
            return (int(h[0] * 2, 16), int(h[1] * 2, 16), int(h[2] * 2, 16))
        m = re.fullmatch(
            r"rgba?\(\s*([\d.]+)\s*,?\s+?([\d.]+)\s*,?\s+?([\d.]+)\s*\)"
            r"|rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*\)", spec)
        if m:
            g = [v for v in m.groups() if v is not None]
            return tuple(round(float(v)) for v in g[:3])
        raise ValueError("%r does not resolve to a flat colour" % spec)


def luminance(c):
    def ch(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(c[0]) + 0.7152 * ch(c[1]) + 0.0722 * ch(c[2])


def ratio(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = (la, lb) if la > lb else (lb, la)
    return (hi + 0.05) / (lo + 0.05)


# -- finding the rules ------------------------------------------------------

RULE = re.compile(r"([^{}();]*:focus-visible[^{}]*?)\{([^{}]*)\}", re.S)


def rules():
    """Every :focus-visible rule in the shipping stylesheets, by selector."""
    found = {}
    for name in SHIPPING:
        path = CSS_DIR / name
        if not path.exists():
            continue
        css = strip_comments(path.read_text(encoding="utf-8"))
        for m in RULE.finditer(css):
            sel = " ".join(m.group(1).split())
            # From where the SELECTOR starts, not where the match does. The
            # prelude term crosses newlines, so a match that follows a blanked
            # paragraph of comment begins hundreds of lines above the rule.
            start = m.start() + (len(m.group(1)) - len(m.group(1).lstrip()))
            line = css[:start].count("\n") + 1
            found.setdefault(sel, []).append((name, line, m.group(2)))
    return found


def outline_colour(body):
    """The colour the outline paints, or None if the rule does not set one."""
    m = re.search(r"outline-color\s*:\s*([^;]+)", body)
    if m:
        return m.group(1).strip()
    m = re.search(r"outline\s*:\s*([^;]+)", body)
    if m:
        parts = m.group(1).strip()
        if parts == "none" or parts == "0":
            return None
        # `outline: <width> solid <colour>` — the colour is the last token, and
        # var() may contain no spaces in this tree, so a split is safe.
        toks = re.findall(r"var\([^)]*\)|[^\s]+", parts)
        return toks[-1] if toks else None
    return None


def inner_ring(body):
    """The colour of the box-shadow ring, or None."""
    m = re.search(r"box-shadow\s*:\s*([^;]+)", body)
    if not m:
        return None
    spec = m.group(1).strip()
    if spec in ("none", "0"):
        return None
    toks = re.findall(r"var\([^)]*\)|[^\s]+", spec)
    return toks[-1] if toks else None


def main():
    palette = Palette(declarations(TOKENS.read_text(encoding="utf-8")))
    all_rules = rules()
    problems = []

    # -- the register -------------------------------------------------------
    for sel, scope, behind, why in REGISTER:
        hits = all_rules.get(sel)
        if not hits:
            problems.append(
                "  %s\n"
                "    is in this check's register and no longer exists in the "
                "shipping stylesheets.\n"
                "    It was the focus indicator over %s.\n"
                "    If the control is gone, take the entry with it. If the "
                "selector was renamed,\n"
                "    rename it here — the guarantee did not move with it."
                % (sel, behind))
            continue
        name, line, body = hits[-1]
        ocol = outline_colour(body)
        if ocol is None:
            # The colour may be inherited from base.css's rule; the register
            # entry names the scope, so --focus-ring is the value in play.
            ocol = "var(--focus-ring)"
        icol = inner_ring(body)
        if icol is None:
            if sel in ON_A_CONTROLLED_SURFACE:
                continue
            problems.append(
                "  %s\n    %s:%d — no inner ring.\n"
                "    Behind it: %s.\n"
                "    %s\n"
                "    The outline is drawn at outline-offset, so BOTH of its "
                "edges are on that\n"
                "    surface and neither is guaranteed. Fill the offset with "
                "an inner ring —\n"
                "      box-shadow: 0 0 0 var(--stroke-2) <the other tone>;\n"
                "    — so the boundary between the two tones carries the "
                "indicator. That edge is\n"
                "    internal and no frame of the artwork can reach it. "
                ".cf-btn--glass is the\n"
                "    worked example, with its derivation."
                % (sel, name, line, behind, why))
            continue
        try:
            a = palette.color(ocol, scope)
            b = palette.color(icol, scope)
        except (KeyError, ValueError) as exc:
            problems.append(
                "  %s\n    %s:%d — cannot resolve the two tones: %s\n"
                "    outline %s, inner ring %s, scope %s."
                % (sel, name, line, exc, ocol, icol, scope))
            continue
        r = ratio(a, b)
        if r < FLOOR:
            problems.append(
                "  %s\n    %s:%d — the two tones are %.2f:1, under the %.1f:1 "
                "floor.\n"
                "    outline %s -> rgb%s, inner ring %s -> rgb%s, as painted "
                "under %s.\n"
                "    The internal boundary IS the guarantee here; at this "
                "ratio there is no\n"
                "    edge left that the artwork cannot wash out."
                % (sel, name, line, r, FLOOR, ocol, a, icol, b, scope))

    # -- the sweep ----------------------------------------------------------
    registered = {sel for sel, _, _, _ in REGISTER}
    for sel, hits in sorted(all_rules.items()):
        if sel in registered:
            continue
        for name, line, body in hits:
            ocol = outline_colour(body)
            if ocol is None:
                continue
            if "--focus-ring" in ocol:
                continue
            problems.append(
                "  %s\n    %s:%d — takes the ring off var(--focus-ring) onto "
                "%s, and is not\n"
                "    in this check's register.\n"
                "    A rule only ever does that because the surface under the "
                "control is not the\n"
                "    system's surface. Say which surface: add it to REGISTER "
                "in\n"
                "    scripts/check-focus-ring-edge.py with the tone it needs, "
                "or — if it sits on a\n"
                "    plate the stylesheet owns and can compute — name it in "
                "ON_A_CONTROLLED_SURFACE\n"
                "    with that plate. Either way somebody writes down what is "
                "behind it."
                % (sel, name, line, ocol))

    if problems:
        print("check-focus-ring-edge: a focus indicator has no edge the "
              "artwork cannot take.\n", file=sys.stderr)
        print("\n\n".join(problems), file=sys.stderr)
        print("\nFloor is %.1f:1 — WCAG 1.4.11, the same one check-contrast.py "
              "carries for\nthe indicator pairs it can compute from tokens "
              "alone." % FLOOR, file=sys.stderr)
        sys.exit(1)

    lines = []
    for sel, scope, behind, _ in REGISTER:
        name, line, body = all_rules[sel][-1]
        ocol = outline_colour(body) or "var(--focus-ring)"
        icol = inner_ring(body)
        if icol is None:
            lines.append("    %-52s on a controlled surface" % sel)
            continue
        r = ratio(palette.color(ocol, scope), palette.color(icol, scope))
        lines.append("    %-52s %6.2f:1" % (sel, r))
    print("check-focus-ring-edge: OK — every indicator over artwork carries an "
          "internal edge.")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
