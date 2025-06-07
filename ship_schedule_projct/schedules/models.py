from django.db import models

# Create your models here.

class VesselSchedule(models.Model):
    """
    船舶航线数据模型
    基于README.md中的字段设计
    实现了数据版本控制和历史记录
    """
    # 自增主键
    id = models.AutoField(primary_key=True, verbose_name="ID")
    
    # 核心字段（组合主键的组成部分）
    polCd = models.CharField(max_length=10, verbose_name="起运港五字码")
    podCd = models.CharField(max_length=10, verbose_name="目的港五字码")
    vessel = models.CharField(max_length=100, verbose_name="船名")
    voyage = models.CharField(max_length=50, verbose_name="航次")
    data_version = models.IntegerField(verbose_name="数据版本号")
    
    # 时间与版本控制字段
    fetch_timestamp = models.BigIntegerField(verbose_name="数据抓取的Unix时间戳")
    fetch_date = models.DateTimeField(verbose_name="格式化的日期时间")
    status = models.SmallIntegerField(default=1, verbose_name="数据状态：1-有效，0-无效")
    
    # 航线基本信息
    routeCd = models.CharField(max_length=50, blank=True, null=True, verbose_name="航线服务名称")
    routeEtd = models.CharField(max_length=20, blank=True, null=True, verbose_name="计划离港班期")
    carriercd = models.CharField(max_length=20, blank=True, null=True, verbose_name="船公司英文名")
    isReferenceCarrier = models.CharField(max_length=5, blank=True, null=True, verbose_name="是否主船东")
    imo = models.CharField(max_length=20, blank=True, null=True, verbose_name="国际海事组织号码")
    shipAgency = models.CharField(max_length=100, blank=True, null=True, verbose_name="船代")
    
    # 港口信息
    pol = models.CharField(max_length=100, blank=True, null=True, verbose_name="起运港英文名")
    polTerminal = models.CharField(max_length=100, blank=True, null=True, verbose_name="起运港码头")
    polTerminalCd = models.CharField(max_length=20, blank=True, null=True, verbose_name="起运港码头代码")
    pod = models.CharField(max_length=100, blank=True, null=True, verbose_name="目的港英文名")
    podTerminal = models.CharField(max_length=100, blank=True, null=True, verbose_name="目的港码头")
    podTerminalCd = models.CharField(max_length=20, blank=True, null=True, verbose_name="目的港码头代码")
    
    # 航运时间相关
    eta = models.CharField(max_length=30, blank=True, null=True, verbose_name="计划到港日期")
    etd = models.CharField(max_length=30, blank=True, null=True, verbose_name="计划离港日期")
    totalDuration = models.CharField(max_length=10, blank=True, null=True, verbose_name="预计航程")
    bookingCutoff = models.CharField(max_length=30, blank=True, null=True, verbose_name="截订舱时间")
    cyOpen = models.CharField(max_length=30, blank=True, null=True, verbose_name="进港时间")
    cyClose = models.CharField(max_length=30, blank=True, null=True, verbose_name="截港时间")
    customCutoff = models.CharField(max_length=30, blank=True, null=True, verbose_name="截放行")
    cutOff = models.CharField(max_length=30, blank=True, null=True, verbose_name="截申报")
    siCutoff = models.CharField(max_length=30, blank=True, null=True, verbose_name="截单时间")
    vgmCutoff = models.CharField(max_length=30, blank=True, null=True, verbose_name="截VGM时间")
    
    # 中转相关信息
    isTransit = models.CharField(max_length=5, blank=True, null=True, verbose_name="是否中转")
    transitPortEn = models.CharField(max_length=100, blank=True, null=True, verbose_name="中转1港口名")
    transitPortCd = models.CharField(max_length=10, blank=True, null=True, verbose_name="中转1港口代码")
    vesselAfterTransit = models.CharField(max_length=100, blank=True, null=True, verbose_name="中转1船名")
    voyageAfterTransit = models.CharField(max_length=50, blank=True, null=True, verbose_name="中转1航次")
    secondTransitPortEn = models.CharField(max_length=100, blank=True, null=True, verbose_name="中转2港口名")
    secondTransitPortCd = models.CharField(max_length=10, blank=True, null=True, verbose_name="中转2港口代码")
    secondVesselAfterTransit = models.CharField(max_length=100, blank=True, null=True, verbose_name="中转2船名")
    secondVoyageAfterTransit = models.CharField(max_length=50, blank=True, null=True, verbose_name="中转2航次")
    
    # 其他与扩展字段
    shareCabins = models.TextField(blank=True, null=True, verbose_name="共舱结果集")
    remark = models.TextField(blank=True, null=True, verbose_name="备注信息")
    ext_field1 = models.CharField(max_length=255, blank=True, null=True, verbose_name="扩展字段1")
    ext_field2 = models.CharField(max_length=255, blank=True, null=True, verbose_name="扩展字段2")
    ext_field3 = models.TextField(blank=True, null=True, verbose_name="扩展字段3")
    
    class Meta:
        """元数据类"""
        db_table = 'vessel_schedule'  # 数据库表名
        verbose_name = '船舶航线'
        verbose_name_plural = '船舶航线'
        # 组合唯一约束，确保在同一版本中不会有重复的航线
        unique_together = ('polCd', 'podCd', 'vessel', 'voyage', 'data_version')
        # 数据库索引优化 - 暂时注释以解决启动问题
        # indexes = [
        #     models.Index(fields=['polCd', 'podCd', 'status'], name='idx_vs_pol_pod_status'),
        #     models.Index(fields=['carriercd', 'status'], name='idx_vs_carrier_status'),
        #     models.Index(fields=['vessel', 'voyage'], name='idx_vs_vessel_voyage'),
        #     models.Index(fields=['data_version', 'status'], name='idx_vs_version_status'),
        #     models.Index(fields=['-fetch_date'], name='idx_vs_fetch_date_desc'),
        #     models.Index(fields=['polCd', 'podCd', 'carriercd', 'status', 'data_version'], name='idx_vs_route_lookup'),
        # ]
        
    def __str__(self):
        """字符串表示"""
        return f"{self.vessel} {self.voyage}: {self.pol}({self.polCd}) → {self.pod}({self.podCd})"


class VesselInfoFromCompany(models.Model):
    """
    船舶价格和舱位,截关时间补充信息
    与VesselSchedule表关联，通过polCd, podCd, vessel, voyage,carrierCd五个字段关联
    """
    # 关联字段
    carrierCd = models.CharField(max_length=10, verbose_name="船公司")  # 对应VesselSchedule的carriercd
    polCd = models.CharField(max_length=10, verbose_name="起运港五字码")
    podCd = models.CharField(max_length=10, verbose_name="目的港五字码")
    vessel = models.CharField(max_length=100, verbose_name="船名")
    voyage = models.CharField(max_length=50, verbose_name="航次")
    
    # 补充字段
    gp_20 = models.CharField(max_length=50, blank=True, null=True, verbose_name="20尺普通箱")
    hq_40 = models.CharField(max_length=50, blank=True, null=True, verbose_name="40尺高箱")
    cut_off_time = models.CharField(max_length=50, blank=True, null=True, verbose_name="截关时间")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="价格")
    
    class Meta:
        """元数据类"""
        db_table = 'vessel_info_from_company'  # 数据库表名
        verbose_name = '船舶额外信息'
        verbose_name_plural = '船舶额外信息'
        # 组合唯一约束
        unique_together = ('carrierCd', 'polCd', 'podCd', 'vessel', 'voyage')
        # 数据库索引优化 - 暂时注释以解决启动问题
        # indexes = [
        #     models.Index(fields=['carrierCd', 'polCd', 'podCd'], name='idx_vi_carrier_pol_pod'),
        #     models.Index(fields=['vessel', 'voyage'], name='idx_vi_vessel_voyage'),
        #     models.Index(fields=['price'], name='idx_vi_price'),
        # ]
        
    def __str__(self):
        """字符串表示"""
        return f"{self.vessel} {self.voyage}: {self.carrierCd} {self.polCd} → {self.podCd}, ¥{self.price if self.price else '--'}"

