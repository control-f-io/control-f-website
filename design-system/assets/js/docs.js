/* Control-F design system — documentation chrome.
   Builds the sidebar, wires the swatch copy buttons, marks the current page.
   Pure DOM work, no fetch, so it runs from file:// as well as over http. */

(function () {
  'use strict';

  var NAV = [
    { title: 'Start', items: [
      { href: 'index.html', label: 'Overview' }
    ]},
    { title: 'Foundations', items: [
      { href: 'foundations/colors.html',      label: 'Colour' },
      { href: 'foundations/typography.html',  label: 'Typography' },
      { href: 'foundations/layout.html',      label: 'Layout & Grid' },
      { href: 'foundations/geometry.html',    label: 'Geometry & Lines' },
      { href: 'foundations/iconography.html', label: 'Iconography' },
      { href: 'foundations/materials.html',   label: 'Materials' },
      { href: 'foundations/logo.html',        label: 'Logo' },
      { href: 'foundations/photography.html', label: 'Photography' },
      { href: 'foundations/motion.html',      label: 'Motion' }
    ]},
    { title: 'Components', items: [
      { href: 'components/buttons.html',        label: 'Buttons' },
      { href: 'components/navigation.html',     label: 'Navigation' },
      { href: 'components/section-header.html', label: 'Section Header' },
      { href: 'components/process-card.html',   label: 'Process Card' },
      { href: 'components/accordion.html',      label: 'Accordion / FAQ' },
      { href: 'components/blog-grid.html',      label: 'Blog Grid' },
      { href: 'components/team.html',           label: 'Team' },
      { href: 'components/forms.html',          label: 'Forms' },
      { href: 'components/footer.html',         label: 'Footer' }
    ]},
    { title: 'Patterns', items: [
      { href: 'patterns/landing-page.html', label: 'Landing Page' },
      { href: 'patterns/ueber-uns.html',    label: 'Über uns page' }
    ]},
    { title: 'Reference', items: [
      { href: 'reference.html', label: 'Source Material' }
    ]}
  ];

  function root() {
    var el = document.body;
    return el.dataset.root === undefined ? '' : el.dataset.root;
  }

  function currentPath() {
    var parts = window.location.pathname.split('/').filter(Boolean);
    var file = parts[parts.length - 1] || 'index.html';
    var dir = parts[parts.length - 2] || '';
    return ['foundations', 'components', 'patterns'].indexOf(dir) > -1
      ? dir + '/' + file
      : file;
  }

  function buildNav() {
    var host = document.querySelector('[data-docs-nav]');
    if (!host) return;
    var here = currentPath();
    var prefix = root();

    var brand = document.createElement('a');
    brand.className = 'docs-sidebar__brand';
    brand.href = prefix + 'index.html';
    brand.innerHTML =
      '<img src="' + prefix + 'assets/img/logo/cf-logo-horizontal-white.svg" alt="Control-F">' +
      '<span>Design System v1.0</span>';
    host.appendChild(brand);

    var nav = document.createElement('nav');
    nav.className = 'docs-nav';
    nav.setAttribute('aria-label', 'Design System');

    NAV.forEach(function (group) {
      var wrap = document.createElement('div');
      wrap.className = 'docs-nav__group';

      var title = document.createElement('p');
      title.className = 'docs-nav__title';
      title.textContent = group.title;
      wrap.appendChild(title);

      var list = document.createElement('ul');
      list.className = 'docs-nav__list';
      group.items.forEach(function (item) {
        var li = document.createElement('li');
        var a = document.createElement('a');
        a.href = prefix + item.href;
        a.textContent = item.label;
        if (item.href === here) a.setAttribute('aria-current', 'page');
        li.appendChild(a);
        list.appendChild(li);
      });
      wrap.appendChild(list);
      nav.appendChild(wrap);
    });

    host.appendChild(nav);
  }

  /* Colour swatches copy their hex on click. */
  function wireSwatches() {
    document.addEventListener('click', function (event) {
      var swatch = event.target.closest ? event.target.closest('.docs-swatch') : null;
      if (!swatch) return;
      var hex = swatch.dataset.hex;
      if (!hex || !navigator.clipboard) return;
      navigator.clipboard.writeText(hex).then(function () {
        swatch.classList.add('is-copied');
        setTimeout(function () { swatch.classList.remove('is-copied'); }, 1400);
      });
    });
  }

  /* Mobile nav toggle for the demo navigation component. */
  function wireNavToggle() {
    document.addEventListener('click', function (event) {
      var toggle = event.target.closest ? event.target.closest('.cf-nav__toggle') : null;
      if (!toggle) return;
      var list = document.getElementById(toggle.getAttribute('aria-controls'));
      if (!list) return;
      var open = list.dataset.open === 'true';
      list.dataset.open = String(!open);
      toggle.setAttribute('aria-expanded', String(!open));
    });
  }

  /* Inject the icon sprite so every page can `<use href="#cf-arrow">`.
     In production this block belongs in the page template, right after
     <body> — see components/buttons.html for the copy-paste version. */
  var SPRITE =
    '<symbol id="cf-arrow" viewBox="0 0 600 480"><g transform="translate(600,0) scale(-1,1)">' +
    '<path d="M425.367 332.683C423.155 331.578 423.155 328.422 425.367 327.317L594.633 242.683C596.845 241.578 ' +
    '596.845 238.422 594.633 237.317L483.578 181.789C481.325 180.663 478.675 180.663 476.422 181.789L185.367 ' +
    '327.317C183.155 328.422 183.155 331.578 185.367 332.683L476.422 478.211C478.675 479.337 481.325 479.337 ' +
    '483.578 478.211L594.633 422.683C596.845 421.578 596.845 418.422 594.633 417.317L425.367 332.683Z"/>' +
    '<path d="M116.422 298.211C118.675 299.337 121.325 299.337 123.578 298.211L594.633 62.6833C596.845 61.5777 ' +
    '596.845 58.4223 594.633 57.3167L483.578 1.78885C481.325 0.662745 478.675 0.662745 476.422 1.78885L5.36656 ' +
    '237.317C3.15542 238.422 3.15542 241.578 5.36656 242.683L116.422 298.211Z"/></g></symbol>';

  function injectSprite() {
    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('aria-hidden', 'true');
    svg.style.display = 'none';
    svg.innerHTML = SPRITE;
    document.body.insertBefore(svg, document.body.firstChild);
  }

  document.addEventListener('DOMContentLoaded', function () {
    injectSprite();
    buildNav();
    wireSwatches();
    wireNavToggle();
  });
})();
