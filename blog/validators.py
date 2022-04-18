import re

from django.db.models import Q
from rest_framework.exceptions import ValidationError


class UniqueWithinClientValidator:
    requires_context = True

    def __init__(self, client_key, fields, exclude_query=None):
        if exclude_query is None:
            exclude_query = {}
        self.client_key = client_key
        self.fields = fields
        self.extra_query = exclude_query

    def __call__(self, attrs, serializer):
        qs = serializer.Meta.model.objects.exclude(**self.extra_query)
        client_value = serializer.context['request'].user.client
        values = {}
        for f in self.fields:
            if f in attrs:
                values[f] = attrs[f]
            else:
                values[f] = getattr(serializer.instance, f, None) if serializer.instance else None
        values[self.client_key] = client_value
        qs = qs.filter(**values)
        if serializer.instance:
            qs = qs.filter(~Q(pk=serializer.instance.pk))
        if qs.exists():
            raise ValidationError({f: '具有同样值的数据已存在' for f in self.fields})


class ShopIDValdiator:
    def __call__(self, value):
        if not re.match(r'^[a-zA-Z0-9]*$', value):
            raise ValidationError('门店ID格式不正确，只允许数字和字母')


class LonLatValidator:
    def __call__(self, value):
        lonlat_arr = value.split(',')
        if len(lonlat_arr) != 2:
            raise ValidationError('经纬度格式不合法')
        try:
            lon, lat = map(float, lonlat_arr)
        except Exception as e:
            raise ValidationError('经纬度必须是数字')
        if lon > 180 or lon < -180:
            raise ValidationError('经度范围为[-180,180]')
        if lat > 90 or lat < -90:
            raise ValidationError('维度范围为[-90,90]')


class MemberGradeDiscountValidator:
    def __call__(self, value):
        if not 10 <= value <= 100:
            raise ValidationError('折扣取值范围为10%~100%')
