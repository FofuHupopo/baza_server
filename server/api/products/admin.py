from django.contrib import admin
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.utils.safestring import mark_safe
from django.http import HttpResponseRedirect
from django.utils.html import escape
from django.shortcuts import render, redirect
from django.contrib import messages

from . import models


class ColorImageInline(admin.StackedInline):
    model = models.ColorImageModel
    extra = 1
    
    readonly_fields = ["image_preview"]
    
    def image_preview(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" style="max-height: 200px;">')
    
    image_preview.short_description = "Изображение"
    


class ProductColorImagesInline(admin.StackedInline):
    model = models.ProductColorImagesModel
    extra = 0
    
    fields = [
        "color", "additional_description","images", "go_to_images", "upload_multiple_images"
    ]

    readonly_fields = ["images", "go_to_images", "upload_multiple_images"]

    def images(self, obj):
        images = models.ColorImageModel.objects.filter(
           product_color=obj 
        )

        image_ui_block = "".join([
            '<div style="display: flex; flex-direction: column; margin-right: 20px;">'
                f'<img src="{image.image.url}" style="max-height: 200px; margin-bottom: 5px;">'
                f'<input type="button" value="Удалить" onclick="window.location.href = `/admin/products/colorimagemodel/{image.pk}/delete/?product_id={obj.product.pk}`"/>'
            '</div>'
            for image in images
        ])

        return mark_safe(
            '<div style="display: flex; flex-wrap: wrap;">' +
            image_ui_block +
            '</div>'
        )

    
    images.short_description = "Изображения"
    images.allow_tags = True
    
    def go_to_images(self, obj):
        if obj.pk:
            return mark_safe(f'<a href="/admin/products/productcolorimagesmodel/{obj.pk}/change/"><input type="button" value="Добавить"></a>')
        else:
            return mark_safe("<h3>Сначала выберите цвет и сохраните товар.</h3>")

    go_to_images.short_description = "Загрузить одно изображение"
    go_to_images.allow_tags = True
    
    
    def upload_multiple_images(self, obj):
        response = render(HttpRequest(), "upload-multiple-images.html", {"product_color_id": obj.pk})
        return mark_safe(response.content.decode("utf-8"))

    upload_multiple_images.short_description = "Загрузить несколько изображений"
    go_to_images.allow_tags = True


class ProductModificationInline(admin.TabularInline):
    model = models.ProductModificationModel
    extra = 0
    
    fields = (
        "color", "size", "quantity", "visible"
    )

    show_change_link = True


@admin.register(models.ProductModel)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name", "category", "price", "visible"
    ]
    fields = [
        "pk", "name", "description", "composition_and_care",
        "code", "price", "old_price",
        "image_preview", "image", "visible",
        "category", "path"
    ]
    search_fields = [
        "name", "description", "code"
    ]
    list_filter = [
        "visible",
        ("description", admin.EmptyFieldListFilter),
        "category"
    ]
    
    readonly_fields = [
        "pk", "image_preview"
    ]

    def image_preview(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" style="max-height: 200px;">')
    
    image_preview.short_description = "Главное изображение"
    
    
    def make_visible(modeladmin, request, queryset):
        queryset.update(visible=True)
    
    make_visible.short_description = "Отобразить на сайте"
    
    
    def make_not_visible(modeladmin, request, queryset):
        queryset.update(visible=False)
    
    make_not_visible.short_description = "Cкрыть на сайте"
    
    actions = [make_visible, make_not_visible]

    inlines = [ProductColorImagesInline, ProductModificationInline]


@admin.register(models.ProductModificationModel)
class ProductModificationAdmin(admin.ModelAdmin):
    list_display = [
        "product", "color", "size", "quantity", "reserved"
    ]
    fields = [
        "pk", "color", "color_preview", "size", "quantity", "reserved"
    ]
    
    readonly_fields = [
        "pk", "color_preview"
    ]
    
    def color_preview(self, obj):
        return mark_safe(f"<div style='background-color: #{obj.color.hex_code}; height: 20px; width: 20px; border-radius: 100%'></div>")
    
    color_preview.short_description = "Пример цвета"

    # inlines = [ProductModificationImageInline]
    

@admin.register(models.ProductColorModel)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = [
        "name", "eng_name", "hex_code", "color_preview"
    ]
    fields = [
        "name", "eng_name", "hex_code", "color_preview"
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
        "name"
    ]
    fields = [
        "name", "size_image"
    ]
    search_fields = [
        "name"
    ]


# class BundleImageInline(admin.StackedInline):
#     model = models.BundleImageModel
#     extra = 1

#     fields = [
#         "image_preview", "image"
#     ]

#     readonly_fields = ["image_preview"]

#     def image_preview(self, obj):
#         return mark_safe(f'<img src="{obj.image.url}" style="max-height: 200px;">')
    
#     image_preview.short_description = "Изображение"


# @admin.register(models.BundleModel)
# class BundleAdmin(admin.ModelAdmin):
#     list_display = [
#         "name", "price", "visible"
#     ]
#     fields = [
#         "name", "description",
#         "product_modifications", "price",
#         "image_preview", "image", "visible",
#         "category", "path"
#     ]
#     search_fields = [
#         "name", "description", "category"
#     ]
#     list_filter = [
#         "visible",
#         ("description", admin.EmptyFieldListFilter),
#         "category"
#     ]
    
#     readonly_fields = [
#         "image_preview"
#     ]

#     def image_preview(self, obj):
#         return mark_safe(f'<img src="{obj.image.url}" style="max-height: 200px;">')
    
#     image_preview.short_description = "Главное изображение"

#     inlines = [BundleImageInline]


@admin.register(models.ProductColorImagesModel)
class ProductColorImagesAdmin(admin.ModelAdmin):
    fields = [
        "color", "go_product"
    ]
    readonly_fields = ["go_product"]
    
    def go_product(self, obj):
        return mark_safe(f'<a href="/admin/products/productmodel/{obj.product.pk}/change/"><input type="button" value="Вернуться"></a>')
    
    go_product.short_description = "Вернуться к товару"
    go_product.allow_tags = True

    inlines = [ColorImageInline]


@admin.register(models.ColorImageModel)
class ColorImageAdmin(admin.ModelAdmin):
    fields = [
        "image_preview", "image"
    ]

    readonly_fields = ["image_preview"]

    def image_preview(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" style="max-height: 200px;">')
    
    image_preview.short_description = "Изображение"
    
    def response_delete(self, request: HttpRequest, obj_display: str, obj_id: int) -> HttpResponse:
        product_id = request.GET.get("product_id")

        if product_id:
            url = f"/admin/products/productmodel/{product_id}/change/"
            return HttpResponseRedirect(url)
        else:
            return super().response_delete(request, obj_display, obj_id)


# admin.site.register(models.ColorImageModel)
# admin.site.register(models.ProductModel)
admin.site.register(models.ProductPathModel)
# admin.site.register(models.ProductCategoryModel)
# admin.site.register(models.ProductModificationModel)
# admin.site.register(models.ProductColorModel)
# admin.site.register(models.ProductSizeModel)
