from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


start_test_markup_uz = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Testni boshlash", callback_data='start_test')],
    ],
    row_width=1
)


start_test_markup_ru = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Начать тест", callback_data='start_test')],
    ],
    row_width=1
)
