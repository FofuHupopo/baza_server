from django.contrib import admin
from django.utils.safestring import mark_safe

from . import models


class ProductModificationImageInline(admin.StackedInline):
    model = models.ProductModificationImageModel
    extra = 1
    
    fields = [
        "image_preview", "image"
    ]

    readonly_fields = ["image_preview"]

    def image_preview(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" style="max-height: 200px;">')
    
    image_preview.short_description = "Изображение"


class ProductModificationInline(admin.TabularInline):
    model = models.ProductModificationModel
    extra = 1

    show_change_link = True


@admin.register(models.ProductModel)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name", "category", "price", "visible"
    ]
    fields = [
        "id", "name", "description", "price",
        "image_preview", "image", "visible",
        "category", "path"
    ]
    search_fields = [
        "name", "description", "category"
    ]
    list_filter = [
        "visible",
        ("description", admin.EmptyFieldListFilter),
        "category"
    ]
    
    readonly_fields = [
        "image_preview"
    ]

    def image_preview(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" style="max-height: 200px;">')
    
    image_preview.short_description = "Главное изображение"

    inlines = [ProductModificationInline]


@admin.register(models.ProductModificationModel)
class ProductModificationAdmin(admin.ModelAdmin):
    list_display = [
        "product", "color", "size", "quantity"
    ]
    fields = [
        "id", "color", "color_preview", "size", "quantity"
    ]
    
    readonly_fields = [
        "color_preview"
    ]
    
    def color_preview(self, obj):
        return mark_safe(f"<div style='background-color: #{obj.color.hex_code}; height: 20px; width: 20px; border-radius: 100%'></div>")
    
    color_preview.short_description = "Пример цвета"

    inlines = [ProductModificationImageInline]
    

@admin.register(models.ProductColorModel)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = [
        "name", "hex_code", "color_preview"
    ]
    fields = [
        "name", "hex_code", "color_preview"
    ]
    
    readonly_fields = [
        "color_preview"
    ]
    
    def color_preview(self, obj):
        return mark_safe(f"<div style='background-color: #{obj.hex_code}; height: 20px; width: 20px; border-radius: 100%'></div>")
    
    color_preview.short_description = "Пример цвета"
    

@admin.register(models.ProductSizeModel)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = [
        "name"
    ]
    fields = [
        "name"
    ]
    search_fields = [
        "name"
    ]


@admin.register(models.ProductCategoryModel)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = [
        "category"
    ]
    fields = [
        "category"
    ]
    search_fields = [
        "category"
    ]


class BundleImageInline(admin.StackedInline):
    model = models.BundleImageModel
    extra = 1

    fields = [
        "image_preview", "image"
    ]

    readonly_fields = ["image_preview"]

    def image_preview(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" style="max-height: 200px;">')
    
    image_preview.short_description = "Изображение"


@admin.register(models.BundleModel)
class BundleAdmin(admin.ModelAdmin):
    list_display = [
        "name", "price", "visible"
    ]
    fields = [
        "name", "description",
        "product_modifications", "price",
        "image_preview", "image", "visible",
        "category", "path"
    ]
    search_fields = [
        "name", "description", "category"
    ]
    list_filter = [
        "visible",
        ("description", admin.EmptyFieldListFilter),
        "category"
    ]
    
    readonly_fields = [
        "image_preview"
    ]

    def image_preview(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" style="max-height: 200px;">')
    
    image_preview.short_description = "Главное изображение"

    inlines = [BundleImageInline]


# admin.site.register(models.ProductModificationImageModel)
# admin.site.register(models.ProductModel)
# admin.site.register(models.ProductPathModel)
# admin.site.register(models.ProductCategoryModel)
# admin.site.register(models.ProductModificationModel)
# admin.site.register(models.ProductColorModel)
# admin.site.register(models.ProductSizeModel)
