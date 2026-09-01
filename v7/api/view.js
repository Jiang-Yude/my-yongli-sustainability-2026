// 瀏覽計數：每次有人開頁面就呼叫這支，對應數字 +1，回傳目前累計。
// 資料存 Upstash Redis，不碰 Google Analytics。
//
// ⚠️ 這個 Redis 跟江江的知識官網（jiangyude.com）共用同一個實例，
//    所以本站所有 key 一律加 `y:` 前綴隔離，不要拿掉。
//
// 需要的環境變數（Vercel 專案設定，不要寫進程式碼）：
//   KV_REST_API_URL、KV_REST_API_TOKEN
//   （或 UPSTASH_REDIS_REST_URL、UPSTASH_REDIS_REST_TOKEN）
//
// 前端 assets/js/views.js 會用「同瀏覽器同頁一小時只計一次」控制，避免重刷灌水。

const P = 'y:';   // 本站命名空間，改動前先想清楚舊資料會不會讀不到
const URL = () => process.env.UPSTASH_REDIS_REST_URL || process.env.KV_REST_API_URL;
const TOKEN = () => process.env.UPSTASH_REDIS_REST_TOKEN || process.env.KV_REST_API_TOKEN;

async function pipe(commands) {
  const r = await fetch(`${URL()}/pipeline`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${TOKEN()}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(commands),
  });
  if (!r.ok) throw new Error(`upstash ${r.status}`);
  return r.json();
}

function taipeiDay(d = new Date()) {
  return new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Asia/Taipei', year: 'numeric', month: '2-digit', day: '2-digit',
  }).format(d);
}

function normalizePath(p) {
  p = String(p || '/').split('?')[0].split('#')[0];
  if (!p.startsWith('/')) p = '/' + p;
  if (p.length > 1 && p.endsWith('/index.html')) p = p.slice(0, -10);
  if (p.length > 1 && !p.endsWith('/') && !p.includes('.')) p = p + '/';
  return p;
}

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  if (req.method === 'OPTIONS') { res.status(204).end(); return; }
  if (req.method !== 'POST') { res.status(405).json({ error: 'POST only' }); return; }
  if (!URL() || !TOKEN()) { res.status(200).json({ page: 0, global: 0, note: 'storage not configured' }); return; }

  let body = req.body;
  if (typeof body === 'string') { try { body = JSON.parse(body); } catch { body = {}; } }
  body = body || {};

  const path = normalizePath(body.path);
  const ua = String(req.headers['user-agent'] || '');
  const isBot = /bot|crawl|spider|slurp|headless|preview|facebookexternalhit|monitor|lighthouse/i.test(ua);
  const increment = body.increment !== false && !isBot;

  const day = taipeiDay();
  const month = day.slice(0, 7);
  const seg = path.split('/').filter(Boolean);
  // 分區：/profiles/xxx/ → profiles、/en/... → en、首頁沒有分區
  const section = seg.length >= 2 ? seg[0] : null;

  const cmds = [];
  if (increment) {
    cmds.push(['INCR', `${P}page:${path}`]);
    cmds.push(['INCR', `${P}global`]);
    cmds.push(['INCR', `${P}global:day:${day}`]);
    cmds.push(['INCR', `${P}global:month:${month}`]);
    if (section) cmds.push(['INCR', `${P}section:${section}`]);
    /* 每頁每日：一天一個 hash，欄位是路徑。page:<path> 只有累計總數，
       看不出「這頁這週有沒有人看」。path 超過 120 字元不記（防灌爆）。 */
    if (path.length <= 120) cmds.push(['HINCRBY', `${P}pageday:${day}`, path, 1]);
    cmds.push(['ZADD', `${P}idx:days`, Number(day.replace(/-/g, '')), day]);
    cmds.push(['ZADD', `${P}idx:months`, Number(month.replace('-', '')), month]);
  }
  cmds.push(['GET', `${P}page:${path}`]);
  cmds.push(['GET', `${P}global`]);

  try {
    const out = await pipe(cmds);
    const results = out.map((o) => (o && o.result != null ? o.result : 0));
    /* 當天這個 hash 的第一筆（HINCRBY 回 1）才設過期時間，留 90 天。
       一定要 await：serverless 在回應送出後會凍結，沒 await 的 promise 送不出去。 */
    if (increment && path.length <= 120) {
      const hIdx = cmds.findIndex((c) => c[0] === 'HINCRBY');
      if (hIdx >= 0 && Number(results[hIdx]) === 1) {
        try { await pipe([['EXPIRE', `${P}pageday:${day}`, 7776000]]); } catch { /* 設不成不擋計數 */ }
      }
    }
    const globalVal = Number(results.pop()) || 0;
    const pageVal = Number(results.pop()) || 0;
    res.status(200).json({ page: pageVal, global: globalVal });
  } catch (e) {
    res.status(200).json({ page: 0, global: 0, error: String(e.message || e) });
  }
};
