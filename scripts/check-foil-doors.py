#!/usr/bin/env python3
"""Every clipping context hands its ink back at all three doors.

A clipping context is a rule that paints a gradient into letterforms —
`background-clip: text` with the fill set transparent, so the glyphs are
windows onto the ramp behind them. There are two in the shipping CSS:
`.text-foil` in base.css and `.cf-btn--solid` in components.css. Both make
the same promise in prose: outside the enhanced block the type is solid and
legible, and wherever the ramp cannot or should not be drawn the element is
handed a real colour back.

THE DOORS ARE THREE, and until this check existed the third one did not exist
either. Print cannot carry a background image and forced colours has a palette
of its own, and both clipping contexts opened for those. Neither is the reader
asking. `prefers-contrast: more` is — and not one rule in the four shipping
stylesheets read that query, so a reader who had asked for more contrast was
handed the foil at its floor: 5.24:1 for the ink half on CF-Grau, 11.9:1 for
the lit half on Schwarz. Both clear AA. Neither is what was asked for, and the
reduced-transparency block at the foot of tokens.css already states the rule
for that: a request is answered in full or not at all.

What makes this a gate rather than a note is that the failure is silent in the
one place it would show. A third clipping context added later — a foil label
on a chip, a gradient counter — renders perfectly at every default setting, in
every screenshot, and only a reader with the preference set ever sees the
ramp where they asked for ink. Nobody takes that screenshot.

WHAT IS CHECKED, off the four shipping stylesheets with comments stripped and
every at-rule prelude tracked by brace depth, so a door nested two levels down
(`@supports { @media { … } }`) is found where it is:

  CONTEXTS   every selector in a rule that clips a background to `text`, with
             its pseudo-classes taken off, so `.cf-btn--solid:hover` and
             `.cf-btn--solid` are one context.

  DOORS      for every context, a rule inside each of `@media print`,
             `@media (forced-colors: active)` and `@media (prefers-contrast:
             more)` whose selector list names that context and whose body
             (a) takes the image away — `background: none` or
                 `background-image: none` — and
             (b) hands the ink back as BOTH `color` and
                 `-webkit-text-fill-color`, neither transparent, and equal to
                 each other. The fill is the one that draws under a clip and
                 the colour is what a browser without the prefixed property
                 reads; check-highlight-fill.py holds every highlight to the
                 same pair for the same reason.

  STATES     a context that clips in more than one state — the solid button
             restates its layer list on :hover and :focus-visible because the
             shorthand above it resets every longhand — has to be handed back
             in every one of those states at every door, or the door is open
             for the resting button and shut the moment a pointer touches it.

WHAT IT DOES NOT CLAIM. Which ink: `var(--cf-schwarz)` on paper, `CanvasText`
or `ButtonText` under forced colours and `var(--text-primary)` for more
contrast are three different right answers, and the check asks only that one
is given. Nor the at-rule's exact spelling beyond the feature — `screen and
(prefers-contrast: more)` would pass — because the reader's setting is the
invariant, not the prelude.

stdlib only, no build step.

    python3 scripts/check-foil-doors.py       # check, exit 1 on a shut door
    python3 scripts/check-foil-doors.py -v    # every context, every state, every door
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"

# The stylesheets that ship — the same four every other CSS gate reads.
CSS = ("tokens.css", "base.css", "components.css", "acts.css")

COMMENT = re.compile(r"/\*.*?\*/", re.S)
PSEUDO = re.compile(r"::?[a-zA-Z-]+(?:\([^)]*\))?")
FILL = "-webkit-text-fill-color"

# A door is recognised by the feature it answers, not by the prelude's exact
# text. Each is matched against the whole stack of enclosing preludes.
DOORS = (
    ("print",          re.compile(r"@media\b[^{]*\bprint\b")),
    ("forced-colors",  re.compile(r"forced-colors\s*:\s*active")),
    ("more-contrast",  re.compile(r"prefers-contrast\s*:\s*more")),
)


def strip_comments(text):
    """Blank comments and keep the newlines, so an offset still names a line."""
    return COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def declarations(body):
    """{property: value}, last wins, as CSS does."""
    out = {}
    for decl in body.split(";"):
        if ":" not in decl:
            continue
        prop, _, value = decl.partition(":")
        out[prop.strip().lower()] = value.strip()
    return out


def rules(src):
    """Yield (line, stack, selector, declarations) for every rule, at any depth.

    Walks the braces once. A prelude beginning with `@` is pushed as a block
    and popped at its closing brace; anything else is a rule whose body runs
    to the next brace of either kind. That is exact for these files, where a
    rule body never contains a block."""
    stack = []
    i, n, start = 0, len(src), 0
    while i < n:
        c = src[i]
        if c == "{":
            prelude = " ".join(src[start:i].split())
            if prelude.startswith("@"):
                stack.append(prelude)
                start = i + 1
                i += 1
                continue
            end = src.find("}", i)
            if end < 0:
                break
            # The line of the selector's first character, not of the previous
            # rule's closing brace: a blanked comment between the two keeps
            # its newlines, and counting from the brace would name the top of
            # that comment.
            head = src[start:i]
            line = src.count("\n", 0, start + len(head) - len(head.lstrip())) + 1
            yield line, tuple(stack), prelude, declarations(src[i + 1:end])
            i = end + 1
            start = i
            continue
        if c == "}":
            if stack:
                stack.pop()
            i += 1
            start = i
            continue
        if c == ";":
            start = i + 1
        i += 1


def contexts_of(selector):
    """The clipping contexts a selector list names: each compound, pseudo-free."""
    out = []
    for part in selector.split(","):
        base = PSEUDO.sub("", part).strip()
        if base:
            out.append((base, part.strip()))
    return out


def is_ink(value):
    return value is not None and value.lower() not in ("transparent", "")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print every context, state and door, not only the shut ones")
    args = ap.parse_args()

    # context -> {state selector -> (file, line)} for every rule that clips.
    contexts = {}
    # (context, door) -> {state selector -> (file, line)} for every rule that
    # hands ink back inside that door.
    handed = {}

    for name in CSS:
        src = strip_comments((DS / "assets" / "css" / name).read_text(encoding="utf-8"))
        for line, stack, selector, decls in rules(src):
            if selector.startswith("@"):
                continue
            clip = (decls.get("background-clip") or decls.get("-webkit-background-clip") or "")
            if "text" in clip.lower().split(","):
                for base, state in contexts_of(selector):
                    contexts.setdefault(base, {})[state] = (name, line)
            # A door rule: image off, ink back as both colour and fill.
            image_off = (decls.get("background", "").lower() == "none"
                         or decls.get("background-image", "").lower() == "none")
            colour, fill = decls.get("color"), decls.get(FILL)
            if not (image_off and is_ink(colour) and is_ink(fill)):
                continue
            same = " ".join(colour.split()).lower() == " ".join(fill.split()).lower()
            for door, feature in DOORS:
                if any(feature.search(p) for p in stack):
                    for base, state in contexts_of(selector):
                        handed.setdefault((base, door), {})[state] = (name, line, same)

    if not contexts:
        print("foil doors: no clipping context found in the shipping CSS. "
              "base.css's .text-foil and components.css's .cf-btn--solid both "
              "clip a background to text; if neither does any more, retire this "
              "check rather than letting it pass on nothing.")
        return 1

    failures = []
    for base, states in sorted(contexts.items()):
        for door, _ in DOORS:
            given = handed.get((base, door), {})
            for state, (name, line) in sorted(states.items()):
                hit = given.get(state)
                if hit is None:
                    failures.append(
                        "%s:%d  %s clips to text and nothing inside "
                        "%s hands it back. Take the image away and restate the "
                        "ink as color AND %s, in that state."
                        % (name, line, state, door, FILL))
                elif not hit[2]:
                    failures.append(
                        "%s:%d  %s inside %s sets color and %s to different "
                        "values; the two are the same ink stated twice and "
                        "must agree." % (hit[0], hit[1], state, door, FILL))
                if args.verbose:
                    status = "ok  " if hit and hit[2] else "SHUT"
                    where = "%s:%d" % (hit[0], hit[1]) if hit else "-"
                    print("%s %-16s %-36s %-14s %s" % (status, base, state, door, where))

    if failures:
        print("\n%d door%s shut on a clipping context:\n"
              % (len(failures), "" if len(failures) == 1 else "s"), file=sys.stderr)
        for f in failures:
            print("  " + f, file=sys.stderr)
        print("\nA gradient in the letters is a solid colour everywhere the ramp "
              "cannot or should not be drawn: paper, forced colours, and a reader "
              "who asked for more contrast. See base.css, FOIL TYPE, and "
              "foundations/colors.html, 'What it falls back to'.", file=sys.stderr)
        return 1

    states = sum(len(s) for s in contexts.values())
    print("foil doors: %d clipping contexts in %d states, every one handed its "
          "ink back at all %d doors." % (len(contexts), states, len(DOORS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
