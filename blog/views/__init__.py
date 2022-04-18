from common.views.mixins import BaseRestfulMixin
from blog.serializers.account import AccountLoginSerializer
from blog.views.base import BaseAPIView


class LoginView(BaseRestfulMixin, BaseAPIView):
    need_log_body = False
    serializer_class = AccountLoginSerializer
    http_method_names = ['post']