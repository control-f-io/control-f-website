#!/usr/bin/env python3
"""Answering the consent banner must not cost the reader the skip link.

The banner is the second stop on every page: skip link, then banner, then the
nav. cf-consent.js deliberately does NOT move focus into it on show, and the
argument is written out in showBanner's own comment — a focus move there buys
one Tab press and costs the first stop, because the skip link is BEFORE the
banner in the document and every forward Tab from inside the banner goes
further down the page. Its closing line is the rule this file enforces:

    A bypass block reachable only after the thing it exists to bypass is not a
    bypass block.

WHAT WENT WRONG. That reasoning closed the door the reader ARRIVES through and
left the door they LEAVE through open. A reader who answers the banner is
standing on a button that is about to be `hidden`, and a focused element that
disappears drops focus to <body> — with the sequential starting point left
where that button was, which is after the skip link. So the skip link was
reachable only by wrapping the entire document. Measured on the landing page in
Chromium, banner answered from the keyboard, counting forward Tab presses until
.skip-link takes focus:

    375 x 900     18 presses
    1280 x 900    29 presses

against 1 press on the return visit with the decision already stored. It is the
same fault showBanner names, arriving through the other door — and it is the
door every first-time reader uses, because answering the banner is the only way
past it.

Nothing caught it because it photographs correctly: the banner slides out, the
page is on screen, and focus is nowhere. It is not a paint fault and there is
no state in the DOM to compare — only a running browser, a real keypress and
the question "where is focus now" can show it.

WHAT IS CHECKED, per page that ships the banner, for each of its two decisions
("Nur notwendige" and "Alle akzeptieren"):

  KEYBOARD  focus the decision button, press Enter, and after the exit
            transition document.activeElement is the page's .skip-link. Enter
            on a focused button is what makes the browser call it
            :focus-visible, which is how cf-consent.js tells a keyboard reader
            from a pointer one.

  POINTER   a real click on the same button leaves focus alone. This is half
            the invariant and not a courtesy: .skip-link paints on :focus, so
            a handover that did not ask WHO answered would slide a black chip
            into the top left of every pointer reader's first visit. A fix that
            always focuses the skip link fails here.

  DESTINATION  the page has a .skip-link for focus to be handed to. The
            handover is only as real as the element it names; check-skip-target
            holds the href, this holds that there is one at all on the pages
            the banner ships with.

WHAT THIS DOES NOT CLAIM. Not that the skip link is the only defensible
destination — the top of <main> would satisfy a reader as well and would need
this file rewritten rather than deleted — and not anything about the settings
dialog, which is a real <dialog>.showModal() and keeps the APG contract on its
own: it moves focus in and hands it back to whatever opened it, and
cf-consent.js closes it before it hides the banner.

Needs playwright and a Chromium, and skips loudly without them, exactly as
check-runtime.py does. CF_REQUIRE_BROWSER=1 turns the skip into a failure,
which is how CI runs it.

    python3 scripts/check-consent-focus-return.py
"""

import argparse
import os
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = ROOT / "design-system" / "patterns"

# Same two places check-runtime.py looks; CF_BROWSER overrides everything.
BROWSER_CANDIDATES = [
    os.environ.get("CF_BROWSER"),
    "/opt/pw-browsers/chromium",
]

SETTLE_MS = 500      # after load, before the banner is answered
EXIT_MS = 700        # > --duration-base, so the exit has finished and hidden is set

DECISIONS = ("reject", "accept")

# The banner is on every page, so a handful of pages proves the script rather
# than the page. The landing page is the one the acts and the tall hero make
# hardest; the other two are an ordinary section page and the page whose footer
# is the banner's other entry point.
SAMPLE = ("landing-page.html", "expertise.html", "kontakt.html")

WHERE = """
() => {
  const a = document.activeElement;
  if (!a) return 'null';
  return a.tagName + '.' + String(a.className || '').split(' ')[0];
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


def fresh(browser, url):
    """A first visit: no stored decision, so the banner is shown."""
    context = browser.new_context(viewport={"width": 1280, "height": 900})
    page = context.new_page()
    page.goto(url, wait_until="load", timeout=30000)
    page.wait_for_timeout(SETTLE_MS)
    return context, page


def probe(browser, url, rel, verbose):
    findings = []

    # DESTINATION — and the banner is actually shown on a first visit.
    context, page = fresh(browser, url)
    try:
        has_skip = page.evaluate("() => !!document.querySelector('.skip-link')")
        shown = page.evaluate("() => {const b=document.querySelector('[data-cf-consent-banner]');"
                              "return !!b && !b.hidden;}")
        if not has_skip:
            findings.append((rel, "DESTINATION", "the page ships the consent banner and no .skip-link, "
                                                 "so there is nothing for the handover to name"))
        if not shown:
            findings.append((rel, "BANNER", "no visible [data-cf-consent-banner] on a first visit — "
                                            "this check cannot see what it exists to check"))
    finally:
        context.close()
    if findings:
        return findings

    for decision in DECISIONS:
        sel = "[data-cf-consent-action='%s']" % decision

        # KEYBOARD — Enter on a focused button is a :focus-visible activation.
        context, page = fresh(browser, url)
        try:
            page.focus(sel)
            page.keyboard.press("Enter")
            page.wait_for_timeout(EXIT_MS)
            landed = page.evaluate(WHERE)
            if landed != "A.skip-link":
                findings.append((rel, "KEYBOARD/" + decision,
                                 "answered from the keyboard and focus landed on %s, not the skip link. "
                                 "The reader has lost the bypass block for the rest of the visit." % landed))
            elif verbose:
                print("  %-24s %-8s keyboard -> %s" % (rel, decision, landed))
        finally:
            context.close()

        # POINTER — a real click must not paint the skip link into the corner.
        context, page = fresh(browser, url)
        try:
            page.click(sel)
            page.wait_for_timeout(EXIT_MS)
            landed = page.evaluate(WHERE)
            if landed == "A.skip-link":
                findings.append((rel, "POINTER/" + decision,
                                 "answered with the pointer and focus was moved to the skip link, which "
                                 "paints on :focus — a pointer reader is shown a control they did not ask "
                                 "for. The handover has to ask who answered."))
            elif verbose:
                print("  %-24s %-8s pointer  -> %s" % (rel, decision, landed))
        finally:
            context.close()

    return findings


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print where focus landed on each path")
    args = ap.parse_args()

    required = bool(os.environ.get("CF_REQUIRE_BROWSER"))

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        msg = "consent-focus-return: SKIPPED — playwright is not installed (pip install playwright)."
        if required:
            print(msg + " CF_REQUIRE_BROWSER is set, so this is a failure.", file=sys.stderr)
            return 1
        print(msg + " The handover is unguarded on this machine; CI still gates it.")
        return 0

    pages = [PATTERNS / name for name in SAMPLE]
    missing = [p for p in pages if not p.exists()]
    if missing:
        for p in missing:
            print("consent-focus-return: %s is in SAMPLE and not in the tree" % p.relative_to(ROOT),
                  file=sys.stderr)
        return 1

    server = serve()
    port = server.server_address[1]
    findings = []
    try:
        with sync_playwright() as ctx:
            browser = launch(ctx)
            if browser is None:
                msg = "consent-focus-return: SKIPPED — no Chromium found (playwright install chromium, or CF_BROWSER)."
                if required:
                    print(msg + " CF_REQUIRE_BROWSER is set, so this is a failure.", file=sys.stderr)
                    return 1
                print(msg + " The handover is unguarded on this machine; CI still gates it.")
                return 0
            for path in pages:
                rel = path.relative_to(ROOT)
                url = "http://127.0.0.1:%d/%s" % (port, rel.as_posix())
                findings += probe(browser, url, str(rel), args.verbose)
            browser.close()
    finally:
        server.shutdown()

    if findings:
        for rel, kind, why in findings:
            print("%s [%s]\n    %s" % (rel, kind, why), file=sys.stderr)
        print("\n%d finding%s. Answering the consent banner from the keyboard hands focus to the "
              "skip link; answering it with the pointer leaves focus alone."
              % (len(findings), "" if len(findings) == 1 else "s"), file=sys.stderr)
        return 1

    print("consent-focus-return: %d pages x 2 decisions x 2 input paths — the keyboard gets the "
          "skip link back, the pointer is left alone." % len(pages))
    return 0


if __name__ == "__main__":
    sys.exit(main())
