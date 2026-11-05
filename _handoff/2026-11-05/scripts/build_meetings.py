#!/usr/bin/env python3
"""永力社 2024-2026 例會與活動展示頁。照片來源：2024-26年度例會資料夾；講者講題：25-26年度行事曆。"""
import json, re, html, pathlib
from collections import OrderedDict

OUT = pathlib.Path(__file__).resolve().parent.parent / "meetings"  # 輸出：_handoff/.../meetings
items = json.load(open(pathlib.Path(__file__).resolve().parent / "items.json"))
DATE_FIX = {"2025-02-25": "2025-02-24"}  # 檔名 0225，海報為 2/24（一）
for _it in items:
    _it["date"] = DATE_FIX.get(_it["date"], _it["date"])

# 25-26 年度行事曆（只放社內例會；講者・講題原文整理）
CAL = {
    # 2024-25 年度：從例會海報整理
    "2024-10-26": ("實體例會", "黃永輝 PDG APPS（3481 地區前總監）：如何撰寫有影響力的服務計畫"),
    "2024-12-23": ("線上例會", "郭麗琴 DORIS（金湛海外遊學創辦人）：菲律賓遊學實務及趣談"),
    "2025-01-04": ("實體例會", "劉影梅 DG HEALTHY（3481 地區總監）：如何透過參與扶輪來擴大醫護專業領域的永續影響力"),
    "2025-02-12": ("實體例會", "呂慶龍（前駐法大使）：多些理性智慧看世界，挑戰與機會"),
    "2025-02-24": ("線上例會", "高清坊 James：2025 高齡住宅趨勢與迷思；林映如 Lisa：如何利用碳手印，提升品牌綠色影響力"),
    "2025-03-06": ("聯合例會", "扶輪社聯合例會 x 公益服務 x 社會影響力論壇｜施振榮：企業暨社會永續發展；黃正忠：公益服務與社會影響力"),
    "2025-03-24": ("線上例會", "陳明勇 Vincent：對話引導，看見永續影響力；卓芳玉 Angel：打造永續綠色香氛生活的美好"),
    "2025-04-12": ("聯合例會", "與台北台美社聯合例會｜鄭雲龍（身體智慧執行長）：健康自「脊」來"),
    "2025-04-21": ("線上例會", "劉彥琳 Grace：失智路上你和我；李琪 Vicky：DEI 女力綻放，淡水女路案例分享"),
    "2025-04-27": ("活動", "喜樂樂團主辦｜日語瘋音樂發表會"),
    "2025-05-10": ("地區", "2024-25 年度 3481 地區年會｜圓山大飯店"),
    "2025-05-26": ("線上例會", "吳淑玲 Annie：永續 CHILL 一下，從 CSR 幕僚到講師的永續實踐；樊世方 Gordon：碳權如何引領我們邁向淨零未來"),
    "2025-06-07": ("聯合例會", "與台北台美社聯合例會｜鄭家鐘（台新銀行文化藝術基金會董事長）：藝術給人生下半場的備忘錄"),
    "2025-06-23": ("線上例會", "林修緯 Wayne：財商房產活化，自住房也能收租；黃世祿 Derek：我經營的永續電子平台介紹"),
    "2025-06-27": ("活動", "年度感恩餐會暨喜樂樂團成果發表會｜大直典華"),
    "2025-07-12": ("實體陽光例會", "淡海輕軌低碳永續之旅｜淡水"),
    "2025-07-21": ("線上例會", "紀冠宇 P. Derek：用影音講出 ESG 好故事；陳明勇 Vincent：非營利組織的永續報告書"),
    "2025-08-09": ("實體例會", "林美惠 Amy Lin：Rotary x ESG，解鎖企業永續新商機"),
    "2025-08-18": ("線上例會", "禧愛社 李芸珮 PP Petty：永續品牌與永續報告書設計；黃丞隆 Rich：醫療 x 永續健康深耕計畫"),
    "2025-09-13": ("實體例會", "黃志湧：導覽解說｜臺北市立圖書館廣慈分館"),
    "2025-09-22": ("線上例會", "姚曼菁：魚尾峰下的彩虹；楊嘉文 Zoe：扶輪公益網，讓你隨手做公益"),
    "2025-10-13": ("實體例會", "DG Sunny 總監公式訪問"),
    "2025-10-20": ("線上例會", "徐玉光：如何用 AI 工具，一個月內完成碳盤查；戴中興：企業如何運用 AI 邁向永續"),
    "2025-11-03": ("線上例會", "葉德偉 Allen Ye：ESG 循環包裝的趨勢與永續創業旅程；黃銘弘 Kole：幸福企業，高齡照顧友善職場"),
    "2025-11-22": ("實體例會", "台北永續影響力社授證一週年慶祝典禮"),
    "2025-12-13": ("實體例會", "陳美伶：找尋地方的美好，台灣地方創生故事分享（理事及社長當選人選舉）"),
    "2025-12-22": ("爐邊例會", "攀登非洲屋脊吉力馬札羅山心得"),
    "2026-01-10": ("實體例會", "魏梅金：從盤查現況到行動藍圖，打造企業的永續影響力"),
    "2026-01-19": ("線上例會", "林呈欣 P. Sean：ESG 與永續金融；黃敏菁博士 Dr. Ivy：女性的內在氣場，用精油香氛打造自信與職場魅力"),
    "2026-02-07": ("實體例會", "林偉賢：把握 5A 新時代的新商機"),
    "2026-02-23": ("線上例會", "邱以慈 Joyce：循環容器計畫政策試辦；王怡晶：介紹碳大師溫室氣體盤查資訊網"),
    "2026-03-09": ("線上例會", "范逸嫻：從一粒米看見未來，ESG 農業與永續餐桌；洪昭勝：永續食堂革命"),
    "2026-03-22": ("實體例會", "陳明勇 Vincent 帶領年度共識營"),
    "2026-04-19": ("實體例會", "第九屆地區年會｜台大體育館"),
    "2026-04-27": ("線上例會", "江昱德：如何用 AI 協助撰寫影響力報告書；沈煒庭：公私部門如何協同合作落實永續影響力"),
    "2026-05-16": ("實體例會", "2026 台灣女力影響力論壇｜台大霖澤館"),
    "2026-06-13": ("實體例會", "變更例會，參與台北國際年會根除小兒麻痺路跑｜總統府廣場"),
    "2026-06-22": ("線上例會", "鹿港陳阿彰：走歪路的觀光系畢業生？張艾筆：AI 時代影像產業的新價值鏈"),
}

CAL_T = {"2025-26 年度幹部研習會": ("地區", "2025-26 年度國際扶輪 3481 地區訓練講習會（DTA）")}

# 大節點：卡片放大
MILESTONE = {"2024-08-20", "2024-11-21", "2024-11-26", "2025-01-04", "2025-03-06", "2025-06-27",
             "2025-11-22", "2026-03-11", "2026-03-22", "2026-05-16", "2026-06-13", "2026-06-17"}


def category(label):
    if re.search(r"世界年會|地區|扶輪日|聯合例會", label): return "region", "地區與國際"
    if re.search(r"創社|證書|社慶|和平|共識營|宣誓|研習|感恩|發起人", label): return "club", "社務大事"
    if re.search(r"樂團|音樂|淡水|論壇|工作坊|鎮瀾宮|路跑", label): return "service", "服務與交流"
    return "meeting", "例會"


def clean(label):
    l = re.sub(r"(大合照|社友合照|主辦社合照|主辦社宣示|分享一|分享|拍照|照片\d|幹部團隊照|樂團發表|\d)$", "", label).strip()
    l = re.sub(r"擔任世界年會擔任志工", "擔任世界年會志工", l)
    l = l.replace("另社創社典禮新社員宣誓", "創社授證典禮・新社員宣誓").replace("永力社創社大合照", "創社授證典禮")
    l = l.replace("世界年會公益路跑", "世界年會根除小兒麻痺路跑").replace("2025-26年度", "2025-26 年度")
    l = l.replace("永力臨時", "永力臨時社")
    l = l.replace("臨時社社", "臨時社")
    return l or label


# 依日期＋活動名稱分組
events = OrderedDict()
for it in sorted(items, key=lambda x: (x["date"], x["img"])):
    name = clean(it["label"])
    if it["date"] == "2025-11-26": pass
    key = (it["date"], "創社授證典禮" if it["date"] == "2024-11-26" else ("世界年會" if it["date"] == "2026-06-13" else name))
    ev = events.setdefault(key, dict(date=it["date"], title=key[1], photos=[], undated=it["undated"]))
    ev["photos"].append(it)

for (d, t), ev in events.items():
    ev["cat"], ev["cat_label"] = category(" ".join(p["label"] for p in ev["photos"]))
    m = re.search(r"第\s*(\d+)\s*次", t)
    ev["no"] = int(m.group(1)) if m else None
    ev["cal"] = CAL_T.get(t) or (None if ev["undated"] else CAL.get(d))
    ev["big"] = d in MILESTONE

WEEK = "一二三四五六日"
import datetime


def fmt_date(d, undated):
    if undated: return "2025-26 年度"
    dt = datetime.date.fromisoformat(d)
    return f"{dt.year}.{dt.month:02d}.{dt.day:02d}（{WEEK[dt.weekday()]}）"


def rotary_year(d):
    dt = datetime.date.fromisoformat(d)
    return "2024-25" if (dt.year, dt.month) < (2025, 7) else "2025-26"


years = OrderedDict([("2024-25", []), ("2025-26", [])])
for ev in events.values():
    years[rotary_year(ev["date"])].append(ev)

n_photos = len(items)
n_events = len(events)
max_no = max(e["no"] for e in events.values() if e["no"])

YEAR_INTRO = {
    "2024-25": ("創社年", "從 2024 年 8 月的發起人會議開始，臨時社一次一次聚起來，11 月正式授證成立。第一年就辦了聯合例會、音樂發表會、年度感恩餐會，大家從彼此認識，走到一起做事。"),
    "2025-26": ("深耕年", "第二年把例會變成永續學習的教室：ESG、碳盤查、循環經濟、AI 應用輪番上場。一週年社慶、成為和平扶輪社、女力影響力論壇，再到台北世界年會的志工與路跑，社友一路都在場。"),
}

MONTHS = "一二三四五六七八九十"


def month_label(d):
    dt = datetime.date.fromisoformat(d)
    m = dt.month
    return f"{dt.year} 年 {m} 月"


def card(ev):
    ph = ev["photos"]
    cover = ph[0]
    more = len(ph) - 1
    no = f'<span class="mt-no">第 {ev["no"]} 次</span>' if ev["no"] else ""
    cal = ""
    if ev["cal"]:
        typ, txt = ev["cal"]
        cal = f'<p class="mt-topic"><span class="mt-type">{html.escape(typ)}</span>{html.escape(txt)}</p>'
    gallery = json.dumps([[p["img"], p["w"], p["h"]] for p in ph])
    badge = f'<span class="mt-more">+{more}</span>' if more else ""
    title = ev["title"]
    if ev["no"]:
        rest = re.sub(r"第\s*\d+\s*次例會", "", title).lstrip("暨").strip()
        rest = {"公式訪問": "總監公式訪問"}.get(rest, rest)
        title = f"第 {ev['no']} 次例會" + (f"｜{rest}" if rest else "")
        no = ""
    big = " mt-big" if ev["big"] else ""
    return f'''<article class="mt-card{big}" data-cat="{ev['cat']}" data-gallery='{gallery}' data-title="{html.escape(ev['title'])}" data-date="{fmt_date(ev['date'], ev['undated'])}">
<button class="mt-photo" type="button" aria-label="看 {html.escape(ev['title'])} 的照片"><img src="../assets/img/meetings/{cover['img']}-s.webp" width="{cover['w']}" height="{cover['h']}" loading="lazy" alt="{html.escape(ev['title'])}">{badge}</button>
<div class="mt-body"><div class="mt-meta"><span class="mt-date">{fmt_date(ev['date'], ev['undated'])}</span>{no}<span class="mt-cat mt-cat-{ev['cat']}">{ev['cat_label']}</span></div>
<h3>{html.escape(title)}</h3>{cal}</div></article>'''


sections = []
for y, evs in years.items():
    name, intro = YEAR_INTRO[y]
    n_meet = sum(1 for e in evs if e["no"])
    month_html = '<div class="mt-wall">' + "".join(card(e) for e in evs) + '</div>'
    n_ph = sum(len(e["photos"]) for e in evs)
    sections.append(f'''<section class="profile-section mt-year" id="y{y}" data-year="{y}"> <div class="container">
<h2>{y} 年度｜{name}</h2> <p class="mt-year-intro">{intro}</p>
<div class="mt-year-stats"><span><b>{len(evs)}</b> 場例會與活動</span><span><b>{n_ph}</b> 張照片與海報</span></div>
{month_html}
</div> </section>''')

CSS = r"""
.mt-hero{padding:56px 0 24px}
.mt-hero h1{font-family:"Noto Serif TC",serif;font-size:clamp(30px,5vw,46px);margin:8px 0 12px;line-height:1.3}
.mt-hero .subtitle{color:var(--ink-soft);font-size:17px;line-height:1.9;max-width:720px;margin:0}
.mt-kicker{display:inline-block;background:var(--gold);color:#fff;border-radius:999px;padding:4px 14px;font-size:14px;letter-spacing:.08em}
.mt-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:32px 0 8px}
.mt-stat{background:var(--bg-card);border:1px solid var(--line);border-top:3px solid var(--gold);border-radius:var(--radius);padding:18px 18px 16px}
.mt-stat .n{font-family:"Noto Serif TC",serif;font-size:36px;color:var(--gold);line-height:1}
.mt-stat .n small{font-size:15px;margin-left:4px;color:var(--ink-soft)}
.mt-stat .l{margin-top:8px;font-size:14px;color:var(--ink-soft)}
.mt-toolbar{position:sticky;top:0;z-index:20;background:color-mix(in srgb,var(--bg) 92%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--line);padding:12px 0}
.mt-toolbar .container{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:center;justify-content:space-between}
.mt-chips{display:flex;flex-wrap:wrap;gap:8px}
.mt-chip{border:1px solid var(--line);background:var(--bg-card);color:var(--ink-soft);border-radius:999px;padding:6px 14px;font-size:14px;cursor:pointer;font-family:inherit}
.mt-chip[aria-pressed="true"]{background:var(--ink);color:#fff;border-color:var(--ink)}
.mt-jump{display:flex;gap:8px}
.mt-jump a{font-size:14px;color:var(--gold);text-decoration:none;border-bottom:1px solid currentColor}
.mt-year-intro{color:var(--ink-soft);line-height:1.9;max-width:760px}
.mt-year-stats{display:flex;gap:20px;flex-wrap:wrap;margin:8px 0 8px;color:var(--ink-soft);font-size:15px}
.mt-year-stats b{font-family:"Noto Serif TC",serif;font-size:24px;color:var(--gold);margin-right:4px}
.mt-month{margin-top:36px}
.mt-month-h{font-family:"Noto Serif TC",serif;font-size:19px;color:var(--ink);margin:0 0 14px;display:flex;align-items:center;gap:12px}
.mt-month-h::after{content:"";flex:1;border-top:1px dashed var(--line)}
.mt-wall{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;margin-top:28px}
.mt-card{display:flex;flex-direction:column;background:var(--bg-card);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;box-shadow:var(--shadow);transition:box-shadow .2s,transform .2s}
.mt-card:hover{box-shadow:var(--shadow-hover);transform:translateY(-2px)}
.mt-card.mt-big .mt-body{background:linear-gradient(180deg,#FCF7E9,var(--bg-card))}
.mt-card.is-hidden{display:none}
.mt-photo{display:block;position:relative;width:100%;aspect-ratio:4/5;padding:10px;border:0;border-bottom:1px solid var(--line-soft);background:var(--bg-soft);cursor:zoom-in}
.mt-photo img{display:block;width:100%;height:100%;object-fit:contain}
.mt-more{position:absolute;right:10px;bottom:10px;background:rgba(42,38,32,.78);color:#fff;font-size:13px;padding:3px 10px;border-radius:999px}
.mt-body{padding:12px 14px 14px}
.mt-meta{display:flex;flex-wrap:wrap;gap:6px;align-items:center;font-size:12.5px;color:var(--ink-mute)}
.mt-no{background:var(--bg-soft);color:var(--ink-soft);border-radius:6px;padding:1px 8px}
.mt-cat{border-radius:6px;padding:1px 8px;color:#fff}
.mt-cat-meeting{background:var(--role-guard)}
.mt-cat-club{background:var(--gold)}
.mt-cat-region{background:var(--role-act)}
.mt-cat-service{background:var(--green)}
.mt-card h3{font-size:16px;margin:8px 0 0;line-height:1.5;color:var(--ink)}
.mt-topic{margin:6px 0 0;font-size:13.5px;line-height:1.7;color:var(--ink-soft)}
.mt-type{display:inline-block;font-size:12px;color:var(--gold);border:1px solid var(--gold-soft);border-radius:4px;padding:0 6px;margin-right:6px}
.mt-empty{display:none;color:var(--ink-mute);padding:20px 0}
.mt-lb{position:fixed;inset:0;z-index:100;background:rgba(20,18,15,.92);display:none;flex-direction:column;align-items:center;justify-content:center;padding:16px}
.mt-lb.open{display:flex}
.mt-lb img{max-width:100%;max-height:calc(100vh - 120px);object-fit:contain;border-radius:6px}
.mt-lb-cap{color:#f2ede3;margin-top:12px;font-size:15px;text-align:center;line-height:1.6}
.mt-lb button{position:absolute;background:rgba(255,255,255,.12);color:#fff;border:0;border-radius:999px;width:44px;height:44px;font-size:22px;cursor:pointer}
.mt-lb .x{top:16px;right:16px}.mt-lb .p{left:16px;top:50%}.mt-lb .n{right:16px;top:50%}
@media(max-width:1000px) and (min-width:761px){.mt-wall{grid-template-columns:repeat(3,1fr)}}
@media(max-width:760px){.mt-stats{grid-template-columns:repeat(2,1fr)}.mt-wall{grid-template-columns:repeat(2,1fr);gap:10px}.mt-photo{padding:6px}.mt-body{padding:10px}.mt-card h3{font-size:14.5px}.mt-topic{font-size:12.5px}.mt-hero{padding-top:36px}}
"""

JS = r"""
(function(){
  var chips=document.querySelectorAll('.mt-chip'), cards=document.querySelectorAll('.mt-card');
  chips.forEach(function(c){c.addEventListener('click',function(){
    chips.forEach(function(x){x.setAttribute('aria-pressed','false')}); c.setAttribute('aria-pressed','true');
    var f=c.dataset.filter;
    cards.forEach(function(k){k.classList.toggle('is-hidden', f!=='all' && k.dataset.cat!==f)});
    document.querySelectorAll('.mt-month').forEach(function(m){
      m.style.display = m.querySelector('.mt-card:not(.is-hidden)') ? '' : 'none';
    });
  })});
  var lb=document.getElementById('mt-lb'), img=lb.querySelector('img'), cap=lb.querySelector('.mt-lb-cap'), g=[], i=0, card=null;
  function show(){ img.src='../assets/img/meetings/'+g[i][0]+'.webp'; cap.textContent=card.dataset.date+'　'+card.dataset.title+(g.length>1?'　（'+(i+1)+' / '+g.length+'）':''); }
  document.querySelectorAll('.mt-photo').forEach(function(b){b.addEventListener('click',function(){
    card=b.closest('.mt-card'); g=JSON.parse(card.dataset.gallery); i=0; show(); lb.classList.add('open'); document.body.style.overflow='hidden';
  })});
  function close(){lb.classList.remove('open'); img.src=''; document.body.style.overflow='';}
  lb.querySelector('.x').onclick=close;
  lb.querySelector('.p').onclick=function(e){e.stopPropagation(); i=(i-1+g.length)%g.length; show();};
  lb.querySelector('.n').onclick=function(e){e.stopPropagation(); i=(i+1)%g.length; show();};
  lb.addEventListener('click',function(e){if(e.target===lb)close();});
  document.addEventListener('keydown',function(e){ if(!lb.classList.contains('open'))return;
    if(e.key==='Escape')close(); if(e.key==='ArrowLeft')lb.querySelector('.p').click(); if(e.key==='ArrowRight')lb.querySelector('.n').click(); });
})();
"""

n_meetings_total = max_no
_org={"@type":"Organization","name":"Rotary Club of Taipei Sustainable Impact","alternateName":"台北永續影響力扶輪社","url":"https://rctsi.3481.org/"}
_evs=[]
for _e in events.values():
    if _e["undated"]: continue
    _online = bool(_e["cal"] and "線上" in _e["cal"][0])
    _d={"@type":"Event","name":re.sub(r"第\s*(\d+)\s*次例會", r"第 \1 次例會", _e["title"]),"startDate":_e["date"],
        "eventAttendanceMode":"https://schema.org/"+("OnlineEventAttendanceMode" if _online else "OfflineEventAttendanceMode"),
        "eventStatus":"https://schema.org/EventScheduled","organizer":_org,
        "image":"https://rctsi.3481.org/assets/img/meetings/"+_e["photos"][0]["img"]+".webp"}
    if _e["cal"]: _d["description"]=_e["cal"][1]
    _evs.append(_d)
LD=json.dumps({"@context":"https://schema.org","@graph":[
  {"@type":"WebPage","name":"例會與活動紀錄 — 永力扶輪社 2024-2026","url":"https://rctsi.3481.org/meetings/","inLanguage":"zh-Hant",
   "isPartOf":{"@type":"WebSite","name":"台北永續影響力扶輪社｜永續影響力報告書","url":"https://rctsi.3481.org/"},"publisher":_org,"dateModified":"2026-11-05"},
  {"@type":"ItemList","name":"永力社 2024-2026 例會與活動","numberOfItems":len(_evs),
   "itemListElement":[{"@type":"ListItem","position":i+1,"item":e} for i,e in enumerate(_evs)]}]}, ensure_ascii=False)
page = f'''<!DOCTYPE html><html lang="zh-Hant"> <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>例會與活動紀錄 — 永力扶輪社 2024-2026 永續報告</title><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;600;700&family=Noto+Serif+TC:wght@500;600;700&display=swap" rel="stylesheet"><link rel="stylesheet" href="../assets/css/common.css?v=9">
<link rel="canonical" href="https://rctsi.3481.org/meetings/">
<meta name="description" content="台北永續影響力扶輪社 2024-2026 兩個年度的例會與活動紀錄：{n_events} 場例會與活動、{n_photos} 張照片與海報，從創社發起人會議一路到台北世界年會。">
<meta property="og:title" content="例會與活動紀錄 — 永力扶輪社 2024-2026">
<meta property="og:image" content="https://rctsi.3481.org/assets/img/meetings/20241126-08.webp">
<script type="application/ld+json">{LD}</script>
<style>{CSS}</style>
</head> <body>
<header class="topbar"> <div class="inner"> <a class="brand" href="../index.html" aria-label="回首頁"> <span class="mark">永</span>永續影響力扶輪社年度報告書 </a> <button class="nav-toggle" aria-label="開啟選單" aria-expanded="false"> <span></span><span></span><span></span> </button> <nav> <a href="../index.html#intro">關於永力社</a><a href="../index.html#impact-report">影響力報告</a><a href="../index.html#five-service">五大服務</a><a href="../index.html#members">社友介紹</a><a href="../index.html#impact-hub">服務計畫</a> </nav> </div> </header>

<section class="mt-hero"> <div class="container">
<span class="mt-kicker">MEETINGS &amp; ACTIVITIES · 2024-2026</span>
<h1>兩年 {n_meetings_total} 次例會，我們一直都在</h1>
<p class="subtitle">從 2024 年 8 月的創社發起人會議開始，永力社每個月都有例會、講座、服務與交流。這一頁把兩個年度的海報與現場照片排在一起，點任一張就能放大看。</p>
<div class="mt-stats">
<div class="mt-stat"><div class="n">{n_meetings_total}<small>次</small></div><div class="l">例會（至 2026 年 6 月）</div></div>
<div class="mt-stat"><div class="n">{n_events}<small>場</small></div><div class="l">留下紀錄的例會與活動</div></div>
<div class="mt-stat"><div class="n">{n_photos}<small>張</small></div><div class="l">海報與現場照片</div></div>
<div class="mt-stat"><div class="n">2<small>屆</small></div><div class="l">2024-25 創社年・2025-26 深耕年</div></div>
</div>
</div> </section>

<div class="mt-toolbar"> <div class="container">
<div class="mt-chips" role="group" aria-label="篩選活動類型">
<button class="mt-chip" data-filter="all" aria-pressed="true">全部</button>
<button class="mt-chip" data-filter="meeting" aria-pressed="false">例會</button>
<button class="mt-chip" data-filter="club" aria-pressed="false">社務大事</button>
<button class="mt-chip" data-filter="service" aria-pressed="false">服務與交流</button>
<button class="mt-chip" data-filter="region" aria-pressed="false">地區與國際</button>
</div>
<div class="mt-jump"><a href="#y2024-25">2024-25</a><a href="#y2025-26">2025-26</a></div>
</div> </div>

{"".join(sections)}

<div class="container"> <nav class="profile-nav"> <a href="../index.html#intro">← 關於永力社</a> <a class="home" href="../index.html">回首頁</a> <a href="../index.html#members">社友介紹 →</a> </nav> </div>

<footer> <div class="container"> <div> <p class="foot-title">台北永續影響力扶輪社</p> <p>Rotary Club of Taipei Sustainable Impact</p> <p>以職業服務社會 · 用影響力衡量價值</p> <p style="margin-top:14px;font-size:14px;color:var(--ink-mute);"> 本報告書由永力社報告書工作小組製作<br> 主筆：陳明勇 Vincent · 工作組：CP 林學賢、艾筆團隊<br> 知識架構、網頁設計：江昱德<br> </p> </div> <div> <p class="foot-title">章節導覽</p> <ul> <li><a href="../index.html#intro">關於永力社</a></li><li><a href="../index.html#impact-report">影響力報告</a></li><li><a href="../index.html#five-service">五大服務</a></li><li><a href="../index.html#members">社友介紹</a></li><li><a href="../index.html#impact-hub">服務計畫</a></li> </ul> </div> <div> <p class="foot-title">版本資訊</p> <ul> <li>2024-2026 永續影響力報告書</li> <li>2026 年 5 月發行</li> <li>持續更新中</li> </ul> </div> <div class="copyright">© 2024-2026 台北永續影響力扶輪社 3481</div> </div> </footer>

<div class="mt-lb" id="mt-lb" role="dialog" aria-modal="true" aria-label="照片放大"><button class="x" aria-label="關閉">×</button><button class="p" aria-label="上一張">‹</button><img alt=""><button class="n" aria-label="下一張">›</button><p class="mt-lb-cap"></p></div>
<script>{JS}</script>
</body></html>
'''
(OUT / "meetings").mkdir(exist_ok=True)
(OUT / "meetings" / "index.html").write_text(page)
print("events", n_events, "photos", n_photos, "max_no", max_no)
for e in events.values():
    print(e["date"], e["title"], len(e["photos"]), e["cat"], "★" if e["big"] else "")
