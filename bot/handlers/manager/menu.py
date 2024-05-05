from aiogram import types
from aiogram.filters import Command
from handlers.filters import ManagerFilter

from db.repository import UserRepository
from .router import router
from .keyboards import menu_keyboard_notifications_off, menu_keyboard_notifications_on



@router.message(Command("menu"), ManagerFilter())
async def menu_handler(message: types.Message) -> None:
    user = UserRepository.get_user_by_tg_id(message.from_user.id)
    keyboard = None
    
    if user.enable_notifications:
        keyboard = menu_keyboard_notifications_on
    else:
        keyboard = menu_keyboard_notifications_off
        
    await message.answer("Меню.", reply_markup=keyboard)


@router.callback_query(lambda cd: cd.data == "menu", ManagerFilter())
async def menu_callback(callback: types.CallbackQuery) -> None:
    user = UserRepository.get_user_by_tg_id(callback.from_user.id)
    keyboard = None
    
    if user.enable_notifications:
        keyboard = menu_keyboard_notifications_on
    else:
        keyboard = menu_keyboard_notifications_off
        
    await callback.message.edit_text("Меню.", reply_markup=keyboard)
