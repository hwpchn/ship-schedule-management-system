# 测试套件说明

## 📋 概述

本测试套件为船舶航线管理系统提供全面的测试覆盖，包括单元测试、集成测试、API测试、性能测试和权限测试。

## 🎯 **重要提示**

> **✅ 系统状态**: 核心功能已通过完整测试，前台API工作正常
>
> **📊 测试覆盖**: 数据模型(100%) | 认证系统(100%) | 权限系统(100%)
>
> **🔗 详细状态**: 请查看 [测试状态报告](../docs/testing/TEST_STATUS.md)
>
> **🚀 快速开始**: 请查看 [测试快速入门](../docs/testing/QUICK_START.md)

## 🧪 测试结构

```
tests/
├── __init__.py                 # 测试包初始化
├── conftest.py                # pytest配置和fixtures
├── test_runner.py             # 自定义测试运行器
├── test_models.py             # 数据模型测试
├── test_authentication_api.py # 认证API测试
├── test_schedules_api.py      # 船期管理API测试
├── test_local_fees_api.py     # 本地费用API测试
├── test_permissions.py        # 权限系统测试
├── test_performance.py        # 性能测试
├── test_integration.py        # 集成测试
└── README.md                  # 本文档
```

## 🎯 测试分类

### 1. 单元测试 (Unit Tests)
- **test_models.py** - 数据模型测试
  - 用户模型测试
  - 权限模型测试
  - 角色模型测试
  - 船舶航线模型测试
  - 船舶信息模型测试
  - 本地费用模型测试
  - 用户权限集成测试

### 2. API测试 (API Tests)
- **test_authentication_api.py** - 认证API测试
  - 用户注册API
  - 用户登录API
  - JWT Token API
  - 用户信息API
  - 权限管理API
  - 角色管理API

- **test_schedules_api.py** - 船期管理API测试
  - 船舶航线CRUD API
  - 船舶信息管理API
  - 共舱分组查询API
  - 权限控制测试

- **test_local_fees_api.py** - 本地费用API测试
  - 本地费用CRUD API
  - 前台查询API
  - 多种计费方式测试
  - 权限控制测试

### 3. 权限测试 (Permission Tests)
- **test_permissions.py** - 权限系统测试
  - RBAC权限模型测试
  - 权限检查机制测试
  - 权限装饰器测试
  - 权限API集成测试
  - 权限缓存测试
  - 边界情况测试

### 4. 性能测试 (Performance Tests)
- **test_performance.py** - 性能测试
  - 数据库性能测试
  - API响应时间测试
  - 内存使用测试
  - 缓存性能测试
  - 负载测试

### 5. 集成测试 (Integration Tests)
- **test_integration.py** - 集成测试
  - 用户工作流程测试
  - 船期管理集成测试
  - 本地费用集成测试
  - 跨模块集成测试
  - 端到端业务场景测试

## 🚀 运行测试

### 使用Django测试命令

```bash
# 运行所有测试
python manage.py test

# 运行特定模块测试
python manage.py test tests.test_models
python manage.py test tests.test_authentication_api
python manage.py test tests.test_schedules_api
python manage.py test tests.test_local_fees_api
python manage.py test tests.test_permissions
python manage.py test tests.test_performance
python manage.py test tests.test_integration

# 运行特定测试类
python manage.py test tests.test_models.UserModelTest

# 运行特定测试方法
python manage.py test tests.test_models.UserModelTest.test_create_user_success

# 并行运行测试
python manage.py test --parallel

# 保留测试数据库
python manage.py test --keepdb

# 详细输出
python manage.py test --verbosity=2
```

### 使用pytest

```bash
# 安装pytest依赖
pip install -r requirements-test.txt

# 运行所有测试
pytest

# 运行特定文件
pytest tests/test_models.py

# 运行特定测试类
pytest tests/test_models.py::UserModelTest

# 运行特定测试方法
pytest tests/test_models.py::UserModelTest::test_create_user_success

# 运行带标记的测试
pytest -m "unit"
pytest -m "api"
pytest -m "integration"
pytest -m "performance"

# 生成覆盖率报告
pytest --cov=. --cov-report=html

# 并行运行
pytest -n auto
```

### 使用自定义测试脚本

```bash
# 使测试脚本可执行
chmod +x run_tests.py

# 运行所有测试
python run_tests.py all

# 运行特定测试套件
python run_tests.py models
python run_tests.py auth
python run_tests.py schedules
python run_tests.py local_fees
python run_tests.py permissions
python run_tests.py performance
python run_tests.py integration

# 运行覆盖率测试
python run_tests.py coverage

# 运行pytest测试
python run_tests.py pytest

# 生成详细报告
python run_tests.py report

# 并行运行
python run_tests.py all --parallel

# 保留数据库
python run_tests.py all --keepdb
```

## 📊 测试覆盖率

### 覆盖率目标
- **总体覆盖率**: ≥90%
- **核心业务逻辑**: 100%
- **API接口**: 100%
- **权限控制**: 100%
- **数据模型**: ≥95%

### 生成覆盖率报告

```bash
# 使用coverage
coverage run --source='.' manage.py test
coverage report
coverage html

# 使用pytest
pytest --cov=. --cov-report=term-missing --cov-report=html

# 查看HTML报告
open htmlcov/index.html
```

## 🔧 测试配置

### 测试数据库
- 使用SQLite内存数据库 (`:memory:`)
- 每次测试运行时重新创建
- 支持`--keepdb`选项保留数据库

### 测试缓存
- 使用本地内存缓存
- 测试间自动清理
- 支持缓存性能测试

### 测试设置
```python
# 测试专用设置
TESTING = True
DEBUG = False
DATABASES['default']['NAME'] = ':memory:'
CACHES['default']['BACKEND'] = 'django.core.cache.backends.locmem.LocMemCache'
```

## 🛠️ 测试工具

### Fixtures
- `api_client` - API测试客户端
- `authenticated_user` - 认证用户
- `admin_user` - 管理员用户
- `test_permission` - 测试权限
- `test_role` - 测试角色
- `test_schedule` - 测试船期
- `test_local_fee` - 测试本地费用

### 测试数据工厂
```python
# 使用factory_boy创建测试数据
user = UserFactory()
schedule = VesselScheduleFactory()
local_fee = LocalFeeFactory()
```

### Mock和Stub
```python
# 使用mock模拟外部依赖
from unittest.mock import patch, Mock

@patch('external_service.api_call')
def test_with_mock(mock_api):
    mock_api.return_value = {'status': 'success'}
    # 测试逻辑
```

## 📈 性能基准

### API响应时间
- 列表查询: < 1秒
- 详情查询: < 0.5秒
- 创建操作: < 2秒
- 更新操作: < 1秒
- 删除操作: < 0.5秒

### 数据库操作
- 批量创建1000条记录: < 5秒
- 复杂查询(5000条数据): < 1秒
- 索引查询: < 0.1秒

### 内存使用
- 大数据集处理: < 500MB增长
- 迭代器查询: 内存使用优化

## 🐛 调试测试

### 调试失败的测试
```bash
# 详细输出
python manage.py test --verbosity=3

# 保留失败时的数据
python manage.py test --keepdb --debug-mode

# 使用pdb调试
import pdb; pdb.set_trace()
```

### 常见问题
1. **数据库连接错误**: 检查测试数据库配置
2. **权限测试失败**: 确保测试用户有正确的权限
3. **API测试失败**: 检查认证和权限设置
4. **性能测试超时**: 调整性能基准或优化代码

## 📝 编写新测试

### 测试命名规范
```python
class TestUserModel(TestCase):
    def test_create_user_success(self):
        """测试成功创建用户"""
        pass

    def test_create_user_with_invalid_email_should_fail(self):
        """测试使用无效邮箱创建用户应该失败"""
        pass
```

### 测试结构
```python
def test_example(self):
    # 1. 准备 (Arrange)
    user = User.objects.create_user(email='test@example.com')

    # 2. 执行 (Act)
    result = user.has_permission('test.permission')

    # 3. 断言 (Assert)
    self.assertFalse(result)
```

### 最佳实践
1. 每个测试只测试一个功能点
2. 测试名称要清晰描述测试内容
3. 使用setUp和tearDown管理测试数据
4. 避免测试间的依赖关系
5. 使用有意义的断言消息

## 🔗 相关链接

- **[开发指南](../docs/development/README.md)** - 开发环境搭建
- **[测试指南](../docs/development/testing.md)** - 详细测试指南
- **[API文档](../docs/api/README.md)** - API接口文档
- **[权限系统](../docs/development/permissions.md)** - 权限系统说明
