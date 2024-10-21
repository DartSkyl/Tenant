from config.configurations import BOT_TOKEN
from utils.tenant_model import Tenant
from database.base import BotBase

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage


bot = Bot(token=BOT_TOKEN, parse_mode="HTML", disable_web_page_preview=True)
dp = Dispatcher(bot=bot, storage=MemoryStorage())
bot_base = BotBase()

# Все "квартиранты" будут храниться в списке
tenant_list = list()

# Словарь с отправляемыми администраторам сообщениями
messages = dict()


async def base_load():
    """Загружаем базу данных"""
    await bot_base.check_db_structure()


async def load_tenants():
    """Загружаем квартирантов из базы"""
    tenants = await bot_base.get_all_tenants()
    for elem in tenants:
        tenant_list.append(Tenant(
            address=elem[0],
            name=elem[1],
            user_id=elem[2]
        ))
        messages[elem[2]] = {'readings': [], 'checks': []}
