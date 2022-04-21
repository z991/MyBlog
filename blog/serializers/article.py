from django.db.transaction import atomic
from rest_framework import serializers

from blog.models.article import Tag, Category, Article, Article2Tag, Avatar
from blog.serializers.account import AccountSerializer
from common.serializers.base import BaseModelSerializer


class TagSerializer(BaseModelSerializer):
    """标签序列化器"""

    def check_tag_obj_exists(self, validated_data):
        text = validated_data.get('text')
        if Tag.objects.filter(text=text).exists():
            raise serializers.ValidationError('Tag with text {} exists.'.format(text))

    def create(self, validated_data):
        self.check_tag_obj_exists(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        self.check_tag_obj_exists(validated_data)
        return super().update(instance, validated_data)

    class Meta:
        model = Tag
        exclude = ['modified', 'created']


class CategorySerializer(BaseModelSerializer):
    """分类的序列化器"""

    class Meta:
        model = Category
        exclude = ['modified', 'created']
        read_only_fields = ['created']


class AvatarSerializer(BaseModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name='avatar-detail')

    class Meta:
        model = Avatar
        exclude = ['modified', 'created']


class _ArticleSerializer(BaseModelSerializer):
    tags = serializers.SerializerMethodField()

    id = serializers.IntegerField(read_only=True)
    author = AccountSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    avatar = AvatarSerializer(read_only=True)

    class Meta:
        model = Article
        exclude = ['modified', 'created']

    def get_tags(self, instance):
        article_relations = Article2Tag.objects.filter(article=instance).prefetch_related("article", "tag")
        tags = [relation.tag for relation in article_relations]
        return TagSerializer(tags, many=True, only_fields=['id', 'text']).data


class ArticleSerializer(BaseModelSerializer):

    tags = serializers.ListSerializer(child=serializers.IntegerField())
    category_id = serializers.IntegerField(write_only=True, allow_null=True, required=False)
    avatar_id = serializers.IntegerField(write_only=True,allow_null=True,required=False)

    class Meta:
        model = Article
        exclude = ['modified', 'created']

    def to_representation(self, instance):
        exclude_fields = None
        return _ArticleSerializer(instance, exclude_fields=exclude_fields).data

    def validate_category_id(self, value):
        if value and not Category.objects.filter(id=value).exists():
            raise serializers.ValidationError(f'id为{value}的分类不存在')
        return value

    def validate_avatar_id(self, value):
        if value and not Avatar.objects.filter(id=value).exists():
            raise serializers.ValidationError(f'id为{value}的图标不存在')
        return value

    def handle_tags(self, instance, value):
        create_list = []
        for tag_pk in value:
            if not Tag.objects.filter(id=tag_pk).exists():
                raise serializers.ValidationError(f'id为{tag_pk}的标签不存在')
            create_list.append(Article2Tag(article=instance, tag_id=tag_pk))

        Article2Tag.objects.filter(article=instance).delete()

        Article2Tag.objects.bulk_create(create_list)

    @atomic
    def create(self, validated_data):
        tags = validated_data.pop("tags", [])
        instance = super(ArticleSerializer, self).create(validated_data)

        # 处理门店信息
        self.handle_tags(instance, tags)
        instance.author = self.context['request'].user
        return instance

