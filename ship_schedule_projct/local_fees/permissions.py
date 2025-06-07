"""
local_fees 应用的权限系统
适配现有的权限架构，不修改已上线的代码
"""
from rest_framework import permissions


class LocalFeeViewPermission(permissions.BasePermission):
    """
    本地费率查看权限
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
            
        return request.user.has_permission('local_fee.view')


class LocalFeeEditPermission(permissions.BasePermission):
    """
    本地费率编辑权限
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
            
        return request.user.has_permission('local_fee.edit')


class LocalFeeDeletePermission(permissions.BasePermission):
    """
    本地费率删除权限
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
            
        return request.user.has_permission('local_fee.delete')


class LocalFeeAdminPermission(permissions.BasePermission):
    """
    本地费率管理权限
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
            
        return request.user.has_permission('local_fee.admin')


# 兼容性别名
LocalFeesAdminPermission = LocalFeeAdminPermission
