import os
from dotenv import load_dotenv
from aiogram import Bot

load_dotenv()
TOKEN = os.getenv("TOKEN")
PAYMENT_PROVIDER_TOKEN = os.getenv("PAYMENT_PROVIDER_TOKEN")

bot = Bot(token=TOKEN)

