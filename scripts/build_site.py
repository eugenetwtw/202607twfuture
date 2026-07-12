#!/usr/bin/env python3
"""Build static site for 台灣大未來 issue pages."""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DATA = SITE / "data"
OUT = SITE  # pages live under site/zh, site/en, etc.

SITE_NAME = {
    "zh": "台灣大未來",
    "en": "Taiwan's Great Future",
}
DEFAULT_DESC = {
    "zh": "張渝江《台灣大未來》議題摘錄：今日瑞士，明日台灣。個人文集，非競選官網。",
    "en": "Issue excerpts from Eugene Chang's Taiwan's Great Future. A personal essay site.",
}

UI = {
    "zh": {
        "nav_home": "議題地圖",
        "nav_about": "關於",
        "nav_books": "借書／買書",
        "nav_gallery": "照片選輯",
        "kicker": "個人文集 · 議題摘錄",
        "hero_title": "台灣大未來",
        "hero_sub": "今日瑞士，明日台灣",
        "hero_lede": "這不是競選官網。這裡把書中的議題拆成可分享的短文——每則約兩三分鐘——完整論述請借閱或購買原書。",
        "cta_map": "瀏覽議題",
        "cta_books": "借書／買書",
        "filter_all": "全部",
        "section_map": "議題地圖",
        "section_map_hint": "依主題篩選；點進任一則即可用網址分享。",
        "read_full": "讀全書",
        "read_full_body": "以上為書中觀點的摘錄。完整脈絡與論證請讀《台灣大未來》。公共圖書館可借電子書；也可購買電子書或紙本。",
        "related": "相關議題",
        "source": "來源",
        "share": "分享連結",
        "copied": "已複製連結",
        "copy": "複製本頁網址",
        "minutes": "約 2–3 分鐘",
        "from_book": "摘自原書",
        "about_title": "關於作者與本書",
        "books_title": "借書／買書",
        "gallery_title": "照片選輯",
        "gallery_lede": "選自書中競選與人生紀錄影像。定位為文集附錄，而非拉票文宣。",
        "home": "首頁",
        "issues": "議題",
        "primary_lib": "到圖書館借電子書",
        "fallback_en": "English text is not ready yet; showing Traditional Chinese.",
        "footer": "摘錄自張渝江《台灣大未來》。圖像著作權屬作者，除非另有標示。",
        "isbn": "ISBN",
        "also_search": "亦可於所屬縣市公共圖書館搜尋書名借閱。",
        "featured": "從這裡開始",
    },
    "en": {
        "nav_home": "Issues",
        "nav_about": "About",
        "nav_books": "Get the book",
        "nav_gallery": "Gallery",
        "kicker": "Personal essays · Issue excerpts",
        "hero_title": "Taiwan's Great Future",
        "hero_sub": "Switzerland Today, Taiwan Tomorrow",
        "hero_lede": "Not a campaign site. Short, shareable issue essays from the book—about two to three minutes each. Borrow or buy the full book for the complete argument.",
        "cta_map": "Browse issues",
        "cta_books": "Get the book",
        "filter_all": "All",
        "section_map": "Issue map",
        "section_map_hint": "Filter by theme; each page has a shareable URL.",
        "read_full": "Read the full book",
        "read_full_body": "These pages are excerpts. For the full context, borrow the ebook from a public library or purchase print/ebook editions.",
        "related": "Related issues",
        "source": "Source",
        "share": "Share",
        "copied": "Link copied",
        "copy": "Copy page URL",
        "minutes": "≈ 2–3 min read",
        "from_book": "From the book",
        "about_title": "About the author & book",
        "books_title": "Borrow or buy",
        "gallery_title": "Photo gallery",
        "gallery_lede": "Selected images from the campaign memoir chapters—personal archive, not campaigning.",
        "home": "Home",
        "issues": "Issues",
        "primary_lib": "Borrow ebook (library)",
        "fallback_en": "English text is not ready yet; showing Traditional Chinese.",
        "footer": "Excerpts from Eugene Chang, Taiwan's Great Future. Images © the author unless noted.",
        "isbn": "ISBN",
        "also_search": "You can also search the title at your local public library.",
        "featured": "Start here",
    },
}

CHAPTER_LABEL = {
    0: {"zh": "0. 序", "en": "0. Preface"},
    1: {"zh": "1. 瑞士與台灣", "en": "1. Switzerland & Taiwan"},
    2: {"zh": "2. 能源政策與環境污染", "en": "2. Energy & environment"},
    3: {"zh": "3. 居住正義與建築營造", "en": "3. Housing & building"},
    4: {"zh": "4. 產業與金融，保險與醫療", "en": "4. Industry, finance, insurance & health"},
    5: {"zh": "5. 文化與教育", "en": "5. Culture & education"},
    6: {"zh": "6. AI, IoT, 遠距上班與司法", "en": "6. AI, IoT, remote work & justice"},
    7: {"zh": "7. 區塊鏈與選舉、內政", "en": "7. Blockchain, elections & governance"},
    8: {"zh": "8. 國家與認同", "en": "8. Nation & identity"},
    9: {"zh": "9. 我的競選歷程", "en": "9. Campaign journal"},
    "9.2": {"zh": "9.2 選後分析", "en": "9.2 Post-election notes"},
    10: {"zh": "10. 後記", "en": "10. Afterword"},
}


def load_json(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def t(obj, lang: str, fallback: str = "zh"):
    if isinstance(obj, dict):
        if lang in obj and obj[lang]:
            return obj[lang]
        return obj.get(fallback) or next(iter(obj.values()), "")
    return obj


def esc(s: str) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def asset(rel: str, depth: int) -> str:
    return "../" * depth + rel.lstrip("/")


def media_src(filename: str, depth: int) -> str:
    # all compressed to .jpg
    stem = Path(filename).stem + ".jpg"
    return asset(f"media/{stem}", depth)


def page_url(lang: str, path: str = "") -> str:
    path = path.strip("/")
    if path:
        return f"/{lang}/{path}/" if not path.endswith(".html") else f"/{lang}/{path}"
    return f"/{lang}/"


def og_tags(title: str, desc: str, image: str, depth: int, page_path: str) -> str:
    # relative image for local; absolute preferred when domain known
    img = media_src(image, depth) if image else ""
    return f"""
  <meta property="og:type" content="article" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(desc)}" />
  <meta property="og:image" content="{esc(img)}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{esc(title)}" />
  <meta name="twitter:description" content="{esc(desc)}" />
  <meta name="description" content="{esc(desc)}" />
"""


def layout(
    lang: str,
    title: str,
    body: str,
    depth: int,
    desc: str | None = None,
    image: str | None = None,
    path: str = "",
    current: str = "home",
) -> str:
    ui = UI[lang]
    desc = desc or DEFAULT_DESC[lang]
    full_title = title if title == SITE_NAME[lang] else f"{title} · {SITE_NAME[lang]}"
    other = "en" if lang == "zh" else "zh"
    other_label = "EN" if other == "en" else "中文"
    # language switch keeps same path suffix
    suffix = path.strip("/")
    lang_href = asset(f"{other}/{suffix}/" if suffix else f"{other}/", depth)

    nav = [
        ("home", ui["nav_home"], asset(f"{lang}/", depth) if depth else f"{lang}/"),
        ("about", ui["nav_about"], asset(f"{lang}/about/", depth)),
        ("books", ui["nav_books"], asset(f"{lang}/books/", depth)),
        ("gallery", ui["nav_gallery"], asset(f"{lang}/gallery/", depth)),
    ]
    # Fix nav when already under lang/
    nav = [
        ("home", ui["nav_home"], asset(f"{lang}/index.html", depth).replace("index.html", "") or asset(f"{lang}/", depth)),
        ("about", ui["nav_about"], asset(f"{lang}/about/", depth)),
        ("books", ui["nav_books"], asset(f"{lang}/books/", depth)),
        ("gallery", ui["nav_gallery"], asset(f"{lang}/gallery/", depth)),
    ]

    nav_html = []
    for key, label, href in nav:
        # normalize hrefs to directories
        if key == "home":
            href = "../" * depth + f"{lang}/"
        elif key == "about":
            href = "../" * depth + f"{lang}/about/"
        elif key == "books":
            href = "../" * depth + f"{lang}/books/"
        else:
            href = "../" * depth + f"{lang}/gallery/"
        cur = ' aria-current="page"' if current == key else ""
        nav_html.append(f'<a href="{href}"{cur}>{esc(label)}</a>')

    brand_href = "../" * depth + f"{lang}/"
    css = asset("css/site.css", depth)
    js = asset("js/site.js", depth)

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(full_title)}</title>
  {og_tags(full_title, desc, image or "image35.jpg", depth, path)}
  <link rel="stylesheet" href="{css}" />
</head>
<body>
  <header class="site-header">
    <div class="inner">
      <a class="brand" href="{brand_href}">{esc(SITE_NAME[lang])} <span>— essays</span></a>
      <nav class="nav">{"".join(nav_html)}</nav>
      <a class="lang-switch" href="{lang_href}">{other_label}</a>
    </div>
  </header>
  <main>
{body}
  </main>
  <footer class="site-footer">
    <div class="inner">
      <div>{esc(ui["footer"])}</div>
      <div><a href="{brand_href}">{esc(ui["home"])}</a> · <a href="{"../" * depth + lang + "/books/"}">{esc(ui["nav_books"])}</a></div>
    </div>
  </footer>
  <script src="{js}"></script>
</body>
</html>
"""


def cta_box(lang: str, books: dict, depth: int) -> str:
    ui = UI[lang]
    links = books["links"]
    buttons = []
    for link in links:
        label = t(link["label"], lang)
        cls = "btn btn-primary" if link.get("primary") else "btn btn-secondary"
        if link.get("primary"):
            label = ui["primary_lib"]
        buttons.append(
            f'<a class="{cls}" href="{esc(link["url"])}" target="_blank" rel="noopener">{esc(label)}</a>'
        )
    more = f'<a class="btn btn-ghost" href="{"../" * depth + lang + "/books/"}">{esc(ui["nav_books"])}</a>'
    return f"""
    <aside class="cta-box">
      <h2>{esc(ui["read_full"])}</h2>
      <p>{esc(ui["read_full_body"])}</p>
      <div class="cta-actions">
        {"".join(buttons[:2])}
        {more}
      </div>
    </aside>
"""


def build_home(lang: str, issues: list, clusters: list, books: dict) -> str:
    ui = UI[lang]
    depth = 1
    cluster_map = {c["id"]: t(c["title"], lang) for c in clusters}

    chips = [f'<button type="button" class="chip is-active" data-filter="all">{esc(ui["filter_all"])}</button>']
    for c in clusters:
        chips.append(
            f'<button type="button" class="chip" data-filter="{esc(c["id"])}">{esc(t(c["title"], lang))}</button>'
        )

    # featured
    featured_slugs = ["covid-as-turning-point", "v2g-and-ev-bonds", "euthanasia-and-autonomy"]
    by_slug = {i["slug"]: i for i in issues}
    featured_html = []
    for s in featured_slugs:
        if s not in by_slug:
            continue
        issue = by_slug[s]
        href = f"issues/{issue['slug']}/"
        featured_html.append(
            f"""<a class="issue-card" href="{href}">
          <div class="thumb"><img src="{media_src(issue['cover'], 0)}" alt="" loading="lazy" /></div>
          <div class="body">
            <div class="cluster-label">{esc(cluster_map.get(issue['cluster'], ''))}</div>
            <h3>{esc(t(issue['title'], lang))}</h3>
            <p class="claim">{esc(t(issue['claim'], lang))}</p>
          </div>
        </a>"""
        )

    cards = []
    for issue in issues:
        href = f"issues/{issue['slug']}/"
        cards.append(
            f"""<a class="issue-card" data-cluster="{esc(issue['cluster'])}" href="{href}">
        <div class="thumb"><img src="{media_src(issue['cover'], 0)}" alt="" loading="lazy" /></div>
        <div class="body">
          <div class="cluster-label">{esc(cluster_map.get(issue['cluster'], ''))}</div>
          <h3>{esc(t(issue['title'], lang))}</h3>
          <p class="claim">{esc(t(issue['claim'], lang))}</p>
        </div>
      </a>"""
        )

    body = f"""
  <section class="hero">
    <div class="wrap">
      <p class="hero-kicker">{esc(ui["kicker"])}</p>
      <h1>{esc(ui["hero_title"])}</h1>
      <p class="subtitle">{esc(ui["hero_sub"])}</p>
      <p class="lede">{esc(ui["hero_lede"])}</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="#map">{esc(ui["cta_map"])}</a>
        <a class="btn btn-secondary" href="books/">{esc(ui["cta_books"])}</a>
      </div>
    </div>
  </section>

  <section class="section wrap">
    <div class="section-head">
      <div>
        <h2>{esc(ui["featured"])}</h2>
      </div>
    </div>
    <div class="issue-grid">
      {"".join(featured_html)}
    </div>
  </section>

  <section class="section wrap" id="map">
    <div class="section-head">
      <div>
        <h2>{esc(ui["section_map"])}</h2>
        <p>{esc(ui["section_map_hint"])}</p>
      </div>
    </div>
    <div class="filters" id="cluster-filters">
      {"".join(chips)}
    </div>
    <div class="issue-grid" id="issue-grid">
      {"".join(cards)}
    </div>
  </section>
"""
    # fix media paths for depth=1 home: media is at ../media
    body = body.replace('src="media/', 'src="../media/')
    return layout(
        lang,
        ui["hero_title"],
        body,
        depth=1,
        desc=DEFAULT_DESC[lang],
        image="image35.jpg",
        path="",
        current="home",
    )


def body_paragraphs(issue: dict, lang: str) -> tuple[str, bool]:
    """Returns html, used_fallback"""
    body = issue.get("body") or {}
    used_fallback = False
    paras = body.get(lang)
    if not paras:
        paras = body.get("zh") or []
        used_fallback = lang != "zh"
    if isinstance(paras, str):
        paras = [paras]
    return "".join(f"<p>{esc(p)}</p>" for p in paras), used_fallback


def build_issue(lang: str, issue: dict, issues: list, books: dict) -> str:
    ui = UI[lang]
    depth = 3
    by_slug = {i["slug"]: i for i in issues}
    title = t(issue["title"], lang)
    claim = t(issue["claim"], lang)
    prose, fallback = body_paragraphs(issue, lang)

    figs = issue.get("figures") or []
    # first figure as cover if present
    cover = issue.get("cover") or (figs[0]["src"] if figs else "image35.jpg")
    cover_cap = ""
    if figs:
        cover_cap = t(figs[0].get("caption") or {}, lang)
    cover_html = f"""
    <figure class="cover-figure">
      <img src="{media_src(cover, depth)}" alt="{esc(title)}" />
      {f'<figcaption>{esc(cover_cap)}</figcaption>' if cover_cap else ''}
    </figure>
"""

    extra_figs = []
    for fig in figs[1:]:
        cap = t(fig.get("caption") or {}, lang)
        extra_figs.append(
            f"""<figure class="inline-figure">
      <img src="{media_src(fig['src'], depth)}" alt="" loading="lazy" />
      {f'<figcaption>{esc(cap)}</figcaption>' if cap else ''}
    </figure>"""
        )

    # interleave: put first extra fig after 2nd para roughly by splitting prose
    # simple: prose then extra figures
    related = []
    for slug in issue.get("related") or []:
        if slug in by_slug:
            rel = by_slug[slug]
            related.append(
                f'<a href="{"../" * 0}../{esc(slug)}/">{esc(t(rel["title"], lang))}</a>'.replace(
                    f"../{slug}/", f"../{slug}/"
                )
            )
    # related links from /zh/issues/foo/ to /zh/issues/bar/
    related = []
    for slug in issue.get("related") or []:
        if slug in by_slug:
            rel = by_slug[slug]
            related.append(f'<a href="../{esc(slug)}/">{esc(t(rel["title"], lang))}</a>')

    chapters = []
    for ch in issue.get("source_chapters") or []:
        label = CHAPTER_LABEL.get(ch) or CHAPTER_LABEL.get(str(ch))
        if label:
            chapters.append(t(label, lang))
        else:
            chapters.append(str(ch))

    fb = f'<div class="lang-fallback">{esc(ui["fallback_en"])}</div>' if fallback else ""

    body = f"""
  <article class="article article-hero">
    <div class="wrap-narrow">
      <div class="breadcrumb">
        <a href="../../">{esc(ui["home"])}</a> / {esc(ui["issues"])} / {esc(title)}
      </div>
      <div class="article-meta">
        <span>{esc(ui["minutes"])}</span>
        <span>{esc(ui["from_book"])}: {esc(" · ".join(chapters))}</span>
      </div>
      <h1>{esc(title)}</h1>
      <p class="claim">{esc(claim)}</p>
      {fb}
      {cover_html}
      <div class="prose">
        {prose}
        {"".join(extra_figs)}
      </div>
      {cta_box(lang, books, depth)}
      <div class="related">
        <h2>{esc(ui["related"])}</h2>
        <div class="related-list">{"".join(related)}</div>
      </div>
      <p class="source-note">{esc(ui["source"])}: {esc(t(books["title"], lang))} — {esc(t(books["author"], lang))} · {esc(" · ".join(chapters))}</p>
      <div class="share-row">
        <span>{esc(ui["share"])}:</span>
        <button type="button" class="btn btn-secondary" data-copy-url>{esc(ui["copy"])}</button>
      </div>
    </div>
  </article>
"""
    return layout(
        lang,
        title,
        body,
        depth=depth,
        desc=claim,
        image=cover,
        path=f"issues/{issue['slug']}",
        current="home",
    )


def build_about(lang: str, books: dict) -> str:
    ui = UI[lang]
    depth = 2
    if lang == "zh":
        content = """
      <p>張渝江，台灣大學土木／法律雙學士與碩士，芝加哥伊利諾大學 MBA（財務管理），土木工程技師。綠圖顧問負責人，亦從事區塊鏈與營造相關工作。著有《無人機大未來》《比特幣區塊鏈大未來》等多部作品。</p>
      <p>《台灣大未來 — 今日瑞士，明日台灣》寫於 2019–2020，交織瑞士參照、能源與居住、醫療與科技，以及八十天立委競選的現場紀錄。2020 年夏於台中完稿。</p>
      <p>本站是<strong>個人文集式的議題摘錄</strong>，方便以網址分享各主題。作者已不再從政參政；此處不從事競選或政黨動員。</p>
      <p>完整論述請透過公共圖書館借閱電子書，或購買紙本／電子書。書目與連結見「借書／買書」。</p>
"""
    else:
        content = """
      <p>Eugene Chang (張渝江) is a civil engineer and writer based in Taiwan, with degrees in civil engineering and law (NTU) and an MBA from the University of Illinois at Chicago. He has written on drones, blockchain, engineering, and public policy.</p>
      <p><em>Taiwan's Great Future — Switzerland Today, Taiwan Tomorrow</em> (2020) weaves Swiss comparisons, energy and housing, healthcare and technology, and a memoir of an eighty-day legislative campaign.</p>
      <p>This site offers <strong>short, shareable issue essays</strong>—not a campaign property. The author is not seeking office.</p>
      <p>For the full book, borrow from public libraries or purchase ebook/print editions.</p>
"""
    body = f"""
  <section class="section">
    <div class="wrap-narrow">
      <h1>{esc(ui["about_title"])}</h1>
      {content}
      {cta_box(lang, books, depth)}
    </div>
  </section>
"""
    return layout(lang, ui["about_title"], body, depth, current="about", path="about")


def build_books(lang: str, books: dict) -> str:
    ui = UI[lang]
    depth = 2
    items = []
    for link in books["links"]:
        cls = "book-link is-primary" if link.get("primary") else "book-link"
        label = ui["primary_lib"] if link.get("primary") else t(link["label"], lang)
        items.append(
            f"""<a class="{cls}" href="{esc(link["url"])}" target="_blank" rel="noopener">
        <strong>{esc(label)}</strong>
        <span>{esc(link["url"])}</span>
      </a>"""
        )
    body = f"""
  <section class="section">
    <div class="wrap-narrow">
      <h1>{esc(ui["books_title"])}</h1>
      <p>{esc(t(books["title"], lang))}<br/>{esc(t(books["subtitle"], lang))}<br/>{esc(t(books["author"], lang))}</p>
      <div class="isbn-list">
        <div>{esc(ui["isbn"])} (print): {esc(books["isbn_print"])}</div>
        <div>{esc(ui["isbn"])} (ebook): {esc(books["isbn_ebook"])}</div>
      </div>
      <p class="notice">{esc(ui["also_search"])}</p>
      <div class="book-links">
        {"".join(items)}
      </div>
    </div>
  </section>
"""
    return layout(lang, ui["books_title"], body, depth, current="books", path="books")


def build_gallery(lang: str, gallery_images: list[str]) -> str:
    ui = UI[lang]
    depth = 2
    cells = []
    for name in gallery_images:
        src = media_src(name, depth)
        cells.append(f'<a href="{src}" target="_blank" rel="noopener"><img src="{src}" alt="" loading="lazy" /></a>')
    body = f"""
  <section class="section">
    <div class="wrap">
      <h1>{esc(ui["gallery_title"])}</h1>
      <p class="lede" style="max-width:40em;color:var(--ink-soft)">{esc(ui["gallery_lede"])}</p>
      <div class="gallery-grid" style="margin-top:1.5rem">
        {"".join(cells)}
      </div>
    </div>
  </section>
"""
    return layout(lang, ui["gallery_title"], body, depth, current="gallery", path="gallery", image=gallery_images[0] if gallery_images else "image35.jpg")


def write(path: Path, html: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def main():
    issues = load_json("issues.json")
    clusters = load_json("clusters.json")
    books = load_json("books.json")

    # gallery: chapter 9.1 images from image_map
    image_map = json.loads((ROOT / "scripts" / "image_map.json").read_text(encoding="utf-8"))
    gallery = []
    for item in image_map:
        if str(item.get("chapter", "")).startswith("9.1"):
            gallery.append(item["file"])
    # unique preserve order, cap at 60 for performance
    seen = set()
    gallery_u = []
    for g in gallery:
        stem = Path(g).stem
        if stem in seen:
            continue
        seen.add(stem)
        gallery_u.append(g)
        if len(gallery_u) >= 60:
            break

    # root redirect
    write(
        OUT / "index.html",
        """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8" />
  <meta http-equiv="refresh" content="0; url=zh/" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>台灣大未來</title>
  <link rel="canonical" href="zh/" />
  <script>location.replace("zh/");</script>
</head>
<body>
  <p><a href="zh/">進入中文版 / Enter Chinese site</a></p>
</body>
</html>
""",
    )

    for lang in ("zh", "en"):
        write(OUT / lang / "index.html", build_home(lang, issues, clusters, books))
        write(OUT / lang / "about" / "index.html", build_about(lang, books))
        write(OUT / lang / "books" / "index.html", build_books(lang, books))
        write(OUT / lang / "gallery" / "index.html", build_gallery(lang, gallery_u))
        for issue in issues:
            write(
                OUT / lang / "issues" / issue["slug"] / "index.html",
                build_issue(lang, issue, issues, books),
            )

    print(f"Built {len(issues)} issues × 2 langs + home/about/books/gallery")
    print(f"Gallery images: {len(gallery_u)}")
    print(f"Output: {OUT}")


if __name__ == "__main__":
    main()
