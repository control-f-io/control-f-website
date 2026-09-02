/* Control-F — the continuous object.
   OPTIONAL. Every page this touches navigates correctly without it. The rake
   in base.css is the page transition and stays the page transition; all this
   file does is lift ONE object out of the wipe and let it travel — the
   headline you clicked in a register becoming the headline of the page it
   opened, instead of being cut away with the rest of the sheet and redrawn
   somewhere else.

   THIS IS THE MOVE foundations/transitions.html HAD PARKED, AND IT PARKED IT
   ON A BUDGET THAT HAD ALREADY BEEN SPENT. The chapter's argument was "the
   system currently ships two [scripts], one of which is legally required and
   one of which is optional and additive, and that ratio is worth protecting."
   The ratio was two-to-eight by the time it was read: every pattern page loads
   cf-nav.js, cf-consent.js and cf-sight.js, and the landing page loads eight.
   What survives of the argument is the SHAPE it asked for — "one small file
   that refuses to run unless the pair actually matches" — and that is the
   whole design below.

   WHAT A PAIR IS. Two elements, in two documents, that are the same object:
   the title of a cell in a register, and the title of the page that cell
   opens. ONE ELEMENT EACH, AND THAT IS THE WHOLE FEATURE. A card's picture is
   the object's illustration and does not travel; its meta line is not the same
   drawing on the two sides — the cell writes author, date and length as one
   run, the page header writes a kind and a date at one end of a row and the
   reading time at the other — and a pair that is not the same drawing morphs
   as two strangers passing. Built with the meta line in, the reading time flew
   across half the viewport and read as a stray label over the outgoing page.
   The name is what carries identity. Nothing else does, so nothing else goes.

   HOW EACH SIDE KNOWS, WITHOUT EITHER SEEING THE OTHER. Both sides answer the
   same question from their own DOM, and neither is allowed to guess:

     leaving   pageswap knows the address being navigated to. This page must be
               a REGISTER — a page with no breadcrumb of its own — because an
               object cannot hand over another object: an article's tail draws
               cells for its neighbours, and a headline that flew out of one of
               those would be leaving a page that is not their home and
               arriving at one that will not answer. Then, if EXACTLY ONE
               registered cell here resolves to that address, that cell is the
               object. Two would mean the page draws the same object twice and
               there is no "the" cell; none means the reader clicked something
               else entirely.

     arriving  pagereveal knows the address navigated FROM. The last link in
               this page's breadcrumb is where this object lives — that is what
               a breadcrumb IS — so the object came out of a register only if
               the page it came from is that link. Anything else is a reader
               arriving sideways, and an object cannot be continuous with a
               page that was not showing it.

   THE BREADCRUMB IS THE ONLY STRUCTURE THAT CAN CARRY THIS, and that is a
   finding rather than a preference. The obvious rule — "the article's address
   sits under the register's address" — holds in design-system/patterns/, where
   news.html sits beside beitrag-….html, and is false on the site that ships,
   where the register is /news.html and the object is /blog/….html. A rule read
   off addresses would have passed every check in this directory and done
   nothing in production. The breadcrumb is drawn from the same hierarchy in
   both trees and in both languages.

   A FILTERED VIEW IS NOT A LEVEL, so a topic page hands nothing over and does
   not load this file. It draws the same cells as the register and is NOT the
   object's home, which is exactly the argument blog-artikel.html already makes
   over its own breadcrumb: "eine gefilterte Ansicht der Liste, keine Ebene
   darüber". Handing over from there would name a headline on the way out that
   nothing answers on the way in — one half of a morph is worse than none,
   because a lifted element is lifted out of the wipe as well. The comparison
   is origin + path, which means a future server-rendered ?thema=… or ?seite=2
   ON THE REGISTER ITSELF does morph: those are the register, with a filter on
   it, at the register's own address.

   WHAT IT WRITES, AND NOTHING ELSE: view-transition-name, on ONE element, for
   the length of one navigation, cleared when the transition finishes. No
   markup, no attributes, no storage, no cookie, no network. Delete the tag and
   every page renders and navigates exactly as it did before the file existed.

   EVERY WAY OUT is the table in foundations/transitions.html. The short of it:
   no view transition means no `e.viewTransition`, and both handlers return on
   the first line — which covers prefers-reduced-motion (base.css only opts in
   under no-preference), a browser without cross-document view transitions, and
   a transition the browser abandoned. scripts/check-morph-pairs.py holds the
   register below to the markup, in both directions.
   → foundations/transitions.html#continuous */

(function () {
  'use strict';

  /* The register. One entry per SHAPE a cell is drawn in, not one per page —
     the blog card is the same drawing on the archive and on a topic page, and
     the vacancy is the same drawing on Karriere and in a filtered register
     that does not exist yet. `scope` is the element that holds the title when
     the link is not itself that element; null means the link is the cell. */
  var SOURCES = [
    { link: 'a.cf-blog-card', scope: null, title: '.cf-blog-card__title' },
    { link: 'a.cf-vacancy__link', scope: '.cf-vacancy', title: '.cf-vacancy__title' }
  ];

  /* The destination is ONE shape for the whole system, and that is the reason
     this works at all: every page in it that is an object rather than a
     section is drawn with the same page header — a title, a hairline, a mono
     line. → components/page-header.html */
  var TARGET = { title: '.cf-page-header__title' };
  var HOME   = '.cf-breadcrumb__link';

  /* One name. The transitions chapter notes `view-transition-class` as
     unclaimed, "worth remembering when there is a fourth" name — this is the
     fourth and it still does not claim it, because a class is how a FAMILY
     says one thing once and this is one name with one behaviour. The note
     stands. */
  var NAME_TITLE = 'cf-morph-title';

  function key(url) {
    var u;
    try { u = new URL(url, document.baseURI); } catch (e) { return null; }
    if (u.origin !== location.origin) return null;
    return u.origin + u.pathname;
  }

  function name(el, n) {
    if (el) el.style.viewTransitionName = n;
  }

  function release(el) {
    if (el) el.style.viewTransitionName = '';
  }

  /* The cell on THIS page that opens `to`, or null if there is not exactly
     one of them. A cell with no title is not a cell. */
  function cell(to) {
    var found = null, hits = 0;
    for (var s = 0; s < SOURCES.length; s++) {
      var shape = SOURCES[s];
      var links = document.querySelectorAll(shape.link);
      for (var i = 0; i < links.length; i++) {
        if (key(links[i].href) !== to) continue;
        hits++;
        var scope = shape.scope ? links[i].closest(shape.scope) : links[i];
        if (!scope) continue;
        var title = scope.matches(shape.title) ? scope : scope.querySelector(shape.title);
        if (!title) continue;
        found = title;
      }
    }
    return hits === 1 ? found : null;
  }

  /* Where this page says its object lives: the last link in the breadcrumb.
     A page with no breadcrumb, or one whose only link is Home, is a section
     rather than an object and never answers. */
  function home() {
    var links = document.querySelectorAll(HOME);
    if (links.length < 2) return null;
    return key(links[links.length - 1].href);
  }

  /* Where the reader came from. The Navigation API is the exact answer and is
     present wherever cross-document view transitions are; the referrer is the
     same fact one remove away, and is sent in full for a same-origin
     navigation under every referrer policy this site can be served with. */
  function from() {
    var nav = window.navigation;
    if (nav && nav.activation && nav.activation.from) return key(nav.activation.from.url);
    return document.referrer ? key(document.referrer) : null;
  }

  window.addEventListener('pageswap', function (e) {
    if (!e.viewTransition) return;
    if (document.querySelector(HOME)) return;   /* an object, not a register */
    var to = e.activation && e.activation.entry ? key(e.activation.entry.url) : null;
    if (!to || to === key(location.href)) return;
    var title = cell(to);
    if (!title) return;
    name(title, NAME_TITLE);
    /* The outgoing document is normally discarded, but it is not always —
       bfcache hands it back on a Back, and a name left behind would be a
       duplicate the next time this page is the one arriving. */
    e.viewTransition.finished.then(function () { release(title); });
  });

  window.addEventListener('pagereveal', function (e) {
    if (!e.viewTransition) return;
    var lives = home();
    if (!lives) return;
    var came = from();
    if (!came || came !== lives || came === key(location.href)) return;
    var title = document.querySelector(TARGET.title);
    if (!title) return;
    name(title, NAME_TITLE);
    e.viewTransition.finished.then(function () { release(title); });
  });
})();
