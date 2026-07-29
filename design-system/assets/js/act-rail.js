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
      /* max(0, …) so a track shorter than the viewport — which is what every
         one of them is below the acts' own gate — collapses to its top rather
         than to a negative offset above it. */
      stops.push({ link: links[i], y: t + at * Math.max(0, h - v) });
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
    if (!on) return;

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
