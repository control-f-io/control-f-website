#!/usr/bin/env python3
"""A page with two shapes must carry the reader between them.

THE FAULT. patterns/landing-page.html gates its pinned "Was wir machen" stage
behind `(min-width: 64rem) and (min-height: 45rem)`. Above the gate the section
is a sticky stage with a track of scroll behind it; below it the section is a
stacked column of four cards. At 1280 x 900 the same section is 6901 px tall in
one mode and 2209 px in the other — 4692 px of scroll that exists on one side
of a one-pixel threshold and not on the other.

A viewport resize does not carry the reader across that on its own. The browser
keeps the scroll OFFSET, in pixels, and the offset means a different thing on
each side of the gate. Measured, reader parked half way through the section:

  1280x900 -> 1023x900   scrollY held at 4537; the section's bottom edge ended
                         up 1005 px ABOVE the window and the reader was looking
                         at "Blog", five sections on.
  1280x900 -> 1280x719   same offset, same section gone, reader on "FAQ".
  1024x768 -> 768x1024   an iPad turned from landscape to portrait, which is
                         the ordinary way a reader crosses both edges at once.

At 85 % of the track the shorter document cannot hold the old offset at all, so
it is clamped to the end and the reader lands on "Das Team", the last section on
the page.

Scroll anchoring does not cover it: it is suppressed for layout changes driven
by a viewport resize. That was tested rather than assumed — with the stage's
stickiness removed, with `overflow-anchor: auto` forced on every element, and
with `overflow-anchor: none` forced across the pin's subtree, scrollY held at
4537 in all three, identical to the baseline. There is no CSS lever, so the cure
is a file — assets/js/cf-pin-gate.js — and a file is a thing a page can simply
not load.

WHAT THIS CHECKS, and why it is the shape of check this repository keeps. The
fault is invisible in every screenshot: both modes render perfectly, and the
only way to see it is to be mid-section at the instant the viewport changes.
Nothing in a static file says "this page switches shape", except the two things
that are countable:

  a page INSTANTIATES the pinned track   markup carrying the .cf-pin scaffold
  a page LOADS THE CURE                  <script src=".../cf-pin-gate.js">

Every page that does the first must do the second. Delete the script tag and
this fails; add a third pinned page without it and this fails on the day it is
added rather than on the day someone turns a tablet.

It also holds the cure itself in place: cf-pin-gate.js must exist, and it must
still be the thing it claims to be — a resize listener. A file that loads and
listens for nothing passes every other check in this repository.

SCOPE: every .html file in the tree except the outgoing generation at the root,
which is a different site and does not carry .cf-pin.
"""

import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CURE = os.path.join("design-system", "assets", "js", "cf-pin-gate.js")

# The pinned scaffold, as it appears in markup. .cf-pin is the track and
# .cf-pin__stage is the sticky box inside it; a page that has either has the
# mode switch, because the gate is on the component and not on the page.
PIN = re.compile(r'class="[^"]*\bcf-pin(?:__stage)?\b[^"]*"')

# A <script src> ending in cf-pin-gate.js, however the page spells the path.
LOADS = re.compile(r'<script\b[^>]*\bsrc="[^"]*\bcf-pin-gate\.js"')

# Comments describe; only markup instantiates. Strip comments before looking,
# or the note that explains this check would itself satisfy it.
COMMENT = re.compile(r"<!--.*?-->", re.S)


def html_files():
    out = []
    for base, dirs, names in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules")]
        rel = os.path.relpath(base, ROOT)
        # The root HTML is the outgoing generation — a different site.
        if rel == ".":
            continue
        if rel.split(os.sep)[0] not in ("design-system", "blog"):
            continue
        for n in sorted(names):
            if n.endswith(".html"):
                out.append(os.path.relpath(os.path.join(base, n), ROOT))
    return sorted(out)


def audit():
    findings = []
    seen = []

    cure_path = os.path.join(ROOT, CURE)
    if not os.path.exists(cure_path):
        findings.append((CURE, "the cure is missing entirely"))
        cure_src = ""
    else:
        with open(cure_path, encoding="utf-8") as fh:
            cure_src = fh.read()
        if "addEventListener" not in cure_src or "'resize'" not in cure_src:
            findings.append((CURE, "no resize listener — the file is loaded by every "
                                   "pinned page and does nothing"))
        if "scrollTo" not in cure_src:
            findings.append((CURE, "never moves the scroll position — a listener that "
                                   "measures the fault and leaves it in place"))

    for rel in html_files():
        with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
            raw = fh.read()
        src = COMMENT.sub("", raw)
        pinned = bool(PIN.search(src))
        loads = bool(LOADS.search(src))
        if pinned and not loads:
            findings.append((rel,
                             "instantiates the pinned track and does not load "
                             "cf-pin-gate.js — a reader mid-section is thrown past the "
                             "whole section the first time this viewport crosses "
                             "(min-width: 64rem) or (min-height: 45rem) downward"))
        if pinned or loads:
            seen.append((rel, pinned, loads))

    return findings, seen


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every page that pins or loads the cure")
    args = ap.parse_args()

    findings, seen = audit()

    if args.verbose:
        for rel, pinned, loads in seen:
            print("  %-46s %-10s %s" % (rel,
                                        "pins" if pinned else "-",
                                        "loads cure" if loads else "NO CURE"))
        print()

    if findings:
        for where, why in findings:
            print("%s\n    %s" % (where, why), file=sys.stderr)
        print("\n%d pinned page%s left without the cure. A section that is 6901 px tall "
              "above the gate and 2209 px below it cannot hand the reader a pixel "
              "offset across it — load design-system/assets/js/cf-pin-gate.js."
              % (len(findings), "" if len(findings) == 1 else "s"), file=sys.stderr)
        return 1

    pins = sum(1 for _, p, _ in seen if p)
    print("pin gate: %d pinned page%s, all %d loading the cure."
          % (pins, "" if pins == 1 else "s", pins))
    return 0


if __name__ == "__main__":
    sys.exit(main())
