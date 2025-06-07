#!/usr/bin/env python3
"""
测试权限修复后的API访问
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ship_schedule.settings')
django.setup()

from authentication.models import User
from authentication.permissions import get_permission_map

def test_permission_logic():
    """测试权限逻辑"""
    user = User.objects.get(email='test3@126.com')
    permission_map = get_permission_map()
    
    print(f"用户：{user.email}")
    print(f"is_superuser: {user.is_superuser}")
    print(f"权限映射：'vessel_schedule_list' -> '{permission_map.get('vessel_schedule_list', 'schedules.view_vesselschedule')}'")
    
    # 模拟API中的权限检查逻辑
    required_permission = permission_map.get('vessel_schedule_list', 'schedules.view_vesselschedule')
    has_permission = user.has_permission(required_permission)
    
    print(f"需要的权限：{required_permission}")
    print(f"用户是否有权限：{has_permission}")
    
    # 检查API访问条件
    api_access_allowed = user.is_superuser or has_permission
    print(f"API访问是否允许：{api_access_allowed}")
    
    if api_access_allowed:
        print("✓ 权限检查通过，用户可以访问船期查询API")
    else:
        print("✗ 权限检查失败，用户无法访问船期查询API")

if __name__ == '__main__':
    test_permission_logic()
