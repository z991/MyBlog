from django.db import models
from markdown import Markdown

from blog.models.account import MSAccount
from common.models.base import BaseModel


class Tag(BaseModel):
    """文章标签"""
    text = models.CharField(max_length=30)

    class Meta:
        db_table = "article_tag"
        ordering = ['-id']

    def __str__(self):
        return self.text


class Category(BaseModel):
    """文章分类"""
    title = models.CharField(max_length=100)

    class Meta:
        db_table = "article_category"
        ordering = ['-created']

    def __str__(self):
        return self.title


class Avatar(BaseModel):
    content = models.ImageField(upload_to='avatar/%Y%m%d')

    class Meta:
        db_table = "article_avatar"


class Article(BaseModel):
    """博客文章 model"""
    author = models.ForeignKey(
        MSAccount,
        null=True,
        on_delete=models.CASCADE,
        related_name='articles'
    )
    # 分类
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='articles'
    )
    # 标签
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='articles', through='Article2Tag'
    )
    # 标题图
    avatar = models.ForeignKey(
        Avatar,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='article'
    )
    # 标题
    title = models.CharField(max_length=100)
    # 正文
    body = models.TextField()

    class Meta:
        db_table = "article"
        ordering = ['-created']

    def __str__(self):
        return self.title

    def get_md(self):
        md = Markdown(
            extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
                'markdown.extensions.toc',
            ]
        )
        md_body = md.convert(self.body)
        return md_body, md.toc


class Article2Tag(BaseModel):

    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    class Meta:
        db_table = "article_2_tag"
