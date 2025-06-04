
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def call_with_admin():
    ikb = InlineKeyboardBuilder()
    ikb.add(InlineKeyboardButton(text='admin', url='https://t.me/shaxob_x'),
    )
    ikb.adjust(1)
    return ikb.as_markup()