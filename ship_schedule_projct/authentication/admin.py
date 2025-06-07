"""
认证应用的Django管理后台配置
配置User模型在管理界面的显示和操作
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Permission, Role


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """
    权限管理界面
    """
    list_display = ('code', 'name', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('code', 'name', 'description')
    ordering = ('category', 'code')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('code', 'name', 'description', 'category')
        }),
        (_('系统信息'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def has_delete_permission(self, request, obj=None):
        """
        限制删除权限，防止系统权限被误删
        """
        if obj and obj.code.startswith('system.'):
            return False
        return super().has_delete_permission(request, obj)


class RolePermissionInline(admin.TabularInline):
    """
    角色权限内联编辑
    """
    model = Role.permissions.through
    extra = 0
    verbose_name = '权限'
    verbose_name_plural = '权限列表'


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """
    角色管理界面
    """
    list_display = ('name', 'is_active', 'permission_count', 'user_count', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('permissions',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'is_active')
        }),
        (_('权限分配'), {
            'fields': ('permissions',),
        }),
        (_('系统信息'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def permission_count(self, obj):
        """获取角色拥有的权限数量"""
        return obj.permissions.count()
    permission_count.short_description = '权限数量'
    
    def user_count(self, obj):
        """获取拥有该角色的用户数量"""
        return obj.user_set.count()
    user_count.short_description = '用户数量'
    
    def get_queryset(self, request):
        """优化查询集"""
        qs = super().get_queryset(request)
        return qs.prefetch_related('permissions', 'user_set')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    自定义用户管理界面
    基于Django内置的UserAdmin进行定制
    """
    # 列表页显示的字段
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff', 'role_list', 'date_joined')
    
    # 列表页过滤器
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'roles', 'date_joined')
    
    # 搜索字段
    search_fields = ('email', 'first_name', 'last_name')
    
    # 排序字段
    ordering = ('-date_joined',)
    
    # 只读字段
    readonly_fields = ('date_joined', 'last_login')
    
    # 水平过滤器
    filter_horizontal = ('groups', 'user_permissions', 'roles')
    
    # 详情页字段分组
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('个人信息'), {'fields': ('first_name', 'last_name')}),
        (_('角色管理'), {'fields': ('roles',)}),
        (_('权限'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('重要日期'), {'fields': ('last_login', 'date_joined')}),
    )
    
    # 添加用户页面的字段
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
        (_('个人信息'), {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name'),
        }),
        (_('角色分配'), {
            'classes': ('wide',),
            'fields': ('roles',),
        }),
        (_('权限'), {
            'classes': ('wide',),
            'fields': ('is_active', 'is_staff'),
        }),
    )
    
    def role_list(self, obj):
        """显示用户的角色列表"""
        roles = obj.roles.filter(is_active=True)
        if roles:
            return ', '.join([role.name for role in roles])
        return '无角色'
    role_list.short_description = '角色'
    
    def get_queryset(self, request):
        """
        优化查询集，减少数据库查询次数
        """
        qs = super().get_queryset(request)
        return qs.select_related().prefetch_related('groups', 'user_permissions', 'roles')
    
    def has_delete_permission(self, request, obj=None):
        """
        限制删除超级用户的权限
        """
        if obj and obj.is_superuser and not request.user.is_superuser:
            return False
        return super().has_delete_permission(request, obj)
