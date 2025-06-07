"""
用户头像功能测试
测试头像上传、删除和获取功能
"""
import os
import tempfile
from PIL import Image
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class AvatarUploadTest(APITestCase):
    """头像上传功能测试"""

    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        self.user_data = {
            'email': 'testuser@example.com',
            'password': 'testpass123',
            'first_name': '测试',
            'last_name': '用户'
        }
        self.user = User.objects.create_user(**self.user_data)

        # 获取JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        # 设置认证头
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # API端点
        self.avatar_url = '/api/auth/me/avatar/'
        self.user_info_url = '/api/auth/me/'

    def create_test_image(self, format='JPEG', size=(100, 100)):
        """创建测试图片"""
        image = Image.new('RGB', size, color='red')
        temp_file = tempfile.NamedTemporaryFile(suffix=f'.{format.lower()}', delete=False)
        image.save(temp_file.name, format=format)
        temp_file.seek(0)
        return temp_file

    def test_upload_avatar_success(self):
        """测试头像上传成功"""
        # 创建测试图片
        test_image = self.create_test_image()

        with open(test_image.name, 'rb') as img_file:
            avatar_file = SimpleUploadedFile(
                name='test_avatar.jpg',
                content=img_file.read(),
                content_type='image/jpeg'
            )

            response = self.client.post(self.avatar_url, {'avatar': avatar_file})

        # 清理临时文件
        os.unlink(test_image.name)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], '头像上传成功')
        self.assertIn('avatar_url', response.data['data'])
        self.assertIn('user', response.data['data'])

        # 验证用户头像已保存
        self.user.refresh_from_db()
        self.assertTrue(self.user.avatar)

    def test_upload_avatar_invalid_format(self):
        """测试上传不支持的文件格式"""
        # 创建文本文件
        text_file = SimpleUploadedFile(
            name='test.txt',
            content=b'This is not an image',
            content_type='text/plain'
        )

        response = self.client.post(self.avatar_url, {'avatar': text_file})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('errors', response.data)

    def test_upload_avatar_too_large(self):
        """测试上传过大的文件"""
        # 创建大图片 (模拟超过5MB)
        test_image = self.create_test_image(size=(3000, 3000))

        with open(test_image.name, 'rb') as img_file:
            # 创建一个模拟的大文件
            large_content = img_file.read() * 100  # 放大文件内容
            avatar_file = SimpleUploadedFile(
                name='large_avatar.jpg',
                content=large_content,
                content_type='image/jpeg'
            )

            response = self.client.post(self.avatar_url, {'avatar': avatar_file})

        # 清理临时文件
        os.unlink(test_image.name)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    def test_upload_avatar_without_authentication(self):
        """测试未认证用户上传头像"""
        # 清除认证信息
        self.client.credentials()

        test_image = self.create_test_image()

        with open(test_image.name, 'rb') as img_file:
            avatar_file = SimpleUploadedFile(
                name='test_avatar.jpg',
                content=img_file.read(),
                content_type='image/jpeg'
            )

            response = self.client.post(self.avatar_url, {'avatar': avatar_file})

        # 清理临时文件
        os.unlink(test_image.name)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_avatar_success(self):
        """测试删除头像成功"""
        # 先上传头像
        test_image = self.create_test_image()

        with open(test_image.name, 'rb') as img_file:
            avatar_file = SimpleUploadedFile(
                name='test_avatar.jpg',
                content=img_file.read(),
                content_type='image/jpeg'
            )

            self.client.post(self.avatar_url, {'avatar': avatar_file})

        # 清理临时文件
        os.unlink(test_image.name)

        # 验证头像已上传
        self.user.refresh_from_db()
        self.assertTrue(self.user.avatar)

        # 删除头像
        response = self.client.delete(self.avatar_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], '头像删除成功')

        # 验证头像已删除
        self.user.refresh_from_db()
        self.assertFalse(self.user.avatar)

    def test_delete_avatar_without_avatar(self):
        """测试删除不存在的头像"""
        response = self.client.delete(self.avatar_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['message'], '用户暂无头像')

    def test_get_user_info_with_avatar(self):
        """测试获取用户信息包含头像URL"""
        # 先上传头像
        test_image = self.create_test_image()

        with open(test_image.name, 'rb') as img_file:
            avatar_file = SimpleUploadedFile(
                name='test_avatar.jpg',
                content=img_file.read(),
                content_type='image/jpeg'
            )

            self.client.post(self.avatar_url, {'avatar': avatar_file})

        # 清理临时文件
        os.unlink(test_image.name)

        # 获取用户信息
        response = self.client.get(self.user_info_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertIn('avatar_url', response.data['user'])
        self.assertIsNotNone(response.data['user']['avatar_url'])

    def test_replace_existing_avatar(self):
        """测试替换现有头像"""
        # 上传第一个头像
        test_image1 = self.create_test_image()

        with open(test_image1.name, 'rb') as img_file:
            avatar_file1 = SimpleUploadedFile(
                name='avatar1.jpg',
                content=img_file.read(),
                content_type='image/jpeg'
            )

            response1 = self.client.post(self.avatar_url, {'avatar': avatar_file1})

        os.unlink(test_image1.name)

        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        first_avatar_url = response1.data['data']['avatar_url']

        # 上传第二个头像
        test_image2 = self.create_test_image()

        with open(test_image2.name, 'rb') as img_file:
            avatar_file2 = SimpleUploadedFile(
                name='avatar2.jpg',
                content=img_file.read(),
                content_type='image/jpeg'
            )

            response2 = self.client.post(self.avatar_url, {'avatar': avatar_file2})

        os.unlink(test_image2.name)

        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        second_avatar_url = response2.data['data']['avatar_url']

        # 验证头像URL已更新
        self.assertNotEqual(first_avatar_url, second_avatar_url)

        # 验证用户只有一个头像
        self.user.refresh_from_db()
        self.assertTrue(self.user.avatar)

    def tearDown(self):
        """测试后清理"""
        # 清理用户头像文件
        if self.user.avatar:
            self.user.delete_avatar()

        # 删除用户
        self.user.delete()


class UserModelAvatarTest(TestCase):
    """用户模型头像相关方法测试"""

    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def test_get_avatar_url_without_avatar(self):
        """测试没有头像时获取头像URL"""
        avatar_url = self.user.get_avatar_url()
        self.assertIsNone(avatar_url)

    def test_delete_avatar_without_avatar(self):
        """测试删除不存在的头像"""
        # 应该不会抛出异常
        self.user.delete_avatar()
        self.assertFalse(self.user.avatar)

    def tearDown(self):
        """测试后清理"""
        if self.user.avatar:
            self.user.delete_avatar()
        self.user.delete()
