/* Control-F — the way INTO a pinned card stack, for a reader who tabs.

   OPTIONAL, and a no-op on every page whose .cf-pin steps hold nothing to
   focus. Load it beside cf-pin-gate.js on a page whose pinned stack carries
   links. Today that is two pages and one stack: the landing page's act 4 and
   prototypes/evidence-scroll.html, the lab it was built in. With the tag
   removed the page is exactly what it was, which is the fault below.

   THE THIRD HALF OF A SENTENCE THAT HAS BEEN WRITTEN TWICE. A .cf-pin track
   stacks its cards in one grid area and shows one at a time on the track's
   view timeline, so three of four are transparent at every scroll position.
   Both halves of "hidden by paint is only honest if both halves are there"
   are now in acts.css: the card releases the POINTER over the interval it is
   not painted (lp-ev-card-hit) and it releases the FOCUS RING over the same
   interval on the same rule (lp-ev-card-seen, `visibility`). Neither is
   wrong. Together they make the whole act invisible to the Tab walk.

   `visibility: hidden` takes a subtree out of the sequential focus order,
   which is exactly what it is there for — a ring must not be drawn around a
   link on a card that is not on the stage. But which card is on the stage is
   a function of the SCROLL, and the walk that would reach those links starts
   at the top of the document, where the track's timeline is clamped at
   progress 0 and NO card is on the stage. So:

     - Sequential focus navigation begins at the start of the document. The
       starting point is null after a load and after a keyboard-only scroll;
       a click sets it, and a click is not how a keyboard reader moves.
     - The two in-flow stops before the track are the hero's still switch and
       the hero's one call to action, at document y 100 and y 750. Focusing
       either scrolls the viewport to the top of the page. Everything between
       them and the track — the nav, the language switch, the act rail — is
       `position: fixed`, so focusing those moves nothing.
     - By the time the walk arrives at the track it is therefore always at
       y 0, all four cards are `visibility: hidden`, and the next stop the
       browser can find is the footer's call to action.

   MEASURED, Chromium, consent already answered, one forward Tab walk from the
   first stop to the wrap and one backward walk from the wrap, counting how
   many of act 4's fourteen source links ever take focus:

                        forward        backward
       1024 x 900       0 of 14        2 of 14
       1280 x 800       0 of 14        2
       1440 x 900       0 of 14        2
       1920 x 1080      0 of 14        2
       768 x 1024      14 of 14       14          below the gate, stacked
       375 x 812       14 of 14       14
       1440 x 900      14 of 14       14          reduced motion, stacked

   The two the backward walk finds are card 04's, and it finds them for the
   one reason that proves the diagnosis: Shift+Tab from the wrap starts at the
   END of the document, where the track's timeline is clamped at progress 1
   and the last card is the one on the stage. Every tier that does NOT pin —
   below the gate, under prefers-reduced-motion, in a browser with no
   animation-timeline — lays the four cards out as a column, hides none of
   them, and hands over all fourteen. The fault is the pinned tier's alone,
   and it is WCAG 2.1.1: fourteen links a pointer can open and a keyboard
   cannot reach.

   WHY THERE IS NO CSS ANSWER, which was worth proving before writing a file.
   The chain would have to grant card N+1's links focus while the track is at
   card N's beat, so that the walk can step from one to the next. Focusing an
   element the browser considers off screen scrolls it into view, and that
   scroll is what would advance the beat — except that the four cards SHARE
   ONE GRID AREA inside a sticky stage. Card N+1's links are already in view,
   at the same coordinates as card N's. Nothing scrolls, the beat never
   advances, and the reader gets a ring on a transparent card: the fault
   lp-ev-card-seen exists to close. Granting the links focus ahead of the beat
   requires moving the scroll, and a stylesheet cannot move the scroll.

   WHAT THIS DOES. It carries the walk across the stack, one card per step,
   the way the reader would carry it themselves:

     ENTERING   the last stop before the track hands over to the first card
                — or, going backward, the first stop after the track hands
                over to the last card. Only when the walk would otherwise
                skip the track whole: if any card is on the stage its links
                are already in the order and the platform is left alone.
     STEPPING   the last link of the card on the stage hands over to the next
                card, and the first link hands back to the previous one.
     LEAVING    the last card's last link is not intercepted, so Tab falls
                through to the footer, and the first card's first link falls
                back to the rail. The track has two doors and both are the
                ones already in the document.

   A handover scrolls the track to the target card's own beat and then focuses
   its first link, so the card the reader is READING is the card whose source
   they are standing on. That is the whole of the behaviour: it never adds a
   stop, never removes one, and never reorders them.

   THE BEAT IS READ OFF THE STYLESHEET, NOT RESTATED HERE. Every step declares
   its own window — `animation-range: contain calc(var(--i) * 25% - 3%) ...`
   in components.css — and the computed value resolves to two plain
   percentages, `contain -3% contain 28%` for the first of four. The midpoint
   of that pair is the beat, and `contain` is the same length act-rail.js
   documents and jumps to:

       y(p) = top + p * (height - viewport)

   so a quarter re-timed in the stylesheet moves this with it, and a stack of
   three or five needs no edit here at all. Nothing in this file names a
   viewport, a width or a count. → scripts/check-script-gates.py

   THE TIER IS ASKED OF THE COMPUTED VALUE for the same reason: a step's
   `animation-timeline` is the stack's own `--cf-pin` in exactly the tier the
   cards are pinned in and `auto` in every tier they are not — below the gate,
   under reduce, and where there is no animation-timeline at all. That one
   read is the whole guard, so in every degraded tier this file listens and
   does nothing, which is correct: those tiers never lost the links.

   `behavior: 'instant'` on the scroll, against base.css's smooth default, and
   it is not an exception to that rule but an instance of it. This is the
   scroll the platform itself performs when Tab moves focus to something off
   screen, and the platform performs it instantly; the visibility the next
   focus depends on is a function of that scroll having landed. A smooth
   scroll here would put focus on a card that is still hidden.
   → scripts/check-pin-focus-walk.py */

(function () {
  'use strict';

  var FOCUSABLE = 'a[href],button:not([disabled]),input:not([disabled]),' +
                  'select:not([disabled]),textarea:not([disabled]),[tabindex]';

  /* A stop the walk can actually land on. `visibility` is the property the
     stack switches, and it inherits, so this is the same question the browser
     asks — read on the element rather than on its card, so a card hidden by
     any other means answers it too. */
  function reachable(el) {
    return el.tabIndex >= 0 &&
           el.getClientRects().length > 0 &&
           getComputedStyle(el).visibility !== 'hidden';
  }

  function stops(root) {
    return Array.prototype.filter.call(root.querySelectorAll(FOCUSABLE), reachable);
  }

  function precedes(el, other) {
    return !!(el.compareDocumentPosition(other) & Node.DOCUMENT_POSITION_FOLLOWING);
  }

  /* Only a stack with more than one LOADED step has a handover to make: one
     card's links are reachable whenever that card is on the stage, and a
     stack whose steps hold nothing — act 3's process cards — needs none of
     this. Same definition of "loaded" as scripts/check-pin-focus-stack.py. */
  var tracks = [];
  Array.prototype.forEach.call(document.querySelectorAll('.cf-pin'), function (el) {
    var steps = Array.prototype.filter.call(
      el.querySelectorAll('.cf-pin__step'),
      function (step) { return step.querySelectorAll(FOCUSABLE).length > 0; });
    if (steps.length > 1) tracks.push({ el: el, steps: steps });
  });
  if (!tracks.length) return;

  function pinned(track) {
    return getComputedStyle(track.steps[0]).animationTimeline.indexOf('--') === 0;
  }

  function beat(track, step) {
    var window_ = getComputedStyle(step).animationRange.match(/-?[\d.]+(?=%)/g);
    if (!window_ || window_.length < 2) return null;
    var p = (parseFloat(window_[0]) + parseFloat(window_[1])) / 200;
    var top = track.el.getBoundingClientRect().top + window.scrollY;
    var contain = Math.max(0, track.el.offsetHeight - window.innerHeight);
    var end = Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
    return Math.max(0, Math.min(Math.round(top + p * contain), end));
  }

  /* LIFT WHATEVER IS ACTUALLY HIDDEN, which is not always the step. The
     landing page's stack switches `visibility` on the .cf-pin__copy PANEL
     inside each card rather than on the card itself — the card stays
     `visible` at opacity 0 — so an override written on the step is
     overridden in turn by the panel's own animated value and buys nothing.
     Rather than name the panel here, each stop's ancestor chain is walked
     from the step down and every link in it that computes `hidden` at that
     moment is lifted. Lifting an outer one makes the ones inheriting from it
     compute `visible`, so what is left after the walk is exactly the elements
     that carry a hidden of their own. */
  function lift(step) {
    var lifted = [];
    var candidates = step.querySelectorAll(FOCUSABLE);
    for (var i = 0; i < candidates.length; i++) {
      if (candidates[i].tabIndex < 0) continue;
      var chain = [];
      for (var node = candidates[i]; node && node !== step.parentNode; node = node.parentNode) {
        chain.unshift(node);
      }
      for (var k = 0; k < chain.length; k++) {
        if (getComputedStyle(chain[k]).visibility === 'hidden') {
          chain[k].style.visibility = 'visible';
          lifted.push(chain[k]);
        }
      }
    }
    return lifted;
  }

  /* HAND THE STEP BACK TO ITS OWN KEYFRAMES WHEN FOCUS LEAVES IT, and not on
     a frame count.

     The first shape of this waited for the timeline to catch up — clear the
     lift on the first frame the card's own opacity says its keyframe holds it,
     give up after 30 — and the give-up is a focused element being hidden,
     which drops focus to <body> and ends the reader's walk. It was rare and it
     was real: two CI runs of scripts/check-pin-focus-walk.py, one cell each,
     the backward walk stopping early at 1440 x 900 and at 1920 x 1080, on a
     loaded runner, where nine local runs and CPU throttling at x4, x6, x10 and
     x20 all passed. A bound that is almost always enough is a bound.

     `focusout` has no bound and cannot lose. Focus leaving the step is exactly
     the moment the lift stops being needed, and it has already left when the
     event fires, so restoring the authored state can take nothing with it. A
     move WITHIN the step is not leaving — relatedTarget says so — and the
     listener is capturing so it hears focus leaving a shadow-less subtree
     whatever is between.

     WHAT IS ACCEPTED, and it is one keypress wide: a reader who scrolls away
     with focus still parked in the card leaves it lifted, so its links stay
     stops until they Tab. The card is transparent there and `visibility:
     visible` at `opacity: 0` paints nothing, so no ring is drawn on it — and
     the next Tab both clears the lift and is the press that would have found
     those stops. Against the alternative, which is dropping the reader
     entirely, that is not a close call. */
  function release(step, lifted) {
    if (!lifted.length) return;
    function clear(e) {
      if (e && e.relatedTarget && step.contains(e.relatedTarget)) return;
      step.removeEventListener('focusout', clear, true);
      for (var i = 0; i < lifted.length; i++) lifted[i].style.visibility = '';
    }
    step.addEventListener('focusout', clear, true);
  }

  /* THE FOCUS IS SYNCHRONOUS AND THE SCROLL FOLLOWS IT, which is the opposite
     of the obvious order and the only one that cannot drop the reader.

     A view timeline's progress is not visible to script in the frame the
     scroll happens in: measured, after `scrollTo({behavior:'instant'})` to a
     card's own beat, getComputedStyle still reports the PREVIOUS frame's
     visibility for all four steps, at 1440 x 900 and 1024 x 720. So scrolling
     first and focusing in a requestAnimationFrame is a Tab press whose focus
     lands one frame later — and on a frame slow enough that the timeline has
     not ticked, lands nowhere at all. That is not theoretical: it is one cell
     of scripts/check-pin-focus-walk.py going red on a loaded CI runner,
     backward walk at 1440 x 900, 0 of 14, while the same walk passed at every
     other viewport on the same run.

     Lifting the step's own visibility inline makes its links stops NOW, so the
     focus is placed inside the keydown that asked for it and preventDefault is
     only ever called on a press that actually moved the reader. The scroll
     then brings the card onto the stage in the same frame, and release() gives
     the property back as soon as the card's own keyframe holds it.

     preventScroll, because the beat is already exactly where it should be and
     the browser's own correction would move it. */
  function handover(track, i, back) {
    var step = track.steps[i];
    var y = beat(track, step);
    if (y === null) return false;

    var lifted = lift(step);
    var list = stops(step);
    if (!list.length) {
      for (var i = 0; i < lifted.length; i++) lifted[i].style.visibility = '';
      return false;
    }

    window.scrollTo({ top: y, behavior: 'instant' });
    list[back ? list.length - 1 : 0].focus({ preventScroll: true });
    release(step, lifted);
    return true;
  }

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Tab' || e.altKey || e.ctrlKey || e.metaKey) return;

    var a = document.activeElement;
    /* Focus on <body> is focus nowhere: the walk is about to start from the
       top of the document and the platform's answer is the right one. */
    if (!a || a === document.body) return;

    var back = e.shiftKey;

    for (var k = 0; k < tracks.length; k++) {
      var track = tracks[k];
      if (!pinned(track)) continue;

      var i = -1, s;
      for (s = 0; s < track.steps.length; s++) {
        if (track.steps[s].contains(a)) i = s;
      }

      /* STEPPING — off the edge of the card the reader is on. */
      if (i >= 0) {
        var own = stops(track.steps[i]);
        if (!own.length || a !== (back ? own[0] : own[own.length - 1])) continue;
        var next = back ? i - 1 : i + 1;
        /* The far end of the stack is not intercepted: the track's two doors
           are the stops the document already has on either side of it. */
        if (next < 0 || next >= track.steps.length) continue;
        if (handover(track, next, back)) { e.preventDefault(); return; }
        continue;
      }

      /* ENTERING — and only where the walk would step over the whole track.
         If any card is on the stage its links are in the order already. */
      if (stops(track.el).length) continue;

      var all = stops(document.body);
      if (all.indexOf(a) < 0) continue;
      var before = [], after = [];
      for (s = 0; s < all.length; s++) {
        (precedes(all[s], track.el) ? before : after).push(all[s]);
      }
      var door = back ? after[0] : before[before.length - 1];
      if (!door || a !== door) continue;
      if (handover(track, back ? track.steps.length - 1 : 0, back)) {
        e.preventDefault();
        return;
      }
    }
  }, true);
}());
