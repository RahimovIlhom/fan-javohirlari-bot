from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import ReplyKeyboardRemove, InputFile

from data.config import ADMINS, CHANNELS
from filters import IsPrivate
from keyboards.default import language_markup, menu_markup, menu_test_ru, menu_test_uz
from keyboards.inline.checksubs import make_check_channels_subs
from loader import dp, db, bot
from states import RegisterStatesGroup, PINFLStateGroup
from utils.misc import subscription


@dp.message_handler(CommandStart(), IsPrivate(), state='*')
async def bot_start(message: types.Message, state: FSMContext):
    if str(message.from_user.id) in ADMINS:
        await message.answer("Menu", reply_markup=menu_markup)
        await state.finish()
        return
    user = await db.select_user(message.from_user.id)
    if user:
        if user[-1] is None:
            if user[2] == 'uzbek':
                result = "⚠️ Botdan foydalanish JSHSHIR (PINFL) raqamingizni kiriting:"
            else:
                result = "⚠️ Введите свой номер ИНН (PINFL) для использования ботом:"
            image = InputFile('data/images/jshshir.jpg')
            await message.answer_photo(image, caption=result, reply_markup=ReplyKeyboardRemove())
            await state.set_data({'language': user[2]})
            await PINFLStateGroup.pinfl.set()
            return
        if user[2] == 'uzbek':
            await message.answer("Test topshirish uchun quyidagi tugmadan foydalaning 👇", reply_markup=menu_test_uz)
        else:
            await message.answer("Используйте кнопку ниже, чтобы пройти тест 👇", reply_markup=menu_test_ru)
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
        await state.set_data({'re_register': True})
        await msg.answer("Iltimos, tilni tanlang.\n\n"
                         "Пожалуйста, выберите язык.", reply_markup=language_markup)
        await state.set_state(RegisterStatesGroup.language)
    else:
        await msg.answer("Siz hali ro'yxatdan o'tmagansiz.\n"
                         "Ro'yxatdan o'tish uchun - /start\n\n"
                         "Вы еще не зарегистрировались.\nДля регистрации - /start")


@dp.message_handler(state=PINFLStateGroup.pinfl)
async def add_pinfl_user(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language')
    if language == 'uzbek':
        if len(msg.text) != 14:
            await msg.answer("JSHSHIR (PINFL) to'g'ri kiritilmadi!\nIltimos qayta kiriting:")
            return
        if not msg.text.isnumeric():
            await msg.answer("JSHSHIR (PINFL) faqat raqamlardan tashkil topadi!\nIltimos qayta kiriting:")
            return
        info = "Ma'lumot saqlandi.\nTest topshirish uchun quyidagi tugmadan foydalaning 👇"
        markup = menu_test_uz
    else:
        if len(msg.text) != 14:
            await msg.answer("Номер ИНН (PINFL) введен неправильно!\nПожалуйста, введите еще раз:")
            return
        if not msg.text.isnumeric():
            await msg.answer("Номер ИНН (PINFL) должен состоять только из цифр!\nПожалуйста, введите еще раз:")
            return
        info = "Информация сохранена.\nИспользуйте кнопку ниже, чтобы пройти тест 👇"
        markup = menu_test_ru
    await db.update_pinfl(msg.from_user.id, msg.text)
    await msg.answer(info, reply_markup=markup)
    await state.finish()


@dp.callback_query_handler(text="check_subs", state='*')
async def checker(call: types.CallbackQuery):
    await call.answer()
    user = await db.select_user(call.from_user.id)
    result = str()
    channels = []
    final_status = True
    for channel in CHANNELS:
        status = await subscription.check(user_id=call.from_user.id,
                                          channel=channel)
        channel = await bot.get_chat(channel)
        final_status *= status
        if not status:
            channels.append(channel)
            if user[2] == 'uzbek':
                result += f"ℹ️ <b>{channel.title}</b> kanaliga obuna bo'lmagansiz!\n\n"
            else:
                result += f"ℹ️ Вы не подписаны на канал <b>{channel.title}</b>!\n\n"
    await call.message.delete()
    if final_status:
        if user[2] == 'uzbek':
            result = "✅ Barcha kanallarga a'zo bo'ldingiz!"
        else:
            result = "✅ Вы подписались на все каналы!"
        await call.message.answer(result, disable_web_page_preview=True)
        return
    if user[2] == 'uzbek':
        result += "⚠️ Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:\n"
    else:
        result += "⚠️ Подпишитесь на следующие каналы для использования бота:\n"
    await call.message.answer(result, reply_markup=await make_check_channels_subs(channels, lang=user[2]),
                              disable_web_page_preview=True)
