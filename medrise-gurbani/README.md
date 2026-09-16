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

## Releasing a new shabad (the automated way)

Everything below runs from a clone of this repo on your Mac (`~/Claude/medrise-gurbani`).
GitHub Actions rebuilds the site from source on every push — no zip needed.

1. Write `medrise-gurbani/releases/<slug>/spec.json` (title, Gurmukhi title, theme, intention,
   source, verses with `g`/`t`/`e`, mark the title line `"key": true`). Copy an existing one.
2. From `medrise-gurbani/`:

       python3 tools/new_shabad.py releases/<slug>/spec.json   # adds the entry, derives slug + keyword variants
       python3 tools/make_cover.py <slug>                       # 3000x3000 cover + 1200/600 web sizes
       python3 tools/make_cover.py <slug> --bg scene.jpg        # ...or over your own photo
       python3 tools/release.py <slug>                          # check -> build -> kit.md -> commit -> push

   `releases/<slug>/kit.md` now holds the YouTube title/description, captions, DistroKid metadata and checklist.
3. After DistroKid delivers and YouTube is up:

       python3 tools/new_shabad.py --set <slug> release_date=2026-10-01 youtube_id=<id> links.Spotify=<url> links."Apple Music"=<url> links."All platforms"=<song.link>
       python3 tools/release.py <slug>

`python3 tools/new_shabad.py --check` validates the whole data file at any time.

## Adding a new shabad (by hand)
1. Put the 3000×3000 cover in `images/full/<slug>.jpg` and create the web sizes:

       python3 -c "from PIL import Image; im=Image.open('images/full/<slug>.jpg'); im.resize((1200,1200),Image.LANCZOS).save('images/<slug>-1200.jpg',quality=86,optimize=True,progressive=True); im.resize((600,600),Image.LANCZOS).save('images/<slug>-600.jpg',quality=84,optimize=True,progressive=True)"

2. Copy one of the entries in `data/shabads.json` and fill in title, Gurmukhi, verses,
   links (paste each store URL from DistroKid / song.link), `release_date`, `youtube_id`, keywords.
3. `python3 build.py`, commit, push. The sitemap updates automatically.

## Submit to Google
Search Console → add the site → submit `https://<your-site>/sitemap.xml`.
