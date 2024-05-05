from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from django.db.models import Q
from functools import reduce
from operator import or_
from rest_framework.permissions import IsAuthenticated, AllowAny

from api.request import AddressSearch
from api.products import models as product_models
from api.products import serializers as product_serializers
from api.authentication import serializers as auth_serializers
from api.authentication import models as auth_models


class FavoritesView(APIView):
    permission_classes = (IsAuthenticated, )
    
    def get(self, request: Request):
        serializer = product_serializers.FavoritesSerializer(
            request.user.favorites.all(),
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
        modification = self._get_modification_from_request(request)

        request.user.favorites.add(
            *modification
        )

        return self.get(request)
    
    def delete(self, request: Request):
        modification = self._get_modification_from_request(request)
        
        request.user.favorites.remove(
            *modification
        )
        
        return self.get(request)
            
    def _get_modification_from_request(self, request: Request) -> list[product_models.ProductModificationModel]:
        slug = request.data.get("slug") or request.query_params.getlist("slug")

        if not slug:
            return Response(
                {
                    "message": "Не были переданы параметры modification_id или modifications[]."
                },
                status.HTTP_400_BAD_REQUEST
            )

        if type(slug) is str:
            modification = [product_models.ProductModificationModel.objects.filter(
                slug__icontains=slug
            ).first()]

        if type(slug) is list:
            q_object = reduce(or_, (Q(slug__icontains=slug_) for slug_ in slug))
            modification = product_models.ProductModificationModel.objects.filter(q_object).distinct("product_id", "color")

        if not modification:
            return Response(
                {
                    "message": "Модификации с данным slug не найдены."
                },
                status.HTTP_404_NOT_FOUND
            )

        return list(filter(lambda mod: mod, modification))


class CartView(APIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = product_serializers.CartSerializer
    
    def get(self, request: Request):    
        serializer = self.serializer_class(
            request.user.cart,
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
        cart = request.data
        
        for ind, product in enumerate(cart):
            slug = product.get("slug")
            
            try:    
                modification = product_models.ProductModificationModel.objects.get(
                    slug=slug
                )
            except product_models.ProductModificationModel.DoesNotExist:
                return Response({
                    "message": f"Modification with slug {slug} not found."
                }, status.HTTP_400_BAD_REQUEST)
            
            cart[ind]["modification_id"] = modification.pk
            cart[ind]["product_quantity"] = modification.count
    
        for product in cart:
            cart, _ = auth_models.CartModel.objects.get_or_create(
                user_model=request.user,
                product_modification_model_id=product["modification_id"],
            )

            cart.quantity += product["quantity"]
            cart.quantity = min(cart.quantity, product["product_quantity"])
            cart.save()

        return Response({
            "message": "Cart syncronized."
        }, status.HTTP_200_OK)

    def delete(self, request: Request):
        modification = CartView._get_modification_from_request(request)

        auth_models.CartModel.objects.filter(
            user_model=request.user,
            product_modification_model_id=modification
        ).first().delete()

        return self.get(request)
    
    @staticmethod
    def _get_modification_from_request(request: Request):
        modification_id = request.data.get("modification_id")
        slug = request.data.get("slug")
        
        if not modification_id and not slug:
            return Response(
                {
                    "message": "No modification_id or slug."
                },
                status.HTTP_400_BAD_REQUEST
            )
            
        if modification_id:
            modification = product_models.ProductModificationModel.objects.filter(
                pk=modification_id
            ).first()
        if slug:
            modification = product_models.ProductModificationModel.objects.filter(
                slug=slug
            ).first()

        if not modification:
            return Response(
                {
                    "message": "Модификация с данным slug не найдена."
                },
                status.HTTP_404_NOT_FOUND
            )

        return modification


class CartAddView(APIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = product_serializers.CartSerializer

    def post(self, request: Request):
        modification = CartView._get_modification_from_request(request)

        cart, _ = auth_models.CartModel.objects.get_or_create(
            user_model=request.user,
            product_modification_model=modification
        )
        
        if cart.quantity + 1 <= cart.product_modification_model.count:
            cart.quantity += 1
            cart.save()

        serializer = self.serializer_class(
            auth_models.CartModel.objects.filter(
                user_model=request.user
            ),
            many=True,
            context={
                "request": request
            }
        )

        return Response(
            serializer.data,
            status.HTTP_200_OK
        )
    
    
class CartRemoveView(APIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = product_serializers.CartSerializer

    def post(self, request: Request):
        modification = CartView._get_modification_from_request(request)

        cart = auth_models.CartModel.objects.filter(
            user_model=request.user,
            product_modification_model=modification
        ).first()

        if cart:
            if cart.quantity <= 1:
                cart.delete()
            else:
                cart.quantity -= 1
                cart.save()

        serializer = self.serializer_class(
            auth_models.CartModel.objects.filter(
                user_model=request.user
            ),
            many=True,
            context={
                "request": request
            }
        )
        
        return Response(
            serializer.data,
            status.HTTP_200_OK
        )


class InfoView(APIView):
    serializer_class = auth_serializers.UserDataSerialzier
    permission_classes = (IsAuthenticated, )
    
    def get(self, request: Request):
        serializer = self.serializer_class(
            request.user,
            context={
                "request": request
            }
        )
        
        return Response(
            serializer.data,
            status.HTTP_200_OK
        )
    
    def post(self, request: Request):
        serializer = auth_serializers.UpdateUserInfoSerializer(
            request.user,
            request.data
        )
        
        if serializer.is_valid():
            serializer.save()
            
            serializer = self.serializer_class(
                request.user
            )
            
            return Response(
                serializer.data,
                status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status.HTTP_400_BAD_REQUEST
        )


class CartMaximizationView(APIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = product_serializers.CartSerializer

    def get(self, request: Request):
        cart = auth_models.CartModel.objects.filter(
            user_model=request.user
        )
        
        for item in cart:
            item.quantity = min(item.product_modification_model.count, item.quantity)
            item.save()
        
        serializer = self.serializer_class(cart, many=True, context={"request": request})
        
        return Response(
            serializer.data,
            status.HTTP_200_OK
        )


class CartClearView(APIView):
    permission_classes = (IsAuthenticated, )
    
    def get(self, request: Request):
        request.user.cart.delete()
        
        return Response(
            {
                "message": "ok"
            },
            status.HTTP_200_OK
        )


class SearchAddressView(APIView):
    permission_classes = (AllowAny, )

    def get(self, request: Request):
        address = request.query_params.get("q", "")
        limit = request.query_params.get("limit", "5")
        
        if not limit.isdecimal():
            return Response({
                "message": "'limit' параметр должен быть числом."
            }, status.HTTP_400_BAD_REQUEST)
        
        limit = int(limit)
        
        response = AddressSearch.search(address, limit)
        
        return Response(
            response,
            status.HTTP_200_OK
        )
