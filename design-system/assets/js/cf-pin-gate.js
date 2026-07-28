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

   A band is an element child of <main>. No class name is baked in here and no
   markup is required: the bands are the page's own top-level structure, and a
   page with no <main> is a no-op. Loading the file is the opt-in, the way
   cf-stream.js is.

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

  var bands = [];
  var anchor = null;
  var ticking = false;
  var frozen = false;   /* anchor held across a reflow, see the resize handler */

  function collect() {
    var main = document.querySelector('main');
    bands = main ? Array.prototype.slice.call(main.children) : [];
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
        anchor = { i: i, f: (y - m.top) / m.height, past: null };
        return;
      }
    }
    /* Past the last band — the footer. There is no fraction to hold, so hold
       the distance from where the content ended. */
    var last = measure(bands[bands.length - 1]);
    anchor = { i: bands.length - 1, f: null, past: y - (last.top + last.height) };
  }

  function restore() {
    if (!anchor || !bands[anchor.i]) { frozen = false; return; }
    var m = measure(bands[anchor.i]);
    var want = anchor.f === null
      ? m.top + m.height + anchor.past
      : m.top + anchor.f * m.height;
    var max = Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
    want = Math.max(0, Math.min(Math.round(want), max));
    if (Math.abs(want - window.scrollY) >= MIN_SHIFT) {
      window.scrollTo({ top: want, behavior: 'instant' });
    }
    /* Re-baseline on the next frame, against the layout that actually landed. */
    requestAnimationFrame(function () { frozen = false; record(); });
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
