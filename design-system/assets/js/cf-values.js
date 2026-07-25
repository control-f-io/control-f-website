/* Control-F — the values stream.
   OPTIONAL. The Unsere Werte section is complete without this file: the six
   values are real markup, the mark is built by a view timeline, and the whole
   thing scrubs, pins and falls back on CSS alone. All this adds is the copy
   arriving character by character instead of whole, which is what the
   prototype in prototypes/werte-scroll.html does and the one thing a view
   timeline cannot do — there is no per-character unit to animate.

   It follows the prototype's timing rather than inventing one:

     reveal window   the first 62 % of each stage, then hold
     title           the first 28 % of that window
     body            starts at 14 % and spans the rest
     easing          smoothstep, so early characters land a touch faster

   Because it is driven by scroll position and not by a timer, scrolling back
   up un-types the text, same as the prototype.

   It refuses to run unless the pinned layout is actually active — no support
   for scroll-driven animations, reduced motion, or a viewport under 820 px all
   mean the section is in its stacked state, where every value is on screen at
   once and typing one of them would be nonsense. It re-checks on resize.

   Accessibility: the streamed span is aria-hidden and a .visually-hidden twin
   carries the full sentence, so assistive technology always gets the whole
   value no matter where the scroll happens to be. Nothing is ever announced
   half-written. */

(function () {
  'use strict';

  var SEL = '.cf-values';
  var REVEAL = 0.62;          /* of a stage; the rest is hold */
  var TITLE_SLICE = 0.28;     /* of the reveal window */
  var BODY_START = 0.14;
  var BODY_SPAN = 0.72;
  var MIN_WIDTH = 820;        /* keep in step with the media query in components.css */

  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }
  function smoothstep(x) { return x * x * (3 - 2 * x); }

  function pinned() {
    if (!window.matchMedia) return false;
    if (!(window.CSS && CSS.supports && CSS.supports('animation-timeline', 'view()'))) return false;
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) return false;
    return matchMedia('(min-width: ' + MIN_WIDTH + 'px)').matches;
  }

  /* Split one element into a streamed span and a full-text twin for AT. */
  function prepare(el) {
    var full = el.textContent.replace(/\s+/g, ' ').trim();
    var stream = document.createElement('span');
    stream.className = 'cf-values__stream';
    stream.setAttribute('aria-hidden', 'true');
    var whole = document.createElement('span');
    whole.className = 'visually-hidden';
    whole.textContent = full;
    el.textContent = '';
    el.appendChild(stream);
    el.appendChild(whole);
    return { full: full, stream: stream, whole: whole, shown: -1 };
  }

  function restore(part, el) {
    el.textContent = part.full;
  }

  function build(section) {
    var track = section.querySelector('.cf-values__track');
    var items = [].slice.call(section.querySelectorAll('.cf-values__item'));
    if (!track || !items.length) return null;
    var parts = items.map(function (li) {
      var t = li.querySelector('.cf-values__title');
      var b = li.querySelector('.cf-values__body');
      return {
        li: li, titleEl: t, bodyEl: b,
        title: prepare(t), body: prepare(b)
      };
    });
    var caret = document.createElement('span');
    caret.className = 'cf-values__caret';
    caret.setAttribute('aria-hidden', 'true');
    return { track: track, parts: parts, caret: caret, active: -1 };
  }

  function teardown(state) {
    state.parts.forEach(function (p) {
      restore(p.title, p.titleEl);
      restore(p.body, p.bodyEl);
    });
    if (state.caret.parentNode) state.caret.parentNode.removeChild(state.caret);
  }

  function paint(part, p) {
    var n = Math.round(part.full.length * smoothstep(p));
    if (n === part.shown) return;
    part.shown = n;
    part.stream.textContent = part.full.slice(0, n);
  }

  function run(state) {
    var r = state.track.getBoundingClientRect();
    /* The same interval the CSS `contain` range covers: the stretch over which
       the track fully covers the viewport, which is exactly the sticky travel. */
    var travel = r.height - window.innerHeight;
    if (travel <= 0) return;
    var progress = clamp(-r.top / travel, 0, 1);

    var n = state.parts.length;
    var f = progress * n;
    var stage = Math.min(Math.floor(f), n - 1);
    var local = clamp((f - stage) / REVEAL, 0, 1);

    var part = state.parts[stage];
    var tp = clamp(local / TITLE_SLICE, 0, 1);
    var bp = clamp((local - BODY_START) / BODY_SPAN, 0, 1);
    paint(part.title, tp);
    paint(part.body, bp);

    /* Every other value sits at rest, complete — scrolling past and back must
       not leave a half-typed sentence behind. */
    state.parts.forEach(function (o, i) {
      if (i === stage) return;
      var done = i < stage ? 1 : 0;
      paint(o.title, done);
      paint(o.body, done);
    });

    if (state.active !== stage) {
      state.active = stage;
      part.body.stream.parentNode.appendChild(state.caret);
    }
    state.caret.classList.toggle('is-resting', bp >= 1);
  }

  function init() {
    [].slice.call(document.querySelectorAll(SEL)).forEach(function (section) {
      var state = null, ticking = false;

      function frame() { ticking = false; if (state) run(state); }
      function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(frame); } }

      function sync() {
        if (pinned() && !state) {
          state = build(section);
          if (!state) return;
          window.addEventListener('scroll', onScroll, { passive: true });
          run(state);
        } else if (!pinned() && state) {
          window.removeEventListener('scroll', onScroll);
          teardown(state);
          state = null;
        }
      }

      sync();
      window.addEventListener('resize', function () { sync(); if (state) onScroll(); }, { passive: true });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
