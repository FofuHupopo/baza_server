from . import repositories
from . import serializers

class LoyaltyService:
    @staticmethod
    def get(user_id: int) -> serializers.LoyaltySerializer:
        loyalty = repositories.LoyaltyRepository.get(user_id=user_id)

        serializer = serializers.LoyaltySerializer(loyalty)

        return serializer

    @staticmethod
    def create(user_id: int) -> serializers.LoyaltySerializer:
        loyalty = repositories.LoyaltyRepository.create(user_id=user_id)

        serializer = serializers.LoyaltySerializer(loyalty)

        return serializer

    @staticmethod
    def get_or_create(user_id: int) -> serializers.LoyaltySerializer:
        loyalty = repositories.LoyaltyRepository.get_or_create(user_id=user_id)
        
        serializer = serializers.LoyaltySerializer(loyalty)

        return serializer

