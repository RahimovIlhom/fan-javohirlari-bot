from aiogram import types
from aiogram.types import ReplyKeyboardRemove

from data.config import ADMINS
from filters import IsPrivate
from keyboards.default import menu_markup, menu_test_ru
from keyboards.default import menu_user_markup
from loader import dp, db


@dp.message_handler(IsPrivate(), state=None, user_id=ADMINS)
async def bot_echo(message: types.Message):
    if message.text == "⬅️ Orqaga":
        await message.answer("Menu", reply_markup=menu_markup)
        return
    await message.answer(message.text)


@dp.message_handler(IsPrivate(), state=None)
async def bot_echo(message: types.Message):
    user = await db.select_user(message.from_user.id)
    if user is None:
        await message.answer("‼️ Siz ro'yxatdan o'tmaganingiz uchun test topshira olmaysiz!\n"
                             "Ro'yxatdan o'tish uchun - /start", reply_markup=ReplyKeyboardRemove())
        return
    if user[2] == 'uzbek':
        markup = await menu_user_markup(message.from_user.id)
    else:
        markup = menu_test_ru
    await message.answer(message.text, reply_markup=markup)
