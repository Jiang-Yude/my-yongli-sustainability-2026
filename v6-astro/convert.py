#!/usr/bin/env python3
"""
v6/*.html → v6-astro/src/pages/*.astro 批次轉換

策略：
- 提取 title / description / inline style
- 提取 body 內容（去掉 header 跟 footer，這兩個由 BaseLayout 提供）
- 包進 BaseLayout，子頁傳 pathPrefix='../'
- inline style 用 <style is:global> 保留
- inline JS（如果在 body 結尾）保留在 slot 內
"""
import re
import os
from pathlib import Path

ROOT = Path("/Users/jiangyude2/Library/Mobile Documents/com~apple~CloudDocs/暫存/yongli-sustainability-2026")
V6 = ROOT / "v6"
PAGES = ROOT / "v6-astro" / "src" / "pages"

# (source path 相對 v6/, target path 相對 src/pages/, is_subpage)
TASKS = [
    # 主頁 7 個（about-yongli 已 PoC 做過、跳過）
    ("index.html", "index.astro", False),
    ("members.html", "members.astro", False),
    ("methodology.html", "methodology.astro", False),
    ("cases.html", "cases.astro", False),
    ("disclosure-framework.html", "disclosure-framework.astro", False),
    ("member-guide.html", "member-guide.astro", False),
    ("analysis.html", "analysis.astro", False),
]

# profiles 15 個
PROFILES = [
    "01-cp-lin", "02-vicky-lee", "03-derek-huang", "04-helen-lai",
    "05-lisa-lin", "06-james-gao", "07-nick-lin", "08-rich-huang",
    "09-vincent-chen", "10-albee-chang", "13-teresa-yao", "15-wayne-lin",
    "16-eric-cheng", "18-meiya-cheng", "19-irene-chen",
]
for p in PROFILES:
    TASKS.append((f"profiles/{p}.html", f"profiles/{p}.astro", True))

# services 7 個
SERVICES = [
    "01-zhongyi", "02-tamsui", "03-eco-edu", "04-life-warrior",
    "05-dental", "06-community", "07-zero-waste-mazu",
]
for s in SERVICES:
    TASKS.append((f"services/{s}.html", f"services/{s}.astro", True))


def extract_title(html):
    m = re.search(r'<title>([^<]+)</title>', html)
    return m.group(1).strip() if m else "Untitled"


def extract_description(html):
    m = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', html)
    return m.group(1).strip() if m else None


def extract_inline_styles(html):
    """提取所有 <style>...</style> 區塊內容"""
    styles = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL)
    return '\n'.join(s.strip() for s in styles).strip()


def extract_body_content(html):
    """提取 <body> 內容，去掉 <header>...</header> 跟 <footer>...</footer>"""
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
    if not body_match:
        return ""
    body = body_match.group(1)
    # 移除所有 header 區塊
    body = re.sub(r'<header[^>]*>.*?</header>', '', body, flags=re.DOTALL)
    # 移除所有 footer 區塊
    body = re.sub(r'<footer[^>]*>.*?</footer>', '', body, flags=re.DOTALL)
    return body.strip()


def detect_extra_fonts(html):
    """index.html 用了 Inter + 700 字重，要傳 extraGoogleFontWeights"""
    return 'family=Inter' in html or 'wght@400;500;600;700' in html and 'Inter' in html


def escape_astro_string(s):
    """字串放進 .astro frontmatter，需要處理引號"""
    if s is None:
        return None
    return s.replace('\\', '\\\\').replace('"', '\\"')


def convert_one(src_rel, tgt_rel, is_subpage):
    src = V6 / src_rel
    tgt = PAGES / tgt_rel
    if not src.exists():
        print(f"❌ 找不到: {src}")
        return False

    html = src.read_text(encoding='utf-8')

    title = extract_title(html)
    description = extract_description(html)
    inline_style = extract_inline_styles(html)
    body = extract_body_content(html)
    has_extra_fonts = detect_extra_fonts(html)

    # Astro frontmatter import 路徑（子頁深 1 層）
    layout_import = "../../layouts/BaseLayout.astro" if is_subpage else "../layouts/BaseLayout.astro"
    path_prefix = "../" if is_subpage else ""

    # 組裝 .astro
    title_escaped = escape_astro_string(title)
    description_attr = f'\n  description="{escape_astro_string(description)}"' if description else ""
    pathPrefix_attr = f'\n  pathPrefix="{path_prefix}"' if path_prefix else ""
    extraFonts_attr = '\n  extraGoogleFontWeights={true}' if has_extra_fonts else ""

    style_block = ""
    if inline_style:
        style_block = f"\n<style is:global>\n{inline_style}\n</style>\n"

    astro = f"""---
import BaseLayout from '{layout_import}';
---

<BaseLayout
  title="{title_escaped}"{description_attr}{pathPrefix_attr}{extraFonts_attr}
>
{style_block}
{body}

</BaseLayout>
"""

    tgt.parent.mkdir(parents=True, exist_ok=True)
    tgt.write_text(astro, encoding='utf-8')
    return True


def main():
    print(f"=== 批次轉換 {len(TASKS)} 個檔 ===\n")
    ok = 0
    fail = 0
    for src_rel, tgt_rel, is_subpage in TASKS:
        if convert_one(src_rel, tgt_rel, is_subpage):
            print(f"✅ {src_rel} → {tgt_rel}")
            ok += 1
        else:
            print(f"❌ {src_rel}")
            fail += 1
    print(f"\n總計：{ok} 成功 / {fail} 失敗")


if __name__ == "__main__":
    main()
