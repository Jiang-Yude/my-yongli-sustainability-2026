# 給本機 Claude 的交接指令（永力社官網 1.0，2026-11-05）

把這整份貼給本機的 Claude Code 就可以開工。

---

你好，我是雲端那邊的 Claude。這份交接寫給在江江 Mac 上的你。

目標：永力社官網 1.0 在 11/28 社慶前上線，網址 rctsi.3481.org，部署在 Cloudflare。
雲端已經做好的東西都放在 GitHub 分支 `handoff/website-1.0` 的 `_handoff/2026-11-05/` 資料夾。這個分支只多了這個資料夾，其他檔案都沒動。

重要：GitHub 上的 v7 停在 10/19，BASE_URL 還是 vercel，比線上版舊。江江 Mac 上那份才是最新的原始檔，所有修改都要以本機版為準，不要用 GitHub main 覆蓋本機。

## 第 0 步：把雲端的成果拿下來

在本機官網資料夾執行（不要切換分支，只把資料夾拿過來）：

```bash
git fetch origin handoff/website-1.0
git checkout origin/handoff/website-1.0 -- _handoff/2026-11-05
```

先讀這兩份，裡面有完整脈絡：

- `_handoff/2026-11-05/reports/永力社官網1.0_工作交接.md`：檔案清單、要接的線、還沒確認的事。
- `_handoff/2026-11-05/faq/產生器修改說明_給本機版.md`：4O 修正要改產生器哪裡。

## 資料夾內容

| 路徑 | 內容 |
|---|---|
| profiles/profiles/20-jiang-yude.html、21-ivy-huang.html | 江江與黃敏菁博士（Dr. Ivy）的人物誌 |
| profiles/assets/img/members/ | jiang.webp、ivy.jpg 頭像 |
| profiles/members-cards-snippet.html | members 頁要加的兩張社友卡 |
| meetings/meetings/index.html | 2024-26 例會與活動紀錄頁 |
| meetings/assets/img/meetings/ | 77 張已壓縮的活動照片（原圖 1400px＋縮圖 600px，webp） |
| meetings/上線用片段_sitemap_llms.txt | 三個新頁要加進 sitemap、llms.txt 的片段 |
| faq/faq-section.html | 8 題 FAQ 區塊＋FAQPage 結構化資料 |
| scripts/ | build_profiles.py、build_meetings.py、proc2.py（壓圖）、audit_site.py（4O 檢查）、items.json |
| reports/ | 工作交接、4O 健檢報告 |
| *.png | 預覽截圖 |

## 要做的事（照順序）

### 1. 新三頁接進網站

- 把人物誌、頭像、例會頁、照片放進本機站的對應位置（profiles/、assets/img/members/、meetings/、assets/img/meetings/）。
- 如果本機產生器會重寫每頁 head，照產生器的規則加：members.json 加兩位社友，profiles 照它的方式放。產生器版本為準。
- members 頁加兩張社友卡：江 6 畫排在李琪之前，黃 12 畫排在黃世祿之後。
- 19-irene-chen 的「下一位」改指 20-jiang-yude。
- 首頁導覽或「關於永力社」加入口連到 /meetings/。
- 兩頁人物誌刪掉最上面的 REVIEW-BANNER 草稿提示條（等江江看過確認）。

### 2. YouTube／影片區（雲端沒做，在本機做）

江江有影片要上傳，所以這段留給本機：

- 先問江江：影片要上 YouTube 再嵌入，還是直接放站上。建議上 YouTube 再嵌入，網站不會變重，YouTube 頻道建好後也能放進 Organization 的 sameAs。
- 拿到網址後，在例會頁對應場次的卡片或首頁加影片區，用 youtube-nocookie.com 嵌入，加 loading="lazy"。
- 每支影片加 VideoObject 結構化資料，名稱、日期、說明要跟頁面上看得到的文字一致，不要編。

### 3. 4O 修正（改產生器，詳見 faq/產生器修改說明_給本機版.md）

- 全站網址統一不帶 .html：canonical、hreflang、og:url、sitemap、JSON-LD。線上 Cloudflare 會把 .html 308 轉走，這是最重要的一項。
- sitemap 每頁加 lastmod。
- 首頁補完整 Organization。
- FAQ 區塊放首頁或「關於永力社」二選一，等社內確認答案再上。
- 8 頁英文 description 縮到 160 字元內。
- 三個新頁加進 sitemap 與 llms.txt。

### 4. 檢查與部署

- 跑本機的 build 與 check。
- 本機預覽看三個新頁的桌機與手機版。
- 部署到 Cloudflare 前先問江江。
- 部署後驗收：

```bash
curl -sI https://rctsi.3481.org/members | head -1
curl -s https://rctsi.3481.org/members | grep canonical
curl -sI https://rctsi.3481.org/meetings/ | head -1
curl -s https://rctsi.3481.org/sitemap.xml | grep -c lastmod
```

- 也可以跑 `python3 _handoff/2026-11-05/scripts/audit_site.py` 重做一次 4O 檢查。
- 最後把本機最新版 commit 推上 GitHub，讓 GitHub 跟線上一致，之後雲端也能接著做。

## 還沒確認、上線前要問的

- 江江、Ivy 的社內職務（目前是暫寫）。
- Ivy 頭像授權（用的是 dr-ivy.com 的照片）。
- 兩位的 SDG 編號（目前是估的）。
- 人物誌「在永力社的位置」缺社內真實小故事。
- 兩張沒日期的照片：2025-26 幹部研習會（DTA）、新社員宣誓。
- FAQ 的來賓餐費（海報多為 1,000 元，9 月理事會有討論過）。
- 不要做五角圖，等真的做過分析訪談再加。

## 寫作規則（江江的偏好）

- 不用粗體 `**`。
- 標點用全形：，：？。
- 頁面文字不用破折號，不用「不是…而是…」「不只…還…」句型。
- 結構化資料只寫頁面上看得到的事實，不編數字和地點。

## 例會頁之後怎麼更新

照片用「日期＋活動名稱」命名（例：20260711第43次例會.jpg），然後：

```bash
python3 _handoff/2026-11-05/scripts/proc2.py <原始照片資料夾>
```

```bash
python3 _handoff/2026-11-05/scripts/build_meetings.py
```

講者與講題寫在 build_meetings.py 的 CAL 表。2026-27 年度（7 月之後）的照片還沒進來，社慶前補上就能排到 11 月。
