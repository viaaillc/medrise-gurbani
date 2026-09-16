#!/usr/bin/env python3
"""Render the 3000x3000 MedRise Gurbani cover for a shabad, plus the 1200/600 web sizes.

Usage
  python3 tools/make_cover.py <slug>                      # painted dawn backdrop
  python3 tools/make_cover.py <slug> --bg photo.jpg       # your own 3000x3000 (or larger) scene underneath
  python3 tools/make_cover.py <slug> --layout top|center  # where the title block sits (default: top)
  python3 tools/make_cover.py <slug> --no-web             # skip 1200/600 resizes
  python3 tools/make_cover.py --all                       # (re)make every cover that has no images/full/<image_slug>.jpg

Writes images/full/<image_slug>.jpg (3000x3000, DistroKid-ready), images/<image_slug>-1200.jpg, images/<image_slug>-600.jpg.
Typography follows the series: brand line + tagline on top, Ik Onkar, Gurmukhi title, English title in a
display serif, subtitle in spaced small caps, source line, thin double gold frame, wordmark at the foot.
Fonts: uses tools/fonts/ if present (Noto Serif Gurmukhi, Cormorant Garamond, Cinzel), else system fallbacks.
"""
import json, sys, math, pathlib, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = json.load(open(ROOT / "data" / "shabads.json", encoding="utf-8"))
FONTS = ROOT / "tools" / "fonts"
S = 3000

# palette (matches style.css)
GOLD = (184, 134, 43); GOLD2 = (217, 178, 95); ROSE = (150, 62, 92); INK = (74, 44, 60); INK2 = (110, 80, 92)
CREAM = (252, 246, 238)

def font(candidates, size, variation=None):
    for c in candidates:
        for base in (FONTS, pathlib.Path("/usr/share/fonts"), pathlib.Path("/Library/Fonts"), pathlib.Path("/System/Library/Fonts"), pathlib.Path.home() / "Library/Fonts"):
            hits = list(base.rglob(c)) if base.exists() else []
            if hits:
                f = ImageFont.truetype(str(hits[0]), size)
                if variation:
                    try: f.set_variation_by_name(variation)
                    except Exception: pass
                return f
    return ImageFont.load_default(size)

F_GURMUKHI = ["NotoSerifGurmukhi*.ttf", "NotoSerifGurmukhi-Medium.ttf", "Gurmukhi MN.ttc", "GurmukhiMN.ttc", "Raavi.ttf", "FreeSerifBold.ttf", "FreeSerif.ttf"]
F_SERIF    = ["CormorantGaramond*.ttf", "CormorantGaramond-SemiBold.ttf", "EBGaramond*.ttf", "Baskerville.ttc", "LiberationSerif-Regular.ttf", "FreeSerif.ttf"]
F_SERIF_I  = ["CormorantGaramond-Italic*.ttf", "LiberationSerif-Italic.ttf", "FreeSerifItalic.ttf"]
F_CAPS     = ["Cinzel*.ttf", "Cinzel-Regular.ttf", "LiberationSerif-Regular.ttf", "FreeSerif.ttf"]

# --- backdrop ----------------------------------------------------------------
def dawn_backdrop(seed=7):
    """Soft golden-hour gradient with bokeh light and a faint horizon glow — the series' colour world."""
    rnd = random.Random(seed)
    small = Image.new("RGB", (300, 300))
    px = small.load()
    top = (248, 214, 196); mid = (250, 222, 176); low = (238, 184, 170); bottom = (226, 160, 150)
    for y in range(300):
        t = y / 299
        if t < .45:  a, b, u = top, mid, t / .45
        elif t < .75: a, b, u = mid, low, (t - .45) / .3
        else:         a, b, u = low, bottom, (t - .75) / .25
        c = tuple(int(a[i] + (b[i] - a[i]) * u) for i in range(3))
        for x in range(300):
            px[x, y] = c
    im = small.resize((S, S), Image.BICUBIC)
    glow = Image.new("RGB", (S, S), (0, 0, 0)); g = ImageDraw.Draw(glow)
    g.ellipse((S * .18, S * .42, S * .82, S * 1.02), fill=(255, 226, 150))
    glow = glow.filter(ImageFilter.GaussianBlur(320))
    im = Image.blend(im, Image.eval(glow, lambda v: v), 0)  # keep im; blend via screen below
    im = Image.composite(Image.new("RGB", (S, S), (255, 240, 200)), im, glow.convert("L").point(lambda v: int(v * .55)))
    bok = Image.new("RGB", (S, S), (0, 0, 0)); b = ImageDraw.Draw(bok)
    for _ in range(38):
        r = rnd.randint(40, 190); x = rnd.randint(0, S); y = rnd.randint(int(S * .35), S)
        b.ellipse((x - r, y - r, x + r, y + r), fill=(255, 236, 200))
    bok = bok.filter(ImageFilter.GaussianBlur(26))
    im = Image.composite(Image.new("RGB", (S, S), (255, 246, 222)), im, bok.convert("L").point(lambda v: int(v * .22)))
    return im

def fit_bg(path):
    im = Image.open(path).convert("RGB")
    w, h = im.size; k = max(S / w, S / h)
    im = im.resize((math.ceil(w * k), math.ceil(h * k)), Image.LANCZOS)
    x = (im.width - S) // 2; y = (im.height - S) // 2
    return im.crop((x, y, x + S, y + S))

def legibility_veil(im, layout):
    """Soft cream veil behind the title block so type reads on any photo."""
    veil = Image.new("L", (S, S), 0); d = ImageDraw.Draw(veil)
    if layout == "top":
        d.rectangle((0, 0, S, int(S * .52)), fill=200)
    else:
        d.rectangle((0, int(S * .18), S, int(S * .82)), fill=200)
    veil = veil.filter(ImageFilter.GaussianBlur(260))
    return Image.composite(Image.new("RGB", (S, S), CREAM), im, veil)

# --- text helpers --------------------------------------------------------------
def wrap(draw, text, fnt, max_w):
    words = text.split(); lines = []; cur = ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w or not cur: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def fit_font(draw, text, cands, max_w, start, min_size, max_lines, variation=None):
    size = start
    while size >= min_size:
        f = font(cands, size, variation)
        lines = wrap(draw, text, f, max_w)
        if len(lines) <= max_lines and all(draw.textlength(l, font=f) <= max_w for l in lines):
            return f, lines
        size -= max(4, size // 25)
    f = font(cands, min_size, variation)
    return f, wrap(draw, text, f, max_w)

def draw_centered(draw, y, lines, fnt, fill, spacing=1.12, shadow=True, tracking=0):
    lh = int(fnt.size * spacing)
    for l in lines:
        if tracking:
            w = sum(draw.textlength(ch, font=fnt) for ch in l) + tracking * (len(l) - 1)
            x = (S - w) / 2
            for ch in l:
                if shadow: draw.text((x + 3, y + 4), ch, font=fnt, fill=(255, 250, 240))
                draw.text((x, y), ch, font=fnt, fill=fill)
                x += draw.textlength(ch, font=fnt) + tracking
        else:
            w = draw.textlength(l, font=fnt); x = (S - w) / 2
            if shadow: draw.text((x + 3, y + 4), l, font=fnt, fill=(255, 250, 240))
            draw.text((x, y), l, font=fnt, fill=fill)
        y += lh
    return y

def ornament(draw, y, w=520):
    cx = S / 2
    draw.line((cx - w / 2, y, cx - 60, y), fill=GOLD, width=4)
    draw.line((cx + 60, y, cx + w / 2, y), fill=GOLD, width=4)
    r = 14
    draw.polygon([(cx, y - r), (cx + r, y), (cx, y + r), (cx - r, y)], outline=GOLD, fill=GOLD2, width=3)
    draw.ellipse((cx - w / 2 - 10, y - 8, cx - w / 2 + 6, y + 8), fill=GOLD)
    draw.ellipse((cx + w / 2 - 6, y - 8, cx + w / 2 + 10, y + 8), fill=GOLD)

def frame(draw):
    m = 96
    draw.rectangle((m, m, S - m, S - m), outline=GOLD, width=6)
    draw.rectangle((m + 22, m + 22, S - m - 22, S - m - 22), outline=GOLD2, width=2)

# --- compose -------------------------------------------------------------------
def render(s, bg=None, layout="top"):
    im = fit_bg(bg) if bg else dawn_backdrop(seed=sum(map(ord, s["slug"])))
    im = legibility_veil(im, layout)
    d = ImageDraw.Draw(im)
    frame(d)

    y = 190 if layout == "top" else int(S * .16)
    # brand line
    f_brand = font(F_CAPS, 64); f_tag = font(F_CAPS, 40)
    y = draw_centered(d, y, ["MEDRISE GURBANI"], f_brand, INK, tracking=14, shadow=False)
    y = draw_centered(d, y + 6, ["MEDITATE  •  LEARN  •  RISE WITH GURBANI"], f_tag, INK2, tracking=8, shadow=False)
    # Ik Onkar
    f_ik = font(F_GURMUKHI, 210)
    y = draw_centered(d, y + 70, ["ੴ"], f_ik, GOLD, spacing=1.0)
    # Gurmukhi title
    f_g, g_lines = fit_font(d, s["gurmukhi_title"].replace("॥", "").strip() + " ॥", F_GURMUKHI, S - 560, 240, 120, 2)
    y = draw_centered(d, y + 50, g_lines, f_g, ROSE, spacing=1.25)
    # English title
    f_e, e_lines = fit_font(d, s["title"], F_SERIF, S - 520, 280, 150, 2, variation="SemiBold")
    y = draw_centered(d, y + 40, e_lines, f_e, INK, spacing=1.05)
    ornament(d, y + 40)
    # subtitle / meaning line
    sub = (s.get("subtitle") or s["theme"]).split(" — ")[-1] if " — " in (s.get("subtitle") or "") else (s.get("subtitle") or s["theme"])
    f_s, s_lines = fit_font(d, sub.upper(), F_CAPS, S - 700, 64, 44, 2)
    y = draw_centered(d, y + 100, s_lines, f_s, INK2, spacing=1.5, tracking=6, shadow=False)
    # source line
    src = s["source"]; parts = [src.get("granth") or ""]
    if src.get("ang"): parts.append(f"Ang {src['ang']}")
    if src.get("writer"): parts.append(src["writer"])
    f_src = font(F_SERIF_I, 58)
    draw_centered(d, y + 30, [" · ".join(p for p in parts if p)], f_src, INK2, shadow=False)

    yb = S - 400
    # no photo: set the shabad's own lines faintly in gold across the lower field
    if not bg:
        f_v = font(F_GURMUKHI, 92)
        lines = [v["g"].replace("॥", "").strip() for v in s["verses"]][:8]
        top = y + 220; avail = yb - 80 - top
        lh = min(int(f_v.size * 1.6), avail // max(1, len(lines)))
        yy = top + (avail - lh * len(lines)) // 2
        for l in lines:
            w = d.textlength(l, font=f_v)
            d.text(((S - w) / 2, yy), l, font=f_v, fill=(206, 168, 104))
            yy += lh

    # foot: wordmark
    f_wm = font(F_SERIF, 96, variation="Medium"); f_wm_tag = font(F_CAPS, 36)
    draw_centered(d, yb, ["MedRise Gurbani"], f_wm, INK)
    draw_centered(d, yb + 120, ["MEDITATE AND RISE WITH GURBANI"], f_wm_tag, INK2, tracking=7, shadow=False)
    d.ellipse((S / 2 - 12, yb + 190, S / 2 + 12, yb + 214), fill=ROSE)
    return im

def write(im, image_slug, web=True):
    full = ROOT / "images" / "full"; full.mkdir(parents=True, exist_ok=True)
    p = full / f"{image_slug}.jpg"
    im.save(p, quality=95, optimize=True, subsampling=0)
    print("wrote", p.relative_to(ROOT), im.size)
    if web:
        for size, q in ((1200, 86), (600, 84)):
            out = ROOT / "images" / f"{image_slug}-{size}.jpg"
            im.resize((size, size), Image.LANCZOS).save(out, quality=q, optimize=True, progressive=True)
            print("wrote", out.relative_to(ROOT))

def main(argv):
    if not argv: sys.exit(__doc__)
    bg = argv[argv.index("--bg") + 1] if "--bg" in argv else None
    layout = argv[argv.index("--layout") + 1] if "--layout" in argv else "top"
    web = "--no-web" not in argv
    if "--all" in argv:
        targets = [s for s in DATA["shabads"] if not (ROOT / "images" / "full" / f"{s['image_slug']}.jpg").exists()]
    else:
        slug = [a for a in argv if not a.startswith("--") and a != bg and a != layout][0]
        targets = [s for s in DATA["shabads"] if s["slug"] == slug or s["image_slug"] == slug]
        if not targets: sys.exit(f"no shabad with slug {slug}")
    for s in targets:
        write(render(s, bg, layout), s["image_slug"], web)

if __name__ == "__main__":
    main(sys.argv[1:])
