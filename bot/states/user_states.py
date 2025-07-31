from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    waiting_for_location = State()
    selecting_photo = State()
    generating_video = State()