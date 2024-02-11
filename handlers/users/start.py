from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import ReplyKeyboardRemove

from data.config import ADMINS
from filters import IsPrivate
from keyboards.default import language_markup, menu_markup, menu_test_ru, menu_test_uz
from loader import dp, db
from states import RegisterStatesGroup


@dp.message_handler(CommandStart(), IsPrivate(), state='*')
async def bot_start(message: types.Message, state: FSMContext):
    if str(message.from_user.id) in ADMINS:
        await message.answer("Menu", reply_markup=menu_markup)
        await state.finish()
        return
    user = await db.select_user(message.from_user.id)
    if user:
        if user[2] == 'uzbek':
            await message.answer("✅ Siz muvaffaqiyatli ro'yxatdan o'tgansiz.\n"
                                 "Test topshirish uchun quyidagi tugmadan foydalaning 👇", reply_markup=menu_test_uz)
        else:
            await message.answer("✅ Вы успешно зарегистрировались.\n"
                                 "Используйте кнопку ниже, чтобы пройти тест 👇", reply_markup=menu_test_ru)
        await state.finish()
        return
    await message.answer(f"Assalomu alaykum! \"Fan javohirlari\" loyihasining rasmiy botiga xush kelibsiz. "
                         f"Iltimos, tilni tanlang.\n\n"
                         f"Добро пожаловать в официальный бот проекта \"Fan javohirlari\". Пожалуйста, выберите язык.",
                         reply_markup=language_markup)
    await state.set_state(RegisterStatesGroup.language)


@dp.message_handler(IsPrivate(), commands=['re_register'])
async def re_register(msg: types.Message, state: FSMContext):
    if str(msg.from_user.id) in ADMINS:
        await msg.answer("Admin uchun ro'yxatdan o'tish shart emas!")
        return
    user = await db.select_user(msg.from_user.id)
    if user:
        await msg.answer("Iltimos, tilni tanlang.\n\n"
                         "Пожалуйста, выберите язык.", reply_markup=language_markup)
        await state.set_state(RegisterStatesGroup.language)
    else:
        await msg.answer("Siz hali ro'yxatdan o'tmagansiz.\n"
                         "Ro'yxatdan o'tish uchun - /start\n\n"
                         "Вы еще не зарегистрировались.\nДля регистрации - /start")
