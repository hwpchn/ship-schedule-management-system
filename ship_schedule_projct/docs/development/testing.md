# 测试指南

## 📋 概述

本指南详细说明船舶航线管理系统的测试策略、测试框架使用方法和测试用例编写规范，确保代码质量和系统稳定性。

## 🎯 测试策略

### 测试金字塔
```
    /\
   /  \     E2E测试 (少量)
  /____\    
 /      \   集成测试 (适量)
/________\  单元测试 (大量)
```

### 测试类型
- **单元测试** - 测试单个函数或方法
- **集成测试** - 测试模块间交互
- **API测试** - 测试API接口
- **功能测试** - 测试完整业务流程
- **性能测试** - 测试系统性能

### 测试覆盖率目标
- **总体覆盖率**: ≥90%
- **核心业务逻辑**: 100%
- **API接口**: 100%
- **权限控制**: 100%
- **数据模型**: ≥95%

## 🧪 测试框架

### Django TestCase
```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from authentication.models import Permission, Role

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
    
    def test_create_user_without_email_should_fail(self):
        """测试不提供邮箱创建用户应该失败"""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='',
                password='testpass123'
            )
    
    def tearDown(self):
        """测试后清理"""
        User.objects.all().delete()
```

### API测试
```python
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

class AuthenticationAPITest(APITestCase):
    """认证API测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.login_url = reverse('authentication:login')
        self.me_url = reverse('authentication:user_info')
    
    def test_user_login_success(self):
        """测试用户登录成功"""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
    
    def test_user_login_with_invalid_credentials_should_fail(self):
        """测试使用无效凭据登录应该失败"""
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_get_user_info_with_authentication(self):
        """测试获取用户信息（已认证）"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.me_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['email'], 'test@example.com')
    
    def test_get_user_info_without_authentication_should_fail(self):
        """测试获取用户信息（未认证）应该失败"""
        response = self.client.get(self.me_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
```

## 🔧 测试工具

### 测试运行
```bash
# 运行所有测试
python manage.py test

# 运行特定应用测试
python manage.py test authentication
python manage.py test schedules
python manage.py test local_fees

# 运行特定测试类
python manage.py test authentication.tests.UserModelTest

# 运行特定测试方法
python manage.py test authentication.tests.UserModelTest.test_create_user_success

# 详细输出
python manage.py test --verbosity=2

# 保留测试数据库
python manage.py test --keepdb

# 并行测试
python manage.py test --parallel
```

### 测试覆盖率
```bash
# 安装coverage
pip install coverage

# 运行测试并收集覆盖率
coverage run --source='.' manage.py test

# 查看覆盖率报告
coverage report

# 生成HTML报告
coverage html
open htmlcov/index.html

# 查看特定文件覆盖率
coverage report authentication/models.py
```

### 测试数据库
```python
# settings.py中配置测试数据库
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # 使用内存数据库加速测试
    }
}

# 或使用专门的测试数据库
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
```

## 📝 测试用例编写

### 模型测试
```python
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
        }
    
    def test_create_vessel_schedule_success(self):
        """测试成功创建船舶航线"""
        schedule = VesselSchedule.objects.create(**self.schedule_data)
        
        self.assertEqual(schedule.polCd, 'CNSHA')
        self.assertEqual(schedule.podCd, 'USNYC')
        self.assertEqual(schedule.vessel, 'TEST_VESSEL')
        self.assertEqual(schedule.status, 1)  # 默认状态
    
    def test_vessel_schedule_str_representation(self):
        """测试船舶航线字符串表示"""
        schedule = VesselSchedule.objects.create(**self.schedule_data)
        expected_str = f"{schedule.vessel} {schedule.voyage}: {schedule.pol}({schedule.polCd}) → {schedule.pod}({schedule.podCd})"
        
        self.assertEqual(str(schedule), expected_str)
    
    def test_unique_constraint_violation_should_fail(self):
        """测试违反唯一约束应该失败"""
        VesselSchedule.objects.create(**self.schedule_data)
        
        with self.assertRaises(IntegrityError):
            VesselSchedule.objects.create(**self.schedule_data)
```

### 视图测试
```python
class VesselScheduleViewTest(APITestCase):
    """船舶航线视图测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        # 创建权限和角色
        self.permission = Permission.objects.create(
            code='vessel_schedule.list',
            name='船期列表查看',
            category='船期管理'
        )
        
        self.role = Role.objects.create(
            name='测试角色',
            description='测试用角色'
        )
        self.role.permissions.add(self.permission)
        self.user.roles.add(self.role)
        
        # 创建测试数据
        self.schedule = VesselSchedule.objects.create(
            polCd='CNSHA',
            podCd='USNYC',
            vessel='TEST_VESSEL',
            voyage='TEST001',
            data_version=20250527,
            carriercd='TEST',
            fetch_timestamp=1716825600,
            fetch_date=timezone.now(),
        )
        
        self.list_url = reverse('schedules:vessel-schedule-list-create')
    
    def test_get_vessel_schedule_list_with_permission(self):
        """测试有权限获取船舶航线列表"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['vessel'], 'TEST_VESSEL')
    
    def test_get_vessel_schedule_list_without_permission_should_fail(self):
        """测试无权限获取船舶航线列表应该失败"""
        # 移除用户权限
        self.user.roles.clear()
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_vessel_schedule_list_without_authentication_should_fail(self):
        """测试未认证获取船舶航线列表应该失败"""
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
```

### 权限测试
```python
class PermissionSystemTest(TestCase):
    """权限系统测试"""
    
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
            name='测试角色',
            description='测试用角色'
        )
    
    def test_user_has_permission_through_role(self):
        """测试用户通过角色获得权限"""
        # 给角色分配权限
        self.role.permissions.add(self.permission1)
        
        # 给用户分配角色
        self.user.roles.add(self.role)
        
        # 检查权限
        self.assertTrue(self.user.has_permission('vessel_schedule.list'))
        self.assertFalse(self.user.has_permission('vessel_schedule.create'))
    
    def test_superuser_has_all_permissions(self):
        """测试超级用户拥有所有权限"""
        self.user.is_superuser = True
        self.user.save()
        
        self.assertTrue(self.user.has_permission('vessel_schedule.list'))
        self.assertTrue(self.user.has_permission('vessel_schedule.create'))
        self.assertTrue(self.user.has_permission('any.permission'))
    
    def test_get_all_permissions(self):
        """测试获取用户所有权限"""
        self.role.permissions.add(self.permission1, self.permission2)
        self.user.roles.add(self.role)
        
        permissions = self.user.get_all_permissions()
        
        self.assertIn('vessel_schedule.list', permissions)
        self.assertIn('vessel_schedule.create', permissions)
        self.assertEqual(len(permissions), 2)
```

## 🔍 测试数据管理

### 测试夹具(Fixtures)
```python
# fixtures/test_data.json
[
    {
        "model": "authentication.permission",
        "pk": 1,
        "fields": {
            "code": "vessel_schedule.list",
            "name": "船期列表查看",
            "category": "船期管理"
        }
    },
    {
        "model": "schedules.vesselschedule",
        "pk": 1,
        "fields": {
            "polCd": "CNSHA",
            "podCd": "USNYC",
            "vessel": "TEST_VESSEL",
            "voyage": "TEST001",
            "data_version": 20250527
        }
    }
]

# 在测试中使用夹具
class MyTestCase(TestCase):
    fixtures = ['test_data.json']
    
    def test_with_fixture_data(self):
        # 使用夹具中的数据
        schedule = VesselSchedule.objects.get(pk=1)
        self.assertEqual(schedule.vessel, 'TEST_VESSEL')
```

### 工厂模式
```python
# tests/factories.py
import factory
from django.contrib.auth import get_user_model
from authentication.models import Permission, Role
from schedules.models import VesselSchedule

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

class PermissionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Permission
    
    code = factory.Sequence(lambda n: f'permission.{n}')
    name = factory.Faker('sentence', nb_words=3)
    category = factory.Faker('word')

class VesselScheduleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VesselSchedule
    
    polCd = 'CNSHA'
    podCd = 'USNYC'
    vessel = factory.Faker('company')
    voyage = factory.Sequence(lambda n: f'V{n:03d}')
    data_version = 20250527
    carriercd = factory.Faker('company_suffix')

# 在测试中使用工厂
class MyTestCase(TestCase):
    def test_with_factory(self):
        user = UserFactory()
        schedule = VesselScheduleFactory(vessel='TEST_VESSEL')
        
        self.assertIsNotNone(user.email)
        self.assertEqual(schedule.vessel, 'TEST_VESSEL')
```

## 🚀 性能测试

### 数据库查询性能测试
```python
from django.test import TestCase
from django.test.utils import override_settings
from django.db import connection

class PerformanceTest(TestCase):
    """性能测试"""
    
    def setUp(self):
        """创建大量测试数据"""
        schedules = []
        for i in range(1000):
            schedules.append(VesselSchedule(
                polCd='CNSHA',
                podCd='USNYC',
                vessel=f'VESSEL_{i}',
                voyage=f'V{i:03d}',
                data_version=20250527,
                carriercd='TEST',
                fetch_timestamp=1716825600,
                fetch_date=timezone.now(),
            ))
        VesselSchedule.objects.bulk_create(schedules)
    
    def test_query_performance(self):
        """测试查询性能"""
        with self.assertNumQueries(1):
            # 应该只执行一次数据库查询
            list(VesselSchedule.objects.filter(polCd='CNSHA'))
    
    def test_api_response_time(self):
        """测试API响应时间"""
        import time
        
        self.client.force_authenticate(user=self.user)
        
        start_time = time.time()
        response = self.client.get('/api/schedules/')
        end_time = time.time()
        
        response_time = end_time - start_time
        self.assertLess(response_time, 1.0)  # 响应时间应小于1秒
        self.assertEqual(response.status_code, 200)
```

## 📊 测试报告

### 生成测试报告
```bash
# 安装pytest和相关插件
pip install pytest pytest-django pytest-cov pytest-html

# 使用pytest运行测试
pytest --cov=. --cov-report=html --html=reports/report.html

# 生成JUnit格式报告
pytest --junitxml=reports/junit.xml
```

### 持续集成配置
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: test_ship_schedule
        options: >-
          --health-cmd="mysqladmin ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=3
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install coverage
    
    - name: Run tests
      run: |
        coverage run --source='.' manage.py test
        coverage xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v1
```

## ⚠️ 测试最佳实践

### 测试原则
1. **独立性** - 测试之间不应相互依赖
2. **可重复性** - 测试结果应该一致
3. **快速性** - 测试应该快速执行
4. **清晰性** - 测试意图应该明确
5. **完整性** - 覆盖所有重要场景

### 命名规范
```python
# 测试类命名
class TestUserModel(TestCase):
class UserModelTest(TestCase):
class TestUserAuthentication(APITestCase):

# 测试方法命名
def test_create_user_success(self):
def test_create_user_with_invalid_email_should_fail(self):
def test_user_login_returns_token(self):
```

### 测试组织
```python
class UserModelTest(TestCase):
    """用户模型测试"""
    
    def setUp(self):
        """每个测试前执行"""
        pass
    
    def tearDown(self):
        """每个测试后执行"""
        pass
    
    @classmethod
    def setUpClass(cls):
        """测试类开始前执行一次"""
        super().setUpClass()
    
    @classmethod
    def tearDownClass(cls):
        """测试类结束后执行一次"""
        super().tearDownClass()
```

## 🔗 相关链接

- **[开发入门指南](getting_started.md)** - 开发环境搭建
- **[权限系统说明](permissions.md)** - 权限测试相关
- **[API文档](../api/README.md)** - API测试参考
- **[模块文档](../modules/README.md)** - 模块测试指南
