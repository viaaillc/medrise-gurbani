#!/usr/bin/env python3
"""One command from data to live site: validate → covers → build → commit → push.

Usage
  python3 tools/release.py <slug>              # full run for one shabad
  python3 tools/release.py <slug> --no-push    # build and commit locally only
  python3 tools/release.py --rebuild           # rebuild + push without a specific shabad (link updates, copy fixes)

Run from the repo clone on your Mac (or anywhere with git credentials for viaaillc/medrise-gurbani).
GitHub Actions then runs build.py again and deploys docs/ — no zip is needed any more.
"""
import subprocess, sys, pathlib, json

ROOT = pathlib.Path(__file__).resolve().parent.parent     # medrise-gurbani/ (source folder)
REPO = ROOT.parent                                        # git repo root
TOOLS = ROOT / "tools"

def run(cmd, cwd=REPO, check=True):
    print("$", " ".join(cmd))
    return subprocess.run(cmd, cwd=cwd, check=check)

def main(argv):
    slug = next((a for a in argv if not a.startswith("--")), None)
    if not slug and "--rebuild" not in argv: sys.exit(__doc__)
    d = json.load(open(ROOT / "data" / "shabads.json", encoding="utf-8"))
    s = next((x for x in d["shabads"] if x["slug"] == slug), None) if slug else None
    if slug and not s: sys.exit(f"no shabad with slug {slug}")

    # 1. covers (only if missing)
    if s and not (ROOT / "images" / "full" / f"{s['image_slug']}.jpg").exists():
        run([sys.executable, str(TOOLS / "make_cover.py"), slug])
    # 2. validate
    run([sys.executable, str(TOOLS / "new_shabad.py"), "--check"])
    # 3. build
    run([sys.executable, str(ROOT / "build.py")])
    # 4. kit
    if s: run([sys.executable, str(TOOLS / "kit.py"), slug], check=False)
    # 5. retire the zip once source builds are in place
    for z in REPO.glob("*.zip"):
        z.unlink(); print("removed", z.name, "(site now builds from source in Actions)")
    # 6. commit + push
    if not (REPO / ".git").exists():
        print("not a git clone — copy this folder into your clone of viaaillc/medrise-gurbani and rerun"); return
    run(["git", "add", "-A"])
    msg = f"Release: {s['title']}" if s else "Site rebuild"
    r = run(["git", "commit", "-m", msg], check=False)
    if r.returncode != 0: print("nothing to commit")
    if "--no-push" not in argv:
        run(["git", "push"])
        base = d["site"]["url"].rstrip("/")
        print("\nPushed. Live in ~1 minute:")
        if s: print(f"  {base}/{s['slug']}.html")
        print(f"  {base}/sitemap.xml")

if __name__ == "__main__":
    main(sys.argv[1:])
