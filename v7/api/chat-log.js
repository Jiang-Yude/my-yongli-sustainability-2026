// 永力秘書聊天記錄：訪客跟 AI 助理聊了什麼，後台可查。
// 資料存 Upstash Redis，跟 view.js 同一套環境變數；每月一個 list，各留最近 20000 筆。
//
// ⚠️ 與知識官網共用 Redis 實例，本站所有 key 一律加 `y:` 前綴。
//
// POST {vid, sid, role, text, page, persona}
//   vid=瀏覽器識別  sid=單次瀏覽識別  role=user|bot  text=訊息  page=所在頁面路徑
//   persona=跟誰講話（secretary 永力秘書／vicky 社友分身）
//   不做會員、不追個人軌跡，只做「大家都問什麼」統計。
//   防灌爆：同一 IP 每分鐘最多 60 筆，超過丟棄。
//
// 讀取一律走 /api/stats-admin（要密碼），本端點只寫不讀。

const P = 'y:';
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

function taipeiStamp(d = new Date()) {
  return new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Asia/Taipei', year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', hour12: false,
  }).format(d); // "YYYY-MM-DD, HH:MM"
}

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  if (req.method === 'OPTIONS') { res.status(204).end(); return; }
  if (req.method !== 'POST') { res.status(405).json({ error: 'POST only' }); return; }
  if (!URL() || !TOKEN()) { res.status(200).json({ ok: false, note: 'storage not configured' }); return; }

  let body = req.body;
  if (typeof body === 'string') { try { body = JSON.parse(body); } catch { body = {}; } }
  body = body || {};

  const text = String(body.text || '').trim().slice(0, 500);
  if (!text) { res.status(200).json({ ok: false, note: 'empty' }); return; }
  const ua = String(req.headers['user-agent'] || '');
  if (/bot|crawl|spider|slurp|headless|preview|facebookexternalhit|monitor|lighthouse/i.test(ua)) {
    res.status(200).json({ ok: false, note: 'bot skipped' }); return;
  }

  const ip = String(req.headers['x-forwarded-for'] || '').split(',')[0].trim() || 'na';
  try {
    const rateKey = `${P}rate:${ip}:${Math.floor(Date.now() / 60000)}`;
    const rate = await pipe([['INCR', rateKey], ['EXPIRE', rateKey, 90]]);
    if (Number(rate[0] && rate[0].result) > 60) {
      res.status(429).json({ ok: false, note: 'rate limited' }); return;
    }
  } catch (e) { /* 限流壞了不擋記錄 */ }

  const stamp = taipeiStamp();
  const month = stamp.slice(0, 7);
  const entry = JSON.stringify({
    t: stamp.replace(', ', ' '),
    vid: String(body.vid || 'na').slice(0, 24),
    sid: String(body.sid || 'na').slice(0, 24),
    persona: body.persona ? String(body.persona).slice(0, 20) : undefined,
    role: body.role === 'bot' ? 'bot' : 'user',
    text,
    page: String(body.page || '').slice(0, 120),
  });

  try {
    await pipe([
      ['LPUSH', `${P}chat:${month}`, entry],
      ['LTRIM', `${P}chat:${month}`, 0, 19999],
    ]);
    res.status(200).json({ ok: true });
  } catch (e) {
    res.status(200).json({ ok: false, error: String(e.message || e) });
  }
};
