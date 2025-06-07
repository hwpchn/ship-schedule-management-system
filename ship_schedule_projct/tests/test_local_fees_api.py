"""
本地费用API测试用例
测试本地费用管理相关API功能
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from authentication.models import Permission, Role
from local_fees.models import LocalFee

User = get_user_model()


class LocalFeeAPITest(APITestCase):
    """本地费用API测试"""
    
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
            code='local_fee.list',
            name='本地费用列表',
            category='本地费用'
        )
        self.create_permission = Permission.objects.create(
            code='local_fee.create',
            name='本地费用创建',
            category='本地费用'
        )
        self.update_permission = Permission.objects.create(
            code='local_fee.update',
            name='本地费用更新',
            category='本地费用'
        )
        self.delete_permission = Permission.objects.create(
            code='local_fee.delete',
            name='本地费用删除',
            category='本地费用'
        )
        self.query_permission = Permission.objects.create(
            code='local_fee.query',
            name='本地费用查询',
            category='本地费用'
        )
        
        # 创建角色并分配权限
        self.role = Role.objects.create(
            name='本地费用管理员',
            description='本地费用管理员角色'
        )
        self.role.permissions.add(
            self.list_permission,
            self.create_permission,
            self.update_permission,
            self.delete_permission,
            self.query_permission
        )
        self.user.roles.add(self.role)
        
        # 测试数据
        self.local_fee_data = {
            'polCd': 'CNSHA',
            'podCd': 'USNYC',
            'carriercd': 'TEST',
            'name': '起运港码头费',
            'unit_name': '箱型',
            'price_20gp': '760.00',
            'price_40gp': '1287.00',
            'price_40hq': '1287.00',
            'currency': 'CNY'
        }
        
        # 创建测试记录
        self.local_fee = LocalFee.objects.create(
            polCd='CNSHA',
            podCd='USNYC',
            carriercd='TEST',
            name='起运港码头费',
            unit_name='箱型',
            price_20gp=Decimal('760.00'),
            price_40gp=Decimal('1287.00'),
            price_40hq=Decimal('1287.00'),
            currency='CNY'
        )
        
        self.list_url = '/api/local-fees/local-fees/'
        self.detail_url = f'/api/local-fees/local-fees/{self.local_fee.id}/'
        self.query_url = '/api/local-fees/local-fees/query/'
    
    def test_get_local_fee_list_with_permission(self):
        """测试有权限获取本地费用列表"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('data', response.data)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], '起运港码头费')
    
    def test_get_local_fee_list_without_permission(self):
        """测试无权限获取本地费用列表"""
        # 移除用户权限
        self.user.roles.clear()
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_local_fee_list_unauthenticated(self):
        """测试未认证获取本地费用列表"""
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_local_fee_success(self):
        """测试成功创建本地费用"""
        self.client.force_authenticate(user=self.user)
        
        new_data = self.local_fee_data.copy()
        new_data['name'] = '目的港码头费'
        new_data['currency'] = 'USD'
        
        response = self.client.post(self.list_url, new_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['data']['name'], '目的港码头费')
        self.assertEqual(response.data['data']['currency'], 'USD')
    
    def test_create_local_fee_duplicate(self):
        """测试创建重复本地费用"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(self.list_url, self.local_fee_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'error')
    
    def test_create_local_fee_per_bill(self):
        """测试创建按票计费的本地费用"""
        self.client.force_authenticate(user=self.user)
        
        bill_fee_data = {
            'polCd': 'CNSHA',
            'podCd': 'USNYC',
            'carriercd': 'TEST',
            'name': '保安费',
            'unit_name': '票',
            'price_per_bill': '50.00',
            'currency': 'USD'
        }
        
        response = self.client.post(self.list_url, bill_fee_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['name'], '保安费')
        self.assertEqual(response.data['data']['unit_name'], '票')
        self.assertEqual(response.data['data']['price_per_bill'], '50.00')
    
    def test_get_local_fee_detail(self):
        """测试获取本地费用详情"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['data']['id'], self.local_fee.id)
        self.assertEqual(response.data['data']['name'], '起运港码头费')
    
    def test_update_local_fee_success(self):
        """测试成功更新本地费用"""
        self.client.force_authenticate(user=self.user)
        
        update_data = self.local_fee_data.copy()
        update_data['name'] = '起运港码头费（更新）'
        update_data['price_20gp'] = '800.00'
        
        response = self.client.put(self.detail_url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['data']['name'], '起运港码头费（更新）')
        self.assertEqual(response.data['data']['price_20gp'], '800.00')
    
    def test_partial_update_local_fee(self):
        """测试部分更新本地费用"""
        self.client.force_authenticate(user=self.user)
        
        update_data = {
            'price_20gp': '850.00',
            'price_40gp': '1350.00'
        }
        
        response = self.client.patch(self.detail_url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['data']['price_20gp'], '850.00')
        self.assertEqual(response.data['data']['price_40gp'], '1350.00')
        # 其他字段应保持不变
        self.assertEqual(response.data['data']['name'], '起运港码头费')
    
    def test_delete_local_fee_success(self):
        """测试成功删除本地费用"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.delete(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('删除成功', response.data['message'])
        
        # 验证记录已被删除
        self.assertFalse(LocalFee.objects.filter(id=self.local_fee.id).exists())
    
    def test_query_local_fees_success(self):
        """测试成功查询本地费用（前台格式）"""
        # 创建更多测试数据
        LocalFee.objects.create(
            polCd='CNSHA',
            podCd='USNYC',
            carriercd='TEST',
            name='保安费',
            unit_name='票',
            price_per_bill=Decimal('50.00'),
            currency='USD'
        )
        
        LocalFee.objects.create(
            polCd='CNSHA',
            podCd='USNYC',
            carriercd='TEST',
            name='文件费',
            unit_name='票',
            price_per_bill=Decimal('25.00'),
            currency='USD'
        )
        
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(self.query_url, {
            'polCd': 'CNSHA',
            'podCd': 'USNYC',
            'carriercd': 'TEST'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(len(response.data['data']), 3)
        
        # 验证返回格式（中文字段名）
        first_item = response.data['data'][0]
        self.assertIn('id', first_item)
        self.assertIn('名称', first_item)
        self.assertIn('单位', first_item)
        self.assertIn('20GP', first_item)
        self.assertIn('40GP', first_item)
        self.assertIn('40HQ', first_item)
        self.assertIn('单票价格', first_item)
        self.assertIn('币种', first_item)
        
        # 验证数据内容
        container_fee = next(item for item in response.data['data'] if item['名称'] == '起运港码头费')
        self.assertEqual(container_fee['单位'], '箱型')
        self.assertEqual(container_fee['20GP'], '760.00')
        self.assertEqual(container_fee['币种'], 'CNY')
        
        bill_fee = next(item for item in response.data['data'] if item['名称'] == '保安费')
        self.assertEqual(bill_fee['单位'], '票')
        self.assertEqual(bill_fee['单票价格'], '50.00')
        self.assertEqual(bill_fee['币种'], 'USD')
    
    def test_query_local_fees_missing_params(self):
        """测试查询本地费用缺少必填参数"""
        self.client.force_authenticate(user=self.user)
        
        # 缺少podCd
        response = self.client.get(self.query_url, {
            'polCd': 'CNSHA',
            'carriercd': 'TEST'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'error')
        self.assertIn('必填参数', response.data['message'])
    
    def test_query_local_fees_no_data(self):
        """测试查询无数据的本地费用"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(self.query_url, {
            'polCd': 'CNPKG',
            'podCd': 'USLAX',
            'carriercd': 'NONEXISTENT'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(len(response.data['data']), 0)
    
    def test_filter_local_fees_by_params(self):
        """测试通过参数过滤本地费用"""
        # 创建不同路线的费用
        LocalFee.objects.create(
            polCd='CNSHK',
            podCd='THBKK',
            carriercd='MSK',
            name='起运港码头费',
            price_20gp=Decimal('800.00'),
            currency='CNY'
        )
        
        LocalFee.objects.create(
            polCd='CNSHA',
            podCd='USLAX',
            carriercd='COSCO',
            name='目的港码头费',
            price_20gp=Decimal('900.00'),
            currency='USD'
        )
        
        self.client.force_authenticate(user=self.user)
        
        # 按polCd过滤
        response = self.client.get(self.list_url, {'polCd': 'CNSHA'})
        self.assertEqual(len(response.data['data']), 2)  # 原有1个 + 新增1个
        
        # 按carriercd过滤
        response = self.client.get(self.list_url, {'carriercd': 'MSK'})
        self.assertEqual(len(response.data['data']), 1)
        
        # 按currency过滤
        response = self.client.get(self.list_url, {'currency': 'USD'})
        self.assertEqual(len(response.data['data']), 1)
    
    def test_search_local_fees(self):
        """测试搜索本地费用"""
        # 创建更多测试数据
        LocalFee.objects.create(
            polCd='CNSHA',
            podCd='USNYC',
            carriercd='TEST',
            name='燃油附加费',
            price_20gp=Decimal('120.00'),
            currency='USD'
        )
        
        self.client.force_authenticate(user=self.user)
        
        # 按费用名称搜索
        response = self.client.get(self.list_url, {'search': '码头费'})
        self.assertEqual(len(response.data['data']), 1)
        
        # 按港口代码搜索
        response = self.client.get(self.list_url, {'search': 'CNSHA'})
        self.assertEqual(len(response.data['data']), 2)
        
        # 按船公司搜索
        response = self.client.get(self.list_url, {'search': 'TEST'})
        self.assertEqual(len(response.data['data']), 2)
    
    def test_create_local_fee_validation_errors(self):
        """测试创建本地费用的验证错误"""
        self.client.force_authenticate(user=self.user)
        
        # 缺少必填字段
        invalid_data = {
            'polCd': 'CNSHA',
            # 缺少podCd
            'name': '测试费用'
        }
        
        response = self.client.post(self.list_url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'error')
        self.assertIn('podCd', response.data['message'])
    
    def test_create_local_fee_negative_price(self):
        """测试创建负价格的本地费用"""
        self.client.force_authenticate(user=self.user)
        
        invalid_data = self.local_fee_data.copy()
        invalid_data['name'] = '负价格费用'
        invalid_data['price_20gp'] = '-100.00'
        
        response = self.client.post(self.list_url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'error')
    
    def test_local_fee_pagination(self):
        """测试本地费用分页"""
        # 创建多个费用记录
        for i in range(25):
            LocalFee.objects.create(
                polCd='CNSHA',
                podCd='USNYC',
                carriercd=f'CARRIER_{i}',
                name=f'费用_{i}',
                price_20gp=Decimal(f'{100 + i}.00'),
                currency='USD'
            )
        
        self.client.force_authenticate(user=self.user)
        
        # 测试第一页
        response = self.client.get(self.list_url, {'page': 1, 'page_size': 10})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 10)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        
        # 测试第二页
        response = self.client.get(self.list_url, {'page': 2, 'page_size': 10})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 10)


class LocalFeePermissionTest(APITestCase):
    """本地费用权限测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        
        # 创建不同权限的用户
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        
        self.readonly_user = User.objects.create_user(
            email='readonly@example.com',
            password='readonlypass123'
        )
        
        # 创建只读权限
        readonly_permission = Permission.objects.create(
            code='local_fee.list',
            name='本地费用列表',
            category='本地费用'
        )
        
        readonly_role = Role.objects.create(
            name='只读用户',
            description='只读用户角色'
        )
        readonly_role.permissions.add(readonly_permission)
        self.readonly_user.roles.add(readonly_role)
        
        # 创建测试数据
        self.local_fee = LocalFee.objects.create(
            polCd='CNSHA',
            podCd='USNYC',
            carriercd='TEST',
            name='测试费用',
            price_20gp=Decimal('100.00'),
            currency='USD'
        )
        
        self.list_url = '/api/local-fees/local-fees/'
        self.detail_url = f'/api/local-fees/local-fees/{self.local_fee.id}/'
    
    def test_admin_has_all_permissions(self):
        """测试管理员拥有所有权限"""
        self.client.force_authenticate(user=self.admin_user)
        
        # 列表权限
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 创建权限
        data = {
            'polCd': 'CNSHA',
            'podCd': 'USNYC',
            'carriercd': 'ADMIN',
            'name': '管理员费用',
            'price_20gp': '200.00',
            'currency': 'USD'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 更新权限
        response = self.client.patch(self.detail_url, {'price_20gp': '150.00'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 删除权限
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_readonly_user_limited_permissions(self):
        """测试只读用户权限限制"""
        self.client.force_authenticate(user=self.readonly_user)
        
        # 可以查看列表
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 不能创建
        data = {
            'polCd': 'CNSHA',
            'podCd': 'USNYC',
            'carriercd': 'READONLY',
            'name': '只读用户费用',
            'price_20gp': '200.00',
            'currency': 'USD'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 不能更新
        response = self.client.patch(self.detail_url, {'price_20gp': '150.00'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 不能删除
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
