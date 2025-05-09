#!/bin/bash

set -e

# Pull code mới từ GitHub
echo "📂 Pulling latest code..."
cd /app
git pull origin main || { echo "❌ Git pull failed"; exit 1; }

echo "🐳 Rebuilding docker image..."
docker build -t discord-bot . || { echo "❌ Docker build failed"; exit 1; }

echo "🔁 Restarting container..."
docker stop the-herta || true
docker rm the-herta || true
docker-compose up -d --build

echo "✅ Update completed!"
