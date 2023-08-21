from rest_framework import status, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request, HttpRequest
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.conf import settings

from . import models
from . import serializers


class ListOrderView(generics.ListAPIView):
    queryset = models.OrderModel.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.ListOrderSerializer
    
    def get_queryset(self, request: Request):
        queryset = super().get_queryset()
        
        return queryset.filter(
            user=request.user
        )
