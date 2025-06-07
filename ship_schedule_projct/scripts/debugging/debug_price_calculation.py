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
            print(f"响应内容: {response.text}")
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
            print(f"消息: {data.get('message')}")
            
            # 打印原始数据结构以便调试
            print("\n📋 原始数据结构:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # 获取实际数据
            groups_data = data.get('data', [])
            print(f"\n总分组数: {len(groups_data)}")
            print(f"数据类型: {type(groups_data)}")
            
            if groups_data and len(groups_data) > 0:
                print(f"第一个分组类型: {type(groups_data[0])}")
                print(f"第一个分组内容: {groups_data[0]}")
            
            print("-" * 80)
                
                # 分析每个船期的ETD和价格数据
                etd_schedules = []
                for j, schedule in enumerate(group.get('schedules', [])):
                    etd = schedule.get('etd')
                    vessel_info = schedule.get('vessel_info', {})
                    price = vessel_info.get('price')
                    
                    print(f"  船期 {j+1}: ETD={etd}, price={price}")
                    
                    if etd:
                        try:
                            etd_date = datetime.strptime(etd, '%Y-%m-%d').date()
                            etd_schedules.append({
                                'etd_date': etd_date,
                                'etd_str': etd,
                                'price': price,
                                'schedule_index': j
                            })
                        except Exception as e:
                            print(f"    ❌ ETD日期解析失败: {e}")
                
                # 找到最早的ETD日期
                if etd_schedules:
                    earliest = min(etd_schedules, key=lambda x: x['etd_date'])
                    print(f"  🎯 最早ETD: {earliest['etd_str']} (船期{earliest['schedule_index']+1})")
                    print(f"  🎯 对应价格: {earliest['price']}")
                    
                    # 模拟价格计算逻辑
                    calculated_price = earliest['price'] if earliest['price'] is not None else '--'
                    print(f"  📊 计算出的价格: {calculated_price}")
                    
                    if calculated_price != group.get('cabin_price'):
                        print(f"  ⚠️  价格不匹配! API返回: {group.get('cabin_price')}, 计算结果: {calculated_price}")
                else:
                    print(f"  ❌ 没有有效的ETD数据")
                
                print("-" * 40)
                
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 执行失败: {e}")

if __name__ == "__main__":
    debug_price_calculation()
