from django.contrib import admin
from django.contrib.auth.models import Group

from . import models


class BasketInlineAdmin(admin.StackedInline):
    model = models.BasketModel
    
    fields = [
        "product_modification_model", "quantity"
    ]


@admin.register(models.UserModel)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        "name", "surname", "email", "phone"
    ]
    fields = [
        "name", "surname", "email", "phone",
        "birthday_date", "last_login",
        "city", "street", "house", "frame", "apartment",
        "favorites", "is_active", "is_superuser", "date_joined"
    ]
    
    inlines = [BasketInlineAdmin]


admin.site.register(models.AuthCodeModel)
admin.site.register(models.BasketModel)

admin.site.unregister(Group)
