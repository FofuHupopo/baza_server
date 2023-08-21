from django.urls import path

from . import views


urlpatterns = [
    path("orders/", views.ListOrderView.as_view(), name="order__order")
]
