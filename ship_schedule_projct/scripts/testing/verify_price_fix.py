#!/usr/bin/env python3
"""
验证修复后的API价格计算
"""

import requests
import json
from datetime import datetime

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

def verify_price_fix():
    """验证价格修复"""
    
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
            groups = data.get('data', {}).get('groups', [])
            
            print("🔍 修复后的API价格计算验证")
            print("=" * 80)
            
            for group in groups:
                group_id = group.get('group_id')
                cabin_price = group.get('cabin_price')
                schedules = group.get('schedules', [])
                
                print(f"\n📊 {group_id}:")
                print(f"   推荐价格: {cabin_price}")
                print(f"   船期数量: {len(schedules)}")
                
                # 分析ETD和价格
                etd_prices = []
                for schedule in schedules:
                    etd = schedule.get('etd')
                    vessel_name = schedule.get('vessel')
                    price = schedule.get('vessel_info', {}).get('price')
                    
                    if etd and price != '--':
                        try:
                            etd_date = datetime.strptime(etd, '%Y-%m-%d %H:%M:%S').date()
                            etd_prices.append((etd_date, price, vessel_name))
                        except:
                            pass
                
                if etd_prices:
                    # 找到最早ETD日期
                    earliest = min(etd_prices, key=lambda x: x[0])
                    print(f"   最早ETD: {earliest[0]} ({earliest[2]}) - 价格: {earliest[1]}")
                    
                    if cabin_price == earliest[1]:
                        print(f"   ✅ 价格计算正确")
                    elif cabin_price == '--' and earliest[1] != '--':
                        print(f"   ❌ 价格计算错误: 应该是 {earliest[1]}，但得到 '--'")
                    else:
                        print(f"   ⚠️  价格不匹配: 期望 {earliest[1]}，实际 {cabin_price}")
                else:
                    print(f"   📝 没有有效价格数据")
            
            print("\n" + "=" * 80)
            print("💡 修复总结:")
            
            # 统计修复效果
            groups_with_price = sum(1 for g in groups if g.get('cabin_price') != '--')
            total_groups = len(groups)
            
            print(f"   总分组数: {total_groups}")
            print(f"   有价格的分组: {groups_with_price}")
            print(f"   修复率: {groups_with_price/total_groups*100:.1f}%" if total_groups > 0 else "   修复率: 0%")
            
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 执行失败: {e}")

if __name__ == "__main__":
    verify_price_fix()
