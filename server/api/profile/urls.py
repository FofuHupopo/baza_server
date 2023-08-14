from django.urls import path

from . import views


urlpatterns = [
    path("favorites/", views.FavoritesView.as_view(), name="favorites"),
    path("basket/", views.BasketView.as_view(), name="basket"),
    path("info/", views.InfoView.as_view(), name="info")
]
