#!/usr/bin/env python3
"""No colour or off-scale literal in a pattern page's own CSS.

Every literal gate in this suite stops at the three shipping stylesheets, and
each says so on purpose. check-spacing-scale.py: "per-page <style> blocks and
prototypes/ are deliberately out of scope." The breakpoint register in
tokens.css: same boundary, same reason — governing page-local CSS from the
shipping side would make the register look like it governed chrome it does
not ship. check-local-thresholds.py exists because that exclusion, correct as
it is, left page-local THRESHOLDS registered nowhere; this file exists because
the same exclusion leaves every OTHER page-local literal gated nowhere.

The exposure is not hypothetical, it is the section's history. Each pattern
page grew a <style> block under deadline, and each block was a small private
fork of the system: expertise.html's block carried the pinned stage byte for
byte until it moved to components.css, the landing page's block carried a
statement figure until the component grew one, and both preambles now open by
listing what LEFT. The blocks that remain are clean — measured today, the two
blocks under patterns/ carry not one colour literal, not one spacing length,
not one font size or weight or radius or shadow or duration typed as a
literal; every value that is a design decision arrives as a token, and every
literal that remains is a derivation documented in place (a lattice cell, a
travel unit, an em floor against wrap). That cleanliness cost eleven pages of
review to reach, and nothing holds it: a `color: #E1FF00` typed into a
pattern's <style> block tomorrow renders correctly, ships to production, and
diverges the day the token moves — the exact failure class every check in
this suite exists for, on the one surface none of them read.

WHAT IT CHECKS. Under design-system/patterns/*.html, in page-local <style>
blocks and style="" attributes — and in every PAGE STYLESHEET those pages
link, with comments stripped:

A page stylesheet is any .css a pattern page links beyond the five shared
sheets (the three shipping ones, docs.css, preview.css). Today that is
acts.css: 216 KB of the landing page's five acts, split out of the page in
the same move that split the acts out of the markup. The split changed where
the bytes live and not who owns the decisions in them — it is a page-local
<style> block in a file — but it walked those bytes out of this gate's
original scope, and out of every other literal gate at the same time, because
the shipping gates stop at the three sheets they name. Measured on the day
this scope was widened, the walk had already cost: acts.css carried
`var(--nav-height, 5rem)` against a token whose value is 5.25rem — a fallback
that restated the token and got it wrong on the day it was typed — plus two
token values retyped as fallback hexes and the --radius-full value retyped as
its literal. A sheet born later is read here from birth: discovery is by
<link>, not by name.

  COLOUR    no colour literal, full stop. Hex and functional notation
            (rgb/hsl/hwb/lab/lch/oklab/oklch/color/color-mix) anywhere a
            value can carry one — declarations in <style> blocks AND
            custom-property data in style="" attributes, because a custom
            property is a value pipe and a colour poured in at the top comes
            out painted at the bottom. Named colours are flagged only in a
            colour-carrying property, so `animation: pane linear both` never
            trips over `linear`. Colour comes from tokens.css; there is no
            page-local colour decision on this site.

  SPACING   margin/padding/gap: a px or rem length is a token's job. The
            property set and length grammar are check-spacing-scale.py's own,
            so the two gates cannot drift apart in what they call spacing.
            em/%/vw stay unflagged there and stay unflagged here: relative to
            things the scale does not govern.

  TYPE      font-size, font-weight, letter-spacing: the scale is
            --text-* / --weight-* / --tracking-*. `font-weight: normal` and
            zero letter-spacing pass — resets, not decisions.

  RADIUS    border-radius and its corners: --radius-none/sm/full is the whole
            radius vocabulary, and anything typed past it is exactly the
            drift the token's own comment warns about.

  SHADOW    a box-shadow that references no var() is a hand-rolled elevation;
            the system ships three.

  MOTION    a ms/s literal or a cubic-bezier() in transition/animation
            properties: durations are --duration-*, curves are --ease-*.
            Keywords (`linear`, `both`) pass — a scroll-scrubbed animation's
            timing function is legitimately the keyword.

Custom-property DECLARATIONS (`--field-unit: 6rem`) are exempt from the
length gates: they are the pages' data channel — lattice cells, viewBox
widths, travel units — and check-class-provenance.py rule 5 already forces
inline style="" down to custom properties only. They are NOT exempt from the
colour gate, for the pipe reason above.

Every rule proves it can fail before it is trusted to pass: a built-in
self-test feeds each gate a minimal synthetic violation and dies if any gate
stays green. A checker that cannot catch a planted fault is documentation,
not enforcement — the spacing table drifted behind a stamp nobody ran, and
this suite's founding lesson is that the run is the check.

stdlib only, no build step, same python3 that serves the pages.

    python3 scripts/check-local-literals.py            # gate, exit 1 on drift
    python3 scripts/check-local-literals.py --verbose  # census of what it read
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PATTERNS = ROOT / "design-system" / "patterns"
CSS_DIR = ROOT / "design-system" / "assets" / "css"

# The stylesheets every pattern page may link without making them page-local:
# the three that ship with their own gates, and the two documentation chromes
# that never reach control-f.de. Anything ELSE a pattern page links is a page
# stylesheet and is read here with exactly the gates the in-page blocks get.
SHARED_SHEETS = frozenset(
    {"tokens.css", "base.css", "components.css", "docs.css", "preview.css"}
)
LINK = re.compile(r'<link[^>]+href="[^"]*?([\w.-]+\.css)"')

# ---------------------------------------------------------------------------
# Grammar. SPACING_PROP and LENGTH are check-spacing-scale.py's, verbatim, so
# "what counts as spacing" is one definition with two enforcement surfaces.
# ---------------------------------------------------------------------------

SPACING_PROP = re.compile(
    r"\b(?:margin|padding)(?:-(?:block|inline)(?:-(?:start|end))?|-(?:top|right|bottom|left))?"
    r"|\b(?:row-|column-)?gap\b"
)
LENGTH = re.compile(r"(?<![\w.-])(-?\d*\.?\d+)(px|rem)(?![\w-])")
FREE = {"0px", "0rem"}

HEX_COLOUR = re.compile(r"#[0-9a-fA-F]{3,8}\b")
FN_COLOUR = re.compile(
    r"(?<![-\w])(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch|color|color-mix)\(", re.I
)

# Properties whose value is (or leads with) a colour, for the named-colour
# rule. The broad gates above do not need this list — hex is hex anywhere.
COLOUR_PROP = re.compile(
    r"^(?:color|background(?:-color)?|border(?:-(?:top|right|bottom|left|block|inline))?(?:-color)?"
    r"|outline(?:-color)?|fill|stroke|text-decoration(?:-color)?|caret-color|accent-color"
    r"|column-rule(?:-color)?|text-emphasis(?:-color)?)$"
)
NAMED_COLOURS = frozenset(
    "aqua black blue brown coral crimson cyan fuchsia gold gray green grey indigo ivory "
    "khaki lavender lime magenta maroon navy olive orange orchid pink plum purple red "
    "salmon silver tan teal tomato turquoise violet wheat white yellow "
    "whitesmoke gainsboro lightgray lightgrey darkgray darkgrey dimgray dimgrey "
    "rebeccapurple aliceblue".split()
)

TYPE_TOKENS = {
    "font-size": "--text-*",
    "font-weight": "--weight-*",
    "letter-spacing": "--tracking-*",
}
RADIUS_PROP = re.compile(
    r"^border(?:-(?:top|bottom)-(?:left|right)|-(?:start|end)-(?:start|end))?-radius$"
)
MOTION_PROP = re.compile(
    r"^(?:transition|animation)(?:-duration|-delay)?$"
)
TIME_LITERAL = re.compile(r"(?<![\w.-])\d*\.?\d+m?s(?![\w-])")

# A declaration boundary: property after "{", ";" or "}", so a pseudo-class
# colon in a selector and a query prelude's "(max-width: …)" never read as
# declarations.
DECL = re.compile(r"(?<=[{;}])\s*((?:--)?[a-zA-Z][-\w]*)\s*:\s*([^;{}]+)")

STYLE_BLOCK = re.compile(r"<style[^>]*>(.*?)</style>", re.S)
STYLE_ATTR = re.compile(r'style="([^"]*)"')

# ---------------------------------------------------------------------------
# Justified literals, each with the reason it is not a token. Keep this list
# short: measured at introduction, the pattern pages needed no entry at all,
# and every future entry is a colour or scale decision made outside the
# system that has to argue for itself here. Keys are the page's or sheet's
# bare name and the declaration as written:
#     ("<file>.html" | "<sheet>.css", "<property>: <value>"): "<the reason>",
# A row whose declaration no longer exists is reported STALE and fails the
# run, so the list cannot outlive what it excuses.
# ---------------------------------------------------------------------------
ALLOWED = {
    ("acts.css", "animation: sp-stream var(--sp-period, 3s) linear infinite"):
        "the 3s is the fallback arm of a data pipe, not a clock decision: every "
        ".sp-stream consumer pipes its own --sp-period inline (21 of 21 today, "
        "2837–3935ms, distinct on purpose so the streams never phase-lock), and "
        "the fallback is the authored defence for a consumer that forgets — "
        "without it a missing pipe paints every label of the stream at once.",
    ("acts.css", "animation-delay: calc(var(--sp-period, 3s) * var(--sp-slot) / 6 * -1)"):
        "the same fallback arm, in the same pipe, one line down — the delay must "
        "default to the same period the duration defaults to or the six slots "
        "de-sync exactly when the fallback is live.",
    ("acts.css", "animation-delay: 0s, 0s, calc(var(--l) * -370ms)"):
        "a phase spread, not a duration: each leaf's shimmer starts -370ms times "
        "its own --l into an infinite alternate cycle so no two leaves glow in "
        "step. The clock tokens name how long a gesture takes; this names where "
        "in an endless one each element stands, per-element, off piped data. "
        "The 0s pair are list placeholders for the two scroll-driven members.",
    ("acts.css", "transition-delay: calc(var(--i) * 40ms)"):
        "the act rail's per-item stagger unit. The clock tokens name whole "
        "gestures — the label reveal itself takes --duration-base — and 40ms is "
        "the gap BETWEEN gestures, an off-scale figure by construction: the five "
        "rows (--i 0–4) top out at 160ms of spread, inside the gesture it staggers.",
    ("acts.css", "padding-inline: round(var(--gutter), 1px)"):
        "the 1px is round()'s precision arm, not a length: the gutter is 5.5vw "
        "snapped to the pixel grid so the stage's hairlines land on it (the "
        "max-width above it snaps to 2px for the same reason, with the note on "
        ".lp-proc-stage telling the story). The spacing decision is var(--gutter).",
}


def stripped(css):
    """CSS comments blanked in place so offsets and line numbers survive."""
    return re.sub(
        r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)), css, flags=re.S
    )


def check_declaration(name, prop, value, findings):
    """Run every gate over one declaration from a <style> block."""
    key = (name, "%s: %s" % (prop, value.strip()))
    if key in ALLOWED:
        return

    def hit(rule, why):
        findings.append((name, rule, "%s: %s" % (prop, value.strip()), why))

    if HEX_COLOUR.search(value) or FN_COLOUR.search(value):
        hit(
            "COLOUR",
            "a colour literal in page-local CSS. Colour comes from tokens.css; "
            "if no token is this colour, that is a finding about the palette, "
            "not a page-local decision.",
        )
    if not prop.startswith("--"):
        if COLOUR_PROP.match(prop):
            words = set(re.findall(r"[a-zA-Z-]+", value.lower()))
            named = sorted(words & NAMED_COLOURS)
            if named:
                hit(
                    "COLOUR",
                    "named colour%s %s in a colour-carrying property — same rule "
                    "as hex, friendlier spelling." % ("s" if len(named) > 1 else "", ", ".join(named)),
                )
        if SPACING_PROP.fullmatch(prop):
            if any(m.group(0) not in FREE for m in LENGTH.finditer(value)):
                hit(
                    "SPACING",
                    "a px/rem length in a spacing property. The scale is "
                    "var(--space-N); check-spacing-scale.py holds the shipping "
                    "stylesheets to this and this file holds the page-local blocks.",
                )
        if prop in TYPE_TOKENS:
            literal = LENGTH.search(value) or re.search(
                r"(?<![\w.-])\d*\.?\d+(?:em)?(?![\w%(-])", value
            )
            reset = (
                (prop == "font-weight" and value.strip() in ("normal", "inherit"))
                or (prop == "letter-spacing" and value.strip() in ("0", "normal"))
            )
            if literal and not reset and "var(" not in value:
                hit(
                    "TYPE",
                    "a literal where the type scale has a name: %s." % TYPE_TOKENS[prop],
                )
        if RADIUS_PROP.match(prop):
            if value.strip() not in ("0", "inherit") and "var(" not in value:
                hit(
                    "RADIUS",
                    "a radius past the vocabulary. --radius-none, --radius-sm and "
                    "--radius-full are the whole set, on purpose — tokens.css tells "
                    "the story of the pill that was deleted.",
                )
        if prop == "box-shadow":
            if value.strip() != "none" and "var(" not in value:
                hit(
                    "SHADOW",
                    "a hand-rolled elevation. The system ships --shadow-sm/md/lg; "
                    "a focus ring composes from --stroke-* and a token colour.",
                )
        if MOTION_PROP.match(prop):
            if TIME_LITERAL.search(value):
                hit(
                    "MOTION",
                    "a duration literal. The system's clock is --duration-fast/"
                    "base/slow/scene.",
                )
            if "cubic-bezier(" in value:
                hit(
                    "MOTION",
                    "a hand-typed curve. The system's easing is --ease-*.",
                )


def page_sheets():
    """{sheet name: [pattern pages that link it]} for every non-shared sheet.

    Discovery is by <link>, not by a list kept here: the sheet this scope was
    widened for arrived without any checker noticing, and a name typed into
    this file would just be the next copy of that mistake.
    """
    sheets = {}
    for path in sorted(PATTERNS.glob("*.html")):
        for m in LINK.finditer(path.read_text()):
            name = m.group(1)
            if name not in SHARED_SHEETS:
                sheets.setdefault(name, []).append(path.name)
    return sheets


def check_sheet(name, css):
    """All findings for one page stylesheet, plus its declaration count."""
    findings = []
    n_decls = 0
    for m in DECL.finditer("{" + stripped(css)):
        n_decls += 1
        check_declaration(name, m.group(1).strip(), m.group(2), findings)
    return findings, n_decls


def check_page(name, html):
    """All findings for one page, plus its census row."""
    findings = []
    n_decls = n_attrs = n_blocks = 0
    for block in STYLE_BLOCK.finditer(html):
        n_blocks += 1
        css = stripped(block.group(1))
        # Prefix so the first declaration after <style> has a boundary too.
        for m in DECL.finditer("{" + css):
            n_decls += 1
            check_declaration(name, m.group(1).strip(), m.group(2), findings)
    plain = stripped(re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.S))
    for m in STYLE_ATTR.finditer(plain):
        n_attrs += 1
        value = m.group(1)
        if HEX_COLOUR.search(value) or FN_COLOUR.search(value):
            findings.append(
                (
                    name,
                    "COLOUR",
                    'style="%s"' % (value if len(value) <= 60 else value[:57] + "…"),
                    "a colour literal in inline style data. A custom property is a "
                    "value pipe; a colour poured in here is painted somewhere below, "
                    "outside every gate. Pipe a token.",
                )
            )
    return findings, (n_blocks, n_decls, n_attrs)


def selftest():
    """Every gate catches a planted fault, or the checker itself is the fault."""
    planted = {
        "COLOUR": (
            '<style>a { color: #E1FF00; }</style>',
            '<style>a { background: white; }</style>',
            '<div style="--glow: rgb(225, 255, 0)"></div>',
        ),
        "SPACING": ('<style>a { margin-block: 24px; }</style>',),
        "TYPE": ('<style>a { font-size: 1.25rem; }</style>',),
        "RADIUS": ('<style>a { border-radius: 12px; }</style>',),
        "SHADOW": ('<style>a { box-shadow: 0 8px 24px #00000019; }</style>',),
        "MOTION": ('<style>a { transition: opacity 240ms cubic-bezier(.2,0,0,1); }</style>',),
    }
    clean = (
        "<style>a:hover { margin: var(--space-4); box-shadow: var(--shadow-sm); "
        "animation: pane linear both; } "
        "@media (max-width: 28rem) { b { --field-unit: 6rem; height: 1.75rem; } }</style>"
        '<div style="--o: 100% 0; --sp-period: 3935ms"></div>'
    )
    for rule, cases in planted.items():
        for case in cases:
            found, _ = check_page("selftest", case)
            if not any(f[1] == rule for f in found):
                sys.exit(
                    "check-local-literals.py: SELF-TEST FAILED — the %s gate did not "
                    "fire on %r. The gate is broken, not the pages; fix the gate."
                    % (rule, case)
                )
    found, _ = check_page("selftest", clean)
    if found:
        sys.exit(
            "check-local-literals.py: SELF-TEST FAILED — a gate fired on the clean "
            "fixture: %r. The gate over-reaches; fix the gate." % (found,)
        )
    # The sheet path runs the same gates over raw CSS — prove it catches a
    # planted fault too, or widening the scope widened nothing.
    found, _ = check_sheet("selftest.css", "a { color: #E1FF00; margin: 24px; }")
    if not any(f[1] == "COLOUR" for f in found) or not any(f[1] == "SPACING" for f in found):
        sys.exit(
            "check-local-literals.py: SELF-TEST FAILED — the sheet path did not "
            "fire on a planted colour and spacing literal. The gate is broken, "
            "not the sheets; fix the gate."
        )
    found, _ = check_sheet("selftest.css", "a { margin: var(--space-4); color: var(--cf-lime); }")
    if found:
        sys.exit(
            "check-local-literals.py: SELF-TEST FAILED — a gate fired on the clean "
            "sheet fixture: %r. The gate over-reaches; fix the gate." % (found,)
        )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true", help="print the census")
    args = ap.parse_args()

    selftest()

    findings, census = [], []
    for path in sorted(PATTERNS.glob("*.html")):
        page_findings, counts = check_page(path.name, path.read_text())
        findings.extend(page_findings)
        census.append((path.name,) + counts)

    sheets = page_sheets()
    sheet_census = []
    for name, pages in sorted(sheets.items()):
        sheet_findings, n_decls = check_sheet(name, (CSS_DIR / name).read_text())
        findings.extend(sheet_findings)
        sheet_census.append((name, pages, n_decls))

    # An ALLOWED row with no declaration behind it describes an exception the
    # system no longer takes — the same staleness rule the threshold register
    # enforces on its own rows.
    if ALLOWED:
        live = set()
        for path in sorted(PATTERNS.glob("*.html")):
            html = path.read_text()
            for block in STYLE_BLOCK.finditer(html):
                for m in DECL.finditer("{" + stripped(block.group(1))):
                    live.add((path.name, "%s: %s" % (m.group(1).strip(), m.group(2).strip())))
        for name in sheets:
            for m in DECL.finditer("{" + stripped((CSS_DIR / name).read_text())):
                live.add((name, "%s: %s" % (m.group(1).strip(), m.group(2).strip())))
        for row in sorted(set(ALLOWED) - live):
            findings.append(
                (row[0], "STALE", row[1], "an ALLOWED row with no declaration behind it. Delete it.")
            )

    if args.verbose:
        print("page-local literal census — patterns/\n")
        for name, blocks, decls, attrs in census:
            print("  %-24s %d <style> block(s), %3d declaration(s), %3d style attr(s)"
                  % (name, blocks, decls, attrs))
        for name, pages, decls in sheet_census:
            print("  %-24s page stylesheet, %4d declaration(s), linked by %s"
                  % (name, decls, ", ".join(pages)))
        print()

    if findings:
        print("local literals: %d finding(s)\n" % len(findings))
        for name, rule, decl, why in findings:
            where = "patterns/" + name if name.endswith(".html") else "assets/css/" + name
            print("  - %s [%s]\n        %s\n    %s\n" % (where, rule, decl, why))
        return 1

    n_blocks = sum(c[1] for c in census)
    n_decls = sum(c[2] for c in census)
    n_attrs = sum(c[3] for c in census)
    n_sheet_decls = sum(c[2] for c in sheet_census)
    print(
        "local literals: %d pages, %d page-local <style> blocks (%d declarations), "
        "%d style attributes, %d page stylesheet(s) (%d declarations) — no colour, "
        "spacing, type, radius, shadow or motion literal outside the token set; "
        "%d justified exception(s)."
        % (len(census), n_blocks, n_decls, n_attrs, len(sheet_census), n_sheet_decls,
           len(ALLOWED))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
