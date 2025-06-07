"""
本地费用相关的API视图
简化版本，只包含基本的CRUD操作
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import LocalFee
from .serializers import LocalFeeSerializer, LocalFeeQuerySerializer
from authentication.permissions import HasPermission, get_permission_map


class LocalFeeViewSet(viewsets.ModelViewSet):
    """
    本地费用管理API
    提供本地费用的增删改查功能
    """
    queryset = LocalFee.objects.all()
    serializer_class = LocalFeeSerializer

    def get_permissions(self):
        """
        根据操作类型设置权限
        """
        permission_map = get_permission_map()

        if self.action == 'list':
            # 查看列表权限
            self.permission_classes = [lambda: HasPermission(permission_map['local_fee_list'])]
        elif self.action == 'retrieve':
            # 查看详情权限
            self.permission_classes = [lambda: HasPermission(permission_map['local_fee_detail'])]
        elif self.action == 'create':
            # 创建权限
            self.permission_classes = [lambda: HasPermission(permission_map['local_fee_create'])]
        elif self.action in ['update', 'partial_update']:
            # 修改权限
            self.permission_classes = [lambda: HasPermission(permission_map['local_fee_update'])]
        elif self.action == 'destroy':
            # 删除权限
            self.permission_classes = [lambda: HasPermission(permission_map['local_fee_delete'])]
        elif self.action == 'query_fees':
            # 查询权限（前台API）
            self.permission_classes = [lambda: HasPermission(permission_map['local_fee_query'])]
        else:
            # 默认需要认证
            self.permission_classes = [IsAuthenticated]

        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        """获取查询集并支持过滤"""
        queryset = super().get_queryset()

        # 支持通过polCd, podCd, carriercd过滤
        polCd = self.request.query_params.get('polCd')
        podCd = self.request.query_params.get('podCd')
        carriercd = self.request.query_params.get('carriercd')

        if polCd:
            queryset = queryset.filter(polCd=polCd)
        if podCd:
            queryset = queryset.filter(podCd=podCd)
        if carriercd:
            queryset = queryset.filter(carriercd=carriercd)

        return queryset.order_by('id')

    def list(self, request):
        """获取本地费用列表"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': 'success',
            'data': serializer.data
        })

    def create(self, request):
        """创建新的本地费用"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': '本地费用创建成功',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status': 'error',
            'message': '数据验证失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """获取单个本地费用详情"""
        local_fee = get_object_or_404(LocalFee, pk=pk)
        serializer = self.get_serializer(local_fee)
        return Response({
            'status': 'success',
            'data': serializer.data
        })

    def update(self, request, pk=None, partial=False):
        """更新本地费用信息"""
        local_fee = get_object_or_404(LocalFee, pk=pk)
        serializer = self.get_serializer(local_fee, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': '本地费用更新成功',
                'data': serializer.data
            })
        return Response({
            'status': 'error',
            'message': '数据验证失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        """部分更新本地费用信息"""
        return self.update(request, pk, partial=True)

    def destroy(self, request, pk=None):
        """删除本地费用"""
        local_fee = get_object_or_404(LocalFee, pk=pk)
        local_fee.delete()
        return Response({
            'status': 'success',
            'message': '本地费用删除成功'
        })

    @action(detail=False, methods=['get'], url_path='query')
    def query_fees(self, request):
        """
        查询本地费用
        通过polCd, podCd, carriercd查询所有费用，按照id升序排列
        返回格式按照前端要求
        """
        polCd = request.query_params.get('polCd')
        podCd = request.query_params.get('podCd')
        carriercd = request.query_params.get('carriercd')

        if not polCd or not podCd:
            return Response({
                'status': 'error',
                'message': '起运港五字码(polCd)和目的港五字码(podCd)为必填参数'
            }, status=status.HTTP_400_BAD_REQUEST)

        queryset = LocalFee.objects.filter(polCd=polCd, podCd=podCd)

        if carriercd:
            queryset = queryset.filter(carriercd=carriercd)

        queryset = queryset.order_by('id')

        serializer = LocalFeeQuerySerializer(queryset, many=True)
        return Response({
            'status': 'success',
            'data': serializer.data
        })