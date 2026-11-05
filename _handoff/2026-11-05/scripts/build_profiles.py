#!/usr/bin/env python3
"""產生永力社社友人物誌：江昱德、Dr. Ivy。版型對齊 rctsi.3481.org/profiles/*。"""
import json, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent / "profiles"
EXTRA_CSS = (ROOT / "assets/css/_profile-extras.css").read_text()

ICON_WEB = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm6.93 6h-2.95a15.65 15.65 0 0 0-1.38-3.56A8.03 8.03 0 0 1 18.93 8zM12 4c.83 1.2 1.5 2.59 1.91 4h-3.82c.41-1.41 1.08-2.8 1.91-4zM4.26 14C4.1 13.36 4 12.69 4 12s.1-1.36.26-2h3.38c-.08.66-.14 1.32-.14 2s.06 1.34.14 2H4.26zm.82 2h2.95c.32 1.25.78 2.45 1.38 3.56A7.99 7.99 0 0 1 5.08 16zm2.95-8H5.08a7.99 7.99 0 0 1 4.33-3.56A15.65 15.65 0 0 0 8.03 8zM12 20c-.83-1.2-1.5-2.59-1.91-4h3.82c-.41 1.41-1.08 2.8-1.91 4zm2.34-6H9.66c-.09-.66-.16-1.32-.16-2s.07-1.34.16-2h4.68c.09.66.16 1.32.16 2s-.07 1.34-.16 2zm.25 5.56c.6-1.11 1.06-2.31 1.38-3.56h2.95a7.99 7.99 0 0 1-4.33 3.56zM16.36 14c.08-.66.14-1.32.14-2s-.06-1.34-.14-2h3.38c.16.64.26 1.31.26 2s-.1 1.36-.26 2h-3.38z"></path></svg>'
ICON_PERSON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm0 4a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zm0 14a8 8 0 0 1-6-2.7c.04-2.7 5.33-4 6-4s5.96 1.3 6 4A8 8 0 0 1 12 20z"></path></svg>'


def chip(platform, url, label):
    ico = ICON_WEB if platform == "web" else ICON_PERSON
    return (f'<a class="social-chip" data-platform="{platform}" href="{url}" target="_blank" rel="noopener" '
            f'aria-label="{label}"> <span class="ico">{ico}</span> <span class="label">{label}</span> <span class="arr">→</span> </a>')


def page(p):
    url = f"https://rctsi.3481.org/profiles/{p['slug']}"
    title = f"{p['name']}｜{p['title_tag']} — 永力扶輪社 2024-2026 永續報告"
    img_abs = f"https://rctsi.3481.org/assets/img/members/{p['img']}"
    person_ld = {"@context": "https://schema.org", "@type": "Person", "name": p["name"], "jobTitle": p["job"],
                 "url": url, "memberOf": {"@type": "Organization", "name": "Rotary Club of Taipei Sustainable Impact",
                                          "alternateName": "台北永續影響力扶輪社", "url": "https://rctsi.3481.org/"},
                 "description": p["one_liner"], "image": img_abs, "sameAs": [c[1] for c in p["chips"]]}
    sdg = " ".join(f'<span class="sdg-chip sdg-chip-{n}">{n}</span>' for n in p["sdgs"])
    meta = " <span>·</span> ".join(f"<span>{m}</span>" for m in p["meta"])
    chips = " ".join(chip(*c) for c in p["chips"])
    radar = p["radar"]
    stats = " ".join(
        f'<div class="stat-card"> <div><span class="stat-num">{n}</span><span class="stat-unit">{u}</span></div> '
        f'<p class="stat-label">{l}</p> <p class="stat-detail">{d}</p> </div>' for n, u, l, d in p["stats"])
    review = f'''<!-- REVIEW-BANNER:START 上線前整段刪除 -->
<div style="background:#FFF6DC;border-bottom:1px solid #E8D49A;padding:12px 16px;font-size:14px;line-height:1.7;color:#5C4A12;">
<div class="container"><strong style="font-weight:600;">草稿・待本人確認</strong>：{p['review_note']}</div></div>
<!-- REVIEW-BANNER:END -->'''
    return f'''<!DOCTYPE html><html lang="zh-Hant"> <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{html.escape(title)}</title><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;600;700&family=Noto+Serif+TC:wght@500;600;700&display=swap" rel="stylesheet"><link rel="stylesheet" href="../assets/css/common.css?v=9"><!--SITE-HEAD:START-->
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="台北永續影響力扶輪社｜永續影響力報告書">
<meta property="og:locale" content="zh_TW">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:url" content="{url}">
<meta name="description" content="{html.escape(p['description'])}">
<meta property="og:description" content="{html.escape(p['description'])}">
<meta property="og:image" content="{img_abs}">
<meta name="twitter:card" content="summary">
<script type="application/ld+json">{json.dumps(person_ld, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps({"@context":"https://schema.org","@type":"WebPage","name":title,"url":url,"inLanguage":"zh-Hant","isPartOf":{"@type":"WebSite","name":"台北永續影響力扶輪社｜永續影響力報告書","url":"https://rctsi.3481.org/"},"about":{"@type":"Person","name":p["name"]},"publisher":{"@type":"Organization","name":"Rotary Club of Taipei Sustainable Impact","alternateName":"台北永續影響力扶輪社","url":"https://rctsi.3481.org/"},"image":img_abs,"description":p["description"],"dateModified":"2026-11-05"}, ensure_ascii=False)}</script>
<!--SITE-HEAD:END-->
<style>{EXTRA_CSS}
.profile-hero .avatar-lg{{background-size:cover;background-position:{p['avatar_pos']};}}
</style>
</head> <body> <!--SITE-HEADER:START-->
<header class="topbar"> <div class="inner"> <a class="brand" href="../index.html" aria-label="回首頁"> <span class="mark">永</span>永續影響力扶輪社年度報告書 </a> <button class="nav-toggle" aria-label="開啟選單" aria-expanded="false"> <span></span><span></span><span></span> </button> <nav> <a href="../index.html#intro">關於永力社</a><a href="../index.html#impact-report">影響力報告</a><a href="../index.html#five-service">五大服務</a><a href="../index.html#members">社友介紹</a><a href="../index.html#impact-hub">服務計畫</a> </nav> </div> </header>
<!--SITE-HEADER:END-->
{review}
<section class="profile-hero"> <div class="container"> <div class="layout"> <div class="avatar-lg" style="background-image:url(../assets/img/members/{p['img']})"></div> <div> <span class="role-tag">{p['role_tag']}</span> <h1>{p['name']}</h1> <div class="theme">{p['theme']}</div> <div class="meta-row"> {meta} </div> <div class="tag-row" style="margin-top:14px;"> {sdg} </div> </div> <div class="hero-tags"> <div class="social-chips"> {chips} </div> </div> </div> </div> </section>

<section class="profile-section dashboard-section"> <div class="container"> <h2>影響力指標</h2> <p class="section-meta">PERSONAL IMPACT INDEX</p> <div class="dashboard-card"> <div class="dashboard-top" style="display:block;"> <div class="dashboard-intro"> <h3>{p['dash_h3']}</h3> <p>{p['dash_p']}</p> <span class="source">{p['dash_source']}</span> </div> </div> <div class="impact-stats-grid"> {stats} </div> </div> </div> </section>

{p['body']}

<div class="container"> <nav class="profile-nav"> <a href="{p['prev'][0]}">← 上一位：{p['prev'][1]}</a> <a class="home" href="../index.html#members">回社友列表</a> <a href="{p['next'][0]}">下一位：{p['next'][1]} →</a> </nav> </div>
<!--SITE-FOOTER:START-->
<footer> <div class="container"> <div> <p class="foot-title">台北永續影響力扶輪社</p> <p>Rotary Club of Taipei Sustainable Impact</p> <p>以職業服務社會 · 用影響力衡量價值</p> <p style="margin-top:14px;font-size:14px;color:var(--ink-mute);"> 本報告書由永力社報告書工作小組製作<br> 主筆：陳明勇 Vincent · 工作組：CP 林學賢、艾筆團隊<br> 知識架構、網頁設計：江昱德<br> </p> </div> <div> <p class="foot-title">章節導覽</p> <ul> <li><a href="../index.html#intro">關於永力社</a></li><li><a href="../index.html#impact-report">影響力報告</a></li><li><a href="../index.html#five-service">五大服務</a></li><li><a href="../index.html#members">社友介紹</a></li><li><a href="../index.html#impact-hub">服務計畫</a></li> </ul> </div> <div> <p class="foot-title">版本資訊</p> <ul> <li>2024-2026 永續影響力報告書</li> <li>2026 年 5 月發行</li> <li>持續更新中</li> <li class="license-li"> 本報告書採用 <strong>CC BY-NC-ND 4.0</strong> 授權<br> <span class="license-rules">可分享 · 必須標示來源 · 不得商用 · 不得改作</span> </li> </ul> </div> <div class="copyright">© 2024-2026 台北永續影響力扶輪社 3481</div> </div> </footer>
<!--SITE-FOOTER:END-->
</body></html>
'''


def sec(h2, inner):
    return f'<section class="profile-section"> <div class="container"> <h2>{h2}</h2> {inner} </div> </section>'


def callout(label, text, gold=False):
    style = ' style="border-left-color:var(--gold);background:linear-gradient(135deg, var(--bg-card) 0%, #FCF7E9 100%);"' if gold else ""
    lab = f'<div class="label">{label}</div> ' if label else ""
    fs = "1.15rem;font-family:'Noto Serif TC',serif" if gold else "1.05rem"
    return f'<div class="callout"{style}> {lab}<p style="margin:0;font-size:{fs};">{text}</p> </div>'


def grid(cells):
    return '<div class="impact-grid"> ' + " ".join(
        f'<div class="impact-cell"><div class="label">{a}</div><div class="val">{b}</div></div>' for a, b in cells) + ' </div>'


def ul(items):
    return "<ul> " + " ".join(f"<li>{i}</li>" for i in items) + " </ul>"


# ───────────────────────── 江昱德 ─────────────────────────
jiang_body = "\n".join([
    sec("開場畫面｜頁尾的那一行小字", "".join([
        "<p>翻到這本報告書的最底部，頁尾有一行很小的字：「知識架構、網頁設計：江昱德」。整本報告書裡，社友的故事、服務計畫的數字、影響力地圖，都排在最前面；他把自己的名字放在最後一行。</p>",
        "<p>這個位置剛好說明了他的工作方式。他很少站在台前說自己做了什麼，他在意的是：別人的故事有沒有被整理好，整理好之後，能不能被找到、被讀懂、被傳下去。</p>",
        callout("那一行字背後", "一份報告書印完就結束了；一個知識架構搭起來，社友的故事可以一年一年接著長。"),
    ])),
    sec("專業底色｜二十年在鏡頭後面看見的事", "".join([
        "<p>在成為「江江教練」之前，他拿了二十年的相機。拍公益組織、文教協會、在地組織的活動紀錄，拍紀錄片，也拍很多沒有被寫進新聞的現場。</p>",
        "<p>鏡頭讓他看見兩條知識流動的路：對外，組織怎麼傳遞價值、怎麼倡議與宣導；對內，組織怎麼帶志工、怎麼培訓夥伴、怎麼把理念交給下一個人。很多最珍貴的東西，都留在資深的人腦袋裡，從來沒有被寫下來。</p>",
        "<p>工具一直在換，從攝影機、剪輯軟體到今天的 AI。他做的事情沒有換過：看見、整理、復現。</p>",
        grid([("過去的工具", "相機與剪輯軟體"), ("現在的工具", "AI 與知識庫"), ("沒有變的事", "把隱性知識留下來"), ("他的名字", "隱性知識提煉師")]),
    ])),
    sec("影響力主線｜流水的 AI 工具，鐵打的知識庫", "".join([
        "<p>他現在的主業，是協助專業知識工作者，以及 5 到 10 人的小公司與團隊，用 AI 培訓出自己的「AI 員工」。他常說一句話：「別再追著學工具。把資料準備好，讓 AI 來學你。」</p>",
        "<p>他的做法很樸實：會寫文件、會分類資料夾，就能開始打造自己的知識庫。先從每天做的一件事開始養，讓 AI 認識你的工作方式，再一件一件把電腦能做的事交出去。遇到對外送出、錢、日期這三種事，AI 會停下來交回給人確認。</p>",
        "<h3>三條協助的路</h3>",
        ul(["AI 課程與工作坊：中小企業內訓、政府專案、公部門培訓，基礎課用手機就能上。",
            "LINE 群組訊息整理：在台灣，工作訊息幾乎都在 LINE 裡。先把群組裡的報帳、待辦、專案進度整理出來，知識才有地方長。",
            "企業陪跑：一個月四次，帶團隊從盤點、建立 AI 辦公室，一路做到第一位 AI 員工上工。交接後隔一週，團隊自己重跑一次，跑得起來才算完成。"]),
        callout("他的核心信念", "AI 懂你，才能幫你。而這需要你先懂自己。"),
    ])),
    sec("方法｜往後跳一步問「為什麼」", "".join([
        "<p>他把自己的工作命名為「隱性知識提煉」。方法的關鍵，在於分辨兩種提問：「追進去問」是一直問細節，然後呢、還有呢；「跳出來問」是往後退一步，問為什麼這樣做、這反映了什麼。</p>",
        "<p>每往後跳一層，前一層藏在經驗裡的判斷就會浮上來，變成可以寫下來、可以交給 AI、也可以交給新人的東西。他把這套做法整理成六個層次：成果、標準、定位、方法、原理、覺察。</p>",
        "<p>給人看，它是新人手冊；給 AI 用，它是技能包。同一份整理，兩邊都能用。</p>",
    ])),
    sec("ESG 不是標籤｜把「人走了，經驗就沒了」這件事接住", "".join([
        "<h3>S｜社會（讓知識可近、可學）</h3>",
        ul(["每月固定舉辦兩場免費線上講座，讓還沒有預算的人也能先開始。",
            "授課足跡包括嘉義縣勞青處青創課程、臺中市女兒館、新北市公共藝術推廣計畫、文藻大學、社區電腦推廣教育基金會，以及永力扶輪社。",
            "基礎課設計成用手機就能上，降低數位落差的門檻。"]),
        "<h3>G｜治理（讓組織的經驗可以傳承）</h3>",
        ul(["協助團隊先找關鍵主管把一條流程做好，再複製出去，讓組織知識不會因為人員異動而斷掉。",
            "成品都放在團隊自己的電腦與帳號裡，資料主權留在組織手上。"]),
        "<h3>E｜環境（少做白工，也是一種減量）</h3>",
        ul(["他的原則是「先刪再自動化」：流程先簡化，再交給 AI，讓瞎忙不會因為 AI 而變得更快。"]),
    ])),
    sec("在永力社的位置｜幫社友的故事，蓋一座圖書館", "".join([
        "<p>在永力社，他負責這本永續影響力報告書的知識架構與網頁設計。每一位社友的人物誌、服務計畫、影響力數字，怎麼分類、怎麼互相連結、怎麼讓人與 AI 都讀得懂，是他在背後一塊一塊排好的。</p>",
        "<p>2026 年 4 月 27 日第 38 次線上例會，他上台分享「如何用 AI 協助撰寫影響力報告書」，把這本報告書背後的做法攤開給社友看，讓每個社都有機會用同一套方法整理自己的影響力。</p>",
        "<p>他做這件事的出發點，和他的職業是同一個：社友們在各自的領域默默做了很多事，這些經驗值得被看見，也值得留給下一屆、下一位新社友。</p>",
        callout("他在永力社的存在感", "把每一位社友的職業服務，整理成可以被查找、被傳承的知識資產。"),
    ])),
    sec("收束｜無形資產，越分享越豐盛", "".join([
        "<p>回到頁尾那一行小字。他把名字放在最後，因為他相信，整理好的知識會自己說話。</p>",
        callout("", "他最遠大的夢想，是累積知識資產。他相信無形資產越分享越豐盛，一份經驗被整理出來，就能在更多人手上繼續長大。", gold=True),
    ])),
    sec("江江自己的官網：江江教練 AI 知識管理", "".join([
        "<p>想更認識他的課程、免費講座與 AI 落地方案，可以到他的官網 <a href=\"https://jiangyude.com/\" target=\"_blank\" rel=\"noopener\">jiangyude.com</a>；合作邀約請洽 <a href=\"https://line.me/R/ti/p/@713kczfc\" target=\"_blank\" rel=\"noopener\">LINE 官方帳號</a>。</p>",
    ])),
])

jiang = dict(
    slug="20-jiang-yude", name="江昱德 Jiang", title_tag="隱性知識提煉師", img="jiang.webp", avatar_pos="center 20%",
    job="AI 應用與知識管理講師 · 隱性知識提煉師",
    role_tag="報告書知識架構 · 網頁設計",
    theme="隱性知識提煉師｜流水的 AI 工具，鐵打的知識庫",
    meta=["江江教練 AI 知識管理 創辦人", "AI 應用、陪跑、知識庫建立"],
    sdgs=[4, 8, 9, 17],
    one_liner="把專業工作者腦中的經驗整理出來，讓 AI 學會你的方式，也讓知識可以被傳承",
    description="翻到這本報告書的最底部，頁尾有一行很小的字：「知識架構、網頁設計：江昱德」。他把自己的名字放在最後一行，在意的是別人的故事有沒有被整理好、能不能被找到、被讀懂、被傳下去…",
    chips=[("web", "https://jiangyude.com/", "江江教練官網"),
           ("web", "https://line.me/R/ti/p/@713kczfc", "LINE 官方帳號"),
           ("web", "https://www.threads.com/@jiang_yude_coach", "Threads"),
           ("web", "https://vocus.cc/salon/Jiang_Coach", "方格子"),
           ("web", "https://www.youtube.com/@aipkmcc", "YouTube")],
    radar=dict(values=[5, 5, 3, 1, 2], details=[
        "負責永續影響力報告書的知識架構與網頁設計，把社友故事整理成可查找、可傳承的系統。",
        "隱性知識提煉師，協助專業工作者與 5 到 10 人團隊建立知識庫、培訓 AI 員工。",
        "每月兩場免費線上講座；社區電腦推廣教育基金會、臺中市女兒館等公共課程。",
        "本年度暫無國際合作專案，下一年規劃可發展之處。",
        "文藻大學、嘉義縣勞青處青創課程等青年培訓。"]),
    dash_h3="把經驗整理成資產，讓 AI 和下一個人都接得住",
    dash_p="他做的事情，從鏡頭後面的紀錄，一路延伸到今天的知識庫與 AI 員工。工具一直在換，看見、整理、復現這三件事沒有變過。",
    dash_source="資料來源：江江教練官網 jiangyude.com（2026 年 11 月）",
    stats=[("20", "年", "鏡頭後面的紀錄經驗", "拍公益組織、文教協會與在地組織的現場，熟悉一個組織對內培訓、對外倡議的知識流動。"),
           ("2", "場／月", "免費線上講座", "每月固定兩場，資訊公布在 LINE 社群，讓想開始的人先有入口。"),
           ("6", "類", "授課單位", "公部門青創、女性培力、公共藝術、大學、社區基金會與扶輪社。"),
           ("4", "週", "企業陪跑週期", "一個月四次實體陪跑，交接後團隊自己重跑一次，跑得起來才算完成。"),
           ("3", "條路", "培訓 AI 員工", "AI 課程與工作坊、LINE 群組訊息整理、企業陪跑。"),
           ("6", "層", "QBQ 提煉層次", "成果、標準、定位、方法、原理、覺察，每往後跳一層，隱性知識就浮上來一層。")],
    review_note="社內職務（目前寫「報告書知識架構 · 網頁設計」）、SDG 編號，以及「在永力社的位置」一段，請確認後再刪除此提示條。",
    prev=("19-irene-chen.html", "陳美華 Irene"), next=("21-ivy-huang.html", "黃敏菁 Dr. Ivy"),
    body=jiang_body,
)

# ───────────────────────── Dr. Ivy ─────────────────────────
ivy_body = "\n".join([
    sec("開場畫面｜一次生命轉折之後", "".join([
        "<p>Dr. Ivy 曾在受訪時分享，921 地震後的那段經驗，讓她重新理解了氣味與陪伴。在最混亂的日子裡，一個熟悉的味道，可能就是讓人安定下來的那一點點力量。</p>",
        "<p>從那之後，她不斷學習、教學、實作，一走就是二十八年。</p>",
        callout("那個起點", "氣味除了好不好聞，也和一個人的經驗、當下的感受、生活的記憶連在一起。"),
    ])),
    sec("專業底色｜府城西市場的「訂製精神」", "".join([
        "<p>她常提起台南府城的百年西市場。在那裡，訂製西服的師傅不會把同一件成衣交給每個人，他會先理解一個人的輪廓、需要與生活，再一針一線細心調整。</p>",
        "<p>她把這份精神帶進香氣的世界：不用固定答案定義一個人，從嗅聞、記憶、場域與故事出發，慢慢找到屬於當下的氣味方向。她的教學理念也是同一句話：「把複雜的知識說清楚，讓學習保有人的溫度。」</p>",
        grid([("專業歷練", "28 年"), ("演講與授課", "3,000 場次"), ("身份", "國際芳香療癒與品牌香氣首席整合顧問"), ("品牌", "WELLINA")]),
        "<h3>她整合的專業</h3>",
        ul(["芳香療法教育與國際芳療師培訓", "法國調香師學習與調香實作", "氣味心理應用，與臨床、心理專業合作場域", "品牌故事與場域香氣設計", "講師與專業人才培育"]),
    ])),
    sec("影響力主線｜一株香草，走成一條產業鏈", "".join([
        "<p>她近年投入最深的，是一條從土地開始的永續路徑。思凡自然農園串聯全台 NPO 與社福團體，讓不同條件的夥伴參與香草的育苗、栽種、照顧與採收；香草原料經專業萃取與分析後，由 Dr. Ivy 進行配方調配與商品設計；最後再由企業透過演講、員工調香、採購與共創加入，讓支持從一次活動，延伸成持續的合作。</p>",
        grid([("01 栽種", "社福夥伴參與香草種植"), ("02 分析", "專業萃取與批次檢驗"), ("03 設計", "Dr. Ivy 配方與商品應用"), ("04 參與", "企業演講、調香與採購")]),
        "<p>她也很堅持一件事：每個數字都要知道從哪裡來。公開資料會標示來源與更新時間，願景與已完成的成果分開記錄，也不把活動紀錄直接換算成 ESG 或認證成果。</p>",
        callout("她在產業鏈裡的角色", "把原料的故事，轉成企業和一般人都能理解、也能參與的合作方案。"),
    ])),
    sec("另一條支線｜把香氣帶進家庭、情緒與生命教育", "".join([
        "<p>除了課堂與品牌，她長期走進公部門、學校與專業機構，用五感與芳香陪伴不同的人：</p>",
        ul(["家庭教育：臺南市家庭教育中心伴侶講座、嘉義市親職教育與親子生命教育、內政部移民署跨國婚姻家庭講座。",
            "職場紓壓：臺南市政府勞工局職工福利講座。",
            "大學與青年：國立中山大學 ALOHA 永續發展冬令營暨種子教師培訓、五感與自我覺察工作坊；指導國立嘉義大學學生芳香創業團隊，獲教育部食品創新銀獎。",
            "高齡照顧：嘉義大學「高齡親密，相伴久久」、樹人家商長者健康照護研習、南護樂齡健康美學。",
            "心理專業合作：嘉義市臨床心理師公會、臺中榮總嘉義分院、禾好心理治療所。"]),
        "<p>2024 年，她也獲得嘉義市祖父母節家庭教育績優個人肯定。</p>",
    ])),
    sec("國際肯定｜站上世界盃的評審席", "".join([
        "<p>2016 年，她受邀擔任 OMC 美容美髮世界盃裁判，並獲選最佳裁判；同年也在韓國國際美容美髮大賽拿下雙料冠軍。這段國際經歷，讓她的芳香教育多了一層跨國的視野。</p>",
        "<p>品牌合作方面，她為日月潭涵碧樓設計一日沉浸式調香課程，也與艾恩斯遊艇、富廣建設、金豐集團、澄市設計、水灣餐廳等品牌與場域合作，把品牌故事變成一段可以被感受的氣味記憶。</p>",
    ])),
    sec("在永力社的位置｜讓職業服務，有一個溫柔的味道", "".join([
        "<p>2026 年 1 月 19 日第 32 次線上例會，她以「女性的內在氣場：用精油香氛打造你自信與職場魅力」為題和社友分享，把芳香教育帶進永力社的例會現場。</p>",
        "<p>永力社相信「以職業服務社會」。Dr. Ivy 的香草產業鏈，剛好把職業服務、社區服務與社福參與接在同一條線上：社福夥伴有了工作與角色，企業有了參與永續的具體方式，香氣也成為大家都能親身體驗的入口。</p>",
        callout("她帶給永力社的", "把專業做成可以被感受、被參與的體驗，讓服務走進每個人的生活。"),
    ])),
    sec("收束｜香氣是一個開始感受的入口", "".join([
        "<p>對 Dr. Ivy 來說，香氣不需要給出標準答案。從一個人的嗅覺經驗，到一個品牌希望留下的印象；從一堂入門課，到能夠獨立判斷的專業培育，這條路她還在繼續走。</p>",
        callout("", "她調的是香，留下的是人與人、人與土地之間，一段被好好記住的溫度。", gold=True),
    ])),
    sec("Dr. Ivy 自己的官網：Dr. Ivy × WELLINA", "".join([
        "<p>課程、國際認證、香氣測驗與合作洽談，都整理在她的官網 <a href=\"https://dr-ivy.com/\" target=\"_blank\" rel=\"noopener\">dr-ivy.com</a>；日常教學影像可以追蹤 Instagram <a href=\"https://www.instagram.com/wellina1965/\" target=\"_blank\" rel=\"noopener\">@wellina1965</a>。</p>",
    ])),
])

ivy = dict(
    slug="21-ivy-huang", name="黃敏菁 Dr. Ivy", title_tag="香氣教育者", img="ivy.jpg", avatar_pos="center 15%",
    job="國際芳香療癒與品牌香氣首席整合顧問",
    role_tag="WELLINA 品牌創辦人 · 芳香教育",
    theme="香氣教育者｜把複雜的知識說清楚，讓學習保有人的溫度",
    meta=["國際芳香療癒與品牌香氣首席整合顧問", "Dr. Ivy × WELLINA"],
    sdgs=[3, 4, 8, 12, 17],
    one_liner="從社福夥伴種下的香草，到企業參與的調香課，把芳香教育走成一條共好的永續產業鏈",
    description="Dr. Ivy 曾在受訪時分享，921 地震後的那段經驗，讓她重新理解了氣味與陪伴。從那之後，她不斷學習、教學、實作，一走就是二十八年…",
    chips=[("web", "https://dr-ivy.com/", "Dr. Ivy 官網"),
           ("web", "https://dr-ivy.com/esg-life-balance/", "ESG 香草產業鏈"),
           ("web", "https://www.instagram.com/wellina1965/", "Instagram"),
           ("web", "https://tr.ee/HpdgvcwyGW", "聯絡合作")],
    radar=dict(values=[2, 5, 4, 3, 3], details=[
        "社內職務待確認。",
        "28 年芳香教育、3,000 場次演講授課；國際芳療師與講師培訓、品牌香氣設計。",
        "與思凡自然農園及社福團體共建香草產業鏈；家庭教育中心、移民署、勞工局公共講座。",
        "2016 OMC 美容美髮世界盃最佳裁判、韓國國際大賽雙料冠軍；國際芳療師認證課程。",
        "中山大學 ALOHA 永續冬令營種子教師培訓；指導嘉義大學學生團隊獲教育部食品創新銀獎。"]),
    dash_h3="從一株香草，到一條共好的產業鏈",
    dash_p="社福夥伴在農場種下香草，專業單位萃取分析，Dr. Ivy 設計成可以被使用的商品與課程，企業再透過演講、調香與採購加入。每個環節的人，都在這條路上有清楚的角色。",
    dash_source="資料來源：Dr. Ivy 官網 dr-ivy.com；思凡自然農園公開資料（來源頁更新於 2026-09-23）",
    stats=[("28", "年", "芳香專業歷練", "從生命經驗走進芳香探索，再走向教育、品牌與場域策略。"),
           ("3,000", "場", "演講與授課累積", "公部門、大學、專業機構、企業與社區，跨越不同對象與場域。"),
           ("14", "家", "合作社福機構", "思凡自然農園公開資料：合作及協助規劃農場的社福機構。"),
           ("3,100", "坪", "香草耕地面積", "思凡自然農園官網公開的目前總耕地面積。"),
           ("2,500", "小時", "農場工作總時數", "思凡「森呼吸＋森守護」活動頁公布，共 344 人次投入。"),
           ("2016", "年", "世界盃最佳裁判", "受邀擔任 OMC 美容美髮世界盃裁判，獲選最佳裁判。")],
    review_note="社內職務（目前寫品牌身份代替）、SDG 編號、頭像照片授權，以及「在永力社的位置」一段，請 Ivy 本人確認後再刪除此提示條。產業鏈數字引自思凡自然農園公開資料，上線前建議再核對一次。",
    prev=("20-jiang-yude.html", "江昱德 Jiang"), next=("01-cp-lin.html", "林學賢 CP Impact"),
    body=ivy_body,
)

for p in (jiang, ivy):
    (ROOT / "profiles" / f"{p['slug']}.html").write_text(page(p))
    print("wrote", p["slug"])

# 社友列表卡片片段（貼進 members.html）
def card(p, theme_line, chips):
    c = " ".join(f'<span class="focus-chip svc-chip-{k}">{v}</span>' for k, v in chips)
    return f'''<!-- {p['name']} --> <article class="member-card"> <a class="profile-btn" href="profiles/{p['slug']}.html">完整人物誌 <span class="arrow">→</span></a> <a class="member-head" href="profiles/{p['slug']}.html"> <div class="avatar" style="background-image:url(assets/img/members/{p['img']})"></div> <div class="info"> <div class="name">{p['name']}</div> <div class="role">{p['role_tag']}</div> </div> </a> <div class="member-body"> <p class="theme-line">{theme_line}</p> <div class="focus-row"> {c} </div> </div> </article>'''

snip = "\n".join([
    "<!-- 貼進 members.html 的社友區（依姓氏筆畫：江 6 畫排在李琪之前；黃 12 畫排在黃世祿之後）-->",
    card(jiang, "把專業工作者腦中的經驗整理出來，讓 AI 學會你的方式，也讓社友的故事可以被傳承。江江教練 AI 知識管理 創辦人。",
         [("vocational", "職業服務"), ("club", "社務服務")]),
    card(ivy, "從社福夥伴種下的香草，到企業參與的調香課，把芳香教育走成一條共好的產業鏈。Dr. Ivy × WELLINA 國際芳香療癒與品牌香氣首席整合顧問。",
         [("vocational", "職業服務"), ("community", "社區服務")]),
])
(ROOT / "members-cards-snippet.html").write_text(snip + "\n")
print("wrote snippet")
