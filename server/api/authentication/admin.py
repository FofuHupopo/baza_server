from django.contrib import admin
from django.contrib.auth.models import Group

from . import models


class CartInlineAdmin(admin.StackedInline):
    model = models.CartModel
    
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
        "favorites", "is_active", "is_superuser", "date_joined"
    ]
    
    inlines = [CartInlineAdmin]


admin.site.register(models.AuthCodeModel)
admin.site.register(models.CartModel)

admin.site.unregister(Group)
