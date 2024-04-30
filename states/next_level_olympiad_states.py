from aiogram.dispatcher.filters.state import StatesGroup, State


class OlympiansListState(StatesGroup):
    science = State()
    result = State()


class ApplicationOlympiad(StatesGroup):
    graduate = State()
    science = State()
    fullname = State()
