import asyncio

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile
from sqlalchemy import select, update
from bot.aditional import generate_excel_file, BATCH_SIZE, send_to_user
from bot.despecher.config import bot
from db.models import Admin, Customer, async_session_maker, Payment
from bot.despecher.state import AdminState
from bot.keys.reply import admin_menu_button, choice_data_button, reply_button
from bot.teksts.teksts import wrong_password, welcome_admin, choice_data, data, \
    back, main_menu_back, all_users, all_daily, all_payments, change_password, warning_change_password, \
    changing_password, \
    return_password, logout, my_order, product_info, buy, free_consultation, settings, start, question, message_all, \
    main_menu, price_exchange, correct_form_to_pay, successful, in_valid_digit, input_message

admin_router = Router()


@admin_router.message(F.text == "admin")
async def admin_panel(message: Message, state: FSMContext):
    async with async_session_maker() as session:
        admin = await session.get(Admin, message.from_user.id)
        await state.clear()
    if admin:
        await message.answer('Parolni kriting 🔒')
        await state.set_state(AdminState.register_admin)
        await message.delete()


@admin_router.message(AdminState.register_admin, F.text)
async def show_stats(message: Message, state: FSMContext):
    password = message.text
    async with async_session_maker() as session:
        admin = await session.get(Admin, message.from_user.id)
        if admin.password != password:
            await message.answer(wrong_password)
            await message.delete()
            await state.clear()
            return
        await message.delete()
        await state.set_state(AdminState.menu_panel)
        await message.answer(welcome_admin, reply_markup=admin_menu_button())


@admin_router.message(AdminState.change_prise, F.text == back)
@admin_router.message(AdminState.data_state, F.text == back)
@admin_router.message(AdminState.change_password_state, F.text == back)
@admin_router.message(AdminState.invalid_password)
async def show_menu(message: Message, state: FSMContext):
    await message.answer(main_menu_back, reply_markup=admin_menu_button())
    await state.set_state(AdminState.menu_panel)


@admin_router.message(AdminState.menu_panel, F.text == data)
async def send_broadcast(message: Message, state: FSMContext):
    await message.answer(choice_data, reply_markup=choice_data_button())
    await state.set_state(AdminState.data_state)


@admin_router.message(AdminState.data_state, F.text.in_([all_users, all_daily, all_payments]))
async def send_data(message: Message):
    file_path = None  # <-- добавлено
    try:
        async with async_session_maker() as session:

            if message.text == all_users:
                result = await session.execute(select(Customer))
                users = result.scalars().all()

                if not users:
                    return await message.answer("⛔ Ma'lumot topilmadi.")

                headers = ["№", "Username", "Name", "Phone", "Location"]
                rows = [
                    [
                        i,
                        f"@{u.username}" if u.username else "",
                        u.name or "",
                        u.phone_number or "",
                        u.location or ""
                    ]
                    for i, u in enumerate(users, 1)
                ]
                file_path = generate_excel_file(users, headers, rows, "customers")
                caption = "📄 Barcha foydalanuvchilar"

            elif message.text in [all_payments, all_daily]:
                result = await session.execute(select(Payment))
                payments = result.scalars().all()

                if not payments:
                    return await message.answer("📭 Hozircha to‘lovlar yo‘q.")

                headers = ["№", "Pay (sum)", "User ID", "Paid Time", "Status", "Location", "Coordinates",
                           "Phone Number"]
                rows = [
                    [
                        i,
                        float(p.pay),
                        p.user_id,
                        p.paid.strftime("%Y-%m-%d %H:%M"),
                        p.status or "",
                        p.location or "",
                        p.coordinates or "",
                        p.phone_number or ""
                    ]
                    for i, p in enumerate(payments, 1)
                ]
                file_path = generate_excel_file(payments, headers, rows, "payments")
                caption = f"💳 To‘lovlar Excel fayli"

            if file_path:
                await message.answer_document(document=FSInputFile(file_path), caption=caption)

    finally:
        if file_path and file_path.exists():
            file_path.unlink(missing_ok=True)



@admin_router.message(AdminState.menu_panel, F.text == change_password)
async def change_password_admin(message: Message, state: FSMContext):
    await message.answer(warning_change_password)
    await message.answer(changing_password, reply_markup=reply_button([back]))
    await state.set_state(AdminState.change_password_state)


@admin_router.message(AdminState.change_password_state, F.text)
async def change_password_state(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    await message.answer(return_password, reply_markup=ReplyKeyboardRemove())
    await state.set_state(AdminState.confirm_password_state)


@admin_router.message(AdminState.confirm_password_state, F.text)
async def confirm_password_state(message: Message, state: FSMContext):
    data = await state.get_data()
    password_from_state = data.get("password")

    if not password_from_state or message.text != password_from_state:
        await state.clear()
        await state.set_state(AdminState.invalid_password)
        await message.answer("❌ Parol noto‘g‘ri. Iltimos, qaytadan urinib ko‘ring.", reply_markup=admin_menu_button())
        return

    async with async_session_maker() as session:
        await session.execute(update(Admin).where(Admin.id == message.from_user.id).values(password=message.text))
        await session.commit()

    await message.answer("✅ Parol tasdiqlandi!", reply_markup=admin_menu_button())
    await state.clear()
    await state.set_state(AdminState.invalid_password)


@admin_router.message(AdminState.menu_panel, F.text == logout)
async def logout_admin(message: Message, state: FSMContext):
    await state.clear()
    btns = [buy, my_order, product_info, question, free_consultation, settings]
    markab = reply_button(btns)
    await message.answer(main_menu, reply_markup=markab)
    await state.set_state(AdminState.logout_admin)


@admin_router.message(AdminState.menu_panel, F.text == price_exchange)
async def price_exchange_admin(message: Message, state: FSMContext):
    await  message.answer(correct_form_to_pay,reply_markup=reply_button([back]))
    await state.set_state(AdminState.change_prise)



@admin_router.message(AdminState.change_prise, F.text)
async def change_prise(message: Message, state: FSMContext):

    if len(message.text) > 4:
        async with async_session_maker() as session:
            admin = await session.get(Admin, message.from_user.id)
        try:
            price = int(message.text)
            admin.product_price = price
        except ValueError:
            await message.answer("❌ Xato kiritdingiz. Iltimos, son kiriting.")
            return
        await session.commit()
        await message.answer(successful)
        await state.set_state(AdminState.menu_panel)
        await message.answer(welcome_admin, reply_markup=admin_menu_button())
    else:
        await message.answer(in_valid_digit)

@admin_router.message(AdminState.menu_panel, F.text==message_all)
async def get_message_for_users(message: Message, state: FSMContext):
    await message.answer(input_message)
    await state.set_state(AdminState.message_all_state)

@admin_router.message(AdminState.message_all_state)
async def message_all(message: Message, state: FSMContext):
    sent_count = 0
    async with async_session_maker() as session:
        result = await session.execute(select(Customer.id))
        user_ids = result.scalars().all()

    tasks = []
    for i, user_id in enumerate(user_ids, 1):
        tasks.append(send_to_user(bot, user_id, message))
        if i % BATCH_SIZE == 0:
            await asyncio.gather(*tasks)
            sent_count += len(tasks)
            tasks.clear()
            await asyncio.sleep(0.2)
    if tasks:
        await asyncio.gather(*tasks)
        sent_count += len(tasks)
    await message.answer(f"✅ {sent_count} ta foydalanuvchiga xabar yuborildi.")
    await state.set_state(AdminState.menu_panel)
    await message.answer(main_menu_back, reply_markup=admin_menu_button())






