from django.db import models
from django_extensions.db.models import TimeStampedModel


class BaseModel(TimeStampedModel, models.Model):
    class Meta:
        abstract = True
