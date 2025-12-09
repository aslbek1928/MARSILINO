from rest_framework.permissions import BasePermission

class IsRestaurantAdmin(BasePermission):
    """
    Allows access only to restaurant admins or superusers.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return hasattr(request.user, 'restaurant_admin_profile')
