"""Regenerates the "accused of what you never did" carousel (slide01-07.jpg, 1080x1350).
Run from repo root:  pip install playwright && python -m playwright install chromium
                     python social/2026-09-29-falsely-accused/build.py
"""
import asyncio, random, os, pathlib, urllib.request, base64
HERE=pathlib.Path(__file__).resolve().parent
FD=HERE/"_fonts"; FD.mkdir(exist_ok=True)
G="https://raw.githubusercontent.com/google/fonts/main/ofl/"
FONTS={"Cormorant Garamond":("cormorantgaramond/CormorantGaramond%5Bwght%5D.ttf","normal"),
       "Cormorant Garamond I":("cormorantgaramond/CormorantGaramond-Italic%5Bwght%5D.ttf","italic"),
       "Noto Serif Gurmukhi":("notoserifgurmukhi/NotoSerifGurmukhi%5Bwght%5D.ttf","normal")}
FACES=""
for fam,(path,style) in FONTS.items():
    f=FD/path.split("/")[-1].replace("%5B","[").replace("%5D","]")
    if not f.exists(): urllib.request.urlretrieve(G+path,f)
    FACES+=f"@font-face{{font-family:'{fam.replace(' I','')}';src:url(data:font/ttf;base64,{base64.b64encode(f.read_bytes()).decode()});font-style:{style};font-weight:300 700}}"
from playwright.async_api import async_playwright

PLUM="#3f2433"; ROSE="#9c3659"; GOLD="#c9a24e"

def waves(seed):
    r=random.Random(seed)
    layers=[("#f2d3bf",.75,880),("#e8b9a9",.7,960),("#d9a09a",.75,1050),("#c98a88",.85,1150),("#bb7a7d",.9,1250)]
    out=""
    for i,(col,op,base) in enumerate(layers):
        a=r.randint(30,70); ph=r.uniform(0,6.28); f=r.uniform(1.2,2.0)
        import math
        pts=[]
        for x in range(0,1101,20):
            y=base+a*math.sin(x/1080*f*math.pi+ph)+0.4*a*math.sin(x/1080*3.1*math.pi+ph*1.7)
            pts.append(f"{x},{y:.1f}")
        d="M0,1350 L"+" L".join(pts)+" L1100,1350 Z"
        out+=f'<path d="{d}" fill="url(#w{i})" opacity="{op}"/>'
        top="M"+" L".join(pts)
        out+=f'<path d="{top}" fill="none" stroke="#fff4ea" stroke-width="3" opacity=".45"/>'
        out+=f'<linearGradient id="w{i}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{col}"/><stop offset="1" stop-color="{col}" stop-opacity=".55"/></linearGradient>'
    # silk highlight line
    return out

def bokeh(seed):
    r=random.Random(seed*7)
    s=""
    for _ in range(26):
        x=r.randint(0,1080); y=r.randint(820,1340); rad=r.randint(6,30); o=r.uniform(.10,.30)
        s+=f'<circle cx="{x}" cy="{y}" r="{rad}" fill="#fff6ea" opacity="{o:.2f}"/>'
    for _ in range(10):
        x=r.randint(0,1080); y=r.randint(80,700); rad=r.randint(6,22); o=r.uniform(.15,.35)
        s+=f'<circle cx="{x}" cy="{y}" r="{rad}" fill="#fff8ee" opacity="{o:.2f}"/>'
    return s

GLOWS=[(540,560),(380,500),(540,470),(700,480),(420,520),(660,500),(540,600)]

def bg(n):
    gx,gy=GLOWS[n-1]
    return f'''<svg class="bgsvg" viewBox="0 0 1080 1350" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#efcfb9"/><stop offset=".35" stop-color="#f4d6b8"/><stop offset=".6" stop-color="#f7e3cf"/><stop offset="1" stop-color="#c58a86"/></linearGradient>
<radialGradient id="glow" cx="{gx/1080}" cy="{gy/1350}" r=".55"><stop offset="0" stop-color="#fffaf2" stop-opacity="1"/><stop offset=".45" stop-color="#fdf1e3" stop-opacity=".75"/><stop offset="1" stop-color="#fdf1e3" stop-opacity="0"/></radialGradient>
<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="14"/></filter><filter id="b2"><feGaussianBlur stdDeviation="4"/></filter><linearGradient id="ray" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff8ee" stop-opacity=".35"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>
<rect width="1080" height="1350" fill="url(#sky)"/>
<rect width="1080" height="1350" fill="url(#glow)"/>
<g filter="url(#b2)">{waves(n)}</g>
<polygon points="{1080 if n%2 else 0},700 {700 if n%2 else 380},1350 {820 if n%2 else 260},1350" fill="url(#ray)" opacity=".6" filter="url(#blur)"/><g filter="url(#blur)">{bokeh(n)}</g>
</svg>'''

CSS=FACES+f"""
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;overflow:hidden}}
.s{{position:relative;width:1080px;height:1350px;overflow:hidden;font-family:'Cormorant Garamond',serif;color:{PLUM}}}
.bgsvg{{position:absolute;inset:0;width:1080px;height:1350px}}
.frame{{position:absolute;inset:30px;border:2px solid rgba(201,162,78,.75)}}
.frame:after{{content:"";position:absolute;inset:8px;border:1px solid rgba(201,162,78,.35)}}
.hd{{position:absolute;top:66px;left:0;right:0;text-align:center}}
.brand{{font-size:30px;letter-spacing:.14em;font-weight:500;font-variant:small-caps;color:#6a4150}}
.tag{{font-size:17px;letter-spacing:.2em;color:#8a6264;margin-top:4px;font-variant:small-caps}}
.ek{{font-family:'Noto Serif Gurmukhi',serif;font-size:52px;color:{GOLD};margin-top:6px;line-height:1.2}}
.pg{{position:absolute;top:78px;right:84px;font-size:20px;letter-spacing:.15em;color:#8a6264}}
.c{{position:absolute;left:110px;right:110px;top:250px;bottom:260px;display:flex;flex-direction:column;justify-content:center;text-align:center}}
.ft{{position:absolute;bottom:62px;left:0;right:0;text-align:center}}
.ft .n{{font-size:36px;font-weight:600;color:#4a2a38}}
.ft .t{{font-size:16px;letter-spacing:.22em;color:#6e4a4e;font-variant:small-caps}}
.ft .d{{width:7px;height:7px;border-radius:50%;background:#6e4a4e;margin:8px auto 0}}
.swipe{{position:absolute;bottom:190px;left:0;right:0;text-align:center;font-size:20px;letter-spacing:.3em;color:#7a5558;font-variant:small-caps}}
.hook{{font-size:96px;line-height:1.08;font-style:italic;font-weight:500;color:{PLUM};text-wrap:balance}}
.sub{{font-size:44px;color:{ROSE};margin-top:44px;font-weight:500;text-wrap:balance}}
.eyebrow{{font-size:22px;letter-spacing:.3em;color:#8a6264;font-variant:small-caps;margin-bottom:26px}}
.h{{font-size:84px;line-height:1.1;font-weight:500;text-wrap:balance}}
.b{{font-size:47px;line-height:1.35;margin-top:36px;color:#4f3140;text-wrap:balance}}
.rose{{color:{ROSE};font-style:italic}}
.gm{{font-family:'Noto Serif Gurmukhi',serif;font-size:76px;line-height:1.55;font-weight:500;color:{ROSE}}}
.tr{{text-wrap:balance;font-size:30px;font-style:italic;color:#6e4a4e;margin-top:14px}}
.div{{display:flex;align-items:center;justify-content:center;gap:16px;margin:34px 0 30px}}
.div i{{display:block;width:140px;height:1.5px;background:{GOLD}}}
.div b{{display:block;width:13px;height:13px;background:{GOLD};transform:rotate(45deg)}}
.en{{font-size:47px;line-height:1.3;font-weight:600;color:#3f2433;text-wrap:balance}}
.src{{font-size:20px;letter-spacing:.2em;color:#7a5558;margin-top:24px;font-variant:small-caps}}
.note{{font-size:34px;font-style:italic;color:#5a3a46;margin-top:26px;text-wrap:balance}}
.gm2{{font-size:66px}}
.gm3{{font-size:58px}}
.verdict{{text-wrap:balance;font-size:44px;font-style:italic;color:{ROSE};margin-top:50px}}
.fateh{{font-family:'Noto Serif Gurmukhi',serif;font-size:38px;color:{ROSE};margin-top:50px;line-height:1.55}}
"""

def page(n,inner,swipe=False):
    return f"""<html><head><style>{CSS}</style></head><body><div class="s">{bg(n)}
<div class="frame"></div>
<div class="hd"><div class="brand">MedRise Gurbani</div><div class="tag">meditate · learn · rise with gurbani</div><div class="ek">ੴ</div></div>
<div class="pg">{n} / 7</div>
<div class="c">{inner}</div>
{'<div class="swipe">swipe →</div>' if swipe else ''}
<div class="ft"><div class="n">MedRise Gurbani</div><div class="t">meditate and rise with gurbani</div><div class="d"></div></div>
</div></body></html>"""

slides=[
 ("""<div class="hook">How do you defend yourself against something you never did?</div>
<div class="sub">Gurbani answered this long before you were accused.</div>""",True),
 ("""<div class="eyebrow">here’s a hard truth</div>
<div class="h">Someone hunting for a flaw will find one, even where none exists.</div>
<div class="b">The accusation shows what they were searching for. <span class="rose">Not what you did.</span></div>""",False),
 ("""<div class="eyebrow">now open gurbani</div>
<div class="gm gm2">ਜਉ ਦੇਖੈ ਛਿਦ੍ਰੁ ਤਉ ਨਿੰਦਕੁ ਉਮਾਹੈ<br>ਭਲੋ ਦੇਖਿ ਦੁਖ ਭਰੀਐ ॥</div>
<div class="tr">Jau dekhai chhidr tau nindak umaahai, bhalo dekh dukh bhareeai.</div>
<div class="div"><i></i><b></b><i></i></div>
<div class="en">When he sees a flaw, the slanderer is delighted; seeing good, he is filled with pain.</div>
<div class="src">guru arjan dev ji · raag bilaval · ang 823</div>
<div class="verdict">He went looking for a hole. So he found one.</div>""",False),
 ("""<div class="gm gm3">ਨਿੰਦਕੁ ਐਸੇ ਹੀ ਝਰਿ ਪਰੀਐ ॥<br>ਇਹ ਨੀਸਾਨੀ ਸੁਨਹੁ ਤੁਮ ਭਾਈ<br>ਜਿਉ ਕਾਲਰ ਭੀਤਿ ਗਿਰੀਐ ॥</div>
<div class="tr">Nindak aise hee jhar pareeai. Ih neesaanee sunahu tum bhaaee jio kaalar bheet gireeai.</div>
<div class="div"><i></i><b></b><i></i></div>
<div class="en">Thus the slanderer crumbles away. Listen, brother, this is the sign: he collapses like a wall of saltpetre.</div>
<div class="src">guru arjan dev ji · raag bilaval · ang 823</div>
<div class="verdict">A false charge is a wall of salt. It falls on its own.</div>""",False),
 ("""<div class="gm gm2">ਨਾਨਕ ਕਾ ਰਾਖਾ ਆਪਿ ਪ੍ਰਭੁ ਸੁਆਮੀ<br>ਕਿਆ ਮਾਨਸ ਬਪੁਰੇ ਕਰੀਐ ॥</div>
<div class="tr">Naanak kaa raakhaa aap prabh suaamee, kiaa maanas bapure kareeai.</div>
<div class="div"><i></i><b></b><i></i></div>
<div class="en">God Himself is Nanak’s protector; what can wretched mortals do?</div>
<div class="src">guru arjan dev ji · raag bilaval · ang 823</div>
<div class="verdict">Your defence was never your job alone.</div>""",False),
 ("""<div class="gm gm2">ਅਨਬੋਲੇ ਕਉ ਤੁਹੀ ਪਛਾਨਹਿ<br>ਜੋ ਜੀਅਨ ਮਹਿ ਹੋਤਾ ॥</div>
<div class="tr">Anbole kau tuhee pachhaanahi jo jeean meh hotaa.</div>
<div class="div"><i></i><b></b><i></i></div>
<div class="en">Without a word spoken, You know whatever is within every heart.</div>
<div class="src">guru arjan dev ji · raag bilaval · ang 823</div>
<div class="verdict">You don’t have to win the argument. The truth is already known.</div>""",False),
 ("""<div class="h">Let the wall fall on its own.</div>
<div class="b rose">Keep your conduct clean. Waheguru is already your witness.</div>
<div class="fateh">ਵਾਹਿਗੁਰੂ ਜੀ ਕਾ ਖ਼ਾਲਸਾ<br>ਵਾਹਿਗੁਰੂ ਜੀ ਕੀ ਫ਼ਤਹਿ</div>""",False),
]

async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={"width":1080,"height":1350})
        for n,(inner,sw) in enumerate(slides,1):
            await pg.set_content(page(n,inner,sw)); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(300)
            await pg.screenshot(path=str(HERE/f"slide0{n}.jpg"),type="jpeg",quality=94)
        await b.close()
asyncio.run(main())
