from common.views.mixins import GeneralCodeMixin


class RequirePasswordResetError(Exception):
    def __init__(self, msg, *args):
        super().__init__(*args)
        self.msg = msg


class NeedLoginException(Exception):
    def __init__(self, msg, *args):
        super().__init__(*args)
        self.msg = msg


class NeedSuperUserException(Exception):

    def __init__(self, *args: object):
        super().__init__(*args)
        self.msg = '需要超级管理员权限'


class CustomValidationError(Exception):
    def __init__(self, code, msg, data=None, *args):
        self.code = code
        self.msg = msg
        self.data = data
        super().__init__(*args)


class InvalidParamsValidationError(CustomValidationError):
    def __init__(self, msg, *args):
        self.msg = msg
        super().__init__(GeneralCodeMixin.CODE_INVALID_PARAMS, msg, *args)
