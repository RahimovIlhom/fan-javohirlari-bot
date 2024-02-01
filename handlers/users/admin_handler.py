from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile, ReplyKeyboardRemove

from data.config import ADMINS
from keyboards.default import menu_markup
from loader import dp, db, bot
from utils.misc.write_excel import write_data_excel


@dp.message_handler(text="O'quvchilar ro'yxati", user_id=ADMINS)
async def show_users_excel(msg: types.Message):
    columns = await db.select_column_names()
    users = await db.select_users()
    await write_data_excel(columns, users)
    file = InputFile(path_or_bytesio="data/users/data.xlsx")
    await msg.answer_document(file, caption="Barcha o'quvchilar ro'yxati!")


@dp.message_handler(text="Xabar yuborish", user_id=ADMINS)
async def show_users_excel(msg: types.Message, state: FSMContext):
    await msg.answer("Barcha o'quvchilar uchun xabarni kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state('send_message')


@dp.message_handler(user_id=ADMINS, state='send_message')
async def send_msg_to_all_users(msg: types.Message, state: FSMContext):
    users = await db.select_users()
    for user in users:
        try:
            await bot.send_message(user[1], msg.text)
        except Exception as e:
            print(f"Failed to send message to user {user[1]}: {e}")
    await msg.answer("Xabar barcha foydalanuvchilarga yuborildi!", reply_markup=menu_markup)
    await state.finish()
