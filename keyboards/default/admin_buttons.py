from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


menu_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📃 O'quvchilar ro'yxati"),
            KeyboardButton(text="✉️ Xabar yuborish")
        ],
        [
            KeyboardButton(text="📥 Test qo'shish uchun"),
            KeyboardButton(text="📊 Test natijalari")
        ]
    ],
    resize_keyboard=True
)


tests_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Fanlar bo'yicha testlar"),
            KeyboardButton(text="Yangi test ochish")
        ],
        [
            KeyboardButton(text="⬅️ Orqaga")
        ]
    ],
    resize_keyboard=True
)
