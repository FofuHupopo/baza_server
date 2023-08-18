from django.urls import path

from . import views


urlpatterns = [
    path("send-code/", views.SendCodeView.as_view(), name="auth__send-code"),
    path("login/", views.LoginView.as_view(), name="auth__login"),
    path("logout/", views.LogoutView.as_view(), name="auth__logout")
]
