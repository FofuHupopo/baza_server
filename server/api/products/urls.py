from django.urls import path

from . import views


urlpatterns = [
    path("path/", views.ProductPathView.as_view(), name="path"),
    path("filter/", views.ListProductView.as_view(), name="filter-products"),
    path("product/<int:pk>/", views.ProductView.as_view(), name="product"),
]
