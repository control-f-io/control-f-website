#!/usr/bin/env python3
"""Hold every bounded key label to the same wrap opt-out, or flag the one that isn't.

A "bounded key" is this system's name for a label absolutely positioned under a
data point and confined to that point's own pitch — .cf-block__key's own comment
states the shape and the reason it cannot use base.css's global
`overflow-wrap: break-word` net: the box is narrow (32 px at 375 px on a
--plot-u*2 column), so the net does not make an overlong word wrap tidily, it
cuts it. A word cut at the box edge is worse than one that overhangs it, and
the key is absolutely positioned so an overhang costs the layout nothing — it
contributes no min-content to any track. The fix is two declarations together:
`overflow-wrap: normal` takes the net off, and `hyphens: manual` puts back only
the breaks the author placed with `&shy;`.

.cf-plot__key is the same shape — position: absolute, no white-space: nowrap,
a label under a data point, bound to its column — and shipped without either
declaration. At 375 px it cut "Abtastung" to ABTA/STUN/G, a three-line key
whose orphaned final letter overlapped the caption below it on
patterns/blog-artikel.html, and it left two authored &shy; entries elsewhere
on components/plot.html ("Verfüg&shy;barkeit", "Lebens&shy;dauer") inert,
since hyphens: manual is what makes a soft hyphen a break point instead of a
no-op. Fixed by giving .cf-plot__key the same two declarations
.cf-block__key already carries.

WHAT THIS SCRIPT CHECKS

Every rule in components.css whose selector is a single class ending in
`__key` (the primary definition, not a modifier like
`.cf-line__point--first :is(..., .cf-line__key)`) is one of three shapes:

  grid-track key     no `position: absolute` — sized by its track, covered by
                      base.css's net like any other text in a flexible column
                      (.cf-gantt__key). Not this script's subject.
  point key          `position: absolute` and `white-space: nowrap` — a label
                      on a continuous domain with no width of its own, meant
                      to overhang by default (.cf-line__key, documented on the
                      rule itself). Not this script's subject.
  bounded key        `position: absolute`, no `white-space: nowrap` — confined
                      to a real pitch (.cf-plot__key, .cf-block__key). MUST
                      declare both `overflow-wrap: normal` and
                      `hyphens: manual`, or a compound word breaks inside its
                      own box instead of overhanging it.

SCOPE

  design-system/assets/css/components.css   the one file every `__key` class
                                             the system ships is defined in.
                                             A future bounded key defined
                                             anywhere else is invisible to
                                             this script — there is none today.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-bound-key-wrap.py       # check, exit 1 on a finding
    python3 scripts/check-bound-key-wrap.py -v    # list every __key rule found
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system" / "assets" / "css" / "components.css"

KEY_SELECTOR = re.compile(r"^\.[A-Za-z0-9_-]+__key$")
ABSOLUTE = re.compile(r"position\s*:\s*absolute\b")
NOWRAP = re.compile(r"white-space\s*:\s*nowrap\b")
WRAP_NORMAL = re.compile(r"overflow-wrap\s*:\s*normal\b")
HYPHENS_MANUAL = re.compile(r"hyphens\s*:\s*manual\b")


def rules(text):
    """(selector, body) for every rule, comments stripped first."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    for m in re.finditer(r"([^{}]*)\{([^{}]*)\}", text):
        sel = " ".join(m.group(1).split())
        if sel and not sel.startswith("@"):
            yield sel, m.group(2)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    text = CSS.read_text(encoding="utf-8")
    findings = []
    seen = []

    for sel, body in rules(text):
        if not KEY_SELECTOR.fullmatch(sel):
            continue
        if not ABSOLUTE.search(body):
            kind = "grid-track"
        elif NOWRAP.search(body):
            kind = "point"
        else:
            kind = "bounded"
        seen.append((sel, kind))
        if kind != "bounded":
            continue
        ok = WRAP_NORMAL.search(body) and HYPHENS_MANUAL.search(body)
        if not ok:
            missing = []
            if not WRAP_NORMAL.search(body):
                missing.append("overflow-wrap: normal")
            if not HYPHENS_MANUAL.search(body):
                missing.append("hyphens: manual")
            findings.append((sel, missing))

    if args.verbose:
        print(f"{len(seen)} __key rule(s) in {CSS.relative_to(ROOT)}:")
        for sel, kind in seen:
            print(f"  {sel:<28} {kind}")

    if not seen:
        print("FAIL  no __key rule found in components.css — the pattern this "
              "script checks is gone, not merely unbroken.")
        return 1

    if findings:
        print(f"FAIL  {len(findings)} bounded key(s) can break a compound word "
              f"inside their own box instead of overhanging it:\n")
        for sel, missing in findings:
            print(f"  {sel}  missing {', '.join(missing)}")
        print("\n  A bounded key is position: absolute and confined to its point's own")
        print("  pitch — base.css's overflow-wrap net cuts an overlong word there instead")
        print("  of wrapping it tidily. Give it overflow-wrap: normal and hyphens: manual,")
        print("  the same pair .cf-block__key carries, and its long comment explains why.")
        return 1

    bounded = sum(1 for _, kind in seen if kind == "bounded")
    print(f"OK    {len(seen)} __key rule(s) in components.css, {bounded} of them bounded "
          f"and each opting out of the net with overflow-wrap: normal; hyphens: manual.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
