from aiogram.fsm.state import StatesGroup, State


class CreateState(StatesGroup):
    category_product = State()
    name_product = State()
    img_product = State()
    description_product = State()
    price_product = State()
    key_product = State()