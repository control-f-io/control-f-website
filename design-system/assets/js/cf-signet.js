/* ==========================================================================
   Control-F — Signet
   A mark that stands for one thing, drawn from that thing's own name.

   WHAT THIS IS FOR. The site has surfaces where an item needs a face and has
   no photograph: a post filed without a Titelbild, a topic page, a search
   result, a position nobody has shot a picture for, and — the one that is
   still missing entirely — the plate a shared link renders on LinkedIn. The
   usual answer to that is an identicon, and every identicon library on the
   web draws the same thing: a symmetrical pixel grid in a hashed hue. It is
   deterministic, it is unique, and it belongs to no brand at all.

   This draws the same idea in the language the manual already set. The
   object is the one on foundations/geometry.html, "Isometric objects" — the
   brand's standard building block, stacked cuboids on the 2:1 lattice, top
   faces filled, 1 px contours, exactly one element carrying the lime
   gradient. Nothing here is a new shape. What the seed decides is only WHERE
   the blocks stand and HOW HIGH, which is the one degree of freedom the
   object already had: 01-discovery.svg is three stacked cuboids and this is
   a nine-plot field of them.

   THE ALPHABET IS FINITE AND ITS DENSITY IS FIXED. The nine heights are not
   nine independent draws. They are a permutation of one fixed multiset —

       0 0 0 1 1 2 2 3 3

   — so every signet in the set has exactly three empty plots, exactly two
   towers at full height, and exactly the same amount of ink. The seed
   chooses the arrangement and nothing else. That is 9! / (3! 2! 2! 2!) =
   7560 distinct marks, and it is why the set has no outliers: there is no
   seed that draws an empty field, and none that draws a solid block. A
   system that hashes into free parameters cannot promise that.

   THE LIME MOMENT IS SINGULAR BY CONSTRUCTION. Of the two full-height
   towers, the light goes on the FRONTMOST — largest a+b, ties to the larger
   a — and never on both. One lime moment per mark, which is the manual's
   rule about a screen applied to an object. It is still possible to put
   twenty lit signets on one screen, and that is what .cf-signet--ink is
   for: it is the default, and the light is opt-in. See the rules on
   components/signet.html.

   CONSTRUCTION. viewBox 120 x 120. The lattice cell is 36 x 18 — 2:1, so
   every ground edge is 26.57 deg and every vertical is 90 deg. A storey is
   18 px, which makes each block a true isometric cube. Cell (a, b) of the
   3 x 3 field has its centre at

       x = 60 + (a - b) * 18        y = 69 + (a + b) * 9

   and is drawn back to front in order of a + b, so a near tower covers a far
   one and the field reads as depth rather than as pattern. Every coordinate
   the generator emits is an integer.

   THE GRADIENT IS THE FAMILY'S, NOT A NEW ONE. Lime -> Glas -> CF-Grau on
   the near rake (63.43 deg, dx 1 / dy 2), with the #DBFC60 waypoint at 19 %
   of the lime leg that every drawing in this system carries — see the
   convention in tokens.css and scripts/check-gradient-family.py, which
   re-derives both numbers rather than trusting them. The stops are written
   as attributes and not as classes on purpose: that checker reads the SVG,
   and a stop whose colour lives in a stylesheet is a stop it cannot see.

   THE FACES ARE CLASSES, so the three greys answer to the theme. They are
   the designer's own three tones off the isometric stack — #DADADA top,
   #CFCFCF left, #C4C4C4 right — and the light comes from the upper left,
   which is where 01-discovery.svg puts it.

   HOW A PAGE USES IT. Two ways, and they are not equivalent:

     - THE MARKUP. CFSignet.svg('seed') returns a complete <svg> string.
       components/signet.html prints it for any seed you type, and a page
       that ships pastes the result. That mark is in the HTML, it is in the
       first paint, and it survives this file being blocked.
     - THE MOUNT. An element carrying data-cf-signet="seed" is filled by
       this file on DOMContentLoaded. That is for documentation and for
       surfaces whose items are not known when the page is written. It is
       never the right answer for a mark that has to be in the markup — an
       Open Graph plate, most of all, which is read by a crawler that runs
       no script at all.

   stdlib JavaScript, no dependency, no build step — the same contract as
   cf-icons.js beside it.
   ========================================================================== */

(function (global) {
  'use strict';

  /* The lattice. W and H are the cell's half-width and half-height, so the
     ratio W/H IS the 2:1 isometry and the ground edges come out at 26.57 deg
     without anyone writing an angle down. STOREY is 2H, which is what makes
     a block a cube rather than a slab. */
  var W = 18, H = 9, STOREY = 18, N = 3, CX = 60, CY = 69;

  /* The fixed multiset. Editing this changes every mark in the set at once,
     which is the point: density is a property of the system, not of a seed. */
  var HEIGHTS = [0, 0, 0, 1, 1, 2, 2, 3, 3];
  var PEAK = 3;

  /* The family's ramp, hand-carried onto an SVG the way tokens.css requires:
     one extra stop at 19 % of the lime leg. The leg here ends at 32 %, so the
     waypoint is at 6.1 %. Do not round these to tidier numbers — the gradient
     checker recomputes both from the leg's own ends. */
  var STOPS = [
    { at: '0%',    color: '#E1FF00' },
    { at: '6.1%',  color: '#DBFC60' },
    { at: '32%',   color: '#C5EBE2' },
    { at: '100%',  color: '#CFCFCF' }
  ];

  /* FNV-1a, 32-bit. Chosen because it is eight lines, has no seed table and
     gives the same answer in Python — which matters the day the Open Graph
     plates are generated by a build script rather than by this file. */
  function hash(seed) {
    var s = String(seed), h = 0x811c9dc5, i;
    for (i = 0; i < s.length; i++) {
      h ^= s.charCodeAt(i);
      h = Math.imul(h, 0x01000193) >>> 0;
    }
    return h >>> 0;
  }

  /* xorshift32. Enough for a shuffle of nine, and reproducible everywhere
     because every step is a 32-bit integer operation. */
  function stream(seed) {
    var s = hash(seed) || 0x9e3779b9;
    return function () {
      s ^= (s << 13); s >>>= 0;
      s ^= (s >>> 17);
      s ^= (s << 5);  s >>>= 0;
      return s >>> 0;
    };
  }

  /* Fisher-Yates over the fixed multiset. Uniform over the 9! orderings of
     the positions, which is uniform over the 7560 distinct marks. */
  function heights(seed) {
    var next = stream(seed), a = HEIGHTS.slice(), i, j, t;
    for (i = a.length - 1; i > 0; i--) {
      j = next() % (i + 1);
      t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }

  /* The nine plots, already in paint order: back to front by depth, and left
     to right inside a depth. Sorting here rather than at the draw site is
     what makes the occlusion a property of the model instead of of the loop
     that happens to render it. */
  function plots(seed) {
    var h = heights(seed), out = [], a, b;
    for (a = 0; a < N; a++) {
      for (b = 0; b < N; b++) {
        out.push({
          a: a, b: b, d: a + b,
          h: h[a * N + b],
          x: CX + (a - b) * W,
          y: CY + (a + b) * H
        });
      }
    }
    out.sort(function (p, q) { return (p.d - q.d) || (p.a - q.a); });
    return out;
  }

  function points(pairs) {
    return pairs.map(function (p) { return p[0] + ',' + p[1]; }).join(' ');
  }

  function poly(cls, pairs, extra) {
    return '<polygon class="' + cls + '" vector-effect="non-scaling-stroke" points="' +
           points(pairs) + '"' + (extra || '') + '/>';
  }

  /* One plot. h === 0 draws the ground rhombus alone — the plot is there and
     nothing stands on it, which is the presence ladder's own distinction and
     is why that outline is dashed rather than absent. */
  function plot(p, lit, gradientId) {
    var x = p.x, y = p.y, top, out;
    if (p.h === 0) {
      return poly('cf-signet__plot',
                  [[x, y - H], [x + W, y], [x, y + H], [x - W, y]]);
    }
    top = y - p.h * STOREY;
    out = poly('cf-signet__left',
               [[x - W, top], [x, top + H], [x, y + H], [x - W, y]]) +
          poly('cf-signet__right',
               [[x + W, top], [x, top + H], [x, y + H], [x + W, y]]);
    if (lit) {
      out += poly('cf-signet__lit',
                  [[x, top - H], [x + W, top], [x, top + H], [x - W, top]],
                  ' fill="url(#' + gradientId + ')"');
      /* The construction dots off the manual's stack: they mark the face the
         light is on, and only that face. Four of them, never more. */
      out += '<g class="cf-signet__dots">' +
             '<circle cx="' + x + '" cy="' + (top - H) + '" r="1.5"/>' +
             '<circle cx="' + (x + W) + '" cy="' + top + '" r="1.5"/>' +
             '<circle cx="' + x + '" cy="' + (top + H) + '" r="1.5"/>' +
             '<circle cx="' + (x - W) + '" cy="' + top + '" r="1.5"/>' +
             '</g>';
    } else {
      out += poly('cf-signet__top',
                  [[x, top - H], [x + W, top], [x, top + H], [x - W, top]]);
    }
    return out;
  }

  /* The near rake on the lit face. The vector is the designer's own, scaled
     off geometry.html's stack: that lit rhombus is 240 wide and its gradient
     runs (80, 160) from a point (-50, -80) off centre; this one is 36 wide,
     so both are multiplied by 0.15 and land on (12, 24) from (-7.5, -12).
     dx 1 / dy 2 is 63.43 deg, which is a sanctioned angle. */
  function gradient(id, x, top) {
    return '<linearGradient id="' + id + '" gradientUnits="userSpaceOnUse" ' +
           'x1="' + (x - 7.5) + '" y1="' + (top - 12) + '" ' +
           'x2="' + (x + 4.5) + '" y2="' + (top + 12) + '">' +
           STOPS.map(function (s) {
             return '<stop offset="' + s.at + '" stop-color="' + s.color + '"/>';
           }).join('') +
           '</linearGradient>';
  }

  /* The lit plot is the frontmost full-height tower. The list is already
     sorted back to front, so it is the last one — no comparison needed, and
     no way for the rule and the paint order to drift apart. */
  function litPlot(list) {
    var i, found = null;
    for (i = 0; i < list.length; i++) {
      if (list[i].h === PEAK) found = list[i];
    }
    return found;
  }

  /* options:
       lit    — true to carry the light. Default false: the mark is ink, and
                the lime is asked for one at a time.
       label  — an accessible name. With it the mark is role="img" and is
                announced; without it it is aria-hidden, which is correct
                wherever the item's own title stands beside it.
       id     — the gradient's id. Derived from the seed by default so the
                same seed prints the same markup byte for byte.
       class  — extra classes on the root.
  */
  function svg(seed, options) {
    var o = options || {};
    var list = plots(seed);
    var lit = o.lit ? litPlot(list) : null;
    var id = o.id || ('cf-signet-' + hash(seed).toString(36));
    var cls = 'cf-signet' + (o.lit ? '' : ' cf-signet--ink') +
              (o['class'] ? ' ' + o['class'] : '');
    var body = list.map(function (p) {
      return plot(p, lit === p, id);
    }).join('');
    var naming = o.label
      ? ' role="img" aria-label="' + String(o.label).replace(/"/g, '&quot;') + '"'
      : ' aria-hidden="true"';
    return '<svg class="' + cls + '" viewBox="0 0 120 120"' + naming +
           ' data-cf-signet-seed="' + String(seed).replace(/"/g, '&quot;') + '">' +
           (lit ? '<defs>' + gradient(id, lit.x, lit.y - lit.h * STOREY) + '</defs>' : '') +
           body +
           '</svg>';
  }

  /* Fill every [data-cf-signet] in a subtree. The attribute's value is the
     seed; data-cf-signet-lit opts into the light; data-cf-signet-label names
     the mark. An element that already holds an <svg> is left alone, so a page
     that pasted its markup and also loads this file keeps the pasted one —
     the same rule cf-icons.js applies to a pasted sprite, and for the same
     reason: the copy that was there for the first frame wins. */
  function mount(root) {
    var scope = root || document;
    var hosts = scope.querySelectorAll('[data-cf-signet]');
    var i, host, seed;
    for (i = 0; i < hosts.length; i++) {
      host = hosts[i];
      if (host.querySelector('svg')) continue;
      seed = host.getAttribute('data-cf-signet');
      host.innerHTML = svg(seed, {
        lit: host.hasAttribute('data-cf-signet-lit'),
        label: host.getAttribute('data-cf-signet-label'),
        /* Two hosts with the same seed on one page would otherwise mint the
           same gradient id twice. The index keeps the document valid without
           making the printed markup non-deterministic — svg() still derives
           the plain id when nobody passes one. */
        id: 'cf-signet-' + hash(seed).toString(36) + '-' + i
      });
    }
  }

  global.CFSignet = {
    svg: svg,
    mount: mount,
    heights: heights,
    hash: hash,
    /* The size of the alphabet, computed rather than quoted, so the number on
       the documentation page cannot drift from the multiset above it. */
    count: (function () {
      var f = function (n) { return n <= 1 ? 1 : n * f(n - 1); };
      var counts = {}, k, d = 1;
      HEIGHTS.forEach(function (h) { counts[h] = (counts[h] || 0) + 1; });
      for (k in counts) { if (counts.hasOwnProperty(k)) { d *= f(counts[k]); } }
      return f(HEIGHTS.length) / d;
    }())
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { mount(); });
  } else {
    mount();
  }
})(window);
