class Tenant:
    """Класс реализует объект 'квартирант' и методы для взаимодействия """

    def __init__(self, address, name, user_id):
        self._address = address
        self._name = name
        self._user_id = user_id
        self._readings = False

        # Словарь показаний используется для сохранения истории в базу.
        # При создании все ключи равны None. Меняются данные по ходу прохождения всех этапов.
        # После сохранения данные не сбрасываются, а переписываются в следующем цикле
        # Сохранение происходит в самом конце оплаты,
        # после подтверждения получения чека со стороны администратора

        self.readings_dict = {
            'reporting_date': None,
            'cold': None,
            'hot': None,
            'electricity': None,
            'heating': None,
            'payment_slip': None,
            'check': None
        }

    def __str__(self):
        tenant_info = (f'Address: {self._address}\n'
                       f'Name: {self._name}\n'
                       f'Readings: {self._readings}'
                       f'Username: {self._user_id}\n\n')
        return tenant_info

    def get_tenant_id(self):
        return self._user_id

    def check_readings_status(self):
        """Возвращает значения для обозначения отправлял ли квартирант показания или еще нет"""
        return self._readings

    def readings_sent(self):
        """Когда квартирант отправляет показания переключаем на True"""
        self._readings = True

    def reset_readings_status(self):
        """После окончания рассылки возвращаем всем статус на False с помощью этого для следующего раза"""
        self._readings = False

    def get_info_string(self):
        info_string = f'<b>{self._name} {self._address}</b>'
        return info_string

    def view_tenant(self):
        ten_string = (f'<b>🏠 Адрес:</b> <i>{self._address}</i>\n'
                      f'<b>👨‍🦰 Имя:</b> <i>{self._name}</i>')
        return ten_string
