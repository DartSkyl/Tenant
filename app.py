import asyncio
import datetime
import handlers  # noqa
from utils.admin_router import admin_router
from utils.sendler import create_sendler
from loader import dp, bot, base_load, load_tenants
from aiogram.types.bot_command import BotCommand


async def start_up():
    # Загружаем базу
    await base_load()
    # Выгружаем всех квартирантов
    await load_tenants()
    # Создаем отправителя напоминаний
    await create_sendler()

    await bot.set_my_commands(
        commands=[
            BotCommand(command='start', description='Главное меню или рестарт')
        ]
    )

    # Для администраторов и всех ролей индивидуальный роутер
    dp.include_router(admin_router)
    with open('bot.log', 'a') as log_file:
        log_file.write(f'\n========== New bot session {datetime.datetime.now()} ==========\n\n')
    print('Стартуем')
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(start_up())
    except KeyboardInterrupt:
        print('Хорош, бро')
