/**
 * 本機開發伺服器（只給本機預覽用，不會被部署）
 * -----------------------------------------------------------
 * 同時提供靜態檔與 /api/chat，行為比對 Vercel 上的樣子。
 *
 *   cd v7 && node _build/dev-server.js
 *
 * 想在本機真的跟 AI 對話（先確認金鑰不會被寫進任何檔案）：
 *   cd v7 && OPENAI_API_KEY='貼在這裡' node _build/dev-server.js
 * 沒帶金鑰時，對話會回「還沒接上」，這跟線上未設定時的行為一致。
 */
const http = require("http");
const fs = require("fs");
const path = require("path");

const ROOT = path.dirname(__dirname);
const PORT = process.env.PORT || 8899;
const chat = require(path.join(ROOT, "api", "chat.js"));

const MIME = {
  ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8", ".json": "application/json; charset=utf-8",
  ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
  ".svg": "image/svg+xml", ".webp": "image/webp", ".ico": "image/x-icon",
  ".txt": "text/plain; charset=utf-8", ".xml": "application/xml; charset=utf-8"
};

http.createServer(function (req, res) {
  const url = decodeURIComponent(req.url.split("?")[0]);

  if (url === "/api/chat") {
    let raw = "";
    req.on("data", function (c) { raw += c; });
    req.on("end", function () {
      try { req.body = JSON.parse(raw || "{}"); } catch (e) { req.body = {}; }
      res.status = function (code) { res.statusCode = code; return res; };
      res.json = function (obj) {
        res.setHeader("Content-Type", "application/json; charset=utf-8");
        res.end(JSON.stringify(obj));
      };
      Promise.resolve(chat(req, res)).catch(function (err) {
        console.error(err);
        if (!res.headersSent) { res.statusCode = 500; res.end('{"error":"dev"}'); }
      });
    });
    return;
  }

  let file = path.join(ROOT, url === "/" ? "index.html" : url);
  if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, "index.html");
  fs.readFile(file, function (err, buf) {
    if (err) { res.statusCode = 404; res.end("Not found"); return; }
    res.setHeader("Content-Type", MIME[path.extname(file).toLowerCase()] || "application/octet-stream");
    res.end(buf);
  });
}).listen(PORT, function () {
  console.log("預覽： http://localhost:" + PORT + "/");
  console.log("金鑰： " + (process.env.OPENAI_API_KEY ? "已帶入，可真的對話" : "未帶入，對話會回「還沒接上」"));
});
