from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, TokenError
from django.contrib.auth import get_user_model
from django.conf import settings
from django.http.cookie import SimpleCookie


class UpdateAccessTokenMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        token = request.COOKIES.get("access_token")
        
        if not token or not response.get("access_token", {}).get("comment"):
            return response

        try:
            access_token = AccessToken(token)
        except TokenError:
            response.delete_cookie("access_token")
            return response

        user_id = access_token.payload.get("user_id")
        
        if not user_id:
            return response
        
        user = get_user_model().objects.filter(
            pk=user_id
        ).first()
        
        if not user:
            return response

        refresh_token: RefreshToken = RefreshToken.for_user(user)
        new_access_token = refresh_token.access_token
        
        response.set_cookie(
            key="access_token",
            value=str(new_access_token),
            max_age=60 * 60 * 24 * 30,
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
            domain=settings.SIMPLE_JWT['AUTH_COOKIE_DOMAIN']
        )
        
        return response


class CookiesTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.COOKIES.get(settings.TOKEN_SETTINGS["COOKIE_NAME"])
        
        if token:
            request.META['HTTP_AUTHORIZATION'] = f'Token {token}'

        return self.get_response(request)
