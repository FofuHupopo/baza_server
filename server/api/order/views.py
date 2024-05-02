from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.http.response import HttpResponseRedirect
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse, OpenApiExample

from . import models
from api.permissions import TinkoffPermission
from .services import MerchantAPI
from api.request import Delivery
from api.products import models as product_models
from api.authentication import models as auth_models
from . import serializers
from . import docs


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

        amount = 0

        for item in cart:
            models.Order2ModificationModel.objects.create(
                order_model_id=order_instance.pk,
                product_modification_model_id=item.product_modification_model.pk,
                quantity=item.quantity
            )
            
            amount += item.product_modification_model.product.price * item.quantity
        
        order_instance.amount = amount
        
        order_instance.save()

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


@extend_schema_view(
    post=extend_schema(
        summary="Предподсчет корзины",
        description="ДОКУМЕНТАЦИЯ БЛЯТЬ",
        responses={
            status.HTTP_200_OK: serializers.PreCalculateSerializer(many=True)
        },
        request=docs.PostPreCalculateSerialzier()
    )
)
class PreCalculatePriceView(APIView):
    serialzier_class = serializers.PreCalculateSerializer
    permission_classes = [AllowAny]

    def post(self, request: Request):
        products: list[dict] = request.data.get("products")
        
        response_objects = []
        for product in products:
            modification_slug = product.get("slug", "")
            quantity = product.get("quantity", 0)

            try:
                modification_instance = product_models.ProductModificationModel.objects.get(
                    slug=modification_slug
                )
            except product_models.ProductModificationModel.DoesNotExist:
                return Response({
                        "message": f"Товар со слагом {modification_slug} не найден"
                }, status.HTTP_400_BAD_REQUEST)
                
            response_object = {
                "name": modification_instance.product.name,
                "size": modification_instance.size.name,
                "color": modification_instance.color.name,
                "price": modification_instance.product.price,
            }
            
            response_objects.append(response_object)
                
            if modification_instance.quantity <= 0:
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
                response_object.update({
                    "quantity": modification_instance.quantity,
                    "message": f"Недостаточно товара на складе. (В наличии {modification_instance.quantity})",
                    "status": "bad"
                })
                continue
            
        serializer = serializers.PreCalculateSerializer(
            data=response_objects, many=True
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
            
            return HttpResponseRedirect("https://thebaza.ru") # Not payment
        
        order = models.OrderModel.objects.get(
            pk=payment.order_id
        )
        
        order.is_paid = True
        order.status = models.OrderModel.OrderStatusChoice.PAID

        order.save()

        return HttpResponseRedirect("https://thebaza.ru") # payment


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
        
        return HttpResponseRedirect("https://thebaza.ru") # Not payment
