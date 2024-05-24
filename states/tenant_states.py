from aiogram.fsm.state import StatesGroup, State


class Tenant(StatesGroup):
    cold_water = State()
    hot_water = State()
    electricity = State()
    view_readings = State()

    edit_cold_water = State()
    edit_hot_water = State()
    edit_electricity = State()
    edit_heating = State()
