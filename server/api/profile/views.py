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
                    "message": "No modification_id or modifications[]."
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
                    "message": "No modification with this slug."
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
        modifications = request.data.get("modifications")
        quantities = request.data.get("quantities", [])
        
        quantities += [1 for _ in range(len(modifications) - len(quantities))]

        if len(modifications) != len(quantities):
            return Response(
                {
                    "message": "Слыш черт, нормальные списки отправь. length of modification not equal the length of quantities"
                }
            )
        
        for modification, quantity in zip(modifications, quantities):
            cart, _ = auth_models.CartModel.objects.get_or_create(
                user_model=request.user,
                product_modification_model_id=modification
            )

            cart.quantity = quantity
            cart.save()

        return self.get(request)

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
        
        if not modification_id:
            return Response(
                {
                    "message": "No modification_id."
                },
                status.HTTP_400_BAD_REQUEST
            )
        
        modification = product_models.ProductModificationModel.objects.filter(
            pk=modification_id
        ).first()
        
        if not modification:
            return Response(
                {
                    "message": "Ну елки палки. No modification with this slug."
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
        field = request.query_params.get("type", "")
        limit = request.query_params.get("limit", 5)
        
        if not limit.isdecimal():
            return Response({
                "message": "Я предупреждал, готовь жопу. limit param number only."
            }, status.HTTP_400_BAD_REQUEST)
        
        limit = int(limit)
        
        if field not in AddressSearch.VALID_SEARCH_FIELDS:
            return Response({
                "message": f"Ёперный театр, \"type\" param not in {AddressSearch.VALID_SEARCH_FIELDS}"
            }, status.HTTP_400_BAD_REQUEST)
        
        response = AddressSearch.search(address, field, limit)
        
        return Response(
            response,
            status.HTTP_200_OK
        )
