"""
船舶航线业务逻辑服务层
将复杂的业务逻辑从视图中分离出来
"""
import json
import logging
from typing import List, Dict, Optional, Tuple
from django.db import transaction
from django.db.models import Q, Prefetch, Count, Max
from django.core.cache import cache
from django.conf import settings

from .models import VesselSchedule, VesselInfoFromCompany
from ship_schedule.utils import CacheHelper, ValidationHelper

logger = logging.getLogger(__name__)


class VesselScheduleService:
    """
    船舶航线服务类
    处理航线相关的业务逻辑
    """
    
    @staticmethod
    def get_vessel_schedules(pol_cd: str = None, pod_cd: str = None, 
                           carrier_cd: str = None, status: int = 1,
                           data_version: int = None) -> List[VesselSchedule]:
        """
        获取船舶航线列表
        
        Args:
            pol_cd: 起运港代码
            pod_cd: 目的港代码
            carrier_cd: 船公司代码
            status: 数据状态
            data_version: 数据版本
            
        Returns:
            List[VesselSchedule]: 航线列表
        """
        queryset = VesselSchedule.objects.select_related().filter(status=status)
        
        # 如果没有指定版本，使用最新版本
        if data_version is None:
            latest_version = VesselSchedule.objects.aggregate(
                max_version=Max('data_version')
            )['max_version']
            if latest_version:
                queryset = queryset.filter(data_version=latest_version)
        else:
            queryset = queryset.filter(data_version=data_version)
        
        # 应用过滤条件
        if pol_cd:
            queryset = queryset.filter(polCd=pol_cd)
        if pod_cd:
            queryset = queryset.filter(podCd=pod_cd)
        if carrier_cd:
            queryset = queryset.filter(carriercd=carrier_cd)
        
        return queryset.order_by('-fetch_date', 'vessel', 'voyage')
    
    @staticmethod
    def get_cabin_grouping_data(pol_cd: str, pod_cd: str, 
                              data_version: int = None) -> Dict:
        """
        获取舱位分组数据
        
        Args:
            pol_cd: 起运港代码
            pod_cd: 目的港代码
            data_version: 数据版本
            
        Returns:
            Dict: 分组后的舱位数据
        """
        # 构建缓存键
        cache_key = f"cabin_grouping:{pol_cd}:{pod_cd}:{data_version or 'latest'}"
        
        def _get_data():
            # 获取基础航线数据
            schedules = VesselScheduleService.get_vessel_schedules(
                pol_cd=pol_cd, 
                pod_cd=pod_cd, 
                data_version=data_version
            )
            
            if not schedules:
                return {'groups': [], 'total': 0}
            
            # 批量获取船舶信息
            vessel_info_map = VesselScheduleService._get_vessel_info_map(schedules)
            
            # 分组处理
            groups = []
            for schedule in schedules:
                # 获取共舱信息
                share_cabins = VesselScheduleService._parse_share_cabins(
                    schedule.shareCabins
                )
                
                # 获取价格信息
                vessel_info = vessel_info_map.get(
                    (schedule.carriercd, schedule.polCd, schedule.podCd, 
                     schedule.vessel, schedule.voyage)
                )
                
                group_data = {
                    'id': schedule.id,
                    'vessel': schedule.vessel,
                    'voyage': schedule.voyage,
                    'carrier': schedule.carriercd,
                    'eta': schedule.eta,
                    'etd': schedule.etd,
                    'route': schedule.routeCd,
                    'total_duration': schedule.totalDuration,
                    'share_cabins': share_cabins,
                    'price_info': {
                        'gp_20': vessel_info.gp_20 if vessel_info else None,
                        'hq_40': vessel_info.hq_40 if vessel_info else None,
                        'price': float(vessel_info.price) if vessel_info and vessel_info.price else None,
                        'cut_off_time': vessel_info.cut_off_time if vessel_info else None,
                    }
                }
                groups.append(group_data)
            
            return {
                'groups': groups,
                'total': len(groups),
                'pol_cd': pol_cd,
                'pod_cd': pod_cd,
                'data_version': data_version
            }
        
        return CacheHelper.get_or_set(cache_key, _get_data, timeout=300)
    
    @staticmethod
    def _get_vessel_info_map(schedules: List[VesselSchedule]) -> Dict:
        """
        批量获取船舶信息映射
        
        Args:
            schedules: 航线列表
            
        Returns:
            Dict: 船舶信息映射 {(carrier, pol, pod, vessel, voyage): VesselInfo}
        """
        if not schedules:
            return {}
        
        # 构建查询条件
        q_objects = Q()
        for schedule in schedules:
            q_objects |= Q(
                carrierCd=schedule.carriercd,
                polCd=schedule.polCd,
                podCd=schedule.podCd,
                vessel=schedule.vessel,
                voyage=schedule.voyage
            )
        
        # 批量查询
        vessel_infos = VesselInfoFromCompany.objects.filter(q_objects)
        
        # 构建映射
        vessel_info_map = {}
        for info in vessel_infos:
            key = (info.carrierCd, info.polCd, info.podCd, info.vessel, info.voyage)
            vessel_info_map[key] = info
        
        return vessel_info_map
    
    @staticmethod
    def _parse_share_cabins(share_cabins_str: str) -> List[Dict]:
        """
        解析共舱信息
        
        Args:
            share_cabins_str: 共舱JSON字符串
            
        Returns:
            List[Dict]: 解析后的共舱信息
        """
        if not share_cabins_str:
            return []
        
        try:
            return json.loads(share_cabins_str)
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"解析共舱信息失败: {e}")
            return []
    
    @staticmethod
    def bulk_create_vessel_schedules(schedules_data: List[Dict]) -> Tuple[bool, str, Dict]:
        """
        批量创建船舶航线
        
        Args:
            schedules_data: 航线数据列表
            
        Returns:
            Tuple[bool, str, Dict]: (是否成功, 消息, 结果数据)
        """
        try:
            with transaction.atomic():
                created_schedules = []
                errors = []
                
                for i, data in enumerate(schedules_data):
                    # 数据验证
                    validation_result = VesselScheduleService._validate_schedule_data(data)
                    if not validation_result[0]:
                        errors.append({
                            'index': i,
                            'error': validation_result[1]
                        })
                        continue
                    
                    # 检查重复
                    existing = VesselSchedule.objects.filter(
                        polCd=data['polCd'],
                        podCd=data['podCd'],
                        vessel=data['vessel'],
                        voyage=data['voyage'],
                        data_version=data['data_version']
                    ).first()
                    
                    if existing:
                        errors.append({
                            'index': i,
                            'error': '该航线已存在'
                        })
                        continue
                    
                    # 创建记录
                    schedule = VesselSchedule.objects.create(**data)
                    created_schedules.append(schedule)
                
                if errors and not created_schedules:
                    return False, "所有数据验证失败", {'errors': errors}
                
                # 清除相关缓存
                VesselScheduleService._clear_schedule_cache()
                
                result = {
                    'created_count': len(created_schedules),
                    'error_count': len(errors),
                    'errors': errors if errors else None
                }
                
                message = f"批量创建完成，成功: {len(created_schedules)}，失败: {len(errors)}"
                return True, message, result
                
        except Exception as e:
            logger.error(f"批量创建船舶航线失败: {e}")
            return False, f"批量创建失败: {str(e)}", {}
    
    @staticmethod
    def _validate_schedule_data(data: Dict) -> Tuple[bool, str]:
        """
        验证航线数据
        
        Args:
            data: 航线数据
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误消息)
        """
        required_fields = ['polCd', 'podCd', 'vessel', 'voyage', 'data_version']
        
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"字段 {field} 是必需的"
        
        # 验证港口代码
        if not ValidationHelper.validate_port_code(data['polCd']):
            return False, "起运港代码格式无效"
        
        if not ValidationHelper.validate_port_code(data['podCd']):
            return False, "目的港代码格式无效"
        
        # 验证船舶信息
        vessel_validation = ValidationHelper.validate_vessel_info(
            data['vessel'], data['voyage']
        )
        if not vessel_validation[0]:
            return False, vessel_validation[1]
        
        return True, ""
    
    @staticmethod
    def _clear_schedule_cache():
        """
        清除航线相关缓存
        """
        try:
            CacheHelper.delete_pattern("cabin_grouping:*")
            CacheHelper.delete_pattern("api:VesselSchedule*")
        except Exception as e:
            logger.warning(f"清除缓存失败: {e}")


class VesselInfoService:
    """
    船舶信息服务类
    处理船舶价格和舱位信息的业务逻辑
    """
    
    @staticmethod
    def get_vessel_info(carrier_cd: str = None, pol_cd: str = None, 
                       pod_cd: str = None, vessel: str = None,
                       voyage: str = None) -> List[VesselInfoFromCompany]:
        """
        获取船舶信息列表
        
        Args:
            carrier_cd: 船公司代码
            pol_cd: 起运港代码
            pod_cd: 目的港代码
            vessel: 船名
            voyage: 航次
            
        Returns:
            List[VesselInfoFromCompany]: 船舶信息列表
        """
        queryset = VesselInfoFromCompany.objects.all()
        
        if carrier_cd:
            queryset = queryset.filter(carrierCd=carrier_cd)
        if pol_cd:
            queryset = queryset.filter(polCd=pol_cd)
        if pod_cd:
            queryset = queryset.filter(podCd=pod_cd)
        if vessel:
            queryset = queryset.filter(vessel__icontains=vessel)
        if voyage:
            queryset = queryset.filter(voyage__icontains=voyage)
        
        return queryset.order_by('carrierCd', 'vessel', 'voyage')
    
    @staticmethod
    def bulk_update_vessel_info(info_data: List[Dict]) -> Tuple[bool, str, Dict]:
        """
        批量更新船舶信息
        
        Args:
            info_data: 船舶信息数据列表
            
        Returns:
            Tuple[bool, str, Dict]: (是否成功, 消息, 结果数据)
        """
        try:
            with transaction.atomic():
                updated_count = 0
                created_count = 0
                errors = []
                
                for i, data in enumerate(info_data):
                    try:
                        # 查找或创建记录
                        vessel_info, created = VesselInfoFromCompany.objects.update_or_create(
                            carrierCd=data['carrierCd'],
                            polCd=data['polCd'],
                            podCd=data['podCd'],
                            vessel=data['vessel'],
                            voyage=data['voyage'],
                            defaults={
                                'gp_20': data.get('gp_20'),
                                'hq_40': data.get('hq_40'),
                                'cut_off_time': data.get('cut_off_time'),
                                'price': data.get('price'),
                            }
                        )
                        
                        if created:
                            created_count += 1
                        else:
                            updated_count += 1
                            
                    except Exception as e:
                        errors.append({
                            'index': i,
                            'error': str(e)
                        })
                
                # 清除相关缓存
                VesselScheduleService._clear_schedule_cache()
                
                result = {
                    'updated_count': updated_count,
                    'created_count': created_count,
                    'error_count': len(errors),
                    'errors': errors if errors else None
                }
                
                message = f"批量操作完成，更新: {updated_count}，创建: {created_count}，错误: {len(errors)}"
                return True, message, result
                
        except Exception as e:
            logger.error(f"批量更新船舶信息失败: {e}")
            return False, f"批量更新失败: {str(e)}", {}


# 导出服务类
__all__ = [
    'VesselScheduleService',
    'VesselInfoService'
]