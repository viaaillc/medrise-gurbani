#!/usr/bin/env python3
"""Write the release kit for a shabad: every copy-paste block the release needs, as Markdown.

Usage
  python3 tools/kit.py <slug>                 # writes releases/<slug>/kit.md and prints it
  python3 tools/kit.py <slug> --words words.md  # splice in an authored word-by-word block (Markdown)

Blocks: YouTube title + description, Spotify/Apple "About", TikTok/Instagram captions, DistroKid
metadata, site URL, store-link checklist, and the word-by-word slot. Reads data/shabads.json.
"""
import json, sys, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = json.load(open(ROOT / "data" / "shabads.json", encoding="utf-8"))
SITE = DATA["site"]; BASE = SITE["url"].rstrip("/")
ORDER = ["Spotify", "Apple Music", "YouTube", "YouTube Music", "Amazon Music", "Deezer", "TIDAL", "All platforms"]

def hashtags(s):
    base = ["#Gurbani", "#Shabad", "#Kirtan", "#MedRiseGurbani", "#SikhMusic", "#Waheguru", "#GurbaniKirtan", "#Sikhi"]
    t = s["theme"].lower()
    for word, tag in [("protection", "#Ardas"), ("debt", "#DebtRelief"), ("peace", "#Peace"), ("student", "#StudyMotivation"),
                      ("courage", "#Courage"), ("fearless", "#Fearless"), ("devotion", "#Bhakti"), ("healing", "#Healing")]:
        if word in t: base.append(tag)
    if "Dasam" in s["source"]["granth"]: base.append("#DasamGranth")
    if "Jaap" in s["source"]["granth"]: base.append("#JaapSahib")
    return " ".join(dict.fromkeys(base))

def lyrics_block(s):
    out = []
    for v in s["verses"]:
        out.append(f"{v['g']}\n{v['t']}\n{v['e']}\n")
    return "\n".join(out)

def links_block(s):
    if not s["links"]: return "(add store links after DistroKit delivers — tools/new_shabad.py --set <slug> links.Spotify=URL ...)"
    return "\n".join(f"{k}: {s['links'][k]}" for k in ORDER if k in s["links"])

def kit(s, words=None):
    src = s["source"]
    ang = f", Ang {src['ang']}" if src.get("ang") else ""
    page = f"{BASE}/{s['slug']}.html"
    key = next((v for v in s["verses"] if v.get("rahao") or v.get("key")), s["verses"][0])
    sub = (s.get("subtitle") or "").split(" — ")[-1]
    yt_title = f"{s['title']} | {s['gurmukhi_title']} | Shabad with Meaning in English | MedRise Gurbani"
    if len(yt_title) > 100:
        yt_title = f"{s['title']} | Shabad with Meaning | MedRise Gurbani"
    yt_desc = f"""{s['title']} ({s['gurmukhi_title']}) — {s['theme'].lower()}.
{s['intention']}

From {src['granth']}{ang}{(' · ' + src['raag']) if src.get('raag') else ''}{(' · ' + src['writer']) if src.get('writer') else ''}.

▶ Full lyrics, transliteration and meaning: {page}
▶ Listen everywhere: {s['links'].get('All platforms') or SITE['artist_links']['Spotify']}

LYRICS · GURMUKHI · TRANSLITERATION · MEANING
{lyrics_block(s)}
CHAPTERS
0:00 {s['title']}
(add timestamps after upload)

MedRise Gurbani — Meditate and Rise with Gurbani. Shabad kirtan sung softly, with every line explained, so the Guru's words can be carried into an exam room, a hospital shift, a new city, or a hard conversation.

Spotify: {SITE['artist_links']['Spotify']}
Apple Music: {SITE['artist_links']['Apple Music']}
Website: {BASE}/

{hashtags(s)}
"""
    about = f"{s['title']} ({s['gurmukhi_title']}) by MedRise Gurbani — {s['theme'].lower()}. {s['intention']} From {src['granth']}{ang}. Sung softly with every line explained; read the full meaning at {page}"
    tiktok = f"{s['title']} — {sub or s['theme']}\n\n“{key['e']}”\n\n{s['intention'].split('.')[0]}.\n\nFull meaning + lyrics in bio · {hashtags(s)}"
    ig = f"{s['title']} · {s['gurmukhi_title']}\n\n{key['g']}\n{key['t']}\n{key['e']}\n\n{s['intention']}\n\n{src['granth']}{ang}. Now on Spotify, Apple Music and YouTube — link in bio.\n\n{hashtags(s)}"
    words_block = words or "_(authored per release — one row per word of the title line: word · literal sense · sense in this line)_\n\n| Word | Literal | In this line |\n|---|---|---|\n" + "\n".join(f"| {w} |  |  |" for w in key["g"].replace("॥", "").split())
    md = f"""# Release kit — {s['title']}
_{s['gurmukhi_title']}_ · {src['granth']}{ang} · generated {datetime.date.today().isoformat()}

Site page: {page}
Cover: images/full/{s['image_slug']}.jpg (3000×3000)
Status: {"released " + s['release_date'] if s.get('release_date') else "coming soon — no release_date yet"}

## 1. DistroKid metadata
- Artist: MedRise Gurbani
- Title: {s['title']}
- Version / subtitle: {s.get('subtitle','')}
- Songwriter: {src.get('writer') or 'Traditional'} (lyrics) · composer/performer: Manpreet Kaur Bindra
- Language: Punjabi · Genre: Devotional / World · Explicit: No
- Cover: images/full/{s['image_slug']}.jpg
- After delivery run: `python3 tools/new_shabad.py --set {s['slug']} release_date=YYYY-MM-DD links.Spotify=... links."Apple Music"=... links."All platforms"=https://song.link/...`

## 2. YouTube title
{yt_title}

## 3. YouTube description
```
{yt_desc}```

## 4. Word-by-word — {key['t']}
{words_block}

## 5. Spotify / Apple Music "About this song"
{about}

## 6. TikTok caption
```
{tiktok}
```

## 7. Instagram / Facebook caption
```
{ig}
```

## 8. Store links (as on the site)
{links_block(s)}

## 9. Checklist
- [ ] Cover approved (3000×3000, no text cut by the frame)
- [ ] DistroKid submitted · release_date set
- [ ] YouTube uploaded · youtube_id set (`--set {s['slug']} youtube_id=...`)
- [ ] Store links added · `python3 tools/new_shabad.py --check` passes
- [ ] `python3 tools/release.py {s['slug']}` pushed · page live
- [ ] Search Console: URL inspection → request indexing for {page}
- [ ] TikTok / Instagram posted with captions above
"""
    return md

def main(argv):
    if not argv: sys.exit(__doc__)
    slug = argv[0]
    s = next((x for x in DATA["shabads"] if x["slug"] == slug), None)
    if not s: sys.exit(f"no shabad with slug {slug}")
    words = None
    if "--words" in argv:
        words = pathlib.Path(argv[argv.index("--words") + 1]).read_text(encoding="utf-8")
    out = ROOT / "releases" / slug / "kit.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(kit(s, words), encoding="utf-8")
    print(out.read_text(encoding="utf-8"))
    print(f"\n[wrote {out.relative_to(ROOT)}]", file=sys.stderr)

if __name__ == "__main__":
    main(sys.argv[1:])
