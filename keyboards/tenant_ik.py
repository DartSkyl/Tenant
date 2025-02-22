from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardBuilder


def readings_send_init(ten_id):
    rsi_kb = InlineKeyboardBuilder()
    rsi_kb.button(text='📨 Отправить показания', callback_data=f'readings_{ten_id}')
    return rsi_kb.as_markup()


need_heating = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='heating_yes'),
     InlineKeyboardButton(text='Нет', callback_data='heating_no')]
])

readings_editor = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='❄️ Изменить холодную воду', callback_data='read_edit_cold')],
    [InlineKeyboardButton(text='🔥 Изменить горячую воду', callback_data='read_edit_hot')],
    [InlineKeyboardButton(text='⚡ Изменить электричество день', callback_data='read_edit_elect_day')],
    [InlineKeyboardButton(text='⚡ Изменить электричество ночь', callback_data='read_edit_elect_night')],
    [InlineKeyboardButton(text='🌡️ Изменить отопление', callback_data='read_edit_heating')],
    [InlineKeyboardButton(text='✅ Отправить показания', callback_data='send_readings')]
])

confirm_sending = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅ Подтвердить', callback_data='send_confirm')],
    [InlineKeyboardButton(text='⛔ Отменить', callback_data='send_cancel')]
])

send_check = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🧾 Скинуть чек', callback_data='check_send')]
])


def  send_debt_check(debt_id):
    debt_check = InlineKeyboardBuilder()
    debt_check.button(text='🧾 Скинуть чек', callback_data=f'debt_{debt_id}')
    return debt_check.as_markup()


check_ready = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📨 Отправить чек', callback_data='check_ready')],
    [InlineKeyboardButton(text='⛔ Скинуть чеки заново', callback_data='check_del')]
])
