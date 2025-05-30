#!/bin/bash

set -e

# Pull code mới từ GitHub
echo "📂 Pulling latest code..."
cd /app
git_output=$(git pull origin main) || {
  echo "❌ Git pull failed"
  exit 1
}

echo "$git_output"

if echo "$git_output" | grep -q "Already up to date."; then
    echo "✅ No changes, no need to restart."
    exit 0
else
    echo "♻️ Changes detected! Restarting container..."
    exit 2
fi
