#!/usr/bin/env python3
"""Every control in the field family is accounted for in the family's shared rules.

components.css draws four controls with the .cf-field__* prefix — input, textarea,
select and file — and states what they have in common in SELECTOR LISTS written by
hand. That is the failure shape this directory already knows by name three times
over: check-wrap-net.py exists because base.css's overflow-wrap list named the
elements that MEAN text rather than the ones that HOLD it, check-focus-ring.py
because the ring's list named the things a person thinks of as controls and
<summary> is not one of them, and check-fluid-record.py for the same reason again.

It had happened twice more here, in one component, and neither was visible in a
screenshot of a page nobody was tabbing through:

  the [disabled] rule    named input, textarea and select. A disabled file field
                         kept a SOLID 1 px line where the other three drop to the
                         2-1 gradient the presence ladder reserves for "here, and
                         not available", and kept `cursor: default` where the
                         other three say `not-allowed`. Its ink was the only part
                         that matched, and by coincidence — .cf-field__file sets
                         --text-secondary at rest, so the one property that looked
                         right was the one this rule was not supplying.

  the :focus rule        named all four, and the file field was the one that did
                         not belong. The rule turns the global ring off because
                         the line thickens to 2 px instead, which speaks for a
                         control whose line IS the control, with the caret on it.
                         A file field has a line and no caret: what a reader
                         operates is the button at the far left. Measured on
                         patterns/bewerbung.html at 1280, at rest against a real
                         Tab onto it, 655 pixels changed and every one of them lay
                         in a single 655 x 1 row at the bottom edge — none on the
                         button. WCAG 2.4.11 asks for the area of a 2 px perimeter
                         of the component and 3:1 against its unfocused state.

So the two directions of the same defect: a control missing from a list it
belongs in, and a control sitting in a list it does not. Both are silent, and
both are settled by asking the question in one place rather than by eye.

WHAT IS ASSERTED. For each of the four shared rules below, the set of control
classes in its selector list equals the expected set exactly. A control that is
deliberately outside a rule is named in EXEMPT with the reason, so the omission
has to be written down rather than merely happen — which is the whole difference
between this file's two findings and the fixes for them.

This does not assert anything about what the rules DECLARE. Adding a fifth
control to the family is meant to fail this check: that is the point.

Usage:
    check-field-family.py       fail if any list is short, long, or undeclared
    check-field-family.py -v    print every rule and its membership
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "design-system" / "assets" / "css" / "components.css"

CONTROLS = ("input", "textarea", "select", "file")

# Each shared rule, found by a property in its body that only that rule declares
# for this family, plus the control classes its selector list must name.
#
# The signature is matched against the rule's DECLARATIONS and the anchor against
# its SELECTOR, so neither a comment nor a neighbouring rule can be mistaken for
# one of these four.
RULES = {
    "base": {
        "anchor": r"\.cf-field__input\s*,",
        "signature": "border-bottom: var(--stroke-1) solid var(--border-strong)",
        "expect": set(CONTROLS),
        "why": "the shared drawing: full width, transparent plate, one hairline under it",
    },
    "focus": {
        "anchor": r"\.cf-field__input:focus",
        "signature": "border-bottom-width: var(--stroke-2)",
        "expect": {"input", "textarea", "select"},
        "why": "the line thickens instead of the global ring, for controls the line speaks for",
    },
    "disabled": {
        "anchor": r"\.cf-field__input\[disabled\]",
        "signature": "cursor: not-allowed",
        "expect": set(CONTROLS),
        "why": "rung 2 of the presence ladder — here, and not available",
    },
    "invalid": {
        "anchor": r"\.cf-field--invalid",
        "signature": "border-bottom-color: var(--feedback-error)",
        "expect": set(CONTROLS),
        "why": "the line goes to --feedback-error on every control alike",
    },
}

# A control outside a rule it would otherwise join, and the reason it is outside.
# Keyed by (rule, control). Being in here is what makes an omission deliberate.
EXEMPT = {
    ("focus", "file"): (
        "keeps base.css's global :focus-visible ring. Its line is not where the "
        "control is — the button is — so a line that thickens indicates nothing. "
        "The read-only field is the first case of the same exception."
    ),
}


def rules(css):
    """(selector, body) for every rule in the file, comments stripped."""
    code = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    # Top-level and nested alike: any "<selector> { <declarations> }" whose body
    # holds no further brace. That reaches inside @media without parsing it.
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", code):
        yield m.group(1).strip(), m.group(2)


def main():
    verbose = "-v" in sys.argv
    if not CSS.exists():
        print(f"check-field-family: {CSS} not found", file=sys.stderr)
        return 1
    css = CSS.read_text(encoding="utf-8")

    failures = []
    for name, spec in RULES.items():
        found = None
        for selector, body in rules(css):
            if not re.search(spec["anchor"], selector):
                continue
            if spec["signature"] not in body:
                continue
            found = selector
            break

        if found is None:
            failures.append(
                f"{name}: no rule found whose selector matches {spec['anchor']!r} "
                f"and whose body declares {spec['signature']!r}.\n"
                f"    That rule is {spec['why']}. If it was renamed or its\n"
                f"    declarations changed, update RULES in this script — the\n"
                f"    check cannot police a list it can no longer find."
            )
            continue

        present = {c for c in CONTROLS if f".cf-field__{c}" in found}
        expect = set(spec["expect"])

        if verbose:
            print(f"{name:9s} {' '.join(sorted(present)) or '(none)'}")

        for control in sorted(expect - present):
            failures.append(
                f"{name}: .cf-field__{control} is missing from the selector list.\n"
                f"    This rule is {spec['why']}.\n"
                f"    Add it, or add ({name!r}, {control!r}) to EXEMPT in this\n"
                f"    script with the reason it stands outside."
            )
        for control in sorted(present - expect):
            key = (name, control)
            if key in EXEMPT:
                failures.append(
                    f"{name}: .cf-field__{control} is in the selector list AND in\n"
                    f"    EXEMPT, which cannot both be true. EXEMPT says:\n"
                    f"    {EXEMPT[key]}"
                )
            else:
                failures.append(
                    f"{name}: .cf-field__{control} is in the selector list and is\n"
                    f"    not expected there. This rule is {spec['why']}.\n"
                    f"    Remove it, or add {control!r} to this rule's `expect`."
                )

    # An exemption for a control that is no longer in the family, or for a rule
    # that no longer exists, is a note about a decision nobody can act on.
    for (name, control), reason in sorted(EXEMPT.items()):
        if name not in RULES:
            failures.append(f"EXEMPT names rule {name!r}, which is not in RULES.")
        elif control not in CONTROLS:
            failures.append(f"EXEMPT names control {control!r}, which is not in the family.")
        elif control in RULES[name]["expect"]:
            failures.append(
                f"EXEMPT names ({name!r}, {control!r}), but that rule expects it.\n"
                f"    An exemption and an expectation cannot both stand."
            )

    if failures:
        print("check-field-family: the family's shared lists and its controls disagree.\n")
        for f in failures:
            print("  " + f + "\n")
        return 1

    print(
        f"check-field-family: {len(RULES)} shared rules, "
        f"{len(CONTROLS)} controls, {len(EXEMPT)} declared exemption(s) — all accounted for."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
