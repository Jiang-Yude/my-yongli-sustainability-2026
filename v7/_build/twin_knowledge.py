# -*- coding: utf-8 -*-
"""
分身知識來源產生器
-----------------------------------------------------------
把指定網頁的正文抽出來，寫成 api/_knowledge.js（Vercel Function 讀得到的模組）。

用法：cd v7 && python3 _build/twin_knowledge.py

來源分兩類：
  local  = 本 repo 內的頁面（直接讀檔）
  remote = 外部網址（抓取，抓不到就沿用上一版，不會把知識洗成空的）

要加新的分身知識，在 SOURCES 加一筆即可。
"""
import os, re, html, json, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # = v7/
OUT = os.path.join(ROOT, "api", "_knowledge.js")

SOURCES = {
    "secretary": [
        ("local", "index.html", "永力社官網首頁"),
        ("local", "about-yongli.html", "關於永力社"),
        ("local", "methodology.html", "影響力衡量方法"),
    ],
    "vicky": [
        ("local", "profiles/02-vicky-lee.html", "李琪 Vicky 在永力社的人物誌"),
        ("remote", "https://tamsuitraveler.vercel.app/", "旅學堂官網首頁"),
    ],
    # 英文站用的知識，key 為「人格_en」，後端依訪客語言取用
    "secretary_en": [
        ("local", "en/index.html", "Club homepage"),
        ("local", "en/about-yongli.html", "About the club"),
        ("local", "en/methodology.html", "Impact measurement methodology"),
    ],
    "vicky_en": [
        ("local", "en/profiles/02-vicky-lee.html", "Vicky Lee's member profile"),
        ("remote", "https://tamsuitraveler.vercel.app/", "Tamsui Traveler website (Chinese)"),
    ],
}


def clean(raw_html):
    """HTML → 純文字正文"""
    h = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", " ", raw_html, flags=re.S)
    # 頁首頁尾導覽不算內容
    h = re.sub(r"<header.*?</header>|<footer.*?</footer>|<nav.*?</nav>", " ", h, flags=re.S)
    h = re.sub(r"<(br|/p|/div|/section|/h[1-6]|/li)\s*/?>", "\n", h)
    txt = html.unescape(re.sub(r"<[^>]+>", " ", h))
    txt = re.sub(r"[ \t]+", " ", txt)
    txt = re.sub(r"\n\s*\n+", "\n", txt)
    return "\n".join(ln.strip() for ln in txt.split("\n") if ln.strip())


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "yongli-secretary-knowledge/1.0"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", "replace")


# 抓不到遠端時的保底：沿用上一版
previous = {}
if os.path.exists(OUT):
    m = re.search(r"module\.exports\s*=\s*(\{.*\});\s*$", open(OUT, encoding="utf-8").read(), re.S)
    if m:
        try:
            previous = json.loads(m.group(1))
        except Exception:
            previous = {}

result, log = {}, []
for persona, items in SOURCES.items():
    chunks = []
    for kind, target, label in items:
        try:
            raw = open(os.path.join(ROOT, target), encoding="utf-8").read() if kind == "local" else fetch(target)
            body = clean(raw)
            chunks.append("【" + label + "】\n" + body)
            log.append("  ✓ %-9s %s（%d 字）" % (persona, label, len(body)))
        except Exception as e:
            log.append("  ✗ %-9s %s 取得失敗：%s" % (persona, label, e))
            old = previous.get(persona, "")
            keep = re.search(r"【" + re.escape(label) + r"】\n(.*?)(?=\n【|\Z)", old, re.S)
            if keep:
                chunks.append("【" + label + "】\n" + keep.group(1).strip())
                log.append("      → 沿用上一版內容，知識未被清空")
    result[persona] = "\n\n".join(chunks)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write("// 由 _build/twin_knowledge.py 產生，請勿手改。\n")
    f.write("// 來源更新後重跑：cd v7 && python3 _build/twin_knowledge.py\n")
    f.write("module.exports = " + json.dumps(result, ensure_ascii=False, indent=1) + ";\n")

print("\n".join(log))
print("✅ 已寫出", os.path.relpath(OUT, ROOT), "｜", " ".join("%s=%d字" % (k, len(v)) for k, v in result.items()))
