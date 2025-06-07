#!/usr/bin/env python3
"""
头像上传功能测试脚本
用于验证头像上传和媒体文件服务是否正常工作
"""

import requests
import os
from PIL import Image
import io

# API配置
API_BASE_URL = 'http://localhost:8000'
LOGIN_URL = f'{API_BASE_URL}/api/auth/login/'
AVATAR_URL = f'{API_BASE_URL}/api/auth/me/avatar/'
USER_INFO_URL = f'{API_BASE_URL}/api/auth/me/'

def create_test_image():
    """创建测试图片"""
    # 创建一个简单的测试图片
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def test_avatar_upload():
    """测试头像上传功能"""
    print("🧪 开始测试头像上传功能...")
    
    # 1. 登录获取token
    print("\n1️⃣ 登录获取访问令牌...")
    login_data = {
        'email': 'admin@example.com',
        'password': 'admin123'
    }
    
    try:
        response = requests.post(LOGIN_URL, json=login_data)
        if response.status_code == 200:
            token = response.json()['tokens']['access']
            print(f"✅ 登录成功，获取到token: {token[:20]}...")
        else:
            print(f"❌ 登录失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 登录请求失败: {e}")
        return False
    
    # 2. 上传头像
    print("\n2️⃣ 上传测试头像...")
    headers = {'Authorization': f'Bearer {token}'}
    
    # 创建测试图片
    test_image = create_test_image()
    files = {'avatar': ('test_avatar.png', test_image, 'image/png')}
    
    try:
        response = requests.post(AVATAR_URL, headers=headers, files=files)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                avatar_url = result['data']['avatar_url']
                print(f"✅ 头像上传成功: {avatar_url}")
            else:
                print(f"❌ 头像上传失败: {result.get('message')}")
                return False
        else:
            print(f"❌ 头像上传请求失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 头像上传请求异常: {e}")
        return False
    
    # 3. 验证头像文件是否可访问
    print("\n3️⃣ 验证头像文件访问...")
    media_url = f"{API_BASE_URL}{avatar_url}"
    
    try:
        response = requests.head(media_url)
        if response.status_code == 200:
            print(f"✅ 头像文件可正常访问: {media_url}")
            print(f"   Content-Type: {response.headers.get('Content-Type')}")
            print(f"   Content-Length: {response.headers.get('Content-Length')} bytes")
        else:
            print(f"❌ 头像文件访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 头像文件访问异常: {e}")
        return False
    
    # 4. 获取用户信息验证头像URL
    print("\n4️⃣ 验证用户信息中的头像URL...")
    
    try:
        response = requests.get(USER_INFO_URL, headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            user_avatar_url = user_info.get('user', {}).get('avatar_url')
            if user_avatar_url:
                print(f"✅ 用户信息中包含头像URL: {user_avatar_url}")
                
                # 验证URL是否一致
                if user_avatar_url == avatar_url:
                    print("✅ 头像URL一致性验证通过")
                else:
                    print(f"⚠️ 头像URL不一致:")
                    print(f"   上传返回: {avatar_url}")
                    print(f"   用户信息: {user_avatar_url}")
            else:
                print("❌ 用户信息中未找到头像URL")
                return False
        else:
            print(f"❌ 获取用户信息失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取用户信息异常: {e}")
        return False
    
    print("\n🎉 头像上传功能测试完成！所有测试通过。")
    return True

def test_existing_avatar():
    """测试现有头像文件访问"""
    print("\n🔍 测试现有头像文件访问...")
    
    existing_avatar_url = f"{API_BASE_URL}/media/user_avatars/1/avatar_1.png"
    
    try:
        response = requests.head(existing_avatar_url)
        if response.status_code == 200:
            print(f"✅ 现有头像文件可正常访问: {existing_avatar_url}")
            print(f"   Content-Type: {response.headers.get('Content-Type')}")
            print(f"   Last-Modified: {response.headers.get('Last-Modified')}")
        else:
            print(f"❌ 现有头像文件访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 现有头像文件访问异常: {e}")

if __name__ == '__main__':
    print("🚀 头像上传功能测试脚本")
    print("=" * 50)
    
    # 测试现有头像文件
    test_existing_avatar()
    
    # 测试完整的头像上传流程
    success = test_avatar_upload()
    
    if success:
        print("\n✅ 所有测试通过！头像上传功能正常工作。")
        print("\n📋 前端修复建议:")
        print("1. 确保前端使用正确的后端URL: http://localhost:8000")
        print("2. 媒体文件URL应该是: http://localhost:8000/media/...")
        print("3. 不要使用前端服务器URL: http://localhost:3000/media/...")
    else:
        print("\n❌ 测试失败，请检查后端配置。")
