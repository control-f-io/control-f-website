#!/usr/bin/env python3
"""The focus ring reaches everything that takes focus.

base.css declares the system's one focus indicator:

    :where(a, button, input, textarea, select, summary, [tabindex]):focus-visible {
      outline: var(--stroke-2) solid var(--focus-ring);
      outline-offset: 2px;
    }

Every ring on every page in this repository is that declaration. Its subject is
a HAND-WRITTEN LIST, which is the failure shape this directory already knows by
name — check-wrap-net.py exists because the overflow-wrap list in the same file,
eleven lines above this one, was a list of the elements that MEAN text rather
than of the elements that HOLD it, and shipped two live faults on the landing
page. This list was short in the same way and by the same element: it named the
things a person thinks of as controls, and <summary> is focusable in every
browser, is none of them, and carries no tabindex. Twenty-one summaries in six
files never received the ring.

WHY A SCRIPT AND NOT A REVIEW. A control with no ring renders identically to one
with a ring until somebody presses Tab, and then it renders identically again
unless that somebody knows what this system's ring looks like — because the user
agent draws its own. Measured on the landing page's first FAQ row, unfocused
against focused: the component's own sheen sweep changes contrast by 1.23:1,
under the 3:1 WCAG 2.4.11 asks of a focus indicator, and the browser's fallback
outline by 13.61:1. So the fallback was doing the whole job, at 1 px where the
system draws 2, at offset 0 where it draws 2, and in the UA's near-black rather
than in --focus-ring, the token that flips to lime under data-theme="inverse".
A screenshot of the focused row looks fine. It is simply not this system's ring.

WHAT IS COUNTED. The narrow, provable half: an element type that is focusable
with NO author attribute at all — the ones an author cannot see in the markup
because there is nothing in the markup to see. Anything focusable BECAUSE of an
attribute (tabindex, contenteditable) is already covered by the [tabindex] term
or is a deliberate act with its own visible evidence, and stays out.

The list of natively-focusable types below is closed on purpose and is not a
guess: each entry names the condition under which the element enters the
sequential focus order, and an entry only fires when the markup actually
satisfies it. A <video> without controls is not a tab stop and is not counted;
the same tag with controls is.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "design-system" / "assets" / "css" / "base.css"

# Element types the HTML standard puts in the sequential focus order with no
# author attribute. Each is (tag, predicate over the tag's attribute text, why).
NATIVELY_FOCUSABLE = [
    ("a",        lambda a: "href=" in a,       "an <a> with href"),
    ("area",     lambda a: "href=" in a,       "an <area> with href"),
    ("button",   lambda a: True,               "a <button>"),
    ("input",    lambda a: 'type="hidden"' not in a.replace("'", '"'),
                                               "an <input> that is not hidden"),
    ("select",   lambda a: True,               "a <select>"),
    ("textarea", lambda a: True,               "a <textarea>"),
    ("summary",  lambda a: True,               "a <summary> (the disclosure's own control)"),
    ("details",  lambda a: False,              "a <details> (its summary takes the focus)"),
    ("audio",    lambda a: "controls" in a,    "an <audio controls>"),
    ("video",    lambda a: "controls" in a,    "a <video controls>"),
    ("iframe",   lambda a: False,              "an <iframe> (its document takes the focus)"),
    ("object",   lambda a: False,              "an <object> (not a tab stop in any current engine)"),
]

# The rule this file is about. Matched on the selector rather than on a comment
# so that renaming the comment cannot silently take the check out of scope.
RULE = re.compile(
    r":where\(([^)]*)\)\s*:focus-visible\s*\{([^}]*)\}",
    re.S,
)

HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)


def blank_comments(html: str) -> str:
    """Drop comment CONTENT but keep every newline, so a reported line number is
    the line the reader will find the tag on. This tree comments in paragraphs —
    stripping them outright moved every citation by hundreds of lines."""
    return HTML_COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), html)


def read_focus_rule():
    css = BASE.read_text(encoding="utf-8")
    css_nc = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    hits = [m for m in RULE.finditer(css_nc) if "outline" in m.group(2)]
    if not hits:
        sys.exit(
            "check-focus-ring: no `:where(...):focus-visible { outline: ... }` rule in\n"
            f"  {BASE.relative_to(ROOT)}\n"
            "This check exists to hold that rule's subject list. If the system's one\n"
            "focus indicator has been rewritten in another shape, rewrite this check\n"
            "with it — do not delete it."
        )
    if len(hits) > 1:
        sys.exit(
            "check-focus-ring: more than one `:where(...):focus-visible` outline rule in\n"
            f"  {BASE.relative_to(ROOT)}\n"
            "The system has ONE focus indicator; two rules means two, and this check\n"
            "cannot say which list governs which element."
        )
    terms = [t.strip() for t in hits[0].group(1).split(",") if t.strip()]
    body = hits[0].group(2)
    return terms, body


def used_types():
    """Which natively-focusable types the tree actually ships, and where."""
    found = {}
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in {".git", "node_modules"} for part in path.parts):
            continue
        html = blank_comments(path.read_text(encoding="utf-8", errors="replace"))
        for tag, focusable, phrase in NATIVELY_FOCUSABLE:
            for m in re.finditer(rf"<{tag}\b([^>]*)>", html, re.I):
                if focusable(m.group(1)):
                    line = html[: m.start()].count("\n") + 1
                    found.setdefault(tag, {"why": phrase, "sites": []})
                    found[tag]["sites"].append(
                        f"{path.relative_to(ROOT)}:{line}"
                    )
                    break          # one witness per file is enough to prove use
    return found


def main():
    terms, body = read_focus_rule()

    # The ring has to still BE the ring. A list that covers everything and paints
    # nothing is the same failure one step along.
    if "--focus-ring" not in body:
        sys.exit(
            "check-focus-ring: the focus rule no longer paints var(--focus-ring).\n"
            f"  found: {' '.join(body.split())}\n"
            "--focus-ring is the token that flips to lime under data-theme=\"inverse\";\n"
            "a literal colour here is invisible on half the surfaces in the system."
        )

    covered = {t for t in terms if not t.startswith("[")}
    has_tabindex_term = any(t.strip() == "[tabindex]" for t in terms)
    used = used_types()

    missing = []
    for tag, info in sorted(used.items()):
        if tag in covered:
            continue
        missing.append((tag, info))

    if missing:
        lines = [
            "check-focus-ring: the system's focus ring does not reach every element",
            "that takes focus without being asked to.",
            "",
            f"  the rule, in {BASE.relative_to(ROOT)}:",
            f"    :where({', '.join(terms)}):focus-visible",
            "",
        ]
        for tag, info in missing:
            sites = info["sites"]
            lines.append(f"  <{tag}> is not in that list, and {info['why']} ships in "
                         f"{len(sites)} file{'s' if len(sites) != 1 else ''}:")
            for s in sites[:8]:
                lines.append(f"      {s}")
            if len(sites) > 8:
                lines.append(f"      … and {len(sites) - 8} more")
            lines.append("")
        lines += [
            "Every one of those takes focus and is drawn by the user agent instead —",
            "1 px at offset 0 in the UA's own colour, where this system draws 2 px at",
            "offset 2 in --focus-ring. It photographs as a focused control either way.",
            "",
            f"Add the tag to the list in {BASE.relative_to(ROOT)}. Do not answer it in a",
            "component: the point of the rule is that there is one of it.",
        ]
        sys.exit("\n".join(lines))

    if not has_tabindex_term:
        sys.exit(
            "check-focus-ring: [tabindex] has left the focus rule's list.\n"
            "Every element made focusable by an author — .cf-team-strip is one — "
            "loses the ring with it."
        )

    shipped = ", ".join(f"<{t}>" for t in sorted(used))
    print(
        f"check-focus-ring: OK — the ring covers every natively-focusable type the "
        f"tree ships ({shipped}), and still paints var(--focus-ring)."
    )


if __name__ == "__main__":
    main()
