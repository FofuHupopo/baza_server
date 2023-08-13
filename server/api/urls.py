from django.urls import path, include


urlpatterns = [
    path("auth/", include("api.authentication.urls")),
    path("profile/", include("api.profile.urls")),
    path("products/", include("api.products.urls")),
]
