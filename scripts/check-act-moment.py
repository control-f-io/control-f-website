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

Firefox is in that tier at every width — Gecko implements scroll-driven
animations behind `layout.css.scroll-driven-animations.enabled` and 154.0 ships
with the pref OFF, so it never enters the gate — and so is any reader who asks
for less motion, on any engine. Nothing rendered wrong. Both layers were exactly
where they belong; the tier simply has no way to say "and then".

AND ONE OF THOSE TIERS FOUND A WAY, WHICH IS WHY THE HEADLINE ABOVE IS NOT THE
WHOLE RULE ANY MORE. "May not draw both" was always shorthand for "may not draw
both IN THE SAME PIXELS": the fault is a double exposure, not a head count. The
tiers outside the gate are two, not one, and they are not alike —

  THE NO-SUPPORT TIER has no axis at all, and it was reading as "not only the
  tree": act 1's claim beside act 2's finished root, three beats of a scroll
  composition arriving as one block, for every Firefox reader at every width.
  acts.css sequences the acts there in SPACE instead — act 1's field takes a
  band of its own at the head of the stage, the claim stands under it, the root
  under that. Both moments are drawn and neither is in the other's pixels.

  THE FLOW TIER has a time axis and spent it on act 2 alone: the root built as
  the reader passed it, .lp-flow-sources stood in for act 1, and the withdrawal
  below was called exactly right for it. It was not. The stand-in is gated at a
  30rem container and a phone's drawing is 347px, so an iPhone got act 2 growing
  out of blank ground — no field, no callouts, no stand-in, measured all three
  `display: none` at 390 x 844 in WebKit 26.5. That tier takes the no-support
  tier's band as well now, and puts the arrival, the pulse and the convergence
  back on top of it: two subjects, two view timelines, and the page's own order
  between them. Both moments drawn, neither in the other's pixels, and the
  "and then" said in space AND in time.

  THE REDUCED-MOTION TIER above 64rem x 45rem is the one that is still bound by
  the rule as written: it can resolve a timeline and may not be given one, and
  neither band's prelude covers its width. .lp-flow-sources is its stand-in and
  now its only home, which is what clause 5 below is measuring.

So the withdrawal clause below is unchanged and still unconditional — a `none`
that a LATER conditional tier lifts on purpose is still a withdrawal, and the
flow tier still inherits it — and clause 6 is what holds the tier that lifts it.
The geometry of the band is check-ground-band.py's `band, not fit` clause; what
is held here is that lifting it is all-or-nothing and that the tier's own
stand-in leaves when the real field arrives.

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
  6. THE TIER THAT SEQUENCES IN SPACE. If the `@supports not (…)` block — the
     tier with no timeline — lifts the withdrawal for one of act 1's ink
     layers, it lifts it for BOTH, and .lp-flow-sources leaves there too. Half
     of act 1 is the fault of clause (2) one tier along: the callouts without
     the beads point at nothing, the beads without the callouts are unnamed
     dots. And the canopy's stand-in row standing under a real field is the
     third telling clause (5) exists to stop, arriving through the second
     door. The cascade order is checked with it: both rules have to stand
     after the ones they override.

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
# The gate's negation — the tier with no timeline at all, which is where every
# Firefox reader is and where the acts are sequenced in space. Its own block and
# not "outside the gate": the flow tier is outside the gate too and is a
# different tier with a different answer.
NO_SUPPORT = re.compile(
    r"@supports\s+not\s*\(\s*\(\s*animation-timeline\s*:\s*view\(\s*\)\s*\)")


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


def no_support_spans(text):
    """(start, end) of every `@supports not (…)` block for that same gate."""
    return block_spans(text, [m.start() for m in NO_SUPPORT.finditer(text)])


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

    # Clause 6. The tier with no timeline may lift the withdrawal, because it
    # sequences the two moments in space instead of in time — but it lifts it
    # for the whole picture or for none of it, and its own stand-in has to
    # leave, for the reasons the gate's restoration gives one line from its own.
    fb = no_support_spans(text)

    def in_fallback(off):
        return any(s <= off <= e for s, e in fb)

    lifted = {layer for layer in ACT_ONE_INK
              if any(v != "none" for sel, v, o, _ in rules
                     if sel == layer and in_fallback(o))}
    if lifted:
        for layer in sorted(set(ACT_ONE_INK) - lifted):
            findings.append(
                "%s is not drawn in the `@supports not (…)` tier, which draws "
                "%s. Half of act 1 is the double exposure's own fault one tier "
                "along: the callouts without their beads point at nothing, the "
                "beads without their callouts are unnamed dots."
                % (layer, ", ".join(sorted(lifted))))
        for layer in sorted(lifted):
            mine = [r for r in rules if r[0] == layer]
            plain_nones = [o for _, v, o, k in mine if k == "plain" and v == "none"]
            shown_fb = [o for _, v, o, _ in mine if v != "none" and in_fallback(o)]
            if plain_nones and shown_fb and max(plain_nones) > max(shown_fb):
                findings.append(
                    "%s's unconditional withdrawal (offset %d) stands after the "
                    "no-support tier's restoration (offset %d) that must beat "
                    "it. Same specificity, so the later rule wins and the tier "
                    "loses act 1 again." % (layer, max(plain_nones), max(shown_fb)))
        for layer in FLOW_ONLY:
            mine = [r for r in rules if r[0] == layer]
            fb_nones = [o for _, v, o, _ in mine if v == "none" and in_fallback(o)]
            shown = [o for _, v, o, _ in mine if v != "none" and not in_fallback(o)]
            if not fb_nones:
                findings.append(
                    "%s is never withdrawn in the `@supports not (…)` tier, "
                    "which now draws act 1's real field. One bead per canopy "
                    "entry standing on the finished root under a field that has "
                    "just been drawn is the third telling clause 5 exists to "
                    "stop, arriving through the second door." % layer)
            elif shown and max(shown) > max(fb_nones):
                findings.append(
                    "%s's no-support withdrawal (offset %d) stands before a "
                    "visible display it must beat (offset %d). Same "
                    "specificity, so the later rule wins."
                    % (layer, max(fb_nones), max(shown)))

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

    print("act-moment OK — act 1's %d ink layers are withdrawn unconditionally "
          "and restored in the pin gate%s, %d flow-only layer%s withdrawn "
          "wherever the real field plays, and act 2's drawing, numerals and "
          "ground survive in every tier."
          % (len(ACT_ONE_INK),
             " and in the no-support tier that sequences them in space"
             if lifted else "",
             len(FLOW_ONLY), "" if len(FLOW_ONLY) == 1 else "s"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
