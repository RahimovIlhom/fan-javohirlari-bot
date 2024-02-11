from aiogram.dispatcher.filters.state import State, StatesGroup


class TestStatesGroup(StatesGroup):
    science = State()
    ready = State()
    execution = State()
    result = State()
