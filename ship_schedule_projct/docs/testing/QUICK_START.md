# 🚀 测试快速入门指南

## 📋 概述

本指南帮助开发者快速上手船舶航线管理系统的测试环境，了解如何运行测试、查看结果和编写新测试。

## ⚡ 快速开始

### 1. 环境准备

```bash
# 确保在项目根目录
cd /path/to/ship_schedule_project

# 检查Python环境
python3 --version  # 需要Python 3.8+

# 检查Django环境
python3 manage.py check
```

### 2. 运行核心测试 (推荐)

```bash
# 运行所有核心功能测试 (约5秒)
python3 run_tests.py models
python3 run_tests.py auth  
python3 run_tests.py permissions

# 或者一次性运行
python3 manage.py test tests.test_models tests.test_authentication_api tests.test_permissions --settings=ship_schedule.test_settings
```

### 3. 验证前台API

```bash
# 测试前台主要API端点
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/schedules/cabin-grouping-with-info/?polCd=CNSHA&podCd=USNYC

# 或运行API测试
python3 manage.py test tests.test_schedules_api.CabinGroupingAPITest --settings=ship_schedule.test_settings
```

## 🧪 测试分类说明

### ✅ **稳定测试 (可放心运行)**

```bash
# 数据模型测试 - 29个测试，100%通过
python3 run_tests.py models

# 认证系统测试 - 29个测试，100%通过  
python3 run_tests.py auth

# 权限系统测试 - 31个测试，100%通过
python3 run_tests.py permissions
```

### 🔄 **开发中测试 (部分功能)**

```bash
# 船期API测试 - 部分测试需要调整
python3 run_tests.py schedules

# 本地费用API测试 - 部分测试需要调整
python3 run_tests.py local_fees

# 集成测试 - 跨模块功能测试
python3 run_tests.py integration
```

## 📊 测试结果解读

### ✅ **成功示例**

```
Found 29 test(s).
Creating test database for alias 'default'...
test_create_user_success ... ok
test_user_permissions ... ok
...
----------------------------------------------------------------------
Ran 29 tests in 1.595s

OK
```

### ❌ **失败示例**

```
FAIL: test_api_permission (tests.test_schedules_api.VesselScheduleAPITest)
AssertionError: 403 != 200
```

**解读**: 这通常表示权限配置与测试期望不符，但不影响前台功能。

## 🛠️ 常用测试命令

### 基础命令

```bash
# 运行单个测试文件
python3 manage.py test tests.test_models --settings=ship_schedule.test_settings

# 运行单个测试类
python3 manage.py test tests.test_models.UserModelTest --settings=ship_schedule.test_settings

# 运行单个测试方法
python3 manage.py test tests.test_models.UserModelTest.test_create_user_success --settings=ship_schedule.test_settings

# 详细输出
python3 manage.py test tests.test_models --verbosity=2 --settings=ship_schedule.test_settings
```

### 高级命令

```bash
# 保留测试数据库 (调试用)
python3 manage.py test tests.test_models --keepdb --settings=ship_schedule.test_settings

# 并行运行测试
python3 manage.py test tests.test_models --parallel --settings=ship_schedule.test_settings

# 生成覆盖率报告
python3 run_tests.py coverage
```

## 🔍 调试测试

### 调试失败的测试

```python
# 在测试代码中添加调试点
import pdb; pdb.set_trace()

def test_example(self):
    user = User.objects.create_user(email='test@example.com')
    pdb.set_trace()  # 调试断点
    result = user.has_permission('test.permission')
    self.assertTrue(result)
```

### 查看测试数据

```python
# 在测试中打印数据
def test_example(self):
    user = User.objects.create_user(email='test@example.com')
    print(f"Created user: {user}")
    print(f"User permissions: {user.get_user_permissions()}")
```

## 📝 编写新测试

### 测试模板

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

User = get_user_model()

class MyNewTest(TestCase):
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
    
    def test_my_feature(self):
        """测试我的新功能"""
        # 1. 准备数据 (Arrange)
        
        # 2. 执行操作 (Act)
        
        # 3. 验证结果 (Assert)
        pass
    
    def tearDown(self):
        """测试后清理"""
        pass
```

### API测试模板

```python
class MyAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
    
    def test_api_endpoint(self):
        """测试API端点"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get('/api/my-endpoint/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
```

## 🚨 重要注意事项

### ✅ **安全操作**

1. **运行核心测试** - 模型、认证、权限测试可以安全运行
2. **查看测试结果** - 不会影响生产数据
3. **编写新测试** - 使用测试数据库，不影响实际数据

### ⚠️ **注意事项**

1. **不要修改前台API权限** - 可能影响前台功能
2. **测试失败不等于功能问题** - 部分测试与实际API不匹配
3. **使用测试设置** - 始终使用 `--settings=ship_schedule.test_settings`

### 🔧 **故障排除**

```bash
# 如果测试数据库有问题
rm -f db.sqlite3
python3 manage.py migrate --settings=ship_schedule.test_settings

# 如果权限测试失败
# 检查是否使用了正确的权限代码

# 如果API测试失败  
# 检查是否测试了正确的API端点
```

## 📚 相关文档

- **[测试状态报告](TEST_STATUS.md)** - 详细的测试覆盖情况
- **[完整测试文档](../tests/README.md)** - 测试套件详细说明
- **[API文档](../api/README.md)** - API接口文档
- **[开发指南](../development/README.md)** - 开发环境搭建

## 🎯 下一步

1. **运行核心测试** - 验证系统基础功能
2. **了解测试结果** - 查看测试状态报告
3. **开始开发** - 基于稳定的测试基础进行开发
4. **编写新测试** - 为新功能添加测试用例

---

**💡 提示**: 如果您是新加入的开发者，建议先运行核心测试熟悉系统，然后阅读测试状态报告了解整体情况。
