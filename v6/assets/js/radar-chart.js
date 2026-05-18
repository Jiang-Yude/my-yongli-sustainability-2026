// Radar Chart v2 — 純 SVG 數據驅動 + hover popover（可點軸彈出詳情卡）
// 用法：
// <div class="radar-chart"
//   data-axes='["A","B","C","D","E"]'
//   data-subs='["Sub","..."]'           (可選，英文小字)
//   data-values='[3,5,5,1,4]'
//   data-details='["詳情 A","詳情 B",...]' (可選，hover 顯示)
//   data-max="5" data-levels="5"></div>
// 改 data-* 即自動重繪。
(function () {
  'use strict';

  const STYLE = `
.radar-chart {
  width: 100%;
  max-width: 480px;
  margin: 0 auto;
  position: relative;
  user-select: none;
}
.radar-chart svg { width: 100%; height: auto; display: block; overflow: visible; }
.radar-grid { fill: none; stroke: var(--line, #E0D8C7); stroke-width: 1; }
.radar-grid-outer { stroke: var(--line, #C9C2B0); stroke-width: 1.5; }
.radar-axis { stroke: var(--line, #D8CFB8); stroke-width: 1; stroke-dasharray: 2 3; }
.radar-data-poly {
  fill: var(--gold, #C9A961);
  fill-opacity: 0.22;
  stroke: var(--gold-deep, #A8884A);
  stroke-width: 2;
  stroke-linejoin: round;
  transition: fill-opacity 0.3s;
  pointer-events: none;
}
.radar-chart:hover .radar-data-poly { fill-opacity: 0.36; }
.radar-data-dot {
  fill: var(--gold-deep, #A8884A);
  stroke: #fff;
  stroke-width: 2;
  cursor: pointer;
  transition: r 0.2s, fill 0.2s;
  pointer-events: all;
}
.radar-data-dot:hover, .radar-data-dot.active { r: 8; fill: var(--gold, #C9A961); }

.radar-label-hit {
  fill: transparent;
  stroke: transparent;
  cursor: pointer;
  pointer-events: all;
}
.radar-axis-label {
  font-family: "Noto Serif TC", serif;
  font-size: 17px;
  font-weight: 600;
  fill: var(--ink, #2B2A26);
  text-anchor: middle;
  pointer-events: none;
  transition: fill 0.2s;
}
.radar-axis-sub {
  font-family: "Inter", sans-serif;
  font-size: 12px;
  fill: var(--ink-4, #7A746B);
  text-anchor: middle;
  letter-spacing: 0.08em;
  pointer-events: none;
}
.radar-axis-value {
  font-family: "Inter", sans-serif;
  font-size: 14px;
  fill: var(--gold-deep, #A8884A);
  text-anchor: middle;
  font-weight: 600;
  letter-spacing: 0.04em;
  pointer-events: none;
  transition: fill 0.2s;
}
.radar-axis-group.active .radar-axis-label { fill: var(--gold-deep, #A8884A); }
.radar-axis-group.active .radar-axis-value { fill: var(--ink, #2B2A26); }
.radar-tick-label {
  font-family: "Inter", sans-serif;
  font-size: 11px;
  fill: var(--ink-4, #9A9388);
  text-anchor: middle;
  pointer-events: none;
}

/* Popover：hover dot/label 時穩穩浮現（漸入漸出，切換軸位置會平滑移動） */
.radar-popover {
  position: absolute;
  pointer-events: none;
  opacity: 0;
  transform: translateY(8px) scale(0.98);
  transform-origin: top center;
  transition:
    opacity 0.32s cubic-bezier(0.16, 1, 0.3, 1),
    transform 0.32s cubic-bezier(0.16, 1, 0.3, 1),
    left 0.28s cubic-bezier(0.4, 0, 0.2, 1),
    top 0.28s cubic-bezier(0.4, 0, 0.2, 1);
  background: #fff;
  border: 1px solid var(--line, #E0D8C7);
  border-top: 4px solid var(--gold, #C9A961);
  border-radius: 10px;
  padding: 14px 16px 14px;
  box-shadow: 0 12px 32px rgba(0,0,0,0.14), 0 2px 6px rgba(0,0,0,0.05);
  min-width: 240px;
  max-width: 320px;
  z-index: 20;
  font-family: "Noto Sans TC", sans-serif;
}
.radar-popover.show {
  opacity: 1;
  transform: translateY(0) scale(1);
  pointer-events: auto;
}
.radar-popover .pop-num {
  font-family: "Inter", sans-serif;
  font-size: 11px;
  letter-spacing: 0.2em;
  color: var(--gold-deep, #A8884A);
  font-weight: 700;
}
.radar-popover h4 {
  font-family: "Noto Serif TC", serif;
  font-size: 1.25rem;
  font-weight: 600;
  margin: 6px 0 3px;
  color: var(--ink, #2B2A26);
  line-height: 1.3;
}
.radar-popover .pop-sub {
  font-size: 12px;
  letter-spacing: 0.1em;
  color: var(--ink-4, #7A746B);
  font-family: "Inter", sans-serif;
  display: block;
  margin-bottom: 10px;
}
.radar-popover .pop-score {
  display: inline-block;
  padding: 4px 12px;
  background: var(--gold-bg, #F5EDD7);
  color: var(--gold-deep, #A8884A);
  font-family: "Inter", sans-serif;
  font-size: 13px;
  font-weight: 600;
  border-radius: 11px;
  letter-spacing: 0.04em;
  margin-bottom: 12px;
}
.radar-popover .pop-detail {
  margin: 0;
  font-size: 15px;
  line-height: 1.7;
  color: var(--ink-3, #5A554C);
}
.radar-popover-hint {
  display: block;
  margin-top: 10px;
  color: var(--ink-4, #9A9388);
  font-size: 11px;
  letter-spacing: 0.04em;
}
@media (max-width: 600px) {
  .radar-axis-label { font-size: 12px; }
  .radar-axis-value { font-size: 10px; }
  .radar-axis-sub { font-size: 9px; }
  .radar-popover { min-width: 180px; max-width: 240px; }
}
  `.trim();

  if (!document.getElementById('radar-chart-style')) {
    const s = document.createElement('style');
    s.id = 'radar-chart-style';
    s.textContent = STYLE;
    document.head.appendChild(s);
  }

  function render(container) {
    const axes = JSON.parse(container.dataset.axes || '[]');
    const values = JSON.parse(container.dataset.values || '[]');
    const subs = JSON.parse(container.dataset.subs || '[]');
    const details = JSON.parse(container.dataset.details || '[]');
    const max = Number(container.dataset.max || 5);
    const levels = Number(container.dataset.levels || 5);
    if (axes.length !== values.length || axes.length < 3) return;

    const N = axes.length;
    const W = 480, H = 480;
    const cx = W / 2, cy = H / 2;
    const R = 150;
    const Rlabel = R + 38;
    const RhitOuter = R + 70;
    const startAngle = -Math.PI / 2;

    function pt(angle, dist) {
      return [cx + dist * Math.cos(angle), cy + dist * Math.sin(angle)];
    }

    let svg = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="五大服務影響力雷達圖">`;

    for (let lv = 1; lv <= levels; lv++) {
      const r = (R * lv) / levels;
      const pts = [];
      for (let i = 0; i < N; i++) {
        const a = startAngle + (i * 2 * Math.PI) / N;
        const [x, y] = pt(a, r);
        pts.push(`${x.toFixed(2)},${y.toFixed(2)}`);
      }
      const klass = lv === levels ? 'radar-grid radar-grid-outer' : 'radar-grid';
      svg += `<polygon class="${klass}" points="${pts.join(' ')}"/>`;
    }

    for (let i = 0; i < N; i++) {
      const a = startAngle + (i * 2 * Math.PI) / N;
      const [x, y] = pt(a, R);
      svg += `<line class="radar-axis" x1="${cx}" y1="${cy}" x2="${x.toFixed(2)}" y2="${y.toFixed(2)}"/>`;
    }

    for (let lv = 1; lv <= levels; lv++) {
      const r = (R * lv) / levels;
      svg += `<text class="radar-tick-label" x="${cx + 6}" y="${cy - r + 4}">${lv}</text>`;
    }

    // 資料多邊形
    const dataPts = [];
    for (let i = 0; i < N; i++) {
      const a = startAngle + (i * 2 * Math.PI) / N;
      const r = (R * Math.max(0, Math.min(max, values[i]))) / max;
      const [x, y] = pt(a, r);
      dataPts.push(`${x.toFixed(2)},${y.toFixed(2)}`);
    }
    svg += `<polygon class="radar-data-poly" points="${dataPts.join(' ')}"/>`;

    // 軸標籤 + 端點：每軸包一個 group，含 hit area
    for (let i = 0; i < N; i++) {
      const a = startAngle + (i * 2 * Math.PI) / N;
      const r = (R * Math.max(0, Math.min(max, values[i]))) / max;
      const [dx, dy] = pt(a, r);
      const [lx, ly] = pt(a, Rlabel);

      svg += `<g class="radar-axis-group" data-index="${i}">`;
      // hit area：包覆 label 區的大方框，方便 hover
      const [hx, hy] = pt(a, RhitOuter);
      svg += `<rect class="radar-label-hit" x="${(hx - 60).toFixed(2)}" y="${(hy - 24).toFixed(2)}" width="120" height="48" rx="8"/>`;
      // 軸文字
      svg += `<text class="radar-axis-label" x="${lx.toFixed(2)}" y="${ly.toFixed(2)}">${axes[i]}</text>`;
      if (subs[i]) {
        svg += `<text class="radar-axis-sub" x="${lx.toFixed(2)}" y="${(ly + 14).toFixed(2)}">${subs[i]}</text>`;
      }
      const valueY = subs[i] ? ly + 28 : ly + 16;
      svg += `<text class="radar-axis-value" x="${lx.toFixed(2)}" y="${valueY.toFixed(2)}">${values[i]} / ${max}</text>`;
      // 端點
      svg += `<circle class="radar-data-dot" cx="${dx.toFixed(2)}" cy="${dy.toFixed(2)}" r="5"><title>${axes[i]}: ${values[i]} / ${max}</title></circle>`;
      svg += `</g>`;
    }

    svg += '</svg>';

    // popover element
    const popoverHTML = `<div class="radar-popover" role="dialog" aria-hidden="true">
      <span class="pop-num"></span>
      <h4></h4>
      <span class="pop-sub"></span>
      <span class="pop-score"></span>
      <p class="pop-detail"></p>
    </div>`;

    container.innerHTML = svg + popoverHTML;

    // === 綁定 hover/click ===
    const popover = container.querySelector('.radar-popover');
    const popNum = popover.querySelector('.pop-num');
    const popH4 = popover.querySelector('h4');
    const popSub = popover.querySelector('.pop-sub');
    const popScore = popover.querySelector('.pop-score');
    const popDetail = popover.querySelector('.pop-detail');
    const groups = container.querySelectorAll('.radar-axis-group');
    let stickyIndex = -1;

    function showPopover(i, anchorEvent) {
      const num = String(i + 1).padStart(2, '0');
      popNum.textContent = num;
      popH4.textContent = axes[i];
      popSub.textContent = subs[i] || '';
      popSub.style.display = subs[i] ? '' : 'none';
      popScore.textContent = `${values[i]} / ${max}`;
      popDetail.textContent = details[i] || '';
      popDetail.style.display = details[i] ? '' : 'none';

      // 定位：浮在 svg 範圍內、軸 label 旁邊
      const svgEl = container.querySelector('svg');
      const svgRect = svgEl.getBoundingClientRect();
      const containerRect = container.getBoundingClientRect();
      const a = startAngle + (i * 2 * Math.PI) / N;
      const rPct = Rlabel / W;
      const labelX = cx / W * svgRect.width + Math.cos(a) * rPct * svgRect.width;
      const labelY = cy / H * svgRect.height + Math.sin(a) * rPct * svgRect.height;
      const relX = svgRect.left - containerRect.left + labelX;
      const relY = svgRect.top - containerRect.top + labelY;

      popover.style.left = '';
      popover.style.right = '';
      popover.style.top = '';
      popover.style.bottom = '';

      // 所有 popover 固定在 svg 正下方居中，內容隨 hover 切換（穩定、不擋、不歪斜）
      const popW = popover.offsetWidth || 220;
      const svgBottomRel = svgRect.bottom - containerRect.top;
      const svgCenterRel = (svgRect.left + svgRect.right) / 2 - containerRect.left;
      let left = svgCenterRel - popW / 2;
      let top = svgBottomRel + 16;

      // 邊界保護：允許 popover 超出 .radar-chart 但限制在 dashboard-card 內
      const card = container.closest('.dashboard-card');
      const cardRect = card ? card.getBoundingClientRect() : containerRect;
      const containerLeftInCard = containerRect.left - cardRect.left;
      const minLeft = -containerLeftInCard + 12;
      const maxLeft = cardRect.width - containerLeftInCard - popW - 12;
      if (left < minLeft) left = minLeft;
      if (left > maxLeft) left = maxLeft;
      if (top < 8) top = 8;

      popover.style.left = left + 'px';
      popover.style.top = top + 'px';
      popover.classList.add('show');
      popover.setAttribute('aria-hidden', 'false');

      groups.forEach(g => g.classList.remove('active'));
      groups[i].classList.add('active');
    }

    // === 延遲隱藏機制：避免軸切換時閃爍 ===
    let leaveTimer = null;

    function cancelHide() {
      if (leaveTimer) {
        clearTimeout(leaveTimer);
        leaveTimer = null;
      }
    }

    function scheduleHide(delay) {
      if (stickyIndex !== -1) return;
      cancelHide();
      leaveTimer = setTimeout(() => {
        popover.classList.remove('show');
        popover.setAttribute('aria-hidden', 'true');
        groups.forEach(g => g.classList.remove('active'));
        leaveTimer = null;
      }, delay);
    }

    function hidePopoverNow() {
      cancelHide();
      popover.classList.remove('show');
      popover.setAttribute('aria-hidden', 'true');
      groups.forEach(g => g.classList.remove('active'));
    }

    groups.forEach((g, i) => {
      g.addEventListener('mouseenter', e => {
        cancelHide();
        if (stickyIndex === -1) showPopover(i, e);
      });
      g.addEventListener('mouseleave', () => scheduleHide(180));
      g.addEventListener('click', e => {
        e.stopPropagation();
        if (stickyIndex === i) {
          stickyIndex = -1;
          scheduleHide(50);
        } else {
          stickyIndex = i;
          cancelHide();
          showPopover(i, e);
        }
      });
    });

    // popover 本身 hover 也算停留（取消隱藏，移到 popover 上不會消失）
    popover.addEventListener('mouseenter', cancelHide);
    popover.addEventListener('mouseleave', () => scheduleHide(180));

    // 點外面取消 sticky
    document.addEventListener('click', e => {
      if (!container.contains(e.target)) {
        stickyIndex = -1;
        hidePopoverNow();
      }
    });
  }

  function bind() {
    document.querySelectorAll('.radar-chart').forEach(c => {
      if (c.dataset.radarBound) return;
      c.dataset.radarBound = '1';
      render(c);
    });
  }

  window.RadarChart = { render, bindAll: bind };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bind);
  } else {
    bind();
  }
})();
