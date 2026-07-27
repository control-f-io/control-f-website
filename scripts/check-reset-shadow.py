#!/usr/bin/env python3
"""Fail a declaration that a reset in base.css already outweighs.

A RESET WITH AN ATTRIBUTE IN IT IS HEAVIER THAN A CLASS, and this system has
one. base.css:150 reads

    ul[role="list"], ol[role="list"] { list-style: none; margin: 0; padding: 0; }

which is (0,1,1) — one class-column weight for the attribute selector, one
type-column weight for the tag. A single class is (0,1,0). So every rule of
the form `.some-class { margin: ...; }` on a list that carries role="list"
loses, in every stylesheet, at every source position, forever. Nothing about
that is visible: the declaration is spelled correctly, it is the last one
written, the class is on the element, and the property computes to the reset's
value as if the line had never been typed.

IT HAS COST THIS SYSTEM THE SAME ELEMENT TWICE.

components.css's .cf-pin__inner note records the first, and records it as a
lesson learned:

    CENTRED BY justify-self AND NOT BY AUTO MARGINS, which is not a taste.
    `margin-inline: auto` here is (0,1,0) and base.css writes
    `ol[role="list"] { margin: 0 }` at (0,1,1) — so the two cards centred, the
    bar centred, and the index alone stayed flush to the container, which is
    the same bug one element narrower.

The second was one property over, on the same <ol>, and survived that note
being written. patterns/landing-page.html declared

    .lp-proc-index { padding-block-end: var(--space-4); }

under a comment saying "this stage spaces its index and bar a rung further
from the card than the Expertise page does" — and the index's computed
padding-bottom was 0 px at every viewport the page has ever been opened at.
It was invisible for a second reason on top of the first: the pinned stage's
middle row was minmax(0, 1fr), so 21 to 317 px of grid slack sat in that gap
anyway, depending on viewport height. The rung was never the thing making the
space. Removing the slack is what surfaced the dead line — the index came to
rest flush on the card's top edge, which is what `padding-block-end: 0` looks
like when nothing else is padding it.

That is the shape every other script in this directory was written for: a rule
the system states in prose, kept by nearly everything, broken by exactly one
declaration, rendering plausibly the whole time. The lesson was even written
down after the first occurrence, in the file the second occurrence's component
lives in, and the second one happened anyway — because a comment on one
selector cannot see the next selector. Nothing ran.

WHAT IT CHECKS

  the resets      every rule in base.css whose selector carries an ATTRIBUTE
                  and no class. Those are the ones that outweigh a bare class;
                  a plain type selector (0,0,1) does not, and is not read here.
  the shadows     every rule anywhere in the tree — the three shipping
                  stylesheets and every page-local <style> block — whose
                  selector is LIGHTER than a reset that can match the same
                  element, and which sets a property that reset already sets.
  the markup      which classes actually land on an element the reset matches,
                  read out of the HTML rather than assumed. `.cf-nav__list` is
                  on a <ul role="list"> and `.cf-consent__actions` is on a
                  <div>; only the first can be shadowed, and only the markup
                  knows which is which.
  shorthands      expanded both ways. `margin: 0` in the reset shadows
                  `margin-block-end` in the rule, and `padding: 0` shadows
                  `padding-inline`. Physical and logical longhands are the same
                  property for this purpose, because they compute onto the same
                  used value and the cascade resolves them against each other.

  agreement       a shadowed declaration whose VALUE is the reset's own value
                  is a restatement, not a defect. It is counted and printed as
                  a total, never failed.

THE LINE BETWEEN THE TWO IS THE WHOLE OF THIS CHECK'S USEFULNESS, and it was
not obvious. Run against the tree the day it was written, the weight test alone
found 33 shadowed declarations. Thirty of them are `margin: 0`, `padding: 0`
and `list-style: none` written onto a class that is already on a role="list" —
components restating the reset they sit under, in eleven separate blocks. Every
one is dead and not one of them is wrong: they say what the reset says, so the
page renders as the author intended by a route the author did not intend.
Failing those would be failing a style, and a check nobody can get to green is
a check somebody deletes.

The other three ASK FOR SOMETHING THE RESET DENIES, and all three were live
defects, each measured in a browser rather than argued from the cascade:

    .cf-nav__list        padding: var(--space-2)      computed 0px
    .cf-pagination__list margin-inline-start: auto    computed 0px
    .cf-info-card__chips margin-top: var(--space-3)   computed 0px

The nav plate's 8 px inset was gone on every page in the tree, with the pills
flush against its border. The pagination's auto margin is the one the comment
above it exists to justify — "without a status line there is only one flex
child, and space-between would park it on the left" — and it parked on the
left. The chips sat flush under their label. Three components, none of them
adjacent, all rendering plausibly, for as long as the declarations existed.

    python3 scripts/check-reset-shadow.py       # check, exit 1 on a finding
    python3 scripts/check-reset-shadow.py -v    # list every reset, every class
                                                # it governs and every
                                                # restatement, not only the
                                                # findings
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
CSS = DS / "assets" / "css"

# The reset lives in base.css and nowhere else. tokens.css declares custom
# properties and components.css declares components; neither writes a bare
# element selector, which is the boundary base.css's own header draws.
RESET_SHEET = CSS / "base.css"

# Every stylesheet a shadowed rule could be written in — the three that ship,
# plus docs.css, plus every page-local <style> block. Wider than the breakpoint
# register's scope on purpose: the register is about numbers that have to agree
# with each other, and page-local numbers genuinely are a different register.
# This is about a rule losing to a reset, and the reset applies to every page
# the browser loads, so scoping it to what ships would leave the case that
# actually happened out.
SHEETS = ("tokens.css", "base.css", "components.css", "docs.css")

# prototypes/ is declared not-yet-system by the README and is out of every
# other check's scope; it is out of this one's for the same reason.
EXCLUDED_DIRS = ("prototypes",)

# Shorthand -> the longhands it sets. Physical and logical are listed together
# because the cascade resolves them against one another: `margin: 0` and
# `margin-block-end: 1rem` are two declarations of the same property for the
# purpose of deciding which one wins.
SHORTHANDS = {
    "margin": (
        "margin-top", "margin-right", "margin-bottom", "margin-left",
        "margin-block", "margin-inline",
        "margin-block-start", "margin-block-end",
        "margin-inline-start", "margin-inline-end",
    ),
    "padding": (
        "padding-top", "padding-right", "padding-bottom", "padding-left",
        "padding-block", "padding-inline",
        "padding-block-start", "padding-block-end",
        "padding-inline-start", "padding-inline-end",
    ),
    "list-style": ("list-style-type", "list-style-position", "list-style-image"),
    "border": (
        "border-width", "border-style", "border-color",
        "border-top", "border-right", "border-bottom", "border-left",
        "border-block", "border-inline",
    ),
    "font": ("font-family", "font-size", "font-weight", "font-style", "line-height"),
    "background": ("background-color", "background-image", "background-position",
                   "background-size", "background-repeat"),
}


def expand(prop):
    """Every property name a declaration of `prop` competes with, including itself."""
    names = {prop}
    for short, longs in SHORTHANDS.items():
        if prop == short:
            names.update(longs)
        elif prop in longs:
            names.add(short)
            # A shorthand and any of its longhands compete; two longhands of the
            # same shorthand do not unless they are the same property. `margin-block`
            # and `margin-block-end` do, so the shorthand chain is walked one more
            # step for the logical pairs.
            for other in longs:
                if other != prop and (other in prop or prop in other):
                    names.add(other)
    return names


def blank(match):
    """Replace a span with as many newlines as it held, so line numbers survive."""
    return "\n" * match.group(0).count("\n")


ZERO = re.compile(r"^0(?:px|rem|em|%|vw|vh|ch)?$")


def normal(value):
    """A value in the one form two spellings of the same thing share.

    Only zero is normalised, because zero is the only value this reset sets that
    has more than one spelling — `0`, `0px` and `0rem` are the same used value
    and the tree writes all three. Nothing else is folded: `auto` is not `0`,
    `var(--space-2)` is not `0`, and a check that guessed at custom properties
    would be reading tokens.css to decide whether a component is broken, which
    is a different script's job and a worse idea.
    """
    v = " ".join(value.lower().split())
    parts = v.split()
    if parts and all(ZERO.match(p) for p in parts):
        return "0"
    return v


def agrees(prop, value, reset):
    """Does this declaration ask for what the reset already gives it?

    Compared against the reset's declaration of the SAME property where there is
    one, and against its shorthand otherwise — `padding-inline: 0` agrees with
    `padding: 0`, because the shorthand sets every longhand to the value it
    carries. A shorthand written against a longhand reset is the one direction
    that cannot be decided here (the shorthand sets sides the longhand never
    mentioned), and it is treated as disagreement: the safe answer, and the
    reset in this system is written as shorthands anyway.
    """
    own = reset["values"].get(prop)
    if own is not None:
        return normal(value) == normal(own)
    for short, longs in SHORTHANDS.items():
        if prop in longs and short in reset["values"]:
            return normal(value) == normal(reset["values"][short])
    return False


def blocks(text):
    """Every rule as (line, selector, body), comments stripped in place.

    Same shape as check-grid-tracks.py's, and for the same reasons: comments go
    first so a selector quoted inside one — this file's own docstring quotes
    two — is never read as a rule, and at-rule preludes fall out because they
    carry no declarations. Nesting is not parsed and does not need to be: a rule
    inside @media or @supports still arrives here with its own selector.
    """
    text = re.sub(r"/\*.*?\*/", blank, text, flags=re.S)
    for m in re.finditer(r"([^{}]*)\{([^{}]*)\}", text):
        raw = m.group(1)
        sel = " ".join(raw.split())
        if not sel or sel.startswith("@"):
            continue
        head = m.start(1) + len(raw) - len(raw.lstrip())
        yield text[: head].count("\n") + 1, sel, m.group(2)


def declarations(body):
    for decl in body.split(";"):
        prop, sep, value = decl.partition(":")
        if sep:
            yield prop.strip().lower(), value.strip()


ID_RE = re.compile(r"#[\w-]+")
CLASS_RE = re.compile(r"\.[\w-]+")
ATTR_RE = re.compile(r"\[[^\]]*\]")
PSEUDO_EL_RE = re.compile(r"::[\w-]+")
PSEUDO_CL_RE = re.compile(r":[\w-]+(?:\([^)]*\))?")
TYPE_RE = re.compile(r"(?:^|[\s>+~])([a-zA-Z][\w-]*)")


def specificity(selector):
    """(id, class, type) for one compound-or-complex selector.

    Deliberately simple. :is()/:where()/:not() argument weighting is not modelled
    because this system writes exactly one form of them — :not(.class) inside a
    class selector — and the comparison this script makes is between a rule with
    no pseudo-class at all and a reset with no pseudo-class at all. A selector
    carrying anything more exotic is heavier than both by inspection, and heavier
    is safe: it is the LIGHT side that loses.
    """
    s = PSEUDO_EL_RE.sub(" \x00 ", selector)
    ids = len(ID_RE.findall(s))
    s = ID_RE.sub(" ", s)
    classes = len(CLASS_RE.findall(s))
    s = CLASS_RE.sub(" ", s)
    attrs = len(ATTR_RE.findall(s))
    s = ATTR_RE.sub(" ", s)
    pseudo_cl = len(PSEUDO_CL_RE.findall(s))
    s = PSEUDO_CL_RE.sub(" ", s)
    types = len(TYPE_RE.findall(" " + s))
    pseudo_el = selector.count("::")
    return (ids, classes + attrs + pseudo_cl, types + pseudo_el)


# A reset selector this script reads: a bare tag with one attribute test and no
# class, no id, no combinator. `ol[role="list"]` and nothing more complicated.
RESET_SEL = re.compile(
    r'^([a-z][\w-]*)\[\s*([\w-]+)\s*(?:([~|^$*]?=)\s*"?([^"\]]*)"?\s*)?\]$'
)


def resets():
    """Every attribute-bearing reset in base.css, as (tag, attr, op, value, props, line)."""
    text = RESET_SHEET.read_text(encoding="utf-8")
    found = []
    for line, sel, body in blocks(text):
        values = {p: v for p, v in declarations(body) if not p.startswith("--")}
        props = set(values)
        if not props:
            continue
        for part in sel.split(","):
            m = RESET_SEL.match(part.strip())
            if not m:
                continue
            tag, attr, op, val = m.group(1), m.group(2), m.group(3), m.group(4)
            found.append({
                "tag": tag.lower(), "attr": attr.lower(), "op": op, "val": val,
                "props": props, "values": values, "line": line, "sel": part.strip(),
                "spec": specificity(part.strip()),
            })
    return found


TAG_RE = re.compile(r"<([a-zA-Z][\w-]*)((?:\s+[^<>]*?)?)/?>", re.S)
ATTRPAIR_RE = re.compile(r'([\w:-]+)\s*=\s*"([^"]*)"')


def html_files():
    for path in sorted(DS.rglob("*.html")):
        if any(part in EXCLUDED_DIRS for part in path.relative_to(DS).parts):
            continue
        yield path
    for path in sorted(ROOT.glob("*.html")):
        yield path


def classes_on_resets(reset_list):
    """class -> the resets that match an element carrying it, read from the markup."""
    governed = {}
    for path in html_files():
        text = path.read_text(encoding="utf-8")
        # Comments out first: the tree's HTML comments are long and quote markup.
        text = re.sub(r"<!--.*?-->", blank, text, flags=re.S)
        for m in TAG_RE.finditer(text):
            tag = m.group(1).lower()
            attrs = {k.lower(): v for k, v in ATTRPAIR_RE.findall(m.group(2) or "")}
            if "class" not in attrs:
                continue
            for reset in reset_list:
                if tag != reset["tag"]:
                    continue
                got = attrs.get(reset["attr"])
                if got is None:
                    continue
                if reset["op"] == "=" and got != reset["val"]:
                    continue
                for cls in attrs["class"].split():
                    governed.setdefault(cls, set()).add(id(reset))
    return governed


def css_sources():
    """(label, text) for every stylesheet and every page-local <style> block."""
    for name in SHEETS:
        path = CSS / name
        if path.exists():
            yield path.relative_to(ROOT).as_posix(), path.read_text(encoding="utf-8"), 0
    for path in html_files():
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"<!--.*?-->", blank, text, flags=re.S)
        for m in re.finditer(r"<style[^>]*>(.*?)</style>", text, flags=re.S):
            offset = text[: m.start(1)].count("\n")
            yield path.relative_to(ROOT).as_posix(), m.group(1), offset


# The subject of a complex selector is its last compound — that is the element
# the declarations land on, and the only one whose classes matter here.
def subject(selector):
    parts = re.split(r"\s*[\s>+~]\s*", selector.strip())
    return parts[-1] if parts else selector


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    reset_list = resets()
    if not reset_list:
        print("check-reset-shadow: no attribute-bearing reset found in base.css.")
        print("  That is either a real simplification or a parse failure, and the")
        print("  two look the same from here. Read base.css before believing it.")
        return 1

    by_id = {id(r): r for r in reset_list}
    governed = classes_on_resets(reset_list)

    if args.verbose:
        print("Resets in base.css that outweigh a bare class:")
        for r in reset_list:
            print(f"  base.css:{r['line']}  {r['sel']}  {r['spec']}  {{ {', '.join(sorted(r['props']))} }}")
        print("\nClasses the markup puts on an element one of them matches:")
        for cls in sorted(governed):
            names = ", ".join(sorted(by_id[i]["sel"] for i in governed[cls]))
            print(f"  .{cls}  <- {names}")
        print()

    findings = []
    restatements = []
    checked = 0
    for label, text, offset in css_sources():
        for line, sel, body in blocks(text):
            for part in sel.split(","):
                part = part.strip()
                if not part:
                    continue
                subj = subject(part)
                cls_names = [c[1:] for c in CLASS_RE.findall(subj)]
                if not cls_names:
                    continue
                hit = set()
                for c in cls_names:
                    hit |= governed.get(c, set())
                if not hit:
                    continue
                spec = specificity(part)
                for rid in sorted(hit):
                    reset = by_id[rid]
                    checked += 1
                    if spec >= reset["spec"]:
                        continue
                    for prop, value in declarations(body):
                        if prop.startswith("--"):
                            continue
                        if not expand(prop) & reset["props"]:
                            continue
                        row = {
                            "file": label, "line": line + offset, "sel": part,
                            "spec": spec, "prop": prop, "value": value,
                            "reset": reset,
                        }
                        if agrees(prop, value, reset):
                            restatements.append(row)
                        else:
                            findings.append(row)

    if args.verbose and restatements:
        print("Restatements — shadowed, but asking for what the reset already gives.")
        print("Counted, never failed; see the docstring for why.")
        for r in restatements:
            print(f"  {r['file']}:{r['line']}  {r['sel']} {{ {r['prop']}: {r['value']}; }}")
        print()

    if findings:
        print(f"check-reset-shadow: {len(findings)} declaration(s) a reset already outweighs\n"
              f"  and contradicts. ({len(restatements)} further restate it harmlessly.)\n")
        for f in findings:
            r = f["reset"]
            print(f"  {f['file']}:{f['line']}")
            print(f"    {f['sel']} {{ {f['prop']}: {f['value']}; }}   {f['spec']}")
            print(f"    loses to  base.css:{r['line']}  {r['sel']} {{ ... }}   {r['spec']}")
            print(f"    The declaration is dead at every viewport. Source order cannot")
            print(f"    save it — the reset is heavier. Move to a property no reset")
            print(f"    owns (justify-self, row-gap on the parent grid), or take the")
            print(f"    selector past {r['spec']} on purpose and say why.\n")
        return 1

    print(f"check-reset-shadow: ok — {len(reset_list)} reset(s), "
          f"{len(governed)} class(es) under them, {checked} rule/reset pair(s) weighed, "
          f"{len(restatements)} harmless restatement(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
