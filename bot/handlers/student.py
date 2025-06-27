from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, InlineQueryResultArticle, InlineQuery, InputTextMessageContent
from aiogram.types import LabeledPrice, PreCheckoutQuery
from sqlalchemy.orm import joinedload

from bot.main import bot
from db.manager import insert_users_if_not_exist
from db.manager import location_funk, update_user_contact
from db.models import Customer, async_session_maker, Payment, DailyPayment, DailyInfo, Admin
from bot.teksts.question import faq_lists
from bot.despecher.state import CustomerState
from bot.keys.inliny import search_inline_keyboard
from bot.keys.reply import reply_button, phone_number, location_button, settings_button
from bot.teksts.teksts import back, buy, question, free_consultation, settings, start, phone, confirmation, \
    location_spend, \
    pay, \
    main_menu_back, change, name, spend_name, successful, get_question, pay_later, product_info, my_order, create_at, \
    product_not_found, paid, main_menu
from decimal import Decimal
from bot.despecher import config
from sqlalchemy.future import select

dp = Dispatcher()
PAYMENT_PROVIDER_TOKEN = config.PAYMENT_PROVIDER_TOKEN

@dp.message(Command("start"))
async def command_start_handler(message: Message, state: FSMContext) -> None:
    btns = [buy, my_order, product_info, question, free_consultation, settings]
    markup = reply_button(btns)
    await message.answer_photo(
        photo="AgACAgQAAxkBAAECqDtoTbsXxEYoXE092i4gJDLY1DE6IwACmrkxG7oZDFLF4sI0k19HyQEAAwIAA3MAAzYE",
        caption=start,
        reply_markup=markup)
    data = await state.get_data()
    register = data.get('register')


    if register is None:
        user_id: int = message.from_user.id
        username = message.from_user.username
        name = message.from_user.first_name
        await insert_users_if_not_exist(user_id, name, username)
        await state.update_data(register=True)


@dp.message(CustomerState.consultation_state, F.text == back)
@dp.message(CustomerState.pay_state, F.text ==main_menu_back )
@dp.message(CustomerState.settings_state, F.text == back)
@dp.message(CustomerState.phone_state, F.text == back)
async def menu_handler(message: Message) -> None:
    btns = [buy, my_order, product_info, question, free_consultation, settings]
    markup = reply_button(btns)
    await message.answer(main_menu,reply_markup=markup)

@dp.message(F.text == product_info)
async def product_info_handler(message: Message) -> None:
    await message.answer_video(video='BAACAgIAAxkBAAECqAdoSsFji9EO-FpLaKfHrXOTuWHsxQACiW4AAisxWEr1l7RzQdW3oTYE',
                               caption='''📌 Xulosa
Ajr Qora Sedana — bu tabiiy qora sedana yog‘i asosida yaratilgan bo‘lib, turli sog‘liq muammolariga yordam beradi. Mahsulot halal sertifikatli, tabiiy, va ijtimoiy maqsadli (xayriya + Umra). Sotib oluvchilar mahsulotdan foydalanib, jismoniy salomatlik va ijtimoiy ehsonni birdaniga tanlaydi.

Agar siz ham uni sinab ko‘rmoqchi bo‘lsangiz yoki buyurtma bermoqchi bo‘lsangiz, yuqoridagi telefonlar orqali bog‘lanishingiz mumkin.

Yana savollaringiz bo‘lsa, bemalol yozing!''')


@dp.message(F.text == question)
async def question_handler(message: Message) -> None:
    await message.answer(get_question, reply_markup=search_inline_keyboard())


@dp.inline_query()
async def inline_query_handler(inline_query: InlineQuery):
    query = inline_query.query.lower()
    result = []

    for faq in faq_lists:
        if query in faq.get('question', '').lower():
            i = InlineQueryResultArticle(
                id=str(faq.get('id')),
                title=faq.get('question'),
                description="Javobni olish uchun bosing",
                input_message_content=InputTextMessageContent(
                    message_text=faq.get('id')
                ),
                thumb_url=faq.get('thumb_url', "")
            )
            result.append(i)

    if not result:
        result.append(
            InlineQueryResultArticle(
                id="not_found",
                title="Savol topilmadi",
                description="Bunday savol topilmadi.",
                input_message_content=InputTextMessageContent(
                    message_text="❌ Savol topilmadi."
                )
            )
        )

    # !!! To'g'ri joy — sikldan keyin javob berish
    await inline_query.answer(result, cache_time=5, is_personal=True)


@dp.message(F.via_bot)
async def chosen_result_handler(message: Message):
    question_id = message.text.strip()
    question = next((q for q in faq_lists if str(q.get("id")) == question_id), None)

    if question:
        caption = f"🧠 <b>Javob:</b>\n{question['answer']}"
        try:
            await message.delete()
        except:
            pass

        await message.answer(caption, parse_mode="HTML")


@dp.message(F.text == free_consultation)
async def admin_handler(message: Message, state: FSMContext):
    await message.answer(phone, reply_markup=phone_number())
    await state.set_state(CustomerState.consultation_state)


@dp.message(F.contact, CustomerState.consultation_state)
async def contact_handler(message: Message, state: FSMContext):
    async with async_session_maker() as session:
        new_daily_info = DailyInfo(
            phone_number=message.contact.phone_number,
                user_id  = message.from_user.id,)
        session.add(new_daily_info)
        await session.commit()
        await state.clear()
        btns = [buy, my_order, product_info, question, free_consultation, settings]
        markup = reply_button(btns)
        await message.answer(successful, reply_markup=markup)


@dp.message(F.text == settings)
async def buy_handler(message: Message, state: FSMContext):
    markup = settings_button()
    await state.set_state(CustomerState.settings_state)
    await message.answer(change, reply_markup=markup)


@dp.message(CustomerState.settings_state, F.text == name)
async def name_change_handler(message: Message, state: FSMContext):
    await message.answer(spend_name, reply_markup=ReplyKeyboardRemove())
    await state.set_state(CustomerState.change_name)


@dp.message(CustomerState.change_name, F.text)
async def change_name_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    async with async_session_maker() as session:
        user = await session.get(Customer, user_id)
        if user is None:
            await message.answer('/start')
            return
        user.name = message.text
        await session.commit()
        await state.clear()
        btns = [buy, my_order, product_info, question, free_consultation, settings]
        markup = reply_button(btns)
        await message.answer(successful, reply_markup=markup)


@dp.message(CustomerState.settings_state, F.contact)
async def settings_handler(message: Message):
    await update_user_contact(message)
    btns = [buy, my_order, product_info, question, free_consultation, settings]
    markup = reply_button(btns)
    await message.answer(successful, reply_markup=markup)


@dp.message(CustomerState.location, F.text == "yoq")
@dp.message(F.text == back, CustomerState.location_state)
@dp.message(F.text == buy)
async def buy_handler(message: Message, state: FSMContext):
    await state.update_data(id=message.from_user.id)
    await message.answer(phone, reply_markup=phone_number())
    await state.set_state(CustomerState.phone_state)


@dp.message(F.contact, CustomerState.phone_state)
async def location_handler(message: Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await message.answer(location_spend, reply_markup=location_button())
    await state.set_state(CustomerState.location_state)


@dp.message(F.location)
async def location_handler(message: Message, state: FSMContext):
    await location_funk(message)
    await state.update_data(latitude=message.location.latitude, longitude=message.location.longitude)
    await message.answer(confirmation, reply_markup=reply_button(['xa', 'yoq']))
    await state.set_state(CustomerState.location)


@dp.message(CustomerState.location, F.text == "xa")
async def yes_location_handler(message : Message,state: FSMContext):
    markup = reply_button([pay, pay_later,main_menu ])
    await state.set_state(CustomerState.pay_state)
    await message.answer('✅', reply_markup=markup)


@dp.message(CustomerState.pay_state, F.text == pay_later)
async def pay_later_handler(message: Message, state: FSMContext):
    data = await state.get_data()  # noqa
    phone_ = data.get('phone')
    user_id = data.get('id')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    async with async_session_maker() as session:
        new_payment = Payment(
            location=f'{latitude}, {longitude}',
            phone_number=phone_,
            user_id=user_id,
            status="processing",
            pay=0  # noqa
        )
        session.add(new_payment)
        await session.commit()
        btns = [buy, my_order, product_info, question, free_consultation, settings]
        markup = reply_button(btns)
        await message.answer("✅ To‘lov muvaffaqiyatli amalga oshirildi. Rahmat!", reply_markup=markup)


@dp.message(CustomerState.pay_state, F.text == pay)
async def pay_handler(message: Message):
    await message.answer('Tolov uchun ', reply_markup=ReplyKeyboardRemove())
    async with async_session_maker() as session:
        result = await session.execute(select(Admin))
        admin = result.scalar()
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Qora sedana",
        description="Qora sedana 1 dona",
        payload="products",
        provider_token=config.PAYMENT_PROVIDER_TOKEN,
        currency="UZS",
        prices=[LabeledPrice(label="Qora sedana", amount=admin.product_price * 100)],
        start_parameter="premium-subscription"
    )


@dp.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(True)


@dp.message(F.successful_payment)
async def successful_payment(message: Message, state: FSMContext):
    if message.successful_payment.invoice_payload == "products":
        btns = [buy, my_order, product_info, question, free_consultation, settings]
        markup = reply_button(btns)
        await message.answer("✅ To‘lov muvaffaqiyatli amalga oshirildi. Rahmat!", reply_markup=markup)
        data = await state.get_data()
        phone_ = data.get('phone')
        user_id = data.get('id')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        amount = Decimal(message.successful_payment.total_amount) / 100

        async with async_session_maker() as session:
            new_payment = Payment(
                location=f'{latitude}, {longitude}',
                phone_number=phone_,
                user_id=user_id,
                status="paid",
                pay=amount  # noqa
            )
            new_daily_payment = DailyPayment(
                location=f'{latitude}, {longitude}',
                phone_number=phone_,
                user_id=user_id,
                status="paid",
                pay=amount  # noqa
            )

            session.add(new_payment)
            session.add(new_daily_payment)
            await session.commit()
    else:
        await message.answer("⚠️ To‘lovda xatolik yuz berdi.")


@dp.message(F.text == my_order)
async def my_orders(message: Message):
    async with async_session_maker() as session:
        result = await session.execute(
            select(Payment)
            .options(joinedload(Payment.user))  # ⏩ JOIN bilan yuklash
            .where(Payment.user_id == message.from_user.id)
        )
        payments = result.scalars().all()
        if payments:
            text = f"{create_at}        {paid}\n"
            for payment in payments:
                text += f" {payment.paid.strftime('%Y-%m-%d %H:%M')}            {payment.pay} so'm\n"
            await message.answer(text)
        else:
            await message.answer(product_not_found)
