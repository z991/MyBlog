from django_filters import rest_framework as filters
from blog.models.account import MSAccount
from common.views.mixins import BaseRestfulMixin
from blog.serializers.account import AccountLoginSerializer, AccountSerializer, AccountManageResetPasswordSerializer
from blog.views.base import BaseAPIView, SuperUserActionView, BaseRestfulActionsView, NoLoginRestfulView


class LoginView(BaseRestfulMixin, BaseAPIView):
    need_log_body = False
    serializer_class = AccountLoginSerializer
    http_method_names = ['post']


class AccountManageView(NoLoginRestfulView):
    class Filter(filters.FilterSet):
        class Meta:
            model = MSAccount
            fields = ['status']

        nickname = filters.CharFilter(field_name='nickname', lookup_expr='icontains')
        phone = filters.CharFilter(field_name='phone', lookup_expr='icontains')

    queryset = MSAccount.objects.all()
    serializer_class = AccountSerializer
    action_serializer_classes = {
        'reset_password': AccountManageResetPasswordSerializer
    }
    filter_class = Filter
