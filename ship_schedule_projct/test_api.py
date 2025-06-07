#!/usr/bin/env python3
"""
API测试脚本
测试船舶航线管理系统的核心API功能
"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_health_check():
    """测试健康检查API"""
    print("🔍 测试健康检查API...")
    try:
        response = requests.get(f"{BASE_URL}/api/")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

def test_login():
    """测试登录API"""
    print("\n🔐 测试登录API...")
    try:
        data = {
            "email": "test@example.com",
            "password": "testpass123"
        }
        response = requests.post(
            f"{BASE_URL}/api/auth/login/",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ 登录成功")
            print(f"用户: {result.get('user', {}).get('email')}")
            return result.get('tokens', {}).get('access')
        else:
            print(f"❌ 登录失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 登录测试失败: {e}")
        return None

def test_schedules_api(token):
    """测试船期查询API"""
    print("\n🚢 测试船期查询API...")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 测试共舱分组API
        response = requests.get(
            f"{BASE_URL}/api/schedules/cabin-grouping/?polCd=CNSHA&podCd=USNYC",
            headers=headers
        )
        print(f"共舱分组API状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 船期查询API正常")
            print(f"返回数据类型: {type(result)}")
            return True
        else:
            print(f"❌ 船期查询失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 船期查询测试失败: {e}")
        return False

def test_vessel_info_api(token):
    """测试船舶信息API"""
    print("\n📊 测试船舶信息API...")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{BASE_URL}/api/vessel-info/",
            headers=headers
        )
        print(f"船舶信息API状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 船舶信息API正常")
            return True
        else:
            print(f"❌ 船舶信息API失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 船舶信息测试失败: {e}")
        return False

def test_public_apis():
    """测试公开API"""
    print("\n🌐 测试公开API...")
    try:
        # 测试船期查询（可能不需要认证）
        response = requests.get(f"{BASE_URL}/api/schedules/cabin-grouping/?polCd=CNSHA&podCd=USNYC")
        print(f"公开船期查询状态码: {response.status_code}")

        if response.status_code in [200, 401, 403]:
            print("✅ 船期查询API端点存在")
            return True
        else:
            print(f"❌ 船期查询API异常: {response.text}")
            return False

    except Exception as e:
        print(f"❌ 公开API测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚢 开始API测试...")

    # 测试健康检查
    if not test_health_check():
        print("❌ 健康检查失败，退出测试")
        sys.exit(1)

    # 测试公开API
    test_public_apis()

    # 测试登录
    token = test_login()
    if not token:
        print("⚠️ 登录失败，跳过需要认证的API测试")
        print("💡 这可能是因为用户不存在或密码错误")
    else:
        # 测试船期API
        test_schedules_api(token)

        # 测试船舶信息API
        test_vessel_info_api(token)

    print("\n🎉 API测试完成！")

if __name__ == "__main__":
    main()
