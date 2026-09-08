#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V7 部署前品質閘門。任何一項失敗 → exit 1，不要部署。

檢查項目：
  1. 內部斷鏈：全站 HTML 的相對 href/src 都要指到實際存在的檔案
     （/_vercel/ 為 Vercel 執行期路徑，排除）
  2. 中英對稱：profiles/ 與 services/ 中英檔名集合必須一致；
     根層每個內容頁 en/ 都要有對應鏡像
     （BACKEND_ONLY 的單語內部後台頁除外）
  3. sitemap 覆蓋：sitemap.xml 列出的每個 URL 都要有對應本地檔案
  4. build 標記完整：每個內容頁都要有 SITE-HEADER / SITE-FOOTER / SITE-HEAD
     標記（缺了 build.py 會靜默跳過，這裡把它變成硬錯誤）
  5. 後台頁防回歸：BACKEND_ONLY 的頁不得被列進 sitemap、不得被埋追蹤碼
     （語言切換不重複驗，它會指向不存在的 en/<page>，第 1 項必然命中）

用法：cd v7 && python3 _build/check.py
"""
import os
import re
import sys
from urllib.parse import unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # = v7/
BASE_URL = "https://3481rctsi.vercel.app"

# 單語內部後台頁：不對外、不進 sitemap、沒有英文鏡像、沒有 footer。
# 對外雙語內容頁的規則（中英對稱、footer 標記）對它不適用。
BACKEND_ONLY = {"stats.html"}

errors = []


def html_pages():
    for dirpath, dirs, files in os.walk(ROOT):
        if "_build" in dirpath:
            continue
        for f in files:
            if f.endswith(".html"):
                yield os.path.join(dirpath, f)


# 1. 內部斷鏈
ref_count = 0
for page in html_pages():
    content = open(page, encoding="utf-8", errors="ignore").read()
    for m in re.finditer(r'(?:href|src)="([^"#?]+)', content):
        u = m.group(1)
        if u.startswith(("http", "mailto:", "tel:", "data:", "//", "javascript:", "/_vercel")):
            continue
        ref_count += 1
        if u.startswith("/"):
            target = os.path.normpath(os.path.join(ROOT, unquote(u).lstrip("/")))
        else:
            target = os.path.normpath(os.path.join(os.path.dirname(page), unquote(u)))
        if not os.path.exists(target):
            errors.append(f"[斷鏈] {os.path.relpath(page, ROOT)} -> {u}")

# 2. 中英對稱
for sub in ("profiles", "services"):
    zh = set(os.listdir(os.path.join(ROOT, sub)))
    en = set(os.listdir(os.path.join(ROOT, "en", sub)))
    for name in sorted(zh - en):
        errors.append(f"[中英不對稱] {sub}/{name} 沒有英文鏡像 en/{sub}/{name}")
    for name in sorted(en - zh):
        errors.append(f"[中英不對稱] en/{sub}/{name} 沒有中文對應 {sub}/{name}")

zh_root = {f for f in os.listdir(ROOT) if f.endswith(".html")} - BACKEND_ONLY
en_root = {f for f in os.listdir(os.path.join(ROOT, "en")) if f.endswith(".html")} - BACKEND_ONLY
for name in sorted(zh_root - en_root):
    errors.append(f"[中英不對稱] 根層 {name} 沒有英文鏡像 en/{name}")
for name in sorted(en_root - zh_root):
    errors.append(f"[中英不對稱] en/{name} 沒有中文對應 {name}")

# 3. sitemap 覆蓋
sitemap_path = os.path.join(ROOT, "sitemap.xml")
if not os.path.exists(sitemap_path):
    errors.append("[sitemap] sitemap.xml 不存在（先跑 _build/build.py）")
else:
    sitemap = open(sitemap_path, encoding="utf-8").read()
    for loc in re.findall(r"<loc>([^<]+)</loc>", sitemap):
        rel = loc.replace(BASE_URL, "").lstrip("/")
        target = os.path.join(ROOT, unquote(rel)) if rel else os.path.join(ROOT, "index.html")
        if not os.path.exists(target):
            errors.append(f"[sitemap] 列了不存在的頁面：{loc}")

# 4. build 標記完整
MARKS = ("<!--SITE-HEADER:START-->", "<!--SITE-FOOTER:START-->", "<!--SITE-HEAD:START-->")
for page in html_pages():
    content = open(page, encoding="utf-8", errors="ignore").read()
    marks = MARKS
    if os.path.relpath(page, ROOT) in BACKEND_ONLY:
        marks = tuple(m for m in MARKS if "FOOTER" not in m)
    missing = [m for m in marks if m not in content]
    if missing:
        errors.append(f"[缺標記] {os.path.relpath(page, ROOT)}: {', '.join(missing)}")

# 5. 後台頁防回歸
#    2026-09 事故：新增 stats.html 時整套後台頁規則沒跟上，CI 連五次失敗、
#    線上英文頁 31 條斷鏈。build.py 的 BACKEND_ONLY 保護一旦被改掉，這裡要響。
#    ⚠️ 只驗兩項。語言切換不驗：它會指向不存在的 en/<page>，第 1 項斷鏈檢查必然命中，
#       重複做只是多一份要維護的東西。
TRACKER_IN_HEAD = ("googletagmanager.com", "/_vercel/insights", "/_vercel/speed-insights")
HEAD_START, HEAD_END = "<!--SITE-HEAD:START-->", "<!--SITE-HEAD:END-->"
for name in sorted(BACKEND_ONLY):
    page = os.path.join(ROOT, name)
    if not os.path.exists(page):
        continue
    content = open(page, encoding="utf-8", errors="ignore").read()

    # 5a. 不該進 sitemap：內部後台頁被搜尋引擎收錄等於對外曝光
    if os.path.exists(sitemap_path):
        sm = open(sitemap_path, encoding="utf-8").read()
        if f"<loc>{BASE_URL}/{name}</loc>" in sm:
            errors.append(f"[後台頁回歸] {name} 被列進 sitemap.xml，內部頁不該被收錄")

    # 5b. 不該被埋追蹤碼：這頁的用途就是看流量，自己被埋點會把查數據算成訪客。
    #     只看 SITE-HEAD 區塊內的 script 來源，不全文掃關鍵字——
    #     這頁本身是流量儀表板，正文出現 analytics 字樣是正常的，全文掃會誤報。
    i, j = content.find(HEAD_START), content.find(HEAD_END)
    head = content[i:j] if i != -1 and j != -1 else ""
    hit = [t for t in TRACKER_IN_HEAD if t in head]
    if hit:
        errors.append(f"[後台頁回歸] {name} 的 SITE-HEAD 被埋了追蹤碼：{', '.join(hit)}")

# 結果
if errors:
    print(f"❌ 檢查失敗，共 {len(errors)} 項（掃描 {ref_count} 個內部引用）：")
    for e in errors:
        print("  " + e)
    sys.exit(1)
print(f"✅ 全部通過：{ref_count} 個內部引用無斷鏈、中英對稱、sitemap 覆蓋完整、build 標記齊全")
