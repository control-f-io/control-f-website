/* Control-F — a page that is not being read is a page that is not moving.

   OPTIONAL, and it adds nothing to the drawing. Every figure it touches is
   already complete, already animated and already correct without it. All this
   does is stop a perpetual animation from running while the figure carrying it
   is nowhere near the viewport. Delete the tag and the page renders exactly as
   it did, and costs what it cost.

   THE FAULT IT EXISTS FOR. A scroll-driven animation is free when nobody
   scrolls: no scroll, no frame, no work. An animation on the DOCUMENT clock is
   the opposite — `infinite` means for the life of the tab, whether the element
   is on screen, off screen or fifteen thousand pixels away, and whether the
   reader is reading, typing in another window or has walked off.

   patterns/landing-page.html ships 128 of them. 126 are `.sp-stream > b`, the
   six readings each of act 1's twenty-one sensor labels cycle through; two are
   the copy stream's caret. Act 1 is about 2 300 px of a 22 931 px document.

   Measured at 1440 x 900, Chromium 1194, page LOADED AND THEN LEFT ALONE — no
   scrolling, no pointer, no keyboard, five seconds of a still page:

     landing 1440, at the top                1351 ms of style recalc in 5 000
                                             299 recalcs — one per frame, 60 Hz
                                             4.5 ms per frame
                                             2246 ms of total task time  (45 %)
     landing 1440, act 5 on screen and       1395 ms — the figure is 15 000 px
       act 1 fifteen thousand px away          away and costs the same
     landing 1440, with the 126 cancelled      319 ms  (-76 %)
     landing 1440, prefers-reduced-motion        0 ms
     landing  375                                0 ms
     expertise 1440                              0 ms
     kontakt   1440                              0 ms

   Half the main thread, at every frame, forever, for a readout that is not on
   the screen. It is the cost this file removes.

   WHY IT IS NOT THE READOUT'S FAULT, and why the cure is here rather than in
   the keyframes. The property is `opacity`, the cheapest thing to animate in
   the system and the one the motion chapter asks for. Substituting a single
   `transform` animation on one empty 4 x 4 div for all 128 measured 1362 ms of
   recalc in the same 5 s — the same figure. The count barely matters either:
   26 shimmering leaves cost 1375 ms and ONE costs 1150. What costs is that the
   page is producing frames at all; every frame it produces then walks a
   1 623-element document against 840 KB of stylesheet. So there is no cheaper
   keyframe to write, and no smaller number of elements to write it on. The
   only lever is time — the animation has to stop.

   WHAT IT DOES. One IntersectionObserver per marked figure. Off screen, the
   figure gets `data-idle`; acts.css and components.css pause the animations
   under that attribute. On screen it goes away and they run. `rootMargin` is a
   whole viewport in each direction, so the readouts are already ticking well
   before the figure's first pixel arrives and there is nothing to "start".

   PAUSED, NOT STOPPED. `animation-play-state: paused` holds every element at
   the value it had, which for a six-slot ticker is the reading it was showing.
   Nothing re-runs from the top when the reader comes back, no number jumps, and
   the phase offsets that make the twenty-one labels tick out of step are kept.
   The alternative — cancelling the animation — restarts the whole field in
   unison the moment it re-enters, which is the one thing the stagger exists to
   prevent.

   WHAT IT REFUSES. No IntersectionObserver, no work: the page keeps its old
   behaviour rather than getting a worse one. Under prefers-reduced-motion there
   is nothing running to pause — measured 0 ms above, because every one of these
   animations is already inside a no-preference gate — so the observers are
   never even built.

   MARKED, NOT GUESSED. A figure opts in with data-cf-idle, the same way a track
   opts into the copy stream by carrying the class the stream looks for. This
   file has no list of class names in it and nothing to keep in step.
   → scripts/check-idle-motion.py */

(function () {
  'use strict';

  if (!window.IntersectionObserver || !window.matchMedia) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  var figures = document.querySelectorAll('[data-cf-idle]');
  if (!figures.length) return;

  /* A whole viewport of margin in each direction. The observer fires on the
     approach rather than on the arrival, so a reader scrolling at any speed
     meets a figure that has been running for at least a screen — the tick is
     never seen starting. */
  var observer = new window.IntersectionObserver(function (entries) {
    for (var i = 0; i < entries.length; i++) {
      var el = entries[i].target;
      if (entries[i].isIntersecting) el.removeAttribute('data-idle');
      else el.setAttribute('data-idle', '');
    }
  }, { rootMargin: '100% 0px 100% 0px' });

  for (var i = 0; i < figures.length; i++) {
    /* IDLE UNTIL TOLD OTHERWISE, so a figure that is off screen at load has
       been still since its first frame rather than since the first callback.

       AND THE FIRST CALLBACK IS NOT BEFORE PAINT. This line first carried the
       claim that it was, which is wrong and was worth measuring rather than
       asserting: sampling the attribute on every animation frame from
       DOMContentLoaded, over three loads at 1440 x 900 with act 1 on screen,
       `data-idle` was still set on 1, 1 and 2 frames before the observer took
       it off. So the readouts ARE held for a frame or two at load.

       It is kept anyway, because the ticker's own step is 500 ms — each of the
       six readings holds for 16.66 % of a 3 s cycle — and one frame of a still
       reading is indistinguishable from the 30 still frames either side of it.
       The alternative costs the thing this file is for: dropping the pre-set
       lets every figure on the page run from load until the first callback,
       including the ones fifteen thousand pixels away, which is the fault. */
    figures[i].setAttribute('data-idle', '');
    observer.observe(figures[i]);
  }
}());
