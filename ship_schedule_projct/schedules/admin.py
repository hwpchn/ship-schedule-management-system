from django.contrib import admin
from .models import VesselSchedule, VesselInfoFromCompany


@admin.register(VesselSchedule)
class VesselScheduleAdmin(admin.ModelAdmin):
    """船舶航线管理界面"""
    
    # 列表显示字段
    list_display = [
        'id', 'vessel', 'voyage', 'polCd', 'podCd', 
        'eta', 'etd', 'status', 'data_version', 'fetch_date'
    ]
    
    # 列表过滤器
    list_filter = [
        'status', 'data_version', 'fetch_date', 'polCd', 
        'podCd', 'carriercd', 'isTransit'
    ]
    
    # 搜索字段
    search_fields = [
        'vessel', 'voyage', 'polCd', 'podCd', 'pol', 'pod',
        'carriercd', 'imo', 'routeCd'
    ]
    
    # 分页
    list_per_page = 20
    
    # 字段分组
    fieldsets = (
        ('基本信息', {
            'fields': ('status', 'data_version', 'fetch_timestamp', 'fetch_date')
        }),
        ('核心航线信息', {
            'fields': ('vessel', 'voyage', 'polCd', 'podCd', 'pol', 'pod')
        }),
        ('航线详情', {
            'fields': ('routeCd', 'routeEtd', 'carriercd', 'isReferenceCarrier', 
                      'imo', 'shipAgency')
        }),
        ('港口信息', {
            'fields': ('polTerminal', 'polTerminalCd', 'podTerminal', 'podTerminalCd')
        }),
        ('时间信息', {
            'fields': ('eta', 'etd', 'totalDuration', 'bookingCutoff', 
                      'cyOpen', 'cyClose', 'customCutoff', 'cutOff', 
                      'siCutoff', 'vgmCutoff')
        }),
        ('中转信息', {
            'fields': ('isTransit', 'transitPortEn', 'transitPortCd', 
                      'vesselAfterTransit', 'voyageAfterTransit',
                      'secondTransitPortEn', 'secondTransitPortCd',
                      'secondVesselAfterTransit', 'secondVoyageAfterTransit'),
            'classes': ('collapse',)
        }),
        ('其他信息', {
            'fields': ('shareCabins', 'remark', 'ext_field1', 'ext_field2', 'ext_field3'),
            'classes': ('collapse',)
        }),
    )
    
    # 只读字段
    readonly_fields = ['id', 'fetch_timestamp', 'fetch_date']
    
    # 排序
    ordering = ['-fetch_date', '-data_version', 'vessel', 'voyage']
    
    # 批量操作
    actions = ['make_active', 'make_inactive']
    
    def make_active(self, request, queryset):
        """批量激活"""
        updated = queryset.update(status=1)
        self.message_user(request, f'{updated} 条记录已激活')
    make_active.short_description = "激活选中的航线"
    
    def make_inactive(self, request, queryset):
        """批量停用"""
        updated = queryset.update(status=0)
        self.message_user(request, f'{updated} 条记录已停用')
    make_inactive.short_description = "停用选中的航线"


@admin.register(VesselInfoFromCompany)
class VesselInfoFromCompanyAdmin(admin.ModelAdmin):
    """船舶额外信息管理界面"""
    
    # 列表显示字段
    list_display = [
        'id', 'vessel', 'voyage', 'carrierCd', 'polCd', 'podCd', 
        'price', 'gp_20', 'hq_40', 'cut_off_time'
    ]
    
    # 列表过滤器
    list_filter = [
        'carrierCd', 'polCd', 'podCd'
    ]
    
    # 搜索字段
    search_fields = [
        'vessel', 'voyage', 'carrierCd', 'polCd', 'podCd'
    ]
    
    # 分页
    list_per_page = 20
    
    # 字段分组
    fieldsets = (
        ('关联信息', {
            'fields': ('carrierCd', 'vessel', 'voyage', 'polCd', 'podCd')
        }),
        ('价格和舱位信息', {
            'fields': ('price', 'gp_20', 'hq_40', 'cut_off_time')
        }),
    )
    
    # 排序
    ordering = ['carrierCd', 'vessel', 'voyage']
    
    # 批量操作
    actions = ['clear_price', 'set_available_cabin']
    
    def clear_price(self, request, queryset):
        """批量清空价格"""
        updated = queryset.update(price=None)
        self.message_user(request, f'{updated} 条记录的价格已清空')
    clear_price.short_description = "清空选中记录的价格"
    
    def set_available_cabin(self, request, queryset):
        """批量设置现舱"""
        updated = queryset.update(gp_20='有现舱', hq_40='有现舱')
        self.message_user(request, f'{updated} 条记录已设置为有现舱')
    set_available_cabin.short_description = "设置选中记录为有现舱"
