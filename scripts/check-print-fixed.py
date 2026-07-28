#!/usr/bin/env python3
"""A layer that floats over the screen must not float over the paper.

`position: fixed` means one thing on a screen and a different thing on paper.
On screen it pins a box to the viewport: one box, over whatever is scrolled
under it. In paged media the viewport IS the page box, so the same declaration
pins the box to EVERY page — the browser repeats it on sheet after sheet, over
whatever the flow had put there. CSS 2.1 §9.6.1 says so in as many words
("fixed boxes are repeated on every page"), and it is the behaviour Chromium,
Firefox and Safari all ship.

WHAT IT COST HERE. .cf-consent is `position: fixed; inset: auto 0 0 0` on
`--surface-inverse` — an opaque black plate the full width of the viewport,
144 px tall at a desktop width and 333 px at 375. Nothing scoped it to screen.
landing-page.html printed to A4 through Chromium on a first visit, before the
fix:

    pages                              9
    plate, in layout units             794 x 253, filled `0 0 0`
    MediaBox                           595.92 x 842.88 pt
    scale (595.92 / 794)               0.7505
    plate on the sheet                 189.9 pt of 842.88  =  22.5 %
    pages carrying it                  9 of 9
    identical trailing operators       4,540 bytes on pages 2-9

Twenty-two and a half per cent of every sheet, painted last, opaque, over the
content. On page four it took "Ihr Vorteil" and the benefit line under it off
the middle of a process card. And the plate is a QUESTION: three buttons that
cannot be pressed, reprinted nine times, asking about cookies on paper.

This is invisible in every screenshot the repository takes, because every
screenshot is `screen`. It is countable in a file, which is what this is.

THE RULE. In the three shipping stylesheets, a declaration of
`position: fixed` must be reachable only where a fixed box is a fixed box.
A rule satisfies that in one of two ways:

  scoped      the declaration sits inside an at-rule prelude that names
              `screen`, so print never reads it at all. This is the same
              screen-scoping check-iso-motion.py already holds the scroll
              timelines to, and it is the better of the two answers because
              the box then does not exist on paper rather than being drawn
              and hidden.

  withdrawn   an `@media print` block sets `display: none` on the same key —
              the rightmost class, id or element of the selector that
              declared the fix. The layer is drawn for the screen and taken
              away for the sheet.

The key, not the whole selector, because the two rules are written for
different jobs and never match character for character: `.cf-consent` declares
the fix on its own, and the print rule that withdraws it is written beside
`.cf-consent__dialog`. Matching on the key is what lets the withdrawal be a
grouped rule, which is how this file already writes them.

THE UA STYLESHEET IS PART OF THE SCOPE, in one place. A modal `<dialog>` and
its `::backdrop` are `position: fixed` with nothing in the author sheet saying
so, so nothing here could see them. `dialog` is therefore treated as a key that
must also be withdrawn — the one entry that is not read out of a declaration.

WHAT IS NOT IN SCOPE. docs.css and preview.css: neither ships. preview.css's
`.ds-back` is the clearest case for the exclusion rather than against it — it
is `position: fixed`, it does drift over the print, and foundations/mobile.html
already says in prose that it is excluded because it is not part of the page.
Per-page <style> blocks are one page's business, and prototypes/ is unshipped
on purpose. Same boundary check-overflow-clip.py and check-grid-tracks.py draw.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-print-fixed.py       # check, exit 1 on a finding
    python3 scripts/check-print-fixed.py -v    # list every fixed layer and its answer
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system" / "assets" / "css"

SHIPPING = ("tokens.css", "base.css", "components.css")

COMMENT = re.compile(r"/\*.*?\*/", re.S)
FIXED = re.compile(r"(?<![\w-])position\s*:\s*fixed(?![\w-])", re.I)
DISPLAY_NONE = re.compile(r"(?<![\w-])display\s*:\s*none(?![\w-])", re.I)

# The rightmost simple selector of a compound: `.cf-consent__dialog` out of
# `.cf-consent .cf-consent__dialog:not([open])`, `dialog` out of `dialog::backdrop`.
KEY = re.compile(r"(\.[-\w]+|#[-\w]+|^[a-z][-\w]*|(?<=[\s>+~])[a-z][-\w]*)")

# The one key no author declaration can name: a modal <dialog> is fixed by the
# UA stylesheet. See the block header.
UA_FIXED = ("dialog",)


def blank(match):
    """Blank a comment in place, newlines kept, so line numbers survive."""
    return re.sub(r"[^\n]", " ", match.group(0))


def key_of(selector):
    """The key a print rule has to name to withdraw this selector.

    Pseudo-elements and pseudo-classes are cut first: `dialog::backdrop` and
    `.cf-consent[hidden]` are the same layer as `dialog` and `.cf-consent`, and
    a withdrawal written on the bare element covers both.
    """
    part = re.split(r"[,]", selector)[0].strip()
    part = re.sub(r"::?[-\w]+(\([^)]*\))?", "", part)      # pseudos
    part = re.sub(r"\[[^\]]*\]", "", part)                  # attribute tests
    part = part.strip()
    if not part:
        return None
    last = re.split(r"[\s>+~]+", part)[-1]
    found = re.findall(r"[.#]?[-\w]+", last)
    return found[-1] if found else None


def rules(text):
    """(line, prelude-stack, selector, body) for every declaration block.

    The prelude stack is every at-rule prelude the block sits inside, outermost
    first, so a `position: fixed` written under `@media screen` can be told
    from one written at the top level. Declaration blocks do not nest, so the
    innermost brace pair is always a real rule; everything above it is an
    at-rule and goes on the stack.
    """
    text = COMMENT.sub(blank, text)
    stack, out, i, n = [], [], 0, len(text)
    depth_preludes = []
    buf_start = 0
    while i < n:
        c = text[i]
        if c == "{":
            head = text[buf_start:i].strip()
            # An at-rule that contains other rules, or a plain rule?
            j, d = i + 1, 1
            while j < n and d:
                d += (text[j] == "{") - (text[j] == "}")
                j += 1
            body = text[i + 1:j - 1]
            if head.startswith("@") and "{" in body:
                depth_preludes.append((j, head))
                stack.append(head)
                buf_start = i + 1
                i += 1
                continue
            if not head.startswith("@"):
                out.append((text.count("\n", 0, i) + 1, tuple(stack),
                            " ".join(head.split()), body))
            i = j
            buf_start = i
            continue
        if c == "}":
            while depth_preludes and depth_preludes[-1][0] == i + 1:
                depth_preludes.pop()
                stack.pop()
            i += 1
            buf_start = i
            continue
        i += 1
    return out


def scoped_to_screen(preludes):
    """True when no print formatting context can reach this block."""
    for p in preludes:
        if re.search(r"(?<![\w-])screen(?![\w-])", p, re.I):
            return True
    return False


def is_print(preludes):
    """True when a print formatting context can reach this block via @media print."""
    for p in preludes:
        if not p.lower().startswith("@media"):
            continue
        for query in p[len("@media"):].split(","):
            q = query.strip()
            if re.match(r"print(?![\w-])", q, re.I) and " and " not in q.lower():
                return True
    return False


def audit():
    fixed, withdrawn, findings = [], set(), []
    for name in SHIPPING:
        path = CSS / name
        if not path.exists():
            findings.append((name, 0, "", "stylesheet is missing"))
            continue
        for line, preludes, selector, body in rules(path.read_text(encoding="utf-8")):
            if is_print(preludes) and DISPLAY_NONE.search(body):
                for part in selector.split(","):
                    k = key_of(part)
                    if k:
                        withdrawn.add(k)
            if not FIXED.search(body):
                continue
            for part in selector.split(","):
                k = key_of(part)
                if k:
                    fixed.append((name, line, part.strip(), k,
                                  scoped_to_screen(preludes)))

    for k in UA_FIXED:
        fixed.append(("(ua stylesheet)", 0, k, k, False))

    seen = []
    for name, line, selector, k, screen_only in fixed:
        if screen_only:
            seen.append((name, line, selector, k, "scoped to screen"))
        elif k in withdrawn:
            seen.append((name, line, selector, k, "withdrawn in @media print"))
        else:
            seen.append((name, line, selector, k, "PRINTS ON EVERY PAGE"))
            findings.append((name, line, selector,
                             "`position: fixed` with nothing scoping it to screen and no "
                             "`@media print` rule setting `display: none` on `%s` — in "
                             "paged media this box is repeated on every sheet, over the "
                             "content" % k))
    return findings, seen


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every fixed layer and the answer it carries")
    args = ap.parse_args()

    findings, seen = audit()

    if args.verbose:
        for name, line, selector, k, note in seen:
            print("  %-16s %5d  %-40s %-24s %s"
                  % (name, line, selector[:40], k, note))
        print()

    if findings:
        for name, line, selector, why in findings:
            print("%s:%d  %s\n    %s" % (name, line, selector or "(file)", why),
                  file=sys.stderr)
        print("\n%d fixed layer%s that paper repeats on every page. Scope the rule to "
              "`screen`, or withdraw the layer in an `@media print` block."
              % (len(findings), "" if len(findings) == 1 else "s"), file=sys.stderr)
        return 1

    scoped = sum(1 for *_, note in seen if note == "scoped to screen")
    gone = sum(1 for *_, note in seen if note.startswith("withdrawn"))
    print("print: %d fixed layer%s, %d scoped to screen, %d withdrawn for print."
          % (len(seen), "" if len(seen) == 1 else "s", scoped, gone))
    return 0


if __name__ == "__main__":
    sys.exit(main())
