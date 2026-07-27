/* Control-F — navigation.
   The disclosure behind the phone layout's menu button. Ships. No
   dependencies, no build step, ~2 kB unminified.

   Like cf-consent.js it creates no markup of its own: the bar, the button and
   the panel are ordinary HTML in the page, and this file only decides when the
   panel is shown and keeps the announced state and the drawn one identical.

   Contract with the page:

     .cf-nav                the bar
     .cf-nav__toggle        the disclosure button, inside the bar, carrying
                            aria-controls and aria-expanded
     .cf-nav__list          the panel, with the id aria-controls names

   What it writes, and nothing else:

     data-cf-nav="ready"    on <html>, the moment the file runs
     aria-expanded          on the button
     data-open              on the panel — what components.css draws from

   THE TAG GOES IN THE <head>, NOT AT THE END OF THE BODY, and the placement is
   the load-bearing part of this file rather than a habit. Below 780 px the
   stylesheet only folds the links into a panel and only renders the button
   when <html> carries data-cf-nav — so with scripting off the five links are
   an ordinary stacked list and the control that would do nothing is not drawn
   at all. That fallback is worth having, and it is only free if the attribute
   is there before the first paint: written any later, every load below 780 px
   would show the open list and then collapse it, and the panel would spend
   that window in the layout with its links focusable. A script element in the
   head runs before the body exists, which is the whole of the trick.

   The panel is a DISCLOSURE, not a dialog. It does not trap focus, it does not
   make the page inert, and it does not lock scrolling: the button and the links
   sit in the normal tab order and Tab walks straight out of the open panel into
   the page, which is what the WAI-ARIA Authoring Practices disclosure
   navigation pattern does and what a menu role would take away.
*/

(function () {
  'use strict';

  /* Before anything else and before the body is parsed — see the header. */
  document.documentElement.setAttribute('data-cf-nav', 'ready');

  function parts(nav) {
    var toggle = nav.querySelector('.cf-nav__toggle');
    if (!toggle) return null;
    var panel = document.getElementById(toggle.getAttribute('aria-controls') || '');
    return panel ? { nav: nav, toggle: toggle, panel: panel } : null;
  }

  function isOpen(p) { return p.panel.getAttribute('data-open') === 'true'; }

  /* One writer for both attributes. They described the same fact and were set
     in two places on seven pages, which is how a drawn state and an announced
     one drift apart in the first place. */
  function set(p, open) {
    p.panel.setAttribute('data-open', String(open));
    p.toggle.setAttribute('aria-expanded', String(open));
  }

  /* Is the bar in its folded form? The threshold is 780 px, and that figure is
     deliberately not repeated here. tokens.css keeps the register of every
     threshold in the shipping CSS and states that the register is only worth
     having if it is complete; a copy in a script is one the register cannot
     see. The question this file actually has is not how wide the viewport is
     but whether the button is on screen, and the stylesheet already answers
     that. So it is asked rather than re-derived. */
  function folded(p) {
    return window.getComputedStyle(p.toggle).display !== 'none';
  }

  function enhance(nav) {
    if (nav.hasAttribute('data-cf-nav-wired')) return;
    var p = parts(nav);
    if (!p) return;
    nav.setAttribute('data-cf-nav-wired', '');

    set(p, false);

    p.toggle.addEventListener('click', function () { set(p, !isOpen(p)); });

    /* APG, disclosure navigation: Escape closes the dropdown and puts focus
       back on the button that controls it. Bound to the bar rather than to the
       document, so Escape inside the panel is answered and Escape anywhere
       else on the page still belongs to the page. */
    nav.addEventListener('keydown', function (event) {
      if (event.key !== 'Escape' || !isOpen(p)) return;
      set(p, false);
      p.toggle.focus();
    });

    /* Same pattern: moving focus out of the navigation region closes it.
       relatedTarget is where focus is going, and it is null when focus leaves
       the document altogether — a tab away to the browser chrome is not the
       reader leaving the menu, so the panel stays as they left it. */
    nav.addEventListener('focusout', function (event) {
      if (!isOpen(p)) return;
      if (event.relatedTarget && !nav.contains(event.relatedTarget)) set(p, false);
    });

    /* A pointer landing anywhere else. The panel is an opaque plate over the
       hero video, so a reader who has moved on should not have to travel back
       to the button to be rid of it. The button's own click has already been
       answered by the time this runs — it is inside the bar, so this does not
       immediately undo it. */
    document.addEventListener('click', function (event) {
      if (isOpen(p) && !nav.contains(event.target)) set(p, false);
    });

    /* Following a link in the panel. On this site every one of them leaves the
       page and takes the panel with it, but a link to a fragment on the current
       page does not, and a menu left standing over the thing it has just
       scrolled to is the failure that costs. */
    p.panel.addEventListener('click', function (event) {
      if (event.target.closest('a')) set(p, false);
    });

    /* The open state belongs to the folded bar. Above the threshold the
       stylesheet draws the links as the bar whatever data-open says, so
       nothing looks wrong — but the attributes survive, and narrowing the
       window again drops open a menu nobody asked for. Read in a frame rather
       than in the event, so dragging a window edge costs one style resolution
       per painted frame instead of one per pixel. */
    var pending = false;
    window.addEventListener('resize', function () {
      if (pending || !isOpen(p)) return;
      pending = true;
      window.requestAnimationFrame(function () {
        pending = false;
        if (isOpen(p) && !folded(p)) set(p, false);
      });
    });
  }

  function run() {
    var bars = document.querySelectorAll('.cf-nav');
    for (var i = 0; i < bars.length; i++) enhance(bars[i]);
  }

  /* The head is too early to find the bar, so the wiring waits for the
     document — and runs immediately if the file has been placed late anyway.
     enhance() is idempotent either way. */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();
