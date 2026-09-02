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
   for scroll-driven animations, reduced motion, or a viewport below the
   consumer's own gate all mean the section is in its stacked state, where
   every stage is on screen at once and typing one of them would be nonsense.
   It re-checks on resize.

   AND IT ASKS THE TRACK RATHER THAN RESTATING THE GATE. This used to test
   `matchMedia('(min-width: 820px)')` against a constant with "keep in step
   with the media queries in components.css" beside it, and the three
   consumers had already walked away from it in three different directions:

     .cf-values__track   ueber-uns     no-preference and (min-width: 51.25rem)
     .cf-pin             expertise     no-preference and (min-width: 64rem)
                                                     and (min-height: 45rem)
     .sp-track/.sp4-track/.map-track   landing, acts.css — the same 64rem x 45rem

   51.25rem IS the 820 this named, converted when the register took the
   threshold in — so the constant was stale in units as well as in value: at a
   24 px root the gate it mirrors waits for 1230 px and this still engaged at
   820. Neither of the other two has ever been 820, and NEITHER OF THE THREE
   HEIGHT TERMS WAS HERE AT ALL.

   .cf-values__track HAS ONE NOW TOO — `and (min-height: 45rem)`, the same
   term the other two rows already carried the day this paragraph was written.
   Asking the track rather than restating the gate is what made that fix free
   here: this file changed nothing to pick it up, because it was never told
   the gate's shape in the first place.

   What that cost, measured on the landing page before this: at any viewport
   whose width cleared 820 while the track's own gate did not — 860 x 900,
   1000 x 800, 1023 x 760, 1280 x 700, 1440 x 719 — build() emptied act 2's
   four paragraphs into their streamed spans and run() then bailed on
   `travel <= 0`, so the 481 characters of "Tausende Sensoren, ein Strom." and
   the three lines under it were never written back. Zero characters on screen,
   at every scroll position, for the whole life of the page. The a11y twin
   still carried the sentence, so it was sighted readers only, and 1366 x 768 —
   a viewport height of about 660 once the browser takes its chrome — is
   squarely inside the band.

   So the question is asked of the element that answers it. A track's tall
   height and its `view-timeline-name` are declared in the SAME rule inside the
   SAME gate — all three consumers are written that way — so a computed
   view-timeline-name that is not `none` means precisely "this track is tall,
   pinned, and scrubbing", in whatever units and with whatever height term that
   consumer wrote, and it folds in @supports and reduced-motion for free
   because the declaration sits inside those too. act-rail.js reads the same
   property for the same reason; the note over `budget` there carries the
   measurements.

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

  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }
  function smoothstep(x) { return x * x * (3 - 2 * x); }

  /* Per track, and computed rather than restated — see the header. `typeof`
     and not a bare `!== 'none'`: a browser with no view-timeline-name at all
     returns undefined for it, and undefined is not 'none', so the loose test
     would read "pinned" in exactly the tier that has no timelines to pin
     with. */
  function pinned(track) {
    var name = getComputedStyle(track).viewTimelineName;
    return typeof name === 'string' && name !== '' && name !== 'none';
  }

  function num(v, fallback) {
    var n = parseFloat(v);
    return isFinite(n) ? n : fallback;
  }

  /* THE INLINE AXIS, MEASURED BEFORE IT IS TAKEN.

     prepare() below empties the element it types into, so from that moment on
     the element's max-content is the characters typed SO FAR — nothing at
     rest. base.css caps .text-foil at max-content for a reason it calls
     load-bearing (`background-clip: text` paints across the WHOLE element box,
     so a headline in a column samples only the first fraction of its ramp),
     and it EXCLUDES a stream-owned line from that cap for exactly the fact
     above: capping a rewritten element at its own content is cyclic, and
     measured on this page it collapsed all four card titles to 22 px and 0.

     THE EXCLUSION WAS RIGHT AND ITS COST WAS NEVER MEASURED. It is measured
     now, on expertise.html, ink over box on the rendered page:

       Maschinenbau           276 / 518 px at 1280,  276 / 593 at 1920
       Erneuerbare Energien   406 / 518              406 / 593
       Großanlagen            244 / 518              244 / 593
       Flotten                136 / 518              136 / 593

     Sampled against --gradient-foil-ink, whose stops sit at 0 / 23.5 / 47 /
     73.5 / 100 %, "Maschinenbau" rendered 0.8–53.0 % of the ramp at 1280 and
     0.5–46.2 % at 1920 — where it does not reach Sky 800 at all — and
     "Flotten" 22.9 %. VIOLETT 800 NEVER APPEARED ON THE PAGE, at either
     width, on any of the four. That is the same failure base.css's own note
     records for the footer title before the cap existed, reproduced on the
     four largest foil moments in the system by the exclusion that spares them
     the cap.

     SO THE STREAM HANDS THE AXIS BACK BEFORE IT TAKES IT. The full string is
     still in the element here, so its max-content is the real one — the same
     number `max-width: max-content` would have resolved to, wrap and all —
     and it is published as a custom property the class can cap on instead.
     Nothing is cyclic: the measurement happens once, before the first
     character is removed, and the ramp is then fixed at the FULL string's
     width for the whole of the typing. It does not rescale letter by letter,
     which is the other failure base.css names; the light crosses a plate of
     the final size and the characters arrive into it.

     IN `em`, AND THAT IS WHAT MAKES IT SURVIVE A RESIZE. prepare() runs once
     per gate flip, not once per resize, so a reservation in px would go stale
     the moment the type moved under it. The same string in the same face
     scales linearly with its own font-size — --tracking-display is in em too —
     so the ratio is the stable form of the measurement.

     THE CARET IS PART OF THE RESERVATION, and it is measured rather than
     named. It is a real inline-block in the flow (0.45em wide, 0.1em of
     margin), so a box capped at the ink alone drops it to a second line the
     moment the line finishes typing. Appending it for the measurement costs
     one node in and out per line at init and keeps the number exact if its
     own CSS ever moves; the alternative is that 0.55em written down a second
     time in a file that cannot see the first. */
  function reserve(el, caret) {
    var width = el.style.width;
    el.appendChild(caret);
    el.style.width = 'max-content';
    var natural = el.getBoundingClientRect().width;
    el.style.width = width;
    el.removeChild(caret);
    var size = parseFloat(getComputedStyle(el).fontSize);
    if (natural > 0 && isFinite(size) && size > 0) {
      el.style.setProperty('--stream-inline', (natural / size).toFixed(4) + 'em');
    }
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

    var caret = document.createElement('span');
    caret.className = 'cf-stream__caret';
    caret.setAttribute('aria-hidden', 'true');

    /* MEASURE EVERY LINE FIRST, THEN SPLIT THEM. Two passes and not one, and
       the reason is the same one reserve() turns on: the moment prepare()
       empties one element, the next element's measurement is taken against a
       document that has changed under it. Reading every natural width while
       the whole track is still whole is one layout for the pass rather than
       one per line, and it is the only order in which every number is the
       number the page actually had. */
    var lines = stages.map(function (stage) {
      return [].slice.call(stage.querySelectorAll(LINE));
    });
    lines.forEach(function (stage) {
      stage.forEach(function (el) { reserve(el, caret); });
    });

    var parts = lines.map(function (stage) { return stage.map(prepare); });
    if (!parts.some(function (stage) { return stage.length; })) return null;

    return {
      track: track,
      parts: parts,
      caret: caret,
      active: -1,
      reveal: num(track.getAttribute('data-stream-reveal'), REVEAL)
    };
  }

  /* Everything this file took, given back — the sentence and the axis both.
     The reservation is only correct while the element it describes is being
     rewritten; once the copy is whole again the class caps on max-content
     itself, and a stale em left behind would cap it twice. */
  function teardown(state) {
    state.parts.forEach(function (lines) {
      lines.forEach(function (line) {
        line.el.textContent = line.full;
        line.el.style.removeProperty('--stream-inline');
      });
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
    /* A TRACK WITH NO TRAVEL IS SHOWN WHOLE, NOT LEFT BLANK. build() has
       already emptied every line into its streamed span by the time this runs,
       so `return` here does not mean "leave it alone" — it means the copy
       stays at nought characters until something else writes it back, and the
       only thing that does is teardown() on a resize that flips the gate.
       That is how 481 characters of act 2 went missing whenever the gate this
       file tested disagreed with the gate that sets the track's height, and it
       is worth keeping the direction of the failure right even now that the
       two agree: whole is the readable state, blank is not. */
    if (travel <= 0) {
      state.parts.forEach(function (lines) {
        lines.forEach(function (line) { paint(line, 1); });
      });
      return;
    }
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
        if (pinned(track) && !state) {
          state = build(track);
          if (!state) return;
          window.addEventListener('scroll', onScroll, { passive: true });
          run(state);
        } else if (!pinned(track) && state) {
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
