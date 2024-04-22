from api.profile import models
from api.authentication import models as auth_models


class LoyaltyRepository:
    @staticmethod
    def get(user_id: int) -> models.LoyaltyModel:
        return models.LoyaltyModel.objects.get(user_id=user_id)
    
    @staticmethod
    def create(user_id: int) -> models.LoyaltyModel:
        return models.LoyaltyModel.objects.create(user_id=user_id)

    @staticmethod
    def get_or_create(user_id: int) -> models.LoyaltyModel:
        try:
            return LoyaltyRepository.get(user_id=user_id)
        except models.LoyaltyModel.DoesNotExist:
            return LoyaltyRepository.create(user_id=user_id)
