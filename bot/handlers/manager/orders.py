from aiogram import types
from handlers.filters import ManagerFilter

from db.repository import UserRepository
from .router import router
from .keyboards import orders_keyboard


@router.callback_query(lambda cd: cd.data == "orders", ManagerFilter())
async def orders_callback(callback: types.CallbackQuery) -> None:
    user = UserRepository.get_user_by_tg_id(callback.from_user.id)
        
    await callback.message.edit_text("Заказы.", reply_markup=orders_keyboard)
