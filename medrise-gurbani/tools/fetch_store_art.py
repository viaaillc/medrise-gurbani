#!/usr/bin/env python3
"""Download a released shabad's real store artwork (the cover DistroKid delivered) into images/.

    python3 tools/fetch_store_art.py <slug>            # Apple Music first, Spotify as a fallback
    python3 tools/fetch_store_art.py <slug> --dry-run  # print the artwork URL only

Finds the shabad's Apple Music link (data/shabads.json, then data/listen.json link_additions),
asks Apple's public lookup API for the artwork and saves:
    images/full/<image_slug>.jpg   largest size Apple serves (3000x3000 for DistroKid uploads)
    images/<image_slug>-1200.jpg, images/<image_slug>-600.jpg   web sizes the site uses
Falls back to Spotify's oEmbed thumbnail (640x640) when there is no Apple Music link.
After it runs, drop "image_remote" from the entry so nothing points at a placeholder.

Needs Pillow and internet access (run it on the Mac or in GitHub Actions; Claude's sandbox
cannot reach Apple or Spotify).
"""
import io, json, re, sys, urllib.parse, urllib.request, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
UA = {"User-Agent": "MedRise-Gurbani-site/1.0 (+https://med-rise.com/gurbani/)"}


def get(url, timeout=30):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read()


def links_for(slug):
    data = json.load(open(ROOT / "data" / "shabads.json", encoding="utf-8"))
    s = next((x for x in data["shabads"] if x["slug"] == slug), None)
    if not s:
        sys.exit(f"no shabad with slug {slug!r}")
    links = dict(s.get("links") or {})
    lj = ROOT / "data" / "listen.json"
    if lj.exists():
        extra = json.load(open(lj, encoding="utf-8")).get("link_additions", {}).get(slug, {}).get("links", {})
        for k, v in extra.items():
            links.setdefault(k, v)
    return s, links


def apple_art(url):
    q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    ids = q.get("i") or re.findall(r"/(\d{6,})(?:\?|$)", url)
    if not ids:
        return None
    res = json.loads(get(f"https://itunes.apple.com/lookup?id={ids[0]}&country=us"))
    for r in res.get("results", []):
        a = r.get("artworkUrl100")
        if a:
            # Apple serves any size up to the uploaded original; ask for the DistroKid size.
            return re.sub(r"/\d+x\d+bb\.(jpg|png|webp)$", "/3000x3000bb.jpg", a), r
    return None


def spotify_art(url):
    res = json.loads(get("https://open.spotify.com/oembed?url=" + urllib.parse.quote(url, safe="")))
    return (res.get("thumbnail_url"), res) if res.get("thumbnail_url") else None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    slug = args[0]
    s, links = links_for(slug)
    found = None
    if links.get("Apple Music"):
        found = apple_art(links["Apple Music"])
        src = "Apple Music"
    if not found and links.get("Spotify"):
        found = spotify_art(links["Spotify"])
        src = "Spotify"
    if not found:
        sys.exit(f"{slug}: no Apple Music or Spotify artwork found")
    url, meta = found
    name = meta.get("trackName") or meta.get("collectionName") or meta.get("title") or ""
    print(f"{slug}: {src} artwork for {name!r}\n  {url}")
    if "--dry-run" in sys.argv:
        return
    from PIL import Image
    raw = get(url, timeout=60)
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    print(f"  downloaded {im.width}x{im.height}, {len(raw)//1024} KB")
    img = s.get("image_slug") or slug
    full = ROOT / "images" / "full"
    full.mkdir(parents=True, exist_ok=True)
    im.save(full / f"{img}.jpg", quality=92, optimize=True, progressive=True)
    for size, q in ((1200, 86), (600, 84)):
        im.resize((size, size), Image.LANCZOS).save(ROOT / "images" / f"{img}-{size}.jpg", quality=q, optimize=True, progressive=True)
    print(f"  wrote images/full/{img}.jpg, images/{img}-1200.jpg, images/{img}-600.jpg")


if __name__ == "__main__":
    main()
