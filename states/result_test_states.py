from aiogram.dispatcher.filters.state import StatesGroup, State


class ResultTestStatesGroup(StatesGroup):
    science = State()
    time = State()
