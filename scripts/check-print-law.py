#!/usr/bin/env python3
"""Hold the print law to its own registers.

foundations/print.html states what this system is on a sheet: paper carries two
of the six layers, ink is data or it is nothing, and nothing drawn as one object
may be divided by a sheet boundary. The first of those is a sentence and cannot
be checked. The other two are registers — a list of what is withdrawn and a list
of what may not be cut — and a register kept by hand is the thing this
repository has now been bitten by often enough to write a script instead.

The failure this exists for is not hypothetical and it is not even old: the
first draft of that chapter shipped its whole `display: none` register in
base.css, which loads BEFORE components.css, so every selector in it lost to the
component's own `display` at equal specificity. The page said the navigation bar
was withdrawn. The navigation bar printed. Nothing rendered wrong, because on a
screen nothing rendered at all — print rules are the one part of this system a
screenshot cannot show you, which is most of why they drifted for as long as
they did.

So this is a drift check between one chapter and the stylesheets it describes,
in both directions, plus two facts about the sheet that are cheap to assert and
expensive to lose.

  1. WITHDRAWN. Every selector the CSS withdraws in `@media print` is named in
     the chapter's register, and every selector the chapter's register names is
     withdrawn by the CSS.

  2. NOT CUT. The same, both ways, for `break-inside: avoid`.

  3. INK. `print-color-adjust` appears nowhere in the three shipping
     stylesheets. The clause is "ink is data or it is nothing", and the moment
     one rule asks the reader for a background the next one has a precedent.

  4. THE PAGE BOX. An `@page` rule exists and its margin is written in mm — A4
     and US Letter disagree about inches, and a margin that is right on one
     paper and wrong on the other is worse than the browser's default.

The registers are READ OUT OF THE CSS, not listed in this file, for the reason
check-glass-budget.py reads its own subject out of the stylesheet: a component
added to the register later should enter this check by existing, not by somebody
remembering that this file is also a place.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
SHIPPING = [
    DS / "assets/css/tokens.css",
    DS / "assets/css/base.css",
    DS / "assets/css/components.css",
]
CHAPTER = DS / "foundations/print.html"

# Selectors the chapter deliberately does not carry in its registers, each with
# the reason it is exempt. Kept short on purpose: an exemption is a hole.
EXEMPT_WITHDRAWN = {
    # Withdrawn beside their own components long before this chapter, and
    # documented there. The chapter names them in prose rather than in the
    # register table, which is where the register check would look.
    ".cf-consent",
    "dialog",
    ".cf-hero__still-toggle",
    ".cf-hero__still",
    ".cf-hero__media video",
    ".cf-stream__text",
    ".cf-stream__caret",
    ".cf-btn:not(.cf-btn--glass)[aria-busy=\"true\"]::after",
    ".cf-ground::before",
    ".cf-gantt__track::before",
    ".cf-arrive__ghost::after",
    ".cf-progress--indeterminate .cf-progress__rail::after",
    ".sp-annots-fig",
    ".sp-field",
}


def strip_comments(text):
    """CSS comments out, before anything looks at a selector.

    This file exists because a rule was in the wrong place; a parser that reads
    a paragraph of prose as a selector list is the same mistake one level down.
    """
    return re.sub(r"/\*.*?\*/", "", text, flags=re.S)


def print_blocks(text):
    """Yield the body of every top-level `@media print` block in a stylesheet.

    Brace counting rather than a regex, because these blocks contain nested
    rules and this file's whole subject is a rule that was in the wrong place.
    """
    for m in re.finditer(r"@media\s+print[^{]*\{", text):
        i = m.end()
        depth = 1
        while i < len(text) and depth:
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
            i += 1
        yield text[m.end(): i - 1]


def declared(body, prop, value):
    """Selectors in one `@media print` body that set `prop` to `value`."""
    found = set()
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", body):
        sels, decls = m.group(1), m.group(2)
        if re.search(r"(?<![-\w])%s\s*:\s*%s\s*(;|$)" % (prop, value), decls.strip()):
            for s in sels.split(","):
                s = " ".join(s.split())
                if s and not s.startswith("/*"):
                    found.add(s)
    return found


def chapter_codes(html):
    """Every `<code>` string in the chapter. The registers are code spans."""
    return {re.sub(r"<[^>]+>", "", c).strip()
            for c in re.findall(r"<code>(.*?)</code>", html, re.S)}


def main():
    findings = []

    css = {p: strip_comments(p.read_text(encoding="utf-8")) for p in SHIPPING}
    if not CHAPTER.exists():
        print("check-print-law: %s is missing — the law has no chapter."
              % CHAPTER.relative_to(ROOT))
        return 1
    html = CHAPTER.read_text(encoding="utf-8")
    named = chapter_codes(html)

    withdrawn, uncut, unstranded = set(), set(), set()
    for path, text in css.items():
        for body in print_blocks(text):
            withdrawn |= declared(body, "display", "none")
            uncut |= declared(body, "break-inside", "avoid")
            unstranded |= declared(body, "break-after", "avoid")

    # 1 + 2. Both registers, both directions.
    for label, found, exempt in (
        ("withdrawn", withdrawn, EXEMPT_WITHDRAWN),
        ("not cut", uncut | unstranded, set()),
    ):
        for sel in sorted(found - exempt):
            # Element selectors (figure, tr, thead) are named in the chapter as
            # bare words inside <code>, the same as class selectors.
            if sel not in named:
                findings.append(
                    "%s: the CSS %s `%s` and foundations/print.html does not name it."
                    % (label.upper(), "withdraws" if label == "withdrawn" else "protects", sel)
                )

    # The other direction, and it is the one that catches a rule written where
    # it cannot win: the chapter names a selector, the CSS never applies it.
    register = re.search(
        r'<h2>What may not be cut</h2>(.*?)</section>', html, re.S)
    if register:
        for code in chapter_codes(register.group(1)):
            if code.startswith(".") and code not in uncut | unstranded:
                findings.append(
                    "NOT CUT: foundations/print.html names `%s` and no `@media print` "
                    "rule gives it `break-inside: avoid`." % code)
    withdrawn_sec = re.search(
        r'<h2>What a sheet does not carry</h2>(.*?)<h3>', html, re.S)
    if withdrawn_sec:
        for code in chapter_codes(withdrawn_sec.group(1)):
            if code.startswith(".") and code not in withdrawn and code not in EXEMPT_WITHDRAWN:
                findings.append(
                    "WITHDRAWN: foundations/print.html names `%s` and no `@media print` "
                    "rule gives it `display: none`." % code)

    # 3. Ink is data or it is nothing.
    for path, text in css.items():
        for m in re.finditer(r"^[^/*\n]*\bprint-color-adjust\s*:", text, re.M):
            line = text[:m.start()].count("\n") + 1
            findings.append(
                "INK: %s:%d declares print-color-adjust. The clause is that a drawing "
                "which needs the reader's ink is a drawing that does not work."
                % (path.relative_to(ROOT), line))

    # 4. The page box.
    base = css[DS / "assets/css/base.css"]
    page = re.search(r"@page\s*\{(.*?)\}", base, re.S)
    if not page:
        findings.append("PAGE BOX: base.css declares no @page rule, so the sheet's margin "
                        "is the browser's default plus --gutter on top of it.")
    else:
        margin = re.search(r"margin\s*:\s*([^;]+);", page.group(1))
        if not margin:
            findings.append("PAGE BOX: @page declares no margin.")
        elif not all(u.endswith("mm") for u in margin.group(1).split()):
            findings.append(
                "PAGE BOX: @page margin `%s` is not written in mm. A4 is 210x297 and "
                "US Letter 216x279; only mm is the same margin on both."
                % margin.group(1).strip())

    if findings:
        print("check-print-law: %d finding(s)\n" % len(findings))
        for f in findings:
            print("  - %s\n" % f)
        return 1

    print("check-print-law: %d withdrawn, %d protected from the cut, %d headings that "
          "cannot be stranded, no ink asked for, page box in mm."
          % (len(withdrawn - EXEMPT_WITHDRAWN), len(uncut), len(unstranded)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
