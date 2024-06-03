import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile, ReplyKeyboardRemove

from filters import IsPrivate
from keyboards.default import menu_user_markup
from loader import dp, db
from utils.misc.create_certificate.create_certificate import create_certificate_new_olympiad


@dp.message_handler(IsPrivate(), text=["📥 Sertifikatni yuklab olish", "📥 Скачать сертификат"])
async def download_certificate(msg: types.Message, state: FSMContext):
    tg_id = msg.from_user.id
    test_result = await db.select_result_olympiad_user(tg_id)
    if test_result:
        responses = test_result[4]
        result = responses.count('1') / len(responses)
        if result >= 0.7:
            await state.set_data({'id': tg_id, 'science': test_result[3]})
            await msg.answer("Ism-familiyangizni kiriting:\n(Ushbu ism-familiya sertifikatingizda nashr qilinadi❗️):",
                             reply_markup=ReplyKeyboardRemove())
            await state.set_state('set_name')
            return
    if msg.text == "📥 Sertifikatni yuklab olish":
        await msg.reply("Sizda sertifikat mavjud emas❗️")
    else:
        await msg.reply("У вас нет сертификата❗️")


@dp.message_handler(state='set_name')
async def set_name_func(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    fullname = msg.text
    user_id = data.get('id')
    science = data.get('science')
    cer_path = await create_certificate_new_olympiad(user_id, fullname, science)
    if cer_path:
        await msg.answer_photo(InputFile(cer_path), caption="Sizning sertifikatingiz!",
                               reply_markup=await menu_user_markup(msg.from_user.id))
        os.remove(cer_path) if os.path.exists(cer_path) else None
    else:
        await msg.answer("Error certificate create", reply_markup=await menu_user_markup(msg.from_user.id))
    await state.reset_data()
    await state.finish()


@dp.message_handler(IsPrivate(), text=["📊 Reyting", "📊 Рейтинг"])
async def download_certificate(msg: types.Message):
    tg_id = msg.from_user.id
