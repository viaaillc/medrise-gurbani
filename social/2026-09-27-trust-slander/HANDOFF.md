# Handoff to Claude Code — Sep 27 trust/slander carousel

Status: design approved in claude.ai chat. Caption (caption.md) and generator (build.py) are committed. The 5 slide JPGs are NOT committed yet (the chat's GitHub connector cannot write binary files).

## Tasks
1. `git pull`
2. `pip install playwright && python -m playwright install chromium`
3. `python social/2026-09-27-trust-slander/build.py` -> writes slide01.jpg..slide05.jpg (1080x1350) into this folder. Fonts auto-download to _fonts/ (gitignored).
4. Open all 5 JPGs and check: Gurmukhi shaped correctly (ਨਿੰਦਾ ਭਲੀ ਕਿਸੈ ਕੀ ਨਾਹੀ / ਮਨਮੁਖ ਮੁਗਧ ਕਰੰਨਿ ॥), no text clipped, frame intact.
5. Commit the JPGs and push to main.
6. Do NOT post to Instagram/Facebook/TikTok until Preety confirms the posting method (manual vs. Airtable evening queue).

## Content (verified)
- Gurbani: ਨਿੰਦਾ ਭਲੀ ਕਿਸੈ ਕੀ ਨਾਹੀ ਮਨਮੁਖ ਮੁਗਧ ਕਰੰਨਿ ॥ — Guru Amar Das Ji, Raag Suhi, Ang 755 (verified against multiple SGGS sources).
- Slide 3 verdict line "Not a flaw in you. A mark on them." is MedRise wording, not Gurbani (styled as the italic verdict, same as the Sep 18 declare post).

## Style decisions
- Matches Sep 18 `declare` series palette: peach-cream dawn top, cream glow center, dusty rose bottom; plum text #3f2433; rose #9c3659; gold #c9a24e; Cormorant Garamond + Noto Serif Gurmukhi; gold double frame, brand header, gold ੴ, footer.
- "Modern" variant requested: painted mountains replaced by generated silk waves + bokeh + light ray. Open option: swap in her painted backgrounds if she prefers.
- Hook at 96px (above the 76-88px spec) so the question fills the cover per her hook rule.
