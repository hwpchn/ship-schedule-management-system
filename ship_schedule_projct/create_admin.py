#!/usr/bin/env python
"""
创建默认管理员账户脚本
用于Docker部署时自动创建超级管理员
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ship_schedule.settings')
django.setup()

from django.contrib.auth import get_user_model
from authentication.models import Permission, Role

def create_default_admin():
    """
    创建默认超级管理员账户
    """
    User = get_user_model()
    
    # 默认管理员信息
    admin_email = "admin@admin.com"
    admin_password = "admin123@"
    
    try:
        # 检查是否已存在
        if User.objects.filter(email=admin_email).exists():
            print(f"✅ 管理员账户已存在: {admin_email}")
            return
        
        # 创建超级管理员
        admin_user = User.objects.create_superuser(
            email=admin_email,
            password=admin_password,
            first_name="系统",
            last_name="管理员"
        )
        
        print(f"🎉 默认管理员账户创建成功!")
        print(f"📧 邮箱: {admin_email}")
        print(f"🔑 密码: {admin_password}")
        print(f"🚀 请登录后及时修改默认密码!")
        
        # 创建默认角色（如果不存在）
        create_default_roles()
        
        return admin_user
        
    except Exception as e:
        print(f"❌ 创建管理员账户失败: {e}")
        sys.exit(1)

def create_default_roles():
    """
    创建默认角色和权限
    """
    try:
        # 创建超级管理员角色
        admin_role, created = Role.objects.get_or_create(
            name="超级管理员",
            defaults={
                'description': '系统超级管理员，拥有所有权限'
            }
        )
        
        if created:
            print(f"✅ 创建默认角色: {admin_role.name}")
        
        # 创建普通用户角色
        user_role, created = Role.objects.get_or_create(
            name="普通用户",
            defaults={
                'description': '普通用户，具有基本查询权限'
            }
        )
        
        if created:
            print(f"✅ 创建默认角色: {user_role.name}")
            
            # 为普通用户角色分配基本权限
            basic_permissions = [
                'vessel_schedule_view',
                'vessel_info_view',
                'local_fee_view'
            ]
            
            for perm_code in basic_permissions:
                permission, _ = Permission.objects.get_or_create(
                    code=perm_code,
                    defaults={
                        'name': f'{perm_code}_permission',
                        'description': f'{perm_code}权限'
                    }
                )
                user_role.permissions.add(permission)
        
    except Exception as e:
        print(f"⚠️ 创建默认角色时出现警告: {e}")

def print_login_info():
    """
    打印登录信息
    """
    print("\n" + "="*60)
    print("🚢 船期管理系统 - 默认管理员账户信息")
    print("="*60)
    print(f"🌐 前端访问地址: http://localhost")
    print(f"🔧 后端API地址: http://localhost:8000")
    print(f"📧 管理员邮箱: admin@admin.com")
    print(f"🔑 管理员密码: admin123@")
    print("="*60)
    print("⚠️  重要提醒:")
    print("   1. 请在首次登录后立即修改默认密码")
    print("   2. 建议创建新的管理员账户后删除此默认账户")
    print("   3. 生产环境请使用强密码策略")
    print("="*60)

if __name__ == "__main__":
    print("🔧 正在创建默认管理员账户...")
    create_default_admin()
    print_login_info()