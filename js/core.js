(function () {
  function onIdle(fn) {
    if (typeof requestIdleCallback === 'function') {
      requestIdleCallback(fn, { timeout: 1200 });
      return;
    }
    setTimeout(fn, 0);
  }

  const menuBtn = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#mainNav');
  if (menuBtn && nav) {
    menuBtn.addEventListener('click', function () {
      const open = nav.classList.toggle('open');
      menuBtn.setAttribute('aria-expanded', String(open));
    });
  }

  function initAnchorScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(function (link) {
      link.addEventListener('click', function (e) {
        const id = link.getAttribute('href');
        if (!id || id === '#') return;
        const target = document.querySelector(id);
        if (!target) return;
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    });
  }

  onIdle(initAnchorScroll);
})();
