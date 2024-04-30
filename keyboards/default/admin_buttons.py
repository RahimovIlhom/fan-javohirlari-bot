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
        [
            KeyboardButton(text="🏆 Olimpiada (2-bosqich) bo'limi")
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

next_level_olympiad_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📅 2-bosqich Olimpiada kunlari"),
        ],
        [
            KeyboardButton(text="📃 2-bosqich Olimpiadistlar ro'yxati"),
        ],
        [
            KeyboardButton(text="✉️ 2-bosqich Olimpiadistlar xabar yuborish"),
        ],
        [
            KeyboardButton(text="⬅️ Orqaga")
        ]
    ],
    resize_keyboard=True
)
