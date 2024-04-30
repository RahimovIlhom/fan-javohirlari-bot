from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

participation_choices = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Ha, borib ishtirok etaman", callback_data='yes_go'),
        ],
        [
            InlineKeyboardButton(text="Yo'q, afsus imkoniyatim yo'q", callback_data='no_go'),
        ],
    ],
)


are_you_graduate = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Ha, men bitiruvchi sinf o'quvchisiman", callback_data='yes_graduate'),
        ],
        [
            InlineKeyboardButton(text="Yo'q, men bitiruvchi sinf o'quvchisi emasman", callback_data='no_graduate'),
        ],
    ],
)

sciences_callback_data = CallbackData('test_results', 'science')


async def make_callback_sciences(science):
    return sciences_callback_data.new(science)


async def choices_olympiad_science(tests):
    markup = InlineKeyboardMarkup()
    for result in tests:
        vaucher = 2000000 if result[8].count('1') / len(result[8]) >= 0.85 else 1500000
        markup.row(InlineKeyboardButton(
            text=f"{result[7]} - {vaucher} so'm vaucher",
            callback_data=await make_callback_sciences(result[7])
        ))
    return markup


my_name_is_right = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Tasdiqlayman", callback_data='true_name')]
    ]
)


next_level_olympiad_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🏆 OLIMPIADA (2-bosqich) UCHUN ARIZA", callback_data='application')]
    ]
)
