FROM debian:bullseye-slim

# Set noninteractive mode for apt to avoid prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies, Python, jq, ngrok, and clean up
RUN apt-get update && apt-get install -y \
    curl gnupg ca-certificates python3 python3-pip unzip jq && \
    rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Install ngrok
RUN curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && \
    echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | tee /etc/apt/sources.list.d/ngrok.list && \
    apt-get update && apt-get install -y ngrok && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy all app files
COPY . .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Optional: create your custom model here if needed
# RUN ollama create herta -f Modelfile

# Expose Ollama's default port
EXPOSE 11434

# Run entrypoint script
CMD ["sh", "entrypoint.sh"]
