/**
 * 永力秘書 / 社友 AI 分身 — 對話後端（Vercel Serverless Function）
 * -----------------------------------------------------------------
 * 前端： POST /api/chat  { persona: "secretary" | "vicky", messages: [{role,text}] }
 * 回傳： { reply: "..." }
 *
 * 需要的環境變數（在 Vercel 專案 → Settings → Environment Variables 設定，
 * 絕對不要寫進程式碼或 commit）：
 *   OPENAI_API_KEY  必填
 *   OPENAI_MODEL    選填，預設 gpt-5.6-luna；換模型只改這個變數
 *
 * 知識來源：./_knowledge.js（由 _build/twin_knowledge.py 產生）
 * 來源網頁更新後要重跑：cd v7 && python3 _build/twin_knowledge.py
 */
const KNOWLEDGE = require("./_knowledge.js");

const PERSONAS = {
  secretary: {
    label: "永力秘書",
    prompt: [
      "你是「永力秘書」，台北永續影響力扶輪社（永力社）2024-2026 永續影響力報告書網站的 AI 助理。",
      "你的工作是幫訪客理解這個社在做什麼、報告書怎麼讀、五大服務與服務計畫的內容。",
      "語氣親切、專業、簡潔，用繁體中文回答，一般回答控制在 200 字內。",
      "只根據下面提供的網站資料回答。資料裡沒有的事情就直說「這個報告書裡沒有寫到」，",
      "並指引對方可以去看網站的哪一區，不要自己編造數字、人名、日期或成果。",
      "你是 AI 助理，不是社的代表，不能代替社或任何社友做出承諾、報價或答應合作。"
    ].join("\n")
  },
  vicky: {
    label: "李琪 Vicky 的 AI 分身",
    prompt: [
      "你是李琪 Vicky 的 AI 分身。Vicky 是旅學堂工作室創辦人、新北市社區旅學關懷協會理事長，",
      "也是台北永續影響力扶輪社的社區服務主委，長年在淡水做女性培力與地方走讀。",
      "用 Vicky 的第一人稱說話，語氣溫暖、實在、不誇大，用繁體中文，一般回答控制在 200 字內。",
      "只根據下面提供的資料回答，那是她的人物誌與旅學堂官網內容。",
      "資料裡沒有的就老實說「這個我這邊沒有資料」，不要編造數字、學員故事、行程或價格。",
      "如果對方問到報價、合作細節、要約時間，請說明你是 AI 分身不能代她決定，",
      "請對方透過旅學堂官網或協會的聯絡管道找本人。",
      "聊到淡水女路、旅學堂的方案、活動或報名時，在回答的最後自然帶一句邀請，",
      "像是「順便看看旅學堂官網」，並附上 https://tamsuitraveler.vercel.app/ 。",
      "不用每次都講，該給的時候給就好，也不要寫成生硬的連結列表。",
      "第一次回答時如果對方沒察覺，可以自然提一句你是 Vicky 的 AI 分身。"
    ].join("\n")
  }
};

const MAX_TURNS = 20;        // 一次最多帶幾則歷史
const MAX_CHARS = 1500;      // 單則訊息長度上限

/* ── 用量上限（2026-08-31 江江訂）──────────────────────────────
   單一 IP：每分鐘 20 次、每天 100 次
   全站   ：每天 2000 次
   計數放在函式執行個體的記憶體裡，零外部依賴。
   ⚠️ 誠實標註：Vercel 會視流量開多個執行個體，各自計數；冷啟動也會歸零。
   所以這是「擋掉單機猛打」的護欄，不是精準配額。要精準就得接 KV／Redis。
   ──────────────────────────────────────────────────────────── */
const LIMITS = { ipPerMin: 20, ipPerDay: 100, sitePerDay: 2000 };
const hits = new Map();      // key -> [timestamps]
let siteDay = { day: "", count: 0 };

function clientIp(req) {
  const fwd = req.headers["x-forwarded-for"];
  if (fwd) return String(fwd).split(",")[0].trim();
  return req.headers["x-real-ip"] || req.socket && req.socket.remoteAddress || "unknown";
}

function overLimit(ip, now) {
  const today = new Date(now).toISOString().slice(0, 10);
  if (siteDay.day !== today) siteDay = { day: today, count: 0 };
  if (siteDay.count >= LIMITS.sitePerDay) return "site_daily";

  const list = (hits.get(ip) || []).filter(function (t) { return now - t < 86400000; });
  if (list.length >= LIMITS.ipPerDay) { hits.set(ip, list); return "ip_daily"; }
  if (list.filter(function (t) { return now - t < 60000; }).length >= LIMITS.ipPerMin) {
    hits.set(ip, list);
    return "ip_minute";
  }

  list.push(now);
  hits.set(ip, list);
  siteDay.count += 1;
  if (hits.size > 5000) hits.clear();   // 記憶體保險，避免無限成長
  return null;
}

const LIMIT_REPLY = {
  ip_minute: "你問得有點快，休息一下下再問我好嗎？",
  ip_daily: "今天聊得很多了，明天再來找我聊吧。",
  site_daily: "今天問的人比較多，已經到今天的上限了，明天再來吧。"
};

module.exports = async function handler(req, res) {
  if (req.method !== "POST") {
    res.status(405).json({ error: "只接受 POST" });
    return;
  }

  var body = req.body;
  if (typeof body === "string") {
    try { body = JSON.parse(body); } catch (e) { body = {}; }
  }
  body = body || {};

  var persona = PERSONAS[body.persona] ? body.persona : "secretary";
  var messages = Array.isArray(body.messages) ? body.messages.slice(-MAX_TURNS) : [];
  if (!messages.length) {
    res.status(400).json({ error: "沒有收到訊息" });
    return;
  }

  var limited = overLimit(clientIp(req), Date.now());
  if (limited) {
    res.status(429).json({ error: limited, reply: LIMIT_REPLY[limited] });
    return;
  }

  var apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    res.status(503).json({
      error: "not_configured",
      reply: "對話功能還沒接上（後台尚未設定 API 金鑰），你可以先看看這一頁的內容。"
    });
    return;
  }

  var model = process.env.OPENAI_MODEL || "gpt-5.6-luna";
  var lang = body.lang === "en" ? "en" : "zh";
  var kb = (lang === "en" && KNOWLEDGE[persona + "_en"]) || KNOWLEDGE[persona] || "（無資料）";
  var systemText = PERSONAS[persona].prompt +
    (lang === "en"
      ? "\n\nThe visitor is reading the English edition of this site. Reply in English, keeping the same persona, tone limits and guardrails."
      : "") +
    "\n\n===== 以下是你能依據的資料 =====\n" + kb;

  var chatMessages = [{ role: "system", content: systemText }].concat(
    messages.map(function (m) {
      return {
        role: m.role === "model" || m.role === "assistant" ? "assistant" : "user",
        content: String(m.text || "").slice(0, MAX_CHARS)
      };
    })
  );

  try {
    var r = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + apiKey
      },
      body: JSON.stringify({ model: model, messages: chatMessages })
    });

    var data = await r.json();
    if (!r.ok) {
      console.error("OpenAI API 回錯：", r.status, JSON.stringify(data).slice(0, 500));
      res.status(502).json({
        error: "upstream",
        detail: (data && data.error && data.error.message) || ("HTTP " + r.status),
        reply: "我這邊剛剛沒接上，麻煩再問一次。"
      });
      return;
    }

    var choice = data && data.choices && data.choices[0];
    var reply = ((choice && choice.message && choice.message.content) || "").trim();

    if (!reply) {
      reply = "這個問題我這邊沒有足夠的資料可以回答，你可以看看網站上其他段落。";
    }
    res.status(200).json({ reply: reply, persona: persona });
  } catch (err) {
    console.error("chat handler error:", err);
    res.status(500).json({ error: "server", reply: "我這邊出了點狀況，麻煩再試一次。" });
  }
};
