from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

question_callback_data = CallbackData('tests', 'ques_id', 'update')


async def make_callback(ques_id, update='0'):
    return question_callback_data.new(ques_id, update)


async def create_edit_question_markup(ques_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.insert(InlineKeyboardButton(
        text="Savolni o'zgartirish ✏️",
        callback_data=await make_callback(ques_id, update='edit')
    ))
    markup.row(InlineKeyboardButton(
        '⬅️ Orqaga',
        callback_data=await make_callback(ques_id, update='back')
    ))
    return markup
