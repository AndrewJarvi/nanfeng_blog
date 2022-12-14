from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

# 用户信息
class User(AbstractUser):

    # 电话号码字段
    # unique 为唯一性字段
    mobile = models.CharField(max_length=11, unique=True, blank=False)

    # 头像
    # upload_to为保存到响应的子目录中
    avatar = models.ImageField(upload_to='avatar/%Y%m%d/', blank=True)

    # 个人简介
    user_desc = models.CharField(max_length=500, blank=True)

    # 修改认证的字段为手机号
    USERNAME_FIELD = 'mobile'
    # 内部类 class Meta 用于给 model 定义元数据

    # 创建超级管理员必需的字段（不包括手机号和密码）
    REQUIRED_FIELDS = ['username', 'email']

    class Meta:
        db_table = 'tb_users'  # 修改默认的表名
        verbose_name = '用户信息'  # Admin后台显示
        verbose_name_plural = verbose_name  # Admin后台显示

    # 方法重写，因为是自定义的
    def __str__(self):
        return self.mobile
