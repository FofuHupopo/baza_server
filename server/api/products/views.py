from rest_framework import status, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request, HttpRequest
from rest_framework.permissions import AllowAny
from django.conf import settings

from . import models
from . import serializers


class ProductPathView(generics.ListAPIView):
    permission_classes = (AllowAny, )
    queryset = models.ProductPathModel.objects.filter(parent=None)
    serializer_class = serializers.ProductPathSerializer
    

class ListProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ListProductView(generics.ListAPIView):
    permission_classes = (AllowAny, )
    queryset = models.ProductModel.objects.filter(
        visible=True,
        productmodificationmodel__isnull=False
    ).distinct().order_by("id")
    serializer_class = serializers.ListProductSerializer
    pagination_class = ListProductPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        query_params = self.request.query_params

        if (slug := query_params.get("slug")):
            path = models.ProductPathModel.objects.filter(
                slug=slug
            ).first()

            return queryset.filter(
                path=path
            )

        if (path_id := query_params.get("path_id")):
            path = models.ProductPathModel.objects.filter(
                pk=path_id
            ).first()

            return queryset.filter(
                path=path
            )

        return queryset


class ProductView(generics.RetrieveAPIView):
    permission_classes = (AllowAny, )
    queryset = models.ProductModel.objects.filter(
        visible=True,
        productmodificationmodel__isnull=False
    ).distinct().order_by("id")
    serializer_class = serializers.ProductSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request

        return context


class ListProductsView(generics.ListAPIView):
    permission_classes = (AllowAny, )
    queryset = models.ProductModificationModel.objects.filter(
        product__visible=True,
    ).distinct("color", "product").order_by("product__id")
    serializer_class = serializers.ListProductsSerializer
    pagination_class = ListProductPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        query_params = self.request.query_params

        if (slug := query_params.get("slug")):
            path = models.ProductPathModel.objects.filter(
                slug=slug
            ).first()

            return queryset.filter(
                product__path=path
            )

        if (path_id := query_params.get("path_id")):
            path = models.ProductPathModel.objects.filter(
                pk=path_id
            ).first()

            return queryset.filter(
                product__path=path
            )

        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request

        return context


class ProductDetailView(APIView):
    permission_classes = (AllowAny, )

    def get(self, request: Request, slug):
        modifications = models.ProductModificationModel.objects.filter(
            slug__icontains=slug
        )
        
        if not modifications:
            return Response(
                {
                    "error": "Incorrect slug"
                },
                status.HTTP_400_BAD_REQUEST
            )
        
        product = modifications[0].product
        
        sizes = modifications.values_list("size__name", "id")

        colors = models.ProductModificationModel.objects.filter(
            product=product
        ).distinct("color").values_list("slug", "color__name", "color__hex_code")
        
        current_color = modifications[0].color
        images = models.ColorImageModel.objects.filter(
            product_color=models.ProductColorImagesModel.objects.filter(
                color=current_color,
                product=product
            ).first()
        )
        
        serializer = serializers.ProductDetailSerializer(product, context={"request": request})
        
        return Response(
            {
                **serializer.data,
                "images": [
                    request.build_absolute_uri(image.image.url)
                    for image in images    
                ],
                "sizes": [
                    {
                        "name": size_name,
                        "mod_id": mod_id
                    }
                    for size_name, mod_id in sizes
                ],
                "current_color": {
                    "slug": slug,
                    "name": current_color.name,
                    "eng_name": current_color.eng_name,
                    "hex_code": current_color.hex_code,
                },
                "colors": [
                    {
                        "slug": "-".join(slug.split("-")[:-1]),
                        "name": color_name,
                        "eng_name": current_color.eng_name,
                        "hex_code": color_hex
                    }
                    for slug, color_name, color_hex in colors
                ]
            },
            status.HTTP_200_OK
        )
