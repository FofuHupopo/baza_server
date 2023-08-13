from django.contrib import admin
from django.contrib.auth.models import Group

from . import models


@admin.register(models.UserModel)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        "name", "surname", "email", "phone"
    ]
    fields = [
        "name", "surname", "email", "phone",
        "birthday_date", "date_joined", "last_login",
        "favorites", "basket",
        "is_active", "is_superuser"
    ]

admin.site.register(models.AuthCodeModel)
# admin.site.register(models.UserModel)

admin.site.unregister(Group)
