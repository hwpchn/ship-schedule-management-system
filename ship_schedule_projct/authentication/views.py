"""
用户认证相关的视图
包括注册、登录和用户信息管理
"""
from rest_framework import status, generics, permissions, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.db import models
from .models import User, Permission, Role
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserUpdateSerializer,
    PermissionSerializer,
    RoleListSerializer,
    RoleDetailSerializer,
    UserRoleSerializer,
    UserRoleAssignSerializer,
    UserPermissionSerializer,
    AvatarUploadSerializer
)
from .permissions import HasPermission, permission_required, get_permission_map


class UserRegistrationView(generics.CreateAPIView):
    """
    用户注册视图
    允许新用户通过邮箱和密码注册账户
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        """
        处理用户注册

        Args:
            request: HTTP请求对象

        Returns:
            Response: 包含注册结果的响应
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 创建用户
        user = serializer.save()

        # 生成JWT token
        refresh = RefreshToken.for_user(user)

        # 返回用户信息和token
        user_serializer = UserSerializer(user)

        return Response({
            'message': '注册成功',
            'user': user_serializer.data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    用户登录视图
    验证用户凭据并返回JWT token

    Args:
        request: HTTP请求对象

    Returns:
        Response: 包含登录结果的响应
    """
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = serializer.validated_data['user']

    # 生成JWT token
    refresh = RefreshToken.for_user(user)

    # 更新最后登录时间
    user.save(update_fields=['last_login'])

    # 返回用户信息和token
    user_serializer = UserSerializer(user)

    return Response({
        'message': '登录成功',
        'user': user_serializer.data,
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    }, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    用户信息视图
    允许用户查看和更新个人信息
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """返回当前登录用户"""
        return self.request.user

    def get_serializer_class(self):
        """根据请求方法返回不同的序列化器"""
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return UserUpdateSerializer
        return UserSerializer

    def update(self, request, *args, **kwargs):
        """
        更新用户信息

        Args:
            request: HTTP请求对象

        Returns:
            Response: 包含更新结果的响应
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # 保存更新
        user = serializer.save()

        # 返回更新后的用户信息
        user_serializer = UserSerializer(user)

        return Response({
            'message': '用户信息更新成功',
            'user': user_serializer.data
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    用户登出视图
    将refresh token加入黑名单

    Args:
        request: HTTP请求对象

    Returns:
        Response: 登出结果响应
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()

        return Response({
            'message': '登出成功'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'error': '登出失败',
            'detail': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_info_view(request):
    """
    获取当前用户信息视图
    返回当前登录用户的详细信息

    Args:
        request: HTTP请求对象

    Returns:
        Response: 用户信息响应
    """
    serializer = UserSerializer(request.user)
    return Response({
        'user': serializer.data
    }, status=status.HTTP_200_OK)


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    权限视图集
    提供权限的查看功能
    """
    queryset = Permission.objects.all().order_by('category', 'code')
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """检查权限"""
        if self.request.user.is_superuser:
            return [permissions.AllowAny()]
        return [HasPermission('permission.list')]

    def list(self, request, *args, **kwargs):
        """
        获取权限列表

        Returns:
            Response: 权限列表响应
        """
        queryset = self.filter_queryset(self.get_queryset())

        # 按分类分组权限
        permissions_by_category = {}
        for permission in queryset:
            category = permission.category
            if category not in permissions_by_category:
                permissions_by_category[category] = []
            permissions_by_category[category].append(PermissionSerializer(permission).data)

        return Response({
            'permissions': permissions_by_category,
            'total': queryset.count()
        }, status=status.HTTP_200_OK)


class RoleViewSet(viewsets.ModelViewSet):
    """
    角色视图集
    提供角色的完整CRUD功能
    """
    queryset = Role.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """根据动作返回不同的序列化器"""
        if self.action in ['retrieve', 'create', 'update', 'partial_update']:
            return RoleDetailSerializer
        return RoleListSerializer

    def get_permissions(self):
        """根据不同动作设置不同权限"""
        permission_map = get_permission_map()

        if self.action == 'list':
            self.permission_classes = [lambda: HasPermission(permission_map['role_list'])]
        elif self.action == 'retrieve':
            self.permission_classes = [lambda: HasPermission(permission_map['role_detail'])]
        elif self.action == 'create':
            self.permission_classes = [lambda: HasPermission(permission_map['role_create'])]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [lambda: HasPermission(permission_map['role_update'])]
        elif self.action == 'destroy':
            self.permission_classes = [lambda: HasPermission(permission_map['role_delete'])]

        return [permission() for permission in self.permission_classes]

    def create(self, request, *args, **kwargs):
        """
        创建角色
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = serializer.save()

        return Response({
            'message': '角色创建成功',
            'role': RoleDetailSerializer(role).data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        更新角色
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        role = serializer.save()

        return Response({
            'message': '角色更新成功',
            'role': RoleDetailSerializer(role).data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        删除角色
        """
        instance = self.get_object()

        # 检查是否有用户使用该角色
        if instance.user_set.exists():
            return Response({
                'error': '无法删除该角色，仍有用户使用该角色'
            }, status=status.HTTP_400_BAD_REQUEST)

        instance.delete()
        return Response({
            'message': '角色删除成功'
        }, status=status.HTTP_200_OK)


class UserRoleViewSet(viewsets.ViewSet):
    """
    用户角色管理视图集
    提供用户角色的查看、分配、修改和移除功能
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """根据不同动作设置不同权限"""
        permission_map = get_permission_map()

        if self.action in ['retrieve', 'list']:
            self.permission_classes = [lambda: HasPermission(permission_map['user_role_view'])]
        elif self.action in ['create', 'update']:
            self.permission_classes = [lambda: HasPermission(permission_map['user_role_assign'])]
        elif self.action == 'destroy':
            self.permission_classes = [lambda: HasPermission(permission_map['user_role_remove'])]

        return [permission() for permission in self.permission_classes]

    def retrieve(self, request, pk=None):
        """
        获取用户的角色信息

        Args:
            pk: 用户ID

        Returns:
            Response: 用户角色信息
        """
        user = get_object_or_404(User, pk=pk)
        serializer = UserRoleSerializer(user)
        return Response({
            'user_id': user.id,
            'roles': serializer.data['roles']
        }, status=status.HTTP_200_OK)

    def create(self, request, pk=None):
        """
        给用户分配角色

        Args:
            pk: 用户ID

        Returns:
            Response: 分配结果
        """
        user = get_object_or_404(User, pk=pk)
        serializer = UserRoleAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        role_ids = serializer.validated_data['roles']
        roles = Role.objects.filter(id__in=role_ids, is_active=True)

        # 分配角色给用户
        user.roles.set(roles)

        # 返回用户角色信息
        user_serializer = UserRoleSerializer(user)
        return Response({
            'message': '角色分配成功',
            'user_id': user.id,
            'roles': user_serializer.data['roles']
        }, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        """
        修改用户角色
        """
        return self.create(request, pk)

    def destroy(self, request, pk=None, role_pk=None):
        """
        移除用户的特定角色

        Args:
            pk: 用户ID
            role_pk: 角色ID

        Returns:
            Response: 移除结果
        """
        user = get_object_or_404(User, pk=pk)
        role = get_object_or_404(Role, pk=role_pk)

        # 从用户角色中移除指定角色
        user.roles.remove(role)

        return Response({
            'message': f'成功移除用户 {user.email} 的角色 {role.name}'
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_permissions_view(request):
    """
    获取当前用户的权限信息

    Args:
        request: HTTP请求对象

    Returns:
        Response: 用户权限信息
    """
    user = request.user

    # 获取用户权限
    user_permissions = user.get_user_permissions()
    user_roles = user.get_role_names()

    serializer = UserPermissionSerializer({
        'permissions': user_permissions,
        'roles': user_roles
    })

    return Response(serializer.data, status=status.HTTP_200_OK)


class UserManagementViewSet(viewsets.ModelViewSet):
    """
    用户管理视图集
    提供用户的完整CRUD功能
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """根据不同动作设置不同权限"""
        permission_map = get_permission_map()

        if self.action == 'list':
            self.permission_classes = [lambda: HasPermission(permission_map['user_list'])]
        elif self.action == 'retrieve':
            self.permission_classes = [lambda: HasPermission(permission_map['user_detail'])]
        elif self.action == 'create':
            self.permission_classes = [lambda: HasPermission(permission_map['user_create'])]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [lambda: HasPermission(permission_map['user_update'])]
        elif self.action == 'destroy':
            self.permission_classes = [lambda: HasPermission(permission_map['user_delete'])]

        return [permission() for permission in self.permission_classes]

    def get_serializer_class(self):
        """根据动作返回不同的序列化器"""
        if self.action == 'create':
            return UserRegistrationSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    def list(self, request, *args, **kwargs):
        """
        获取用户列表
        支持搜索和分页
        """
        queryset = self.get_queryset()

        # 搜索功能
        search = request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                models.Q(email__icontains=search) |
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search)
            )

        # 活跃状态过滤
        is_active = request.GET.get('is_active', '')
        if is_active:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        # 分页处理
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size

        users_page = queryset[start:end]
        serializer = self.get_serializer(users_page, many=True)

        return Response({
            'users': serializer.data,
            'total': queryset.count(),
            'page': page,
            'page_size': page_size
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        创建新用户
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 创建用户
        user = serializer.save()

        # 返回用户信息
        user_serializer = UserSerializer(user)

        return Response({
            'message': '用户创建成功',
            'user': user_serializer.data
        }, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        """
        获取用户详情
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'user': serializer.data
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """
        更新用户信息
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # 保存更新
        user = serializer.save()

        # 返回更新后的用户信息
        user_serializer = UserSerializer(user)

        return Response({
            'message': '用户信息更新成功',
            'user': user_serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        删除用户
        """
        instance = self.get_object()

        # 防止删除超级管理员
        if instance.is_superuser:
            return Response({
                'error': '无法删除超级管理员账户'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 防止用户删除自己
        if instance.id == request.user.id:
            return Response({
                'error': '无法删除自己的账户'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 软删除：设置为非活跃状态
        instance.is_active = False
        instance.save()

        return Response({
            'message': f'用户 {instance.email} 已被删除'
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@permission_required('user.list')
def users_list_view(request):
    """
    获取用户列表（保持向后兼容）
    需要用户列表查看权限

    Args:
        request: HTTP请求对象

    Returns:
        Response: 用户列表
    """
    users = User.objects.all().order_by('-date_joined')

    # 分页处理（简单实现）
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size

    users_page = users[start:end]
    serializer = UserSerializer(users_page, many=True)

    return Response({
        'users': serializer.data,
        'total': users.count(),
        'page': page,
        'page_size': page_size
    }, status=status.HTTP_200_OK)


@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def avatar_management_view(request):
    """
    用户头像管理视图
    POST: 上传头像
    DELETE: 删除头像

    Args:
        request: HTTP请求对象

    Returns:
        Response: 操作结果
    """
    try:
        if request.method == 'POST':
            # 上传头像
            serializer = AvatarUploadSerializer(data=request.data)
            if serializer.is_valid():
                # 保存头像
                user = serializer.save(request.user)

                # 返回更新后的用户信息
                user_serializer = UserSerializer(user)

                return Response({
                    'success': True,
                    'message': '头像上传成功',
                    'data': {
                        'avatar_url': user.get_avatar_url(),
                        'user': user_serializer.data
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': '头像上传失败',
                    'data': None,
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            # 删除头像
            user = request.user

            if not user.avatar:
                return Response({
                    'success': False,
                    'message': '用户暂无头像',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)

            # 删除头像
            user.delete_avatar()

            # 返回更新后的用户信息
            user_serializer = UserSerializer(user)

            return Response({
                'success': True,
                'message': '头像删除成功',
                'data': {
                    'user': user_serializer.data
                }
            }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'头像操作失败: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
