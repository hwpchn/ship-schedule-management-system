# 部署文档总览

## 📋 概述

本文档提供船舶航线管理系统的完整部署指南，包括环境准备、安装配置、生产部署等内容。

## 🎯 部署架构

### 系统架构图
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端应用      │    │   负载均衡器    │    │   Web服务器     │
│   (React/Vue)   │◄──►│   (Nginx)       │◄──►│   (Django)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                       ┌─────────────────┐             │
                       │   缓存服务      │◄────────────┤
                       │   (Redis)       │             │
                       └─────────────────┘             │
                                                        │
                       ┌─────────────────┐             │
                       │   数据库        │◄────────────┘
                       │   (MySQL)       │
                       └─────────────────┘
```

### 环境要求

#### 最低配置
- **CPU**: 2核心
- **内存**: 4GB RAM
- **存储**: 50GB SSD
- **网络**: 10Mbps带宽

#### 推荐配置
- **CPU**: 4核心
- **内存**: 8GB RAM
- **存储**: 100GB SSD
- **网络**: 100Mbps带宽

#### 生产环境配置
- **CPU**: 8核心
- **内存**: 16GB RAM
- **存储**: 200GB SSD
- **网络**: 1Gbps带宽

## 🛠️ 技术栈

### 后端技术
- **Python**: 3.8+
- **Django**: 4.2.7
- **Django REST Framework**: 3.14.0
- **MySQL**: 8.0+
- **Redis**: 6.0+

### 前端技术
- **Node.js**: 16.0+
- **React/Vue**: 最新稳定版
- **Nginx**: 1.20+

### 部署工具
- **Docker**: 20.0+
- **Docker Compose**: 2.0+
- **Git**: 2.30+

## 📚 部署方式

### 1. 开发环境部署
适用于本地开发和测试：
- 直接运行Django开发服务器
- 使用SQLite数据库
- 无需负载均衡和缓存

**详细指南**: [安装指南](installation.md)

### 2. 测试环境部署
适用于功能测试和集成测试：
- 使用Docker容器化部署
- MySQL数据库
- Redis缓存
- 简化的Nginx配置

### 3. 生产环境部署
适用于正式生产环境：
- 完整的容器化部署
- 高可用数据库配置
- 负载均衡和反向代理
- 监控和日志系统
- SSL证书配置

## 🔧 部署流程

### 标准部署流程
```
1. 环境准备 → 2. 代码部署 → 3. 依赖安装 → 4. 数据库配置 → 5. 服务启动
```

### 详细步骤
1. **环境准备**
   - 服务器配置
   - 软件安装
   - 网络配置

2. **代码部署**
   - 代码下载
   - 版本控制
   - 文件权限设置

3. **依赖安装**
   - Python依赖
   - 系统依赖
   - 前端依赖

4. **数据库配置**
   - 数据库创建
   - 用户权限设置
   - 数据迁移

5. **服务启动**
   - 后端服务启动
   - 前端服务启动
   - 反向代理配置

## 🐳 Docker部署

### Docker Compose配置
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=mysql://user:pass@db:3306/ship_schedule
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
      - ./media:/app/media

  db:
    image: mysql:8.0
    environment:
      - MYSQL_DATABASE=ship_schedule
      - MYSQL_USER=ship_user
      - MYSQL_PASSWORD=ship_password
      - MYSQL_ROOT_PASSWORD=root_password
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"

  redis:
    image: redis:6.0-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web

volumes:
  mysql_data:
  redis_data:
```

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 收集静态文件
RUN python manage.py collectstatic --noinput

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "ship_schedule.wsgi:application"]
```

## 🔒 安全配置

### SSL证书配置
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    
    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 防火墙配置
```bash
# 开放必要端口
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS

# 关闭不必要端口
ufw deny 3306/tcp   # MySQL (仅内部访问)
ufw deny 6379/tcp   # Redis (仅内部访问)

# 启用防火墙
ufw enable
```

## 📊 监控和日志

### 日志配置
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/django.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

### 监控指标
- **系统指标**: CPU、内存、磁盘使用率
- **应用指标**: 响应时间、错误率、吞吐量
- **数据库指标**: 连接数、查询性能、锁等待
- **缓存指标**: 命中率、内存使用、连接数

## 🚀 性能优化

### 数据库优化
```sql
-- 创建索引
CREATE INDEX idx_vessel_schedule_pol_pod ON vessel_schedule(polCd, podCd);
CREATE INDEX idx_vessel_schedule_version ON vessel_schedule(data_version);
CREATE INDEX idx_vessel_info_carrier ON vessel_info_from_company(carriercd);

-- 配置优化
SET innodb_buffer_pool_size = 2G;
SET query_cache_size = 256M;
SET max_connections = 200;
```

### 缓存配置
```python
# Redis缓存配置
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            }
        },
        'KEY_PREFIX': 'ship_schedule',
        'TIMEOUT': 300,  # 5分钟默认过期
    }
}
```

## 📋 部署检查清单

### 部署前检查
- [ ] 服务器资源充足
- [ ] 网络连接正常
- [ ] 域名解析配置
- [ ] SSL证书准备
- [ ] 数据库备份

### 部署后检查
- [ ] 服务正常启动
- [ ] API接口可访问
- [ ] 数据库连接正常
- [ ] 缓存服务正常
- [ ] 日志记录正常
- [ ] 监控指标正常

### 功能测试
- [ ] 用户登录功能
- [ ] 船期查询功能
- [ ] 数据管理功能
- [ ] 权限控制功能
- [ ] 性能测试通过

## 🔗 相关链接

- **[安装指南](installation.md)** - 详细安装步骤
- **[配置说明](configuration.md)** - 系统配置参数
- **[API文档](../api/README.md)** - API接口文档
- **[开发指南](../development/README.md)** - 开发环境搭建

## 📞 技术支持

如果在部署过程中遇到问题，请：

1. 查看相关文档和FAQ
2. 检查日志文件获取错误信息
3. 联系技术支持团队
4. 提交Issue到项目仓库

**技术支持邮箱**: support@example.com  
**项目仓库**: https://github.com/your-org/ship-schedule
