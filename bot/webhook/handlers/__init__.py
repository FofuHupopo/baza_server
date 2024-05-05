from ..app import app
from .orders import new_order_handler


app.router.add_post("/new-order/", new_order_handler)
