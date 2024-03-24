from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


download_certificate_markup_uz = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Sertifikatni yuklab olish", callback_data='download_certificate')],
    ],
)

download_certificate_markup_ru = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Скачать сертификат", callback_data='download_certificate')],
    ],
)
