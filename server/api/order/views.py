from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.http.response import HttpResponseRedirect
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes

from . import models
from api.permissions import TinkoffPermission
from .services import MerchantAPI
from api.request import Delivery
from api.profile import models as profile_models
from api.authentication import models as auth_models
from api.request import BotServer
from . import serializers
from . import docs


merchant_api = MerchantAPI(
    terminal_key="1693394744755DEMO",
    secret_key="cvr9aqrb3mq60a74"
)

@extend_schema_view(
    get=extend_schema(
        summary="Просмотр всех заказов",
        responses={
            status.HTTP_200_OK: serializers.ViewOrderSerializer(many=True)
        }
    ),
    post=extend_schema(
        summary="Создание заказа",
        responses={
            status.HTTP_201_CREATED: serializers.ViewOrderSerializer()
        },
        request=serializers.CreateOrderSerializer
    )
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

        for cart_instance in cart:
            cart_instance.quantity = min(cart_instance.product_modification_model.quantity, cart_instance.quantity)
            cart_instance.save()

        serializer = serializers.CreateOrderSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )

        order_instance: models.OrderModel = serializer.save(user=request.user)
        
        if order_instance.receiving != "pickup":
            address, created = profile_models.AddressModel.objects.get_or_create(
                user=request.user,
                type=order_instance.receiving,
                address=order_instance.address,
                code=order_instance.code,
                apartment_number=order_instance.apartment_number,
                floor_number=order_instance.floor_number,
                intercom=order_instance.intercom
            )
            
            address.is_main = True
            address.save()

        amount = 0

        for item in cart:
            models.Order2ModificationModel.objects.create(
                order_model_id=order_instance.pk,
                product_modification_model_id=item.product_modification_model.pk,
                quantity=item.quantity
            )
            
            amount += item.product_modification_model.product.price * item.quantity
            
        cart.delete()
        
        for item in cart:
            item.product_modification_model.reserved += item.quantity
            item.product_modification_model.save()

        order_instance.amount = amount
        
        if order_instance.use_loyalty:
            loyalty_instance = profile_models.LoyaltyModel.get_by_user_id(order_instance.user.pk)
            order_instance.use_loyalty_balance = min(int(amount * 0.15), loyalty_instance.balance)
            order_instance.amount -= order_instance.use_loyalty_balance
        
        if order_instance.receiving == "personal" and order_instance.is_express:
            order_instance.amount += 150000

        if order_instance.receiving == "personal" and not order_instance.is_express:
            order_instance.amount += 120000

        if order_instance.receiving == "cdek":
            order_instance.amount += 60000

        order_instance.save()

        serializer = self.serializer_class(
            order_instance
        )

        return Response(
            serializer.data,
            status.HTTP_200_OK
        )


class CancelOrderView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request: Request):
        order_id = request.query_params.get("order_id")

        try:
            order = models.OrderModel.objects.get(
                pk=order_id
            )
        except models.OrderModel.DoesNotExist:
            return Response(
                {"error": "Заказ не найден."},
                status.HTTP_400_BAD_REQUEST
            )

        order.set_order_cancel()
        
        for order2modification in models.Order2ModificationModel.objects.filter(
            order_model_id=order_id
        ):
            order2modification.product_modification_model.reserved -= order2modification.quantity
            order2modification.product_modification_model.save()

        return Response(
            {"status": "Заказ отменен."},
            status.HTTP_200_OK
        )


class OldCalculatePriceView(APIView):
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


@extend_schema_view(
    get=extend_schema(
        summary="Предподсчет корзины",
        responses={
            status.HTTP_200_OK: serializers.CalculateSerializer
        }
    )
)
class CalculateView(APIView):
    serialzier_class = serializers.CalculateSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        products_object = []
        cart = auth_models.CartModel.objects.filter(
            user_model=request.user
        )
        for cart_instance in cart:
            modification_instance = cart_instance.product_modification_model
            quantity = cart_instance.quantity
                
            response_object = {
                "name": modification_instance.product.name,
                "size": modification_instance.size.name,
                "color": modification_instance.color.name,
                "price": modification_instance.product.price,
                "image": modification_instance.get_image_url(),
            }

            products_object.append(response_object)
                
            if modification_instance.quantity <= 0:
                cart_instance.quantity = 0
                cart_instance.save()

                response_object.update({
                    "quantity": 0,
                    "message": "Товара нет в наличии.",
                    "status": "bad"
                })
                continue

            if quantity <= modification_instance.quantity:
                response_object.update({
                    "quantity": quantity,
                    "message": "",
                    "status": "ok"
                })                
                continue
            
            if modification_instance.quantity < quantity:
                cart_instance.quantity = modification_instance.quantity
                cart_instance.save()

                response_object.update({
                    "quantity": modification_instance.quantity,
                    "message": f"Недостаточно товара на складе. (В наличии {modification_instance.quantity})",
                    "status": "bad"
                })
                continue


        price = 0
        for product in products_object:
            price += product["price"] * product["quantity"]


        loyalty_instance = profile_models.LoyaltyModel.get_by_user_id(request.user.pk)
        available_loyalty = min(int(price * 0.15), loyalty_instance.balance)

        calculate_object = {
            "products": products_object,
            "price": price,
            "available_loyalty": available_loyalty,
        }

        serializer = serializers.CalculateSerializer(
            data=calculate_object
        )
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )
            
        return Response(
            serializer.data,
            status.HTTP_200_OK
        )   


@extend_schema_view(
    get=extend_schema(
        summary="Предподсчет корзины",
        responses={
            status.HTTP_200_OK: serializers.PaymentSerializer
        },
        parameters=[
            OpenApiParameter("order_id", OpenApiTypes.STR),
        ]
    )
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
        
        if payment.message != "OK":
            payment.set_payment_fail()
            
        if payment.is_paid():
            order = models.OrderModel.objects.get(
                pk=payment.order_id
            )
            
            order.is_paid = payment.is_paid()
            order.status = models.OrderModel.OrderStatusChoice.PAID

            order.save()

        serializer = self.serializer_class(payment)

        return Response(
            serializer.data,
            status.HTTP_200_OK
        )


class PaymentResponseSuccessView(APIView):
    serializer_class = serializers.PaymentSerializer
    permission_classes = [TinkoffPermission]

    def get(self, request: Request, payment_id: int):
        payment = models.Payment.objects.get(
            pk=payment_id
        )
        
        merchant_api.status(payment)
        payment.save()
        
        if not payment.is_paid():
            payment.payment_fail = True
            payment.save()
            
            return HttpResponseRedirect("https://thebaza.ru/order/failed") # Not payment
        
        order = models.OrderModel.objects.get(
            pk=payment.order_id
        )
        
        order.is_paid = True
        order.status = models.OrderModel.OrderStatusChoice.PAID

        order.save()
        
        products = models.Order2ModificationModel.objects.filter(
            order_model_id=order.pk
        )
        
        BotServer.new_order({
            "order_id": order.pk,
            "receiving": order.receiving,
            "address": order.address,
            "code": order.code,
            "is_express": order.is_express,
            "floor_number": order.floor_number,
            "apartment_number": order.apartment_number,
            "intercom": order.intercom,
            "products": [
                {
                    "name": product.product_modification_model.product.name,
                    "color": product.product_modification_model.color.name,
                    "size": product.product_modification_model.size.name,
                    "quantity": product.quantity
                }
                for product in products
            ]
        })

        return HttpResponseRedirect("https://thebaza.ru/order/successful") # payment


class PaymentResponseFailView(APIView):
    serializer_class = serializers.PaymentSerializer
    permission_classes = [TinkoffPermission]

    def get(self, request: Request, payment_id: int):
        payment = models.Payment.objects.get(
            id=payment_id
        )
        
        merchant_api.status(payment)
        payment.save()
        
        if not payment.is_paid():
            payment.payment_fail = True

        payment.save()
        
        order = models.OrderModel.objects.get(
            pk=payment.order_id
        )
        order.status = models.OrderModel.OrderStatusChoice.FAILED_PAYMENT
        order.save()

        return HttpResponseRedirect("https://thebaza.ru/order/failed") # Not payment
