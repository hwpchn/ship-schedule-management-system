"""
用户认证模型
使用邮箱作为用户名进行认证
"""
import os
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.conf import settings
from .managers import UserManager


def user_avatar_upload_path(instance, filename):
    """
    生成用户头像上传路径
    格式: user_avatars/{user_id}/{filename}
    """
    # 获取文件扩展名
    ext = filename.split('.')[-1]
    # 生成新的文件名，避免冲突
    new_filename = f'avatar_{instance.id}.{ext}'
    return f'user_avatars/{instance.id}/{new_filename}'


class Permission(models.Model):
    """
    权限模型
    定义系统中的各种权限
    """
    code = models.CharField(
        verbose_name='权限代码',
        max_length=100,
        unique=True,
        help_text='权限的唯一标识符，如 user.list, user.create'
    )

    name = models.CharField(
        verbose_name='权限名称',
        max_length=100,
        help_text='权限的显示名称'
    )

    description = models.TextField(
        verbose_name='权限描述',
        blank=True,
        help_text='权限的详细描述'
    )

    category = models.CharField(
        verbose_name='权限分类',
        max_length=50,
        default='system',
        help_text='权限所属的功能模块分类'
    )

    created_at = models.DateTimeField(
        verbose_name='创建时间',
        auto_now_add=True
    )

    class Meta:
        verbose_name = '权限'
        verbose_name_plural = '权限'
        db_table = 'auth_custom_permission'
        ordering = ['category', 'code']

    def __str__(self):
        return f'{self.name} ({self.code})'


class Role(models.Model):
    """
    角色模型
    定义用户角色和对应的权限
    """
    name = models.CharField(
        verbose_name='角色名称',
        max_length=50,
        unique=True,
        help_text='角色的名称'
    )

    description = models.TextField(
        verbose_name='角色描述',
        blank=True,
        help_text='角色的详细描述'
    )

    permissions = models.ManyToManyField(
        Permission,
        verbose_name='权限',
        blank=True,
        help_text='该角色拥有的权限'
    )

    is_active = models.BooleanField(
        verbose_name='是否激活',
        default=True,
        help_text='角色是否处于激活状态'
    )

    created_at = models.DateTimeField(
        verbose_name='创建时间',
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        verbose_name='更新时间',
        auto_now=True
    )

    class Meta:
        verbose_name = '角色'
        verbose_name_plural = '角色'
        db_table = 'auth_role'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_permission_codes(self):
        """
        获取该角色的所有权限代码
        """
        return list(self.permissions.values_list('code', flat=True))


class User(AbstractBaseUser, PermissionsMixin):
    """
    自定义用户模型
    使用邮箱代替用户名进行认证
    """
    email = models.EmailField(
        verbose_name='邮箱地址',
        max_length=255,
        unique=True,
        help_text='用户的邮箱地址，用于登录认证'
    )

    first_name = models.CharField(
        verbose_name='名字',
        max_length=30,
        blank=True,
        help_text='用户的名字'
    )

    last_name = models.CharField(
        verbose_name='姓氏',
        max_length=30,
        blank=True,
        help_text='用户的姓氏'
    )

    avatar = models.ImageField(
        verbose_name='头像',
        upload_to=user_avatar_upload_path,
        blank=True,
        null=True,
        help_text='用户头像图片'
    )

    roles = models.ManyToManyField(
        Role,
        verbose_name='角色',
        blank=True,
        help_text='用户拥有的角色'
    )

    is_active = models.BooleanField(
        verbose_name='是否激活',
        default=True,
        help_text='用户账户是否处于激活状态'
    )

    is_staff = models.BooleanField(
        verbose_name='是否为管理员',
        default=False,
        help_text='用户是否可以访问管理后台'
    )

    date_joined = models.DateTimeField(
        verbose_name='注册时间',
        auto_now_add=True,
        help_text='用户账户创建的时间'
    )

    last_login = models.DateTimeField(
        verbose_name='最后登录时间',
        null=True,
        blank=True,
        help_text='用户最后一次登录的时间'
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        db_table = 'auth_user'
        ordering = ['-date_joined']

    def __str__(self):
        """返回用户的字符串表示"""
        return self.email

    def get_full_name(self):
        """
        返回用户的全名
        如果没有设置名字，则返回邮箱
        """
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name if full_name else self.email

    def get_short_name(self):
        """返回用户的简短名称"""
        return self.first_name if self.first_name else self.email.split('@')[0]

    def get_user_permissions(self):
        """
        获取用户的所有权限代码
        通过用户的角色来获取权限
        """
        permissions = set()
        for role in self.roles.filter(is_active=True):
            permissions.update(role.get_permission_codes())
        return list(permissions)

    def has_permission(self, permission_code):
        """
        检查用户是否拥有特定权限
        """
        if self.is_superuser:
            return True
        return permission_code in self.get_user_permissions()

    def get_role_names(self):
        """
        获取用户的所有角色名称
        """
        return list(self.roles.filter(is_active=True).values_list('name', flat=True))

    def get_avatar_url(self):
        """
        获取用户头像URL
        如果没有头像则返回None
        """
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return None

    def delete_avatar(self):
        """
        删除用户头像文件
        """
        if self.avatar:
            # 删除文件系统中的文件
            if os.path.isfile(self.avatar.path):
                os.remove(self.avatar.path)
            # 清空数据库字段
            self.avatar = None
            self.save(update_fields=['avatar'])
