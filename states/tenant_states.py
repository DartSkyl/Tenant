from aiogram.fsm.state import StatesGroup, State


class Tenant(StatesGroup):
    set_readings = State()
    heating = State()

    view_readings = State()

    edit_cold_water = State()
    edit_hot_water = State()
    edit_electricity_day = State()
    edit_electricity_night = State()
    edit_heating = State()

    send_first_check = State()
    send_second_check = State()

    debt_send_first_check = State()
    debt_send_second_check = State()
