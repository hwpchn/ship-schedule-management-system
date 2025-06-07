from django.shortcuts import render
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Max
from django.db import models
import json
from collections import defaultdict, Counter
from datetime import datetime, timezone
from .models import VesselSchedule, VesselInfoFromCompany
from .serializers import (
    VesselScheduleSerializer,
    VesselScheduleListSerializer,
    VesselScheduleCreateSerializer,
    VesselInfoFromCompanySerializer,
    GroupInfoSerializer,
    CabinGroupingResponseSerializer
)
from authentication.permissions import HasPermission, get_permission_map
from .signals import manual_sync_vessel_schedules
from django.core.paginator import Paginator, EmptyPage


class VesselScheduleListCreateView(generics.ListCreateAPIView):
    """船舶航线列表和创建视图"""
    queryset = VesselSchedule.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'polCd', 'podCd', 'carriercd', 'data_version']
    search_fields = ['vessel', 'voyage', 'pol', 'pod', 'routeCd']
    ordering_fields = ['fetch_date', 'eta', 'etd', 'data_version']
    ordering = ['-fetch_date']

    def get_serializer_class(self):
        """根据请求方法选择序列化器"""
        if self.request.method == 'POST':
            return VesselScheduleCreateSerializer
        return VesselScheduleListSerializer

    def get_queryset(self):
        """自定义查询集"""
        queryset = VesselSchedule.objects.all()

        # 按状态过滤（默认只显示有效数据）
        status_filter = self.request.query_params.get('status', '1')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # 按起运港和目的港过滤
        pol_cd = self.request.query_params.get('pol_cd')
        pod_cd = self.request.query_params.get('pod_cd')
        if pol_cd:
            queryset = queryset.filter(polCd=pol_cd)
        if pod_cd:
            queryset = queryset.filter(podCd=pod_cd)

        # 按日期范围过滤
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(fetch_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(fetch_date__lte=date_to)

        return queryset


class VesselScheduleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """船舶航线详情、更新和删除视图"""
    queryset = VesselSchedule.objects.all()
    serializer_class = VesselScheduleSerializer
    permission_classes = [IsAuthenticated]


class VesselInfoFromCompanyListCreateView(generics.ListCreateAPIView):
    """船舶额外信息列表和创建视图"""
    queryset = VesselInfoFromCompany.objects.all()
    serializer_class = VesselInfoFromCompanySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['carriercd', 'polCd', 'podCd']
    search_fields = ['vessel', 'voyage', 'carriercd']
    ordering_fields = ['carriercd', 'vessel', 'voyage']
    ordering = ['carriercd', 'vessel', 'voyage']

    def perform_create(self, serializer):
        """创建时的额外处理"""
        # 记录创建者信息（如果需要的话）
        serializer.save()


class VesselInfoFromCompanyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """船舶额外信息详情、更新和删除视图"""
    queryset = VesselInfoFromCompany.objects.all()
    serializer_class = VesselInfoFromCompanySerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        """更新时的额外处理"""
        # 可以在这里添加更新日志或其他业务逻辑
        serializer.save()

    def perform_destroy(self, instance):
        """删除时的额外处理"""
        # 可以在这里添加删除日志或其他业务逻辑
        instance.delete()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cabin_grouping_api(request):
    """
    共舱分组API
    根据shareCabins字段中的船公司组合进行分组
    返回按班期排序的分组数据
    """
    try:
        # 获取请求参数
        pol_cd = request.GET.get('polCd')
        pod_cd = request.GET.get('podCd')

        if not pol_cd or not pod_cd:
            return Response({
                'success': False,
                'message': '缺少必需参数 polCd 和 podCd',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # 构建过滤条件
        # 首先获取最新的数据版本号
        latest_version = VesselSchedule.objects.filter(
            polCd=pol_cd,
            podCd=pod_cd,
            status=1
        ).aggregate(max_version=models.Max('data_version'))['max_version']

        if latest_version is None:
            latest_version = 1  # 默认版本号

        queryset = VesselSchedule.objects.filter(
            polCd=pol_cd,
            podCd=pod_cd,
            status=1,  # 只查询有效记录
            data_version=latest_version  # 只查询最新版本
        )

        if not queryset.exists():
            return Response({
                'success': True,
                'message': '没有找到符合条件的航线数据',
                'data': {
                    'version': latest_version,
                    'total_groups': 0,
                    'filter': {'polCd': pol_cd, 'podCd': pod_cd},
                    'groups': []
                }
            })

        # 分组处理
        groups = defaultdict(list)

        for schedule in queryset:
            # 解析shareCabins字段获取船公司代码
            carrier_codes = []
            if schedule.shareCabins:
                try:
                    share_cabins_data = json.loads(schedule.shareCabins) if isinstance(schedule.shareCabins, str) else schedule.shareCabins
                    if isinstance(share_cabins_data, list):
                        for cabin in share_cabins_data:
                            if isinstance(cabin, dict) and 'carrierCd' in cabin:
                                carrier_codes.append(cabin['carrierCd'])
                            elif isinstance(cabin, str):
                                # 如果shareCabins是简单的字符串列表
                                carrier_codes.append(cabin)
                except (json.JSONDecodeError, TypeError):
                    # 如果解析失败，使用当前航线的船公司代码
                    if schedule.carriercd:
                        carrier_codes = [schedule.carriercd]

            # 如果没有解析到船公司代码，使用当前航线的船公司代码
            if not carrier_codes and schedule.carriercd:
                carrier_codes = [schedule.carriercd]

            # 去重并排序形成分组key
            unique_carriers = sorted(list(set(carrier_codes)))
            group_key = ','.join(unique_carriers)

            groups[group_key].append(schedule)

        # 处理每个分组
        result_groups = []
        group_id = 1

        for group_key, group_schedules in groups.items():
            # 按routeEtd排序
            group_schedules.sort(key=lambda x: int(x.routeEtd) if x.routeEtd and x.routeEtd.isdigit() else 999)

            # 计算汇总字段
            carrier_codes = group_key.split(',') if group_key else []

            # 统计routeEtd出现次数，选择最多的
            route_etds = [s.routeEtd for s in group_schedules if s.routeEtd]
            route_etd_counter = Counter(route_etds)
            plan_open = [etd for etd, count in route_etd_counter.most_common(3)]  # 取前3个最常见的

            # 计算最短航程
            durations = []
            for s in group_schedules:
                if s.totalDuration and s.totalDuration.isdigit():
                    durations.append(int(s.totalDuration))
            plan_duration = str(min(durations)) if durations else "--"

            # 构建每个航线的详细信息
            schedule_details = []
            for schedule in group_schedules:
                # 解析shareCabins为JSON格式
                parsed_share_cabins = []
                if schedule.shareCabins:
                    try:
                        parsed_share_cabins = json.loads(schedule.shareCabins) if isinstance(schedule.shareCabins, str) else schedule.shareCabins
                    except (json.JSONDecodeError, TypeError):
                        parsed_share_cabins = []

                schedule_details.append({
                    'id': schedule.id,
                    'vessel': schedule.vessel,
                    'voyage': schedule.voyage,
                    'polCd': schedule.polCd,
                    'podCd': schedule.podCd,
                    'pol': schedule.pol,
                    'pod': schedule.pod,
                    'eta': schedule.eta,
                    'etd': schedule.etd,
                    'routeEtd': schedule.routeEtd,
                    'carriercd': schedule.carriercd,
                    'totalDuration': schedule.totalDuration,
                    'shareCabins': parsed_share_cabins
                })

            group_info = {
                'group_id': f"group_{group_id}",
                'cabins_count': len(carrier_codes),
                'carrier_codes': carrier_codes,
                'plan_open': plan_open,
                'plan_duration': plan_duration,
                'schedules': schedule_details
            }

            result_groups.append(group_info)
            group_id += 1

        # 按plan_open排序（周一到周日）
        def sort_by_plan_open(group):
            if not group['plan_open']:
                return 999  # 没有班期的排在最后
            # 取第一个班期进行排序
            first_open = group['plan_open'][0]
            return int(first_open) if first_open.isdigit() else 999

        result_groups.sort(key=sort_by_plan_open)

        return Response({
            'success': True,
            'message': '共舱分组数据获取成功',
            'data': {
                'version': latest_version,
                'total_groups': len(result_groups),
                'filter': {'polCd': pol_cd, 'podCd': pod_cd},
                'groups': result_groups
            }
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': f'共舱分组数据获取失败: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vessel_schedule_search(request):
    """船舶航线高级搜索"""
    try:
        # 获取搜索参数
        vessel = request.GET.get('vessel', '')
        voyage = request.GET.get('voyage', '')
        pol_cd = request.GET.get('pol_cd', '')
        pod_cd = request.GET.get('pod_cd', '')
        carrier = request.GET.get('carrier', '')

        # 构建查询条件
        queryset = VesselSchedule.objects.filter(status=1)

        if vessel:
            queryset = queryset.filter(vessel__icontains=vessel)
        if voyage:
            queryset = queryset.filter(voyage__icontains=voyage)
        if pol_cd:
            queryset = queryset.filter(polCd=pol_cd)
        if pod_cd:
            queryset = queryset.filter(podCd=pod_cd)
        if carrier:
            queryset = queryset.filter(carriercd__icontains=carrier)

        # 排序
        queryset = queryset.order_by('-fetch_date', 'eta')

        # 分页
        page_size = int(request.GET.get('page_size', 20))
        page = int(request.GET.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size

        total_count = queryset.count()
        results = queryset[start:end]

        serializer = VesselScheduleListSerializer(results, many=True)

        return Response({
            'success': True,
            'message': '搜索成功',
            'data': {
                'results': serializer.data,
                'total_count': total_count,
                'page': page,
                'page_size': page_size,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': f'搜索失败: {str(e)}',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vessel_schedule_stats(request):
    """船舶航线统计信息"""
    try:
        # 总记录数
        total_count = VesselSchedule.objects.count()
        active_count = VesselSchedule.objects.filter(status=1).count()
        inactive_count = VesselSchedule.objects.filter(status=0).count()

        # 按船公司统计
        carrier_stats = VesselSchedule.objects.filter(status=1)\
            .values('carriercd')\
            .annotate(count=Count('id'))\
            .order_by('-count')[:10]

        # 按起运港统计
        pol_stats = VesselSchedule.objects.filter(status=1)\
            .values('polCd', 'pol')\
            .annotate(count=Count('id'))\
            .order_by('-count')[:10]

        # 按目的港统计
        pod_stats = VesselSchedule.objects.filter(status=1)\
            .values('podCd', 'pod')\
            .annotate(count=Count('id'))\
            .order_by('-count')[:10]

        return Response({
            'success': True,
            'message': '统计信息获取成功',
            'data': {
                'total_count': total_count,
                'active_count': active_count,
                'inactive_count': inactive_count,
                'carrier_stats': list(carrier_stats),
                'pol_stats': list(pol_stats),
                'pod_stats': list(pod_stats)
            }
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': f'统计信息获取失败: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def manual_sync_vessel_info_api(request):
    """
    手动同步VesselSchedule到VesselInfoFromCompany的API接口
    需要超级管理员权限
    """
    try:
        # 检查权限（只有超级管理员可以执行同步）
        if not request.user.is_superuser:
            return Response({
                'success': False,
                'message': '只有超级管理员可以执行数据同步操作',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        # 获取请求参数
        vessel_schedule_ids = request.data.get('vessel_schedule_ids')
        force_update = request.data.get('force_update', False)

        # 参数验证
        if vessel_schedule_ids is not None:
            if not isinstance(vessel_schedule_ids, list):
                return Response({
                    'success': False,
                    'message': 'vessel_schedule_ids必须是数组格式',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)

            # 验证ID是否存在
            existing_ids = VesselSchedule.objects.filter(
                id__in=vessel_schedule_ids,
                status=1
            ).values_list('id', flat=True)

            if len(existing_ids) != len(vessel_schedule_ids):
                missing_ids = set(vessel_schedule_ids) - set(existing_ids)
                return Response({
                    'success': False,
                    'message': f'以下VesselSchedule ID不存在或状态无效: {list(missing_ids)}',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)

        # 执行同步
        result = manual_sync_vessel_schedules(
            vessel_schedule_ids=vessel_schedule_ids,
            force_update=force_update
        )

        return Response({
            'success': True,
            'message': '数据同步完成',
            'data': {
                'sync_result': result,
                'total_vessel_info_records': VesselInfoFromCompany.objects.count()
            }
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': f'数据同步失败: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vessel_info_sync_status(request):
    """
    获取VesselInfo同步状态的API接口
    显示同步统计信息
    """
    try:
        # 检查权限
        permission_map = get_permission_map()
        if not request.user.is_superuser and not request.user.has_permission(permission_map.get('vessel_info_list')):
            return Response({
                'success': False,
                'message': '没有权限查看同步状态',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        # 统计VesselSchedule
        total_schedules = VesselSchedule.objects.filter(status=1).count()

        # 统计VesselInfoFromCompany
        total_vessel_info = VesselInfoFromCompany.objects.count()
        filled_vessel_info = VesselInfoFromCompany.objects.filter(
            models.Q(gp_20__isnull=False) |
            models.Q(hq_40__isnull=False) |
            models.Q(cut_off_time__isnull=False) |
            models.Q(price__isnull=False)
        ).count()
        empty_vessel_info = total_vessel_info - filled_vessel_info

        # 按船公司统计
        carrier_stats = VesselInfoFromCompany.objects.values('carriercd')\
            .annotate(count=Count('id'))\
            .order_by('-count')[:10]

        # 按航线统计
        route_stats = VesselInfoFromCompany.objects.values('polCd', 'podCd')\
            .annotate(count=Count('id'))\
            .order_by('-count')[:10]

        return Response({
            'success': True,
            'message': '同步状态获取成功',
            'data': {
                'vessel_schedule_count': total_schedules,
                'vessel_info_count': total_vessel_info,
                'filled_info_count': filled_vessel_info,
                'empty_info_count': empty_vessel_info,
                'fill_rate': round(filled_vessel_info / total_vessel_info * 100, 2) if total_vessel_info > 0 else 0,
                'carrier_stats': list(carrier_stats),
                'route_stats': list(route_stats),
                'last_updated': datetime.now().isoformat()
            }
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取同步状态失败: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vessel_info_query_api(request):
    """
    VesselInfoFromCompany查询API
    根据关联字段查询特定的船舶额外信息记录

    参数：
    - carriercd: 船公司代码（必需）
    - polCd: 起运港五字码（必需）
    - podCd: 目的港五字码（必需）
    - vessel: 船名（必需）
    - voyage: 航次（必需）
    """
    try:
        # 检查权限
        permission_map = get_permission_map()
        if not request.user.is_superuser and not request.user.has_permission(permission_map.get('vessel_info_detail')):
            return Response({
                'success': False,
                'message': '没有权限查看船舶额外信息',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        # 获取请求参数
        carriercd = request.GET.get('carriercd')
        pol_cd = request.GET.get('polCd')
        pod_cd = request.GET.get('podCd')
        vessel = request.GET.get('vessel')
        voyage = request.GET.get('voyage')

        # 参数验证
        required_params = {
            'carriercd': carriercd,
            'polCd': pol_cd,
            'podCd': pod_cd,
            'vessel': vessel,
            'voyage': voyage
        }

        missing_params = [param for param, value in required_params.items() if not value]
        if missing_params:
            return Response({
                'success': False,
                'message': f'缺少必需参数: {", ".join(missing_params)}',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # 查询VesselInfoFromCompany记录
        try:
            vessel_info = VesselInfoFromCompany.objects.get(
                carriercd=carriercd,
                polCd=pol_cd,
                podCd=pod_cd,
                vessel=vessel,
                voyage=voyage
            )

            serializer = VesselInfoFromCompanySerializer(vessel_info)

            return Response({
                'success': True,
                'message': '查询成功',
                'data': serializer.data
            })

        except VesselInfoFromCompany.DoesNotExist:
            return Response({
                'success': False,
                'message': '未找到匹配的船舶额外信息记录',
                'data': None,
                'query_params': required_params
            }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'查询失败: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vessel_info_bulk_query_api(request):
    """
    VesselInfoFromCompany批量查询API
    支持批量查询多个船舶额外信息记录

    参数：
    - queries: JSON格式的查询条件数组，每个元素包含carriercd, polCd, podCd, vessel, voyage

    示例：
    GET /api/vessel-info/bulk-query/?queries=[
        {"carriercd":"ONE","polCd":"CNSHA","podCd":"USNYC","vessel":"EVER GIVEN","voyage":"2501E"},
        {"carriercd":"MSK","polCd":"CNSHA","podCd":"USNYC","vessel":"EVER GIVEN","voyage":"2501E"}
    ]
    """
    try:
        # 检查权限
        permission_map = get_permission_map()
        if not request.user.is_superuser and not request.user.has_permission(permission_map.get('vessel_info_list')):
            return Response({
                'success': False,
                'message': '没有权限查看船舶额外信息',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        # 获取查询条件
        queries_param = request.GET.get('queries')
        if not queries_param:
            return Response({
                'success': False,
                'message': '缺少必需参数: queries',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # 解析查询条件
        try:
            queries = json.loads(queries_param)
            if not isinstance(queries, list):
                raise ValueError("queries必须是数组格式")
        except (json.JSONDecodeError, ValueError) as e:
            return Response({
                'success': False,
                'message': f'queries参数格式错误: {str(e)}',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # 限制查询数量
        if len(queries) > 100:
            return Response({
                'success': False,
                'message': '一次最多查询100条记录',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # 批量查询
        results = []
        not_found = []

        for i, query in enumerate(queries):
            # 验证单个查询条件
            required_fields = ['carriercd', 'polCd', 'podCd', 'vessel', 'voyage']
            missing_fields = [field for field in required_fields if not query.get(field)]

            if missing_fields:
                results.append({
                    'index': i,
                    'query': query,
                    'success': False,
                    'message': f'缺少必需字段: {", ".join(missing_fields)}',
                    'data': None
                })
                continue

            try:
                vessel_info = VesselInfoFromCompany.objects.get(
                    carriercd=query['carriercd'],
                    polCd=query['polCd'],
                    podCd=query['podCd'],
                    vessel=query['vessel'],
                    voyage=query['voyage']
                )

                serializer = VesselInfoFromCompanySerializer(vessel_info)
                results.append({
                    'index': i,
                    'query': query,
                    'success': True,
                    'message': '查询成功',
                    'data': serializer.data
                })

            except VesselInfoFromCompany.DoesNotExist:
                not_found.append(query)
                results.append({
                    'index': i,
                    'query': query,
                    'success': False,
                    'message': '未找到匹配记录',
                    'data': None
                })

        # 统计结果
        success_count = sum(1 for r in results if r['success'])
        total_count = len(queries)

        return Response({
            'success': True,
            'message': f'批量查询完成: {success_count}/{total_count} 成功',
            'data': {
                'results': results,
                'summary': {
                    'total_queries': total_count,
                    'success_count': success_count,
                    'not_found_count': len(not_found)
                }
            }
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': f'批量查询失败: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def vessel_info_bulk_create_api(request):
    """
    VesselInfoFromCompany批量创建API
    需要vessel_info.create权限
    """
    try:
        # 检查权限
        permission_map = get_permission_map()
        if not request.user.is_superuser and not request.user.has_permission(permission_map.get('vessel_info_create')):
            return Response({
                'success': False,
                'message': '没有权限创建船舶额外信息',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        # 获取批量数据
        bulk_data = request.data.get('data', [])
        if not isinstance(bulk_data, list):
            return Response({
                'success': False,
                'message': 'data字段必须是数组格式',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        if len(bulk_data) > 100:
            return Response({
                'success': False,
                'message': '一次最多创建100条记录',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # 批量创建
        created_records = []
        failed_records = []

        for i, item_data in enumerate(bulk_data):
            try:
                serializer = VesselInfoFromCompanySerializer(data=item_data)
                if serializer.is_valid():
                    vessel_info = serializer.save()
                    created_records.append({
                        'index': i,
                        'success': True,
                        'data': VesselInfoFromCompanySerializer(vessel_info).data
                    })
                else:
                    failed_records.append({
                        'index': i,
                        'success': False,
                        'errors': serializer.errors,
                        'data': item_data
                    })
            except Exception as e:
                failed_records.append({
                    'index': i,
                    'success': False,
                    'errors': str(e),
                    'data': item_data
                })

        return Response({
            'success': True,
            'message': f'批量创建完成: {len(created_records)}/{len(bulk_data)} 成功',
            'data': {
                'created': created_records,
                'failed': failed_records,
                'summary': {
                    'total_requests': len(bulk_data),
                    'success_count': len(created_records),
                    'failed_count': len(failed_records)
                }
            }
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': f'批量创建失败: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def vessel_info_bulk_update_api(request):
    """
    VesselInfoFromCompany批量更新API
    需要vessel_info.update权限
    """
    try:
        # 检查权限
        permission_map = get_permission_map()
        if not request.user.is_superuser and not request.user.has_permission(permission_map.get('vessel_info_update')):
            return Response({
                'success': False,
                'message': '没有权限更新船舶额外信息',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        # 获取批量数据
        bulk_data = request.data.get('data', [])
        if not isinstance(bulk_data, list):
            return Response({
                'success': False,
                'message': 'data字段必须是数组格式',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        if len(bulk_data) > 100:
            return Response({
                'success': False,
                'message': '一次最多更新100条记录',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # 批量更新
        updated_records = []
        failed_records = []

        for i, item_data in enumerate(bulk_data):
            try:
                # 通过关联字段查找记录
                required_fields = ['carriercd', 'polCd', 'podCd', 'vessel', 'voyage']
                missing_fields = [field for field in required_fields if field not in item_data]

                if missing_fields:
                    failed_records.append({
                        'index': i,
                        'success': False,
                        'errors': f'缺少必需字段: {", ".join(missing_fields)}',
                        'data': item_data
                    })
                    continue

                vessel_info = VesselInfoFromCompany.objects.get(
                    carriercd=item_data['carriercd'],
                    polCd=item_data['polCd'],
                    podCd=item_data['podCd'],
                    vessel=item_data['vessel'],
                    voyage=item_data['voyage']
                )

                # 使用序列化器更新
                serializer = VesselInfoFromCompanySerializer(vessel_info, data=item_data, partial=True)
                if serializer.is_valid():
                    updated_vessel_info = serializer.save()
                    updated_records.append({
                        'index': i,
                        'success': True,
                        'data': VesselInfoFromCompanySerializer(updated_vessel_info).data
                    })
                else:
                    failed_records.append({
                        'index': i,
                        'success': False,
                        'errors': serializer.errors,
                        'data': item_data
                    })

            except VesselInfoFromCompany.DoesNotExist:
                failed_records.append({
                    'index': i,
                    'success': False,
                    'errors': '记录不存在',
                    'data': item_data
                })
            except Exception as e:
                failed_records.append({
                    'index': i,
                    'success': False,
                    'errors': str(e),
                    'data': item_data
                })

        return Response({
            'success': True,
            'message': f'批量更新完成: {len(updated_records)}/{len(bulk_data)} 成功',
            'data': {
                'updated': updated_records,
                'failed': failed_records,
                'summary': {
                    'total_requests': len(bulk_data),
                    'success_count': len(updated_records),
                    'failed_count': len(failed_records)
                }
            }
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': f'批量更新失败: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def vessel_info_bulk_delete_api(request):
    """
    VesselInfoFromCompany批量删除API
    需要vessel_info.delete权限
    """
    try:
        # 检查权限
        permission_map = get_permission_map()
        if not request.user.is_superuser and not request.user.has_permission(permission_map.get('vessel_info_delete')):
            return Response({
                'success': False,
                'message': '没有权限删除船舶额外信息',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        # 获取删除条件
        delete_conditions = request.data.get('conditions', [])
        if not isinstance(delete_conditions, list):
            return Response({
                'success': False,
                'message': 'conditions字段必须是数组格式',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        if len(delete_conditions) > 100:
            return Response({
                'success': False,
                'message': '一次最多删除100条记录',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # 批量删除
        deleted_records = []
        failed_records = []

        for i, condition in enumerate(delete_conditions):
            try:
                # 验证删除条件
                required_fields = ['carriercd', 'polCd', 'podCd', 'vessel', 'voyage']
                missing_fields = [field for field in required_fields if field not in condition]

                if missing_fields:
                    failed_records.append({
                        'index': i,
                        'success': False,
                        'errors': f'缺少必需字段: {", ".join(missing_fields)}',
                        'condition': condition
                    })
                    continue

                vessel_info = VesselInfoFromCompany.objects.get(
                    carriercd=condition['carriercd'],
                    polCd=condition['polCd'],
                    podCd=condition['podCd'],
                    vessel=condition['vessel'],
                    voyage=condition['voyage']
                )

                # 保存删除前的数据用于返回
                deleted_data = VesselInfoFromCompanySerializer(vessel_info).data
                vessel_info.delete()

                deleted_records.append({
                    'index': i,
                    'success': True,
                    'data': deleted_data
                })

            except VesselInfoFromCompany.DoesNotExist:
                failed_records.append({
                    'index': i,
                    'success': False,
                    'errors': '记录不存在',
                    'condition': condition
                })
            except Exception as e:
                failed_records.append({
                    'index': i,
                    'success': False,
                    'errors': str(e),
                    'condition': condition
                })

        return Response({
            'success': True,
            'message': f'批量删除完成: {len(deleted_records)}/{len(delete_conditions)} 成功',
            'data': {
                'deleted': deleted_records,
                'failed': failed_records,
                'summary': {
                    'total_requests': len(delete_conditions),
                    'success_count': len(deleted_records),
                    'failed_count': len(failed_records)
                }
            }
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': f'批量删除失败: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cabin_config_detail_api(request):
    """
    获取单个航线的共舱配置详情

    参数：
    - schedule_id: VesselSchedule的ID（可选）
    - polCd: 起运港五字码（必需，如果没有schedule_id）
    - podCd: 目的港五字码（必需，如果没有schedule_id）
    - vessel: 船名（必需，如果没有schedule_id）
    - voyage: 航次（必需，如果没有schedule_id）
    """
    try:
        # 检查权限
        permission_map = get_permission_map()
        if not request.user.is_superuser and not request.user.has_permission(permission_map.get('vessel_schedule_detail', 'schedules.view_vesselschedule')):
            return Response({
                'success': False,
                'message': '没有权限查看共舱配置',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        # 获取航线记录
        schedule_id = request.GET.get('schedule_id')

        if schedule_id:
            try:
                schedule = VesselSchedule.objects.get(id=schedule_id, status=1)
            except VesselSchedule.DoesNotExist:
                return Response({
                    'success': False,
                    'message': f'航线记录不存在: {schedule_id}',
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            # 通过其他字段查找
            pol_cd = request.GET.get('polCd')
            pod_cd = request.GET.get('podCd')
            vessel = request.GET.get('vessel')
            voyage = request.GET.get('voyage')

            if not all([pol_cd, pod_cd, vessel, voyage]):
                return Response({
                    'success': False,
                    'message': '缺少必需参数: schedule_id 或 (polCd, podCd, vessel, voyage)',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                # 获取最新版本的记录
                latest_version = VesselSchedule.objects.aggregate(max_version=Max('data_version'))['max_version']
                schedule = VesselSchedule.objects.get(
                    polCd=pol_cd,
                    podCd=pod_cd,
                    vessel=vessel,
                    voyage=voyage,
                    data_version=latest_version,
                    status=1
                )
            except VesselSchedule.DoesNotExist:
                return Response({
                    'success': False,
                    'message': '航线记录不存在',
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)

        # 解析共舱配置
        share_cabins_config = []
        if schedule.shareCabins:
            try:
                if isinstance(schedule.shareCabins, str):
                    share_cabins_config = json.loads(schedule.shareCabins)
                else:
                    share_cabins_config = schedule.shareCabins
            except (json.JSONDecodeError, TypeError):
                share_cabins_config = []

        return Response({
            'success': True,
            'message': '共舱配置获取成功',
            'data': {
                'schedule_id': schedule.id,
                'schedule_info': {
                    'polCd': schedule.polCd,
                    'podCd': schedule.podCd,
                    'vessel': schedule.vessel,
                    'voyage': schedule.voyage,
                    'carriercd': schedule.carriercd,
                    'routeEtd': schedule.routeEtd,
                    'eta': schedule.eta,
                    'etd': schedule.etd
                },
                'share_cabins_config': share_cabins_config,
                'carrier_count': len(share_cabins_config) if isinstance(share_cabins_config, list) else 0
            }
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取共舱配置失败: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def cabin_config_update_api(request):
    """
    更新航线的共舱配置

    PUT: 完全替换共舱配置
    PATCH: 部分更新共舱配置

    请求体：
    {
        "schedule_id": 123,  // 或者使用 polCd, podCd, vessel, voyage
        "share_cabins_config": [
            {
                "carrierCd": "ONE",
                "price": 4200.00,
                "available": true,
                "remark": "主要承运商"
            },
            {
                "carrierCd": "MSK",
                "price": 4500.00,
                "available": true,
                "remark": "共舱承运商"
            }
        ]
    }
    """
    try:
        # 检查权限
        permission_map = get_permission_map()
        if not request.user.is_superuser and not request.user.has_permission(permission_map.get('vessel_schedule_update', 'schedules.change_vesselschedule')):
            return Response({
                'success': False,
                'message': '没有权限更新共舱配置',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        # 获取航线记录
        schedule_id = request.data.get('schedule_id')

        if schedule_id:
            try:
                schedule = VesselSchedule.objects.get(id=schedule_id, status=1)
            except VesselSchedule.DoesNotExist:
                return Response({
                    'success': False,
                    'message': f'航线记录不存在: {schedule_id}',
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            # 通过其他字段查找
            pol_cd = request.data.get('polCd')
            pod_cd = request.data.get('podCd')
            vessel = request.data.get('vessel')
            voyage = request.data.get('voyage')

            if not all([pol_cd, pod_cd, vessel, voyage]):
                return Response({
                    'success': False,
                    'message': '缺少必需参数: schedule_id 或 (polCd, podCd, vessel, voyage)',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                latest_version = VesselSchedule.objects.aggregate(max_version=Max('data_version'))['max_version']
                schedule = VesselSchedule.objects.get(
                    polCd=pol_cd,
                    podCd=pod_cd,
                    vessel=vessel,
                    voyage=voyage,
                    data_version=latest_version,
                    status=1
                )
            except VesselSchedule.DoesNotExist:
                return Response({
                    'success': False,
                    'message': '航线记录不存在',
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)

        # 获取新的共舱配置
        new_share_cabins_config = request.data.get('share_cabins_config', [])

        # 验证配置格式
        if not isinstance(new_share_cabins_config, list):
            return Response({
                'success': False,
                'message': 'share_cabins_config必须是数组格式',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # 验证每个配置项
        for i, config in enumerate(new_share_cabins_config):
            if not isinstance(config, dict):
                return Response({
                    'success': False,
                    'message': f'配置项{i}必须是对象格式',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)

            if 'carrierCd' not in config:
                return Response({
                    'success': False,
                    'message': f'配置项{i}缺少必需字段: carrierCd',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)

        # 处理PATCH请求（部分更新）
        if request.method == 'PATCH':
            current_config = []
            if schedule.shareCabins:
                try:
                    if isinstance(schedule.shareCabins, str):
                        current_config = json.loads(schedule.shareCabins)
                    else:
                        current_config = schedule.shareCabins
                except (json.JSONDecodeError, TypeError):
                    current_config = []

            # 合并配置：新配置覆盖同carrierCd的旧配置
            current_carriers = {item.get('carrierCd'): item for item in current_config if isinstance(item, dict)}

            for new_item in new_share_cabins_config:
                if isinstance(new_item, dict) and 'carrierCd' in new_item:
                    current_carriers[new_item['carrierCd']] = new_item

            final_config = list(current_carriers.values())
        else:
            # PUT请求：完全替换
            final_config = new_share_cabins_config

        # 更新数据库
        schedule.shareCabins = json.dumps(final_config, ensure_ascii=False)
        schedule.save(update_fields=['shareCabins'])

        return Response({
            'success': True,
            'message': '共舱配置更新成功',
            'data': {
                'schedule_id': schedule.id,
                'schedule_info': {
                    'polCd': schedule.polCd,
                    'podCd': schedule.podCd,
                    'vessel': schedule.vessel,
                    'voyage': schedule.voyage,
                    'carriercd': schedule.carriercd
                },
                'share_cabins_config': final_config,
                'carrier_count': len(final_config),
                'update_method': request.method
            }
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': f'更新共舱配置失败: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cabin_config_delete_api(request):
    """
    删除航线的共舱配置

    请求体：
    {
        "schedule_id": 123,  // 或者使用 polCd, podCd, vessel, voyage
        "carrier_codes": ["ONE", "MSK"]  // 要删除的船公司代码，如果为空则删除全部
    }
    """
    try:
        # 检查权限
        permission_map = get_permission_map()
        if not request.user.is_superuser and not request.user.has_permission(permission_map.get('vessel_schedule_update', 'schedules.change_vesselschedule')):
            return Response({
                'success': False,
                'message': '没有权限删除共舱配置',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        # 获取航线记录
        schedule_id = request.data.get('schedule_id')

        if schedule_id:
            try:
                schedule = VesselSchedule.objects.get(id=schedule_id, status=1)
            except VesselSchedule.DoesNotExist:
                return Response({
                    'success': False,
                    'message': f'航线记录不存在: {schedule_id}',
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            # 通过其他字段查找
            pol_cd = request.data.get('polCd')
            pod_cd = request.data.get('podCd')
            vessel = request.data.get('vessel')
            voyage = request.data.get('voyage')

            if not all([pol_cd, pod_cd, vessel, voyage]):
                return Response({
                    'success': False,
                    'message': '缺少必需参数: schedule_id 或 (polCd, podCd, vessel, voyage)',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                latest_version = VesselSchedule.objects.aggregate(max_version=Max('data_version'))['max_version']
                schedule = VesselSchedule.objects.get(
                    polCd=pol_cd,
                    podCd=pod_cd,
                    vessel=vessel,
                    voyage=voyage,
                    data_version=latest_version,
                    status=1
                )
            except VesselSchedule.DoesNotExist:
                return Response({
                    'success': False,
                    'message': '航线记录不存在',
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)

        # 获取要删除的船公司代码
        carrier_codes_to_delete = request.data.get('carrier_codes', [])

        # 获取当前配置
        current_config = []
        if schedule.shareCabins:
            try:
                if isinstance(schedule.shareCabins, str):
                    current_config = json.loads(schedule.shareCabins)
                else:
                    current_config = schedule.shareCabins
            except (json.JSONDecodeError, TypeError):
                current_config = []

        # 保存删除前的配置
        deleted_items = []

        if not carrier_codes_to_delete:
            # 删除全部配置
            deleted_items = current_config.copy()
            final_config = []
        else:
            # 删除指定的船公司配置
            final_config = []
            for item in current_config:
                if isinstance(item, dict) and item.get('carrierCd') in carrier_codes_to_delete:
                    deleted_items.append(item)
                else:
                    final_config.append(item)

        # 更新数据库
        schedule.shareCabins = json.dumps(final_config, ensure_ascii=False) if final_config else None
        schedule.save(update_fields=['shareCabins'])

        return Response({
            'success': True,
            'message': f'共舱配置删除成功: 删除了{len(deleted_items)}项配置',
            'data': {
                'schedule_id': schedule.id,
                'schedule_info': {
                    'polCd': schedule.polCd,
                    'podCd': schedule.podCd,
                    'vessel': schedule.vessel,
                    'voyage': schedule.voyage,
                    'carriercd': schedule.carriercd
                },
                'deleted_items': deleted_items,
                'remaining_config': final_config,
                'remaining_count': len(final_config)
            }
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': f'删除共舱配置失败: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cabin_config_bulk_update_api(request):
    """
    批量更新多个航线的共舱配置

    请求体：
    {
        "updates": [
            {
                "schedule_id": 123,  // 或者使用 polCd, podCd, vessel, voyage
                "share_cabins_config": [...],
                "update_method": "replace"  // "replace" 或 "merge"
            },
            {
                "polCd": "CNSHA",
                "podCd": "USNYC",
                "vessel": "EVER GIVEN",
                "voyage": "2501E",
                "share_cabins_config": [...],
                "update_method": "merge"
            }
        ]
    }
    """
    try:
        # 检查权限
        permission_map = get_permission_map()
        if not request.user.is_superuser and not request.user.has_permission(permission_map.get('vessel_schedule_update', 'schedules.change_vesselschedule')):
            return Response({
                'success': False,
                'message': '没有权限批量更新共舱配置',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        # 获取批量更新数据
        updates = request.data.get('updates', [])
        if not isinstance(updates, list):
            return Response({
                'success': False,
                'message': 'updates字段必须是数组格式',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        if len(updates) > 100:
            return Response({
                'success': False,
                'message': '一次最多更新100个航线配置',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # 批量更新处理
        updated_records = []
        failed_records = []

        for i, update_item in enumerate(updates):
            try:
                # 获取航线记录
                schedule_id = update_item.get('schedule_id')

                if schedule_id:
                    try:
                        schedule = VesselSchedule.objects.get(id=schedule_id, status=1)
                    except VesselSchedule.DoesNotExist:
                        failed_records.append({
                            'index': i,
                            'success': False,
                            'error': f'航线记录不存在: {schedule_id}',
                            'data': update_item
                        })
                        continue
                else:
                    # 通过其他字段查找
                    pol_cd = update_item.get('polCd')
                    pod_cd = update_item.get('podCd')
                    vessel = update_item.get('vessel')
                    voyage = update_item.get('voyage')

                    if not all([pol_cd, pod_cd, vessel, voyage]):
                        failed_records.append({
                            'index': i,
                            'success': False,
                            'error': '缺少必需参数',
                            'data': update_item
                        })
                        continue

                    try:
                        latest_version = VesselSchedule.objects.aggregate(max_version=Max('data_version'))['max_version']
                        schedule = VesselSchedule.objects.get(
                            polCd=pol_cd,
                            podCd=pod_cd,
                            vessel=vessel,
                            voyage=voyage,
                            data_version=latest_version,
                            status=1
                        )
                    except VesselSchedule.DoesNotExist:
                        failed_records.append({
                            'index': i,
                            'success': False,
                            'error': '航线记录不存在',
                            'data': update_item
                        })
                        continue

                # 获取新配置
                new_config = update_item.get('share_cabins_config', [])
                update_method = update_item.get('update_method', 'replace')

                # 处理更新方式
                if update_method == 'merge':
                    # 合并配置
                    current_config = []
                    if schedule.shareCabins:
                        try:
                            if isinstance(schedule.shareCabins, str):
                                current_config = json.loads(schedule.shareCabins)
                            else:
                                current_config = schedule.shareCabins
                        except (json.JSONDecodeError, TypeError):
                            current_config = []

                    current_carriers = {item.get('carrierCd'): item for item in current_config if isinstance(item, dict)}

                    for new_item in new_config:
                        if isinstance(new_item, dict) and 'carrierCd' in new_item:
                            current_carriers[new_item['carrierCd']] = new_item

                    final_config = list(current_carriers.values())
                else:
                    # 替换配置
                    final_config = new_config

                # 更新数据库
                schedule.shareCabins = json.dumps(final_config, ensure_ascii=False)
                schedule.save(update_fields=['shareCabins'])

                updated_records.append({
                    'index': i,
                    'success': True,
                    'schedule_id': schedule.id,
                    'schedule_info': {
                        'polCd': schedule.polCd,
                        'podCd': schedule.podCd,
                        'vessel': schedule.vessel,
                        'voyage': schedule.voyage
                    },
                    'carrier_count': len(final_config),
                    'update_method': update_method
                })

            except Exception as e:
                failed_records.append({
                    'index': i,
                    'success': False,
                    'error': str(e),
                    'data': update_item
                })

        return Response({
            'success': True,
            'message': f'批量更新完成: {len(updated_records)}/{len(updates)} 成功',
            'data': {
                'updated': updated_records,
                'failed': failed_records,
                'summary': {
                    'total_requests': len(updates),
                    'success_count': len(updated_records),
                    'failed_count': len(failed_records)
                }
            }
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': f'批量更新共舱配置失败: {str(e)}',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cabin_grouping_with_vessel_info_api(request):
    """
    获取共舱分组数据并附带船舶额外信息
    用于前台航期查询页面，按照船公司组合进行分组

    参数：
    - polCd: 起运港五字码（必需）
    - podCd: 目的港五字码（必需）
    """
    try:
        from datetime import datetime, date
        from collections import Counter

        # 获取请求参数
        pol_cd = request.GET.get('polCd')
        pod_cd = request.GET.get('podCd')

        if not pol_cd or not pod_cd:
            return Response({
                'success': False,
                'message': '起运港和目的港不能为空',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # 获取最新版本数据
        latest_version = VesselSchedule.objects.filter(
            polCd=pol_cd,
            podCd=pod_cd,
            status=1
        ).aggregate(max_version=models.Max('data_version'))['max_version']

        if latest_version is None:
            return Response({
                'success': True,
                'message': '没有找到符合条件的航线数据',
                'data': {
                    'version': None,
                    'total_groups': 0,
                    'filter': {'polCd': pol_cd, 'podCd': pod_cd},
                    'groups': []
                }
            })

        # 查询数据
        queryset = VesselSchedule.objects.filter(
            polCd=pol_cd,
            podCd=pod_cd,
            status=1,
            data_version=latest_version
        )

        # 按船公司组合分组
        groups = {}
        group_counter = 1

        for schedule in queryset:
            try:
                share_cabins = json.loads(schedule.shareCabins) if schedule.shareCabins else []
            except:
                share_cabins = []

            # 提取船公司代码
            carrier_codes = []
            for cabin in share_cabins:
                if isinstance(cabin, dict) and 'carrierCd' in cabin:
                    carrier_codes.append(cabin['carrierCd'])

            # 如果没有共舱信息，使用主船公司
            if not carrier_codes:
                carrier_codes = [schedule.carriercd]

            # 生成分组key：按船公司代码排序组合
            group_key = ','.join(sorted(set(carrier_codes)))

            if group_key not in groups:
                groups[group_key] = {
                    'group_id': f'group_{group_counter}',
                    'cabins_count': len(set(carrier_codes)),
                    'carrier_codes': sorted(list(set(carrier_codes))),
                    'schedules': [],
                    'route_etds': [],  # 用于计算plan_open
                    'total_durations': [],  # 用于计算plan_duration
                }
                group_counter += 1

            # 获取每条航线的船舶额外信息
            vessel_info = {}
            try:
                vessel_info_obj = VesselInfoFromCompany.objects.filter(
                    polCd=schedule.polCd,
                    podCd=schedule.podCd,
                    vessel=schedule.vessel,
                    voyage=schedule.voyage,
                    carriercd=schedule.carriercd
                ).first()

                if vessel_info_obj:
                    vessel_info = {
                        'id': vessel_info_obj.id,
                        'gp_20': vessel_info_obj.gp_20 if vessel_info_obj.gp_20 is not None else '--',
                        'hq_40': vessel_info_obj.hq_40 if vessel_info_obj.hq_40 is not None else '--',
                        'price': vessel_info_obj.price if vessel_info_obj.price is not None else '--',
                        'cut_off_time': vessel_info_obj.cut_off_time if vessel_info_obj.cut_off_time is not None else '--'
                    }
            except:
                pass

            # 添加航线到分组
            groups[group_key]['schedules'].append({
                'id': schedule.id,
                'vessel': schedule.vessel,
                'voyage': schedule.voyage,
                'polCd': schedule.polCd,
                'podCd': schedule.podCd,
                'pol': schedule.pol,
                'pod': schedule.pod,
                'eta': schedule.eta,
                'etd': schedule.etd,
                'routeEtd': schedule.routeEtd,
                'carriercd': schedule.carriercd,
                'totalDuration': schedule.totalDuration,
                'shareCabins': share_cabins,
                'vessel_info': vessel_info
            })

            # 收集用于汇总计算的数据
            if schedule.routeEtd is not None:
                groups[group_key]['route_etds'].append(schedule.routeEtd)
            if schedule.totalDuration is not None:
                groups[group_key]['total_durations'].append(schedule.totalDuration)

        # 计算汇总字段
        current_date = date.today()

        for group_key, group_data in groups.items():
            # 组内按routeEtd排序
            group_data['schedules'].sort(key=lambda x: x['routeEtd'] if x['routeEtd'] is not None else 999)

            # 计算plan_open：routeEtd出现次数最多的值
            if group_data['route_etds']:
                route_etd_counter = Counter(group_data['route_etds'])
                most_common_etds = route_etd_counter.most_common()
                # 如果多个相同，选择所有最多的
                max_count = most_common_etds[0][1]
                plan_open_values = [etd for etd, count in most_common_etds if count == max_count]
                # 修改：当有多个最高频率值时，选择最小的值（最早的航线）
                group_data['plan_open'] = min(plan_open_values) if plan_open_values else None
            else:
                group_data['plan_open'] = None

            # 计算plan_duration：totalDuration的最小值
            if group_data['total_durations']:
                group_data['plan_duration'] = min(group_data['total_durations'])
            else:
                group_data['plan_duration'] = None

            # 计算cabin_price：使用最近ETD日期（最早开船）的航线价格
            cabin_price = None
            earliest_etd_schedule = None
            earliest_etd = None

            for schedule in group_data['schedules']:
                if schedule['etd']:
                    try:
                        # 支持两种ETD格式：'%Y-%m-%d %H:%M:%S' 和 '%Y-%m-%d'
                        etd_str = schedule['etd']
                        if ' ' in etd_str:
                            etd_date = datetime.strptime(etd_str, '%Y-%m-%d %H:%M:%S').date()
                        else:
                            etd_date = datetime.strptime(etd_str, '%Y-%m-%d').date()

                        # 找到最早的ETD日期（最近要开船的）
                        if earliest_etd is None or etd_date < earliest_etd:
                            earliest_etd = etd_date
                            earliest_etd_schedule = schedule
                    except:
                        pass

            # 使用最早ETD日期对应的价格
            if earliest_etd_schedule and earliest_etd_schedule['vessel_info'].get('price'):
                cabin_price = earliest_etd_schedule['vessel_info']['price']

            # 如果没有价格数据，显示 '--'
            group_data['cabin_price'] = cabin_price if cabin_price is not None else '--'

            # 计算is_has_gp_20和is_has_hq_40 - 检查字段是否不为空
            has_gp_20 = False
            has_hq_40 = False

            for schedule in group_data['schedules']:
                vessel_info = schedule['vessel_info']

                # 检查gp_20字段是否不为空（不是None、不是空字符串、不是0、不是'--'）
                gp_20_val = vessel_info.get('gp_20')
                if (gp_20_val is not None and
                    str(gp_20_val).strip() != '' and
                    str(gp_20_val).strip() != '0' and
                    str(gp_20_val).strip() != '--'):
                    has_gp_20 = True

                # 检查hq_40字段是否不为空（不是None、不是空字符串、不是0、不是'--'）
                hq_40_val = vessel_info.get('hq_40')
                if (hq_40_val is not None and
                    str(hq_40_val).strip() != '' and
                    str(hq_40_val).strip() != '0' and
                    str(hq_40_val).strip() != '--'):
                    has_hq_40 = True

            group_data['is_has_gp_20'] = '有现舱' if has_gp_20 else '--'
            group_data['is_has_hq_40'] = '有现舱' if has_hq_40 else '--'

            # 清理临时数据
            del group_data['route_etds']
            del group_data['total_durations']

        # 转换为列表并按plan_open排序（周一到周日）
        groups_list = list(groups.values())

        def sort_key(group):
            plan_open = group['plan_open']
            if plan_open is None:
                return (7, 0)  # 没有plan_open的排在最后
            elif isinstance(plan_open, list):
                return (min(plan_open), 0)  # 多个值时取最小的
            else:
                return (plan_open, 0)

        groups_list.sort(key=sort_key)

        return Response({
            'success': True,
            'message': '共舱分组数据获取成功',
            'data': {
                'version': latest_version,
                'total_groups': len(groups_list),
                'filter': {'polCd': pol_cd, 'podCd': pod_cd},
                'groups': groups_list
            }
        })

    except Exception as e:
        import traceback
        error_msg = f"航期查询出错: {str(e)}"
        print(f"API Error: {error_msg}")
        print(traceback.format_exc())
        return Response({
            'success': False,
            'message': error_msg,
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
