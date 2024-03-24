from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


menu_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📃 O'quvchilar ro'yxati"),
            KeyboardButton(text="✉️ Xabar yuborish")
        ],
        [
            KeyboardButton(text="📚 Test bo'limi"),
            KeyboardButton(text="📊 Test natijalari")
        ],
        [
            KeyboardButton(text="🏆 Olimpiada bo'limi"),
            KeyboardButton(text="📈 Olimpiada natijalari")
        ],
    ],
    resize_keyboard=True
)


tests_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📓 Fanlar bo'yicha testlar"),
            KeyboardButton(text="➕ Yangi test ochish")
        ],
        [
            KeyboardButton(text="⬅️ Orqaga")
        ]
    ],
    resize_keyboard=True
)


olympiad_tests_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📓 Olimpiada testlari"),
            KeyboardButton(text="➕ Olimpiada testi ochish")
        ],
        [
            KeyboardButton(text="⬅️ Orqaga")
        ]
    ],
    resize_keyboard=True
)
