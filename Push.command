#!/bin/bash
# Double-click to push whatever is committed (e.g. after Claude ran the tools for you).
cd "$(dirname "$0")" || exit 1
git status --short | head; git push && echo "Pushed — GitHub Actions is deploying." || echo "Push failed — if it asked for a login, run: gh auth login   (or paste a GitHub token as the password)"
echo; echo "Press any key to close."; read -n 1
