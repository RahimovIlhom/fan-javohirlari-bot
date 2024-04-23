import asyncio
import datetime
import os
import time

import pytz
from aiogram import types
from aiogram.types import ReplyKeyboardRemove, ContentType, InlineKeyboardMarkup, InputFile
from aiogram.dispatcher import FSMContext

from data.config import sciences_uz, sciences_ru, sciences_dict, responses_uz, responses_ru
from filters import IsPrivate
from keyboards.default import sciences_uz_markup, sciences_ru_markup, menu_test_ru, menu_test_uz, id_card_uz_markup, \
    id_card_ru_markup
from keyboards.inline import start_test_markup_uz, start_test_markup_ru, make_keyboard_test_responses, callback_data, \
    download_certificate_markup_uz, download_certificate_markup_ru
from loader import dp, db
from states import TestStatesGroup, PINFLStateGroup
from utils.db_api import post_or_put_result
from utils.misc.create_certificate import create_certificate, photo_link


@dp.message_handler(IsPrivate(), text="👨‍💻 TEST TOPSHIRISH")
async def solution_test_uz(msg: types.Message, state: FSMContext):
    user = await db.select_user(msg.from_user.id)
    if user is None:
        await msg.answer("‼️ Siz ro'yxatdan o'tmaganingiz uchun test topshira olmaysiz!\n"
                         "Ro'yxatdan o'tish uchun - /start", reply_markup=ReplyKeyboardRemove())
        return
    await state.set_data({'language': 'uzbek'})
    if user[-1] is None:
        result = ("⚠️ Botdan foydalanish uchun ID-kartangizdagi Shaxsiy raqamingizni kiriting. ID karta olmagan "
                  "bo’lsangiz pastda “Hali ID karta olmaganman” tugmasini bosing.")
        image = InputFile('data/images/pinfl.jpg')
        image_url = "http://telegra.ph//file/97b3043fbcdc89ba48360.jpg"
        try:
            await msg.answer_photo(image_url, caption=result, reply_markup=id_card_uz_markup)
        except:
            await msg.answer_photo(image, caption=result, reply_markup=id_card_uz_markup)
        await PINFLStateGroup.pinfl.set()
        return
    await msg.reply("Olimpiada vaqtida test topshira olmaysiz!")
    return
    info = f"Qaysi fandan test topshirmoqchisiz?"
    await msg.answer(info, reply_markup=sciences_uz_markup)
    await state.set_state(TestStatesGroup.science)


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

    # if await db.select_result_test_user(msg.from_user.id, user[8], True):
    #     await msg.answer(f"{user[8]} fanidan olimpiada testini yechib bo'lgansiz!\n"
    #                      f"Sertifikatingizni yuklab olish uchun quyidagi tugmani bosing.",
    #                      reply_markup=download_certificate_markup_uz)
    #     return

    start_localized_datetime = test_app[8]
    stop_localized_datetime = test_app[6]
    now_localized_datetime = datetime.datetime.now()

    if now_localized_datetime < start_localized_datetime:
        await msg.answer(f"{user[8]} fanidan olimpiada test sinovlari {test_app[8].date()} soat 00:00da boshlanadi!")
    elif now_localized_datetime < stop_localized_datetime:
        await start_olympiad_test_uz(msg, state, test_app, user[8])
    else:
        await msg.answer(f"{user[8]} fanidan olimpiada test sinovlari {test_app[6].date()} soat 00:00da yakunlangan!")


async def start_olympiad_test_uz(msg: types.Message, state: FSMContext, test_app, subject):
    info = (f"OLIMPIADA (1-bosqich)\n\n"
            f"Fan: {subject}\n\n"
            f"📝 Savollar soni: {test_app[4]}\n\n"
            f"Testni boshlash uchun \"👨‍💻 Testni boshlash\" tugmasini bosing!")

    await state.update_data({
        'language': 'uzbek',
        'test_id': test_app[0],
        'questions_count': test_app[4],
        'science': subject,
        'olympiad_test': True
    })
    success = "✅ Juda yaxshi!"
    await state.set_state(TestStatesGroup.ready)
    message = await msg.answer(success, reply_markup=ReplyKeyboardRemove())
    await msg.answer(info, reply_markup=start_test_markup_uz)
    await asyncio.sleep(1)
    await message.delete()


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

    # if await db.select_result_test_user(msg.from_user.id, sciences_dict.get(user[8]), True):
    #     await msg.answer(f"Вы успешно сдали олимпиадный тест по {user[8]} предмету!\n"
    #                      f"Для загрузки вашего сертификата нажмите на следующую кнопку.",
    #                      reply_markup=download_certificate_markup_ru)
    #     return

    start_localized_datetime = test_app[8].date()
    stop_localized_datetime = test_app[6].date()
    now_localized_datetime = datetime.datetime.now()

    if now_localized_datetime < start_localized_datetime:
        await msg.answer(f"Олимпиадное тестирование по {user[8]} начнется {test_app[8].date()} в 00:00!")
    elif now_localized_datetime < stop_localized_datetime:
        await start_olympiad_test(msg, state, test_app, user[8])
    else:
        await msg.answer(f"Тест по {user[8]} для олимпиады завершён {test_app[6].date()} в 00:00!")


async def start_olympiad_test(msg: types.Message, state: FSMContext, test_app, subject):
    info = (f"ОЛИМПИАДА (1-й этап)\n\n"
            f"Предмет: {subject}\n\n"
            f"📝 Количество вопросов: {test_app[4]}\n\n"
            f"Нажмите кнопку \"👨‍💻 Начать тест\" для начала тестирования!")

    await state.update_data({
        'language': 'russian',
        'test_id': test_app[0],
        'questions_count': test_app[4],
        'science': subject,
        'olympiad_test': True
    })

    success = "✅ Очень хорошо!"
    await state.set_state(TestStatesGroup.ready)
    message = await msg.answer(success, reply_markup=ReplyKeyboardRemove())
    await msg.answer(info, reply_markup=start_test_markup_ru)
    await asyncio.sleep(1)
    await message.delete()


@dp.message_handler(IsPrivate(), text="👨‍💻 ПРОЙТИ ТЕСТ")
async def solution_test_ru(msg: types.Message, state: FSMContext):
    user = await db.select_user(msg.from_user.id)
    if user is None:
        await msg.answer("‼️ Вы не можете пройти тест, не зарегистрировавшись!\n"
                         "Для регистрации - /start", reply_markup=ReplyKeyboardRemove())
        return
    await state.set_data({'language': 'russian'})
    if user[-1] is None:
        result = ("Введите персональный идентификационный номер, указанный на ID-карте. Если вы еще не получили "
                  "ID-карту, нажмите кнопку «Я еще не получил ID-карту» ниже.")
        image = InputFile('data/images/pinfl_ru.jpg')
        image_url = "http://telegra.ph//file/e815e58a3c4c08948b617.jpg"
        try:
            await msg.answer_photo(image_url, caption=result, reply_markup=id_card_ru_markup)
        except:
            await msg.answer_photo(image, caption=result, reply_markup=id_card_ru_markup)
        await PINFLStateGroup.pinfl.set()
        return
    await msg.reply("Во время Олимпиады тест сдавать нельзя!")
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
    questions = list(await db.select_questions_test_id(test_id))
    question = questions[0]
    questions.pop(0)
    await state.update_data(
        {'question_number': question_num, 'responses': f'{question[4]}', 'start_time': datetime.datetime.now()})
    if data.get('language') == 'uzbek':
        test_info = (f"1-savol.\n\n"
                     f"{question[2].replace('>', '&gt').replace('<', '&lt')}")
    else:
        test_info = (f"Вопрос 1.\n\n"
                     f"{question[3].replace('>', '&gt').replace('<', '&lt')}")
    await state.update_data({'image': bool(question[5]), 'questions': questions})
    if question[5]:
        await call.message.delete()
        await call.message.answer_photo(question[5], caption=test_info,
                                        reply_markup=await make_keyboard_test_responses(data.get('language')))
    else:
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
async def handle_callback_query(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    data = await state.get_data()
    questions, test_id, number, count, user_resp, current_resp, responses, language, image = (
        data.get('questions'),
        data.get('test_id'),
        data.get('question_number'),
        data.get('questions_count'),
        data.get('user_responses', ''),
        int(callback_data.get('response')),
        data.get('responses', ''),
        data.get('language'),
        data.get('image', False)
    )

    user_resp += str(current_resp)
    await state.update_data({'user_responses': user_resp})

    text_template = "{}\n\nВаш ответ: {}" if language != 'uzbek' else "{}\n\nSizning javobingiz: {}"
    if image:
        caption = text_template.format(call.message.caption, responses_uz[int(current_resp) - 1] if language == 'uzbek' else responses_ru[int(current_resp) - 1])
    else:
        caption = text_template.format(call.message.text, responses_uz[int(current_resp) - 1] if language == 'uzbek' else responses_ru[int(current_resp) - 1])

    await call.message.edit_caption(caption.replace('>', '&gt').replace('<', '&lt'), reply_markup=None) if image else await call.message.edit_text(caption.replace('>', '&gt').replace('<', '&lt'), reply_markup=None)

    if questions:
        question = questions[0]
        questions.pop(0)
    else:
        await TestStatesGroup.next()
        await handle_test_completion(call, state, test_id, user_resp, language, responses)
        return

    if number >= count:
        await TestStatesGroup.next()
        await handle_test_completion(call, state, test_id, user_resp, language, responses)
        return

    await state.update_data({'question_number': number + 1, 'responses': responses + str(question[4]), 'image': bool(question[5]), 'questions': questions})

    test_info_template = "Вопрос {}.\n\n{}" if language != 'uzbek' else "{}-savol.\n\n{}"
    test_info = test_info_template.format(number + 1, question[3 if language != 'uzbek' else 2].replace('>', '&gt').replace('<', '&lt'))

    if bool(question[5]):
        await call.message.answer_photo(question[5], caption=test_info, reply_markup=await make_keyboard_test_responses(language))
    else:
        await call.message.answer(test_info, reply_markup=await make_keyboard_test_responses(language))


async def handle_test_completion(call, state, test_id, user_resp, language, responses):
    data = await state.get_data()
    user_id = call.from_user.id
    user = await db.select_user(user_id)
    user_name = user[3]
    db_responses = ''.join(['1' if x == y else '0' for x, y in zip(responses, user_resp)])
    true_response_count = db_responses.count('1')

    if data.get('olympiad_test'):
        text1 = ("✅ Olimpiada testi yakunlandi!\n\nHurmatli {}, siz test savollarining {} tasiga to'g'ri javob berib, "
                 "{} ballni qo'lga kiritdingiz.\n\nTabriklaymiz, siz olimpiadaning 2-bosqichiga o'tdingiz. 2-bosqich "
                 "may oyida Fan va texnologiyalar universitetining binosida bo'lib o'tadi.\n\nShu bilan birga, "
                 "siz 2 million so'mlik vaucherni ham qo'lga kiritdingiz. Ushbu vaucherni Fan va texnologiyalar "
                 "universitetida kunduzgi ta'lim shaklidagi shartnoma to'lovi uchun bir martalik chegirma sifatida "
                 "ishlatishingiz mumkin.\n\nFan va texnologiyalar universitetining yangiliklaridan xabardor bo'lib "
                 "turish uchun @usatuzb telegram kanaliga a'zo bo'lishingiz mumkin. Batafsil ma'lumot uchun "
                 "78-888-38-88 telefon raqamiga qo'ng'iroq qiling.\n\nBizni sizni kutamiz!")
        text2 = ("✅ Olimpiada testi yakunlandi!\n\nHurmatli {}, siz test savollarining {} tasiga to'g'ri javob berib, "
                 "{} ballni qo'lga kiritdingiz.\n\nTabriklaymiz, siz olimpiadaning 2-bosqichiga o'tdingiz. 2-bosqich "
                 "may oyida Fan va texnologiyalar universitetining binosida bo'lib o'tadi. \n\nShu bilan birga, "
                 "siz 1,5 million so'mlik vaucherni ham qo'lga kiritdingiz. Ushbu vaucherni Fan va texnologiyalar "
                 "universitetida kunduzgi ta'lim shaklidagi shartnoma to'lovi uchun bir martalik chegirma sifatida "
                 "ishlatishingiz mumkin.\n\nFan va texnologiyalar universitetining yangiliklaridan xabardor bo'lib "
                 "turish uchun @usatuzb telegram kanaliga a'zo bo'lishingiz mumkin. Batafsil ma'lumot uchun "
                 "78-888-38-88 telefon raqamiga qo'ng'iroq qiling.\n\nBizni sizni kutamiz!")
        text3 = ("✅ Olimpiada testi yakunlandi!\n\nHurmatli {}, siz test savollarining {} tasiga to'g'ri javob berib, "
                 "{} ballni qo'lga kiritdingiz.\n\nTabriklaymiz, siz olimpiadada muvaffaqiyatli ishtirok etdingiz, "
                 "ammo 2-bosqichda ishtirok etish uchun yetarlicha ball to'play olmadingiz. "
                 "\n\nShunga qaramay, universitetimizda ta'lim olish istagini bildirganingiz va faolligingiz uchun "
                 "sizga qiymati 1 million so'mlik vaucherni taqdim etamiz. Ushbu vaucherni Fan va texnologiyalar "
                 "universitetida kunduzgi ta'lim shaklidagi shartnoma to'lovi uchun bir martalik chegirma sifatida "
                 "ishlatishingiz mumkin. Shu bilan birga, Fan va texnologiyalar universitetiga hujjatlaringizni "
                 "topshirsangiz, sizni imtihonlarsiz qabul qilamiz."
                 "\n\nFan va texnologiyalar universitetining yangiliklaridan xabardor bo'lib turish uchun "
                 "@usatuzb telegram kanaliga a'zo bo'lishingiz mumkin. Batafsil ma'lumot uchun 78-888-38-88 telefon "
                 "raqamiga qo'ng'iroq qiling.\n\nSiz bilan universitetimizning talabasi sifatida uchrashishimizni "
                 "sabrsizlik bilan kutib qolamiz! 🤗")
        text4 = ("✅ Olimpiada testi yakunlandi!\n\nHurmatli {}, siz test savollarining {} tasiga to'g'ri javob berib, "
                 "{} ballni qo'lga kiritdingiz.\n\nAfsuski, siz olimpiadaning 2-bosqichida ishtirok etish uchun "
                 "yetarlicha ball to'play olmadingiz. \n\nAmmo hech tushkunlikka tushmang. Yaqin kunlarda "
                 "universitetimizda 2024/2025 o'quv yili uchun qabul boshlanadi va siz hujjatlaringizni hamda "
                 "imtihonni onlayn topshirib, o'z kuchingizni yana sinab ko'rishingiz mumkin bo'ladi.\n\nFan va "
                 "texnologiyalar universitetining yangiliklaridan xabardor bo'lib turish uchun @usatuzb telegram "
                 "kanaliga a'zo bo'lishingiz mumkin. Batafsil ma'lumot uchun 78-888-38-88 telefon raqamiga qo'ng'iroq "
                 "qiling.\n\nSiz bilan universitetimizning talabasi sifatida uchrashishimizni sabrsizlik bilan kutib "
                 "qolamiz! 🤗")

        result = true_response_count / len(db_responses)
        image_index = (2 if result >= 0.85 else 1 if result >= 0.65 else 0) if result > 0.33 else 3
        info_template = (text1 if result >= 0.85 else text2 if result >= 0.65 else text3) if result > 0.33 else text4

        info = info_template.format(user_name, true_response_count, true_response_count*2)
        await call.message.answer(info, reply_markup=menu_test_uz if language == 'uzbek' else menu_test_ru)

        image_path = await create_certificate(user_id=user_id, fullname=user[3], image_index=image_index, science=user[8], language=language)
        await call.message.answer_photo(InputFile(image_path), caption="Sizni sertifikat bilan tabriklaymiz!")
        image_url = await photo_link(image_path)
        await db.add_test_result(test_id, user_id, language, *user[3:8], data.get('science'),
                                 db_responses, datetime.datetime.now(), user[-1], image_url, data.get('olympiad_test'))
        await post_or_put_result(user[0], user_id, result, image_url)
        os.remove(image_path) if os.path.exists(image_path) else None
    else:
        info_template = "✅ Test yakunlandi!\nHurmatli {}, siz test savollarining {} tasiga to’g’ri va {} tasiga noto’g’ri javob berdingiz." if language == 'uzbek' else "✅ Тест завершен!\nУважаемый(ая) {}, Вы ответили на {} вопросов теста правильно, а на {} — неправильно."
        info = info_template.format(user_name, db_responses.count('1'), db_responses.count('0'))
        await call.message.answer(info, reply_markup=menu_test_uz if language == 'uzbek' else menu_test_ru)
        image_url = None
        await db.add_test_result(test_id, user_id, language, *user[3:8], data.get('science'),
                                 db_responses, datetime.datetime.now(), user[-1], image_url, data.get('olympiad_test'))
    await state.reset_data()
    await state.finish()


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
