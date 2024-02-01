from aiogram.dispatcher.filters.state import State, StatesGroup


class RegisterStatesGroup(StatesGroup):
    language = State()
    fullname = State()
    phone = State()
    region = State()
    district = State()
    school = State()
    science = State()
