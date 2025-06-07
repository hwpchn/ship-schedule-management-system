#!/usr/bin/env python3
"""
测试修复后的船期查询API
"""
import requests
import json

def test_cabin_grouping_api():
    """测试舱位分组API"""
    base_url = "http://localhost:8000"
    
    # 首先登录获取token
    login_data = {
        "email": "test3@126.com",
        "password": "123456"
    }
    
    print("1. 尝试登录...")
    login_response = requests.post(f"{base_url}/api/auth/login/", json=login_data)
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        print(f"登录响应: {json.dumps(login_result, ensure_ascii=False, indent=2)}")
        
        if login_result.get('tokens') and login_result.get('tokens').get('access'):
            token = login_result['tokens']['access']
            print(f"✓ 登录成功，获取到token: {token[:20]}...")
            
            # 测试船期查询API
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # 测试参数
            api_url = f"{base_url}/api/schedules/cabin-grouping-with-info/"
            params = {
                'polCd': 'CNSHK',
                'podCd': 'THBKK'
            }
            
            print("\n2. 测试船期查询API...")
            print(f"请求URL: {api_url}")
            print(f"请求参数: {params}")
            
            api_response = requests.get(api_url, params=params, headers=headers)
            
            print(f"\n3. API响应:")
            print(f"状态码: {api_response.status_code}")
            
            if api_response.status_code == 200:
                try:
                    result = api_response.json()
                    print("✓ API请求成功!")
                    print(f"响应数据: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}...")
                except:
                    print("响应内容:")
                    print(api_response.text[:500])
            else:
                print("✗ API请求失败!")
                try:
                    error_result = api_response.json()
                    print(f"错误响应: {json.dumps(error_result, ensure_ascii=False, indent=2)}")
                except:
                    print("错误响应内容:")
                    print(api_response.text)
                    
        else:
            print(f"✗ 登录失败: {login_result}")
    else:
        print(f"✗ 登录请求失败，状态码: {login_response.status_code}")
        print(f"响应内容: {login_response.text}")

if __name__ == '__main__':
    print("=== 测试修复后的船期查询API ===")
    test_cabin_grouping_api()
    print("\n=== 测试完成 ===")
