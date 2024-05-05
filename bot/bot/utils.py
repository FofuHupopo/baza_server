from .bot import bot

from db.repository import UserRepository
from db.models import UserModel


async def send_message(user_id, text, **kwargs):
    await bot.send_message(chat_id=user_id, text=text, **kwargs)


async def send_multiply_messages(users_id: list[int], text, **kwargs):
    for user_id in users_id:
       await send_message(user_id, text, **kwargs)


async def notify_admins(text):
    admins: list[UserModel] = UserRepository.get_admins()
    
    admins_id = [admin.telegram_id for admin in admins]

    await send_multiply_messages(admins_id, text)


async def notify_managers(text):
    users: list[UserModel] = UserRepository.get_users()
    
    users_id = [user.telegram_id for user in users]

    await send_multiply_messages(users_id, text)
