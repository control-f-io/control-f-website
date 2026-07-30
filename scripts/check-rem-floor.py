#!/usr/bin/env python3
"""A gate's threshold restated as a floor must be capped at what it is a floor for.

THE FAULT, and it is one word of CSS in two places.

`rem` means two different things in the two contexts this system writes it in.
In a DECLARATION it resolves against the root element's actual font size, which
is the reader's text-size setting. In a MEDIA QUERY it resolves against the root
element's INITIAL font size and never against the reader's — so
`(min-height: 45rem)` is 720 px at every text size there has ever been, while
`block-size: 45rem` in the block that query opens is 720 px at a 16 px default,
900 at 20, 1080 at 24 and 1440 at 32.

acts.css gated the landing page's pinned act 3 on
`(min-width: 64rem) and (min-height: 45rem)` and then, inside it, restated the
same 45rem as a floor twice:

    main { --lp-measure: calc((max(45rem, 100vh - banner) - 13rem) * 2) }
    .lp-proc-stage { block-size: max(45rem, calc(100% - banner)) }

The intent is right: the composition should never get less room than the
smallest viewport the gate admits. The consequence is that the gate admits a
768 px viewport and the floor inside it then asks for 1440 — a floor 672 px
above the ceiling that clips it. .cf-pin__stage is `height: 100vh` and
`overflow: clip`, so the surplus is not scrolled, it is cut.

Measured on patterns/landing-page.html, act 3's twenty copy runs — title,
subtitle, body, benefit label and benefit, across four cards — counting only
the ones wholly inside the stage's clip rect:

    root    1280x900          1920x1080         1024x768
     16     20/20  cut   0    20/20  cut   0    20/20  cut   0
     20     20/20  cut   0    20/20  cut   0    10/20  cut 213
     24      9/20  cut 278    20/20  cut   0     2/20  cut 421
     32      0/20  cut 684     5/20  cut 491     0/20  cut 776

At a 32 px default — 200 % text, which is WCAG 1.4.4 at level AA — every word
of "Was wir machen" was below the clip, and the one section that says what the
company does rendered as an isometric figure, a row of numerals, and nothing
else. Nothing errored, nothing scrolled sideways, and none of the seventy-odd
gates in this directory caught it, because every one of them reads a 16 px root.

THE CURE is to cap the floor at the thing it is a floor for —
`max(min(45rem, 100vh), …)` — which is provably a no-op at the default size:
the gate does not apply below a 45rem viewport, 45rem is 720 px in the gate, so
at a 16 px root the floor is never above the height it is capped to. Measured
row for row, the 16 px line is identical before and after at all three
viewports; the 32 px line goes 0/20 to 10/20.

WHAT THIS CHECKS. For every `@media` block gated on `min-width` or `min-height`
in rem, no declaration inside it may use that same rem length as an argument of
`max()` without capping it — because that is the exact shape of "a floor the
gate cannot see". The rule is countable, it is about the coupling rather than
about a value, and it says why in the failure.

It is deliberately narrow. A rem length inside a gated block is fine; a rem
FLOOR that restates the gate's own threshold is not, because those are the two
that have to agree and cannot.

Proven failing on three reintroductions: either declaration reverted, and the
cap moved outside the max().

SCOPE: the four shipping stylesheets. docs.css and preview.css never ship.
"""

import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SHEETS = [os.path.join("design-system", "assets", "css", n)
          for n in ("tokens.css", "base.css", "components.css", "acts.css")]

CSS_COMMENT = re.compile(r"/\*.*?\*/", re.S)
MQ_REM = re.compile(r"min-(width|height)\s*:\s*(\d+(?:\.\d+)?)rem")


def blank_comments(src):
    """Blank comments in place so line numbers survive — the prose in these
    files states thresholds it does not apply."""
    return CSS_COMMENT.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), src)


def block_end(src, open_brace):
    """Index just past the matching close brace."""
    depth = 0
    for i in range(open_brace, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return i
    return len(src)


def split_args(s):
    """Top-level comma-separated arguments of a function's body."""
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
            continue
        cur += ch
    out.append(cur)
    return [a.strip() for a in out]


def calls(src, name):
    """(start, body) for every `name(...)` in src, with balanced parens."""
    out = []
    for m in re.finditer(r"(?<![\w-])%s\(" % name, src):
        depth, i = 1, m.end()
        while i < len(src) and depth:
            if src[i] == "(":
                depth += 1
            elif src[i] == ")":
                depth -= 1
            i += 1
        out.append((m.start(), src[m.end():i - 1]))
    return out


def uncapped_floors(body, rem):
    """Arguments of a max() inside `body` that use `<rem>rem` as a bare floor —
    i.e. not wrapped in a min() that also contains it."""
    lit = re.compile(r"(?<![\w.])%srem(?![\w-])" % re.escape(rem))
    bad = []
    for start, args in calls(body, "max"):
        for a in split_args(args):
            if not lit.search(a):
                continue
            # Capped if every occurrence of the literal sits inside a min().
            capped = False
            for _, inner in calls(a, "min"):
                if lit.search(inner):
                    capped = True
            if not capped:
                bad.append((start, a.strip()))
    return bad


def audit():
    findings = []
    seen = []
    for rel in SHEETS:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        raw = open(path, encoding="utf-8").read()
        src = blank_comments(raw)
        for m in re.finditer(r"@media\b", src):
            brace = src.find("{", m.end())
            if brace < 0:
                continue
            prelude = src[m.end():brace]
            thresholds = MQ_REM.findall(prelude)
            if not thresholds:
                continue
            end = block_end(src, brace)
            body = src[brace + 1:end]
            line = src.count("\n", 0, m.start()) + 1
            for axis, rem in thresholds:
                bad = uncapped_floors(body, rem)
                seen.append((rel, line, axis, rem, len(bad)))
                for off, arg in bad:
                    bl = src.count("\n", 0, brace + 1 + off) + 1
                    findings.append((
                        "%s:%d" % (rel, bl),
                        "max(%s) uses the gate's own %srem as a floor. The gate "
                        "at %s:%d reads `min-%s: %srem`, where rem is the "
                        "INITIAL root font size and so is %g px at every text "
                        "size; here rem is the READER's, so the same length is "
                        "%g px at a 24 px default and %g px at 32. The floor "
                        "then asks for more than the box that clips it and the "
                        "surplus is cut, not scrolled. Cap it: "
                        "max(min(%srem, <the viewport length>), …)"
                        % (arg[:60], rem, rel, line, axis, rem,
                           float(rem) * 16, float(rem) * 24, float(rem) * 32, rem)))
    return findings, seen


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every rem-gated media block")
    args = ap.parse_args()

    findings, seen = audit()

    if args.verbose:
        for rel, line, axis, rem, n in seen:
            print("  %-40s:%-5d min-%-6s %srem   %d uncapped floor%s"
                  % (rel, line, axis, rem, n, "" if n == 1 else "s"))
        print()

    if findings:
        for where, why in findings:
            print("%s\n    %s" % (where, why), file=sys.stderr)
        print("\n%d uncapped floor%s. A threshold written in rem means the "
              "initial root font size in a media query and the reader's in a "
              "declaration; a gate and a floor that restate one number in both "
              "places agree only at a 16 px default."
              % (len(findings), "" if len(findings) == 1 else "s"),
              file=sys.stderr)
        return 1

    print("rem floors: %d rem-gated media block%s, no threshold restated as an "
          "uncapped floor." % (len(seen), "" if len(seen) == 1 else "s"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
