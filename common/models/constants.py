class BASE_CHOICE:
    CHOICES = []

    @classmethod
    def choice(cls, value):
        return {'value': value, 'text': cls.text(value)}

    @classmethod
    def is_valid_value(cls, value):
        return value in [c[0] for c in cls.CHOICES]

    @classmethod
    def text(cls, value):
        for c in cls.CHOICES:
            if str(c[0]) == str(value):
                return c[1]
        return None


class FILE_TYPE(BASE_CHOICE):
    IMAGE = 1
    AUDIO = 2
    VIDEO = 3
    ARCHIVE = 4
    FONT = 5
    UNKNOWN = 999
    CHOICES = [
        (IMAGE, '图片'),
        (AUDIO, '音频'),
        (VIDEO, '视频'),
        (ARCHIVE, '档案'),
        (FONT, '字体'),
        (UNKNOWN, '不详'),
    ]

    @classmethod
    def get_type(cls, obj):
        from filetype import filetype
        from filetype.types import IMAGE, AUDIO, VIDEO, ARCHIVE, FONT
        file_type_map = [
            (IMAGE, FILE_TYPE.IMAGE),
            (AUDIO, FILE_TYPE.AUDIO),
            (VIDEO, FILE_TYPE.VIDEO),
            (ARCHIVE, FILE_TYPE.ARCHIVE),
            (FONT, FILE_TYPE.FONT),
        ]
        t = filetype.guess(obj)
        for k, v in file_type_map:
            if t in k:
                return v
        return FILE_TYPE.UNKNOWN


class ENABLE_STATUS(BASE_CHOICE):
    DISABLED = 0
    ENABLED = 1
    CHOICES = [
        (ENABLED, '启用'),
        (DISABLED, '禁用'),
    ]


class RESOURCE_USAGE(BASE_CHOICE):
    GENERAL = 1
    CHOICES = [
        (GENERAL, '通用')
    ]


class SYSTEM(BASE_CHOICE):
    MARKETING = 1
    MINI_PROGRAM = 2
    CHOICES = [
        (MARKETING, '营销系统'),
        (MINI_PROGRAM, '小程序')
    ]


class PAY_TYPE(BASE_CHOICE):
    CASH = 1
    WECHAT_PAY = 2

    CHOICES = [
        (CASH, '现金'),
        (WECHAT_PAY, '微信支付')
    ]


ERR_MSG = {
    'invalid_choice': '不支持的值：%(value)r',
    'null': '此处为必填项',
    'blank': '此处不能为空',
    'unique': "具有同样'%(field_label)s'的'%(model_name)s'已存在",
    'min_length': '至少需要{min_length}个元素',
}
