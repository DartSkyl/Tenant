import sqlite3


class BotBase:
    """Класс для реализации базы данных и методов для взаимодействия с ней"""

    @staticmethod
    async def check_db_structure():
        """Создаем при первом подключении, а в последующем проверяем, таблицы необходимые для работы бота"""
        with sqlite3.connect('tenant_base.db') as connection:
            cursor = connection.cursor()

            # Таблица со всеми квартирантами
            cursor.execute('CREATE TABLE IF NOT EXISTS Tenants ('
                           'address TEXT,'
                           'name TEXT,'
                           'user_id INTEGER PRIMARY KEY'
                           ');')

            # Таблица истории
            cursor.execute('CREATE TABLE IF NOT EXISTS History (ten_id INTEGER,'
                           'reporting_date TEXT,'
                           'cold TEXT,'
                           'hot TEXT,'
                           'electricity_day TEXT,'
                           'electricity_night TEXT,'
                           'heating TEXT,'
                           'payment_slip TEXT,'
                           'check_id TEXT'
                           ');')

            connection.commit()

    # ========== Операции с историей о квартплате ==========

    @staticmethod
    async def add_report(ten_id, data, cold, hot, electricity_day, electricity_night, heating, payment_slip, check_id):
        """Вставляем сразу все столбцы"""
        with sqlite3.connect('tenant_base.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f'INSERT INTO History (ten_id, reporting_date, cold, hot,'
                           f'electricity_day, electricity_night, heating, payment_slip, check_id) '
                           f'VALUES ({ten_id}, "{data}", "{cold}", "{hot}", "{electricity_day}", "{electricity_night}", "{heating}", "{payment_slip}", "{check_id}")')
            connection.commit()

    @staticmethod
    async def get_tenant_history(ten_id):
        with sqlite3.connect('tenant_base.db') as connection:
            cursor = connection.cursor()
            tenant_history = cursor.execute(f'SELECT * FROM History WHERE ten_id = {ten_id};').fetchall()
            return tenant_history

    # ========== Операции с квартирантами ==========

    @staticmethod
    async def add_tenant(address, name, user_id):
        """Добавление квартиранта в базу"""
        with sqlite3.connect('tenant_base.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f'INSERT INTO Tenants (address, name, user_id) '
                           f'VALUES ("{address}", "{name}", "{user_id}")')
            connection.commit()

    @staticmethod
    async def get_all_tenants():
        """Возвращает список всех квартирантов. Нужно при запуске бота"""
        with sqlite3.connect('tenant_base.db') as connection:
            cursor = connection.cursor()
            tenants = cursor.execute('SELECT * FROM Tenants;').fetchall()
            return tenants

    @staticmethod
    async def get_tenants_id():
        """Возвращает ID всех зарегистрированных квартирантов"""
        with sqlite3.connect('tenant_base.db') as connection:
            cursor = connection.cursor()
            tenants_id = cursor.execute('SELECT user_id FROM Tenants;').fetchall()

            # Так как из базы возвращается кортеж, то перед возвратом преобразуем в список
            return [ten_id[0] for ten_id in tenants_id]

    @staticmethod
    async def delete_tenant_from_base(ten_id):
        """Удаляем квартиранта из базы"""
        with sqlite3.connect('tenant_base.db') as connection:
            cursor = connection.cursor()
            cursor.execute(f'DELETE FROM Tenants WHERE user_id = {ten_id}')
            connection.commit()
