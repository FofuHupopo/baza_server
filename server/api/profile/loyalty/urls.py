from django.urls import path

from . import controllers


urlpatterns = [
    path("", controllers.LoyaltyController.as_view(), name="loyalty"),
    path("history/", controllers.LoyaltyHistoryController.as_view(), name="loyalty_hisotry"),
    path("faker/", controllers.FakeLoyaltyController.as_view(), name="loyalty_fake"),
]
