#!/bin/bash

set -e

# Pull code mới từ GitHub
echo "📂 Pulling latest code..."
cd /app
git pull origin main || { echo "❌ Git pull failed"; exit 1; }

echo "🔁 Restarting bot container..."
docker restart the-herta || { echo "❌ Docker restart failed"; exit 1; }

echo "✅ Bot updated and restarted!"
