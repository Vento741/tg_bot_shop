from aiogram.fsm.state import StatesGroup, State

class BuyStates(StatesGroup):
    ENTER_QUANTITY = State()
    # ... другие состояния, если необходимо ...

class BasketStates(StatesGroup):
    ENTER_QUANTITY = State()
    # ... другие состояния, если необходимо ...