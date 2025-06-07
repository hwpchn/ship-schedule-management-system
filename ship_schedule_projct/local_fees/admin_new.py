"""
本地费用Django Admin配置
提供完整的后台管理界面，包含权限控制
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Currency, FeeType, LocalFeeRate, Unit, Ship, ShipFee
from .permissions import LocalFeesAdminPermission


class LocalFeesAdminMixin(LocalFeesAdminPermission):
    """本地费用Admin权限混合类"""
    pass


@admin.register(Currency)
class CurrencyAdmin(LocalFeesAdminMixin, admin.ModelAdmin):
    """货币管理"""
    list_display = ['code', 'name', 'symbol']
    list_filter = ['code']
    search_fields = ['code', 'name']
    ordering = ['code']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('code', 'name', 'symbol')
        }),
    )


@admin.register(FeeType)
class FeeTypeAdmin(LocalFeesAdminMixin, admin.ModelAdmin):
    """费用类型管理"""
    list_display = ['name', 'description', 'is_active', 'created_at', 'rate_count']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description')
        }),
        ('状态', {
            'fields': ('is_active',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def rate_count(self, obj):
        """显示关联的费率数量"""
        count = obj.localfeerate_set.count()
        if count > 0:
            url = reverse('admin:local_fees_localfeerate_changelist')
            return format_html(
                '<a href="{}?fee_type__id={}">{} 个费率</a>',
                url, obj.id, count
            )
        return '无费率'
    rate_count.short_description = '关联费率'


@admin.register(LocalFeeRate)
class LocalFeeRateAdmin(LocalFeesAdminMixin, admin.ModelAdmin):
    """本地费用费率管理"""
    list_display = [
        'fee_type', 'unit_name', 'price_summary', 'currency', 
        'port_code', 'route_code', 'is_active', 'updated_at'
    ]
    list_filter = ['currency', 'is_active', 'unit_name', 'fee_type', 'port_code']
    search_fields = ['fee_type__name', 'port_code', 'route_code', 'remarks']
    ordering = ['fee_type__name', 'port_code']
    
    fieldsets = (
        ('费用信息', {
            'fields': ('fee_type', 'unit_name')
        }),
        ('价格设置', {
            'fields': (
                ('price_20gp', 'price_40gp', 'price_40hq'), 
                'price_per_bill', 
                'currency'
            )
        }),
        ('适用范围', {
            'fields': ('port_code', 'route_code'),
            'description': '如果不填写，则适用于所有港口和航线'
        }),
        ('其他', {
            'fields': ('is_active', 'remarks')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def price_summary(self, obj):
        """价格摘要"""
        return obj.get_price_summary()
    price_summary.short_description = '价格摘要'
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related('fee_type', 'currency')


# 为了兼容现有数据，也注册旧模型但标记为只读
@admin.register(Unit)
class UnitAdmin(LocalFeesAdminMixin, admin.ModelAdmin):
    """单位管理（已弃用）"""
    list_display = ['code', 'name', 'description']
    search_fields = ['code', 'name']
    ordering = ['code']
    
    def get_readonly_fields(self, request, obj=None):
        """设置为只读"""
        if obj:  # 编辑时
            return ['code', 'name', 'description']
        return []
    
    class Meta:
        verbose_name = "单位（已弃用）"


@admin.register(Ship)
class ShipAdmin(LocalFeesAdminMixin, admin.ModelAdmin):
    """船舶管理（已弃用）"""
    list_display = ['code', 'name', 'company', 'description']
    search_fields = ['code', 'name', 'company']
    ordering = ['name']
    
    def get_readonly_fields(self, request, obj=None):
        """设置为只读"""
        if obj:  # 编辑时
            return ['code', 'name', 'company', 'description']
        return []
    
    class Meta:
        verbose_name = "船舶（已弃用）"


@admin.register(ShipFee)
class ShipFeeAdmin(LocalFeesAdminMixin, admin.ModelAdmin):
    """船舶费用管理（已弃用）"""
    list_display = ['ship', 'fee_type', 'amount', 'currency', 'port_code', 'is_active']
    list_filter = ['currency', 'is_active', 'fee_type']
    search_fields = ['ship__name', 'port_code']
    ordering = ['ship__name']
    
    def get_readonly_fields(self, request, obj=None):
        """设置为只读"""
        if obj:  # 编辑时
            return [field.name for field in self.model._meta.fields]
        return []
    
    class Meta:
        verbose_name = "船舶费用（已弃用）"


# Admin站点配置
admin.site.site_header = "船舶调度系统管理后台"
admin.site.site_title = "船舶调度系统"
admin.site.index_title = "欢迎使用船舶调度系统管理后台"
