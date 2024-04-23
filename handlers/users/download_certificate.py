import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile, ReplyKeyboardRemove

from filters import IsPrivate
from keyboards.default import menu_test_uz
from loader import dp, db
from utils.misc.create_certificate import create_certificate


@dp.message_handler(IsPrivate(), text="📥 Sertifikatni yuklab olish")
async def download_certificate(msg: types.Message, state: FSMContext):
    tg_id = msg.from_user.id
    user = await db.select_user(tg_id)
    test_result = await db.select_result_test_user(tg_id, user[8], True)
    if test_result:
        responses = test_result[9]
        result = responses.count('1') / len(responses)
        image_index = (2 if result >= 0.85 else 1 if result >= 0.65 else 0) if result > 0.33 else 3
        await state.set_data({'id': tg_id, 'science': user[8], 'image_index': image_index})
        await msg.answer("Ism-familiyangizni kiriting(Ushbu ism-familiya sertifikatingizda nashr qilinadi❗️):",
                         reply_markup=ReplyKeyboardRemove())
        await state.set_state('set_name')
    else:
        await msg.reply("Sizda sertifikat mavjud emas❗️")


@dp.message_handler(state='set_name')
async def set_name_func(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    fullname = msg.text
    user_id = data.get('id')
    image_index = data.get('image_index')
    science = data.get('science')
    cer_path = await create_certificate(user_id, image_index, fullname, science)
    if cer_path:
        await msg.answer_photo(InputFile(cer_path), caption="Sizning sertifikatingiz!", reply_markup=menu_test_uz)
        os.remove(cer_path) if os.path.exists(cer_path) else None
    else:
        await msg.answer("Error certificate create", reply_markup=menu_test_uz)
    await state.reset_data()
    await state.finish()
