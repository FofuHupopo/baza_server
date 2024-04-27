from rest_framework.permissions import IsAuthenticated

from . import serializers
from .. import models

from rest_framework import generics


class AddressView(generics.ListCreateAPIView):
    """
    Адресы пользователя.

    Добавление и получение списка адресов пользователя, доступно только для
    текущего пользователю.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.AddressSerializer
    queryset = models.AddressModel.objects.all()
    
    def get_queryset(self):
        return self.queryset.filter(user_id=self.request.user.id)
    
    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user.id)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Адрес пользователя.

    Обновление и удаление адреса, доступно только для адреса, принадлежащего
    текущему пользователю.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.AddressSerializer
    queryset = models.AddressModel.objects.all()

    def get_queryset(self):
        return models.AddressModel.objects.filter(user_id=self.request.user.id)

    def perform_update(self, serializer):
        serializer.save(user_id=self.request.user.id)

    def perform_destroy(self, instance):
        instance.delete()

