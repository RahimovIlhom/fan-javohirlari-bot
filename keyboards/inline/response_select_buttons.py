from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .callback_data import callback_data


async def make_keyboard_test_responses(language):
    markup = InlineKeyboardMarkup(row_width=2)
    if language == 'uzbek':
        responses = ['A', 'B', 'C', 'D']
    else:
        responses = ['А', 'Б', 'В', 'Г']
    count = 1
    for i in responses:
        markup.insert(InlineKeyboardButton(text=i, callback_data=callback_data.new(response=f'{count}')))
        count += 1
    return markup
