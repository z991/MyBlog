import humanize
from django.conf import settings
from django.db import models
from django_extensions.db.models import TimeStampedModel
from rest_framework import serializers

from common.helper import get_local_now, uuid_str
from common.models.constants import RESOURCE_USAGE, FILE_TYPE, SYSTEM


def file_root_folder():
    f = 'blog'
    if settings.DEBUG:
        f = 'test.' + f
    return f


def file_upload_to(instance, filename):
    usage = instance.usage
    filename = uuid_str(with_dash=False)
    now = get_local_now()
    date_str = now.strftime('%Y/%m/%d')
    return '{}/file/{}/{}/{}/{}'.format(file_root_folder(), usage, instance.file_type, date_str, filename)


class SizeValidation:
    def __init__(self, max_size):
        self.max_size = max_size

    def __call__(self, image):
        if image.size > self.max_size:
            raise serializers.ValidationError('大小不可超过{}'.format(humanize.naturalsize(self.max_size)))


class WidthHeightValidation:

    def __init__(self, max_width, max_height):
        self.max_width = max_width
        self.max_height = max_height

    def __call__(self, image):
        errors = []
        if self.max_width and image.image.width > self.max_width:
            errors.append('宽度不可超过{}'.format(self.max_width))
        if self.max_height and image.image.height > self.max_height:
            errors.append('高度不可超过{}'.format(self.max_height))
        if errors:
            raise serializers.ValidationError(errors)


class ImageValidator:
    requires_context = True

    def __init__(self):
        super().__init__()

    def __call__(self, image, context):
        usage = context.parent.initial_data.get('usage')
        method_name = 'validators_for_usage_{}'.format(usage)
        if not hasattr(self, method_name):
            return
        validators = getattr(self, method_name)()
        for v in validators:
            v(image)

    def validators_for_usage_1(self):
        return []

    def validators_for_usage_2(self):
        return [
            SizeValidation(2000 * 1024),
            WidthHeightValidation(2048, 2048)
        ]

    def validators_for_usage_3(self):
        return [
            SizeValidation(2000 * 1024),
            WidthHeightValidation(2048, 2048)
        ]


class CommonFileResource(TimeStampedModel):
    class Meta:
        abstract = True
        db_table = 'common_file_resource'
        managed = False
        verbose_name = '文件资源'
        verbose_name_plural = '文件资源'

    usage = models.IntegerField('使用模块', choices=RESOURCE_USAGE.CHOICES, default=RESOURCE_USAGE.GENERAL)
    system = models.IntegerField('关联系统', choices=SYSTEM.CHOICES)
    file = models.FileField('资源', upload_to=file_upload_to, max_length=200)
    file_type = models.IntegerField('文件类型', choices=FILE_TYPE.CHOICES)
    filename = models.CharField('上传文件名', max_length=200)
    content_type = models.CharField('Content-Type', max_length=100)
    size = models.PositiveIntegerField('大小', help_text='单位为Byte', default=0)

    def save(self, **kwargs):
        is_new = self.pk is None
        super().save(**kwargs)
        if is_new:
            # 在OBS中，给文件设置content-type和content-disposition
            disposition = 'attachment; filename="download"; filename*=UTF-8{}{}'.format("''", self.filename)
            headers = {
                'contentType': self.content_type,
            }
            if self.file_type != FILE_TYPE.IMAGE:
                headers['contentDisposition'] = disposition
            storage = self.file.storage
            storage.client.setObjectMetadata(bucketName=storage.bucket, objectKey=self.file.name, headers=headers)

    def delete(self, using=None, keep_parents=False):
        if self.file:
            self.file.storage.delete(self.file.name)
        return super().delete(using, keep_parents)
