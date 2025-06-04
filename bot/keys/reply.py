from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.teksts import spend_number, back


def start_button(buttons):
    rkb = ReplyKeyboardBuilder()
    rkb.add(*[KeyboardButton(text=btn) for btn in buttons])
    size = [3, 2,]
    rkb.adjust(*size)
    return rkb.as_markup(resize_keyboard=True)

def phone_number():
    rkb = ReplyKeyboardBuilder()
    rkb.add(KeyboardButton(text=spend_number,request_contact=True),
            KeyboardButton(text=back))
    size = [1]
    rkb.adjust(*size)
    return rkb.as_markup(resize_keyboard=True)


def location_button():
    rkb = ReplyKeyboardBuilder()
    rkb.add(KeyboardButton(text='Location',request_location=True),
            KeyboardButton(text=back))
    size = [1]
    rkb.adjust(*size)
    return rkb.as_markup(resize_keyboard=True)
