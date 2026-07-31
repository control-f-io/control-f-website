#!/usr/bin/env python3
"""Recompute every contrast ratio the token file's guarantees rest on.

The eighteenth check, and the first whose subject is arithmetic the stylesheets
already show their work for. tokens.css does not treat contrast as a vibe: the
glass comment derives that 46 % white over a pure black frame renders
rgb(117,117,117) and clears 4.5:1 by 1.3 %, warns that 0.45 renders
rgb(115,115,115) and fails at 4.43:1, and closes "raise it or leave it". The
inverse block states that 56 % black is where white type still clears 4.5:1
composited over a pure white backdrop. colors.html publishes the wash's floor
and components.css says four separate times that a label sits on the page wash
and therefore may not be --text-muted, because #919191 on CF-Grau is 2.0:1.

Every one of those figures was computed by a person, once, on the day the
value was chosen. None of them is computed by anything since. The failure
shape is the one all seventeen checks beside this one exist for, in its purest
form: a token is one number in one file, every claim about it lives in prose
somewhere else, and the page after the nudge renders beautifully — slightly
lighter, slightly calmer, exactly what the person nudging it wanted — on every
screen belonging to anyone who would review it. The reader it fails for is the
one at the edge of the ratio, and they are not in the review.

WHAT THIS CHECK KNOWS THAT A SCREENSHOT CANNOT. The tightest guarantee in the
system clears its floor by 1.3 %. There is no screenshot, no diff, and no pair
of working eyes that can tell 4.56:1 from 4.43:1 — the entire difference
between "meets WCAG AA on every frame of any video" and "fails it" is below
the threshold of human comparison, which is why the comment that derived the
number had to derive it rather than look at it.

THE REGISTER. Same shape as the breakpoint register and the FOREIGN register
in check-a11y.py: a hand-kept list whose value is not that it is complete but
that what is on it can never rot silently. Each entry is one pair the shipping
pages actually render, its floor, and where the claim comes from. Ratios are
computed the way a browser paints them — alpha composited channel by channel
and ROUNDED TO THE RENDERED INTEGER before the luminance is taken, because
tokens.css itself documents that the unquantized figure is the wrong one to
quote (0.46 white over black computes 4.58 unquantized and renders 4.56).

Floors are WCAG 2.x AA: 4.5:1 for text, 3:1 for the focus indicator (2.4.11 /
1.4.11, non-text). They are floors and not the current figures on purpose — a
register of exact values would fail on every deliberate retune; a register of
floors fails only when a guarantee stops being true. The current figures are
what --verbose prints.

THE WASH IS CHECKED AT EVERY STOP. Text on the page sits on a gradient from
#CFCFD2 to white, so "on the page" is a range of backdrops, not one. The stops
are read out of --wash-stops rather than restated here; dark text's worst case
is the CF-Grau end today, but that is a fact about today's stops, not part of
the rule.

THE MUTED RULE. components.css states it in prose at least four times: what
sits on the page wash is never --text-muted, because 2.0:1. The users that
remain are each a decision with a documented reason, so — FOREIGN-register
shape again — they are enumerated, and a new `var(--text-muted)` as a color
anywhere in the shipping stylesheets or in a pattern page's own <style> block
is a finding until it is either moved to --text-secondary or added here with
a reason as good as the five below.

"THE SHIPPING STYLESHEETS" IS PLURAL, AND FOR MOST OF THIS RULE'S LIFE THE
SWEEP READ ONE FILE. The rule was written when components.css was the only
place a component could be styled, and it went on reading only that file after
acts.css was split out to carry the landing page's five acts. That is 200 KB
of shipping CSS — the whole body of the flagship page between the hero and the
FAQ — inside which the rule was unenforced and, measured on the rendered page
at 1280 x 800 with the type hidden and the pixels behind each run sampled:

  .lp-flow__val    "1 360 /s"     2.48:1     the rates the drawing's own
  .lp-flow__read   "74 °C"        2.25:1     arithmetic rests on, and the
                                             instrument readings beside them
  .map__tag i      "Hauptsitz"    1.89:1     a place name on the map
  .map__key-n      the counts     2.43:1     the legend's payload
  .sp-head__count  "4 Schritte"   2.31:1     32 px, so against a 3:1 floor

Five runs against a 4.5:1 floor (3:1 for the last, which is large text), none
of them chrome, none registered, none reachable by a check that opens one
file. base.css is swept too and contributes the one entry that is a definition
rather than a use. The sweep now reads every stylesheet a pattern page links.

  components.css ::placeholder      components/forms.html: the placeholder
                                    supplements the label, never replaces it —
                                    the label above the field carries the name
                                    at full contrast, and the hint dies the
                                    moment the field is typed in.
  components.css .cf-pin__index     the pinned stage's step counter. Ghosted
                                    chrome by design: the CURRENT step is
                                    inked to --text-primary by cf-pin-mark,
                                    the others recede. The information — where
                                    you are — is carried at full contrast.
  components.css cf-pin-mark        the keyframe pair of the same chrome: the
                                    rest state it returns each mark to.
  landing-page.html .lp-logo-wall   wordmarks in the partner wall. WCAG 1.4.3
                                    exempts text that is part of a logo or
                                    brand name, and a ghosted logo wall is the
                                    convention the exemption exists for.
  base.css       .t-muted           the utility's DEFINITION and not a use.
                                    It is registered rather than special-cased
                                    because base.css is now swept like the
                                    other two, and a definition is the one
                                    shape in that file the rule cannot mean.

A USE of `.t-muted` on a pattern page is a finding all the same, and none
exists today; the first one to arrive answers to this register.

stdlib only, no build step, no dependency — the same contract as the
seventeen checks beside it.

    python3 scripts/check-contrast.py       # check, exit 1 on a finding
    python3 scripts/check-contrast.py -v    # print every computed ratio
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOKENS = ROOT / "design-system" / "assets" / "css" / "tokens.css"
COMPONENTS = ROOT / "design-system" / "assets" / "css" / "components.css"
PATTERNS = ROOT / "design-system" / "patterns"

# Every stylesheet a pattern page <link>s, and therefore every stylesheet the
# muted rule has to hold. It was components.css alone for as long as the rule
# existed, which is why acts.css shipped four unregistered users of the token
# on the flagship page — see the module docstring.
CSS = ROOT / "design-system" / "assets" / "css"
SHIPPING = (CSS / "base.css", CSS / "components.css", CSS / "acts.css")

# -- reading the token file -------------------------------------------------

def declarations(css):
    """Custom-property declarations per scope: 'root' and 'inverse'.

    A small brace walker rather than a CSS parser. Only declarations directly
    under `:root` or `[data-theme="inverse"]` count — the @supports and @media
    blocks inside tokens.css re-declare gradients and geometry, never the flat
    colors this check reads, and crediting an override that only holds under a
    condition would make the register claim more than the page guarantees.
    """
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    scopes = {"root": {}, "inverse": {}}
    stack = []
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
    """Resolve a token to the color a browser would paint, per theme scope.

    The inverse scope reads its own declarations first and falls through to
    :root, which is exactly the cascade `[data-theme="inverse"]` produces.
    """

    def __init__(self, scopes):
        self.scopes = scopes

    def raw(self, name, scope):
        if scope == "inverse" and name in self.scopes["inverse"]:
            return self.scopes["inverse"][name]
        if name in self.scopes["root"]:
            return self.scopes["root"][name]
        raise KeyError("%s is not declared in tokens.css" % name)

    def color(self, spec, scope):
        """A color as (r, g, b, a) floats, following var() chains."""
        spec = spec.strip()
        m = re.fullmatch(r"var\(\s*(--[\w-]+)\s*\)", spec)
        if m:
            return self.color(self.raw(m.group(1), scope), scope)
        m = re.fullmatch(r"#([0-9a-fA-F]{6})", spec)
        if m:
            h = m.group(1)
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 1.0)
        m = re.fullmatch(r"#([0-9a-fA-F]{3})", spec)
        if m:
            h = m.group(1)
            return (int(h[0] * 2, 16), int(h[1] * 2, 16), int(h[2] * 2, 16), 1.0)
        m = re.fullmatch(
            r"rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*(?:,\s*([\d.]+)\s*)?\)",
            spec)
        if m:
            r, g, b = (float(m.group(i)) for i in (1, 2, 3))
            return (r, g, b, float(m.group(4)) if m.group(4) else 1.0)
        raise ValueError("%r does not resolve to a flat color" % spec)

    def wash_stops(self, scope):
        """Every flat color in --wash-stops — the backdrops 'on the page' means.

        The stop POSITIONS in that token are calc() expressions over numeric
        tokens, so anything that does not resolve to a color is a position and
        is passed over. Fewer than two colors would mean the token stopped
        being a gradient, which is a change this check must not absorb.
        """
        raw = self.raw("--wash-stops", scope)
        stops = []
        for spec in re.findall(r"#[0-9a-fA-F]{3,6}|var\(\s*--[\w-]+\s*\)", raw):
            try:
                stops.append((spec, self.color(spec, scope)))
            except ValueError:
                continue
        if len(stops) < 2:
            raise ValueError("--wash-stops no longer reads as a gradient of "
                             "flat colors; the register needs updating")
        return stops


# -- the arithmetic ---------------------------------------------------------

def over(fg, bg):
    """fg composited over an opaque bg, QUANTIZED to the rendered integers.

    tokens.css shows why the rounding is load-bearing: 0.46 white over black
    is 4.58:1 as real numbers and 4.56:1 as the rgb(117,117,117) that actually
    reaches the screen. The rendered integer is the truth this check reports.
    """
    a = fg[3]
    return (round(fg[0] * a + bg[0] * (1 - a)),
            round(fg[1] * a + bg[1] * (1 - a)),
            round(fg[2] * a + bg[2] * (1 - a)),
            1.0)


def luminance(c):
    def channel(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return (0.2126 * channel(c[0]) + 0.7152 * channel(c[1])
            + 0.0722 * channel(c[2]))


def ratio(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = (la, lb) if la > lb else (lb, la)
    return (hi + 0.05) / (lo + 0.05)


# -- the register -----------------------------------------------------------
# (label, scope, text spec, backdrop specs bottom-up, floor, the claim's home)
#
# A backdrop list ["#000000", "--surface-glass"] is black with the glass tint
# composited onto it — the order a browser stacks them. "wash" expands to one
# entry per stop of --wash-stops. Text with alpha is composited onto the final
# backdrop before the ratio is taken, same as the browser does.

WASH = "wash"

REGISTER = [
    ("text-primary on the page wash", "root",
     "var(--text-primary)", [WASH], 4.5,
     "colors.html: never drops below 11.91:1"),
    ("text-secondary on the page wash", "root",
     "var(--text-secondary)", [WASH], 4.5,
     "colors.html: the floor is the CF-Grau end"),
    ("text-secondary on surface-raised", "root",
     "var(--text-secondary)", ["var(--surface-raised)"], 4.5,
     "prose on cards and plates throughout components.css"),
    ("accent-ink on accent", "root",
     "var(--accent-ink)", ["var(--accent)"], 4.5,
     "tokens.css: 'text on lime'"),
    ("black type on bearing glass over a pure black frame", "root",
     "var(--text-primary)", ["#000000", "var(--surface-glass)"], 4.5,
     "tokens.css: 'the floor at which black type still clears 4.5:1 "
     "composited over a *pure black* backdrop' — clears by 1.3 %"),
    ("black type on the opaque glass stand-in", "root",
     "var(--text-primary)", ["var(--surface-glass-solid)"], 4.5,
     "tokens.css: the no-blur fallback carries the same text"),
    ("the focus ring against the page wash", "root",
     "var(--focus-ring)", [WASH], 3.0,
     "WCAG 1.4.11 — the ring is the one indicator every control shares"),
    ("inverse text on the inverse surface", "inverse",
     "var(--text-inverse)", ["var(--surface-inverse)"], 4.5,
     "the footer of every pattern page"),
    ("inverse text-secondary over Schwarz", "inverse",
     "var(--text-secondary)", ["var(--surface-page)"], 4.5,
     "tokens.css: '9.46:1 across the line'"),
    ("inverse text-muted over Schwarz", "inverse",
     "var(--text-muted)", ["var(--surface-page)"], 4.5,
     "48 % white — the register's tightest inverse figure"),
    ("text-inverse-dim over Schwarz", "inverse",
     "var(--text-inverse-dim)", ["var(--surface-page)"], 4.5,
     "the footer's secondary line"),
    ("white type on inverse glass over a pure white backdrop", "inverse",
     "var(--text-inverse)", ["#FFFFFF", "var(--surface-glass)"], 4.5,
     "tokens.css: '56 % black is where white type still clears 4.5:1 "
     "composited over a pure white backdrop'"),
    ("the inverse focus ring on Schwarz", "inverse",
     "var(--focus-ring)", ["var(--surface-page)"], 3.0,
     "WCAG 1.4.11, on the dark side"),
]

# The muted rule's exemptions: (file, selector-or-prelude substring, reason).
# See the module docstring for why each is a decision and not an oversight.
MUTED_EXEMPT = [
    ("base.css", ".t-muted", "the utility's DEFINITION, not a use of it"),
    ("components.css", "::placeholder", "supplements the label, never replaces it"),
    ("components.css", ".cf-pin__index", "ghosted chrome; the current step is inked"),
    ("components.css", "cf-pin-mark", "the same chrome's rest state"),
    ("landing-page.html", ".lp-logo-wall", "wordmarks — WCAG 1.4.3 logotype exemption"),
]


def rules(css):
    """(prelude, body) for every declaration block, however nested."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out = []
    prelude = ""
    stack = []
    for piece in re.split(r"([{}])", css):
        if piece == "{":
            stack.append(prelude.strip())
        elif piece == "}":
            if stack:
                stack.pop()
        else:
            prelude = piece.rsplit(";", 1)[-1].rsplit("}", 1)[-1]
            if stack and "--text-muted" in piece:
                out.append((" ".join(stack), piece))
    return out


def audit_muted():
    """Every color: var(--text-muted) outside the exemption register."""
    findings = []

    def sweep(name, css, exempt_here):
        for prelude, body in rules(css):
            if not re.search(r"color\s*:\s*var\(\s*--text-muted\s*\)", body):
                continue
            if any(marker in prelude for _, marker, _ in exempt_here):
                continue
            findings.append(
                (name, prelude,
                 "sets color: var(--text-muted). #919191 on the page wash is "
                 "2.0:1 — use --text-secondary, or add this rule to the "
                 "register in scripts/check-contrast.py with a reason."))

    for path in SHIPPING:
        sweep(path.name, path.read_text(encoding="utf-8"),
              [e for e in MUTED_EXEMPT if e[0] == path.name])

    for page in sorted(PATTERNS.glob("*.html")):
        text = page.read_text(encoding="utf-8")
        exempt_here = [e for e in MUTED_EXEMPT if e[0] == page.name]
        for style in re.findall(r"<style[^>]*>(.*?)</style>", text, flags=re.S):
            sweep(page.name, style, exempt_here)
        for m in re.finditer(r'class="[^"]*\bt-muted\b[^"]*"', text):
            findings.append(
                (page.name, m.group(0),
                 "uses the .t-muted utility on a pattern page. On the page "
                 "wash it is 2.0:1; if this use sits on an inverse surface "
                 "and clears 4.5:1, register it in scripts/check-contrast.py."))
    return findings


def audit_register(palette, verbose):
    findings, table = [], []
    for label, scope, fg_spec, bg_specs, floor, home in REGISTER:
        backdrops = []
        for spec in bg_specs:
            if spec == WASH:
                backdrops.extend(palette.wash_stops(scope))
            else:
                backdrops = [(spec,
                              over(palette.color(spec, scope),
                                   backdrops[-1][1]) if backdrops
                              else palette.color(spec, scope))]
        fg = palette.color(fg_spec, scope)
        worst = None
        for stop_spec, backdrop in backdrops:
            r = ratio(over(fg, backdrop), backdrop)
            if worst is None or r < worst[0]:
                worst = (r, stop_spec)
        table.append((worst[0], floor, label, worst[1]))
        if worst[0] < floor:
            findings.append(
                ("tokens.css", label,
                 "computes %.2f:1 (worst backdrop %s) against a floor of "
                 "%.1f:1. The claim this breaks: %s."
                 % (worst[0], worst[1], floor, home)))
    if verbose:
        for r, floor, label, at in table:
            print("  %6.2f:1  (floor %.1f, worst at %s)  %s"
                  % (r, floor, at, label))
        print()
    return findings


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print every computed ratio, not only the failures")
    args = ap.parse_args()

    palette = Palette(declarations(TOKENS.read_text(encoding="utf-8")))
    findings = audit_register(palette, args.verbose)
    findings += audit_muted()

    if findings:
        for where, what, why in findings:
            print("%s  %s\n    %s" % (where, what, why), file=sys.stderr)
        print("\n%d contrast finding%s."
              % (len(findings), "" if len(findings) == 1 else "s"),
              file=sys.stderr)
        return 1

    print("contrast: %d pairs recomputed from tokens.css and every floor "
          "holds; %d exempt users of --text-muted and no unregistered one."
          % (len(REGISTER), len(MUTED_EXEMPT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
