#!/bin/bash

set -e

# Pull code mới từ GitHub
echo "📂 Pulling latest code..."
cd /app
git_output=$(git pull origin main 2>&1)
# shellcheck disable=SC2181
if [[ $? -ne 0 ]]; then
    echo "❌ Git pull failed"
    echo "$git_output"
    exit 1
fi

if [[ "$git_output" != "Already up to date." ]]; then
    echo "♻️ Changes detected! Restarting container..."
    echo "$git_output"
    docker restart the-herta || { echo "❌ Docker restart failed"; exit 1; }
else
    echo "✅ No changes, no need to restart."
    exit 0
fi

sleep 5

echo "✅ Bot updated and restarted!"
