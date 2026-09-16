#!/usr/bin/env python3
"""Add or update a shabad entry in data/shabads.json from a small spec file.

Usage
  python3 tools/new_shabad.py releases/<slug>/spec.json          # add (fails if slug exists)
  python3 tools/new_shabad.py releases/<slug>/spec.json --update # merge into existing entry
  python3 tools/new_shabad.py --check                             # validate the whole file
  python3 tools/new_shabad.py --set <slug> links.Spotify=URL youtube_id=abc release_date=2026-10-01

Spec (JSON). Required: title, gurmukhi_title, theme, intention, source{granth,...}, verses[{g,t,e,key?,rahao?}].
Optional: subtitle, slug, image_slug, release_date, duration, youtube_id, links{}, keywords[] (extra),
          meaning[], faq[[q,a]], hindi_title, short_title, coming_soon.
Everything else (slug, image_slug, keyword variants, coming_soon text) is derived.
"""
import json, re, sys, pathlib, unicodedata, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "shabads.json"
PLATFORMS = ["Spotify", "Apple Music", "YouTube", "YouTube Music", "Amazon Music", "Deezer", "TIDAL", "All platforms"]
REQUIRED = ["title", "gurmukhi_title", "theme", "intention", "source", "verses"]

def load():
    return json.load(open(DATA, encoding="utf-8"))

def save(d):
    DATA.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def slugify(s, max_words=8):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return "-".join(s.split("-")[:max_words])

# --- keyword variants -------------------------------------------------------
SUBS = [  # common Roman-Punjabi spelling swaps, applied one at a time
    ("ee", "i"), ("aa", "a"), ("oo", "u"), ("ai", "e"), ("v", "w"), ("w", "v"),
    ("Mein", "Meh"), ("Mein", "Me"), ("Meh", "Mein"), ("Satguru", "Satgur"), ("Satgur", "Satguru"),
    ("Naal", "Nal"), ("Pyara", "Piara"), ("Pyaara", "Pyara"), ("Kirpa", "Kripa"), ("Sabad", "Shabad"),
    ("Shabad", "Sabad"), ("Prabh", "Prabhu"), ("Ji", "Jee"), ("Chahe", "Chahai"), ("Leh", "Lehu"),
    ("ya", "ia"), ("ia", "ya"), ("Raam", "Ram"), ("Ram", "Raam"), ("Gur", "Guru"),
]

def variants(title):
    out, seen = [], set()
    def add(x):
        x = re.sub(r"\s+", " ", x).strip()
        if x and x.lower() not in seen:
            seen.add(x.lower()); out.append(x)
    add(title)
    for a, b in SUBS:
        if a in title:
            add(title.replace(a, b))
        if a.lower() in title.lower() and a != a.lower():
            add(re.sub(a, b, title, flags=re.I))
    return out[:10]

def build_keywords(s, extra):
    kw = []
    def add(x):
        if x and x not in kw: kw.append(x)
    for v in variants(s["title"]): add(v)
    if s.get("subtitle"):
        first = s["subtitle"].split(" — ")[0]
        for v in variants(first)[:3]: add(v)
    for v in s["verses"]:
        if v.get("key") or v.get("rahao"):
            t = re.sub(r"[.।॥]+$", "", v["t"]).strip()
            for x in variants(t)[:3]: add(x)
    add(s["gurmukhi_title"])
    for v in s["verses"]:
        if v.get("key") or v.get("rahao"):
            add(re.sub(r"\s*॥\s*$", "", v["g"]).strip())
    src = s["source"]
    if src.get("ang"): add(f"{src['granth']} Ang {src['ang']}")
    theme = s["theme"].lower()
    m = re.search(r"prayer for (.+)", theme)
    if m:
        for part in re.split(r",| and ", m.group(1)):
            part = part.strip()
            if part: add(f"shabad for {part}")
    for x in extra: add(x)
    for x in [f"{s['title']} meaning", f"{s['title']} lyrics", f"{s['title']} translation",
              "MedRise Gurbani", "shabad kirtan", "Gurbani kirtan with English translation", "Gurmukhi lyrics with meaning"]:
        add(x)
    return kw

# --- entry -------------------------------------------------------------------
def make_entry(spec):
    missing = [k for k in REQUIRED if not spec.get(k)]
    if missing:
        sys.exit(f"spec missing required fields: {', '.join(missing)}")
    for i, v in enumerate(spec["verses"], 1):
        for k in ("g", "t", "e"):
            if not v.get(k): sys.exit(f"verse {i} missing '{k}'")
    if not any(v.get("key") or v.get("rahao") for v in spec["verses"]):
        print("warning: no verse marked key/rahao — mark the title line with \"key\": true", file=sys.stderr)
    src = dict(spec["source"])
    src.setdefault("granth", "Sri Guru Granth Sahib Ji"); src.setdefault("ang", None)
    src.setdefault("raag", None); src.setdefault("writer", None)
    slug = spec.get("slug") or slugify(spec["title"])
    e = {
        "slug": slug,
        "title": spec["title"],
        "subtitle": spec.get("subtitle") or spec["theme"],
        "gurmukhi_title": spec["gurmukhi_title"],
        "theme": spec["theme"],
        "intention": spec["intention"],
        "source": src,
        "release_date": spec.get("release_date"),
        "duration": spec.get("duration"),
        "image_slug": spec.get("image_slug") or slugify(spec["title"], 5),
        "links": spec.get("links") or {},
        "youtube_id": spec.get("youtube_id"),
        "verses": spec["verses"],
        "keywords": [],
    }
    for k in ("hindi_title", "short_title", "meaning", "faq", "image_remote"):
        if spec.get(k): e[k] = spec[k]
    if not e["release_date"]:
        e["coming_soon"] = spec.get("coming_soon") or "Coming soon to Spotify, Apple Music, YouTube and all platforms."
    e["keywords"] = build_keywords(e, spec.get("keywords") or [])
    return e

def check(d):
    errs, slugs = [], set()
    for s in d["shabads"]:
        for k in ("slug", "title", "gurmukhi_title", "theme", "intention", "source", "verses", "keywords", "image_slug", "links"):
            if k not in s: errs.append(f"{s.get('slug','?')}: missing {k}")
        if s["slug"] in slugs: errs.append(f"duplicate slug {s['slug']}")
        slugs.add(s["slug"])
        for k in s.get("links", {}):
            if k not in PLATFORMS: errs.append(f"{s['slug']}: unknown platform '{k}'")
        if s.get("release_date"):
            try: datetime.date.fromisoformat(s["release_date"])
            except ValueError: errs.append(f"{s['slug']}: bad release_date {s['release_date']}")
            if not s.get("links"): errs.append(f"{s['slug']}: released but no store links")
        if s.get("youtube_id") and not re.fullmatch(r"[\w-]{11}", s["youtube_id"]):
            errs.append(f"{s['slug']}: youtube_id should be the 11-char id, not a URL")
        for size in (1200, 600):
            if not (ROOT / "images" / f"{s['image_slug']}-{size}.jpg").exists() and not s.get("image_remote"):
                errs.append(f"{s['slug']}: images/{s['image_slug']}-{size}.jpg missing (run tools/make_cover.py)")
    return errs

def setvals(d, slug, pairs):
    s = next((x for x in d["shabads"] if x["slug"] == slug), None)
    if not s: sys.exit(f"no shabad with slug {slug}")
    for p in pairs:
        k, _, v = p.partition("=")
        if k.startswith("links."):
            s["links"][k[6:]] = v
        elif k == "youtube_id" and "youtu" in v:
            m = re.search(r"(?:v=|youtu\.be/|shorts/)([\w-]{11})", v); s["youtube_id"] = m.group(1) if m else v
        else:
            s[k] = None if v in ("", "null") else v
    if s.get("release_date") and s.get("links"):
        s.pop("coming_soon", None)
    return s

def main(argv):
    d = load()
    if "--check" in argv:
        errs = check(d)
        print("\n".join(errs) if errs else f"OK — {len(d['shabads'])} shabads valid")
        sys.exit(1 if errs else 0)
    if "--set" in argv:
        i = argv.index("--set"); slug = argv[i + 1]; pairs = argv[i + 2:]
        s = setvals(d, slug, pairs); save(d)
        print(f"updated {slug}: " + ", ".join(pairs)); return
    specs = [a for a in argv if not a.startswith("--")]
    if not specs: sys.exit(__doc__)
    spec = json.load(open(specs[0], encoding="utf-8"))
    entry = make_entry(spec)
    existing = next((i for i, s in enumerate(d["shabads"]) if s["slug"] == entry["slug"]), None)
    if existing is not None and "--update" not in argv:
        sys.exit(f"slug {entry['slug']} already exists — pass --update to merge")
    if existing is not None:
        old = d["shabads"][existing]
        for k, v in entry.items():
            if v not in (None, {}, []) or k not in old: old[k] = v
        if old.get("release_date") and old.get("links"): old.pop("coming_soon", None)
        d["shabads"][existing] = old
    else:
        d["shabads"].append(entry)
    save(d)
    errs = [e for e in check(d) if entry["slug"] in e and "images/" not in e]
    print(f"{'updated' if existing is not None else 'added'} {entry['slug']} ({len(entry['keywords'])} keywords)")
    if errs: print("\n".join(errs))

if __name__ == "__main__":
    main(sys.argv[1:])
