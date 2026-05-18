# v6-astro：Astro 化 PoC

> 2026-05-18 江昱德拍板：v6 走 Astro 架構。本資料夾是 PoC 階段（1 個檔 + 3 個 component + 2 個 data），確認方向後再批次擴散到剩 29 個檔。

## 狀態

- ✅ PoC 跑通：`about-yongli.astro` build 成 `dist/about-yongli.html`
- ✅ 視覺對齊 v6/about-yongli.html（內容區完全一致）
- ✅ Footer 含 CC BY-NC-ND 4.0 授權聲明（全站統一）
- ⏳ 等雷哥校稿、確認後啟動批次擴散
- ⏳ 確認後才把 dist/* 取代 v6/，推 G 網

## 結構

```
v6-astro/
├── package.json                    # 依賴 astro
├── astro.config.mjs                # build format: 'file' 對齊 v5/v6 URL
├── public/
│   └── assets/                     # 從 ../v6/assets 複製過來（PoC 階段重複）
└── src/
    ├── data/
    │   ├── site.json               # 扶輪社資訊、授權、版本
    │   └── nav.json                # 主導航 + 頁尾章節
    ├── components/
    │   ├── Topbar.astro            # 共用頂部導航
    │   └── Footer.astro            # 共用頁尾（含版本資訊欄 + 授權）
    ├── layouts/
    │   └── BaseLayout.astro        # 共用 head + topbar + footer 殼
    └── pages/
        └── about-yongli.astro      # PoC：第一個轉換的頁面
```

## 本地跑通的指令

```bash
cd v6-astro
npm install              # 第一次跑要、之後不用
npm run build            # 產出 dist/about-yongli.html
open dist/about-yongli.html  # 用瀏覽器看 build 結果
```

## 跟 v6/ 純複製版的關係

| 差別 | v6/（純複製版） | v6-astro/dist/（Astro build） |
|---|---|---|
| topbar | 30 個檔各寫一份 | 1 個 Topbar.astro 共用 |
| footer | 30 個檔各寫一份 | 1 個 Footer.astro 共用 |
| 授權聲明 | 沒有 | ✅ 每個頁自動有 |
| 改 footer 一個字要動幾個檔 | 30 個 | 1 個 |
| AI 改 token 用量 | 高（讀 30 個檔）| 低（讀 1-2 個檔）|

## 雷哥校稿要看什麼

1. **內容完全對齊 v6 嗎？**
   - 用 Chrome 開 v6/about-yongli.html 跟 v6-astro/dist/about-yongli.html 對比
2. **footer 多的「版本資訊欄 + CC BY-NC-ND 4.0 授權」OK 嗎？**
3. **連結都通嗎？**（nav 的 5 個連結、footer 5 個章節連結）
4. **data 抽出去的 site.json + nav.json 結構 OK 嗎？**
   - 想清楚未來 Google Sheets 對應這些欄位

## 確認後的下一步

1. 批次擴散：把剩 29 個檔（index, members, methodology, cases, disclosure-framework, member-guide, analysis + 15 profiles + 7 services）用同樣 pattern 改寫成 .astro
2. 抽社員資料：profiles/ 統一抽到 `src/data/members.json`
3. 抽服務計畫資料：services/ 統一抽到 `src/data/services.json`
4. 整合 v6：把 dist/* 取代 v6/（或改 GitHub Pages 路徑指向 dist/）
5. 推 G 網 + 校驗 + 推 V 網

## 相關工作日記

- [[2026-05-18-0924 合作·永力扶輪社·工作日記：v6 規劃啟動]] — 完整背景與三大原則（快/穩/省 token）
