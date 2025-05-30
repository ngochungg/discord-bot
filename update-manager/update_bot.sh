#!/bin/bash

set -e

# Pull code mới từ GitHub
echo "📂 Pulling latest code..."
cd /app
git_output=$(git pull origin main) || {
  echo "❌ Git pull failed"; exit 1;
}
# shellcheck disable=SC2154
echo "$git_output"

if [[ "$git_output" != "Already up to date." ]]; then
    echo "♻️ Changes detected! Restarting container..."
    docker restart the-herta || { echo "❌ Docker restart failed"; exit 1; }
else
    echo "✅ No changes, no need to restart."
    exit 0
fi

sleep 5

echo "✅ Bot updated and restarted!"
