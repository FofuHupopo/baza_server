from django.urls import path

from . import views


urlpatterns = [
    path("orders/", views.OrderView.as_view(), name="order__orders"),
    path("calculate/", views.CalculatePriceView.as_view(), name="order__calculate"),
    
    path("pre-calculate/", views.PreCalculatePriceView.as_view(), name="order__pre_calculate"),
    
    path("payment/", views.PaymentView.as_view(), name="order__payment_init"),
    path("payment/status/", views.PaymentStatusView.as_view(), name="order__payment_status"),
    
    path("payment/response/success/<int:payment_id>", views.PaymentResponseSuccessView.as_view(), name="order__payment_response_success"),
    path("payment/response/fail/<int:payment_id>", views.PaymentResponseFailView.as_view(), name="order__payment_response_fail"),
]
