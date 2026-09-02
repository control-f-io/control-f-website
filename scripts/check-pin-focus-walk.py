#!/usr/bin/env python3
"""A pinned card stack that holds links must be reachable by the Tab walk.

scripts/check-pin-focus-stack.py holds the pair that keeps the ring honest: a
.cf-pin card releases the pointer and the focus ring over exactly the interval
it is not painted, on one rule and one timeline. `visibility: hidden` is what
takes the ring off a card that is not on the stage, and it does that by taking
the card's subtree out of the sequential focus order — which is the platform's
own mechanism and the right one.

WHAT THAT LEFT. Which card is on the stage is a function of the SCROLL, and
the walk that would reach the cards' links begins at the start of the document,
where the track's timeline is clamped at progress 0 and no card is on the
stage. The stops between the top of the page and the track cannot change that:
on the landing page the nav, the language switch and the act rail are all
`position: fixed`, so focusing them scrolls nothing, and the only two in-flow
stops before the track are the hero's still switch and its call to action, at
document y 100 and y 750 — focusing either puts the reader back at the top. So
the walk arrives at the track at y 0 every time, finds four hidden cards, and
takes the next stop it can find, which is in the footer.

Measured before the fix, Chromium, consent already answered, one forward walk
from the first stop and one backward walk from the wrap, counting how many of
act 4's fourteen source links ever took focus:

    1024 x 900      forward 0 of 14     backward 2 of 14
    1280 x 800      forward 0           backward 2
    1440 x 900      forward 0           backward 2
    1920 x 1080     forward 0           backward 2
    768 x 1024      forward 14          backward 14     below the gate
    375 x 812       forward 14          backward 14
    1440 x 900      forward 14          backward 14     reduced motion

The two the backward walk found are the last card's, and they are what proves
the diagnosis rather than an exception to it: Shift+Tab from the wrap starts at
the END of the document, where the timeline is clamped at progress 1 and the
last card is the one on the stage. Every tier that does not pin lays the cards
out as a column, hides none of them and hands over all fourteen. The loss is
the pinned tier's alone. WCAG 2.1.1: fourteen links a pointer can open and a
keyboard cannot reach.

assets/js/cf-pin-focus.js is the fix — it carries the walk across the stack a
card at a time, scrolling each card onto the stage before focusing it — and it
is a script, which is the reason this check has to open a browser. Whether a
Tab press moves focus into a subtree whose visibility is computed from the
scroll position is not a question about any file.

WHAT IS CHECKED, per page that ships a LOADED .cf-pin stack — the same
definition scripts/check-pin-focus-stack.py uses, a step containing an <a
href>, a button, a select, a textarea, a non-hidden input or a non-negative
tabindex — and a page with no such stack is skipped by name:

  REACH        walk Tab from the top of the document to the wrap. Every
               focusable inside the stack must take focus exactly once. This
               is the check; the two below are what stop it being satisfied
               the wrong way.
  BACK         walk Shift+Tab from the wrap. The same set, so the stack is not
               a one-way street — a reader who has passed it can come back.
  ON STAGE     at every stop inside the stack, the stop's own card must be the
               one that is painted: computed opacity above zero and visibility
               `visible`. A handover that focused a link without bringing its
               card onto the stage would satisfy REACH and put the ring on a
               transparent card, which is the fault the sibling check exists
               for, re-arriving through this door.
  ORDER        the stops inside the stack arrive in document order. A stack
               walked out of order reads as one list and is another.

Both walks run at four viewports above the gate and two below it. Below the
gate nothing is hidden and nothing is intercepted, so those two are the control:
they must pass with the script absent, and CF_PIN_FOCUS_OFF is how this file
proves it fails on the defect — it strips the script tag from the page before
loading, and every viewport above the gate must then fail REACH.

    python3 scripts/check-pin-focus-walk.py
    CF_PIN_FOCUS_OFF=1 python3 scripts/check-pin-focus-walk.py   # must fail
"""

import argparse
import os
import re
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE_DIRS = [ROOT / "design-system/patterns", ROOT / "design-system/prototypes"]

# Same two places check-runtime.py looks; CF_BROWSER overrides everything.
BROWSER_CANDIDATES = [
    os.environ.get("CF_BROWSER"),
    "/opt/pw-browsers/chromium",
]

SETTLE_MS = 900      # load, fonts, the banner measured and published
STEP_MS = 60         # between Tab presses: one frame for the handover, and slack

# Four above the pin gate and two below it. The two below are the control: the
# cards are a column there, nothing is hidden and nothing is intercepted.
VIEWPORTS = [(1024, 900), (1280, 800), (1440, 900), (1920, 1080),
             (768, 1024), (375, 812)]

# Enough to wrap the longest of these pages twice over at any viewport.
MAX_PRESSES = 140

STEP = "cf-pin__step"
FOCUSABLE = re.compile(
    r"""<(?:a\s[^>]*\bhref=
         |button\b
         |select\b
         |textarea\b
         |input\b(?![^>]*\btype=["']?hidden)
         |[a-z]+\s[^>]*\btabindex=["']?(?!-))""",
    re.I | re.X)

# Mark every stop in the stack so a walk can name which one it is standing on
# without depending on link text, which is German prose and moves.
TAG_STOPS = """
() => {
  const sel = 'a[href],button:not([disabled]),input:not([disabled]),' +
              'select:not([disabled]),textarea:not([disabled]),[tabindex]';
  let n = 0;
  document.querySelectorAll('.cf-pin__step').forEach((step, s) => {
    step.querySelectorAll(sel).forEach(el => {
      if (el.tabIndex < 0) return;
      el.dataset.cfWalk = String(n++);
      el.dataset.cfWalkStep = String(s);
    });
  });
  return n;
}
"""

# Where focus is now, and — when it is inside the stack — whether the card it
# belongs to is the card on the stage.
WHERE = """
() => {
  const a = document.activeElement;
  if (!a || a === document.body) return { at: null, body: true };
  const id = a.dataset ? a.dataset.cfWalk : undefined;
  if (id === undefined) return { at: null, body: false };
  const step = a.closest('.cf-pin__step');
  const cs = getComputedStyle(step);
  return { at: Number(id), body: false,
           step: Number(a.dataset.cfWalkStep),
           opacity: Number(cs.opacity), visibility: cs.visibility };
}
"""


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def serve():
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def launch(playwright_ctx):
    try:
        return playwright_ctx.chromium.launch()
    except Exception:
        pass
    for candidate in BROWSER_CANDIDATES:
        if candidate and Path(candidate).exists():
            try:
                return playwright_ctx.chromium.launch(executable_path=candidate)
            except Exception:
                continue
    return None


def element_extent(html, start):
    """Slice from the tag opening at `start` to its own closing tag.

    Borrowed whole from check-pin-focus-stack.py, and for its reason: a step is
    an <article> among other <article>s, so a class-to-next-class slice runs the
    last step to the end of the document and counts the footer's links as its
    own.
    """
    tag = re.match(r"<([a-zA-Z][\w-]*)", html[start:]).group(1)
    pat = re.compile(rf"<(/?){tag}\b", re.I)
    depth = 0
    for m in pat.finditer(html, start):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return html[start:m.end()]
    return html[start:]


def loaded_steps(html):
    """How many .cf-pin__step elements on this page hold a focusable."""
    n = 0
    for m in re.finditer(rf'class="[^"]*\b{STEP}\b[^"]*"', html):
        start = html.rfind("<", 0, m.start())
        if start < 0:
            continue
        if FOCUSABLE.search(element_extent(html, start)):
            n += 1
    return n


def walk(page, back):
    """One pass of the document, from the wrap to the wrap.

    Focus starts on <body> — nowhere — so the first press enters the document
    at its first stop going forward and at its last going backward, which is
    where a reader's own walk starts from too. The pass ends when focus comes
    back to <body>, which is the document wrapping once.
    """
    key = "Shift+Tab" if back else "Tab"
    page.evaluate("() => {if (document.activeElement) document.activeElement.blur(); "
                  "window.scrollTo({top: 0, behavior: 'instant'});}")
    page.wait_for_timeout(200)
    reached = []
    off_stage = []
    entered = False
    for _ in range(MAX_PRESSES):
        page.keyboard.press(key)
        page.wait_for_timeout(STEP_MS)
        where = page.evaluate(WHERE)
        if where["body"]:
            if entered:
                break
            continue
        entered = True
        if where["at"] is None or where["at"] in reached:
            continue
        reached.append(where["at"])
        if where["opacity"] <= 0 or where["visibility"] != "visible":
            off_stage.append((where["at"], where["opacity"], where["visibility"]))
    return reached, off_stage


def probe(browser, url, rel, verbose, without):
    findings = []
    for width, height in VIEWPORTS:
        size = "%d x %d" % (width, height)
        context = browser.new_context(viewport={"width": width, "height": height})
        page = context.new_page()
        try:
            # PROVING IT FAILS ON THE DEFECT, without editing the tree: the fix
            # is one <script> tag, and a route that refuses to serve the file is
            # that tag removed. Every viewport above the gate must go red.
            if without:
                page.route("**/cf-pin-focus.js", lambda route: route.abort())

            page.goto(url, wait_until="load", timeout=30000)
            page.wait_for_timeout(SETTLE_MS)
            # Answer the banner and reload, so the walk is the page's own stops
            # and not a first visit's. A page without one is unchanged by this.
            page.evaluate("() => {const b = document.querySelector("
                          "'[data-cf-consent-action=\"accept\"]'); if (b) b.click();}")
            page.wait_for_timeout(250)
            page.reload(wait_until="load", timeout=30000)
            page.wait_for_timeout(SETTLE_MS)

            expected = page.evaluate(TAG_STOPS)
            if expected < 2:
                findings.append((rel, size, "REACH",
                                 "the file says this page ships a loaded .cf-pin stack and the "
                                 "browser found %d stop(s) in it — this check cannot see what it "
                                 "exists to check" % expected))
                continue

            forward, off_stage = walk(page, False)
            backward, off_back = walk(page, True)

            if len(forward) != expected:
                findings.append((rel, size, "REACH",
                                 "the forward Tab walk reached %d of the stack's %d stops. A link a "
                                 "pointer can open and a keyboard cannot reach is WCAG 2.1.1."
                                 % (len(forward), expected)))
            elif forward != sorted(forward):
                findings.append((rel, size, "ORDER",
                                 "the forward walk reached all %d stops out of document order: %s"
                                 % (expected, forward)))
            if len(backward) != expected:
                findings.append((rel, size, "BACK",
                                 "the backward Shift+Tab walk reached %d of the stack's %d stops. "
                                 "A stack a reader can only leave is a one-way street."
                                 % (len(backward), expected)))
            for at, opacity, visibility in off_stage + off_back:
                findings.append((rel, size, "ON STAGE",
                                 "stop %d took focus while its own card was at opacity %s and "
                                 "visibility %s — the ring is drawn on a card that is not on the "
                                 "stage, over the card the reader is looking at."
                                 % (at, opacity, visibility)))
            if verbose and not findings:
                print("  %-38s %-11s forward %d/%d  backward %d/%d"
                      % (rel, size, len(forward), expected, len(backward), expected))
        finally:
            context.close()
    return findings


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print each viewport's two counts")
    args = ap.parse_args()

    required = bool(os.environ.get("CF_REQUIRE_BROWSER"))

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        msg = "pin-focus-walk: SKIPPED — playwright is not installed (pip install playwright)."
        if required:
            print(msg + " CF_REQUIRE_BROWSER is set, so this is a failure.", file=sys.stderr)
            return 1
        print(msg + " The walk is unguarded on this machine; CI still gates it.")
        return 0

    without = bool(os.environ.get("CF_PIN_FOCUS_OFF"))

    pages = []
    skipped = []
    for directory in PAGE_DIRS:
        for path in sorted(directory.glob("*.html")):
            html = path.read_text(encoding="utf-8")
            if STEP not in html:
                continue
            if loaded_steps(html) > 1:
                pages.append(path)
            else:
                skipped.append(path.name)

    if not pages:
        print("pin-focus-walk: FAIL — no page ships a loaded .cf-pin stack, so this "
              "check has nothing to hold. Delete it or fix the glob.", file=sys.stderr)
        return 1

    server = serve()
    port = server.server_address[1]
    findings = []
    try:
        with sync_playwright() as ctx:
            browser = launch(ctx)
            if browser is None:
                msg = ("pin-focus-walk: SKIPPED — no Chromium found "
                       "(playwright install chromium, or CF_BROWSER).")
                if required:
                    print(msg + " CF_REQUIRE_BROWSER is set, so this is a failure.", file=sys.stderr)
                    return 1
                print(msg + " The walk is unguarded on this machine; CI still gates it.")
                return 0
            for path in pages:
                rel = path.relative_to(ROOT)
                url = "http://127.0.0.1:%d/%s" % (port, rel.as_posix())
                findings += probe(browser, url, str(rel), args.verbose, without)
            browser.close()
    finally:
        server.shutdown()

    if findings:
        for rel, size, kind, why in findings:
            print("%s  %s  [%s]\n    %s" % (rel, size, kind, why), file=sys.stderr)
        print("\n%d finding%s. A pinned stack that holds links has to hand the Tab walk "
              "across it, one card at a time, with each card on the stage as its own "
              "link takes focus." % (len(findings), "" if len(findings) == 1 else "s"),
              file=sys.stderr)
        return 1

    if without:
        print("pin-focus-walk: FAIL — CF_PIN_FOCUS_OFF withheld assets/js/cf-pin-focus.js "
              "and every walk still arrived. This check does not see the fault it exists "
              "for; it is passing on something other than what it claims.", file=sys.stderr)
        return 1

    print("pin-focus-walk: %d page(s) x %d viewports, both directions — every stop in "
          "every loaded .cf-pin stack takes focus, in order, with its own card on the "
          "stage%s" % (len(pages), len(VIEWPORTS),
                       "" if not skipped else "; %d stack(s) hold none and need nothing (%s)"
                       % (len(skipped), ", ".join(skipped))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
