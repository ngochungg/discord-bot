#!/bin/bash
set -e

echo "📂 Pulling latest code..."
cd /app

git_output=$(git pull origin main) || {
  echo "❌ Git pull failed"
  exit 1
}

echo "$git_output"

sleep 10

if echo "$git_output" | grep -q "Already up to date."; then
    echo "✅ No changes, no need to restart."
else
    echo "♻️ Changes detected! Restarting container..."
    docker restart the-herta || {
        echo "❌ Docker restart failed"
        exit 1
    }
    echo "✅ Bot updated and restarted!"
fi

exit 0  # 💡 Luôn exit 0 nếu không có lỗi thực sự