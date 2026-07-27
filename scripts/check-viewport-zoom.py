#!/usr/bin/env python3
"""Nothing in design-system/ may take pinch zoom away from the reader.

The fourteenth check. check-a11y.py next door is arithmetic about what a page
*says* — an id is there or it is not, a heading level is one more than the last
or it is two. This one is about a control the reader owns, and a page taking it
away.

foundations/mobile.html states this twice, which in this repository is the
reliable sign that nothing runs it:

    "Every page carries width=device-width, initial-scale=1 and nothing
     else. No maximum-scale, no user-scalable=no: pinch zoom works
     everywhere, which is not a nicety — it is how a large share of people
     read on a phone at all."

and again, in the Don't list at the foot of the same page:

    "Never user-scalable=no, and never a maximum-scale under 5."

WHY A SCRIPT AND NOT A CODE REVIEW. `user-scalable=no` is the most invisible
regression this system can ship. It renders identically at every width, on
every machine a designer owns, in every screenshot, and in every measurement
the responsive lane takes — scrollWidth is unchanged, no element overflows, no
console error, no network failure. A desktop browser ignores the directive
outright, so it cannot be caught by looking. It is visible only to someone
holding a phone who needs the text bigger and finds that it will not move, and
that person is not in the review. Every other check in this directory exists
because a claim written in prose was broken by exactly one declaration; this
one exists because the claim cannot be broken *visibly* at all.

It is also the one accessibility failure here with a number attached: WCAG 2.1
SC 1.4.4 (Resize Text, AA) requires text to scale to 200 % without loss of
content or function, and a viewport tag that pins the scale defeats it on the
devices where it matters most.

WHAT IT CHECKS, on every .html file under design-system/:

  present      exactly one <meta name="viewport">. A page with none gets
               desktop-width emulation on a phone — the whole layout renders
               at ~980 px and is scaled down, which is a different bug with
               the same symptom (unreadable type) and the same invisibility
               on a desktop.
  shape        the content declares width=device-width and initial-scale=1.
  user-scalable   never `no` or `0`.
  maximum-scale   absent, or 5 and above. The register's own wording.
  minimum-scale   absent, or 1 and below — a floor above 1 cannot block zoom
               in, but it pins the reader out of zooming back to fit, which
               is the same class of seizure of a control that is theirs.

And, in the three shipping stylesheets:

  text-size-adjust   `100%` or `auto`, never `none`. base.css sets 100 % on
               html to switch off iOS Safari's automatic text inflation in
               landscape, which would otherwise resize some blocks and not
               others and quietly break every measured line length on this
               site. `none` reads as the same intent and is not: on the
               engines that still honour the non-standard value it is a
               third behaviour, and it has been the standard way to break
               zoom on iOS for a decade. The distinction is one word and no
               screenshot shows it.

WHAT IT DOES NOT READ, and why each exclusion is load-bearing here:

  <pre>, <code>, <textarea> and HTML comments. THIS IS NOT HYGIENE. The page
  that states the rule quotes every value the rule forbids — mobile.html
  writes `user-scalable=no` and `maximum-scale` inside <code> in the same
  sentence that bans them, and this docstring does the same. A checker that
  read prose would fail on the specification and pass on a real regression,
  which is precisely backwards.

  The outgoing generation at the repository root. Scoped to design-system/,
  the same boundary check-links.py draws and for the same reason: those pages
  are the previous generation and are not this system's to govern.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-viewport-zoom.py       # check, exit 1 on a finding
    python3 scripts/check-viewport-zoom.py -v    # list every page, not only failures
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TREE = ROOT / "design-system"
CSS = TREE / "assets" / "css"
SHIPPING = ("tokens.css", "base.css", "components.css")

# Regions whose contents are documentation, not markup the browser acts on.
MASK = re.compile(
    r"<!--.*?-->|<pre\b.*?</pre>|<code\b.*?</code>|<textarea\b.*?</textarea>",
    re.S | re.I,
)
META = re.compile(r"<meta\b[^>]*>", re.I)
NAME = re.compile(r"""\bname\s*=\s*["']?viewport["']?""", re.I)
CONTENT = re.compile(r"""\bcontent\s*=\s*["']([^"']*)["']""", re.I)
ADJUST = re.compile(r"(?<![\w-])(?:-\w+-)?text-size-adjust\s*:\s*([^;{}]+)", re.I)


def blank(m):
    """Replace a masked region with spaces, keeping newlines for line numbers."""
    return re.sub(r"[^\n]", " ", m.group(0))


def pairs(content):
    """The viewport content string as {key: value}, lowercased."""
    out = {}
    for part in re.split(r"[,;]", content):
        key, sep, value = part.partition("=")
        if sep:
            out[key.strip().lower()] = value.strip().lower()
    return out


def number(value):
    """The leading number in a scale value, or None. `2.0`, `1`, `yes` -> None."""
    m = re.match(r"-?\d*\.?\d+", value)
    return float(m.group(0)) if m else None


def audit_pages():
    findings, seen = [], []
    for path in sorted(TREE.rglob("*.html")):
        rel = path.relative_to(ROOT)
        text = MASK.sub(blank, path.read_text(encoding="utf-8"))
        tags = [(text.count("\n", 0, m.start()) + 1, m.group(0))
                for m in META.finditer(text) if NAME.search(m.group(0))]

        if not tags:
            findings.append((rel, 0, "no <meta name=\"viewport\"> — a phone will "
                                     "emulate a ~980 px desktop and scale the page down"))
            continue
        if len(tags) > 1:
            findings.append((rel, tags[1][0], "%d <meta name=\"viewport\"> tags; the "
                                              "last one wins and the first is a lie"
                                              % len(tags)))
        line, tag = tags[0]
        got = CONTENT.search(tag)
        if not got:
            findings.append((rel, line, "<meta name=\"viewport\"> with no content"))
            continue
        content = got.group(1)
        kv = pairs(content)
        notes = []

        if kv.get("width") != "device-width":
            findings.append((rel, line, "width=%s, not device-width"
                             % kv.get("width", "(absent)")))
        scale = number(kv.get("initial-scale", ""))
        if scale != 1:
            findings.append((rel, line, "initial-scale=%s, not 1"
                             % kv.get("initial-scale", "(absent)")))

        us = kv.get("user-scalable")
        if us in ("no", "0"):
            findings.append((rel, line, "user-scalable=%s takes pinch zoom away "
                                        "(WCAG 2.1 SC 1.4.4)" % us))
        elif us is not None:
            notes.append("user-scalable=%s" % us)

        for key, limit, how in (("maximum-scale", 5, "under"),
                                ("minimum-scale", 1, "over")):
            if key not in kv:
                continue
            value = number(kv[key])
            if value is None:
                findings.append((rel, line, "%s=%s is not a number" % (key, kv[key])))
            elif (value < limit) if how == "under" else (value > limit):
                findings.append((rel, line, "%s=%g is %s %g and pins the reader's zoom"
                                 % (key, value, how, limit)))
            else:
                notes.append("%s=%g" % (key, value))

        seen.append((rel, line, content, ", ".join(notes)))
    return findings, seen


def audit_css():
    findings, seen = [], []
    for name in SHIPPING:
        path = CSS / name
        if not path.exists():
            findings.append((pathlib.Path("design-system/assets/css") / name, 0,
                             "stylesheet is missing"))
            continue
        text = re.sub(r"/\*.*?\*/", blank, path.read_text(encoding="utf-8"), flags=re.S)
        for m in ADJUST.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            value = m.group(1).strip().lower()
            rel = pathlib.Path("design-system/assets/css") / name
            if value in ("100%", "auto"):
                seen.append((rel, line, "text-size-adjust: " + value, ""))
            else:
                findings.append((rel, line, "text-size-adjust: %s — only 100%% or auto; "
                                            "`none` is how zoom gets broken on iOS" % value))
    return findings, seen


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every page read, not only the failures")
    args = ap.parse_args()

    findings, seen = audit_pages()
    css_findings, css_seen = audit_css()
    findings += css_findings
    seen += css_seen

    if args.verbose:
        for rel, line, content, notes in seen:
            print("  %-46s %5d  %-44s %s" % (str(rel)[-46:], line, content[:44], notes))
        print()

    if findings:
        for rel, line, why in findings:
            print("%s:%d\n    %s" % (rel, line, why), file=sys.stderr)
        print("\n%d page%s that can refuse a reader more type. Every page carries "
              "width=device-width, initial-scale=1 and nothing that pins the scale."
              % (len(findings), "" if len(findings) == 1 else "s that"), file=sys.stderr)
        return 1

    pages = sum(1 for rel, *_ in seen if str(rel).endswith(".html"))
    print("viewport: %d pages carry device-width at initial-scale 1 with zoom "
          "unrestricted, %d text-size-adjust declaration(s) read."
          % (pages, len(seen) - pages))
    return 0


if __name__ == "__main__":
    sys.exit(main())
