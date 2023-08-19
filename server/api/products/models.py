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
        self.slug = slugify(self.__str__().replace("/", " "))

        return super().save(*args, **kwargs)
    

def category_image_upload_path(instance, filename):
    return 'category_size/{}/{}'.format(instance.category, filename)


class ProductCategoryModel(models.Model):
    category = models.CharField(
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
        return f"{self.category}"


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
    old_price = models.IntegerField(
        "Старая цена",
        null=True, blank=True
    )
    price = models.IntegerField(
        "Цена"
    )
    visible = models.BooleanField(
        "Отображается на сайте?",
        default=True
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
    quantity = models.IntegerField(
        "Количество", default=0
    )
    
    class Meta:
        db_table = "product__product_modification"
        verbose_name = "Модификация товара"
        verbose_name_plural = "Модификации товаров"
    
    def __str__(self) -> str:
        if self.color:
            return f"{self.product.name} ({self.color.name}, {self.size})"
        else:
            return f"{self.product.name} ({self.size})"


def product_modification_image_upload_path(instance, filename):
    return 'product_images/{}/{}/{}'.format(
        instance.product_modification.product.product_id,
        instance.id,
        filename
    )


class ProductModificationImageModel(models.Model):
    product_modification = models.ForeignKey(
        ProductModificationModel, models.CASCADE,
        related_name="images",
        verbose_name="Модификация товара"
    )
    image = models.ImageField(
        upload_to=product_modification_image_upload_path,
        max_length=511,
        default="product_images/Заглушка фото карточки товара.jpg",
        verbose_name="Выбрать изображение"
    )
    
    class Meta:
        db_table = "product__product_modification_image"
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"
    
    def __str__(self) -> str:
        return f"{self.product_modification}"
    

def bundle_image_upload_path(instance, filename):
    return 'product_images/{}/{}'.format(
        instance.bundle_id,
        filename
    )


class BundleModel(models.Model):
    bundle_id = models.CharField(
        "МойСклад id", max_length=63
    )
    name = models.CharField(
        "Название", max_length=255
    )
    description = models.TextField(
        "Описание",
        null=True, blank=True
    )
    product_modifications = models.ManyToManyField(
        ProductModificationModel, 
        verbose_name="Продукты комплекта",
        blank=True
    )
    visible = models.BooleanField(
        "Отображается на сайте?",
        default=True
    )
    price = models.IntegerField(
        "Цена"
    )

    image = models.ImageField(
        upload_to=bundle_image_upload_path,
        max_length=511,
        default="product_images/Заглушка фото карточки товара.jpg",
        verbose_name="Выбрать главное изображение"
    )

    category = models.ForeignKey(
        ProductCategoryModel, models.CASCADE,
        verbose_name="Категория товара",
        null=True, blank=True
    )
    path = models.ForeignKey(
        ProductPathModel, models.CASCADE,
        verbose_name="Путь к комплекту"
    )

    class Meta:
        db_table = "product__bundle"
        verbose_name = "Комплект товаров"
        verbose_name_plural = "Комплекты товаров"
    
    def __str__(self) -> str:
        return f"{self.name}"


def bundle_images_upload_path(instance, filename):
    return 'product_images/{}/{}'.format(
        instance.bundle.bundle_id,
        filename
    )


class BundleImageModel(models.Model):
    bundle = models.ForeignKey(
        BundleModel, models.CASCADE,
        related_name="images",
        verbose_name="Комплект"
    )
    image = models.ImageField(
        upload_to=bundle_images_upload_path,
        max_length=511,
        default="product_images/Заглушка фото карточки товара.jpg",
        verbose_name="Выбрать изображение"
    )
    
    class Meta:
        db_table = "product__bundle_image"
        verbose_name = "Изображение комплекта"
        verbose_name_plural = "Изображения комплекта"
    
    def __str__(self) -> str:
        return f"{self.bundle}"
