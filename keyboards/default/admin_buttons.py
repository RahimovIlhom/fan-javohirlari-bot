from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


menu_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="O'quvchilar ro'yxati"),
            KeyboardButton(text="Xabar yuborish")
        ],
    ],
    resize_keyboard=True
)
