
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def call_with_admin():
    ikb = InlineKeyboardBuilder()
    ikb.add(InlineKeyboardButton(text='admin', url='https://t.me/shaxob_x'),
    )
    ikb.adjust(1)
    return ikb.as_markup()
def search_inline_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❓ Savol berish",
                    switch_inline_query_current_chat=""
                )
            ]
        ]
    )