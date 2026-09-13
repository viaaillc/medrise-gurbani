#!/usr/bin/env python3
"""MedRise Gurbani — static site generator.

Reads data/shabads.json, writes a complete static site into docs/ (GitHub Pages).
Run:  python3 build.py
"""
import json, os, shutil, html, datetime, pathlib

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "docs"
DATA = json.load(open(ROOT / "data" / "shabads.json", encoding="utf-8"))
SITE = DATA["site"]
SHABADS = DATA["shabads"]
BASE = SITE["url"].rstrip("/")
TODAY = datetime.date.today().isoformat()

def esc(s):
    return html.escape(s or "", quote=True)

def img_src(slug_or_shabad, size=1200, remote_fallback=None):
    slug = slug_or_shabad
    local = ROOT / "images" / f"{slug}-{size}.jpg"
    if local.exists():
        return f"images/{slug}-{size}.jpg"
    return remote_fallback or f"images/{slug}-{size}.jpg"

# ----------------------------------------------------------------------------- platforms
PLATFORM_META = {
    "Spotify":       ("#1DB954", "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm4.3 14.4a.7.7 0 0 1-1 .2c-2.6-1.6-5.9-2-9.8-1.1a.7.7 0 0 1-.3-1.4c4.3-1 8-.5 10.9 1.3.3.2.4.7.2 1zm1.1-2.6a.9.9 0 0 1-1.2.3c-3-1.8-7.5-2.4-11-1.3a.9.9 0 1 1-.5-1.7c4-1.2 9-.6 12.4 1.5.4.3.6.8.3 1.2zm.1-2.7c-3.6-2.1-9.5-2.3-12.9-1.3a1.1 1.1 0 1 1-.6-2c3.9-1.2 10.4-1 14.5 1.5a1.1 1.1 0 0 1-1 1.8z"),
    "Apple Music":   ("#FA2D48", "M17.4 2H6.6A4.6 4.6 0 0 0 2 6.6v10.8A4.6 4.6 0 0 0 6.6 22h10.8a4.6 4.6 0 0 0 4.6-4.6V6.6A4.6 4.6 0 0 0 17.4 2zm-1 4.6v8.2c0 1.4-1.1 2.3-2.4 2.3s-2.2-.8-2.2-1.8.9-1.8 2.2-1.8c.4 0 .8.1 1 .2V9.2l-4.6 1v6.4c0 1.4-1.1 2.3-2.4 2.3S5.8 18 5.8 17s.9-1.8 2.2-1.8c.4 0 .8.1 1 .2V8.2l7.4-1.6z"),
    "YouTube":       ("#FF0000", "M23 7.2a3 3 0 0 0-2.1-2.1C19 4.6 12 4.6 12 4.6s-7 0-8.9.5A3 3 0 0 0 1 7.2 31 31 0 0 0 .5 12 31 31 0 0 0 1 16.8a3 3 0 0 0 2.1 2.1c1.9.5 8.9.5 8.9.5s7 0 8.9-.5a3 3 0 0 0 2.1-2.1A31 31 0 0 0 23.5 12 31 31 0 0 0 23 7.2zM9.7 15.1V8.9l6 3.1-6 3.1z"),
    "YouTube Music": ("#FF0000", "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm0 15.6a5.6 5.6 0 1 1 0-11.2 5.6 5.6 0 0 1 0 11.2zm0-9.8a4.2 4.2 0 1 0 0 8.4 4.2 4.2 0 0 0 0-8.4zm-1.4 6.4V9.8l3.8 2.2-3.8 2.2z"),
    "Amazon Music":  ("#25D1DA", "M2.6 16.9c3 2.2 6.3 3.3 9.7 3.3 2.9 0 6-.7 8.5-2.1.4-.2.7.2.4.5-2.3 2-5.8 3-9 3-3.9 0-7.5-1.4-10.1-3.9-.3-.3 0-.6.5-.8zm18.4-1.7c-.3-.4-2-.2-2.8-.1-.2 0-.3-.2-.1-.3 1.4-1 3.6-.7 3.9-.4.3.3-.1 2.6-1.3 3.7-.2.2-.4.1-.3-.1.3-.7.9-2.3.6-2.8zM9.2 8.5V7.4c0-.2.1-.3.3-.3h5.3c.2 0 .3.1.3.3v1c0 .2-.1.4-.4.8l-2.7 3.9c1-.1 2.1.1 3 .6.2.1.3.3.3.5v1.2c0 .2-.2.4-.4.3a6 6 0 0 0-5.6 0c-.2.1-.4-.1-.4-.3v-1.1c0-.2 0-.6.2-.9l3.2-4.5H9.5c-.2 0-.3-.1-.3-.4z"),
    "Deezer":        ("#A238FF", "M18.8 4h4.7v2.8h-4.7zM18.8 8.1h4.7v2.8h-4.7zM18.8 12.2h4.7V15h-4.7zM18.8 16.3h4.7v2.8h-4.7zM12.6 12.2h4.7V15h-4.7zM12.6 16.3h4.7v2.8h-4.7zM6.4 12.2h4.7V15H6.4zM6.4 16.3h4.7v2.8H6.4zM.2 16.3h4.7v2.8H.2zM12.6 8.1h4.7v2.8h-4.7z"),
    "TIDAL":         ("currentColor", "M8 4l4 4-4 4-4-4zm8 0l4 4-4 4-4-4zm-4 8l4 4-4 4-4-4z"),
    "All platforms": ("#7A5C2E", "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm0 2c1.3 0 2.5 2.8 2.8 6.5h-5.6C9.5 6.8 10.7 4 12 4zM4.3 13.5h4.4c.1 1.9.5 3.6 1 5A8 8 0 0 1 4.3 13.5zm0-3a8 8 0 0 1 5.4-5c-.5 1.4-.9 3.1-1 5H4.3zm7.7 9.5c-1.3 0-2.5-2.8-2.8-6.5h5.6C14.5 17.2 13.3 20 12 20zm2.3-1.5c.5-1.4.9-3.1 1-5h4.4a8 8 0 0 1-5.4 5zm1-8c-.1-1.9-.5-3.6-1-5a8 8 0 0 1 5.4 5h-4.4z"),
}
PLATFORM_ORDER = ["Spotify", "Apple Music", "YouTube", "YouTube Music", "Amazon Music", "Deezer", "TIDAL", "All platforms"]

def platform_buttons(links, big=False):
    items = []
    for name in PLATFORM_ORDER:
        if name not in links:
            continue
        color, path = PLATFORM_META[name]
        items.append(
            f'<a class="store" href="{esc(links[name])}" target="_blank" rel="noopener" style="--brand:{color}">'
            f'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="{path}"/></svg><span>{esc(name)}</span></a>')
    return f'<div class="stores{" stores-big" if big else ""}">{"".join(items)}</div>'

# ----------------------------------------------------------------------------- CSS
CSS = r"""
:root{
  --ground:#FBF6EE; --surface:#F4ECE2; --surface-2:#EDE2D4; --line:#E1D3C1;
  --ink:#2B2330; --ink-2:#5E5262; --ink-3:#8A7D8C;
  --gold:#B8862B; --gold-2:#D9B25F; --rose:#B4566E; --rose-soft:#F1DCE1;
  --shadow:0 18px 50px rgba(74,50,20,.16);
  --serif:"Cormorant Garamond",Georgia,"Times New Roman",serif;
  --sans:"Source Sans 3","Segoe UI",Helvetica,Arial,sans-serif;
  --gurmukhi:"Noto Serif Gurmukhi","Raavi","Mukta Mahee",serif;
  color-scheme:light;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --ground:#1B1620; --surface:#241D2A; --surface-2:#2E2534; --line:#3D3243;
    --ink:#F2E9DF; --ink-2:#C9BCC4; --ink-3:#978A99;
    --gold:#D9A84E; --gold-2:#B8862B; --rose:#E28FA6; --rose-soft:#3A2830;
    --shadow:0 18px 50px rgba(0,0,0,.45); color-scheme:dark;
  }
}
:root[data-theme="dark"]{
  --ground:#1B1620; --surface:#241D2A; --surface-2:#2E2534; --line:#3D3243;
  --ink:#F2E9DF; --ink-2:#C9BCC4; --ink-3:#978A99;
  --gold:#D9A84E; --gold-2:#B8862B; --rose:#E28FA6; --rose-soft:#3A2830;
  --shadow:0 18px 50px rgba(0,0,0,.45); color-scheme:dark;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--ground);color:var(--ink);font-family:var(--sans);font-size:17px;line-height:1.6;
  padding-inline:clamp(16px,4vw,48px);padding-block:0}
img{max-width:100%;height:auto;display:block}
a{color:inherit}
:focus-visible{outline:2px solid var(--gold);outline-offset:3px;border-radius:4px}
.wrap{max-width:1180px;margin:0 auto}
.eyebrow{font-family:var(--sans);font-size:.72rem;letter-spacing:.18em;text-transform:uppercase;color:var(--gold);font-weight:600}
h1,h2,h3{font-family:var(--serif);font-weight:600;line-height:1.08;margin:0;text-wrap:balance}
h1{font-size:clamp(2.2rem,5vw,3.6rem)} h2{font-size:clamp(1.7rem,3.2vw,2.4rem)} h3{font-size:1.35rem}
.gurmukhi{font-family:var(--gurmukhi);font-weight:500}

/* header */
.top{display:flex;align-items:center;justify-content:space-between;gap:16px;padding-block:22px;border-bottom:1px solid var(--line)}
.brand{display:flex;align-items:center;gap:12px;text-decoration:none}
.brand svg{width:34px;height:34px;color:var(--gold)}
.brand b{font-family:var(--serif);font-weight:600;font-size:1.35rem;letter-spacing:.01em}
.brand small{display:block;font-size:.66rem;letter-spacing:.16em;text-transform:uppercase;color:var(--ink-3);font-weight:600;margin-top:2px}
nav.main{display:flex;gap:22px;font-size:.92rem;font-weight:600}
nav.main a{text-decoration:none;color:var(--ink-2)} nav.main a:hover{color:var(--gold)}
@media(max-width:560px){nav.main{display:none}}

/* hero (home) */
.hero{display:grid;grid-template-columns:1.1fr .9fr;gap:clamp(24px,5vw,64px);align-items:center;padding-block:clamp(40px,7vw,88px)}
.hero p.lede{font-family:var(--serif);font-size:clamp(1.25rem,2vw,1.55rem);line-height:1.45;color:var(--ink-2);max-width:34ch;margin:18px 0 26px}
.hero .gk{font-size:clamp(1.3rem,2.4vw,1.8rem);color:var(--rose);margin-top:14px}
.hero-art{position:relative;aspect-ratio:1;max-width:100%}
.hero-art img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;border-radius:18px;box-shadow:var(--shadow)}
.hero-art img:nth-child(1){transform:rotate(-7deg) translate(-9%,3%) scale(.86);opacity:.85}
.hero-art img:nth-child(2){transform:rotate(5deg) translate(9%,-4%) scale(.9);opacity:.92}
.hero-art img:nth-child(3){transform:none}
@media(max-width:820px){.hero{grid-template-columns:1fr}.hero-art{max-width:420px;margin:0 auto}}

/* store buttons */
.stores{display:flex;flex-wrap:wrap;gap:10px}
.store{display:inline-flex;align-items:center;gap:9px;padding:9px 16px 9px 12px;border:1px solid var(--line);border-radius:999px;
  background:var(--surface);text-decoration:none;font-size:.9rem;font-weight:600;color:var(--ink);transition:transform .15s,border-color .15s,box-shadow .15s}
.store svg{width:18px;height:18px;fill:var(--brand)}
.store:hover{transform:translateY(-1px);border-color:var(--brand);box-shadow:0 6px 18px rgba(0,0,0,.08)}
.stores-big .store{padding:12px 20px 12px 15px;font-size:.98rem}
.stores-big .store svg{width:21px;height:21px}
:root[data-theme="dark"] .store svg[style],.store svg{filter:none}

/* release grid */
.section{padding-block:clamp(36px,6vw,72px);border-top:1px solid var(--line)}
.section-head{display:flex;align-items:end;justify-content:space-between;gap:16px;margin-bottom:28px;flex-wrap:wrap}
.section-head p{margin:6px 0 0;color:var(--ink-2);max-width:60ch}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:28px 24px}
.card{text-decoration:none;color:inherit;display:grid;gap:12px}
.card .art{aspect-ratio:1;border-radius:14px;overflow:hidden;box-shadow:var(--shadow);background:var(--surface-2)}
.card .art img{width:100%;height:100%;object-fit:cover;transition:transform .5s ease}
.card:hover .art img{transform:scale(1.035)}
.card h3{font-size:1.5rem}
.card .gk{color:var(--rose);font-size:1.05rem;margin-top:-4px}
.card .theme{color:var(--ink-2);font-size:.95rem;margin:0}
.card .meta{font-size:.78rem;color:var(--ink-3);letter-spacing:.04em}
.badge{display:inline-block;font-size:.68rem;letter-spacing:.14em;text-transform:uppercase;font-weight:700;color:var(--rose);background:var(--rose-soft);padding:4px 10px;border-radius:999px}

/* shabad page */
.crumbs{font-size:.85rem;color:var(--ink-3);padding-block:18px 0}
.crumbs a{text-decoration:none;color:var(--ink-2)}
.shabad-top{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,7fr);gap:clamp(28px,5vw,72px);padding-block:clamp(28px,4vw,56px);align-items:start}
.shabad-top .art{position:sticky;top:24px;border-radius:18px;overflow:hidden;box-shadow:var(--shadow)}
.shabad-top .art img{aspect-ratio:1;object-fit:cover;width:100%}
.art-dl{display:block;margin-top:10px;font-size:.8rem;color:var(--ink-3);text-decoration:none;letter-spacing:.04em}
.art-dl:hover{color:var(--gold)}
.title-block .gk-title{font-size:clamp(1.55rem,3.4vw,2.4rem);color:var(--rose);margin:14px 0 6px;line-height:1.35}
.title-block .sub{font-family:var(--serif);font-size:1.3rem;color:var(--ink-2);margin:0 0 14px;line-height:1.35}
.source{display:flex;flex-wrap:wrap;gap:8px 22px;font-size:.86rem;color:var(--ink-3);margin:0 0 26px;padding:0;list-style:none}
.source b{color:var(--ink-2);font-weight:600}
.intent{font-size:1.05rem;color:var(--ink-2);max-width:62ch;margin:0 0 26px}
.notice{border-left:3px solid var(--gold);padding:10px 16px;background:var(--surface);border-radius:0 10px 10px 0;font-size:.95rem;margin:0 0 22px;color:var(--ink-2)}
.listen-label{margin:0 0 12px}
@media(max-width:820px){.shabad-top{grid-template-columns:1fr}.shabad-top .art{position:static;max-width:520px}}

/* video */
.video{margin-top:34px}
.video .frame{position:relative;aspect-ratio:16/9;border-radius:14px;overflow:hidden;background:#000;box-shadow:var(--shadow)}
.video .frame img,.video .frame iframe{position:absolute;inset:0;width:100%;height:100%;border:0;object-fit:cover}
.video button{position:absolute;inset:0;width:100%;height:100%;border:0;background:transparent;cursor:pointer;display:grid;place-items:center}
.video button span{display:grid;place-items:center;width:78px;height:78px;border-radius:50%;background:rgba(255,255,255,.92);color:#B4566E;box-shadow:0 10px 30px rgba(0,0,0,.35)}
.video button svg{width:30px;height:30px;margin-left:4px}

/* verses */
.verses{padding-block:clamp(36px,6vw,72px);border-top:1px solid var(--line)}
.verses .lead{max-width:64ch;color:var(--ink-2);margin:8px 0 34px}
.verse{display:grid;grid-template-columns:44px 1fr;gap:0 18px;padding:22px 0;border-bottom:1px solid var(--line);max-width:860px}
.verse .n{font-family:var(--serif);font-size:1.1rem;color:var(--ink-3);padding-top:6px;font-variant-numeric:tabular-nums}
.verse .g{font-family:var(--gurmukhi);font-size:clamp(1.35rem,2.3vw,1.7rem);line-height:1.7;font-weight:500}
.verse .h{font-family:"Noto Serif Devanagari","Mangal",serif;font-size:1.05rem;color:var(--ink-2);margin:6px 0 0;line-height:1.6}
.verse .t{font-family:var(--serif);font-style:italic;font-size:1.15rem;color:var(--ink-2);margin:8px 0 6px;line-height:1.45}
.verse .e{margin:0;color:var(--ink);max-width:62ch}
.verse.key{background:linear-gradient(90deg,var(--surface),transparent);border-left:3px solid var(--gold);padding-left:18px;margin-left:-21px;border-radius:0 12px 12px 0}
.verse.key .n{color:var(--gold)}
.tag{display:inline-block;font-size:.66rem;letter-spacing:.16em;text-transform:uppercase;color:var(--gold);font-weight:700;margin-bottom:6px}
.legend{font-size:.82rem;color:var(--ink-3);margin-top:18px;max-width:64ch}

/* meaning + faq */
.meaning{padding-block:clamp(36px,6vw,64px);border-top:1px solid var(--line)}
.meaning p{max-width:68ch;color:var(--ink-2);margin:0 0 16px;font-size:1.05rem}
.meaning p:first-of-type{color:var(--ink);font-family:var(--serif);font-size:1.3rem;line-height:1.5}
.faq{padding-block:clamp(36px,6vw,64px);border-top:1px solid var(--line)}
.faq details{border-bottom:1px solid var(--line);padding:14px 0;max-width:800px}
.faq summary{font-family:var(--serif);font-size:1.25rem;font-weight:600;cursor:pointer;list-style:none;display:flex;justify-content:space-between;gap:16px}
.faq summary::after{content:"+";color:var(--gold);font-weight:400}
.faq details[open] summary::after{content:"–"}
.faq details p{margin:10px 0 0;color:var(--ink-2);max-width:66ch}
.lang-switch{display:inline-flex;gap:8px;align-items:center;font-size:.85rem;margin-top:14px}
.lang-switch a{text-decoration:none;color:var(--gold);font-weight:700;border:1px solid var(--line);border-radius:999px;padding:5px 12px;background:var(--surface)}
/* two-col info */
.info{display:grid;grid-template-columns:1fr 1fr;gap:32px;padding-block:clamp(36px,6vw,64px);border-top:1px solid var(--line)}
.info h2{font-size:1.6rem;margin-bottom:10px}
.info p{margin:0 0 12px;color:var(--ink-2);max-width:60ch}
@media(max-width:720px){.info{grid-template-columns:1fr}}

/* prev/next */
.pn{display:grid;grid-template-columns:1fr 1fr;gap:20px;padding-block:32px;border-top:1px solid var(--line)}
.pn a{display:flex;gap:14px;align-items:center;text-decoration:none;padding:12px;border:1px solid var(--line);border-radius:14px;background:var(--surface)}
.pn a img{width:64px;height:64px;border-radius:8px;object-fit:cover;flex:none}
.pn a.next{flex-direction:row-reverse;text-align:right}
.pn small{display:block;font-size:.68rem;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-3);font-weight:700}
.pn b{font-family:var(--serif);font-size:1.15rem;font-weight:600}
@media(max-width:600px){.pn{grid-template-columns:1fr}}

/* keywords */
.keywords{padding-block:clamp(32px,5vw,56px);border-top:1px solid var(--line)}
.keywords h2{font-size:1.25rem;margin-bottom:6px}
.keywords p{color:var(--ink-3);font-size:.9rem;margin:0 0 16px;max-width:64ch}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:0;padding:0;list-style:none}
.chips li{font-size:.82rem;padding:5px 12px;border:1px solid var(--line);border-radius:999px;background:var(--surface);color:var(--ink-2)}

/* footer */
footer{border-top:1px solid var(--line);padding-block:36px 44px;display:grid;gap:18px;color:var(--ink-3);font-size:.88rem}
footer .row{display:flex;flex-wrap:wrap;justify-content:space-between;gap:16px;align-items:center}
footer .links{display:flex;flex-wrap:wrap;gap:14px}
footer .links a{text-decoration:none;color:var(--ink-2);font-weight:600} footer .links a:hover{color:var(--gold)}
.ornament{color:var(--gold);letter-spacing:.4em;font-size:.9rem}

@media(prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
"""

# ----------------------------------------------------------------------------- shell
LOTUS = '<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M24 40c-8-4-13-11-13-19 5 1 9 4 13 9 4-5 8-8 13-9 0 8-5 15-13 19z"/><path d="M24 30c-2-8-1-16 0-22 1 6 2 14 0 22z"/><path d="M11 21c-4 1-7 3-9 6 6 2 12 2 18 0M37 21c4 1 7 3 9 6-6 2-12 2-18 0"/></svg>'

def shell(title, desc, canonical_path, body, og_image, jsonld, extra_head="", og_type="website", keywords="", lang="en", alternates=None):
    canonical = f"{BASE}/{canonical_path}".rstrip("/") + ("/" if canonical_path == "" else "")
    if alternates:
        extra_head += "".join(f'<link rel="alternate" hreflang="{l}" href="{esc(u)}">' for l, u in alternates)
    return f"""<!DOCTYPE html>
<html lang="{lang}" prefix="og: https://ogp.me/ns#">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{f'<meta name="keywords" content="{esc(keywords)}">' if keywords else ''}
<link rel="canonical" href="{esc(canonical)}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#FBF6EE" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#1B1620" media="(prefers-color-scheme: dark)">
<meta property="og:site_name" content="MedRise Gurbani">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(canonical)}">
<meta property="og:image" content="{esc(og_image)}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="1200">
<meta property="og:locale" content="{"es_ES" if lang=="es" else "en_US"}"><meta property="og:locale:alternate" content="pa_IN">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{esc(og_image)}">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Noto+Serif+Gurmukhi:wght@400;500;600&family=Noto+Serif+Devanagari:wght@400;500&family=Source+Sans+3:wght@400;600;700&display=swap">
<link rel="stylesheet" href="style.css">
<link rel="sitemap" type="application/xml" href="sitemap.xml">
{extra_head}
<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
</head>
<body>
<div class="wrap">
<header class="top">
  <a class="brand" href="./" aria-label="MedRise Gurbani home">{LOTUS}<span><b>MedRise Gurbani</b><small>Meditate and Rise with Gurbani</small></span></a>
  <nav class="main" aria-label="Main"><a href="./#shabads">Shabads</a><a href="./#listen">Listen</a><a href="about.html">About</a></nav>
</header>
{body}
<footer>
  <div class="ornament" aria-hidden="true">✦ ✦ ✦</div>
  <div class="row">
    <div>© {TODAY[:4]} MedRise Gurbani · Meditate and Rise with Gurbani. Gurbani text is Sri Guru Granth Sahib Ji and Sri Dasam Granth Sahib; translations are provided for understanding and may be imperfect.</div>
    <div class="links">{''.join(f'<a href="{esc(u)}" target="_blank" rel="noopener">{esc(n)}</a>' for n,u in SITE['artist_links'].items())}</div>
  </div>
</footer>
</div>
</body>
</html>"""

ORG_LD = {
    "@type": "MusicGroup", "@id": f"{BASE}/#artist", "name": "MedRise Gurbani",
    "url": BASE + "/", "genre": ["Shabad Kirtan", "Gurbani", "Devotional"],
    "alternateName": SITE.get("alternate_names", []),
    "sameAs": list(SITE["artist_links"].values()),
    "description": SITE["description"],
    "logo": f"{BASE}/favicon.svg",
    "image": f"{BASE}/images/inhi-ki-kirpa-1200.jpg",
}

# ----------------------------------------------------------------------------- pages
def home():
    latest = [s for s in SHABADS if s.get("release_date")]
    latest.sort(key=lambda s: s["release_date"], reverse=True)
    hero_imgs = [latest[2], latest[1], latest[0]]
    hero_art = "".join(f'<img src="{img_src(s["image_slug"],1200,s.get("image_remote"))}" alt="{esc(s["title"])} cover art" width="1200" height="1200" {"loading=lazy" if i<2 else ""}>' for i, s in enumerate(hero_imgs))

    cards = []
    for s in SHABADS:
        badge = f'<span class="badge">{"Coming soon" if not s.get("release_date") else "New"}</span>' if (not s.get("release_date") or s["release_date"] >= "2026-09-07") else ""
        meta = f'{s["source"]["granth"]}' + (f' · Ang {s["source"]["ang"]}' if s["source"].get("ang") else "")
        cards.append(f"""<a class="card" href="{s['slug']}.html">
  <div class="art"><img src="{img_src(s['image_slug'],600,s.get('image_remote'))}" alt="{esc(s['title'])} — MedRise Gurbani cover art" width="600" height="600" loading="lazy"></div>
  <div>{badge}<h3>{esc(s['title'])}</h3><div class="gk gurmukhi">{esc(s['gurmukhi_title'])}</div></div>
  <p class="theme">{esc(s['theme'])}</p>
  <div class="meta">{esc(meta)}</div>
</a>""")
        if s.get("variant", {}).get("slug"):
            v = s["variant"]
            cards.append(f"""<a class="card" href="{v['slug']}.html" hreflang="es" lang="es">
  <div class="art"><img src="{img_src(v['image_slug'],600,v.get('image_remote'))}" alt="{esc(v['title'])} — MedRise Gurbani portada" width="600" height="600" loading="lazy"></div>
  <div><span class="badge">En español</span><h3>{esc(v['title'].split(' — ')[0])}</h3><div class="gk gurmukhi" lang="pa">{esc(s['gurmukhi_title'])}</div></div>
  <p class="theme">{esc(v.get('theme') or s['theme'])}</p>
  <div class="meta">{esc(meta)} · Gurbani en Español</div>
</a>""")

    body = f"""
<section class="hero">
  <div>
    <div class="eyebrow">Shabad Kirtan · Gurmukhi · Transliteration · Meaning</div>
    <h1 style="margin-top:14px">Meditate and Rise with Gurbani</h1>
    <div class="gk gurmukhi">ਖੋਜ ਸਬਦ ਮਹਿ ਲੇਹ</div>
    <p class="lede">A shabad for every moment of your life — protection, debt relief, peace of mind, study and success — sung softly, with every line explained.</p>
    <div id="listen">{platform_buttons(SITE['artist_links'])}</div>
  </div>
  <div class="hero-art">{hero_art}</div>
</section>

<section class="section" id="shabads">
  <div class="section-head"><div><div class="eyebrow">The shabads</div><h2>Every release, line by line</h2><p>Each page carries the full Gurmukhi, a Roman transliteration you can sing from, the English meaning, and the source Ang — plus links to every store the shabad is on.</p></div></div>
  <div class="grid">{''.join(cards)}</div>
</section>

<section class="section">
  <div class="info" style="border:0;padding-block:0">
    <div><h2>Why MedRise Gurbani</h2><p>MedRise Gurbani was created so that anyone — whether they grew up with kirtan or are hearing it for the first time — can understand what they are singing. Every shabad is chosen for a real-life need and presented with its meaning, so the Guru's words can be carried into an exam room, a hospital shift, a new city, or a hard conversation.</p></div>
    <div><h2>How to use these pages</h2><p>Read the Gurmukhi if you can; if not, sing from the transliteration. Read the meaning once before you listen, then let the shabad play. The highlighted line on each page is the <em>rahao</em> or central line — the one to hold onto through the day.</p></div>
  </div>
</section>
"""
    jsonld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebSite", "@id": f"{BASE}/#website", "url": BASE + "/", "name": "MedRise Gurbani",
         "description": SITE["description"], "inLanguage": ["en", "pa"], "publisher": {"@id": f"{BASE}/#artist"}},
        ORG_LD,
        {"@type": "ItemList", "name": "MedRise Gurbani shabads", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "url": u, "name": n} for i, (u, n) in enumerate(
                [(f"{BASE}/{s['slug']}.html", s["title"]) for s in SHABADS] +
                [(f"{BASE}/{s['variant']['slug']}.html", s["variant"]["title"]) for s in SHABADS if s.get("variant", {}).get("slug")])]},
    ]}
    og = f"{BASE}/{img_src(latest[0]['image_slug'],1200,latest[0].get('image_remote'))}"
    kw = ", ".join(["MedRise Gurbani", "shabad kirtan", "Gurbani with English translation", "Gurmukhi transliteration", "shabad for protection", "shabad for debt relief", "shabad for peace", "shabad for students"] + [s["title"] for s in SHABADS])
    return shell("MedRise Gurbani — Shabad Kirtan with Gurmukhi, Transliteration & Meaning", SITE["description"], "", body, og, jsonld, keywords=kw)


def shabad_page(i, s):
    prev_s = SHABADS[i - 1] if i > 0 else None
    next_s = SHABADS[i + 1] if i < len(SHABADS) - 1 else None
    src = s["source"]
    art = img_src(s["image_slug"], 1200, s.get("image_remote"))
    full = ROOT / "images" / "full" / f"{s['image_slug']}.jpg"
    dl = f'<a class="art-dl" href="images/full/{s["image_slug"]}.jpg" download>Download cover art · 3000 × 3000</a>' if full.exists() else ""

    source_items = [f"<li><b>{esc(src['granth'])}</b></li>"]
    if src.get("ang"): source_items.append(f"<li>Ang {src['ang']}</li>")
    if src.get("raag"): source_items.append(f"<li>{esc(src['raag'])}</li>")
    if src.get("writer"): source_items.append(f"<li>{esc(src['writer'])}</li>")
    if s.get("release_date"):
        d = datetime.date.fromisoformat(s["release_date"])
        source_items.append(f"<li>Released {d.strftime('%B %-d, %Y')}</li>")

    notice = f'<p class="notice">{esc(s["coming_soon"])}</p>' if s.get("coming_soon") else ""
    listen = f'<p class="eyebrow listen-label">Listen on</p>{platform_buttons(s["links"], big=True)}' if s["links"] else ""

    variant = ""
    if s.get("variant"):
        v = s["variant"]
        variant = f"""
<section class="section">
  <div class="shabad-top" style="padding-block:0">
    <div class="art" style="position:static"><img src="{img_src(v['image_slug'],1200,v.get('image_remote'))}" alt="{esc(v['title'])} cover art" width="1200" height="1200" loading="lazy"></div>
    <div><div class="eyebrow">Spanish version · Versión en español</div><h2 style="margin:12px 0 10px">{esc(v['title'])}</h2><p class="intent">{esc(v['note'])}</p>{platform_buttons(v['links'], big=True)}</div>
  </div>
</section>"""

    video = ""
    if s.get("youtube_id"):
        yid = s["youtube_id"]
        video = f"""
<div class="video">
  <p class="eyebrow listen-label">Watch</p>
  <div class="frame" id="yt-{yid}">
    <img src="https://i.ytimg.com/vi/{yid}/hqdefault.jpg" alt="Play {esc(s['title'])} on YouTube" width="480" height="360" loading="lazy">
    <button type="button" aria-label="Play video" onclick="var f=this.parentNode,i=document.createElement('iframe');i.src='https://www.youtube-nocookie.com/embed/{yid}?autoplay=1';i.allow='autoplay; encrypted-media; picture-in-picture';i.allowFullscreen=true;i.title='{esc(s['title'])}';f.replaceChildren(i)"><span><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg></span></button>
  </div>
</div>"""

    verses = render_verses(s["verses"])
    meaning = meaning_section(s.get("meaning"), f"{s['title']} — meaning", "Meaning")
    faq = faq_section(s.get("faq"), "Frequently asked", f"{s['title']} — questions and answers")
    lang_switch = ""
    alternates = None
    if s.get("variant", {}).get("slug"):
        v = s["variant"]
        lang_switch = f'<div class="lang-switch"><span>Versión en español:</span><a href="{v["slug"]}.html" hreflang="es" lang="es">{esc(v["title"])}</a></div>'
        alternates = [("en", f"{BASE}/{s['slug']}.html"), ("es", f"{BASE}/{v['slug']}.html"), ("x-default", f"{BASE}/{s['slug']}.html")]

    pn = ""
    if prev_s or next_s:
        def pn_link(t, cls, label):
            return f'<a class="{cls}" href="{t["slug"]}.html"><img src="{img_src(t["image_slug"],600,t.get("image_remote"))}" alt="" width="64" height="64" loading="lazy"><span><small>{label}</small><b>{esc(t["title"])}</b></span></a>'
        pn = '<nav class="pn" aria-label="More shabads">' + (pn_link(prev_s, "prev", "Previous shabad") if prev_s else "<span></span>") + (pn_link(next_s, "next", "Next shabad") if next_s else "<span></span>") + "</nav>"

    chips = "".join(f"<li>{esc(k)}</li>" for k in s["keywords"])

    body = f"""
<nav class="crumbs" aria-label="Breadcrumb"><a href="./">MedRise Gurbani</a> › <a href="./#shabads">Shabads</a> › {esc(s['title'])}</nav>
<section class="shabad-top">
  <div><div class="art"><img src="{art}" alt="{esc(s['title'])} — MedRise Gurbani cover art" width="1200" height="1200" fetchpriority="high"></div>{dl}</div>
  <div class="title-block">
    <div class="eyebrow">{esc(s['theme'])}</div>
    <h1 style="margin-top:12px">{esc(s['title'])}</h1>
    <div class="gk-title gurmukhi" lang="pa">{esc(s['gurmukhi_title'])}</div>
    <p class="sub">{esc(s['subtitle'])}</p>
    <ul class="source">{''.join(source_items)}</ul>
    <p class="intent">{esc(s['intention'])}</p>
    {notice}{listen}{lang_switch}{video}
  </div>
</section>
{variant}
<section class="verses" id="lyrics">
  <div class="eyebrow">Gurmukhi · {"Hindi · " if any(v.get("h") for v in s["verses"]) else ""}Transliteration · Meaning</div>
  <h2 style="margin-top:10px">{esc(s['title'])} — lyrics and meaning</h2>
  <p class="lead">Read each line in layers: the original Gurmukhi{", the same line in Devanagari (Hindi script)" if any(v.get("h") for v in s["verses"]) else ""}, a Roman transliteration to sing from, and the English meaning. Line numbers follow the order sung in the recording.</p>
  {''.join(verses)}
  <p class="legend">Gurbani is quoted from {esc(src['granth'])}{f", Ang {src['ang']}" if src.get('ang') else ''}. English renderings draw on the Sant Singh Khalsa translation and are lightly clarified for readers new to Gurbani.</p>
</section>
{meaning}
{faq}
<section class="info">
  <div><h2>About this shabad</h2><p>{esc(s['intention'])}</p><p>Composed by {esc(src.get('writer') or 'the Guru')}{f" in {esc(src['raag'])}" if src.get('raag') else ''}. MedRise Gurbani presents it in a gentle, meditative arrangement so the words stay in front — sung for listeners who want to understand as they listen.</p></div>
  <div><h2>When to listen</h2><p>{esc(s['theme'])}. Play it in the morning before the day begins, or whenever the situation it speaks to is on your mind. Reading the meaning first turns listening into simran.</p>{'<p>Available on ' + esc(", ".join([k for k in PLATFORM_ORDER if k in s["links"] and k != "All platforms"])) + '.</p>' if s['links'] else ''}</div>
</section>
{pn}
<section class="keywords" id="keywords">
  <h2>Also searched as</h2>
  <p>Common spellings and ways people search for this shabad, so you can find it however you remember it.</p>
  <ul class="chips">{chips}</ul>
</section>
"""
    has_meaning = bool(s.get("meaning"))
    title = f"{s['title']} — Lyrics, Meaning & Translation | MedRise Gurbani" if has_meaning else f"{s['title']} — Gurmukhi, Transliteration & Meaning | MedRise Gurbani"
    ang_txt = f", Ang {src['ang']}" if src.get("ang") else ""
    stores_txt = ", ".join([k for k in PLATFORM_ORDER if k in s["links"] and k != "All platforms"][:4]) or "YouTube"
    hindi_txt = ", Hindi" if any(v.get("h") for v in s["verses"]) else ""
    desc = f"{s['title']} ({s['gurmukhi_title']}) by MedRise Gurbani — {s['theme'].lower()}. Full lyrics in Gurmukhi{hindi_txt} and Roman transliteration with English meaning, from {src['granth']}{ang_txt}. Listen on {stores_txt}."
    og = f"{BASE}/{art}" if not art.startswith("http") else art
    rec = recording_ld(s, og)
    graph = [rec, ORG_LD,
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "MedRise Gurbani", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Shabads", "item": BASE + "/#shabads"},
            {"@type": "ListItem", "position": 3, "name": s["title"], "item": f"{BASE}/{s['slug']}.html"}]}]
    if s.get("youtube_id"):
        graph.append(video_ld(s, s["youtube_id"]))
    if s.get("faq"):
        graph.append(faq_ld(s["faq"]))
    if has_meaning:
        graph.append({"@type": "Article", "@id": f"{BASE}/{s['slug']}.html#article", "headline": f"{s['title']} — meaning and lyrics",
                      "about": {"@id": rec["@id"]}, "author": {"@id": f"{BASE}/#artist"}, "publisher": {"@id": f"{BASE}/#artist"},
                      "inLanguage": "en", "image": og, "datePublished": s.get("release_date", TODAY), "dateModified": TODAY,
                      "mainEntityOfPage": f"{BASE}/{s['slug']}.html", "articleBody": " ".join(s["meaning"])})
    jsonld = {"@context": "https://schema.org", "@graph": graph}
    return shell(title, desc, f"{s['slug']}.html", body, og, jsonld, og_type="music.song", keywords=", ".join(s["keywords"]), alternates=alternates)


# ----------------------------------------------------------------------------- shared helpers
def render_verses(verses, lang="en"):
    out = []
    for n, v in enumerate(verses, 1):
        cls = "verse key" if v.get("key") or v.get("rahao") else "verse"
        if lang == "es":
            tag = '<span class="tag">Rahao · el verso central</span>' if v.get("rahao") else ('<span class="tag">Verso del título</span>' if v.get("key") else "")
            e = v.get("s") or v["e"]
        else:
            tag = '<span class="tag">Rahao · the central line</span>' if v.get("rahao") else ('<span class="tag">Title line</span>' if v.get("key") else "")
            e = v["e"]
        h = f'<p class="h" lang="hi">{esc(v["h"])}</p>' if v.get("h") else ""
        out.append(f"""<article class="{cls}" id="line-{n}">
  <div class="n">{n}</div>
  <div>{tag}<p class="g" lang="pa">{esc(v['g'])}</p>{h}<p class="t" lang="pa-Latn">{esc(v['t'])}</p><p class="e">{esc(e)}</p></div>
</article>""")
    return out

def meaning_section(paras, heading, eyebrow):
    if not paras: return ""
    return f'<section class="meaning" id="meaning"><div class="eyebrow">{esc(eyebrow)}</div><h2 style="margin:10px 0 18px">{esc(heading)}</h2>' + "".join(f"<p>{esc(p)}</p>" for p in paras) + "</section>"

def faq_section(faq, eyebrow, heading):
    if not faq: return ""
    items = "".join(f"<details{' open' if i == 0 else ''}><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for i, (q, a) in enumerate(faq))
    return f'<section class="faq" id="faq"><div class="eyebrow">{esc(eyebrow)}</div><h2 style="margin:10px 0 18px">{esc(heading)}</h2>{items}</section>'

def faq_ld(faq):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}

def video_ld(s, yid, lang="en"):
    return {"@type": "VideoObject", "name": f"{s['title']} — MedRise Gurbani", "description": s["intention"],
            "thumbnailUrl": [f"https://i.ytimg.com/vi/{yid}/maxresdefault.jpg", f"https://i.ytimg.com/vi/{yid}/hqdefault.jpg"],
            "uploadDate": s.get("release_date", TODAY), "embedUrl": f"https://www.youtube-nocookie.com/embed/{yid}",
            "contentUrl": f"https://www.youtube.com/watch?v={yid}", "inLanguage": lang, "publisher": {"@id": f"{BASE}/#artist"}}

def recording_ld(s, og, slug=None, name=None, links=None, lang="pa", release=None):
    src = s["source"]
    slug = slug or s["slug"]; links = links or s["links"]
    rec = {
        "@type": "MusicRecording", "@id": f"{BASE}/{slug}.html#recording",
        "name": name or s["title"], "alternateName": [s["gurmukhi_title"], s["subtitle"]] + s["keywords"][:6],
        "byArtist": {"@id": f"{BASE}/#artist"}, "inLanguage": lang, "genre": "Shabad Kirtan",
        "image": og, "url": f"{BASE}/{slug}.html",
        "sameAs": [u for k, u in links.items() if k != "All platforms"],
        "recordingOf": {"@type": "MusicComposition", "name": s["title"], "lyricist": {"@type": "Person", "name": src.get("writer") or "Traditional"},
                        "inLanguage": "pa", "lyrics": {"@type": "CreativeWork", "text": "\n".join(v["g"] for v in s["verses"])}},
    }
    if s.get("duration"): rec["duration"] = s["duration"]
    rd = release or s.get("release_date")
    if rd: rec["datePublished"] = rd
    return rec


def variant_page(s):
    """Spanish-language page for a shabad's Spanish-narrated variant."""
    v = s["variant"]; src = s["source"]
    art = img_src(v["image_slug"], 1200, v.get("image_remote"))
    og = f"{BASE}/{art}" if not art.startswith("http") else art
    source_items = [f"<li><b>{esc(src['granth'])}</b></li>"]
    if src.get("ang"): source_items.append(f"<li>Página {src['ang']}</li>")
    if src.get("writer"): source_items.append(f"<li>{esc(src['writer'])}</li>")
    if v.get("release_date"):
        d = datetime.date.fromisoformat(v["release_date"])
        source_items.append(f"<li>Publicado el {d.day} de {['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'][d.month-1]} de {d.year}</li>")
    verses = render_verses(s["verses"], lang="es")
    meaning = meaning_section(v.get("meaning"), f"{s['title']} — significado", "Significado")
    faq = faq_section(v.get("faq"), "Preguntas frecuentes", "Preguntas y respuestas")
    yid = v.get("youtube_id")
    video = ""
    if yid:
        video = f"""
<div class="video"><p class="eyebrow listen-label">Ver</p><div class="frame" id="yt-{yid}">
<img src="https://i.ytimg.com/vi/{yid}/hqdefault.jpg" alt="Reproducir {esc(v['title'])} en YouTube" width="480" height="360" loading="lazy">
<button type="button" aria-label="Reproducir video" onclick="var f=this.parentNode,i=document.createElement('iframe');i.src='https://www.youtube-nocookie.com/embed/{yid}?autoplay=1';i.allow='autoplay; encrypted-media; picture-in-picture';i.allowFullscreen=true;i.title='{esc(v['title'])}';f.replaceChildren(i)"><span><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg></span></button></div></div>"""
    chips = "".join(f"<li>{esc(k)}</li>" for k in v.get("keywords", []))
    body = f"""
<nav class="crumbs" aria-label="Ruta"><a href="./">MedRise Gurbani</a> › <a href="./#shabads">Shabads</a> › <a href="{s['slug']}.html">{esc(s['title'])}</a> › Español</nav>
<section class="shabad-top">
  <div><div class="art"><img src="{art}" alt="{esc(v['title'])} — portada MedRise Gurbani" width="1200" height="1200" fetchpriority="high"></div></div>
  <div class="title-block">
    <div class="eyebrow">{esc(v.get('theme') or s['theme'])}</div>
    <h1 style="margin-top:12px">{esc(v['title'])}</h1>
    <div class="gk-title gurmukhi" lang="pa">{esc(s['gurmukhi_title'])}</div>
    <p class="sub">Inhi Ki Kirpa Ke Saje Hum Hain · Gurbani con narración y significado en español</p>
    <ul class="source">{''.join(source_items)}</ul>
    <p class="intent">{esc(v.get('intention') or v['note'])}</p>
    <p class="eyebrow listen-label">Escúchalo en</p>{platform_buttons(v['links'], big=True)}
    <div class="lang-switch"><span>English version:</span><a href="{s['slug']}.html" hreflang="en" lang="en">{esc(s['title'])}</a></div>
    {video}
  </div>
</section>
<section class="verses" id="lyrics">
  <div class="eyebrow">Gurmukhi · Transliteración · Significado en español</div>
  <h2 style="margin-top:10px">{esc(s['title'])} — letra y significado en español</h2>
  <p class="lead">Lee cada verso en capas: el Gurmukhi original, la transliteración para cantar y el significado en español. La numeración sigue el orden de la grabación.</p>
  {''.join(verses)}
  <p class="legend">El Gurbani se cita de {esc(src['granth'])}{f", página {src['ang']}" if src.get('ang') else ''}. La traducción al español es de MedRise Gurbani y puede ser imperfecta.</p>
</section>
{meaning}
{faq}
<section class="info">
  <div><h2>Sobre este shabad</h2><p>{esc(v.get('intention') or v['note'])}</p><p>Compuesto por {esc(src.get('writer') or 'el Guru')}. MedRise Gurbani lo presenta en un arreglo suave y meditativo, con narración en español, para que las palabras queden al frente.</p></div>
  <div><h2>Cuándo escucharlo</h2><p>Por la mañana, antes de que empiece el día, o siempre que la situación de la que habla esté en tu mente. Leer el significado antes de escuchar convierte la escucha en simran (meditación).</p></div>
</section>
<section class="keywords" id="keywords">
  <h2>También se busca como</h2>
  <p>Formas comunes de buscar este shabad, para que lo encuentres como lo recuerdes.</p>
  <ul class="chips">{chips}</ul>
</section>
"""
    title = f"{v['title']} — Letra y significado | MedRise Gurbani"
    desc = f"Inhi Ki Kirpa Ke Saje Hum Hain en español: shabad de Guru Gobind Singh Ji ({src['granth']}, página {src.get('ang','')}) con letra en Gurmukhi, transliteración y significado en español. Escúchalo en Spotify, Apple Music, Amazon Music y más."
    rec = recording_ld(s, og, slug=v["slug"], name=v["title"], links=v["links"], lang="es", release=v.get("release_date"))
    graph = [rec, ORG_LD,
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "MedRise Gurbani", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": s["title"], "item": f"{BASE}/{s['slug']}.html"},
            {"@type": "ListItem", "position": 3, "name": v["title"], "item": f"{BASE}/{v['slug']}.html"}]}]
    if v.get("faq"): graph.append(faq_ld(v["faq"]))
    if v.get("meaning"):
        graph.append({"@type": "Article", "@id": f"{BASE}/{v['slug']}.html#article", "headline": f"{v['title']} — significado y letra",
                      "about": {"@id": rec["@id"]}, "author": {"@id": f"{BASE}/#artist"}, "publisher": {"@id": f"{BASE}/#artist"},
                      "inLanguage": "es", "image": og, "datePublished": v.get("release_date", TODAY), "dateModified": TODAY,
                      "mainEntityOfPage": f"{BASE}/{v['slug']}.html", "articleBody": " ".join(v["meaning"])})
    alternates = [("en", f"{BASE}/{s['slug']}.html"), ("es", f"{BASE}/{v['slug']}.html"), ("x-default", f"{BASE}/{s['slug']}.html")]
    return shell(title, desc, f"{v['slug']}.html", body, og, {"@context": "https://schema.org", "@graph": graph}, og_type="music.song",
                 keywords=", ".join(v.get("keywords", [])), lang="es", alternates=alternates)


def about():
    body = f"""
<section class="section" style="border:0">
  <div class="eyebrow">About</div>
  <h1 style="margin:12px 0 18px">Meditate and Rise with Gurbani</h1>
  <div class="info" style="border:0;padding-block:0">
    <div><p>MedRise Gurbani is a series of Shabad Kirtan recordings made for understanding. Each shabad is chosen for a moment people actually live through — fear before a new beginning, the weight of debt, an argument that will not end, a night of studying — and released with its full Gurmukhi text, a transliteration to sing from, and the meaning in plain English.</p>
    <p>The recordings are gentle and meditative on purpose: the words stay in front, the music holds them up.</p></div>
    <div><p>Gurbani is quoted from Sri Guru Granth Sahib Ji and Sri Dasam Granth Sahib. Translations draw on the Sant Singh Khalsa rendering and are lightly clarified for readers new to Gurbani; any error in them is ours, not the Guru's.</p>
    <p class="eyebrow" style="margin-top:22px">Follow &amp; listen</p>{platform_buttons(SITE['artist_links'])}</div>
  </div>
</section>"""
    jsonld = {"@context": "https://schema.org", "@graph": [ORG_LD, {"@type": "AboutPage", "url": f"{BASE}/about.html", "name": "About MedRise Gurbani", "about": {"@id": f"{BASE}/#artist"}}]}
    og = f"{BASE}/{img_src('inhi-ki-kirpa',1200)}"
    return shell("About MedRise Gurbani", "MedRise Gurbani records Shabad Kirtan with Gurmukhi, transliteration and English meaning — Gurbani for understanding.", "about.html", body, og, jsonld)


def not_found():
    body = '<section class="section" style="border:0;text-align:center"><div class="eyebrow">404</div><h1 style="margin:12px 0">That page has moved on</h1><p style="color:var(--ink-2)">Try the <a href="./">home page</a> — every shabad is listed there.</p></section>'
    return shell("Page not found — MedRise Gurbani", "Page not found.", "404.html", body, f"{BASE}/{img_src('inhi-ki-kirpa',1200)}", {"@context": "https://schema.org", "@type": "WebPage", "name": "Not found"}, extra_head='<meta name="robots" content="noindex">')


FAVICON = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><rect width="48" height="48" rx="10" fill="#2B2330"/><g fill="none" stroke="#D9A84E" stroke-width="1.8"><path d="M24 40c-8-4-13-11-13-19 5 1 9 4 13 9 4-5 8-8 13-9 0 8-5 15-13 19z"/><path d="M24 30c-2-8-1-16 0-22 1 6 2 14 0 22z"/></g></svg>'

# ----------------------------------------------------------------------------- build
def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "images", OUT / "images")
    (OUT / "style.css").write_text(CSS.strip() + "\n", encoding="utf-8")
    (OUT / "favicon.svg").write_text(FAVICON, encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    (OUT / "index.html").write_text(home(), encoding="utf-8")
    (OUT / "about.html").write_text(about(), encoding="utf-8")
    (OUT / "404.html").write_text(not_found(), encoding="utf-8")
    variants = []
    for i, s in enumerate(SHABADS):
        (OUT / f"{s['slug']}.html").write_text(shabad_page(i, s), encoding="utf-8")
        if s.get("variant", {}).get("slug"):
            (OUT / f"{s['variant']['slug']}.html").write_text(variant_page(s), encoding="utf-8")
            variants.append(s)

    urls = [("", "1.0", "weekly")] + [(f"{s['slug']}.html", "0.9", "monthly") for s in SHABADS] + [(f"{s['variant']['slug']}.html", "0.8", "monthly") for s in variants] + [("about.html", "0.4", "yearly")]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for u, p, f in urls:
        loc = f"{BASE}/{u}" if u else BASE + "/"
        img = ""; alt = ""
        m = [s for s in SHABADS if u == f"{s['slug']}.html"]
        mv = [s for s in variants if u == f"{s['variant']['slug']}.html"]
        if m:
            src = img_src(m[0]["image_slug"], 1200, m[0].get("image_remote"))
            img = f"<image:image><image:loc>{esc(src if src.startswith('http') else BASE + '/' + src)}</image:loc><image:title>{esc(m[0]['title'])} — MedRise Gurbani</image:title></image:image>"
        if mv:
            v = mv[0]["variant"]
            src = img_src(v["image_slug"], 1200, v.get("image_remote"))
            img = f"<image:image><image:loc>{esc(src if src.startswith('http') else BASE + '/' + src)}</image:loc><image:title>{esc(v['title'])} — MedRise Gurbani</image:title></image:image>"
        pair = m[0] if (m and m[0].get("variant", {}).get("slug")) else (mv[0] if mv else None)
        if pair:
            alt = (f'<xhtml:link rel="alternate" hreflang="en" href="{BASE}/{pair["slug"]}.html"/>'
                   f'<xhtml:link rel="alternate" hreflang="es" href="{BASE}/{pair["variant"]["slug"]}.html"/>'
                   f'<xhtml:link rel="alternate" hreflang="x-default" href="{BASE}/{pair["slug"]}.html"/>')
        sm.append(f"<url><loc>{esc(loc)}</loc><lastmod>{TODAY}</lastmod><changefreq>{f}</changefreq><priority>{p}</priority>{alt}{img}</url>")
    sm.append("</urlset>")
    (OUT / "sitemap.xml").write_text("\n".join(sm), encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
    print(f"Built {len(SHABADS)} shabad pages + home/about/404 into {OUT}")

if __name__ == "__main__":
    build()
