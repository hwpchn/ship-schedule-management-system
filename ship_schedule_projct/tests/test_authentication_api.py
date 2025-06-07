"""
认证API测试用例
测试用户注册、登录、权限管理等API功能
"""
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.models import Permission, Role

User = get_user_model()


class UserRegistrationAPITest(APITestCase):
    """用户注册API测试"""

    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.valid_data = {
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
            'first_name': '新',
            'last_name': '用户'
        }

    def test_user_registration_success(self):
        """测试用户注册成功"""
        response = self.client.post(self.register_url, self.valid_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)

        # 验证用户已创建
        user = User.objects.get(email=self.valid_data['email'])
        self.assertTrue(user.check_password(self.valid_data['password']))

    def test_user_registration_password_mismatch(self):
        """测试密码不匹配"""
        invalid_data = self.valid_data.copy()
        invalid_data['password_confirm'] = 'differentpass'

        response = self.client.post(self.register_url, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data)

    def test_user_registration_duplicate_email(self):
        """测试重复邮箱注册"""
        User.objects.create_user(
            email=self.valid_data['email'],
            password='existingpass123'
        )

        response = self.client.post(self.register_url, self.valid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_user_registration_invalid_email(self):
        """测试无效邮箱格式"""
        invalid_data = self.valid_data.copy()
        invalid_data['email'] = 'invalid-email'

        response = self.client.post(self.register_url, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_user_registration_weak_password(self):
        """测试弱密码"""
        invalid_data = self.valid_data.copy()
        invalid_data['password'] = '123'
        invalid_data['password_confirm'] = '123'

        response = self.client.post(self.register_url, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginAPITest(APITestCase):
    """用户登录API测试"""

    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.login_url = '/api/auth/login/'
        self.user_data = {
            'email': 'testuser@example.com',
            'password': 'testpass123'
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
            'email': 'testuser@example.com',
            'password': 'wrongpassword'
        }

        response = self.client.post(self.login_url, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_user_login_nonexistent_user(self):
        """测试不存在的用户登录"""
        invalid_data = {
            'email': 'nonexistent@example.com',
            'password': 'somepassword'
        }

        response = self.client.post(self.login_url, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_inactive_user(self):
        """测试非活跃用户登录"""
        self.user.is_active = False
        self.user.save()

        response = self.client.post(self.login_url, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_missing_fields(self):
        """测试缺少必填字段"""
        # 缺少密码
        response = self.client.post(self.login_url, {'email': 'test@example.com'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # 缺少邮箱
        response = self.client.post(self.login_url, {'password': 'password123'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class JWTTokenAPITest(APITestCase):
    """JWT Token API测试"""

    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123'
        )
        self.refresh_url = '/api/auth/token/refresh/'
        self.logout_url = '/api/auth/logout/'

    def test_token_refresh_success(self):
        """测试Token刷新成功"""
        refresh = RefreshToken.for_user(self.user)

        response = self.client.post(self.refresh_url, {'refresh': str(refresh)})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_token_refresh_invalid_token(self):
        """测试无效Token刷新"""
        response = self.client.post(self.refresh_url, {'refresh': 'invalid_token'})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_missing_token(self):
        """测试缺少Token"""
        response = self.client.post(self.refresh_url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_success(self):
        """测试登出成功"""
        refresh = RefreshToken.for_user(self.user)
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.logout_url, {'refresh': str(refresh)})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_logout_invalid_token(self):
        """测试使用无效Token登出"""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.logout_url, {'refresh': 'invalid_token'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserInfoAPITest(APITestCase):
    """用户信息API测试"""

    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            first_name='测试',
            last_name='用户'
        )
        self.user_info_url = '/api/auth/me/'
        self.user_permissions_url = '/api/auth/me/permissions/'

    def test_get_user_info_authenticated(self):
        """测试获取用户信息（已认证）"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.user_info_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'testuser@example.com')
        self.assertEqual(response.data['user']['full_name'], '测试 用户')

    def test_get_user_info_unauthenticated(self):
        """测试获取用户信息（未认证）"""
        response = self.client.get(self.user_info_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_permissions_authenticated(self):
        """测试获取用户权限（已认证）"""
        # 创建权限和角色
        permission = Permission.objects.create(
            code='test.permission',
            name='测试权限',
            category='测试'
        )
        role = Role.objects.create(
            name='测试角色',
            description='测试角色'
        )
        role.permissions.add(permission)
        self.user.roles.add(role)

        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.user_permissions_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('permissions', response.data)
        self.assertIn('roles', response.data)
        self.assertIn('test.permission', response.data['permissions'])
        self.assertIn('测试角色', response.data['roles'])

    def test_get_user_permissions_unauthenticated(self):
        """测试获取用户权限（未认证）"""
        response = self.client.get(self.user_permissions_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PermissionAPITest(APITestCase):
    """权限管理API测试"""

    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        self.normal_user = User.objects.create_user(
            email='user@example.com',
            password='userpass123'
        )

        self.permission = Permission.objects.create(
            code='test.permission',
            name='测试权限',
            category='测试'
        )

        self.permission_list_url = '/api/auth/permissions/'

    def test_get_permissions_as_admin(self):
        """测试管理员获取权限列表"""
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(self.permission_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('permissions', response.data)

    def test_get_permissions_as_normal_user(self):
        """测试普通用户获取权限列表（应被拒绝）"""
        self.client.force_authenticate(user=self.normal_user)

        response = self.client.get(self.permission_list_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_permissions_unauthenticated(self):
        """测试未认证用户获取权限列表"""
        response = self.client.get(self.permission_list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RoleAPITest(APITestCase):
    """角色管理API测试"""

    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        self.normal_user = User.objects.create_user(
            email='user@example.com',
            password='userpass123'
        )

        self.permission = Permission.objects.create(
            code='test.permission',
            name='测试权限',
            category='测试'
        )

        self.role = Role.objects.create(
            name='测试角色',
            description='测试角色描述'
        )
        self.role.permissions.add(self.permission)

        self.role_list_url = '/api/auth/roles/'
        self.role_detail_url = f'/api/auth/roles/{self.role.pk}/'

    def test_create_role_as_admin(self):
        """测试管理员创建角色"""
        self.client.force_authenticate(user=self.admin_user)

        data = {
            'name': '新角色',
            'description': '新角色描述',
            'permission_codes': ['test.permission']
        }

        response = self.client.post(self.role_list_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('role', response.data)

    def test_get_role_list_as_admin(self):
        """测试管理员获取角色列表"""
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(self.role_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_update_role_as_admin(self):
        """测试管理员更新角色"""
        self.client.force_authenticate(user=self.admin_user)

        data = {
            'name': '更新后的角色',
            'description': '更新后的描述'
        }

        response = self.client.patch(self.role_detail_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_delete_role_as_admin(self):
        """测试管理员删除角色"""
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.delete(self.role_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_role_operations_as_normal_user(self):
        """测试普通用户角色操作（应被拒绝）"""
        self.client.force_authenticate(user=self.normal_user)

        # 获取角色列表
        response = self.client.get(self.role_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 创建角色
        data = {'name': '新角色', 'description': '描述'}
        response = self.client.post(self.role_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class APIHealthCheckTest(APITestCase):
    """API健康检查测试"""

    def test_api_health_check(self):
        """测试API健康检查端点"""
        response = self.client.get('/api/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], '船舶调度系统API服务正常运行')

    def test_api_health_check_no_auth_required(self):
        """测试健康检查不需要认证"""
        # 确保没有认证
        self.client.force_authenticate(user=None)

        response = self.client.get('/api/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
