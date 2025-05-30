#!/bin/bash

set -e

# Pull code mới từ GitHub
echo "📂 Pulling latest code..."
cd /app
git_output=$(git pull origin main)

if [[ "$git_output" != "Already up to date." ]]; then
    echo "♻️ Changes detected! Restarting container..."
    echo "$git_output"
    sleep 1
    docker restart the-herta || { echo "❌ Docker restart failed"; exit 1; }
else
    echo "✅ No changes, no need to restart."
    exit 0
fi

echo "✅ Bot updated and restarted!"
