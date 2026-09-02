#!/usr/bin/env python3
"""No file in the tree carries a conflict marker.

This is the narrowest check in the directory and the only one whose subject
is not a design decision. It is here because it has already happened: a pull
request landed on main with its own rebase unresolved, and
`<<<<<<< HEAD` shipped as literal text in five files — the design system's
index, the reference page, two paragraphs of a foundation chapter, the
README, and a 29-line block inside a comment in components.css.

EVERY OTHER GATE PASSED OVER IT, and none of them was wrong to. A marker
inside a CSS comment is comment text; a marker in a documentation page is a
paragraph; a marker in Markdown is a line of prose. The thirty-odd checks in
this directory each read one decision — a distance, a ramp, a dash period, a
count — and a conflict marker is not a wrong value of anything. It is the one
shape that is never correct in any file type this repository ships, and
nothing was reading for it.

Cheap enough to be free: one pass over the tracked text files, one string
comparison per line.

WHAT COUNTS. `<<<<<<< ` and `>>>>>>> ` at the start of a line are findings on
their own — no file here has a legitimate reason for either. A bare
`=======` is a finding ONLY between them, because seven equals signs is also
a setext heading rule in Markdown and a divider in an ASCII figure, and a
check that failed those would be enforcing a rule nobody wrote.

    python3 scripts/check-merge-markers.py
    python3 scripts/check-merge-markers.py -v   # print what was scanned
"""

import argparse
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Binary payloads have no lines to read and would only cost time. Everything
# else in the tree is text somebody edits, which is where a marker can land.
SKIP_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".mp4", ".mov",
    ".woff", ".woff2", ".ttf", ".otf", ".pdf", ".zip", ".gz",
}

OPEN = "<<<<<<< "
CLOSE = ">>>>>>> "
MID = "======="


def tracked_files():
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-z"],
        capture_output=True, text=True, check=True).stdout
    for name in out.split("\0"):
        if not name:
            continue
        path = ROOT / name
        if path.suffix.lower() in SKIP_SUFFIXES or not path.is_file():
            continue
        yield name, path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print how many files were read")
    args = ap.parse_args()

    findings = []
    scanned = 0
    for name, path in tracked_files():
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        scanned += 1
        inside = False
        for n, line in enumerate(text.split("\n"), 1):
            if line.startswith(OPEN):
                inside = True
                findings.append((name, n, line[:60]))
            elif line.startswith(CLOSE):
                inside = False
                findings.append((name, n, line[:60]))
            elif inside and line.rstrip() == MID:
                findings.append((name, n, line))

    if args.verbose:
        print("scanned %d tracked text file(s)" % scanned)

    if findings:
        print("merge markers: %d line(s) in %d file(s)\n"
              % (len(findings), len({f for f, _, _ in findings})))
        for name, n, line in findings:
            print("  %s:%d  %s" % (name, n, line))
        print("\n  A conflict marker is the one shape that is never correct in any file")
        print("  this repository ships. Resolve the conflict; do not delete the lines")
        print("  and keep whichever half happens to be on top.")
        return 1

    print("merge markers: none, in %d tracked text file(s)." % scanned)
    return 0


if __name__ == "__main__":
    sys.exit(main())
