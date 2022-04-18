import random
import re
import time
from datetime import timedelta, datetime
from datetime import timezone as datetime_timezone

from django.conf import settings
from pytz import timezone

_tz = datetime_timezone(offset=timedelta(seconds=3600 * 8), name=settings.TIME_ZONE)


def get_CST_timezone():
    return _tz


def get_timestamp():
    return int(time.time() * 1000)


def get_timestamp_in_sec():
    return int(time.time())


def humanize_ts(ts, tz_info=None, format='%Y%m%d%H%M%S'):
    if tz_info is None:
        tz_info = settings.TIME_ZONE
    dobj = datetime.fromtimestamp(ts)
    localtz = timezone(tz_info)
    local_dobj = localtz.localize(dobj)
    return local_dobj.strftime(format)


def get_local_now():
    return datetime.now(tz=_tz)


def md5(text):
    import hashlib
    m = hashlib.md5()
    m.update(text.encode('UTF-8'))
    return m.hexdigest()


def uuid_str(with_dash=True):
    import uuid
    result = str(uuid.uuid4())
    if not with_dash:
        result.replace('-', '')
    return result


def first(iterable, callable):
    for i in iterable:
        if callable(i):
            return i
    return None


def last(iterable, callable):
    for i in reversed(iterable):
        if callable(i):
            return i
    return None


def rest_urls(obj_name, view, download_view=None, actions=None):
    from django.urls import path
    urls = []
    if download_view:
        urls.append(path(obj_name + '/download', download_view.as_view()))
    urls.extend([
        path(obj_name, view.as_view()),
        path(obj_name + '/<str:pk>', view.as_view()),
    ])
    if isinstance(actions, list):
        for action in actions:
            urls.append(path('{}/<str:pk>/{}'.format(obj_name, action), view.as_view(action=action)))
    return urls


def generate_random_id():
    now = get_local_now()
    return now.strftime('%Y%m%d%H%M%S%f')[:-3] + str(random.randrange(100, 900))


def is_phone_number(value):
    # 手机号码以1开头，第二位可能为：3，4，5，6, 7，8，9，后面紧跟着9位数字
    return len(value) == 11 and re.compile(r'1[3,4,5,6,7,8,9]\d{9}').match(value)


def is_telephone_number(value):
    """
    验证固定电话
    """
    return len(value) == 12 and re.compile(r'\d{3}-\d{7,8}|\d{4}-\d{7,8}').match(value)
