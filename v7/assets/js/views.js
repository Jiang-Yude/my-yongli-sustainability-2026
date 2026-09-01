// 網頁瀏覽計數（前端）。全站每頁由 footer 模板載入這支。
// 後端＝/api/view，資料存 Upstash Redis（與知識官網共用實例，本站 key 加 y: 前綴）。
// 防重刷：同一瀏覽器、同一頁、同一小時只送一次 +1。不記 IP、不放 cookie。
// 要在頁面上顯示數字：放 <span data-views="page"></span> 或 data-views="global"。
(function () {
  /* 瀏覽器識別碼：只為了算「幾個人」，不是帳號、不對應到任何真人。
     存這台瀏覽器的 localStorage，清掉就換一個新的。 */
  function vid() {
    try {
      var v = localStorage.getItem('yviewsVid');
      if (!v) { v = Math.random().toString(36).slice(2, 12); localStorage.setItem('yviewsVid', v); }
      return v;
    } catch (e) { return ''; }
  }
  function path() {
    var p = location.pathname.split('?')[0].split('#')[0];
    if (p.length > 1 && p.slice(-11) === '/index.html') p = p.slice(0, -10);
    if (p.length > 1 && p.slice(-1) !== '/' && p.indexOf('.') === -1) p = p + '/';
    return p;
  }
  function hourStamp() {
    var s = new Intl.DateTimeFormat('en-CA', {
      timeZone: 'Asia/Taipei', year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', hour12: false,
    }).format(new Date());
    return s.replace(/[^0-9]/g, '').slice(0, 10); // YYYYMMDDHH
  }
  function fill(name, val) {
    if (val == null) return;
    var els = document.querySelectorAll('[data-views="' + name + '"]');
    for (var i = 0; i < els.length; i++) els[i].textContent = Number(val).toLocaleString();
  }
  try {
    var p = path();
    /* 後台自己的瀏覽不算進統計，否則越看數字越髒 */
    if (p === '/stats.html') return;
    var key = 'yviewed:' + p + ':' + hourStamp();
    var firstThisHour = true;
    try { firstThisHour = !localStorage.getItem(key); } catch (e) {}
    fetch('/api/view', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: p, increment: firstThisHour, vid: vid(), ref: document.referrer || '' }),
    })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (firstThisHour) { try { localStorage.setItem(key, '1'); } catch (e) {} }
        fill('page', d.page);
        fill('global', d.global);
      })
      .catch(function () {});
  } catch (e) {}
})();
