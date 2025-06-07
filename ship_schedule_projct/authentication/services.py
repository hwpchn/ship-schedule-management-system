"""
认证服务层
处理用户认证、权限管理等业务逻辑
"""
import logging
from typing import Dict, List, Optional, Tuple
from django.contrib.auth import authenticate
from django.db import transaction
from django.core.cache import cache
from django.utils import timezone

from .models import User, Role, Permission
from ship_schedule.utils import CacheHelper

logger = logging.getLogger(__name__)


class AuthService:
    """
    认证服务类
    处理用户登录、注册等认证相关业务逻辑
    """
    
    @staticmethod
    def authenticate_user(email: str, password: str) -> Tuple[bool, str, Optional[User]]:
        """
        用户认证
        
        Args:
            email: 邮箱
            password: 密码
            
        Returns:
            Tuple[bool, str, Optional[User]]: (是否成功, 消息, 用户对象)
        """
        try:
            # 基础验证
            if not email or not password:
                return False, "邮箱和密码不能为空", None
            
            # 尝试认证
            user = authenticate(email=email, password=password)
            if not user:
                logger.warning(f"用户认证失败: {email}")
                return False, "邮箱或密码错误", None
            
            if not user.is_active:
                return False, "账户已被禁用", None
            
            # 更新最后登录时间
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            logger.info(f"用户登录成功: {email}")
            return True, "登录成功", user
            
        except Exception as e:
            logger.error(f"用户认证异常: {e}")
            return False, "认证服务异常", None
    
    @staticmethod
    def register_user(email: str, password: str, **extra_fields) -> Tuple[bool, str, Optional[User]]:
        """
        用户注册
        
        Args:
            email: 邮箱
            password: 密码
            **extra_fields: 其他用户字段
            
        Returns:
            Tuple[bool, str, Optional[User]]: (是否成功, 消息, 用户对象)
        """
        try:
            # 检查邮箱是否已存在
            if User.objects.filter(email=email).exists():
                return False, "该邮箱已被注册", None
            
            # 创建用户
            with transaction.atomic():
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    **extra_fields
                )
                
                # 分配默认角色（如果存在）
                default_role = Role.objects.filter(name='普通用户').first()
                if default_role:
                    user.roles.add(default_role)
                
                logger.info(f"用户注册成功: {email}")
                return True, "注册成功", user
                
        except Exception as e:
            logger.error(f"用户注册异常: {e}")
            return False, f"注册失败: {str(e)}", None


class PermissionService:
    """
    权限服务类
    处理权限检查、角色管理等业务逻辑
    """
    
    @staticmethod
    def check_user_permission(user: User, permission_code: str) -> bool:
        """
        检查用户权限
        
        Args:
            user: 用户对象
            permission_code: 权限代码
            
        Returns:
            bool: 是否有权限
        """
        if not user or not user.is_authenticated:
            return False
        
        # 超级管理员拥有所有权限
        if user.is_superuser:
            return True
        
        # 检查缓存
        cache_key = f"user_permission:{user.id}:{permission_code}"
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # 检查权限
        has_permission = user.has_permission(permission_code)
        
        # 缓存结果5分钟
        cache.set(cache_key, has_permission, 300)
        
        return has_permission
    
    @staticmethod
    def get_user_permissions(user: User) -> List[str]:
        """
        获取用户所有权限
        
        Args:
            user: 用户对象
            
        Returns:
            List[str]: 权限代码列表
        """
        if not user or not user.is_authenticated:
            return []
        
        # 检查缓存
        cache_key = f"user_permissions:{user.id}"
        cached_permissions = cache.get(cache_key)
        if cached_permissions is not None:
            return cached_permissions
        
        # 获取权限
        permissions = []
        
        if user.is_superuser:
            # 超级管理员拥有所有权限
            permissions = list(Permission.objects.values_list('code', flat=True))
        else:
            # 通过角色获取权限
            permissions = list(
                Permission.objects.filter(
                    roles__users=user
                ).distinct().values_list('code', flat=True)
            )
        
        # 缓存结果5分钟
        cache.set(cache_key, permissions, 300)
        
        return permissions
    
    @staticmethod
    def assign_user_roles(user: User, role_ids: List[int]) -> Tuple[bool, str]:
        """
        分配用户角色
        
        Args:
            user: 用户对象
            role_ids: 角色ID列表
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            with transaction.atomic():
                # 清除现有角色
                user.roles.clear()
                
                # 分配新角色
                roles = Role.objects.filter(id__in=role_ids)
                user.roles.set(roles)
                
                # 清除用户权限缓存
                PermissionService._clear_user_permission_cache(user)
                
                logger.info(f"用户角色分配成功: {user.email}, 角色: {[r.name for r in roles]}")
                return True, "角色分配成功"
                
        except Exception as e:
            logger.error(f"分配用户角色失败: {e}")
            return False, f"角色分配失败: {str(e)}"
    
    @staticmethod
    def _clear_user_permission_cache(user: User):
        """
        清除用户权限相关缓存
        
        Args:
            user: 用户对象
        """
        try:
            # 清除用户权限列表缓存
            cache.delete(f"user_permissions:{user.id}")
            
            # 清除具体权限检查缓存
            CacheHelper.delete_pattern(f"user_permission:{user.id}:*")
            
        except Exception as e:
            logger.warning(f"清除用户权限缓存失败: {e}")


class RoleService:
    """
    角色服务类
    处理角色管理相关业务逻辑
    """
    
    @staticmethod
    def create_role(name: str, description: str = "", permission_ids: List[int] = None) -> Tuple[bool, str, Optional[Role]]:
        """
        创建角色
        
        Args:
            name: 角色名称
            description: 角色描述
            permission_ids: 权限ID列表
            
        Returns:
            Tuple[bool, str, Optional[Role]]: (是否成功, 消息, 角色对象)
        """
        try:
            # 检查角色名是否已存在
            if Role.objects.filter(name=name).exists():
                return False, "角色名已存在", None
            
            with transaction.atomic():
                # 创建角色
                role = Role.objects.create(
                    name=name,
                    description=description
                )
                
                # 分配权限
                if permission_ids:
                    permissions = Permission.objects.filter(id__in=permission_ids)
                    role.permissions.set(permissions)
                
                logger.info(f"角色创建成功: {name}")
                return True, "角色创建成功", role
                
        except Exception as e:
            logger.error(f"创建角色失败: {e}")
            return False, f"创建角色失败: {str(e)}", None
    
    @staticmethod
    def update_role_permissions(role: Role, permission_ids: List[int]) -> Tuple[bool, str]:
        """
        更新角色权限
        
        Args:
            role: 角色对象
            permission_ids: 权限ID列表
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            with transaction.atomic():
                # 更新权限
                permissions = Permission.objects.filter(id__in=permission_ids)
                role.permissions.set(permissions)
                
                # 清除相关用户的权限缓存
                for user in role.users.all():
                    PermissionService._clear_user_permission_cache(user)
                
                logger.info(f"角色权限更新成功: {role.name}")
                return True, "权限更新成功"
                
        except Exception as e:
            logger.error(f"更新角色权限失败: {e}")
            return False, f"更新权限失败: {str(e)}"
    
    @staticmethod
    def delete_role(role: Role) -> Tuple[bool, str]:
        """
        删除角色
        
        Args:
            role: 角色对象
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            # 检查是否有用户在使用此角色
            if role.users.exists():
                return False, f"无法删除角色，还有 {role.users.count()} 个用户在使用此角色"
            
            with transaction.atomic():
                role_name = role.name
                role.delete()
                
                logger.info(f"角色删除成功: {role_name}")
                return True, "角色删除成功"
                
        except Exception as e:
            logger.error(f"删除角色失败: {e}")
            return False, f"删除角色失败: {str(e)}"


# 导出服务类
__all__ = [
    'AuthService',
    'PermissionService', 
    'RoleService'
]