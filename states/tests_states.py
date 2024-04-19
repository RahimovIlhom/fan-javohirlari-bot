from aiogram.dispatcher.filters.state import State, StatesGroup


class AddQuestionTestStatesGroup(StatesGroup):
    science = State()
    test = State()
    update = State()
    image = State()
    question = State()
    start_date = State()
    end_date = State()


class CreateTestStatesGroup(StatesGroup):
    science = State()
    language = State()
    count = State()
    start_time = State()
    end_time = State()
