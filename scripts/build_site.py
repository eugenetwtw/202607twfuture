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
    "zh": "瑞士人均八萬美金、台灣兩萬四——差在哪？工程師張渝江把瑞士當鏡子，拆解台灣的能源、居住、醫療與未來。",
    "en": "Switzerland's GDP per capita is triple Taiwan's—why? Engineer Eugene Chang uses Switzerland as a mirror for Taiwan's future.",
}

UI = {
    "zh": {
        "nav_home": "議題地圖",
        "nav_about": "關於",
        "nav_books": "借書／買書",
        "nav_gallery": "照片選輯",
        "kicker": "張渝江 · 工程師怎麼看台灣的下一步",
        "hero_title": "若台灣變成瑞士，你的生活會差多少？",
        "hero_sub": "《台灣大未來》— 今日瑞士，明日台灣",
        "hero_lede": "人均所得差三倍、空氣差一截、房子卻貴到喘不過氣。他不是空談，而是帶著高鐵工地、區塊鏈與八十天選戰現場，把「有沒有可能」一題題拆開——每則兩三分鐘，點進去就知道。",
        "cta_map": "先看最刺痛的幾題",
        "cta_books": "借書／買全書",
        "filter_all": "全部",
        "section_map": "議題地圖",
        "section_map_hint": "能源、居住、醫療、科技……挑你在意的點進去；每頁都能直接分享。",
        "read_full": "想看完整推理？",
        "read_full_body": "上面只是入口。書裡有數據、現場與完整論證——圖書館可借電子書，也可直接買。",
        "related": "你可能也會點這些",
        "source": "來源",
        "share": "分享連結",
        "copied": "已複製連結",
        "copy": "複製本頁網址",
        "minutes": "約 2–3 分鐘",
        "from_book": "摘自原書",
        "about_title": "這個人是誰？",
        "about_hook": "台大土木與法律、芝加哥 MBA、工地裡長大的工程師——也曾用八十天拿下一萬四千票。他寫書不是為了站台，是為了把「台灣有沒有機會變瑞士」說清楚。",
        "books_title": "借書／買書",
        "gallery_title": "照片選輯",
        "gallery_lede": "八十天、菜市場、特斯拉宣傳車、開票之夜——點進去看現場，也看他怎麼走這一趟。",
        "gallery_count": "共 {n} 張",
        "gallery_open": "開啟說明",
        "gallery_close": "關閉",
        "gallery_prev": "上一張",
        "gallery_next": "下一張",
        "gallery_play": "自動播放",
        "gallery_pause": "暫停",
        "gallery_fullscreen": "全螢幕",
        "gallery_fullscreen_exit": "離開全螢幕",
        "gallery_delay": "每張秒數",
        "gallery_delay_dec": "減少秒數",
        "gallery_delay_inc": "增加秒數",
        "gallery_video": "影片",
        "gallery_clip": "動態",
        "gallery_open_link": "開啟連結",
        "gallery_of": "/",
        "gallery_mode_photo": "輪播：相片",
        "gallery_mode_video": "輪播：短片",
        "gallery_still_label": "原圖",
        "gallery_clip_label": "短片",
        "home": "首頁",
        "issues": "議題",
        "issue_no": "議題",
        "photo_clip": "由本頁照片生成的短片",
        "primary_lib": "到圖書館借電子書",
        "fallback_en": "English text is not ready yet; showing Traditional Chinese.",
        "footer": "張渝江《台灣大未來》— 工程師視角的台灣下一步。圖像除另有標示外屬作者。",
        "footer_by": "作者 張渝江",
        "isbn": "ISBN",
        "also_search": "亦可於所屬縣市公共圖書館搜尋書名借閱。",
        "featured": "先從這幾題刺進去",
        "cover_caption": "《台灣大未來》封面",
        "author_name": "張渝江",
        "author_role": "工程師 · 作者 · 八十天選戰紀錄者",
        "compose_title": "發表框",
        "compose_hint": "改幾句話，就能貼上 FB、LINE、Threads。預覽卡會帶出標題與封面。",
        "compose_preview": "連結預覽（示意）",
        "compose_draft": "發表文案",
        "compose_copy_text": "複製文案",
        "compose_copy_link": "複製連結",
        "compose_native": "系統分享",
        "compose_fb": "Facebook",
        "compose_x": "X",
        "compose_line": "LINE",
        "compose_threads": "Threads",
        "compose_copied_text": "已複製文案",
        "compose_copied_link": "已複製連結",
        "compose_site_tag": "張渝江 · 台灣大未來",
        "compose_footer_line": "— 張渝江《台灣大未來》",
    },
    "en": {
        "nav_home": "Issues",
        "nav_about": "About",
        "nav_books": "Get the book",
        "nav_gallery": "Gallery",
        "kicker": "Eugene Chang · An engineer’s map of Taiwan’s next move",
        "hero_title": "What if Taiwan became Switzerland?",
        "hero_sub": "Taiwan's Great Future — Switzerland Today, Taiwan Tomorrow",
        "hero_lede": "Triple the GDP per capita. Cleaner air. A housing market that doesn’t crush the young. He doesn’t lecture—he opens the case file: HSR job sites, blockchain, an 80-day campaign. Two or three minutes per issue. Click if you’re curious.",
        "cta_map": "Start with the sharp ones",
        "cta_books": "Borrow / buy the book",
        "filter_all": "All",
        "section_map": "Issue map",
        "section_map_hint": "Energy, housing, health, tech—pick what hits you. Every page is shareable.",
        "read_full": "Want the full argument?",
        "read_full_body": "This is the doorway. The book has the data and the field notes—borrow the ebook or buy it.",
        "related": "You might open these next",
        "source": "Source",
        "share": "Share",
        "copied": "Link copied",
        "copy": "Copy page URL",
        "minutes": "≈ 2–3 min read",
        "from_book": "From the book",
        "about_title": "Who is this?",
        "about_hook": "NTU civil engineering & law. Chicago MBA. Builder of sites and systems—and once, an 80-day outsider campaign. He writes to answer one question: can Taiwan grow up to Switzerland?",
        "books_title": "Borrow or buy",
        "gallery_title": "Photo gallery",
        "gallery_lede": "Eighty days, night markets, a Tesla campaign car, election night—open a frame and stay a second.",
        "gallery_count": "{n} photos",
        "gallery_open": "Open",
        "gallery_close": "Close",
        "gallery_prev": "Previous",
        "gallery_next": "Next",
        "gallery_play": "Autoplay",
        "gallery_pause": "Pause",
        "gallery_fullscreen": "Fullscreen",
        "gallery_fullscreen_exit": "Exit fullscreen",
        "gallery_delay": "Seconds per photo",
        "gallery_delay_dec": "Decrease seconds",
        "gallery_delay_inc": "Increase seconds",
        "gallery_video": "Video",
        "gallery_clip": "Clip",
        "gallery_open_link": "Open link",
        "gallery_of": "/",
        "gallery_mode_photo": "Slideshow: photos",
        "gallery_mode_video": "Slideshow: clips",
        "gallery_still_label": "Photo",
        "gallery_clip_label": "Clip",
        "home": "Home",
        "issues": "Issues",
        "issue_no": "Issue",
        "photo_clip": "Short clip generated from this photo",
        "primary_lib": "Borrow ebook (library)",
        "fallback_en": "English text is not ready yet; showing Traditional Chinese.",
        "footer": "Eugene Chang · Taiwan's Great Future — an engineer's map of what's next. Images © the author unless noted.",
        "footer_by": "Eugene Chang",
        "isbn": "ISBN",
        "also_search": "You can also search the title at your local public library.",
        "featured": "Start with these",
        "cover_caption": "Book cover — Taiwan's Great Future",
        "author_name": "Eugene Chang",
        "author_role": "Engineer · Author · 80-day campaign chronicler",
        "compose_title": "Share box",
        "compose_hint": "Tweak a line, then post to social. The preview card carries title and image.",
        "compose_preview": "Link preview (mock)",
        "compose_draft": "Post draft",
        "compose_copy_text": "Copy text",
        "compose_copy_link": "Copy link",
        "compose_native": "Share…",
        "compose_fb": "Facebook",
        "compose_x": "X",
        "compose_line": "LINE",
        "compose_threads": "Threads",
        "compose_copied_text": "Text copied",
        "compose_copied_link": "Link copied",
        "compose_site_tag": "Eugene Chang · Taiwan's Great Future",
        "compose_footer_line": "— Eugene Chang, Taiwan's Great Future",
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
    name = str(filename).lstrip("/")
    # video / explicit subpaths under media/
    if name.startswith("clips/") or Path(name).suffix.lower() in {
        ".mp4",
        ".webm",
        ".mov",
        ".svg",
    }:
        return asset(f"media/{name}", depth)
    # photos compressed to .jpg
    stem = Path(name).stem + ".jpg"
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
    about_href = "../" * depth + f"{lang}/about/"
    css = asset("css/site.css", depth)
    js = asset("js/site.js", depth)
    # Circular UI uses head-and-shoulders crop (full-body original was cutting off the head)
    author_img = asset("media/author-avatar.jpg", depth)
    author_name = esc(ui.get("author_name") or "張渝江")
    author_role = esc(ui.get("author_role") or "")
    footer_by = esc(ui.get("footer_by") or author_name)

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(full_title)}</title>
  {og_tags(full_title, desc, image or "author-avatar.jpg", depth, path)}
  <link rel="icon" href="{asset("favicon.svg", depth)}" type="image/svg+xml" />
  <link rel="icon" href="{asset("favicon.ico", depth)}" sizes="any" />
  <link rel="icon" href="{asset("favicon-32.png", depth)}" type="image/png" sizes="32x32" />
  <link rel="apple-touch-icon" href="{asset("apple-touch-icon.png", depth)}" />
  <link rel="stylesheet" href="{css}" />
</head>
<body>
  <header class="site-header">
    <div class="inner">
      <a class="brand" href="{brand_href}">
        <img class="brand-avatar" src="{author_img}" alt="{author_name}" width="36" height="36" />
        <span class="brand-text">{esc(SITE_NAME[lang])} <span class="brand-sub">— {author_name}</span></span>
      </a>
      <nav class="nav">{"".join(nav_html)}</nav>
      <a class="lang-switch" href="{lang_href}">{other_label}</a>
    </div>
  </header>
  <main>
{body}
  </main>
  <footer class="site-footer">
    <div class="inner">
      <a class="footer-author" href="{about_href}">
        <img src="{author_img}" alt="{author_name}" width="40" height="40" />
        <span>
          <strong>{footer_by}</strong>
          <span class="footer-role">{author_role}</span>
        </span>
      </a>
      <div class="footer-meta">
        <div>{esc(ui["footer"])}</div>
        <div><a href="{brand_href}">{esc(ui["home"])}</a> · <a href="{about_href}">{esc(ui["nav_about"])}</a> · <a href="{"../" * depth + lang + "/books/"}">{esc(ui["nav_books"])}</a></div>
      </div>
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
            f'<a class="{cls}" href="{esc(link["url"])}" target="_blank" rel="noopener noreferrer">{esc(label)}</a>'
        )
    return f"""
    <aside class="cta-box">
      <h2>{esc(ui["read_full"])}</h2>
      <p>{esc(ui["read_full_body"])}</p>
      <div class="cta-actions">
        {"".join(buttons)}
      </div>
    </aside>
"""


def compose_box(lang: str, title: str, claim: str, cover: str, depth: int) -> str:
    """Share / publish composer box for social posting."""
    ui = UI[lang]
    if lang == "zh":
        draft = f"「{title}」\n\n{claim}\n\n{ui['compose_footer_line']}"
    else:
        draft = f'"{title}"\n\n{claim}\n\n{ui["compose_footer_line"]}'
    img = media_src(cover, depth)
    return f"""
    <aside class="compose-box" data-compose-box
      data-msg-copied-text="{esc(ui["compose_copied_text"])}"
      data-msg-copied-link="{esc(ui["compose_copied_link"])}">
      <div class="compose-box__head">
        <h2>{esc(ui["compose_title"])}</h2>
        <p>{esc(ui["compose_hint"])}</p>
      </div>

      <div class="compose-preview" aria-label="{esc(ui["compose_preview"])}">
        <div class="compose-preview__label">{esc(ui["compose_preview"])}</div>
        <div class="compose-preview__card">
          <div class="compose-preview__thumb">
            <img src="{img}" alt="" />
          </div>
          <div class="compose-preview__body">
            <div class="compose-preview__site">{esc(ui["compose_site_tag"])}</div>
            <div class="compose-preview__title">{esc(title)}</div>
            <div class="compose-preview__desc">{esc(claim)}</div>
          </div>
        </div>
      </div>

      <label class="compose-label" for="compose-draft">{esc(ui["compose_draft"])}</label>
      <textarea id="compose-draft" class="compose-textarea" data-compose-text rows="6">{esc(draft)}</textarea>

      <div class="compose-actions">
        <button type="button" class="btn btn-primary" data-copy-text>{esc(ui["compose_copy_text"])}</button>
        <button type="button" class="btn btn-secondary" data-copy-url>{esc(ui["compose_copy_link"])}</button>
        <button type="button" class="btn btn-secondary" data-share-native hidden>{esc(ui["compose_native"])}</button>
      </div>

      <div class="compose-social" role="group" aria-label="{esc(ui["compose_title"])}">
        <button type="button" class="compose-social__btn" data-share="facebook">{esc(ui["compose_fb"])}</button>
        <button type="button" class="compose-social__btn" data-share="x">{esc(ui["compose_x"])}</button>
        <button type="button" class="compose-social__btn" data-share="line">{esc(ui["compose_line"])}</button>
        <button type="button" class="compose-social__btn" data-share="threads">{esc(ui["compose_threads"])}</button>
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

    # Stable issue numbers from list order (01, 02, …)
    num_by_slug = {issue["slug"]: idx for idx, issue in enumerate(issues, start=1)}

    def issue_no_label(n: int) -> str:
        return f"{n:02d}"

    # featured
    featured_slugs = ["detail-and-craft", "coal-and-air", "eighty-days-campaign"]
    by_slug = {i["slug"]: i for i in issues}
    featured_html = []
    for s in featured_slugs:
        if s not in by_slug:
            continue
        issue = by_slug[s]
        n = num_by_slug[issue["slug"]]
        href = f"issues/{issue['slug']}/"
        featured_html.append(
            f"""<a class="issue-card" href="{href}">
          <div class="thumb">
            <span class="issue-no" aria-label="{esc(ui["issue_no"])} {issue_no_label(n)}">{issue_no_label(n)}</span>
            <img src="{media_src(issue['cover'], 0)}" alt="" loading="lazy" />
          </div>
          <div class="body">
            <div class="cluster-label"><span class="issue-no-inline">{issue_no_label(n)}</span> · {esc(cluster_map.get(issue['cluster'], ''))}</div>
            <h3>{esc(t(issue['title'], lang))}</h3>
            <p class="claim">{esc(t(issue['claim'], lang))}</p>
          </div>
        </a>"""
        )

    cards = []
    for issue in issues:
        n = num_by_slug[issue["slug"]]
        href = f"issues/{issue['slug']}/"
        cards.append(
            f"""<a class="issue-card" data-cluster="{esc(issue['cluster'])}" href="{href}">
        <div class="thumb">
          <span class="issue-no" aria-label="{esc(ui["issue_no"])} {issue_no_label(n)}">{issue_no_label(n)}</span>
          <img src="{media_src(issue['cover'], 0)}" alt="" loading="lazy" />
        </div>
        <div class="body">
          <div class="cluster-label"><span class="issue-no-inline">{issue_no_label(n)}</span> · {esc(cluster_map.get(issue['cluster'], ''))}</div>
          <h3>{esc(t(issue['title'], lang))}</h3>
          <p class="claim">{esc(t(issue['claim'], lang))}</p>
        </div>
      </a>"""
        )

    cover_src = media_src("cover.jpg", 0)
    author_src = media_src("author-avatar.jpg", 0)
    author_portrait = media_src("author-upper.jpg", 0)
    body = f"""
  <section class="hero">
    <div class="wrap hero-layout">
      <div class="hero-copy">
        <p class="hero-kicker">{esc(ui["kicker"])}</p>
        <h1>{esc(ui["hero_title"])}</h1>
        <p class="subtitle">{esc(ui["hero_sub"])}</p>
        <p class="lede">{esc(ui["hero_lede"])}</p>
        <div class="hero-author-chip">
          <img src="{author_src}" alt="{esc(ui["author_name"])}" width="56" height="56" />
          <div>
            <strong>{esc(ui["author_name"])}</strong>
            <span>{esc(ui["author_role"])}</span>
          </div>
        </div>
        <div class="hero-actions">
          <a class="btn btn-primary" href="#map">{esc(ui["cta_map"])}</a>
          <a class="btn btn-secondary" href="books/">{esc(ui["cta_books"])}</a>
          <a class="btn btn-ghost" href="about/">{esc(ui["nav_about"])}</a>
        </div>
      </div>
      <div class="hero-visuals">
        <figure class="hero-cover">
          <img src="{cover_src}" alt="{esc(ui["cover_caption"])}" width="640" height="1008" />
          <figcaption>{esc(ui["cover_caption"])}</figcaption>
        </figure>
        <figure class="hero-portrait">
          <img src="{author_portrait}" alt="{esc(ui["author_name"])}" width="600" height="800" />
          <figcaption>{esc(ui["author_name"])}</figcaption>
        </figure>
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
        image="cover.jpg",
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


def build_issue(lang: str, issue: dict, issues: list, books: dict, clips: dict | None = None) -> str:
    ui = UI[lang]
    depth = 3
    by_slug = {i["slug"]: i for i in issues}
    num_by_slug = {i["slug"]: idx for idx, i in enumerate(issues, start=1)}
    issue_n = num_by_slug.get(issue["slug"], 0)
    issue_no = f"{issue_n:02d}" if issue_n else ""
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
    # Optional AI short clip under the original photo (not on homepage)
    clip = (clips or {}).get(issue["slug"])
    clip_html = ""
    if clip and clip.get("src"):
        clip_label = clip.get("label_zh") if lang == "zh" else clip.get("label_en")
        clip_label = clip_label or ui.get("photo_clip") or ""
        poster = media_src(clip.get("poster") or cover, depth)
        src_v = media_src(clip["src"], depth)
        clip_html = f"""
    <figure class="clip-figure">
      <video class="clip-video" controls playsinline preload="metadata" poster="{poster}">
        <source src="{src_v}" type="video/mp4" />
      </video>
      <figcaption>{esc(clip_label)}</figcaption>
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
            rn = num_by_slug.get(slug, 0)
            rno = f"{rn:02d} " if rn else ""
            related.append(f'<a href="../{esc(slug)}/">{rno}{esc(t(rel["title"], lang))}</a>')

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
        <a href="../../">{esc(ui["home"])}</a> / {esc(ui["issues"])} / {esc(ui["issue_no"])} {issue_no}
      </div>
      <div class="article-meta">
        <span class="issue-no-badge">{esc(ui["issue_no"])} {issue_no}</span>
        <span>{esc(ui["minutes"])}</span>
        <span>{esc(ui["from_book"])}: {esc(" · ".join(chapters))}</span>
      </div>
      <h1><span class="issue-no-title">{issue_no}</span> {esc(title)}</h1>
      <p class="claim">{esc(claim)}</p>
      {fb}
      {cover_html}
      {clip_html}
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
    author = media_src("author-upper.jpg", depth)
    if lang == "zh":
        content = f"""
      <p class="about-hook">{esc(ui.get("about_hook") or "")}</p>
      <p>台大土木與法律雙學士、碩士；芝加哥伊利諾大學 MBA（財務與風險）。土木工程技師、綠圖顧問負責人，也做區塊鏈與營造。他在工地學細節，再把視野寫進書裡。</p>
      <p>著有《無人機大未來》《比特幣區塊鏈大未來》《台灣大未來》等。這一站，是他的<strong>個人品牌入口</strong>：短議題好分享，長論證在書裡、在圖書館、在你願意往下點的地方。</p>
      <p>《台灣大未來》寫於 2019–2020：瑞士參照、能源與空污、居住、醫療與科技。他要回答的不是口號，是：方向對了，台灣能不能站上另一個量級。</p>
"""
    else:
        content = f"""
      <p class="about-hook">{esc(ui.get("about_hook") or "")}</p>
      <p>NTU (civil engineering & law), University of Illinois MBA, licensed engineer, founder work in consulting and blockchain. He learned detail on job sites—then put the long view on the page.</p>
      <p>Author of books on drones, bitcoin, and Taiwan’s future. This site is his <strong>personal brand front door</strong>: short issues you can share, full arguments in the book.</p>
      <p><em>Taiwan's Great Future</em> (2019–2020) covers Switzerland as mirror, energy, housing, health, and tech. The question is simple and hard: if the direction is right, how high can Taiwan climb?</p>
"""
    body = f"""
  <section class="section">
    <div class="wrap about-page">
      <div class="about-hero">
        <img class="about-hero__photo" src="{author}" alt="{esc(ui["author_name"])}" width="600" height="800" />
        <div>
          <h1>{esc(ui["about_title"])}</h1>
          <p class="about-name">{esc(ui["author_name"])}</p>
          <p class="about-role">{esc(ui["author_role"])}</p>
        </div>
      </div>
      <div class="about-body wrap-narrow">
        {content}
        {cta_box(lang, books, depth)}
      </div>
    </div>
  </section>
"""
    return layout(
        lang,
        ui["about_title"],
        body,
        depth,
        current="about",
        path="about",
        image="author-avatar.jpg",
        desc=ui.get("about_hook") or DEFAULT_DESC[lang],
    )


def build_books(lang: str, books: dict) -> str:
    ui = UI[lang]
    depth = 2
    items = []
    for link in books["links"]:
        cls = "book-link is-primary" if link.get("primary") else "book-link"
        label = ui["primary_lib"] if link.get("primary") else t(link["label"], lang)
        items.append(
            f"""<a class="{cls}" href="{esc(link["url"])}" target="_blank" rel="noopener noreferrer">{esc(label)}</a>"""
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


def build_gallery(lang: str, gallery_data: dict) -> str:
    ui = UI[lang]
    depth = 2
    items = gallery_data.get("items") or []
    intro = t(gallery_data.get("intro") or {}, lang)
    clips_dir = SITE / "media" / "clips"
    thumbs = []
    payload = []
    for idx, item in enumerate(items):
        src = media_src(item["src"], depth)
        cap = t(item.get("caption") or {}, lang)
        if not cap:
            cap = t(item.get("caption") or {}, "zh")
        yt_id = item.get("youtube_id") or ""
        link = item.get("link") or ""
        link_type = item.get("link_type") or ""
        stem = Path(item.get("src") or "").stem
        clip_rel = ""
        clip_file = clips_dir / f"img-{stem}.mp4"
        if clip_file.exists() and not yt_id:
            clip_rel = f"clips/img-{stem}.mp4"
        thumb_src = src
        badge = ""
        extra_cls = ""
        if yt_id:
            badge = f'<span class="gallery-thumb__badge">{esc(ui["gallery_video"])}</span>'
            extra_cls = " gallery-thumb--video"
        elif clip_rel:
            badge = f'<span class="gallery-thumb__badge gallery-thumb__badge--clip">{esc(ui["gallery_clip"])}</span>'
            extra_cls = " gallery-thumb--clip"
        elif link_type in ("facebook", "web") and link:
            badge = f'<span class="gallery-thumb__badge">Link</span>'
            extra_cls = " gallery-thumb--link"
        alt = esc((cap[:60] if cap else f"Photo {idx + 1}").replace("\n", " "))
        thumbs.append(
            f"""<button type="button" class="gallery-thumb{extra_cls}" data-gallery-open="{idx}" aria-label="{esc(ui["gallery_open"])} {idx + 1}">
          <img src="{thumb_src}" alt="{alt}" loading="lazy" />
          <span class="gallery-thumb__n">{idx + 1}</span>
          {badge}
        </button>"""
        )
        payload.append(
            {
                "src": src,
                "caption": cap,
                "youtube_id": yt_id,
                "link": link,
                "link_type": link_type,
                "poster": thumb_src if yt_id else src,
                "clip": media_src(clip_rel, depth) if clip_rel else "",
                "kind": "youtube" if yt_id else ("clip" if clip_rel else "photo"),
            }
        )

    cover = items[0]["src"] if items else "image35.jpg"
    count_label = ui["gallery_count"].replace("{n}", str(len(items)))
    intro_html = f'<p class="gallery-intro">{esc(intro)}</p>' if intro else ""
    payload_json = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")

    body = f"""
  <section class="section">
    <div class="wrap gallery-page">
      <h1>{esc(ui["gallery_title"])}</h1>
      <p class="lede" style="color:var(--ink-soft)">{esc(ui["gallery_lede"])}</p>
      {intro_html}
      <p class="gallery-meta">{esc(count_label)}</p>
      <div class="gallery-grid" data-gallery-grid>
        {"".join(thumbs)}
      </div>
    </div>
  </section>

  <div class="lb" id="gallery-lightbox" hidden data-gallery-lightbox
       data-label-play="{esc(ui["gallery_play"])}"
       data-label-pause="{esc(ui["gallery_pause"])}"
       data-label-fs="{esc(ui["gallery_fullscreen"])}"
       data-label-fs-exit="{esc(ui["gallery_fullscreen_exit"])}"
       data-label-open-link="{esc(ui["gallery_open_link"])}"
       data-label-mode-photo="{esc(ui["gallery_mode_photo"])}"
       data-label-mode-video="{esc(ui["gallery_mode_video"])}"
       data-label-still="{esc(ui["gallery_still_label"])}"
       data-label-clip="{esc(ui["gallery_clip_label"])}"
       data-label-of="{esc(ui["gallery_of"])}">
    <div class="lb__backdrop" data-gallery-close tabindex="-1"></div>
    <div class="lb__panel" role="dialog" aria-modal="true" aria-label="{esc(ui["gallery_title"])}" data-gallery-panel>
      <button type="button" class="lb__close" data-gallery-close aria-label="{esc(ui["gallery_close"])}">×</button>
      <div class="lb__stage">
        <button type="button" class="lb__nav lb__nav--prev" data-gallery-prev aria-label="{esc(ui["gallery_prev"])}">‹</button>
        <div class="lb__media">
          <div class="lb__stack" data-gallery-stack>
            <div class="lb__pane lb__pane--still" data-gallery-still-pane>
              <div class="lb__pane-label" data-gallery-still-label>{esc(ui["gallery_still_label"])}</div>
              <img class="lb__img" data-gallery-img alt="" />
            </div>
            <div class="lb__pane lb__pane--clip" data-gallery-clip-pane hidden>
              <div class="lb__pane-label" data-gallery-clip-label>{esc(ui["gallery_clip_label"])}</div>
              <video class="lb__clip" data-gallery-clip controls playsinline preload="metadata"></video>
            </div>
            <div class="lb__video" data-gallery-video hidden></div>
          </div>
        </div>
        <button type="button" class="lb__nav lb__nav--next" data-gallery-next aria-label="{esc(ui["gallery_next"])}">›</button>
      </div>
      <div class="lb__footer">
        <div class="lb__counter">
          <span data-gallery-mode-label></span>
          · <span data-gallery-index>1</span>{esc(ui["gallery_of"])}<span data-gallery-total>{len(items)}</span>
        </div>
        <div class="lb__actions">
          <button type="button" class="btn btn-secondary lb__play" data-gallery-play>{esc(ui["gallery_play"])}</button>
          <span class="lb__countdown" data-gallery-countdown hidden aria-live="polite"></span>
          <div class="lb__delay" role="group" aria-label="{esc(ui["gallery_delay"])}">
            <button type="button" class="lb__delay-btn" data-gallery-delay-dec aria-label="{esc(ui["gallery_delay_dec"])}">−</button>
            <span class="lb__delay-val" data-gallery-delay-label>5 秒</span>
            <button type="button" class="lb__delay-btn" data-gallery-delay-inc aria-label="{esc(ui["gallery_delay_inc"])}">+</button>
          </div>
          <button type="button" class="btn btn-secondary lb__fs" data-gallery-fullscreen>{esc(ui["gallery_fullscreen"])}</button>
          <a class="btn btn-secondary" data-gallery-extlink hidden target="_blank" rel="noopener noreferrer">{esc(ui["gallery_open_link"])}</a>
        </div>
        <div class="lb__caption" data-gallery-caption></div>
      </div>
    </div>
  </div>
  <script type="application/json" id="gallery-data">{payload_json}</script>
"""
    return layout(
        lang,
        ui["gallery_title"],
        body,
        depth,
        current="gallery",
        path="gallery",
        image=cover,
        desc=ui["gallery_lede"],
    )


def write(path: Path, html: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def main():
    issues = load_json("issues.json")
    clusters = load_json("clusters.json")
    books = load_json("books.json")

    gallery_data = load_json("gallery.json")
    try:
        clips = load_json("clips.json")
    except Exception:
        clips = {}

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
        write(OUT / lang / "gallery" / "index.html", build_gallery(lang, gallery_data))
        for issue in issues:
            write(
                OUT / lang / "issues" / issue["slug"] / "index.html",
                build_issue(lang, issue, issues, books, clips),
            )

    n_gal = len(gallery_data.get("items") or [])
    print(f"Built {len(issues)} issues × 2 langs + home/about/books/gallery")
    print(f"Gallery photos: {n_gal}")
    print(f"Output: {OUT}")


if __name__ == "__main__":
    main()
