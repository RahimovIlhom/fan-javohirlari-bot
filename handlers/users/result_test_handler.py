import time

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove, InputFile, ContentType

from data.config import ADMINS, sciences_uz
from filters import IsPrivate
from keyboards.default import sciences_uz_markup, menu_markup
from keyboards.inline import day_tests_markup
from loader import dp, db
from states import ResultTestStatesGroup
from utils.misc.write_excel import write_data_excel


@dp.message_handler(IsPrivate(), text="📊 Test natijalari", user_id=ADMINS)
async def result_test(msg: types.Message, state: FSMContext):
    await msg.answer("Qaysi fan bo'yicha test natijasini olmoqchisiz?",
                     reply_markup=sciences_uz_markup)
    await state.set_state(ResultTestStatesGroup.science)


@dp.message_handler(state=ResultTestStatesGroup.science, text='⬅️ Orqaga')
async def back_base_menu(msg: types.Message, state: FSMContext):
    await msg.answer("Menu", reply_markup=menu_markup)
    await state.reset_data()
    await state.finish()


@dp.message_handler(state=ResultTestStatesGroup.science, user_id=ADMINS)
async def result_test_science(msg: types.Message, state: FSMContext):
    if msg.text not in sciences_uz:
        await msg.delete()
        await msg.answer("‼️ Iltimos, quyidagi tugmalardan foydalaning!", reply_markup=sciences_uz_markup)
        return
    test_app = await db.select_test(msg.text)
    if test_app is False:
        await msg.answer("Hali test mavjud emas!")
        return
    await state.set_data({'science': msg.text})
    await msg.answer(msg.text, reply_markup=ReplyKeyboardRemove())
    await msg.answer("Qaysi kundagi test natijasini ko'rmoqchisiz?",
                     reply_markup=await day_tests_markup(msg.text))
    await ResultTestStatesGroup.next()


@dp.callback_query_handler(state=ResultTestStatesGroup.time, text='back')
async def back_base_menu(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer("Qaysi fan bo'yicha test natijasini olmoqchisiz?", reply_markup=sciences_uz_markup)
    await ResultTestStatesGroup.previous()


@dp.callback_query_handler(state=ResultTestStatesGroup.time)
async def send_test_result_excel(call: types.CallbackQuery, state: FSMContext):
    test_id = call.data
    columns = list(await db.select_test_result_column_names())
    # ['id', 'tg_id', 'language', 'fullname', 'phone_number', 'region', 'district', 'school_number',
    # 'science', 'responses', 'result_time', 'test_id', 'pinfl', 'certificate_image']
    result = await db.select_test_result(test_id)
    columns.pop()
    columns.pop()
    columns.pop(-2)
    columns.append('pinfl')
    test = await db.select_test_id(test_id)
    for i in range(1, test[4]+1):
        columns.append(f"{i}")
    new_result = []
    for user_result in result:
        user_result = list(user_result)
        pinfl = user_result.pop()
        pinfl = pinfl if pinfl else '-'
        user_result.pop()
        responses = user_result.pop(-2)
        user_result.append(pinfl)
        for res in responses:
            user_result.append(res)
        new_result.append(user_result)
    await write_data_excel(columns, new_result, file_path=test[2])
    file = InputFile(path_or_bytesio=f"data/users/{test[2]}.xlsx")
    await call.message.answer_document(file, caption="Barcha o'quvchilar ro'yxati!")


@dp.message_handler(state=ResultTestStatesGroup.time, content_types=ContentType.ANY)
async def err_send_result(msg: types.Message, state: FSMContext):
    await msg.delete()
    message = await msg.answer("‼️ Iltimos, yuqoridagi tugmalardan foydalaning!")
    time.sleep(2)
    await message.delete()
