import datetime
from sqlite3 import IntegrityError
from loader import bot, tenant_list, bot_base
from utils.admin_router import admin_router
from utils.tenant_model import Tenant
from utils.sendler import SendlerInterface
from keyboards import (main_menu, edit_tenant_data, settings, send_payment_slip,
                       send_ps, send_check, viewing_tenant, ten_rem_conf, view_history_checks)
from states import AdminStates
from config.configurations import ADMIN_ID

from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext


@admin_router.message(Command('start'))
async def start_function(msg: Message, state: FSMContext):
    """Функция старта и главное меню"""
    await state.clear()
    await msg.answer(text='Главное меню:', reply_markup=main_menu)


# ========== Основной функционал ==========


@admin_router.callback_query(F.data.startswith('rd_come_'))
async def catch_readings(callback: CallbackQuery, state: FSMContext):
    """Подтверждаем получение показаний"""
    await callback.answer()
    ten_id = int(callback.data.replace('rd_come_', ''))
    await bot.send_message(chat_id=ten_id, text='<b>Показания получены, ожидайте платежку!</b>')
    ten_info = ''
    for ten in tenant_list:
        if ten.get_tenant_id() == ten_id:
            ten_info += ten.get_info_string()
            break
    msg_text = f'Квартирант {ten_info} ожидает платежку\n\n<b>{datetime.datetime.now().strftime("%H:%M %d.%m.%Y")}</b>'

    for admin in ADMIN_ID:
        await bot.send_message(chat_id=admin, text=msg_text, reply_markup=send_payment_slip(ten_id))


@admin_router.callback_query(F.data.startswith('send_ps_'))
async def send_payment(callback: CallbackQuery, state: FSMContext):
    """Предлагаем скинуть документ с платежкой и сохраняем ID адресата"""
    await callback.answer()
    await state.set_data({'ten_id': int(callback.data.replace('send_ps_', ''))})
    await state.set_state(AdminStates.send_first_payment_slip)
    await callback.message.answer('Скиньте первую платежку:')


@admin_router.message(AdminStates.send_first_payment_slip)
async def catch_first_payment_slip(msg: Message, state: FSMContext):
    """Ловим платежку. Может быть фото либо документ"""
    if msg.photo:
        await state.update_data({'first_payment_slip': (msg.photo[-1].file_id, 'photo')})
        await msg.answer('Скиньте вторую платежку:')
        await state.set_state(AdminStates.send_second_payment_slip)
    elif msg.document:
        await state.update_data({'first_payment_slip': (msg.document.file_id, 'document')})
        await msg.answer('Скиньте вторую платежку:')
        await state.set_state(AdminStates.send_second_payment_slip)


@admin_router.message(AdminStates.send_second_payment_slip)
async def catch_second_payment_slip(msg: Message, state: FSMContext):
    """Ловим платежку. Может быть фото либо документ"""
    ten_id = (await state.get_data())['ten_id']

    if msg.photo:
        await state.update_data({'second_payment_slip': (msg.photo[-1].file_id, 'photo')})
        await msg.answer(text='Готово! Отправьте платежки или скиньте заново', reply_markup=send_ps(ten_id))

    elif msg.document:
        await state.update_data({'second_payment_slip': (msg.document.file_id, 'document')})
        await msg.answer(text='Готово! Отправьте платежки или скиньте заново', reply_markup=send_ps(ten_id))


@admin_router.callback_query(AdminStates.send_second_payment_slip, F.data.startswith('sps_'))
async def payment_slip_go_to_tenant(callback: CallbackQuery, state: FSMContext):
    """Отправляем платежку адресату"""
    await callback.answer()

    if callback.data != 'sps_del':

        payment_slip_info = await state.get_data()

        ten_info = ''

        for ten in tenant_list:
            if ten.get_tenant_id() == payment_slip_info['ten_id']:
                ten_info += ten.get_info_string()

                # И сразу заносим платежку в словарь для истории

                ten.readings_dict['payment_slip'] = payment_slip_info['first_payment_slip'][0] + '^^^^^' + \
                                                    payment_slip_info['first_payment_slip'][1] + '$$$'
                ten.readings_dict['payment_slip'] += payment_slip_info['second_payment_slip'][0] + '^^^^^' + \
                                                     payment_slip_info['second_payment_slip'][1]
                break
        msg_text = f'Платежка для {ten_info} отправлена'

        if payment_slip_info['first_payment_slip'][1] == 'photo':
            await bot.send_photo(
                chat_id=payment_slip_info['ten_id'],
                photo=payment_slip_info['first_payment_slip'][0],
                caption=f'<b>{datetime.datetime.now().strftime("%H:%M %d.%m.%Y")}</b>',
            )
            await state.clear()

        elif payment_slip_info['first_payment_slip'][1] == 'document':
            await bot.send_document(
                chat_id=payment_slip_info['ten_id'],
                document=payment_slip_info['first_payment_slip'][0],
                caption=f'<b>{datetime.datetime.now().strftime("%H:%M %d.%m.%Y")}</b>',
            )
            await state.clear()

        if payment_slip_info['second_payment_slip'][1] == 'photo':
            await bot.send_photo(
                chat_id=payment_slip_info['ten_id'],
                photo=payment_slip_info['second_payment_slip'][0],
                caption=f'<b>{datetime.datetime.now().strftime("%H:%M %d.%m.%Y")}</b>',
                reply_markup=send_check
            )

        elif payment_slip_info['second_payment_slip'][1] == 'document':
            await bot.send_document(
                chat_id=payment_slip_info['ten_id'],
                document=payment_slip_info['second_payment_slip'][0],
                caption=f'<b>{datetime.datetime.now().strftime("%H:%M %d.%m.%Y")}</b>',
                reply_markup=send_check
            )

        for admin in ADMIN_ID:
            await bot.send_message(chat_id=admin, text=msg_text)
    else:
        await state.set_state(AdminStates.send_first_payment_slip)
        await callback.message.answer('Скиньте первую платежку:')


@admin_router.callback_query(F.data.startswith('ch_conf_'))
async def check_confirming(callback: CallbackQuery, state: FSMContext):
    """Ловим чек и подтверждаем получение"""
    await callback.answer()
    ten_id = int(callback.data.replace('ch_conf_', ''))
    ten_info = ''

    for ten in tenant_list:
        if ten.get_tenant_id() == ten_id:
            ten_info += ten.get_info_string()
            await bot_base.add_report(
                ten_id=ten.get_tenant_id(),
                data=ten.readings_dict['reporting_date'],
                cold=ten.readings_dict['cold'],
                hot=ten.readings_dict['hot'],
                electricity_day=ten.readings_dict['electricity_day'],
                electricity_night=ten.readings_dict['electricity_night'],
                heating=ten.readings_dict['heating'],
                payment_slip=ten.readings_dict['payment_slip'],
                check_id=ten.readings_dict['check']
            )
            ten.reset_readings()
            break
    await bot.send_message(chat_id=ten_id, text='Получение чека подтверждено')

    msg_text = (f'Квартирант {ten_info} оплатил коммуналку!\n\n'
                f'<b>{datetime.datetime.now().strftime("%H:%M %d.%m.%Y")}</b>')

    for admin in ADMIN_ID:
        await bot.send_message(chat_id=admin, text=msg_text)


# ========== Просмотр истории квартирантов ==========

@admin_router.callback_query(F.data.startswith('hist_true_'))
async def view_tenant_history_pay(callback: CallbackQuery, state: FSMContext):
    """Показываем оплаченную историю конкретного квартиранта"""
    await callback.answer()
    await state.set_data({'empty': None})  # Заглушка для того, что бы просто задать data и использовать ниже
    ten_history = await bot_base.get_tenant_history(callback.data.replace('hist_true_', ''))
    for elem in ten_history:
        msg_text = (f'<b>📆 Отчетный период:</b> {elem[1]}\n'
                    f'<b>❄️ Холодная вода:</b> {elem[2]}\n'
                    f'<b>🔥 Горячая вода:</b> {elem[3]}\n'
                    f'<b>⚡ Электричество день:</b> {elem[4]}\n'
                    f'<b>⚡ Электричество ночь:</b> {elem[5]}\n'
                    f'<b>🌡️ Отопление:</b> {elem[6]}')

        # Ключ это ID квартиранта и дата отчетного периода. Значение это file_id платежки и чека
        # Да извращение, но лучше я ничего не придумал!
        await state.update_data({f'{elem[0]}_{elem[1]}': (f'{elem[7]}', f'{elem[8]}')})
        await callback.message.answer(
            text=msg_text,
            reply_markup=view_history_checks(f'{elem[0]}_{elem[1]}',
                                             pay_status=True)
        )


@admin_router.callback_query(F.data.startswith('hist_false_'))
async def view_tenant_history_(callback: CallbackQuery, state: FSMContext):
    """Показываем неоплаченный период, то есть текущий месяц"""
    await callback.answer()
    empty_answer = 'На данный момент все оплачено'
    message_markup = None
    ten_id = int(callback.data.replace('hist_false_', ''))
    for ten in tenant_list:
        if ten.get_tenant_id() == ten_id:
            ten_readings_info = ten.get_readings_dict()
            msg_text = (f'<b>📆 Отчетный период:</b> {ten_readings_info["reporting_date"]}\n'
                        f'<b>❄️ Холодная вода:</b> {ten_readings_info["cold"]}\n'
                        f'<b>🔥 Горячая вода:</b> {ten_readings_info["hot"]}\n'
                        f'<b>⚡ Электричество день:</b> {ten_readings_info["electricity_day"]}\n'
                        f'<b>⚡ Электричество ночь:</b> {ten_readings_info["electricity_night"]}\n'
                        f'<b>🌡️ Отопление:</b> {ten_readings_info["heating"]}') if ten_readings_info["cold"] else (
                empty_answer)
            if ten_readings_info["payment_slip"]:
                await state.set_data({'payment_slip': (ten_readings_info["payment_slip"], '')})
                message_markup = view_history_checks(doc_key='payment_slip')
            await callback.message.answer(text=msg_text, reply_markup=message_markup)
            break


@admin_router.callback_query(F.data.startswith('p_'))
async def view_payment_slip(callback: CallbackQuery, state: FSMContext):
    """Отправляем в чат платежку"""
    await callback.answer()
    pay_slip = (await state.get_data())[callback.data.replace('p_', '')][0].split('$$$')
    pay_slip = [pay.split('^^^^^') for pay in pay_slip]
    for pay in pay_slip:
        if pay[1] == 'document':
            await callback.message.answer_document(document=pay[0])
        else:
            await callback.message.answer_photo(photo=pay[0])


@admin_router.callback_query(F.data.startswith('ch_'))
async def view_payment_check(callback: CallbackQuery, state: FSMContext):
    """Отправляем в чат чек оплаты коммуналки"""
    await callback.answer()
    check = (await state.get_data())[callback.data.replace('ch_', '')][1].split('$$$')
    check = [pay.split('^^^^^') for pay in check]
    for pay in check:
        if pay[1] == 'document':
            await callback.message.answer_document(document=pay[0])
        else:
            await callback.message.answer_photo(photo=pay[0])


# ========== Просмотр/удаление квартирантов ==========

@admin_router.message(F.text == '📋 Текущие квартиранты')
async def view_tenants(msg: Message):
    """Просмотр всех квартирантов"""
    for ten in tenant_list:
        await msg.answer(text=ten.view_tenant(), reply_markup=viewing_tenant(ten.get_tenant_id()))


@admin_router.callback_query(F.data.startswith('del_'))
async def remove_tenant(callback: CallbackQuery, state: FSMContext):
    """Удаляем квартиранта с подтверждением"""
    await callback.answer()
    if callback.data == 'del_yes':
        rem_ten_id = (await state.get_data())['del_ten_id']
        for ten in tenant_list:
            if ten.get_tenant_id() == rem_ten_id:
                await bot_base.delete_tenant_from_base(rem_ten_id)
                tenant_list.remove(ten)
                break

        await callback.message.answer('Удаление завершено!')

    elif callback.data == 'del_no':
        for ten in tenant_list:
            await callback.message.answer(text=ten.view_tenant(), reply_markup=viewing_tenant(ten.get_tenant_id()))
        await state.clear()
    else:
        ten_id = int(callback.data.replace('del_', ''))
        ten_info = ''

        for ten in tenant_list:
            if ten.get_tenant_id() == ten_id:
                ten_info += ten.get_info_string()
                break
        await state.set_data({'del_ten_id': ten_id})
        await callback.message.answer(text=f'Вы уверены, что хотите удалить квартиранта {ten_info}?',
                                      reply_markup=ten_rem_conf)


# ========== Настройки бота ==========


@admin_router.message(F.text == '⚙️ Настройки')
async def open_settings_menu(msg: Message):
    """Открываем меню настройки отправителя напоминаний"""
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
    await state.set_data({'user_id': int(callback.data.replace('reg_', ''))})
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

        try:
            # сохраняем в базу
            await bot_base.add_tenant(
                address=tenant_data['address'],
                name=tenant_data['name'],
                user_id=tenant_data['user_id']
            )

            tenant = Tenant(
                address=tenant_data['address'],
                name=tenant_data['name'],
                user_id=tenant_data['user_id']
            )

            # Добавляем в общий список
            tenant_list.append(tenant)

            await bot.send_message(chat_id=tenant_data['user_id'],
                                   text='Вы были добавлены в бота-квартиранта!')
            await callback.message.answer('Квартирант зарегистрирован!')

            for admin in ADMIN_ID:
                if admin != callback.from_user.id:
                    await bot.send_message(chat_id=admin,
                                           text=f'Зарегистрирован квартирант <b>{tenant_data["name"]}</b>'
                                                f' по адресу <b>{tenant_data["address"]}</b>')
        except IntegrityError:
            await callback.message.answer('Квартирант уже зарегистрирован!')
        await start_function(msg=callback.message, state=state)


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
