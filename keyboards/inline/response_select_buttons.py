from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .callback_data import callback_data


async def make_keyboard_test_responses():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.insert(InlineKeyboardButton(text="A", callback_data=callback_data.new(response='1')))
    markup.insert(InlineKeyboardButton(text="B", callback_data=callback_data.new(response='2')))
    markup.insert(InlineKeyboardButton(text="C", callback_data=callback_data.new(response='3')))
    markup.insert(InlineKeyboardButton(text="D", callback_data=callback_data.new(response='4')))
    return markup
