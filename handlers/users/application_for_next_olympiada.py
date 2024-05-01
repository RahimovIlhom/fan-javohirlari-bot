import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove, ContentType

from filters import IsPrivate
from keyboards.default import menu_user_markup
from keyboards.inline import participation_choices, are_you_graduate, choices_olympiad_science, my_name_is_right, \
    sciences_callback_data
from loader import dp, db
from states import ApplicationOlympiad


@dp.message_handler(IsPrivate(), text="🏆 OLIMPIADA (2-bosqich) UCHUN ARIZA")
async def application_next_level_olympiad(msg: types.Message):
    if not await db.get_next_olympiad_user(msg.from_user.id):
        test_result = await db.select_result_user(msg.from_user.id)
        if test_result:
            info = ("Hurmatli {}! Sizni yana bir bor \"Fan javohirlari\" olimpiadasining 2-bosqichiga o'tganingiz bilan "
                    "tabriklaymiz! Olimpiadaning 2-bosqichi Toshkent shahridagi Fan va texnologiyalar universitetida "
                    "oflayn bo'lib o'tadi.  "
                    "\n\nAytingchi, siz Toshkentga universitet binosiga kelib, olimpiadada ishtirok etasizmi?")
            await msg.answer(info.format(test_result[0][2]), reply_markup=participation_choices)
        else:
            await msg.answer("Siz Fan olimpiadasida 2-bosqichga o'ta olmagansiz!",
                             reply_markup=await menu_user_markup(msg.from_user.id))
    else:
        await msg.answer("Siz allaqachon 2-bosqich olimpiada uchun ro'yxatdan o'tgansiz!",
                         reply_markup=await menu_user_markup(msg.from_user.id))


@dp.callback_query_handler(text='application')
async def application_next_level_olympiad2(call: types.CallbackQuery):
    if not await db.get_next_olympiad_user(call.from_user.id):
        test_result = await db.select_result_user(call.from_user.id)
        if test_result:
            info = ("Hurmatli {}! Sizni yana bir bor \"Fan javohirlari\" olimpiadasining 2-bosqichiga o'tganingiz bilan"
                    "tabriklaymiz! Olimpiadaning 2-bosqichi Toshkent shahridagi Fan va texnologiyalar universitetida "
                    "oflayn bo'lib o'tadi.  "
                    "\n\nAytingchi, siz Toshkentga universitet binosiga kelib, olimpiadada ishtirok etasizmi?")
            await call.message.edit_text(info.format(test_result[0][2]), reply_markup=participation_choices)
        else:
            await call.message.delete()
            await call.message.answer("Siz Fan olimpiadasida 2-bosqichga o'ta olmagansiz!",
                                      reply_markup=await menu_user_markup(call.from_user.id))
    else:
        await call.message.delete()
        await call.message.answer("Siz allaqachon 2-bosqich olimpiada uchun ro'yxatdan o'tgansiz!",
                                  reply_markup=await menu_user_markup(call.from_user.id))


@dp.callback_query_handler(text="yes_go")
async def yes_or_no_graduate(call: types.CallbackQuery, state: FSMContext):
    answer = ("Eslatib o'tamiz, olimpiadaning 2-bosqichida faqat maktab bitiruvchi sinflari (11-sinflar), "
              "akademik litsey, kollej va texnikum bitiruvchilari ishtirok etishlari mumkin.\n\nIltimos, "
              "siz ham bitiruvchi sinf o'quvchisi ekanligingizni tasdiqlang.")
    await call.message.edit_text(answer, reply_markup=are_you_graduate)
    await state.set_state(ApplicationOlympiad.graduate)


@dp.callback_query_handler(text="no_go")
async def no_go_olympian(call: types.CallbackQuery):
    resp = ("Afsuslanmang, universitetimizda ta'lim olish istagini bildirganingiz va faolligingiz uchun sizga "
            "minnatdorlik bildiramiz!\n\nShu bilan birga eslatib o'tamiz, 1-bosqichda qo'lga kiritgan vaucheringizni "
            "Fan va texnologiyalar universitetida shartnoma to'lovi uchun bir martalik chegirma sifatida "
            "ishlatishingiz mumkin. Shu bilan birga, 1-bosqichda muvaffaqiyatli ishtirok etganingiz sababli sizni Fan "
            "va texnologiyalar universitetiga imtihonlarsiz qabul qilamiz. Hujjatlaringizni onlayn "
            "https://admission.usat.uz saytida ro'yxatdan o'tib, topshirishingiz mumkin.\n\nFan va texnologiyalar "
            "universitetining yangiliklaridan xabardor bo'lib turish uchun @usatuzb telegram kanaliga a'zo bo'lishni "
            "unutmang! Savollaringiz bo'lsa, 78-888-38-88 telefon raqamiga qo'ng'iroq qiling.\n\nSiz bilan "
            "universitetimizning talabasi sifatida uchrashishimizni sabrsizlik bilan kutib qolamiz! 🤗")
    await call.message.edit_text(resp, reply_markup=None)


@dp.callback_query_handler(text="yes_graduate", state=ApplicationOlympiad.graduate)
async def yes_or_no_graduate(call: types.CallbackQuery, state: FSMContext):
    test_result = await db.select_result_user(call.from_user.id)
    await state.set_data({'test_result': test_result})
    if len(test_result) > 1:
        answer = ("Olimpiadaning 2-bosqichida bitta abituriyent bitta fandan ishtirok etishi mumkin. Aytingchi, "
                  "siz qaysi fandan ishtirok etasiz?")
        await call.message.edit_text(answer, reply_markup=await choices_olympiad_science(test_result))
        await ApplicationOlympiad.next()
    else:
        await true_fullname(call, state)


@dp.callback_query_handler(sciences_callback_data.filter(), state=ApplicationOlympiad.science)
async def choice_olympiad_science(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    science = callback_data.get('science')
    await state.update_data({'science': science})
    await ApplicationOlympiad.next()
    await true_fullname(call, state)


@dp.callback_query_handler(text="no_graduate", state=ApplicationOlympiad.graduate)
async def yes_or_no_graduate(call: types.CallbackQuery, state: FSMContext):
    resp = ("Afsuski, olimpiadaning 2-bosqichida faqat maktab bitiruvchi sinflari (11-sinflar), akademik litsey, "
            "kollej va texnikum bitiruvchilari ishtirok etishlari mumkin.\n\nAmmo, tushkunlikka tushmang. \"Fan "
            "javohirlari\" olimpiadasi har yili o'tkaziladi va kelgusida siz yana olimpiadada ishtirok etib, "
            "o'z bilimingizni sinab ko'rasiz va universitimizda grant asosida ta'lim olish imkoniyatini qo'lga "
            "kiritasiz degan umiddamiz!\n\nSiz bilan universitetimizning talabasi sifatida uchrashishimizni "
            "sabrsizlik bilan kutib qolamiz! 🤗")
    await call.message.edit_text(resp, None)
    await state.reset_data()
    await state.finish()


async def true_fullname(call, state: FSMContext):
    data = await state.get_data()
    fullname = data.get('test_result')[0][2]
    answer = ("Siz olimpiadaga ro'yxatdan o'tganingizda ismingizni \"{}\" deb kiritgan ekansiz. Ismingiz va "
              "familiyangiz to'g'ri kiritilgan bo'lsa, pastdagi \"Tasdiqlayman\" tugmasini bosing. Noto'g'ri "
              "kiritilgan bo'lsa, ismingiz va familiyangizni to'g'irlab yozib yuboring.")
    await call.message.edit_text(answer.format(fullname), reply_markup=my_name_is_right)
    await call.message.answer("Ism-familiyangizni kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(ApplicationOlympiad.fullname)


@dp.callback_query_handler(text="true_name", state=ApplicationOlympiad.fullname)
async def true_name_success(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    science = data.get('science', None)
    test_result = data.get('test_result')
    if science:
        for res in test_result:
            if res[7] == science:
                test_result = [res]
    await db.add_next_olympiad_user(*test_result[0][1:8], test_result[0][8].count('1'), test_result[0][9])
    password = await db.get_next_olympiad_user_password(call.from_user.id)
    resp = (f"Tabriklaymiz! Siz \"Fan javohirlari\" olimpiadasining 2-bosqichiga muvaffaqiyatli ro'yxatdan o'tdingiz."
            f"\n\n{science if science else test_result[0][7]} fani bo'yicha 2-bosqich Toshkent shahridagi Fan va "
            f"texnologiyalar universitetida oflayn "
            f"bo'lib o'tadi. Olimpiada kuni va vaqtini @fanjavohirlari kanalimiz orqali e'lon qilamiz.\n\nImtihonda "
            f"ishtirok etish uchun quyidagi ID-raqamni yozib oling yoki eslab qoling.\n\nSizning ID-raqamingiz: "
            f"{password[0][0]}"
            f"\n\nFan va texnologiyalar universiteti manzili: Toshkent shahri, Algoritm dahasi, "
            f"Diydor ko'chasi 71.\nMo'ljal: sobiq Roison binosi (<a "
            f"href='https://yandex.uz/maps/10335/tashkent/?ll=69.163080%2C41.261028&mode=whatshere&whatshere%5Bpoint"
            f"%5D=69.163055%2C41.261021&whatshere%5Bzoom%5D=19.98&z=19'>Lokatsiya</a>)\n\nYangiliklardan xabardor "
            f"bo'lib turish uchun @usatuzb telegram kanaliga a'zo bo'lishni unutmang! Savollaringiz bo'lsa, "
            f"78-888-38-88 telefon raqamiga qo'ng'iroq qiling.")
    await call.message.delete()
    await call.message.answer(resp, reply_markup=await menu_user_markup(call.from_user.id))
    await state.reset_data()
    await state.finish()


@dp.message_handler(state=ApplicationOlympiad.fullname, content_types=ContentType.TEXT)
async def new_fullname(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    science = data.get('science', None)
    test_result = data.get('test_result')
    fullname = msg.text
    if science:
        for res in test_result:
            if res[7] == science:
                test_result = [res]
    await db.add_next_olympiad_user(msg.from_user.id, fullname, *test_result[0][3:8], test_result[0][8].count('1'),
                                    test_result[0][9])
    password = await db.get_next_olympiad_user_password(msg.from_user.id)
    resp = (f"Tabriklaymiz! Siz \"Fan javohirlari\" olimpiadasining 2-bosqichiga muvaffaqiyatli ro'yxatdan o'tdingiz."
            f"\n\n{science if science else test_result[0][7]} fani bo'yicha 2-bosqich Toshkent shahridagi Fan va texnologiyalar universitetida oflayn "
            f"bo'lib o'tadi. Olimpiada kuni va vaqtini @fanjavohirlari kanalimiz orqali e'lon qilamiz.\n\nImtihonda "
            f"ishtirok etish uchun quyidagi ID-raqamni yozib oling yoki eslab qoling.\n\nSizning ID-raqamingiz: "
            f"{password[0][0]}"
            f"\n\nFan va texnologiyalar universiteti manzili: Toshkent shahri, Algoritm dahasi, "
            f"Diydor ko'chasi 71.\nMo'ljal: sobiq Roison binosi (<a "
            f"href='https://yandex.uz/maps/10335/tashkent/?ll=69.163080%2C41.261028&mode=whatshere&whatshere%5Bpoint"
            f"%5D=69.163055%2C41.261021&whatshere%5Bzoom%5D=19.98&z=19'>Lokatsiya</a>)\n\nYangiliklardan xabardor "
            f"bo'lib turish uchun @usatuzb telegram kanaliga a'zo bo'lishni unutmang! Savollaringiz bo'lsa, "
            f"78-888-38-88 telefon raqamiga qo'ng'iroq qiling.")
    await msg.answer(resp, reply_markup=await menu_user_markup(msg.from_user.id))
    await state.reset_data()
    await state.finish()


@dp.message_handler(state=[ApplicationOlympiad.graduate, ApplicationOlympiad.science, ApplicationOlympiad.fullname],
                    content_types=ContentType.ANY)
async def error_application(msg: types.Message):
    await msg.delete()
    err_msg = await msg.answer("❗️ Iltimos olimpiadaning 2-bosqichi uchun ariza yuborish ketma-ketligiga amal qiling.")
    await asyncio.sleep(2)
    await err_msg.delete()
