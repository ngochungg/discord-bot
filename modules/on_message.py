import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "herta"
TRIGGER_NAME = ["herta", "hey Herta", "hey herta",
                "Herta?", "herta?", "yo herta",
                "yo Herta"]

def ask_ollama(prompt):
    #print(f"Sending to Ollama: {prompt}")  # 👀 debug

    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL_NAME,
            "prompt": prompt,
            #"system": "You are a helpful and talkative assistant. Always reply clearly and helpfully.",
            "stream": False
        })
        data = response.json()
        #print(f"🧠 Ollama response: {data}")
        return data.get("response", "❌ No response from Herta.")
    except Exception as e:
        #print(f"🔥 ERROR: {e}")
        return "⚠️ Failed to connect to Herta."

async def handle_message(message, client):
    if message.author == client.user:
        return

    if any(word in message.content.lower() for word in TRIGGER_NAME):
        prompt = message.content
        for word in TRIGGER_NAME:
            prompt = prompt.replace(word, "")

        user_input = message.content[5:]
        await message.channel.send(f"🧠 Thinking...")
        reply = ask_ollama(user_input)
        await message.channel.send(f"{reply}")