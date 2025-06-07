"""
船期管理API测试用例
测试船舶航线管理、船舶额外信息管理、共舱分组查询等API功能
"""
import json
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from authentication.models import Permission, Role
from schedules.models import VesselSchedule, VesselInfoFromCompany

User = get_user_model()


class VesselScheduleAPITest(APITestCase):
    """船舶航线API测试"""

    def setUp(self):
        """测试前准备"""
        self.client = APIClient()

        # 创建测试用户和权限
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123'
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
        self.update_permission = Permission.objects.create(
            code='vessel_schedule.update',
            name='船期更新',
            category='船期管理'
        )
        self.delete_permission = Permission.objects.create(
            code='vessel_schedule.delete',
            name='船期删除',
            category='船期管理'
        )

        # 创建角色并分配权限
        self.role = Role.objects.create(
            name='船期管理员',
            description='船期管理员角色'
        )
        self.role.permissions.add(
            self.list_permission,
            self.create_permission,
            self.update_permission,
            self.delete_permission
        )
        self.user.roles.add(self.role)

        # 测试数据
        self.schedule_data = {
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

        # 创建测试记录
        self.schedule = VesselSchedule.objects.create(
            polCd='CNSHA',
            podCd='USNYC',
            vessel='TEST_VESSEL',
            voyage='TEST001',
            data_version=20250527,
            carriercd='TEST',
            fetch_timestamp=1716825600,
            fetch_date=timezone.now(),
            pol='上海',
            pod='纽约',
            eta='2025-06-15',
            etd='2025-05-20',
            status=1
        )

        self.list_url = '/api/schedules/'
        self.detail_url = f'/api/schedules/{self.schedule.id}/'

    def test_get_schedule_list_with_permission(self):
        """测试有权限获取船舶航线列表"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['vessel'], 'TEST_VESSEL')

    def test_get_schedule_list_without_permission(self):
        """测试无权限获取船舶航线列表"""
        # 移除用户权限
        self.user.roles.clear()
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_schedule_list_unauthenticated(self):
        """测试未认证获取船舶航线列表"""
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_schedule_success(self):
        """测试成功创建船舶航线"""
        self.client.force_authenticate(user=self.user)

        new_data = self.schedule_data.copy()
        new_data['voyage'] = 'TEST002'

        response = self.client.post(self.list_url, new_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['vessel'], 'TEST_VESSEL')
        self.assertEqual(response.data['voyage'], 'TEST002')

    def test_create_schedule_duplicate(self):
        """测试创建重复船舶航线"""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.list_url, self.schedule_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_schedule_detail(self):
        """测试获取船舶航线详情"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.schedule.id)
        self.assertEqual(response.data['vessel'], 'TEST_VESSEL')

    def test_update_schedule_success(self):
        """测试成功更新船舶航线"""
        self.client.force_authenticate(user=self.user)

        update_data = {
            'polCd': 'CNSHA',
            'podCd': 'USNYC',
            'vessel': 'UPDATED_VESSEL',
            'voyage': 'TEST001',
            'data_version': 20250527,
            'carriercd': 'TEST',
            'fetch_timestamp': 1716825600,
            'fetch_date': timezone.now().isoformat(),
            'pol': '上海',
            'pod': '纽约',
            'eta': '2025-06-16',
            'etd': '2025-05-21'
        }

        response = self.client.put(self.detail_url, update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['vessel'], 'UPDATED_VESSEL')
        self.assertEqual(response.data['eta'], '2025-06-16')

    def test_delete_schedule_success(self):
        """测试成功删除船舶航线"""
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # 验证记录已被删除
        self.assertFalse(VesselSchedule.objects.filter(id=self.schedule.id).exists())

    def test_filter_schedules_by_params(self):
        """测试通过参数过滤船舶航线"""
        # 创建更多测试数据
        VesselSchedule.objects.create(
            polCd='CNSHK',
            podCd='THBKK',
            vessel='ANOTHER_VESSEL',
            voyage='TEST003',
            data_version=20250527,
            carriercd='MSK',
            fetch_timestamp=1716825600,
            fetch_date=timezone.now(),
            status=1
        )

        self.client.force_authenticate(user=self.user)

        # 按polCd过滤
        response = self.client.get(self.list_url, {'polCd': 'CNSHA'})
        self.assertEqual(len(response.data['results']), 1)

        # 按carriercd过滤
        response = self.client.get(self.list_url, {'carriercd': 'MSK'})
        self.assertEqual(len(response.data['results']), 1)

        # 按status过滤
        response = self.client.get(self.list_url, {'status': 1})
        self.assertEqual(len(response.data['results']), 2)

    def test_search_schedules(self):
        """测试搜索船舶航线"""
        self.client.force_authenticate(user=self.user)

        # 按船名搜索
        response = self.client.get(self.list_url, {'search': 'TEST_VESSEL'})
        self.assertEqual(len(response.data['results']), 1)

        # 按航次搜索
        response = self.client.get(self.list_url, {'search': 'TEST001'})
        self.assertEqual(len(response.data['results']), 1)

        # 搜索不存在的内容
        response = self.client.get(self.list_url, {'search': 'NONEXISTENT'})
        self.assertEqual(len(response.data['results']), 0)


class VesselInfoAPITest(APITestCase):
    """船舶额外信息API测试"""

    def setUp(self):
        """测试前准备"""
        self.client = APIClient()

        # 创建测试用户和权限
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123'
        )

        # 创建权限
        self.list_permission = Permission.objects.create(
            code='vessel_info.list',
            name='船舶信息列表',
            category='船舶信息'
        )
        self.create_permission = Permission.objects.create(
            code='vessel_info.create',
            name='船舶信息创建',
            category='船舶信息'
        )

        # 创建角色并分配权限
        self.role = Role.objects.create(
            name='船舶信息管理员',
            description='船舶信息管理员角色'
        )
        self.role.permissions.add(self.list_permission, self.create_permission)
        self.user.roles.add(self.role)

        # 测试数据
        self.vessel_info_data = {
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

        # 创建测试记录
        self.vessel_info = VesselInfoFromCompany.objects.create(
            carriercd='TEST',
            polCd='CNSHA',
            podCd='USNYC',
            vessel='TEST_VESSEL',
            voyage='TEST001',
            gp_20='100',
            hq_40='50',
            cut_off_time='2025-05-18 18:00',
            price=Decimal('4500.00')
        )

        self.list_url = '/api/vessel-info/'
        self.detail_url = f'/api/vessel-info/{self.vessel_info.id}/'
        self.bulk_create_url = '/api/vessel-info/bulk-create/'
        self.query_url = '/api/vessel-info/query/'

    def test_get_vessel_info_list(self):
        """测试获取船舶信息列表"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_vessel_info_success(self):
        """测试成功创建船舶信息"""
        self.client.force_authenticate(user=self.user)

        new_data = self.vessel_info_data.copy()
        new_data['voyage'] = 'TEST002'

        response = self.client.post(self.list_url, new_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['voyage'], 'TEST002')

    def test_bulk_create_vessel_info(self):
        """测试批量创建船舶信息"""
        self.client.force_authenticate(user=self.user)

        bulk_data = {
            'items': [
                {
                    'carriercd': 'MSK',
                    'polCd': 'CNSHA',
                    'podCd': 'USNYC',
                    'vessel': 'MSK_VESSEL',
                    'voyage': 'MSK001',
                    'price': '4200.00'
                },
                {
                    'carriercd': 'ONE',
                    'polCd': 'CNSHA',
                    'podCd': 'USNYC',
                    'vessel': 'ONE_VESSEL',
                    'voyage': 'ONE001',
                    'price': '4300.00'
                }
            ]
        }

        response = self.client.post(self.bulk_create_url, bulk_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertEqual(len(response.data['data']), 2)

    def test_query_vessel_info(self):
        """测试查询特定船舶信息"""
        self.client.force_authenticate(user=self.user)

        query_params = {
            'vessel': 'TEST_VESSEL',
            'voyage': 'TEST001',
            'carriercd': 'TEST',
            'polCd': 'CNSHA',
            'podCd': 'USNYC'
        }

        response = self.client.get(self.query_url, query_params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['vessel'], 'TEST_VESSEL')

    def test_query_vessel_info_missing_params(self):
        """测试查询船舶信息缺少必填参数"""
        self.client.force_authenticate(user=self.user)

        # 缺少必填参数
        response = self.client.get(self.query_url, {'vessel': 'TEST_VESSEL'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class CabinGroupingAPITest(APITestCase):
    """共舱分组API测试"""

    def setUp(self):
        """测试前准备"""
        self.client = APIClient()

        # 清理可能存在的测试数据
        VesselSchedule.objects.all().delete()
        VesselInfoFromCompany.objects.all().delete()

        # 创建测试用户和权限
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123'
        )

        # 注意：前台API只需要IsAuthenticated，不需要特定权限
        # 这里创建权限只是为了测试权限系统本身

        # 创建测试数据
        self.schedule1 = VesselSchedule.objects.create(
            polCd='CNSHA',
            podCd='USNYC',
            vessel='VESSEL_1',
            voyage='V001',
            data_version=20250527,
            carriercd='MSK',
            fetch_timestamp=1716825600,
            fetch_date=timezone.now(),
            routeEtd='3',
            totalDuration='26',
            shareCabins=json.dumps([
                {'carrierCd': 'MSK'},
                {'carrierCd': 'ONE'}
            ]),
            status=1
        )

        self.schedule2 = VesselSchedule.objects.create(
            polCd='CNSHA',
            podCd='USNYC',
            vessel='VESSEL_2',
            voyage='V002',
            data_version=20250527,
            carriercd='ONE',
            fetch_timestamp=1716825600,
            fetch_date=timezone.now(),
            routeEtd='3',
            totalDuration='26',
            shareCabins=json.dumps([
                {'carrierCd': 'MSK'},
                {'carrierCd': 'ONE'}
            ]),
            status=1
        )

        # 创建对应的船舶信息（使用get_or_create避免重复）
        VesselInfoFromCompany.objects.get_or_create(
            carriercd='MSK',
            polCd='CNSHA',
            podCd='USNYC',
            vessel='VESSEL_1',
            voyage='V001',
            defaults={
                'gp_20': '100',
                'hq_40': '50',
                'price': Decimal('4500.00')
            }
        )

        VesselInfoFromCompany.objects.get_or_create(
            carriercd='ONE',
            polCd='CNSHA',
            podCd='USNYC',
            vessel='VESSEL_2',
            voyage='V002',
            defaults={
                'gp_20': '80',
                'hq_40': '40',
                'price': Decimal('4200.00')
            }
        )

        self.cabin_grouping_url = '/api/schedules/cabin-grouping-with-info/'
        self.basic_grouping_url = '/api/schedules/cabin-grouping/'

    def test_cabin_grouping_with_info_success(self):
        """测试共舱分组查询（含额外信息）成功"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.cabin_grouping_url, {
            'polCd': 'CNSHA',
            'podCd': 'USNYC'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertIn('groups', response.data['data'])

        # 验证分组数据
        groups = response.data['data']['groups']
        self.assertEqual(len(groups), 1)  # 应该有一个分组

        group = groups[0]
        self.assertEqual(group['cabins_count'], 2)
        self.assertIn('MSK', group['carrier_codes'])
        self.assertIn('ONE', group['carrier_codes'])
        self.assertEqual(len(group['schedules']), 2)

    def test_cabin_grouping_missing_params(self):
        """测试共舱分组查询缺少必填参数"""
        self.client.force_authenticate(user=self.user)

        # 缺少podCd
        response = self.client.get(self.cabin_grouping_url, {'polCd': 'CNSHA'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('success', response.data)
        self.assertFalse(response.data['success'])

    def test_basic_cabin_grouping(self):
        """测试基础共舱分组查询"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.basic_grouping_url, {
            'polCd': 'CNSHA',
            'podCd': 'USNYC'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertIn('groups', response.data['data'])

    def test_cabin_grouping_no_data(self):
        """测试查询无数据的路线"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.cabin_grouping_url, {
            'polCd': 'CNPKG',
            'podCd': 'USLAX'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']['groups']), 0)

    def test_cabin_grouping_without_authentication(self):
        """测试未认证用户进行共舱分组查询"""
        # 不进行认证
        response = self.client.get(self.cabin_grouping_url, {
            'polCd': 'CNSHA',
            'podCd': 'USNYC'
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
