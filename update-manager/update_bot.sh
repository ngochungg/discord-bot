#!/bin/bash
set -e

cd /app
git_output=$(git pull origin main) || {
  echo "❌ Git pull failed"
  exit 1
}

echo "$git_output"

if echo "$git_output" | grep -q "Already up to date."; then
    echo "✅ No changes, no need to restart."
else
    echo "♻️ Changes detected! Restarting container..."
fi