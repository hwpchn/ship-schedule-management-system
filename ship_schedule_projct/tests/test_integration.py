"""
集成测试用例
测试系统各模块间的集成和端到端业务流程
"""
import json
from decimal import Decimal
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from authentication.models import Permission, Role
from schedules.models import VesselSchedule, VesselInfoFromCompany
from local_fees.models import LocalFee

User = get_user_model()


class UserWorkflowIntegrationTest(APITestCase):
    """用户工作流程集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
    
    def test_complete_user_registration_and_login_workflow(self):
        """测试完整的用户注册和登录工作流程"""
        # 1. 用户注册
        register_data = {
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
            'first_name': '新',
            'last_name': '用户'
        }
        
        response = self.client.post('/api/auth/register/', register_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        
        # 保存注册时获得的token
        register_tokens = response.data['tokens']
        
        # 2. 使用注册时的token访问用户信息
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {register_tokens["access"]}')
        
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['email'], 'newuser@example.com')
        
        # 3. 登出
        response = self.client.post('/api/auth/logout/', {
            'refresh': register_tokens['refresh']
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. 重新登录
        login_data = {
            'email': 'newuser@example.com',
            'password': 'securepass123'
        }
        
        response = self.client.post('/api/auth/login/', login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        
        # 5. 使用新token访问API
        new_tokens = response.data['tokens']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_tokens["access"]}')
        
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_permission_assignment_workflow(self):
        """测试用户权限分配工作流程"""
        # 1. 创建管理员用户
        admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        
        # 2. 创建普通用户
        normal_user = User.objects.create_user(
            email='user@example.com',
            password='userpass123'
        )
        
        # 3. 管理员创建权限
        self.client.force_authenticate(user=admin_user)
        
        permission_data = {
            'code': 'test.permission',
            'name': '测试权限',
            'description': '测试权限描述',
            'category': '测试'
        }
        
        permission = Permission.objects.create(**permission_data)
        
        # 4. 管理员创建角色
        role_data = {
            'name': '测试角色',
            'description': '测试角色描述',
            'permission_codes': ['test.permission']
        }
        
        role = Role.objects.create(
            name=role_data['name'],
            description=role_data['description']
        )
        role.permissions.add(permission)
        
        # 5. 分配角色给用户
        normal_user.roles.add(role)
        
        # 6. 验证用户权限
        self.assertTrue(normal_user.has_permission('test.permission'))
        
        # 7. 切换到普通用户，验证权限生效
        self.client.force_authenticate(user=normal_user)
        
        response = self.client.get('/api/auth/me/permissions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('test.permission', response.data['permissions'])


class ScheduleManagementIntegrationTest(APITestCase):
    """船期管理集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        
        # 创建有权限的用户
        self.user = User.objects.create_user(
            email='scheduleuser@example.com',
            password='schedulepass123'
        )
        
        # 创建所需权限
        permissions = [
            ('vessel_schedule.list', '船期列表查看'),
            ('vessel_schedule.create', '船期创建'),
            ('vessel_schedule.update', '船期更新'),
            ('vessel_schedule.delete', '船期删除'),
            ('vessel_info.list', '船舶信息列表'),
            ('vessel_info.create', '船舶信息创建'),
            ('vessel_schedule_list', '前台船期查询'),
        ]
        
        role = Role.objects.create(
            name='船期管理员',
            description='船期管理员角色'
        )
        
        for code, name in permissions:
            permission = Permission.objects.create(
                code=code,
                name=name,
                category='船期管理'
            )
            role.permissions.add(permission)
        
        self.user.roles.add(role)
        self.client.force_authenticate(user=self.user)
    
    def test_complete_schedule_management_workflow(self):
        """测试完整的船期管理工作流程"""
        # 1. 创建船舶航线
        schedule_data = {
            'polCd': 'CNSHA',
            'podCd': 'USNYC',
            'vessel': 'TEST_VESSEL',
            'voyage': 'TEST001',
            'data_version': 20250527,
            'carriercd': 'TEST',
            'fetch_timestamp': 1716825600,
            'fetch_date': timezone.now().isoformat(),
            'pol': '上海',
            'pod': '纽约',
            'eta': '2025-06-15',
            'etd': '2025-05-20',
            'routeEtd': '3',
            'totalDuration': '26',
            'shareCabins': json.dumps([
                {'carrierCd': 'TEST'},
                {'carrierCd': 'MSK'}
            ])
        }
        
        response = self.client.post('/api/schedules/', schedule_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        schedule_id = response.data['id']
        
        # 2. 验证自动创建的船舶额外信息
        vessel_info = VesselInfoFromCompany.objects.filter(
            carriercd='TEST',
            polCd='CNSHA',
            podCd='USNYC',
            vessel='TEST_VESSEL',
            voyage='TEST001'
        ).first()
        
        self.assertIsNotNone(vessel_info, "船舶额外信息应该自动创建")
        
        # 3. 更新船舶额外信息
        vessel_info_data = {
            'carriercd': 'TEST',
            'polCd': 'CNSHA',
            'podCd': 'USNYC',
            'vessel': 'TEST_VESSEL',
            'voyage': 'TEST001',
            'gp_20': '100',
            'hq_40': '50',
            'cut_off_time': '2025-05-18 18:00',
            'price': '4500.00'
        }
        
        response = self.client.put(f'/api/vessel-info/{vessel_info.id}/', vessel_info_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. 查询船期列表
        response = self.client.get('/api/schedules/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # 5. 更新船期信息
        update_data = schedule_data.copy()
        update_data['eta'] = '2025-06-16'
        
        response = self.client.put(f'/api/schedules/{schedule_id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['eta'], '2025-06-16')
        
        # 6. 前台共舱分组查询
        response = self.client.get('/api/schedules/cabin-grouping-with-info/', {
            'polCd': 'CNSHA',
            'podCd': 'USNYC'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']['groups']), 1)
        
        # 验证分组包含船舶额外信息
        group = response.data['data']['groups'][0]
        self.assertEqual(len(group['schedules']), 1)
        self.assertIsNotNone(group['schedules'][0]['vessel_info'])
        self.assertEqual(group['schedules'][0]['vessel_info']['price'], '4500.00')
        
        # 7. 删除船期
        response = self.client.delete(f'/api/schedules/{schedule_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 验证船期已删除
        response = self.client.get('/api/schedules/')
        self.assertEqual(len(response.data['results']), 0)
    
    def test_data_synchronization_between_modules(self):
        """测试模块间数据同步"""
        # 1. 创建船舶航线
        schedule = VesselSchedule.objects.create(
            polCd='CNSHA',
            podCd='USNYC',
            vessel='SYNC_VESSEL',
            voyage='SYNC001',
            data_version=20250527,
            carriercd='SYNC',
            fetch_timestamp=1716825600,
            fetch_date=timezone.now(),
            status=1
        )
        
        # 2. 验证自动创建的船舶额外信息
        vessel_info = VesselInfoFromCompany.objects.filter(
            carriercd='SYNC',
            polCd='CNSHA',
            podCd='USNYC',
            vessel='SYNC_VESSEL',
            voyage='SYNC001'
        ).first()
        
        self.assertIsNotNone(vessel_info, "船舶额外信息应该自动创建")
        
        # 3. 更新船舶额外信息
        vessel_info.price = Decimal('5000.00')
        vessel_info.gp_20 = '200'
        vessel_info.save()
        
        # 4. 通过API查询，验证数据同步
        response = self.client.get('/api/vessel-info/query/', {
            'vessel': 'SYNC_VESSEL',
            'voyage': 'SYNC001',
            'carriercd': 'SYNC',
            'polCd': 'CNSHA',
            'podCd': 'USNYC'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['price'], '5000.00')
        self.assertEqual(response.data['data']['gp_20'], '200')
        
        # 5. 删除船舶航线
        schedule.delete()
        
        # 6. 验证船舶额外信息仍然存在（不级联删除）
        vessel_info.refresh_from_db()
        self.assertIsNotNone(vessel_info)


class LocalFeeIntegrationTest(APITestCase):
    """本地费用集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        
        # 创建有权限的用户
        self.user = User.objects.create_user(
            email='feeuser@example.com',
            password='feepass123'
        )
        
        # 创建所需权限
        permissions = [
            ('local_fee.list', '本地费用列表'),
            ('local_fee.create', '本地费用创建'),
            ('local_fee.update', '本地费用更新'),
            ('local_fee.delete', '本地费用删除'),
            ('local_fee.query', '本地费用查询'),
        ]
        
        role = Role.objects.create(
            name='本地费用管理员',
            description='本地费用管理员角色'
        )
        
        for code, name in permissions:
            permission = Permission.objects.create(
                code=code,
                name=name,
                category='本地费用'
            )
            role.permissions.add(permission)
        
        self.user.roles.add(role)
        self.client.force_authenticate(user=self.user)
    
    def test_complete_local_fee_management_workflow(self):
        """测试完整的本地费用管理工作流程"""
        # 1. 创建多种类型的本地费用
        fees_data = [
            {
                'polCd': 'CNSHA',
                'podCd': 'USNYC',
                'carriercd': 'TEST',
                'name': '起运港码头费',
                'unit_name': '箱型',
                'price_20gp': '760.00',
                'price_40gp': '1287.00',
                'price_40hq': '1287.00',
                'currency': 'CNY'
            },
            {
                'polCd': 'CNSHA',
                'podCd': 'USNYC',
                'carriercd': 'TEST',
                'name': '保安费',
                'unit_name': '票',
                'price_per_bill': '50.00',
                'currency': 'USD'
            },
            {
                'polCd': 'CNSHA',
                'podCd': 'USNYC',
                'carriercd': 'TEST',
                'name': '文件费',
                'unit_name': '票',
                'price_per_bill': '25.00',
                'currency': 'USD'
            }
        ]
        
        created_fees = []
        for fee_data in fees_data:
            response = self.client.post('/api/local-fees/local-fees/', fee_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            created_fees.append(response.data['data'])
        
        # 2. 查询费用列表
        response = self.client.get('/api/local-fees/local-fees/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 3)
        
        # 3. 前台格式查询
        response = self.client.get('/api/local-fees/local-fees/query/', {
            'polCd': 'CNSHA',
            'podCd': 'USNYC',
            'carriercd': 'TEST'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 3)
        
        # 验证前台格式
        for item in response.data['data']:
            self.assertIn('名称', item)
            self.assertIn('单位', item)
            self.assertIn('币种', item)
        
        # 验证不同计费方式
        container_fee = next(item for item in response.data['data'] if item['名称'] == '起运港码头费')
        self.assertEqual(container_fee['20GP'], '760.00')
        self.assertIsNone(container_fee['单票价格'])
        
        bill_fee = next(item for item in response.data['data'] if item['名称'] == '保安费')
        self.assertEqual(bill_fee['单票价格'], '50.00')
        self.assertIsNone(bill_fee['20GP'])
        
        # 4. 更新费用
        fee_id = created_fees[0]['id']
        update_data = {
            'polCd': 'CNSHA',
            'podCd': 'USNYC',
            'carriercd': 'TEST',
            'name': '起运港码头费（更新）',
            'unit_name': '箱型',
            'price_20gp': '800.00',
            'price_40gp': '1350.00',
            'price_40hq': '1350.00',
            'currency': 'CNY'
        }
        
        response = self.client.put(f'/api/local-fees/local-fees/{fee_id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], '起运港码头费（更新）')
        
        # 5. 删除费用
        response = self.client.delete(f'/api/local-fees/local-fees/{fee_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证删除成功
        response = self.client.get('/api/local-fees/local-fees/')
        self.assertEqual(len(response.data['data']), 2)


class CrossModuleIntegrationTest(APITestCase):
    """跨模块集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        
        # 创建有全部权限的用户
        self.user = User.objects.create_user(
            email='fulluser@example.com',
            password='fullpass123'
        )
        
        # 创建所有必要权限
        all_permissions = [
            ('vessel_schedule.list', '船期列表查看'),
            ('vessel_schedule.create', '船期创建'),
            ('vessel_info.list', '船舶信息列表'),
            ('vessel_info.create', '船舶信息创建'),
            ('local_fee.list', '本地费用列表'),
            ('local_fee.create', '本地费用创建'),
            ('local_fee.query', '本地费用查询'),
            ('vessel_schedule_list', '前台船期查询'),
        ]
        
        role = Role.objects.create(
            name='全功能用户',
            description='拥有所有功能权限的用户'
        )
        
        for code, name in all_permissions:
            permission = Permission.objects.create(
                code=code,
                name=name,
                category='全功能'
            )
            role.permissions.add(permission)
        
        self.user.roles.add(role)
        self.client.force_authenticate(user=self.user)
    
    def test_complete_business_scenario(self):
        """测试完整的业务场景"""
        # 1. 创建船舶航线
        schedule_data = {
            'polCd': 'CNSHA',
            'podCd': 'USNYC',
            'vessel': 'BUSINESS_VESSEL',
            'voyage': 'BIZ001',
            'data_version': 20250527,
            'carriercd': 'BIZ',
            'fetch_timestamp': 1716825600,
            'fetch_date': timezone.now().isoformat(),
            'pol': '上海',
            'pod': '纽约',
            'eta': '2025-06-15',
            'etd': '2025-05-20',
            'routeEtd': '3',
            'totalDuration': '26',
            'shareCabins': json.dumps([
                {'carrierCd': 'BIZ'},
                {'carrierCd': 'PARTNER'}
            ])
        }
        
        response = self.client.post('/api/schedules/', schedule_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 2. 更新船舶额外信息
        vessel_info = VesselInfoFromCompany.objects.get(
            carriercd='BIZ',
            polCd='CNSHA',
            podCd='USNYC',
            vessel='BUSINESS_VESSEL',
            voyage='BIZ001'
        )
        
        vessel_info_data = {
            'carriercd': 'BIZ',
            'polCd': 'CNSHA',
            'podCd': 'USNYC',
            'vessel': 'BUSINESS_VESSEL',
            'voyage': 'BIZ001',
            'gp_20': '150',
            'hq_40': '75',
            'cut_off_time': '2025-05-18 18:00',
            'price': '4800.00'
        }
        
        response = self.client.put(f'/api/vessel-info/{vessel_info.id}/', vessel_info_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 3. 创建相关本地费用
        local_fees = [
            {
                'polCd': 'CNSHA',
                'podCd': 'USNYC',
                'carriercd': 'BIZ',
                'name': '起运港码头费',
                'unit_name': '箱型',
                'price_20gp': '800.00',
                'price_40gp': '1350.00',
                'price_40hq': '1350.00',
                'currency': 'CNY'
            },
            {
                'polCd': 'CNSHA',
                'podCd': 'USNYC',
                'carriercd': 'BIZ',
                'name': '目的港码头费',
                'unit_name': '箱型',
                'price_20gp': '900.00',
                'price_40gp': '1500.00',
                'price_40hq': '1500.00',
                'currency': 'USD'
            }
        ]
        
        for fee_data in local_fees:
            response = self.client.post('/api/local-fees/local-fees/', fee_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 4. 前台综合查询 - 船期信息
        response = self.client.get('/api/schedules/cabin-grouping-with-info/', {
            'polCd': 'CNSHA',
            'podCd': 'USNYC'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # 验证船期分组信息
        groups = response.data['data']['groups']
        self.assertEqual(len(groups), 1)
        
        group = groups[0]
        self.assertEqual(group['cabins_count'], 1)
        self.assertIn('BIZ', group['carrier_codes'])
        
        # 验证船舶额外信息
        schedule = group['schedules'][0]
        self.assertIsNotNone(schedule['vessel_info'])
        self.assertEqual(schedule['vessel_info']['price'], '4800.00')
        self.assertEqual(schedule['vessel_info']['gp_20'], '150')
        
        # 5. 前台综合查询 - 本地费用信息
        response = self.client.get('/api/local-fees/local-fees/query/', {
            'polCd': 'CNSHA',
            'podCd': 'USNYC',
            'carriercd': 'BIZ'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 2)
        
        # 验证费用信息格式
        fees = response.data['data']
        origin_fee = next(fee for fee in fees if fee['名称'] == '起运港码头费')
        self.assertEqual(origin_fee['20GP'], '800.00')
        self.assertEqual(origin_fee['币种'], 'CNY')
        
        dest_fee = next(fee for fee in fees if fee['名称'] == '目的港码头费')
        self.assertEqual(dest_fee['20GP'], '900.00')
        self.assertEqual(dest_fee['币种'], 'USD')
        
        # 6. 验证数据一致性
        # 船期、船舶信息、本地费用应该都关联到同一条航线
        self.assertEqual(schedule['polCd'], 'CNSHA')
        self.assertEqual(schedule['podCd'], 'USNYC')
        self.assertEqual(schedule['carriercd'], 'BIZ')
        
        for fee in fees:
            # 本地费用的路线信息应该与船期一致
            # 这里通过查询参数验证，实际业务中应该有更直接的关联
            pass
    
    def test_data_consistency_across_modules(self):
        """测试跨模块数据一致性"""
        # 创建基础数据
        schedule = VesselSchedule.objects.create(
            polCd='CNSHK',
            podCd='THBKK',
            vessel='CONSISTENCY_VESSEL',
            voyage='CON001',
            data_version=20250527,
            carriercd='CON',
            fetch_timestamp=1716825600,
            fetch_date=timezone.now(),
            status=1
        )
        
        # 验证自动创建的船舶信息
        vessel_info = VesselInfoFromCompany.objects.get(
            carriercd='CON',
            polCd='CNSHK',
            podCd='THBKK',
            vessel='CONSISTENCY_VESSEL',
            voyage='CON001'
        )
        
        # 创建本地费用
        local_fee = LocalFee.objects.create(
            polCd='CNSHK',
            podCd='THBKK',
            carriercd='CON',
            name='一致性测试费用',
            price_20gp=Decimal('100.00'),
            currency='USD'
        )
        
        # 通过API验证数据一致性
        # 1. 船期查询
        response = self.client.get('/api/schedules/', {
            'polCd': 'CNSHK',
            'podCd': 'THBKK',
            'carriercd': 'CON'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # 2. 船舶信息查询
        response = self.client.get('/api/vessel-info/', {
            'polCd': 'CNSHK',
            'podCd': 'THBKK',
            'carriercd': 'CON'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # 3. 本地费用查询
        response = self.client.get('/api/local-fees/local-fees/', {
            'polCd': 'CNSHK',
            'podCd': 'THBKK',
            'carriercd': 'CON'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        
        # 验证所有模块的数据都指向同一条航线
        schedule_data = response.data['data'][0]
        # 这里可以添加更多的一致性验证逻辑
