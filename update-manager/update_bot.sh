#!/bin/bash

set -e

# Pull code mới từ GitHub
echo "📂 Pulling latest code..."
cd /app
if ! git_output=$(git pull origin main 2>&1); then
  echo "❌ Git pull failed"
  echo "$git_output"
  exit 1
fi

if [[ "$git_output" != "Already up to date." ]]; then
    echo "♻️ Changes detected! Restarting container..."
    docker restart the-herta || { echo "❌ Docker restart failed"; exit 1; }
else
    echo "✅ No changes, no need to restart."
    exit 0
fi

echo "✅ Bot updated and restarted!"
