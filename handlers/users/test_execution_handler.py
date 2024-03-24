import datetime
import time

import pytz
from aiogram import types
from aiogram.types import ReplyKeyboardRemove, ContentType, InlineKeyboardMarkup, InputFile
from aiogram.dispatcher import FSMContext

from data.config import sciences_uz, sciences_ru, sciences_dict, responses_uz, responses_ru
from filters import IsPrivate
from keyboards.default import sciences_uz_markup, sciences_ru_markup, menu_test_ru, menu_test_uz
from keyboards.inline import start_test_markup_uz, start_test_markup_ru, make_keyboard_test_responses, callback_data
from loader import dp, db
from states import TestStatesGroup, PINFLStateGroup


@dp.message_handler(IsPrivate(), text="👨‍💻 TEST TOPSHIRISH")
async def solution_test_uz(msg: types.Message, state: FSMContext):
    user = await db.select_user(msg.from_user.id)
    if user is None:
        await msg.answer("‼️ Siz ro'yxatdan o'tmaganingiz uchun test topshira olmaysiz!\n"
                         "Ro'yxatdan o'tish uchun - /start", reply_markup=ReplyKeyboardRemove())
        return
    await state.set_data({'language': 'uzbek'})
    if user[-1] is None:
        result = "⚠️ Botdan foydalanish uchun ID-kartangizdagi Shaxsiy raqamingizni kiriting:"
        image = InputFile('data/images/pinfl.jpg')
        image_url = "http://telegra.ph//file/97b3043fbcdc89ba48360.jpg"
        try:
            await msg.answer_photo(image_url, caption=result, reply_markup=ReplyKeyboardRemove())
        except:
            await msg.answer_photo(image, caption=result, reply_markup=ReplyKeyboardRemove())
        await PINFLStateGroup.pinfl.set()
        return
    info = f"Qaysi fandan test topshirmoqchisiz?"
    await msg.answer(info, reply_markup=sciences_uz_markup)
    await state.set_state(TestStatesGroup.science)


# (2, '5442563505', 'uzbek', 'Ilhomjon Raximov', '+998336589340', 'Buxoro viloyati',
# 'Olot tumani', '3', 'BIOLOGIYA', '2024-03-24 23:47:50.025367', '2024-03-24 23:47:50.025370',
# '-', '-', '-', 'Hali ID karta olmaganman')
@dp.message_handler(IsPrivate(), text="🏆 OLIMPIADA (1-bosqich)")
async def solution_test_uz(msg: types.Message, state: FSMContext):
    user = await db.select_user(msg.from_user.id)
    if user is None:
        await msg.answer("‼️ Siz ro'yxatdan o'tmaganingiz uchun olimpiadada qatnasha olmaysiz!\n"
                         "Ro'yxatdan o'tish uchun - /start", reply_markup=ReplyKeyboardRemove())
        return
    test_app = await db.select_test(user[8], 'uzbek', True)
    if test_app is False:
        await msg.answer(f"Hozirda {user[8]} fanidan olimpiada testi mavjud emas!")
        return
    if await db.select_result_test_user(msg.from_user.id, user[8], True):
        await msg.answer(f"{user[8]} fanidan olimpiada testini yechib bo'lgansiz!\n"
                         f"Sertifikatingizni yuklab olish uchun quyidagi tugmani bosing.")
        return
    tashkent_timezone = pytz.timezone('Asia/Tashkent')
    start_localized_datetime = tashkent_timezone.localize(datetime.datetime.strptime(test_app[8][:10], '%Y-%m-%d'))
    stop_localized_datetime = tashkent_timezone.localize(datetime.datetime.strptime(test_app[6][:10], '%Y-%m-%d'))
    now_localized_datetime = tashkent_timezone.localize(datetime.datetime.now())
    if now_localized_datetime < start_localized_datetime:
        await msg.answer(f"{user[8]} fanidan olimpiada test sinovlari {test_app[8][:10]} soat 00:00da boshlanadi!")
    elif now_localized_datetime < stop_localized_datetime:
        info = (f"OLIMPIADA (1-bosqich)\n\n{user[8]} fani uchun olimpiada testi.\n\n"
                f"📝 Savollar soni: {test_app[4]}\n\n"
                f"Testni boshlash uchun \"👨‍💻 Testni boshlash\" tugmasini bosing!")
        markup = start_test_markup_uz
        await state.update_data(
            {'language': 'uzbek', 'test_id': test_app[0], 'questions_count': test_app[4], 'science': user[8],
             'olympiad_test': True})
        success = "✅ Olimpiada davom etmoqda!"
        await state.set_state(TestStatesGroup.ready)
        message = await msg.answer(success, reply_markup=ReplyKeyboardRemove())
        await msg.answer(info, reply_markup=markup)
        time.sleep(2)
        await message.delete()
    else:
        await msg.answer(f"{user[8]} fanidan olimpiada test sinovlari {test_app[6][:10]} soat 00:00da yakunlangan!")


@dp.message_handler(IsPrivate(), text="🏆 ОЛИМПИАДА (1-й этап)")
async def solution_test_uz(msg: types.Message, state: FSMContext):
    user = await db.select_user(msg.from_user.id)
    if user is None:
        await msg.answer("‼️ Вы не сможете участвовать в олимпиаде, так как не прошли регистрацию!\n"
                         "Для регистрации - /start", reply_markup=ReplyKeyboardRemove())
        return
    test_app = await db.select_test(sciences_dict.get(user[8]), 'russian', True)
    if test_app is False:
        await msg.answer(f"Сейчас нет олимпиадного теста по {user[8]} предмету!")
        return
    if await db.select_result_test_user(msg.from_user.id, sciences_dict.get(user[8]), True):
        await msg.answer(f"Вы успешно сдали олимпиадный тест по {user[8]} предмету!\n"
                         f"Для загрузки вашего сертификата нажмите на следующую кнопку.")
        return
    tashkent_timezone = pytz.timezone('Asia/Tashkent')
    start_localized_datetime = tashkent_timezone.localize(datetime.datetime.strptime(test_app[8][:10], '%Y-%m-%d'))
    stop_localized_datetime = tashkent_timezone.localize(datetime.datetime.strptime(test_app[6][:10], '%Y-%m-%d'))
    now_localized_datetime = tashkent_timezone.localize(datetime.datetime.now())
    if now_localized_datetime < start_localized_datetime:
        await msg.answer(f"Олимпиадное тестирование по {user[8]} начнется {test_app[8][:10]} в 00:00!")
    elif now_localized_datetime < stop_localized_datetime:
        info = (f"ОЛИМПИАДА (1-й этап)\n\n"
                f"Тест по предмету {user[8]} для олимпиады.\n\n"
                f"📝 Количество вопросов: {test_app[4]}\n\n"
                f"Нажмите кнопку \"👨‍💻 Начать тест\" для начала тестирования!")
        markup = start_test_markup_ru
        await state.update_data(
            {'language': 'russian', 'test_id': test_app[0], 'questions_count': test_app[4], 'science': user[8],
             'olympiad_test': True})
        success = "✅ Олимпиада продолжается!"
        await state.set_state(TestStatesGroup.ready)
        message = await msg.answer(success, reply_markup=ReplyKeyboardRemove())
        await msg.answer(info, reply_markup=markup)
        time.sleep(2)
        await message.delete()
    else:
        await msg.answer(f"Тест по {user[8]} для олимпиады завершён {test_app[6][:10]} в 00:00!")


@dp.message_handler(IsPrivate(), text="👨‍💻 ПРОЙТИ ТЕСТ")
async def solution_test_ru(msg: types.Message, state: FSMContext):
    user = await db.select_user(msg.from_user.id)
    if user is None:
        await msg.answer("‼️ Вы не можете пройти тест, не зарегистрировавшись!\n"
                         "Для регистрации - /start", reply_markup=ReplyKeyboardRemove())
        return
    await state.set_data({'language': 'russian'})
    if user[-1] is None:
        result = ("⚠️ Введите персональный идентификационный номер, указанный в вашем ID-карте, чтобы воспользоваться "
                  "ботом:")
        image = InputFile('data/images/pinfl_ru.jpg')
        image_url = "http://telegra.ph//file/e815e58a3c4c08948b617.jpg"
        try:
            await msg.answer_photo(image_url, caption=result, reply_markup=ReplyKeyboardRemove())
        except:
            await msg.answer_photo(image, caption=result, reply_markup=ReplyKeyboardRemove())
        await PINFLStateGroup.pinfl.set()
        return
    info = f"Из какого предмета вы хотите сдать тест?"
    await msg.answer(info, reply_markup=sciences_ru_markup)
    await state.set_state(TestStatesGroup.science)


@dp.message_handler(state=TestStatesGroup.science, text=['⬅️ Orqaga', "⬅️ Назад"])
async def back_base_menu(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    if data.get('language') == 'uzbek':
        await msg.answer("Test topshirib ko’rish uchun quyidagi tugmani bosing.",
                         reply_markup=menu_test_uz)
    else:
        await msg.answer("Чтобы попробовать пройти тест, нажмите кнопку ниже.",
                         reply_markup=menu_test_ru)
    await state.reset_data()
    await state.finish()


@dp.message_handler(state=TestStatesGroup.science)
async def choice_test_science(msg: types.Message, state: FSMContext):
    await state.update_data({'science': msg.text})
    data = await state.get_data()
    if data.get('language') == 'uzbek':
        if msg.text not in sciences_uz:
            await msg.delete()
            await msg.answer("‼️ Iltimos, quyidagi tugmalardan foydalaning!", reply_markup=sciences_uz_markup)
            return
        test_app = await db.select_test(msg.text, data.get('language'))
        if test_app is False:
            await msg.answer(f"Hozirda {msg.text} fanidan test mavjud emas!")
            return
        if await db.select_result_test_user(msg.from_user.id, msg.text):
            await msg.answer("Bu testni allaqachon yechib bo'lgansiz!\n"
                             "Iltimos yangi test yuklanishini kuting.")
            return
        success = "✅ Juda yaxshi!"
        info = (f"{msg.text} fani uchun test.\n\n"
                f"📝 Savollar soni: {test_app[4]}\n\n"
                f"Testni boshlash uchun \"👨‍💻 Testni boshlash\" tugmasini bosing!")
        markup = start_test_markup_uz
    else:
        if msg.text not in sciences_ru:
            await msg.delete()
            await msg.answer("‼️ Пожалуйста, используйте кнопки ниже!", reply_markup=sciences_ru_markup)
            return
        test_app = await db.select_test(sciences_dict.get(msg.text), data.get('language'))
        if test_app is False:
            await msg.answer(f"Сейчас нет теста по {msg.text}!")
            return
        if await db.select_result_test_user(msg.from_user.id, sciences_dict.get(msg.text)):
            await msg.answer("Вы уже завершили этот тест!\n"
                             "Пожалуйста, подождите загрузки нового теста.")
            return
        success = "✅ Очень хорошо!"
        info = (f"Тест по предмету {msg.text}\n\n"
                f"📝 Количество вопросов: {test_app[4]}\n\n"
                f"Нажмите кнопку \"👨‍💻 Начать тест\" для начала тестирования!")
        markup = start_test_markup_ru
    await state.update_data({'test_id': test_app[0], 'questions_count': test_app[4], 'time_continue': test_app[3]})
    message = await msg.answer(success, reply_markup=ReplyKeyboardRemove())
    await msg.answer(info, reply_markup=markup)
    await TestStatesGroup.next()
    time.sleep(2)
    await message.delete()


@dp.message_handler(state=TestStatesGroup.science, content_types=ContentType.ANY)
async def err_science_test(msg: types.Message, state: FSMContext):
    await msg.delete()
    data = await state.get_data()
    if data.get('language') == 'uzbek':
        await msg.answer("‼️ Iltimos, quyidagi tugmalardan foydalaning!",
                         reply_markup=sciences_uz_markup)
    else:
        await msg.answer("‼️ Пожалуйста, используйте кнопки ниже!",
                         reply_markup=sciences_ru_markup)


@dp.callback_query_handler(text="start_test", state=TestStatesGroup.ready)
async def start_test(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    test_id = data.get('test_id')
    question_num = 1
    question = await db.select_question(test_id, question_num)
    await state.update_data(
        {'question_number': question_num, 'responses': f'{question[4]}', 'start_time': datetime.datetime.now()})
    if data.get('language') == 'uzbek':
        test_info = (f"1-savol.\n\n"
                     f"{question[2]}")
    else:
        test_info = (f"Вопрос 1.\n\n"
                     f"{question[3]}")
    if question[5]:
        await state.update_data({'image': True})
        await call.message.delete()
        await call.message.answer_photo(question[5], caption=test_info,
                                        reply_markup=await make_keyboard_test_responses(data.get('language')))
    else:
        await state.update_data({'image': False})
        await call.message.delete()
        await call.message.answer(test_info, reply_markup=await make_keyboard_test_responses(data.get('language')))
    await TestStatesGroup.next()


@dp.message_handler(state=TestStatesGroup.ready, content_types=ContentType.ANY)
async def err_ready_test(msg: types.Message, state: FSMContext):
    await msg.delete()
    data = await state.get_data()
    if data.get('language') == 'uzbek':
        message = await msg.answer("‼️ Iltimos, tugmalardan foydalaning!")
    else:
        message = await msg.answer("‼️ Пожалуйста, используйте кнопки!")
    time.sleep(2)
    await message.delete()


# {'language': 'russian', 'science': 'ФИЗИКА', 'test_id': 1, 'questions_count': 5, 'question_number': 1, 'responses': 2}
@dp.callback_query_handler(callback_data.filter(), state=TestStatesGroup.execution)
async def select_response(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    data = await state.get_data()
    test_id = data.get('test_id')
    number = data.get('question_number')
    count = data.get('questions_count')
    user_resp = data.get('user_responses')
    current_resp = callback_data.get('response')
    responses = data.get('responses')
    markup = InlineKeyboardMarkup(inline_keyboard=None)
    # foydalanuvchini javoblarini saqlash
    if user_resp:
        await state.update_data({'user_responses': user_resp + current_resp})
    else:
        await state.update_data({'user_responses': f"{current_resp}"})
    # belgilangan javobni ko'rsatish
    if data.get('image'):
        if data.get('language') == 'uzbek':
            old_message = call.message.caption + f"\n\nSizning javobingiz: {responses_uz[int(current_resp) - 1]}"
        else:
            old_message = call.message.caption + f"\n\nВаш ответ: {responses_ru[int(current_resp) - 1]}"
        await call.message.edit_caption(old_message, reply_markup=markup)
    else:
        if data.get('language') == 'uzbek':
            old_message = call.message.text + f"\n\nSizning javobingiz: {responses_uz[int(current_resp) - 1]}"
        else:
            old_message = call.message.text + f"\n\nВаш ответ: {responses_ru[int(current_resp) - 1]}"
        await call.message.edit_text(old_message, reply_markup=markup)

    # test savollari tugaganligini tekshirish
    if number >= count:
        user = await db.select_user(call.from_user.id)
        db_responses = ''.join(
            map(lambda x, y: '1' if x == y else '0', responses, user_resp if user_resp else '' + current_resp))
        await db.add_test_result(test_id, call.from_user.id, data.get('language'), *user[3:8], data.get('science'),
                                 db_responses, datetime.datetime.now(), user[-1])
        if data.get('language') == 'uzbek':
            await call.message.answer("✅ Test yakunlandi!\n"
                                      f"Hurmatli {user[3]}, siz test savollarining "
                                      f"{db_responses.count('1')} tasiga to’g’ri va {db_responses.count('0')} "
                                      f"tasiga noto’g’ri javob berdingiz.",
                                      reply_markup=menu_test_uz)
        else:
            await call.message.answer("✅ Тест завершен!\n"
                                      f"Уважаемый(ая) {user[3]}, Вы ответили на "
                                      f"{db_responses.count('1')} вопросов теста правильно, а на "
                                      f"{db_responses.count('0')} — неправильно",
                                      reply_markup=menu_test_ru)
        await state.reset_state()
        await state.finish()
        return
    question = await db.select_question(test_id, number + 1)
    await state.update_data({'question_number': number + 1,
                             'responses': responses + str(question[4])})
    if data.get('language') == 'uzbek':
        test_info = (f"{number + 1}-savol.\n\n"
                     f"{question[2]}")
    else:
        test_info = (f"Вопрос {number + 1}.\n\n"
                     f"{question[3]}")
    if question[5]:
        await state.update_data({'image': True})
        await call.message.answer_photo(question[5], caption=test_info,
                                        reply_markup=await make_keyboard_test_responses(data.get('language')))
    else:
        await state.update_data({'image': False})
        await call.message.answer(test_info,
                                  reply_markup=await make_keyboard_test_responses(data.get('language')))


@dp.message_handler(state=TestStatesGroup.execution, content_types=ContentType.ANY)
async def err_ready_test(msg: types.Message, state: FSMContext):
    await msg.delete()
    data = await state.get_data()
    if data.get('language') == 'uzbek':
        message = await msg.answer("‼️ Iltimos, tugmalardan foydalaning!")
    else:
        message = await msg.answer("‼️ Пожалуйста, используйте кнопки!")
    time.sleep(2)
    await message.delete()
