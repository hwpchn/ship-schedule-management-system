"""
自定义权限类和装饰器
用于实现细粒度的权限控制
"""
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from functools import wraps


class HasPermission(permissions.BasePermission):
    """
    自定义权限类
    检查用户是否拥有特定权限
    """
    permission_required = None

    def __init__(self, permission_code=None):
        """
        初始化权限类

        Args:
            permission_code (str): 需要检查的权限代码
        """
        if permission_code:
            self.permission_required = permission_code

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

        # 获取需要检查的权限代码
        permission_code = self.permission_required
        if hasattr(view, 'permission_required'):
            permission_code = view.permission_required

        # 如果没有指定权限代码，默认允许访问
        if not permission_code:
            return True

        # 检查用户是否拥有指定权限
        return request.user.has_permission(permission_code)

    def has_object_permission(self, request, view, obj):
        """
        检查用户是否有权限访问特定对象

        Args:
            request: HTTP请求对象
            view: 视图对象
            obj: 要访问的对象

        Returns:
            bool: 是否有权限
        """
        return self.has_permission(request, view)


def permission_required(permission_code):
    """
    权限检查装饰器
    用于在视图方法上检查权限

    Args:
        permission_code (str): 需要检查的权限代码

    Returns:
        function: 装饰器函数
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # 检查用户是否已认证
            if not hasattr(request, 'user') or not request.user.is_authenticated:
                return Response(
                    {'detail': '认证信息未提供'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # 超级管理员拥有所有权限
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # 检查用户权限
            if not request.user.has_permission(permission_code):
                return Response(
                    {'detail': f'您没有权限执行此操作，需要权限: {permission_code}'},
                    status=status.HTTP_403_FORBIDDEN
                )

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


class RoleBasedPermission(permissions.BasePermission):
    """
    基于角色的权限类
    检查用户是否拥有特定角色
    """
    role_required = None

    def __init__(self, role_name=None):
        """
        初始化权限类

        Args:
            role_name (str): 需要检查的角色名称
        """
        if role_name:
            self.role_required = role_name

    def has_permission(self, request, view):
        """
        检查用户是否拥有特定角色

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

        # 获取需要检查的角色名称
        role_name = self.role_required
        if hasattr(view, 'role_required'):
            role_name = view.role_required

        # 如果没有指定角色名称，默认允许访问
        if not role_name:
            return True

        # 检查用户是否拥有指定角色
        user_roles = request.user.get_role_names()
        return role_name in user_roles


class IsOwnerOrHasPermission(permissions.BasePermission):
    """
    对象所有者或有权限的用户可以访问
    """
    permission_required = None

    def __init__(self, permission_code=None):
        if permission_code:
            self.permission_required = permission_code

    def has_object_permission(self, request, view, obj):
        """
        检查对象权限
        """
        # 超级管理员拥有所有权限
        if request.user.is_superuser:
            return True

        # 如果对象有owner字段，检查是否为对象所有者
        if hasattr(obj, 'owner') and obj.owner == request.user:
            return True

        # 如果对象就是用户本身
        if obj == request.user:
            return True

        # 检查是否有相应权限
        permission_code = self.permission_required
        if hasattr(view, 'permission_required'):
            permission_code = view.permission_required

        if permission_code:
            return request.user.has_permission(permission_code)

        return False


def get_permission_map():
    """
    获取权限映射表
    定义各个操作对应的权限代码

    权限映射说明：
    - 左侧为API中使用的权限键名
    - 右侧为数据库中实际存储的权限代码
    - 普通业务用户通常只需要 list、detail 类权限
    - 管理员用户需要 create、update、delete 类权限

    Returns:
        dict: 权限映射表
    """
    return {
        # 用户管理权限 - 仅管理员使用
        'user_list': 'user.list',                    # 查看用户列表
        'user_detail': 'user.detail',                # 查看用户详情
        'user_create': 'user.create',                # 创建新用户
        'user_update': 'user.update',                # 修改用户信息
        'user_delete': 'user.delete',                # 删除用户

        # 角色管理权限 - 仅管理员使用
        'role_list': 'role.list',                    # 查看角色列表
        'role_detail': 'role.detail',                # 查看角色详情
        'role_create': 'role.create',                # 创建新角色
        'role_update': 'role.update',                # 修改角色信息
        'role_delete': 'role.delete',                # 删除角色

        # 权限管理 - 仅管理员使用
        'permission_list': 'permission.list',        # 查看权限列表
        'permission_detail': 'permission.detail',    # 查看权限详情

        # 用户角色分配 - 仅管理员使用
        'user_role_view': 'user.role.view',          # 查看用户角色
        'user_role_assign': 'user.role.assign',      # 分配用户角色
        'user_role_remove': 'user.role.remove',      # 移除用户角色

        # 船期管理权限 - 管理员使用，未来扩展
        'vessel_schedule_list': 'vessel_schedule.list',      # 查看船期列表（管理端）
        'vessel_schedule_detail': 'vessel_schedule.detail',  # 查看船期详情（管理端）
        'vessel_schedule_create': 'vessel_schedule.create',  # 创建船期
        'vessel_schedule_update': 'vessel_schedule.update',  # 修改船期
        'vessel_schedule_delete': 'vessel_schedule.delete',  # 删除船期

        # 船期查询权限 - 前台API专用，业务用户使用
        'vessel_schedule_query': 'vessel_schedule_list',  # 前台船期查询API专用权限

        # 船舶额外信息管理权限
        'vessel_info_list': 'vessel_info.list',      # 查看船舶信息列表
        'vessel_info_detail': 'vessel_info.detail',  # 查看船舶信息详情
        'vessel_info_create': 'vessel_info.create',  # 创建船舶信息
        'vessel_info_update': 'vessel_info.update',  # 修改船舶信息
        'vessel_info_delete': 'vessel_info.delete',  # 删除船舶信息

        # 本地费用管理权限 - 新的简化权限
        'local_fee_list': 'local_fee.list',          # 查看本地费用列表
        'local_fee_detail': 'local_fee.detail',      # 查看本地费用详情
        'local_fee_create': 'local_fee.create',      # 创建本地费用
        'local_fee_update': 'local_fee.update',      # 修改本地费用
        'local_fee_delete': 'local_fee.delete',      # 删除本地费用
        'local_fee_query': 'local_fee.query',        # 查询本地费用（前台API）
    }