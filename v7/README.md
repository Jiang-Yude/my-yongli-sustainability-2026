# V7 中英雙語版 · 正式官網（目前線上版本）

正式官網：https://3481rctsi.vercel.app/ （中文）
英文版：https://3481rctsi.vercel.app/en/
GitHub Pages 鏡像（工作備存，非對外）：https://jiang-yude.github.io/my-yongli-sustainability-2026/v7/

> 本資料夾是**目前對外的唯一正式版本**（2026-05-31 上線，取代舊 v4）。
> 對外發布、教稿、商會推廣一律用 Vercel 網址。
> 曝光政策（2026-07-08 江江拍板）：本站刻意公開，含 sitemap、GA4、歡迎 AI 爬蟲，成員真名屬正常公開內容。

## 架構（B 架構：單一來源產生器）

- `_build/build.py`：全站頁首頁尾、`<head>` SEO（canonical / hreflang / OG / JSON-LD）、sitemap.xml、robots.txt 的唯一來源。可重複執行（idempotent）。
- `_build/templates/`：中英頁首頁尾模板。改導航或簽名檔只改這裡，然後跑 build。
- `_build/data/members.json`：**社員名冊唯一來源**（2026-07-10 起）。新增／修改社員只改這份 JSON，`members.html` 中英兩頁的社員卡由 build.py 自動重生，不要手改 HTML 的 MEMBERS 標記區。
- 中文頁在 v7 根層，英文鏡像在 `en/`（結構完全對稱）。英文源稿在 repo 根的 `_i18n-en/*.md`。
- `profiles/`：社員個人誌（中英各 15 頁，編號有跳號屬正常，部分社員尚無個人頁）。
- `services/`：七項服務計畫頁。
- 影片區塊：YouTube embed `efSFDYWcwG0`（2026-06-08 起，取代 Vimeo）。
- 流量：GA4 `G-1RCWR62S07` ＋ Vercel Web Analytics / Speed Insights。

## 修改與部署流程（鐵則：先 commit push、再 deploy）

```bash
cd /Users/jiangyude2/Developer/my-yongli-sustainability-2026/v7

# 1. 改內容（頁首頁尾改 _build/templates/，其餘直接改對應頁）
# 2. 重跑產生器
python3 _build/build.py

# 3. 品質檢查（斷鏈／中英對稱／build 冪等，任何一項失敗都不要部署）
python3 _build/check.py

# 4. commit + push（真相源是 GitHub main）
git add -A && git commit -m "..." && git push

# 5. 部署（若已接 Vercel Git integration，push 即自動部署，本步免跑）
/Users/jiangyude2/.npm-global/bin/vercel --prod --yes
```

- BASE_URL 在 `_build/build.py` 開頭，換網域改該常數再 rebuild。
- Vercel 專案：`jiang-coach/3481rctsi`（projectId `prj_AsFeRk75gQ05uaMojCLpSgpMyXWZ`），`v7/.vercel` 已 link。

## 版本沿革

v1（根目錄）、v2、v6 為歷史備存，只留在 GitHub Pages，不對外使用。v3/v4/v5/v6-astro 已於 2026-05-29 移除（git 歷史可還原）。舊版 README 對 v2/v4 的描述已隨 2026-07-10 文件真相修正移除，考古請看 git log。
