"""
VesselSchedule数据同步信号处理器
实现VesselSchedule到VesselInfoFromCompany的实时同步
"""
import json
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import VesselSchedule, VesselInfoFromCompany

# 配置日志
logger = logging.getLogger(__name__)


@receiver(post_save, sender=VesselSchedule)
def sync_vessel_schedule_to_info(sender, instance, created, **kwargs):
    """
    VesselSchedule创建或更新时，同步到VesselInfoFromCompany
    
    同步逻辑：
    1. 解析shareCabins字段，提取所有船公司代码
    2. 为每个船公司创建或更新VesselInfoFromCompany记录
    3. 关联字段从VesselSchedule同步，补充字段保持原值或设为空
    """
    try:
        # 只同步有效的数据
        if instance.status != 1:
            logger.info(f"跳过同步：VesselSchedule {instance.id} 状态为无效")
            return
        
        # 解析shareCabins字段
        carrier_codes = extract_carrier_codes_from_share_cabins(instance.shareCabins)
        
        if not carrier_codes:
            # 如果没有共舱信息，使用VesselSchedule的船公司代码
            if instance.carriercd:
                carrier_codes = [instance.carriercd]
            else:
                logger.warning(f"VesselSchedule {instance.id} 没有有效的船公司信息")
                return
        
        # 为每个船公司创建或更新VesselInfoFromCompany记录
        created_count = 0
        updated_count = 0
        
        for carrier_code in carrier_codes:
            vessel_info, created = VesselInfoFromCompany.objects.get_or_create(
                carriercd=carrier_code,
                polCd=instance.polCd,
                podCd=instance.podCd,
                vessel=instance.vessel,
                voyage=instance.voyage,
                defaults={
                    # 补充字段默认为空，允许后续手动填写
                    'gp_20': None,
                    'hq_40': None,
                    'cut_off_time': None,
                    'price': None,
                }
            )
            
            if created:
                created_count += 1
                logger.info(f"创建VesselInfoFromCompany: {carrier_code} - {instance.vessel} {instance.voyage}")
            else:
                # 更新关联字段，但保留已填写的补充字段
                # 只有当关联字段发生变化时才更新
                needs_update = False
                if vessel_info.polCd != instance.polCd:
                    vessel_info.polCd = instance.polCd
                    needs_update = True
                if vessel_info.podCd != instance.podCd:
                    vessel_info.podCd = instance.podCd
                    needs_update = True
                if vessel_info.vessel != instance.vessel:
                    vessel_info.vessel = instance.vessel
                    needs_update = True
                if vessel_info.voyage != instance.voyage:
                    vessel_info.voyage = instance.voyage
                    needs_update = True
                
                if needs_update:
                    vessel_info.save()
                    updated_count += 1
                    logger.info(f"更新VesselInfoFromCompany: {carrier_code} - {instance.vessel} {instance.voyage}")
        
        if created_count > 0 or updated_count > 0:
            logger.info(f"同步完成：VesselSchedule {instance.id} -> 创建{created_count}条，更新{updated_count}条VesselInfoFromCompany记录")
    
    except Exception as e:
        logger.error(f"同步VesselSchedule {instance.id} 到VesselInfoFromCompany失败: {str(e)}")


@receiver(post_delete, sender=VesselSchedule)
def cleanup_vessel_info_on_schedule_delete(sender, instance, **kwargs):
    """
    VesselSchedule删除时，清理相关的VesselInfoFromCompany记录
    
    注意：只清理没有填写补充信息的记录，避免删除有价值的数据
    """
    try:
        # 解析shareCabins字段
        carrier_codes = extract_carrier_codes_from_share_cabins(instance.shareCabins)
        
        if not carrier_codes and instance.carriercd:
            carrier_codes = [instance.carriercd]
        
        if not carrier_codes:
            return
        
        # 清理没有补充信息的VesselInfoFromCompany记录
        deleted_count = 0
        for carrier_code in carrier_codes:
            try:
                vessel_info = VesselInfoFromCompany.objects.get(
                    carriercd=carrier_code,
                    polCd=instance.polCd,
                    podCd=instance.podCd,
                    vessel=instance.vessel,
                    voyage=instance.voyage
                )
                
                # 只删除没有填写补充信息的记录
                if (not vessel_info.gp_20 and 
                    not vessel_info.hq_40 and 
                    not vessel_info.cut_off_time and 
                    not vessel_info.price):
                    vessel_info.delete()
                    deleted_count += 1
                    logger.info(f"删除空的VesselInfoFromCompany: {carrier_code} - {instance.vessel} {instance.voyage}")
                else:
                    logger.info(f"保留有补充信息的VesselInfoFromCompany: {carrier_code} - {instance.vessel} {instance.voyage}")
            
            except VesselInfoFromCompany.DoesNotExist:
                # 记录不存在，跳过
                pass
        
        if deleted_count > 0:
            logger.info(f"清理完成：删除{deleted_count}条空的VesselInfoFromCompany记录")
    
    except Exception as e:
        logger.error(f"清理VesselSchedule {instance.id} 相关VesselInfoFromCompany记录失败: {str(e)}")


def extract_carrier_codes_from_share_cabins(share_cabins_field):
    """
    从shareCabins字段中提取船公司代码列表
    
    Args:
        share_cabins_field: VesselSchedule的shareCabins字段值
        
    Returns:
        list: 船公司代码列表，去重后排序
    """
    carrier_codes = []
    
    if not share_cabins_field:
        return carrier_codes
    
    try:
        # 解析JSON字符串
        if isinstance(share_cabins_field, str):
            share_cabins_data = json.loads(share_cabins_field)
        else:
            share_cabins_data = share_cabins_field
        
        # 提取carrierCd字段
        if isinstance(share_cabins_data, list):
            for cabin in share_cabins_data:
                if isinstance(cabin, dict) and 'carrierCd' in cabin:
                    carrier_code = cabin['carrierCd']
                    if carrier_code and carrier_code not in carrier_codes:
                        carrier_codes.append(carrier_code)
                elif isinstance(cabin, str):
                    # 兼容简单字符串格式
                    if cabin not in carrier_codes:
                        carrier_codes.append(cabin)
    
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"解析shareCabins字段失败: {e}")
        return []
    
    # 去重并排序
    return sorted(list(set(carrier_codes)))


def manual_sync_vessel_schedules(vessel_schedule_ids=None, force_update=False):
    """
    手动同步VesselSchedule到VesselInfoFromCompany
    
    Args:
        vessel_schedule_ids: 指定要同步的VesselSchedule ID列表，None表示同步所有
        force_update: 是否强制更新已存在的记录
        
    Returns:
        dict: 同步结果统计
    """
    logger.info("开始手动同步VesselSchedule到VesselInfoFromCompany")
    
    # 构建查询条件
    queryset = VesselSchedule.objects.filter(status=1)
    if vessel_schedule_ids:
        queryset = queryset.filter(id__in=vessel_schedule_ids)
    
    total_count = queryset.count()
    created_count = 0
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    logger.info(f"找到{total_count}条VesselSchedule记录需要同步")
    
    for i, schedule in enumerate(queryset, 1):
        try:
            if i % 100 == 0:
                logger.info(f"同步进度: {i}/{total_count}")
            
            # 解析船公司代码
            carrier_codes = extract_carrier_codes_from_share_cabins(schedule.shareCabins)
            if not carrier_codes and schedule.carriercd:
                carrier_codes = [schedule.carriercd]
            
            if not carrier_codes:
                skipped_count += 1
                continue
            
            # 为每个船公司创建或更新记录
            for carrier_code in carrier_codes:
                try:
                    vessel_info, created = VesselInfoFromCompany.objects.get_or_create(
                        carriercd=carrier_code,
                        polCd=schedule.polCd,
                        podCd=schedule.podCd,
                        vessel=schedule.vessel,
                        voyage=schedule.voyage,
                        defaults={
                            'gp_20': None,
                            'hq_40': None,
                            'cut_off_time': None,
                            'price': None,
                        }
                    )
                    
                    if created:
                        created_count += 1
                    elif force_update:
                        # 强制更新关联字段
                        vessel_info.polCd = schedule.polCd
                        vessel_info.podCd = schedule.podCd
                        vessel_info.vessel = schedule.vessel
                        vessel_info.voyage = schedule.voyage
                        vessel_info.save()
                        updated_count += 1
                
                except Exception as e:
                    logger.error(f"处理船公司{carrier_code}记录失败: {e}")
                    error_count += 1
        
        except Exception as e:
            logger.error(f"处理VesselSchedule {schedule.id} 失败: {e}")
            error_count += 1
    
    result = {
        'total_processed': total_count,
        'created': created_count,
        'updated': updated_count,
        'skipped': skipped_count,
        'errors': error_count
    }
    
    logger.info(f"手动同步完成: {result}")
    return result 