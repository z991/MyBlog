# -*- coding: UTF-8 -*-
import tempfile
from pathlib import Path

from django.conf import settings
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from django.utils.functional import cached_property
from obs import ObsClient


class Config:
    def __init__(self, option):
        self.access_key = option['AccessKey']
        self.secret_key = option['SecretKey']
        self.server = option['Server']
        self.url = option['URL']


@deconstructible()
class HuaweiStorage(Storage):
    def __init__(self, option=None):
        if not option:
            option = settings.HUAWEI_OBS_SETTINGS
        self.config = Config(option)
        self.bucket = option['Bucket']

    @cached_property
    def client(self):
        return ObsClient(access_key_id=self.config.access_key,
                         secret_access_key=self.config.secret_key,
                         server=self.config.server)

    def _check_url(self, name):
        return name.startswith('http')

    def _open(self, name, mode='rb'):
        if self._check_url(name):
            return b''

        tmpf = Path(tempfile.gettempdir(), name)
        parent = tmpf.parent
        if not parent.exists():
            parent.mkdir(parents=True)
        self.client.getObject(self.bucket, name, downloadPath=tmpf)
        return open(tmpf, mode)

    def _save(self, name, content):
        if self._check_url(name):
            return name

        _ = self.client.putObject(self.bucket, name, content)
        return name

    def exists(self, name):
        if self._check_url(name):
            return True

        response = self.client.getObjectMetadata(self.bucket, name)
        return response.status == 200

    def url(self, name):
        if self._check_url(name):
            return name

        return '{}/{}'.format(self.config.url, name)

    def size(self, name):
        if self._check_url(name):
            return 0

        response = self.client.getObjectMetadata(self.bucket, name)
        return response.body.contentLength

    def delete(self, name):
        if self._check_url(name):
            return

        self.client.deleteObject(self.bucket, name)
