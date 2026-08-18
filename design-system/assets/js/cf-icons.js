/* ==========================================================================
   Control-F — Icon sprite
   The one file that defines the icon set. Everything else reads from here:
   the documentation page renders its gallery, its anatomy table and its
   copy-paste production block from this array, so there is exactly one place
   an icon is drawn.

   Unlike docs.js this file SHIPS. Include it once per page, or paste the
   markup it prints on foundations/iconography.html straight after <body>.

   Construction. Every glyph is drawn in a 24 x 24 box with a 2 px margin, so
   the live area is 20 x 20. Contours are 1 px and stay 1 px at every size
   (vector-effect: non-scaling-stroke). Only the four sanctioned angles are
   used: 26.57 deg (dx 2 / dy 1), 63.43 deg (dx 1 / dy 2), 45 deg and 90 deg.
   Anything round is an ellipse at 2:1 — a circle seen in isometry — except
   cf-sphere and cf-globe, where the true circle is the silhouette of a ball
   and the 2:1 ellipses inside it are its equator and meridians.

   TWO WEIGHTS, which is the part this file used to be missing. The manual's
   Icon System plate draws its first two rows as the same marks twice: a SOLID
   row and a LINE row. The line weight is the working set — it is what an
   interface uses. The solid weight is the mark at label scale, where a 1 px
   contour inside 12 px stops reading, and it is built by one rule rather than
   redrawn: a solid glyph is the isometric rhombus with a rhombus notch cut out
   of one of its four vertices. Cut the bottom vertex and the rhombus becomes a
   chevron pointing up; cut the left one and it points right. The ends stay
   pointed, because they are the rhombus's own vertices.

   The four directions are one glyph rotated by 90 deg, four times, in both
   weights. The plate's own left/right marks look wider than a rotation would
   make them, but they are a 200 px render of a compressed archive plate and
   the difference is inside its noise; a true rotation is the rule the manual
   states, so that is what is drawn here.
   ========================================================================== */

(function (global) {
  'use strict';

  /* Each entry: id, label, what it is for, the keyline it was built on, and
     the raw shapes. Stroke, size and colour come from the .cf-icon class in
     components.css — the only presentation attribute allowed here is
     fill="currentColor" on the handful of marks that are solid rather than
     drawn, because fill cannot reach into a <use> shadow tree from CSS. */
  var ICONS = [
    /* --- Direction. One glyph rotated by 90 deg, four times. The arms are
       the 26.57 deg edge of the isometric rhombus; rotating it gives 63.43
       deg, which is the same angle read off the other axis. ------------- */
    { id: 'cf-chevron-right', label: 'Chevron right', use: 'Next, forward, disclosure to the side',
      keyline: 'rhombus edge, 26.57 deg', shapes: '<path d="M4 4 L20 12 L4 20"/>' },
    { id: 'cf-chevron-left', label: 'Chevron left', use: 'Previous, back',
      keyline: 'rhombus edge, 26.57 deg', shapes: '<path d="M20 4 L4 12 L20 20"/>' },
    { id: 'cf-chevron-up', label: 'Chevron up', use: 'Collapse, scroll to top',
      keyline: 'rhombus edge, 63.43 deg', shapes: '<path d="M4 20 L12 4 L20 20"/>' },
    { id: 'cf-chevron-down', label: 'Chevron down', use: 'Expand, open a select, scroll hint',
      keyline: 'rhombus edge, 63.43 deg', shapes: '<path d="M4 4 L12 20 L20 4"/>' },
    { id: 'cf-chevron-double', label: 'Chevron double right', use: 'Skip, jump to the end, "more"',
      keyline: 'two half-rhombi, 26.57 deg', shapes: '<path d="M4 7 L14 12 L4 17"/><path d="M10 7 L20 12 L10 17"/>' },
    { id: 'cf-chevron-double-left', label: 'Chevron double left', use: 'Skip back, jump to the start',
      keyline: 'two half-rhombi, 26.57 deg', shapes: '<path d="M20 7 L10 12 L20 17"/><path d="M14 7 L4 12 L14 17"/>' },
    { id: 'cf-chevron-double-up', label: 'Chevron double up', use: 'Collapse all, back to the top',
      keyline: 'two half-rhombi, 63.43 deg', shapes: '<path d="M7 20 L12 10 L17 20"/><path d="M7 14 L12 4 L17 14"/>' },
    { id: 'cf-chevron-double-down', label: 'Chevron double down', use: 'Expand all, keep reading',
      keyline: 'two half-rhombi, 63.43 deg', shapes: '<path d="M7 10 L12 20 L17 10"/><path d="M7 4 L12 14 L17 4"/>' },
    { id: 'cf-converge', label: 'Converge', use: 'Narrow a result set, a filter, "fewer"',
      keyline: 'two chevrons crossing, 26.57 deg',
      shapes: '<path d="M3 6 L15 12 L3 18"/><path d="M21 6 L9 12 L21 18"/>' },

    /* --- Operators. 90 deg and 45 deg only. --------------------------- */
    { id: 'cf-plus', label: 'Plus', use: 'Add, expand an accordion',
      keyline: 'axes, 90 deg', shapes: '<path d="M12 3 V21"/><path d="M3 12 H21"/>' },
    { id: 'cf-minus', label: 'Minus', use: 'Remove, collapse an accordion',
      keyline: 'axis, 90 deg', shapes: '<path d="M3 12 H21"/>' },
    { id: 'cf-close', label: 'Close', use: 'Dismiss a dialog, clear a field',
      keyline: 'neutral diagonals, 45 deg', shapes: '<path d="M5 5 L19 19"/><path d="M19 5 L5 19"/>' },

    /* --- Primitives. The isometric rhombus and the isometric circle: the
       two shapes the whole language is built from. -------------------- */
    { id: 'cf-diamond', label: 'Diamond', use: 'Marker, list bullet, a point in a diagram',
      keyline: 'rhombus 20 x 10', shapes: '<path d="M12 7 L22 12 L12 17 L2 12 Z"/>' },
    { id: 'cf-diamond-nested', label: 'Diamond nested', use: 'Selected state, "you are here"',
      keyline: 'rhombus 20 x 10 + 8 x 4', shapes: '<path d="M12 7 L22 12 L12 17 L2 12 Z"/><path d="M12 10 L16 12 L12 14 L8 12 Z"/>' },
    { id: 'cf-ring', label: 'Ring', use: 'Radio, node, an empty state',
      keyline: 'ellipse 2:1', shapes: '<ellipse cx="12" cy="12" rx="10" ry="5"/><ellipse cx="12" cy="12" rx="4" ry="2"/>' },
    { id: 'cf-dot', label: 'Dot', use: 'Status, a data point, the smallest mark in the set',
      keyline: 'ellipse 2:1, filled', shapes: '<ellipse cx="12" cy="12" rx="4" ry="2" fill="currentColor"/>' },

    /* --- The solid weight. The manual's first row: the same marks with a
       body instead of a contour, for label scale and for a dark plate. Each
       chevron is the rhombus with a rhombus notch cut out of one vertex, so
       its ends stay pointed — see the note at the top of this file. Nothing
       here is a new mark; every one of them has a line twin above. ------ */
    { id: 'cf-chevron-up-solid', label: 'Chevron up, solid', use: 'The line chevron at label scale',
      keyline: 'rhombus 20 x 14, notch cut from the bottom vertex',
      shapes: '<path d="M2 12 L12 5 L22 12 L12 9 Z" fill="currentColor"/>' },
    { id: 'cf-chevron-down-solid', label: 'Chevron down, solid', use: 'The line chevron at label scale',
      keyline: 'rhombus 20 x 14, notch cut from the top vertex',
      shapes: '<path d="M2 12 L12 19 L22 12 L12 15 Z" fill="currentColor"/>' },
    { id: 'cf-chevron-right-solid', label: 'Chevron right, solid', use: 'The line chevron at label scale',
      keyline: 'rhombus 14 x 20, notch cut from the left vertex',
      shapes: '<path d="M12 2 L19 12 L12 22 L15 12 Z" fill="currentColor"/>' },
    { id: 'cf-chevron-left-solid', label: 'Chevron left, solid', use: 'The line chevron at label scale',
      keyline: 'rhombus 14 x 20, notch cut from the right vertex',
      shapes: '<path d="M12 2 L5 12 L12 22 L9 12 Z" fill="currentColor"/>' },
    { id: 'cf-close-solid', label: 'Close, solid', use: 'Dismiss, at label scale or on a dark plate',
      keyline: 'two bands on the neutral diagonals, 45 deg',
      shapes: '<path d="M4 2 L22 20 L20 22 L2 4 Z" fill="currentColor"/><path d="M20 2 L22 4 L4 22 L2 20 Z" fill="currentColor"/>' },
    { id: 'cf-diamond-solid', label: 'Diamond, solid', use: 'A bullet, a marker that has to hold at 12 px',
      keyline: 'rhombus 20 x 10, filled',
      shapes: '<path d="M12 7 L22 12 L12 17 L2 12 Z" fill="currentColor"/>' },
    /* The two holes are cut by fill-rule rather than by a second shape in the
       page colour: the page is a gradient wash, so a "hole" painted with a
       flat colour would be a patch that only matches at one scroll position. */
    { id: 'cf-diamond-nested-solid', label: 'Diamond nested, solid', use: 'Selected state at label scale',
      keyline: 'rhombus 20 x 10 with a 8 x 4 rhombus cut out',
      shapes: '<path d="M12 7 L22 12 L12 17 L2 12 Z M12 10 L16 12 L12 14 L8 12 Z" fill="currentColor" fill-rule="evenodd"/>' },
    { id: 'cf-ring-solid', label: 'Ring, solid', use: 'A node, a radio at label scale',
      keyline: 'ellipse 2:1 with a 2:1 ellipse cut out',
      shapes: '<path d="M2 12 A10 5 0 1 0 22 12 A10 5 0 1 0 2 12 Z M8 12 A4 2 0 1 0 16 12 A4 2 0 1 0 8 12 Z" fill="currentColor" fill-rule="evenodd"/>' },

    /* --- Objects. Built the way the process illustrations are built:
       a rhombus top face, vertical edges, nothing filled. -------------- */
    { id: 'cf-cube', label: 'Cube', use: 'An asset, a machine, one unit of anything',
      keyline: 'rhombus 16 x 8 + 8 px extrusion',
      shapes: '<path d="M12 4 L20 8 L12 12 L4 8 Z"/><path d="M4 8 V16"/><path d="M20 8 V16"/><path d="M12 12 V20"/><path d="M4 16 L12 20 L20 16"/>' },
    { id: 'cf-layers', label: 'Layers', use: 'The data foundation, a stack, versions',
      keyline: 'three rhombi 20 x 10, offset 5',
      shapes: '<path d="M12 2 L22 7 L12 12 L2 7 Z"/><path d="M12 7 L22 12 L12 17 L2 12 Z"/><path d="M12 12 L22 17 L12 22 L2 17 Z"/>' },
    { id: 'cf-cylinder', label: 'Cylinder', use: 'A data store, a historian, a database',
      keyline: 'ellipse 2:1 + 10 px extrusion',
      shapes: '<ellipse cx="12" cy="7" rx="8" ry="4"/><path d="M4 7 V17"/><path d="M20 7 V17"/><path d="M4 17 A8 4 0 0 0 20 17"/>' },
    { id: 'cf-sphere', label: 'Sphere', use: 'The whole plant, a fleet, global scope',
      keyline: 'circle r 9 + equator and meridian at 2:1',
      shapes: '<circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="9" ry="4.5"/><ellipse cx="12" cy="12" rx="4.5" ry="9"/>' },
    { id: 'cf-globe', label: 'Globe', use: 'Sites across countries, an export market, the whole network',
      keyline: 'the sphere plus two parallels — chords, not ellipses, so the grid reads at 16 px',
      shapes: '<circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="9" ry="4.5"/><ellipse cx="12" cy="12" rx="4.5" ry="9"/><path d="M4.2 7.5 H19.8"/><path d="M4.2 16.5 H19.8"/>' },
    { id: 'cf-sphere-cut', label: 'Sphere cut', use: 'A cross-section, one plane through a whole system',
      keyline: 'the sphere plus its equatorial plane as a 45 deg rhombus',
      shapes: '<circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="9" ry="4.5"/><ellipse cx="12" cy="12" rx="4.5" ry="9"/><path d="M12 3 L21 12 L12 21 L3 12 Z"/>' },
    { id: 'cf-coin', label: 'Coin', use: 'Cost, the business case, what a decision is worth',
      keyline: 'ellipse 2:1 + 5 px extrusion, the mark squashed onto the top face',
      shapes: '<ellipse cx="12" cy="10" rx="9" ry="4.5"/><path d="M3 10 V15"/><path d="M21 10 V15"/><path d="M3 15 A9 4.5 0 0 0 21 15"/><path d="M14.6 8.2 A3.6 1.9 0 1 0 14.6 11.8"/><path d="M9.4 9.4 H13"/><path d="M9.4 10.6 H13"/>' },
    { id: 'cf-triangle', label: 'Triangle', use: 'A peak, a threshold crossed, an alert',
      keyline: 'two 63.43 deg edges on a level base',
      shapes: '<path d="M12 4 L20 20 L4 20 Z"/>' },
    { id: 'cf-wedge', label: 'Wedge', use: 'A ramp, a run-up, capacity being built',
      keyline: 'a 63.43 deg triangle extruded along the level step',
      shapes: '<path d="M3 20 L9 8 L15 20 Z"/><path d="M9 8 L15 8 L21 20 L15 20"/>' },
    /* The cube, unaltered, with a gable over it — and the only glyph in the
       set that was ever drawn THROUGH. It carried the top face's whole rhombus
       and the far roof slope, both of which a roof of this pitch covers: the
       far slope's outward normal faces away from the viewer, so what the two
       extra paths added was the far eave and the far ridge crossing the near
       slope in an X. At --act-glyph, 16 px, that X is most of the mark. Every
       other solid here is hidden-line drawn — cf-cube omits its far verticals,
       cf-cylinder draws the near half of its base arc — and this one now is
       too: what is left is the near slope, the gable end, and the cube. */
    { id: 'cf-house', label: 'House', use: 'A site, a plant, a building — one address',
      keyline: 'the cube + a gable: rakes at 63.43 and 45 deg, ridge and eaves at 26.57',
      shapes: '<path d="M4 10 L12 14 L16 6 L8 2 Z"/><path d="M12 14 L20 10 L16 6"/><path d="M4 10 V18"/><path d="M12 14 V22"/><path d="M20 10 V18"/><path d="M4 18 L12 22 L20 18"/>' },
    { id: 'cf-overlap', label: 'Overlap', use: 'Two readings of the same thing, a correlation, interference',
      keyline: 'three 1:2 rhombi, offset by one level step of 4',
      shapes: '<path d="M8 2 L13 12 L8 22 L3 12 Z"/><path d="M12 2 L17 12 L12 22 L7 12 Z"/><path d="M16 2 L21 12 L16 22 L11 12 Z"/>' },
    { id: 'cf-pyramid', label: 'Pyramid', use: 'Hierarchy, a maturity model, aggregation',
      keyline: 'rhombus 20 x 10 base, apex on the vertical axis',
      shapes: '<path d="M12 12 L22 17 L12 22 L2 17 Z"/><path d="M2 17 L12 4 L22 17"/>' },
    { id: 'cf-plane', label: 'Plane', use: 'A document, a report, a dataset',
      keyline: 'rhombus 20 x 10, rules parallel to the 26.57 deg edge',
      shapes: '<path d="M12 7 L22 12 L12 17 L2 12 Z"/><path d="M8 12 L14 9"/><path d="M10 14 L16 11"/>' },
    { id: 'cf-hourglass', label: 'Hourglass', use: 'Downtime, latency, a time window',
      keyline: 'two triangles, 63.43 deg',
      shapes: '<path d="M7 2 L17 2 L12 12 Z"/><path d="M7 22 L17 22 L12 12 Z"/>' },
    /* The plate the site already draws at full size — .sp4-plate frames both
       photographs of act 4 this way, and .sp4-tick is the chamfer. It is the
       brand's one diagonal on an otherwise square frame, which is what stops a
       rectangle reading as a browser default border, and at 16 px the caption
       rule is what stops the frame reading as an empty box. The set had no
       flat frame at all: every other object in this block is an isometric
       solid, and a picture is not a solid. */
    { id: 'cf-plate', label: 'Plate', use: 'A framed picture, a portrait, a plate with its caption',
      keyline: 'square frame 20 x 20, 45 deg chamfer on the top-left vertex, caption rule at 90 deg',
      shapes: '<path d="M7 2 H22 V22 H2 V7 Z"/><path d="M6 18 H18"/>' },

    /* --- Instruments. A mark placed in space. ------------------------- */
    { id: 'cf-node', label: 'Node', use: 'An integration, a connection, three systems meeting',
      keyline: 'three arms at 90 / 26.57 deg, dots at the ends',
      shapes: '<path d="M12 13 V4"/><path d="M12 13 L4 17"/><path d="M12 13 L20 17"/><circle cx="12" cy="4" r="1.5" fill="currentColor"/><circle cx="4" cy="17" r="1.5" fill="currentColor"/><circle cx="20" cy="17" r="1.5" fill="currentColor"/>' },
    /* The plate draws this one landing on the plane: a dot at the top of the
       stem and an arrowhead at the bottom of it. The head is the difference
       between a marker sitting on a surface and a value arriving at one. */
    { id: 'cf-pin', label: 'Pin', use: 'A site, a location, one machine on the floor',
      keyline: 'ellipse 2:1 base + 90 deg stem, 45 deg head',
      shapes: '<ellipse cx="12" cy="19" rx="6" ry="3"/><path d="M12 19 V7"/><path d="M9.5 16 L12 19 L14.5 16"/><circle cx="12" cy="5" r="2" fill="currentColor"/>' },
    { id: 'cf-target', label: 'Target', use: 'A goal, a threshold, precision',
      keyline: 'three ellipses at 2:1',
      shapes: '<ellipse cx="12" cy="12" rx="10" ry="5"/><ellipse cx="12" cy="12" rx="6" ry="3"/><ellipse cx="12" cy="12" rx="2" ry="1" fill="currentColor"/>' },
    /* The rotor of process card 03 at icon scale, trace and all: the rings are
       1:2, the axis they are read on is horizontal, and the signal arrives
       along it carrying the same chevrons the illustration's trace does. */
    { id: 'cf-signal', label: 'Signal', use: 'A reading arriving, a sensor, live data',
      keyline: 'two 1:2 ellipses on a level axis, 45 deg chevrons',
      shapes: '<ellipse cx="15" cy="12" rx="5" ry="9"/><ellipse cx="15" cy="12" rx="2.5" ry="4.5"/><circle cx="15" cy="12" r="1.2" fill="currentColor"/><path d="M15 12 H7"/><path d="M5 10 L7 12 L5 14"/><path d="M2 10 L4 12 L2 14"/>' },
    { id: 'cf-expand', label: 'Expand', use: 'Scale, roll out, the same thing in three directions',
      keyline: 'the three isometric axes, arrowheads at both ends of each',
      shapes: '<path d="M12 3 V21"/><path d="M4 8 L20 16"/><path d="M4 16 L20 8"/><path d="M9.5 6.5 L12 3 L14.5 6.5"/><path d="M9.5 17.5 L12 21 L14.5 17.5"/><path d="M16.2 15.9 L20 16 L17.6 13"/><path d="M6.4 11 L4 8 L7.9 8.1"/><path d="M17.6 11 L20 8 L16.2 8.1"/><path d="M7.9 15.9 L4 16 L6.4 13"/>' }
  ];

  /* Every shape gets vector-effect so the contour stays 1 px whether the icon
     is set at 16 px or 96 px — the same rule the process illustrations follow.
     Doing it here rather than in the source strings keeps the drawings readable
     and guarantees not one of them is forgotten. */
  function harden(shapes) {
    return shapes.replace(/<(path|ellipse|circle|line|polygon)\b/g,
                          '<$1 vector-effect="non-scaling-stroke"');
  }

  function symbol(icon) {
    return '<symbol id="' + icon.id + '" viewBox="0 0 24 24">' + harden(icon.shapes) + '</symbol>';
  }

  /* No <defs> here on purpose. A gradient paint server referenced from inside
     a <use> shadow tree does not resolve reliably across engines — the stroke
     computes to url(#...) and then paints nothing. The light layer is therefore
     built from a lime contour plus --glow-lime in components.css, which is what
     the manual describes anyway: light as a temporary effect, not a fill.
     See the note on foundations/iconography.html. */

  var SPRITE = '<svg aria-hidden="true" style="display:none">' +
               ICONS.map(symbol).join('') +
               '</svg>';

  /* THE TWO WAYS OF INCLUDING THIS SET ARE NOT EXCLUSIVE, and the header above
     has offered both from the start: "Include it once per page, or paste the
     markup it prints on foundations/iconography.html straight after <body>."
     A page that needs a glyph before this file has run has to do BOTH — paste
     the symbol so the first paint has it, and load the script so everything
     else on the page still resolves — and doing both used to put two elements
     with the same id in one document.

     What that cost, on the landing page: seven ids twice over (the act rail's
     five marks and its two double chevrons), invalid markup, and a <use> whose
     target depends on which copy comes first in document order — this host is
     inserted at the top of <body> and a pasted sprite sits below it, so the
     script's drawing silently won every reference the page had already
     answered for itself.

     So a symbol the document already carries is not injected. The page's own
     copy is the authority: it is the one that was there for the first frame,
     and it is the one that is still there when this file is blocked, cached
     stale or switched off. SPRITE keeps the whole set — iconography.html
     prints it as the paste-in block, and a partial one would teach the wrong
     thing — and the filtering happens here, once, against the live document. */
  function inject() {
    if (document.getElementById('cf-icon-sprite')) return;
    var missing = ICONS.filter(function (icon) {
      return !document.getElementById(icon.id);
    });
    if (!missing.length) return;
    var host = document.createElement('div');
    host.id = 'cf-icon-sprite';
    host.setAttribute('aria-hidden', 'true');
    host.style.display = 'none';
    host.innerHTML = '<svg aria-hidden="true" style="display:none">' +
                     missing.map(symbol).join('') +
                     '</svg>';
    document.body.insertBefore(host, document.body.firstChild);
  }

  global.CF_ICONS = ICONS;
  global.CF_ICON_SPRITE = SPRITE;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inject);
  } else {
    inject();
  }
})(window);
