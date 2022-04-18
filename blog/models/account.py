from django.db import models

from common.models.user import BaseUser


class MSAccount(BaseUser):
    class Meta:
        managed = False
        db_table = 'ms_account'
        verbose_name = '系统账号'
        verbose_name_plural = '博客管理 - 账号管理'

    is_superuser = models.BooleanField('超级管理员', default=False)
