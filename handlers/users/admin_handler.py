import datetime
import os
import time
from io import BytesIO

import pytz
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile, ReplyKeyboardRemove, ContentType
from aiogram_datepicker import Datepicker, DatepickerSettings

from data.config import ADMINS, sciences_uz
from filters import IsPrivate
from keyboards.default import menu_markup, sciences_uz_markup, language_markup, skip_markup
from keyboards.default import tests_markup, olympiad_tests_markup
from keyboards.inline import create_all_tests_markup, test_callback_data, create_edit_test_markup, \
    create_questions_markup, create_edit_question_markup, question_callback_data
from loader import dp, db, bot
from states import AddQuestionTestStatesGroup, CreateTestStatesGroup
from utils import question_photo_link
from utils.misc.write_excel import write_data_excel


def _get_datepicker_settings():
    return DatepickerSettings()  # some settings


@dp.message_handler(IsPrivate(), text="📃 O'quvchilar ro'yxati", user_id=ADMINS)
async def show_users_excel(msg: types.Message):
    columns = await db.select_column_names()
    users = await db.select_users()
    await write_data_excel(columns, users)
    file = InputFile(path_or_bytesio="data/users/data.xlsx")
    await msg.answer_document(file, caption="Barcha o'quvchilar ro'yxati!")
    if os.path.exists('data/users/data.xlsx'):
        os.remove('data/users/data.xlsx')


@dp.message_handler(IsPrivate(), text="✉️ Xabar yuborish", user_id=ADMINS)
async def show_users_excel(msg: types.Message, state: FSMContext):
    await msg.answer("Barcha o'quvchilar uchun xabarni kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state('send_message')


@dp.message_handler(user_id=ADMINS, state='send_message', content_types=[ContentType.TEXT, ContentType.PHOTO])
async def send_msg_to_all_users(msg: types.Message, state: FSMContext):
    users = await db.select_users()
    photos = msg.photo
    if photos:
        photo_id = photos[-1].file_id
        for user in users:
            try:
                await bot.send_photo(user[1], photo=photo_id, caption=msg.caption)
            except Exception as e:
                print(f"Failed to send message to user {user[1]}: {e}")
    else:
        for user in users:
            try:
                await bot.send_message(user[1], msg.text)
            except Exception as e:
                print(f"Failed to send message to user {user[1]}: {e}")
    await msg.answer("Xabar barcha foydalanuvchilarga yuborildi!", reply_markup=menu_markup)
    await state.finish()


@dp.message_handler(IsPrivate(), text="📚 Test bo'limi", user_id=ADMINS)
async def add_test_or_question(msg: types.Message):
    await msg.answer("Bo'limni tanlang:", reply_markup=tests_markup)


@dp.message_handler(IsPrivate(), text="🏆 Olimpiada bo'limi", user_id=ADMINS)
async def add_test_or_question(msg: types.Message):
    await msg.answer("Bo'limni tanlang:", reply_markup=olympiad_tests_markup)


@dp.message_handler(IsPrivate(), text="➕ Yangi test ochish", user_id=ADMINS)
async def show_all_tests(msg: types.Message, state: FSMContext):
    await msg.answer("Fanni tanlang", reply_markup=sciences_uz_markup)
    await state.set_state(CreateTestStatesGroup.science)


@dp.message_handler(IsPrivate(), text="➕ Olimpiada testi ochish", user_id=ADMINS)
async def show_all_tests(msg: types.Message, state: FSMContext):
    await msg.answer("<b>Olimpiada</b> fanini tanlang", reply_markup=sciences_uz_markup)
    await state.set_state(CreateTestStatesGroup.science)
    await state.set_data({'olympiad': True})


@dp.message_handler(state=CreateTestStatesGroup.science, user_id=ADMINS)
async def choice_science_test(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    olympiad_test = True if data.get('olympiad') else False
    if msg.text == "⬅️ Orqaga":
        await msg.answer("Bo'limni tanlang:", reply_markup=olympiad_tests_markup if olympiad_test else tests_markup)
        await state.finish()
        return
    if msg.text not in sciences_uz:
        await msg.delete()
        await msg.answer("Iltimos, tugmalardan foydalaning!")
        return
    await state.update_data({'science': msg.text})
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
        if data.get('olympiad'):
            datepicker = Datepicker(_get_datepicker_settings())
            markup = datepicker.start_calendar()
            await msg.answer("⏱ <b>Olimpiada</b> <b>boshlanish</b> sanasini tanlang.\n"
                             "So'ng, \"Select\" tugmasini bosing:\n\n"
                             "Eslatma!\n<b>Olimpiada</b> tanlangan sananing 00:00 vaqtida boshlanadi.",
                             reply_markup=markup)
            await state.update_data({'count': int(msg.text)})
            await CreateTestStatesGroup.next()
        else:
            await db.add_test(data.get('science'), data.get('language'), int(msg.text))
            await msg.answer("✅ Yangi test ochildi.\n"
                             "\"📓 Fanlar bo'yicha testlar\" bo'limida ko'rishingiz va savollar qo'shishingiz mumkin!",
                             reply_markup=tests_markup)
            await state.reset_data()
            await state.finish()
    else:
        await msg.answer("Test savollar sonini kiritishda xatolik!\n"
                         "Qayta kiriting")


@dp.message_handler(state=CreateTestStatesGroup.start_time, user_id=ADMINS, content_types=ContentType.ANY)
async def choice_start_time_err(msg: types.Message, state: FSMContext):
    await msg.delete()
    err_msg = await msg.answer("Iltimos sanani tanlab, keyin \"Select\" tugmasini bosing!")
    time.sleep(2)
    await err_msg.delete()


@dp.callback_query_handler(Datepicker.datepicker_callback.filter(), state=CreateTestStatesGroup.start_time)
async def choice_start_time(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    datepicker = Datepicker(_get_datepicker_settings())

    date = await datepicker.process(callback_query, callback_data)
    if date:
        naive_dt = datetime.datetime(date.year, date.month, date.day, 0, 0, 0)
        await state.update_data({'start_time': naive_dt})
        datepicker = Datepicker(_get_datepicker_settings())
        markup = datepicker.start_calendar()
        info = (f"⏱ <b>Olimpiada</b> boshlanish vaqti: {date.strftime('%d/%m/%Y')}, 00:00:00\n"
                f"🏁 <b>Olimpiada</b> <b>tugash sanasini tanlang</b>.\n"
                f"So'ng, \"Select\" tugmasini bosing:\n\n"
                f"Eslatma!\n<b>Olimpiada</b> tanlangan sananing 00:00 vaqtida tugaydi.")
        await callback_query.message.edit_text(info, reply_markup=markup)
        await CreateTestStatesGroup.next()

    await callback_query.answer()


@dp.callback_query_handler(Datepicker.datepicker_callback.filter(), state=CreateTestStatesGroup.end_time)
async def choice_end_time(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    datepicker = Datepicker(_get_datepicker_settings())

    date = await datepicker.process(callback_query, callback_data)
    if date:
        naive_dt = datetime.datetime(date.year, date.month, date.day, 0, 0, 0)
        await state.update_data({'end_time': naive_dt})
        data = await state.get_data()
        if data.get('start_time') >= naive_dt:
            await callback_query.message.answer("Tugash vaqti xato, qayta tanlang 👆")
            return
        await callback_query.message.delete()
        await db.add_test(**data)
        info = ("✅ <b>Olimpiada</b> testi ochildi.\n"
                "\"📓 Olimpiada testlari\" bo'limida ko'rishingiz va savollar qo'shishingiz mumkin!")
        await callback_query.message.answer(info, reply_markup=olympiad_tests_markup)
        await state.reset_data()
        await state.finish()

    await callback_query.answer()


@dp.message_handler(IsPrivate(), text="📓 Fanlar bo'yicha testlar", user_id=ADMINS)
async def show_all_tests(msg: types.Message, state: FSMContext):
    await msg.answer("Fanni tanlang", reply_markup=sciences_uz_markup)
    await state.set_state(AddQuestionTestStatesGroup.science)


@dp.message_handler(IsPrivate(), text="📓 Olimpiada testlari", user_id=ADMINS)
async def show_all_tests(msg: types.Message, state: FSMContext):
    await msg.answer("<b>Olimpiada</b> fanini tanlang", reply_markup=sciences_uz_markup)
    await state.set_state(AddQuestionTestStatesGroup.science)
    await state.set_data({'olympiad': True})


@dp.message_handler(state=AddQuestionTestStatesGroup.science, user_id=ADMINS)
async def choice_science_admin(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    olympiad_test = True if data.get('olympiad') else False
    if msg.text == "⬅️ Orqaga":
        if data.get('olympiad'):
            await msg.answer("Bo'limni tanlang:", reply_markup=olympiad_tests_markup)
        else:
            await msg.answer("Bo'limni tanlang:", reply_markup=tests_markup)
        await state.finish()
        return
    if msg.text not in sciences_uz:
        await msg.delete()
        await msg.answer("Iltimos, tugmalardan foydalaning!")
        return
    if await db.select_science_tests(msg.text, olympiad_test) is False:
        await msg.answer(
            f"Hozirda {msg.text} fanidan {'<b>olimpiada</b> ' if olympiad_test else ''}testlar mavjud emas!")
        return
    await msg.answer("Ajoyib, testni tanlab unga savol qo'shishingiz, tahrirlashingiz yoki o'chirishingiz "
                     "mumkin.", reply_markup=ReplyKeyboardRemove())
    await msg.answer(f"""{msg.text} fani {"bo'yicha <b>olimpiada</b> " if olympiad_test else ''}testlari: """,
                     reply_markup=await create_all_tests_markup(msg.text, olympiad_test))
    await state.update_data({'science': msg.text})
    await AddQuestionTestStatesGroup.next()


@dp.callback_query_handler(text='back', state=AddQuestionTestStatesGroup.test, user_id=ADMINS)
async def back_science_menu(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.delete()
    await call.message.answer("<b>Olimpiada</b> fanini tanlang" if data.get('olympiad') else "Fanni tanlang",
                              reply_markup=sciences_uz_markup)
    await AddQuestionTestStatesGroup.previous()


@dp.callback_query_handler(test_callback_data.filter(), state=AddQuestionTestStatesGroup.test, user_id=ADMINS)
async def edit_test(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    data = await state.get_data()
    olympiad_test = True if data.get('olympiad') else False
    test_id = callback_data.get('test_id')
    action = callback_data.get('update')
    test_info = await db.select_test_id(test_id)
    await state.update_data({'language': test_info[3]})
    if action == 'back':
        await call.message.edit_text(
            f"""{data.get('science')} fani {"bo'yicha <b>olimpiada</b> " if olympiad_test else ''}testlari: """,
            reply_markup=await create_all_tests_markup(data.get('science'), olympiad_test))
        return
    elif action == 'del':
        await db.delete_test(test_id)
        if await db.select_science_tests(data.get('science'), olympiad_test) is False:
            await call.message.delete()
            await call.message.answer("<b>Olimpiada</b> fanini tanlang" if data.get('olympiad') else "Fanni tanlang",
                                      reply_markup=sciences_uz_markup)
            await AddQuestionTestStatesGroup.previous()
            return
        await call.message.edit_text(
            f"{data.get('science')} fani tanlangan {'<b>olimpiada</b> ' if data.get('olympiad') else ''}testi o'chirildi!\n"
            f"Shu fan bo'yicha boshqa testlar:",
            reply_markup=await create_all_tests_markup(data.get('science'), olympiad_test))
        return
    elif action == "add":
        await add_question_image(call, test_id, state)
        await AddQuestionTestStatesGroup.image.set()
        return
    elif action == 'edit':
        await edit_question(call, test_id, state)
        await AddQuestionTestStatesGroup.next()
        return
    elif action == 'edit_date':
        await edit_start_date(call, test_id, state)
        await AddQuestionTestStatesGroup.start_date.set()
        return
    all_tests = await db.select_questions_test_id(test_id)
    await state.update_data({'tests_count': len(all_tests), 'quantity': test_info[4]})
    if olympiad_test:
        start_localized_datetime = test_info[8]
        stop_localized_datetime = test_info[6]
        now_localized_datetime = datetime.datetime.now()
        if now_localized_datetime < start_localized_datetime:
            status = "⏸ Boshlanmagan!"
        elif now_localized_datetime < stop_localized_datetime:
            status = "▶️ Davom etmoqda!"
        else:
            status = "⏹ Tugagan!"
        info = f"{test_info[1]} fani '{test_info[6].date()} - {test_info[3][:2]}' <b>olimpiada</b> testi uchun amalni tanlang:\n"
        info += f"Holat: {status}\n"
    else:
        info = f"{test_info[1]} fani {test_info[2]} - {test_info[3][:2]} testi uchun amalni tanlang:\n"
    info += f"Testlar soni: {len(all_tests)}/{test_info[4]} {'✅' if len(all_tests) >= test_info[4] else ''}"
    await call.message.edit_text(info, reply_markup=await create_edit_test_markup(test_id, olympiad_test))


async def add_question_image(call, test_id, state, *args, **kwargs):
    data = await state.get_data()
    all_questions = await db.select_questions_test_id(test_id)
    number = len(all_questions) + 1
    await state.update_data({'test_id': test_id, 'number_question': number})
    await call.message.delete()
    await call.message.answer(
        f"{data.get('science')} fani {'<b>olimpiada</b> ' if data.get('olympiad') else ''}testi uchun {number}-savolni rasmini yuboring!",
        reply_markup=skip_markup)


async def edit_start_date(call, test_id, state):
    datepicker = Datepicker(_get_datepicker_settings())
    markup = datepicker.start_calendar()
    await call.message.delete()
    await call.message.answer("⏱ <b>Olimpiada</b> <b>boshlanish</b> sanasini tanlang.\n"
                              "So'ng, \"Select\" tugmasini bosing:\n\n"
                              "Eslatma!\n<b>Olimpiada</b> tanlangan sananing 00:00 vaqtida boshlanadi.",
                              reply_markup=markup)
    await state.update_data({'test_id': test_id})


@dp.callback_query_handler(Datepicker.datepicker_callback.filter(), state=AddQuestionTestStatesGroup.start_date)
async def select_start_date(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    datepicker = Datepicker(_get_datepicker_settings())

    date = await datepicker.process(callback_query, callback_data)
    if date:
        naive_dt = datetime.datetime(date.year, date.month, date.day, 0, 0, 0)
        await state.update_data({'start_time': naive_dt})
        datepicker = Datepicker(_get_datepicker_settings())
        markup = datepicker.start_calendar()
        info = (f"⏱ <b>Olimpiada</b> boshlanish vaqti: {date.strftime('%d/%m/%Y')}, 00:00:00\n"
                f"🏁 <b>Olimpiada</b> <b>tugash sanasini tanlang</b>.\n"
                f"So'ng, \"Select\" tugmasini bosing:\n\n"
                f"Eslatma!\n<b>Olimpiada</b> tanlangan sananing 00:00 vaqtida tugaydi.")
        await callback_query.message.edit_text(info, reply_markup=markup)
        await AddQuestionTestStatesGroup.next()

    await callback_query.answer()


@dp.callback_query_handler(Datepicker.datepicker_callback.filter(), state=AddQuestionTestStatesGroup.end_date)
async def select_end_date(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    datepicker = Datepicker(_get_datepicker_settings())

    date = await datepicker.process(callback_query, callback_data)
    if date:
        naive_dt = datetime.datetime(date.year, date.month, date.day, 0, 0, 0)
        await state.update_data({'end_time': naive_dt})
        data = await state.get_data()
        test_id = data.get('test_id')
        olympiad_test = data.get('olympiad')
        if data.get('start_time') >= naive_dt:
            await callback_query.message.answer("Tugash vaqti xato, qayta tanlang 👆")
            return
        await callback_query.message.delete()
        await db.update_date_test(data.get('test_id'), data.get('start_time'), naive_dt)
        info = "✅ <b>Olimpiada</b> testi vaqti o'zgartirildi!"
        await callback_query.message.answer(info)
        test_info = await db.select_test_id(test_id)
        all_tests = await db.select_questions_test_id(test_id)
        await state.update_data({'tests_count': len(all_tests), 'quantity': test_info[4]})

        start_localized_datetime = test_info[8]
        stop_localized_datetime = test_info[6]
        now_localized_datetime = datetime.datetime.now()
        if now_localized_datetime < start_localized_datetime:
            status = "⏸ Boshlanmagan!"
        elif now_localized_datetime < stop_localized_datetime:
            status = "▶️ Davom etmoqda!"
        else:
            status = "⏹ Tugagan!"
        info = f"{test_info[1]} fani '{test_info[6].date()} - {test_info[3][:2]}' <b>olimpiada</b> testi uchun amalni tanlang:\n"
        info += f"Holat: {status}\n"

        info += f"Testlar soni: {len(all_tests)}/{test_info[4]} {'✅' if len(all_tests) >= test_info[4] else ''}"
        await callback_query.message.answer(info, reply_markup=await create_edit_test_markup(test_id, olympiad_test))
        await AddQuestionTestStatesGroup.test.set()
    await callback_query.answer()


@dp.message_handler(text="Rasm mavjud emas!", state=AddQuestionTestStatesGroup.image)
async def add_question_skip_image(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if data.get('language') == 'uzbek':
        word = 'o\'zbek'
    else:
        word = 'rus'
    await message.answer(
        f"{data.get('science')} fani {'<b>olimpiada</b> ' if data.get('olympiad') else ''}"
        f"testi uchun {data.get('number_question')}-savolni {word} tilida kiriting"
        f"(Oxirgi qismda to'g'ri variantni raqam orqali ifodalang):", reply_markup=ReplyKeyboardRemove())
    await AddQuestionTestStatesGroup.next()


@dp.message_handler(state=AddQuestionTestStatesGroup.image, content_types=ContentType.PHOTO)
async def add_question_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if data.get('language') == 'uzbek':
        word = 'o\'zbek'
    else:
        word = 'rus'
    await message.answer(
        f"{data.get('science')} fani {'<b>olimpiada</b> ' if data.get('olympiad') else ''}"
        f"testi uchun {data.get('number_question')}-savolni {word} tilida kiriting"
        f"(Oxirgi qismda to'g'ri variantni raqam orqali ifodalang):", reply_markup=ReplyKeyboardRemove())
    photo = message.photo[-1]
    image_url = await question_photo_link(photo)
    await state.update_data({'image_id': image_url})
    await AddQuestionTestStatesGroup.next()


async def edit_question(call, test_id, state, *args, **kwargs):
    data = await state.get_data()
    all_questions = await db.select_questions_test_id(test_id)
    markup = await create_questions_markup(all_questions)
    await state.update_data({'test_id': test_id})
    await call.message.edit_text(f"{data.get('science')} fani {'<b>olimpiada</b> ' if data.get('olympiad') else ''}"
                                 f"testining qaysi savolini tahrirlamoqchisiz?", reply_markup=markup)


@dp.callback_query_handler(question_callback_data.filter(), state=AddQuestionTestStatesGroup.update)
async def choice_set_question(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    ques_id = callback_data.get('ques_id')
    action = callback_data.get('update')
    data = await state.get_data()
    if action == 'back':
        all_questions = await db.select_questions_test_id(data.get('test_id'))
        markup = await create_questions_markup(all_questions)
        await call.message.delete()
        await call.message.answer(f"{data.get('science')} fani {'<b>olimpiada</b> ' if data.get('olympiad') else ''}"
                                  f"testining qaysi savolini tahrirlamoqchisiz?", reply_markup=markup)
        return
    elif action == 'edit':
        await call.message.delete()
        question = await db.select_question_id(ques_id)
        await state.update_data({'question_id': ques_id, 'number_question': question[1]})
        await call.message.answer(
            f"{data.get('science')} fani {'<b>olimpiada</b> ' if data.get('olympiad') else ''}"
            f"testi uchun {question[1]}-savolni rasmini yuboring!", reply_markup=skip_markup)
        await AddQuestionTestStatesGroup.next()


@dp.callback_query_handler(text='back', state=AddQuestionTestStatesGroup.update)
async def choice_set_question(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    test_id = data.get('test_id')
    test_info = await db.select_test_id(test_id)
    all_tests = await db.select_questions_test_id(test_id)
    await state.update_data({'tests_count': len(all_tests), 'quantity': test_info[4]})
    if data.get('olympiad'):
        start_localized_datetime = test_info[8]
        stop_localized_datetime = test_info[6]
        now_localized_datetime = datetime.datetime.now()
        if now_localized_datetime < start_localized_datetime:
            status = "⏸ Boshlanmagan!"
        elif now_localized_datetime < stop_localized_datetime:
            status = "▶️ Davom etmoqda!"
        else:
            status = "⏹ Tugagan!"
        info = f"{test_info[1]} fani '{test_info[6].date()} - {test_info[3][:2]}' <b>olimpiada</b> testi uchun amalni tanlang:\n"
        info += f"Holat: {status}\n"
    else:
        info = f"{test_info[1]} fani {test_info[2]} - {test_info[3][:2]} testi uchun amalni tanlang:\n"
    info += f"Testlar soni: {len(all_tests)}/{test_info[4]} {'✅' if len(all_tests) >= test_info[4] else ''}"
    await call.message.edit_text(info, reply_markup=await create_edit_test_markup(test_id, olympiad_test=data.get(
        'olympiad')))
    await AddQuestionTestStatesGroup.test.set()


@dp.callback_query_handler(state=AddQuestionTestStatesGroup.update)
async def choice_set_question(call: types.CallbackQuery, state: FSMContext):
    question = await db.select_question_id(call.data)
    data = await state.get_data()
    if data.get('language') == 'uzbek':
        info = (f"{question[1]}-savol\n"
                f"Uz:\n"
                f"{question[2].replace('>', '&gt').replace('<', '&lt')}\n"
                f"To'g'ri javob: {question[4]}")
    else:
        info = (f"{question[1]}-savol\n"
                f"Ru:\n"
                f"{question[3].replace('>', '&gt').replace('<', '&lt')}\n"
                f"To'g'ri javob: {question[4]}")
    if question[5]:
        await call.message.delete()
        await call.message.answer_photo(question[5], caption=info,
                                        reply_markup=await create_edit_question_markup(question[0]))
    else:
        await call.message.edit_text(info, reply_markup=await create_edit_question_markup(question[0]))


@dp.message_handler(state=AddQuestionTestStatesGroup.question)
async def send_question_uz(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    true_response = str(msg.text)[-1]
    if data.get('language') == 'uzbek':
        await state.update_data({'question_uz': str(msg.text)[:len(msg.text) - 1], 'question_ru': 'Mavjud emas'})
    else:
        await state.update_data({'question_uz': 'Mavjud emas', 'question_ru': str(msg.text)[:len(msg.text) - 1]})
    if true_response.isdigit() and true_response in ['1', '2', '3', '4']:
        true_response = int(true_response)
    else:
        await msg.answer("‼️ To'g'ri javob kiritishda xatolik, qayta kiriting!")
        return
    await state.update_data({'true_response': true_response})
    data = await state.get_data()
    science = data.get('science')
    language = data.get('language')
    if data.get('question_id'):
        await db.update_question_test(**data)
        info = "Savol muvaffaqiyatli o'zgartirildi!"
    else:
        await db.add_question_test(**data)
        info = "Savol muvaffaqiyatli qo'shildi!"
    await msg.answer(info)
    test_id = data.get('test_id')
    test_info = await db.select_test_id(test_id)
    all_tests = await db.select_questions_test_id(test_id)
    await state.set_data({'olympiad': data.get('olympiad'), 'science': science, 'tests_count': len(all_tests),
                          'quantity': test_info[4], 'language': language})
    if data.get('olympiad'):
        start_localized_datetime = test_info[8]
        stop_localized_datetime = test_info[6]
        now_localized_datetime = datetime.datetime.now()
        if now_localized_datetime < start_localized_datetime:
            status = "⏸ Boshlanmagan!"
        elif now_localized_datetime < stop_localized_datetime:
            status = "▶️ Davom etmoqda!"
        else:
            status = "⏹ Tugagan!"
        info = f"{test_info[1]} fani '{test_info[6].date()} - {test_info[3][:2]}' <b>olimpiada</b> testi uchun amalni tanlang:\n"
        info += f"Holat: {status}\n"
    else:
        info = f"{test_info[1]} fani {test_info[2]} - {test_info[3][:2]} testi uchun amalni tanlang:\n"
    info += f"Testlar soni: {len(all_tests)}/{test_info[4]} {'✅' if len(all_tests) >= test_info[4] else ''}"

    await msg.answer(info, reply_markup=await create_edit_test_markup(test_id, olympiad_test=data.get('olympiad')))
    await AddQuestionTestStatesGroup.test.set()
