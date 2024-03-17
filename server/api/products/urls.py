from django.urls import path

from . import views


urlpatterns = [
    # path("path/", views.ProductPathView.as_view(), name="path"),
    path("path/", views.ProductFakePathView.as_view(), name="path"),
    path("filter/", views.FilterProductModificationView.as_view(), name="filter-products"),
    path("product/<int:pk>/", views.ProductView.as_view(), name="product"),

    path("products/", views.ListProductsView.as_view(), name="list-products"),
    path("detail/<slug:slug>/", views.ProductDetailView.as_view(), name="detail-product"),
]
