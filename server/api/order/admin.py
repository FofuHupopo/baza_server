from django.contrib import admin

from . import models


class ProductModificationInline(admin.StackedInline):
    model = models.OrderModel.products_modification.through
    extra = 0


@admin.register(models.OrderModel)
class OrderAdmin(admin.ModelAdmin):
    inlines = [ProductModificationInline]
