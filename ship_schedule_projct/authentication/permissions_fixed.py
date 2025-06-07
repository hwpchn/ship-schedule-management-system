"""
修复后的自定义权限类和装饰器
用于实现细粒度的权限控制
"""
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from functools import wraps


class HasPermission(permissions.BasePermission):
    """
    自定义权限类 - 修复版
    使用类属性而不是初始化参数来避免DRF实例化问题
    """
    
    def has_permission(self, request, view):
        """
        检查用户是否有权限访问视图
        
        Args:
            request: HTTP请求对象
            view: 视图对象
            
        Returns:
            bool: 是否有权限
        """
        # 如果用户未认证，拒绝访问
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 超级管理员拥有所有权限
        if request.user.is_superuser:
            return True
        
        # 从视图获取权限代码
        permission_code = getattr(view, 'permission_required', None)
        
        # 如果没有指定权限代码，默认允许访问
        if not permission_code:
            return True
        
        # 检查用户是否拥有指定权限
        return request.user.has_permission(permission_code)


# 创建具体的权限类，每个权限一个类
class LocalFeeViewPermission(permissions.BasePermission):
    """查看本地费用权限"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.has_permission('local_fee.view')


class LocalFeeAddPermission(permissions.BasePermission):
    """添加本地费用权限"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.has_permission('local_fee.add')


class LocalFeeChangePermission(permissions.BasePermission):
    """修改本地费用权限"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.has_permission('local_fee.change')


class LocalFeeDeletePermission(permissions.BasePermission):
    """删除本地费用权限"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.has_permission('local_fee.delete')


def require_permission(permission_code):
    """
    权限装饰器
    
    Args:
        permission_code (str): 需要的权限代码
        
    Returns:
        function: 装饰器函数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            # 检查用户是否认证
            if not request.user or not request.user.is_authenticated:
                return Response(
                    {'error': '未认证用户'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # 超级管理员拥有所有权限
            if request.user.is_superuser:
                return func(self, request, *args, **kwargs)
            
            # 检查用户权限
            if not request.user.has_permission(permission_code):
                return Response(
                    {'error': f'缺少权限: {permission_code}'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            return func(self, request, *args, **kwargs)
        return wrapper
    return decorator


# 便捷的权限装饰器
require_view_permission = require_permission('local_fee.view')
require_add_permission = require_permission('local_fee.add')
require_change_permission = require_permission('local_fee.change')
require_delete_permission = require_permission('local_fee.delete')
