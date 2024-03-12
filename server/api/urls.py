from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    path("auth/", include("api.authentication.urls")),
    path("profile/", include("api.profile.urls")),
    path("products/", include("api.products.urls")),
    path("orders/", include("api.order.urls")),

    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"), 
]
