from rest_framework.permissions import BasePermission
import jwt
from django.conf import settings

class IsCashier(BasePermission):
    """
    Allows access only to authenticated cashiers.
    Checks for 'role': 'cashier' in the JWT token.
    """
    def has_permission(self, request, view):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return False
        
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            return payload.get('role') == 'cashier'
        except jwt.InvalidTokenError:
            return False
