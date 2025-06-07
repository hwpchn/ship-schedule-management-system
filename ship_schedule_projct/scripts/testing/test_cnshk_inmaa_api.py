#!/usr/bin/env python3
"""
测试CNSHK到INMAA航线的cabin_grouping_with_vessel_info_api接口
"""

import requests
import json
from datetime import datetime

# 配置API设置
API_BASE_URL = "http://127.0.0.1:8000"
API_ENDPOINT = "/api/schedules/cabin-grouping-with-info/"
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

def test_cabin_grouping_api():
    """测试cabin_grouping_with_vessel_info_api接口"""
    
    print("🚢 测试 CNSHK -> INMAA 共舱分组API")
    print("=" * 80)
    
    # 获取认证令牌
    token = get_auth_token()
    
    if not token:
        print("❌ 无法获取认证令牌，退出测试")
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # 设置测试参数 - CNSHK到INMAA
    params = {
        'polCd': 'CNSHK',  # 蛇口港
        'podCd': 'INMAA',  # 马德拉斯港
    }
    
    print(f"🔗 API端点: {API_BASE_URL}{API_ENDPOINT}")
    print(f"📋 测试参数: {params}")
    print(f"🔐 认证状态: {'已认证' if token else '未认证'}")
    print("=" * 80)
    
    try:
        # 发送GET请求
        response = requests.get(
            f"{API_BASE_URL}{API_ENDPOINT}",
            params=params,
            headers=headers,
            timeout=30
        )
        
        print(f"📊 HTTP状态码: {response.status_code}")
        print(f"📈 响应头: {dict(response.headers)}")
        print("=" * 80)
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                print("✅ API调用成功！")
                print("\n📋 JSON响应数据:")
                print(json.dumps(json_data, ensure_ascii=False, indent=2))
                
                # 分析响应结构
                if json_data.get('success'):
                    data = json_data.get('data', {})
                    print(f"\n📊 响应分析:")
                    print(f"- 请求成功: {json_data.get('success')}")
                    print(f"- 响应消息: {json_data.get('message')}")
                    print(f"- 数据版本: {data.get('version')}")
                    print(f"- 分组总数: {data.get('total_groups')}")
                    print(f"- 筛选条件: {data.get('filter')}")
                    
                    groups = data.get('groups', [])
                    if groups:
                        print(f"\n🏢 分组详情:")
                        for i, group in enumerate(groups, 1):
                            print(f"\n  📦 分组 {i} ({group['group_id']}):")
                            print(f"     🏢 船公司数量: {group['cabins_count']}")
                            print(f"     📋 船公司列表: {', '.join(group['carrier_codes'])}")
                            print(f"     📅 推荐开船班期: {group['plan_open']}")
                            print(f"     ⏱️  推荐航程天数: {group['plan_duration']}")
                            print(f"     💰 推荐价格: {group['cabin_price']}")
                            print(f"     📦 20GP现舱: {group['is_has_gp_20']}")
                            print(f"     📦 40HQ现舱: {group['is_has_hq_40']}")
                            print(f"     🚢 航线数量: {len(group['schedules'])}")
                            
                            # 显示组内航线详情
                            if group['schedules']:
                                print(f"     航线详情:")
                                for j, schedule in enumerate(group['schedules'][:3], 1):  # 显示前3条航线
                                    print(f"       航线{j}: {schedule['vessel']} / {schedule['voyage']} - {schedule['carriercd']}")
                                    print(f"         开船时间: routeEtd={schedule['routeEtd']}, etd={schedule['etd']}")
                                    if schedule.get('vessel_info'):
                                        vi = schedule['vessel_info']
                                        print(f"         船舶信息: 价格={vi.get('price', 'N/A')}, 20GP={vi.get('gp_20', 'N/A')}, 40HQ={vi.get('hq_40', 'N/A')}")
                                        print(f"         截关时间: {vi.get('cut_off_time', 'N/A')}")
                                if len(group['schedules']) > 3:
                                    print(f"       ... 还有 {len(group['schedules']) - 3} 条航线")
                    else:
                        print("⚠️  没有找到分组数据")
                else:
                    print(f"❌ API返回失败: {json_data.get('message')}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败: {e}")
                print(f"原始响应内容: {response.text}")
                
        elif response.status_code == 403:
            print(f"❌ 权限不足 (403): 可能需要相应的权限")
            print(f"错误内容: {response.text}")
        elif response.status_code == 401:
            print(f"❌ 认证失败 (401): Token可能已过期")
            print(f"错误内容: {response.text}")
        else:
            print(f"❌ API调用失败 ({response.status_code})")
            print(f"错误内容: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求错误: {e}")
    
    print("=" * 80)
    print(f"🕒 测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_cabin_grouping_api()
