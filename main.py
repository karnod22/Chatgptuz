import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message
from flask import Flask
from threading import Thread
import os

# === API kalitlar (Railway environment variables orqali o'qiladi) ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# === Flask — Railway botni tirik ushlab turish uchun ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot tirik!", 200

def run():
    port = int(os.environ.get("PORT", 8080))  # Railway uchun portni avtomatik oladi
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# === Bot va loglar ===
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot=bot)

# === ChatGPT javobi ===
async def get_chatgpt_response(user_message):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": user_message}]
    }
    async with aiohttp.ClientSession() as session:
        async with session.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload) as resp:
            if resp.status == 200:
                result = await resp.json()
                return result['choices'][0]['message']['content']
            else:
                return f"❌ Xatolik yuz berdi! Kod: {resp.status}"

# === /start komandasi ===
@dp.message(CommandStart())
async def start_command(message: Message):
    await message.answer("Salom! Men ChatGPT botman. Savolingizni yozing.")

# === Har qanday matnga javob ===