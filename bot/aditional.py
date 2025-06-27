from select import select

from openpyxl import Workbook
from pathlib import Path
import re
from datetime import datetime

from db.models import async_session_maker, Admin

base_dir = Path("temp_excel")
base_dir.mkdir(exist_ok=True)

def generate_excel_file(data: list[dict], headers: list[str], rows: list[list], filename_prefix: str) -> Path:
    today = datetime.now().strftime("%Y-%m-%d")
    safe_date = re.sub(r'[\\/*?:"<>|]', "_", today)
    filename = f"{filename_prefix}_{safe_date}.xlsx"
    file_path = base_dir / filename
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = filename_prefix.capitalize()
    sheet.append(headers)
    for row in rows:
        sheet.append(row)

    workbook.save(file_path)
    return file_path


async def product_change() -> list[int]:
    async with async_session_maker() as session:
        result = await session.execute(select(Admin.product_prise))
        all_ids = result.scalars().all()
        return all_ids

BATCH_SIZE = 100

async def send_to_user(bot, user_id: int, message):
    try:
        if message.photo:
            await bot.send_photo(user_id, photo=message.photo[-1].file_id, caption=message.caption or "")
        elif message.document:
            await bot.send_document(user_id, document=message.document.file_id, caption=message.caption or "")
        elif message.text:
            await bot.send_message(user_id, text=message.text)
    except Exception as e:
        print(f"❌ {user_id} - Error: {e}")