from aiogram.fsm.state import State, StatesGroup

class ProfileEditStates(StatesGroup):
    main = State()
    edit_name = State()
    edit_age = State()
    edit_photo = State()
    edit_location = State()
