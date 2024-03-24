from aiogram import types

from data.config import ADMINS
from keyboards.default import menu_markup, menu_test_uz, menu_test_ru
from loader import dp, db


@dp.message_handler(state=None, user_id=ADMINS)
async def bot_echo(message: types.Message):
    if message.text == "⬅️ Orqaga":
        await message.answer("Menu", reply_markup=menu_markup)
        return
    await message.answer(message.text)


@dp.message_handler(state=None)
async def bot_echo(message: types.Message):
    if message.text in ['⬅️ Orqaga', "⬅️ Назад"]:
        user = await db.select_user(message.from_user.id)
        if user[2] == 'uzbek':
            info = "Test topshirib ko’rish uchun quyidagi tugmani bosing."
            markup = menu_test_uz
        else:
            info = "Чтобы попробовать пройти тест, нажмите кнопку ниже."
            markup = menu_test_ru
        await message.answer(info, reply_markup=markup)
        return
    await message.answer(message.text)
