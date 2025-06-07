#!/usr/bin/env python3
"""
分析分组1的plan_open计算逻辑
"""

import requests
import json
from collections import Counter

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

def analyze_plan_open():
    """分析plan_open计算逻辑"""
    
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
            
            # 找到group_1
            group_1 = None
            for group in groups:
                if group.get('group_id') == 'group_1':
                    group_1 = group
                    break
            
            if not group_1:
                print("❌ 找不到group_1")
                return
            
            print("🔍 分析group_1的plan_open计算")
            print("=" * 80)
            print(f"分组ID: {group_1.get('group_id')}")
            print(f"API返回的plan_open: {group_1.get('plan_open')}")
            print(f"船期数量: {len(group_1.get('schedules', []))}")
            print("-" * 40)
            
            # 分析每个船期的routeEtd值
            route_etds = []
            print("📊 各船期的routeEtd值:")
            
            for i, schedule in enumerate(group_1.get('schedules', []), 1):
                vessel = schedule.get('vessel')
                voyage = schedule.get('voyage')
                route_etd = schedule.get('routeEtd')
                etd = schedule.get('etd')
                
                print(f"  船期{i}: {vessel} {voyage}")
                print(f"         ETD: {etd}")
                print(f"         routeEtd: {route_etd}")
                
                if route_etd is not None:
                    try:
                        route_etd_int = int(route_etd)
                        route_etds.append(route_etd_int)
                    except:
                        print(f"         ❌ routeEtd格式错误: {route_etd}")
                else:
                    print(f"         📝 routeEtd为空")
                print()
            
            print("-" * 40)
            print("🧮 plan_open计算过程:")
            print(f"收集到的routeEtd值: {route_etds}")
            
            if route_etds:
                # 计算routeEtd出现次数
                route_etd_counter = Counter(route_etds)
                print(f"routeEtd计数统计: {dict(route_etd_counter)}")
                
                # 找到出现次数最多的值
                most_common_etds = route_etd_counter.most_common()
                print(f"按出现次数排序: {most_common_etds}")
                
                max_count = most_common_etds[0][1]
                plan_open_values = [etd for etd, count in most_common_etds if count == max_count]
                print(f"最高出现次数: {max_count}")
                print(f"最高频率的routeEtd值: {plan_open_values}")
                
                # 选择最小值（最早的航线）
                calculated_plan_open = min(plan_open_values) if plan_open_values else None
                print(f"选择最小值作为plan_open: {calculated_plan_open}")
                
                # 与API返回值对比
                api_plan_open = group_1.get('plan_open')
                if str(calculated_plan_open) == str(api_plan_open):
                    print(f"✅ 计算结果与API一致: {calculated_plan_open}")
                else:
                    print(f"⚠️  计算结果与API不一致:")
                    print(f"   计算结果: {calculated_plan_open}")
                    print(f"   API返回: {api_plan_open}")
            else:
                print("❌ 没有有效的routeEtd数据")
            
            print("=" * 80)
            print("💡 plan_open计算规则解释:")
            print("1. 收集分组内所有船期的routeEtd值")
            print("2. 统计每个routeEtd值的出现次数")
            print("3. 找到出现次数最多的routeEtd值")
            print("4. 如果有多个相同最高次数的值，选择其中最小的（最早的航线）")
            print("5. routeEtd表示航线出发日期相对于当前日期的天数差")
            
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 执行失败: {e}")

if __name__ == "__main__":
    analyze_plan_open()
