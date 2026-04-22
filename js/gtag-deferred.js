(function () {
  var GA_ID = 'G-TT4DGZ3R3W';
  var started = false;

  function injectGtag() {
    if (started) return;
    started = true;
    window.dataLayer = window.dataLayer || [];
    function gtag() {
      dataLayer.push(arguments);
    }
    window.gtag = gtag;
    gtag('js', new Date());
    gtag('config', GA_ID);
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(GA_ID);
    document.head.appendChild(s);
  }

  window.addEventListener('load', injectGtag);
  if (typeof requestIdleCallback === 'function') {
    requestIdleCallback(injectGtag, { timeout: 4000 });
  }
})();
