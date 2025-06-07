"""
pytest配置文件
配置测试环境和公共测试工具
"""
import pytest
import os
import django
from django.conf import settings
from django.test.utils import get_runner


def pytest_configure():
    """配置pytest环境"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ship_schedule.settings')
    django.setup()
    
    # 配置测试数据库
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
    
    # 禁用缓存
    settings.CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
    
    # 禁用日志输出
    settings.LOGGING_CONFIG = None


@pytest.fixture(scope='session')
def django_db_setup():
    """设置测试数据库"""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }


@pytest.fixture
def api_client():
    """API客户端fixture"""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_user():
    """认证用户fixture"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    user = User.objects.create_user(
        email='test@example.com',
        password='testpass123'
    )
    return user


@pytest.fixture
def admin_user():
    """管理员用户fixture"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    admin = User.objects.create_superuser(
        email='admin@example.com',
        password='adminpass123'
    )
    return admin


@pytest.fixture
def test_permission():
    """测试权限fixture"""
    from authentication.models import Permission
    
    permission = Permission.objects.create(
        code='test.permission',
        name='测试权限',
        description='测试用权限',
        category='测试'
    )
    return permission


@pytest.fixture
def test_role(test_permission):
    """测试角色fixture"""
    from authentication.models import Role
    
    role = Role.objects.create(
        name='测试角色',
        description='测试用角色'
    )
    role.permissions.add(test_permission)
    return role


@pytest.fixture
def test_schedule():
    """测试船期fixture"""
    from schedules.models import VesselSchedule
    from django.utils import timezone
    
    schedule = VesselSchedule.objects.create(
        polCd='CNSHA',
        podCd='USNYC',
        vessel='TEST_VESSEL',
        voyage='TEST001',
        data_version=20250527,
        carriercd='TEST',
        fetch_timestamp=1716825600,
        fetch_date=timezone.now(),
        status=1
    )
    return schedule


@pytest.fixture
def test_local_fee():
    """测试本地费用fixture"""
    from local_fees.models import LocalFee
    from decimal import Decimal
    
    local_fee = LocalFee.objects.create(
        polCd='CNSHA',
        podCd='USNYC',
        carriercd='TEST',
        name='测试费用',
        price_20gp=Decimal('100.00'),
        currency='USD'
    )
    return local_fee
