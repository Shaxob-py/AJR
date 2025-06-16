from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.teksts.teksts import spend_number, back, phone_change, name, data, change_password, price_exchange, message_all, \
    all_users, all_payments, all_daily


def reply_button(buttons):
    rkb = ReplyKeyboardBuilder()
    rkb.add(*[KeyboardButton(text=btn) for btn in buttons])
    size = [3, 2, ]
    rkb.adjust(*size)
    return rkb.as_markup(resize_keyboard=True)


def phone_number():
    rkb = ReplyKeyboardBuilder()
    rkb.add(KeyboardButton(text=spend_number, request_contact=True),
            KeyboardButton(text=back))
    size = [1]
    rkb.adjust(*size)
    return rkb.as_markup(resize_keyboard=True)


def location_button():
    rkb = ReplyKeyboardBuilder()
    rkb.add(KeyboardButton(text='Location', request_location=True),
            KeyboardButton(text=back))
    size = [1]
    rkb.adjust(*size)
    return rkb.as_markup(resize_keyboard=True)


def settings_button():
    rkb = ReplyKeyboardBuilder()
    rkb.add(
        KeyboardButton(text=phone_change, request_contact=True),
        KeyboardButton(text=name),
        KeyboardButton(text=back))
    size = [1]
    rkb.adjust(*size)
    return rkb.as_markup(resize_keyboard=True)


def admin_menu_button():
    rkb = ReplyKeyboardBuilder()
    rkb.add(KeyboardButton(text=data),
            KeyboardButton(text=change_password),
            KeyboardButton(text=price_exchange),
            KeyboardButton(text=message_all),
            )
    size = [1 ]
    rkb.adjust(*size)
    return rkb.as_markup(resize_keyboard=True)


def choice_data_button():
    rkb = ReplyKeyboardBuilder()
    rkb.add(KeyboardButton(text=all_users),
            KeyboardButton(text=all_payments),
            KeyboardButton(text=all_daily),
            KeyboardButton(text=back)
            )
    size = [1 ]
    rkb.adjust(*size)
    return rkb.as_markup(resize_keyboard=True)