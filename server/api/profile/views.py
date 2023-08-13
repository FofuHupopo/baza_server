from rest_framework import status, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request, HttpRequest
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.conf import settings

from api.products import models as product_models
from api.products import serializers as product_serializers


class FavoritesView(APIView):
    permission_classes = (IsAuthenticated, )
    
    def get(self, request: Request):
        serializer = product_serializers.ListProductSerializer(
            request.user.favorites.all(),
            many=True
        )
        
        return Response(
            serializer.data,
            status.HTTP_200_OK
        )

    def post(self, request: Request):
        product = self._get_product_from_request(request)
        
        request.user.favorites.add(
            product
        )
        
        return Response(
            {
                "message": "ok"
            },
            status.HTTP_200_OK
        )
    
    def delete(self, request: Request):
        product = self._get_product_from_request(request)
        
        request.user.favorites.remove(
            product
        )
        
        return Response(
            {
                "message": "ok"
            },
            status.HTTP_200_OK
        )
            
    def _get_product_from_request(self, request: Request):
        product_id = request.data.get("product_id")
        
        if not product_id:
            return Response(
                {
                    "message": "No product id."
                },
                status.HTTP_400_BAD_REQUEST
            )
        
        product = product_models.ProductModel.objects.filter(
            pk=product_id
        ).first()
        
        if not product:
            return Response(
                {
                    "message": "No product with this id."
                },
                status.HTTP_400_BAD_REQUEST
            )
        
        return product


class BasketView(APIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = product_serializers.ListProductModificationSerializer
    
    def get(self, request: Request):
        serializer = self.serializer_class(
            request.user.basket.all(),
            many=True
        )

        return Response(
            serializer.data,
            status.HTTP_200_OK
        )

    def post(self, request: Request):
        product_modification = self._get_product_modification_from_request(request)
        
        request.user.basket.add(
            product_modification
        )
        
        return Response(
            {
                "message": "ok"
            },
            status.HTTP_200_OK
        )
    
    def delete(self, request: Request):
        product_modification = self._get_product_modification_from_request(request)
        
        request.user.basket.remove(
            product_modification
        )
        
        return Response(
            {
                "message": "ok"
            },
            status.HTTP_200_OK
        )
            
    def _get_product_modification_from_request(self, request: Request):
        product_modification_id = request.data.get("product_modification_id")
        
        if not product_modification_id:
            return Response(
                {
                    "message": "No product_modification id."
                },
                status.HTTP_400_BAD_REQUEST
            )
        
        product_modification = product_models.ProductModificationModel.objects.filter(
            pk=product_modification_id
        ).first()
        
        if not product_modification:
            return Response(
                {
                    "message": "No product_modification with this id."
                },
                status.HTTP_400_BAD_REQUEST
            )
        
        return product_modification


class EditInfoView(APIView):
    serializer_class = ...
    