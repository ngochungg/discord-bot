#!/bin/bash
set -e

echo "📂 Pulling latest code..."
cd /app
git_output=$(git pull origin main)

echo "$git_output"