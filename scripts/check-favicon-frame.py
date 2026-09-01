#!/usr/bin/env python3
"""The favicon is the signet on nothing, and it stays that way.

The icon shipped as the manual's APP ICON frame: a #101010 tile at rx="96"
with the white symbol inside it. That was a considered choice and it is
written into the file it replaced — the bare symbol ships in exactly two
colours, white is invisible on a light tab strip and black on a dark one, and
a plate under the mark is legible on both without a media query.

The site's owner asked for the other frame. A filled black square with a
rounded corner is an app icon, and at 16 px the plate is most of what a reader
sees: the tab shows a black chip where every neighbouring tab shows a mark.
The manual defines five frames and the first of them is transparent. The icon
is now the signet alone, CF-Schwarz on a light strip and CF-Weiss on a dark
one, switched by prefers-color-scheme inside the file.

WHY A SCRIPT. Every part of this is invisible where it is decided and obvious
where it is not. The file renders correctly in the design system's own logo
chapter either way — an <img> on a white docs page paints the black mark and
paints the old plate just as happily. The one surface that shows the
difference is a browser tab strip, which is chrome: no screenshot the routines
take contains it, no DOM sweep reaches it, and Playwright cannot render it.
And the failure mode is not a wrong picture but a silently DEAD media query —
a `fill` attribute left on a path overrides the stylesheet's rule, the icon
goes on painting black, and the only reader who ever finds out is one with a
dark tab strip looking for a mark that is not there.

The reintroduction is the likelier fault than the regression. The next run to
notice that a black mark is invisible on a dark strip has the plate sitting in
this file's git history with a paragraph arguing for it, and putting it back
fixes the symptom.

WHAT IT CHECKS, on design-system/assets/img/logo/cf-favicon.svg:

  no background   no <rect>, <circle>, <ellipse>, <polygon> or <path> that
                  paints the canvas behind the mark, and no fill on <svg>
                  itself other than "none". A frame the manual calls
                  transparent has nothing behind the art.
  the art is the signet   the two path d= strings are byte-identical to
                  cf-symbol-white.svg's, which is also cf-symbol-black.svg's.
                  The favicon is the mark at a different size, never a mark
                  redrawn to survive one.
  both strips     the stylesheet fills the mark #000000, and #FFFFFF under
                  (prefers-color-scheme: dark). Both are palette tokens —
                  --cf-schwarz and --cf-weiss — and the near-blacks the plate
                  used are not.
  the query is live   no <path> or <g> carrying the mark may declare its own
                  fill attribute. A presentation attribute on the element the
                  rule targets is not overridden by it; it is the rule that
                  loses, and the dark strip gets black on black.
  declared everywhere   every page under design-system/ that ships a
                  rel="icon" points at this file, and every page outside
                  prototypes/ carries one — the pattern pages, both editions,
                  and the documentation: the overview, reference.html, every
                  chapter and every specimen. A browser asks for an icon
                  either way, and an undeclared ask is a 404 at the origin
                  root of a site that deploys to a subpath.

THE DOCUMENTATION WAS HELD TO THE SECOND HALF OF THAT AND NOT THE FIRST, and
it showed the day a chapter was added. As first written, "carries one" was
asserted on patterns/ and patterns/en/ only; a chapter or a specimen was read
for where its link pointed and excused if it had none. That scope was the
state of the tree when the check was written — index.html's own head comment
records the declaration "made on all 38 pattern pages and on none of the 46
documentation pages" — and the documentation was then brought into line
without the check following it. Measured 2026-09-01: 47 of the 48
documentation pages carried the link and foundations/light.html, the chapter
added the day before, did not; its tab showed no mark, its console carried
the one 404 the overview's comment describes as the fault, and this check
passed. A convention 47 pages keep and one page misses is not a rule until
something counts it, so the documentation is now held to the same line as
the patterns. prototypes/ stays out: the four pages there are the designer's
raw material, unshipped by the README's own account and outside every other
check for the same reason, and none of them declares an icon.

Proven failing on: the plate restored, a fill= put back on a path, the dark
rule deleted, #101010 in place of #000000, a path redrawn, the rel="icon"
line removed from one pattern page, and — after the widening — the same line
removed from foundations/light.html, which the check had passed the day
before.
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
ICON = DS / "assets/img/logo/cf-favicon.svg"
SYMBOL = DS / "assets/img/logo/cf-symbol-white.svg"

# --cf-schwarz and --cf-weiss, tokens.css. The two colours the logo has.
INK_LIGHT = "#000000"
INK_DARK = "#FFFFFF"

SHAPES = ("rect", "circle", "ellipse", "polygon", "polyline")
PATH_D = re.compile(r"<path\b[^>]*?\bd=\"([^\"]+)\"", re.S)
COMMENT = re.compile(r"<!--.*?-->", re.S)
STYLE_BLOCK = re.compile(r"<style\b[^>]*>(.*?)</style>", re.S)
ICON_LINK = re.compile(r"<link\b[^>]*\brel=\"[^\"]*\bicon\b[^\"]*\"[^>]*>", re.I)
HREF = re.compile(r"\bhref=\"([^\"]+)\"")


def strip_comments(text):
    """The file argues for itself at length; the argument is not markup."""
    return COMMENT.sub("", text)


def audit_icon():
    findings = []
    facts = []

    if not ICON.exists():
        return [("design-system/assets/img/logo/cf-favicon.svg", 0,
                 "the favicon is gone; every page in the repository names it")], facts
    if not SYMBOL.exists():
        return [("design-system/assets/img/logo/cf-symbol-white.svg", 0,
                 "the symbol the favicon is cut from is gone")], facts

    rel = ICON.relative_to(ROOT).as_posix()
    raw = ICON.read_text(encoding="utf-8")
    body = strip_comments(raw)

    def line_of(needle):
        idx = raw.find(needle)
        return raw.count("\n", 0, idx) + 1 if idx >= 0 else 1

    # 1. NOTHING BEHIND THE MARK.
    for tag in SHAPES:
        if re.search(r"<%s\b" % tag, body):
            findings.append((rel, line_of("<%s" % tag),
                             "<%s> in the favicon: the transparent frame has nothing "
                             "behind the art. A plate here is the app icon, which is "
                             "what the site's owner asked to be rid of." % tag))
    svg_open = re.search(r"<svg\b[^>]*>", body)
    if not svg_open:
        findings.append((rel, 1, "no <svg> element"))
        return findings, facts
    root_fill = re.search(r"\bfill=\"([^\"]+)\"", svg_open.group(0))
    if root_fill and root_fill.group(1) != "none":
        findings.append((rel, line_of("<svg"),
                         "<svg fill=\"%s\">: the root paints the canvas. It must be "
                         "fill=\"none\"." % root_fill.group(1)))

    # 2. THE ART IS THE SIGNET, UNCHANGED.
    icon_paths = PATH_D.findall(body)
    symbol_paths = PATH_D.findall(strip_comments(SYMBOL.read_text(encoding="utf-8")))
    if icon_paths != symbol_paths:
        findings.append((rel, line_of("<path"),
                         "the %d path%s here %s not cf-symbol-white.svg's %d. The "
                         "favicon is the mark at another size, never a mark redrawn "
                         "to survive one."
                         % (len(icon_paths), "" if len(icon_paths) == 1 else "s",
                            "is" if len(icon_paths) == 1 else "are",
                            len(symbol_paths))))
    facts.append(("paths", "%d, identical to cf-symbol-white.svg"
                  % len(icon_paths) if icon_paths == symbol_paths
                  else "%d, DIVERGED" % len(icon_paths)))

    # 3. THE QUERY IS LIVE — no presentation attribute over the rule.
    for m in re.finditer(r"<(path|g)\b[^>]*>", body):
        if re.search(r"\bfill=\"", m.group(0)):
            findings.append((rel, raw.count("\n", 0, raw.find(m.group(0)[:40])) + 1,
                             "<%s fill=…>: a fill attribute on the element the "
                             "stylesheet targets wins over the rule, so the dark "
                             "strip keeps the light strip's ink." % m.group(1)))

    # 4. BOTH STRIPS.
    styles = "\n".join(STYLE_BLOCK.findall(body))
    if not styles.strip():
        findings.append((rel, 1,
                         "no <style>: with the plate gone the media query is the only "
                         "thing making the mark legible on a dark tab strip"))
    else:
        dark = re.search(r"@media[^{]*prefers-color-scheme:\s*dark[^{]*\{(.*?\})\s*\}",
                         styles, re.S)
        # The media block is stripped before the light rule is read, so the two
        # inks are never counted as one another's.
        outside = re.sub(r"@media[^{]*\{.*?\}\s*\}", "", styles, flags=re.S)
        light_decls = re.findall(r"fill:\s*(#[0-9A-Fa-f]{3,8})\s*;", outside)
        if [c.upper() for c in light_decls] != [INK_LIGHT]:
            findings.append((rel, line_of("<style"),
                             "the light strip's ink is %s, not %s (--cf-schwarz). The "
                             "logo has two colours and a near-black is neither."
                             % (light_decls or "unset", INK_LIGHT)))
        if not dark:
            findings.append((rel, line_of("<style"),
                             "no (prefers-color-scheme: dark) rule: a black mark on a "
                             "dark tab strip is the fault the plate used to cover"))
        else:
            dark_decls = re.findall(r"fill:\s*(#[0-9A-Fa-f]{3,8})\s*;", dark.group(1))
            if [c.upper() for c in dark_decls] != [INK_DARK]:
                findings.append((rel, line_of("prefers-color-scheme"),
                                 "the dark strip's ink is %s, not %s (--cf-weiss)"
                                 % (dark_decls or "unset", INK_DARK)))
        facts.append(("ink", "%s on a light strip, %s on a dark one"
                      % (INK_LIGHT, INK_DARK)))

    return findings, facts


def audit_declarations():
    """A browser asks for an icon either way. Every page has to answer."""
    findings, seen = [], []
    for path in sorted(DS.rglob("*.html")):
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        links = ICON_LINK.findall(strip_comments(text))
        # Every page outside prototypes/ has to answer the ask: the patterns in
        # both editions, and the documentation with them. The scope used to be
        # patterns/ and patterns/en/ alone, which is how a chapter shipped
        # without the link while this check passed — see the docstring.
        is_page = path.relative_to(DS).parts[0] != "prototypes"
        if not links:
            if is_page:
                findings.append((rel, 1,
                                 "no rel=\"icon\": the ask falls back to GET "
                                 "/favicon.ico at the origin root, which this site "
                                 "does not own"))
            continue
        for link in links:
            href = HREF.search(link)
            target = href.group(1) if href else ""
            if not target.endswith("assets/img/logo/cf-favicon.svg"):
                findings.append((rel, text.count("\n", 0, text.find(link)) + 1,
                                 "rel=\"icon\" points at %s; there is one favicon in "
                                 "this repository" % (target or "nothing")))
            elif not (path.parent / target).resolve().exists():
                findings.append((rel, text.count("\n", 0, text.find(link)) + 1,
                                 "rel=\"icon\" href %s does not resolve" % target))
            else:
                seen.append((rel, target))
    return findings, seen


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list every page that declares the icon")
    args = ap.parse_args()

    findings, facts = audit_icon()
    more, seen = audit_declarations()
    findings += more

    if args.verbose:
        for name, value in facts:
            print("  %-8s %s" % (name, value))
        for rel, target in seen:
            print("  %-52s %s" % (rel[-52:], target))
        print()

    if findings:
        for rel, line, why in findings:
            print("%s:%d\n    %s" % (rel, line, why), file=sys.stderr)
        print("\n%d finding%s: the favicon is the signet on nothing — black on a light "
              "tab strip, white on a dark one — and every page in the repository names "
              "it." % (len(findings), "" if len(findings) == 1 else "s"), file=sys.stderr)
        return 1

    print("favicon: the signet on a transparent frame, %s / %s by "
          "prefers-color-scheme, declared by %d page%s."
          % (INK_LIGHT, INK_DARK, len(seen), "" if len(seen) == 1 else "s"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
