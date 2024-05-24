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
                           'user_id INTEGER'
                           ');')

            connection.commit()

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
