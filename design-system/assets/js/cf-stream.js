/* Control-F — the copy stream.
   OPTIONAL. Every section that uses this is complete without it: the copy is
   real markup, the stages are built by view timelines, and the whole thing
   scrubs, pins and falls back on CSS alone. All this adds is the copy arriving
   character by character instead of whole, which is the one thing a view
   timeline cannot do — there is no per-character unit to animate.

   IT IS ONE ENGINE AND IT USED TO BE TWO. This was cf-values.js, named for its
   only consumer, until Expertise wanted the same behaviour. A second copy of a
   scrubbing typewriter is two timings that will not stay equal, so the file
   took the name of the job instead: any pinned track can ask for it, and the
   pacing below is the same pacing in both places by construction rather than
   by somebody comparing two files.

   It follows the werte-scroll prototype's timing, which is also where the HOLD
   comes from — and the hold is the point:

     reveal window   the first 62 % of each stage, THEN HOLD
     title           the first 28 % of that window
     body            starts at 14 % and spans the rest
     easing          smoothstep, so early characters land a touch faster

   THE HOLD IS NOT SPARE RANGE. A stage whose copy finishes typing at the exact
   moment it starts leaving cannot be read at all: the reader is chasing the
   last character with the wheel. Ending the reveal at 62 % buys the remaining
   38 % as a still — the object built, the sentence whole, nothing moving —
   which is the only part of the sequence anybody actually reads.

   Because it is driven by scroll position and not by a timer, scrolling back
   up un-types the text.

   It refuses to run unless the pinned layout is actually active — no support
   for scroll-driven animations, reduced motion, or a viewport under 820 px all
   mean the section is in its stacked state, where every stage is on screen at
   once and typing one of them would be nonsense. It re-checks on resize.

   MARKUP, all data attributes, so no class name is baked in here:

     [data-stream]         the TRACK: the tall element the sticky stage lives
                           in. Optionally data-stream-reveal to move the hold.
     [data-stream-stage]   one per stage, in order.
     [data-stream-line]    a line of copy inside a stage. Its value is
                           "from span", both fractions of the reveal window;
                           an empty value takes the body default.

   Accessibility: the streamed span is aria-hidden and a .visually-hidden twin
   carries the full sentence, so assistive technology always gets the whole
   line no matter where the scroll happens to be. Nothing is ever announced
   half-written. */

(function () {
  'use strict';

  var TRACK = '[data-stream]';
  var STAGE = '[data-stream-stage]';
  var LINE = '[data-stream-line]';
  var REVEAL = 0.62;          /* of a stage; the rest is the hold */
  var DEFAULT_LINE = [0.14, 0.72];
  var MIN_WIDTH = 820;        /* keep in step with the media queries in components.css */

  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }
  function smoothstep(x) { return x * x * (3 - 2 * x); }

  function pinned() {
    if (!window.matchMedia) return false;
    if (!(window.CSS && CSS.supports && CSS.supports('animation-timeline', 'view()'))) return false;
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) return false;
    return matchMedia('(min-width: ' + MIN_WIDTH + 'px)').matches;
  }

  function num(v, fallback) {
    var n = parseFloat(v);
    return isFinite(n) ? n : fallback;
  }

  /* Split one element into a streamed span and a full-text twin for AT. */
  function prepare(el) {
    var full = el.textContent.replace(/\s+/g, ' ').trim();
    var stream = document.createElement('span');
    stream.className = 'cf-stream__text';
    stream.setAttribute('aria-hidden', 'true');
    var whole = document.createElement('span');
    whole.className = 'visually-hidden';
    whole.textContent = full;
    el.textContent = '';
    el.appendChild(stream);
    el.appendChild(whole);

    var slice = (el.getAttribute('data-stream-line') || '').trim().split(/\s+/);
    return {
      el: el, full: full, stream: stream, shown: -1,
      from: num(slice[0], DEFAULT_LINE[0]),
      span: num(slice[1], DEFAULT_LINE[1])
    };
  }

  function build(track) {
    var stages = [].slice.call(track.querySelectorAll(STAGE));
    if (!stages.length) return null;
    var parts = stages.map(function (stage) {
      return [].slice.call(stage.querySelectorAll(LINE)).map(prepare);
    });
    if (!parts.some(function (lines) { return lines.length; })) return null;

    var caret = document.createElement('span');
    caret.className = 'cf-stream__caret';
    caret.setAttribute('aria-hidden', 'true');
    return {
      track: track,
      parts: parts,
      caret: caret,
      active: -1,
      reveal: num(track.getAttribute('data-stream-reveal'), REVEAL)
    };
  }

  function teardown(state) {
    state.parts.forEach(function (lines) {
      lines.forEach(function (line) { line.el.textContent = line.full; });
    });
    if (state.caret.parentNode) state.caret.parentNode.removeChild(state.caret);
  }

  function paint(line, p) {
    var n = Math.round(line.full.length * smoothstep(clamp(p, 0, 1)));
    if (n === line.shown) return;
    line.shown = n;
    line.stream.textContent = line.full.slice(0, n);
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
    var local = clamp((f - stage) / state.reveal, 0, 1);

    /* The caret sits on the line being typed, not on the last line in the
       block. Two lines was the values section's whole case and "last" was the
       same answer; with four it parks a blinking cursor on an empty paragraph
       two lines below the one that is actually moving. */
    var lines = state.parts[stage];
    var cursor = 0;
    lines.forEach(function (line, i) {
      var p = (local - line.from) / line.span;
      paint(line, p);
      if (p > 0) cursor = i;
    });

    /* Every other stage sits at rest, whole — scrolling past and back must not
       leave a half-typed sentence behind. */
    state.parts.forEach(function (other, i) {
      if (i === stage) return;
      var done = i < stage ? 1 : 0;
      other.forEach(function (line) { paint(line, done); });
    });

    var here = stage + ':' + cursor;
    if (lines.length && state.active !== here) {
      state.active = here;
      lines[cursor].stream.parentNode.appendChild(state.caret);
    }
    state.caret.classList.toggle('is-resting', !lines.length || local >= 1);
  }

  function init() {
    [].slice.call(document.querySelectorAll(TRACK)).forEach(function (track) {
      var state = null, ticking = false;

      function frame() { ticking = false; if (state) run(state); }
      function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(frame); } }

      function sync() {
        if (pinned() && !state) {
          state = build(track);
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
