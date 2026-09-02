#!/usr/bin/env python3
"""Every pattern page must run clean in a real browser, not merely read clean.

The one check in this directory that opens the pages instead of reading them.
Some ninety siblings parse the files — grammar, ids, headings, contrast,
tokens, tracks — and between them they have made the *static* fault classes of
design-system/patterns/ close to extinct. But four of this system's fault
classes do not exist in a file at all. They exist only in a browser, at
runtime, after the scripts have run, and until this check nothing here had a
browser to see them with. Four when it was written and five now — the fifth
is the one that needs two scroll positions rather than one:

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
                construct at runtime. A request the server ANSWERED and the
                page then abandoned is not one of these; see the note over
                `on_request_failed`.
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
  TIMELINE      a scroll-driven animation whose clock does not run. This is
                the quietest fault in the system and it is the fifth class
                because foundations/motion.html asked for it in prose:
                "getAnimations() reports a frozen timeline and a running one
                identically", and "nothing on screen to distinguish it from an
                animation that had never been written — which is what makes
                this worth a warning rather than a sentence." This is the
                warning. A view timeline resolves against its subject's
                NEAREST scroll container, and overflow: hidden makes an
                element one whether or not anything ever scrolls inside it —
                so a crop written for a picture silently hands every timeline
                beneath it a box that never moves. The glass button's rim pass
                shipped that way inside .cf-hero: a live ViewTimeline whose
                progress sat at 0.116 at every scroll position on the page.
                The fix was overflow: clip, and the fix was found by hand.

WHY A SINGLE READING CANNOT SEE IT, which is the whole reason this class
belongs in a browser and not in a file. Every property a static check could
read is correct in the frozen case: the @supports gate matched, the
animation-timeline resolved, the keyframes are there, the animation exists,
its playState is "running", and its currentTime is a number. The one thing
that is wrong is that the number is the SAME number at every scroll position
on the page — so the fault is not a value, it is the absence of a difference
between two values, and nothing that opens the page once can hold two. The
sweep below already visits every scroll position this needs; watching the
clocks on the way costs one property read per animation per step.

WHAT FOUND THIS. A full runtime sweep of the fourteen pattern pages — every
console message, every network failure, a keyboard walk, axe-core, the consent
flow, the nav disclosure, reduced-motion emulation — found them CLEAN: zero
console events, zero failed requests, zero axe violations, zero running
animations under reduce. Fourteen clean pages and no gate is the same
non-fact check-markup.py's header names: a dozen routines edit these files
every hour, and the classes above are precisely the ones a routine ships
without noticing, because they are invisible in every diff and every file
read.

THE HERO VIDEO WAS THIS GATE'S ONE HONEST LIMITATION AND IS NOW ITS ONE
BROWSER-DEPENDENT ONE. This paragraph used to read "the hero video cannot be
*played* under this gate, because Playwright's Chromium ships no H.264
decoder — hero-abstract-art.mp4 sits at readyState 0 with no error and no
console entry there." That is true of some runners and false of others.
Measured on patterns/landing-page.html, default visit, three loads per build,
the same page and the same file:

    Chromium 141.0.7390.37  (Playwright build 1194)   net 3  ready 0  paused
    Chromium 151.0.7922.34  (Playwright build 1234)   net 1  ready 4  playing

So the decoder arrived somewhere between the two, and the newer build is what
`playwright install chromium` fetches for CI today. On it the loop really runs
here, which means the MOTION class's "a <video> is playing under reduce" has
stopped passing vacuously: under reduce the `<source media>` selects nothing,
currentSrc stays empty, only hero-poster.jpg is requested and the element is
`display: none` behind its sibling <img> — measured, not assumed. Playback
beyond that is still check-hero-video.py's, as far as a file allows.

What the OLDER build leaves behind is an abandoned request, and that is the
case the note over `on_request_failed` is written against.

HOW IT CHECKS. The repository root is served over HTTP in-process (the pages
refuse file:// — module scripts and fetch would too) and headless Chromium
visits every design-system/patterns/*.html twice: once as the default
visitor, once with prefers-reduced-motion: reduce emulated. Each visit is a
fresh browser context — empty localStorage, so the consent banner's
first-visit path, the only path a new reader gets, is the path exercised.
The page is loaded, allowed to settle, scrolled end to end in steps — with
`behavior: 'instant'`, for the reason below, so the sweep arrives where it
says it does and the scroll-bound scripts do their work on the way — and
every console message of
severity warning or error, every uncaught page error, every failed request
and every response of 400 and above is a finding. Under reduce, any
Animation still in playState "running" after the scroll settles is a
finding, so is an unpaused <video>, and so is a <video> that selected a
source at all — the loop is meant to be withheld from that reader, not
merely held still. In both passes, any id carried by two elements of the
settled DOM is a finding.

The timeline pass rides that same sweep and only in the DEFAULT visit, which
is not a saving but the correct scope: every scroll-driven animation in this
system is written inside (prefers-reduced-motion: no-preference), so under
reduce there is nothing to watch and a frozen clock there is the design. The
default visit takes a reference to every animation whose timeline is not the
DocumentTimeline, reads timeline.currentTime once per scroll step, and a
timeline that reported one single value across the whole page — or null at
every step, which is a timeline that found no scroller at all — is a finding.
One value at forty scroll positions is not a clock.

THE FIRST THING THE TIMELINE CLASS FOUND WAS THIS FILE. On its first run it
reported five frozen clocks on /suche and five on /news, and the obvious
reading was a false positive: those pages are short, a short page cannot
scroll, and a timeline on a page that cannot scroll is parked rather than
broken. That reading was wrong, and the measurement that showed it was wrong
is the one worth keeping — window.scrollY after each step of the sweep:

    /suche       asked for 0, 700          reached 0, 2
    /news        asked for 0, 700, 1400    reached 0, 0, 2
    /suche-leer  asked for 0, 700, 1400    reached 0, 0, 0

base.css sets `scroll-behavior: smooth` on the root, which every page in this
system therefore carries. `window.scrollTo(0, y)` under that declaration does
not move the page; it STARTS an animation towards y, and the sweep's own 40 ms
between steps is a fraction of one. So the sweep did not scroll the pages. It
nudged them by two pixels and read the top of every one, and it had done that
since the day it was written, in both passes, for all five classes — the
console, the requests and the reduced-motion reading are all documented above
as "after a full scroll" and none of them had ever had one. Nothing showed it
because a page that is never scrolled reports no fault of any kind. The sweep
now scrolls with `behavior: 'instant'`, which overrides the CSS per call and
leaves the reader's smooth scrolling exactly where it was, and every page in
the tree reaches its own end. With that fixed, no page in this repository has
a frozen clock and none is short enough to be exempt either.

THE ONE EXEMPTION IS GEOMETRY, NOT A LIST OF NAMES, and it fires on nothing
today. A page genuinely shorter than the viewport — a 404, an empty result,
some future thank-you page — has no scroll range at all, so every timeline
sourced on its document is parked for a reason that has nothing to do with a
crop, and the parked state is what a reader of that page is designed to get.
A frozen timeline is therefore excused only when its SOURCE is the document's
own scrolling element AND that element has no scroll range. A timeline sourced
on anything else is never excused, which is what keeps the exemption from
swallowing the class: .cf-hero under `overflow: hidden` is precisely a source
with no scroll range, and it is the defect this exists for. The verbose line
says when a page was excused and how many clocks it parked, so an exemption
that starts firing cannot do so silently.

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

Proven failing on reintroduced instances of all five classes: a script
dereferencing a querySelector miss (CONSOLE), a poster pointing at a file
that is not there (REQUEST), an infinite keyframe loop outside the reduce
guard (MOTION), cf-icons.js's sprite guard removed (RUNTIME-ID), and the
original defect itself put back — the `overflow: clip` line deleted from
.cf-hero so the `overflow: hidden` beneath it stands alone again (TIMELINE).

The sourced-video half of MOTION was proven the same way, by deleting the
`media="(prefers-reduced-motion: no-preference)"` attribute from the hero's
<source> so the loop is selected for every reader:

    design-system/patterns/landing-page.html [reduce]
        MOTION: 1 <video> element(s) selected a source under
        prefers-reduced-motion: reduce — the loop was fetched for a reader
        who asked for the still

AND THE OTHER HALF DID NOT FIRE ON IT, which is the argument for having both.
That run was on build 1194, where the file cannot be decoded: the loop was
requested in full, `paused` stayed true because nothing could play it, and the
"a <video> is playing" line said nothing. A regression that hands a
reduced-motion reader 3.3 MB is invisible to a runner without the decoder and
visible to one with it — so the assertion that holds it has to be about
selection, not about playback. Both are kept: the newer build's playing loop
is caught by the first line, the older build's fetched-but-frozen one by the
second, and neither runner can pass the pair on a page that has given the
guard up. The original TIMELINE report:

    design-system/patterns/landing-page.html [default]
        TIMELINE: 1 scroll-driven animation(s) on a ViewTimeline that never
        advanced — held at 12.6816 across the whole page.
        scroller: header#anfang.cf-hero
        subject(s): a.cf-btn.cf-btn--glass.cf-btn--wide (cf-glass-rim-pass)

The scroller line is the deliverable. The animation is not what is wrong with
it — .cf-glass-rim's own declarations are all correct and were correct while
it shipped broken — so a report that named only the subject would send the
next reader to the wrong file. The element that has to change is the one
holding the crop, and it can be several boxes up the tree from the animation
it silences.
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
  // NOT PLAYING IS THE WEAKER HALF OF WHAT THE HERO PROMISES. A paused loop
  // still costs the reader who asked for reduce the whole file, and "paused"
  // is also what a browser with no decoder for it reports — so on such a
  // runner the check above passes whether the page withheld the loop or sent
  // it. currentSrc is the half that is decided by resource selection rather
  // than by codecs: a <source> whose media does not match is skipped, and a
  // <video> that selected nothing reports the empty string on every browser.
  // Empty here is the measured state of the hero under reduce, and it is the
  // sentence foundations/motion.html writes — "only the still is shown, and
  // only the still is fetched" — asserted rather than restated.
  const sourcedVideo = Array.from(document.querySelectorAll('video'))
    .filter(v => v.currentSrc).length;
  return { dupes, running, playingVideo, sourcedVideo };
}
"""

# `behavior: 'instant'` is load-bearing and not a preference. base.css declares
# `scroll-behavior: smooth` on the root, so a bare window.scrollTo(0, y) starts
# an animation towards y rather than arriving at it, and 40 ms later the page
# has moved single-digit pixels. Measured before the fix: /news asked for 0,
# 700 and 1400 and reached 0, 0 and 2. The option overrides the declaration for
# this call only, so the reader's smooth scrolling is untouched and the sweep
# actually visits the positions it names.
SCROLL = """
async (maxSteps) => {
  const h = document.documentElement.scrollHeight;
  const step = Math.max(700, Math.ceil(h / maxSteps));
  for (let y = 0; y <= h; y += step) {
    window.scrollTo({ top: y, left: 0, behavior: 'instant' });
    await new Promise(r => setTimeout(r, 40));
  }
  window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
}
"""

# The same sweep, watching the clocks on the way. References to the animations
# are taken ONCE and held across the whole scroll: document.getAnimations()
# returns a fresh list in an order that is not promised to be stable, so
# sampling it twice and pairing by index would compare one animation's clock
# against another's. Holding the objects is what makes the two readings two
# readings of the same thing.
#
# `t.currentTime` is a CSSNumericValue on a scroll or view timeline and a plain
# number on nothing else here, so both shapes are read. null is kept as a
# distinct value rather than skipped — a timeline that is null at every step
# found no scroller at all, which is the same fault one step further along.
SCROLL_WATCHING = """
async (maxSteps) => {
  const driven = document.getAnimations().filter(
    a => a.timeline && !(a.timeline instanceof DocumentTimeline));
  const read = a => {
    const c = a.timeline && a.timeline.currentTime;
    if (c === null || c === undefined) return null;
    return typeof c === 'number' ? c : c.value;
  };
  const seen = driven.map(a => new Set([read(a)]));
  const h = document.documentElement.scrollHeight;
  const step = Math.max(700, Math.ceil(h / maxSteps));
  for (let y = 0; y <= h; y += step) {
    window.scrollTo({ top: y, left: 0, behavior: 'instant' });
    await new Promise(r => setTimeout(r, 40));
    for (let i = 0; i < driven.length; i++) seen[i].add(read(driven[i]));
  }
  window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
  const name = el => {
    if (!el || !el.tagName) return '(none)';
    const cls = el.getAttribute && el.getAttribute('class');
    return (el.tagName.toLowerCase()
            + (el.id ? '#' + el.id : '')
            + (cls ? '.' + cls.trim().split(/\\s+/).join('.') : '')).slice(0, 90);
  };
  // THE ONE EXEMPTION, AND IT IS GEOMETRY RATHER THAN A LIST. A page shorter
  // than the viewport has no scroll range at all, so every timeline sourced on
  // the document is parked there for a reason that is nothing to do with a
  // crop: there is no scroll to be driven by. No page in this repository is
  // that short today — see the docstring on why it once looked as though four
  // were — and a timeline sourced on any OTHER element is never exempt, which
  // is the whole point: .cf-hero with `overflow: hidden` has exactly this
  // shape, a source with no scroll range, and it is the defect this class
  // exists for.
  const root = document.scrollingElement || document.documentElement;
  const rootIsStill = root.scrollHeight <= root.clientHeight + 1;
  const frozen = [];
  let parked = 0;
  for (let i = 0; i < driven.length; i++) {
    if (seen[i].size > 1) continue;
    if (rootIsStill && driven[i].timeline.source === root) { parked++; continue; }
    const held = Array.from(seen[i])[0];
    frozen.push({
      animation: driven[i].animationName || '(unnamed)',
      timeline: driven[i].timeline.constructor.name,
      subject: name(driven[i].effect && driven[i].effect.target),
      source: name(driven[i].timeline.source),
      held: held === null ? null : Math.round(held * 1e4) / 1e4,
    });
  }
  return { driven: driven.length, frozen, parked, rootIsStill };
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


def group_frozen(frozen):
    """Frozen clocks by the scroller that froze them, subjects in page order."""
    grouped = {}
    for f in frozen:
        grouped.setdefault((f["timeline"], f["source"], f["held"]), []).append(
            "%s (%s)" % (f["subject"], f["animation"]))
    return grouped


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

    # A REQUEST THE SERVER ANSWERED AND THE PAGE THEN WALKED AWAY FROM IS NOT A
    # DEAD REQUEST, and telling the two apart is what keeps this class from
    # being a property of the runner's codec licence rather than of the page.
    #
    # THE CASE. The hero's <video> is the only element in the tree that can
    # abandon a resource it has already been given. On a Chromium with no H.264
    # decoder the media element runs the resource selection algorithm, is handed
    # the file, finds nothing it can play, and gives up — and giving up cancels
    # the fetch that is still running. Measured on patterns/landing-page.html,
    # three loads, deterministic on both binaries of build 1194:
    #
    #     request   GET hero-abstract-art.mp4    Range: bytes=0-
    #     response  200                          the whole file, served
    #     then      net::ERR_ABORTED             networkState 3, readyState 0,
    #                                            video.error null
    #
    # networkState 3 is NETWORK_NO_SOURCE: no candidate was usable. Nothing
    # about that is a fault of the page — it is the codec-less browser reaching
    # the poster fallback the hero is designed around — and on build 1234 the
    # same page produces no failed request at all, because there the file plays.
    # A gate that is red on one runner and green on the next teaches every
    # routine to read past it, which costs more than the class is worth.
    #
    # THE RULE IS THE DISTINCTION, NOT THE FILENAME. Nothing here names the
    # video, the media type or the URL: an ERR_ABORTED whose request carries a
    # response below 400 had its bytes delivered, so whatever else went wrong,
    # the resource arrived. ERR_ABORTED with NO response — cancelled before any
    # header, blocked, or refused — is still a finding, and so is every other
    # failure code.
    #
    # AND IT TAKES NOTHING OFF THE CLASS'S TEETH, because a missing file never
    # arrives here in the first place. Measured against this same server, with
    # an <img> and a <video> pointed at files that do not exist: both produced
    # `http-404` response events and NO requestfailed at all. The proven-failing
    # instance this class was built on — "a poster pointing at a file that is
    # not there" — is held entirely by the 4xx handler below, which this does
    # not touch.
    def on_request_failed(request):
        failure = request.failure or ""
        if failure == "net::ERR_ABORTED":
            try:
                response = request.response()
            except Exception:
                response = None
            if response is not None and response.status < 400:
                return
        events.append(("requestfailed", "%s :: %s" % (request.url, failure)))

    page.on("requestfailed", on_request_failed)
    page.on("response", lambda r: events.append(("http-%d" % r.status, r.url))
            if r.status >= 400 else None)

    mode = "reduce" if reduced else "default"
    try:
        page.goto(url, wait_until="load", timeout=30000)
        page.wait_for_timeout(SETTLE_MS)
        if reduced:
            clocks = {"driven": 0, "frozen": [], "parked": 0, "rootIsStill": False}
            page.evaluate(SCROLL, SCROLL_STEPS_MAX)
        else:
            clocks = page.evaluate(SCROLL_WATCHING, SCROLL_STEPS_MAX)
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
    if reduced and state["sourcedVideo"]:
        findings.append((rel, mode,
                         "MOTION: %d <video> element(s) selected a source under "
                         "prefers-reduced-motion: reduce — the loop was fetched for a "
                         "reader who asked for the still" % state["sourcedVideo"]))

    # One clipping ancestor freezes every timeline beneath it, so the finding is
    # reported per SCROLLER rather than per animation: forty lines naming forty
    # animations would bury the one element that has to change.
    for (kind, source, held), subjects in group_frozen(clocks["frozen"]).items():
        shown = ", ".join(subjects[:3]) + (" …" if len(subjects) > 3 else "")
        at = "no scroller — currentTime was null at every step" \
            if held is None else "held at %s across the whole page" % held
        findings.append((rel, mode,
                         "TIMELINE: %d scroll-driven animation(s) on a %s that never "
                         "advanced — %s.\n    scroller: %s\n    subject(s): %s"
                         % (len(subjects), kind, at, source, shown)))

    if verbose:
        print("  %-28s %-8s events=%d anims=%d dupes=%d driven=%d frozen=%d%s"
              % (rel, mode, len(events), state["running"], len(state["dupes"]),
                 clocks["driven"], len(clocks["frozen"]),
                 "  (page does not scroll; %d parked)" % clocks["parked"]
                 if clocks["rootIsStill"] else ""))
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
              "id, every scroll-driven clock advancing, and nothing moving — or even "
              "fetched to move — for a reader who asked for reduce."
              % (len(findings), "" if len(findings) == 1 else "s"), file=sys.stderr)
        return 1

    print("runtime: %d pages visited twice each — console silent, every request "
          "answered, ids unique after scripts, every scroll-driven timeline live, "
          "nothing running and no loop even fetched under reduce." % len(pages))
    return 0


if __name__ == "__main__":
    sys.exit(main())
