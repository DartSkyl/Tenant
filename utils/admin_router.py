from typing import List
from config.configurations import ADMIN_ID
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import BaseFilter


class IsAdminFilter(BaseFilter):
    """Фильтр, проверяющий является ли отправитель сообщения админом"""
    def __init__(self, admins_list: List[int]):

        # Список ID администраторов прописывается вручную
        self.admins_list = admins_list

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.admins_list


admin_router = Router()

# Выше описанный фильтр добавляем прямо в роутер
admin_router.message.filter(IsAdminFilter(admins_list=[ADMIN_ID]))
