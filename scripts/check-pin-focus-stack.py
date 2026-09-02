#!/usr/bin/env python3
"""A pinned card stack that holds links hides them from the pointer AND the ring.

A .cf-pin track stacks its cards in ONE grid area and shows them one at a time
by opacity on the track's view timeline. Three of four are therefore at
opacity 0 at every scroll position, and an element at opacity 0 is still in the
document: it still hit-tests, and it is still a sequential focus stop.

The first half of that was found and fixed — acts.css, "AN INVISIBLE CARD STILL
CATCHES THE POINTER": the card goes `pointer-events: none` for the whole
overlap and its copy panel takes it back over exactly the interval the card is
painted, on the same timeline and the same range. What that fix did not do was
the keyboard, and scripts/check-focus-reach.py had already written down why
that is not a separate finding but the same one:

    Hidden by paint is only honest if both halves are there: opacity alone
    leaves a click trap, and POINTER-EVENTS ALONE LEAVES AN INVISIBLE FOCUS
    STOP.

Measured on the landing page's act 4 with the pointer half in and the keyboard
half missing — Chromium, consent accepted, Tab walked forward into
.lp-ev-track at nine positions across the track's contain 0-100 %, each stop
scored by its own card's computed opacity:

    1440 x 900     126 stops    96 on a card at opacity 0    76 %
    1280 x 800     126 stops    96                           76 %
    1920 x 1080    126 stops    96                           76 %

The ring is not merely wasted there. The four cards share one grid area, so it
is drawn ON TOP of the card the reader is looking at, around a link belonging
to a card that is not on the stage. WCAG 2.4.7 asks that the focus indicator be
visible and 2.4.11 that it not be obscured.

WHAT IS CHECKED, and it is one sentence in three parts.

  WHO NEEDS THE PAIR.  Every page that ships a .cf-pin stack is read, every
      .cf-pin__step in it is sliced to its own closing tag, and a step is
      "loaded" if it contains a focusable — <a href>, <button>, <select>,
      <textarea>, <input> that is not hidden, or a positive tabindex. A stack
      with no loaded step needs nothing and is skipped by name in the summary:
      act 3's process cards hold no targets, which is why the pointer fix was
      written for act 4 alone and belongs where it is.

  THE PAIR ITSELF.  For a loaded stack, some rule in the shipping sheets must
      give the step's own class an `animation` list carrying BOTH a keyframe
      that switches `pointer-events` and one that switches `visibility`, under
      ONE animation-timeline and ONE animation-range. One rule and one range
      because the two switches are the same switch: split across two rules they
      become two windows that can be edited apart, which is exactly how the
      keyboard half went missing from the pointer half in the first place.

  THE WINDOWS AGREE.  The two keyframe blocks must open and close on the same
      selector literals — `0%, 100%` off and `11%, 89%` on, whatever those
      numbers are on the day — and each must have a `-last` partner that holds
      ON at 100 % instead of leaving, because the last quarter has no next
      quarter to hand over to. That is cf-pin-step-last's argument, and a stack
      whose last card keeps standing while its links go dark is the same dead
      end with the other property.

WHY `visibility` IS THE PROPERTY. The attribute `hidden` is what the act rail
was fixed away FROM: it is a state a stylesheet cannot reach, so a script would
have to re-derive from the scroll the sheet already owns, and it was a keyboard
trap when it tried. `visibility` is a property, it rides this timeline, and it
takes descendants out of the sequential focus order the way the platform means
it to. This file does not require that property by name — it requires that
whatever the sheet uses to release the pointer is paired with something that
releases the ring, and `visibility` is the only property in CSS that does.

WHAT THIS DOES NOT CLAIM. Not the numbers in the windows — 11/89 is
cf-pin-step's shape and this only holds the two pairs to EACH OTHER. Not that
a stack is the right form for evidence. Not anything about act 3, which has no
targets to steal. And not that focus could not instead DRIVE the stage — a
keyboard reader tabbing to card 03 and having the page scroll to card 03 would
satisfy the reader better than this does, and would need this file rewritten
rather than deleted.

stdlib only, no build step, no dependency. Same python3 that serves the pages.

    python3 scripts/check-pin-focus-stack.py
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHEETS = [ROOT / "design-system/assets/css/acts.css",
          ROOT / "design-system/assets/css/components.css"]
PAGE_DIRS = [ROOT / "design-system/patterns", ROOT / "design-system/prototypes"]

STEP = "cf-pin__step"
# <input type=hidden> is not a stop; a negative tabindex is not one either.
FOCUSABLE = re.compile(
    r"""<(?:a\s[^>]*\bhref=
         |button\b
         |select\b
         |textarea\b
         |input\b(?![^>]*\btype=["']?hidden)
         |[a-z]+\s[^>]*\btabindex=["']?(?!-))""",
    re.I | re.X)


def fail(msg):
    print(f"FAIL  {msg}")
    return 1


def strip_css_comments(css):
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def element_extent(html, start):
    """Slice from the tag opening at `start` to its own closing tag.

    A step is an <article> or <div> among other <article>s and <div>s, so a
    class-to-next-class slice runs the LAST step to the end of the document and
    counts the footer's links as its own. Depth-matching on the element's own
    tag name is what makes "this step holds a link" a statement about the step.
    """
    tag = re.match(r"<([a-zA-Z][\w-]*)", html[start:]).group(1)
    pat = re.compile(rf"<(/?){tag}\b", re.I)
    depth = 0
    for m in pat.finditer(html, start):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return html[start:m.end()]
    return html[start:]


def steps_with_targets(html):
    """{step class -> number of loaded steps} for every .cf-pin stack on a page."""
    loaded = {}
    seen = {}
    for m in re.finditer(r"<[a-zA-Z][\w-]*\s[^>]*class=\"([^\"]*\b" + STEP + r"\b[^\"]*)\"", html):
        classes = [c for c in m.group(1).split() if c != STEP]
        name = classes[0] if classes else STEP
        seen[name] = seen.get(name, 0) + 1
        if FOCUSABLE.search(element_extent(html, m.start())):
            loaded[name] = loaded.get(name, 0) + 1
    return seen, loaded


def keyframes(css):
    """{name: [(selector text, {prop: value})]} for every @keyframes block."""
    out = {}
    for m in re.finditer(r"@keyframes\s+([\w-]+)\s*\{", css):
        i = m.end()
        depth = 1
        while depth and i < len(css):
            depth += {"{": 1, "}": -1}.get(css[i], 0)
            i += 1
        body = css[m.end():i - 1]
        stops = []
        for s in re.finditer(r"([^{}]+)\{([^{}]*)\}", body):
            decls = {d.split(":", 1)[0].strip(): d.split(":", 1)[1].strip()
                     for d in s.group(2).split(";") if ":" in d}
            stops.append((" ".join(s.group(1).split()), decls))
        out[m.group(1)] = stops
    return out


def rules(css):
    for m in re.finditer(r"([^{}@]+)\{([^{}]*)\}", css):
        body = m.group(2)
        if "{" in body:
            continue
        decls = {}
        for d in body.split(";"):
            if ":" in d:
                k, v = d.split(":", 1)
                decls[k.strip()] = v.strip()
        yield [t.strip() for t in m.group(1).split(",")], decls


def switches(frames, prop):
    """Names of keyframe blocks whose only job is to switch `prop`."""
    return {n for n, stops in frames.items()
            if stops and all(prop in decls for _, decls in stops)}


def window(frames, name):
    """The block's ordered (selector, value) stops for its one property."""
    return [sel for sel, _ in frames[name]]


def holds_last(frames, name, on):
    """The -last partner ends ON rather than handing over."""
    stops = frames[name]
    return any("100%" in sel and list(decls.values())[0] == on for sel, decls in stops)


def main():
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()
    bad = 0

    css = "\n".join(strip_css_comments(s.read_text(encoding="utf-8")) for s in SHEETS)
    frames = keyframes(css)
    pe_names = switches(frames, "pointer-events")
    vis_names = switches(frames, "visibility")

    # step class -> the animation lists any rule gives it
    applied = {}
    for terms, decls in rules(css):
        names = decls.get("animation-name") or decls.get("animation")
        if not names:
            continue
        used = [n for n in re.split(r"[,\s]+", names) if n in frames]
        if not used:
            continue
        for t in terms:
            for cls in re.findall(r"\.([\w-]+)", t):
                entry = applied.setdefault(cls, [])
                entry.append((t, used, decls, ":last-child" in t))

    checked, skipped = [], []
    for d in PAGE_DIRS:
        for page in sorted(d.glob("*.html")):
            html = page.read_text(encoding="utf-8")
            if STEP not in html:
                continue
            seen, loaded = steps_with_targets(html)
            for name, count in sorted(seen.items()):
                if name not in loaded:
                    skipped.append(f"{page.name}:{name}")
                    continue

                lists = applied.get(name, []) + applied.get(f"{name}__panel", [])
                base = [e for e in lists if not e[3]]
                last = [e for e in lists if e[3]]

                pair = None
                for term, used, decls, _ in base:
                    pe = [n for n in used if n in pe_names]
                    vis = [n for n in used if n in vis_names]
                    if pe and vis:
                        pair = (term, pe[0], vis[0], decls)
                        break
                if not pair:
                    got = sorted({n for _, u, _, _ in base for n in u})
                    bad |= fail(
                        f"{page.name}: the pinned stack `.{name}` holds "
                        f"{loaded[name]} card(s) with focusable content and no "
                        f"one rule releases both the pointer and the ring on "
                        f"it — found {got or 'no animation at all'}. Three of "
                        f"its cards are at opacity 0 at every scroll position; "
                        f"without a `visibility` switch beside the "
                        f"`pointer-events` one their links stay in the tab "
                        f"order and the focus ring lands on a card nobody can "
                        f"see, over the card they can.")
                    continue

                term, pe, vis, decls = pair
                if len(set(re.findall(r"animation-timeline:\s*([^;]+)", str(decls)))) > 1:
                    bad |= fail(f"{page.name}: `{term}` runs its two switches on "
                                f"different timelines.")
                if window(frames, pe) != window(frames, vis):
                    bad |= fail(
                        f"{page.name}: `{pe}` opens on {window(frames, pe)} and "
                        f"`{vis}` on {window(frames, vis)}. What a reader can "
                        f"click and what a reader can reach are the same "
                        f"window or they are two numbers waiting to disagree.")

                for nm, off_on in ((pe, "auto"), (vis, "visible")):
                    partner = f"{nm}-last"
                    if partner not in frames:
                        bad |= fail(f"{page.name}: `{nm}` has no `{partner}`. The "
                                    f"last quarter has no next quarter to hand "
                                    f"over to, so the last card stands on the "
                                    f"stage with its own links switched off.")
                    elif not holds_last(frames, partner, off_on):
                        bad |= fail(f"{page.name}: `{partner}` does not hold "
                                    f"`{off_on}` at 100 %.")
                    elif not any(partner in u for _, u, _, _ in last):
                        bad |= fail(f"{page.name}: nothing applies `{partner}` to "
                                    f"`.{name}`'s last card.")
                checked.append(f"{page.name}:{name}")

    if bad:
        return 1
    if not checked:
        return fail("no pinned stack on any page carries focusable content — "
                    "the register is stale, or a stack lost its links")
    print(f"OK  {len(checked)} pinned stack(s) that hold links release the "
          f"pointer and the focus ring on one rule, one timeline and one "
          f"window ({', '.join(checked)}); {len(skipped)} that hold none need "
          f"neither ({', '.join(skipped)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
