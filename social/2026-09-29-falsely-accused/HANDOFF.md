# Handoff to Claude Code — "falsely accused" carousel

Status: approved in claude.ai chat. build.py + caption.md committed. The 7 slide JPGs are NOT committed (chat connector can't write binaries).

## Tasks
1. `git pull`
2. `pip install playwright && python -m playwright install chromium` (skip if done)
3. `python social/2026-09-29-falsely-accused/build.py` -> slide01.jpg..slide07.jpg (1080x1350). Fonts auto-download to _fonts/ (gitignored).
4. Open all 7 JPGs: check Gurmukhi shaping (esp. ਛਿਦ੍ਰੁ on slide 3, ਪ੍ਰਭੁ on slide 5), no clipped text, no orphan ॥, frame intact.
5. Verify slide 5 line on SikhiToTheMax: ਨਾਨਕ ਕਾ ਰਾਖਾ ਆਪਿ ਪ੍ਰਭੁ ਸੁਆਮੀ ਕਿਆ ਮਾਨਸ ਬਪੁਰੇ ਕਰੀਐ ॥ (one source truncated after ਬਪੁਰੇ). Fix build.py if it differs.
6. Commit the JPGs and push to main.
7. Do NOT post to Instagram/Facebook/TikTok until Preety confirms posting method.

## Content
- Slides 3–5: one shabad — Bilaval Mahala 5, Ang 823 (ਨਿੰਦਕੁ ਐਸੇ ਹੀ ਝਰਿ ਪਰੀਐ). This shabad opens her "Ham Utre Paar" set.
- Slide 6: separate shabad, same Ang/Raag (ਅਨਬੋਲੇ ਕਉ ਤੁਹੀ ਪਛਾਨਹਿ). Keep it on its own slide.
- Italic verdict lines and slide 7 are MedRise wording, not Gurbani.
- Hook avoids the word "cheating" deliberately (Gurbani frames it as slander/false accusation).
