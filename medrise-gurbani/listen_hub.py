#!/usr/bin/env python3
"""MedRise Gurbani — full site build + "Listen everywhere" hub page.

Runs build.py's normal build, then adds:
  docs/medrise-gurbani-spotify-apple-music-youtube.html  (one page listing every release with
  Spotify / Apple Music / YouTube links, Spotify playlist embed, videos, FAQ + schema)
and links it from the nav, the home page, every shabad page and the sitemap.

Extra data lives in data/listen.json (playlists, releases not yet in shabads.json,
store links to add to existing entries). build.py and shabads.json are not modified.

Run:  python3 listen_hub.py      (GitHub Actions runs this instead of build.py)
"""
import json, re, datetime, pathlib
import build as B
from build import esc, img_src, platform_buttons, faq_section, faq_ld, PLATFORM_META

ROOT = B.ROOT
OUT = B.OUT
_LISTEN_FILE = ROOT / "data" / "listen.json"
LISTEN = json.load(open(_LISTEN_FILE, encoding="utf-8")) if _LISTEN_FILE.exists() else {}
LISTEN_SLUG = "medrise-gurbani-spotify-apple-music-youtube"
HUB_STORES = ["Spotify", "Apple Music", "YouTube", "YouTube Music", "All platforms"]

HUB_CSS = r"""
/* listen hub */
.hub-link{margin:16px 0 0;font-size:.95rem}
.hub-link a{color:var(--gold);font-weight:700;text-decoration:none;border-bottom:1px solid currentColor}
.hub-hero{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr);gap:clamp(24px,5vw,64px);align-items:center;padding-block:clamp(28px,5vw,64px)}
.hub-hero .lede{font-family:var(--serif);font-size:clamp(1.2rem,2vw,1.45rem);line-height:1.45;color:var(--ink-2);max-width:40ch;margin:16px 0 22px}
.hub-hero .gk{font-size:clamp(1.2rem,2.2vw,1.6rem);color:var(--rose);margin-top:12px}
.hub-hero .more{margin-top:14px}
.embed{border-radius:16px;overflow:hidden;box-shadow:var(--shadow);background:var(--surface-2)}
.embed iframe{display:block;width:100%;height:452px;border:0}
.embed-note{font-size:.8rem;color:var(--ink-3);margin:8px 2px 0}
@media(max-width:820px){.hub-hero{grid-template-columns:1fr}.embed iframe{height:380px}}
.tracks{display:grid;gap:0}
.track{display:grid;grid-template-columns:112px minmax(0,1fr);gap:18px 22px;padding:22px 0;border-bottom:1px solid var(--line);align-items:start}
.track .t-art img{width:112px;height:112px;object-fit:cover;border-radius:12px;box-shadow:0 8px 22px rgba(74,50,20,.14)}
.track h3{font-size:1.5rem}
.track h3 a{text-decoration:none}
.track .gk{color:var(--rose);font-size:1.08rem;margin:2px 0 4px}
.track .theme{margin:0 0 4px;color:var(--ink-2)}
.track .meta{font-size:.78rem;color:var(--ink-3);letter-spacing:.04em;margin-bottom:12px}
.track .t-more{display:inline-block;margin-top:10px;font-size:.88rem;font-weight:700;color:var(--gold);text-decoration:none}
.stores-sm .store{padding:7px 13px 7px 10px;font-size:.84rem}
.stores-sm .store svg{width:16px;height:16px}
@media(max-width:560px){.track{grid-template-columns:76px minmax(0,1fr);gap:12px 14px}.track .t-art img{width:76px;height:76px}.track h3{font-size:1.25rem}}
.plat{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px}
.plat > div{border:1px solid var(--line);border-radius:16px;padding:22px;background:var(--surface)}
.plat h3{font-size:1.45rem;margin-bottom:8px;display:flex;align-items:center;gap:10px}
.plat h3 svg{width:24px;height:24px;flex:none}
.plat p{margin:0 0 14px;color:var(--ink-2);font-size:.98rem}
.plat ul{margin:0 0 14px;padding-left:18px;color:var(--ink-2);font-size:.95rem}
.plat ul a{color:var(--ink);font-weight:600}
@media(max-width:900px){.plat{grid-template-columns:1fr}}
.vgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:22px}
.vgrid .video{margin:0}
.vgrid h3{font-size:1.15rem;margin-top:10px}
.vgrid h3 a{text-decoration:none}
.needs{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px;margin:0;padding:0;list-style:none}
.needs a{display:block;padding:14px 16px;border:1px solid var(--line);border-radius:12px;background:var(--surface);text-decoration:none}
.needs a:hover{border-color:var(--gold)}
.needs b{display:block;font-family:var(--serif);font-size:1.2rem;font-weight:600}
.needs span{font-size:.9rem;color:var(--ink-2)}
"""


def apply_link_additions():
    """Add store links from listen.json to shabads.json entries in memory (existing values always win)."""
    adds = LISTEN.get("link_additions", {})
    for s in B.SHABADS:
        a = adds.get(s["slug"])
        if not a:
            continue
        for k, v in (a.get("links") or {}).items():
            s.setdefault("links", {}).setdefault(k, v)
        if a.get("coming_soon") and s.get("coming_soon"):
            s["coming_soon"] = a["coming_soon"]


def yt_facade(yid, title):
    return f"""<div class="video"><div class="frame" id="yt-{yid}">
    <img src="https://i.ytimg.com/vi/{yid}/hqdefault.jpg" alt="Play {esc(title)} on YouTube" width="480" height="360" loading="lazy">
    <button type="button" aria-label="Play {esc(title)}" onclick="var f=this.parentNode,i=document.createElement('iframe');i.src='https://www.youtube-nocookie.com/embed/{yid}?autoplay=1';i.allow='autoplay; encrypted-media; picture-in-picture';i.allowFullscreen=true;i.title='{esc(title)}';f.replaceChildren(i)"><span><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg></span></button>
  </div></div>"""


def hub_tracks():
    """Every release as one flat list: shabads.json entries, their Spanish variants, then listen.json extras."""
    BASE = B.BASE
    out, known = [], set()
    for s in B.SHABADS:
        known.update({s["slug"], s["title"].lower()})
        out.append({"title": s["title"], "gk": s["gurmukhi_title"], "theme": s["theme"], "source": s["source"],
                    "date": s.get("release_date"), "links": s.get("links") or {}, "page": f"{s['slug']}.html",
                    "id": f"{BASE}/{s['slug']}.html#recording", "duration": s.get("duration"), "yid": s.get("youtube_id"),
                    "img": img_src(s["image_slug"], 600, s.get("image_remote")), "lang": "pa"})
        v = s.get("variant") or {}
        if v.get("slug"):
            out.append({"title": v["title"].split(" — ")[0] + " (Gurbani en Español)", "gk": s["gurmukhi_title"], "theme": v.get("theme") or s["theme"],
                        "source": s["source"], "date": v.get("release_date"), "links": v.get("links") or {}, "page": f"{v['slug']}.html",
                        "id": f"{BASE}/{v['slug']}.html#recording", "duration": None, "yid": v.get("youtube_id"),
                        "img": img_src(v["image_slug"], 600, v.get("image_remote")), "lang": "es"})
    for x in LISTEN.get("extra_tracks", []):
        if x.get("slug") in known or x["title"].lower() in known:
            continue   # already has a full page in shabads.json
        out.append({"title": x["title"], "gk": x["gurmukhi_title"], "theme": x["theme"], "source": x["source"],
                    "date": x.get("release_date"), "links": x.get("links") or {}, "page": None, "id": None,
                    "duration": x.get("duration"), "yid": x.get("youtube_id"), "img": x.get("image_remote") or "", "lang": "pa"})
    released = sorted([t for t in out if t["date"] and t["links"]], key=lambda t: t["date"], reverse=True)
    upcoming = [t for t in out if not (t["date"] and t["links"])]
    return released, upcoming


def need_label(theme):
    for p in ("A prayer for ", "A shabad for "):
        if theme.startswith(p):
            return "Shabad for " + theme[len(p):]
    return theme


def listen_page():
    BASE, SITE, TODAY = B.BASE, B.SITE, B.TODAY
    released, upcoming = hub_tracks()
    url = f"{BASE}/{LISTEN_SLUG}.html"
    al = SITE["artist_links"]
    playlists = LISTEN.get("playlists", [])
    main_pl = next((p for p in playlists if p.get("embed")), None)

    def row(t):
        src = t["source"]
        meta = [src["granth"]] + ([f"Ang {src['ang']}"] if src.get("ang") else [])
        if t["date"]:
            meta.append("Released " + datetime.date.fromisoformat(t["date"]).strftime("%B %-d, %Y"))
        links = {k: v for k, v in t["links"].items() if k in HUB_STORES}
        missing = [k for k in ("Spotify", "Apple Music") if k not in t["links"]]
        note = f'<p class="meta" style="margin:8px 0 0">Not yet on {esc(" or ".join(missing))}.</p>' if (missing and t["links"]) else ""
        href = t["page"] or t["links"].get("All platforms") or next(iter(t["links"].values()), "#")
        ext = "" if t["page"] else ' target="_blank" rel="noopener"'
        more = f'<a class="t-more" href="{t["page"]}#lyrics">{"Letra y significado" if t["lang"] == "es" else "Lyrics &amp; meaning"} →</a>' if t["page"] else ""
        return f"""<article class="track"{' lang="es"' if t["lang"] == "es" else ""}>
  <a class="t-art" href="{esc(href)}"{ext} tabindex="-1" aria-hidden="true"><img src="{esc(t['img'])}" alt="" width="112" height="112" loading="lazy"></a>
  <div>
    <h3><a href="{esc(href)}"{ext}>{esc(t['title'])}</a></h3>
    <div class="gk gurmukhi" lang="pa">{esc(t['gk'])}</div>
    <p class="theme">{esc(t['theme'])}</p>
    <div class="meta">{esc(" · ".join(meta))}</div>
    {platform_buttons(links).replace('class="stores"', 'class="stores stores-sm"') if links else ""}{note}{more}
  </div>
</article>"""

    rows = "".join(row(t) for t in released)
    soon = "".join(f'<li><a href="{t["page"]}">{esc(t["title"])}</a> — {esc(t["theme"])}</li>' for t in upcoming if t["page"])

    needs = "".join(
        f'<li><a href="{esc(t["page"] or t["links"].get("Spotify") or "#")}"{"" if t["page"] else " target=_blank rel=noopener"}><b>{esc(need_label(t["theme"]))}</b><span>{esc(t["title"])}</span></a></li>'
        for t in released if t["lang"] == "pa")

    videos = "".join(f'<div>{yt_facade(t["yid"], t["title"])}<h3><a href="{t["page"] or "https://www.youtube.com/watch?v=" + t["yid"]}">{esc(t["title"])}</a></h3></div>'
                     for t in released if t.get("yid"))

    on_spotify = [t["title"] for t in released if "Spotify" in t["links"]]
    on_apple = [t["title"] for t in released if "Apple Music" in t["links"]]
    on_yt = [t["title"] for t in released if "YouTube" in t["links"] or t.get("yid")]

    def btn(name, label=None):
        if name not in al: return ""
        color, path = PLATFORM_META[name]
        return (f'<a class="store" href="{esc(al[name])}" target="_blank" rel="noopener" style="--brand:{color}">'
                f'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="{path}"/></svg><span>{esc(label or name)}</span></a>')

    def icon(name):
        color, path = PLATFORM_META[name]
        return f'<svg viewBox="0 0 24 24" aria-hidden="true" style="fill:{color}"><path d="{path}"/></svg>'

    pl_items = "".join(f'<li><a href="{esc(p["url"])}" target="_blank" rel="noopener"{" lang=es" if p.get("lang") == "es" else ""}>{esc(p["name"])}</a></li>' for p in playlists if p.get("platform") == "Spotify")
    embed = ""
    if main_pl:
        embed = f"""<div><div class="embed"><iframe title="{esc(main_pl['name'])} — Spotify playlist" src="{esc(main_pl['embed'])}" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe></div>
  <p class="embed-note">Press play above to listen on Spotify without leaving this page. Log in to Spotify to hear full tracks.</p></div>"""

    needs_txt = "; ".join(f"{need_label(t['theme']).replace('Shabad for ', '')}: {t['title']}" for t in released if t["lang"] == "pa")
    faq = [
        ("Is MedRise Gurbani on Spotify?",
         f"Yes. MedRise Gurbani is on Spotify — search “MedRise Gurbani” or open the artist page and tap Follow so new shabads land in your Release Radar. On Spotify now: {', '.join(on_spotify)}."),
        ("Is MedRise Gurbani on Apple Music?",
         f"Yes. Open the MedRise Gurbani artist page on Apple Music and add the singles to your library. On Apple Music now: {', '.join(on_apple)}."),
        ("What is the MedRise Gurbani YouTube channel?",
         f"The channel is @MedRiseGurbani (youtube.com/@MedRiseGurbani), with music videos and shorts. The recordings are also on YouTube Music. On YouTube now: {', '.join(on_yt)}."),
        ("Which MedRise Gurbani shabad should I listen to?",
         f"Each shabad is chosen for a real-life moment — {needs_txt}."),
        ("Is there Gurbani in Spanish?",
         "Yes. Por Su Gracia is Inhi Ki Kirpa with Spanish narration (Gurbani en Español), on Spotify, Apple Music and other platforms, with its own Spanish lyrics-and-meaning page on this site."),
        ("Where can I read the lyrics and meaning?",
         "Every shabad with a page on this site carries the full Gurmukhi, a Roman transliteration you can sing from, the English meaning line by line, and the source Ang. Tap “Lyrics & meaning” under any shabad above."),
        ("Can I listen for free?",
         "Yes. YouTube is free, and Spotify's free tier plays every MedRise Gurbani shabad. Apple Music, Amazon Music, Deezer and TIDAL need their own subscriptions."),
    ]
    if not any(t["lang"] == "es" for t in released):
        faq = [f for f in faq if not f[0].startswith("Is there Gurbani in Spanish")]

    kw = ["MedRise Gurbani Spotify", "MedRise Gurbani Apple Music", "MedRise Gurbani YouTube", "Med Rise Gurbani", "Medrise Gurbani shabad",
          "MedRise Gurbani playlist", "MedRise shabad kirtan", "new Gurbani shabad 2026", "Gurbani shabad with meaning", "shabad kirtan on Spotify",
          "Gurbani playlist Spotify", "Gurbani on Apple Music", "Gurbani YouTube channel with translation", "Sikh meditation music", "Waheguru simran Spotify",
          "shabad for worry", "shabad for debt relief", "shabad for protection", "shabad for students", "Gurbani en Español"]
    chips = "".join(f"<li>{esc(k)}</li>" for k in kw)

    body = f"""
<nav class="crumbs" aria-label="Breadcrumb"><a href="./">MedRise Gurbani</a> › Listen everywhere</nav>
<section class="hub-hero">
  <div>
    <div class="eyebrow">Spotify · Apple Music · YouTube</div>
    <h1 style="margin-top:12px">MedRise Gurbani Shabads on Spotify, Apple Music &amp; YouTube</h1>
    <div class="gk gurmukhi" lang="pa">ਖੋਜ ਸਬਦ ਮਹਿ ਲੇਹ</div>
    <p class="lede">Every MedRise Gurbani shabad in one place. Pick your app and press play. Each one has its Gurmukhi, transliteration and English meaning on this site, so you understand every line you hear.</p>
    <div class="stores stores-big">{btn("Spotify", "Follow on Spotify")}{btn("Apple Music", "Apple Music")}{btn("YouTube", "Subscribe on YouTube")}</div>
    <div class="more">{platform_buttons({k: v for k, v in al.items() if k not in ("Spotify", "Apple Music", "YouTube")})}</div>
  </div>
  {embed}
</section>

<section class="section" id="all">
  <div class="section-head"><div><div class="eyebrow">{len(released)} releases · newest first</div><h2>Every shabad, every app</h2><p>Tap a store to open the shabad in that app. Tap the title for the full lyrics and meaning.</p></div></div>
  <div class="tracks">{rows}</div>
  {f'<p class="legend" style="margin-top:22px">Coming next:</p><ul class="legend" style="margin-top:4px">{soon}</ul>' if soon else ""}
</section>

<section class="section" id="needs">
  <div class="section-head"><div><div class="eyebrow">By need</div><h2>Find a shabad for what you're going through</h2><p>Every MedRise Gurbani release is chosen for a real moment in life.</p></div></div>
  <ul class="needs">{needs}</ul>
</section>

<section class="section" id="platforms">
  <div class="section-head"><div><div class="eyebrow">Where to listen</div><h2>Follow MedRise Gurbani in your app</h2><p>Following or subscribing is the single most useful thing you can do: it brings every new shabad to you the day it comes out.</p></div></div>
  <div class="plat">
    <div id="spotify"><h3>{icon("Spotify")}MedRise Gurbani on Spotify</h3><p>Follow the artist and new shabads appear in your Release Radar. Save the playlists to keep every shabad in one place.</p>{f"<ul>{pl_items}</ul>" if pl_items else ""}<div class="stores">{btn("Spotify", "Open on Spotify")}</div></div>
    <div id="apple-music"><h3>{icon("Apple Music")}MedRise Gurbani on Apple Music</h3><p>{len(on_apple)} shabads on Apple Music, from {esc(on_apple[-1]) if on_apple else "the first release"} to {esc(on_apple[0]) if on_apple else "the latest"}. Add them to your library to play them offline.</p><div class="stores">{btn("Apple Music", "Open on Apple Music")}</div></div>
    <div id="youtube"><h3>{icon("YouTube")}MedRise Gurbani on YouTube</h3><p>Music videos and shorts on the @MedRiseGurbani channel, plus every recording on YouTube Music. Subscribe and turn on notifications.</p><div class="stores">{btn("YouTube", "Open YouTube channel")}{btn("YouTube Music")}</div></div>
  </div>
</section>

{f'''<section class="section" id="videos">
  <div class="section-head"><div><div class="eyebrow">Watch</div><h2>MedRise Gurbani videos</h2><p>Tap any video to play it here.</p></div></div>
  <div class="vgrid">{videos}</div>
</section>''' if videos else ""}

{faq_section(faq, "Frequently asked", "Listening to MedRise Gurbani — questions and answers")}

<section class="keywords" id="keywords">
  <h2>Also searched as</h2>
  <p>Ways people look for MedRise Gurbani on each platform.</p>
  <ul class="chips">{chips}</ul>
</section>
"""

    items = []
    for i, t in enumerate(released):
        rec = {"@type": "MusicRecording", "name": t["title"], "alternateName": t["gk"], "byArtist": {"@id": f"{BASE}/#artist"},
               "genre": "Shabad Kirtan", "inLanguage": t["lang"], "datePublished": t["date"],
               "url": f"{BASE}/{t['page']}" if t["page"] else (t["links"].get("All platforms") or next(iter(t["links"].values()))),
               "sameAs": [u for k, u in t["links"].items() if k != "All platforms"],
               "image": t["img"] if t["img"].startswith("http") else f"{BASE}/{t['img']}"}
        if t["id"]: rec["@id"] = t["id"]
        if t["duration"]: rec["duration"] = t["duration"]
        items.append({"@type": "ListItem", "position": i + 1, "item": rec})
    graph = [
        {"@type": "CollectionPage", "@id": f"{url}#page", "url": url, "name": "MedRise Gurbani Shabads on Spotify, Apple Music & YouTube",
         "isPartOf": {"@id": f"{BASE}/#website"}, "about": {"@id": f"{BASE}/#artist"}, "inLanguage": "en", "dateModified": TODAY,
         "mainEntity": {"@type": "ItemList", "name": "MedRise Gurbani releases", "numberOfItems": len(items), "itemListElement": items}},
        B.ORG_LD,
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "MedRise Gurbani", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Listen everywhere", "item": url}]},
        faq_ld(faq),
    ] + [{"@type": "MusicPlaylist", "name": p["name"], "url": p["url"], "author": {"@id": f"{BASE}/#artist"}} for p in playlists]
    og_t = released[0] if released else None
    og = (og_t["img"] if og_t["img"].startswith("http") else f"{BASE}/{og_t['img'].replace('-600.', '-1200.')}") if og_t else f"{BASE}/{img_src('inhi-ki-kirpa',1200)}"
    newest = ", ".join([t["title"] for t in released if t["lang"] == "pa"][:3])
    desc = f"Every MedRise Gurbani shabad on Spotify, Apple Music & YouTube — {newest} and more, with Gurmukhi and meaning."
    return B.shell("MedRise Gurbani Shabads — Spotify, Apple Music & YouTube", desc, f"{LISTEN_SLUG}.html", body, og,
                   {"@context": "https://schema.org", "@graph": graph}, keywords=", ".join(kw))


def link_hub_everywhere():
    """Point the nav, home page and every shabad page at the hub, and add it to the sitemap."""
    hub = f"{LISTEN_SLUG}.html"
    home_old = f'<div id="listen">{platform_buttons(B.SITE["artist_links"])}</div>'
    home_new = (f'<div id="listen">{platform_buttons(B.SITE["artist_links"])}'
                f'<p class="hub-link"><a href="{hub}">Every MedRise Gurbani shabad on Spotify, Apple Music &amp; YouTube →</a></p></div>')
    shabad_link = f'<p class="hub-link"><a href="{hub}">Hear every MedRise Gurbani shabad on Spotify, Apple Music &amp; YouTube →</a></p>'
    for f in OUT.glob("*.html"):
        h = f.read_text(encoding="utf-8")
        h2 = h.replace('<a href="./#listen">Listen</a>', f'<a href="{hub}">Listen</a>')
        if f.name == "index.html":
            h2 = h2.replace(home_old, home_new)
        h2 = re.sub(r'(<div><h2>When to listen</h2>.*?)(</div>\n</section>)', lambda m: m.group(1) + shabad_link + m.group(2), h2, count=1, flags=re.S)
        if h2 != h:
            f.write_text(h2, encoding="utf-8")
    sm = OUT / "sitemap.xml"
    x = sm.read_text(encoding="utf-8")
    if hub not in x:
        entry = f"<url><loc>{esc(B.BASE)}/{hub}</loc><lastmod>{B.TODAY}</lastmod><changefreq>weekly</changefreq><priority>0.9</priority></url>"
        x = x.replace("</url>", "</url>\n" + entry, 1)
        sm.write_text(x, encoding="utf-8")
    css = OUT / "style.css"
    css.write_text(css.read_text(encoding="utf-8") + HUB_CSS.lstrip("\n"), encoding="utf-8")


def main():
    apply_link_additions()
    B.build()
    (OUT / f"{LISTEN_SLUG}.html").write_text(listen_page(), encoding="utf-8")
    link_hub_everywhere()
    print(f"Added hub page {LISTEN_SLUG}.html (+ nav, home, shabad-page and sitemap links)")


if __name__ == "__main__":
    main()
