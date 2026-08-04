#!/usr/bin/env python3
"""A tier that cannot sequence two moments of one drawing may not draw both.

WHAT THE ACT IS. Act 1 of patterns/landing-page.html is a sensor field: a
sliced 1600 x 900 backdrop of beads (.sp-field) and twenty-one callouts naming
their readings (.sp-annots-fig). Act 1c converges every bead onto the trunk's
head. Act 2 is what is left when they have arrived — the root, drawn from that
head down, with the field gone. They are not two drawings on one stage. They are
ONE drawing at two moments, and the pinned tier can show both because it has
three hundred vh of scroll to put between them.

WHAT SHIPPED. Every tier that does not pin — no scroll-driven animations,
reduced motion, or a viewport under the gate's own thresholds — drew the lot at
rest, in the same pixels: the finished root, the field that becomes it, and the
callouts that name the field. Reported from a Firefox window as "the tree and
sensors are totally mashed and mixed up". Measured on the shipped render,
objects of act 1 standing inside the root's own box:

    1850 x 950   5 beads, 4 leaders (2 crossing a branch), labels S01/S05/S02
     390 x 844   2 beads, label "S03 30.7 A" over the canopy

Firefox is in that tier at every width — it has no scroll-driven animations, so
it never enters the gate — and so is any reader who asks for less motion, on any
engine. Nothing rendered wrong. Both layers were exactly where they belong; the
tier simply has no way to say "and then".

WHAT IS HELD, read out of the shipping stylesheet:

  1. THE WITHDRAWAL. Act 1's ink layers resolve to `display: none` in the
     UNCONDITIONAL cascade — outside every @media, @supports and @container,
     not just outside the pin gate — and the last unconditional `display` each
     one is given is that `none`. A withdrawal a later rule quietly overrides
     is not one, and neither is a `none` that only applies somewhere: the
     `@media print` rule on .sp-annots-fig (the blank-raster guard, stated
     ~110 lines above the withdrawal) would otherwise satisfy this clause
     while every screen flow tier drew all twenty-one callouts again.
  2. THE RESTORATION. The same set of layers, exactly, is given a display that
     is not `none` inside the pin gate. Withdrawing two and restoring one is
     the shape this check exists to catch, so the two sets are compared rather
     than each being looked for on its own.
  3. THE LATER MOMENT SURVIVES. Nothing ungated withdraws the root, its numeral
     layer or the lattice ground. The rule is "draw one moment", not "draw
     nothing": a tier that drops act 1's ink and act 2's drawing has no figure
     at all, which is a worse fault than the one being fixed and is one edit
     away from it.
  4. THE GATE IS THE ONE THE ACTS RUN ON. The restoration must sit inside the
     `@supports (animation-timeline: view()) and (animation-range: …)` block —
     not a media query that happens to agree with it today. The tier that can
     sequence the moments is defined by whether the timeline resolves, and
     nothing else is allowed to stand in for it.

  5. THE MIRROR. A flow-only layer (.lp-flow-sources — the static telling of
     act 1's subject, one bead per canopy entry) must be withdrawn INSIDE the
     gate, where the real field plays that part, and must render somewhere
     outside it, or the layer the flow tier's story rests on is dead weight.
     Same shape as (1)+(2), the other way round.

stdlib only, no build step, no dependency — the same contract as the checks
beside it.

    python3 scripts/check-act-moment.py       # check, exit 1 on a finding
    python3 scripts/check-act-moment.py -v    # print every display each layer is given
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ACTS = ROOT / "design-system" / "assets" / "css" / "acts.css"

# Act 1's ink: the field of beads and the callout layer that names it.
ACT_ONE_INK = [".sp-field", ".sp-annots-fig"]
# The flow tier's own telling: layers that exist BECAUSE the tier cannot
# sequence the acts, and that must therefore leave when the acts play. The
# mirror of ACT_ONE_INK: drawn outside the gate, withdrawn inside it.
FLOW_ONLY = [".lp-flow-sources"]
# Act 2's drawing, its numerals, and the ground all three tiers stand on.
MUST_SURVIVE = [".lp-flow", ".lp-flow-data", ".sp-drawing", ".sp-stage", ".cf-ground"]

GATE = re.compile(
    r"@supports\s*\(\s*animation-timeline:\s*view\(\)\s*\)\s*and\s*"
    r"\(\s*animation-range:")


def strip_comments(text):
    """Blank out comments, keeping every byte offset intact."""
    out = list(text)
    for m in re.finditer(r"/\*.*?\*/", text, flags=re.S):
        for i in range(m.start(), m.end()):
            if out[i] != "\n":
                out[i] = " "
    return "".join(out)


def block_spans(text, starts):
    """(start, end) for each at-rule start offset, braces balanced."""
    spans = []
    for start in starts:
        i = text.find("{", start)
        if i < 0:
            continue
        depth = 0
        for j in range(i, len(text)):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    spans.append((start, j))
                    break
    return spans


def gate_spans(text):
    """(start, end) of every scroll-driven @supports block."""
    return block_spans(text, [m.start() for m in GATE.finditer(text)])


def conditional_spans(text):
    """(start, end) of EVERY conditional group rule — @media, @supports,
    @container. A declaration inside any of these is conditional on something,
    and 'withdrawn outside the pin gate' means withdrawn UNCONDITIONALLY: the
    first shipped guard counted the pre-existing `@media print` none on
    .sp-annots-fig as the withdrawal, so dropping the layer from the screen
    withdrawal kept this check green while every screen flow tier drew all
    twenty-one callouts again — the reported fault, half-returned, with CI
    passing. Found by the rebase review, proven live before this function
    existed."""
    starts = [m.start() for m in
              re.finditer(r"@(?:media|supports|container)\b", text)]
    return block_spans(text, starts)


def display_rules(text, gated_spans, cond_spans):
    """Every `display` declaration: (selector, value, offset, kind).

    kind is 'gated' inside a pin-gate @supports block, 'plain' inside no
    conditional at-rule at all, and 'other' inside some other conditional
    (@media print, a stray @container) — 'other' is NEITHER a withdrawal NOR
    a restoration; it is invisible to both clauses on purpose."""
    found = []
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", text):
        selector, body = m.group(1), m.group(2)
        # The selector runs back to the previous } or {; keep the last line-ish
        selector = selector.strip()
        if not selector or selector.startswith("@"):
            continue
        for d in re.finditer(r"(?<![-\w])display\s*:\s*([a-zA-Z-]+)", body):
            off = m.start(2) + d.start()
            if any(s <= off <= e for s, e in gated_spans):
                kind = "gated"
            elif any(s <= off <= e for s, e in cond_spans):
                kind = "other"
            else:
                kind = "plain"
            for part in [p.strip() for p in selector.split(",")]:
                part = part.split("\n")[-1].strip()
                found.append((part, d.group(1), off, kind))
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    raw = ACTS.read_text(encoding="utf-8")
    text = strip_comments(raw)
    spans = gate_spans(text)
    findings = []

    if not spans:
        print("act-moment: 1 finding")
        print("  - acts.css has no `@supports (animation-timeline: view()) and "
              "(animation-range: …)` block. The tier that can sequence the two "
              "moments is defined by that gate; without it there is nothing to "
              "hold the restoration to.")
        return 1

    rules = display_rules(text, spans, conditional_spans(text))

    withdrawn, restored = set(), set()
    for layer in ACT_ONE_INK:
        mine = [r for r in rules if r[0] == layer]
        # 'plain' only: a none inside @media print (or any other conditional)
        # is not a withdrawal — see conditional_spans' own docstring for the
        # half-revert that counting it would wave through.
        plain = sorted([r for r in mine if r[3] == "plain"], key=lambda r: r[2])
        gated = [r for r in mine if r[3] == "gated"]
        if args.verbose:
            print("  %-16s plain %-24s gated %-18s other %s"
                  % (layer,
                     ", ".join("%s@%d" % (v, o) for _, v, o, _ in plain) or "-",
                     ", ".join("%s@%d" % (v, o) for _, v, o, _ in gated) or "-",
                     ", ".join("%s@%d" % (v, o) for _, v, o, k in mine
                               if k == "other") or "-"))
        if not plain:
            findings.append(
                "%s is never given an unconditional `display` outside the pin "
                "gate — a `none` inside @media print or another conditional "
                "does not count — so act 1's ink is drawn in the screen tier "
                "that also draws act 2's root: the double exposure at the head "
                "of this file." % layer)
        elif plain[-1][1] != "none":
            findings.append(
                "%s resolves to `display: %s` outside the pin gate (the last "
                "unconditional declaration, at offset %d). Act 1's ink has to "
                "be withdrawn where the tier cannot sequence it."
                % (layer, plain[-1][1], plain[-1][2]))
        else:
            withdrawn.add(layer)
        if any(v != "none" for _, v, _, _ in gated):
            restored.add(layer)
        # The mirror of FLOW_ONLY's order clause: the gated restoration must
        # stand LATER than the unconditional withdrawal it overrides, or the
        # pinned tier inherits the flow tier's none and act 1 is deleted.
        restores = [o for _, v, o, _ in gated if v != "none"]
        plain_nones = [o for _, v, o, _ in plain if v == "none"]
        if restores and plain_nones and max(plain_nones) > max(restores):
            findings.append(
                "%s's withdrawal (offset %d) stands after the gated "
                "restoration (offset %d) that must beat it. Same specificity, "
                "so the later rule wins and the pinned tier loses act 1's "
                "ink. Keep the withdrawal before the gate."
                % (layer, max(plain_nones), max(restores)))

    if withdrawn and withdrawn != restored:
        for layer in sorted(withdrawn - restored):
            findings.append(
                "%s is withdrawn outside the pin gate and never restored inside "
                "it. The pinned tier is the one tier that can put time between "
                "the two moments; withdrawing the layer there as well deletes "
                "act 1." % layer)
        for layer in sorted(restored - withdrawn):
            findings.append(
                "%s is restored inside the pin gate but not withdrawn outside "
                "it. The two sets have to match: withdrawing one layer and "
                "restoring two leaves the tier drawing half of act 1 over act "
                "2's root." % layer)

    # The mirror clause. A flow-only layer is the tier's own telling of the
    # story the acts tell in time; when the acts play, it has to leave, or the
    # pinned tier carries a third telling over act 2's ending — the double
    # exposure again, built the other way round. And it has to actually SHOW
    # somewhere outside the gate, or the layer is dead weight the next tidy
    # deletes along with the argument for it.
    for layer in FLOW_ONLY:
        mine = [r for r in rules if r[0] == layer]
        gated = [r for r in mine if r[3] == "gated"]
        outside = [r for r in mine if r[3] != "gated"]
        if args.verbose:
            print("  %-16s outside %-22s gated %s"
                  % (layer,
                     ", ".join("%s@%d" % (v, o) for _, v, o, _ in outside) or "-",
                     ", ".join("%s@%d" % (v, o) for _, v, o, _ in gated) or "-"))
        if not any(v == "none" for _, v, _, _ in gated):
            findings.append(
                "%s is never withdrawn inside the pin gate. It is the flow "
                "tier's telling of act 1; in the pinned tier the real field "
                "plays that part, and both at once is the double exposure "
                "built the other way round." % layer)
        if not any(v != "none" for _, v, _, _ in outside):
            findings.append(
                "%s is never given a visible display outside the pin gate — "
                "the layer the flow tier's story rests on renders nowhere."
                % layer)
        # THE ORDER IS THE CASCADE. Every rule here is one class at (0,1,0),
        # so source order is the whole decision, and a withdrawal that stands
        # EARLIER than a conditional non-none it is supposed to beat is not a
        # withdrawal — the container rule re-shows the layer inside the gate.
        # Found by adversarial mutation of the shipped file: moving the
        # @container block after the @supports block flipped the pinned tier
        # back to the double exposure while both checks stayed green.
        gated_nones = [o for _, v, o, _ in gated if v == "none"]
        shown_outside = [o for _, v, o, _ in outside if v != "none"]
        if gated_nones and shown_outside and max(shown_outside) > max(gated_nones):
            findings.append(
                "%s's gated withdrawal (offset %d) stands before a visible "
                "display it must beat (offset %d). Same specificity, so the "
                "later rule wins and the pinned tier draws the layer over the "
                "acts. Keep the gate after every rule that shows the layer."
                % (layer, max(gated_nones), max(shown_outside)))

    for layer in MUST_SURVIVE:
        killed = [r for r in rules
                  if r[0] == layer and r[3] == "plain" and r[1] == "none"]
        if killed:
            findings.append(
                "%s is set to `display: none` outside the pin gate (offset %d). "
                "The rule is draw ONE moment, not none: the tier keeps act 2's "
                "root, its numerals and the ground it stands on."
                % (layer, killed[0][2]))

    if findings:
        print("act-moment: %d finding%s"
              % (len(findings), "" if len(findings) == 1 else "s"))
        for f in findings:
            print("  - " + f)
        return 1

    print("act-moment OK — act 1's %d ink layers are withdrawn outside the pin "
          "gate and restored inside it, %d flow-only layer%s withdrawn inside "
          "it, and act 2's drawing, numerals and ground survive in every "
          "tier." % (len(ACT_ONE_INK), len(FLOW_ONLY),
                     "" if len(FLOW_ONLY) == 1 else "s"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
