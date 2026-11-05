#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V7 單一來源產生器（B 架構）

用法：  cd v7 && python3 _build/build.py

做什麼（每次跑都會做、可重複跑 idempotent）：
  1. 頁首 <header class="topbar"> / 頁尾 <footer> 整段換成 _build/templates/ 模板產出
     （中文頁用 .zh、en/ 下用 .en）。
  2. 設正確 <html lang>（en/ → en；其餘 → zh-Hant）。
  3. <head> 注入 SEO/GEO：canonical、hreflang（zh-Hant / en / x-default 雙向）、
     Open Graph、JSON-LD（Organization + WebSite）。
  4. 產生 sitemap.xml（含 hreflang 替代連結）與 robots.txt（放行一般與 AI 爬蟲）。

改導航/簽名檔 → 只改 templates/ → 跑這支 → 全站中英一起更新。

⚠️ 部署網域：下方 BASE_URL 預設指向目前正式官網。若 V7 部署到別的網址，
   改這一個常數再跑一次 build 即可，hreflang/canonical/sitemap 全部跟著更新。
"""
import os, re, html, json
import members_render

# ====== 設定 ======
BASE_URL = "https://rctsi.3481.org"   # ⚠️ V7 若換網址，改這裡再 rebuild

SITE_NAME = {
    "zh": "台北永續影響力扶輪社",
    "en": "Rotary Club of Taipei Sustainable Impact",
}
OG_LOCALE = {"zh": "zh_TW", "en": "en_US"}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # = v7/
TPL  = os.path.join(ROOT, "_build", "templates")

def load(name):
    with open(os.path.join(TPL, name), encoding="utf-8") as f:
        return f.read().strip()

TEMPLATES = {
    ("zh", "header"): load("header.zh.html"),
    ("zh", "footer"): load("footer.zh.html"),
    ("en", "header"): load("header.en.html"),
    ("en", "footer"): load("footer.en.html"),
}

HEADER_MARK = ("<!--SITE-HEADER:START-->", "<!--SITE-HEADER:END-->")
FOOTER_MARK = ("<!--SITE-FOOTER:START-->", "<!--SITE-FOOTER:END-->")
HEAD_MARK   = ("<!--SITE-HEAD:START-->",   "<!--SITE-HEAD:END-->")

# 單語內部後台頁：不對外、不進 sitemap、沒有英文鏡像、不埋追蹤碼、沒有語言切換。
# ⚠️ _build/check.py 有一份同名的 BACKEND_ONLY，兩邊要一起改。
BACKEND_ONLY = {"stats.html"}

def iter_pages():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        if os.sep + "_build" in dirpath or dirpath.endswith("_build"):
            continue
        for fn in filenames:
            if fn.endswith(".html"):
                yield os.path.join(dirpath, fn)

def page_vars(abspath):
    rel = os.path.relpath(abspath, ROOT).replace(os.sep, "/")   # en/profiles/01.html
    lang = "en" if rel.startswith("en/") else "zh"
    tree_rel = rel[len("en/"):] if lang == "en" else rel
    depth = tree_rel.count("/")
    REL = "../" * depth
    lang_href = (REL + "en/" + tree_rel) if lang == "zh" else ("../" + REL + tree_rel)
    return rel, lang, tree_rel, REL, lang_href

def url_of(lang, tree_rel):
    """對外網址一律不帶 .html：Cloudflare Pages 會把 .html 308 轉到無副檔名，
    canonical／hreflang／og:url／sitemap／JSON-LD 都要寫最終網址（2026-11 4O 修正）。"""
    path = tree_rel
    if path == "index.html" or path.endswith("/index.html"):
        path = path[:-len("index.html")]
    elif path.endswith(".html"):
        path = path[:-len(".html")]
    return BASE_URL + "/" + ("en/" if lang == "en" else "") + path


LASTMOD = {}   # (lang, tree_rel) → 正文最後修改日，給 sitemap 的 <lastmod>


def _person_index():
    """人物誌頁 → Person schema 資料。來源 members.json，社員異動只改那一份。"""
    idx = {}
    for sec in members_render.load_data()["sections"]:
        for card in sec.get("cards", []):
            prof = card.get("profile")
            if not prof:
                continue
            img = ""
            m = re.search(r"url\(([^)]+)\)", card.get("avatarStyle", "") or "")
            if m:
                img = m.group(1).strip("'\"")
            idx[prof] = {"name": card["name"], "role": card["role"],
                         "theme": card.get("theme", {}), "image": img}
    return idx


PERSONS = _person_index()


def person_jsonld(lang, tree_rel):
    """人物誌頁的 Person 結構化資料；非人物誌頁回 None。"""
    p = PERSONS.get(tree_rel)
    if not p:
        return None
    def lv(v):
        return v.get(lang, v.get("zh", "")) if isinstance(v, dict) else (v or "")
    desc = lv(p["theme"]).split("。")[0]
    data = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": lv(p["name"]),
        "jobTitle": lv(p["role"]),
        "url": url_of(lang, tree_rel),
        "memberOf": {
            "@type": "Organization",
            "name": "Rotary Club of Taipei Sustainable Impact",
            "alternateName": "台北永續影響力扶輪社",
            "url": BASE_URL + "/",
        },
    }
    if desc:
        data["description"] = desc
    if p["image"]:
        data["image"] = BASE_URL + "/" + p["image"]

    # sameAs / affiliation：從該頁的社群 chip 抽出來
    # 個人帳號進 sameAs（讓 AI 確認跨平台是同一人），組織連結進 affiliation
    same, orgs = [], []
    page_path = os.path.join(ROOT, ("en/" if lang == "en" else "") + tree_rel)
    try:
        page = open(page_path, encoding="utf-8").read()
    except OSError:
        page = ""
    for m in re.finditer(r'<a class="social-chip"[^>]*?href="(https://[^"]+)"[^>]*?aria-label="([^"]*)"', page):
        url, label = m.group(1), m.group(2)
        if url in same or any(o.get("url") == url for o in orgs):
            continue
        if "個人" in label or "personal" in label.lower():
            same.append(url)
        else:
            orgs.append({"@type": "Organization", "name": label, "url": url})
    if same:
        data["sameAs"] = same
    if orgs:
        data["affiliation"] = orgs if len(orgs) > 1 else orgs[0]
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def page_exists(lang, tree_rel):
    """對應語言的頁面是否真的存在。單語頁（例如 agent.html 只有中文）
    不能產生指向不存在檔案的 hreflang，否則是壞的 SEO 訊號。"""
    return os.path.exists(os.path.join(ROOT, ("en/" if lang == "en" else "") + tree_rel))

def render(lang, part, REL, lang_href):
    s = TEMPLATES[(lang, part)]
    return s.replace("{{REL}}", REL).replace("{{LANG_HREF}}", lang_href)

def replace_block(content, rendered, marks, legacy_pattern, label, relname):
    start, end = marks
    wrapped = start + "\n" + rendered + "\n" + end
    if start in content and end in content:
        return re.sub(re.escape(start) + r".*?" + re.escape(end),
                      lambda m: wrapped, content, count=1, flags=re.S)
    m = re.search(legacy_pattern, content, flags=re.S)
    if m:
        return content[:m.start()] + wrapped + content[m.end():]
    print(f"  ⚠️ {relname}：找不到 {label}，跳過")
    return content

ORG = {"@type": "Organization", "name": "Rotary Club of Taipei Sustainable Impact",
       "alternateName": "台北永續影響力扶輪社", "url": BASE_URL + "/"}
DEFAULT_IMAGE = BASE_URL + "/assets/img/yongli-logo.png"

def _strip(t):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t))).strip()

def own_description(content):
    """頁面原本自己寫的 meta description（SITE-HEAD 區塊以外）。"""
    outside = re.sub(re.escape(HEAD_MARK[0]) + r".*?" + re.escape(HEAD_MARK[1]), "", content, flags=re.S)
    m = re.search(r'<meta name="description" content="([^"]*)"', outside)
    return html.unescape(m.group(1)).strip() if m else None

def auto_description(content, lang):
    """沒寫 description 的頁，從正文第一段夠長的 <p> 擷取，不另寫新字。"""
    body = re.sub(r"<!--SITE-(HEADER|FOOTER):START-->.*?<!--SITE-\1:END-->", "", content, flags=re.S)
    body = re.sub(r"<(script|style)\b.*?</\1>", "", body, flags=re.S)
    h1 = re.search(r"</h1>", body)
    if h1:
        body = body[h1.end():]
    limit, floor = (155, 80) if lang == "en" else (110, 50)
    for m in re.finditer(r"<p\b([^>]*)>(.*?)</p>", body, flags=re.S):
        if re.search(r'class="[^"]*(eyebrow|label|kicker|caption|tag|meta|quote|credit|proposer)', m.group(1)):
            continue
        t = _strip(m.group(2))
        if re.match(r"(Proposer|提案人)\s*[·・]", t):
            continue
        if len(t) >= floor:
            if len(t) > limit:
                cut = t[:limit]
                stop = max(cut.rfind(c) for c in ("。", "，", ". ", ", ", "；"))
                t = (cut[:stop + 1] if stop > limit * 0.5 else cut).rstrip(" ,，、") + "…"
            return t
    return None

def _body_text(page_html):
    """正文純文字：去掉 build 注入的頁首、導覽、頁尾、script/style 與標籤，網域統一，
    只要正文字面沒變就視為同一版內容。"""
    t = re.sub(r"<!--SITE-(HEAD|HEADER|FOOTER):START-->.*?<!--SITE-\1:END-->", "", page_html, flags=re.S)
    t = re.sub(r"<(head|script|style|header|footer|nav)\b.*?</\1>", "", t, flags=re.S | re.I)
    t = t.replace("3481rctsi.vercel.app", "rctsi.3481.org")
    return _strip(t)

def last_content_date(rel, content=""):
    """正文最後一次真的有改的 commit 日期：逐版比對正文純文字，跟前一版不同的最新那版。
    只有一版就用那版（新建頁）。淺層 clone 或 git 讀不到時，沿用頁面上已記的日期
    （沒有就不寫），避免淺層邊界被當成建立日期、也讓 build 結果跟已 commit 的一致。"""
    import subprocess
    def git(*args):
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                              text=True, timeout=30).stdout
    m = re.search(r'"@type":"WebPage".*?"dateModified":"([^"]+)"', content)
    kept = m.group(1) if m else None
    try:
        if git("rev-parse", "--is-shallow-repository").strip() != "false":
            return kept
        log = [l.split(" ", 1) for l in git("log", "--format=%H %cI", "--", rel).splitlines() if l]
        if not log:
            return kept
        texts = [_body_text(git("show", f"{h}:v7/{rel}")) for h, _ in log]
    except Exception:
        return kept
    for i, (h, date) in enumerate(log):
        if i + 1 == len(log) or texts[i] != texts[i + 1]:
            return date
    return None

def head_block(lang, tree_rel, title_text, content="", rel=""):
    self_url = url_of(lang, tree_rel)
    zh_url = url_of("zh", tree_rel)
    en_url = url_of("en", tree_rel)
    t = html.escape(title_text, quote=True)
    other = "en" if lang == "zh" else "zh"
    jsonld = (
        '{"@context":"https://schema.org","@type":"WebSite",'
        f'"name":"{SITE_NAME[lang]}","url":"{BASE_URL}/",'
        f'"inLanguage":"{"zh-Hant" if lang=="zh" else "en"}",'
        '"publisher":{"@type":"Organization",'
        '"name":"Rotary Club of Taipei Sustainable Impact",'
        f'"url":"{BASE_URL}/"}}}}'
    )
    bilingual = page_exists("zh", tree_rel) and page_exists("en", tree_rel)
    lines = [
        HEAD_MARK[0],
        f'<link rel="canonical" href="{self_url}">',
    ]
    if bilingual:
        lines += [
            f'<link rel="alternate" hreflang="zh-Hant" href="{zh_url}">',
            f'<link rel="alternate" hreflang="en" href="{en_url}">',
            f'<link rel="alternate" hreflang="x-default" href="{zh_url}">',
        ]
    lines += [
        '<meta property="og:type" content="website">',
        f'<meta property="og:site_name" content="{html.escape(SITE_NAME[lang],quote=True)}">',
        f'<meta property="og:locale" content="{OG_LOCALE[lang]}">',
        f'<meta property="og:locale:alternate" content="{OG_LOCALE[other]}">',
        f'<meta property="og:title" content="{t}">',
        f'<meta property="og:url" content="{self_url}">',
    ]
    desc = own_description(content)
    if desc is None:
        desc = auto_description(content, lang)
        if desc:
            lines.append(f'<meta name="description" content="{html.escape(desc, quote=True)}">')
    person_img = (PERSONS.get(tree_rel) or {}).get("image")
    image = BASE_URL + "/" + person_img if person_img else DEFAULT_IMAGE
    if desc:
        lines.append(f'<meta property="og:description" content="{html.escape(desc, quote=True)}">')
    lines += [
        f'<meta property="og:image" content="{image}">',
        '<meta name="twitter:card" content="summary">',
        f'<script type="application/ld+json">{jsonld}</script>',
    ]
    if tree_rel not in BACKEND_ONLY:
        page = {"@context": "https://schema.org", "@type": "WebPage",
                "name": title_text, "url": self_url,
                "inLanguage": "zh-Hant" if lang == "zh" else "en",
                "isPartOf": {"@type": "WebSite", "url": BASE_URL + "/"},
                "author": ORG, "publisher": ORG, "image": image}
        if desc:
            page["description"] = desc
        modified = last_content_date(rel, content)
        if modified:
            page["dateModified"] = modified
            LASTMOD[(lang, tree_rel)] = modified[:10]
        lines.append('<script type="application/ld+json">'
                     + json.dumps(page, ensure_ascii=False, separators=(",", ":")) + '</script>')
    if tree_rel == "index.html":
        org = {"@context": "https://schema.org", "@type": "Organization",
               "name": "Rotary Club of Taipei Sustainable Impact",
               "alternateName": ["台北永續影響力扶輪社", "永力社"],
               "url": BASE_URL + "/", "logo": DEFAULT_IMAGE, "foundingDate": "2024",
               "parentOrganization": {"@type": "Organization", "name": "Rotary International District 3481"}}
        lines.append('<script type="application/ld+json">'
                     + json.dumps(org, ensure_ascii=False, separators=(",", ":")) + '</script>')
    person = person_jsonld(lang, tree_rel)
    if person:
        lines.append(f'<script type="application/ld+json">{person}</script>')
    # ===== 流量追蹤（全站共用，每頁自動帶）=====
    # ⚠️ 後台流量查詢頁 stats.html 完全不埋點：這頁的用途就是看流量，
    #    自己被埋點會把「查數據」這個動作算成訪客，污染自己要看的統計。
    #    密碼擋不住：gtag 在 head，密碼輸入框在 body，驗證前就已送出 page_view。
    #    noindex 只影響搜尋引擎收錄，跟追蹤無關。
    if tree_rel not in BACKEND_ONLY:
        lines += [
            # GA4（property「永力社永續報告書官網」, Measurement ID G-1RCWR62S07, 帳戶 David a27882089）
            '<!-- Google tag (gtag.js) -->',
            '<script async src="https://www.googletagmanager.com/gtag/js?id=G-1RCWR62S07"></script>',
            "<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-1RCWR62S07');</script>",
        ]
    lines.append(HEAD_MARK[1])
    return "\n".join(lines)

def inject_head(content, block):
    start, end = HEAD_MARK
    if start in content and end in content:
        return re.sub(re.escape(start) + r".*?" + re.escape(end),
                      lambda m: block, content, count=1, flags=re.S)
    # 插在 </head> 前
    i = content.lower().find("</head>")
    if i == -1:
        print("  ⚠️ 找不到 </head>，跳過 head 注入")
        return content
    return content[:i] + block + "\n" + content[i:]

def write_sitemap(pages_meta):
    # pages_meta: list of (lang, tree_rel)
    seen = set(); entries = []
    for lang, tree_rel in pages_meta:
        loc = url_of(lang, tree_rel)
        if loc in seen: continue
        seen.add(loc)
        zh_url = url_of("zh", tree_rel); en_url = url_of("en", tree_rel)
        alt = ""
        if page_exists("zh", tree_rel) and page_exists("en", tree_rel):
            alt = (f'    <xhtml:link rel="alternate" hreflang="zh-Hant" href="{zh_url}"/>\n'
                   f'    <xhtml:link rel="alternate" hreflang="en" href="{en_url}"/>\n'
                   f'    <xhtml:link rel="alternate" hreflang="x-default" href="{zh_url}"/>\n')
        lm = LASTMOD.get((lang, tree_rel))
        entries.append(
            "  <url>\n"
            f"    <loc>{loc}</loc>\n"
            + (f"    <lastmod>{lm}</lastmod>\n" if lm else "")
            + alt +
            "  </url>"
        )
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
           'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
           + "\n".join(entries) + "\n</urlset>\n")
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(xml)
    return len(seen)

def write_robots():
    txt = (
        "# Rotary Club of Taipei Sustainable Impact — public report site\n"
        "User-agent: *\n"
        "Allow: /\n\n"
        "# Welcome generative AI engines (this is a public report)\n"
        "User-agent: GPTBot\nAllow: /\n\n"
        "User-agent: OAI-SearchBot\nAllow: /\n\n"
        "User-agent: ChatGPT-User\nAllow: /\n\n"
        "User-agent: ClaudeBot\nAllow: /\n\n"
        "User-agent: Claude-Web\nAllow: /\n\n"
        "User-agent: PerplexityBot\nAllow: /\n\n"
        "User-agent: Google-Extended\nAllow: /\n\n"
        "User-agent: Applebot-Extended\nAllow: /\n\n"
        f"Sitemap: {BASE_URL}/sitemap.xml\n\n"
        "# AI 接待入口（AXO）：代替訪客閱讀本站的 AI，請先讀這兩個檔\n"
        f"# {BASE_URL}/llms.txt\n"
        f"# {BASE_URL}/agent.html\n"
    )
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(txt)

def main():
    pages = sorted(iter_pages())
    stats = {"zh": 0, "en": 0}; pages_meta = []; samples = []
    page_titles = {}   # 給 /stats.html 用：路徑 → 頁面標題
    for p in pages:
        rel, lang, tree_rel, REL, lang_href = page_vars(p)
        with open(p, encoding="utf-8") as f:
            content = f.read()
        # lang
        want = "en" if lang == "en" else "zh-Hant"
        content = re.sub(r'(<html[^>]*\blang=")[^"]*(")',
                         lambda m: m.group(1) + want + m.group(2), content, count=1)
        # header / footer
        header_html = render(lang,"header",REL,lang_href)
        # 後台流量查詢頁是單語內部頁，沒有英文鏡像，
        # 保留語言切換會連到不存在的 en/stats.html（斷鏈）。
        if tree_rel in BACKEND_ONLY:
            header_html = re.sub(r'<a class="lang-switch".*?</a>\s*', '', header_html, flags=re.S)
        content = replace_block(content, header_html,
                                HEADER_MARK, r'<header class="topbar">.*?</header>', "header", rel)
        content = replace_block(content, render(lang,"footer",REL,lang_href),
                                FOOTER_MARK, r'<footer\b.*?</footer>', "footer", rel)
        # 社員名冊（資料驅動：_build/data/members.json，只有 members.html 有標記）
        content = members_render.apply_members(content, lang)
        # head SEO/GEO
        tm = re.search(r'<title>(.*?)</title>', content, flags=re.S)
        title_text = tm.group(1).strip() if tm else SITE_NAME[lang]
        content = inject_head(content, head_block(lang, tree_rel, title_text, content, rel))
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        stats[lang] += 1
        # 後台流量查詢頁是 noindex 的內部頁，不該出現在 sitemap
        if tree_rel not in BACKEND_ONLY:
            pages_meta.append((lang, tree_rel))
        # 後台流量查詢頁要把 /profiles/xxx.html 翻成人看得懂的名字，這裡順手收一份。
        # ⚠️ 用 rel 不能用 tree_rel：tree_rel 對英文頁已經去掉 en/ 前綴，
        #    中英文會共用同一個 key，後跑的英文標題會蓋掉中文的。
        _t = title_text.split("｜")[0].split(" | ")[0].strip()
        _u = "/" + rel
        if _u.endswith("/index.html"):
            _u = _u[:-10]
        page_titles[_u] = {"title": _t, "lang": lang}
        if len(samples) < 4:
            samples.append(f"  {rel}  canonical={url_of(lang,tree_rel)}  ↔ {lang_href}")
    n = write_sitemap(pages_meta); write_robots()
    with open(os.path.join(ROOT, "page-titles.json"), "w", encoding="utf-8") as f:
        json.dump(page_titles, f, ensure_ascii=False, indent=1)
    print(f"✅ build 完成：中文 {stats['zh']} 頁、英文 {stats['en']} 頁")
    print(f"   sitemap.xml（{n} URLs）+ robots.txt + page-titles.json（{len(page_titles)} 筆）已產生  | BASE_URL={BASE_URL}")
    print("路徑抽樣：\n" + "\n".join(samples))

if __name__ == "__main__":
    main()
