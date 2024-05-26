from aiogram.fsm.state import StatesGroup, State


class Tenant(StatesGroup):
    set_readings = State()
    heating = State()

    view_readings = State()

    edit_cold_water = State()
    edit_hot_water = State()
    edit_electricity = State()
    edit_heating = State()

    send_first_check = State()
    send_second_check = State()
