import asyncio
import logging
from bot.despecher.config import bot
from bot.handlers import student
from bot.handlers.admin import admin_router

logging.basicConfig(level=logging.INFO)

async def main():
    student.dp.include_router(admin_router)
    await student.dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
