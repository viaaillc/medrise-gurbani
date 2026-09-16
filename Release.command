#!/bin/bash
# Double-click to release. Runs check -> build -> kit -> commit -> push for the newest spec (or a slug you pass).
cd "$(dirname "$0")/medrise-gurbani" || exit 1
SLUG="$1"
if [ -z "$SLUG" ]; then
  SLUG=$(ls -t releases 2>/dev/null | head -1)
  echo "Newest release folder: $SLUG"
  read -r -p "Slug to release [$SLUG] (or 'rebuild'): " ANS; SLUG=${ANS:-$SLUG}
fi
if [ "$SLUG" = "rebuild" ]; then python3 tools/release.py --rebuild; else
  # add the entry if it isn't in the data file yet
  python3 - "$SLUG" <<'PY'
import json,sys,pathlib
slug=sys.argv[1]; d=json.load(open('data/shabads.json',encoding='utf-8'))
if not any(s['slug']==slug for s in d['shabads']):
    spec=pathlib.Path('releases')/slug/'spec.json'
    if spec.exists():
        import subprocess; subprocess.run([sys.executable,'tools/new_shabad.py',str(spec)],check=True)
    else: sys.exit(f"no entry and no releases/{slug}/spec.json")
PY
  python3 tools/release.py "$SLUG"
fi
echo; echo "Done. Press any key to close."; read -n 1
