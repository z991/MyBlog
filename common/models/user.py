import time

import jwt
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import models
from jwt import ExpiredSignatureError

from common.helper import uuid_str
from common.models.constants import ERR_MSG
from common.models.mixins import EnableStatusMixin


class BaseUser(EnableStatusMixin(), models.Model):
    class Meta:
        abstract = True

    JWT_TOKEN_ALGORITHM = 'HS256'
    JWT_SECRET = '_'

    username = models.CharField('登录名', max_length=50, blank=False, unique=True, error_messages=ERR_MSG)
    nickname = models.CharField('姓名', blank=False, max_length=50)
    phone = models.CharField('手机号', blank=False, max_length=20)
    password = models.CharField(max_length=200)
    salt = models.CharField(max_length=50)
    reset_pw_time = models.DateTimeField('重置密码时间', null=True)
    registered_at = models.DateTimeField('注册日期', auto_now_add=True)

    def reset_password(self, password):
        self.salt = uuid_str().split('-')[0]
        self.password = make_password(password, self.salt)

    def issue_token(self):
        now = int(time.time())
        payload = {
            'id': self.pk,
            'iat': now,
            'exp': now + settings.JWT_EXP_SECOND
        }
        return jwt.encode(payload, self.JWT_SECRET, algorithm=self.JWT_TOKEN_ALGORITHM)

    @classmethod
    def get_user_by_token(cls, token):
        try:
            payload = jwt.decode(token, cls.JWT_SECRET,
                                 algorithms=[cls.JWT_TOKEN_ALGORITHM],
                                 options={'require': ['id', 'iat', 'exp']})
            id = payload.get('id')
            user = cls.objects.filter(pk=id).first()
            if not user:
                return None
            iat = payload['iat']
            if user.reset_pw_time is not None and int(user.reset_pw_time.timestamp()) > iat:
                # 用户重置密码会重新发放新的token，之前发放的token都作为失效处理
                return None
            return user
        except ExpiredSignatureError as e:
            return None
        except Exception as e:
            return None

    def __eq__(self, other):
        return other and self.pk == other.pk

    def __hash__(self):
        return super().__hash__()

    def __str__(self):
        return self.nickname
