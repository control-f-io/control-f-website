/* Control-F — the line of sight.
   OPTIONAL. Every material this touches is complete without it, and rests at
   the value the designer drew. All this file does is answer one question CSS
   cannot ask: where across the screen is the reader?

   The system already reads the other half of that question. A view() timeline
   tells a material how far it is above or below the middle of the viewport,
   and both the foil's rake and the field's pool of light are scrubbed off one.
   But a view timeline measures the ELEMENT's position, and the model those two
   are built on is about the READER's: "116.57° is what you see head-on", "the
   light is where you are looking". Vertically the two coincide, because an eye
   at the middle of the screen is the only assumption available. Horizontally
   they do not, and the assumption is wrong the moment a viewport is wider than
   a headline. This file replaces it with a measurement.

   WHAT IT WRITES, AND NOTHING ELSE:

     --sight-h        on .text-foil — how square the reader is to the type,
                      1 directly in front of it, 0 a half-viewport to the side.
                      Multiplied into the rake in base.css.
     --field-light-x  on .cf-ground--lit — where the pool of light stands
                      across the floor, as a percentage of the section.

   Both are angles and positions. Neither is a colour, an opacity or a
   composite, so no contrast figure in this system is a function of the
   pointer, and none of them has to be re-measured for this file. That is the
   rule the chapter states and the reason it is only these two properties:
   what a material may show the reader about where they are standing is WHERE
   ITS LIGHT COMES FROM, never how much of it there is.

   WHEN IT REFUSES TO RUN. No pointer that can hover (a finger has no position
   between taps, and reading a touch as a light source makes the page twitch
   when it is scrolled). Reduced motion. No support for scroll-driven
   animations — the same gate base.css puts on the swing, so the CSS and the
   script can never disagree about whether the vertical half is running. It
   re-checks on a media-query change and puts everything back when a condition
   stops holding.

   COST. One passive pointermove listener, coalesced to one rAF. Only elements
   currently on screen are tracked, via one IntersectionObserver. Both written
   values are quantised — the rake to 1/64 of its swing, the pool to whole
   percent — so a slow gesture writes on a minority of its frames and a still
   pointer writes on none. --field-light-x is inherited (it has to reach a
   pseudo-element), so its quantisation is the coarser of the two on purpose.

   Delete the tag and every page renders as it did before this file existed. */

(function () {
  'use strict';

  var FOIL = '.text-foil';
  var GROUND = '.cf-ground--lit';

  /* 1/64 of the swing is 0.42° of rake — under the width of the antialias on
     a stop boundary, and 64 steps across a half-viewport is one step every
     15 px at 1920. Whole percent on the pool is ~14 px of section at the same
     width, well inside a 1152 px ellipse's own falloff. */
  var FOIL_STEPS = 64;

  var mqPointer = null;
  var mqMotion = null;
  var observer = null;
  var visible = [];        /* the tracked elements currently on screen */
  var pointerX = null;     /* null until the reader has actually moved one */
  var frame = 0;
  var running = false;

  function supported() {
    if (!window.matchMedia || !window.IntersectionObserver || !window.requestAnimationFrame) return false;
    if (!(window.CSS && CSS.supports && CSS.supports('animation-timeline', 'view()'))) return false;
    return mqPointer.matches && !mqMotion.matches;
  }

  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }

  /* Squareness on one axis: 1 when the reader is in front of the centre of the
     box, falling to 0 a half-viewport away from it. A half-viewport is the
     furthest a pointer can get from something in the middle of the screen, so
     the full range is reachable for a centred element and clipped for one at
     an edge — which is the honest answer. Something pinned to the left margin
     is never seen head-on from the right of the screen. */
  function squareness(rect) {
    var reach = window.innerWidth / 2;
    if (reach <= 0) return 1;
    var centre = rect.left + rect.width / 2;
    return 1 - clamp(Math.abs(pointerX - centre) / reach, 0, 1);
  }

  function apply() {
    frame = 0;
    if (pointerX === null) return;
    for (var i = 0; i < visible.length; i++) {
      var el = visible[i];
      var rect = el.getBoundingClientRect();
      if (!rect.width) continue;

      if (el.matches(FOIL)) {
        var h = Math.round(squareness(rect) * FOIL_STEPS) / FOIL_STEPS;
        if (el.__cfSight !== h) { el.__cfSight = h; el.style.setProperty('--sight-h', h); }
      } else {
        var x = Math.round(clamp((pointerX - rect.left) / rect.width, 0, 1) * 100);
        if (el.__cfSight !== x) { el.__cfSight = x; el.style.setProperty('--field-light-x', x + '%'); }
      }
    }
  }

  function schedule() {
    if (!frame) frame = requestAnimationFrame(apply);
  }

  function onMove(e) { pointerX = e.clientX; schedule(); }

  /* Leaving the window is not "the reader is at the edge" — it is "the reader
     is not here". Both materials go back to the designed still rather than
     freezing wherever the pointer happened to cross the boundary. */
  function onLeave() {
    pointerX = null;
    for (var i = 0; i < visible.length; i++) rest(visible[i]);
  }

  function rest(el) {
    el.__cfSight = undefined;
    el.style.removeProperty('--sight-h');
    el.style.removeProperty('--field-light-x');
  }

  function start() {
    if (running) return;
    running = true;
    observer = new IntersectionObserver(function (entries) {
      for (var i = 0; i < entries.length; i++) {
        var el = entries[i].target;
        var at = visible.indexOf(el);
        if (entries[i].isIntersecting) {
          if (at < 0) visible.push(el);
        } else if (at > -1) {
          visible.splice(at, 1);
          rest(el);
        }
      }
      schedule();
    });
    var all = document.querySelectorAll(FOIL + ', ' + GROUND);
    for (var i = 0; i < all.length; i++) observer.observe(all[i]);

    window.addEventListener('pointermove', onMove, { passive: true });
    document.documentElement.addEventListener('pointerleave', onLeave);
    window.addEventListener('blur', onLeave);
  }

  function stop() {
    if (!running) return;
    running = false;
    window.removeEventListener('pointermove', onMove);
    document.documentElement.removeEventListener('pointerleave', onLeave);
    window.removeEventListener('blur', onLeave);
    if (frame) { cancelAnimationFrame(frame); frame = 0; }
    if (observer) { observer.disconnect(); observer = null; }
    onLeave();
    visible = [];
  }

  function sync() { if (supported()) start(); else stop(); }

  function init() {
    if (!window.matchMedia) return;
    mqPointer = matchMedia('(pointer: fine)');
    mqMotion = matchMedia('(prefers-reduced-motion: reduce)');
    /* addEventListener on a MediaQueryList is the modern spelling and the only
       one worth carrying; a browser too old for it is a browser without
       scroll-driven animations, so supported() has already said no. */
    if (mqPointer.addEventListener) {
      mqPointer.addEventListener('change', sync);
      mqMotion.addEventListener('change', sync);
    }
    sync();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
}());
