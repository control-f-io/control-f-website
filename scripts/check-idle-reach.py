#!/usr/bin/env python3
"""A pause rule must reach the thing it pauses.

check-idle-motion.py holds the other half of this and states the bill in full:
an `infinite` animation on the DOCUMENT clock runs for the life of the tab, on
screen or fifteen thousand pixels away, and half the landing page's main thread
went to twenty-one sensor labels nobody was looking at. Its rule is in two
halves — the stylesheet must pause every perpetual animation under `[data-idle]`,
and a page carrying markup those selectors reach must mark a box with
`data-cf-idle` and load assets/js/cf-idle.js.

Both halves passed on patterns/landing-page.html while the gate reached two of
its three subjects. This is the half that was missing: the marked box has to
CONTAIN the elements the pause rule matches. A gate somewhere else on the page
is not a gate.

WHAT IT FOUND, on the page it was written for. components.css pauses
`.cf-stream__caret` under `[data-idle]`, with the note "the last two go the same
way as the other 126". They did not. cf-stream.js builds one caret per
`[data-stream]` track and patterns/landing-page.html has three of them — act 1+2,
act 4 and act 5 — of which only the first carried `data-cf-idle`. Measured at
1440 x 900, the two unreached carets stand at document y 13 643 and 16 982, five
and nine thousand pixels outside the only box that could ever hold them still.
The rule matched nothing, on every load, from the day it was written, and
nothing in the suite could say so: check-idle-motion.py asks whether SOME box on
the page carries the attribute, which was true.

The same page's `.lp-flow__leaf` is the other shape of the fault and the
expensive one — reached by a box, but by a box 5 760 px tall whose top edge
stands above the fold, so the gate was open at the top of the page and cost 65 %
of a core at the hero. That one is a distance rather than a containment and is
answered by `data-cf-idle="<rootMargin>"`; the measurements are in
assets/js/cf-idle.js. This check holds the containment, which is the part a file
can see.

THE RULE, in two clauses.

  in the markup   for every `[data-idle] SUBJ` rule in the shipping CSS, every
                  element in every page that matches SUBJ must have an ancestor
                  carrying `data-cf-idle`. The subject is read out of the CSS,
                  so a pause rule written tomorrow enters this check by existing
                  — the argument check-idle-motion.py and check-glass-budget.py
                  both make for reading the rule out of the stylesheet instead
                  of keeping a list here.

  from a script   an element a script CREATES is in no page's markup and cannot
                  be walked to. cf-stream.js declares its own insertion root in
                  three lines at the top of the file — `var TRACK =
                  '[data-stream]'` — and appends its caret inside the track it
                  is driving, so the containment rule for a script-built subject
                  is that every one of those roots carries the mark. Both the
                  class it builds and the root it builds into are read from the
                  file rather than repeated here.

WHAT IS OUT OF SCOPE. A page that does not load cf-idle.js has no gate to hold
and is not read — the same boundary check-idle-motion.py draws, and the reason
foundations and components pages are not dragged in by owning a caret they never
animate. `docs.css` and `preview.css` do not ship. Neither does the root
generation of the site.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-idle-reach.py        # check, exit 1 on drift
    python3 scripts/check-idle-reach.py -v     # show every subject, not only hits
"""

import argparse
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
CSS = DS / "assets" / "css"
JS = DS / "assets" / "js"

SHIPPING_CSS = ("tokens.css", "base.css", "components.css", "acts.css")
PAGE_DIRS = ("patterns", "prototypes", "foundations", "components")

IDLE_SCRIPT = "cf-idle.js"
IDLE_MARK = "data-cf-idle"

# The scripts that BUILD a gated element rather than finding one in the markup.
# Each is read for two things it already states about itself: the class name it
# assigns, and the selector it names as the root it inserts into. Nothing about
# either is repeated here — a script that renames its own caret renames it in
# this check on the same commit.
BUILDER_SCRIPTS = ("cf-stream.js",)


def strip_comments(text):
    """Blank out /* ... */ so a selector quoted in prose is never a rule."""
    return re.sub(r"/\*.*?\*/", lambda m: " " * len(m.group(0)), text, flags=re.S)


def preludes(text):
    """Every selector list that opens a block, at any nesting depth.

    A linear scan and not `([^{}]*)\\{`: that pattern rescans from each start
    position and takes quadratic time on a 144 KB stylesheet, which is long
    enough to look like a hang. check-idle-motion.py walks its rules by hand for
    the same reason.
    """
    out = []
    start = 0
    for i, ch in enumerate(text):
        if ch in "{}":
            chunk = text[start:i].strip()
            if ch == "{" and chunk:
                out.append(chunk)
            start = i + 1
    return out


def split_selectors(prelude):
    """A selector list split on its top-level commas only.

    `:is(a, b)` holds a comma that does not separate selectors, and splitting on
    every comma cuts the rule in half — `[data-idle] :is(.sp-stream > b` and a
    stray `.sp-stream > b + b)`. The first still names its element and would
    still be checked; the second would be dropped on the floor, which is a
    subject silently leaving the check.
    """
    parts = []
    depth = 0
    buf = ""
    for ch in prelude:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(buf)
            buf = ""
        else:
            buf += ch
    parts.append(buf)
    return [p for p in parts if p.strip()]


def pause_subjects():
    """Every SUBJ in a `[data-idle] SUBJ { ... }` rule across the shipping CSS.

    The subject is what follows the gate: the selector whose elements the rule
    holds still. `:is(a, b)` is expanded, because one rule pausing two families
    is two subjects to reach.
    """
    subs = {}
    for name in SHIPPING_CSS:
        path = CSS / name
        if not path.exists():
            continue
        text = strip_comments(path.read_text(encoding="utf-8"))
        for prelude in preludes(text):
            for part in split_selectors(prelude):
                part = part.strip()
                if not part.startswith("[data-idle]"):
                    continue
                rest = part[len("[data-idle]"):].strip()
                if not rest:
                    continue
                for sub in expand(rest):
                    subs.setdefault(sub, []).append(name)
    return subs


def expand(selector):
    """`:is(a, b) > c` -> ['a > c', 'b > c']; anything else comes back as one."""
    m = re.search(r":is\(([^()]*)\)", selector)
    if not m:
        return [selector.strip()]
    out = []
    for alt in m.group(1).split(","):
        out.extend(expand(selector[:m.start()] + alt.strip() + selector[m.end():]))
    return out


def key_class(selector):
    """The rightmost class in a subject selector — the element it selects.

    `.sp-stream > b` selects a <b>, and the thing to find in the page is the
    .sp-stream that holds it: an element with no class of its own cannot be
    found by class, and its parent's containment answers the same question,
    because an ancestor of the parent is an ancestor of the child.
    """
    classes = re.findall(r"\.([A-Za-z0-9_-]+)", selector)
    return classes[-1] if classes else None


class Tree(HTMLParser):
    """Elements with their class list, their attributes and their ancestry.

    Only what this check asks of a page: which elements carry a class, which
    carry an attribute, and whether one is inside another. No selector engine —
    containment is the whole question.
    """

    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
            "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.nodes = []          # (classes, attrs, marked_ancestor, line)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = set((a.get("class") or "").split())
        marked = any(m for _, _, m, _ in [] ) # placeholder, replaced below
        marked = self.stack[-1][2] if self.stack else False
        self.nodes.append((classes, a, marked, self.getpos()[0]))
        if tag not in self.VOID:
            self.stack.append((tag, classes, marked or IDLE_MARK in a))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                return


def builders():
    """(class the script creates, selector it inserts into) for each builder."""
    out = []
    for name in BUILDER_SCRIPTS:
        path = JS / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        made = re.findall(r"\.className\s*=\s*['\"]([A-Za-z0-9_ -]+)['\"]", text)
        root = re.search(r"var\s+TRACK\s*=\s*['\"]\[([a-z-]+)\][\"']", text)
        if made and root:
            for cls in made:
                for one in cls.split():
                    out.append((name, one, root.group(1)))
    return out


def pages():
    for d in PAGE_DIRS:
        base = DS / d
        if base.exists():
            for p in sorted(base.glob("*.html")):
                yield p


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    subjects = pause_subjects()
    if not subjects:
        print("check-idle-reach: no [data-idle] pause rule in the shipping CSS.")
        return 1

    built = builders()
    built_classes = {cls: (script, attr) for script, cls, attr in built}

    failures = []
    checked = 0

    for page in pages():
        text = page.read_text(encoding="utf-8")
        if IDLE_SCRIPT not in text:
            continue
        checked += 1
        tree = Tree()
        tree.feed(text)
        rel = page.relative_to(ROOT)

        for subject in sorted(subjects):
            cls = key_class(subject)
            if not cls:
                continue

            # A subject a script builds is nowhere in the markup. Its
            # containment is the containment of the root it is built into.
            if cls in built_classes:
                script, attr = built_classes[cls]
                if script.replace(".js", "") not in text and script not in text:
                    continue
                roots = [n for n in tree.nodes if attr in n[1]]
                for classes, attrs, marked, line in roots:
                    if IDLE_MARK not in attrs and not marked:
                        failures.append(
                            f"{rel}:{line}: [{attr}] gets a .{cls} from {script}, "
                            f"and neither it nor an ancestor carries {IDLE_MARK} — "
                            f"`[data-idle] {subject}` reaches nothing here")
                if args.verbose and roots:
                    print(f"  {rel}: .{cls} <- {script} into [{attr}] x{len(roots)}")
                continue

            hits = [n for n in tree.nodes if cls in n[0]]
            for classes, attrs, marked, line in hits:
                if not marked and IDLE_MARK not in attrs:
                    failures.append(
                        f"{rel}:{line}: .{cls} has no {IDLE_MARK} ancestor — "
                        f"`[data-idle] {subject}` never reaches it")
            if args.verbose and hits:
                print(f"  {rel}: {subject} x{len(hits)} reached")

    if failures:
        print("check-idle-reach: a pause rule does not reach what it pauses.\n")
        for f in failures:
            print("  " + f)
        print(f"\n{len(failures)} unreached. An `infinite` animation on the document "
              f"clock that no box can hold still runs for the life of the tab.")
        return 1

    print(f"check-idle-reach: {len(subjects)} pause subject(s) across {checked} "
          f"page(s) — every one inside a {IDLE_MARK} box.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
