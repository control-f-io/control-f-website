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
   cf-sphere, where the true circle is the silhouette of a ball and the two
   2:1 ellipses inside it are its equator and meridian.
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
    { id: 'cf-chevron-double', label: 'Chevron double', use: 'Skip, jump to the end, "more"',
      keyline: 'two half-rhombi, 26.57 deg', shapes: '<path d="M4 7 L14 12 L4 17"/><path d="M10 7 L20 12 L10 17"/>' },

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
    { id: 'cf-pyramid', label: 'Pyramid', use: 'Hierarchy, a maturity model, aggregation',
      keyline: 'rhombus 20 x 10 base, apex on the vertical axis',
      shapes: '<path d="M12 12 L22 17 L12 22 L2 17 Z"/><path d="M2 17 L12 4 L22 17"/>' },
    { id: 'cf-plane', label: 'Plane', use: 'A document, a report, a dataset',
      keyline: 'rhombus 20 x 10, rules parallel to the 26.57 deg edge',
      shapes: '<path d="M12 7 L22 12 L12 17 L2 12 Z"/><path d="M8 12 L14 9"/><path d="M10 14 L16 11"/>' },
    { id: 'cf-hourglass', label: 'Hourglass', use: 'Downtime, latency, a time window',
      keyline: 'two triangles, 63.43 deg',
      shapes: '<path d="M7 2 L17 2 L12 12 Z"/><path d="M7 22 L17 22 L12 12 Z"/>' },

    /* --- Instruments. A mark placed in space. ------------------------- */
    { id: 'cf-node', label: 'Node', use: 'An integration, a connection, three systems meeting',
      keyline: 'three arms at 90 / 26.57 deg, dots at the ends',
      shapes: '<path d="M12 13 V4"/><path d="M12 13 L4 17"/><path d="M12 13 L20 17"/><circle cx="12" cy="4" r="1.5" fill="currentColor"/><circle cx="4" cy="17" r="1.5" fill="currentColor"/><circle cx="20" cy="17" r="1.5" fill="currentColor"/>' },
    { id: 'cf-pin', label: 'Pin', use: 'A site, a location, one machine on the floor',
      keyline: 'ellipse 2:1 base + 90 deg stem',
      shapes: '<ellipse cx="12" cy="19" rx="6" ry="3"/><path d="M12 19 V7"/><circle cx="12" cy="5" r="2" fill="currentColor"/>' },
    { id: 'cf-target', label: 'Target', use: 'A goal, a threshold, precision',
      keyline: 'three ellipses at 2:1',
      shapes: '<ellipse cx="12" cy="12" rx="10" ry="5"/><ellipse cx="12" cy="12" rx="6" ry="3"/><ellipse cx="12" cy="12" rx="2" ry="1" fill="currentColor"/>' }
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

  function inject() {
    if (document.getElementById('cf-icon-sprite')) return;
    var host = document.createElement('div');
    host.id = 'cf-icon-sprite';
    host.setAttribute('aria-hidden', 'true');
    host.style.display = 'none';
    host.innerHTML = SPRITE;
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
