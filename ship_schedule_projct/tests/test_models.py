"""
模型测试用例
测试所有数据模型的创建、验证、关联等功能
"""
import json
from decimal import Decimal
from django.test import TestCase
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from django.utils import timezone

from authentication.models import Permission, Role
from schedules.models import VesselSchedule, VesselInfoFromCompany
from local_fees.models import LocalFee

User = get_user_model()


class UserModelTest(TestCase):
    """用户模型测试"""

    def setUp(self):
        """测试前准备"""
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': '测试',
            'last_name': '用户'
        }

    def test_create_user_success(self):
        """测试成功创建用户"""
        user = User.objects.create_user(**self.user_data)

        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser_success(self):
        """测试成功创建超级用户"""
        user = User.objects.create_superuser(**self.user_data)

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_user_email_required(self):
        """测试邮箱必填"""
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='testpass123')

    def test_user_email_unique(self):
        """测试邮箱唯一性"""
        User.objects.create_user(**self.user_data)

        with self.assertRaises(IntegrityError):
            User.objects.create_user(**self.user_data)

    def test_user_string_representation(self):
        """测试用户字符串表示"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'test@example.com')

    def test_get_full_name(self):
        """测试获取全名"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.get_full_name(), '测试 用户')

    def test_get_short_name(self):
        """测试获取简短名称"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.get_short_name(), '测试')


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

    def test_permission_code_unique(self):
        """测试权限代码唯一性"""
        Permission.objects.create(**self.permission_data)

        with self.assertRaises(IntegrityError):
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

    def test_role_name_unique(self):
        """测试角色名称唯一性"""
        Role.objects.create(**self.role_data)

        with self.assertRaises(IntegrityError):
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


class VesselScheduleModelTest(TestCase):
    """船舶航线模型测试"""

    def setUp(self):
        """测试前准备"""
        self.schedule_data = {
            'polCd': 'CNSHA',
            'podCd': 'USNYC',
            'vessel': 'TEST_VESSEL',
            'voyage': 'TEST001',
            'data_version': 20250527,
            'carriercd': 'TEST',
            'fetch_timestamp': 1716825600,
            'fetch_date': timezone.now(),
            'pol': '上海',
            'pod': '纽约',
            'eta': '2025-06-15',
            'etd': '2025-05-20',
            'status': 1
        }

    def test_create_vessel_schedule_success(self):
        """测试成功创建船舶航线"""
        schedule = VesselSchedule.objects.create(**self.schedule_data)

        self.assertEqual(schedule.polCd, 'CNSHA')
        self.assertEqual(schedule.podCd, 'USNYC')
        self.assertEqual(schedule.vessel, 'TEST_VESSEL')
        self.assertEqual(schedule.status, 1)

    def test_vessel_schedule_unique_constraint(self):
        """测试船舶航线唯一性约束"""
        VesselSchedule.objects.create(**self.schedule_data)

        with self.assertRaises(IntegrityError):
            VesselSchedule.objects.create(**self.schedule_data)

    def test_vessel_schedule_string_representation(self):
        """测试船舶航线字符串表示"""
        schedule = VesselSchedule.objects.create(**self.schedule_data)
        expected = f"TEST_VESSEL TEST001: 上海(CNSHA) → 纽约(USNYC)"
        self.assertEqual(str(schedule), expected)

    def test_share_cabins_json_field(self):
        """测试共舱信息JSON字段"""
        share_cabins = [
            {'carrierCd': 'TEST'},
            {'carrierCd': 'MSK'}
        ]
        self.schedule_data['shareCabins'] = json.dumps(share_cabins)

        schedule = VesselSchedule.objects.create(**self.schedule_data)
        self.assertEqual(schedule.shareCabins, json.dumps(share_cabins))


class VesselInfoFromCompanyModelTest(TestCase):
    """船舶额外信息模型测试"""

    def setUp(self):
        """测试前准备"""
        self.vessel_info_data = {
            'carriercd': 'TEST',
            'polCd': 'CNSHA',
            'podCd': 'USNYC',
            'vessel': 'TEST_VESSEL',
            'voyage': 'TEST001',
            'gp_20': '100',
            'hq_40': '50',
            'cut_off_time': '2025-05-18 18:00',
            'price': Decimal('4500.00')
        }

    def test_create_vessel_info_success(self):
        """测试成功创建船舶额外信息"""
        vessel_info = VesselInfoFromCompany.objects.create(**self.vessel_info_data)

        self.assertEqual(vessel_info.carriercd, 'TEST')
        self.assertEqual(vessel_info.vessel, 'TEST_VESSEL')
        self.assertEqual(vessel_info.price, Decimal('4500.00'))

    def test_vessel_info_unique_constraint(self):
        """测试船舶额外信息唯一性约束"""
        VesselInfoFromCompany.objects.create(**self.vessel_info_data)

        with self.assertRaises(IntegrityError):
            VesselInfoFromCompany.objects.create(**self.vessel_info_data)

    def test_vessel_info_string_representation(self):
        """测试船舶额外信息字符串表示"""
        vessel_info = VesselInfoFromCompany.objects.create(**self.vessel_info_data)
        expected = "TEST_VESSEL TEST001: TEST CNSHA → USNYC, ¥4500.00"
        self.assertEqual(str(vessel_info), expected)


class LocalFeeModelTest(TestCase):
    """本地费用模型测试"""

    def setUp(self):
        """测试前准备"""
        self.local_fee_data = {
            'polCd': 'CNSHA',
            'podCd': 'USNYC',
            'carriercd': 'TEST',
            'name': '起运港码头费',
            'unit_name': '箱型',
            'price_20gp': Decimal('760.00'),
            'price_40gp': Decimal('1287.00'),
            'price_40hq': Decimal('1287.00'),
            'currency': 'CNY'
        }

    def test_create_local_fee_success(self):
        """测试成功创建本地费用"""
        local_fee = LocalFee.objects.create(**self.local_fee_data)

        self.assertEqual(local_fee.polCd, 'CNSHA')
        self.assertEqual(local_fee.name, '起运港码头费')
        self.assertEqual(local_fee.price_20gp, Decimal('760.00'))

    def test_local_fee_unique_constraint(self):
        """测试本地费用唯一性约束"""
        LocalFee.objects.create(**self.local_fee_data)

        with self.assertRaises(IntegrityError):
            LocalFee.objects.create(**self.local_fee_data)

    def test_local_fee_string_representation(self):
        """测试本地费用字符串表示"""
        local_fee = LocalFee.objects.create(**self.local_fee_data)
        expected = "TEST [CNSHA-USNYC] 起运港码头费"
        self.assertEqual(str(local_fee), expected)

    def test_local_fee_per_bill_pricing(self):
        """测试按票计费"""
        bill_fee_data = {
            'polCd': 'CNSHA',
            'podCd': 'USNYC',
            'carriercd': 'TEST',
            'name': '保安费',
            'unit_name': '票',
            'price_per_bill': Decimal('50.00'),
            'currency': 'USD'
        }

        local_fee = LocalFee.objects.create(**bill_fee_data)
        self.assertEqual(local_fee.price_per_bill, Decimal('50.00'))
        self.assertIsNone(local_fee.price_20gp)


class UserPermissionIntegrationTest(TestCase):
    """用户权限集成测试"""

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

        self.role = Role.objects.create(
            name='船期查询员',
            description='负责船期查询'
        )
        self.role.permissions.add(self.permission1)

    def test_user_has_permission_through_role(self):
        """测试用户通过角色获得权限"""
        self.user.roles.add(self.role)

        self.assertTrue(self.user.has_permission('vessel_schedule.list'))
        self.assertFalse(self.user.has_permission('vessel_schedule.create'))

    def test_superuser_has_all_permissions(self):
        """测试超级用户拥有所有权限"""
        superuser = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )

        self.assertTrue(superuser.has_permission('vessel_schedule.list'))
        self.assertTrue(superuser.has_permission('vessel_schedule.create'))
        self.assertTrue(superuser.has_permission('any.permission'))

    def test_get_user_permissions(self):
        """测试获取用户权限列表"""
        self.user.roles.add(self.role)

        permissions = self.user.get_user_permissions()
        self.assertIn('vessel_schedule.list', permissions)
        self.assertEqual(len(permissions), 1)

    def test_get_role_names(self):
        """测试获取用户角色名称"""
        self.user.roles.add(self.role)

        role_names = self.user.get_role_names()
        self.assertIn('船期查询员', role_names)
        self.assertEqual(len(role_names), 1)
