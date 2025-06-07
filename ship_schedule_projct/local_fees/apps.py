"""
本地费用应用配置
"""
from django.apps import AppConfig


class LocalFeesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'local_fees'
    verbose_name = '本地费用管理'
