from django.db import models

from common.models.constants import ENABLE_STATUS, ERR_MSG


class EnabledStatusManager(models.Manager):
    def __init__(self, name):
        super().__init__()
        self.status_name = name

    def get_queryset(self):
        return super().get_queryset().filter(**{self.status_name: ENABLE_STATUS.ENABLED})


def EnableStatusMixin(name=None):
    if name is None:
        name = 'status'

    class Meta:
        abstract = True
        default_manager_name = 'objects'

    status = models.SmallIntegerField('启用/禁用', db_column=name, choices=ENABLE_STATUS.CHOICES,
                                      default=ENABLE_STATUS.ENABLED, error_messages=ERR_MSG)
    enabled_objects = EnabledStatusManager(name)

    attrs = {
        'Meta': Meta,
        'status': status,
        'objects': models.Manager(),
        'enabled_objects': enabled_objects,
        '__module__': 'common.model.mixins'
    }
    new_class = type('EnableStatusMixin', (models.Model,), attrs)
    return new_class
