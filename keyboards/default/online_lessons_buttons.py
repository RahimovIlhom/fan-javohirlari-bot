from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from data.config import sciences_uz, sciences_ru


async def make_lessons_uz_markup(sc1=None, sc2=None, sc3=None):
    sciences = sciences_uz.copy()
    if sc1 != '-' and sc1:
        sciences.remove(sc1)
    if sc2 != '-' and sc2:
        sciences.remove(sc2)
    if sc3 != '-' and sc3:
        sciences.remove(sc3)
    sciences_uz_markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for science in sciences:
        sciences_uz_markup.insert(KeyboardButton(text=science))
    if sc1 is None:
        sciences_uz_markup.row(KeyboardButton(text="ONLAYN DARSLARDA ISHTIROK ETMAYMAN"))
    else:
        sciences_uz_markup.row(KeyboardButton(text="✅ Tanlab bo'ldim!"))
    sciences_uz_markup.row(KeyboardButton(text="⬅️ Orqaga"))
    return sciences_uz_markup


async def make_lessons_ru_markup(sc1=None, sc2=None, sc3=None):
    sciences = sciences_ru.copy()
    if sc1 != '-' and sc1:
        sciences.remove(sc1)
    if sc2 != '-' and sc2:
        sciences.remove(sc2)
    if sc3 != '-' and sc3:
        sciences.remove(sc3)
    sciences_ru_markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for science in sciences:
        sciences_ru_markup.insert(KeyboardButton(text=science))
    if sc1 is None:
        sciences_ru_markup.row(KeyboardButton(text="Я НЕ БУДУ УЧАСТВОВАТЬ В ОНЛАЙН-ЗАНЯТИЯХ"))
    else:
        sciences_ru_markup.row(KeyboardButton(text="✅ я выбрал!"))
    sciences_ru_markup.row(KeyboardButton(text="⬅️ Назад"))
    return sciences_ru_markup
