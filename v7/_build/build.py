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
import os, re, html
import members_render

# ====== 設定 ======
BASE_URL = "https://3481rctsi.vercel.app"   # ⚠️ V7 若換網址，改這裡再 rebuild

SITE_NAME = {
    "zh": "台北永續影響力扶輪社｜永續影響力報告書",
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
    return BASE_URL + "/" + ("en/" if lang == "en" else "") + tree_rel

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

def head_block(lang, tree_rel, title_text):
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
    lines = [
        HEAD_MARK[0],
        f'<link rel="canonical" href="{self_url}">',
        f'<link rel="alternate" hreflang="zh-Hant" href="{zh_url}">',
        f'<link rel="alternate" hreflang="en" href="{en_url}">',
        f'<link rel="alternate" hreflang="x-default" href="{zh_url}">',
        '<meta property="og:type" content="website">',
        f'<meta property="og:site_name" content="{html.escape(SITE_NAME[lang],quote=True)}">',
        f'<meta property="og:locale" content="{OG_LOCALE[lang]}">',
        f'<meta property="og:locale:alternate" content="{OG_LOCALE[other]}">',
        f'<meta property="og:title" content="{t}">',
        f'<meta property="og:url" content="{self_url}">',
        '<meta name="twitter:card" content="summary">',
        f'<script type="application/ld+json">{jsonld}</script>',
        # ===== 流量追蹤（全站共用，每頁自動帶）=====
        # GA4（property「永力社永續報告書官網」, Measurement ID G-1RCWR62S07, 帳戶 David a27882089）
        '<!-- Google tag (gtag.js) -->',
        '<script async src="https://www.googletagmanager.com/gtag/js?id=G-1RCWR62S07"></script>',
        "<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-1RCWR62S07');</script>",
        # Vercel Web Analytics + Speed Insights（需在 Vercel 專案後台開啟 Analytics 才會 serve script）
        '<script defer src="/_vercel/insights/script.js"></script>',
        '<script defer src="/_vercel/speed-insights/script.js"></script>',
        HEAD_MARK[1],
    ]
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
        entries.append(
            "  <url>\n"
            f"    <loc>{loc}</loc>\n"
            f'    <xhtml:link rel="alternate" hreflang="zh-Hant" href="{zh_url}"/>\n'
            f'    <xhtml:link rel="alternate" hreflang="en" href="{en_url}"/>\n'
            f'    <xhtml:link rel="alternate" hreflang="x-default" href="{zh_url}"/>\n'
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
        f"Sitemap: {BASE_URL}/sitemap.xml\n"
    )
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(txt)

def main():
    pages = sorted(iter_pages())
    stats = {"zh": 0, "en": 0}; pages_meta = []; samples = []
    for p in pages:
        rel, lang, tree_rel, REL, lang_href = page_vars(p)
        with open(p, encoding="utf-8") as f:
            content = f.read()
        # lang
        want = "en" if lang == "en" else "zh-Hant"
        content = re.sub(r'(<html[^>]*\blang=")[^"]*(")',
                         lambda m: m.group(1) + want + m.group(2), content, count=1)
        # header / footer
        content = replace_block(content, render(lang,"header",REL,lang_href),
                                HEADER_MARK, r'<header class="topbar">.*?</header>', "header", rel)
        content = replace_block(content, render(lang,"footer",REL,lang_href),
                                FOOTER_MARK, r'<footer\b.*?</footer>', "footer", rel)
        # 社員名冊（資料驅動：_build/data/members.json，只有 members.html 有標記）
        content = members_render.apply_members(content, lang)
        # head SEO/GEO
        tm = re.search(r'<title>(.*?)</title>', content, flags=re.S)
        title_text = tm.group(1).strip() if tm else SITE_NAME[lang]
        content = inject_head(content, head_block(lang, tree_rel, title_text))
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        stats[lang] += 1; pages_meta.append((lang, tree_rel))
        if len(samples) < 4:
            samples.append(f"  {rel}  canonical={url_of(lang,tree_rel)}  ↔ {lang_href}")
    n = write_sitemap(pages_meta); write_robots()
    print(f"✅ build 完成：中文 {stats['zh']} 頁、英文 {stats['en']} 頁")
    print(f"   sitemap.xml（{n} URLs）+ robots.txt 已產生  | BASE_URL={BASE_URL}")
    print("路徑抽樣：\n" + "\n".join(samples))

if __name__ == "__main__":
    main()
