class Tenant:
    """Класс реализует объект 'квартирант' и методы для взаимодействия """

    def __init__(self, address, name, user_id):
        self._address = address
        self._name = name
        self._user_id = user_id
        self._readings = False

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
        info_string = f'<b>{self._name, self._address}</b>'
        return info_string
