(function () {
  function onIdle(fn) {
    if (typeof requestIdleCallback === 'function') {
      requestIdleCallback(fn, { timeout: 1200 });
      return;
    }
    setTimeout(fn, 0);
  }

  function initFaq() {
    const faqButtons = document.querySelectorAll('.faq-question');
    if (!faqButtons.length) return;
    faqButtons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        const item = btn.closest('.faq-item');
        if (item) item.classList.toggle('open');
      });
    });
  }

  onIdle(initFaq);
})();
