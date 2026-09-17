#!/bin/bash
# Double-click: pull GitHub's newer commits, then push what's committed here.
cd "$(dirname "$0")" || exit 1
git pull --rebase --autostash && git push && echo "Synced + pushed — GitHub Actions is deploying." || echo "Sync failed — see above."
echo; echo "Press any key to close."; read -n 1
