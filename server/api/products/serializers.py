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
        

class ProductModificationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductModificationImageModel
        fields = (
            "image",
        )


class ProductModificationSerializer(serializers.ModelSerializer):
    color = ProductColorSerializer()
    size = ProductSizeSerializer()
    images = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()

    class Meta:
        model = models.ProductModificationModel
        fields = (
            "id", "color", "size", "images", "quantity"
        )
    
    def get_images(self, obj):
        serializer = [
            self.context['request'].build_absolute_uri(image.image.url)
            for image in obj.images.all()
        ]
        
        return serializer
    
    def get_size(self, obj):
        return obj.size.name


class ListProductSerializer(serializers.ModelSerializer):
    path = AloneProductPathSerializer()
    colours = serializers.SerializerMethodField()

    class Meta:
        model = models.ProductModel
        fields = (
            "id", "name", "price", "image", "colours", "path"
        )
        
    def get_colours(self, obj):
        colours = models.ProductModificationModel.objects.filter(
            product=obj
        ).values_list(
            'color__name',
            flat=True
        ).distinct()
        
        return filter(lambda color: color, colours)


class ProductSerializer(serializers.ModelSerializer):
    modifications = serializers.SerializerMethodField()
    path = AloneProductPathSerializer()
    full_path = serializers.SerializerMethodField()
    slug_path = serializers.SerializerMethodField()

    class Meta:
        model = models.ProductModel
        fields = (
            "id", "name", "description", "price", "image",
            "category", "path", "modifications", "full_path", "slug_path"
        )
    
    def get_modifications(self, obj):
        modifications = models.ProductModificationModel.objects.filter(
            product=obj
        )
        serializer = ProductModificationSerializer(
            modifications,
            many=True,
            context={
                "request": self.context["request"]
            }
        )

        return serializer.data
    
    def get_full_path(self, obj):
        return obj.path.__str__()
    
    def get_slug_path(self, obj):
        return obj.path.get_slug_path()


class ListProductModificationSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    path = serializers.SerializerMethodField()
    full_path = serializers.SerializerMethodField()
    slug_path = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    
    class Meta:
        model = models.ProductModificationModel
        fields = (
            "id", "name", "description", "price", "images",
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
    
    def get_images(self, obj):
        serializer = ProductModificationImageSerializer(
            models.ProductModificationImageModel.objects.filter(
                product_modification=obj
            ),
            many=True
        )
    
        return serializer.data
