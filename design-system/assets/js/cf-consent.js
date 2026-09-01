/* Control-F — consent.
   One of the two pieces of JavaScript the system requires — cf-nav.js is the
   other. No dependencies, no build step, no network calls, ~5 kB unminified.

   It does not create any markup. The banner and the settings dialog live in
   the page as ordinary HTML with `hidden` on them, and this file only decides
   when they are shown and what the decision means. That ordering matters:
   with JavaScript switched off the banner never appears and no non-essential
   script is ever activated, which is the compliant outcome rather than a
   degraded one.

   Contract with the page:

     [data-cf-consent-banner]              the first-layer banner
     [data-cf-consent-dialog]              the settings <dialog>
     [data-cf-consent-action="accept"]     grant every category
     [data-cf-consent-action="reject"]     grant nothing beyond necessary
     [data-cf-consent-action="save"]       grant what the checkboxes say
     [data-cf-consent-action="open"]       open the settings dialog
     [data-cf-consent-action="close"]      close it without deciding
     [data-cf-consent-category="statistik"] a checkbox, one per category

   `[data-cf-consent-action="open"]` works anywhere on the page, which is how
   withdrawal is offered: a "Cookie-Einstellungen" link in the footer reopens
   the dialog with the stored answers filled in. Art. 7(3) DSGVO requires
   withdrawing to be as easy as consenting, so it is the same control.

   Gating a script on a category:

     <script type="text/plain" data-cf-consent="statistik" src="…"></script>

   Nothing loads until the category is granted; on grant the tag is rewritten
   as a real <script> and runs. Revoking does not unload what already ran —
   only a reload can do that, so revoking reloads the page.

   The page also gets a `cf:consent` CustomEvent on every decision, with the
   granted categories in `event.detail`, for anything that needs to react
   without being a script tag.
*/

(function () {
  'use strict';

  /* Bump when the categories or their meaning change: an old record is then
     treated as no record and the visitor is asked again, which is what a
     changed purpose requires. */
  var KEY = 'cf-consent';
  var VERSION = 1;

  /* "notwendig" is deliberately not in here. It is not a choice, so it is
     never stored, never unchecked and never asked about. */
  var CATEGORIES = ['statistik', 'marketing'];

  function read() {
    var raw;
    try { raw = window.localStorage.getItem(KEY); } catch (e) { return null; }
    if (!raw) return null;
    var record;
    try { record = JSON.parse(raw); } catch (e) { return null; }
    if (!record || record.v !== VERSION || !record.categories) return null;
    return record;
  }

  function write(granted) {
    var record = { v: VERSION, ts: new Date().toISOString(), categories: {} };
    CATEGORIES.forEach(function (name) {
      record.categories[name] = granted.indexOf(name) > -1;
    });
    try { window.localStorage.setItem(KEY, JSON.stringify(record)); } catch (e) { /* private mode */ }
    return record;
  }

  function grantedFrom(record) {
    if (!record) return [];
    return CATEGORIES.filter(function (name) { return record.categories[name] === true; });
  }

  /* Turn <script type="text/plain" data-cf-consent="x"> into a live script.
     Attributes are copied across so src, async, defer and type all survive. */
  function activate(granted) {
    var pending = document.querySelectorAll('script[type="text/plain"][data-cf-consent]');
    Array.prototype.forEach.call(pending, function (tag) {
      if (granted.indexOf(tag.dataset.cfConsent) === -1) return;
      var live = document.createElement('script');
      Array.prototype.forEach.call(tag.attributes, function (attr) {
        if (attr.name === 'type' || attr.name === 'data-cf-consent') return;
        live.setAttribute(attr.name, attr.value);
      });
      live.text = tag.text;
      tag.parentNode.replaceChild(live, tag);
    });
  }

  function announce(granted) {
    document.documentElement.dataset.cfConsent = granted.join(' ');
    document.dispatchEvent(new CustomEvent('cf:consent', {
      detail: { granted: granted, categories: CATEGORIES }
    }));
  }

  /* WHEN THIS RUNS IS A LAYOUT FACT, NOT A LIFECYCLE PREFERENCE, and the
     reason is publishHeight() below. This file measures the banner and writes
     --cf-consent-height, and components.css spends that number on
     `.cf-hero { min-height: min(92vh, 56rem, calc(100vh - …)) }`. The hero is
     the first screen. So the property is an input to the FIRST PAINT, and a
     script that waits for DOMContentLoaded publishes it one frame too late:
     the browser paints the hero at 92vh, this file then measures the banner,
     and the hero collapses onto the banner's top edge with the whole document
     following it up.

     Measured on patterns/landing-page.html, first visit, nothing stored —
     cumulative layout shift, and the hero's height across the shift:

       viewport      FCP      shift at    CLS       hero px
       375 x 812     192 ms   194 ms      0.32341   747 -> 501
       768 x 1024    192 ms   202 ms      0.09053   896 -> 791
       1280 x 900    224 ms   227 ms      0.03016   828 -> 756
       1440 x 900    240 ms   235 ms      0.02675   828 -> 756

     0.32341 is over twice the 0.25 that counts as a poor score, on a phone, on
     the one visit every new reader has: the hero paints, and 2 ms later 246 px
     of it is gone. On a return visit, with a decision stored, the banner never
     shows and every one of those numbers is 0.000 — which is why the fault
     survived: it is absent from the second load onward, and from every load
     anybody reviewing the page has after the first.

     THE FIX IS WHERE THE SCRIPT TAG SITS, and this function is what lets the
     tag move. The banner and the settings dialog are the first two elements in
     the body, so a <script> placed directly after them runs while the parser
     is still above the hero: boot() shows the banner, measures it, and writes
     the property before the hero has a box at all. Same measurements after the
     move: 0.000 / 0.011 / 0.000 / 0.000. Nothing about the banner's behaviour
     changes — it is the same show, the same measurement, the same observer,
     one parse position earlier.

     It is the argument cf-nav.js's own header makes for sitting in the head:
     a script that writes something the first paint depends on has to run
     before that paint, and where it runs is the only lever.

     BOTH ENTRY POINTS STAY, because only one page has the tag in the new
     position today. Where the banner is already parsed, boot() runs now; where
     the tag is still at the end of the body — the other fourteen pages, whose
     only consumer is the footer's bottom padding, which moves nothing because
     nothing follows it — the banner is not there yet and DOMContentLoaded is
     the entry point exactly as before. → scripts/check-consent-paint-order.py */
  function boot() {
    var banner = document.querySelector('[data-cf-consent-banner]');
    var dialog = document.querySelector('[data-cf-consent-dialog]');
    if (!banner) return;

    var boxes = dialog
      ? dialog.querySelectorAll('[data-cf-consent-category]')
      : [];
    var opener = null;   /* what to give focus back to when the dialog closes */

    /* THE BANNER PUBLISHES ITS OWN HEIGHT, because something on the page has
       to reserve it and nothing could. The banner is `position: fixed` at the
       viewport's bottom edge; the landing page's hero is `min(92vh, 56rem)`
       tall and hangs its kicker and its one call to action off its OWN bottom
       edge. 92vh + the banner's height exceeds the viewport at every height
       under about 1800 px, so on a first visit — the only visit the banner is
       shown on — the banner lands on the hero's bottom row.

       Measured before this line existed, first load, nothing dismissed:

         viewport      banner h   CTA buried   kicker buried   hit test at the CTA's centre
         375 x 812        333.5      48 / 48      48.8 / 48.9   the banner's "Nur notwendige"
         768 x 1024       232.9      48 / 48         —          the banner's own heading
         1024 x 768       144.4    34.9 / 48      32.9 / 32.9   the banner's plate
         1280 x 900       144.4    24.4 / 48      24.4 / 32.9   the banner's plate
         1440 x 900       144.4    24.4 / 48      24.4 / 32.9   the banner's plate
         1920 x 1080      144.4         —            —          the button itself

       Five of the six sizes, and the two narrowest bury the control whole. It
       is not only a paint fault: elementFromPoint at the middle of
       "Kennenlernen" returns the BANNER on five of six, so the page's primary
       call to action is a dead target for as long as the notice is up.

       The height cannot be a constant. It is 144.4, 232.9 and 333.5 px at the
       three breakpoints the copy wraps at, and it moves again with a reader's
       type size or a translation — which is the kind of hand-computed number
       this repository keeps finding in its own history. So it is measured, by
       the one script that already owns the banner's lifecycle, and read back
       in CSS as --cf-consent-height. Unset, `var(--cf-consent-height, 0px)`
       resolves to 0 and every consumer is exactly what it was: the property
       exists only while the banner does. → components.css, .cf-hero;
       scripts/check-consent-clearance.py */
    function publishHeight() {
      var root = document.documentElement;
      if (banner.hidden) { root.style.removeProperty('--cf-consent-height'); return; }
      root.style.setProperty('--cf-consent-height', banner.offsetHeight + 'px');
    }
    /* Observed rather than measured once: the plate re-wraps on rotation and on
       a zoom change, and a height taken at DOMContentLoaded would go stale
       there. Where there is no ResizeObserver the one-shot calls below still
       run, so the fix degrades to the first measurement instead of to nothing. */
    if (window.ResizeObserver) new window.ResizeObserver(publishHeight).observe(banner);

    function showBanner() {
      banner.dataset.enter = 'true';
      banner.hidden = false;
      publishHeight();
      /* Two frames: one for the browser to lay the banner out in its entry
         state, one for the transition to have something to run from. */
      requestAnimationFrame(function () {
        requestAnimationFrame(function () { delete banner.dataset.enter; });
      });
      /* NO FOCUS MOVE, and the sentence that used to be here says why it was
         never needed. It read: "The banner sits immediately after the skip
         link, so it is already first in reading and tab order" — and then
         moved focus to the heading anyway. Both halves cannot be true. If the
         banner is already the second stop, the focus move buys one Tab press;
         what it costs is the first stop, because the skip link is BEFORE the
         banner in the document and every forward Tab from inside the banner
         goes further down the page, never back to it.

         Measured on the landing page, first visit, banner shown: the skip
         link was 47 Tab presses away at 375 px and 52 at 1280 — the whole
         page, chrome and all — against 1 press on a return visit with the
         decision stored. It is one Shift+Tab backwards, which is not how
         anybody looks for a skip link. A bypass block reachable only after
         the thing it exists to bypass is not a bypass block.

         The reason the old comment gave for moving focus — "a visitor who has
         begun reading further down would otherwise never meet the thing asking
         them a question" — does not describe this moment. This runs at
         DOMContentLoaded on a fresh navigation, where focus is at the start of
         the document and nobody has begun reading anything; and the banner is
         a fixed layer, so it is on screen at whatever scroll position a
         restored page opens at. It is met either way, and it is announced
         either way: it is role="dialog", non-modal, and second in the
         document, so a screen reader arrives at it immediately after the skip
         link rather than instead of it.

         The settings dialog is the other half of this and keeps its focus
         handling exactly: it is opened BY the reader, it is a real
         <dialog>.showModal(), and openDialog/the close listener below still
         move focus in and hand it back to whatever opened it. */
    }

    /* Matches --duration-base, and its reduced-motion override, so the banner
       is not left sitting in a transition nobody asked to watch. */
    function exitDuration() {
      return window.matchMedia &&
             window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 240;
    }

    /* AND THE BANNER HANDS THE SKIP LINK BACK, which is the other half of
       showBanner's argument and the half that was never written.

       showBanner does not move focus in, so that the skip link keeps the first
       stop; the reasoning is in its own comment and it is right. But a reader
       who ANSWERS the banner is standing on a button that is about to be
       `hidden`, and a focused element that disappears drops focus to <body>.
       Chrome then leaves the sequential starting point where that button was —
       AFTER the skip link — so every forward Tab goes down the page and the
       skip link is reachable only by wrapping the whole document.

       Measured on this page, banner answered from the keyboard, counting Tab
       presses forward until .skip-link takes focus:

         375 x 900     18 presses
         1280 x 900    29 presses

       against 1 press on the return visit with the decision already stored.
       That is the same fault showBanner's comment names — "a bypass block
       reachable only after the thing it exists to bypass is not a bypass
       block" — arriving through the other door, and it is the door every
       first-time reader uses, because answering the banner is the only way
       past it.

       So: if the banner holds focus as it leaves, the skip link takes it. That
       is the stop immediately before the banner in the document, so the reader
       lands exactly where showBanner's reasoning says they should be, and the
       next Tab is the nav.

       :focus-visible AND NOT :focus, because this fires for the mouse too and
       .skip-link paints on :focus — a pointer reader clicking "Alle
       akzeptieren" would watch a black chip slide in at the top left for no
       reason they could name. :focus-visible is the browser's own answer to
       "should this focus be shown", so it is the browser's answer to "is there
       a keyboard reader here to hand the link to". Where it is not supported
       the match throws and nothing moves, which is the behaviour that shipped
       before this block.

       The test is made just before the element goes, not when hideBanner was
       called: the exit runs for --duration-base and a reader can Tab out of the
       banner inside it. Focus that has already left is focus this must not
       take back.

       decide() closes the settings dialog before it calls this, and the
       dialog's own close listener has by then handed focus to whatever opened
       it. Opened from the footer, that button is outside the banner and this
       leaves it alone; opened from the banner's own "Einstellungen", it is
       inside the banner and about to be hidden too, so the skip link is right
       there as well. → assets/css/base.css, .skip-link;
       scripts/check-focus-reach.py */
    function hideBanner() {
      if (banner.hidden) return;
      banner.dataset.enter = 'true';
      window.setTimeout(function () {
        var held = false;
        try {
          held = !!document.activeElement &&
                 banner.contains(document.activeElement) &&
                 document.activeElement.matches(':focus-visible');
        } catch (e) { held = false; }
        banner.hidden = true;
        publishHeight();
        if (held) {
          var skip = document.querySelector('.skip-link');
          if (skip) skip.focus();
        }
      }, exitDuration());
    }

    function decide(granted, opts) {
      var previous = grantedFrom(read());
      write(granted);
      /* Anything already granted and running cannot be taken back out of the
         page by script. If this decision removes a category, reload. */
      var revoked = previous.some(function (name) { return granted.indexOf(name) === -1; });
      announce(granted);
      activate(granted);
      if (dialog && dialog.open) dialog.close();
      hideBanner();
      if (revoked && !(opts && opts.silent)) window.location.reload();
    }

    function syncBoxes() {
      var granted = grantedFrom(read());
      Array.prototype.forEach.call(boxes, function (box) {
        box.checked = granted.indexOf(box.dataset.cfConsentCategory) > -1;
      });
    }

    /* The dialog's own name, resolved the way an assistive technology resolves
       it: through aria-labelledby, which every page carrying this dialog
       already sets. So there is no new contract and no markup to add — the
       element that names the dialog is the element focus lands on. */
    function dialogTitle() {
      if (!dialog) return null;
      var id = dialog.getAttribute('aria-labelledby');
      return id ? document.getElementById(id) : null;
    }

    function openDialog(trigger) {
      if (!dialog) return;
      opener = trigger || null;
      syncBoxes();
      if (typeof dialog.showModal === 'function') {
        /* showModal brings the focus trap, the inert background, Escape and
           the ::backdrop with it — all of it native, none of it reimplemented
           here. That is the whole reason the second layer is a <dialog>. */
        if (!dialog.open) dialog.showModal();
      } else {
        dialog.setAttribute('open', '');
      }
      /* AND THEN THE HEADING: nothing is pre-selected, and the reader meets
         the question before the answers. showModal's own rule is the first
         tabbable descendant, and in this dialog that is the "Alle Einträge im
         Detail" link in the explanation — so opening the settings put a
         keyboard or screen-reader user PAST the dialog's name and past the
         sentence saying what it decides, on a link that leaves the page.
         Measured: on open, document.activeElement was
         a[href="datenschutz.html#cookies"], and Enter — the key that had just
         opened the dialog — navigated away from the decision.

         THIS LAYER AND NOT THE BANNER, and the difference is the whole rule.
         This comment used to say the banner did the same thing for the same
         reason; showBanner no longer focuses anything, and the reason is in
         its own comment. A modal is opened BY the reader, so moving focus into
         it is the APG pattern and the only way Escape and the trap have
         anything to act on. The banner appears unbidden at DOMContentLoaded,
         where the same move costs the stop in front of it — the skip link,
         which sits earlier in the document and was 47 Tab presses away once
         focus landed past it. Opened by the reader: move focus. Arriving on
         its own: do not.

         tabindex is set here rather than in the markup so no page has to be
         edited to gain it, and -1 keeps the heading out of the tab sequence it
         is now the head of. */
      var title = dialogTitle();
      if (title) {
        if (!title.hasAttribute('tabindex')) title.setAttribute('tabindex', '-1');
        title.focus();
      }
    }

    /* Restore focus to whatever opened the dialog, per the APG dialog pattern.
       `close` fires for the button and for Escape alike, so this covers both. */
    if (dialog) {
      dialog.addEventListener('close', function () {
        if (opener && document.contains(opener)) opener.focus();
        opener = null;
      });
    }

    document.addEventListener('click', function (event) {
      var target = event.target.closest ? event.target.closest('[data-cf-consent-action]') : null;
      if (!target) return;
      var action = target.dataset.cfConsentAction;

      if (action === 'open') {
        event.preventDefault();
        openDialog(target);
      } else if (action === 'close') {
        if (dialog) dialog.close();
      } else if (action === 'accept') {
        decide(CATEGORIES.slice());
      } else if (action === 'reject') {
        decide([]);
      } else if (action === 'save') {
        decide(Array.prototype.filter.call(boxes, function (box) {
          return box.checked;
        }).map(function (box) {
          return box.dataset.cfConsentCategory;
        }));
      }
    });

    var stored = read();
    if (stored) {
      var granted = grantedFrom(stored);
      announce(granted);
      activate(granted);
    } else {
      announce([]);
      showBanner();
    }

    /* AND ONE THING HAS TO HAPPEN TWICE WHEN boot() RUNS EARLY. activate()
       rewrites every <script type="text/plain" data-cf-consent> the document
       holds, and run from the top of the body it can only see the ones parsed
       so far — which is none of them, since a gated tag sits with the thing it
       gates. So the sweep is repeated once the document is complete. It is
       idempotent by construction: a tag it activates stops matching the
       selector, so the second pass finds only what the first could not yet
       see, and on the pages where boot() still runs at DOMContentLoaded the
       document is already complete and the second pass finds nothing. */
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', function () {
        activate(grantedFrom(read()));
      });
    }
  }

  /* Parsed already means the tag sits after the banner — run now, before the
     hero has a box. Not parsed means the tag is at the end of the body, where
     DOMContentLoaded is the earliest this can run at all. */
  if (document.querySelector('[data-cf-consent-banner]')) boot();
  else document.addEventListener('DOMContentLoaded', boot);
})();
