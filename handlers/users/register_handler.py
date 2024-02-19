import json

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType, ReplyKeyboardRemove

from data.config import regions_uz, regions_ru, sciences_uz, sciences_ru
from keyboards.default import phone_ru_markup, phone_uz_markup, language_markup, region_uz_markup, region_ru_markup, \
    district_uz_markup, district_ru_markup, back_uz_button, back_ru_button, sciences_uz_markup, sciences_ru_markup, \
    make_lessons_uz_markup, make_lessons_ru_markup, menu_test_uz, menu_test_ru
from loader import dp, db
from states import RegisterStatesGroup


@dp.message_handler(text='O’zbek tili', state=RegisterStatesGroup.language)
async def language_uzbek(msg: types.Message, state: FSMContext):
    await state.update_data({'language': 'uzbek'})
    await msg.answer("Ro'yxatdan o'tish uchun ismingiz va familiyangizni kiriting.", reply_markup=ReplyKeyboardRemove())
    await RegisterStatesGroup.next()


@dp.message_handler(text='Русский язык', state=RegisterStatesGroup.language)
async def language_russian(msg: types.Message, state: FSMContext):
    await state.update_data({'language': 'russian'})
    await msg.answer("Для регистрации введите свое имя и фамилию.", reply_markup=ReplyKeyboardRemove())
    await RegisterStatesGroup.next()


@dp.message_handler(state=RegisterStatesGroup.language, content_types=ContentType.ANY)
async def err_language_choice(msg: types.Message):
    await msg.delete()
    await msg.answer("‼️ Iltimos, quyidagi tugmalardan foydalaning!\n\n"
                     "‼️ Пожалуйста, используйте кнопки ниже!",
                     reply_markup=language_markup)


@dp.message_handler(state=RegisterStatesGroup.fullname, content_types=ContentType.TEXT)
async def send_fullname(msg: types.Message, state: FSMContext):
    await state.update_data({'fullname': msg.text})
    data = await state.get_data()
    language = data.get('language')
    if language == 'uzbek':
        info = 'Endi pastdagi tugmani bosib, telefon raqamingizni yuboring.'
        markup = phone_uz_markup
    else:
        info = 'Теперь нажмите на кнопку ниже и отправьте свой номер телефона.'
        markup = phone_ru_markup
    await msg.answer(info, reply_markup=markup)
    await RegisterStatesGroup.next()


@dp.message_handler(state=RegisterStatesGroup.fullname, content_types=ContentType.ANY)
async def err_send_fullname(msg: types.Message, state: FSMContext):
    await msg.delete()
    data = await state.get_data()
    if data.get('language') == 'uzbek':
        await msg.answer("‼️ Iltimos, ism-familiyangizni kiriting!")
    else:
        await msg.answer("‼️ Пожалуйста, введите свое имя и фамилию!")


@dp.message_handler(state=RegisterStatesGroup.phone, content_types=ContentType.CONTACT)
async def send_phone(msg: types.Message, state: FSMContext):
    await state.update_data({'phone': msg.contact.phone_number})
    data = await state.get_data()
    language = data.get('language')
    if language == 'uzbek':
        if data.get('re_register') is None:
            if await db.select_user_phone(msg.contact.phone_number):
                await msg.reply(text="Ushbu raqam ro’yxatga olingan")
                return
        info = "O’zbekistonning qaysi hududidansiz?"
        markup = region_uz_markup
    else:
        if data.get('re_register') is None:
            if await db.select_user_phone(msg.contact.phone_number):
                await msg.reply(text="Этот номер зарегистрирован")
                return
        info = "В каком регионе Узбекистана вы проживаете?"
        markup = region_ru_markup
    await msg.answer(info, reply_markup=markup)
    await RegisterStatesGroup.next()


@dp.message_handler(state=RegisterStatesGroup.phone, content_types=ContentType.ANY)
async def err_send_phone(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    if data.get('language') == 'uzbek':
        err_info = "‼️ Iltimos, pastdagi tugmani bosib, telefon raqamingizni yuboring!"
        err_markup = phone_uz_markup
    else:
        err_info = "‼️ Пожалуйста, нажмите на кнопку ниже и отправьте свой номер телефона!"
        err_markup = phone_ru_markup
    await msg.delete()
    await msg.answer(err_info, reply_markup=err_markup)


@dp.message_handler(state=RegisterStatesGroup.region)
async def send_region(msg: types.Message, state: FSMContext):
    await state.update_data({'region': msg.text})
    data = await state.get_data()
    if data.get('language') == 'uzbek':
        if msg.text not in regions_uz:
            await msg.delete()
            await msg.answer("‼️ Iltimos, quyidagi tugmalardan foydalaning!",
                             reply_markup=region_uz_markup)
            return
        info = f"{msg.text}ning qaysi tumanidansiz?"
        markup = await district_uz_markup(msg.text)
    else:
        if msg.text not in regions_ru:
            await msg.delete()
            await msg.answer("‼️ Пожалуйста, используйте кнопки ниже!",
                             reply_markup=region_ru_markup)
            return
        info = f"В каком районе {msg.text} вы проживаете?"
        markup = await district_ru_markup(msg.text)
    await msg.answer(info, reply_markup=markup)
    await RegisterStatesGroup.next()


@dp.message_handler(state=RegisterStatesGroup.region, content_types=ContentType.ANY)
async def err_send_region(msg: types.Message, state: FSMContext):
    await msg.delete()
    data = await state.get_data()
    if data.get('language') == 'uzbek':
        await msg.answer("‼️ Iltimos, quyidagi tugmalardan foydalaning!",
                         reply_markup=region_uz_markup)
    else:
        await msg.answer("‼️ Пожалуйста, используйте кнопки ниже!",
                         reply_markup=region_ru_markup)


@dp.message_handler(state=RegisterStatesGroup.district)
async def send_district(msg: types.Message, state: FSMContext):
    await state.update_data({'district': msg.text})
    data = await state.get_data()
    if data.get('language') == 'uzbek':
        if msg.text == "⬅️ Orqaga":
            await msg.answer(f"O’zbekistonning qaysi hududidansiz?", reply_markup=region_uz_markup)
            await RegisterStatesGroup.previous()
            return
        with open('data/districts_uz.json', 'r') as file:
            districts = json.load(file).get(data.get('region'))
        if msg.text not in districts:
            await msg.delete()
            await msg.answer("‼️ Iltimos, quyidagi tugmalardan foydalaning!",
                             reply_markup=await district_uz_markup(data.get('region')))
            return
        info = "Maktabingiz raqamini kiriting."
        markup = back_uz_button
    else:
        if msg.text == '⬅️ Назад':
            await msg.answer(f"В каком регионе Узбекистана вы проживаете?", reply_markup=region_ru_markup)
            await RegisterStatesGroup.previous()
            return
        with open('data/districts_ru.json', 'r') as file:
            districts = json.load(file).get(data.get('region'))
        if msg.text not in districts:
            await msg.delete()
            await msg.answer("‼️ Пожалуйста, используйте кнопки ниже!",
                             reply_markup=await district_ru_markup(data.get('region')))
            return
        info = "Введите номер вашей школы."
        markup = back_ru_button
    await msg.answer(info, reply_markup=markup)
    await RegisterStatesGroup.next()


@dp.message_handler(state=RegisterStatesGroup.district, content_types=ContentType.ANY)
async def err_send_district(msg: types.Message, state: FSMContext):
    await msg.delete()
    data = await state.get_data()
    if data.get('language') == 'uzbek':
        await msg.answer("‼️ Iltimos, quyidagi tugmalardan foydalaning!",
                         reply_markup=await district_uz_markup(data.get('region')))
    else:
        await msg.answer("‼️ Пожалуйста, используйте кнопки ниже!",
                         reply_markup=await district_ru_markup(data.get('region')))


@dp.message_handler(state=RegisterStatesGroup.school)
async def send_school_number(msg: types.Message, state: FSMContext):
    await state.update_data({'school': msg.text})
    data = await state.get_data()
    if data.get('language') == 'uzbek':
        if msg.text == "⬅️ Orqaga":
            await msg.answer(f"{data.get('region')}ning qaysi tumanidansiz?",
                             reply_markup=await district_uz_markup(data.get('region')))
            await RegisterStatesGroup.previous()
            return
        info = "Qaysi fanlar bo’yicha onlayn darslarda ishtirok etasiz? (3 tagacha fan tanlash mumkin)"
        markup = await make_lessons_uz_markup()
    else:
        if msg.text == "⬅️ Назад":
            await msg.answer(f"В каком районе {data.get('region')} вы проживаете?",
                             reply_markup=await district_ru_markup(data.get('region')))
            await RegisterStatesGroup.previous()
            return
        info = "По каким предметам вы будете участвовать в онлайн-занятиях? (Можно выбрать до 3-х предметов)"
        markup = await make_lessons_ru_markup()
    await msg.answer(info, reply_markup=markup)
    await RegisterStatesGroup.next()


@dp.message_handler(state=RegisterStatesGroup.school, content_types=ContentType.ANY)
async def err_send_school(msg: types.Message, state: FSMContext):
    await msg.delete()
    data = await state.get_data()
    if data.get('language') == 'uzbek':
        await msg.answer("‼️ Iltimos, maktabingiz raqamini kiriting!",
                         reply_markup=back_uz_button)
    else:
        await msg.answer("‼️ Пожалуйста, введите номер вашей школы!",
                         reply_markup=back_ru_button)


@dp.message_handler(state=RegisterStatesGroup.online_sc)
async def choice_online_lesson(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    sc1, sc2, sc3 = data.get('sc1'), data.get('sc2'), data.get('sc3')
    if data.get('language') == 'uzbek':
        if msg.text == '⬅️ Orqaga':
            await msg.answer("Maktabingiz raqamini kiriting.", reply_markup=back_uz_button)
            await state.update_data({'sc1': None, 'sc2': None, 'sc3': None})
            await RegisterStatesGroup.previous()
            return
        if msg.text in ('ONLAYN DARSLARDA ISHTIROK ETMAYMAN', "✅ Tanlab bo'ldim!"):
            await msg.answer("Qaysi fandan olimpiadada ishtirok etasiz?", reply_markup=sciences_uz_markup)
            await RegisterStatesGroup.next()
            return
        if msg.text not in sciences_uz:
            await msg.answer("‼️ Iltimos, quyidagi tugmalardan foydalaning!", reply_markup=await make_lessons_uz_markup(sc1, sc2, sc3))
            return
        if sc1 is None:
            await state.update_data({'sc1': msg.text})
            sc1 = msg.text
            sc2 = '-'
            sc3 = '-'
        elif sc2 is None:
            await state.update_data({'sc2': msg.text})
            sc2 = msg.text
            sc3 = '-'
        else:
            await state.update_data({'sc3': msg.text})
            sc3 = msg.text
            info_next = "Qaysi fandan olimpiadada ishtirok etasiz?"
            markup_next = sciences_uz_markup
        info = (f"Yana tanlash uchun quyidagi tugmalardan foydalaning.\n\n"
                f"Sizning tanlagan fanlaringiz:\n"
                f"1. {sc1}\n"
                f"2. {sc2}\n"
                f"3. {sc3}")
        markup = await make_lessons_uz_markup(sc1, sc2, sc3)
    else:
        if msg.text == '⬅️ Назад':
            await msg.answer("Введите номер вашей школы.", reply_markup=back_ru_button)
            await state.update_data({'sc1': None, 'sc2': None, 'sc3': None})
            await RegisterStatesGroup.previous()
            return
        if msg.text in ('Я НЕ БУДУ УЧАСТВОВАТЬ В ОНЛАЙН-ЗАНЯТИЯХ', "✅ я выбрал!"):
            await msg.answer("По какому предмету вы будете участвовать в олимпиаде?", reply_markup=sciences_ru_markup)
            await RegisterStatesGroup.next()
            return
        if msg.text not in sciences_ru:
            await msg.answer("‼️ Пожалуйста, используйте кнопки ниже!", reply_markup=await make_lessons_ru_markup(sc1, sc2, sc3))
            return
        if sc1 is None:
            await state.update_data({'sc1': msg.text})
            sc1 = msg.text
            sc2 = '-'
            sc3 = '-'
        elif sc2 is None:
            await state.update_data({'sc2': msg.text})
            sc2 = msg.text
            sc3 = '-'
        else:
            await state.update_data({'sc3': msg.text})
            sc3 = msg.text
            info_next = "По какому предмету вы будете участвовать в олимпиаде?"
            markup_next = sciences_ru_markup
        info = (f"Используйте следующие кнопки для дополнительного выбора.\n\n"
                f"Ваши выбранные предметы:\n"
                f"1. {sc1}\n"
                f"2. {sc2}\n"
                f"3. {sc3}")
        markup = await make_lessons_ru_markup(sc1, sc2, sc3)
    await msg.answer(info, reply_markup=markup)
    if sc3 != '-':
        await msg.answer(info_next, reply_markup=markup_next)
        await RegisterStatesGroup.next()


@dp.message_handler(state=RegisterStatesGroup.online_sc, content_types=ContentType.ANY)
async def err_online_lessons(msg: types.Message, state: FSMContext):
    await msg.delete()
    data = await state.get_data()
    sc1, sc2, sc3 = data.get('sc1'), data.get('sc2'), data.get('sc3')
    if data.get('language') == 'uzbek':
        await msg.answer("‼️ Iltimos, quyidagi tugmalardan foydalaning!",
                         reply_markup=await make_lessons_uz_markup(sc1, sc2, sc3))
    else:
        await msg.answer("‼️ Пожалуйста, используйте кнопки ниже!",
                         reply_markup=await make_lessons_ru_markup(sc1, sc2, sc3))


@dp.message_handler(state=RegisterStatesGroup.science)
async def send_science(msg: types.Message, state: FSMContext):
    await state.update_data({'science': msg.text})
    data = await state.get_data()
    if data.get('language') == 'uzbek':
        if msg.text == '⬅️ Orqaga':
            await msg.answer("Qaysi fanlar bo’yicha onlayn darslarda ishtirok etasiz? (3 tagacha fan tanlash mumkin)",
                             reply_markup=await make_lessons_uz_markup())
            await state.update_data({'sc1': None, 'sc2': None, 'sc3': None})
            await RegisterStatesGroup.previous()
            return
        if msg.text not in sciences_uz:
            await msg.answer("‼️ Iltimos, quyidagi tugmalardan foydalaning!", reply_markup=sciences_uz_markup)
            return
        info = ("Tabriklaymiz! Siz ro’yxatdan muvaffaqiyatli o’tdingiz.\n\n"
                "Loyiha yangiliklari haqida boxabar bo'lib "
                "turish uchun kanalimizga a'zo bo'ling 👉 https://t.me/FanJavohirlari\n\n"
                "Test topshirib ko’rish uchun quyidagi tugmani bosing.")
        markup = menu_test_uz
    else:
        if msg.text == '⬅️ Назад':
            await msg.answer("По каким предметам вы будете участвовать в онлайн-занятиях? (Можно выбрать до 3-х "
                             "предметов)",
                             reply_markup=await make_lessons_ru_markup())
            await state.update_data({'sc1': None, 'sc2': None, 'sc3': None})
            await RegisterStatesGroup.previous()
            return
        if msg.text not in sciences_ru:
            await msg.answer("‼️ Пожалуйста, используйте кнопки ниже!", reply_markup=sciences_ru_markup)
            return
        info = ("Поздравляем! Вы успешно зарегистрировались.\n\n"
                "Подпишитесь на наш канал, чтобы быть в курсе новостей "
                "проекта 👉 https://t.me/FanJavohirlari\n\n"
                "Чтобы попробовать пройти тест, нажмите кнопку ниже.")
        markup = menu_test_ru
    await msg.answer(info, reply_markup=markup)
    await db.add_or_update_user(tg_id=msg.from_user.id, **data)
    await state.reset_state()
    await state.finish()


@dp.message_handler(state=RegisterStatesGroup.science, content_types=ContentType.ANY)
async def err_send_science(msg: types.Message, state: FSMContext):
    await msg.delete()
    data = await state.get_data()
    if data.get('language') == 'uzbek':
        await msg.answer("‼️ Iltimos, quyidagi tugmalardan foydalaning!",
                         reply_markup=sciences_uz_markup)
    else:
        await msg.answer("‼️ Пожалуйста, используйте кнопки ниже!",
                         reply_markup=sciences_ru_markup)
