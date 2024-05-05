from aiogram import types
from handlers.filters import AdminFilter

from db.repository import RequestRepository
from bot.utils import send_message
from .router import router


@router.callback_query(lambda cd: cd.data == "requests", AdminFilter())
async def requests_callback(callback: types.CallbackQuery) -> None:
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="Просмотреть заявки", callback_data="view_request_1"
                ),
            ],
            [
                types.InlineKeyboardButton(
                    text="Назад", callback_data="admin"
                ),
            ]
        ]
    )

    await callback.message.edit_text(
        "Меню заявок.",
        reply_markup=keyboard
    )
    

@router.callback_query(lambda cd: cd.data.startswith("view_request_"), AdminFilter())
async def view_request_callback(callback: types.CallbackQuery) -> None:
    page = int(callback.data.replace("view_request_", ""))
    
    request, count, next_page, prev_page = RequestRepository.get_request_by_page(page)
    
    keyboard_panel_row = [
        types.InlineKeyboardButton(
            text="Назад", callback_data="requests"
        ),
    ]

    if prev_page:
        keyboard_panel_row = [
            types.InlineKeyboardButton(
                text="<<", callback_data=f"view_request_{prev_page}"
            )
        ] + keyboard_panel_row
        
    if next_page:
        keyboard_panel_row.append(
            types.InlineKeyboardButton(
                text=">>", callback_data=f"view_request_{next_page}"
            )
        )
        

    if request:
        message = f"Заявкa ({page} из {count}):\nИмя: {request.username}\nДата обращения: {request.created_at}"

        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="Принять", callback_data=f"request_accept_{request.id}"
                    ),
                    types.InlineKeyboardButton(
                        text="Отклонить", callback_data=f"request_decline_{request.id}"
                    ),
                    
                ],
                keyboard_panel_row
            ]
        )
    else:
        message = "Заявки отсутствуют."
        
        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[keyboard_panel_row]
        )

    await callback.message.edit_text(
        message,
        reply_markup=keyboard
    )


@router.callback_query(lambda cd: cd.data.startswith("request_accept_"), AdminFilter())
async def accept_request_callback(callback: types.CallbackQuery) -> None:
    request_id = int(callback.data.replace("request_accept_", ""))
    request = RequestRepository.get_request_by_id(request_id)
    
    await send_message(request.telegram_id, "Ваша заявка принята.\nВоспользуйтесь командой /menu.")
    RequestRepository.accept_request(request.id)
    
    return await requests_callback(callback)


@router.callback_query(lambda cd: cd.data.startswith("request_decline_"), AdminFilter())
async def delcine_request_callback(callback: types.CallbackQuery) -> None:
    request_id = int(callback.data.replace("request_decline_", ""))
    request = RequestRepository.get_request_by_id(request_id)
    
    await send_message(request.telegram_id, "Ваша заявка отклонена.")
    RequestRepository.decline_request(request.id)
    
    return await requests_callback(callback)
