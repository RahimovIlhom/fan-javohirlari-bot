import json

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from data.config import regions_uz, regions_ru, sciences_uz, sciences_ru

language_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='O’zbek tili'),
            KeyboardButton(text='Русский язык'),
        ]
    ],
    resize_keyboard=True
)

phone_uz_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="☎️ Telefon raqamingizni yuboring", request_contact=True),
        ],
    ],
    resize_keyboard=True
)

phone_ru_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="☎️ Отправьте свой номер телефона", request_contact=True),
        ],
    ],
    resize_keyboard=True
)

id_card_uz_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Hali ID karta olmaganman"),
        ],
    ],
    resize_keyboard=True
)

id_card_ru_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Я еще не получил(а) ID-карту"),
        ],
    ],
    resize_keyboard=True
)

region_uz_markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
for region in regions_uz:
    region_uz_markup.insert(KeyboardButton(text=region))


region_ru_markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
for region in regions_ru:
    region_ru_markup.insert(KeyboardButton(text=region))


async def district_uz_markup(region_uz: str):
    with open('data/districts_uz.json', 'r') as file:
        districts = json.load(file).get(region_uz)
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for district in districts:
        markup.insert(KeyboardButton(text=district))
    markup.row(KeyboardButton(text="⬅️ Orqaga"))
    return markup


async def district_ru_markup(region_ru: str):
    with open('data/districts_ru.json', 'r') as file:
        districts = json.load(file).get(region_ru)
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for district in districts:
        markup.insert(KeyboardButton(text=district))
    markup.row(KeyboardButton(text="⬅️ Назад"))
    return markup


sciences_uz_markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
for science in sciences_uz:
    sciences_uz_markup.insert(KeyboardButton(text=science))
sciences_uz_markup.row(KeyboardButton(text="⬅️ Orqaga"))


sciences_ru_markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
for science in sciences_ru:
    sciences_ru_markup.insert(KeyboardButton(text=science))
sciences_ru_markup.row(KeyboardButton(text="⬅️ Назад"))
