import os
import requests

from dotenv import load_dotenv

MODEL_NAME = "the-herta"
TRIGGER_NAME = ["herta", "hey Herta", "hey herta", "Herta?", "herta?", "yo herta", "yo Herta"]
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

conversation = {}


def ask_bot(prompt, usr_id):
    # Build the conversation history for the user
    messages = [
        {
            "role": "system",
            "content": "You are a helpful, friendly, and knowledgeable AI assistant, similar to ChatGPT. "
                       "You understand and respond in English, using a natural and conversational tone. "
                       "Your goal is to help users clearly and kindly. "
                       "You can answer questions, write and explain code (Python, Linux, Docker, Raspberry Pi), "
                       "and help with AI-related tasks. If the user is vague, ask follow-up questions. "
                       "If the user speaks English, reply in English using natural, friendly language. "
                       "And your name will be Herta."
        }
    ]

    # Add user message and assistant's previous messages from conversation history
    messages.extend(conversation.get(usr_id, []))  # Include past conversation if exists

    # Add current user message
    messages.append({"role": "user", "content": prompt})

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        data = response.json()["choices"][0]["message"]["content"]
        return data or "❌ No response from Herta."
    except requests.exceptions.RequestException:
        return "⚠️ Failed to connect to Herta API."


async def handle_message(message, client):
    if message.author == client.user:
        return

    usr_id = str(message.author.id)
    if usr_id not in conversation:
        conversation[usr_id] = []

    # Add user message to conversation
    conversation[usr_id].append({"role": "user", "content": message.content})

    # Check if message contains trigger words
    if any(word in message.content.lower() for word in TRIGGER_NAME):
        prompt = message.content
        for word in TRIGGER_NAME:
            prompt = prompt.replace(word, "")

        user_input = message.content[5:]  # Remove trigger word
        await message.channel.send(f"🧠 Thinking...")

        # Get response from bot
        reply = ask_bot(user_input, usr_id)

        # Add assistant reply to conversation
        conversation[usr_id].append({"role": "assistant", "content": reply})

        await message.channel.send(f"{reply}")