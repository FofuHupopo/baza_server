from rest_framework import status, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request, HttpRequest
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.conf import settings

from . import models
from api.request import Delivery
from api.authentication import models as auth_models
from . import serializers


class OrderView(APIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.ViewOrderSerializer
    
    def get(self, request: Request):
        serializer = self.serializer_class(
            models.OrderModel.objects.filter(
                user=request.user
            ).order_by("-id"),
            many=True,
            context={
                "request": request
            }
        )
        
        return Response(
            serializer.data,
            status.HTTP_200_OK
        )
    
    def post(self, request: Request):
        cart = auth_models.CartModel.objects.filter(
            user_model=request.user
        )
        
        if not cart:
            return Response(
                {"error": "no products in cart"},
                status.HTTP_400_BAD_REQUEST
            )

        serializer = serializers.CreateOrderSerializer(
            data=request.data
        )
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )

        order_instance: models.OrderModel = serializer.save(user=request.user)
        
        for item in cart:
            models.Order2ModificationModel.objects.create(
                order_model=order_instance,
                product_modification_model=item.product_modification_model,
                quantity=item.quantity
            )
        
        cart.delete()
        
        serializer = self.serializer_class(
            order_instance,
            context={
                "request": request
            }
        )
        
        return Response(
            serializer.data,
            status.HTTP_200_OK
        )


class CalculatePriceView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request: Request):
        delivery_address = request.query_params.get("delivery_address")
        delivery_stock = request.query_params.get("delivery_stock")
        delivery = bool(delivery_stock or delivery_address)

        cart = auth_models.CartModel.objects.filter(
            user_model=request.user
        )
        
        result = {
            "price": 0,
            "sale": 0
        }
        
        weight = 0
        
        for cart_instance in cart:
            quantity = cart_instance.quantity

            price = cart_instance.product_modification_model.product.price
            old_price = cart_instance.product_modification_model.product.old_price
            
            weight += cart_instance.product_modification_model.weight or 500
            
            if old_price > price:
                result["sale"] += quantity * (
                    old_price - price
                )
            
            result["price"] += quantity * price
        
        if delivery:
            delivery_price = 0

            if delivery_address:
                delivery_price = Delivery.calculate_address(delivery_address, weight)
            
            if delivery_stock:
                delivery_price = Delivery.calculate_stock(delivery_stock, weight)

            result["delivery"] = delivery_price
            result["price"] += delivery_price


        return Response(
            result,
            status.HTTP_200_OK
        )
