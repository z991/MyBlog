from django.conf import settings
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied
from rest_framework.status import HTTP_405_METHOD_NOT_ALLOWED, HTTP_401_UNAUTHORIZED

from common.exceptions import RequirePasswordResetError, NeedLoginException, NeedSuperUserException, \
    CustomValidationError
from common.views import mixins
from common.views.mixins import BaseRestfulMixin, BaseDownloadMixin, BaseExcelComposeMixin
from common.views.views import LogApiView
from blog.auth.authentication import UserTokenAuthentication
from blog.auth.permission import UserPermission, SuperUserPermission, ShopAccountReadPermission, \
    ShopAccountActionPermission



class BaseAPIView(mixins.GeneralCodeMixin, mixins.BaseAPIViewMixin, LogApiView):
    authentication_classes = [UserTokenAuthentication]

    def handle_exception(self, exc):
        if isinstance(exc, MethodNotAllowed):
            return self.non_ok_resp(status=HTTP_405_METHOD_NOT_ALLOWED)
        if isinstance(exc, CustomValidationError):
            return self.ok_resp(code=exc.code, msg=exc.msg, data=exc.data)
        self.logger.exception("Exception", exc_info=exc)
        return self.ok_resp(self.CODE_GENERAL_ERROR, msg=str(exc) if settings.DEBUG else None)


class LoginRequiredApiView(BaseAPIView):
    permission_classes = [UserPermission]

    def handle_exception(self, exc):
        if isinstance(exc, NeedSuperUserException):
            return self.ok_resp(code=self.CODE_GENERAL_ERROR, msg=exc.msg)
        if isinstance(exc, RequirePasswordResetError):
            return self.non_ok_resp(status=HTTP_401_UNAUTHORIZED, code=self.CODE_NEED_RESET_PW, msg=exc.msg)
        if isinstance(exc, NeedLoginException):
            return self.non_ok_resp(status=HTTP_401_UNAUTHORIZED, code=self.CODE_NEED_LOGIN, msg=exc.msg)
        if isinstance(exc, PermissionDenied):
            return self.non_ok_resp(status=HTTP_401_UNAUTHORIZED, code=self.CODE_NOT_PERMITTED, msg=exc.detail)
        return super().handle_exception(exc)


class BaseRestfulView(BaseRestfulMixin, LoginRequiredApiView):
    pass


class BaseRestfulActionsView(BaseRestfulView):
    action_serializer_classes = {}

    action = None

    def __init__(self, action=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.action = action

    def get_serializer_class(self):
        if self.action:
            return self.action_serializer_classes.get(self.action, None)
        return super(BaseRestfulView, self).get_serializer_class()

    def get_serializer(self, *args, **kwargs):
        if self.action:
            kwargs['partial'] = False
        return super().get_serializer(*args, **kwargs)


class BaseDownloadView(BaseDownloadMixin, BaseRestfulView):
    pass


class BaseExportExcelView(BaseExcelComposeMixin, BaseDownloadView):
    def download(self, queryset):
        return self.create_excel(queryset)


class SuperUserView(BaseRestfulView):
    permission_classes = [SuperUserPermission]


class SuperUserActionView(BaseRestfulActionsView):
    permission_classes = [SuperUserPermission]


class ShopAccountReadView(BaseRestfulActionsView):
    permission_classes = [ShopAccountReadPermission | SuperUserPermission]


class ShopAccountActionView(BaseRestfulActionsView):
    permission_classes = [ShopAccountActionPermission | SuperUserPermission]
