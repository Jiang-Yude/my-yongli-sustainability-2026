// Lightbox v2 — 點圖開全螢幕，預設真實尺寸 100%，支援縮放（滾輪/雙擊/按鈕）+ 拖曳移動
(function () {
  'use strict';

  // --- 動態 inject style，不污染 common.css ---
  const STYLE = `
.lightbox-overlay{
  position:fixed;inset:0;
  background:rgba(15,15,15,0.94);
  z-index:9999;
  overflow:hidden;
  cursor:zoom-out;
  user-select:none;
}
.lightbox-stage{
  position:absolute;inset:0;
  overflow:hidden;
  display:flex;align-items:center;justify-content:center;
}
.lightbox-image{
  max-width:none;max-height:none;
  cursor:grab;
  transition:transform 0.18s ease-out;
  -webkit-user-drag:none;
  user-select:none;
  pointer-events:auto;
  will-change:transform;
}
.lightbox-image.dragging{cursor:grabbing;transition:none}
.lightbox-close{
  position:fixed;top:18px;right:22px;
  background:rgba(0,0,0,0.55);color:#fff;
  border:1px solid rgba(255,255,255,0.18);border-radius:50%;
  width:46px;height:46px;
  font-size:26px;line-height:1;cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  transition:background 0.2s, transform 0.2s;
  z-index:10001;font-family:inherit;
}
.lightbox-close:hover{background:rgba(0,0,0,0.85);transform:rotate(90deg)}
.lightbox-controls{
  position:fixed;bottom:36px;left:50%;
  transform:translateX(-50%);
  display:flex;gap:10px;
  z-index:10001;
}
.lb-btn{
  background:rgba(0,0,0,0.55);color:#fff;
  border:1px solid rgba(255,255,255,0.18);border-radius:50%;
  width:44px;height:44px;
  font-size:20px;cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  transition:background 0.2s;
  font-family:inherit;
}
.lb-btn:hover{background:rgba(0,0,0,0.85)}
.lb-scale{
  background:rgba(0,0,0,0.55);color:rgba(255,255,255,0.85);
  border:1px solid rgba(255,255,255,0.18);border-radius:22px;
  padding:0 16px;height:44px;
  display:flex;align-items:center;
  font-size:13px;letter-spacing:0.04em;
  font-family:"Inter",sans-serif;
  min-width:60px;justify-content:center;
}
.lightbox-hint{
  position:fixed;bottom:14px;left:50%;
  transform:translateX(-50%);
  color:rgba(255,255,255,0.5);font-size:12px;
  margin:0;letter-spacing:0.06em;
  z-index:10001;
  font-family:"Noto Sans TC",sans-serif;
  pointer-events:none;
  white-space:nowrap;
}
.lightbox-nav{
  position:fixed;top:50%;transform:translateY(-50%);
  background:rgba(0,0,0,0.55);color:#fff;
  border:1px solid rgba(255,255,255,0.18);border-radius:50%;
  width:52px;height:52px;
  font-size:28px;line-height:1;cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  transition:background 0.2s, transform 0.2s;
  z-index:10001;font-family:inherit;
}
.lightbox-nav:hover{background:rgba(0,0,0,0.85)}
.lightbox-nav.lb-prev{left:22px}
.lightbox-nav.lb-next{right:22px}
.lightbox-nav.lb-prev:hover{transform:translateY(-50%) translateX(-2px)}
.lightbox-nav.lb-next:hover{transform:translateY(-50%) translateX(2px)}
.lightbox-counter{
  position:fixed;top:22px;left:50%;
  transform:translateX(-50%);
  background:rgba(0,0,0,0.55);color:rgba(255,255,255,0.9);
  border:1px solid rgba(255,255,255,0.18);border-radius:18px;
  padding:6px 16px;font-size:13px;letter-spacing:0.06em;
  font-family:"Noto Sans TC",sans-serif;
  z-index:10001;
}
@media(max-width:640px){
  .lightbox-controls{bottom:78px;gap:8px}
  .lb-btn,.lightbox-close{width:40px;height:40px;font-size:18px}
  .lb-scale{height:40px;padding:0 12px;font-size:12px;min-width:54px}
  .lightbox-hint{bottom:58px;font-size:11px}
  .lightbox-close{top:14px;right:14px}
  .lightbox-nav{width:44px;height:44px;font-size:22px}
  .lightbox-nav.lb-prev{left:10px}
  .lightbox-nav.lb-next{right:10px}
  .lightbox-counter{top:14px;font-size:12px;padding:5px 14px}
}
  `.trim();

  if (!document.getElementById('lightbox-style')) {
    const s = document.createElement('style');
    s.id = 'lightbox-style';
    s.textContent = STYLE;
    document.head.appendChild(s);
  }

  // --- 核心：開啟 lightbox ---
  // group: 同相片集的 img 陣列（從 [data-lightbox-group] 或 .case-gallery 偵測）
  // startIndex: 開啟時是第幾張
  function openLightbox(src, alt, group, startIndex) {
    const overlay = document.createElement('div');
    overlay.className = 'lightbox-overlay';
    const hasGroup = Array.isArray(group) && group.length > 1;
    let currentIndex = (typeof startIndex === 'number' && startIndex >= 0) ? startIndex : 0;

    const navHTML = hasGroup ? `
      <button class="lightbox-nav lb-prev" aria-label="上一張" type="button">‹</button>
      <button class="lightbox-nav lb-next" aria-label="下一張" type="button">›</button>
      <div class="lightbox-counter">${currentIndex + 1} / ${group.length}</div>
    ` : '';

    overlay.innerHTML = `
      <div class="lightbox-stage">
        <img class="lightbox-image" src="${src}" alt="${alt || ''}" draggable="false">
      </div>
      <button class="lightbox-close" aria-label="關閉" type="button">×</button>
      ${navHTML}
      <div class="lightbox-controls">
        <button class="lb-btn lb-zoom-out" aria-label="縮小" type="button">−</button>
        <div class="lb-scale">100%</div>
        <button class="lb-btn lb-zoom-in" aria-label="放大" type="button">＋</button>
        <button class="lb-btn lb-reset" aria-label="重置" type="button" title="重置">⊙</button>
      </div>
      <p class="lightbox-hint">${hasGroup ? '← / → 切換 · ' : ''}滾輪 / 雙擊放大 · 拖曳移動 · ESC 關閉</p>
    `;

    document.body.appendChild(overlay);
    document.body.style.overflow = 'hidden';

    const stage = overlay.querySelector('.lightbox-stage');
    const img = overlay.querySelector('.lightbox-image');
    const scaleLabel = overlay.querySelector('.lb-scale');

    let scale = 1;
    let tx = 0, ty = 0;
    let isDragging = false;
    let startX = 0, startY = 0;

    const MIN = 0.25, MAX = 6;

    function apply() {
      img.style.transform = `translate(${tx}px, ${ty}px) scale(${scale})`;
      scaleLabel.textContent = Math.round(scale * 100) + '%';
    }

    function zoomTo(newScale, originX, originY) {
      newScale = Math.max(MIN, Math.min(MAX, newScale));
      if (originX !== undefined && originY !== undefined) {
        const rect = img.getBoundingClientRect();
        const cx = rect.left + rect.width / 2;
        const cy = rect.top + rect.height / 2;
        const dx = originX - cx;
        const dy = originY - cy;
        const ratio = newScale / scale;
        tx -= dx * (ratio - 1);
        ty -= dy * (ratio - 1);
      }
      scale = newScale;
      apply();
    }

    function zoomIn(ox, oy) { zoomTo(scale * 1.2, ox, oy); }
    function zoomOut(ox, oy) { zoomTo(scale / 1.2, ox, oy); }
    function reset() { scale = 1; tx = 0; ty = 0; apply(); }

    // 相片集切換（cycle：第一張 ← 跳到最後、最後一張 → 跳到第一張）
    const counterEl = overlay.querySelector('.lightbox-counter');
    function navigateTo(newIndex) {
      if (!hasGroup) return;
      if (newIndex < 0) newIndex = group.length - 1;
      if (newIndex >= group.length) newIndex = 0;
      currentIndex = newIndex;
      const target = group[currentIndex];
      img.src = target.src;
      img.alt = target.alt || '';
      // 切張時重置縮放與位移
      scale = 1; tx = 0; ty = 0; apply();
      if (counterEl) counterEl.textContent = (currentIndex + 1) + ' / ' + group.length;
    }
    function prevImage() { navigateTo(currentIndex - 1); }
    function nextImage() { navigateTo(currentIndex + 1); }

    // 圖片載入後：預設真實尺寸 100%（不縮放到 fit-to-screen）
    img.addEventListener('load', () => {
      scale = 1; tx = 0; ty = 0;
      apply();
    });

    overlay.querySelector('.lb-zoom-in').addEventListener('click', e => { e.stopPropagation(); zoomIn(); });
    overlay.querySelector('.lb-zoom-out').addEventListener('click', e => { e.stopPropagation(); zoomOut(); });
    overlay.querySelector('.lb-reset').addEventListener('click', e => { e.stopPropagation(); reset(); });

    if (hasGroup) {
      overlay.querySelector('.lb-prev').addEventListener('click', e => { e.stopPropagation(); prevImage(); });
      overlay.querySelector('.lb-next').addEventListener('click', e => { e.stopPropagation(); nextImage(); });
    }

    // 雙擊放大；已放大時雙擊回到 100%
    let lastClick = 0;
    img.addEventListener('click', e => {
      e.stopPropagation();
      const now = Date.now();
      if (now - lastClick < 300) {
        if (scale > 1.4) reset();
        else zoomTo(1.8, e.clientX, e.clientY);
      }
      lastClick = now;
    });

    // 滾輪縮放：根據 deltaY 大小自適應（trackpad 細膩，滑鼠滾輪較粗）
    stage.addEventListener('wheel', e => {
      e.preventDefault();
      // deltaY 通常 trackpad 在 ±1~20，滑鼠滾輪 ±100。用 log 平滑
      const intensity = Math.min(Math.abs(e.deltaY), 50) / 500;  // 最多 10%
      const delta = e.deltaY < 0 ? (1 + intensity) : 1 / (1 + intensity);
      zoomTo(scale * delta, e.clientX, e.clientY);
    }, { passive: false });

    img.addEventListener('mousedown', e => {
      isDragging = true;
      startX = e.clientX - tx;
      startY = e.clientY - ty;
      img.classList.add('dragging');
      e.preventDefault();
    });
    function onMouseMove(e) {
      if (!isDragging) return;
      tx = e.clientX - startX;
      ty = e.clientY - startY;
      apply();
    }
    function onMouseUp() {
      if (!isDragging) return;
      isDragging = false;
      img.classList.remove('dragging');
    }
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);

    // 觸控：單指拖曳 + 雙指捏合縮放
    let touchStartDist = 0;
    let touchStartScale = 1;
    img.addEventListener('touchstart', e => {
      if (e.touches.length === 1) {
        startX = e.touches[0].clientX - tx;
        startY = e.touches[0].clientY - ty;
        isDragging = true;
      } else if (e.touches.length === 2) {
        const dx = e.touches[0].clientX - e.touches[1].clientX;
        const dy = e.touches[0].clientY - e.touches[1].clientY;
        touchStartDist = Math.hypot(dx, dy);
        touchStartScale = scale;
        isDragging = false;
      }
    }, { passive: true });
    img.addEventListener('touchmove', e => {
      e.preventDefault();
      if (e.touches.length === 1 && isDragging) {
        tx = e.touches[0].clientX - startX;
        ty = e.touches[0].clientY - startY;
        apply();
      } else if (e.touches.length === 2 && touchStartDist > 0) {
        const dx = e.touches[0].clientX - e.touches[1].clientX;
        const dy = e.touches[0].clientY - e.touches[1].clientY;
        const dist = Math.hypot(dx, dy);
        const cx = (e.touches[0].clientX + e.touches[1].clientX) / 2;
        const cy = (e.touches[0].clientY + e.touches[1].clientY) / 2;
        zoomTo(touchStartScale * (dist / touchStartDist), cx, cy);
      }
    }, { passive: false });
    img.addEventListener('touchend', () => { isDragging = false; touchStartDist = 0; });

    function close() {
      overlay.remove();
      document.body.style.overflow = '';
      document.removeEventListener('keydown', escHandler);
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
    }
    function escHandler(e) {
      if (e.key === 'Escape') close();
      else if (e.key === '+' || e.key === '=') zoomIn();
      else if (e.key === '-' || e.key === '_') zoomOut();
      else if (e.key === '0') reset();
      else if (hasGroup && e.key === 'ArrowLeft') prevImage();
      else if (hasGroup && e.key === 'ArrowRight') nextImage();
    }
    overlay.querySelector('.lightbox-close').addEventListener('click', e => { e.stopPropagation(); close(); });
    overlay.addEventListener('click', e => {
      if (e.target === overlay || e.target === stage) close();
    });
    document.addEventListener('keydown', escHandler);
  }

  // --- 觸發：偵測需要 lightbox 的元素 ---
  function bind() {
    // 偵測相片集 group：img 的最近 ancestor 是 [data-lightbox-group] 或 .case-gallery
    function getGroup(img) {
      const galleryEl = img.closest('[data-lightbox-group], .case-gallery');
      if (!galleryEl) return { group: null, index: 0 };
      const groupImgs = Array.from(galleryEl.querySelectorAll('img.cover'));
      return { group: groupImgs, index: groupImgs.indexOf(img) };
    }

    // 1. img.cover（service 海報、profile 大頭照、案例相片集等）
    document.querySelectorAll('img.cover').forEach(img => {
      if (img.dataset.lightboxBound) return;
      img.dataset.lightboxBound = '1';
      img.style.cursor = 'zoom-in';
      img.setAttribute('role', 'button');
      img.setAttribute('tabindex', '0');
      img.title = '點擊放大檢視';
      img.addEventListener('click', e => {
        e.preventDefault();
        const { group, index } = getGroup(img);
        openLightbox(img.src, img.alt, group, index);
      });
      img.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          const { group, index } = getGroup(img);
          openLightbox(img.src, img.alt, group, index);
        }
      });
    });

    // 2. .impact-map a（影響力地圖海報）— 拿掉 target="_blank"，改開 lightbox
    document.querySelectorAll('.impact-map a').forEach(a => {
      if (a.dataset.lightboxBound) return;
      a.dataset.lightboxBound = '1';
      a.removeAttribute('target');
      a.addEventListener('click', e => {
        e.preventDefault();
        const img = a.querySelector('img');
        openLightbox(a.href, img ? img.alt : '');
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bind);
  } else {
    bind();
  }
})();
