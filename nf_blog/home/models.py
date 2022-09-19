from django.db import models
from django.utils import timezone
# Create your models here.


class ArticleCategory(models.Model):
    """
    文章分类
    """
    # 栏目标题
    title = models.CharField(max_length=100, blank=True)
    # 创建时间
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'tb_category'
        verbose_name = '类别管理'
        verbose_name_plural = verbose_name


from users.models import User
from django.utils import timezone


class Article(models.Model):
    """
    作者
    标题图片
    标题
    分类
    标签
    摘要信息
    文章正文
    浏览量
    评论量
    博客创建时间
    文章的修改时间
    """
    # 作者
    # 参数on_delete 当user表中的数据删除之后，文章信息同步删除
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # 标题图片
    avatar = models.ImageField(upload_to='article/%Y%m%d/', blank=True)
    # 标题
    title = models.CharField(max_length=25, blank=True)
    # 分类 related_name 是可以通过分类来反向获取文章信息
    category = models.ForeignKey(
        ArticleCategory,
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='article'
    )
    # 标签
    tags = models.CharField(max_length=20, blank=True)
    # 摘要信息
    summary = models.CharField(max_length=20, null=False, blank=False)
    # 文章正文
    content = models.TextField()
    # 浏览量
    total_views = models.PositiveIntegerField(default=0)
    # 评论量
    comments_count = models.PositiveIntegerField(default=0)
    # 博客创建时间
    created = models.DateTimeField(default=timezone.now)
    # 文章的修改时间
    updated = models.DateTimeField(auto_now=True)

    # 修改表明以及admin展示的配置信息等
    class Meta:
        db_table = 'tb_article'
        ordering = ('-created',)
        verbose_name = '文章管理'
        verbose_name_plural = verbose_name

    # 文章标题返回
    def __str__(self):
        return self.title


class Comment(models.Model):
    """
    1.评论内容
    2.评论时间
    3.评论的用户
    4.评论的时间
    """
    # 1.评论内容
    content = models.TextField()
    # 2.评论时间
    article = models.ForeignKey(Article, on_delete=models.SET_NULL, null=True)
    # 3.评论的用户
    user = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    # 4.评论的时间
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.article.title

    class Meta:
        db_table='tb_comment'
        verbose_name = '评论管理'
        verbose_name_plural = verbose_name
