from common.models.constants import FILE_TYPE
from marketing.models.file import MSFileResource
from marketing.serializers.file import MSFileResourceSerializer
from marketing.views.base import BaseRestfulView


class BaseFileUploadView(BaseRestfulView):
    need_log_body = False

    queryset = MSFileResource.objects.all()
    serializer_class = MSFileResourceSerializer

    http_method_names = ['post']

    resource_client_key = None
    allowed_file_types = []

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(allowed_file_types=self.allowed_file_types, *args, **kwargs)


class ImageUploadView(BaseFileUploadView):
    allowed_file_types = [FILE_TYPE.IMAGE]


class AttachmentUploadView(BaseFileUploadView):
    allowed_file_types = [FILE_TYPE.IMAGE, FILE_TYPE.ARCHIVE]
