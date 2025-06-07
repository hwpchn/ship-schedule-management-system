"""
用户认证功能测试
包含注册、登录、用户信息管理等功能的完整测试用例
"""
import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from factory import Factory, Faker
from .models import User, Permission, Role

User = get_user_model()


class UserFactory(Factory):
    """用户工厂类，用于生成测试用户数据"""
    class Meta:
        model = User
    
    email = Faker('email')
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    is_active = True


class PermissionModelTest(TestCase):
    """权限模型测试"""
    
    def setUp(self):
        """测试前准备"""
        self.permission_data = {
            'code': 'test.permission',
            'name': '测试权限',
            'description': '这是一个测试权限',
            'category': 'test_category'
        }
    
    def test_create_permission(self):
        """测试创建权限"""
        permission = Permission.objects.create(**self.permission_data)
        
        self.assertEqual(permission.code, self.permission_data['code'])
        self.assertEqual(permission.name, self.permission_data['name'])
        self.assertEqual(permission.description, self.permission_data['description'])
        self.assertEqual(permission.category, self.permission_data['category'])
    
    def test_permission_string_representation(self):
        """测试权限字符串表示"""
        permission = Permission.objects.create(**self.permission_data)
        expected_str = f"{self.permission_data['name']} ({self.permission_data['code']})"
        self.assertEqual(str(permission), expected_str)
    
    def test_permission_unique_code(self):
        """测试权限代码唯一性"""
        Permission.objects.create(**self.permission_data)
        
        with self.assertRaises(Exception):
            Permission.objects.create(**self.permission_data)


class RoleModelTest(TestCase):
    """角色模型测试"""
    
    def setUp(self):
        """测试前准备"""
        self.role_data = {
            'name': '测试角色',
            'description': '这是一个测试角色',
            'is_active': True
        }
        self.permission1 = Permission.objects.create(
            code='test.permission1',
            name='测试权限1',
            category='test'
        )
        self.permission2 = Permission.objects.create(
            code='test.permission2',
            name='测试权限2',
            category='test'
        )
    
    def test_create_role(self):
        """测试创建角色"""
        role = Role.objects.create(**self.role_data)
        
        self.assertEqual(role.name, self.role_data['name'])
        self.assertEqual(role.description, self.role_data['description'])
        self.assertTrue(role.is_active)
    
    def test_role_string_representation(self):
        """测试角色字符串表示"""
        role = Role.objects.create(**self.role_data)
        self.assertEqual(str(role), self.role_data['name'])
    
    def test_role_permissions(self):
        """测试角色权限关联"""
        role = Role.objects.create(**self.role_data)
        role.permissions.add(self.permission1, self.permission2)
        
        permission_codes = role.get_permission_codes()
        self.assertIn('test.permission1', permission_codes)
        self.assertIn('test.permission2', permission_codes)
        self.assertEqual(len(permission_codes), 2)


class UserPermissionTest(TestCase):
    """用户权限测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword123'
        )
        self.permission1, _ = Permission.objects.get_or_create(
            code='user.list',
            defaults={
                'name': '查看用户列表',
                'category': 'user_management'
            }
        )
        self.permission2, _ = Permission.objects.get_or_create(
            code='user.create',
            defaults={
                'name': '创建用户',
                'category': 'user_management'
            }
        )
        self.role = Role.objects.create(
            name='测试角色',
            description='测试角色描述'
        )
        self.role.permissions.add(self.permission1, self.permission2)
    
    def test_user_has_permission_through_role(self):
        """测试用户通过角色获得权限"""
        self.user.roles.add(self.role)
        
        self.assertTrue(self.user.has_permission('user.list'))
        self.assertTrue(self.user.has_permission('user.create'))
        self.assertFalse(self.user.has_permission('user.delete'))
    
    def test_superuser_has_all_permissions(self):
        """测试超级用户拥有所有权限"""
        superuser = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpassword123'
        )
        
        self.assertTrue(superuser.has_permission('any.permission'))
        self.assertTrue(superuser.has_permission('user.list'))
    
    def test_user_get_permissions(self):
        """测试获取用户权限列表"""
        self.user.roles.add(self.role)
        
        permissions = self.user.get_user_permissions()
        self.assertIn('user.list', permissions)
        self.assertIn('user.create', permissions)
        self.assertEqual(len(permissions), 2)
    
    def test_user_get_role_names(self):
        """测试获取用户角色名称"""
        self.user.roles.add(self.role)
        
        role_names = self.user.get_role_names()
        self.assertIn('测试角色', role_names)
        self.assertEqual(len(role_names), 1)


class UserModelTest(TestCase):
    """用户模型测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpassword123',
            'first_name': '测试',
            'last_name': '用户'
        }
    
    def test_create_user(self):
        """测试创建普通用户"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.email, self.user_data['email'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_superuser(self):
        """测试创建超级用户"""
        admin_data = self.user_data.copy()
        admin_data['email'] = 'admin@example.com'
        
        user = User.objects.create_superuser(**admin_data)
        
        self.assertEqual(user.email, admin_data['email'])
        self.assertTrue(user.check_password(admin_data['password']))
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
    
    def test_user_string_representation(self):
        """测试用户字符串表示"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), self.user_data['email'])
    
    def test_get_full_name(self):
        """测试获取全名"""
        user = User.objects.create_user(**self.user_data)
        expected_name = f"{self.user_data['first_name']} {self.user_data['last_name']}"
        self.assertEqual(user.get_full_name(), expected_name)
    
    def test_get_short_name(self):
        """测试获取简短名称"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.get_short_name(), self.user_data['first_name'])
    
    def test_email_required(self):
        """测试邮箱必填验证"""
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='password123')


class PermissionAPITest(APITestCase):
    """权限API测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpassword123'
        )
        self.normal_user = User.objects.create_user(
            email='user@example.com',
            password='userpassword123'
        )
        
        # 创建测试权限
        self.permission1 = Permission.objects.create(
            code='test.permission1',
            name='测试权限1',
            category='test_category'
        )
        self.permission2 = Permission.objects.create(
            code='test.permission2',
            name='测试权限2',
            category='test_category'
        )
    
    def test_get_permissions_as_admin(self):
        """测试管理员获取权限列表"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('authentication:permission-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('permissions', response.data)
    
    def test_get_permissions_as_normal_user(self):
        """测试普通用户获取权限列表（应该被拒绝）"""
        self.client.force_authenticate(user=self.normal_user)
        url = reverse('authentication:permission-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class RoleAPITest(APITestCase):
    """角色API测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpassword123'
        )
        self.normal_user = User.objects.create_user(
            email='user@example.com',
            password='userpassword123'
        )
        
        # 创建测试权限和角色
        self.permission = Permission.objects.create(
            code='test.permission',
            name='测试权限',
            category='test'
        )
        self.role = Role.objects.create(
            name='测试角色',
            description='测试角色描述'
        )
        self.role.permissions.add(self.permission)
    
    def test_create_role_as_admin(self):
        """测试管理员创建角色"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('authentication:role-list')
        
        data = {
            'name': '新角色',
            'description': '新角色描述',
            'permission_codes': ['test.permission']
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('role', response.data)
    
    def test_get_role_list_as_admin(self):
        """测试管理员获取角色列表"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('authentication:role-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_update_role_as_admin(self):
        """测试管理员更新角色"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('authentication:role-detail', kwargs={'pk': self.role.pk})
        
        data = {
            'name': '更新后的角色',
            'description': '更新后的描述'
        }
        
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
    
    def test_delete_role_as_admin(self):
        """测试管理员删除角色"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('authentication:role-detail', kwargs={'pk': self.role.pk})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)


class UserRoleAPITest(APITestCase):
    """用户角色API测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpassword123'
        )
        self.test_user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword123'
        )
        
        self.role = Role.objects.create(
            name='测试角色',
            description='测试角色描述'
        )
    
    def test_assign_role_to_user(self):
        """测试给用户分配角色"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('authentication:user_roles', kwargs={'pk': self.test_user.pk})
        
        data = {'roles': [self.role.pk]}
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # 验证角色已分配
        self.test_user.refresh_from_db()
        self.assertIn(self.role, self.test_user.roles.all())
    
    def test_get_user_roles(self):
        """测试获取用户角色"""
        self.test_user.roles.add(self.role)
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('authentication:user_roles', kwargs={'pk': self.test_user.pk})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('roles', response.data)
    
    def test_remove_user_role(self):
        """测试移除用户角色"""
        self.test_user.roles.add(self.role)
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('authentication:user_role_remove', kwargs={
            'pk': self.test_user.pk,
            'role_pk': self.role.pk
        })
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # 验证角色已移除
        self.test_user.refresh_from_db()
        self.assertNotIn(self.role, self.test_user.roles.all())


class UserPermissionAPITest(APITestCase):
    """用户权限API测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword123'
        )
        
        self.permission = Permission.objects.create(
            code='test.permission',
            name='测试权限',
            category='test'
        )
        self.role = Role.objects.create(
            name='测试角色',
            description='测试角色描述'
        )
        self.role.permissions.add(self.permission)
        self.user.roles.add(self.role)
    
    def test_get_user_permissions(self):
        """测试获取用户权限"""
        self.client.force_authenticate(user=self.user)
        url = reverse('authentication:user_permissions')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('permissions', response.data)
        self.assertIn('roles', response.data)
        self.assertIn('test.permission', response.data['permissions'])
        self.assertIn('测试角色', response.data['roles'])


class UserRegistrationTest(APITestCase):
    """用户注册测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.register_url = reverse('authentication:register')
        self.valid_user_data = {
            'email': 'newuser@example.com',
            'password': 'securepassword123',
            'password_confirm': 'securepassword123',
            'first_name': '新',
            'last_name': '用户'
        }
    
    def test_user_registration_success(self):
        """测试用户注册成功"""
        response = self.client.post(self.register_url, self.valid_user_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        
        # 验证用户已创建
        user = User.objects.get(email=self.valid_user_data['email'])
        self.assertTrue(user.check_password(self.valid_user_data['password']))
    
    def test_user_registration_password_mismatch(self):
        """测试密码不匹配的情况"""
        invalid_data = self.valid_user_data.copy()
        invalid_data['password_confirm'] = 'differentpassword'
        
        response = self.client.post(self.register_url, invalid_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data)
    
    def test_user_registration_duplicate_email(self):
        """测试重复邮箱注册"""
        # 先创建一个用户
        User.objects.create_user(
            email=self.valid_user_data['email'],
            password='password123'
        )
        
        response = self.client.post(self.register_url, self.valid_user_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_user_registration_weak_password(self):
        """测试弱密码注册"""
        invalid_data = self.valid_user_data.copy()
        invalid_data['password'] = '123'
        invalid_data['password_confirm'] = '123'
        
        response = self.client.post(self.register_url, invalid_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)


class UserLoginTest(APITestCase):
    """用户登录测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.login_url = reverse('authentication:login')
        self.user_data = {
            'email': 'testuser@example.com',
            'password': 'testpassword123'
        }
        self.user = User.objects.create_user(**self.user_data)
    
    def test_user_login_success(self):
        """测试用户登录成功"""
        response = self.client.post(self.login_url, self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
    
    def test_user_login_invalid_credentials(self):
        """测试无效凭据登录"""
        invalid_data = {
            'email': self.user_data['email'],
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, invalid_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
    
    def test_user_login_inactive_user(self):
        """测试未激活用户登录"""
        self.user.is_active = False
        self.user.save()
        
        response = self.client.post(self.login_url, self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
    
    def test_user_login_missing_fields(self):
        """测试缺少字段的登录"""
        response = self.client.post(self.login_url, {'email': self.user_data['email']})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)


class UserProfileTest(APITestCase):
    """用户信息管理测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword123',
            first_name='测试',
            last_name='用户'
        )
        self.profile_url = reverse('authentication:user_profile')
        self.user_info_url = reverse('authentication:user_info')
        
        # 认证用户
        self.client.force_authenticate(user=self.user)
    
    def test_get_user_profile(self):
        """测试获取用户信息"""
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['first_name'], self.user.first_name)
    
    def test_update_user_profile(self):
        """测试更新用户信息"""
        update_data = {
            'first_name': '更新的名字',
            'last_name': '更新的姓氏'
        }
        
        response = self.client.patch(self.profile_url, update_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # 验证数据已更新
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, update_data['first_name'])
        self.assertEqual(self.user.last_name, update_data['last_name'])
    
    def test_get_user_info(self):
        """测试获取用户信息（简化接口）"""
        response = self.client.get(self.user_info_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], self.user.email)
    
    def test_unauthenticated_access(self):
        """测试未认证访问"""
        self.client.force_authenticate(user=None)
        
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class JWTTokenTest(APITestCase):
    """JWT令牌测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword123'
        )
        self.refresh_url = reverse('authentication:token_refresh')
        self.logout_url = reverse('authentication:logout')
    
    def test_token_refresh(self):
        """测试令牌刷新"""
        refresh = RefreshToken.for_user(self.user)
        
        response = self.client.post(self.refresh_url, {'refresh': str(refresh)})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_logout_with_token_blacklist(self):
        """测试登出并将令牌加入黑名单"""
        refresh = RefreshToken.for_user(self.user)
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(self.logout_url, {'refresh': str(refresh)})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # 验证令牌已被加入黑名单（尝试再次使用应该失败）
        refresh_response = self.client.post(self.refresh_url, {'refresh': str(refresh)})
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)


class APIHealthCheckTest(APITestCase):
    """API健康检查测试"""
    
    def test_api_health_check(self):
        """测试API健康检查端点"""
        response = self.client.get('/api/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
