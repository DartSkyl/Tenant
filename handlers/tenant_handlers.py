from loader import bot, tenant_list, bot_base, dp
from config.configurations import ADMIN_ID
from utils.admin_router import admin_router
from utils.tenant_model import Tenant
from keyboards import registration_application, readings_editor, confirm_sending, readings_come
from states import Tenant

from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext


@dp.message(Command('start'), F.from_user.id != ADMIN_ID)
async def start_for_tenants(msg: Message):
    """При первом взаимодействие администратору отправляется заявка на регистрацию"""
    id_list = await bot_base.get_tenants_id()
    if msg.from_user.id not in id_list:
        msg_text = f'Заявка на регистрацию от <b>{msg.from_user.full_name}</b>'
        await msg.answer('Заявка на регистрацию отправлена. Ожидайте.')
        await bot.send_message(chat_id=ADMIN_ID, text=msg_text, reply_markup=registration_application(msg.from_user.id))
    else:
        await msg.answer('Главное меню')


@dp.callback_query(F.data.startswith('readings_'))
async def start_readings_send(callback: CallbackQuery, state: FSMContext):
    """Начало скидывания показаний счетчиков"""
    await state.set_data({'tenant_id': callback.data.replace('readings_', '')})
    await callback.answer()
    await callback.message.answer('Введите показания холодной воды:')
    await state.set_state(Tenant.cold_water)


@dp.message(Tenant.cold_water)
async def cold_water(msg: Message, state: FSMContext):
    """Ловим холодную воду и просим скинуть горячую"""
    await state.update_data({'cold': msg.text})
    await msg.answer('Введите показания горячей воды')
    await state.set_state(Tenant.hot_water)


@dp.message(Tenant.hot_water)
async def hot_water(msg: Message, state: FSMContext):
    """Ловим горячую воду и просим ввести электричество"""
    await state.update_data({'hot': msg.text})
    await msg.answer('Введите показания электричества')
    await state.set_state(Tenant.electricity)


async def view_readings(msg: Message, state: FSMContext):
    """Вывод введенных данных"""
    readings_data = await state.get_data()
    msg_text = (f'<b><i>Показания счетчиков:</i></b>\n\n'
                f'<b>Холодная вода:</b> {readings_data["cold"]}\n'
                f'<b>Горячая вода:</b> {readings_data["hot"]}\n'
                f'<b>Электричество:</b>{readings_data["electricity"]}\n'
                f'<b>Отопление:</b> {readings_data["heating"]}')

    await msg.answer(text=msg_text, reply_markup=readings_editor)
    await state.set_state(Tenant.view_readings)


@dp.message(Tenant.electricity)
async def get_electricity(msg: Message, state: FSMContext):
    """Ловим электричество и выводим введенную информацию с возможностью изменить"""

    # Так же вставим значения для отопления, которое можно будет изменить перед отправкой если нужно
    await state.update_data({'electricity': msg.text, 'heating': 0})
    await view_readings(msg=msg, state=state)


@dp.callback_query(F.data.startswith('read_edit_'))
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


@dp.message(Tenant.edit_cold_water)
async def edit_cold_water(msg: Message, state: FSMContext):
    """Изменяем показания холодной воды"""
    await state.update_data({'cold': msg.text})
    await view_readings(msg=msg, state=state)


@dp.message(Tenant.edit_hot_water)
async def edit_hot_water(msg: Message, state: FSMContext):
    """Изменяем показания горячей воды"""
    await state.update_data({'hot': msg.text})
    await view_readings(msg=msg, state=state)


@dp.message(Tenant.edit_electricity)
async def edit_electricity(msg: Message, state: FSMContext):
    """Изменяем показания электричества"""
    await state.update_data({'electricity': msg.text})
    await view_readings(msg=msg, state=state)


@dp.message(Tenant.edit_heating)
async def edit_heating(msg: Message, state: FSMContext):
    """Изменяем показания отопления"""
    await state.update_data({'heating': msg.text})
    await view_readings(msg=msg, state=state)


@dp.callback_query(Tenant.view_readings, F.data.startswith('send_'))
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
                print(ten)
        msg_text = (f'<i>Показания счетчиков {tenant_info}:</i>\n\n'
                    f'<b>Холодная вода:</b> {readings["cold"]}\n'
                    f'<b>Горячая вода:</b> {readings["hot"]}\n'
                    f'<b>Электричество:</b>{readings["electricity"]}\n'
                    f'<b>Отопление:</b> {readings["heating"]}')

        await bot.send_message(chat_id=ADMIN_ID, text=msg_text, reply_markup=readings_come(readings['tenant_id']))
        await callback.message.answer('Показания отправлены, ожидайте подтверждение')

    else:
        await view_readings(msg=callback.message, state=state)
