from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from loader import db

test_callback_data = CallbackData('tests', 'test_id', 'update')


async def make_callback(test_id, update='0'):
    return test_callback_data.new(test_id, update)


async def create_all_tests_markup(science):
    markup = InlineKeyboardMarkup(row_width=2)
    all_tests = await db.select_science_tests(science)
    for test_info in all_tests:
        if test_info[5]:
            markup.insert(
                InlineKeyboardButton(
                    text=f"{test_info[2]} - {test_info[3][:2]}, "
                         f"{len(await db.select_questions_test_id(test_info[0]))}/{test_info[4]} ✅",
                    callback_data=await make_callback(test_info[0]))
            )
        else:
            markup.insert(
                InlineKeyboardButton(
                    text=f"{test_info[2]} - {test_info[3][:2]}, "
                         f"{len(await db.select_questions_test_id(test_info[0]))}/{test_info[4]} ♻️",
                    callback_data=await make_callback(test_info[0]))
            )
    markup.row(InlineKeyboardButton('⬅️ Orqaga', callback_data='back'))
    return markup


async def create_edit_test_markup(test_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.insert(InlineKeyboardButton(
        text="O'chirish ❌",
        callback_data=await make_callback(test_id, update='del')
    ))
    markup.insert(InlineKeyboardButton(
        text="Savol qo'shish ➕",
        callback_data=await make_callback(test_id, update='add')
    ))
    markup.insert(InlineKeyboardButton(
        text="Savolni o'zgartirish ✏️",
        callback_data=await make_callback(test_id, update='edit')
    ))
    markup.row(InlineKeyboardButton(
        '⬅️ Orqaga',
        callback_data=await make_callback(test_id, update='back')
    ))
    return markup


async def create_questions_markup(questions):
    markup = InlineKeyboardMarkup(row_width=2)
    for ques in questions:
        markup.insert(InlineKeyboardButton(
            text=f"{ques[1]}-savol",
            callback_data=f"{ques[0]}"
        ))
    markup.row(InlineKeyboardButton(
        text="⬅️ Orqaga",
        callback_data='back',
    ))
    return markup

