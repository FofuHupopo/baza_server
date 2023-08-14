from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request, HttpRequest
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt import exceptions
from django.conf import settings


from .models import AuthCodeModel, UserModel
from .serializers import PhoneNumberSerializer, LoginSerializer, UserDataSerialzier


class SendCodeView(APIView):
    permission_classes = (AllowAny, )
    serializer_class = PhoneNumberSerializer

    def post(self, request: Request):
        serializer = self.serializer_class(data=request.data)
    
        if not serializer.is_valid():
            return Response(serializer.errors)
        
        phone = serializer.validated_data['phone']
        code = AuthCodeModel.generate_code(phone)
        
        print(f"{code.phone}: {code.code}")

        return Response(
            {
                "success": "Код был успешно отправлен.",
                "code": f"{code.code}"
            },
            status.HTTP_201_CREATED
        )


class LoginView(APIView):
    permission_classes = (AllowAny, )
    serializer_class= LoginSerializer

    def post(self, request: Request):
        serializer = self.serializer_class(data=request.data)
    
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            code = serializer.validated_data['code']
            
            if AuthCodeModel.check_code(phone, code):
                user: UserModel = UserModel.objects.filter(
                    phone=phone
                ).first()
                
                if not user:
                    user = UserModel.objects.create_user(
                        phone=phone
                    )
        
                return LoginView.generate_response(user)
            else:
                return Response(
                    {
                        "error": "Неправильный код."
                    },
                    status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(serializer.errors)
    
    @staticmethod
    def generate_response(user: UserModel) -> Response:
        refresh_token: RefreshToken = RefreshToken.for_user(user)
        access_token = refresh_token.access_token

        user_serializer = UserDataSerialzier(user)

        response = Response(
            {
                "access_token": str(access_token),
                "user": user_serializer.data,
                # "refresh_token": str(refresh_token),
            },
            status.HTTP_200_OK
        )

        # response.set_cookie(
        #     key=settings.SIMPLE_JWT["AUTH_COOKIE"],
        #     value=str(refresh_token),
        #     max_age=settings.SIMPLE_JWT["MAX_AGE"],
        #     secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
        #     httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
        #     samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
        #     domain=settings.SIMPLE_JWT['AUTH_COOKIE_DOMAIN']
        # )

        response.set_cookie(
            key="access_token",
            value=str(access_token),
            max_age=60 * 60 * 24 * 30,
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
            domain=settings.SIMPLE_JWT['AUTH_COOKIE_DOMAIN']
        )

        return response


class UpdateTokensView(APIView):
    permission_classes = (AllowAny, )

    def get(self, request: HttpRequest):
        refresh_token = request.COOKIES.get("refresh_token", "")
        
        try:
            payload = RefreshToken(refresh_token).payload
            user = UserModel.objects.get(id=payload['user_id'])

            return LoginView.generate_response(user)
        except exceptions.TokenError as e:
            print(e)
        except UserModel.DoesNotExist as e:
            print(e)
        
        return Response(
            {
                "error": "Ошибка refresh токена"
            },
            status.HTTP_400_BAD_REQUEST
        )
