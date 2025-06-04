import asyncio
import logging
from aiogram import Bot
from bot.handlers import student
from bot.handlers.student import TOKEN
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
# Run the bot
async def main() -> None:
    await student.dp.start_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())
