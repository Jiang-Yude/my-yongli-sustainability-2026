// Lightbox — 點擊 .cover 圖片放全螢幕
(function () {
  'use strict';

  function openLightbox(src, alt) {
    const overlay = document.createElement('div');
    overlay.className = 'lightbox-overlay';
    overlay.innerHTML = `
      <img src="${src}" alt="${alt || ''}" class="lightbox-image">
      <button class="lightbox-close" aria-label="關閉" type="button">×</button>
      <p class="lightbox-hint">點任意處或按 ESC 關閉</p>
    `;

    function close() {
      overlay.remove();
      document.body.style.overflow = '';
      document.removeEventListener('keydown', escHandler);
    }

    function escHandler(e) {
      if (e.key === 'Escape') close();
    }

    overlay.addEventListener('click', close);
    document.addEventListener('keydown', escHandler);
    document.body.appendChild(overlay);
    document.body.style.overflow = 'hidden';
  }

  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('img.cover').forEach(img => {
      img.style.cursor = 'zoom-in';
      img.setAttribute('role', 'button');
      img.setAttribute('tabindex', '0');
      img.title = '點擊放全螢幕';
      img.addEventListener('click', () => openLightbox(img.src, img.alt));
      img.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          openLightbox(img.src, img.alt);
        }
      });
    });
  });
})();
