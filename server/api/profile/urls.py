from django.urls import path, include

from . import views


urlpatterns = [
    path("favorites/", views.FavoritesView.as_view(), name="favorites"),
    path("info/", views.InfoView.as_view(), name="info"),

    path("cart/", views.CartView.as_view(), name="cart"),
    path("cart/add/", views.CartAddView.as_view(), name="cart-add"),
    path("cart/remove/", views.CartRemoveView.as_view(), name="cart-remove"),
    path("cart/clear/", views.CartClearView.as_view(), name="cart-clear"),
    path("cart/maximization/", views.CartMaximizationView.as_view(), name="cart-maximization"),
    
    path("search-address/", views.SearchAddressView.as_view(), name="address__search"),
    
    path("loyalty/", include('api.profile.loyalty.urls')),
]
