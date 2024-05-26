import datetime
from loader import bot, tenant_list, bot_base
from config.configurations import ADMIN_ID
from utils.tenant_router import tenant_router
from utils.tenant_model import Tenant
from keyboards import (registration_application, readings_editor,
                       confirm_sending, readings_come, check_ready, confirm_check)
from states import Tenant

from aiogram.types import Message, CallbackQuery
from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext


@tenant_router.message(Command('start'))
async def start_for_tenants(msg: Message):
    """При первом взаимодействие администратору отправляется заявка на регистрацию"""
    id_list = await bot_base.get_tenants_id()
    if msg.from_user.id not in id_list:
        msg_text = f'Заявка на регистрацию от <b>{msg.from_user.full_name}</b>'
        await msg.answer('Заявка на регистрацию отправлена. Ожидайте.')
        for admin in ADMIN_ID:
            await bot.send_message(chat_id=admin, text=msg_text,
                                   reply_markup=registration_application(msg.from_user.id))
    else:
        await msg.answer('Вы зарегистрированы как квартирант!\n'
                         'Ожидайте оповещения о необходимости скинуть показания счетчиков')


@tenant_router.callback_query(F.data.startswith('readings_'))
async def start_readings_send(callback: CallbackQuery, state: FSMContext):
    """Начало скидывания показаний счетчиков"""
    await state.set_data({'tenant_id': callback.data.replace('readings_', '')})
    await callback.answer()
    await callback.message.answer('Введите показания холодной воды:')
    await state.set_state(Tenant.cold_water)


@tenant_router.message(Tenant.cold_water)
async def cold_water(msg: Message, state: FSMContext):
    """Ловим холодную воду и просим скинуть горячую"""
    await state.update_data({'cold': msg.text})
    await msg.answer('Введите показания горячей воды')
    await state.set_state(Tenant.hot_water)


@tenant_router.message(Tenant.hot_water)
async def hot_water(msg: Message, state: FSMContext):
    """Ловим горячую воду и просим ввести электричество"""
    await state.update_data({'hot': msg.text})
    await msg.answer('Введите показания электричества')
    await state.set_state(Tenant.electricity)


async def view_readings(msg: Message, state: FSMContext):
    """Вывод введенных данных"""
    readings_data = await state.get_data()
    msg_text = (f'<b><i>Показания счетчиков:</i></b>\n\n'
                f'<b>❄️ Холодная вода:</b> {readings_data["cold"]}\n'
                f'<b>🔥 Горячая вода:</b> {readings_data["hot"]}\n'
                f'<b>⚡ Электричество:</b>{readings_data["electricity"]}\n'
                f'<b>🌡️ Отопление:</b> {readings_data["heating"]}')

    await msg.answer('<b>Проверьте правильность введенных данных перед отправкой!\n'
                     'Так же укажите отопление, если необходимо</b>❗')
    await msg.answer(text=msg_text, reply_markup=readings_editor)
    await state.set_state(Tenant.view_readings)


@tenant_router.message(Tenant.electricity)
async def get_electricity(msg: Message, state: FSMContext):
    """Ловим электричество и выводим введенную информацию с возможностью изменить"""

    # Так же вставим значения для отопления, которое можно будет изменить перед отправкой если нужно
    await state.update_data({'electricity': msg.text, 'heating': '0'})
    await view_readings(msg=msg, state=state)


@tenant_router.callback_query(F.data.startswith('read_edit_'))
async def edit_readings(callback: CallbackQuery, state: FSMContext):
    """Запускаем замену показаний"""
    readings_editor_dict = {
        'read_edit_cold': (Tenant.edit_cold_water, 'Введите показания холодной воды:'),
        'read_edit_hot': (Tenant.edit_hot_water, 'Введите показания горячей воды:'),
        'read_edit_elect': (Tenant.edit_electricity, 'Введите показания электричества:'),
        'read_edit_heating': (Tenant.edit_heating, 'Введите показания отопления:')
    }

    await callback.answer()
    await callback.message.answer(readings_editor_dict[callback.data][1])
    await state.set_state(readings_editor_dict[callback.data][0])


@tenant_router.message(Tenant.edit_cold_water)
async def edit_cold_water(msg: Message, state: FSMContext):
    """Изменяем показания холодной воды"""
    await state.update_data({'cold': msg.text})
    await view_readings(msg=msg, state=state)


@tenant_router.message(Tenant.edit_hot_water)
async def edit_hot_water(msg: Message, state: FSMContext):
    """Изменяем показания горячей воды"""
    await state.update_data({'hot': msg.text})
    await view_readings(msg=msg, state=state)


@tenant_router.message(Tenant.edit_electricity)
async def edit_electricity(msg: Message, state: FSMContext):
    """Изменяем показания электричества"""
    await state.update_data({'electricity': msg.text})
    await view_readings(msg=msg, state=state)


@tenant_router.message(Tenant.edit_heating)
async def edit_heating(msg: Message, state: FSMContext):
    """Изменяем показания отопления"""
    await state.update_data({'heating': msg.text})
    await view_readings(msg=msg, state=state)


@tenant_router.callback_query(Tenant.view_readings, F.data.startswith('send_'))
async def send_readings_func(callback: CallbackQuery, state: FSMContext):
    """Отправляем показания админу, предварительно подтвердив отправку"""
    await callback.answer()
    if callback.data == 'send_readings':
        await callback.message.answer(text='Подтвердите отправление:', reply_markup=confirm_sending)
    elif callback.data == 'send_confirm':
        readings = await state.get_data()
        tenant_info = ''
        for ten in tenant_list:
            if ten.get_tenant_id() == int(readings['tenant_id']):
                tenant_info += ten.get_info_string()
                ten.readings_sent()  # Заодно укажем, что квартирант отправил показания

                # А так же сохраним данные в словарь, что бы потом сохранить в историю

                ten.readings_dict['cold'] = readings["cold"]
                ten.readings_dict['hot'] = readings["hot"]
                ten.readings_dict['electricity'] = readings["electricity"]
                ten.readings_dict['heating'] = readings["heating"]
                break

        msg_text = (f'<i>Показания счетчиков {tenant_info}:</i>\n\n'
                    f'<b>❄️ Холодная вода:</b> {readings["cold"]}\n'
                    f'<b>🔥 Горячая вода:</b> {readings["hot"]}\n'
                    f'<b>⚡ Электричество:</b>{readings["electricity"]}\n'
                    f'<b>🌡️ Отопление:</b> {readings["heating"]}\n\n'
                    f'<b>{datetime.datetime.now().strftime("%H:%M %d.%m.%Y")}</b>')

        for admin in ADMIN_ID:
            await bot.send_message(chat_id=admin, text=msg_text, reply_markup=readings_come(readings['tenant_id']))
        await callback.message.answer('Показания отправлены, ожидайте подтверждение')
        await state.clear()

    else:
        await view_readings(msg=callback.message, state=state)


@tenant_router.callback_query(F.data == 'check_send')
async def send_check_start(callback: CallbackQuery, state: FSMContext):
    """Начинаем отправку чека"""
    await callback.answer()
    await state.set_state(Tenant.send_check)
    # await state.set_data({'ten_check_id': callback.from_user.id})
    await callback.message.answer('Скиньте чек в виде фото или документа:')


@tenant_router.message(Tenant.send_check)
async def catch_ten_check(msg: Message, state: FSMContext):
    """Ловим чек, либо фото, либо документ. Отправляем или предлагаем скинуть заново"""
    if msg.photo:
        await state.update_data({'check': (msg.photo[-1].file_id, 'photo')})
        await msg.answer(text='Отправьте чек или скиньте заново', reply_markup=check_ready)
    elif msg.document:
        await state.update_data({'check': (msg.document.file_id, 'document')})
        await msg.answer(text='Отправьте чек или скиньте заново', reply_markup=check_ready)


@tenant_router.callback_query(F.data == 'check_ready')
async def send_check_to_admin(callback: CallbackQuery, state: FSMContext):
    """Отправляем чек админу в соответствии с форматом"""
    await callback.answer()
    payment_slip_info = await state.get_data()

    ten_info = ''

    for ten in tenant_list:
        if ten.get_tenant_id() == callback.from_user.id:
            ten_info += ten.get_info_string()

            # И сразу заносим чек в словарь для истории

            ten.readings_dict['check'] = payment_slip_info['check'][0] + '^^^^^' + \
                                         payment_slip_info['check'][1]

            break

    msg_text = f'Чек от {ten_info}\n<b>{datetime.datetime.now().strftime("%H:%M %d.%m.%Y")}</b>'

    if payment_slip_info['check'][1] == 'photo':
        for admin in ADMIN_ID:
            await bot.send_photo(
                chat_id=admin,
                photo=payment_slip_info['check'][0],
                caption=msg_text,
                reply_markup=confirm_check(callback.from_user.id)
            )
        await state.clear()

    elif payment_slip_info['check'][1] == 'document':
        for admin in ADMIN_ID:
            await bot.send_document(
                chat_id=admin,
                document=payment_slip_info['check'][0],
                caption=msg_text,
                reply_markup=confirm_check(callback.from_user.id)
            )
        await state.clear()

    await callback.message.answer('Чек отправлен, ожидайте подтверждения')
