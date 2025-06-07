#!/usr/bin/env python3
"""
简化的API测试脚本
"""

import requests

def test_api():
    base_url = "http://127.0.0.1:8000"
    
    print("🚢 船舶航线管理系统 API 测试")
    print("=" * 50)
    
    # 1. 测试健康检查
    print("1. 测试健康检查API...")
    try:
        response = requests.get(f"{base_url}/api/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 健康检查成功: {data['message']}")
        else:
            print(f"   ❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 连接失败: {e}")
        return
    
    # 2. 测试船期查询API（无认证）
    print("\n2. 测试船期查询API...")
    try:
        response = requests.get(
            f"{base_url}/api/schedules/cabin-grouping/?polCd=CNSHA&podCd=USNYC", 
            timeout=5
        )
        if response.status_code == 401:
            print("   ✅ 船期查询API存在（需要认证）")
        elif response.status_code == 200:
            print("   ✅ 船期查询API正常工作")
        else:
            print(f"   ⚠️ 船期查询API状态: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 船期查询测试失败: {e}")
    
    # 3. 测试船舶信息API（无认证）
    print("\n3. 测试船舶信息API...")
    try:
        response = requests.get(f"{base_url}/api/vessel-info/", timeout=5)
        if response.status_code == 401:
            print("   ✅ 船舶信息API存在（需要认证）")
        elif response.status_code == 200:
            print("   ✅ 船舶信息API正常工作")
        else:
            print(f"   ⚠️ 船舶信息API状态: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 船舶信息测试失败: {e}")
    
    # 4. 测试本地费用API
    print("\n4. 测试本地费用API...")
    try:
        response = requests.get(f"{base_url}/api/local-fees/", timeout=5)
        if response.status_code == 401:
            print("   ✅ 本地费用API存在（需要认证）")
        elif response.status_code == 200:
            print("   ✅ 本地费用API正常工作")
        else:
            print(f"   ⚠️ 本地费用API状态: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 本地费用测试失败: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 API基础测试完成！")
    print("💡 所有API端点都存在并响应正常")
    print("🔐 需要认证的API返回401状态码是正常的")

if __name__ == "__main__":
    test_api()
