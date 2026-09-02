#!/usr/bin/env python3
"""No shipping script may restate a layout gate as a viewport threshold.

WHY THIS EXISTS, WHICH IS A BUG IT WOULD HAVE CAUGHT

assets/js/cf-stream.js decided whether a track was pinned — and therefore
whether its copy should be typed character by character or shown whole — with

    var MIN_WIDTH = 820;   /* keep in step with the media queries in
                              components.css */
    ...
    return matchMedia('(min-width: ' + MIN_WIDTH + 'px)').matches;

Nothing keeps a constant in step with a stylesheet, and by the time this was
measured its three consumers had walked away from it in three directions:

    .cf-values__track   ueber-uns    no-preference and (min-width: 51.25rem)
    .cf-pin             expertise    no-preference and (min-width: 64rem)
                                                   and (min-height: 45rem)
    .sp-track           landing                    acts.css, the same
    .sp4-track          ueber-uns                  64rem x 45rem for all
    .map-track          expertise                  three

51.25rem IS that 820, converted the day scripts/check-local-thresholds.py's
register took the threshold in — so the constant was stale in units as well as
in value, and at a 24 px default the gate it mirrored waited for 1230 px while
the script still engaged at 820. Neither of the other two gates was ever 820,
and not one of the three height terms existed in the script at all.

What it cost, measured on the landing page: at every viewport whose width
cleared 820 while the track's own gate did not — 860 x 900, 1000 x 800,
1023 x 760, 1280 x 700, 1440 x 719, and a 1366 x 768 laptop once the browser
has taken its chrome — the engine emptied act 2's four paragraphs into their
streamed spans and then bailed out of writing them back, because a track that
is not pinned has no travel to scrub. 481 characters of "Tausende Sensoren,
ein Strom." and the three lines under it were blank on screen at every scroll
position, for the whole life of the page. The .visually-hidden twin still
carried the sentence, so it read correctly to assistive technology and to
nobody else.

WHAT IT CHECKS

  no viewport thresholds   a shipping module in assets/js/ may not name
                           min-width, max-width, min-height or max-height, in
                           a matchMedia() string or anywhere else, and may not
                           compare innerWidth / innerHeight against a numeric
                           literal. Both are the same mistake: a gate written
                           twice, in two languages, with nothing holding the
                           copies together.

  feature queries stay     prefers-reduced-motion, pointer, prefers-color-scheme
                           and the rest are not layout gates and are not
                           touched. They ask the browser about the reader, and
                           there is no stylesheet declaration they could drift
                           from.

  comments are exempt      the note in cf-stream.js quotes the query it used to
                           run precisely so the next reader knows why the file
                           is shaped the way it is. Prose about a mistake is
                           not the mistake, so block and line comments and
                           string-free code are stripped before the scan.

WHAT TO DO INSTEAD, which is what cf-stream.js and act-rail.js both now do:
ask the element. A track's tall height and its `view-timeline-name` are
declared in the same rule inside the same gate, so

    var named = getComputedStyle(track).getPropertyValue('view-timeline-name');
    named && named !== 'none'

is true in precisely the tier the stylesheet pins in — in that consumer's own
units, with that consumer's own height term, folding in @supports and
prefers-reduced-motion for free because the declaration sits inside those too.
One gate, written once, read where it is needed.

AND IT IS READ AS A PROPERTY VALUE, NOT AS A DOM PROPERTY, which this section
recommended for as long as it has existed and which cost act-rail.js a live
fault in one engine. `getComputedStyle(track).viewTimelineName` is the value in
every browser that HAS view-timeline-name and `undefined` in every browser that
does not — Gecko, which has no scroll-driven animation at all and is therefore
the one engine permanently in the degraded tier. Compared against 'none' either
way round, `undefined` reads as "this track is pinned" there, which is the
opposite of the truth and the exact inversion this section exists to prevent.
getPropertyValue() returns the empty string for a property the engine does not
implement AND for one that is not set, so the two ways a track can be unpinned
answer the same falsy thing. cf-stream.js's pinned() guards the DOM read with a
`typeof` for the same reason and has its own note on it.
→ scripts/check-act-beats.py holds this shape for the rail.
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
JS_DIR = ROOT / "design-system" / "assets" / "js"

# The four that are layout, and not the ones that are about the reader.
THRESHOLD = re.compile(r"\b(?:min|max)-(?:width|height)\b")
# innerWidth / innerHeight weighed against a bare number, either way round.
VIEWPORT_CMP = re.compile(
    r"(?:\binner(?:Width|Height)\s*[<>]=?\s*\d"
    r"|\d\s*[<>]=?\s*\binner(?:Width|Height)\b)"
)


def strip_comments(src):
    """Blank out /* */ and // runs, keeping line numbering intact."""
    out = []
    i, n = 0, len(src)
    state = None  # None | 'block' | 'line' | 'sq' | 'dq'
    while i < n:
        c = src[i]
        nxt = src[i + 1] if i + 1 < n else ""
        if state is None:
            if c == "/" and nxt == "*":
                state, i = "block", i + 2
                out.append("  ")
                continue
            if c == "/" and nxt == "/":
                state, i = "line", i + 2
                out.append("  ")
                continue
            if c in "'\"":
                state = "sq" if c == "'" else "dq"
            out.append(c)
        elif state == "block":
            if c == "*" and nxt == "/":
                state, i = None, i + 2
                out.append("  ")
                continue
            out.append("\n" if c == "\n" else " ")
        elif state == "line":
            if c == "\n":
                state = None
                out.append("\n")
            else:
                out.append(" ")
        else:  # inside a string literal — kept, it is where a query would hide
            if c == "\\":
                out.append(c)
                i += 1
                if i < n:
                    out.append(src[i])
                i += 1
                continue
            if (state == "sq" and c == "'") or (state == "dq" and c == '"'):
                state = None
            out.append(c)
        i += 1
    return "".join(out)


def fail(msg):
    print(f"FAIL  {msg}")
    return True


def main():
    files = sorted(JS_DIR.glob("*.js"))
    if not files:
        return fail(f"no shipping scripts under {JS_DIR.relative_to(ROOT)}")

    bad = False
    scanned = 0
    for path in files:
        src = path.read_text(encoding="utf-8")
        code = strip_comments(src)
        scanned += 1
        rel = path.relative_to(ROOT)
        for lineno, line in enumerate(code.splitlines(), 1):
            for rx, what in ((THRESHOLD, "a viewport threshold"),
                             (VIEWPORT_CMP, "a viewport comparison")):
                m = rx.search(line)
                if not m:
                    continue
                shown = src.splitlines()[lineno - 1].strip()
                bad |= fail(
                    f"{rel}:{lineno} restates a layout gate as {what} "
                    f"— {m.group(0)!r} in: {shown[:88]}"
                )

    if bad:
        print(
            "\n      A gate written in a stylesheet and again in a script is two "
            "gates.\n      Read it off the element instead — see this file's "
            "header, and the\n      note over pinned() in assets/js/cf-stream.js."
        )
        return 1

    print(
        f"OK  {scanned} shipping scripts carry no min-/max-width or "
        f"min-/max-height threshold and weigh innerWidth/innerHeight against no "
        f"literal; every layout gate is read off the element that declares it"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
