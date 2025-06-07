"""
Django管理命令：同步VesselSchedule到VesselInfoFromCompany
用法：
    python manage.py sync_vessel_info                    # 同步所有记录
    python manage.py sync_vessel_info --force           # 强制更新所有记录  
    python manage.py sync_vessel_info --ids 1,2,3       # 只同步指定ID的记录
    python manage.py sync_vessel_info --dry-run         # 预览模式，不实际执行
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from schedules.signals import manual_sync_vessel_schedules
from schedules.models import VesselSchedule, VesselInfoFromCompany
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '同步VesselSchedule数据到VesselInfoFromCompany表'

    def add_arguments(self, parser):
        parser.add_argument(
            '--ids',
            type=str,
            help='指定要同步的VesselSchedule ID列表，逗号分隔，如: 1,2,3'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制更新已存在的VesselInfoFromCompany记录'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='预览模式，显示将要执行的操作但不实际执行'
        )
        
        parser.add_argument(
            '--chunk-size',
            type=int,
            default=100,
            help='每次处理的记录数量，默认100'
        )

    def handle(self, *args, **options):
        self.stdout.write("🚀 开始同步VesselSchedule到VesselInfoFromCompany")
        
        # 解析ID列表
        vessel_schedule_ids = None
        if options['ids']:
            try:
                vessel_schedule_ids = [int(id.strip()) for id in options['ids'].split(',')]
                self.stdout.write(f"指定同步ID: {vessel_schedule_ids}")
            except ValueError:
                raise CommandError("ID列表格式错误，请使用逗号分隔的数字，如: 1,2,3")
        
        # 预览模式
        if options['dry_run']:
            self.show_preview(vessel_schedule_ids, options['force'])
            return
        
        # 执行同步
        try:
            with transaction.atomic():
                result = manual_sync_vessel_schedules(
                    vessel_schedule_ids=vessel_schedule_ids,
                    force_update=options['force']
                )
                
                self.display_results(result)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ 同步过程中发生错误: {str(e)}")
            )
            raise CommandError(f"同步失败: {str(e)}")

    def show_preview(self, vessel_schedule_ids, force_update):
        """显示预览信息"""
        self.stdout.write(self.style.WARNING("🔍 预览模式 - 不会实际修改数据"))
        
        # 构建查询条件
        queryset = VesselSchedule.objects.filter(status=1)
        if vessel_schedule_ids:
            queryset = queryset.filter(id__in=vessel_schedule_ids)
        
        total_schedules = queryset.count()
        self.stdout.write(f"📊 找到 {total_schedules} 条VesselSchedule记录")
        
        if total_schedules == 0:
            self.stdout.write("⚠️  没有找到符合条件的记录")
            return
        
        # 统计将要创建的记录
        will_create = 0
        will_update = 0
        will_skip = 0
        
        for schedule in queryset[:10]:  # 只预览前10条
            from schedules.signals import extract_carrier_codes_from_share_cabins
            
            carrier_codes = extract_carrier_codes_from_share_cabins(schedule.shareCabins)
            if not carrier_codes and schedule.carriercd:
                carrier_codes = [schedule.carriercd]
            
            if not carrier_codes:
                will_skip += 1
                continue
            
            for carrier_code in carrier_codes:
                exists = VesselInfoFromCompany.objects.filter(
                    carriercd=carrier_code,
                    polCd=schedule.polCd,
                    podCd=schedule.podCd,
                    vessel=schedule.vessel,
                    voyage=schedule.voyage
                ).exists()
                
                if exists:
                    if force_update:
                        will_update += 1
                    else:
                        will_skip += 1
                else:
                    will_create += 1
        
        self.stdout.write(f"📈 预计操作 (仅基于前10条记录):")
        self.stdout.write(f"  ✅ 将创建: {will_create} 条记录")
        self.stdout.write(f"  🔄 将更新: {will_update} 条记录")
        self.stdout.write(f"  ⏭️  将跳过: {will_skip} 条记录")
        
        # 显示样例
        if queryset.exists():
            sample = queryset.first()
            from schedules.signals import extract_carrier_codes_from_share_cabins
            carrier_codes = extract_carrier_codes_from_share_cabins(sample.shareCabins)
            
            self.stdout.write(f"\n📋 样例记录:")
            self.stdout.write(f"  VesselSchedule ID: {sample.id}")
            self.stdout.write(f"  船名航次: {sample.vessel} {sample.voyage}")
            self.stdout.write(f"  航线: {sample.polCd} → {sample.podCd}")
            self.stdout.write(f"  共舱船公司: {carrier_codes}")

    def display_results(self, result):
        """显示同步结果"""
        self.stdout.write(self.style.SUCCESS("🎉 同步完成!"))
        self.stdout.write(f"📊 同步统计:")
        self.stdout.write(f"  📝 处理记录: {result['total_processed']}")
        self.stdout.write(f"  ✅ 创建记录: {result['created']}")
        self.stdout.write(f"  🔄 更新记录: {result['updated']}")
        self.stdout.write(f"  ⏭️  跳过记录: {result['skipped']}")
        
        if result['errors'] > 0:
            self.stdout.write(f"  ❌ 错误记录: {result['errors']}")
        
        # 显示当前总数
        total_vessel_info = VesselInfoFromCompany.objects.count()
        self.stdout.write(f"\n📈 当前VesselInfoFromCompany总记录数: {total_vessel_info}") 