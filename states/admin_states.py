from aiogram.fsm.state import StatesGroup, State


class AdminStates(StatesGroup):

    # Регистрация квартиранта
    address = State()
    tenant_name = State()
    input_end = State()
    data_edit = State()
    edit_address = State()
    edit_name = State()
    edit_username = State()

    # Настройки отправителя напоминаний

    set_data = State()
    set_time = State()
    set_interval = State()

    # Отправка платежки

    send_payment_slip = State()
