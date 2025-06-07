#!/usr/bin/env python3
"""
检查用户权限的脚本
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ship_schedule.settings')
django.setup()

from authentication.models import User, Role, Permission

def check_user_permissions(email):
    """检查用户权限"""
    try:
        user = User.objects.get(email=email)
        print(f"用户信息：{user.email}")
        print(f"是否为超级用户：{user.is_superuser}")
        print(f"是否为管理员：{user.is_staff}")
        print(f"是否激活：{user.is_active}")
        print()
        
        # 检查用户角色
        roles = user.roles.filter(is_active=True)
        print(f"用户角色数量：{roles.count()}")
        for role in roles:
            print(f"  - 角色：{role.name} ({role.description})")
        print()
        
        # 检查用户权限
        permissions = user.get_user_permissions()
        print(f"用户权限数量：{len(permissions)}")
        for perm in permissions:
            print(f"  - {perm}")
        print()
        
        # 检查特定权限
        target_permissions = ['schedule.list', 'vessel_info.list', 'vessel_info.detail']
        print("关键权限检查：")
        for perm in target_permissions:
            has_perm = user.has_permission(perm)
            print(f"  - {perm}: {'✓' if has_perm else '✗'}")
        
        return True
        
    except User.DoesNotExist:
        print(f"用户 {email} 不存在")
        return False

def list_all_permissions():
    """列出所有可用权限"""
    print("\n所有系统权限：")
    permissions = Permission.objects.all().order_by('category', 'code')
    for perm in permissions:
        print(f"  - {perm.code}: {perm.name}")

if __name__ == '__main__':
    print("=== 用户权限检查工具 ===")
    
    # 检查test3@126.com用户
    user_email = 'test3@126.com'
    print(f"检查用户：{user_email}")
    print("-" * 50)
    
    success = check_user_permissions(user_email)
    
    if success:
        list_all_permissions()
    
    print("\n=== 检查完成 ===")
