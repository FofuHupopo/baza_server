from django.urls import path

from . import views


urlpatterns = [
    path("", views.AddressView.as_view(), name="profile_address"),
    path("<int:pk>/", views.AddressDetailView.as_view(), name="profile_address_detail"),
]
