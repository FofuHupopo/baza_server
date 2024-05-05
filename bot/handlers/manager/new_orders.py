from aiogram import types
from handlers.filters import ManagerFilter

from db.repository import UserRepository, OrderRepository
from .router import router
from .keyboards import orders_keyboard


@router.callback_query(lambda cd: cd.data == "orders", ManagerFilter())
async def orders_callback(callback: types.CallbackQuery) -> None:
    orders = OrderRepository.get_new_orders()

    await callback.message.edit_text("Заказы.", reply_markup=orders_keyboard)


# @router.callback_query(lambda cd: cd.data.startswith("order_page_"), ManagerFilter())
# async def order_page_callback(callback: types.CallbackQuery) -> None:
#     page = int(callback.data.split("_")[-1])
#     order_id = int(callback.data.split("_")[2])
#     order = OrderRepository.get_order_by_id(order_id)

#     user_id = callback.from_user.id
#     user = UserRepository.get_user_by_tg_id(user_id)

#     await callback.message.delete()

#     if order is not None:
#         keyboard = order_keyboard(order, page, user)
#         text = f"Заказ #{order.id}"

#         if order.status == OrderStatus.CANCELED:
#             text += "\nЗаказ отменен."

#         await bot.send_message(
#             callback.from_user.id,
#             text,
#             parse_mode="HTML",
#             reply_markup=keyboard
#         )


# def order_keyboard(order: OrderModel, page: int, user: UserModel) -> types.InlineKeyboardMarkup:
#     markup = types.InlineKeyboardMarkup()
#     items = order.items
#     per_page = 5

#     index_start = (page - 1) * per_page
#     index_end = page * per_page

#     if len(items) > per_page:
#         if page > 1:
#             markup.add(types.InlineKeyboardButton(
#                 text="Предыдущая",
#                 callback_data=f"order_page_{order.id}_{page - 1}"
#             ))

#         if index_end < len(items):
#             markup.add(types.InlineKeyboardButton(
#                 text="Следующая",
#                 callback_data=f"order_page_{order.id}_{page + 1}"
#             ))

#     for i in range(index_start, index_end):
#         if i >= len(items):
#             break

#         item = items[i]
#         markup.add(
#             types.InlineKeyboardButton(
#                 text=f"{item.product.name} x {item.quantity}",
#                 callback_data=f"item_page_{item.id}_{order.id}"
#             )
#         )

#         if user.is_manager:
#             markup.add(
#                 types.InlineKeyboardButton(
#                     text="Отменить",
#                     callback_data=f"cancel_item_{item.id}_{order.id}"
#                 )
#             )

#     return markup


# @router.callback_query(lambda cd: cd.data.startswith("item_page_"), ManagerFilter())
# async def item_page_callback(callback: types.CallbackQuery) -> None:
#     item_id = int(callback.data.split("_")[1])
#     order_id = int(callback.data.split("_")[2])

#     order = OrderRepository.get_order_by_id(order_id)
#     item = OrderItemRepository.get_order_item_by_id(item_id)

#     if item is not None and order is not None:
#         await callback.message.delete()
#         await bot.send_message(
#             callback.from_user.id,
#             f"{item.product.name} x {item.quantity}",
#             parse_mode="HTML"
#         )
