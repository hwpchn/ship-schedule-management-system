"""
自定义用户管理器
用于创建和管理邮箱认证的用户
"""
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    自定义用户管理器
    使用邮箱代替用户名创建用户
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """
        创建普通用户
        
        Args:
            email (str): 用户邮箱
            password (str): 用户密码
            **extra_fields: 其他用户字段
            
        Returns:
            User: 创建的用户实例
            
        Raises:
            ValueError: 如果邮箱为空
        """
        if not email:
            raise ValueError(_('邮箱地址不能为空'))
        
        # 规范化邮箱地址
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        
        # 设置密码（会自动加密）
        user.set_password(password)
        user.save(using=self._db)
        
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        创建超级用户
        
        Args:
            email (str): 管理员邮箱
            password (str): 管理员密码
            **extra_fields: 其他用户字段
            
        Returns:
            User: 创建的超级用户实例
        """
        # 设置超级用户默认权限
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        # 验证权限设置
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('超级用户必须设置 is_staff=True'))
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('超级用户必须设置 is_superuser=True'))
        
        return self.create_user(email, password, **extra_fields) 