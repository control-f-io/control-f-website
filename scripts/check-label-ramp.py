#!/usr/bin/env python3
"""Hold the mono label ramp.

base.css calls .t-label "the single most recognisable text style in the brand"
and tokens.css writes the size into the token itself:

    --text-xs: 0.6875rem; /* 11 - mono labels only, never prose */

Mono AND uppercase is that style's signature. It is on the section header's
label and its counter, the nav, every eyebrow, every meta line, every counter
on every card - and every one of them is 11 px, because a label ramp with two
sizes in it is not a ramp. The system has exactly one deliberate step above
it, and it is a named class: .t-label-lg at --text-sm, which .cf-btn and
.cf-prose h4 also take.

WHAT THIS CHECK IS FOR. The failure it caught is not a wrong-looking rule. It
is a rule that copies four of .t-label's five declarations by hand and gets the
fifth wrong, which is what a hand-restated utility does eventually. On the
landing page's partner wall that produced mono uppercase at --text-lg: the one
run of it in the system above 13 px, on a GHOSTED placeholder, 45 % larger than
the <h2> standing on the hairline directly above it. Nothing about it read as
broken in isolation. It read as broken beside the heading it dwarfed, and no
existing check looks at type size at all.

THE RAMP, and it is short on purpose. It has two rungs, and EACH RUNG IS A
PAIR - a size and the tracking that travels with it:

    --text-xs + --tracking-label    the label. .t-label.
    --text-sm + --tracking-wide     the named larger form: .t-label-lg, and the
                                    two components that take that form,
                                    .cf-btn and .cf-prose h4.

The lengths behind those four names are read out of tokens.css at run time and
printed in the messages below rather than typed here, because this docstring
had them wrong: it said --text-sm was 0.875rem / 14 when the token has been
0.75rem / 12, and the failure message a developer actually reads said the same.
A check whose own statement of the rule drifts is the thing it exists to stop.

A rule that sets font-family to the mono stack and text-transform: uppercase,
and sets a font-size that is neither rung, is a finding until the size becomes
one of the two or the rule is added to EXEMPT below with a reason.

TRACKING IS THE SECOND HALF AND WAS UNHELD FOR AS LONG AS THE FIRST WAS HELD.
One step of size is 1 px; two mono labels a pixel apart are told apart by their
tracking long before they are told apart by their size, so a rule wearing one
rung's size and the other's tracking reads as neither. Three were, in both
directions, and each is the same hand-restated utility this check was written
about - four of five declarations copied and the fifth taken from the wrong
rung:

    .cf-prose h4          --text-sm with --tracking-label. Named in this very
                          docstring as a .t-label-lg, and set 0.84 px narrower
                          per character than the buttons beside it.
    .cf-consent__title    --text-xs with --tracking-wide. The only 11 px mono
                          label in the shipping tree not on --tracking-label,
                          and it is the first type a first-time reader meets.
    .icon-toggle          --text-xs with --tracking-wide, in the <style> block
    (iconography.html)    on foundations/iconography.html - a docs control
                          dressed as a small button, which is how it got there.

So a rule on a rung takes that rung's tracking, or states no tracking at all
and inherits one. A rule that states a tracking off its own rung is a finding.

SCOPE is every stylesheet that ships plus every <style> block on a page in
design-system/ - wider than check-spacing-scale.py's, because this is exactly
the boundary the defect crossed. A page's own <style> block is where a utility
gets restated by hand; a check that stopped at the shipping stylesheets would
have looked straight past two of the three rules above. docs.css is
documentation chrome and is out, the same call every check here makes.

AND ACTS.CSS SHIPS. It was not in this check's SHIPPING tuple, which named
three files where the site has four: acts.css is the scroll composition on
eight pages and it carries two mono uppercase rules this check had never read.
Both are on the ramp, and that is luck rather than enforcement - the same reach
gap check-gradient-family.py was widened for, in the same file, for the same
reason. A gate whose reach stops moving has a half-life.

Sizes and trackings are compared as tokens, not as computed lengths.
`var(--text-xs)` and `var(--text-xs, .6875rem)` are the same decision; a bare
`0.6875rem` is not, because the point of the ramp is that the value is named.

stdlib only, no build step, no dependency - the same contract as the
twenty-two checks beside it.

    python3 scripts/check-label-ramp.py       # check, exit 1 on a finding
    python3 scripts/check-label-ramp.py -v    # print every rule on the ramp
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system" / "assets" / "css"
DESIGN_SYSTEM = ROOT / "design-system"

SHIPPING = ("tokens.css", "base.css", "components.css", "acts.css")

# The ramp. Two rungs, each a size and the tracking that travels with it. A
# mono uppercase rule sets one of these sizes or it is a finding; if it also
# states a tracking, the tracking is the one its rung carries.
RAMP = {
    "--text-xs": "--tracking-label",
    "--text-sm": "--tracking-wide",
}

# Rules that are mono and uppercase and off the ramp, each with the reason.
# Keep this list short: every entry is a place the ramp does not reach, and a
# long list would mean the ramp is wrong rather than that the exceptions are.
EXEMPT = {
    # Type inside an SVG, not type on the page. The plan is drawn in a
    # viewBox and scales with it, so its 13 px is a coordinate in the
    # drawing's own space - the ramp governs px that land on the document.
    ("foundations/sight.html", ".sight-plan text"),
}

MONO = re.compile(r"font-family:[^;]*--font-mono")
UPPER = re.compile(r"text-transform:\s*uppercase")
SIZE = re.compile(r"font-size:\s*([^;}]+)")
TRACK = re.compile(r"letter-spacing:\s*([^;}]+)")
TOKEN = re.compile(r"var\(\s*(--[\w-]+)")
DECL = re.compile(r"(--[\w-]+):\s*([^;}]+)")


def blank_comments(text):
    """Blank /* ... */ keeping BOTH the length and the newlines.

    ` ` * len(match) keeps the length, which is what offsets need, and eats
    every newline inside the comment, which is what line numbers need. In a
    stylesheet that is mostly prose the second loss is total: this file
    reported .cf-prose h4 at components.css:2239 when it is at 6306, because
    4,067 lines of comment above it had been flattened. A finding that points
    at the wrong rule is worse than no line number at all, and it points there
    confidently.
    """
    return re.sub(r"/\*.*?\*/",
                  lambda m: re.sub(r"[^\n]", " ", m.group(0)), text, flags=re.S)


def token_lengths():
    """The four ramp values as tokens.css declares them, for the messages.

    Typed into this file they went stale and said 14 px where the token says
    12; read from the source they cannot. A token the file no longer declares
    prints as its own name, which is a legible failure rather than a wrong
    number.
    """
    text = (CSS / "tokens.css").read_text(encoding="utf-8")
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    seen = dict(DECL.findall(text))
    return {name: " ".join(seen[name].split()) if name in seen else name
            for rung in RAMP.items() for name in rung}


def gloss(name, lengths):
    """`--text-sm (0.75rem)` - the token and what it currently resolves to."""
    return "%s (%s)" % (name, lengths.get(name, name))


def blocks(text):
    """Every `selector { ... }` pair, comments blanked, line numbers kept.

    A brace walker and not a parser, the same shape as the other checks: at-
    rules nest, so a block whose body still contains a brace is passed over
    and its inner blocks are found on their own.
    """
    text = blank_comments(text)
    for m in re.finditer(r"\{([^{}]*)\}", text):
        body = m.group(1)
        head = text[:m.start()]
        selector = re.split(r"[{}]", head)[-1]
        selector = selector.rsplit(";", 1)[-1].strip()
        selector = " ".join(selector.split())
        yield selector, body, head.count("\n") + 1


def sources():
    """(label, text) for every file whose rules this check governs."""
    for name in SHIPPING:
        yield name, (CSS / name).read_text(encoding="utf-8")
    for page in sorted(DESIGN_SYSTEM.rglob("*.html")):
        text = page.read_text(encoding="utf-8")
        label = str(page.relative_to(DESIGN_SYSTEM))
        for m in re.finditer(r"<style[^>]*>(.*?)</style>", text, flags=re.S):
            # Keep the offset so reported line numbers are the page's own.
            lead = text[:m.start(1)].count("\n")
            yield label, "\n" * lead + m.group(1)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print every mono uppercase rule, its size and its "
                         "tracking")
    args = ap.parse_args()

    lengths = token_lengths()
    ramp_gloss = " and ".join(
        "%s + %s (%s)" % (gloss(size, lengths), track, lengths.get(track, track))
        for size, track in RAMP.items())

    on_ramp, findings, mistracked, exempt_seen = [], [], [], set()

    for label, text in sources():
        for selector, body, line in blocks(text):
            if not (MONO.search(body) and UPPER.search(body)):
                continue
            m = SIZE.search(body)
            size = m.group(1).strip() if m else None
            if size is None:
                # No size of its own: it inherits one, and inheriting is not a
                # decision this check can read. .t-numeric and the colour-only
                # utilities land here.
                continue
            token = TOKEN.search(size)
            named = token.group(1) if token else None
            t = TRACK.search(body)
            track = t.group(1).strip() if t else None
            t_token = TOKEN.search(track) if track else None
            t_named = t_token.group(1) if t_token else None
            entry = (label, selector, size, track, line)
            if (label, selector) in EXEMPT:
                exempt_seen.add((label, selector))
                on_ramp.append(entry)
            elif named in RAMP:
                on_ramp.append(entry)
                # A rule may say nothing about tracking and inherit one. If it
                # says something, it says its own rung's.
                if track is not None and t_named != RAMP[named]:
                    mistracked.append(entry)
            else:
                findings.append(entry)

    if args.verbose:
        for label, selector, size, track, line in sorted(on_ramp):
            print("  %-28s %-34s %-20s %s"
                  % (label, selector[:34], size, track or "inherited"))
        print("  %d rules on the ramp" % len(on_ramp))

    stale = EXEMPT - exempt_seen
    for label, selector in sorted(stale):
        print("check-label-ramp: %s %s is exempted and no longer exists. "
              "Drop the entry." % (label, selector), file=sys.stderr)

    for label, selector, size, track, line in findings:
        print("check-label-ramp: %s:%d  %s sets mono + uppercase at %s.\n"
              "    The label ramp is %s. Take one of the two, use the class "
              "rather than restating it, or add the rule to EXEMPT in this "
              "file with a reason."
              % (label, line, selector, size, ramp_gloss), file=sys.stderr)

    for label, selector, size, track, line in mistracked:
        named = TOKEN.search(size).group(1)
        print("check-label-ramp: %s:%d  %s is on the %s rung and sets "
              "letter-spacing: %s.\n"
              "    Each rung is a size AND the tracking that travels with it, "
              "because one step of size is 1 px and the tracking is what tells "
              "the two rungs apart. %s takes %s. Take it, take the class that "
              "already pairs them, or state no tracking and inherit one."
              % (label, line, selector, named, track,
                 gloss(named, lengths), gloss(RAMP[named], lengths)),
              file=sys.stderr)

    if findings or mistracked or stale:
        return 1
    print("check-label-ramp: %d mono uppercase rules, all on the ramp and on "
          "their rung's tracking (%d exempt)."
          % (len(on_ramp), len(exempt_seen)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
