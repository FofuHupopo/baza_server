from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from . import serializers
from .. import models
from . import services


class LoyaltyController(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.LoyaltySerializer
    
    def get(self, request: Request):
        serializer = services.LoyaltyService.get_or_create(user_id=request.user.id)
        serializer.instance.save()
        
        return Response(
            serializer.data,
            status.HTTP_200_OK
        )
        
    def delete(self, request: Request):
        instance = services.LoyaltyService.get_or_create(user_id=request.user.id).instance
        
        instance.status = "black"
        instance.balance = 0
        instance.awaiting_balance = 0
        instance.remained = 0
        instance.total_spent = 0
        
        instance.save()
        
        models.LoyaltyHistoryModel.objects.filter(
            user_id=request.user.id
        ).delete()
        
        return Response(
            "Ok",
            status.HTTP_200_OK
        )

class LoyaltyHistoryController(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.LoyaltyHistorySerializer
    queryset = models.LoyaltyHistoryModel.objects.all()
    
    def get_queryset(self):
        return self.queryset.filter(user_id=self.request.user.id)


class FakeLoyaltyController(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request: Request):
        type_ = request.data.get("type")
        amount = int(request.data.get("amount"))
        
        if type_ == "add":
            loyalty_instance = services.LoyaltyService.get_or_create(
                user_id=request.user.id
            ).instance
            loyalty_instance.add_awaiting_balance(amount)
            
            models.LoyaltyHistoryModel.objects.create(
                user_id=request.user.id,
                operation=models.LoyaltyOperationModel.MARKETING,
                value=amount * models.LOYALTY_LEVELS.get(loyalty_instance.status).get("percent"),
                total=loyalty_instance.balance + loyalty_instance.awaiting_balance
            )

        if type_ == "confirm":
            services.LoyaltyService.get_or_create(
                user_id=request.user.id
            ).instance.confirm_balance(amount)
        
        return Response(
            "",
            status.HTTP_200_OK
        )
