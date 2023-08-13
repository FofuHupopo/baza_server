from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.core.exceptions import ValidationError



class PhoneBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        print(username, password)
        UserModel = get_user_model()

        try:
            phone = username
            user = UserModel.objects.get(phone=phone)
        except UserModel.DoesNotExist:
            return None
        
        if user.check_password(password):
            print("yes")
            return user
        else:
            return None

    def get_user(self, user_id):
        UserModel = get_user_model()

        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
