from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


async def menu_user_markup(user_id):
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='🏆 YANGI OLIMPIADA')],
        ],
        resize_keyboard=True
    )
    markup.row(KeyboardButton(text="📥 Sertifikatni yuklab olish"))
    markup.row(KeyboardButton(text='📊 Reyting'))
    return markup


menu_test_ru = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='🏆 НОВАЯ ОЛИМПИАДА')],
        [KeyboardButton(text='📥 Скачать сертификат')],
        [KeyboardButton(text='📊 Рейтинг')],
    ],
    resize_keyboard=True
)
