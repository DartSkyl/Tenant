from loader import bot, tenant_list, bot_base
from utils.admin_router import admin_router
from utils.tenant_model import Tenant
from utils.sendler import SendlerInterface
from keyboards import main_menu, edit_tenant_data, settings
from states import AdminStates

from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext


@admin_router.message(Command('start'))
async def start_function(msg: Message, state: FSMContext):
    """Функция старта и главное меню"""
    await state.clear()
    await msg.answer(text='Главное меню:', reply_markup=main_menu)


@admin_router.message(F.text == 'Настройки')
async def open_settings_menu(msg: Message):
    """Открываем меню настройки отправителя напоминаний"""
    # print(type(sendler_inst))
    await msg.answer(text=await SendlerInterface.get_settings_info(), reply_markup=settings)


@admin_router.callback_query(F.data.startswith('set_'))
async def init_settings_changes(callback: CallbackQuery, state: FSMContext):
    """Инициализируем изменения настроек отправителя напоминаний"""
    settings_dict = {
        'set_data': (AdminStates.set_data, 'Введите новую дату:'),
        'set_time': (AdminStates.set_time, 'Введите новое час дня:'),
        'set_interval': (AdminStates.set_interval, 'Введите интервал напоминаний в часах:')
    }

    await callback.answer()
    await callback.message.answer(text=settings_dict[callback.data][1])
    await state.set_state(settings_dict[callback.data][0])


@admin_router.message(AdminStates.set_data, F.text.isdigit())
async def set_new_data(msg: Message):
    """Устанавливаем новую дату начала оповещения"""
    if 0 < int(msg.text) < 32:
        await SendlerInterface.set_new_data(new_data=int(msg.text))
        await open_settings_menu(msg=msg)
    else:
        await msg.answer('Введите число от 1 до 31')


@admin_router.message(AdminStates.set_time, F.text.isdigit())
async def set_new_time(msg: Message):
    """Устанавливаем новое время начала рассылки оповещений"""
    if 0 <= int(msg.text) <= 23:
        await SendlerInterface.set_new_time(new_time=int(msg.text))
        await open_settings_menu(msg=msg)
    else:
        await msg.answer('Введите число от 0 до 23')


@admin_router.message(AdminStates.set_interval, F.text.isdigit())
async def set_new_interval(msg: Message):
    """Устанавливаем новый интервал напоминаний"""
    await SendlerInterface.set_new_interval(new_interval=int(msg.text))
    await open_settings_menu(msg=msg)


# ========== Регистрация нового квартиранта ==========


@admin_router.callback_query(F.data.startswith('reg_'))
async def tenant_registration_start(callback: CallbackQuery, state: FSMContext):
    """Запуск регистрации квартиранта"""
    await callback.answer()
    await state.set_data({'user_id': callback.data.replace('reg_', '')})
    await callback.message.answer(text='Введите адрес квартиранта:')
    await state.set_state(AdminStates.address)


@admin_router.message(AdminStates.address)
async def catch_tenant_address(msg: Message, state: FSMContext):
    """Ловим адрес квартиранта"""
    await state.update_data({'address': msg.text})
    await msg.answer(text='Введите имя квартирант:')
    await state.set_state(AdminStates.tenant_name)


async def view_tenant_data(msg: Message, state: FSMContext):
    """Демонстрация данных в отдельной функции"""
    tenant_data = await state.get_data()
    msg_text = (f'Проверьте правильность введенных данных:\n\n'
                f'<b>Адрес:</b> {tenant_data["address"]}\n'
                f'<b>Имя:</b> {tenant_data["name"]}\n')
    await msg.answer(text=msg_text, reply_markup=edit_tenant_data)
    await state.set_state(AdminStates.data_edit)


@admin_router.message(AdminStates.tenant_name)
async def catch_tenant_name(msg: Message, state: FSMContext):
    """Ловим имя квартирант"""
    await state.update_data({'name': msg.text})
    await view_tenant_data(msg=msg, state=state)


@admin_router.callback_query(F.data.startswith('edit_'))
async def edit_tenant_data_func(callback: CallbackQuery, state: FSMContext):
    """Изменяем данные или регистрируем"""
    await callback.answer()
    if callback.data != 'edit_registration':
        data_dict = {
            'edit_address': (AdminStates.edit_address, 'Введите новый адрес:'),
            'edit_name': (AdminStates.edit_name, 'Введите новое имя:'),
        }

        await callback.message.answer(text=data_dict[callback.data][1])
        await state.set_state(data_dict[callback.data][0])

    else:
        tenant_data = await state.get_data()

        await bot.send_message(chat_id=tenant_data['user_id'],
                               text='Добрый день! Вы были добавлены в бота-квартиранта!')

        tenant = Tenant(
            address=tenant_data['address'],
            name=tenant_data['name'],
            user_id=tenant_data['user_id']
        )

        # Добавляем в общий список
        tenant_list.append(tenant)

        # И сохраняем в базу
        await bot_base.add_tenant(
            address=tenant_data['address'],
            name=tenant_data['name'],
            user_id=tenant_data['user_id']
        )


@admin_router.message(AdminStates.edit_address)
async def edit_address(msg: Message, state: FSMContext):
    """Изменяем адрес квартиранта"""
    await state.update_data({'address': msg.text})
    await msg.answer('Адрес изменен')
    await view_tenant_data(msg=msg, state=state)


@admin_router.message(AdminStates.edit_name)
async def tenant_new_name(msg: Message, state: FSMContext):
    """Изменяем имя квартиранта"""
    await state.update_data({'name': msg.text})
    await msg.answer('Имя изменено')
    await view_tenant_data(msg=msg, state=state)
