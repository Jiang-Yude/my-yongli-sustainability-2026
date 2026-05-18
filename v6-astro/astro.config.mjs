import { defineConfig } from 'astro/config';

// PoC 配置
// - format: 'file' 產出 about-yongli.html（不是 about-yongli/index.html），URL 對齊 v5/v6
// - public/assets/ 內容會原樣放到 dist/assets/
// - 部署：把 dist/* 複製到 ../v6/ 取代純複製版，G 網路徑不變
export default defineConfig({
  outDir: './dist',
  build: {
    format: 'file',
  },
});
