from rest_framework import serializers

from . import models


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

    class Meta:
        model = models.ProductModificationModel
        fields = (
            "id", "color", "size", "quantity"
        )

    def get_size(self, obj):
        return obj.size.name if obj.size else None
    
    
class ShortProductModificationSerializer(serializers.ModelSerializer):
    color = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    
    class Meta:
        model = models.ProductModificationModel
        fields = (
            "id", "color", "size", "images"
        )
        
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
            "id", "name", "description", "price", "image", "color_images",
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
    price = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    path = serializers.SerializerMethodField()
    full_path = serializers.SerializerMethodField()
    slug_path = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    
    class Meta:
        model = models.ProductModificationModel
        fields = (
            "id", "name", "description", "price"
            "category", "path", "full_path", "slug_path", "size", "color"
        )
        depth = 2

    def get_name(self, obj):
        return obj.product.name
    
    def get_description(self, obj):
        return obj.product.description
    
    def get_price(self, obj):
        return obj.product.price
    
    def get_category(self, obj):
        return obj.product.category.category
    
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
