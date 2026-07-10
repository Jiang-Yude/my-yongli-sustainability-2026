#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V7 部署前品質閘門。任何一項失敗 → exit 1，不要部署。

檢查項目：
  1. 內部斷鏈：全站 HTML 的相對 href/src 都要指到實際存在的檔案
     （/_vercel/ 為 Vercel 執行期路徑，排除）
  2. 中英對稱：profiles/ 與 services/ 中英檔名集合必須一致；
     根層每個內容頁 en/ 都要有對應鏡像
  3. sitemap 覆蓋：sitemap.xml 列出的每個 URL 都要有對應本地檔案
  4. build 標記完整：每個內容頁都要有 SITE-HEADER / SITE-FOOTER / SITE-HEAD
     標記（缺了 build.py 會靜默跳過，這裡把它變成硬錯誤）

用法：cd v7 && python3 _build/check.py
"""
import os
import re
import sys
from urllib.parse import unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # = v7/
BASE_URL = "https://3481rctsi.vercel.app"

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

zh_root = {f for f in os.listdir(ROOT) if f.endswith(".html")}
en_root = {f for f in os.listdir(os.path.join(ROOT, "en")) if f.endswith(".html")}
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
    missing = [m for m in MARKS if m not in content]
    if missing:
        errors.append(f"[缺標記] {os.path.relpath(page, ROOT)}: {', '.join(missing)}")

# 結果
if errors:
    print(f"❌ 檢查失敗，共 {len(errors)} 項（掃描 {ref_count} 個內部引用）：")
    for e in errors:
        print("  " + e)
    sys.exit(1)
print(f"✅ 全部通過：{ref_count} 個內部引用無斷鏈、中英對稱、sitemap 覆蓋完整、build 標記齊全")
