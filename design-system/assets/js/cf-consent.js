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

  document.addEventListener('DOMContentLoaded', function () {
    var banner = document.querySelector('[data-cf-consent-banner]');
    var dialog = document.querySelector('[data-cf-consent-dialog]');
    if (!banner) return;

    var boxes = dialog
      ? dialog.querySelectorAll('[data-cf-consent-category]')
      : [];
    var opener = null;   /* what to give focus back to when the dialog closes */

    function showBanner() {
      banner.dataset.enter = 'true';
      banner.hidden = false;
      /* Two frames: one for the browser to lay the banner out in its entry
         state, one for the transition to have something to run from. */
      requestAnimationFrame(function () {
        requestAnimationFrame(function () { delete banner.dataset.enter; });
      });
      /* The banner sits immediately after the skip link, so it is already first
         in reading and tab order. Focus moves to its heading too, because a visitor who
         has begun reading further down would otherwise never meet the thing
         asking them a question. The heading is the target rather than the
         accept button, so nothing is pre-selected. */
      var title = banner.querySelector('[data-cf-consent-title]');
      if (title) title.focus();
    }

    /* Matches --duration-base, and its reduced-motion override, so the banner
       is not left sitting in a transition nobody asked to watch. */
    function exitDuration() {
      return window.matchMedia &&
             window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 240;
    }

    function hideBanner() {
      if (banner.hidden) return;
      banner.dataset.enter = 'true';
      window.setTimeout(function () { banner.hidden = true; }, exitDuration());
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
  });
})();
