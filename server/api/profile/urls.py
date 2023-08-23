from django.urls import path

from . import views


urlpatterns = [
    path("favorites/", views.FavoritesView.as_view(), name="favorites"),
    path("cart/", views.BasketView.as_view(), name="cart"),
    path("info/", views.InfoView.as_view(), name="info")
]
