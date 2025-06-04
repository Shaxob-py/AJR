from os import getenv
from aiogram import Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from dotenv import load_dotenv
from bot.db.crud import chek_register, location_funk
from bot.db.models import Customer, async_session_maker
from bot.state import CustomerState
from bot.keys.inliny import call_with_admin
from bot.keys.reply import start_button, phone_number, location_button
from bot.teksts import back, buy ,question , admin , settings , start , phone , confirmation , call_with_us , location
load_dotenv()

TOKEN = getenv("TOKEN")

dp = Dispatcher()

@dp.message(CustomerState.phone_state,F.text == back)
@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    btns = [buy, question, admin, settings]
    markab = start_button(btns)
    await message.answer_photo(
        photo="https://ibb.co/dwqQNj6n",
        caption=start,
        parse_mode=ParseMode.HTML, reply_markup=markab)
    await chek_register(message)


@dp.message(F.text == admin)
async def admin_handler(message: Message):
    await message.answer(call_with_us, reply_markup=call_with_admin())


@dp.message(F.text == settings)
async def buy_handler(message: Message):
    async with async_session_maker() as session:
        user = await session.get(Customer, message.from_user.id)
        await message.answer('s')


@dp.message(F.text == back, CustomerState.location_state)
@dp.message(F.text == buy)
async def buy_handler(message: Message, state: FSMContext):
    await message.answer(phone, reply_markup=phone_number())
    await state.set_state(CustomerState.phone_state)


@dp.message(CustomerState.location_state,F.text == "no" )
@dp.message(F.contact,CustomerState.phone_state)
async def location_handler(message: Message, state: FSMContext):
    await message.answer(location, reply_markup=location_button())
    await state.set_state(CustomerState.location_state)

@dp.message(F.location)
async def location_handler(message: Message, state: FSMContext):
    await location_funk(message)
    await message.answer(confirmation,reply_markup=start_button(['yes','no']))
    # await state.set_state(CustomerState.location_state)
