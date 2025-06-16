# main.py
import asyncio
import logging
from aiogram import Bot
from bot.despecher import config
from bot.handlers import student
from bot.handlers.admin import admin_router

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN)

async def main():
    student.dp.include_router(admin_router)
    await student.dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())