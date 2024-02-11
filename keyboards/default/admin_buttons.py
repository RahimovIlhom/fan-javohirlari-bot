from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


menu_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📃 O'quvchilar ro'yxati"),
            KeyboardButton(text="✉️ Xabar yuborish")
        ],
        [
            KeyboardButton(text="📥 Test qo'shish"),
            KeyboardButton(text="📊 Test natijalari")
        ]
    ],
    resize_keyboard=True
)
