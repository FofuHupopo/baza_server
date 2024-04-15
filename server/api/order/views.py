from rest_framework import status, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request, HttpRequest
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.conf import settings
from django.http.response import HttpResponseRedirect
from django.db import IntegrityError

from . import models
from .services import MerchantAPI
from api.request import Delivery
from api.authentication import models as auth_models
from . import serializers


merchant_api = MerchantAPI(
    terminal_key="1693394744755DEMO",
    secret_key="cvr9aqrb3mq60a74"
)


class OrderView(APIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.ViewOrderSerializer

    def get(self, request: Request):
        payment_type = request.query_params.get("payment_type", None)
        is_paid = request.query_params.get("is_paid", None)
        is_received = request.query_params.get("is_received", None)

        orders = models.OrderModel.objects.filter(
            user=request.user
        ).order_by("-id")

        for order in orders:
            order.save()

        if payment_type:
            orders = orders.filter(
                payment_type=payment_type
            )

        if is_paid:
            is_paid = True if is_paid.lower() == "true" else False

            orders = orders.filter(
                is_paid=is_paid
            )

        if is_received:
            is_received = True if is_received.lower() == "true" else False

            orders = orders.filter(
                is_received=is_received
            )

        serializer = self.serializer_class(
            orders.order_by("-id"),
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
                {"error": "Корзина пуста."},
                status.HTTP_400_BAD_REQUEST
            )

        for item in cart:
            if item.quantity > item.product_modification_model.count:
                return Response(
                    {
                        "status": "Количество товара в корзине превышает количество товара на складе."
                    },
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
                order_model_id=order_instance.pk,
                product_modification_model_id=item.product_modification_model.pk,
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
                ) / 100

            result["price"] += quantity * price / 100

        if delivery:
            delivery_price = 0

            if delivery_address:
                delivery_price = Delivery.calculate_address(
                    delivery_address, weight)

            if delivery_stock:
                delivery_price = Delivery.calculate_stock(
                    delivery_stock, weight)

            result["delivery"] = delivery_price

        return Response(
            result,
            status.HTTP_200_OK
        )


class PaymentView(APIView):
    serializer_class = serializers.PaymentSerializer

    def get(self, request: Request):
        order_id = request.query_params.get("order_id")

        try:
            order = models.OrderModel.objects.get(
                pk=order_id
            )
        except models.OrderModel.DoesNotExist:
            return Response(
                {
                    "status": "Не был передан параметр order_id."
                },
                status.HTTP_400_BAD_REQUEST
            )

        try:
            payment = models.Payment.get(
                order_id=order_id
            )
        except models.Payment.DoesNotExist:
            payment_description = ""

            order_to_modifications = models.Order2ModificationModel.objects.filter(
                order_model_id=order_id
            )

            for order_to_modification in order_to_modifications:
                payment_description += f"{order_to_modification.product_modification_model.product.name} ({order_to_modification.product_modification_model.color.name}, {order_to_modification.product_modification_model.size.name}), количество: {order_to_modification.quantity};"

            payment = models.Payment.create(
                amount=order.amount,
                order_id=order.pk,
                description=payment_description
            )

            merchant_api.init(payment)

            payment.save()

        serializer = self.serializer_class(
            payment
        )

        return Response(
            serializer.data,
            status.HTTP_200_OK
        )


class PaymentStatusView(APIView):
    serializer_class = serializers.PaymentSerializer

    def get(self, request: Request):
        payment_id = request.query_params.get("payment_id")

        try:
            payment = models.Payment.objects.get(
                pk=payment_id
            )
        except models.OrderModel.DoesNotExist:
            return Response(
                {
                    "status": "Не был передан параметр payment_id."
                },
                status.HTTP_400_BAD_REQUEST
            )

        merchant_api.status(payment)
        payment.save()
        
        if payment.error_code != 0:
            payment.set_payment_fail()
            
        if payment.is_paid():
            order = models.OrderModel.objects.get(
                pk=payment.order_id
            )
            
            order.is_paid = payment.is_paid()

            order.save()

        serializer = self.serializer_class(payment)

        return Response(
            serializer.data,
            status.HTTP_200_OK
        )


class PaymentResponseSuccessView(APIView):
    serializer_class = serializers.PaymentSerializer

    def get(self, request: Request):
        print("=" * 20)
        print("PAYMENT SUCCESS (GET):")
        print("BODY:", request.data)
        print("QUERY:", request.query_params)
        print("=" * 20)

        return HttpResponseRedirect("https://thebaza.ru")
        
    def post(self, request: Request):
        print("=" * 20)
        print("PAYMENT SUCCESS (POST):")
        print("BODY:", request.data)
        print("QUERY:", request.query_params)
        print("=" * 20)

        return HttpResponseRedirect("https://thebaza.ru")


class PaymentResponseFailView(APIView):
    serializer_class = serializers.PaymentSerializer

    def get(self, request: Request):
        print("=" * 20)
        print("PAYMENT FAIL (GET):")
        print("BODY:", request.data)
        print("QUERY:", request.query_params)
        print("=" * 20)

        return HttpResponseRedirect("https://thebaza.ru")
        
    def post(self, request: Request):
        print("=" * 20)
        print("PAYMENT FAIL (POST):")
        print("BODY:", request.data)
        print("QUERY:", request.query_params)
        print("=" * 20)

        return HttpResponseRedirect("https://thebaza.ru")
