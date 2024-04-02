from types import NoneType
from django.db import models
from django.core import validators
from slugify import slugify


class ProductPathModel(models.Model):
    parent = models.ForeignKey(
        "ProductPathModel", models.CASCADE,
        null=True, blank=True,
        verbose_name="Родитель"
    )
    name = models.CharField(
        "Название",
        max_length=63
    )
    slug = models.SlugField(
        "Слаг (создается автоматически)",
        unique=True,
        blank=True
    )
    
    class Meta:
        db_table = "product__path"
        verbose_name = "Путь товара"
        verbose_name_plural = "Пути товаров"

    def __str__(self):
        return (f"{self.parent}/" if self.parent else "") + f"{self.name}"
    
    def get_slug_path(self):
        return (f"{self.parent.get_slug_path()}/" if self.parent else "") + f"{self.slug}"
    
    def save(self, *args, **kwargs) -> None:
        if not (self.parent is None and self.slug is not None):
            self.slug = (self.parent.slug if self.parent else "") + "--" + slugify(self.name)
        # self.slug = slugify(self.__str__().replace("/", " "))

        return super().save(*args, **kwargs)
    

def category_image_upload_path(instance, filename):
    return 'category_size/{}/{}'.format(instance.category, filename)


class ProductCategoryModel(models.Model):
    name = models.CharField(
        "Название категории", max_length=127
    )
    size_image = models.ImageField(
        upload_to=category_image_upload_path,
        max_length=511,
        default="product_images/Заглушка фото карточки товара.jpg",
        verbose_name="Выбрать изображение размеров для категории"
    )
    
    class Meta:
        db_table = "product__product_category"
        verbose_name = "Категория товара"
        verbose_name_plural = "Категории товаров"
    
    def __str__(self) -> str:
        return f"{self.name}"


def product_image_upload_path(instance, filename):
    return 'product_images/{}/{}'.format(instance.product_id, filename)


class ProductModel(models.Model):
    product_id = models.CharField(
        "МойСклад id", max_length=63
    )
    name = models.CharField(
        "Название", max_length=255
    )
    description = models.TextField(
        "Описание",
        null=True, blank=True
    )
    code = models.CharField(
        "Код MoySklad", max_length=32,
        null=True, blank=True
    )
    
    old_price = models.IntegerField(
        "Старая цена",
        null=True, blank=True
    )
    price = models.IntegerField(
        "Цена"
    )
    
    visible = models.BooleanField(
        "Отображается на сайте?",
        default=False
    )
    
    image = models.ImageField(
        upload_to=product_image_upload_path,
        max_length=511,
        default="product_images/Заглушка фото карточки товара.jpg",
        verbose_name="Выбрать главное изображение"
    )
    
    category = models.ForeignKey(
        ProductCategoryModel, models.CASCADE,
        verbose_name="Категория товара"
    )
    path = models.ForeignKey(
        ProductPathModel, models.CASCADE,
        verbose_name="Путь к товару"
    )
    
    class Meta:
        db_table = "product__product"
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        
    def __str__(self) -> str:
        return f"{self.name}"
        

class ProductColorModel(models.Model):
    name = models.CharField(
        "Название", max_length=127
    )
    eng_name = models.CharField(
        "Английское название", max_length=127,
        null=True, blank=True
    )
    hex_code = models.CharField(
        "HEX цвета", max_length=6,
        validators=[validators.MinLengthValidator(6)],
        null=True, blank=True
    )

    class Meta:
        db_table = "product__product_color"
        verbose_name = "Цвет"
        verbose_name_plural = "Цвета"
    
    def __str__(self) -> str:
        return f"{self.name}"
    
    def save(self, *args, **kwargs) -> None:
        self.hex_code = self.hex_code.replace("#", "")
        
        if not self.eng_name:
            self.eng_name = slugify(self.name)

        return super().save(*args, **kwargs)


class ProductSizeModel(models.Model):
    name = models.CharField(
        "Название размера",
        max_length=63
    )

    class Meta:
        db_table = "product__product_size"
        verbose_name = "Размер"
        verbose_name_plural = "Размеры"
    
    def __str__(self) -> str:
        return f"{self.name}"


class ProductModificationModel(models.Model):
    product = models.ForeignKey(
        ProductModel, models.CASCADE,
        verbose_name="Родительский товар"
    )
    slug = models.SlugField(
        "Слаг", max_length=255,
        unique=True, db_index=True,
        null=True, blank=True
    )
    modification_id = models.CharField(
        "МойСклад id", max_length=63
    )

    color = models.ForeignKey(
        ProductColorModel, models.CASCADE,
        verbose_name="Цвет товара",
        null=True, blank=True
    )
    size = models.ForeignKey(
        ProductSizeModel, models.CASCADE,
        verbose_name="Размер товара",
        null=True, blank=True
    )
    weight = models.IntegerField(
        "Вес (граммы)", default=0
    )
    
    booked = models.IntegerField(
        "Забронировано", default=0
    )
    quantity = models.IntegerField(
        "Количество", default=0
    )

    visible = models.BooleanField(
        "Отображается на сайте?", default=False
    )
    
    @property
    def count(self):
        count = self.quantity - self.booked
        
        if count >= 0:
            return count
    
        return 0

    class Meta:
        db_table = "product__product_modification"
        verbose_name = "Модификация товара"
        verbose_name_plural = "Модификации товаров"

    def __str__(self) -> str:
        if self.color:
            return f"{self.product.name} ({self.color.name}, {self.size})"
        else:
            return f"{self.product.name} ({self.size})"

    def save(self, *args, **kwargs) -> None:
        if type(self.color) is NoneType:
            self.color, _ = ProductColorModel.objects.get_or_create(
                name="Стандартный"
            )

        if type(self.size) is NoneType:
            self.size, _ = ProductSizeModel.objects.get_or_create(
                name="OS"
            )

        self.slug = slugify(f"{self.product.name} {self.product.code} {self.color.name} {self.size.name}")

        return super().save(*args, **kwargs)

    @property
    def name(self):
        return f"{self.product.name} ({self.color.name}, {self.size.name})"
    
    def get_product_slug(self):
        return "-".join(self.slug.split("-")[:-1])


def product_color_images_upload_path(instance, filename):
    return 'product_images/{}/{}/{}'.format(
        instance.product_color.product.product_id,
        instance.product_color.color.name,
        filename
    )


class ProductColorImagesModel(models.Model):
    product = models.ForeignKey(
        ProductModel, models.CASCADE,
        verbose_name="Товар"
    )
    color = models.ForeignKey(
        ProductColorModel, models.CASCADE,
        verbose_name="Цвет"
    )
    additional_description = models.TextField(
        "Дополнительное описание к цвету", default="",
        null=True, blank=True
    )

    class Meta:
        db_table = "product__product_color_images"
        verbose_name = "Изображения товара по цвету"
        verbose_name_plural = "Изображения товаров по цветам"
    
    def __str__(self) -> str:
        return f"{self.product.name} {self.color}"


class ColorImageModel(models.Model):
    product_color = models.ForeignKey(
        ProductColorImagesModel, models.CASCADE,
        verbose_name="Цвет товара"
    )
    image = models.ImageField(
        upload_to=product_color_images_upload_path,
        max_length=511,
        default="product_images/Заглушка фото карточки товара.jpg",
        verbose_name="Выбрать изображение"
    )
    
    class Meta:
        db_table = "product__color_image"
        verbose_name = "Изображение цвету"
        verbose_name_plural = "Изображения по цветам"
    
    def __str__(self) -> str:
        return f"{self.product_color.product.name}"
    

def bundle_image_upload_path(instance, filename):
    return 'product_images/{}/{}'.format(
        instance.bundle_id,
        filename
    )


# class ParentBundleModel(models.Model):
#     bundle_id = models.CharField(
#         "МойСклад id", max_length=63
#     )
#     name = models.CharField(
#         "Название", max_length=255
#     )
#     description = models.TextField(
#         "Описание",
#         null=True, blank=True
#     )
#     visible = models.BooleanField(
#         "Отображается на сайте?",
#         default=True
#     )
#     price = models.IntegerField(
#         "Цена"
#     )
#     old_price = models.IntegerField(
#         "Цена"
#     )

#     image = models.ImageField(
#         upload_to=bundle_image_upload_path,
#         max_length=511,
#         default="product_images/Заглушка фото карточки товара.jpg",
#         verbose_name="Выбрать главное изображение"
#     )

#     category = models.ForeignKey(
#         ProductCategoryModel, models.CASCADE,
#         verbose_name="Категория товара",
#         null=True, blank=True
#     )
#     path = models.ForeignKey(
#         ProductPathModel, models.CASCADE,
#         verbose_name="Путь к комплекту"
#     )

#     class Meta:
#         db_table = "product__parent_bundle"
#         verbose_name = "Родительский комплект"
#         verbose_name_plural = "Родительские комплекты"
    
#     def __str__(self) -> str:
#         return f"{self.name}"


# class BundleModel(models.Model):
#     parent_bundle = models.ForeignKey(
#         ParentBundleModel, models.CASCADE,
#         verbose_name="Родительский комплект"
#     )

#     color = models.ForeignKey(
#         ProductColorModel, models.CASCADE,
#         verbose_name="Цвет товара",
#         null=True, blank=True
#     )
#     size = models.ForeignKey(
#         ProductSizeModel, models.CASCADE,
#         verbose_name="Размер товара",
#         null=True, blank=True
#     )
    
#     products = models.ManyToManyField(
#         ProductModificationModel,
#         verbose_name="Продукты"
#     )
    
#     class Meta:
#         db_table = "product__bundle"
#         verbose_name = "Комплект"
#         verbose_name_plural = "Комплекты"
        
#     def __str__(self) -> str:
#         return f"{self.parent_bundle.name} {self.color.name} {self.size.name}"


def bundle_images_upload_path(instance, filename):
    return 'product_images/{}/{}'.format(
        instance.bundle.bundle_id,
        filename
    )


# class BundleImageModel(models.Model):
#     bundle = models.ForeignKey(
#         BundleModel, models.CASCADE,
#         related_name="images",
#         verbose_name="Комплект"
#     )
#     image = models.ImageField(
#         upload_to=bundle_images_upload_path,
#         max_length=511,
#         default="product_images/Заглушка фото карточки товара.jpg",
#         verbose_name="Выбрать изображение"
#     )

#     class Meta:
#         db_table = "product__bundle_image"
#         verbose_name = "Изображение комплекта"
#         verbose_name_plural = "Изображения комплекта"
    
#     def __str__(self) -> str:
#         return f"{self.bundle}"


def product_modification_image_upload_path():
    ...
    

class ProductModificationImageModel:
    ...
