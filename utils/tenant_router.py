from typing import List
from configurations import ADMIN_ID
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import BaseFilter


class IsTenantFilter(BaseFilter):
    """Фильтр, проверяющий является ли отправитель сообщения админом"""
    def __init__(self, admins_list: List[int]):

        # Список ID администраторов прописывается вручную
        self.admins_list = admins_list

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id not in self.admins_list


tenant_router = Router()

# Выше описанный фильтр добавляем прямо в роутер
tenant_router.message.filter(IsTenantFilter(admins_list=ADMIN_ID))