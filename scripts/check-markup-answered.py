#!/usr/bin/env python3
"""A shipping page may not state something the rest of the system never answers.

Two findings of the same shape, from the same audit, which is why they are one
script. Both are markup writing into a void: the page says something, correctly,
in the system's own vocabulary — and nothing anywhere picks it up.

  RULE 1, THE MODIFIER THE COMPONENT'S OWN PAGE DOES NOT SHOW.
  `.cf-footer--detached` shipped on ueber-uns and blog-artikel, was named in
  foundations/layout.html's rhythm table, and was already guarded by
  check-footer-parity.py — and components/footer.html, the page with the live
  footer on it, did not mention it. A reader building a footer from the
  component page could not learn that the modifier exists, let alone that a
  biconditional binds it to `.section--flush` on the last section. That is
  drift, and it is invisible from either end: the pattern renders right, and the
  documentation page reads complete, because you cannot see the paragraph that
  is not there.

  RULE 2, THE PROPERTY NOBODY READS. patterns/ueber-uns.html set
  `style="--layer:N"` on each of the four grid layers of the Werte mark, and no
  stylesheet, no page-local block and no script ever read it — the ranges those
  layers animate over were four hand-written pairs selected by `:nth-of-type`
  instead. The same index, written twice, one copy inert. The inert copy is the
  dangerous one: reorder the layers, or wrap them in a <g> for a clip, and
  :nth-of-type silently follows the new positions while --layer keeps saying
  what the drawing meant, with nothing in the system able to tell you they have
  come apart. (Closed by making --layer the copy that runs.)

  check-class-provenance.py asks the neighbouring question of a CLASS — who
  DECLARES this — and its rule 5 explicitly permits any custom property in an
  inline style=, "per-instance data the markup genuinely owns". It never asks
  whether anything owns it back. This does.

WHAT RULE 1 MEANS BY "THE COMPONENT'S OWN PAGE", and why it is not "any page
that mentions the block". Mentioning is cheap and every rhythm table does it;
foundations/layout.html names `.cf-footer--detached` three times and is not
where anybody builds a footer. The page a reader builds from is the page with
the thing ON it — a LIVE specimen, `class="cf-footer …"` in the document rather
than inside a <pre> listing. So:

    a modifier of block cf-X, shipping on a page under patterns/, must appear
    on at least one documentation page that carries a live specimen of cf-X.

Where a block has no live specimen anywhere the rule softens to its floor —
the name has to be findable under components/ or foundations/ at all — because
there is no page to hold to the stronger version. The hero's pause switch is
that case: foundations/motion.html documents the control at length and draws no
hero of its own.

The bar inside a qualifying page is deliberately generous: a specimen, a row in
an anatomy table, a line in a markup listing all count. It is that a reader can
find the name at all, not that it is drawn twice.

  KNOWN, below, is the register of gaps that exist today and are not this
  script's to close: it names them, with the reason, so they stay visible
  rather than becoming permission. A row whose gap has been closed fails too —
  a register that outlives its subject is how the next one hides inside it.
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "design-system"
PATTERNS = ROOT / "patterns"
DOCS = [ROOT / "components", ROOT / "foundations"]

COMMENT = re.compile(r"<!--.*?-->", re.S)
LISTING = re.compile(r"<pre.*?</pre>|<code.*?</code>|<textarea.*?</textarea>", re.S)
CLASS = re.compile(r'class="([^"]*)"')
INLINE = re.compile(r'style="([^"]*)"')
STYLE_BLOCK = re.compile(r"<style[^>]*>(.*?)</style>", re.S)
MODIFIER = re.compile(r"^cf-[a-z0-9]+(?:__[a-z0-9-]+)?--[a-z0-9-]+$")

# Modifiers that ship with no documentation anywhere, and why this script is not
# the thing that closes them. Each row is a real finding, parked in the open.
KNOWN = {}
# Empty, and that is the register working rather than the register being
# skipped. It held two rows — cf-culture__row--tall and cf-culture__row--wide —
# whose reason was that the block behind them had no documentation page at all:
# the two modifiers were the visible edge of a missing components/culture.html
# rather than a paragraph left out of an existing page. That page exists now and
# carries a live specimen of both frames, so rule 1 finds them shown, and the
# rows had to go with the gap they named — a row whose subject is closed fails
# this script as a STALE ROW, which is the half of it that keeps the register
# honest in the direction registers usually rot.


def block_of(cls):
    return cls.split("__")[0].split("--")[0]


def classes_in(text):
    for m in CLASS.finditer(text):
        for c in m.group(1).split():
            yield c


def rule_1(verbose):
    # Which documentation pages carry a LIVE specimen of which block.
    specimens = {}
    text_of = {}
    for d in DOCS:
        for p in sorted(d.glob("*.html")):
            raw = p.read_text(encoding="utf-8")
            text_of[p] = raw
            for c in classes_in(LISTING.sub("", COMMENT.sub("", raw))):
                if c.startswith("cf-"):
                    specimens.setdefault(block_of(c), set()).add(p)

    shipping = {}
    for page in sorted(PATTERNS.glob("*.html")):
        for c in classes_in(COMMENT.sub("", page.read_text(encoding="utf-8"))):
            if MODIFIER.match(c):
                shipping.setdefault(c, set()).add(page.name)

    findings = []
    open_gaps = set()
    for mod in sorted(shipping):
        where = ", ".join(sorted(shipping[mod]))
        owners = specimens.get(block_of(mod), set())
        named = re.compile(r"\b" + re.escape(mod) + r"\b")
        if owners:
            hit = sorted(p.name for p in owners if named.search(text_of[p]))
            gap = None if hit else (
                "  UNSHOWN       %s\n"
                "      ships on %s. %d documentation page%s carr%s a live specimen\n"
                "      of %s — %s — and none of them names this modifier. The page a\n"
                "      reader builds the component from has to show every state the\n"
                "      site ships of it."
                % (mod, where, len(owners), "" if len(owners) == 1 else "s",
                   "ies" if len(owners) == 1 else "y", block_of(mod),
                   ", ".join(sorted(p.name for p in owners))))
        else:
            anywhere = any(named.search(t) for t in text_of.values())
            gap = None if anywhere else (
                "  UNDOCUMENTED  %s\n"
                "      ships on %s and appears on no page under components/ or\n"
                "      foundations/, which also carry no live specimen of %s. A\n"
                "      state the system cannot be read to have is a state the next\n"
                "      person re-invents." % (mod, where, block_of(mod)))
        if gap is None:
            continue
        open_gaps.add(mod)
        if mod in KNOWN:
            if verbose:
                print("  known    %-32s %s" % (mod, where))
            continue
        findings.append(gap)

    for mod in sorted(set(KNOWN) - open_gaps):
        findings.append(
            "  STALE ROW     %s\n"
            "      is in KNOWN and is documented now (or no longer ships). Drop the\n"
            "      row: a register that outlives its subject is how the next gap\n"
            "      hides inside it." % mod)

    if verbose and not findings:
        print("  rule 1   %d modifiers ship, %d shown where they are built from, "
              "%d known-open" % (len(shipping), len(shipping) - len(open_gaps),
                                 len(open_gaps)))
    return findings


def rule_2(verbose):
    readers = ""
    for p in sorted((ROOT / "assets" / "css").glob("*.css")):
        readers += p.read_text(encoding="utf-8")
    for p in sorted((ROOT / "assets" / "js").glob("*.js")):
        readers += p.read_text(encoding="utf-8")

    findings = []
    count = 0
    for page in sorted(ROOT.glob("**/*.html")):
        text = COMMENT.sub("", page.read_text(encoding="utf-8"))
        local = "".join(STYLE_BLOCK.findall(text))
        names = set()
        for m in INLINE.finditer(text):
            for decl in m.group(1).split(";"):
                decl = decl.strip()
                if decl.startswith("--"):
                    names.add(decl.split(":")[0].strip())
        count += len(names)
        for name in sorted(names):
            # var(--name) in anything that runs, or a script naming it as a string.
            if re.search(r"var\(\s*" + re.escape(name) + r"\b", readers + local):
                continue
            if re.search(r"[\"']" + re.escape(name) + r"[\"']", readers + local):
                continue
            findings.append(
                "  UNREAD        %s on %s\n"
                "      is set in an inline style= and read by no stylesheet, no\n"
                "      page-local block and no script. Either something should read\n"
                "      it, or the markup should stop saying it."
                % (name, page.relative_to(ROOT)))

    if verbose and not findings:
        print("  rule 2   %d inline custom properties across the tree, all read"
              % count)
    return findings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    findings = rule_1(args.verbose) + rule_2(args.verbose)
    if findings:
        print("markup answered: %d finding%s\n"
              % (len(findings), "" if len(findings) == 1 else "s"))
        print("\n\n".join(findings))
        return 1

    print("markup answered: every modifier the pattern pages ship is shown on a "
          "page the component is built from, every inline custom property is read "
          "by something that runs, and %s."
          % ("KNOWN is empty — no gap is parked open" if not KNOWN else
             "the %d gap%s in KNOWN %s still open"
             % (len(KNOWN), "" if len(KNOWN) == 1 else "s",
                "is" if len(KNOWN) == 1 else "are")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
