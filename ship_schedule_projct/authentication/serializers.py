"""
用户认证相关的序列化器
包括注册、登录和用户信息序列化
"""
import os
from PIL import Image
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.files.uploadedfile import InMemoryUploadedFile
from .models import User, Permission, Role


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    用户注册序列化器
    处理用户注册数据的验证和序列化
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text='密码，至少8位'
    )
    password_confirm = serializers.CharField(
        write_only=True,
        help_text='确认密码，必须与密码一致'
    )

    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirm', 'first_name', 'last_name')
        extra_kwargs = {
            'email': {'help_text': '邮箱地址，用于登录'},
            'first_name': {'help_text': '名字（可选）'},
            'last_name': {'help_text': '姓氏（可选）'},
        }

    def validate(self, attrs):
        """
        验证注册数据

        Args:
            attrs (dict): 待验证的数据

        Returns:
            dict: 验证后的数据

        Raises:
            serializers.ValidationError: 验证失败时抛出
        """
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')

        # 验证两次密码是否一致
        if password != password_confirm:
            raise serializers.ValidationError({'password_confirm': '两次输入的密码不一致'})

        # 使用Django内置密码验证器
        try:
            validate_password(password)
        except Exception as e:
            raise serializers.ValidationError({'password': list(e.messages)})

        return attrs

    def create(self, validated_data):
        """
        创建新用户

        Args:
            validated_data (dict): 验证后的数据

        Returns:
            User: 创建的用户实例
        """
        # 移除确认密码字段
        validated_data.pop('password_confirm')

        # 创建用户
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    用户登录序列化器
    验证用户登录凭据
    """
    email = serializers.EmailField(
        help_text='用户邮箱地址'
    )
    password = serializers.CharField(
        write_only=True,
        help_text='用户密码'
    )

    def validate(self, attrs):
        """
        验证登录凭据

        Args:
            attrs (dict): 登录数据

        Returns:
            dict: 包含用户实例的验证数据

        Raises:
            serializers.ValidationError: 登录失败时抛出
        """
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            # 使用Django内置认证系统验证用户
            user = authenticate(email=email, password=password)

            if not user:
                raise serializers.ValidationError('邮箱或密码错误')

            if not user.is_active:
                raise serializers.ValidationError('用户账户已被禁用')

            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('必须提供邮箱和密码')


class UserSerializer(serializers.ModelSerializer):
    """
    用户信息序列化器
    用于序列化用户基本信息
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    short_name = serializers.CharField(source='get_short_name', read_only=True)
    avatar_url = serializers.CharField(source='get_avatar_url', read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name',
            'full_name', 'short_name', 'avatar', 'avatar_url',
            'is_superuser', 'is_staff', 'is_active', 'date_joined', 'last_login'
        )
        read_only_fields = ('id', 'is_superuser', 'is_staff', 'is_active', 'date_joined', 'last_login', 'avatar_url')


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    用户信息更新序列化器
    用于更新用户基本信息
    """
    class Meta:
        model = User
        fields = ('first_name', 'last_name')

    def update(self, instance, validated_data):
        """
        更新用户信息

        Args:
            instance (User): 用户实例
            validated_data (dict): 验证后的数据

        Returns:
            User: 更新后的用户实例
        """
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()
        return instance


class PermissionSerializer(serializers.ModelSerializer):
    """
    权限序列化器
    用于权限数据的序列化
    """
    class Meta:
        model = Permission
        fields = ('id', 'code', 'name', 'description', 'category', 'created_at')
        read_only_fields = ('id', 'created_at')


class RoleListSerializer(serializers.ModelSerializer):
    """
    角色列表序列化器
    用于角色列表显示
    """
    permission_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ('id', 'name', 'description', 'is_active', 'permission_count', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_permission_count(self, obj):
        """获取角色拥有的权限数量"""
        return obj.permissions.count()


class RoleDetailSerializer(serializers.ModelSerializer):
    """
    角色详情序列化器
    用于角色详情显示和编辑
    """
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_codes = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        help_text='权限代码列表'
    )

    class Meta:
        model = Role
        fields = ('id', 'name', 'description', 'is_active', 'permissions', 'permission_codes', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_permission_codes(self, value):
        """
        验证权限代码
        """
        if value:
            # 检查权限代码是否存在
            existing_codes = Permission.objects.filter(code__in=value).values_list('code', flat=True)
            invalid_codes = set(value) - set(existing_codes)
            if invalid_codes:
                raise serializers.ValidationError(f'以下权限代码不存在: {", ".join(invalid_codes)}')
        return value

    def create(self, validated_data):
        """
        创建角色
        """
        permission_codes = validated_data.pop('permission_codes', [])
        role = Role.objects.create(**validated_data)

        if permission_codes:
            permissions = Permission.objects.filter(code__in=permission_codes)
            role.permissions.set(permissions)

        return role

    def update(self, instance, validated_data):
        """
        更新角色
        """
        permission_codes = validated_data.pop('permission_codes', None)

        # 更新基本字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 更新权限
        if permission_codes is not None:
            permissions = Permission.objects.filter(code__in=permission_codes)
            instance.permissions.set(permissions)

        return instance


class UserRoleSerializer(serializers.ModelSerializer):
    """
    用户角色序列化器
    用于显示用户拥有的角色
    """
    roles = RoleListSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'roles')
        read_only_fields = ('id', 'email', 'first_name', 'last_name')


class UserRoleAssignSerializer(serializers.Serializer):
    """
    用户角色分配序列化器
    用于分配角色给用户
    """
    roles = serializers.ListField(
        child=serializers.IntegerField(),
        help_text='角色ID列表'
    )

    def validate_roles(self, value):
        """
        验证角色ID
        """
        if value:
            # 检查角色是否存在且激活
            existing_roles = Role.objects.filter(id__in=value, is_active=True)
            existing_ids = list(existing_roles.values_list('id', flat=True))
            invalid_ids = set(value) - set(existing_ids)
            if invalid_ids:
                raise serializers.ValidationError(f'以下角色ID不存在或未激活: {", ".join(map(str, invalid_ids))}')
        return value


class UserPermissionSerializer(serializers.Serializer):
    """
    用户权限序列化器
    用于返回用户的所有权限
    """
    permissions = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
        help_text='用户拥有的权限代码列表'
    )
    roles = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
        help_text='用户拥有的角色名称列表'
    )


class AvatarUploadSerializer(serializers.Serializer):
    """
    头像上传序列化器
    处理头像文件上传和验证
    """
    avatar = serializers.ImageField(
        help_text='头像图片文件，支持jpg、png、gif格式，最大5MB'
    )

    def validate_avatar(self, value):
        """
        验证头像文件 - 增强安全性
        """
        # 检查文件大小 (2.5MB - 更严格)
        max_size = 2.5 * 1024 * 1024  # 2.5MB
        if value.size > max_size:
            raise serializers.ValidationError('头像文件大小不能超过2.5MB')

        # 检查文件扩展名
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        file_extension = os.path.splitext(value.name)[1].lower()
        if file_extension not in allowed_extensions:
            raise serializers.ValidationError('不支持的文件扩展名，请上传jpg、png或gif格式的图片')

        # 检查MIME类型
        allowed_mimes = ['image/jpeg', 'image/png', 'image/gif']
        if hasattr(value, 'content_type') and value.content_type not in allowed_mimes:
            raise serializers.ValidationError('不支持的文件类型')

        # 检查文件头部magic bytes
        try:
            value.seek(0)
            header = value.read(12)
            value.seek(0)
            
            # JPEG: FF D8 FF
            # PNG: 89 50 4E 47
            # GIF: 47 49 46 38
            valid_headers = [
                b'\xff\xd8\xff',  # JPEG
                b'\x89PNG\r\n\x1a\n',  # PNG
                b'GIF87a', b'GIF89a'  # GIF
            ]
            
            if not any(header.startswith(h) for h in valid_headers):
                raise serializers.ValidationError('文件头部验证失败，可能是伪造的图片文件')
                
        except Exception as e:
            raise serializers.ValidationError('文件读取失败，请检查文件完整性')

        # 使用PIL进一步验证图片
        try:
            image = Image.open(value)
            image.verify()  # 验证图片完整性
            value.seek(0)  # 重置文件指针
            
            # 重新打开进行尺寸检查
            image = Image.open(value)
            allowed_formats = ['JPEG', 'PNG', 'GIF']
            if image.format not in allowed_formats:
                raise serializers.ValidationError('图片格式验证失败')

            # 检查图片尺寸
            max_dimension = 1920  # 降低最大尺寸
            if image.width > max_dimension or image.height > max_dimension:
                raise serializers.ValidationError(f'图片尺寸过大，最大支持{max_dimension}x{max_dimension}像素')
                
            # 检查图片模式
            if image.mode not in ['RGB', 'RGBA', 'L', 'P']:
                raise serializers.ValidationError('不支持的图片模式')

        except Exception as e:
            if isinstance(e, serializers.ValidationError):
                raise e
            raise serializers.ValidationError('图片文件验证失败，请确保文件是有效的图片')

        return value

    def save(self, user):
        """
        保存头像
        """
        avatar_file = self.validated_data['avatar']

        # 删除旧头像
        if user.avatar:
            user.delete_avatar()

        # 保存新头像
        user.avatar = avatar_file
        user.save(update_fields=['avatar'])

        return user