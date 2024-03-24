import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import ReplyKeyboardRemove, InputFile, ContentType

from data.config import ADMINS, CHANNELS
from filters import IsPrivate
from keyboards.default import language_markup, menu_markup, menu_test_ru, menu_test_uz
from keyboards.inline.checksubs import make_check_channels_subs
from loader import dp, db, bot
from states import RegisterStatesGroup, PINFLStateGroup
from utils.misc import subscription
from utils.misc.create_certificate import create_certificate, photo_link


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
                result = "⚠️ Botdan foydalanish uchun ID-kartangizdagi Shaxsiy raqamingizni kiriting:"
                image = InputFile('data/images/pinfl.jpg')
                image_url = "http://telegra.ph//file/97b3043fbcdc89ba48360.jpg"
            else:
                result = ("⚠️ Введите персональный идентификационный номер, указанный в вашем ID-карте, "
                          "чтобы воспользоваться ботом:")
                image = InputFile('data/images/pinfl_ru.jpg')
                image_url = "http://telegra.ph//file/e815e58a3c4c08948b617.jpg"
            try:
                await message.answer_photo(image_url, caption=result, reply_markup=ReplyKeyboardRemove())
            except:
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
            await msg.answer("Shaxsiy raqam to'g'ri kiritilmadi!\nIltimos qayta kiriting:")
            return
        if not msg.text.isnumeric():
            await msg.answer("Shaxsiy raqam faqat raqamlardan tashkil topadi!\nIltimos qayta kiriting:")
            return
        info = "Ma'lumot saqlandi.\nTest topshirish uchun quyidagi tugmadan foydalaning 👇"
        markup = menu_test_uz
    else:
        if len(msg.text) != 14:
            await msg.answer("Персональный идентификационный номер введен неверно!\nПожалуйста, введите еще раз:")
            return
        if not msg.text.isnumeric():
            await msg.answer("Персональный идентификационный номер должен состоять только из цифр!\nПожалуйста, "
                             "введите еще раз:")
            return
        info = "Информация сохранена.\nИспользуйте кнопку ниже, чтобы пройти тест 👇"
        markup = menu_test_ru
    await db.update_pinfl(msg.from_user.id, msg.text)
    await msg.answer(info, reply_markup=markup)
    await state.finish()


@dp.callback_query_handler(text="check_subs", state='*')
async def checker(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
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
    info_uz = (
        "Arizangiz qabul qilinishi uchun, iltimos, \"Fan javohirlari\" telegram kanaliga a'zo bo'ling. U yerda "
        "loyiha haqida ma'lumotlar, fanlar bo'yicha testlar va ularning javoblari, olimpiada o'tkazilish "
        "kunlari e'lon qilinib boriladi. Shu bilan birga, kanalda abituriyentlar uchun qiziq bo'lgan "
        "ma'lumotlar, talabalar hayoti, hajviy postlar berib boriladi.")
    success_uz = ("✅ Tabriklaymiz, siz ro'yxatdan o'tdingiz. O'zingizni sinab ko'rish uchun test topshirmoqchi "
                  "bo'lsangiz, quyidagi \"Test topshirish\" tugmasini bosing.")
    info_ru = (
        "Для того, чтобы вашу заявку приняли, пожалуйста, подпишитесь на Telegram-канал «Fan javohirlari». Там "
        "публикуется информация о проекте, тесты по разным предметам и   ответы на них, а также даты "
        "проведения олимпиады. Также на канале публикуется   интересная информация для абитуриентов, "
        "посты про студенческую жизнь, юмористические посты.")
    success_ru = ("✅ Поздравляем, теперь вы зарегистрированы! Если вы хотите пройти тест, чтобы проверить себя, "
                  "нажмите кнопку «Пройти тест».")
    if final_status:
        if user[2] == 'uzbek':
            result = success_uz if data.get('level') == 'registration' else "✅ Barcha kanallarga a'zo bo'ldingiz!"
            markup = menu_test_uz
        else:
            result = success_ru if data.get('level') == 'registration' else "✅ Вы подписались на все каналы!"
            markup = menu_test_ru
        await call.message.answer(result, reply_markup=markup, disable_web_page_preview=True)
        await state.reset_state()
        await state.finish()
        return
    if user[2] == 'uzbek':
        result += info_uz if data.get('level') == 'registration' else ("⚠️ Botdan foydalanish uchun quyidagi "
                                                                       "kanallarga obuna bo'ling:\n")
    else:
        result += info_ru if data.get('level') == 'registration' else ("⚠️ Подпишитесь на следующие каналы для "
                                                                       "использования бота:\n")
    await call.message.answer(result, reply_markup=await make_check_channels_subs(channels, lang=user[2]),
                              disable_web_page_preview=True)


# @dp.message_handler(content_types=[ContentType.TEXT, ContentType.PHOTO])
# async def send_cer(msg: types.Message):
#     image_path = await create_certificate(1234657, 2, 'Rahimov Ilhomjon Iqboljon o\'g\'li')
#     image_url = await photo_link(image_path)
#     print(image_url)
#     await msg.answer_photo(image_url, caption="Sertifikatingiz")
#     if os.path.exists(image_path):
#         os.remove(image_path)
