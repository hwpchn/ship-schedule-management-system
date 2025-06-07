"""
本地费用管理后台配置
简化版本
"""
from django.contrib import admin
from .models import LocalFee


@admin.register(LocalFee)
class LocalFeeAdmin(admin.ModelAdmin):
    """本地费用管理"""
    list_display = [
        'id', 'polCd', 'podCd', 'carriercd', 'name', 'unit_name',
        'price_20gp', 'price_40gp', 'price_40hq', 'price_per_bill',
        'currency', 'created_at'
    ]
    list_filter = ['polCd', 'podCd', 'carriercd', 'currency', 'created_at']
    search_fields = ['polCd', 'podCd', 'carriercd', 'name']
    ordering = ['id']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('polCd', 'podCd', 'carriercd', 'name', 'unit_name')
        }),
        ('价格信息', {
            'fields': ('price_20gp', 'price_40gp', 'price_40hq', 'price_per_bill', 'currency')
        }),
    )
