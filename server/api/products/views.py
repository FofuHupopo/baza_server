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
        visible=True
    )
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
        visible=True
    )
    serializer_class = serializers.ProductSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request

        return context
