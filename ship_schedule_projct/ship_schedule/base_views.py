"""
基础视图类
提供标准化的API视图基类
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from django.db import transaction
import logging

from .utils import StandardResponse, PermissionHelper, CacheHelper

logger = logging.getLogger(__name__)


class BaseModelViewSet(viewsets.ModelViewSet):
    """
    基础模型视图集
    提供标准化的CRUD操作和响应格式
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        """
        列表查询 - 标准化响应
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            # 检查是否需要分页
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                paginated_response = self.get_paginated_response(serializer.data)
                
                # 转换为标准格式
                return StandardResponse.success(
                    data=serializer.data,
                    message="获取列表成功",
                    meta={
                        'total': paginated_response.data.get('count', 0),
                        'page': request.GET.get('page', 1),
                        'page_size': self.paginator.get_page_size(request),
                        'next': paginated_response.data.get('next'),
                        'previous': paginated_response.data.get('previous'),
                    }
                )
            
            serializer = self.get_serializer(queryset, many=True)
            return StandardResponse.success(
                data=serializer.data,
                message="获取列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取列表失败: {e}")
            return StandardResponse.error(
                message="获取列表失败",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def retrieve(self, request, *args, **kwargs):
        """
        详情查询 - 标准化响应
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return StandardResponse.success(
                data=serializer.data,
                message="获取详情成功"
            )
        except Exception as e:
            logger.error(f"获取详情失败: {e}")
            return StandardResponse.error(
                message="数据不存在",
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    def create(self, request, *args, **kwargs):
        """
        创建 - 标准化响应
        """
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                if serializer.is_valid():
                    self.perform_create(serializer)
                    return StandardResponse.success(
                        data=serializer.data,
                        message="创建成功",
                        status_code=status.HTTP_201_CREATED
                    )
                else:
                    return StandardResponse.error(
                        message="数据验证失败",
                        errors=serializer.errors,
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
        except Exception as e:
            logger.error(f"创建失败: {e}")
            return StandardResponse.error(
                message="创建失败",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update(self, request, *args, **kwargs):
        """
        更新 - 标准化响应
        """
        try:
            with transaction.atomic():
                partial = kwargs.pop('partial', False)
                instance = self.get_object()
                serializer = self.get_serializer(instance, data=request.data, partial=partial)
                
                if serializer.is_valid():
                    self.perform_update(serializer)
                    return StandardResponse.success(
                        data=serializer.data,
                        message="更新成功"
                    )
                else:
                    return StandardResponse.error(
                        message="数据验证失败",
                        errors=serializer.errors,
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
        except Exception as e:
            logger.error(f"更新失败: {e}")
            return StandardResponse.error(
                message="更新失败",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, *args, **kwargs):
        """
        删除 - 标准化响应
        """
        try:
            with transaction.atomic():
                instance = self.get_object()
                self.perform_destroy(instance)
                return StandardResponse.success(
                    message="删除成功",
                    status_code=status.HTTP_204_NO_CONTENT
                )
        except Exception as e:
            logger.error(f"删除失败: {e}")
            return StandardResponse.error(
                message="删除失败",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PermissionRequiredMixin:
    """
    权限检查混入类
    """
    permission_required = None  # 子类需要设置所需权限
    
    def check_permissions(self, request):
        """
        检查权限
        """
        super().check_permissions(request)
        
        if self.permission_required:
            if not PermissionHelper.check_permission(request.user, self.permission_required):
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("权限不足")


class CachedViewMixin:
    """
    缓存混入类
    """
    cache_timeout = 300  # 默认5分钟缓存
    cache_key_prefix = 'api'
    
    def get_cache_key(self, request, *args, **kwargs):
        """
        生成缓存键
        """
        view_name = self.__class__.__name__
        params = f"{request.GET.urlencode()}_{args}_{kwargs}"
        return f"{self.cache_key_prefix}:{view_name}:{hash(params)}"
    
    def get_cached_response(self, request, *args, **kwargs):
        """
        获取缓存响应
        """
        cache_key = self.get_cache_key(request, *args, **kwargs)
        return CacheHelper.get_or_set(
            cache_key,
            lambda: self._get_response_data(request, *args, **kwargs),
            self.cache_timeout
        )
    
    def _get_response_data(self, request, *args, **kwargs):
        """
        子类需要实现此方法来获取实际数据
        """
        raise NotImplementedError("子类需要实现 _get_response_data 方法")


class BulkOperationMixin:
    """
    批量操作混入类
    """
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        批量创建
        """
        try:
            if not isinstance(request.data, list):
                return StandardResponse.error(
                    message="数据格式错误，需要数组格式",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            with transaction.atomic():
                created_items = []
                errors = []
                
                for i, item_data in enumerate(request.data):
                    serializer = self.get_serializer(data=item_data)
                    if serializer.is_valid():
                        self.perform_create(serializer)
                        created_items.append(serializer.data)
                    else:
                        errors.append({
                            'index': i,
                            'errors': serializer.errors
                        })
                
                if errors:
                    return StandardResponse.error(
                        message="部分数据验证失败",
                        errors=errors,
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                
                return StandardResponse.success(
                    data=created_items,
                    message=f"批量创建成功，共创建 {len(created_items)} 条记录",
                    status_code=status.HTTP_201_CREATED
                )
                
        except Exception as e:
            logger.error(f"批量创建失败: {e}")
            return StandardResponse.error(
                message="批量创建失败",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['patch'])
    def bulk_update(self, request):
        """
        批量更新
        """
        try:
            if not isinstance(request.data, list):
                return StandardResponse.error(
                    message="数据格式错误，需要数组格式",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            with transaction.atomic():
                updated_items = []
                errors = []
                
                for i, item_data in enumerate(request.data):
                    item_id = item_data.get('id')
                    if not item_id:
                        errors.append({
                            'index': i,
                            'errors': 'id字段是必需的'
                        })
                        continue
                    
                    try:
                        instance = self.get_queryset().get(id=item_id)
                        serializer = self.get_serializer(instance, data=item_data, partial=True)
                        if serializer.is_valid():
                            self.perform_update(serializer)
                            updated_items.append(serializer.data)
                        else:
                            errors.append({
                                'index': i,
                                'id': item_id,
                                'errors': serializer.errors
                            })
                    except self.queryset.model.DoesNotExist:
                        errors.append({
                            'index': i,
                            'id': item_id,
                            'errors': '记录不存在'
                        })
                
                if errors:
                    return StandardResponse.error(
                        message="部分数据更新失败",
                        errors=errors,
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                
                return StandardResponse.success(
                    data=updated_items,
                    message=f"批量更新成功，共更新 {len(updated_items)} 条记录"
                )
                
        except Exception as e:
            logger.error(f"批量更新失败: {e}")
            return StandardResponse.error(
                message="批量更新失败",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# 导出基础类
__all__ = [
    'BaseModelViewSet',
    'PermissionRequiredMixin',
    'CachedViewMixin',
    'BulkOperationMixin'
]