#!/usr/bin/env python3
"""
在Django环境中直接测试权限逻辑
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ship_schedule.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from authentication.models import User
from schedules.views import cabin_grouping_with_vessel_info_api
from authentication.permissions import get_permission_map

def test_api_permission_directly():
    """直接测试API权限逻辑"""
    try:
        # 获取用户
        user = User.objects.get(email='test3@126.com')
        
        # 创建模拟请求
        factory = RequestFactory()
        request = factory.get('/api/schedules/cabin-grouping-with-info/', {
            'polCd': 'CNSHK',
            'podCd': 'THBKK'
        })
        request.user = user
        
        print(f"测试用户: {user.email}")
        print(f"用户权限: {user.get_user_permissions()}")
        
        # 测试权限检查逻辑
        permission_map = get_permission_map()
        required_permission = permission_map.get('vessel_schedule_list', 'schedules.view_vesselschedule')
        has_permission = user.has_permission(required_permission)
        
        print(f"需要权限: {required_permission}")
        print(f"用户是否有权限: {has_permission}")
        print(f"用户是否为超级用户: {user.is_superuser}")
        
        # 模拟权限检查
        permission_check_pass = user.is_superuser or has_permission
        print(f"权限检查结果: {permission_check_pass}")
        
        if permission_check_pass:
            print("✓ 权限检查通过，应该可以访问API")
            
            # 尝试调用API函数（这可能会因为其他依赖而失败，但权限部分应该通过）
            try:
                response = cabin_grouping_with_vessel_info_api(request)
                print(f"API调用结果: 状态码 {response.status_code}")
                if hasattr(response, 'data'):
                    print(f"响应数据: {str(response.data)[:200]}...")
            except Exception as e:
                print(f"API调用异常（可能是数据问题，但权限已通过）: {str(e)[:200]}...")
        else:
            print("✗ 权限检查失败，无法访问API")
            
    except User.DoesNotExist:
        print("用户不存在")
    except Exception as e:
        print(f"测试过程中出现异常: {e}")

if __name__ == '__main__':
    print("=== 直接测试API权限逻辑 ===")
    test_api_permission_directly()
    print("\n=== 测试完成 ===")
