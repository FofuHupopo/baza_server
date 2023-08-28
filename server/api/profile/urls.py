from django.urls import path

from . import views


urlpatterns = [
    path("favorites/", views.FavoritesView.as_view(), name="favorites"),
    path("info/", views.InfoView.as_view(), name="info"),

    path("cart/", views.CartView.as_view(), name="cart"),
    path("cart/add/", views.CartAddView.as_view(), name="cart-add"),
    path("cart/remove/", views.CartRemoveView.as_view(), name="cart-remove"),
]
