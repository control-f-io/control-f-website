/* Team Closer — Hover Spotlight
   ------------------------------------------------------------
   Sets --spot-cx / --spot-cy / --spot-r on .cf-team-closer to match
   whichever .cf-team-closer__spot is currently hovered/active, so the
   radial-gradient darken layer in cf-reveal.css can follow that person
   around the group photo. A plain CSS :hover cannot forward a hovered
   child's own position up to a gradient painted on its parent, so this
   is the one place a few lines of script are simpler and more correct
   than a pure-CSS approximation (see the comment in cf-reveal.css).
   Pointer + touch both route through the same two handlers.

   SINGLE SOURCE OF TRUTH FOR THE SEVEN SPOTS' COORDINATES
   ------------------------------------------------------------
   The group photo (gruppe.jpg) is used on both language versions of
   this page (/ueber-uns.html and /en/ueber-uns.html), and each spot's
   hit-box, glow-centre and name-label position used to be hand-typed
   as inline `style` attributes on BOTH pages' markup. That meant every
   coordinate tweak had to be copied into two files by hand -- easy to
   miss, and the two pages silently drifted apart when it happened.

   Names aren't translated, so `data-name` is a stable, language-
   independent key: the coordinate data now lives ONCE, here, keyed by
   that name, and applied to whichever page's spots are present. The
   markup itself only needs `data-name="…"` on each span; every other
   positioning custom property is set from this table at runtime.
   Edit a person's numbers here and both language pages pick it up. */
  // COORDINATES BELOW ARE DERIVED, NOT HAND-TUNED
  // ------------------------------------------------------------
  // Earlier revisions of this table were nudged by eye, one small
  // adjustment at a time, and adjacent people's hit-boxes ended up
  // overlapping (Piet's box reached x=52% while Daniel's started at
  // x=51%) -- so hovering near a shared edge, e.g. Piet's face, could
  // trigger the WRONG person's spotlight. Fixed by re-measuring the
  // source photo (design-system/assets/img/team/gruppe.jpg, 1600x1067)
  // directly: each person's actual horizontal extent was read off a
  // percentage grid overlaid on the raw image, boundaries between
  // neighbours were drawn at the real midpoint between them (so the
  // seven x-ranges tile the row with NO gaps or overlaps), and those
  // raw-image percentages were then remapped through the object-fit:
  // cover / object-position: 50% 42% crop (raw Y 6.57%-90.92% maps to
  // the visible box's 0%-100%; X is uncropped, 1:1) to get the y1/y2/
  // faceY values below. Changing a person's box: re-measure from the
  // photo and keep neighbouring x-ranges touching, don't just nudge a
  // number until it looks right, or the overlap bug comes back.
  var SPOT_COORDS = {
    'Birk Burghardt':      { x1: '5%',  y1: '-0.68%', x2: '24%', y2: '110.76%', faceY: '14.73%', labelX: '83.44%', labelY: '32.38%' },
    'Marie Ernø-Møller':   { x1: '24%', y1: '8.80%',  x2: '39%', y2: '65.71%',  faceY: '8%',      labelX: '80.53%', labelY: '-2.88%', centerXOffset: 40 },
    'Piet Brömmel':        { x1: '39%', y1: '1.69%',  x2: '52%', y2: '37.26%',  faceY: '4%',      labelX: '77.41%', labelY: '72.30%', centerXOffset: 40 },
    'Daniel Tremer':       { x1: '52%', y1: '1.69%',  x2: '70%', y2: '110.76%', faceY: '10%',     labelX: '33.33%', labelY: '31.83%', centerXOffset: -20, radiusScale: 0.65 },
    'Simon Deussen':       { x1: '70%', y1: '-1.87%', x2: '98%', y2: '110.76%', faceY: '8.80%',  labelX: '31.86%', labelY: '27.29%' },
    'Henry Beiker':        { x1: '18%', y1: '33.70%', x2: '54%', y2: '110.76%', faceY: '52%',    labelX: '48.55%', labelY: '47.34%', radiusScale: 0.55 },
    'Robin Marzucca':      { x1: '54%', y1: '37.26%', x2: '82%', y2: '110.76%', faceY: '53.86%', labelX: '42.15%', labelY: '46.20%' }
  };

(function () {
  var figures = document.querySelectorAll('.cf-team-closer');
  figures.forEach(function (figure) {
    var spots = figure.querySelectorAll('.cf-team-closer__spot');
    if (!spots.length) return;

    spots.forEach(function (spot) {
      var name = spot.getAttribute('data-name');
      var c = name && SPOT_COORDS[name];
      if (!c) return;
      spot.style.setProperty('--x1', c.x1);
      spot.style.setProperty('--y1', c.y1);
      spot.style.setProperty('--x2', c.x2);
      spot.style.setProperty('--y2', c.y2);
      spot.style.setProperty('--face-y', c.faceY);
      spot.style.setProperty('--label-x', c.labelX);
      spot.style.setProperty('--label-y', c.labelY);
    });

    function activate(spot) {
      var rect = spot.getBoundingClientRect();
      var figRect = figure.getBoundingClientRect();
      var name0 = spot.getAttribute('data-name');
      var coords0 = name0 && SPOT_COORDS[name0];
      // The hit-box is drawn to tile cleanly with its neighbours for
      // accurate hover detection (see the SPOT_COORDS comment above), so
      // it doesn't always sit exactly centred on the person's actual
      // face -- an optional per-person centerXOffset (in px) nudges only
      // the glow's horizontal centre, independent of the hit-box, so
      // fixing where the light falls never risks reopening the hover
      // overlap bug.
      var centerXOffset = (coords0 && coords0.centerXOffset) || 0;
      var cx = rect.left + rect.width / 2 - figRect.left + centerXOffset;
      // The hit-box spans the whole body (head to feet), so its vertical
      // MIDPOINT lands around the chest/waist, not the face -- the glow
      // was centring there and only grazing the top of the head. Each spot
      // carries its own --face-y (a figure-relative % of that person's
      // actual face centre, set inline in the markup), and that -- not the
      // box's own midpoint -- is what the glow centres on vertically.
      var faceYPercent = parseFloat(getComputedStyle(spot).getPropertyValue('--face-y')) || 50;
      // Centre a little BELOW the face rather than exactly on it: a glow
      // centred on the face alone faded out around the neck and cut off
      // the shoulders/chest, so the highlighted area read as "just a head"
      // rather than "this whole person". Nudging the centre down by ~14%
      // of the figure's height (roughly one head-height) plus a larger
      // radius keeps the face at full brightness while extending the glow
      // down over the body.
      var cy = (faceYPercent / 100) * figRect.height + figRect.height * 0.14;
      // Boxes are body+head sized (roughly one person's shoulder width but
      // full photo height), so basing the radius on Math.max(width,height)
      // used the box's HEIGHT -- nearly the whole photo -- and lit up half
      // the group at once. The radius should track how WIDE a person is,
      // not how tall their hit-box is, so it's based on width alone (with a
      // floor so a narrow box like Marie's or Piet's still gets a readable
      // glow rather than a sliver).
      // Some people's hit-box is intentionally wider than their body (to
      // close a gap with a neighbour, or reach a shared boundary with no
      // overlap -- see the SPOT_COORDS comment above), and a radius based
      // on that full width would light up more of the photo than just
      // them. An optional per-person radiusScale in SPOT_COORDS overrides
      // the 0.95 default so the hit-box can stay wide (correct hover
      // detection) while the visible glow stays sized to the person.
      var name = spot.getAttribute('data-name');
      var coords = name && SPOT_COORDS[name];
      var radiusScale = (coords && coords.radiusScale) || 0.95;
      var r = Math.max(rect.width * radiusScale, 150);
      figure.style.setProperty('--spot-cx', cx + 'px');
      figure.style.setProperty('--spot-cy', cy + 'px');
      figure.style.setProperty('--spot-r', r + 'px');
      figure.classList.add('is-spotlit');
    }

    function deactivate() {
      figure.classList.remove('is-spotlit');
    }

    spots.forEach(function (spot) {
      spot.addEventListener('pointerenter', function () { activate(spot); });
      spot.addEventListener('pointerleave', deactivate);
      spot.addEventListener('touchstart', function () { activate(spot); }, { passive: true });
    });
    figure.addEventListener('touchend', deactivate, { passive: true });
  });
})();
