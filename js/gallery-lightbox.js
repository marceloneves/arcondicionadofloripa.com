(function () {
  function onIdle(fn) {
    if (typeof requestIdleCallback === 'function') {
      requestIdleCallback(fn, { timeout: 1500 });
      return;
    }
    setTimeout(fn, 0);
  }

  function initGalleryLightbox() {
    const galleryLinks = document.querySelectorAll('.home-instalacao-link');
    if (!galleryLinks.length) return;

    const lightbox = document.createElement('div');
    lightbox.className = 'img-lightbox';
    lightbox.innerHTML = '<button class="img-lightbox-close" type="button" aria-label="Fechar imagem">Fechar</button><img alt="">';
    document.body.appendChild(lightbox);

    const lbImg = lightbox.querySelector('img');
    const closeBtn = lightbox.querySelector('.img-lightbox-close');
    const close = function () {
      lightbox.classList.remove('open');
    };

    galleryLinks.forEach(function (link) {
      link.addEventListener('click', function (e) {
        e.preventDefault();
        const img = link.querySelector('img');
        lbImg.src = link.getAttribute('href');
        lbImg.alt = img ? img.alt : 'Imagem ampliada';
        lightbox.classList.add('open');
      });
    });

    closeBtn.addEventListener('click', close);
    lightbox.addEventListener('click', function (e) {
      if (e.target === lightbox) close();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') close();
    });
  }

  onIdle(initGalleryLightbox);
})();
