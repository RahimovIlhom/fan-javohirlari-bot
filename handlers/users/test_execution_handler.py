import datetime
import time

from aiogram import types
from aiogram.types import ReplyKeyboardRemove, ContentType, InlineKeyboardMarkup, InputFile
from aiogram.dispatcher import FSMContext

from data.config import sciences_uz, sciences_ru, sciences_dict, responses_uz, responses_ru
from filters import IsPrivate
from keyboards.default import sciences_uz_markup, sciences_ru_markup, menu_test_ru, menu_test_uz
from keyboards.inline import start_test_markup_uz, start_test_markup_ru, make_keyboard_test_responses, callback_data
from loader import dp, db
from states import TestStatesGroup, PINFLStateGroup


@dp.message_handler(IsPrivate(), text="TEST TOPSHIRISH")
async def solution_test_uz(msg: types.Message, state: FSMContext):
    user = await db.select_user(msg.from_user.id)
    if user is None:
        await msg.answer("‼️ Siz ro'yxatdan o'tmaganingiz uchun test topshira olmaysiz!\n"
                         "Ro'yxatdan o'tish uchun - /start", reply_markup=ReplyKeyboardRemove())
        return
    await state.set_data({'language': 'uzbek'})
    if user[-1] is None:
        result = "⚠️ Botdan foydalanish JSHSHIR (PINFL) raqamingizni kiriting:"
        image = InputFile('data/images/jshshir.jpg')
        await msg.answer_photo(image, caption=result, reply_markup=ReplyKeyboardRemove())
        await PINFLStateGroup.pinfl.set()
        return
    info = f"Qaysi fandan test topshirmoqchisiz?"
    await msg.answer(info, reply_markup=sciences_uz_markup)
    await state.set_state(TestStatesGroup.science)


@dp.message_handler(IsPrivate(), text="ПРОЙТИ ТЕСТ")
async def solution_test_ru(msg: types.Message, state: FSMContext):
    user = await db.select_user(msg.from_user.id)
    if user is None:
        await msg.answer("‼️ Вы не можете пройти тест, не зарегистрировавшись!\n"
                         "Для регистрации - /start", reply_markup=ReplyKeyboardRemove())
        return
    await state.set_data({'language': 'russian'})
    if user[-1] is None:
        result = "⚠️ Введите свой номер ИНН (PINFL) для использования ботом:"
        image = InputFile('data/images/jshshir.jpg')
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
        print(test_app)
        if test_app is False:
            await msg.answer("Hali test mavjud emas!")
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
            await msg.answer("Тест еще не существует!")
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
            map(lambda x, y: '1' if x == y else '0', responses, user_resp + current_resp))
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
