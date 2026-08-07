/* Control-F — a way past a build, for the reader who does not want to scroll it.

   WHAT IT IS FOR. A pinned act holds the reader's scroll for as long as its
   build takes: measured on patterns/landing-page.html at 1440 x 900, acts 1+2
   are 4860 px of scroll, act 3 is 5760 and act 4 is 2700 — 13 320 px, about
   fifteen full turns of a wheel, before the page moves on. That is the
   composition working as designed for a reader who wants it and a wall for one
   who does not, and until this file the only way past it was to keep scrolling.
   The control this drives is the way out: one press and the build in front of
   the reader is finished, with the act still on the stage.

   IT LANDS AT THE END OF A BUILD, NOT PAST IT. A jump is a contain position on
   the track's own timeline — the scroll position where that fraction of the
   track has passed the viewport, which above the gate is exactly the fraction
   acts.css writes its windows in:

       y = top + at * (height - viewport)

   the same arithmetic act-rail.js jumps on, so a beat quoted in one is the beat
   this lands on. `at = 1` is the track's contain end: the last moment the stage
   is pinned and the one where every range in the stylesheet has run to 100 %.

   ONE TRACK CAN HOLD MORE THAN ONE BUILD, WHICH IS WHY THE STOPS ARE A LIST.
   The default is the single stop `1`, and for two of the three controls on the
   site that is the whole story — act 3's cards and act 4's plates are one build
   each on a track of their own. .sp-track is not: it is 640vh carrying TWO acts
   that the rail already names separately, "Tausende Sensoren" over contain
   0 - 36 % and "Ein Strom" over 36 - 100 %. With one stop, a reader who pressed
   the control at the first frame of the sensor field landed on the finished
   root — the sensors' own build, the beat the button was standing in, was the
   thing that got skipped.  → https://app.notion.com/p/3b52e8e39877806c9b4ef2346724bc58

   So a page may write `data-cf-skip-at` on the button: contain fractions in
   ascending order, separated by spaces. A press takes the FIRST stop still
   ahead of the reader, so the control walks the track's beats one press at a
   time and always finishes the build in front of it rather than the one after.
   The 2 px of slack is act-rail.js's, for the same reason: a smooth scroll
   lands inside it, and without the slack the stop just reached would be
   "ahead" and pressing twice would go nowhere.

   The fractions are the stylesheet's, not this file's. `1` is appended if the
   list does not end there, because the last thing the control must always be
   able to do is finish the track.

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

   TWO STATES, AND THE SECOND IS WHY THE CONTROL CAN STAND IN THE MARGIN.
   `is-gated` is the tier above: this button has a track, so it exists at all.
   `is-live` is the reader's position: the viewport's MIDDLE is inside that
   track, which is act-rail.js's own test and carries the same meaning there.
   The control is fixed to the viewport now — components.css mirrors the rail
   across the page — and a fixed control cannot be "inside its stage" by layout
   the way an absolutely placed one was. Without the second state the landing
   page's two controls would stand on the same 24 px of the right margin for
   the whole of the acts, and each would offer to finish a build the reader is
   4 000 px away from.

   NO MARKUP CONTRACT BEYOND THE CLASS. The button is `.cf-skip`, it stands
   inside the stage it skips, and the track is whatever ancestor above it the
   stylesheet gave a timeline to. A page adds the control by writing the button;
   nothing has to be named twice. `data-cf-skip-at` is optional and is the only
   thing a page ever states twice, because a beat is a number in acts.css that
   no computed style publishes.

   WITH JS OFF the button is not shown at all — components.css hides it and this
   file is what reveals it — so the page is exactly what it was.

   Optional. A page with no .cf-skip loads this and does nothing. */
(function () {
  'use strict';

  var buttons = Array.prototype.slice.call(document.querySelectorAll('.cf-skip'));
  if (!buttons.length) return;

  var gated = [];   /* { btn, track, at } — only the buttons with a build to skip */
  var ticking = false;

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

  /* Ascending, in (0, 1], and always ending at 1. A malformed entry is dropped
     rather than thrown on: the fallback is the single stop this control had
     before the attribute existed, which is a working control. */
  function stopsOf(btn) {
    var raw = btn.getAttribute('data-cf-skip-at') || '';
    var parts = raw.split(/\s+/);
    var out = [];
    var i, n;
    for (i = 0; i < parts.length; i++) {
      n = parseFloat(parts[i]);
      if (n > 0 && n <= 1 && out.indexOf(n) === -1) out.push(n);
    }
    out.sort(function (a, b) { return a - b; });
    if (out[out.length - 1] !== 1) out.push(1);
    return out;
  }

  /* Re-read rather than cached: view-timeline-name is behind a width and a
     height gate, so the same track carries a timeline at one viewport and none
     at the next. The rail re-measures for the same reason. */
  function measure() {
    var i;
    gated = [];
    for (i = 0; i < buttons.length; i++) {
      var track = trackOf(buttons[i]);
      buttons[i].classList.toggle('is-gated', !!track);
      if (!track) buttons[i].classList.remove('is-live');
      if (track) gated.push({ btn: buttons[i], track: track, at: stopsOf(buttons[i]) });
    }
    read();
  }

  function boxOf(track) {
    var top = track.getBoundingClientRect().top + window.scrollY;
    return { top: top, height: track.offsetHeight };
  }

  function yOf(box, at) {
    return Math.round(box.top + at * Math.max(0, box.height - window.innerHeight));
  }

  function read() {
    ticking = false;
    var mid = window.scrollY + window.innerHeight / 2;
    for (var i = 0; i < gated.length; i++) {
      var box = boxOf(gated[i].track);
      gated[i].btn.classList.toggle('is-live', mid >= box.top && mid <= box.top + box.height);
    }
  }

  function schedule() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(read);
  }

  document.addEventListener('click', function (e) {
    var btn = e.target.closest ? e.target.closest('.cf-skip') : null;
    if (!btn) return;
    for (var i = 0; i < gated.length; i++) {
      if (gated[i].btn !== btn) continue;
      var box = boxOf(gated[i].track);
      var at = gated[i].at;
      var y = yOf(box, at[at.length - 1]);
      for (var k = 0; k < at.length; k++) {
        var stop = yOf(box, at[k]);
        if (stop > window.scrollY + 2) { y = stop; break; }
      }
      /* No `behavior`, so the jump takes html's scroll-behavior — the same
         journey the act rail's five jumps take, and the reason neither names
         'smooth' here: base.css already answers prefers-reduced-motion with
         `auto`, and this control is only ever shown where that preference is
         no-preference anyway. */
      window.scrollTo({ top: y });
      return;
    }
  });

  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', measure);
  /* The gate moves with the document as well as with the window — the consent
     banner is worth 72 px of it on the landing page and fires no resize —
     which is the observer act-rail.js keeps for the same reason. */
  if (window.ResizeObserver) {
    new ResizeObserver(measure).observe(document.documentElement);
  }

  measure();
}());
