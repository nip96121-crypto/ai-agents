from aiogram.fsm.state import State, StatesGroup


class OrderState(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_address = State()
    waiting_for_payment = State()
    waiting_for_confirmation = State()


class SearchState(StatesGroup):
    waiting_for_query = State()
