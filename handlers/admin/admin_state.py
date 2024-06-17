from aiogram.fsm.state import StatesGroup, State




class AddProduct(StatesGroup):
    ENTER_NAME = State()
    ENTER_CATEGORY = State()
    ENTER_IMAGES = State()
    ENTER_DESCRIPTION = State()
    ENTER_PRICE = State()
    ENTER_QUANTITY = State()
    ENTER_LINKS = State()