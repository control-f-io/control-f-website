/* Control-F — the act rail: where you are in the five acts, and a way into any
   of them without scrolling to it.

   WHY A SCRIPT AT ALL, on a composition that is otherwise pure CSS. Two of the
   rail's three jobs cannot be written as declarations.

     THE JUMP. Four of the five acts begin at an element and could be plain
     anchors. Act 2 does not: acts 1 and 2 share one 640vh track and one
     timeline, and the confluence begins at contain 36 % of it — a scroll
     position, not a box. There is nothing to put an id on. The same is true of
     act 3 from the other side: its heading, "Was wir machen", lives at the
     bottom of act 2's STICKY stage, so the heading's document position is not
     where the cards are and a native anchor lands on the wrong act.

     THE MARK. Which act the reader is in is a function of scroll against four
     tracks, one of which has to be split at a fraction. A view timeline can
     light an element as it passes; it cannot answer "which of five".

   So every entry is measured the same way and jumped to the same way, and the
   href stays a real address so that the rail without JavaScript is still a list
   of links that go roughly where they say. Roughly, because acts 2 and 3 land
   at their track's top instead of at their own beat — the honest degradation,
   and the reason the hrefs are the ones they are.

   CONTAIN, IN SCROLL PIXELS. A track taller than the viewport is "contained"
   for as long as it covers the viewport completely, so its timeline runs from
   the scroll position where its top meets the viewport's top to the one where
   its bottom meets the viewport's bottom:

       y(p) = top + p * (height - viewport)

   which is the same mapping every window in acts.css is written in. One
   arithmetic for the CSS and for this, so a beat quoted in one is the beat the
   other jumps to.

   WHAT IT DOES NOT DO. It does not move focus. The pattern for in-page
   navigation is to send focus to the target, and the targets here are
   visually-hidden headings inside sticky stages — a reader sent there has left
   the rail, has nothing to read at the landing point, and has to walk back to
   try the next act. The rail says where it has taken you instead:
   aria-current="true" moves with the scroll, on the link the reader is still
   standing on.

   AND IT NO LONGER TOUCHES THE TAB ORDER. It used to set `hidden` alongside the
   class, so that a rail off screen was also out of the sequence. The intent was
   right and the effect was that the rail could not be reached by keyboard at
   all, forwards or backwards: `hidden` is only ever off while the reader is
   inside the acts, and by then Tab has already passed the rail's own place in
   the document — the measurements are over .act-rail.is-live in acts.css. So
   this file writes one thing for the state, `is-live`, and the stylesheet hides
   the rail by paint and lifts it on :focus-within. A rail nobody can see still
   catches nothing; a rail somebody Tabs to shows itself.

   Optional. A page without .act-rail loads this and does nothing. */
(function () {
  'use strict';

  var rail = document.querySelector('.act-rail');
  if (!rail) return;

  var links = Array.prototype.slice.call(rail.querySelectorAll('[data-act-track]'));
  if (!links.length) return;

  var stops = [];        /* { link, y } in document space, in act order */
  var span = null;       /* { top, bottom } — the acts' whole extent */
  var current = -1;
  var live = null;
  var ticking = false;

  function top(el) {
    return el.getBoundingClientRect().top + window.scrollY;
  }

  /* Re-measured rather than cached across a resize: every term in it — the
     track's height in vh, the viewport, the gate the acts themselves are
     behind — changes with the window. */
  function measure() {
    var v = window.innerHeight;
    var first = null;
    var last = null;

    stops = [];
    for (var i = 0; i < links.length; i++) {
      var track = document.querySelector(links[i].getAttribute('data-act-track'));
      if (!track) continue;
      var t = top(track);
      var h = track.offsetHeight;
      var at = parseFloat(links[i].getAttribute('data-act-at')) || 0;
      /* WHICH ARITHMETIC, ASKED OF THE STYLESHEET RATHER THAN GUESSED FROM THE
         HEIGHTS — and the difference is whether the rail can name act 1 at all.

         `contain` is a length: h - v, the scroll over which a track taller than
         the viewport covers it completely. Every fraction quoted in acts.css is
         a fraction of THAT, which is why this file measures it the same way.
         It only exists where the track has a timeline. In every degraded tier
         it does not: the 640vh height and `view-timeline-name` are declared
         together, inside the same @supports and the same
         (min-width: 64rem) and (min-height: 45rem) and no-preference gate, so
         below the gate, under prefers-reduced-motion, and in a browser without
         animation-timeline the tracks are ordinary blocks a little shorter than
         the window and h - v is zero or a rounding error.

         This used to read `Math.max(0, h - v)`, which kept the offset from
         going negative and, in doing so, multiplied every fraction by nothing.
         Act 2's beat is the only fractional one — contain 36 %, where the
         confluence begins — so act 2's stop landed on act 1's, and read() takes
         the LAST stop the reader has passed, which is act 2's. Measured, of the
         scroll the reader spends INSIDE .sp-track, how much of it the rail spent
         naming act 1:

                                    before          after
           375 x 900, below gate     0 of 901 px     324 px  (36.0 %)
           768 x 900, below gate     0 of 842        304      36.1
           1023 x 900, below gate    0 of 783        280      35.8
           320 x 900, below gate     4 of 910        328      36.0
           375 x 812, below gate    32 of 901        324      36.0
           1280 x 700, below gate   56 of 856        308      36.0
           1440 x 900, no timeline   0 of 714        256      35.9
           1440 x 900, reduced       0 of 714        256      35.9
           1440 x 900, above gate 1748 of 5760      1748      30.3  unchanged

         Mark 01 was lit only over the half-screen BEFORE act 1's track begins —
         off read()'s own `i = 0` default, not off a stop — and went out at the
         moment the reader arrived at the sensor field. Five marks, four
         reachable: for the whole of the act whose label is "Tausende Sensoren"
         the rail said "Ein Strom". Above the gate, where the timeline is real,
         it was always right — which is where it was read, and why this stood.
         The 30.3 % there is not a discrepancy: contain runs over h - v, so
         0.36 of it is 0.36 * 4860 / 5760 of the track.

         So the tier decides the arithmetic, and the tier is a computed value
         rather than an inference: view-timeline-name is `--sp` in exactly the
         tier the contain fractions are written for and `none` in each one they
         are not. Where there is no timeline the honest reading of "36 % of the
         way through" is 36 % of the track's own box — the acts are laid out in
         it rather than scrubbed across it, and the fraction still lands in act
         2's copy: 1152 against .sp-say's 1048 at 375 x 900, 1131 against 1229
         at 768. Above the gate nothing moves, so a beat quoted in acts.css is
         still the beat this jumps to.

         AND THE TIER IS ASKED FOR AS A PROPERTY VALUE, NOT AS A DOM PROPERTY,
         which is the whole of this correction and is one engine's alone. This
         line read `getComputedStyle(track).viewTimelineName === 'none'`. Gecko
         has no view-timeline-name at all — it has no scroll-driven animation,
         which is the entire reason the degraded tier exists there — so that
         property is not on the CSSStyleDeclaration and the read is `undefined`.
         `undefined === 'none'` is false, so the ONE engine that never has a
         timeline took the has-a-timeline arm at every viewport and every
         fraction went back to being a fraction of h - v. The table above is the
         fix's own before-and-after and Firefox was on the "before" row the
         whole time. cf-stream.js states this trap over its own `pinned()` and
         guards it with `typeof`; this line was written without it.

         getPropertyValue() answers the same question in one shape: CSSOM
         returns the empty string for a property the engine does not implement
         and for one that is not set, and both of those mean "no timeline
         here", so `named && named !== 'none'` is the whole test and there is no
         undefined to fall through it.

         Measured, Firefox 153 against Chromium 141, on the shipped page with
         consent answered — of the scroll a reader spends inside .sp-track, how
         much of it the rail spends naming act 1, taken off the two stops this
         function places rather than off a walk, so it is two pixels longer than
         the table above wherever the two overlap: that is read()'s own slack.
         Firefox is in the degraded tier at every row; Chromium is in it at every
         row but the two marked:

                          Firefox before   Firefox after   Chromium
            1440 x 900      361 of 1902     685 of 1902    1750 of 5760  *
            1280 x 700      328 of 1611     580 of 1611     575 of 1597
            1023 x 900      197 of 1448     521 of 1448     509 of 1413
             768 x 900      193 of 1435     517 of 1435     505 of 1402
             375 x 900      198 of 1450     522 of 1450     508 of 1412
             375 x 812      230 of 1450     522 of 1450     508 of 1412
             320 x 900      209 of 1481     533 of 1481     520 of 1445
             768 x 1024     148 of 1435     517 of 1435     505 of 1402
             834 x 1194      92 of 1450     522 of 1450     510 of 1417
             912 x 1368      50 of 1507     543 of 1507     531 of 1474
            1024 x 1366      30 of 1449     522 of 1449    2655 of 8742  *

         The tall rows are the collapse this whole test exists to prevent,
         reached from the other side: h - v shrinks as the window grows, so at
         1024 x 1366 act 2's beat stood 30 px past act 1's and act 1 was named
         over 2 % of its own field. 834 x 1194 is an iPad Air held upright.

         Chromium's every number is unchanged by this edit, in both tiers: it
         reads '--sp' where the timeline is real and 'none' where it is not, and
         `named && named !== 'none'` picks the same arm for both as the test it
         replaces. → scripts/check-act-beats.py */
      var named = getComputedStyle(track).getPropertyValue('view-timeline-name');
      var budget = named && named !== 'none' ? h - v : h;
      stops.push({ link: links[i], y: t + at * Math.max(0, budget) });
      if (first === null) first = t;
      last = t + h;
    }
    span = first === null ? null : { top: first, bottom: last };
  }

  function read() {
    ticking = false;
    if (!span) return;

    var v = window.innerHeight;
    var y = window.scrollY;

    /* THE VIEWPORT'S MIDDLE, not its top: the rail arrives half a screen before
       act 1 does and leaves half a screen after act 5, so it fades over the
       seams instead of appearing on top of the first frame of the field. */
    var mid = y + v / 2;
    var on = mid >= span.top && mid <= span.bottom;
    if (on !== live) {
      live = on;
      rail.classList.toggle('is-live', on);
    }

    /* AND THE MARK GOES OUT WITH THE RAIL. This used to be a bare
       `if (!on) return;`, which left aria-current="true" standing on whichever
       act the reader was in when they left the acts — and both ends of the
       page are outside the band. Scroll into act 3 and back to the hero and
       the rail still said "you are in 03 Service Offering"; ride it to the
       footer and it said the same thing from below. `is-live` came off in both
       cases, so the rail was painted out and nobody could see the claim, but
       nobody can see aria-current either: it is read, and this rail is
       deliberately still in the tab order — see the header above — so a reader
       who Tabs to it from the hero is shown the lit mark and told they are
       standing in an act they have not reached.

       current = -1 and not merely the attribute, because the two are one
       state: without the reset, re-entering the acts at the act you left at
       returns i === current, `read()` takes its early exit, and the mark stays
       off for the whole of it. The invariant is that the rail carries exactly
       one aria-current while it is live and none while it is not. */
    if (!on) {
      if (current >= 0) {
        stops[current].link.removeAttribute('aria-current');
        current = -1;
      }
      return;
    }

    /* The last act whose beat the reader has reached. The 2 px is the rounding
       slack a smooth scroll lands inside of; without it a jump to an act can
       leave the act before it marked. */
    var i = 0;
    for (var k = 0; k < stops.length; k++) {
      if (y + 2 >= stops[k].y) i = k;
    }
    if (i === current) return;
    if (current >= 0) stops[current].link.removeAttribute('aria-current');
    stops[i].link.setAttribute('aria-current', 'true');
    current = i;
  }

  function schedule() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(read);
  }

  rail.addEventListener('click', function (e) {
    var link = e.target.closest ? e.target.closest('[data-act-track]') : null;
    if (!link) return;
    for (var k = 0; k < stops.length; k++) {
      if (stops[k].link !== link) continue;
      e.preventDefault();
      /* No `behavior`, so the scroll takes html's scroll-behavior — smooth by
         default and `auto` under prefers-reduced-motion, which base.css already
         restores. Naming 'smooth' here would be the one journey on the site
         that does not ask. */
      window.scrollTo({ top: Math.round(stops[k].y) });
      return;
    }
  });

  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', function () { measure(); schedule(); });
  window.addEventListener('load', function () { measure(); schedule(); });

  /* A RESIZE IS NOT THE ONLY THING THAT MOVES THE ACTS. Dismissing the consent
     banner is worth 72 px of document on the landing page, measured — the
     banner's height feeds --cf-consent-height, which the pinned stage's
     block-size and --lp-measure both read — and it fires no resize event.
     Fonts landing and images decoding do the same, smaller. Watching the
     document's own height catches all of them and costs nothing while it is
     not changing. */
  if (window.ResizeObserver) {
    new ResizeObserver(function () { measure(); schedule(); })
      .observe(document.documentElement);
  }

  measure();
  read();
})();
