from django.urls import path
from . import views

app_name = 'schedules'

urlpatterns = [
    # 船舶航线CRUD接口
    path('schedules/', views.VesselScheduleListCreateView.as_view(), name='vessel-schedule-list-create'),
    path('schedules/<int:pk>/', views.VesselScheduleDetailView.as_view(), name='vessel-schedule-detail'),
    
    # 船舶航线搜索和统计接口
    path('schedules/search/', views.vessel_schedule_search, name='vessel-schedule-search'),
    path('schedules/stats/', views.vessel_schedule_stats, name='vessel-schedule-stats'),
    
    # 共舱分组API
    path('schedules/cabin-grouping/', views.cabin_grouping_api, name='cabin-grouping'),
    path('schedules/cabin-grouping-with-info/', views.cabin_grouping_with_vessel_info_api, name='cabin-grouping-with-info'),
    
    # 共舱配置管理API
    path('cabin-config/detail/', views.cabin_config_detail_api, name='cabin-config-detail'),
    path('cabin-config/update/', views.cabin_config_update_api, name='cabin-config-update'),
    path('cabin-config/delete/', views.cabin_config_delete_api, name='cabin-config-delete'),
    path('cabin-config/bulk-update/', views.cabin_config_bulk_update_api, name='cabin-config-bulk-update'),
    
    # 船舶额外信息CRUD接口
    path('vessel-info/', views.VesselInfoFromCompanyListCreateView.as_view(), name='vessel-info-list-create'),
    path('vessel-info/<int:pk>/', views.VesselInfoFromCompanyDetailView.as_view(), name='vessel-info-detail'),
    
    # VesselInfo查询API
    path('vessel-info/query/', views.vessel_info_query_api, name='vessel-info-query'),
    path('vessel-info/bulk-query/', views.vessel_info_bulk_query_api, name='vessel-info-bulk-query'),
    
    # VesselInfo批量操作API
    path('vessel-info/bulk-create/', views.vessel_info_bulk_create_api, name='vessel-info-bulk-create'),
    path('vessel-info/bulk-update/', views.vessel_info_bulk_update_api, name='vessel-info-bulk-update'),
    path('vessel-info/bulk-delete/', views.vessel_info_bulk_delete_api, name='vessel-info-bulk-delete'),
] 