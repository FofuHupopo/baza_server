from rest_framework.permissions import BasePermission
from rest_framework.request import Request
import ipaddress

from .utils import get_ip_from_request


class TinkoffPermission(BasePermission):
    def has_permission(self, request: Request, view):
        return request.META.get("HTTP_REFERER", "") == "https://securepayments.tinkoff.ru/"


class IsSuperUser(BasePermission):
    def has_permission(self, request, view) -> bool:
        return request.user and request.user.is_superuser


class DolyamePermission(BasePermission):
    def has_permission(self, request, view) -> bool:
        ip = get_ip_from_request(request)
        
        ip_address = ipaddress.ip_address(ip)
        dolyame_net = ipaddress.ip_network("91.194.226.0/23")
        
        if ip_address in dolyame_net:
            return True
        
        return False
