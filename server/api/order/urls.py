from django.urls import path

from . import views


urlpatterns = [
    path("orders/", views.OrderView.as_view(), name="order__orders"),
    # path("calculate/", views.CalculatePriceView.as_view(), name="order__calculate"),
    
    path("calculate/", views.CalculateView.as_view(), name="order__calculate"),
    path("orders/cancel/", views.CancelOrderView.as_view(), name="order__cancel"),
    
    path("payment/", views.PaymentView.as_view(), name="order__payment_init"),
    path("payment/status/", views.PaymentStatusView.as_view(), name="order__payment_status"),
    
    path("payment/response/success/<str:payment_id>", views.PaymentResponseSuccessView.as_view(), name="order__payment_response_success"),
    path("payment/response/fail/<str:payment_id>", views.PaymentResponseFailView.as_view(), name="order__payment_response_fail"),
]
