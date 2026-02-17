from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    language = State()
    photo = State()
    name = State()
    nickname = State()
    age = State()
    gender = State()
    target_gender = State()
    target_age = State()
    location = State()
    phone = State()
