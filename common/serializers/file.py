from filetype import filetype
from rest_framework import serializers
from rest_framework.fields import empty

from common.models.constants import FILE_TYPE
from common.models.files import CommonFileResource
from common.serializers.base import BaseModelSerializer


class BaseFileResourceSerializer(BaseModelSerializer):
    class Meta:
        model = CommonFileResource
        exclude = ['modified']
        extra_kwargs = {
            'filename': {'required': False},
            'file_type': {'required': False},
            'content_type': {'required': False},
            'size': {'required': False},
        }

    created = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')

    def __init__(self, allowed_file_types=None, *args, **kwargs):
        self.allowed_file_types = allowed_file_types
        super().__init__(*args, **kwargs)

    def validate(self, attrs):
        file = attrs['file']
        file_type = FILE_TYPE.get_type(file)
        if file_type not in self.allowed_file_types:
            msg = '只支持 [{}] 类型的文件'.format(', '.join([FILE_TYPE.text(t) for t in self.allowed_file_types]))
            raise serializers.ValidationError({'file': msg})
        file.seek(0)
        attrs['file_type'] = file_type
        attrs['filename'] = file.name
        attrs['content_type'] = filetype.guess_mime(file) or file.content_type
        attrs['size'] = file.size
        file.seek(0)
        return super().validate(attrs)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        return {
            'id': rep['id'],
            'url': rep['file'],
            'filename': rep['filename'],
            'file_type': rep['file_type'],
            'created': rep['created'],
        }


class FileIdSerializer(serializers.Serializer):
    def __init__(self, instance=None, data=empty, file_class=None, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.file_class = file_class

    def to_internal_value(self, data):
        file = self.file_class.objects.filter(pk=data).first()
        if not file:
            raise serializers.ValidationError('资源不存在')
        return file

    def to_representation(self, instance):
        file_resource = instance.file_resource
        return {
            'id': file_resource.id,
            'url': file_resource.file.url
        }
