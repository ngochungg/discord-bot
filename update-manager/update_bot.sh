#!/bin/bash

set -e

# Pull code mới từ GitHub
echo "📂 Pulling latest code..."
cd /app
git_output=$(git pull origin main)

if echo "$git_output" | grep -q "Already up to date."; then
    echo "✅ No changes, no need to restart."
    exit 0

else
    echo "♻️ Changes detected! Restarting container..."
    echo "$git_output"

    sleep 10

    docker restart the-herta || { echo "❌ Docker restart failed"; exit 1; }
fi

echo "✅ Bot updated and restarted!"
