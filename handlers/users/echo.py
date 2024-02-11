from aiogram import types

from data.config import ADMINS
from keyboards.default import menu_markup
from loader import dp


@dp.message_handler(state=None, user_id=ADMINS)
async def bot_echo(message: types.Message):
    if message.text == "⬅️ Orqaga":
        await message.answer("Menu", reply_markup=menu_markup)
        return
    await message.answer(message.text)


@dp.message_handler(state=None)
async def bot_echo(message: types.Message):
    await message.answer(message.text)
