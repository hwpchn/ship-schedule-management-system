#!/usr/bin/env python3
"""
检查和重置用户密码
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ship_schedule.settings')
django.setup()

from authentication.models import User

def check_and_reset_password():
    """检查和重置用户密码"""
    try:
        user = User.objects.get(email='test3@126.com')
        print(f"用户: {user.email}")
        
        # 重置密码为123456
        user.set_password('123456')
        user.save()
        print("✓ 密码已重置为: 123456")
        
        # 验证密码
        if user.check_password('123456'):
            print("✓ 密码验证成功")
        else:
            print("✗ 密码验证失败")
            
    except User.DoesNotExist:
        print("用户不存在")

if __name__ == '__main__':
    check_and_reset_password()
