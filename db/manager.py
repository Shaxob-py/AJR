import asyncio
from mailbox import Message
from sqlalchemy import select, update
import httpx
from sqlalchemy.dialects.postgresql import insert

from bot.despecher.config import bot
from db.models import async_session_maker, Customer


# async def chek_register(message: Message):
#     async with async_session_maker() as session:
#         exists = await session.scalar(
#             select(Customer.id).where(Customer.id == message.from_user.id)
#         )
#         if not exists:
#             new_user = Customer(
#                 id=message.from_user.id,
#                 full_name=message.from_user.full_name,
#                 username=message.from_user.username,
#             )
#             session.add(new_user)
#             await session.commit()


async def get_location_data(lat: float, lon: float):
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1&accept-language=uz,en"
    async with httpx.AsyncClient(headers={"User-Agent": "MyTelegramBot/1.0"}, timeout=5.0) as client:
        return (await client.get(url)).json()

async def location_funk(message: Message):
    lat, lon = message.location.latitude, message.location.longitude
    try:
        data = await get_location_data(lat, lon)
        address_parts = data.get("address", {})

        fields = {
            "house_number": "🏠 Uy", "road": "🛣️ Ko‘cha", "street": "🛣️ Ko‘cha",
            "village": "🏘️ Qishloq", "neighbourhood": "🏘️ Mahalla", "suburb": "🏘️ Hudud",
            "county": "🏛️ Tuman", "municipality": "🏛️ Tuman", "state": "🗺️ Viloyat",
            "region": "🗺️ Viloyat", "postcode": "📮 Pochta kodi", "country": "🌍 Mamlakat"
        }

        result = "\n".join(f"{fields[k]}: {v}" for k, v in address_parts.items() if k in fields)
        result += f"\n📍 Koordinatalar: {lat:.6f}, {lon:.6f}"
        result += f"\n🗺️ [Google Maps da ochish](https://www.google.com/maps?q={lat},{lon})"

        await message.answer(f"📍 **Aniq manzil:**\n\n{result}", parse_mode="Markdown")

    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")


async def update_user_contact(message):
    async with async_session_maker() as session:
        await session.execute(
            update(Customer)
            .where(Customer.id == message.from_user.id)
            .values(phone_number=message.contact.phone_number)
        )
        await session.commit()


async def insert_users_if_not_exist(user_id: int, name, username):
    async with async_session_maker() as session:
        stmt = (
            insert(Customer)
            .values(id=user_id, name=name, username=username)
            .on_conflict_do_nothing(index_elements=['id'])  # id = primary key
        )
        await session.execute(stmt)
        await session   .commit()


async def stream_customer_ids() -> list[int]:
    async with async_session_maker() as session:
        result = await session.execute(select(Customer.id))
        all_ids = result.scalars().all()
        return all_ids

async def send_message(user_id: int, text: str):
    try:
        await bot.send_message(user_id, text)
    except Exception as e:
        print(f"Xatolik user {user_id}: {e}")


