from rest_framework import status, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import authentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from django.conf import settings
from rest_framework import parsers
import json

from api.permissions import IsSuperUser
from . import models
from . import serializers


class ProductPathView(CacheResponseMixin, generics.ListAPIView):
    permission_classes = (AllowAny, )
    queryset = models.ProductPathModel.objects.filter(parent=None)
    serializer_class = serializers.ProductPathSerializer


class ProductFakePathView(APIView):
    permission_classes = (AllowAny, )
    
    def get(self, request: Request):
        path = settings.BASE_DIR / "api/static/json/fake_path.json"
        
        return Response(
            json.load(open(path, "r", encoding="utf-8"))
        )


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


class ListProductsView(CacheResponseMixin, generics.ListAPIView):
    permission_classes = (AllowAny, )
    queryset = models.ProductModificationModel.objects.filter(
        product__visible=True,
        visible=True
    ).distinct("color", "product").order_by("product__id")
    serializer_class = serializers.ListProductsSerializer
    # pagination_class = ListProductPagination

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


class FilterProductModificationView(APIView):
    serializer_class = serializers.FilterProductModificationSerializer
    permission_classes = (AllowAny, )
    
    def get(self, request: Request):
        slug = request.query_params.get("slug")
        
        path = models.ProductPathModel.objects.filter(
            slug=slug
        ).first()

        child_path = models.ProductPathModel.objects.filter(
            slug__startswith=slug
        )
        
        if child_path is None:
            return Response({
                "products": [],
                "breadcrumbs": []
            }, status.HTTP_200_OK)
        
        products = models.ProductModificationModel.objects.filter(
            product__visible=True,
            visible=True,
            product__path__in=child_path
        ).distinct("color", "product").order_by("product__id")

        serializer = self.serializer_class(data={
            "products": products,
            "breadcrumbs": path
        }, context={
            "request": request
        })
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )
            
        return Response(
            serializer.data,
            status.HTTP_200_OK
        )


class ProductDetailView(APIView):
    permission_classes = (AllowAny, )

    def get(self, request: Request, slug):
        # slug = "-".join(slug.split("-")[:-1])

        modifications = models.ProductModificationModel.objects.filter(
            slug__icontains=slug,
            visible=True
        )
        
        if not modifications:
            return Response(
                {
                    "message": "Некорректный slug."
                },
                status.HTTP_404_NOT_FOUND
            )
        
        product = modifications[0].product
        
        sizes = modifications.values_list("id", "size__name", "quantity", "reserved", "slug")

        colors = models.ProductModificationModel.objects.filter(
            product=product,
            visible=True
        ).distinct("color").values_list("slug", "color__name", "color__eng_name", "color__hex_code")

        current_color = modifications[0].color

        product_color = models.ProductColorImagesModel.objects.filter(
            color=current_color,
            product=product
        ).first()
        
        images = models.ColorImageModel.objects.filter(
            product_color=product_color
        )
        
        serializer = serializers.ProductDetailSerializer(product, context={"request": request})
        
        serializer = {
            **serializer.data
        }

        if product_color.additional_description:
            serializer["description"] += f"\n\n{product_color.additional_description}"

        return Response(
            {
                **serializer,
                "images": [
                    image.image.url
                    for image in images    
                ],
                "sizes": [
                    {
                        "name": size_name,
                        "mod_id": mod_id,
                        "quantity": quantity - reserved,
                        "slug": slug
                    }
                    for mod_id, size_name, quantity, reserved, slug in sizes
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
                        "eng_name": color_eng_name,
                        "hex_code": color_hex
                    }
                    for slug, color_name, color_eng_name, color_hex in colors
                ],
                "breadcrumbs": serializers.get_breadcrumbs(product.path)
            },
            status.HTTP_200_OK
        )


class UploadImageViews(APIView):
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    permission_classes = [IsAuthenticated, IsSuperUser]
    authentication_classes = [
        authentication.SessionAuthentication
    ]

    def post(self, request: Request):
        serializer = serializers.UploadImagesSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response(serializer.data, status.HTTP_201_CREATED)
