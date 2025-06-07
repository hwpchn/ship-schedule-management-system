"""
认证应用的URL配置
定义用户认证相关的API端点
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView,
    login_view,
    logout_view,
    UserProfileView,
    user_info_view,
    PermissionViewSet,
    RoleViewSet,
    UserRoleViewSet,
    UserManagementViewSet,
    user_permissions_view,
    users_list_view,
    avatar_management_view
)

app_name = 'authentication'

# 创建路由器用于ViewSet
router = DefaultRouter()
router.register(r'permissions', PermissionViewSet, basename='permission')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'users-management', UserManagementViewSet, basename='user-management')

urlpatterns = [
    # 用户注册
    path('register/', UserRegistrationView.as_view(), name='register'),

    # 用户登录
    path('login/', login_view, name='login'),

    # 用户登出
    path('logout/', logout_view, name='logout'),

    # JWT token刷新
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 用户信息管理
    path('user/', UserProfileView.as_view(), name='user_profile'),

    # 获取用户信息（简化接口）
    path('me/', user_info_view, name='user_info'),

    # 获取当前用户权限
    path('me/permissions/', user_permissions_view, name='user_permissions'),

    # 用户头像管理
    path('me/avatar/', avatar_management_view, name='avatar_management'),

    # 用户列表（需要权限）
    path('users/', users_list_view, name='users_list'),

    # 用户角色管理
    path('users/<int:pk>/roles/', UserRoleViewSet.as_view({
        'get': 'retrieve',
        'post': 'create',
        'put': 'update'
    }), name='user_roles'),

    path('users/<int:pk>/roles/<int:role_pk>/', UserRoleViewSet.as_view({
        'delete': 'destroy'
    }), name='user_role_remove'),

    # 权限和角色的ViewSet路由
    path('', include(router.urls)),
]