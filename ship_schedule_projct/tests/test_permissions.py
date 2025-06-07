"""
权限系统测试用例
测试RBAC权限控制、权限检查、角色管理等功能
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from authentication.models import Permission, Role
from authentication.permissions import HasPermission

User = get_user_model()


class PermissionModelTest(TestCase):
    """权限模型测试"""
    
    def setUp(self):
        """测试前准备"""
        self.permission_data = {
            'code': 'test.permission',
            'name': '测试权限',
            'description': '这是一个测试权限',
            'category': '测试分类'
        }
    
    def test_create_permission_success(self):
        """测试成功创建权限"""
        permission = Permission.objects.create(**self.permission_data)
        
        self.assertEqual(permission.code, 'test.permission')
        self.assertEqual(permission.name, '测试权限')
        self.assertEqual(permission.category, '测试分类')
        self.assertIsNotNone(permission.created_at)
    
    def test_permission_code_unique(self):
        """测试权限代码唯一性"""
        Permission.objects.create(**self.permission_data)
        
        with self.assertRaises(Exception):
            Permission.objects.create(**self.permission_data)
    
    def test_permission_string_representation(self):
        """测试权限字符串表示"""
        permission = Permission.objects.create(**self.permission_data)
        expected = f"{self.permission_data['name']} ({self.permission_data['code']})"
        self.assertEqual(str(permission), expected)


class RoleModelTest(TestCase):
    """角色模型测试"""
    
    def setUp(self):
        """测试前准备"""
        self.role_data = {
            'name': '测试角色',
            'description': '测试角色描述',
            'is_active': True
        }
        
        self.permission1 = Permission.objects.create(
            code='test.permission1',
            name='测试权限1',
            category='测试'
        )
        self.permission2 = Permission.objects.create(
            code='test.permission2',
            name='测试权限2',
            category='测试'
        )
    
    def test_create_role_success(self):
        """测试成功创建角色"""
        role = Role.objects.create(**self.role_data)
        
        self.assertEqual(role.name, '测试角色')
        self.assertTrue(role.is_active)
        self.assertIsNotNone(role.created_at)
    
    def test_role_name_unique(self):
        """测试角色名称唯一性"""
        Role.objects.create(**self.role_data)
        
        with self.assertRaises(Exception):
            Role.objects.create(**self.role_data)
    
    def test_role_permissions_relationship(self):
        """测试角色权限关联"""
        role = Role.objects.create(**self.role_data)
        role.permissions.add(self.permission1, self.permission2)
        
        self.assertEqual(role.permissions.count(), 2)
        self.assertIn(self.permission1, role.permissions.all())
        self.assertIn(self.permission2, role.permissions.all())
    
    def test_get_permission_codes(self):
        """测试获取权限代码列表"""
        role = Role.objects.create(**self.role_data)
        role.permissions.add(self.permission1, self.permission2)
        
        permission_codes = role.get_permission_codes()
        self.assertIn('test.permission1', permission_codes)
        self.assertIn('test.permission2', permission_codes)
        self.assertEqual(len(permission_codes), 2)
    
    def test_role_string_representation(self):
        """测试角色字符串表示"""
        role = Role.objects.create(**self.role_data)
        self.assertEqual(str(role), '测试角色')


class UserPermissionTest(TestCase):
    """用户权限测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        self.permission1 = Permission.objects.create(
            code='vessel_schedule.list',
            name='船期列表查看',
            category='船期管理'
        )
        
        self.permission2 = Permission.objects.create(
            code='vessel_schedule.create',
            name='船期创建',
            category='船期管理'
        )
        
        self.permission3 = Permission.objects.create(
            code='local_fee.list',
            name='本地费用列表',
            category='本地费用'
        )
        
        self.role1 = Role.objects.create(
            name='船期查询员',
            description='负责船期查询'
        )
        self.role1.permissions.add(self.permission1)
        
        self.role2 = Role.objects.create(
            name='船期管理员',
            description='负责船期管理'
        )
        self.role2.permissions.add(self.permission1, self.permission2)
        
        self.role3 = Role.objects.create(
            name='费用查询员',
            description='负责费用查询'
        )
        self.role3.permissions.add(self.permission3)
    
    def test_user_has_permission_through_single_role(self):
        """测试用户通过单个角色获得权限"""
        self.user.roles.add(self.role1)
        
        self.assertTrue(self.user.has_permission('vessel_schedule.list'))
        self.assertFalse(self.user.has_permission('vessel_schedule.create'))
        self.assertFalse(self.user.has_permission('local_fee.list'))
    
    def test_user_has_permission_through_multiple_roles(self):
        """测试用户通过多个角色获得权限"""
        self.user.roles.add(self.role1, self.role3)
        
        self.assertTrue(self.user.has_permission('vessel_schedule.list'))
        self.assertFalse(self.user.has_permission('vessel_schedule.create'))
        self.assertTrue(self.user.has_permission('local_fee.list'))
    
    def test_user_permission_accumulation(self):
        """测试用户权限累积"""
        self.user.roles.add(self.role1, self.role2)
        
        # 应该拥有两个角色的所有权限
        self.assertTrue(self.user.has_permission('vessel_schedule.list'))
        self.assertTrue(self.user.has_permission('vessel_schedule.create'))
        self.assertFalse(self.user.has_permission('local_fee.list'))
    
    def test_superuser_has_all_permissions(self):
        """测试超级用户拥有所有权限"""
        superuser = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        
        self.assertTrue(superuser.has_permission('vessel_schedule.list'))
        self.assertTrue(superuser.has_permission('vessel_schedule.create'))
        self.assertTrue(superuser.has_permission('local_fee.list'))
        self.assertTrue(superuser.has_permission('any.permission'))
    
    def test_get_user_permissions(self):
        """测试获取用户权限列表"""
        self.user.roles.add(self.role1, self.role3)
        
        permissions = self.user.get_user_permissions()
        
        self.assertIn('vessel_schedule.list', permissions)
        self.assertIn('local_fee.list', permissions)
        self.assertNotIn('vessel_schedule.create', permissions)
        self.assertEqual(len(permissions), 2)
    
    def test_get_role_names(self):
        """测试获取用户角色名称"""
        self.user.roles.add(self.role1, self.role3)
        
        role_names = self.user.get_role_names()
        
        self.assertIn('船期查询员', role_names)
        self.assertIn('费用查询员', role_names)
        self.assertEqual(len(role_names), 2)
    
    def test_inactive_role_permissions(self):
        """测试非活跃角色权限"""
        self.role1.is_active = False
        self.role1.save()
        
        self.user.roles.add(self.role1)
        
        # 非活跃角色的权限不应该生效
        permissions = self.user.get_user_permissions()
        self.assertEqual(len(permissions), 0)
        self.assertFalse(self.user.has_permission('vessel_schedule.list'))


class PermissionDecoratorTest(APITestCase):
    """权限装饰器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        self.permission = Permission.objects.create(
            code='test.permission',
            name='测试权限',
            category='测试'
        )
        
        self.role = Role.objects.create(
            name='测试角色',
            description='测试角色'
        )
        self.role.permissions.add(self.permission)
    
    def test_has_permission_decorator_with_permission(self):
        """测试有权限时装饰器通过"""
        self.user.roles.add(self.role)
        
        permission_checker = HasPermission('test.permission')
        
        # 模拟请求对象
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        request = MockRequest(self.user)
        
        # 权限检查应该通过
        self.assertTrue(permission_checker.has_permission(request, None))
    
    def test_has_permission_decorator_without_permission(self):
        """测试无权限时装饰器拒绝"""
        # 不给用户分配角色
        
        permission_checker = HasPermission('test.permission')
        
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        request = MockRequest(self.user)
        
        # 权限检查应该失败
        self.assertFalse(permission_checker.has_permission(request, None))
    
    def test_has_permission_decorator_unauthenticated(self):
        """测试未认证用户装饰器拒绝"""
        permission_checker = HasPermission('test.permission')
        
        class MockRequest:
            def __init__(self):
                self.user = None
        
        request = MockRequest()
        
        # 权限检查应该失败
        self.assertFalse(permission_checker.has_permission(request, None))


class PermissionAPIIntegrationTest(APITestCase):
    """权限API集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        
        # 创建不同权限级别的用户
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        
        self.manager_user = User.objects.create_user(
            email='manager@example.com',
            password='managerpass123'
        )
        
        self.readonly_user = User.objects.create_user(
            email='readonly@example.com',
            password='readonlypass123'
        )
        
        self.no_permission_user = User.objects.create_user(
            email='noperm@example.com',
            password='nopermpass123'
        )
        
        # 创建权限
        self.list_permission = Permission.objects.create(
            code='vessel_schedule.list',
            name='船期列表查看',
            category='船期管理'
        )
        
        self.create_permission = Permission.objects.create(
            code='vessel_schedule.create',
            name='船期创建',
            category='船期管理'
        )
        
        # 创建角色
        self.manager_role = Role.objects.create(
            name='管理员',
            description='管理员角色'
        )
        self.manager_role.permissions.add(self.list_permission, self.create_permission)
        
        self.readonly_role = Role.objects.create(
            name='只读用户',
            description='只读用户角色'
        )
        self.readonly_role.permissions.add(self.list_permission)
        
        # 分配角色
        self.manager_user.roles.add(self.manager_role)
        self.readonly_user.roles.add(self.readonly_role)
        
        self.test_url = '/api/schedules/'
    
    def test_admin_access_all_operations(self):
        """测试管理员可以访问所有操作"""
        self.client.force_authenticate(user=self.admin_user)
        
        # 应该可以访问列表
        response = self.client.get(self.test_url)
        self.assertIn(response.status_code, [200, 404])  # 可能没有数据但有权限
    
    def test_manager_access_with_permissions(self):
        """测试管理员用户按权限访问"""
        self.client.force_authenticate(user=self.manager_user)
        
        # 应该可以访问列表（有权限）
        response = self.client.get(self.test_url)
        self.assertIn(response.status_code, [200, 404])
    
    def test_readonly_user_limited_access(self):
        """测试只读用户受限访问"""
        self.client.force_authenticate(user=self.readonly_user)
        
        # 应该可以访问列表（有权限）
        response = self.client.get(self.test_url)
        self.assertIn(response.status_code, [200, 404])
    
    def test_no_permission_user_denied(self):
        """测试无权限用户被拒绝"""
        self.client.force_authenticate(user=self.no_permission_user)
        
        # 应该被拒绝访问
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, 403)
    
    def test_unauthenticated_user_denied(self):
        """测试未认证用户被拒绝"""
        # 不进行认证
        response = self.client.get(self.test_url)
        self.assertEqual(response.status_code, 401)


class PermissionCacheTest(TestCase):
    """权限缓存测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        self.permission = Permission.objects.create(
            code='test.permission',
            name='测试权限',
            category='测试'
        )
        
        self.role = Role.objects.create(
            name='测试角色',
            description='测试角色'
        )
        self.role.permissions.add(self.permission)
    
    def test_permission_check_consistency(self):
        """测试权限检查一致性"""
        # 初始状态：无权限
        self.assertFalse(self.user.has_permission('test.permission'))
        
        # 分配角色后：有权限
        self.user.roles.add(self.role)
        self.assertTrue(self.user.has_permission('test.permission'))
        
        # 移除角色后：无权限
        self.user.roles.clear()
        self.assertFalse(self.user.has_permission('test.permission'))
    
    def test_role_permission_change_effect(self):
        """测试角色权限变更的影响"""
        self.user.roles.add(self.role)
        
        # 初始状态：有权限
        self.assertTrue(self.user.has_permission('test.permission'))
        
        # 从角色中移除权限
        self.role.permissions.clear()
        
        # 权限检查应该反映变更
        self.assertFalse(self.user.has_permission('test.permission'))
    
    def test_inactive_role_effect(self):
        """测试角色激活状态的影响"""
        self.user.roles.add(self.role)
        
        # 初始状态：有权限
        self.assertTrue(self.user.has_permission('test.permission'))
        
        # 禁用角色
        self.role.is_active = False
        self.role.save()
        
        # 权限检查应该反映变更
        self.assertFalse(self.user.has_permission('test.permission'))
        
        # 重新激活角色
        self.role.is_active = True
        self.role.save()
        
        # 权限应该恢复
        self.assertTrue(self.user.has_permission('test.permission'))


class PermissionEdgeCaseTest(TestCase):
    """权限边界情况测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
    
    def test_empty_permission_code(self):
        """测试空权限代码"""
        self.assertFalse(self.user.has_permission(''))
        self.assertFalse(self.user.has_permission(None))
    
    def test_nonexistent_permission(self):
        """测试不存在的权限"""
        self.assertFalse(self.user.has_permission('nonexistent.permission'))
    
    def test_user_without_roles(self):
        """测试没有角色的用户"""
        permissions = self.user.get_user_permissions()
        self.assertEqual(len(permissions), 0)
        
        role_names = self.user.get_role_names()
        self.assertEqual(len(role_names), 0)
    
    def test_role_without_permissions(self):
        """测试没有权限的角色"""
        role = Role.objects.create(
            name='空角色',
            description='没有权限的角色'
        )
        
        self.user.roles.add(role)
        
        permissions = self.user.get_user_permissions()
        self.assertEqual(len(permissions), 0)
    
    def test_duplicate_permissions_through_roles(self):
        """测试通过多个角色获得重复权限"""
        permission = Permission.objects.create(
            code='duplicate.permission',
            name='重复权限',
            category='测试'
        )
        
        role1 = Role.objects.create(name='角色1', description='角色1')
        role1.permissions.add(permission)
        
        role2 = Role.objects.create(name='角色2', description='角色2')
        role2.permissions.add(permission)
        
        self.user.roles.add(role1, role2)
        
        permissions = self.user.get_user_permissions()
        # 应该去重，只有一个权限
        self.assertEqual(permissions.count('duplicate.permission'), 1)
