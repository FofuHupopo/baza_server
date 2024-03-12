from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request, HttpRequest
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from api.request import SendMessage
from django.conf import settings


from .models import AuthCodeModel, UserModel
from .serializers import PhoneNumberSerializer, LoginSerializer, UserDataSerialzier
from api.utils import get_country_phone_code


class SendCodeView(APIView):
    permission_classes = (AllowAny, )
    serializer_class = PhoneNumberSerializer

    def post(self, request: Request):
        serializer = self.serializer_class(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors)
        
        phone = serializer.validated_data['phone']
        
        code = AuthCodeModel.generate_code(phone)
        
        
        print(code.phone, code.code)
        
        if settings.SEND_CODE:
            message_status = SendMessage.send(code.phone, code.code)
        else:
            message_status = 200

        if message_status:
            return Response(
                {
                    "success": "Код успешно отправлен."
                },
                status.HTTP_201_CREATED
            )
        else:
            return Response(
                {
                    "error": "Не удалось отправить код, попробуйте снова через некоторое время."
                },
                status.HTTP_400_BAD_REQUEST
            )


class LoginView(APIView):
    permission_classes = (AllowAny, )
    serializer_class= LoginSerializer

    def post(self, request: Request):
        serializer = self.serializer_class(data=request.data, context={"request": request})
    
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
        
                return LoginView.generate_response(request, user)
            
            return Response(
                {
                    "error": "Неправильный код."
                },
                status.HTTP_400_BAD_REQUEST
            )
        else:
            return Response(serializer.errors)
    
    @staticmethod
    def generate_response(request: Request, user: UserModel) -> Response:
        token, created = Token.objects.get_or_create(user=user)

        user_serializer = UserDataSerialzier(user, context={"request": request})

        response = Response(
            user_serializer.data,
            status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

        response.set_cookie(
            key=settings.TOKEN_SETTINGS["COOKIE_NAME"],
            value=token.key,
            max_age=settings.TOKEN_SETTINGS["COOKIE_MAX_AGE"],
            secure=settings.TOKEN_SETTINGS['COOKIE_SECURE'],
            httponly=settings.TOKEN_SETTINGS['COOKIE_HTTP_ONLY'],
            samesite=settings.TOKEN_SETTINGS['COOKIE_SAMESITE'],
            domain=settings.TOKEN_SETTINGS['COOKIE_DOMAIN']
        )

        return response


class LogoutView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request: Request):
        response = Response(
            {
                "status": "logout"
            },
            status.HTTP_200_OK
        )
        
        if request.COOKIES.get(settings.TOKEN_SETTINGS["COOKIE_NAME"]):
            response.delete_cookie(settings.TOKEN_SETTINGS["COOKIE_NAME"])

        return response


class CountryPhoneCodeView(APIView):
    permission_classes = (AllowAny, )
    
    def get(self, request: Request):
        query = request.query_params.get("q", "")
        limit = request.query_params.get("limit", "5")
        
        if not limit.isnumeric():
            return Response(
                {
                    "error": "'limit' параметр должен быть числом."
                },
                status.HTTP_400_BAD_REQUEST
            )
        
        countries = get_country_phone_code(
            query=query.strip(),
            limit=int(limit)
        )
        
        return Response(
            countries,
            status.HTTP_200_OK
        )
