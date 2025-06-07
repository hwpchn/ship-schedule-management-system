"""
测试专用设置
继承主设置并覆盖测试相关配置
"""
from .settings import *
import sys

# 测试标识
TESTING = True

# 调试模式
DEBUG = False

# 使用SQLite内存数据库进行测试
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'OPTIONS': {
            'timeout': 20,
        }
    }
}

# 禁用缓存
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# 简化密码验证器
AUTH_PASSWORD_VALIDATORS = []

# 禁用日志输出
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}

# 简化中间件
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# 禁用迁移（加速测试）
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

if 'test' in sys.argv:
    MIGRATION_MODULES = DisableMigrations()

# 邮件后端
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# 静态文件
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# 媒体文件
MEDIA_URL = '/media/'
MEDIA_ROOT = '/tmp/test_media'

# 时区设置
USE_TZ = True

# 测试专用JWT配置
SIMPLE_JWT.update({
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=10),
})

# 测试专用CORS配置
CORS_ALLOW_ALL_ORIGINS = True
