from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardBuilder


edit_tenant_data = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🏠 Изменить адрес', callback_data='edit_address')],
    [InlineKeyboardButton(text='👨‍🦰 Изменить имя', callback_data='edit_name')],
    [InlineKeyboardButton(text='🗃️ Зарегистрировать квартиранта', callback_data='edit_registration')]
])


def registration_application(user_id):
    reg = InlineKeyboardBuilder()
    reg.button(text='✒️ Зарегистрировать', callback_data=f'reg_{user_id}')
    return reg.as_markup()


settings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📆 Установить дату', callback_data='set_data')],
    [InlineKeyboardButton(text='⌚ Установить время дня', callback_data='set_time')],
    [InlineKeyboardButton(text='⏱️ Установить интервал', callback_data='set_interval')]
])


def readings_come(ten_id):
    read_cm = InlineKeyboardBuilder()
    read_cm.button(text='✅ Подтвердить получение', callback_data=f'rd_come_{ten_id}')
    return read_cm.as_markup()


def send_payment_slip(ten_id):
    send = InlineKeyboardBuilder()
    send.button(text='📨 Отправить платежку', callback_data=f'send_ps_{ten_id}')
    return send.as_markup()


def send_ps(ten_id):
    send = InlineKeyboardBuilder()
    send.button(text='📨 Отправить платежку', callback_data=f'sps_{ten_id}')
    send.button(text='⛔ Скинуть платежки заново', callback_data='sps_del')
    send.adjust(1)
    return send.as_markup()


def confirm_check(ten_id):
    conf = InlineKeyboardBuilder()
    conf.button(text='✅ Подтвердить получение чека', callback_data=f'ch_conf_{ten_id}')
    return conf.as_markup()


def viewing_tenant(ten_id):
    view_ten = InlineKeyboardBuilder()
    view_ten.button(text='📂 Посмотреть историю', callback_data=f'hist_{ten_id}')
    view_ten.button(text='❌ Удалить квартиранта', callback_data=f'del_{ten_id}')
    view_ten.adjust(1)
    return view_ten.as_markup()


ten_rem_conf = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='❌ Удалить', callback_data='del_yes')],
    [InlineKeyboardButton(text='⛔ Отмена', callback_data='del_no')]
])


def view_history_checks(doc_key):
    view_t = InlineKeyboardBuilder()
    view_t.button(text='🧾 Посмотреть платежку', callback_data=f'p_{doc_key}')
    view_t.button(text='📃 Посмотреть чек оплаты', callback_data=f'ch_{doc_key}')
    view_t.adjust(1)
    return view_t.as_markup()
