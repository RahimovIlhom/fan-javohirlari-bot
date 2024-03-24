from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


menu_test_uz = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='🏆 OLIMPIADA (1-bosqich)')],
        [KeyboardButton(text='👨‍💻 TEST TOPSHIRISH')],
    ],
    resize_keyboard=True
)

menu_test_ru = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='🏆 ОЛИМПИАДА (1-й этап)')],
        [KeyboardButton(text='👨‍💻 ПРОЙТИ ТЕСТ')],
    ],
    resize_keyboard=True
)
