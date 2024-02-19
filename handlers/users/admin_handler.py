from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile, ReplyKeyboardRemove, ContentType

from data.config import ADMINS, sciences_uz
from filters import IsPrivate
from keyboards.default import menu_markup, sciences_uz_markup, language_markup
from keyboards.default.admin_buttons import tests_markup
from keyboards.inline import create_all_tests_markup, test_callback_data, create_edit_test_markup, variants, \
    create_questions_markup, create_edit_question_markup, question_callback_data
from loader import dp, db, bot
from states import AddQuestionTestStatesGroup, CreateTestStatesGroup
from utils.misc.write_excel import write_data_excel


@dp.message_handler(IsPrivate(), text="📃 O'quvchilar ro'yxati", user_id=ADMINS)
async def show_users_excel(msg: types.Message):
    columns = await db.select_column_names()
    users = await db.select_users()
    await write_data_excel(columns, users)
    file = InputFile(path_or_bytesio="data/users/data.xlsx")
    await msg.answer_document(file, caption="Barcha o'quvchilar ro'yxati!")


@dp.message_handler(IsPrivate(), text="✉️ Xabar yuborish", user_id=ADMINS)
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


@dp.message_handler(IsPrivate(), text="📥 Test qo'shish uchun", user_id=ADMINS)
async def add_test_or_question(msg: types.Message):
    await msg.answer("Bo'limni tanlang:", reply_markup=tests_markup)


@dp.message_handler(IsPrivate(), text="Yangi test ochish", user_id=ADMINS)
async def show_all_tests(msg: types.Message, state: FSMContext):
    await msg.answer("Fanni tanlang", reply_markup=sciences_uz_markup)
    await state.set_state(CreateTestStatesGroup.science)


@dp.message_handler(state=CreateTestStatesGroup.science, user_id=ADMINS)
async def choice_science_test(msg: types.Message, state: FSMContext):
    if msg.text == "⬅️ Orqaga":
        await msg.answer("Bo'limni tanlang:", reply_markup=tests_markup)
        await state.finish()
        return
    if msg.text not in sciences_uz:
        await msg.delete()
        await msg.answer("Iltimos, tugmalardan foydalaning!")
        return
    await state.set_data({'science': msg.text})
    await msg.answer("Test tilini tanlang:", reply_markup=language_markup)
    await CreateTestStatesGroup.next()


@dp.message_handler(state=CreateTestStatesGroup.language, text=['O’zbek tili', 'Русский язык'])
async def time_continue_test(msg: types.message, state: FSMContext):
    if msg.text == 'O’zbek tili':
        language = 'uzbek'
    else:
        language = 'russian'
    await state.update_data({'language': language})
    await msg.answer("Savollar sonini kiriting: ", reply_markup=ReplyKeyboardRemove())
    await CreateTestStatesGroup.next()


@dp.message_handler(state=CreateTestStatesGroup.language, content_types=ContentType.ANY)
async def send_error_test_language(msg: types.Message, state: FSMContext):
    await msg.answer("❗️ Quyidagi tugmalardan foydalaning!")


@dp.message_handler(state=CreateTestStatesGroup.count, user_id=ADMINS)
async def time_continue_test(msg: types.message, state: FSMContext):
    if str(msg.text).isdigit():
        data = await state.get_data()
        await db.add_test(data.get('science'), data.get('language'), int(msg.text))
        await msg.answer("✅ Yangi test ochildi.\n"
                         "\"Fan bo'yicha testlar\" bo'limida ko'rishingiz va savollar qo'shishingiz mumkin!",
                         reply_markup=tests_markup)
        await state.reset_data()
        await state.finish()
    else:
        await msg.answer("Test davomiyligini kiritishda xatolik!\n"
                         "Qayta kiriting")


@dp.message_handler(IsPrivate(), text="Fanlar bo'yicha testlar", user_id=ADMINS)
async def show_all_tests(msg: types.Message, state: FSMContext):
    await msg.answer("Fanni tanlang", reply_markup=sciences_uz_markup)
    await state.set_state(AddQuestionTestStatesGroup.science)


@dp.message_handler(state=AddQuestionTestStatesGroup.science, user_id=ADMINS)
async def choice_science_admin(msg: types.Message, state: FSMContext):
    if msg.text == "⬅️ Orqaga":
        await msg.answer("Bo'limni tanlang:", reply_markup=tests_markup)
        await state.finish()
        return
    if msg.text not in sciences_uz:
        await msg.delete()
        await msg.answer("Iltimos, tugmalardan foydalaning!")
        return
    if await db.select_science_tests(msg.text) is False:
        await msg.answer(f"Hozirda {msg.text} fanidan testlar mavjud emas!\n"
                         f"Test qo'shish uchun \"⬅️ Orqaga\" tugmasini borib so'ng,\n"
                         f"\"Yangi test ochish\" tugmasidan foydalaning!")
        return
    await msg.answer("Ajoyib, testni tanlab unga savol qo'shishingiz, tahrirlashingiz yoki o'chirishingiz "
                     "mumkin.", reply_markup=ReplyKeyboardRemove())
    await msg.answer(f"{msg.text} fani bo'yicha testlar: ", reply_markup=await create_all_tests_markup(msg.text))
    await state.set_data({'science': msg.text})
    await AddQuestionTestStatesGroup.next()


@dp.callback_query_handler(text='back', state=AddQuestionTestStatesGroup.test, user_id=ADMINS)
async def back_science_menu(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer("Fanni tanlang", reply_markup=sciences_uz_markup)
    await AddQuestionTestStatesGroup.previous()


@dp.callback_query_handler(test_callback_data.filter(), state=AddQuestionTestStatesGroup.test, user_id=ADMINS)
async def edit_test(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    test_id = callback_data.get('test_id')
    action = callback_data.get('update')
    data = await state.get_data()
    if action == 'back':
        await call.message.edit_text(f"{data.get('science')} fani bo'yicha testlar: ",
                                     reply_markup=await create_all_tests_markup(data.get('science')))
        return
    elif action == 'del':
        await db.delete_test(test_id)
        if await db.select_science_tests(data.get('science')) is False:
            await call.message.delete()
            await call.message.answer("Fanni tanlang", reply_markup=sciences_uz_markup)
            await AddQuestionTestStatesGroup.previous()
            return
        await call.message.edit_text(f"{data.get('science')} fani tanlangan testi o'chirildi!\n"
                                     f"Shu fan bo'yicha boshqa testlar:",
                                     reply_markup=await create_all_tests_markup(data.get('science')))
        return
    elif action == "add":
        await add_question(call, test_id, state)
        await AddQuestionTestStatesGroup.question_uz.set()
        return
    elif action == 'edit':
        await edit_question(call, test_id, state)
        await AddQuestionTestStatesGroup.next()
        return
    test_info = await db.select_test_id(test_id)
    all_tests = await db.select_questions_test_id(test_id)
    await state.update_data({'tests_count': len(all_tests), 'quantity': test_info[4]})
    await call.message.edit_text(f"{test_info[1]} fani {test_info[2]} testi uchun amalni tanlang:\n"
                                 f"Testlar soni: {len(all_tests)}/{test_info[4]}{'✅' if len(all_tests) >= test_info[4] else ''}",
                                 reply_markup=await create_edit_test_markup(test_id))


async def add_question(call, test_id, state, *args, **kwargs):
    data = await state.get_data()
    all_questions = await db.select_questions_test_id(test_id)
    number = len(all_questions) + 1
    await state.update_data({'test_id': test_id, 'number_question': number})
    await call.message.delete()
    await call.message.answer(
        f"{data.get('science')} fani testi uchun {number}-savolning o'zbekcha variantini kiriting:")
    await AddQuestionTestStatesGroup.next()


async def edit_question(call, test_id, state, *args, **kwargs):
    data = await state.get_data()
    all_questions = await db.select_questions_test_id(test_id)
    markup = await create_questions_markup(all_questions)
    await state.update_data({'test_id': test_id})
    await call.message.edit_text(f"{data.get('science')} fani testining qaysi savolini tahrirlamoqchisiz?",
                                 reply_markup=markup)


@dp.callback_query_handler(question_callback_data.filter(), state=AddQuestionTestStatesGroup.update)
async def choice_set_question(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    ques_id = callback_data.get('ques_id')
    action = callback_data.get('update')
    data = await state.get_data()
    if action == 'back':
        all_questions = await db.select_questions_test_id(data.get('test_id'))
        markup = await create_questions_markup(all_questions)
        await call.message.edit_text(f"{data.get('science')} fani testining qaysi savolini tahrirlamoqchisiz?",
                                     reply_markup=markup)
        return
    elif action == 'edit':
        await call.message.delete()
        question = await db.select_question_id(ques_id)
        await state.update_data({'question_id': ques_id, 'number_question': question[1]})
        await call.message.answer(
            f"{data.get('science')} fani testi uchun {question[1]}-savolning o'zbekcha variantini kiriting:")
        await AddQuestionTestStatesGroup.next()


@dp.callback_query_handler(text='back', state=AddQuestionTestStatesGroup.update)
async def choice_set_question(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    test_id = data.get('test_id')
    test_info = await db.select_test_id(test_id)
    all_tests = await db.select_questions_test_id(test_id)
    await state.update_data({'tests_count': len(all_tests), 'quantity': test_info[4]})
    await call.message.edit_text(f"{test_info[1]} fani {test_info[2]} testi uchun amalni tanlang:\n"
                                 f"Testlar soni: {len(all_tests)}/{test_info[4]}{'✅' if len(all_tests) >= test_info[4] else ''}",
                                 reply_markup=await create_edit_test_markup(test_id))
    await AddQuestionTestStatesGroup.test.set()


@dp.callback_query_handler(state=AddQuestionTestStatesGroup.update)
async def choice_set_question(call: types.CallbackQuery, state: FSMContext):
    question = await db.select_question_id(call.data)
    info = (f"{question[1]}-savol\n"
            f"Uz:\n"
            f"{question[2]}\n"
            f"Ru:\n"
            f"{question[3]}\n"
            f"To'g'ri javob: {question[4]}")
    await call.message.edit_text(info, reply_markup=await create_edit_question_markup(question[0]))


@dp.message_handler(state=AddQuestionTestStatesGroup.question_uz)
async def send_question_uz(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data({'question_uz': msg.text})
    await msg.answer(
        f"{data.get('science')} fani testi uchun {data.get('number_question')}-savolning ruscha variantini "
        f"kiriting:")
    await AddQuestionTestStatesGroup.next()


@dp.message_handler(state=AddQuestionTestStatesGroup.question_ru)
async def send_question_ru(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data({'question_ru': msg.text})
    await msg.answer(
        f"{data.get('science')} fani testi uchun {data.get('number_question')}-savolning to'g'ri variantini "
        f"tanlang: ", reply_markup=variants)
    await AddQuestionTestStatesGroup.next()


@dp.callback_query_handler(state=AddQuestionTestStatesGroup.true_response)
async def send_true_response(call: types.CallbackQuery, state: FSMContext):
    await state.update_data({'true_response': call.data})
    data = await state.get_data()
    science = data.get('science')
    if data.get('question_id'):
        await db.update_question_test(**data)
        info = "Savol muvaffaqiyatli o'zgartirildi!"
    else:
        await db.add_question_test(**data)
        info = "Savol muvaffaqiyatli qo'shildi!"
    await state.reset_data()
    await call.message.delete()
    await call.message.answer(info)
    test_id = data.get('test_id')
    test_info = await db.select_test_id(test_id)
    all_tests = await db.select_questions_test_id(test_id)
    await state.update_data({'science': science, 'tests_count': len(all_tests), 'quantity': test_info[4]})
    await call.message.answer(f"{test_info[1]} fani {test_info[2]} testi uchun amalni tanlang:\n"
                              f"Testlar soni: {len(all_tests)}/{data.get('quantity')}"
                              f"{'✅' if len(all_tests) >= data.get('quantity') else ''}",
                              reply_markup=await create_edit_test_markup(test_id))
    await AddQuestionTestStatesGroup.test.set()
