import json

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType, ReplyKeyboardRemove

from data.config import regions_uz, regions_ru, sciences_uz, sciences_ru
from keyboards.default import phone_ru_markup, phone_uz_markup, language_markup, region_uz_markup, region_ru_markup, \
    district_uz_markup, district_ru_markup, back_uz_button, back_ru_button, sciences_uz_markup, sciences_ru_markup
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
        info = "O’zbekistonning qaysi hududidansiz?"
        markup = region_uz_markup
    else:
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
        info = "Qaysi fanlar sizga qiziq va qaysi fanlar bo’yicha olimpiadada ishtirok etasiz?"
        markup = sciences_uz_markup
    else:
        if msg.text == "⬅️ Назад":
            await msg.answer(f"В каком районе {data.get('region')} вы проживаете?",
                             reply_markup=await district_ru_markup(data.get('region')))
            await RegisterStatesGroup.previous()
            return
        info = "Какие предметы вам интересны и по каким предметам вы будете участвовать в олимпиаде?"
        markup = sciences_ru_markup
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


@dp.message_handler(state=RegisterStatesGroup.science)
async def send_science(msg: types.Message, state: FSMContext):
    await state.update_data({'science': msg.text})
    data = await state.get_data()
    if data.get('language') == 'uzbek':
        if msg.text == '⬅️ Orqaga':
            await msg.answer("Maktabingiz raqamini kiriting.", reply_markup=back_uz_button)
            await RegisterStatesGroup.previous()
            return
        if msg.text not in sciences_uz:
            await msg.answer("‼️ Iltimos, quyidagi tugmalardan foydalaning!", reply_markup=sciences_uz_markup)
            return
        info = ("Tabriklaymiz! Siz ro’yxatdan muvaffaqiyatli o’tdingiz. Loyiha yangiliklari haqida boxabar bo'lib "
                "turish uchun kanalimizga a'zo bo'ling 👉 https://t.me/FanJavohirlari")
    else:
        if msg.text == '⬅️ Назад':
            await msg.answer("Введите номер вашей школы.", reply_markup=back_ru_button)
            await RegisterStatesGroup.previous()
            return
        if msg.text not in sciences_ru:
            await msg.answer("‼️ Пожалуйста, используйте кнопки ниже!", reply_markup=sciences_ru_markup)
        info = ("Поздравляем! Вы успешно зарегистрировались. Подпишитесь на наш канал, чтобы быть в курсе новостей "
                "проекта 👉 https://t.me/FanJavohirlari")
    await msg.answer(info, reply_markup=ReplyKeyboardRemove())
    await db.add_or_update_user(tg_id=msg.from_user.id, **data)
    # await state.reset_state()
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
