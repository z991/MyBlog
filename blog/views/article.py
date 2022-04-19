from blog.models.article import Tag, Category
from blog.serializers.article import TagSerializer, CategorySerializer
from blog.views.base import SuperUserActionView, NoLoginRestfulView


class TagManageView(NoLoginRestfulView):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class CategoryManageView(NoLoginRestfulView):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
