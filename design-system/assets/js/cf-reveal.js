/* Control-F — reveal + one-shot typing for .cf-reveal-track (#wer-wir-sind).

   Replaces the shared scroll-scrubbed engine (cf-stream.js) for this one
   section only: elements just fade up once when they cross into the
   viewport, and the description paragraph plays a normal typewriter
   animation once instead of tracking scroll position. Nothing here reads
   or writes [data-stream*] -- cf-stream.js and every other consumer of it
   are untouched. */

(function () {
  'use strict';

  var TRACK = '.cf-reveal-track';
  var TYPE_SPEED_MS = 6;

  function prefersReducedMotion() {
    return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  function typeOnce(el) {
    if (el.dataset.cfTyped) return;
    el.dataset.cfTyped = '1';

    var full = el.textContent.replace(/\s+/g, ' ').trim();
    if (prefersReducedMotion()) {
      el.textContent = full;
      el.classList.add('is-typed');
      return;
    }

    var caret = document.createElement('span');
    caret.className = 'cf-type__caret';
    caret.setAttribute('aria-hidden', 'true');

    var visible = document.createElement('span');
    visible.setAttribute('aria-hidden', 'true');

    var fullText = document.createElement('span');
    fullText.className = 'visually-hidden';
    fullText.textContent = full;

    el.textContent = '';
    el.appendChild(visible);
    el.appendChild(caret);
    el.appendChild(fullText);
    el.classList.add('is-typed');

    var i = 0;
    (function step() {
      i += 1;
      visible.textContent = full.slice(0, i);
      if (i < full.length) {
        setTimeout(step, TYPE_SPEED_MS);
      } else {
        caret.remove();
      }
    })();
  }

  function reveal(el) {
    el.classList.add('is-revealed');
  }

  function init() {
    var tracks = document.querySelectorAll(TRACK);
    if (!tracks.length) return;

    var revealTargets = [];
    var typeTargets = [];
    tracks.forEach(function (track) {
      revealTargets = revealTargets.concat([].slice.call(track.querySelectorAll('[data-cf-reveal], [data-cf-reveal-item]')));
      typeTargets = typeTargets.concat([].slice.call(track.querySelectorAll('[data-cf-type]')));
    });

    if (!('IntersectionObserver' in window)) {
      revealTargets.forEach(reveal);
      typeTargets.forEach(typeOnce);
      return;
    }

    var revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          reveal(entry.target);
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.2, rootMargin: '0px 0px -10% 0px' });

    var typeObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          typeOnce(entry.target);
          typeObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.4 });

    revealTargets.forEach(function (el) { revealObserver.observe(el); });
    typeTargets.forEach(function (el) { typeObserver.observe(el); });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

/* ---- CFV2: autoplaying values list (replaces the old pinned .cf-values__track) ----
   Normal flow, no scroll-hijack. Starts once the section enters the
   viewport, cycles through all six rows on a timer, highlights the active
   one, and fills a timer bar under it that resets on each switch. Clicking
   a row jumps there directly and resets the cycle from that row. */
(function () {
  'use strict';

  // Mode: Set to true to scroll to load progress bar and advance; set to false to keep timer
  var SCROLL_TO_PLAY = false;
  var DURATION = 2600; // ms per value when SCROLL_TO_PLAY is false

  function initValues(root) {
    var items = [].slice.call(root.querySelectorAll('.cfv2-item'));
    if (!items.length) return;

    var art = root.querySelector('.cfv2-art');
    var descs = [].slice.call(root.querySelectorAll('.cfv2-desc'));
    var current = 0;
    var timerId = null;
    var playing = false;

    // Check attribute first if explicitly provided, otherwise fall back to SCROLL_TO_PLAY
    var isScrollMode = SCROLL_TO_PLAY;
    if (root.hasAttribute('data-scroll-to-play')) {
      isScrollMode = root.getAttribute('data-scroll-to-play') === 'true';
    }

    if (isScrollMode) {
      root.setAttribute('data-scroll-to-play', 'true');
    } else {
      root.removeAttribute('data-scroll-to-play');
    }

    function setStage(i) {
      current = i;
      items.forEach(function (el, idx) {
        el.classList.toggle('is-active', idx === i);
      });

      descs.forEach(function (d, idx) {
        d.classList.toggle('is-active', idx === i);
      });

      if (art) {
        for (var s = 0; s < items.length; s++) {
          art.classList.remove('cfv2-step-' + s);
        }
        art.classList.add('cfv2-step-' + i);

        var layers = [].slice.call(art.querySelectorAll('.cf-values__grid-layer'));
        var drawnThrough = i - 1;
        layers.forEach(function (g) {
          var style = g.getAttribute('style') || '';
          var m = style.match(/--layer:\s*(\d+)/);
          var idx = m ? parseInt(m[1], 10) : -1;
          g.classList.remove('cfv2-drawn', 'cfv2-drawing');
          if (idx < drawnThrough) {
            g.classList.add('cfv2-drawn');
          } else if (idx === drawnThrough) {
            g.classList.add('cfv2-drawing');
          }
        });
      }
    }

    // -------------------------------------------------------------
    // MODE: SCROLL TO PLAY (scroll loads progress bar & advances)
    // -------------------------------------------------------------
    if (isScrollMode) {
      setStage(0);

      var ticking = false;
      function onScroll() {
        if (!ticking) {
          requestAnimationFrame(function () {
            updateScroll();
            ticking = false;
          });
          ticking = true;
        }
      }

      function updateScroll() {
        var rect = root.getBoundingClientRect();
        var scrollHeight = root.offsetHeight - window.innerHeight;
        if (scrollHeight <= 0) return;

        var scrolled = -rect.top;
        var progress = Math.max(0, Math.min(1, scrolled / scrollHeight));

        var totalStages = items.length;
        var scaled = progress * totalStages;
        var activeIdx = Math.min(totalStages - 1, Math.floor(scaled));
        var innerP = (scaled - activeIdx) * 100;

        setStage(activeIdx);

        // Directly drive progress bar for the active item with scroll position
        items.forEach(function (el, idx) {
          var bar = el.querySelector('.cfv2-timer-bar');
          if (!bar) return;
          bar.classList.remove('is-animating');
          bar.style.transition = 'none';
          if (idx === activeIdx) {
            bar.style.width = innerP.toFixed(1) + '%';
          } else {
            bar.style.width = '0%';
          }
        });

      }

      window.addEventListener('scroll', onScroll, { passive: true });
      window.addEventListener('resize', onScroll, { passive: true });
      updateScroll();

      // Clicking any item smooth-scrolls to its position in the track
      items.forEach(function (el, idx) {
        el.addEventListener('click', function () {
          var scrollHeight = root.offsetHeight - window.innerHeight;
          var rootTop = window.pageYOffset + root.getBoundingClientRect().top;
          var targetY = rootTop + ((idx + 0.05) / items.length) * scrollHeight;
          window.scrollTo({ top: targetY, behavior: 'smooth' });
        });
      });

      return;
    }

    setStage(0);

    // -------------------------------------------------------------
    // MODE: TIMER AUTOPLAY
    // -------------------------------------------------------------
    function activate(i) {
      setStage(i);
      items.forEach(function (el, idx) {
        var isActive = idx === i;
        var bar = el.querySelector('.cfv2-timer-bar');
        if (!bar) return;
        bar.classList.remove('is-animating');
        bar.style.transitionDuration = '0s';
        bar.style.width = isActive ? '0%' : '0%';
        if (isActive) {
          void bar.offsetWidth; // restart transition
          bar.classList.add('is-animating');
          bar.style.transitionDuration = DURATION + 'ms';
          requestAnimationFrame(function () {
            bar.style.width = '100%';
          });
        }
      });
    }

    function advance() {
      activate((current + 1) % items.length);
      clearTimeout(timerId);
      timerId = setTimeout(advance, DURATION);
    }

    function start() {
      if (playing) return;
      playing = true;
      activate(0);
      timerId = setTimeout(advance, DURATION);
    }

    items.forEach(function (el, idx) {
      el.addEventListener('click', function () {
        clearTimeout(timerId);
        activate(idx);
        timerId = setTimeout(advance, DURATION);
      });
    });

    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      activate(0);
      return;
    }

    if (!('IntersectionObserver' in window)) {
      start();
      return;
    }

    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          start();
          obs.disconnect();
        }
      });
    }, { threshold: 0.3 });
    obs.observe(root);

  }

  function init() {
    [].slice.call(document.querySelectorAll('.cfv2')).forEach(initValues);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

/* ---- Footer Isometric Exploded Layers (matches Home Page) ---- */
(function () {
  'use strict';

  function initFooterLayers() {
    var footerEl = document.querySelector('.cf-footer--v2');
    var topLayer = footerEl ? footerEl.querySelector('.cf-footer-layer--top') : null;
    var midLayer = footerEl ? footerEl.querySelector('.cf-footer-layer--mid') : null;
    var botLayer = footerEl ? footerEl.querySelector('.cf-footer-layer--bot') : null;

    if (!footerEl || !topLayer || !botLayer) return;

    var currentSpread = 0;
    var targetSpread = 0;

    function updateFooterLayers() {
      var rect = footerEl.getBoundingClientRect();
      var windowHeight = window.innerHeight;

      if (rect.top < windowHeight && rect.bottom > 0) {
        var currentDistance = windowHeight - rect.top;
        var totalDistance = windowHeight + rect.height * 0.45;
        var progress = Math.max(0, Math.min(1, currentDistance / totalDistance));
        targetSpread = progress * 38;
      } else {
        targetSpread = 0;
      }

      currentSpread += (targetSpread - currentSpread) * 0.12;

      topLayer.style.transform = 'translate3d(0, ' + (-currentSpread).toFixed(2) + 'px, 0)';
      if (midLayer) {
        midLayer.style.transform = 'translate3d(0, 0, 0)';
      }
      botLayer.style.transform = 'translate3d(0, ' + currentSpread.toFixed(2) + 'px, 0)';

      requestAnimationFrame(updateFooterLayers);
    }

    requestAnimationFrame(updateFooterLayers);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFooterLayers);
  } else {
    initFooterLayers();
  }
})();

