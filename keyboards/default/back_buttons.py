from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


back_uz_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='⬅️ Orqaga')],
    ],
    resize_keyboard=True
)

back_ru_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='⬅️ Назад')],
    ],
    resize_keyboard=True
)
