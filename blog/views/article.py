from blog.models.article import Tag, Category, Article, Avatar
from blog.serializers.article import TagSerializer, CategorySerializer, AvatarSerializer, ArticleSerializer
from blog.views.base import SuperUserActionView, NoLoginRestfulView


class AvatarView(SuperUserActionView):
    queryset = Avatar.objects.all()
    serializer_class = AvatarSerializer


class TagManageView(NoLoginRestfulView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class CategoryManageView(NoLoginRestfulView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ArticleView(SuperUserActionView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
