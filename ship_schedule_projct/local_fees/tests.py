"""
本地费用测试
使用pytest进行测试
"""
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import LocalFee

User = get_user_model()


class LocalFeeModelTest(TestCase):
    """LocalFee模型测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.local_fee_data = {
            'polCd': 'CNSHK',
            'podCd': 'THBKK',
            'carriercd': 'MSK',
            'name': '起运港码头费',
            'unit_name': '箱型',
            'price_20gp': Decimal('760.00'),
            'price_40gp': Decimal('1287.00'),
            'price_40hq': Decimal('1287.00'),
            'currency': 'CNY'
        }
    
    def test_create_local_fee(self):
        """测试创建本地费用"""
        local_fee = LocalFee.objects.create(**self.local_fee_data)
        self.assertEqual(local_fee.polCd, 'CNSHK')
        self.assertEqual(local_fee.podCd, 'THBKK')
        self.assertEqual(local_fee.carriercd, 'MSK')
        self.assertEqual(local_fee.name, '起运港码头费')
        self.assertEqual(local_fee.price_20gp, Decimal('760.00'))
        self.assertEqual(local_fee.currency, 'CNY')
    
    def test_local_fee_str(self):
        """测试字符串表示"""
        local_fee = LocalFee.objects.create(**self.local_fee_data)
        expected_str = "MSK [CNSHK-THBKK] 起运港码头费"
        self.assertEqual(str(local_fee), expected_str)
    
    def test_unique_together_constraint(self):
        """测试唯一性约束"""
        LocalFee.objects.create(**self.local_fee_data)
        
        # 尝试创建相同的记录应该失败
        with self.assertRaises(Exception):
            LocalFee.objects.create(**self.local_fee_data)
    
    def test_optional_fields(self):
        """测试可选字段"""
        minimal_data = {
            'polCd': 'CNSHK',
            'podCd': 'THBKK',
            'name': '保安费',
            'price_per_bill': Decimal('50.00'),
            'currency': 'USD'
        }
        local_fee = LocalFee.objects.create(**minimal_data)
        self.assertIsNone(local_fee.carriercd)
        self.assertEqual(local_fee.unit_name, '箱型')  # 默认值
        self.assertIsNone(local_fee.price_20gp)


class LocalFeeAPITest(APITestCase):
    """LocalFee API测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.client = APIClient()
        
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # 测试数据
        self.local_fee_data = {
            'polCd': 'CNSHK',
            'podCd': 'THBKK',
            'carriercd': 'MSK',
            'name': '起运港码头费',
            'unit_name': '箱型',
            'price_20gp': '760.00',
            'price_40gp': '1287.00',
            'price_40hq': '1287.00',
            'currency': 'CNY'
        }
        
        # 创建测试记录
        self.local_fee = LocalFee.objects.create(
            polCd='CNSHK',
            podCd='THBKK',
            carriercd='MSK',
            name='起运港码头费',
            unit_name='箱型',
            price_20gp=Decimal('760.00'),
            price_40gp=Decimal('1287.00'),
            price_40hq=Decimal('1287.00'),
            currency='CNY'
        )
    
    def test_create_local_fee(self):
        """测试创建本地费用API"""
        url = '/local_fees/api/local-fees/'
        data = {
            'polCd': 'CNSHA',
            'podCd': 'USLAX',
            'carriercd': 'COSCO',
            'name': '目的港码头费',
            'unit_name': '箱型',
            'price_20gp': '850.00',
            'price_40gp': '1400.00',
            'currency': 'USD'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['data']['polCd'], 'CNSHA')
        self.assertEqual(response.data['data']['name'], '目的港码头费')
    
    def test_list_local_fees(self):
        """测试获取本地费用列表API"""
        url = '/local_fees/api/local-fees/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], '起运港码头费')
    
    def test_retrieve_local_fee(self):
        """测试获取单个本地费用API"""
        url = f'/local_fees/api/local-fees/{self.local_fee.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['data']['id'], self.local_fee.id)
        self.assertEqual(response.data['data']['name'], '起运港码头费')
    
    def test_update_local_fee(self):
        """测试更新本地费用API"""
        url = f'/local_fees/api/local-fees/{self.local_fee.id}/'
        data = {
            'polCd': 'CNSHK',
            'podCd': 'THBKK',
            'carriercd': 'MSK',
            'name': '起运港码头费（更新）',
            'unit_name': '箱型',
            'price_20gp': '800.00',
            'price_40gp': '1300.00',
            'price_40hq': '1300.00',
            'currency': 'CNY'
        }
        
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['data']['name'], '起运港码头费（更新）')
        self.assertEqual(response.data['data']['price_20gp'], '800.00')
    
    def test_delete_local_fee(self):
        """测试删除本地费用API"""
        url = f'/local_fees/api/local-fees/{self.local_fee.id}/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['message'], '本地费用删除成功')
        
        # 验证记录已被删除
        self.assertFalse(LocalFee.objects.filter(id=self.local_fee.id).exists())
    
    def test_query_fees_api(self):
        """测试查询费用API"""
        # 创建更多测试数据
        LocalFee.objects.create(
            polCd='CNSHK',
            podCd='THBKK',
            carriercd='MSK',
            name='保安费',
            unit_name='票',
            price_per_bill=Decimal('50.00'),
            currency='USD'
        )
        
        url = '/local_fees/api/local-fees/query/'
        response = self.client.get(url, {
            'polCd': 'CNSHK',
            'podCd': 'THBKK',
            'carriercd': 'MSK'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(len(response.data['data']), 2)
        
        # 验证返回格式
        first_item = response.data['data'][0]
        self.assertIn('id', first_item)
        self.assertIn('名称', first_item)
        self.assertIn('单位', first_item)
        self.assertIn('20GP', first_item)
        self.assertIn('40GP', first_item)
        self.assertIn('40HQ', first_item)
        self.assertIn('单票价格', first_item)
        self.assertIn('币种', first_item)
    
    def test_query_fees_missing_params(self):
        """测试查询费用API缺少必填参数"""
        url = '/local_fees/api/local-fees/query/'
        response = self.client.get(url, {'polCd': 'CNSHK'})  # 缺少podCd
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'error')
        self.assertIn('必填参数', response.data['message'])
    
    def test_filter_by_params(self):
        """测试通过参数过滤"""
        # 创建不同的测试数据
        LocalFee.objects.create(
            polCd='CNSHA',
            podCd='USLAX',
            carriercd='COSCO',
            name='目的港码头费',
            price_20gp=Decimal('900.00'),
            currency='USD'
        )
        
        url = '/local_fees/api/local-fees/'
        
        # 按polCd过滤
        response = self.client.get(url, {'polCd': 'CNSHK'})
        self.assertEqual(len(response.data['data']), 1)
        
        # 按carriercd过滤
        response = self.client.get(url, {'carriercd': 'COSCO'})
        self.assertEqual(len(response.data['data']), 1)
    
    def test_unauthorized_access(self):
        """测试未授权访问"""
        self.client.force_authenticate(user=None)
        url = '/local_fees/api/local-fees/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# @pytest.mark.django_db
class TestLocalFeeWithPytest:
    """使用pytest的测试类"""
    
    def test_local_fee_creation(self):
        """测试本地费用创建"""
        local_fee = LocalFee.objects.create(
            polCd='CNSHK',
            podCd='THBKK',
            carriercd='MSK',
            name='起运港码头费',
            price_20gp=Decimal('760.00'),
            currency='CNY'
        )
        assert local_fee.polCd == 'CNSHK'
        assert local_fee.name == '起运港码头费'
        assert local_fee.price_20gp == Decimal('760.00')
    
    def test_local_fee_query(self):
        """测试本地费用查询"""
        # 创建测试数据
        LocalFee.objects.create(
            polCd='CNSHK',
            podCd='THBKK',
            carriercd='MSK',
            name='起运港码头费',
            price_20gp=Decimal('760.00'),
            currency='CNY'
        )
        
        LocalFee.objects.create(
            polCd='CNSHK',
            podCd='THBKK',
            carriercd='MSK',
            name='保安费',
            price_per_bill=Decimal('50.00'),
            currency='USD'
        )
        
        # 查询测试
        fees = LocalFee.objects.filter(polCd='CNSHK', podCd='THBKK')
        assert fees.count() == 2
        
        fees_with_carrier = LocalFee.objects.filter(
            polCd='CNSHK', 
            podCd='THBKK', 
            carriercd='MSK'
        )
        assert fees_with_carrier.count() == 2
    
    def test_local_fee_update(self):
        """测试本地费用更新"""
        local_fee = LocalFee.objects.create(
            polCd='CNSHK',
            podCd='THBKK',
            carriercd='MSK',
            name='起运港码头费',
            price_20gp=Decimal('760.00'),
            currency='CNY'
        )
        
        # 更新价格
        local_fee.price_20gp = Decimal('800.00')
        local_fee.save()
        
        # 验证更新
        updated_fee = LocalFee.objects.get(id=local_fee.id)
        assert updated_fee.price_20gp == Decimal('800.00')
    
    def test_local_fee_delete(self):
        """测试本地费用删除"""
        local_fee = LocalFee.objects.create(
            polCd='CNSHK',
            podCd='THBKK',
            carriercd='MSK',
            name='起运港码头费',
            price_20gp=Decimal('760.00'),
            currency='CNY'
        )
        
        fee_id = local_fee.id
        local_fee.delete()
        
        # 验证删除
        assert not LocalFee.objects.filter(id=fee_id).exists()


# 运行测试的命令示例
"""
运行所有测试:
python manage.py test local_fees

运行pytest测试:
pytest local_fees/tests.py -v

运行特定测试:
pytest local_fees/tests.py::TestLocalFeeWithPytest::test_local_fee_creation -v
""" 