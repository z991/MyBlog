from django.db import models


class BaseApiLog(models.Model):
    class Meta:
        abstract = True

    METHOD_UNKNOWN = 0
    METHOD_GET = 1
    METHOD_POST = 2
    METHOD_PUT = 3
    METHOD_DELETE = 4
    METHODS = [
        (METHOD_GET, 'GET'),
        (METHOD_POST, 'POST'),
        (METHOD_PUT, 'PUT'),
        (METHOD_DELETE, 'DELETE')
    ]

    sessionid = models.CharField(max_length=50, blank=True, null=True)
    ip = models.CharField(max_length=30, blank=True, null=True)
    user_agent = models.CharField(max_length=500, blank=True, null=True)
    method = models.CharField(choices=METHODS, max_length=50, blank=True, null=True)
    path = models.CharField(max_length=200, blank=True, null=True)
    query = models.CharField(max_length=500, blank=True, null=True)
    payload = models.JSONField(blank=True, null=True)
    req_id = models.CharField(max_length=20, blank=True, null=True)
    resp_status = models.IntegerField(blank=True, null=True)
    spent = models.PositiveIntegerField(blank=True, null=True)
    received = models.PositiveBigIntegerField(blank=True, null=True)
    handled = models.PositiveBigIntegerField(blank=True, null=True)
    date = models.DateField(blank=True, null=True, auto_now=True)

    @classmethod
    def method_value(cls, string):
        string = string.upper()
        for value, str in cls.METHODS:
            if string == str:
                return value
        return cls.METHOD_UNKNOWN

    def set_user(self, user):
        if not user:
            return
        setattr(self, 'user', user)

    def pre_save_request(self, req):
        pass

    def pre_save_response(self, resp):
        pass

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.received and self.handled:
            self.spent = self.handled - self.received
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return str(self.pk)


