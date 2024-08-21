import asyncio
import datetime
from loader import tenant_list, bot, bot_base
from keyboards import readings_send_init


from aiogram.exceptions import TelegramForbiddenError
from apscheduler.schedulers.asyncio import AsyncIOScheduler


sendler_inst = None


async def create_sendler():
    global sendler_inst
    sendler_inst = Sendler()
    # Сразу добавим рассылку с настройками по умолчанию
    await sendler_inst.add_job_for_sendler()


async def send_reminder(interval):
    """Функция рассылки напоминаний о показаниях счетчиков. Состоит из двух циклов. Внешний while нужен для того,
    что бы после того, как внутренний for пройдет по всем квартирантам встать на интервал рассылки ип потом все
    повторить. Останавливать while будем с помощью подсчета отправленных показаний"""

    for ten in tenant_list:
        ten_id = ten.get_tenant_id()
        print(ten, ten_id)
        print(ten.readings_dict)
        # Проверим, оплатил ли предыдущий месяц. Если показания не сбросились, значит не оплачено
        if ten.readings_dict['cold']:
            print(ten.readings_dict)
            await bot_base.add_dept(
                ten_id=ten_id,
                data=ten.readings_dict['reporting_date'],
                cold=ten.readings_dict['cold'],
                hot=ten.readings_dict['hot'],
                electricity_day=ten.readings_dict['electricity_day'],
                electricity_night=ten.readings_dict['electricity_night'],
                heating=ten.readings_dict['heating'],
                payment_slip=ten.readings_dict['payment_slip'] if ten.readings_dict['payment_slip'] else None
            )

        # С самого начала пройдемся по всем квартирантам и установим новый отчетный период
        ten.readings_dict['reporting_date'] = str(datetime.datetime.now().strftime("%d.%m.%Y"))

    ten_list_for_sending = tenant_list[:]  # Создадим отдельную копию списка, что бы не напортачить с основным

    # Если к моменту начала рассылки квартирант уже скинул показания, то добавляем его в этот список,
    # а после конца цикла исключаем его из списка для рассылки
    tenant_send = []

    while len(ten_list_for_sending) > 0:
        for ten in ten_list_for_sending:
            if not ten.check_readings_status():  # Проверяем статус показаний
                ten_id = ten.get_tenant_id()
                try:
                    await bot.send_message(
                        chat_id=ten_id,
                        text='Пора снять показания!',
                        reply_markup=readings_send_init(ten_id)
                    )
                except TelegramForbiddenError:
                    print(ten_id)
                    pass
            else:
                tenant_send.append(ten)

        # После основного цикла, запускаем дополнительный, для очистки списка рассылки от тех уже скинул показания

        for ten in tenant_send:
            ten_list_for_sending.remove(ten)

        # После чего, обнуляем список для следующего цикла
        tenant_send = []

        # И становимся на интервал (измеряется в часах)
        await asyncio.sleep(interval*60*60)

    # И в самом конце возвращаем всем квартирантам статус показаний обратно на False

    for ten in tenant_list:
        ten.reset_readings_status()


class Sendler:
    """Класс для создания рассылки с напоминанием о снятии показания счетчика"""
    def __init__(self):
        self._scheduler = AsyncIOScheduler(gconfig={'apscheduler.timezone': 'Europe/Moscow'})
        self._scheduler.start()
        self._send_date = 21  # Число, когда начинается напоминание о снятии показаний счетчиков
        self._send_time = 9  # Время дня во сколько начинать рассылку
        self._interval = 2  # Интервал в часах для повторной отправки напоминая

    def get_settings_info(self):
        """Возвращает строку с информацией о текущих настройках"""
        settings_string = (f'Текущие настройки:\n\n'
                           f'<b>📆 Число начала рассылки:</b> {self._send_date}\n'
                           f'<b>⌚ Час дня начала рассылки:</b> {self._send_time}\n'
                           f'<b>⏱️ Интервал напоминаний:</b> {self._interval}')
        return settings_string

    async def add_job_for_sendler(self):
        """Добавление работы планировщику"""
        self._scheduler.add_job(
            func=send_reminder,
            kwargs={'interval': self._interval},
            trigger='cron',
            day=self._send_date,
            hour=self._send_time,
            minute=38,
            id='send',
            max_instances=1,
            replace_existing=True
        )

    async def edit_send_data(self, new_data):
        """Изменяем дату начала рассылки. При изменении даты сразу обновляем саму задачу в планировщике"""
        self._send_date = new_data
        await self.add_job_for_sendler()

    async def edit_send_time(self, new_time):
        """Изменяем час дня начала рассылки. При изменении часа дня сразу обновляем саму задачу в планировщике"""
        self._send_time = new_time
        await self.add_job_for_sendler()

    async def edit_interval(self, new_interval):
        """Изменяем интервал напоминай о показаниях"""
        self._interval = new_interval


class SendlerInterface:
    """Класс для взаимодействия с отправителем"""

    @staticmethod
    async def set_new_data(new_data):
        await sendler_inst.edit_send_data(new_data)

    @staticmethod
    async def set_new_time(new_time):
        await sendler_inst.edit_send_time(new_time)

    @staticmethod
    async def set_new_interval(new_interval):
        await sendler_inst.edit_interval(new_interval)

    @staticmethod
    async def get_settings_info():
        return sendler_inst.get_settings_info()
