"""
通用工具类
包含标准化响应、权限检查等工具函数
"""
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class StandardResponse:
    """
    标准化API响应格式
    确保所有API返回一致的响应格式
    """
    
    @staticmethod
    def success(data=None, message="操作成功", meta=None, status_code=status.HTTP_200_OK):
        """
        成功响应
        
        Args:
            data: 返回的数据
            message: 成功消息
            meta: 额外的元数据（如分页信息）
            status_code: HTTP状态码
            
        Returns:
            Response: 标准化的成功响应
        """
        response_data = {
            'success': True,
            'message': message,
            'data': data,
            'code': status_code
        }
        
        if meta:
            response_data['meta'] = meta
            
        return Response(response_data, status=status_code)
    
    @staticmethod
    def error(message="操作失败", errors=None, status_code=status.HTTP_400_BAD_REQUEST, code=None):
        """
        错误响应
        
        Args:
            message: 错误消息
            errors: 详细错误信息
            status_code: HTTP状态码
            code: 自定义错误代码
            
        Returns:
            Response: 标准化的错误响应
        """
        response_data = {
            'success': False,
            'message': message,
            'data': None,
            'code': code or status_code
        }
        
        if errors:
            response_data['errors'] = errors
            
        return Response(response_data, status=status_code)
    
    @staticmethod
    def paginated_success(queryset, serializer_class, request, message="获取成功"):
        """
        分页成功响应
        
        Args:
            queryset: 查询集
            serializer_class: 序列化器类
            request: 请求对象
            message: 成功消息
            
        Returns:
            Response: 带分页信息的标准化响应
        """
        from django.core.paginator import Paginator
        from rest_framework.pagination import PageNumberPagination
        
        # 获取分页参数
        page_size = request.GET.get('page_size', getattr(settings, 'REST_FRAMEWORK', {}).get('PAGE_SIZE', 20))
        page = request.GET.get('page', 1)
        
        try:
            page_size = int(page_size)
            page = int(page)
        except (ValueError, TypeError):
            page_size = 20
            page = 1
        
        # 分页处理
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        # 序列化数据
        serializer = serializer_class(page_obj.object_list, many=True)
        
        # 构建分页元数据
        meta = {
            'total': paginator.count,
            'page': page,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
        
        return StandardResponse.success(
            data=serializer.data,
            message=message,
            meta=meta
        )


class PermissionHelper:
    """
    权限检查助手类
    简化权限验证逻辑
    """
    
    @staticmethod
    def check_permission(user, permission_code):
        """
        检查用户权限
        
        Args:
            user: 用户对象
            permission_code: 权限代码
            
        Returns:
            bool: 是否有权限
        """
        if not user or not user.is_authenticated:
            return False
            
        # 超级管理员拥有所有权限
        if user.is_superuser:
            return True
            
        # 检查用户权限
        return user.has_permission(permission_code)
    
    @staticmethod
    def require_permission(permission_code):
        """
        权限装饰器
        
        Args:
            permission_code: 所需权限代码
            
        Returns:
            decorator: 权限装饰器
        """
        def decorator(view_func):
            def wrapper(self, request, *args, **kwargs):
                if not PermissionHelper.check_permission(request.user, permission_code):
                    return StandardResponse.error(
                        message="权限不足",
                        status_code=status.HTTP_403_FORBIDDEN
                    )
                return view_func(self, request, *args, **kwargs)
            return wrapper
        return decorator


class CacheHelper:
    """
    缓存助手类
    简化缓存操作
    """
    
    @staticmethod
    def get_or_set(key, callable_func, timeout=300):
        """
        获取缓存，如果不存在则设置
        
        Args:
            key: 缓存键
            callable_func: 获取数据的函数
            timeout: 缓存超时时间（秒）
            
        Returns:
            缓存的数据
        """
        try:
            data = cache.get(key)
            if data is None:
                data = callable_func()
                cache.set(key, data, timeout)
            return data
        except Exception as e:
            logger.warning(f"缓存操作失败: {e}")
            return callable_func()
    
    @staticmethod
    def delete_pattern(pattern):
        """
        删除匹配模式的缓存
        
        Args:
            pattern: 缓存键模式
        """
        try:
            if hasattr(cache, 'delete_pattern'):
                cache.delete_pattern(pattern)
            else:
                # Fallback for non-Redis cache
                logger.warning("当前缓存后端不支持模式删除")
        except Exception as e:
            logger.warning(f"删除缓存模式失败: {e}")


class ValidationHelper:
    """
    验证助手类
    常用的数据验证方法
    """
    
    @staticmethod
    def validate_port_code(port_code):
        """
        验证港口代码格式
        
        Args:
            port_code: 港口代码
            
        Returns:
            bool: 是否有效
        """
        if not port_code or not isinstance(port_code, str):
            return False
        return len(port_code.strip()) >= 3 and port_code.strip().isalpha()
    
    @staticmethod
    def validate_vessel_info(vessel, voyage):
        """
        验证船舶信息
        
        Args:
            vessel: 船名
            voyage: 航次
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        if not vessel or not voyage:
            return False, "船名和航次不能为空"
            
        if len(vessel.strip()) < 2:
            return False, "船名至少需要2个字符"
            
        if len(voyage.strip()) < 1:
            return False, "航次不能为空"
            
        return True, None


# 导出常用类和函数
__all__ = [
    'StandardResponse',
    'PermissionHelper', 
    'CacheHelper',
    'ValidationHelper'
]