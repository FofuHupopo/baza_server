from aiogram import types


menu_keyboard_notifications_on = types.InlineKeyboardMarkup(inline_keyboard=[
    [
        types.InlineKeyboardButton(
            text="Заказы", callback_data="orders"
        )
    ],
    [
        types.InlineKeyboardButton(
            text="Отключить уведомления", callback_data="notifications_off"
        )
    ]
])


menu_keyboard_notifications_off = types.InlineKeyboardMarkup(inline_keyboard=[
    [
        types.InlineKeyboardButton(
            text="Заказы", callback_data="orders"
        )
    ],
    [
        types.InlineKeyboardButton(
            text="Включить уведомления", callback_data="notifications_on"
        )
    ]
])


orders_keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
    [
        types.InlineKeyboardButton(
            text="Новые заказы", callback_data="orders_new"
        ),
    ],
    [
        types.InlineKeyboardButton(
            text="Заказы в работе", callback_data="orders_working"
        )
    ],
    [
        types.InlineKeyboardButton(
            text="История заказов", callback_data="orders_history"
        )
    ],
    [
        types.InlineKeyboardButton(
            text="Поиск заказа по id", callback_data="orders_search"
        )
    ]
])
