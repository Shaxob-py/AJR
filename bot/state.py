from aiogram.fsm.state import State, StatesGroup


class CustomerState(StatesGroup):
    phone_state = State()
    help_cus = State()
    location_state = State()
    cus_category = State()
    cus_product = State()
    products = State()