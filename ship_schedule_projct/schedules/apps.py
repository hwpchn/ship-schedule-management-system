from django.apps import AppConfig


class SchedulesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'schedules'
    
    def ready(self):
        """应用启动时导入信号处理器"""
        import schedules.signals
