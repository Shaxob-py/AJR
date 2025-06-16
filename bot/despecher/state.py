from aiogram.fsm.state import State, StatesGroup


class CustomerState(StatesGroup):
    register = State()
    phone_state = State()
    help_cus = State()
    location_state = State()
    cus_category = State()
    cus_product = State()
    products = State()
    pay_state = State()
    settings_state = State()
    change_name = State()
    location = State()
    consultation_state = State()


class AdminState(StatesGroup):
    register_admin = State()
    menu_panel = State()
    data_state = State()
    successfully_register = State()
    change_password_state = State()
    confirm_password_state = State()
