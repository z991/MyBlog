from rest_framework import permissions

from common.exceptions import NeedLoginException
from common.models.constants import ENABLE_STATUS
from common.models.user import BaseUser

MSG_NEED_LOGIN = '需要登录'
MSG_ACCOUNT_BANNED = '账号已被禁用，请联系管理员'


class UserAccessPermission(permissions.BasePermission):
    user_model = BaseUser

    def has_permission(self, request, view):
        user = request.user
        if not isinstance(user, self.user_model):
            raise NeedLoginException(MSG_NEED_LOGIN)
        if user.status != ENABLE_STATUS.ENABLED:
            raise NeedLoginException(MSG_ACCOUNT_BANNED)
        return True
