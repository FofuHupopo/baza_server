from rest_framework import serializers

from . import models
from api.authentication import models as auth_models


def get_breadcrumbs(path) -> list:
    result = []

    if path.parent is not None:
        parent_path = models.ProductPathModel.objects.get(pk=path.parent_id)
        
        result = get_breadcrumbs(parent_path)
    
    result.append({
        "slug": path.slug,
        "name": path.name
    })
    
    return result


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductCategoryModel
        fields = ("name", "size_image")


class ProductPathSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = models.ProductPathModel
        fields = (
            "id", "name", "slug", "children"
        )
        depth = 10
    
    def get_children(self, obj):
        children = self.Meta.model.objects.filter(parent=obj.id)
        serializer = self.__class__(children, many=True)
        return serializer.data
    

class AloneProductPathSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductPathModel
        fields = (
            "id", "name", "slug",
        )
    

class ProductColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductColorModel
        fields = (
            "name", "hex_code"
        )


class ProductSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductSizeModel
        fields = (
            "name",
        )


class ProductModificationSerializer(serializers.ModelSerializer):
    color = ProductColorSerializer()
    size = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()

    class Meta:
        model = models.ProductModificationModel
        fields = (
            "id", "color", "size", "quantity"
        )

    def get_size(self, obj):
        return obj.size.name if obj.size else None
    
    def get_quantity(self, obj):
        return obj.count

    
class ShortProductModificationSerializer(serializers.ModelSerializer):
    color = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()
    
    class Meta:
        model = models.ProductModificationModel
        fields = (
            "id", "color", "size", "images", "quantity"
        )
        
    def get_quantity(self, obj):
        return obj.count
        
    def get_size(self, obj):
        return obj.size.name if obj.size else None
    
    def get_color(self, obj):
        return obj.color.name if obj.color else None
    
    def get_images(self, obj):
        product_colors = models.ProductColorImagesModel.objects.filter(
            product=obj.product,
            color=obj.color
        )
        
        images = models.ColorImageModel.objects.filter(
            product_color__in=product_colors
        )
        
        request = self.context.get('request')

        return [
            request.build_absolute_uri(image.image.url)
            for image in images
        ]


class ListProductSerializer(serializers.ModelSerializer):
    path = AloneProductPathSerializer()
    colours = serializers.SerializerMethodField()
    modifications = serializers.SerializerMethodField()

    class Meta:
        model = models.ProductModel
        fields = (
            "id", "name", "price", "image", "colours", "path", "modifications"
        )
        
    def get_colours(self, obj):
        colours = models.ProductModificationModel.objects.filter(
            product=obj
        ).values_list(
            'color__name',
            flat=True
        ).distinct()
        
        return filter(lambda color: color, colours)

    def get_modifications(self, obj):
        return ShortProductModificationSerializer(
            models.ProductModificationModel.objects.filter(
                product=obj
            ),
            many=True,
            context={
                "request": self.context.get("request")
            }
        ).data


class ListProductsSerializer(serializers.ModelSerializer):
    product_id = serializers.SerializerMethodField()
    modification_id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    old_price = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    path = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    colors_count = serializers.SerializerMethodField()

    class Meta:
        model = models.ProductModificationModel
        fields = (
            "product_id", "modification_id", "name", "price", "old_price", "images", "colors_count", "path", "slug"
        )
    
    def get_name(self, obj):
        return f"{obj.product.name} {obj.color.eng_name.title()}"

    def get_price(self, obj):
        return obj.product.price

    def get_old_price(self, obj):
        return obj.product.old_price
    
    def get_product_id(self, obj):
        return obj.product.id
    
    def get_modification_id(self, obj):
        return obj.id
    
    def get_path(self, obj):
        return AloneProductPathSerializer(obj.product.path).data
    
    def get_colors_count(self, obj):
        return models.ProductModificationModel.objects.filter(
            product=obj.product,
            visible=True
        ).values_list(
            'color__name',
            flat=True
        ).distinct().count()

    def get_images(self, obj):
        product_color = models.ProductColorImagesModel.objects.filter(
            product=obj.product,
            color=obj.color
        ).first()

        images = models.ColorImageModel.objects.filter(
            product_color=product_color
        )

        request = self.context.get('request')

        return [
            request.build_absolute_uri(image.image.url)
            for image in images
        ]
    
    def get_slug(self, obj):
        return "-".join(obj.slug.split("-")[:-1])


class FilterProductModificationSerializer(serializers.Serializer):
    products = serializers.SerializerMethodField()
    breadcrumbs = serializers.SerializerMethodField()
    
    def get_products(self, obj):
        products = self.initial_data.get("products")
        return ListProductsSerializer(products, many=True, context=self.context).data

    def get_breadcrumbs(self, obj):
        path = get_breadcrumbs(self.initial_data.get("breadcrumbs"))
        
        return path


class ProductColorImagesSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()

    class Meta:
        model = models.ProductColorImagesModel
        fields = (
            "color", "images"
        )
    
    def get_images(self, obj):
        images = models.ColorImageModel.objects.filter(
            product_color=obj
        )
        
        request = self.context.get('request')

        return [
            request.build_absolute_uri(image.image.url)
            for image in images
        ]
    
    def get_color(self, obj):
        return obj.color.name


class ProductSerializer(serializers.ModelSerializer):
    modifications = serializers.SerializerMethodField()
    path = AloneProductPathSerializer()
    full_path = serializers.SerializerMethodField()
    slug_path = serializers.SerializerMethodField()
    color_images = serializers.SerializerMethodField()

    class Meta:
        model = models.ProductModel
        fields = (
            "id", "name", "description", "composition_and_care", "price", "image", "color_images",
            "category", "path", "modifications", "full_path", "slug_path"
        )
    
    def get_full_path(self, obj):
        return obj.path.__str__()
    
    def get_slug_path(self, obj):
        return obj.path.get_slug_path()
    
    def get_color_images(self, obj):
        return ProductColorImagesSerializer(
            models.ProductColorImagesModel.objects.filter(
                product=obj
            ),
            many=True,
            context={
                "request": self.context["request"]
            }
        ).data
    
    def get_modifications(self, obj):
        return ListProductModificationSerializer(
            models.ProductModificationModel.objects.filter(
                product=obj
            ),
            many=True
        ).data


class ListProductModificationSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    composition_and_care = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    path = serializers.SerializerMethodField()
    full_path = serializers.SerializerMethodField()
    slug_path = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    
    class Meta:
        model = models.ProductModificationModel
        fields = (
            "id", "name", "description", "composition_and_care", "price", "images",
            "category", "path", "full_path", "slug_path", "size", "color"
        )
        depth = 2

    def get_name(self, obj):
        return obj.product.name
    
    def get_description(self, obj):
        return f"{obj.product.description}"
    
    def get_composition_and_care(self, obj):
        return f"{obj.product.composition_and_care}"

    def get_price(self, obj):
        return obj.product.price
    
    def get_category(self, obj):
        return obj.product.category.name
    
    def get_path(self, obj):
        return AloneProductPathSerializer(obj.product).data
    
    def get_full_path(self, obj):
        return obj.product.path.__str__()
    
    def get_slug_path(self, obj):
        return obj.product.path.get_slug_path()
    
    def get_size(self, obj):
        return obj.size.name if obj.size else None
    
    def get_color(self, obj):
        return obj.color.name if obj.color else None
    
    def get_images(self, obj):
        return ProductColorImagesSerializer(
            models.ProductColorImagesModel.objects.filter(
                product=obj.product,
                color=obj.color
            ).first(),
            context={
                "request": self.context["request"]
            }
        ).data  


class ProductDetailSerializer(serializers.ModelSerializer):
    path = AloneProductPathSerializer()
    category = serializers.SerializerMethodField()
    
    class Meta:
        model = models.ProductModel
        fields = (
            "name", "description", "composition_and_care", "price", "old_price", "path", "category"
        )

    def get_category(self, obj):
        return CategorySerializer(
            obj.category,
            context={
                "request": self.context["request"]
            }
        ).data
        
        
class ShortModificationSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    old_price = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()

    class Meta:
        model = models.ProductModificationModel
        fields = (
            "id", "name", "image", "price", "old_price",
            "size", "color", "slug", "quantity"
        )
    
    def get_name(self, obj):
        return obj.product.name
    
    def get_image(self, obj):
        product_colors = models.ProductColorImagesModel.objects.filter(
            product=obj.product,
            color=obj.color
        )

        image = models.ColorImageModel.objects.filter(
            product_color__in=product_colors
        ).first()
        
        request = self.context.get('request')

        return image.image.url
    
    def get_quantity(self, obj):
        return obj.count

    def get_price(self, obj):
        return obj.product.price
    
    def get_old_price(self, obj):
        return obj.product.old_price
    
    def get_size(self, obj):
        return obj.size.name

    def get_color(self, obj):
        return obj.color.name
    
    def get_slug(self, obj):
        return obj.slug


class CartSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()

    class Meta:
        model = auth_models.CartModel
        fields = (
            "product", "quantity"
        )
    
    def get_product(self, obj):
        return ShortModificationSerializer(
            obj.product_modification_model,
            context={
                "request": self.context["request"]
            }
        ).data


class FavoritesSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()

    class Meta:
        model = models.ProductModificationModel
        fields = (
            "name", "image", "price", "slug"
        )

    def get_name(self, obj):
        return obj.product.name

    def get_price(self, obj):
        return obj.product.price
    
    def get_slug(self, obj):
        return obj.get_product_slug()
    
    def get_image(self, obj):
        product_colors = models.ProductColorImagesModel.objects.filter(
            product=obj.product,
            color=obj.color
        )

        image = models.ColorImageModel.objects.filter(
            product_color__in=product_colors
        ).first()
        
        request = self.context.get('request')

        return request.build_absolute_uri(image.image.url)


class UploadImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ColorImageModel
        fields = (
            "image", "product_color"
        )
