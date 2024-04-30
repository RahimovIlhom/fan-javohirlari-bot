from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from loader import db


async def menu_user_markup(user_id):
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='🏆 OLIMPIADA (1-bosqich)')],
        ],
        resize_keyboard=True
    )
    if not await db.get_next_olympiad_user(user_id):
        user_result = await db.select_result_user(user_id)
        if user_result:
            markup.row(KeyboardButton(text="🏆 OLIMPIADA (2-bosqich) UCHUN ARIZA"))
    markup.row(KeyboardButton(text="📥 Sertifikatni yuklab olish"))
    markup.row(KeyboardButton(text='👨‍💻 TEST TOPSHIRISH'))
    return markup


menu_test_ru = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='🏆 ОЛИМПИАДА (1-й этап)')],
        [KeyboardButton(text='👨‍💻 ПРОЙТИ ТЕСТ')],
    ],
    resize_keyboard=True
)
