"""
本地费用模型
简化版本，只包含必要的字段
"""
from django.db import models


class LocalFee(models.Model):
    """本地费用模型"""
    id = models.AutoField(primary_key=True, verbose_name="ID")
    
    # 核心字段
    polCd = models.CharField(max_length=10, verbose_name="起运港五字码")
    podCd = models.CharField(max_length=10, verbose_name="目的港五字码")
    carriercd = models.CharField(max_length=20, blank=True, null=True, verbose_name="船公司英文名")
    name = models.CharField(max_length=100, verbose_name="费用类型名称")  # 起运港吊头费、保安费等
    unit_name = models.CharField(max_length=50, default="箱型", verbose_name="单位名称")  # 箱型、票等
    
    # 价格字段
    price_20gp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="20GP价格")
    price_40gp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="40GP价格") 
    price_40hq = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="40HQ价格")
    price_per_bill = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="每票价格")
    
    currency = models.CharField(max_length=20, blank=True, null=True, verbose_name="货币")
    
    # 时间字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'local_fee'
        verbose_name = "本地费用"
        verbose_name_plural = "本地费用"
        # 唯一性约束
        unique_together = ['carriercd', 'polCd', 'podCd', 'name']

    def __str__(self):
        return f"{self.carriercd or 'N/A'} [{self.polCd}-{self.podCd}] {self.name}"
