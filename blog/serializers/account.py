from django.contrib.auth.hashers import check_password
from django.db.transaction import atomic
from rest_framework import serializers

from blog.serializers.base import BaseModelSerializer
from common.models.constants import ENABLE_STATUS
from common.serializers.base import BaseSerializer, ChoiceSerializer
from blog.models.account import MSAccount
from blog.models.log import MSAccountLoginLog
from common.validators import UsernameValidator, PhoneNumberValidator, PasswordValidator


class AccountSerializer(BaseModelSerializer):
    class Meta:
        model = MSAccount
        exclude = ['password', 'salt', 'reset_pw_time']
        extra_kwargs = {
            'username': {'validators': [UsernameValidator()]},
            'phone': {'validators': [PhoneNumberValidator()]},
            'is_superuser': {'read_only': True},
            'registered_at': {'read_only': True}
        }

    status = ChoiceSerializer(choice_class=ENABLE_STATUS)
    init_password = serializers.CharField(write_only=True, validators=[PasswordValidator()])
    init_password_confirm = serializers.CharField(write_only=True, validators=[PasswordValidator()])

    def to_internal_value(self, data):
        # TODO: Optimize, how to add non native fields
        instance = super().to_internal_value(data)
        return instance

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        if not self.instance:
            password = validated_data.get('init_password')
            password_confirm = validated_data.get('init_password_confirm')
            if password != password_confirm:
                raise serializers.ValidationError('两次输入的密码不一致')
        return super().validate(attrs)

    @atomic
    def create(self, validated_data):
        password = validated_data.pop('init_password')
        validated_data.pop('init_password_confirm')

        instance = super().create(validated_data)
        instance.reset_password(password)
        instance.save()
        return instance


class AccountLoginSerializer(BaseSerializer):
    username = serializers.CharField(required=True, allow_blank=False, allow_null=False)
    password = serializers.CharField(required=True, allow_blank=False, allow_null=False)
    account = None

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        account = MSAccount.objects.filter(username=validated_data['username']).first()
        if not account:
            raise serializers.ValidationError({'username': '账号不存在'})

        if not check_password(validated_data['password'], account.password):
            raise serializers.ValidationError({'password': '密码错误'})

        if account.status != ENABLE_STATUS.ENABLED:
            raise serializers.ValidationError('账号已被禁用，请联系管理员')

        request = self.context['request']
        MSAccountLoginLog.create_log(account, ip=request.META['REMOTE_ADDR'],
                                     user_agent=request.META['HTTP_USER_AGENT'])
        self.account = account
        return validated_data

    def create(self, validated_data):
        return self.account

    def to_representation(self, instance):
        return {'token': self.account.issue_token()}


class AccountManageResetPasswordSerializer(BaseSerializer):
    new_password = serializers.CharField(allow_null=False, allow_blank=False, validators=[PasswordValidator()])
    new_password_confirm = serializers.CharField(allow_null=False, allow_blank=False, validators=[PasswordValidator()])

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        new_password = validated_data['new_password']
        new_password_confirm = validated_data['new_password_confirm']
        if new_password != new_password_confirm:
            raise serializers.ValidationError('两次输入的密码不一致')
        return validated_data

    def update(self, instance, validated_data):
        new_password = validated_data.pop('new_password')
        instance.reset_password(new_password)
        instance.save()
        return instance

    def to_representation(self, instance):
        return {}


class AccountResetPasswordSerializer(AccountManageResetPasswordSerializer):

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        request_user = self.context['request'].user
        if self.instance.id != request_user.id:
            raise serializers.ValidationError('非法操作，无法重置他人密码')
        return validated_data
