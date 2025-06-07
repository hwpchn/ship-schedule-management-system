"""
URL configuration for ship_schedule project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


@api_view(['GET'])
@permission_classes([AllowAny])
def api_health_check(request):
    """
    API健康检查端点
    用于验证API服务是否正常运行
    """
    return Response({
        'status': 'ok',
        'message': '船舶调度系统API服务正常运行',
        'version': '1.0.0'
    }, status=status.HTTP_200_OK)


urlpatterns = [
    # 管理后台
    path('admin/', admin.site.urls),

    # API根路径健康检查
    path('api/', api_health_check, name='api_health_check'),

    # 认证相关API
    path('api/auth/', include('authentication.urls')),

    # 船舶航线相关API
    path('api/', include('schedules.urls')),

    # 本地费用相关API
    path('api/local-fees/', include('local_fees.urls')),
]

# 开发环境下提供媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
