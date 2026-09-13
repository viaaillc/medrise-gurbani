# MedRise Gurbani — website

Free static site for GitHub Pages. One page per shabad with Gurmukhi, transliteration,
English meaning, store links (Spotify, Apple Music, YouTube, YouTube Music, Amazon Music,
Deezer, TIDAL, song.link), JSON-LD `MusicRecording` schema, Open Graph tags, sitemap and a
keyword footer of spelling variations.

## Deploy (about 5 minutes)

1. Create a new GitHub repository (e.g. `medrise-gurbani`). Public is fine.
2. Upload everything in this folder (drag-and-drop on github.com works, or `git push`).
3. Repo → **Settings → Pages** → Source: *Deploy from a branch* → Branch: `main`, Folder: **`/docs`** → Save.
4. Your site is live at `https://<your-username>.github.io/medrise-gurbani/` within a minute or two.

### Custom domain (optional, e.g. medrisegurbani.com)
Add the domain in Settings → Pages, point the domain's DNS at GitHub Pages
(CNAME `www` → `<username>.github.io`), then set `"url"` in `data/shabads.json` to the new
domain and rebuild (below) so canonical/OG/sitemap URLs match.

### Set the site URL once
Open `data/shabads.json` and change `site.url` to your real GitHub Pages URL, then rebuild.
Everything in `docs/` is regenerated from `data/shabads.json` by:

    python3 build.py

(Needs Python 3; no packages beyond the standard library. Pillow is only needed if you add new cover art — see below.)

## Adding a new shabad
1. Put the 3000×3000 cover in `images/full/<slug>.jpg` and create the web sizes:

       python3 -c "from PIL import Image; im=Image.open('images/full/<slug>.jpg'); im.resize((1200,1200),Image.LANCZOS).save('images/<slug>-1200.jpg',quality=86,optimize=True,progressive=True); im.resize((600,600),Image.LANCZOS).save('images/<slug>-600.jpg',quality=84,optimize=True,progressive=True)"

2. Copy one of the entries in `data/shabads.json` and fill in title, Gurmukhi, verses,
   links (paste each store URL from DistroKid / song.link), `release_date`, `youtube_id`, keywords.
3. `python3 build.py`, commit, push. The sitemap updates automatically.

## Submit to Google
Search Console → add the site → submit `https://<your-site>/sitemap.xml`.
