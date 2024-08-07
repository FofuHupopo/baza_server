import os
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.http.response import HttpResponseRedirect
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
from django.conf import settings

from . import models
from api.permissions import TinkoffPermission
from .services import MerchantAPI, DolyameAPI
from api.request import Delivery
from api.profile import models as profile_models
from api.authentication import models as auth_models
from api.request import BotServer

from .utils import send_bot_order
from . import serializers
from . import docs


merchant_api = MerchantAPI(
    terminal_key=os.getenv("TERMINAL_KEY"),
    secret_key=os.getenv("SECRET_KEY"),
)

dolyame_api = DolyameAPI(
    login=os.getenv("DOLYAME_LOGIN"),
    password=os.getenv("DOLYAME_PASSWORD"),
    cert_path=os.getenv("DOLYAME_CERT_PATH"),
    key_path=os.getenv("DOLYAME_KEY_PATH"),
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
            cart_instance.quantity = min(cart_instance.product_modification_model.count, cart_instance.quantity)
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
            try:
                address = profile_models.AddressModel.objects.get(
                    user=request.user,
                    type=order_instance.receiving,
                    address=order_instance.address,
                    code=order_instance.code,
                    apartment_number=order_instance.apartment_number,
                    floor_number=order_instance.floor_number,
                    intercom=order_instance.intercom
                )
            except profile_models.AddressModel.DoesNotExist:
                address = profile_models.AddressModel.objects.create(
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
        
        for item in cart:
            item.product_modification_model.reserved += item.quantity
            item.product_modification_model.save()

        cart.delete()

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
                # cart_instance.quantity = 0
                # cart_instance.save()

                response_object.update({
                    "quantity": 0,
                    "message": "Товара нет в наличии.",
                    "status": "bad"
                })
                continue

            if quantity <= modification_instance.count:
                response_object.update({
                    "quantity": quantity,
                    "message": "",
                    "status": "ok"
                })                
                continue
            
            if modification_instance.count < quantity:
                # cart_instance.quantity = modification_instance.count
                # cart_instance.save()

                response_object.update({
                    "quantity": modification_instance.count,
                    "message": f"Недостаточно товара на складе. (В наличии {modification_instance.count})",
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
    permission_classes = [IsAuthenticated]

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
                payment_description += f"{order_to_modification.product_modification_model.product.name} " \
                    f"({order_to_modification.product_modification_model.color.name}, {order_to_modification.product_modification_model.size.name}), " \
                    f"количество: {order_to_modification.quantity};"

            payment = models.Payment.create(
                amount=order.amount,
                order_id=order.pk,
                description=payment_description
            )

            receipt = payment.with_receipt(
                email=request.user.email or order.email,
                phone=request.user.phone or order.phone
            )

            receipt_items = [
                {
                    "product": product.product_modification_model,
                    "price": product.product_modification_model.product.price,
                    "quantity": product.quantity,
                    "amount": product.product_modification_model.product.price * product.quantity
                }
                for product in order_to_modifications
            ]

            if order.receiving == "personal" and order.is_express:
                receipt_items.append({
                    "product": None,
                    "name": "Экспресс доствка",
                    "price": 150000,
                    "quantity": 1,
                    "amount": 150000
                })

            if order.receiving == "personal" and not order.is_express:
                receipt_items.append({
                    "product": None,
                    "name": "Обычная доствка",
                    "price": 120000,
                    "quantity": 1,
                    "amount": 120000
                })

            if order.receiving == "cdek":
                receipt_items.append({
                    "product": None,
                    "name": "Доствка CDEK",
                    "price": 60000,
                    "quantity": 1,
                    "amount": 60000
                })
            
            items = payment.with_items(receipt_items)

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
    permission_classes = [IsAuthenticated]

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
        
        
class DolyameView(APIView):
    serializer_class = serializers.DolyameSerializer
    permission_classes = [IsAuthenticated]

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
            dolyame = models.DolyameModel.get(
                order_id=order_id
            )
        except models.DolyameModel.DoesNotExist:
            dolyame = models.DolyameModel.create(
                amount=order.amount,
                order_id=order.pk,
            )

            dolyame_api.create(dolyame)

            dolyame.save()

        serializer = self.serializer_class(
            dolyame
        )

        return Response(
            serializer.data,
            status.HTTP_200_OK
        )


class DolyameInfoView(APIView):
    serializer_class = serializers.DolyameSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        dolyame_id = request.query_params.get("dolyame_id")

        try:
            dolyame = models.DolyameModel.objects.get(
                pk=dolyame_id
            )
        except models.DolyameModel.DoesNotExist:
            return Response(
                {"status": "Не был передан query параметр dolyame_id."},
                status.HTTP_400_BAD_REQUEST
            )

        dolyame_api.info(dolyame)
        dolyame.save()
            
        if dolyame.is_paid():
            order = models.OrderModel.objects.get(
                pk=dolyame.order.id
            )

            order.is_paid = dolyame.is_paid()
            order.status = models.OrderModel.OrderStatusChoice.PAID

            order.save()
        else:
            dolyame.payment_fail = True
            dolyame.save()

        serializer = self.serializer_class(dolyame)

        return Response(
            serializer.data,
            status.HTTP_200_OK
        )


class PaymentResponseSuccessView(APIView):
    serializer_class = serializers.PaymentSerializer
    permission_classes = [AllowAny]

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

        send_bot_order(order, products)

        return HttpResponseRedirect("https://thebaza.ru/order/successful")


class PaymentResponseFailView(APIView):
    serializer_class = serializers.PaymentSerializer
    permission_classes = [AllowAny]

    def get(self, request: Request, payment_id: int):
        payment = models.Payment.objects.get(
            id=payment_id
        )
        
        payment = merchant_api.status(payment)
        payment.save()

        if not payment.is_paid():
            payment.payment_fail = True
            payment.save()

        order = models.OrderModel.objects.get(
            pk=payment.order_id
        )
        order.status = models.OrderModel.OrderStatusChoice.FAILED_PAYMENT
        order.save()

        return HttpResponseRedirect("https://thebaza.ru/order/failed")


class DolyameResponseSuccessView(APIView):
    serializer_class = serializers.DolyameSerializer
    permission_classes = [AllowAny]

    def get(self, request: Request, dolyame_id: str):
        dolyame = models.DolyameModel.objects.get(
            pk=dolyame_id
        )

        dolyame_api.info(dolyame)
        dolyame.save()
        
        if not dolyame.is_paid():
            dolyame.payment_fail = True
            dolyame.save()
            
            return HttpResponseRedirect("https://thebaza.ru/order/failed") # Not payment
        
        order = models.OrderModel.objects.get(
            pk=dolyame.order.id
        )

        order.is_paid = True
        order.status = models.OrderModel.OrderStatusChoice.PAID

        order.save()

        products = models.Order2ModificationModel.objects.filter(
            order_model_id=order.pk
        )

        send_bot_order(order, products)

        return HttpResponseRedirect("https://thebaza.ru/order/successful")


class DolyameResponseFailView(APIView):
    serializer_class = serializers.DolyameSerializer
    permission_classes = [AllowAny]

    def get(self, request: Request, dolyame_id: str):
        dolyame = models.DolyameModel.objects.get(
            id=dolyame_id
        )
        
        dolyame_api.info(dolyame)
        dolyame.save()

        if not dolyame.is_paid():
            dolyame.payment_fail = True
            dolyame.save()

        order = models.OrderModel.objects.get(
            pk=dolyame.order.id
        )
        order.status = models.OrderModel.OrderStatusChoice.FAILED_PAYMENT
        order.save()

        return HttpResponseRedirect("https://thebaza.ru/order/failed")


class DolyameNotificationView(APIView):
    
    def get(self, request: Request, dolyame_id: str):
        print("DOLYAME NOTIFICATION:", request.data, dolyame_id)
        
        dolyame = models.DolyameModel.objects.get(
            id=dolyame_id
        )
        
        dolyame_status = request.data.get("status")
        
        if dolyame_status == "approved":
            dolyame_api.commit(dolyame)
            dolyame.save()

        if dolyame_status == "rejected":
            dolyame.payment_fail = True
            dolyame.save()

        return Response({
            "message": "ok"
        }, status.HTTP_200_OK)
