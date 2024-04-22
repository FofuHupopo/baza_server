from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from . import serializers
from . import services


class LoyaltyController(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.LoyaltySerializer
    
    def get(self, request: Request):
        serializer = services.LoyaltyService.get_or_create(user_id=request.user.id)
        
        return Response(
            serializer.data,
            status.HTTP_200_OK
        )
