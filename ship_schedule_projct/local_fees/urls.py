"""
本地费用应用的URL配置
简化版本
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LocalFeeViewSet

router = DefaultRouter()
router.register(r'local-fees', LocalFeeViewSet, basename='local-fees')

urlpatterns = [
    path('', include(router.urls)),
] 