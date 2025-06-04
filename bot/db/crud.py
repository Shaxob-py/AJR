import httpx

from bot.db.models import async_session_maker, Customer


async def chek_register(message):
    async with async_session_maker() as session:
        user = await session.get(Customer, message.from_user.id)
        if not user:
            user = Customer(
                id=message.from_user.id,
                full_name=message.from_user.full_name,
                username=message.from_user.username,   
            )
            session.add(user)
            await session.commit()

async def location_funk(message):
    latitude = message.location.latitude
    longitude = message.location.longitude
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()
        address = data.get("display_name", "Manzil topilmadi")
    await message.answer(f"{'Address'}\n{address}")
