/* ===========================================================
   永力秘書（Yongli Secretary）— 站內 AI 對話元件
   -----------------------------------------------------------
   兩種狀態：
     1. 客服狀態（預設，所有中文頁）：聊永力社、聊永續影響力報告書
     2. 分身狀態（個人頁）：載入該位社友的 AI 分身，換人格繼續聊

   掛載：由 _build/templates/footer.zh.html 注入，跑 build 全站生效。
     <script src="{{REL}}assets/js/yongli-secretary.js" data-rel="{{REL}}" defer></script>

   個人頁要開放分身，在該頁任一元素加上： data-secretary-twin="vicky"
   值對應下方 PERSONAS 的 key，也對應後端 api/chat.js 的 persona。

   對話後端：POST {REL}api/chat（Vercel Serverless Function）
   後端沒設好 API 金鑰時會回可讀的說明，前端照樣不會壞。
   =========================================================== */
(function () {
  "use strict";

  var script = document.currentScript ||
    document.querySelector('script[src*="yongli-secretary.js"]');
  var REL = (script && script.getAttribute("data-rel")) || "";
  var API = REL + "api/chat";
  var LANG = (document.documentElement.getAttribute("lang") || "zh")
    .toLowerCase().indexOf("en") === 0 ? "en" : "zh";
  function t(v) {
    return (v && typeof v === "object" && !Array.isArray(v)) ? (v[LANG] || v.zh) : v;
  }

  var PERSONAS = {
    secretary: {
      key: "secretary",
      name: { zh: "永力秘書", en: "Yongli Secretary" },
      sub: { zh: "永力社 AI 助理", en: "Club AI assistant" },
      avatar: REL + "assets/img/yongli-secretary.png",
      accent: "#B8860B",
      greet: {
        zh: "你好，我是<strong>永力秘書</strong>。這個網站是台北永續影響力扶輪社的 2024-2026 永續影響力報告書，想知道什麼都可以問我。",
        en: "Hello, I am the <strong>Yongli Secretary</strong>. This site is the 2024-2026 Sustainability Impact Report of the Rotary Club of Taipei Sustainable Impact. Ask me anything about it."
      },
      quick: {
        zh: ["永力社在做什麼？", "這份報告書怎麼讀？", "SROI 是什麼意思？", "有哪些服務計畫？"],
        en: ["What does the club do?", "How do I read this report?", "What does SROI mean?", "What service projects are there?"]
      }
    },
    vicky: {
      key: "vicky",
      name: { zh: "李琪 Vicky", en: "Vicky Lee" },
      sub: { zh: "AI 分身 · 旅學女力", en: "AI twin · Tamsui Women's Path" },
      avatar: REL + "assets/img/members/vicky-ai-avatar.png",
      accent: "#C2477E",
      greet: {
        zh: "你好，我是 <strong>Vicky</strong> 的 AI 分身。這幾年我和一群女性在淡水的街巷裡走路、說故事，慢慢長出了一條女路，你想聊什麼都可以。",
        en: "Hello, I am <strong>Vicky</strong>'s AI twin. Over the past few years I have walked the lanes of Tamsui with a group of women, telling stories, and slowly a women's path grew out of it. Ask me anything."
      },
      quick: {
        zh: ["陪力卡是什麼？", "淡水女路在做什麼？", "SROI 2.68 怎麼算出來的？", "旅學堂有哪些方案？"],
        en: ["What are the companionship cards?", "What is the Tamsui Women's Path?", "How was the SROI of 2.68 calculated?", "What does Tamsui Traveler offer?"]
      },
      switchLabel: { zh: "這一頁是", en: "This page is about" },
      switchCta: { zh: "載入 Vicky 的 AI 分身", en: "Load Vicky's AI twin" }
    }
  };

  var UI = {
    ask: { zh: "想問什麼都可以", en: "Ask me anything" },
    askTwin: { zh: "跟 ", en: "Chat with " },
    askTwinTail: { zh: " 聊聊", en: "" },
    hintDefault: { zh: "有問題問我", en: "Ask me anything" },
    hintTwinAvailable: { zh: "可切換個人分身", en: "AI twin available" },
    hintTwinLoaded: { zh: "分身已載入", en: "AI twin loaded" },
    offline: {
      zh: "對話功能還沒接上，你可以先看看這一頁的內容。",
      en: "The chat service is not connected yet. Please browse this page in the meantime."
    }
  };

  // ── 這一頁有沒有掛分身 ──
  var twinEl = document.querySelector("[data-secretary-twin]");
  var twinKey = twinEl ? twinEl.getAttribute("data-secretary-twin") : null;
  var twin = (twinKey && PERSONAS[twinKey]) ? PERSONAS[twinKey] : null;

  var current = PERSONAS.secretary;
  var history = [];          // [{role:'user'|'model', text}]
  var busy = false;

  var STORE = "ysec-state";
  function save() {
    try {
      localStorage.setItem(STORE, JSON.stringify({
        persona: current.key,
        mode: root.getAttribute("data-mode"),
        open: root.getAttribute("data-open") === "true",
        history: history.slice(-20)
      }));
    } catch (e) {}
  }
  function restore() {
    try { return JSON.parse(localStorage.getItem(STORE) || "null"); }
    catch (e) { return null; }
  }

  // ── DOM ──
  var root = document.createElement("div");
  root.className = "ysec";
  root.setAttribute("data-open", "false");
  root.setAttribute("data-mode", "secretary");
  root.setAttribute("data-has-twin", twin ? "true" : "false");
  if (twin) root.style.setProperty("--ysec-twin-accent", twin.accent);

  root.innerHTML = [
    '<div class="ysec-panel" role="dialog" aria-modal="false" aria-label="永力秘書">',
    '  <div class="ysec-head">',
    '    <div class="ysec-head-inner">',
    '      <img class="ysec-head-avatar" alt="" src="">',
    '      <div class="ysec-head-text">',
    '        <div class="ysec-head-name"></div>',
    '        <div class="ysec-head-sub"></div>',
    '      </div>',
    '      <button class="ysec-iconbtn ysec-reset" type="button" aria-label="重新開始這段對話">↻</button>',
    '      <button class="ysec-iconbtn ysec-zoom" type="button" aria-label="放大對話視窗" aria-pressed="false">⤢</button>',
    '      <button class="ysec-iconbtn ysec-close" type="button" aria-label="關閉">✕</button>',
    '    </div>',
    '  </div>',
    '  <div class="ysec-body">',
    '    <div class="ysec-switch">',
    '      <div class="ysec-switch-row">',
    '        <img class="ysec-switch-avatar" alt="" src="">',
    '        <div>',
    '          <div class="ysec-switch-label"></div>',
    '          <div class="ysec-switch-name"></div>',
    '        </div>',
    '      </div>',
    '      <button class="ysec-btn ysec-switch-btn" type="button"></button>',
    '    </div>',
    '    <div class="ysec-log"></div>',
    '  </div>',
    '  <div class="ysec-foot">',
    '    <form class="ysec-form">',
    '      <label class="ysec-sr" for="ysec-input">想問什麼</label>',
    '      <input class="ysec-input" id="ysec-input" type="text" autocomplete="off"',
    '             placeholder="想問什麼都可以" maxlength="500">',
    '      <button class="ysec-send" type="submit" aria-label="送出">↑</button>',
    '    </form>',
    '  </div>',
    '</div>',
    '<button class="ysec-fab" type="button" aria-expanded="false">',
    '  <span class="ysec-fab-dot"></span>',
    '  <img class="ysec-fab-avatar" alt="" src="">',
    '  <span class="ysec-fab-text">',
    '    <span class="ysec-fab-name"></span>',
    '    <span class="ysec-fab-hint"></span>',
    '  </span>',
    '</button>'
  ].join("");

  var $ = function (s) { return root.querySelector(s); };
  var fab = $(".ysec-fab"), panel = $(".ysec-panel");
  var log = $(".ysec-log");
  var quickBox = document.createElement("div");
  quickBox.className = "ysec-quick";
  var input = $(".ysec-input"), form = $(".ysec-form");

  // ── 訊息 ──
  function addMsg(role, textOrHtml, isHtml) {
    var el = document.createElement("div");
    el.className = "ysec-msg ysec-msg-" + role;
    if (role === "bot") el.setAttribute("aria-live", "polite");
    if (isHtml) el.innerHTML = textOrHtml; else el.textContent = textOrHtml;
    log.appendChild(el);
    log.scrollTop = log.scrollHeight;
    return el;
  }

  function renderQuick(persona) {
    quickBox.innerHTML = "";
    log.appendChild(quickBox);
    (t(persona.quick) || []).forEach(function (q) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "ysec-chip";
      b.textContent = q;
      b.addEventListener("click", function () { send(q); });
      quickBox.appendChild(b);
    });
    quickBox.style.display = "";
  }

  // ── 切換人格：換頭、清對話、重新開場 ──
  function load(persona, mode) {
    current = persona;
    history = [];
    root.setAttribute("data-mode", mode);

    $(".ysec-head-avatar").src = persona.avatar;
    $(".ysec-head-avatar").alt = t(persona.name);
    $(".ysec-head-name").textContent = t(persona.name);
    $(".ysec-head-sub").textContent = t(persona.sub);

    log.innerHTML = "";
    addMsg("bot", t(persona.greet), true);
    renderQuick(persona);

    input.placeholder = mode === "twin"
      ? (t(UI.askTwin) + t(persona.name) + t(UI.askTwinTail))
      : t(UI.ask);

    $(".ysec-fab-avatar").src = persona.avatar;
    $(".ysec-fab-name").textContent = t(persona.name);
    $(".ysec-fab-hint").textContent = t(
      mode === "twin" ? UI.hintTwinLoaded : (twin ? UI.hintTwinAvailable : UI.hintDefault));
  }

  // ── 送出 ──
  function send(text) {
    text = String(text || "").trim();
    if (!text || busy) return;
    busy = true;
    quickBox.style.display = "none";
    input.value = "";
    addMsg("me", text);
    history.push({ role: "user", text: text });
    save();

    var typing = addMsg("bot", '<span class="ysec-dots"><i></i><i></i><i></i></span>', true);
    typing.classList.add("ysec-typing");

    fetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ persona: current.key, messages: history, lang: LANG })
    })
      .then(function (r) { return r.json().catch(function () { return {}; }); })
      .then(function (data) {
        var reply = (data && data.reply) || t(UI.offline);
        typing.classList.remove("ysec-typing");
        typing.textContent = reply;
        if (data && data.reply && !data.error) history.push({ role: "model", text: reply });
        save();
        log.scrollTop = log.scrollHeight;
      })
      .catch(function () {
        typing.classList.remove("ysec-typing");
        typing.textContent = t(UI.offline);
      })
      .then(function () { busy = false; input.focus(); });
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    send(input.value);
  });

  // ── 分身切換 ──
  if (twin) {
    $(".ysec-switch-avatar").src = twin.avatar;
    $(".ysec-switch-avatar").alt = t(twin.name);
    $(".ysec-switch-label").textContent = t(twin.switchLabel);
    $(".ysec-switch-name").textContent = t(twin.name);
    $(".ysec-switch-btn").textContent = t(twin.switchCta);
    $(".ysec-switch-btn").addEventListener("click", function () {
      load(twin, "twin");
      save();
      input.focus();
    });
  }

  // ── 重置：退出分身、清空對話，回到剛進網頁時的狀態 ──
  $(".ysec-reset").addEventListener("click", function () {
    load(PERSONAS.secretary, "secretary");
    save();
    input.focus();
  });

  // ── 放大／縮小 ──
  var zoomBtn = $(".ysec-zoom");
  function setBig(big) {
    root.setAttribute("data-size", big ? "large" : "normal");
    zoomBtn.setAttribute("aria-pressed", big ? "true" : "false");
    zoomBtn.setAttribute("aria-label", big ? "縮小對話視窗" : "放大對話視窗");
    zoomBtn.textContent = big ? "⤡" : "⤢";
    try { localStorage.setItem("ysec-size", big ? "large" : "normal"); } catch (e) {}
    log.scrollTop = log.scrollHeight;
  }
  zoomBtn.addEventListener("click", function () {
    setBig(root.getAttribute("data-size") !== "large");
  });
  var savedSize = "normal";
  try { savedSize = localStorage.getItem("ysec-size") || "normal"; } catch (e) {}
  setBig(savedSize === "large");

  // ── 開關 ──
  function setOpen(open) {
    root.setAttribute("data-open", open ? "true" : "false");
    fab.setAttribute("aria-expanded", open ? "true" : "false");
    if (open) input.focus(); else fab.focus();
    save();
  }
  fab.addEventListener("click", function () {
    setOpen(root.getAttribute("data-open") !== "true");
  });
  $(".ysec-close").addEventListener("click", function () { setOpen(false); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && root.getAttribute("data-open") === "true") setOpen(false);
  });

  // ── 頁面上的入口：點了直接開面板並載入指定人格 ──
  Array.prototype.forEach.call(
    document.querySelectorAll("[data-secretary-open]"),
    function (el) {
      el.addEventListener("click", function (e) {
        e.preventDefault();
        var key = el.getAttribute("data-secretary-open");
        var p = PERSONAS[key];
        if (p) load(p, key === "secretary" ? "secretary" : "twin");
        setOpen(true);
      });
    }
  );

  // ── 啟動：還原上次的人格與對話，沒有就從永力秘書開始 ──
  var prev = restore();
  var startPersona = (prev && PERSONAS[prev.persona]) || PERSONAS.secretary;
  var startMode = (prev && prev.mode === "twin" && startPersona.key !== "secretary") ? "twin" : "secretary";
  load(startPersona, startMode);

  if (prev && prev.history && prev.history.length) {
    quickBox.style.display = "none";
    prev.history.forEach(function (m) {
      addMsg(m.role === "user" ? "me" : "bot", m.text);
    });
    history = prev.history.slice();
  }

  document.body.appendChild(root);
  if (prev && prev.open) setOpen(true);
})();
