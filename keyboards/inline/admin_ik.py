from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardBuilder


edit_tenant_data = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Изменить адрес', callback_data='edit_address')],
    [InlineKeyboardButton(text='Изменить имя', callback_data='edit_name')],
    [InlineKeyboardButton(text='Зарегистрировать квартиранта', callback_data='edit_registration')]
])


def registration_application(user_id):
    reg = InlineKeyboardBuilder()
    reg.button(text='Зарегистрировать', callback_data=f'reg_{user_id}')
    return reg.as_markup()


settings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Установить дату', callback_data='set_data')],
    [InlineKeyboardButton(text='Установить время дня', callback_data='set_time')],
    [InlineKeyboardButton(text='Установить интервал', callback_data='set_interval')]
])


def readings_come(ten_id):
    read_cm = InlineKeyboardBuilder()
    read_cm.button(text='Подтвердить получение', callback_data=f'rd_come_{ten_id}')
    return read_cm.as_markup()
