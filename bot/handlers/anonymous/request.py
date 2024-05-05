import logging
from aiogram import types
from aiogram.filters import Command, CommandStart
from handlers.filters import AnonymousFilter

from bot.utils import notify_admins
from db.repository import RequestRepository
from .router import router


@router.message(Command("request"), AnonymousFilter())
async def request_handler(message: types.Message) -> None:
    request, status = RequestRepository.get_or_create_request(
        message.from_user.id, message.from_user.username
    )
    
    if status:
        await notify_admins("Появилась новая заявка.")
        await message.answer("Заявка была отправлена администратору.")
    else:
        await message.answer("Ваша заявка уже на рассмотрении.")


@router.message(CommandStart, AnonymousFilter())
async def start_handler(message: types.Message) -> None:    
    await message.answer("Чтобы подать заявку, нажмите /request.")
