import os
import re
from pathlib import Path

import requests
from dotenv import load_dotenv

from utils.long_message import send_long_message

ALLOWED_USER_IDS = [377676460334514176]

# --- Setup bot ---
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- File path ---
__File__ = Path(__file__).parent.resolve()
project_dir = __File__.parent

# --- !summarize: summarize url or long text ---
async def summarize(ctx, *, message_text: str):

    # Text to chat
    await ctx.channel.send(f"🔍📝 Summarizing...")

    # Check if message_text url or text
    if is_url(message_text):

        # prompt for AI
        base_prompt = "Summarize the main information from the webpage at this URL. Provide a brief and clear summary of the key ideas and important details: "
        # Combine prompt and msg
        messages = [{
            "role": "system",
            "content": base_prompt + ctx.content
        }]

        # AI url
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": messages
        }

        # try to take response from AI model
        try:
            response = requests.post(url, headers=headers, json=data)
            data = response.json()["choices"][0]["message"]["content"]
            await send_long_message(ctx.channel, data) or "❌ No response from Herta."
        except requests.exceptions.RequestException:
            await ctx.channel.send("⚠️ Failed to connect to Herta API.")
    else:
        # prompt for AI
        base_prompt = "Summarize the following passage into key points as bullet points, each point concise and easy to understand:"

        # Combine prompt and msg
        messages = [{
            "role": "system",
            "content": base_prompt + ctx.content
        }]

        # AI url
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": messages
        }

        # try to take response from AI model
        try:
            response = requests.post(url, headers=headers, json=data)
            data = response.json()["choices"][0]["message"]["content"]
            await send_long_message(ctx.channel, data) or "❌ No response from Herta."
        except requests.exceptions.RequestException:
            await ctx.channel.send("⚠️ Failed to connect to Herta API.")

# --- !translate: vi <-> en ---
async def translate(ctx, *, message_text: str):
    # Text to chat
    await ctx.channel.send(f"🇻🇳🔁🇬🇧 Translating...")

    # Check if message_text is vi or en
    if is_vietnamese(message_text):
        # prompt for AI
        base_prompt = f"Translate the following Vietnamese text into English: "

        # Combine prompt and msg
        messages = [{
            "role": "system",
            "content": base_prompt + ctx.content
        }]
        # AI url
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": messages
        }

        # try to take response from AI model
        try:
            response = requests.post(url, headers=headers, json=data)
            data = response.json()["choices"][0]["message"]["content"]
            await send_long_message(ctx.channel, data) or "❌ No response from Herta."
        except requests.exceptions.RequestException:
            await ctx.channel.send("⚠️ Failed to connect to Herta API.")
    else:
        # prompt for AI
        base_prompt = f"Dịch đoạn văn tiếng Anh sau sang tiếng Việt: "

        # Combine prompt and msg
        messages = [{
            "role": "system",
            "content": base_prompt + ctx.content
        }]
        # AI url
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": messages
        }

        # try to take response from AI model
        try:
            response = requests.post(url, headers=headers, json=data)
            data = response.json()["choices"][0]["message"]["content"]
            await send_long_message(ctx.channel, data) or "❌ No response from Herta."
        except requests.exceptions.RequestException:
            await ctx.channel.send("⚠️ Failed to connect to Herta API.")

# --- !fix_grammar: fix grammar ---
async def fix_grammar(ctx):
    # Text to chat
    await ctx.channel.send(f"📝🔧 Fixing grammar...")

    # prompt for AI
    base_prompt = f"Fix the grammar and spelling errors in this text: "

    # Combine prompt and msg
    messages = [{
        "role": "system",
        "content": base_prompt + ctx.content
    }]
    # AI url
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages
    }

    # try to take response from AI model
    try:
        response = requests.post(url, headers=headers, json=data)
        data = response.json()["choices"][0]["message"]["content"]
        await send_long_message(ctx.channel, data) or "❌ No response from Herta."
    except requests.exceptions.RequestException:
        await ctx.channel.send("⚠️ Failed to connect to Herta API.")

def is_url(text: str) -> bool:
    # Regex đơn giản để nhận diện URL
    url_pattern = re.compile(
        r'^(https?:\/\/)?'        # http:// hoặc https:// (có thể có hoặc không)
        r'([\w\-]+\.)+[\w]{2,}'   # domain, ví dụ: example.com
        r'(\/[\w\-._~:\/?#\[\]@!$&\'()*+,;=%]*)?$'  # path (tùy chọn)
    )
    return bool(url_pattern.match(text.strip()))

def is_vietnamese(text: str) -> bool:
    # Kiểm tra xem có dấu tiếng Việt không
    pattern = re.compile(r"[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]", re.IGNORECASE)
    return bool(pattern.search(text))