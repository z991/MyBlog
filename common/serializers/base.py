from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework.serializers import ListSerializer


class BaseSerializer(serializers.Serializer):
    pass


class BaseModelSerializer(serializers.ModelSerializer):
    # 会把初始化的data中的响应field对应值修改为UpperCase
    uppercase_fields = []

    def __init__(self, *args, **kwargs):
        data = kwargs.get('data')
        if data and len(self.uppercase_fields) > 0:
            for f in self.uppercase_fields:
                if f in data and isinstance(data[f], str):
                    data[f] = data[f].upper()

        self.only_fields = kwargs.pop('only_fields', None)
        self.exclude_fields = kwargs.pop('exclude_fields', None)

        assert not (self.only_fields and self.exclude_fields), (
            "Cannot set both 'only_fields' and 'exclude_fields' options on "
            f"serializer {self.__class__.__name__}"
        )

        super(BaseModelSerializer, self).__init__(*args, **kwargs)
        if self.only_fields is not None:
            allowed = set(self.only_fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        if self.exclude_fields is not None:
            not_allowed = set(self.exclude_fields)
            existing = set(self.fields)
            for field_name in existing & not_allowed:
                self.fields.pop(field_name)

    def is_many(self):
        return isinstance(self.parent, ListSerializer)

    def get_field_default_value(self, field_name):
        ModelClass = self.Meta.model
        field = ModelClass._meta.get_field(field_name)
        return field.get_default()


class ChoiceSerializer(serializers.Serializer):
    choice_class = None

    def __init__(self, instance=None, data=empty, choice_class=None, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.choice_class = choice_class

    def to_representation(self, instance):
        return self.choice_class.choice(instance)

    def to_internal_value(self, data):
        if not self.choice_class.is_valid_value(data):
            raise serializers.ValidationError('不支持的值')
        return data
