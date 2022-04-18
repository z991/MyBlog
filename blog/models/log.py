from django.db import models
from django_extensions.db.models import TimeStampedModel

from blog.models.account import MSAccount

class MSAccountLoginLog(TimeStampedModel):
    class Meta:
        db_table = 'ms_account_login_log'
        managed = False
        verbose_name = '系统账号登录日志'
        verbose_name_plural = 'Misc - 用户登录日志'

    account = models.ForeignKey(MSAccount, models.SET_NULL, blank=True, null=True)
    ip = models.CharField(max_length=30, blank=True, null=True)
    user_agent = models.CharField(max_length=500, blank=True, null=True)

    @classmethod
    def create_log(cls, user, ip, user_agent):
        return cls.objects.create(account=user, ip=ip, user_agent=user_agent)

