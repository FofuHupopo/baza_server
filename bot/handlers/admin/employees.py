from aiogram import types
from handlers.filters import AdminFilter

from db.repository import UserRepository
from bot.utils import send_message
from .router import router


@router.callback_query(lambda cd: cd.data == "employees", AdminFilter())
async def employees_callback(callback: types.CallbackQuery) -> None:
    await callback.message.edit_text(
        "Меню сотрудников.",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="Список сотрудников", callback_data="view_employee_1"
                    ),
                ],
                [
                    types.InlineKeyboardButton(
                        text="назад", callback_data="admin"
                    ),
                ]
            ]
        ),
    )


@router.callback_query(lambda cd: cd.data.startswith("view_employee_"), AdminFilter())
async def view_employee_callback(callback: types.CallbackQuery) -> None:
    page = int(callback.data.replace("view_employee_", ""))
    
    user, count, next_page, prev_page = UserRepository.get_user_by_page(page)
    
    keyboard_panel_row = [
        types.InlineKeyboardButton(
            text="Назад", callback_data="employees"
        ),
    ]

    if prev_page:
        keyboard_panel_row = [
            types.InlineKeyboardButton(
                text="<<", callback_data=f"view_employee_{prev_page}"
            )
        ] + keyboard_panel_row
        
    if next_page:
        keyboard_panel_row.append(
            types.InlineKeyboardButton(
                text=">>", callback_data=f"view_employee_{next_page}"
            )
        )
        

    if user:
        message = f"Cотрудник ({page} из {count}):\nИмя: {user.username}"

        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="Удалить", callback_data=f"employee_delete_{user.id}"
                    ),
                ],
                keyboard_panel_row
            ]
        )
    else:
        message = "У вас пока что нет сотрудников("

        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[keyboard_panel_row]
        )

    await callback.message.edit_text(
        message,
        reply_markup=keyboard
    )


@router.callback_query(lambda cd: cd.data.startswith("employee_delete_"), AdminFilter())
async def employee_delete_callback(callback: types.CallbackQuery) -> None:
    user_id = int(callback.data.replace("employee_delete_", ""))
    UserRepository.delete_user(user_id)
    
    return await employees_callback(callback)
