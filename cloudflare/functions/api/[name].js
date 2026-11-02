// Cloudflare Pages Functions 轉接層：把 v7/api/ 的 Vercel 寫法（req/res）原封不動跑在 Cloudflare。
// 後端邏輯只改 v7/api/，這裡不放商業邏輯。資料仍存同一個 Upstash（y: 前綴），舊紀錄延續。
import chat from "../../../v7/api/chat.js";
import chatLog from "../../../v7/api/chat-log.js";
import statsAdmin from "../../../v7/api/stats-admin.js";
import view from "../../../v7/api/view.js";

const HANDLERS = { chat, "chat-log": chatLog, "stats-admin": statsAdmin, view };

export async function onRequest(context) {
  const handler = HANDLERS[context.params.name];
  if (!handler) return new Response("Not found", { status: 404 });

  const { request, env } = context;
  globalThis.process = globalThis.process || {};
  process.env = Object.assign(process.env || {}, env);

  const headers = {};
  request.headers.forEach((v, k) => { headers[k] = v; });
  const ip = request.headers.get("cf-connecting-ip") || "";
  if (ip) headers["x-forwarded-for"] = ip;

  let body;
  if (request.method !== "GET" && request.method !== "HEAD") {
    const text = await request.text();
    try { body = text ? JSON.parse(text) : {}; } catch { body = text; }
  }
  const url = new URL(request.url);
  const req = {
    method: request.method, headers, body, url: url.pathname + url.search,
    query: Object.fromEntries(url.searchParams), socket: { remoteAddress: ip },
  };

  let status = 200, out = null;
  const resHeaders = new Headers();
  const res = {
    setHeader(k, v) { resHeaders.set(k, v); return res; },
    status(c) { status = c; return res; },
    json(o) { resHeaders.set("Content-Type", "application/json; charset=utf-8"); out = JSON.stringify(o); return res; },
    send(s) { out = s; return res; },
    end(s) { if (s != null) out = s; return res; },
  };
  await handler(req, res);
  return new Response(status === 204 ? null : out, { status, headers: resHeaders });
}
