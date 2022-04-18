import logging
import os
import time
from datetime import datetime, timedelta
from logging import FileHandler, LogRecord, Formatter, Filter, StreamHandler

from django.conf import settings

from common.helper import get_CST_timezone, get_local_now

level_short_name_map = {
    logging.DEBUG: 'D',
    logging.INFO: 'I',
    logging.WARNING: 'W',
    logging.ERROR: 'E',
    logging.CRITICAL: 'C'
}


class LogFilter(Filter):

    def filter(self, record: LogRecord):
        if record.name.startswith('django.') and record.levelno < logging.WARNING:
            return 0
        record.short_level = level_short_name_map.get(record.levelno, record.levelname)
        return super().filter(record)


class LogFormatter(Formatter):

    def __init__(self):
        fmt = "%(short_level)s|%(asctime)s.%(msecs)d|%(processName)s|%(name)s|%(message)s"
        datefmt = "%H:%M:%S"
        super().__init__(fmt=fmt, datefmt=datefmt)

    def converter(self, *args):
        return datetime.now(tz=get_CST_timezone()).timetuple()


class DateRotatingFileHandler(FileHandler):

    def __init__(self, base_dir, only_error, mode='a', encoding=None, delay=True):
        self.base_dir = base_dir
        self.only_error = only_error
        self.today = self.get_today_start()
        self.next_rotate_ts = self.get_next_rotate_ts()
        filename = self.get_filename()
        super().__init__(filename, mode, encoding, delay=delay)
        self.level = logging.ERROR if self.only_error else logging.DEBUG

    def get_next_rotate_ts(self):
        tomorrow = self.today + timedelta(days=1)
        return tomorrow.timestamp()

    def emit(self, record: LogRecord):
        self.rollover_if_needed()
        super().emit(record)

    def rollover_if_needed(self):
        if time.time() < self.next_rotate_ts:
            return
        self.today = self.get_today_start()
        self.next_rotate_ts = self.get_next_rotate_ts()
        filename = self.get_filename()
        if self.stream:
            self.stream.close()
            self.stream = None
        self.baseFilename = os.path.abspath(filename)
        self.stream = self._open()

    def get_filename(self):
        os.makedirs(self.base_dir, exist_ok=True)
        extension = self.only_error and '.error.log' or '.log'
        return os.path.join(self.base_dir, self.today.strftime("%Y%m%d") + extension)

    def get_today_start(self):
        format = '%Y%m%d'
        datetime_obj = datetime.strptime(get_local_now().strftime(format), format)
        return datetime_obj.replace(tzinfo=get_CST_timezone())


def _get_handler(dir_name, only_error):
    base_dir = str(settings.BASE_DIR) + "/storage/{}/".format(dir_name)
    file_handler = DateRotatingFileHandler(base_dir, only_error)
    file_handler.addFilter(LogFilter())
    file_handler.setFormatter(LogFormatter())
    return file_handler


handlers = [_get_handler('logs', True), _get_handler('logs', False)]
if settings.DEBUG:
    handlers.append(StreamHandler())


def config_logging():
    global handlers
    logging.basicConfig(level=settings.LOG_LEVEL, handlers=handlers)
