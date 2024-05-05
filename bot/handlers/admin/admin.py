from aiogram import types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F
from handlers.filters import AdminFilter

from .router import router


@router.message(Command("admin"), AdminFilter())
async def admin_handler(message: types.Message) -> None:
    keyboard = InlineKeyboardBuilder([[
        types.InlineKeyboardButton(    
            text="Заявки", callback_data="requests"
        ),
        types.InlineKeyboardButton(
            text="Сотрудники", callback_data="employees"
        )
    ]])

    await message.answer("Панель администратора.", reply_markup=keyboard.as_markup())
    
    
@router.callback_query(lambda cd: cd.data == "admin", AdminFilter())
async def admin_callback(callback: types.CallbackQuery) -> None:
    keyboard = InlineKeyboardBuilder([[
        types.InlineKeyboardButton(    
            text="Заявки", callback_data="requests"
        ),
        types.InlineKeyboardButton(
            text="Сотрудники", callback_data="employees"
        )
    ]])

    await callback.message.edit_text(
        "Панель администратора.", reply_markup=keyboard.as_markup()
    )
