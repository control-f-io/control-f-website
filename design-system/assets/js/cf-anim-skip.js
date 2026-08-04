/* Control-F — a way past a build, for the reader who does not want to scroll it.

   WHAT IT IS FOR. A pinned act holds the reader's scroll for as long as its
   build takes: measured on patterns/landing-page.html at 1440 x 900, acts 1+2
   are 4860 px of scroll, act 3 is 5760 and act 4 is 2700 — 13 320 px, about
   fifteen full turns of a wheel, before the page moves on. That is the
   composition working as designed for a reader who wants it and a wall for one
   who does not, and until this file the only way past it was to keep scrolling.
   The control this drives is the way out: one press and the build is finished,
   at the last frame of its own track, with the act still on the stage.

   IT LANDS AT THE END OF THE BUILD, NOT PAST IT. The jump is the track's own
   contain end — the scroll position where the track's bottom meets the
   viewport's bottom, which is the last moment the stage is pinned and the one
   where every range in the stylesheet has run to 100 %. A reader who presses
   it sees the assembled drawing, which is the thing the build was assembling;
   a jump to the next section would have skipped the act rather than its
   animation.

       y = top + (height - viewport)

   the same arithmetic act-rail.js jumps on and the same one every window in
   acts.css is written in, so a beat quoted in one is the beat this lands on.

   THE TIER IS ASKED OF THE STYLESHEET, NOT RESTATED HERE. A build only exists
   where its track carries a view timeline, and that is a declaration behind a
   gate — @supports (animation-timeline: view()) and (animation-range: …),
   prefers-reduced-motion: no-preference, (min-width: 64rem) and
   (min-height: 45rem). Below the gate, under reduced motion, and in a browser
   without view timelines the same markup is a stacked column that is already
   in its finished state: there is nothing to skip, and a control offering to
   skip it would be a button that scrolls the reader somewhere for no reason.

   So the button finds its own track by walking up from itself to the first
   ancestor whose COMPUTED view-timeline-name is a name, and shows itself only
   if it found one. No threshold is written in this file — the stylesheet is
   the single source of the gate, which is the rule scripts/check-script-gates.py
   exists to hold. The undefined case is the one that matters and is tested
   explicitly: a browser with no scroll-driven animations has no
   `viewTimelineName` in its computed style at all, so the property reads
   `undefined` — and `undefined !== 'none'` would have shown the control on
   exactly the browsers where it cannot work.

   NO MARKUP CONTRACT BEYOND THE CLASS. The button is `.cf-skip`, it stands
   inside the stage it skips, and the track is whatever ancestor above it the
   stylesheet gave a timeline to. A page adds the control by writing the button;
   nothing has to be named twice.

   WITH JS OFF the button is not shown at all — components.css hides it and this
   file is what reveals it — so the page is exactly what it was.

   Optional. A page with no .cf-skip loads this and does nothing. */
(function () {
  'use strict';

  var buttons = Array.prototype.slice.call(document.querySelectorAll('.cf-skip'));
  if (!buttons.length) return;

  var live = [];   /* { btn, track } — only the buttons with a build to skip */

  function trackOf(btn) {
    var el = btn.parentNode;
    var name;
    while (el && el.nodeType === 1) {
      name = getComputedStyle(el).viewTimelineName;
      if (name && name !== 'none') return el;
      el = el.parentNode;
    }
    return null;
  }

  /* Re-read rather than cached: view-timeline-name is behind a width and a
     height gate, so the same track carries a timeline at one viewport and none
     at the next. The rail re-measures for the same reason. */
  function measure() {
    var i;
    live = [];
    for (i = 0; i < buttons.length; i++) {
      var track = trackOf(buttons[i]);
      buttons[i].classList.toggle('is-live', !!track);
      if (track) live.push({ btn: buttons[i], track: track });
    }
  }

  function endOf(track) {
    var top = track.getBoundingClientRect().top + window.scrollY;
    return Math.round(top + Math.max(0, track.offsetHeight - window.innerHeight));
  }

  document.addEventListener('click', function (e) {
    var btn = e.target.closest ? e.target.closest('.cf-skip') : null;
    if (!btn) return;
    for (var i = 0; i < live.length; i++) {
      if (live[i].btn !== btn) continue;
      /* No `behavior`, so the jump takes html's scroll-behavior — the same
         journey the act rail's five jumps take, and the reason neither names
         'smooth' here: base.css already answers prefers-reduced-motion with
         `auto`, and this control is only ever shown where that preference is
         no-preference anyway. */
      window.scrollTo({ top: endOf(live[i].track) });
      return;
    }
  });

  window.addEventListener('resize', measure);
  /* The gate moves with the document as well as with the window — the consent
     banner is worth 72 px of it on the landing page and fires no resize —
     which is the observer act-rail.js keeps for the same reason. */
  if (window.ResizeObserver) {
    new ResizeObserver(measure).observe(document.documentElement);
  }

  measure();
}());
