#!/usr/bin/env python3
"""A container-query unit is read where it is declared, or Firefox keeps a stale one.

WHAT THIS EXISTS FOR. The sensor field on patterns/landing-page.html is an SVG
sliced over the stage, and its twenty-one notes are HTML beside it. The layer
converts one to the other with a single number:

    .sp-annots { --sp-u: max(1cqw / 16, 1cqh / 9); }

which is `xMidYMid slice`'s own scale — max(box width / 1600, box height / 900)
— as a CSS length, so a note can be placed at a crossing's own position with
nothing measuring anything at runtime. acts.css argues the whole construction
where it is declared; this check holds the one thing that argument depends on
and cannot state in CSS.

THE FAULT. Gecko resolves the cq units in --sp-u once, against the stage's
height in an EARLIER layout pass — the stage still stacked, before
`@container (min-width: 56rem)` folds .cf-statement into two columns and takes
about 390 px out of it — and never resolves them again. The layer is then laid
out at a scale the field is not sliced at, and because the scale multiplies a
crossing's distance from the centre, the error grows with it. Measured on the
shipped page, Firefox 153, flow tier, all 21 notes wrong at every desktop width:

                  u used   u correct   worst note   labels cut by the frame
     1024 x 768   1.1428     0.8433      218.9 px    10 of 21   (7 after)
     1280 x 800   1.2359     0.9242      227.8       10         (3 after)
     1440 x 900   1.3167     0.9         304.6        9         (0 after)
     1920 x 1080  1.3167     1.2          85.3        0         (0 after)

Firefox is the only engine in that tier — it has no scroll-driven animations, so
it never enters the pinned gate — which is why a fault this size could sit on
the flagship page's first act unseen. Chromium and WebKit re-resolve and are
correct with or without the fix, to the pixel, at every width measured.

THE FIX IS ONE DECLARATION AND IT LOOKS LIKE A DUPLICATE. .sp-annots — the
element that declares --sp-u — carries `container-type: size` of its own, so the
notes read their units off the box their number is written on rather than off
their grandparent. The two boxes are THE SAME BOX: .sp-annots-fig is
`position: absolute; inset: 0` of the stage and the list is `position: absolute;
inset: 0` of the fig, so no number can change, and none does. That is exactly
why the declaration is at risk from a reader tidying the sheet: it is inert in
two of the three engines and identical in the third once it is there.

WHAT THIS HOLDS, all of it read out of the shipping stylesheets:

  1. Both boxes declare `container-type: size` — the fig, so the units are the
     stage's box in every tier (acts.css's own argument), and the list, so
     Gecko re-reads them.
  2. Both are `position: absolute` with `inset: 0`, which is the equivalence the
     second declaration rests on. Lose it and the list is a different box from
     the fig, the second container silently re-scales all twenty-one notes, and
     this check has to be re-argued rather than passed.
  3. THE REGISTER. Every rule in the shipped CSS that writes a container-query
     unit into a custom property is named here with what it reads and why it is
     or is not held to (1). A third one appearing is a finding, because the
     failure it would inherit is invisible in two engines and silent in the
     third — nothing else in this directory would say a word.

    python3 scripts/check-annot-container.py       # check, exit 1 on a finding
    python3 scripts/check-annot-container.py -v    # print the register and the boxes
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
SHIPPING = [
    DS / "assets" / "css" / "tokens.css",
    DS / "assets" / "css" / "base.css",
    DS / "assets" / "css" / "components.css",
    DS / "assets" / "css" / "acts.css",
]

PAGE = DS / "patterns" / "landing-page.html"

CQ_UNIT = re.compile(r"\d\s*cq(?:w|h|i|b|min|max)\b")
CUSTOM_PROP = re.compile(r"(--[A-Za-z0-9_-]+)\s*:\s*([^;{}]*);")

# The register. Selector -> (what it reads, held to rule 1?, why.)
REGISTER = {
    ".sp-annots": (
        "max(1cqw / 16, 1cqh / 9) — the stage's slice scale, read off the "
        "stage's own box",
        True,
        "the box moves under it: the stage's height changes when the "
        "statement folds, which is the pass Gecko keeps",
    ),
    ".cf-annot-set": (
        "clamp(0.875rem, 3.2cqi, 1.75rem) — a leader length, read off the "
        "drawing's width",
        False,
        "the component's own layer, which goes `position: static` in legend "
        "mode below 28rem — size containment there would collapse a flex row "
        "whose height is its content. It reads an inline size that no fold "
        "moves, and it is clamped to 14–28 px, so the fault above is bounded "
        "at 14 px on a leader rather than 300 px on a position",
    ),
    ".lp-flow__src": (
        "clamp(5px, 1cqi, 8px) — a bead diameter, read off sp-root, the "
        "drawing's own inline-size container",
        False,
        "measured clean where .sp-annots was not: real vs appended-clone "
        "computed width identical in pref-off AND pref-on Firefox 153 at "
        "940/960/980/1000 (stacked, slope live), at 1020 (the fold's far "
        "side, sp-root 890 -> 525 in one pass) and at 1850 (cap). The axis "
        "the fold moves IS the container's own inline axis, which Gecko "
        "evidently re-reads; the stale pass kept a *size* container's "
        "height. Bounded at 3 px of diameter either way, not 300 of "
        "position — but re-measure before trusting this row for a new "
        "consumer",
    ),
}

# The two boxes the sensor-note layer is made of, outermost first. Named by the
# class the page carries, not by a selector: the list is `.cf-annot-set
# .sp-annots` and the declarations that make it a box are the component's, so
# what has to be read is the ELEMENT and every class on it.
BOXES = ["sp-annots-fig", "sp-annots"]


def rules(text):
    """(selector, body) for every rule in the sheet, comments stripped."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    out = []
    depth = 0
    buf = []
    sel = []
    for ch in text:
        if ch == "{":
            depth += 1
            if depth == 1:
                sel = "".join(buf).strip()
                buf = []
                continue
        elif ch == "}":
            depth -= 1
            if depth == 0:
                out.append((sel, "".join(buf)))
                buf = []
                continue
        buf.append(ch)
    return out


def classes_on(markup, wanted):
    """Every class on the page's element carrying `wanted`, and its ancestry."""
    stack = []
    for m in re.finditer(r"<(/?)([a-zA-Z][\w-]*)([^>]*?)(/?)>", markup):
        closing, tag, attrs, selfclose = m.groups()
        if closing:
            for i in range(len(stack) - 1, -1, -1):
                if stack[i][0] == tag:
                    del stack[i:]
                    break
            continue
        cm = re.search(r'class="([^"]*)"', attrs)
        node = (tag, set((cm.group(1) if cm else "").split()))
        if wanted in node[1]:
            return node[1], [n[1] for n in stack]
        if not selfclose and tag not in {
                "area", "base", "br", "col", "embed", "hr", "img", "input",
                "link", "meta", "param", "source", "track", "wbr"}:
            stack.append(node)
    return None, None


def declarations(selector, sheets):
    """Every declaration made by rules whose selector list names `selector`."""
    found = {}
    for name, text in sheets:
        for sel, body in rules(text):
            parts = [s.strip() for s in sel.split(",")]
            if selector not in parts:
                # A nested rule inside @media/@supports arrives here as the
                # whole block; recurse one level so a gated declaration counts.
                if "{" in body and selector in body:
                    for inner_sel, inner_body in rules(body):
                        if selector in [s.strip() for s in inner_sel.split(",")]:
                            for prop, val in re.findall(
                                    r"([a-z-]+|--[A-Za-z0-9_-]+)\s*:\s*([^;{}]+)", inner_body):
                                found.setdefault(prop.strip(), []).append(
                                    (name, val.strip()))
                continue
            for prop, val in re.findall(
                    r"([a-z-]+|--[A-Za-z0-9_-]+)\s*:\s*([^;{}]+)", body):
                found.setdefault(prop.strip(), []).append((name, val.strip()))
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    sheets = [(p.name, p.read_text(encoding="utf-8")) for p in SHIPPING]
    findings = []

    # ---- 3. the register, first, because it decides what (1) has to cover ----
    writers = {}
    for name, text in sheets:
        for sel, body in rules(text):
            for prop, val in CUSTOM_PROP.findall(body):
                if CQ_UNIT.search(val):
                    for part in [s.strip() for s in sel.split(",")]:
                        writers.setdefault(part, []).append((name, prop, val.strip()))
            # one level of nesting, same reason as above
            if "{" in body:
                for inner_sel, inner_body in rules(body):
                    for prop, val in CUSTOM_PROP.findall(inner_body):
                        if CQ_UNIT.search(val):
                            for part in [s.strip() for s in inner_sel.split(",")]:
                                writers.setdefault(part, []).append(
                                    (name, prop, val.strip()))

    for sel, wrote in sorted(writers.items()):
        if sel not in REGISTER:
            findings.append(
                "%s writes a container-query unit into %s and is not in this "
                "check's register. Either it reads a box that cannot move "
                "under it — say so here — or it needs the same "
                "`container-type` on the declaring element that .sp-annots "
                "carries, for the reason at the head of this file."
                % (sel, ", ".join(sorted({p for _, p, _ in wrote}))))
    for sel in REGISTER:
        if sel not in writers:
            findings.append(
                "%s is registered here as a writer of container-query units "
                "and no longer writes one. The register is the argument; "
                "retire the entry with the declaration." % sel)

    # ---- 1 and 2. the two boxes of the sensor-note layer ----
    markup = PAGE.read_text(encoding="utf-8")
    for box in BOXES:
        on_element, ancestry = classes_on(markup, box)
        if on_element is None:
            findings.append(
                ".%s is not on any element of %s. The sensor-note layer is "
                "two boxes and this is one of them." % (box, PAGE.name))
            continue
        if box == BOXES[1] and not any(BOXES[0] in a for a in ancestry):
            findings.append(
                ".%s does not stand inside .%s. The second container is only "
                "inert while it is `inset: 0` of the first."
                % (box, BOXES[0]))
        decls = {}
        for cls in sorted(on_element):
            for prop, vals in declarations("." + cls, sheets).items():
                decls.setdefault(prop, []).extend(vals)
        if not decls:
            findings.append(
                ".%s and its element's other classes (%s) declare nothing in "
                "the shipping stylesheets."
                % (box, " ".join(sorted(on_element))))
            continue
        box = "." + box
        ct = [v for _, v in decls.get("container-type", [])]
        if "size" not in ct:
            findings.append(
                "%s does not declare `container-type: size`%s. The layer's "
                "units are the stage's box in every tier because the fig "
                "declares it, and Firefox re-reads them because the list "
                "declares it too — both, or the notes leave their beads in "
                "one engine or in all of them."
                % (box, " (found %s)" % ", ".join(ct) if ct else ""))
        pos = [v for _, v in decls.get("position", [])]
        if "absolute" not in pos:
            findings.append(
                "%s is not `position: absolute` (found %s). The second "
                "container is only inert while the two boxes are the same "
                "box." % (box, ", ".join(pos) or "nothing"))
        inset = [v for _, v in decls.get("inset", [])]
        if not any(v.split()[0] == "0" and len(v.split()) == 1 for v in inset):
            findings.append(
                "%s is not `inset: 0` (found %s). The second container is "
                "only inert while the two boxes are the same box: a list "
                "inset from the fig would re-scale all twenty-one notes "
                "against a box the field is not sliced into."
                % (box, ", ".join(inset) or "nothing"))

    if args.verbose:
        print("  register")
        for sel, (what, held, why) in sorted(REGISTER.items()):
            print("    %-16s %s" % (sel, what))
            print("    %-16s %s — %s"
                  % ("", "held to (1)" if held else "not held to (1)", why))
        print("  boxes")
        for box in BOXES:
            on_element, _ = classes_on(markup, box)
            d = {}
            for cls in sorted(on_element or []):
                for prop, vals in declarations("." + cls, sheets).items():
                    d.setdefault(prop, []).extend(vals)
            print("    %-16s %s" % ("." + box, "; ".join(
                "%s: %s" % (p, d[p][0][1])
                for p in ("position", "inset", "container-type") if p in d)))

    if findings:
        print("annot-container: %d finding%s"
              % (len(findings), "" if len(findings) == 1 else "s"))
        for f in findings:
            print("  - " + f)
        return 1

    print("annot-container OK — %d rules write container-query units into a "
          "custom property, all registered; the sensor-note layer's %d boxes "
          "are the same box and both declare container-type: size."
          % (len(writers), len(BOXES)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
