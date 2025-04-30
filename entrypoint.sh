#!/bin/bash
echo "🚀 Starting The Herta Bot..."

# Kill any existing ngrok or ollama sessions (optional in Docker)
pkill ngrok 2>/dev/null || true
pkill -f "ollama serve" 2>/dev/null || true

# Start Ollama in the background
echo "🧠 Starting Ollama..."
OLLAMA_HOST=0.0.0.0 ollama serve &

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to be ready..."
until curl -s http://localhost:11434 > /dev/null; do
  sleep 1
done
echo "✅ Ollama is ready!"

# Pull mistral model (skip if already pulled)
ollama pull mistral

# Create custom model if not exists
if ! ollama list | grep -q the-herta; then
  echo "✨ Creating custom model: the-herta"
  ollama create the-herta -f Modelfile
fi

# Start ngrok using your config file
echo "🌐 Starting ngrok..."
ngrok start --all --config /app/ngrok.yml > /dev/null &

# Wait for ngrok to initialize
sleep 3

# Get the public ngrok URL
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url')
echo "🔗 Ngrok Public URL: $NGROK_URL"

# Export the URL so your Python bot can use it
export NGROK_URL

#  Ensure copy ngrok.yml
COPY ngrok.yml /app/ngrok.yml

# Run your bot
echo "🤖 Launching your bot..."
python3 bot.py
