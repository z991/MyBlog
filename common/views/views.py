import logging
import random

from django.conf import settings
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import GenericAPIView

from common.models.log import BaseApiLog
from common.models.user import BaseUser
from common.views.resp import JSONResponse
from common.helper import get_timestamp


def suppress_exception(func):
    def inner(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as ex:
            if settings.DEBUG:
                raise ex
            else:
                logging.error('Exception', exc_info=ex)

    return inner


class LogApiView(GenericAPIView):
    """
    接收req和发送resp都会进行相应的日志记录，并且把记录保存到数据库中
    """
    skip_log_exc_classes = [PermissionDenied]

    need_log_body = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.req_id = random.randrange(1, 1000)
        self.user = None

    def initialize_request(self, request, *args, **kwargs):
        req = super().initialize_request(request, *args, **kwargs)
        req.init_ts = get_timestamp()
        return req

    def initial(self, request, *args, **kwargs):
        try:
            super().initial(request, *args, **kwargs)
        finally:
            # 可能在initial的过程中抛出异常，用finally来确保能执行
            self.log_request(request)

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        self.log_response(response)
        return response

    def handle_exception(self, exc):
        self.log_exception(exc)
        return super().handle_exception(exc)

    def log_exception(self, exc):
        exc_info = exc
        for clazz in self.skip_log_exc_classes:
            if isinstance(exc, clazz):
                exc_info = None
                break
        self.logger.exception('[Exc {}] {}'.format(self.req_id, repr(exc)), exc_info=exc_info)

    def query_params_to_str(self, request):
        query_params = request.query_params
        params = ['{}={}'.format(k, v) for k, v in query_params.items()]
        return ("?" + "&".join(params)) if params else ''

    def log_item_str(self, k, v):
        return '[{}|{}]'.format(k, v or '')

    def log_request(self, request):
        user_id = request.user.pk if isinstance(request.user, BaseUser) else None
        req_data_str = None
        if self.need_log_body and request.method != 'GET':
            req_data_str = str(request.data)
        msg = '{req}{session}{user} {method}: {path}{query} {payload}'.format(
            req=self.log_item_str('Req', self.req_id),
            session=self.log_item_str('S', request.headers.get('X-SESSIONID')),
            user=self.log_item_str('U', user_id),
            method=request.method,
            path=request.path,
            query=self.query_params_to_str(request),
            payload=req_data_str
        )
        self.logger.info(msg)

    def log_response(self, response):
        prefix = '{resp}{session}'.format(resp=self.log_item_str('Resp', self.req_id),
                                          session=self.log_item_str('S', response.headers.get('X-SESSIONID')))
        if response.status_code == 200:
            if isinstance(response, JSONResponse):
                code = response.data['code']
                msg = response.data['msg']
                self.logger.info('{}: Code: {} Msg: {}'.format(prefix, code, msg))
            else:
                self.logger.info('{}: {}'.format(prefix, response))
        else:
            self.logger.warning('{}: StatusCode: {} '.format(prefix, response.status_code))
