from django.urls import path

from . import controllers


urlpatterns = [
    path("", controllers.LoyaltyController.as_view(), name="loyalty"),
]
