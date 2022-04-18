from rest_framework.permissions import SAFE_METHODS

from common.auth.permission import UserAccessPermission
from blog.models.account import MSAccount


class UserPermission(UserAccessPermission):
    user_model = MSAccount


class SuperUserPermission(UserPermission):
    def has_permission(self, request, view):
        super().has_permission(request, view)
        user = request.user
        return user and user.is_superuser


class ShopAccountActionPermission(UserPermission):
    pass


class ShopAccountReadPermission(UserPermission):
    def has_permission(self, request, view):
        super().has_permission(request, view)
        user = request.user
        return user and not user.is_superuser and request.method in SAFE_METHODS
