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

  var PERSONAS = {
    secretary: {
      key: "secretary",
      name: "永力秘書",
      sub: "永力社 AI 助理",
      avatar: REL + "assets/img/yongli-secretary.png",
      accent: "#B8860B",
      greet: "你好，我是<strong>永力秘書</strong>。這個網站是台北永續影響力扶輪社的 2024-2026 永續影響力報告書，想知道什麼都可以問我。",
      quick: [
        "永力社在做什麼？",
        "這份報告書怎麼讀？",
        "SROI 是什麼意思？",
        "有哪些服務計畫？"
      ]
    },
    vicky: {
      key: "vicky",
      name: "李琪 Vicky",
      sub: "AI 分身 · 旅學女力",
      avatar: REL + "assets/img/members/vicky-ai-avatar.png",
      accent: "#C2477E",
      greet: "你好，我是 <strong>Vicky</strong> 的 AI 分身。這幾年我和一群女性在淡水的街巷裡走路、說故事，慢慢長出了一條女路，你想聊什麼都可以。",
      quick: [
        "陪力卡是什麼？",
        "淡水女路在做什麼？",
        "SROI 2.68 怎麼算出來的？",
        "旅學堂有哪些方案？"
      ],
      // 分身面板底下的次要入口：這位社友自己的網站
      siteUrl: "https://tamsuitraveler.vercel.app/",
      siteLabel: "順便看看旅學堂官網 ↗",
      switchLabel: "這一頁是",
      switchCta: "載入 Vicky 的 AI 分身"
    }
  };

  // ── 這一頁有沒有掛分身 ──
  var twinEl = document.querySelector("[data-secretary-twin]");
  var twinKey = twinEl ? twinEl.getAttribute("data-secretary-twin") : null;
  var twin = (twinKey && PERSONAS[twinKey]) ? PERSONAS[twinKey] : null;

  var current = PERSONAS.secretary;
  var history = [];          // [{role:'user'|'model', text}]
  var busy = false;

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
    '    <button class="ysec-iconbtn ysec-back" type="button" aria-label="回到永力秘書">←</button>',
    '    <img class="ysec-head-avatar" alt="" src="">',
    '    <div class="ysec-head-text">',
    '      <div class="ysec-head-name"></div>',
    '      <div class="ysec-head-sub"></div>',
    '    </div>',
    '    <button class="ysec-iconbtn ysec-close" type="button" aria-label="關閉">✕</button>',
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
    '    <div class="ysec-log" role="log" aria-live="polite"></div>',
    '    <div class="ysec-quick"></div>',
    '  </div>',
    '  <div class="ysec-foot">',
    '    <a class="ysec-sublink" href="#" target="_blank" rel="noopener"></a>',
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
  var log = $(".ysec-log"), quickBox = $(".ysec-quick");
  var input = $(".ysec-input"), form = $(".ysec-form");

  // ── 訊息 ──
  function addMsg(role, textOrHtml, isHtml) {
    var el = document.createElement("div");
    el.className = "ysec-msg ysec-msg-" + role;
    if (isHtml) el.innerHTML = textOrHtml; else el.textContent = textOrHtml;
    log.appendChild(el);
    log.scrollTop = log.scrollHeight;
    return el;
  }

  function renderQuick(persona) {
    quickBox.innerHTML = "";
    (persona.quick || []).forEach(function (q) {
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
    $(".ysec-head-avatar").alt = persona.name;
    $(".ysec-head-name").textContent = persona.name;
    $(".ysec-head-sub").textContent = persona.sub;

    log.innerHTML = "";
    addMsg("bot", persona.greet, true);
    renderQuick(persona);

    var sub = $(".ysec-sublink");
    if (persona.siteUrl) {
      sub.textContent = persona.siteLabel || "看看他的網站 ↗";
      sub.href = persona.siteUrl;
      sub.style.display = "block";
    } else {
      sub.style.display = "none";
    }

    input.placeholder = mode === "twin"
      ? ("跟 " + persona.name + " 聊聊")
      : "想問什麼都可以";

    $(".ysec-fab-avatar").src = persona.avatar;
    $(".ysec-fab-name").textContent = persona.name;
    $(".ysec-fab-hint").textContent =
      mode === "twin" ? "分身已載入" : (twin ? "可切換個人分身" : "有問題問我");
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

    var typing = addMsg("bot", '<span class="ysec-dots"><i></i><i></i><i></i></span>', true);
    typing.classList.add("ysec-typing");

    fetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ persona: current.key, messages: history })
    })
      .then(function (r) { return r.json().catch(function () { return {}; }); })
      .then(function (data) {
        var reply = (data && data.reply) ||
          "對話功能還沒接上，你可以先看看這一頁的內容。";
        typing.classList.remove("ysec-typing");
        typing.textContent = reply;
        if (data && data.reply && !data.error) history.push({ role: "model", text: reply });
        log.scrollTop = log.scrollHeight;
      })
      .catch(function () {
        typing.classList.remove("ysec-typing");
        typing.textContent = "對話功能還沒接上，你可以先看看這一頁的內容。";
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
    $(".ysec-switch-avatar").alt = twin.name;
    $(".ysec-switch-label").textContent = twin.switchLabel || "這一頁是";
    $(".ysec-switch-name").textContent = twin.name;
    $(".ysec-switch-btn").textContent = twin.switchCta || ("載入 " + twin.name + " 的 AI 分身");
    $(".ysec-switch-btn").addEventListener("click", function () {
      load(twin, "twin");
      input.focus();
    });
  }
  $(".ysec-back").addEventListener("click", function () {
    load(PERSONAS.secretary, "secretary");
  });

  // ── 開關 ──
  function setOpen(open) {
    root.setAttribute("data-open", open ? "true" : "false");
    fab.setAttribute("aria-expanded", open ? "true" : "false");
    if (open) input.focus(); else fab.focus();
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

  load(PERSONAS.secretary, "secretary");
  document.body.appendChild(root);
})();
