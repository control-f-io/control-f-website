/* Control-F — Exit Intent & Inactivity Timeout CTA Modal.
   Triggers when:
   1. User shows exit intent (pointer moves toward top of viewport to leave/close).
   2. User is inactive/idle for a timeout period (default 35 seconds).

   Ships zero dependencies, pure vanilla JS.
*/

(function () {
  'use strict';

  var IDLE_TIMEOUT_MS = 35000; // 35 seconds idle timeout
  var EXIT_INITIAL_DELAY_MS = 1500; // 1.5 seconds initial delay before exit-intent is armed

  var STRINGS = {
    de: {
      eyebrow: 'BEREIT FÜR DEN NÄCHSTEN SCHRITT?',
      title: 'Starten Sie Ihr Projekt jetzt.',
      subtitle: 'Weniger ungeplante Stillstände, mehr Durchsatz aus Daten, die Sie schon haben.',
      btn: 'KONTAKT AUFNEHMEN',
      btnHref: '/kontakt',
      dismiss: 'Nein danke, ich möchte nur die Seite verlassen',
      closeAria: 'Schließen'
    },
    en: {
      eyebrow: 'READY FOR THE NEXT STEP?',
      title: 'Launch your project today.',
      subtitle: 'Fewer unplanned downtimes, higher throughput from data you already have.',
      btn: 'GET IN TOUCH',
      btnHref: '/en/kontakt',
      dismiss: 'No thanks, just let me leave',
      closeAria: 'Close'
    }
  };

  var state = {
    isOpen: false,
    modalEl: null,
    previouslyFocusedEl: null,
    idleTimer: null,
    canTriggerExit: false,
    dismissedThisPage: false
  };

  function getLang() {
    var docLang = (document.documentElement.lang || '').toLowerCase();
    if (docLang.indexOf('en') === 0 || window.location.pathname.indexOf('/en/') === 0 || window.location.pathname === '/en') {
      return 'en';
    }
    return 'de';
  }

  function isExcludedPage() {
    var path = window.location.pathname.toLowerCase();
    var exclusions = ['/kontakt', '/bewerbung', 'danke'];
    for (var i = 0; i < exclusions.length; i++) {
      if (path.indexOf(exclusions[i]) !== -1) {
        return true;
      }
    }
    return false;
  }

  function createModalMarkup(lang) {
    var t = STRINGS[lang] || STRINGS.de;
    var dialog = document.createElement('dialog');
    dialog.className = 'cf-exit-modal';
    dialog.setAttribute('data-cf-exit-modal', '');
    dialog.setAttribute('aria-modal', 'true');
    dialog.setAttribute('aria-labelledby', 'cf-exit-modal-title');
    dialog.setAttribute('aria-describedby', 'cf-exit-modal-desc');

    dialog.innerHTML = [
      '<div class="cf-exit-modal__backdrop" data-cf-exit-close tabindex="-1"></div>',
      '<div class="cf-exit-modal__panel" role="document">',
      '  <button type="button" class="cf-exit-modal__close" data-cf-exit-close aria-label="' + t.closeAria + '">',
      '    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">',
      '      <line x1="12" y1="2" x2="2" y2="12"></line>',
      '      <line x1="2" y1="2" x2="12" y2="12"></line>',
      '    </svg>',
      '  </button>',
      '  <p class="cf-exit-modal__eyebrow">' + t.eyebrow + '</p>',
      '  <h2 class="cf-exit-modal__title" id="cf-exit-modal-title">' + t.title + '</h2>',
      '  <p class="cf-exit-modal__subtitle" id="cf-exit-modal-desc">' + t.subtitle + '</p>',
      '  <a class="cf-exit-modal__btn" href="' + t.btnHref + '" data-cf-exit-cta>',
      '    <span>' + t.btn + '</span>',
      '    <svg class="cf-exit-modal__arrow" width="18" height="15" viewBox="0 0 600 480" fill="currentColor" aria-hidden="true">',
      '      <g transform="translate(600,0) scale(-1,1)">',
      '        <path d="M425.367 332.683C423.155 331.578 423.155 328.422 425.367 327.317L594.633 242.683C596.845 241.578 596.845 238.422 594.633 237.317L483.578 181.789C481.325 180.663 478.675 180.663 476.422 181.789L185.367 327.317C183.155 328.422 183.155 331.578 185.367 332.683L476.422 478.211C478.675 479.337 481.325 479.337 483.578 478.211L594.633 422.683C596.845 421.578 596.845 418.422 594.633 417.317L425.367 332.683Z"/>',
      '        <path d="M116.422 298.211C118.675 299.337 121.325 299.337 123.578 298.211L594.633 62.6833C596.845 61.5777 596.845 58.4223 594.633 57.3167L483.578 1.78885C481.325 0.662745 478.675 0.662745 476.422 1.78885L5.36656 237.317C3.15542 238.422 3.15542 241.578 5.36656 242.683L116.422 298.211Z"/>',
      '      </g>',
      '    </svg>',
      '  </a>',
      '  <button type="button" class="cf-exit-modal__dismiss" data-cf-exit-close>' + t.dismiss + '</button>',
      '</div>'
    ].join('\n');

    document.body.appendChild(dialog);
    return dialog;
  }

  function getFocusableElements(container) {
    if (!container) return [];
    var selector = 'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])';
    return Array.prototype.slice.call(container.querySelectorAll(selector));
  }

  function openModal() {
    if (state.isOpen || isExcludedPage() || state.dismissedThisPage) return;

    // Check if user is actively interacting with form inputs
    var activeTag = document.activeElement ? document.activeElement.tagName.toLowerCase() : '';
    if (activeTag === 'input' || activeTag === 'textarea' || activeTag === 'select') {
      return;
    }

    // Check if consent modal is currently open
    var consentDialog = document.querySelector('.cf-consent__dialog[open]');
    if (consentDialog) return;

    if (!state.modalEl) {
      state.modalEl = document.querySelector('[data-cf-exit-modal]');
      if (!state.modalEl) {
        state.modalEl = createModalMarkup(getLang());
      }
    }

    state.previouslyFocusedEl = document.activeElement;
    state.isOpen = true;

    if (typeof state.modalEl.showModal === 'function') {
      try {
        state.modalEl.showModal();
      } catch (e) {
        state.modalEl.setAttribute('open', '');
      }
    } else {
      state.modalEl.setAttribute('open', '');
    }

    state.modalEl.classList.add('is-active');
    document.documentElement.classList.add('has-modal-open');

    document.dispatchEvent(new CustomEvent('cf:exit-modal:open', { detail: { modal: state.modalEl } }));
  }

  function closeModal() {
    if (!state.isOpen || !state.modalEl) return;

    state.isOpen = false;
    state.dismissedThisPage = true;
    state.modalEl.classList.remove('is-active');
    document.documentElement.classList.remove('has-modal-open');

    if (typeof state.modalEl.close === 'function') {
      try {
        state.modalEl.close();
      } catch (e) {
        state.modalEl.removeAttribute('open');
      }
    } else {
      state.modalEl.removeAttribute('open');
    }

    if (state.previouslyFocusedEl && typeof state.previouslyFocusedEl.focus === 'function') {
      try {
        state.previouslyFocusedEl.focus();
      } catch (e) {}
    }

    document.dispatchEvent(new CustomEvent('cf:exit-modal:close', { detail: { modal: state.modalEl } }));
  }

  function handleKeydown(e) {
    if (!state.isOpen) return;

    if (e.key === 'Escape' || e.keyCode === 27) {
      e.preventDefault();
      closeModal();
      return;
    }

    if (e.key === 'Tab' || e.keyCode === 9) {
      var focusables = getFocusableElements(state.modalEl);
      if (!focusables.length) return;

      var first = focusables[0];
      var last = focusables[focusables.length - 1];

      if (e.shiftKey) {
        if (document.activeElement === first) {
          e.preventDefault();
          last.focus();
        }
      } else {
        if (document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    }
  }

  function handleMouseLeave(e) {
    if (!state.canTriggerExit || state.isOpen || state.dismissedThisPage) return;

    // Trigger when cursor leaves through the top of the viewport
    if (e.clientY <= 25) {
      openModal();
    }
  }

  function resetIdleTimer() {
    if (state.isOpen || state.dismissedThisPage) return;

    if (state.idleTimer) {
      clearTimeout(state.idleTimer);
    }

    state.idleTimer = setTimeout(function () {
      if (!state.isOpen && !state.dismissedThisPage) {
        openModal();
      }
    }, IDLE_TIMEOUT_MS);
  }

  function bindEvents() {
    // Arm exit-intent after short initial delay
    setTimeout(function () {
      state.canTriggerExit = true;
    }, EXIT_INITIAL_DELAY_MS);

    // Exit intent listener
    document.documentElement.addEventListener('mouseleave', handleMouseLeave);

    // Inactivity listener
    var activityEvents = ['mousemove', 'mousedown', 'keydown', 'scroll', 'touchstart'];
    activityEvents.forEach(function (evt) {
      window.addEventListener(evt, resetIdleTimer, { passive: true });
    });

    // Start initial idle timer
    resetIdleTimer();

    // Modal click delegation
    document.addEventListener('click', function (e) {
      if (!state.isOpen) return;

      var closeBtn = e.target.closest('[data-cf-exit-close]');
      if (closeBtn) {
        e.preventDefault();
        closeModal();
      }
    });

    // Keyboard navigation and ESC key
    document.addEventListener('keydown', handleKeydown);
  }

  function init() {
    if (isExcludedPage()) return;

    // Check if modal already exists in DOM or create it
    state.modalEl = document.querySelector('[data-cf-exit-modal]');
    if (!state.modalEl) {
      state.modalEl = createModalMarkup(getLang());
    }

    bindEvents();
  }

  // Public API
  window.cfExitIntent = {
    open: function () {
      state.dismissedThisPage = false;
      openModal();
    },
    close: closeModal,
    reset: function () {
      state.dismissedThisPage = false;
      state.canTriggerExit = true;
      resetIdleTimer();
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
