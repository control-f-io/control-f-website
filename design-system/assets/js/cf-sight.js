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

   TWO SOURCES, ONE MEASUREMENT. On a desk the eye moves and the screen stays;
   on a phone the screen moves and the eye stays. Both are the same quantity —
   the angle between the reader's line of sight and the plane of the screen —
   read from opposite ends. The pointer is that angle on a desk. The TILT of
   the device is that angle in a hand, and it is the one this file used to
   throw away: every coarse pointer rested, because a finger has no position
   between taps. A finger still has none. The phone does, and it is the very
   thing a holographic foil is read by — a foil catalogue is photographed
   tilting, and a phone in a hand is a sheet being tilted. Exactly one source
   runs on any page: the pointer where there is a fine one, the tilt where
   there is not and a sensor answers without being asked for, and neither
   where neither holds. Never both. One reader, one light.

   THE REACH IS A BRAND ANGLE, NOT A NUMBER PICKED FOR FEEL. The desk model
   flattens the rake to 90° when the line of sight has fallen to --angle-b,
   26.57°, and the sight chapter draws that as its plan view. A sight line
   makes --angle-b with a plane when the plane is tilted --angle-a, 63.43°,
   away from square — the two isometric angles are complements. So a phone
   tilted 63.43° from the pose it is held in shows the foil flat, exactly as
   a desk reader a half-viewport to the side does. The reach is read out of
   --angle-a in the stylesheet at start, and the literal below is only what
   stands in when a page has no tokens.

   THE STILL IS WHEREVER THE HAND SETTLES. The sensor reports the device
   against gravity, and nobody reads a phone at a fixed angle to gravity: in a
   chair it is 40° off, in bed it is 90°, and neither reader is looking at the
   page obliquely. So the departure is measured from a baseline that follows
   the hand slowly — a first-order filter with a two-second time constant —
   rather than from the sensor's zero. A tilt is seen at once and at full
   size, because the baseline has not moved yet; a phone held still, in any
   pose, settles back to the designer's rake within a few seconds, because
   the baseline has caught up. A physical foil stays shifted while it is held
   tilted; this one does not, and that is the trade: a reader who changes
   posture is not left with the flat 90° rake for the rest of the page.

   WHAT IT WRITES, AND NOTHING ELSE:

     --sight-h        on .text-foil — how square the reader is to the type,
                      1 directly in front of it, 0 a half-viewport to the side
                      or --angle-a of tilt away. Multiplied into the rake in
                      base.css.
     --field-light-x  on .cf-ground--lit — where the pool of light stands
                      across the floor, as a percentage of the section.

   Both are angles and positions. Neither is a colour, an opacity or a
   composite, so no contrast figure in this system is a function of the
   pointer or of the sensor, and none of them has to be re-measured for this
   file. That is the rule the chapter states and the reason it is only these
   two properties: what a material may show the reader about where they are
   standing is WHERE ITS LIGHT COMES FROM, never how much of it there is.

   WHEN IT REFUSES TO RUN. Reduced motion. No support for scroll-driven
   animations — the same gate base.css puts on the swing, so the CSS and the
   script can never disagree about whether the vertical half is running. The
   pointer source needs a pointer that can hover. The tilt source needs a
   sensor the page may read WITHOUT ASKING: where the browser gates the
   sensor behind a permission prompt (Safari on iOS exposes a
   requestPermission function for this) the source is declined outright,
   because a prompt for atmosphere is a cost the reader never agreed to pay
   and the chapter's rule is that sight is the last layer. It also needs a
   secure context, which is where browsers deliver the event at all. It
   re-checks on a media-query change and puts everything back when a
   condition stops holding.

   COST. One passive listener — pointermove or deviceorientation, never both
   — coalesced to one rAF. Only elements currently on screen are tracked,
   via one IntersectionObserver. Both written values are quantised — the rake
   to 1/64 of its swing, the pool to whole percent — so a slow gesture writes
   on a minority of its frames and a still pointer or a settled phone writes
   on none. --field-light-x is inherited (it has to reach a pseudo-element),
   so its quantisation is the coarser of the two on purpose. The tilt
   baseline is arithmetic on two numbers per event and allocates nothing.

   Delete the tag and every page renders as it did before this file existed. */

(function () {
  'use strict';

  var FOIL = '.text-foil';
  var GROUND = '.cf-ground--lit';

  /* 1/64 of the swing is 0.42° of rake — under the width of the antialias on
     a stop boundary, and 64 steps across a half-viewport is one step every
     15 px at 1920. Whole percent on the pool is ~14 px of section at the same
     width, well inside a 1152 px ellipse's own falloff. On the tilt source
     one step of the foil is a degree of the hand, which is under a resting
     hand's own tremor — so a phone that is merely being held flickers
     between two adjacent steps and the damping in base.css turns that into
     the faint shimmer a held sheet of foil actually has. */
  var FOIL_STEPS = 64;

  /* The reach of the tilt, in degrees. Read from --angle-a at start; this is
     the value when there is no stylesheet to read it from. */
  var REACH_FALLBACK = 63.43;

  /* The time constant of the baseline the tilt is measured against. A hand
     takes well under half a second to tilt a phone and a few seconds to
     settle; two seconds lets the whole of a gesture through at full size and
     has the still back before the reader has read the next line. */
  var SETTLE_MS = 2000;

  var mqPointer = null;
  var mqMotion = null;
  var observer = null;
  var visible = [];        /* the tracked elements currently on screen */
  var source = null;       /* 'pointer' | 'tilt' | null — never both */
  var pointerX = null;     /* null until the reader has actually moved one */
  var tilt = null;         /* degrees off the still, null until a reading */
  var tiltBase = null;     /* the still, following the hand slowly */
  var tiltAt = 0;          /* timestamp of the last reading, for the filter */
  var reach = REACH_FALLBACK;
  var frame = 0;

  function common() {
    if (!window.matchMedia || !window.IntersectionObserver || !window.requestAnimationFrame) return false;
    if (!(window.CSS && CSS.supports && CSS.supports('animation-timeline', 'view()'))) return false;
    return !mqMotion.matches;
  }

  /* The sensor is admitted only where it can be read without a prompt. A
     browser that exposes requestPermission on the event class is one that
     will show a dialog before delivering a single reading, and this file
     never raises one. */
  function tiltAvailable() {
    if (!('DeviceOrientationEvent' in window) || !window.DeviceOrientationEvent) return false;
    if (typeof window.DeviceOrientationEvent.requestPermission === 'function') return false;
    if (window.isSecureContext === false) return false;
    return true;
  }

  function pick() {
    if (!common()) return null;
    if (mqPointer.matches) return 'pointer';
    if (tiltAvailable()) return 'tilt';
    return null;
  }

  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }

  /* --angle-a as a number of degrees, so the reach follows the token. */
  function readReach() {
    try {
      var raw = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--angle-a'));
      if (raw > 0 && raw < 90) return raw;
    } catch (e) { /* no stylesheet, no token: the fallback stands */ }
    return REACH_FALLBACK;
  }

  /* Squareness on one axis: 1 when the reader is in front of the centre of the
     box, falling to 0 a half-viewport away from it. A half-viewport is the
     furthest a pointer can get from something in the middle of the screen, so
     the full range is reachable for a centred element and clipped for one at
     an edge — which is the honest answer. Something pinned to the left margin
     is never seen head-on from the right of the screen. */
  function squareness(rect) {
    var reachPx = window.innerWidth / 2;
    if (reachPx <= 0) return 1;
    var centre = rect.left + rect.width / 2;
    return 1 - clamp(Math.abs(pointerX - centre) / reachPx, 0, 1);
  }

  /* The same squareness from the tilt. One plane, so one value for every
     element on it: the phone does not tilt differently under each headline. */
  function tiltSquareness() {
    return 1 - clamp(Math.abs(tilt) / reach, 0, 1);
  }

  /* Where the reader stands across the floor when the floor has been tilted.
     Dipping the right edge of the screen away is looking at it from the
     left, so the pool moves left as the tilt goes positive, and it reaches
     the edge of the section at the same --angle-a the foil goes flat at. */
  function tiltPool() {
    return 50 - 50 * clamp(tilt / reach, -1, 1);
  }

  function apply() {
    frame = 0;
    if (source === 'pointer' && pointerX === null) return;
    if (source === 'tilt' && tilt === null) return;
    if (!source) return;
    for (var i = 0; i < visible.length; i++) {
      var el = visible[i];
      var rect = el.getBoundingClientRect();
      if (!rect.width) continue;

      if (el.matches(FOIL)) {
        var sq = source === 'tilt' ? tiltSquareness() : squareness(rect);
        var h = Math.round(sq * FOIL_STEPS) / FOIL_STEPS;
        if (el.__cfSight !== h) { el.__cfSight = h; el.style.setProperty('--sight-h', h); }
      } else {
        var pos = source === 'tilt' ? tiltPool() : (pointerX - rect.left) / rect.width * 100;
        var x = Math.round(clamp(pos, 0, 100));
        if (el.__cfSight !== x) { el.__cfSight = x; el.style.setProperty('--field-light-x', x + '%'); }
      }
    }
  }

  function schedule() {
    if (!frame) frame = requestAnimationFrame(apply);
  }

  function onMove(e) { pointerX = e.clientX; schedule(); }

  /* Which of the sensor's two axes is the screen's horizontal depends on how
     the screen is turned. Upright, the screen's vertical is the device's long
     axis and the left-right tilt is gamma. Turned on its side, the screen's
     vertical is the device's short axis and the same tilt is beta — with its
     sign following which way the device was turned, so that dipping the
     screen's right edge is positive either way round, as gamma has it. */
  function screenAngle() {
    if (window.screen && screen.orientation && typeof screen.orientation.angle === 'number') return screen.orientation.angle;
    if (typeof window.orientation === 'number') return (window.orientation + 360) % 360;
    return 0;
  }

  function onTilt(e) {
    var angle = screenAngle();
    var raw;
    if (angle === 90) raw = e.beta;
    else if (angle === 270) raw = e.beta === null ? null : -e.beta;
    else raw = e.gamma;
    if (raw === null || raw === undefined || raw !== raw) return;   /* no sensor behind the event */

    var now = e.timeStamp || Date.now();
    if (tiltBase === null) {
      /* The first reading is the still: the page opens square to the reader,
         wherever the reader is. */
      tiltBase = raw;
    } else {
      var k = 1 - Math.exp(-(now - tiltAt) / SETTLE_MS);
      tiltBase += (raw - tiltBase) * k;
    }
    tiltAt = now;
    tilt = raw - tiltBase;
    schedule();
  }

  /* Leaving the window is not "the reader is at the edge" — it is "the reader
     is not here". Both materials go back to the designed still rather than
     freezing wherever the pointer happened to cross the boundary. A page put
     in the background is the same case for the tilt: the sensor stops, and
     the baseline is dropped so the next reading is a fresh still rather than
     a departure from a pose the reader may have left long ago. */
  function onLeave() {
    pointerX = null;
    tilt = null;
    tiltBase = null;
    for (var i = 0; i < visible.length; i++) rest(visible[i]);
  }

  function onVisibility() {
    if (document.visibilityState === 'hidden') onLeave();
  }

  function rest(el) {
    el.__cfSight = undefined;
    el.style.removeProperty('--sight-h');
    el.style.removeProperty('--field-light-x');
  }

  function start(which) {
    if (source === which) return;
    if (source) stop();
    source = which;
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

    if (which === 'pointer') {
      window.addEventListener('pointermove', onMove, { passive: true });
      document.documentElement.addEventListener('pointerleave', onLeave);
      window.addEventListener('blur', onLeave);
    } else {
      reach = readReach();
      window.addEventListener('deviceorientation', onTilt, { passive: true });
      document.addEventListener('visibilitychange', onVisibility);
    }
  }

  function stop() {
    if (!source) return;
    window.removeEventListener('pointermove', onMove);
    document.documentElement.removeEventListener('pointerleave', onLeave);
    window.removeEventListener('blur', onLeave);
    window.removeEventListener('deviceorientation', onTilt);
    document.removeEventListener('visibilitychange', onVisibility);
    source = null;
    if (frame) { cancelAnimationFrame(frame); frame = 0; }
    if (observer) { observer.disconnect(); observer = null; }
    onLeave();
    visible = [];
  }

  function sync() {
    var which = pick();
    if (which) start(which); else stop();
  }

  function init() {
    if (!window.matchMedia) return;
    mqPointer = matchMedia('(pointer: fine)');
    mqMotion = matchMedia('(prefers-reduced-motion: reduce)');
    /* addEventListener on a MediaQueryList is the modern spelling and the only
       one worth carrying; a browser too old for it is a browser without
       scroll-driven animations, so common() has already said no. */
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
