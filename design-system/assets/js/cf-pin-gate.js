/* Control-F — hold the reader's place through a reflow.

   OPTIONAL, and a no-op on every resize that does not move anything. Load it on
   a page whose layout has a MODE, not just a width: a section that is one shape
   above a threshold and a different shape below it, with a different height. On
   every other page it costs one scroll listener and changes nothing.

   THE FAULT IT EXISTS FOR. patterns/landing-page.html gates its pinned "Was wir
   machen" stage behind (min-width: 64rem) and (min-height: 45rem). Above the
   gate the section is a sticky stage with a track of scroll behind it; below it
   the section is a stacked column of four cards. Measured at 1280 x 900, the
   same section is 6901 px tall in one mode and 2209 px in the other — the track
   is 4692 px of scroll that exists on one side of the gate and not the other.

   A viewport resize does not carry the reader across that. The browser keeps
   the scroll OFFSET, in pixels, and the offset means something different on
   each side. Measured, reader parked half way through the section, then the
   viewport crossed the gate downward:

     1280x900 -> 1023x900   scrollY 4537 held; section top -3091 -> -3214 with
                            the section now 2209 tall, so its BOTTOM is -1005:
                            the whole of "Was wir machen" is above the window
                            and the reader is looking at "Blog".
     1280x900 -> 1280x719   same offset, same section gone, reader on "FAQ".
     1024x768 -> 768x1024   an iPad turned from landscape to portrait: reader
                            on "Partner & Technologien" at half way, on "Blog"
                            at 85 %.

   At 85 % of the track the new document is shorter than the old offset, so the
   offset is clamped to the end and the reader lands on "Das Team", the last
   section on the page. Turning a tablet skips five sections.

   Crossing the gate UPWARD is fine — the section grows underneath the reader
   and its top moves 123 to 167 px — which is why this only ever looked like a
   one-way fault and why nothing caught it.

   SCROLL ANCHORING DOES NOT COVER THIS, and that was worth proving rather than
   assuming, because it is the platform's own answer to content moving under a
   reader. It is suppressed for layout changes driven by a viewport resize.
   Tested at the width gate with the stage's stickiness removed, with
   overflow-anchor forced to auto on every element, and with it forced to none
   across the pin's subtree: scrollY held at 4537 in all three, byte for byte
   with the baseline. There is no CSS lever here.

   WHAT IT DOES. It keeps the reader's FRACTION through the band they are
   reading, rather than their pixel offset into the document — which is the same
   number on both sides of the gate, because both modes lay the same four cards
   out across the whole of the section. Half way through the pinned track is
   card 02 arriving; half way down the stacked column is card 02.

   A band is an IN-FLOW element child of <main>. No class name is baked in here
   and no markup is required: the bands are the page's own top-level structure,
   and a page with no <main> is a no-op. Loading the file is the opt-in, the way
   cf-stream.js is.

   IN-FLOW IS THE LOAD-BEARING HALF OF THAT SENTENCE, and it was assumed rather
   than written for as long as every child of every <main> happened to be in
   flow. `nav.act-rail` ended that: it is a child of <main> on
   patterns/landing-page.html and prototypes/statement-to-process.html, and
   above (min-width: 64rem) it is `position: fixed`.

   A fixed element has no document-space extent, so the one arithmetic this
   file is built on — `top = rect.top + scrollY` — returns the reader's own
   scroll position plus a constant instead of a fixed place in the document.
   Measured at 1280 x 900, the rail's rect.top is 378 and its height 144, so
   `top + height` evaluates to `scrollY + 522` and the test

       y < top + height

   is true at EVERY scroll position past the hero's foot. The rail therefore
   swallowed the anchor for the whole document below 828 px, held a fraction of
   -3.77 that meant nothing, and — because restore() re-measured the same fixed
   element and got the same `scrollY + 378` back — corrected the scroll to
   within a pixel of where the browser had already left it. The cure was a
   no-op on both of the two pages that need it most, and it read as working
   because it ran, listened, and moved the page by 0.

   Measured across the gate, reader carried 1280 x 900 -> 700 x 900 -> back,
   before and after this filter, on patterns/landing-page.html. "band after"
   is where the reader ended up at 700; "round trip" is how far from their own
   starting pixel they came back to:

     start       band before      band after 700   round trip   with the filter
     y  1203     sp-track  .06    sp-track  .38      +1812 px         +2 px
     y  2881     sp-track  .36    section   .32      +5905 px        +68 px
     y  5753     sp-track  .85    sp4-track .11      +8004 px         -2 px
     y  7111     section   .08    sp4-track .93      +9604 px         +0 px
     y 10386     section   .56    section   .45     +11506 px         +0 px
     y 12731     section   .91    section   .45      +9161 px         +0 px
     y 15728     sp4-track .65    section   .45      +6164 px         +0 px
     y 19008     map-track .45    section   .45      +2884 px       +153 px
     y 20501     map-track .78    section   .45      +1391 px         +0 px

   Four of the nine clamped to y 21892 — the end of the document — so a reader
   half way through "Was wir machen" who turned a tablet arrived at the FAQ.
   patterns/expertise.html, whose <main> has no out-of-flow child, held its
   fraction to within 1 px before this change and still does — which is what
   said the fault was the band list and not the arithmetic.

   `sticky` is in the filter beside `fixed` for the same reason and one step
   ahead of it: a stuck element's rect.top is pinned to the viewport too, so
   its document-space top drifts with the reader for exactly as long as it is
   stuck. No <main> currently has a sticky child — every sticky stage in the
   system is a grandchild, inside its own track — so this half of the filter
   changes nothing today and stops the same fault arriving by a second door.
   → scripts/check-band-flow.py

   WHY IT IS NOT SCOPED TO THE PINNED SECTION. A reader BELOW the gate's section
   is stranded by the same 4692 px without their own band changing shape at all
   — everything above them shrank and their offset did not. Anchoring to
   whichever band the reader is actually in covers both, and covers the ordinary
   resize too: 1280x900 -> 1100x900 drifts the section 86 px with no mode change
   at all, and that drift goes as well.

   It never scrolls for less than MIN_SHIFT, so a resize that moves nothing —
   a phone's address bar showing and hiding, which fires resize and changes no
   band's geometry — is arithmetic and no motion. Restoring is `behavior:
   'instant'` on purpose: base.css sets scroll-behavior: smooth on <html>, and
   an animated correction after a resize is worse than the fault.

   With JS off the page is exactly what it was. */

(function () {
  'use strict';

  /* Below this the correction is noise, and moving the page by a pixel after
     every resize tick is worse than the pixel. */
  var MIN_SHIFT = 2;

  /* How many frames the held fraction is re-applied for before the anchor is
     re-baselined. See restore(). */
  var SETTLE = 3;

  var bands = [];
  var anchor = null;
  var ticking = false;
  var frozen = false;   /* anchor held across a reflow, see the resize handler */

  /* Re-read on every resize rather than once, because `position` is a
     declaration behind a media query: the act rail is fixed above
     (min-width: 64rem) and static below it, so the same child is a band on
     one side of that threshold and not on the other. */
  function collect() {
    var main = document.querySelector('main');
    var kids = main ? Array.prototype.slice.call(main.children) : [];
    var pos;
    bands = [];
    for (var i = 0; i < kids.length; i++) {
      pos = getComputedStyle(kids[i]).position;
      if (pos !== 'fixed' && pos !== 'sticky') bands.push(kids[i]);
    }
  }

  /* Document-space, not viewport-space: the whole point is a number that
     survives the viewport changing. */
  function measure(el) {
    var r = el.getBoundingClientRect();
    return { top: r.top + window.scrollY, height: r.height };
  }

  function record() {
    ticking = false;
    if (frozen || !bands.length) return;
    var y = window.scrollY;
    for (var i = 0; i < bands.length; i++) {
      var m = measure(bands[i]);
      if (m.height > 0 && y < m.top + m.height) {
        anchor = { el: bands[i], f: (y - m.top) / m.height, past: null };
        return;
      }
    }
    /* Past the last band — the footer. There is no fraction to hold, so hold
       the distance from where the content ended. */
    var lastEl = bands[bands.length - 1];
    var last = measure(lastEl);
    anchor = { el: lastEl, f: null, past: y - (last.top + last.height) };
  }

  /* THE ANCHOR HOLDS THE ELEMENT AND NOT ITS INDEX, which is the other half of
     the filter above rather than a tidy-up. collect() runs again on the resize,
     between the last record() and this restore(), and the band list it builds
     is now allowed to have a different LENGTH on the two sides of a threshold —
     the act rail leaves the list going up through (min-width: 64rem) and
     rejoins it coming down. An index taken before the reflow would name the
     band after the one the reader was in, and the correction would be confident
     and wrong. An element reference cannot slip. */
  /* The arithmetic, once, against whatever the layout is in this frame. */
  function place() {
    var m = measure(anchor.el);
    var want = anchor.f === null
      ? m.top + m.height + anchor.past
      : m.top + anchor.f * m.height;
    var max = Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
    want = Math.max(0, Math.min(Math.round(want), max));
    if (Math.abs(want - window.scrollY) >= MIN_SHIFT) {
      window.scrollTo({ top: want, behavior: 'instant' });
    }
  }

  function restore() {
    if (!anchor || !anchor.el || !anchor.el.isConnected) { frozen = false; return; }
    /* THE HELD FRACTION IS APPLIED UNTIL THE LAYOUT STOPS MOVING, and the frame
       after the resize is not that frame. A viewport change is not one reflow: a
       drag fires resize on many consecutive frames, and each of those frames
       lands an intermediate layout. Re-baselining on the first one recorded the
       fraction of a shape that was still on its way somewhere, and the next
       correction then held THAT — so the reader's place walked, one intermediate
       layout at a time, inside the right band.

       Measured on patterns/landing-page.html, 1280 x 900 -> 700 x 900 -> back,
       reader a third of the way through act 1's track, with the band filter
       above in place and this loop not yet: the fraction walked 0.355 -> 0.511
       across the pair and the reader came back 899 px low. The band was right
       and the arithmetic was right; the baseline was taken a frame too early.
       Applying the ORIGINAL fraction for SETTLE frames and re-baselining only
       after it converges took the same journey to +68 px, and took the eight
       other start positions in the table at the head of this file to between
       -2 and +153, six of them to 0.

       SETTLE is frames and not milliseconds because the thing being waited for
       is a layout, and three is what the measured worst case needed — a
       cross-gate resize on this page settles on frame 2. It costs three
       arithmetic passes on a resize and nothing at all otherwise; the MIN_SHIFT
       guard means a frame that moved nothing also scrolls nothing.

       WHAT IS LEFT is a fraction that can still shift by up to about 0.03 of a
       band on a cross-gate resize — 153 px at the worst of nine measured start
       positions, against 11 506 before any of this. It is a re-baselining
       question and not a band question, and it is bounded by the band the
       reader is in rather than by the document. */
    var left = SETTLE;
    (function step() {
      place();
      if (--left > 0) { requestAnimationFrame(step); return; }
      /* Re-baseline, against the layout that has actually landed. */
      requestAnimationFrame(function () { frozen = false; record(); });
    }());
  }

  window.addEventListener('scroll', function () {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(record);
  }, { passive: true });

  window.addEventListener('resize', function () {
    /* Freeze first. Collapsing the document can clamp scrollY and fire a scroll
       event before the correction runs, and that event would overwrite the one
       number this file exists to keep. */
    frozen = true;
    collect();
    requestAnimationFrame(restore);
  }, { passive: true });

  collect();
  record();
}());
