#!/bin/bash
# 把 v7 靜態檔複製到 cloudflare/public（不含 api 原始碼與 _build），再部署：
#   cd cloudflare && ./build.sh && wrangler pages deploy public --project-name 3481rctsi
set -e
cd "$(dirname "$0")"
rm -rf public && mkdir public
rsync -a --exclude api --exclude _build --exclude README.md --exclude '.DS_Store' ../v7/ public/
# Vercel 專屬的 insights 腳本在 Cloudflare 會 404，部署版拿掉
find public -name '*.html' -exec sed -i '' '/\/_vercel\/\(speed-\)\{0,1\}insights\/script\.js/d' {} +
