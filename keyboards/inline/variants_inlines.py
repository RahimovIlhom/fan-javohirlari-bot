from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


variants = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="A", callback_data='1'),
            InlineKeyboardButton(text="B", callback_data='2'),
        ],
        [
            InlineKeyboardButton(text="C", callback_data='3'),
            InlineKeyboardButton(text="D", callback_data='4')
        ],
    ],
)
