#!/usr/bin/env python3
"""
检查权限数据一致性
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ship_schedule.settings')
django.setup()

from authentication.models import User, Role, Permission

def check_permission_consistency():
    """检查权限数据一致性"""
    
    # 检查用户
    user = User.objects.get(email='test3@126.com')
    print(f"用户 {user.email} 的角色和权限：")
    
    role = user.roles.first()
    if role:
        print(f"角色：{role.name}")
        print("角色的权限：")
        for perm in role.permissions.all():
            print(f"  - {perm.code}: {perm.name}")
        
        print(f"\n用户通过 get_user_permissions() 得到的权限：")
        for perm_code in user.get_user_permissions():
            print(f"  - {perm_code}")
            
        # 检查特定权限
        print(f"\n权限检查结果：")
        print(f"  schedule.list: {user.has_permission('schedule.list')}")
        print(f"  vessel_schedule_list: {user.has_permission('vessel_schedule_list')}")
        
        # 查看权限对象是否存在
        try:
            schedule_list_perm = Permission.objects.get(code='schedule.list')
            print(f"\n权限对象 'schedule.list' 存在：{schedule_list_perm.name}")
        except Permission.DoesNotExist:
            print(f"\n权限对象 'schedule.list' 不存在！")
            
        try:
            vessel_schedule_list_perm = Permission.objects.get(code='vessel_schedule_list')
            print(f"权限对象 'vessel_schedule_list' 存在：{vessel_schedule_list_perm.name}")
        except Permission.DoesNotExist:
            print(f"权限对象 'vessel_schedule_list' 不存在！")

if __name__ == '__main__':
    check_permission_consistency()
