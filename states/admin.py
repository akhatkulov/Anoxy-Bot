from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    stats = State()
    broadcast_text = State()
    search_user = State()
    give_boost = State()
