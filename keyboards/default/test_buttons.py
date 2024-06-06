from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


async def menu_user_markup(user_id):
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='🏆 SINOV TEST IMTIHONI')],
        ],
        resize_keyboard=True
    )
    markup.row(KeyboardButton(text="📥 Sertifikatni yuklab olish"))
    markup.row(KeyboardButton(text='📊 Reyting'))
    return markup


menu_test_ru = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='🏆 ЭКЗАМЕНАЦИОННЫЙ ТЕСТ')],
        [KeyboardButton(text='📥 Скачать сертификат')],
        [KeyboardButton(text='📊 Рейтинг')],
    ],
    resize_keyboard=True
)
