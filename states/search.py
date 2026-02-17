from aiogram.fsm.state import State, StatesGroup

class SearchStates(StatesGroup):
    target_gender = State()
    age_range = State()
    browsing = State() # Showing profiles
