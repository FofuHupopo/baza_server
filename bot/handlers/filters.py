from typing import Union
from aiogram import types
from aiogram.filters import BaseFilter

from db.models import UserModel
from db.repository import UserRepository


class AdminFilter(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        user = UserRepository.get_user_by_id(message.from_user.id)

        if not user:
            return False

        return user.is_admin


class ManagerFilter(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        user = UserRepository.get_user_by_id(message.from_user.id)

        return bool(user)
    

class AnonymousFilter(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        user = UserRepository.get_user_by_id(message.from_user.id)

        return not bool(user)
