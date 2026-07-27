#!/usr/bin/env python3
"""A pinned track's last step has no exit.

The system wrote this rule down once and then lost it in a move.

Unsere Werte is the first of the three pinned tracks and it has carried the
rule since it was written: cf-values-item ends at opacity 0, the sixth stage
runs cf-values-item-last instead, and the comment over it says "the last one
holds: there is no seventh stage to hand over to". foundations/motion.html#hold
states it a second time about Expertise's glass pane — "The last cycle has no
exit, because the track ends with the pane still standing" — which the pane
obeys because the pane is one element with its cycle written out four times and
somebody had to type the fourth one.

Then Expertise and the landing page's byte-identical private copies of the
scaffolding were folded into .cf-pin. The quarters came across, the crossfade
came across, the 62 % hold and the chrome came across. The last-stage exception
did not, because there was nothing in either page's copy to fold — neither had
ever had it. So the three animations that carry every part of a .cf-pin stage
are all HANDOVER animations, each authored to come back to nothing at 100 % so
the next quarter can take the stage from it, and all three were handed to the
fourth quarter, which has no next quarter:

    .cf-pin__step   opacity 0 -> 1 -> 0     the drawing crossfades
    .cf-pin__copy   opacity 1 -> 0          the copy snaps out at its edge
    .cf-pin__mark   muted -> ink -> muted   the index un-names the card

So both pinned tracks dismantled themselves and then made the reader scroll the
wreckage. Measured on the landing page at 1440 x 900, contain 0-100 % spanning
y 1664-7424:

    copy 04    opacity 1 -> 0    contain 96.5 -> 99.3    y 7224 - 7384
    mark 04    ink -> muted      contain 96.5 -> 100     y 7224 - 7424
    step 04    opacity 1 -> 0    contain 100  -> 103.5   y 7424 - 7624

— and from y 7624 to the section's end at y 8324, 700 px in which nothing on
the page changes at all: an empty lectern, four dead index numbers and a full
progress bar. Expertise was the same to a tenth of a point.

None of that is visible in a screenshot of any single moment, which is the
whole difficulty: every frame of it renders exactly as authored. It is only
wrong as a sequence, and only at the one end of the track that nobody scrolls
to twice.

WHAT IS CHECKED, across all three tracks — Werte included, so that the place
this rule was learned is held to it too. Four things, and the last two are the
ones that will break.

  1. The base keyframe sets still LEAVE — each ends at 100 % in a state other
     than the one it holds through the middle of its range. That is what makes
     a handover a handover, and a well-meant edit that removed it would
     silently stop the quarters crossfading.
  2. The last stage runs those animations without their exits — a keyframe set
     that ends at 100 % in the state it holds, or `none` for an animation that
     only ever left. And where the last set still has an arrival, that arrival
     is the SAME literal as the base's, so the last stage arrives exactly like
     the others rather than nearly like them.
  3. The markup shape `:last-child` depends on. The landing page's lectern
     plate is an <article> sibling of the four cards, so `:last-of-type` is
     right for the step and wrong for the copy, whose panel is the last <div>
     in EVERY card; the binding is therefore `:last-child`, and `:last-child`
     stops matching the moment somebody appends a sibling to the steps
     container or the index.
  4. The count Werte's ending is bound to instead. It has no `:last-child` to
     keep it honest — the ending is on `:nth-child(6)` and the 6 is a literal
     in a stylesheet while the stages are elements in a page. A seventh value
     leaves the sixth holding an ending it is no longer at.

Nothing renders wrong when 3 or 4 breaks. The track just quietly starts
dismantling itself again, 6,000 px down a page, at the one position a reviewer
arrives at last and with the least attention left.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-pin-handover.py
"""

import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
DS = ROOT / "design-system"
COMPONENTS = DS / "assets" / "css" / "components.css"

# Every role on every pinned track, and how each is bound for the last stage.
# The selector is the literal the stylesheet has to carry: this script asserts
# the binding, not merely that some rule somewhere mentions the class.
#
# The two .cf-values rows are the PRECEDENT, not an afterthought. Unsere Werte
# is the track this rule was first written on and the only one that never lost
# it; they are here so that the place the system learned this is held to it too.
ROLES = [
    ("step", ".cf-pin__step", ".cf-pin__step:last-child"),
    ("copy", ".cf-pin__copy", ".cf-pin__step:last-child .cf-pin__copy"),
    ("mark", ".cf-pin__mark", ".cf-pin__mark:last-child"),
    ("value", ".cf-values__item", ".cf-values__item:nth-child(6)"),
    ("value index", ".cf-values__index-n", ".cf-values__index-n:nth-child(6)"),
]

# A track bound by :nth-child(N) has no `:last-child` to keep it honest — the
# literal is the count. These are the selectors whose highest ranged nth-child
# has to equal how many of them the markup actually holds.
COUNTED = [".cf-values__item", ".cf-values__index-n"]

MOTION = "-> design-system/foundations/motion.html#hold"

VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


def strip_comments(css):
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


# --------------------------------------------------------------------------
# the stylesheet: keyframes and the rules that name them
# --------------------------------------------------------------------------
def keyframes(css):
    """@keyframes NAME -> [(percent, {prop: value}), ...], stops in order.

    A selector may list several stops (`11%, 89%`); each becomes its own entry
    with the same declarations, which is what the interpolation actually does.
    """
    out = {}
    for m in re.finditer(r"@keyframes\s+([\w-]+)\s*\{", css):
        name = m.group(1)
        i, depth = m.end(), 1
        while i < len(css) and depth:
            depth += (css[i] == "{") - (css[i] == "}")
            i += 1
        body, stops = css[m.end():i - 1], []
        for sm in re.finditer(r"([^{}]+)\{([^{}]*)\}", body):
            decls = {}
            for d in sm.group(2).split(";"):
                if ":" in d:
                    k, v = d.split(":", 1)
                    decls[k.strip()] = " ".join(v.split())
            for stop in sm.group(1).split(","):
                stop = stop.strip().lower()
                pct = {"from": 0.0, "to": 100.0}.get(stop)
                if pct is None and stop.endswith("%"):
                    pct = float(stop[:-1])
                if pct is not None:
                    stops.append((pct, decls))
        out[name] = sorted(stops, key=lambda s: s[0])
    return out


def animation_name(css, selector):
    """The keyframe name a rule assigns, via `animation` shorthand or
    `animation-name`. Returns None if the selector has no rule at all."""
    found = None
    for m in re.finditer(r"(?m)^[ \t]*([^{}@]+?)\s*\{([^{}]*)\}", css):
        sels = [s.strip() for s in m.group(1).split(",")]
        if selector not in sels:
            continue
        body = m.group(2)
        n = re.search(r"animation-name\s*:\s*([^;]+)", body)
        if n:
            found = n.group(1).strip()
            continue
        n = re.search(r"(?<![\w-])animation\s*:\s*([^;]+)", body)
        if n:
            # shorthand: the name is the one word that is not a keyword
            words = n.group(1).split()
            kw = {"linear", "both", "forwards", "backwards", "none", "normal",
                  "infinite", "alternate", "reverse", "paused", "running"}
            names = [w for w in words
                     if w not in kw and not re.match(r"^[\d.]|^(ease|cubic|steps|var)", w)]
            if names:
                found = names[0]
    return found


def show(decls):
    """`{'opacity': '1'}` is not a sentence. Print what the keyframe says."""
    return "; ".join("%s: %s" % kv for kv in sorted(decls.items())) or "(nothing)"


def value_at(stops, pct):
    """The declarations in force at `pct`, and whether the animation is
    stationary there — i.e. the stops on both sides declare the same thing."""
    before = [s for s in stops if s[0] <= pct]
    after = [s for s in stops if s[0] >= pct]
    if not before or not after:
        return None, False
    lo, hi = before[-1][1], after[0][1]
    return hi, lo == hi


def check_css(findings):
    css = strip_comments(COMPONENTS.read_text())
    kf = keyframes(css)
    for role, base_sel, last_sel in ROLES:
        base_name = animation_name(css, base_sel)
        if base_name is None or base_name not in kf:
            findings.append(
                "%s has no readable animation. This script binds the rule that ends\n"
                "    a pinned track to the rule that runs it; it cannot check a name it\n"
                "    cannot find.\n    %s" % (base_sel, MOTION))
            continue
        stops = kf[base_name]
        held, still = value_at(stops, 50.0)
        end, _ = value_at(stops, 100.0)
        if not still:
            findings.append(
                "@keyframes %s is still moving at the middle of its range, so there is\n"
                "    no held state to compare its end against. Every stage on a pinned\n"
                "    track has a hold; an animation without one cannot be read.\n    %s"
                % (base_name, MOTION))
            continue

        # 1. the base still hands over
        if end == held:
            findings.append(
                "@keyframes %s ends at 100 %% in the state it holds, so %s never\n"
                "    leaves and the quarters no longer cross over. The overlap is what\n"
                "    stops the stage going blank at a boundary — the three points of range\n"
                "    at each end are the crossfade, not decoration.\n    %s"
                % (base_name, base_sel, MOTION))

        # 2. the last quarter runs it without the exit
        last_name = animation_name(css, last_sel)
        if last_name is None:
            findings.append(
                "There is no rule for `%s`, so the last quarter runs %s —\n"
                "    a handover animation with nothing to hand over to. It comes back to\n"
                "    nothing at 100 %%, and the reader is then left scrolling the empty\n"
                "    stage it left behind: measured at 700 px on the landing page at\n"
                "    1440 x 900, in which nothing on the page changes at all.\n    %s"
                % (last_sel, base_name, MOTION))
            continue
        if last_name == "none":
            continue  # an animation that only ever left, removed outright
        if last_name not in kf:
            findings.append(
                "%s names @keyframes %s, which is not defined.\n    %s"
                % (last_sel, last_name, MOTION))
            continue
        last_stops = kf[last_name]
        last_held, last_still = value_at(last_stops, 50.0)
        last_end, _ = value_at(last_stops, 100.0)
        if not last_still or last_end != last_held:
            findings.append(
                "@keyframes %s does not end standing: it holds %s and ends at %s.\n"
                "    The last quarter of a pinned track has no successor, so the track\n"
                "    ends with the last step still on the stage — the same rule the glass\n"
                "    pane's last cycle already follows.\n    %s"
                % (last_name, show(last_held), show(last_end), MOTION))
            continue

        # 3. and it arrives exactly like the other three, not nearly like them
        def arrival(st, target):
            for pct, decls in st:
                if decls == target:
                    return pct
            return None
        a_base, a_last = arrival(stops, held), arrival(last_stops, last_held)
        if a_base != a_last:
            findings.append(
                "@keyframes %s reaches its held state at %s %% where %s reaches it at\n"
                "    %s %%. The last step arrives on the same ramp as the other three or it\n"
                "    reads as a different kind of arrival; the literals are shared on\n"
                "    purpose.\n    %s"
                % (last_name, a_last, base_name, a_base, MOTION))
    return kf


# --------------------------------------------------------------------------
# the markup: what `:last-child` is standing on
# --------------------------------------------------------------------------
class PinFinder(HTMLParser):
    """Element tree, thin: every element gets a serial number, so a parent is
    identified by a value that cannot be recycled while the tree is walked.
    Records each element's parent, its class list and its line, and the child
    order under every parent — which is all `:last-child` is."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = [0]                     # serial numbers, 0 is the document
        self.next_id = 1
        self.node = {0: ([], 0)}             # id -> (classes, line)
        self.parent = {}                     # id -> parent id
        self.children = {0: []}              # id -> [child id, ...]
        self.hits = []                       # (cls, id)

    def handle_starttag(self, tag, attrs):
        nid, self.next_id = self.next_id, self.next_id + 1
        cls = dict(attrs).get("class", "").split()
        parent = self.stack[-1]
        self.node[nid] = (cls, self.getpos()[0])
        self.parent[nid] = parent
        self.children.setdefault(parent, []).append(nid)
        self.children.setdefault(nid, [])
        for c in cls:
            if c.startswith("cf-pin__"):
                self.hits.append((c, nid))
        if tag not in VOID:
            self.stack.append(nid)
            self.open_tag = getattr(self, "open_tag", {})
            self.open_tag[nid] = tag

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.stack[-1] != 0:
            self.stack.pop()

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if getattr(self, "open_tag", {}).get(self.stack[i]) == tag:
                del self.stack[i:]
                return

    def ancestors(self, nid):
        out, cur = [], self.parent.get(nid, 0)
        while cur:
            out += self.node[cur][0]
            cur = self.parent.get(cur, 0)
        return out


def check_counts(findings):
    """A track bound by :nth-child(N) is bound to a NUMBER, and the number is
    in the stylesheet while the elements are in the markup. Add a seventh value
    and the sixth keeps the ending mid-track while the seventh gets no range at
    all — the same failure as an appended sibling, one file over."""
    css = strip_comments(COMPONENTS.read_text())
    for sel in COUNTED:
        ranged = [int(m.group(1)) for m in
                  re.finditer(re.escape(sel) + r":nth-child\((\d+)\)\s*\{([^{}]*)\}", css)
                  if "animation-range" in m.group(2)]
        if not ranged:
            continue
        want = max(ranged)
        cls = sel.lstrip(".")
        for page in sorted(DS.rglob("*.html")):
            text = page.read_text()
            if cls not in text:
                continue
            parser = PinFinder()
            parser.feed(text)
            have = sum(1 for nid, (c, _) in parser.node.items() if cls in c)
            if have and have != want:
                findings.append(
                    "%s holds %d .%s and components.css ranges %d of them. The last\n"
                    "    stage's ending is bound to `:nth-child(%d)`, so the %s stage keeps\n"
                    "    an ending it is no longer at and the %s gets no range at all.\n    %s"
                    % (page.relative_to(ROOT), have, cls, want, want,
                       "%dth" % want, "%dth" % have, MOTION))


def check_markup(findings):
    pages = [p for p in sorted(DS.rglob("*.html"))
             if "cf-pin__step" in p.read_text()]
    tracks = 0
    for page in pages:
        rel = page.relative_to(ROOT)
        parser = PinFinder()
        parser.feed(page.read_text())
        for role in ("cf-pin__step", "cf-pin__mark"):
            hits = [h for h in parser.hits if h[0] == role]
            if not hits:
                continue
            tracks += role == "cf-pin__step"
            nid = hits[-1][1]
            line = parser.node[nid][1]
            siblings = parser.children[parser.parent[nid]]
            if siblings[-1] != nid:
                last_cls, last_line = parser.node[siblings[-1]]
                findings.append(
                    "%s:%d is the last .%s and it is NOT the last child of its parent —\n"
                    "    .%s at line %d is. components.css binds the track's ending to\n"
                    "    `:last-child`, so a sibling appended after the last %s takes the\n"
                    "    ending with it and the track goes back to dismantling itself at\n"
                    "    the end. Nothing renders wrong when this breaks.\n    %s"
                    % (rel, line, role, ".".join(last_cls) or "(no class)", last_line,
                       role.replace("cf-pin__", ""), MOTION))
        for cls, nid in parser.hits:
            if cls == "cf-pin__copy" and "cf-pin__step" not in parser.ancestors(nid):
                findings.append(
                    "%s:%d is a .cf-pin__copy outside any .cf-pin__step. The last copy is\n"
                    "    reached through `.cf-pin__step:last-child .cf-pin__copy` — a panel\n"
                    "    is the last <div> in EVERY card, so the step is what says WHICH\n"
                    "    copy is the last one.\n    %s"
                    % (rel, parser.node[nid][1], MOTION))
    return len(pages), tracks


def main():
    findings = []
    check_css(findings)
    check_counts(findings)
    pages, tracks = check_markup(findings)

    if findings:
        print("pinned handover: %d finding(s)\n" % len(findings))
        for f in findings:
            print("  - %s\n" % f)
        return 1

    print(
        "pinned handover: %d roles across three tracks hand over and end standing;\n"
        "%d .cf-pin track(s) on %d page(s) with the last step, copy and mark where\n"
        "`:last-child` can reach them, and the counted track at its stated count."
        % (len(ROLES), tracks, pages))
    return 0


if __name__ == "__main__":
    sys.exit(main())
