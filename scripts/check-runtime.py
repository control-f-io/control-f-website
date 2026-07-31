#!/usr/bin/env python3
"""Every pattern page must run clean in a real browser, not merely read clean.

The one check in this directory that opens the pages instead of reading them.
Some ninety siblings parse the files — grammar, ids, headings, contrast,
tokens, tracks — and between them they have made the *static* fault classes of
design-system/patterns/ close to extinct. But four of this system's fault
classes do not exist in a file at all. They exist only in a browser, at
runtime, after the scripts have run, and until this check nothing here had a
browser to see them with:

  CONSOLE       an uncaught exception, a console.error, a console.warn. The
                classic shape is a script written on one page and shipped to
                eleven: a querySelector that finds its element on the page it
                was demoed on returns null on the other ten, and the next
                line dereferences it. The page renders; the feature below the
                throw silently does not exist; no file shows it, because the
                file is correct on the page it was written for.
  REQUEST       a resource that fails to arrive — a 404 poster, a misspelled
                video path, a stylesheet that moved. check-links.py proves
                every *reference in the markup* lands on a file, but only a
                browser issues the requests a page's scripts and CSS
                construct at runtime.
  MOTION        prefers-reduced-motion honoured in fact rather than in
                declaration. The stylesheets' reduce paths are static text;
                whether any animation still RUNS under reduce is a question
                about document.getAnimations() after load and a full scroll,
                and it has exactly this system's failure shape: a loop that
                keeps playing for the reader who asked it to stop renders
                pixel-identical for everyone else.
  RUNTIME-ID    a duplicate id that exists only after scripts run.
                check-a11y.py proves the FILES carry no duplicate — but
                cf-icons.js appends an icon sprite to the body, and all
                fourteen pages now carry the same sprite inline. Today the
                script checks before appending and the runtime DOM is clean;
                the day that guard is lost, every id in the icon set is
                duplicated on five pages and no static check can ever see it.

WHAT FOUND THIS. A full runtime sweep of the fourteen pattern pages — every
console message, every network failure, a keyboard walk, axe-core, the consent
flow, the nav disclosure, reduced-motion emulation — found them CLEAN: zero
console events, zero failed requests, zero axe violations, zero running
animations under reduce. Fourteen clean pages and no gate is the same
non-fact check-markup.py's header names: a dozen routines edit these files
every hour, and the classes above are precisely the ones a routine ships
without noticing, because they are invisible in every diff and every file
read. The sweep also found the one honest limitation: the hero video cannot
be *played* under this gate, because Playwright's Chromium ships no H.264
decoder — hero-abstract-art.mp4 sits at readyState 0 with no error and no
console entry there. The poster fallback is what such a browser shows, which
is the page's own designed answer; playback is checked by check-hero-video.py
as far as a file allows, and is out of scope here.

HOW IT CHECKS. The repository root is served over HTTP in-process (the pages
refuse file:// — module scripts and fetch would too) and headless Chromium
visits every design-system/patterns/*.html twice: once as the default
visitor, once with prefers-reduced-motion: reduce emulated. Each visit is a
fresh browser context — empty localStorage, so the consent banner's
first-visit path, the only path a new reader gets, is the path exercised.
The page is loaded, allowed to settle, scrolled end to end in steps (the
scroll-bound scripts do their work on the way), and every console message of
severity warning or error, every uncaught page error, every failed request
and every response of 400 and above is a finding. Under reduce, any
Animation still in playState "running" after the scroll settles is a
finding, and so is an unpaused <video>. In both passes, any id carried by
two elements of the settled DOM is a finding.

WHAT IT DOES NOT CHECK, and why the boundary is where it is. Only
patterns/ — the same line check-a11y.py draws: those files are the pages a
visitor is given; foundations/ and components/ are documentation chrome with
its own script, and holding the manual to the product's gate would teach
routines to route around the gate. And it does not click: the consent
decision, the nav disclosure and the dialog were walked by hand in the sweep
above, and a click path in CI is where a gate becomes a flake. Load, scroll,
settle, read — everything asserted here is deterministic.

THE DEPENDENCY, stated rather than hidden. This is the one check that is not
stdlib-only: it needs playwright and a Chromium. Where neither can be found
the check prints SKIPPED and exits 0 — a routine's local gate loop must not
break on a machine without a browser — EXCEPT when CF_REQUIRE_BROWSER is set,
which .github/workflows/design-system.yml sets after installing the browser,
so the gate that cannot be dodged is CI. A skip is printed loudly: a silent
pass and a skip must never look alike.

    python3 scripts/check-runtime.py        # check, exit 1 on a finding
    python3 scripts/check-runtime.py -v     # per-page event counts as it runs

Proven failing on reintroduced instances of all four classes: a script
dereferencing a querySelector miss (CONSOLE), a poster pointing at a file
that is not there (REQUEST), an infinite keyframe loop outside the reduce
guard (MOTION), and cf-icons.js's sprite guard removed (RUNTIME-ID).
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

# Where a Chromium may live when playwright's own download is absent. The
# remote sessions this repository is groomed from pre-install one and export
# its path in the first entry; CF_BROWSER overrides everything.
BROWSER_CANDIDATES = [
    os.environ.get("CF_BROWSER"),
    "/opt/pw-browsers/chromium",
]

SETTLE_MS = 500          # after load and after the scroll, before reading
SCROLL_STEPS_MAX = 40    # a long page scrolls in larger strides, not longer

COLLECTOR = """
() => {
  const dupes = [];
  const seen = Object.create(null);
  for (const el of document.querySelectorAll('[id]')) {
    if (seen[el.id]) dupes.push(el.id); else seen[el.id] = true;
  }
  const running = document.getAnimations().filter(a => a.playState === 'running').length;
  const playingVideo = Array.from(document.querySelectorAll('video'))
    .some(v => !v.paused && !v.ended);
  return { dupes, running, playingVideo };
}
"""

SCROLL = """
async (maxSteps) => {
  const h = document.documentElement.scrollHeight;
  const step = Math.max(700, Math.ceil(h / maxSteps));
  for (let y = 0; y <= h; y += step) {
    window.scrollTo(0, y);
    await new Promise(r => setTimeout(r, 40));
  }
  window.scrollTo(0, 0);
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


def visit(browser, url, reduced, verbose, rel):
    """One page under one motion setting. Returns a list of findings."""
    findings = []
    events = []
    context = browser.new_context(viewport={"width": 1440, "height": 900},
                                  reduced_motion="reduce" if reduced else "no-preference")
    page = context.new_page()
    page.on("console", lambda m: events.append(("console-" + m.type, m.text))
            if m.type in ("error", "warning") else None)
    page.on("pageerror", lambda e: events.append(("pageerror", str(e))))
    page.on("requestfailed", lambda r: events.append(("requestfailed", "%s :: %s" % (r.url, r.failure))))
    page.on("response", lambda r: events.append(("http-%d" % r.status, r.url))
            if r.status >= 400 else None)

    mode = "reduce" if reduced else "default"
    try:
        page.goto(url, wait_until="load", timeout=30000)
        page.wait_for_timeout(SETTLE_MS)
        page.evaluate(SCROLL, SCROLL_STEPS_MAX)
        page.wait_for_timeout(SETTLE_MS)
        state = page.evaluate(COLLECTOR)
    except Exception as exc:
        findings.append((rel, mode, "the visit itself failed: %s" % exc))
        context.close()
        return findings

    for kind, text in events:
        findings.append((rel, mode, "%s: %s" % (kind, text[:300])))
    for dupe in state["dupes"]:
        findings.append((rel, mode, "RUNTIME-ID: id \"%s\" on two elements of the settled DOM" % dupe))
    if reduced and state["running"]:
        findings.append((rel, mode,
                        "MOTION: %d animation(s) still running under prefers-reduced-motion: reduce"
                        % state["running"]))
    if reduced and state["playingVideo"]:
        findings.append((rel, mode, "MOTION: a <video> is playing under prefers-reduced-motion: reduce"))

    if verbose:
        print("  %-28s %-8s events=%d anims=%d dupes=%d"
              % (rel, mode, len(events), state["running"], len(state["dupes"])))
    context.close()
    return findings


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print per-page event counts as pages are visited")
    args = ap.parse_args()

    required = bool(os.environ.get("CF_REQUIRE_BROWSER"))

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        msg = "runtime: SKIPPED — playwright is not installed (pip install playwright)."
        if required:
            print(msg + " CF_REQUIRE_BROWSER is set, so this is a failure.", file=sys.stderr)
            return 1
        print(msg + " The runtime classes are unguarded on this machine; CI still gates them.")
        return 0

    pages = sorted(PATTERNS.glob("*.html"))
    if not pages:
        print("runtime: no pages under %s" % PATTERNS, file=sys.stderr)
        return 1

    server = serve()
    port = server.server_address[1]
    findings = []
    try:
        with sync_playwright() as ctx:
            browser = launch(ctx)
            if browser is None:
                msg = "runtime: SKIPPED — no Chromium found (playwright install chromium, or CF_BROWSER)."
                if required:
                    print(msg + " CF_REQUIRE_BROWSER is set, so this is a failure.", file=sys.stderr)
                    return 1
                print(msg + " The runtime classes are unguarded on this machine; CI still gates them.")
                return 0
            for path in pages:
                rel = path.relative_to(ROOT)
                url = "http://127.0.0.1:%d/%s" % (port, rel.as_posix())
                for reduced in (False, True):
                    findings += visit(browser, url, reduced, args.verbose, str(rel))
            browser.close()
    finally:
        server.shutdown()

    if findings:
        for rel, mode, why in findings:
            print("%s [%s]\n    %s" % (rel, mode, why), file=sys.stderr)
        print("\n%d finding%s only a running page can show. Every pattern page loads, "
              "scrolls and settles with a silent console, no dead request, no duplicate "
              "id, and nothing moving for a reader who asked for reduce."
              % (len(findings), "" if len(findings) == 1 else "s"), file=sys.stderr)
        return 1

    print("runtime: %d pages visited twice each — console silent, every request "
          "answered, ids unique after scripts, nothing running under reduce."
          % len(pages))
    return 0


if __name__ == "__main__":
    sys.exit(main())
