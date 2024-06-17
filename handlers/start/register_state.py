from aiogram.fsm.state import StatesGroup, State


class RegisterState(StatesGroup):
    name = State()