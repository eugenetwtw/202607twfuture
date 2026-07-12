# 台灣大未來 — 議題網站

依 `DESIGN.md` 建置的靜態網站：把《台灣大未來 — 今日瑞士，明日台灣》拆成可分享的議題短文（約 2–3 分鐘），並引導借書／買書。

## 本機預覽

```bash
cd site
python3 -m http.server 8765
```

瀏覽：<http://127.0.0.1:8765/>（會導向 `/zh/`）

範例議題網址：

- <http://127.0.0.1:8765/zh/issues/euthanasia-and-autonomy/>
- <http://127.0.0.1:8765/zh/issues/v2g-and-ev-bonds/>
- <http://127.0.0.1:8765/zh/books/>

## 目錄

| 路徑 | 說明 |
|------|------|
| `site/` | 可部署的靜態站根目錄 |
| `site/zh/`、`site/en/` | 多語頁面（英文正文第一版 fallback 中文） |
| `site/data/issues.json` | 33 則議題內容 |
| `site/media/` | 網頁用壓縮圖（約 30MB） |
| `scripts/build_site.py` | 由 data 重新產生 HTML |
| `DESIGN.md` | 產品設計文件 |
| `2019 台灣大未來-….docx` | 原書來源 |

## 重新建置

```bash
# 若改了 site/data/issues.json 或 build 腳本
python3 scripts/build_site.py
```

從 docx 重抽圖（可選）：

```bash
# 見既有 site/media；原圖可另存
```

## 部署

將 **`site/` 目錄內容** 上傳至任何靜態主機（GitHub Pages、Cloudflare Pages、Netlify、S3…）。

上線後請把正式網域填進 OG／canonical（目前 `og:image` 為相對路徑，社群預覽在部分平台需絕對 URL）。可在 `scripts/build_site.py` 加 `BASE_URL` 後重建。

## 借書／買書連結

- [北市圖 HyRead](https://tpml.ebook.hyread.com.tw/bookDetail.jsp?id=231869)（主 CTA）
- [Google Play Books](https://play.google.com/store/books/details?id=bsH2DwAAQBAJ)
- [Pubu](https://www.pubu.com.tw/ebook/200261)
- [Apple Books](https://books.apple.com/us/book/id1528029318)

ISBN 紙本 `978-957-43-7441-0` · 電子 `9789574377404`
