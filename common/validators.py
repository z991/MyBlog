import re

from django.core.exceptions import ValidationError

from blog.models.account import MSAccount
from common.helper import is_phone_number


class PhoneNumberValidator:
    def __init__(self, many=False):
        self.many = many

    def __call__(self, value):
        values = value.split(',') if self.many else [value]
        if self.many:
            values = value.split(',')
        for v in values:
            if not is_phone_number(v):
                raise ValidationError('不正确的手机号码格式')


class AlphaNumericValidator:

    def __call__(self, value):
        if not re.match('^[a-zA-Z0-9_]*$', value):
            raise ValidationError('包含非法字符，只允许英文字母、数字以及下划线_')


class NoDuplicateValidator:

    def __call__(self, value):
        if len(value) != len(list(set(value))):
            raise ValidationError('不能包含重复的元素')


class PositiveNumericValidator:
    def __call__(self, value):
        if not value > 0:
            raise ValidationError('非法数字，只允许正数')


class UsernameValidator:
    def __call__(self, value):
        max_len = 30

        if MSAccount.objects.filter(username=value).exists():
            raise ValidationError("账号不可重复注册")

        if len(value) > max_len:
            raise ValidationError('账号最大长度不能超过{}个字符'.format(max_len))
        AlphaNumericValidator()(value)
        if is_phone_number(value):
            raise ValidationError('账号不能为手机号')


class PasswordValidator:
    def __call__(self, value):
        min_len = 8
        if len(value) < min_len:
            raise ValidationError('密码长度必须至少{}位'.format(min_len))
        if not (re.search('[a-zA-Z]+', value) and re.search('[0-9]+', value)):
            raise ValidationError('密码必须至少有1个字母和1个数字')


class ContacterNameValidator:
    def __call__(self, value):
        if not (2 <= len(value) <= 4):
            raise ValidationError('联系人长度必须在2-4之间')
        if not re.match(r'^[\u4e00-\u9fa5]{2,4}$', value):
            raise ValidationError('不正确的联系人格式')
