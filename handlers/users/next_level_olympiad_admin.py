import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile, ContentType, ReplyKeyboardRemove

from data.config import ADMINS, sciences_uz
from filters import IsPrivate
from keyboards.default import next_level_olympiad_menu, sciences_uz_markup, menu_markup
from keyboards.inline import next_level_olympiad_markup
from loader import dp, db, bot
from states import OlympiansListState
from utils.misc.write_excel_for_pandas import olympians_for_next_level_excel


@dp.message_handler(IsPrivate(), text="🏆 Olimpiada (2-bosqich) bo'limi", user_id=ADMINS)
async def next_level_olympiad(msg: types.Message):
    await msg.answer("Bo'limni tanlang:", reply_markup=next_level_olympiad_menu)


# @dp.message_handler(IsPrivate(), text="📅 2-bosqich Olimpiada kunlari", user_id=ADMINS)
# async def day_of_science_list(msg: types.Message, state: FSMContext):
#     await msg.answer("Qaysi fandan 2-bosqich Olimpiada kunini ko'rmoqchisiz?", reply_markup=sciences_uz_markup)
#     await state.set_state()


@dp.message_handler(IsPrivate(), text="📃 2-bosqich Olimpiadistlar ro'yxati", user_id=ADMINS)
async def olympians_list_for_science(msg: types.Message, state: FSMContext):
    await msg.answer("Qaysi fandan 2-bosqich Olimpiadistlar ro'yxati olmoqchisiz?",
                     reply_markup=sciences_uz_markup)
    await state.set_state(OlympiansListState.science)


@dp.message_handler(IsPrivate(), user_id=ADMINS, state=OlympiansListState.science)
async def choice_science_for_olympian_list(msg: types.Message, state: FSMContext):
    if msg.text == "⬅️ Orqaga":
        await msg.answer("Bo'limni tanlang:", reply_markup=next_level_olympiad_menu)
        await state.finish()
    elif msg.text in sciences_uz:
        excel_file_path = await olympians_for_next_level_excel(*await db.get_olympians_next_level(msg.text), msg.text)
        file = InputFile(path_or_bytesio=excel_file_path)
        await msg.answer_document(file, caption=f"{msg.text} fani bo'yicha 2-bosqich olimpiadistlar ro'yxati!")
        if os.path.exists(excel_file_path):
            os.remove(excel_file_path)
    else:
        await msg.answer("‼️ Iltimos quyidagi tugmalardan foydalaning.", reply_markup=sciences_uz_markup)


@dp.message_handler(IsPrivate(), text="✉️ 2-bosqich Olimpiadistlar xabar yuborish", user_id=ADMINS)
async def send_olympiad_users_message(msg: types.Message, state: FSMContext):
    await msg.answer("Xabarni kiriting.\n\n"
                     "‼️ xabar ostida \"🏆 OLIMPIADA (2-bosqich) UCHUN ARIZA\" tugmasi bo'ladi.",
                     reply_markup=ReplyKeyboardRemove())
    await state.set_state('send_message_next_olympiad_users')


@dp.message_handler(IsPrivate(), user_id=ADMINS, state='send_message_next_olympiad_users',
                    content_types=[ContentType.TEXT, ContentType.PHOTO])
async def send_olympiad_users_message(msg: types.Message, state: FSMContext):
    users = await db.select_next_level_users()
    photos = msg.photo
    if photos:
        photo_id = photos[-1].file_id
        for user in users:
            try:
                await bot.send_photo(user[0], photo=photo_id, caption=msg.caption,
                                     reply_markup=next_level_olympiad_markup)
            except Exception as e:
                print(f"Failed to send message to user {user[1]}: {e}")
    else:
        for user in users:
            try:
                await bot.send_message(user[0], msg.text, reply_markup=next_level_olympiad_markup)
            except Exception as e:
                print(f"Failed to send message to user {user[1]}: {e}")
    await msg.answer("Xabar 2-bosqich olimpiadachilarga yuborildi!", reply_markup=menu_markup)
    await state.finish()


