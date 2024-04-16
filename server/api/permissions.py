from rest_framework.permissions import BasePermission
from rest_framework.request import Request


class TinkoffPermission(BasePermission):
    def has_permission(self, request: Request, view):
        return request.META.get("HTTP_REFERER", "") == "https://securepayments.tinkoff.ru/"
