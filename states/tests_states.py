from aiogram.dispatcher.filters.state import State, StatesGroup


class AddQuestionTestStatesGroup(StatesGroup):
    science = State()
    test = State()
    update = State()
    question_uz = State()
    question_ru = State()
    true_response = State()


class CreateTestStatesGroup(StatesGroup):
    science = State()
    language = State()
    count = State()
