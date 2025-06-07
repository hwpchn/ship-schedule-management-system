#!/usr/bin/env python3
import json
import sys
import os
from datetime import datetime, date

# 添加项目根目录到Python路径
sys.path.append('/Users/huangcc/work/ship_schedule_projct')

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ship_schedule.settings')
import django
django.setup()

import requests

# 配置API设置
API_BASE_URL = "http://127.0.0.1:8000"
USERNAME = "admin@example.com"
PASSWORD = "admin123456"

def get_auth_token():
    """获取认证令牌"""
    login_url = f"{API_BASE_URL}/api/auth/login/"
    
    try:
        response = requests.post(login_url, json={
            'email': USERNAME,
            'password': PASSWORD
        })
        
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get('tokens', {}).get('access')
        else:
            print(f"❌ 登录失败: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 认证错误: {e}")
        return None

def debug_price_calculation():
    """调试价格计算逻辑"""
    
    # 获取认证令牌
    token = get_auth_token()
    
    if not token:
        print("❌ 无法获取认证令牌，退出测试")
        return
    
    # 调用API获取数据
    url = f"{API_BASE_URL}/api/schedules/cabin-grouping-with-info/"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    params = {
        'polCd': 'CNSHK',
        'podCd': 'INMAA'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ API调用成功")
            print(f"成功状态: {data.get('success')}")
            
            # 打印原始数据结构
            print("\n📋 原始响应数据:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 执行失败: {e}")

if __name__ == "__main__":
    debug_price_calculation()
