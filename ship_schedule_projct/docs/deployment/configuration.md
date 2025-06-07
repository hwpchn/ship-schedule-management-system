# 配置说明

## 📋 概述

本文档详细说明船舶航线管理系统的各项配置参数，包括Django设置、数据库配置、缓存配置、安全配置等。

## 🔧 Django配置

### 基础配置
```python
# settings.py

# 调试模式（生产环境必须设为False）
DEBUG = False

# 安全密钥（生产环境必须使用强密钥）
SECRET_KEY = 'your-secret-key-here'

# 允许的主机
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'your-domain.com',
    'www.your-domain.com'
]

# 应用配置
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # 第三方应用
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    'corsheaders',
    
    # 项目应用
    'authentication',
    'schedules',
    'local_fees',
]

# 中间件配置
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

### 国际化配置
```python
# 语言和时区
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# 日期时间格式
DATETIME_FORMAT = 'Y-m-d H:i:s'
DATE_FORMAT = 'Y-m-d'
TIME_FORMAT = 'H:i:s'
```

## 🗄️ 数据库配置

### MySQL配置
```python
# 生产环境数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ship_schedule',
        'USER': 'ship_user',
        'PASSWORD': 'ship_password',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'isolation_level': 'read committed',
        },
        'CONN_MAX_AGE': 600,  # 连接池配置
    }
}

# 数据库路由配置（如需读写分离）
DATABASE_ROUTERS = ['path.to.db_router.DatabaseRouter']
```

### SQLite配置（开发环境）
```python
# 开发环境数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### 数据库连接池配置
```python
# 使用django-db-pool
DATABASES = {
    'default': {
        'ENGINE': 'dj_db_conn_pool.backends.mysql',
        'NAME': 'ship_schedule',
        'USER': 'ship_user',
        'PASSWORD': 'ship_password',
        'HOST': 'localhost',
        'PORT': '3306',
        'POOL_OPTIONS': {
            'POOL_SIZE': 10,
            'MAX_OVERFLOW': 10,
            'RECYCLE': 24 * 60 * 60,  # 24小时
        }
    }
}
```

## 🚀 缓存配置

### Redis缓存配置
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        },
        'KEY_PREFIX': 'ship_schedule',
        'TIMEOUT': 300,  # 5分钟默认过期
        'VERSION': 1,
    },
    
    # 会话缓存
    'session': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'session',
        'TIMEOUT': 86400,  # 24小时
    }
}

# 会话配置
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'session'
SESSION_COOKIE_AGE = 86400  # 24小时
```

### 内存缓存配置（开发环境）
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
            'CULL_FREQUENCY': 3,
        }
    }
}
```

## 🔐 安全配置

### HTTPS和安全头配置
```python
# HTTPS配置（生产环境）
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# 安全头配置
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000  # 1年
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookie安全配置
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
```

### CORS配置
```python
# 跨域配置
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-domain.com",
    "https://www.your-frontend-domain.com",
]

# 开发环境可以使用
CORS_ALLOW_ALL_ORIGINS = True  # 仅开发环境

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
```

## 🔑 JWT配置

### JWT Token配置
```python
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}
```

## 📧 邮件配置

### SMTP邮件配置
```python
# 邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.example.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'noreply@example.com'
EMAIL_HOST_PASSWORD = 'email-password'
DEFAULT_FROM_EMAIL = 'Ship Schedule System <noreply@example.com>'

# 管理员邮箱
ADMINS = [
    ('Admin', 'admin@example.com'),
]

# 服务器错误邮件
SERVER_EMAIL = 'server@example.com'
```

### 开发环境邮件配置
```python
# 开发环境使用控制台输出
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# 或使用文件输出
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/app-messages'
```

## 📝 日志配置

### 详细日志配置
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/ship_schedule/django.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/ship_schedule/error.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['error_file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'authentication': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'schedules': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'local_fees': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## 📁 静态文件配置

### 静态文件和媒体文件配置
```python
# 静态文件配置
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/ship_schedule/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# 媒体文件配置
MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/ship_schedule/media/'

# 文件上传配置
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000
```

## 🔧 REST Framework配置

### DRF配置
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    },
    'EXCEPTION_HANDLER': 'authentication.exceptions.custom_exception_handler',
}
```

## 🌍 环境变量配置

### .env文件示例
```bash
# Django配置
DEBUG=False
SECRET_KEY=your-very-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# 数据库配置
DATABASE_URL=mysql://ship_user:ship_password@localhost:3306/ship_schedule

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 邮件配置
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=noreply@example.com
EMAIL_HOST_PASSWORD=your-email-password
EMAIL_USE_TLS=True

# 安全配置
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/var/log/ship_schedule/django.log

# 第三方服务配置
SENTRY_DSN=https://your-sentry-dsn
```

### 环境变量加载
```python
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 使用环境变量
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
SECRET_KEY = os.getenv('SECRET_KEY')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# 数据库URL解析
import dj_database_url
DATABASES = {
    'default': dj_database_url.parse(os.getenv('DATABASE_URL'))
}
```

## 📊 性能配置

### 数据库优化配置
```python
# 数据库连接配置
DATABASES['default']['OPTIONS'].update({
    'init_command': """
        SET sql_mode='STRICT_TRANS_TABLES';
        SET innodb_strict_mode=1;
        SET transaction_isolation='READ-COMMITTED';
    """,
    'charset': 'utf8mb4',
    'use_unicode': True,
})

# 查询优化
DATABASES['default']['CONN_MAX_AGE'] = 600
```

### 缓存优化配置
```python
# 缓存键前缀
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 600
CACHE_MIDDLEWARE_KEY_PREFIX = 'ship_schedule'

# 模板缓存
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]
```

## ⚠️ 配置注意事项

1. **安全性**: 生产环境必须设置强密钥和安全配置
2. **性能**: 根据实际负载调整数据库连接池和缓存配置
3. **监控**: 配置适当的日志级别和错误通知
4. **备份**: 定期备份配置文件和数据库
5. **环境隔离**: 不同环境使用不同的配置文件
6. **敏感信息**: 使用环境变量存储敏感配置信息

## 🔗 相关链接

- **[安装指南](installation.md)** - 详细安装步骤
- **[部署总览](README.md)** - 部署架构概述
- **[开发指南](../development/README.md)** - 开发环境配置
