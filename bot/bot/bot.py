import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Не указан токен в переменных окружения.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
