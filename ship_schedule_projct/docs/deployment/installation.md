# 安装指南

## 📋 概述

本指南提供船舶航线管理系统的详细安装步骤，包括开发环境和生产环境的安装配置。

## 🔧 系统要求

### 操作系统
- **Linux**: Ubuntu 20.04+ / CentOS 8+ / Debian 10+
- **macOS**: 10.15+
- **Windows**: Windows 10+ (推荐使用WSL2)

### 软件依赖
- **Python**: 3.8+
- **Node.js**: 16.0+ (如需前端开发)
- **Git**: 2.30+
- **MySQL**: 8.0+ (生产环境)
- **Redis**: 6.0+ (生产环境)

## 🚀 快速开始

### 1. 克隆项目
```bash
# 克隆项目代码
git clone <repository-url>
cd ship_schedule_projct

# 查看项目结构
ls -la
```

### 2. 创建虚拟环境
```bash
# 创建Python虚拟环境
python3 -m venv .venv

# 激活虚拟环境
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

# 验证虚拟环境
which python
python --version
```

### 3. 安装依赖
```bash
# 升级pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt

# 验证安装
pip list
```

### 4. 数据库配置

#### 开发环境（SQLite）
```bash
# 执行数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 输入用户信息
Email address: admin@example.com
Password: ********
Password (again): ********
```

#### 生产环境（MySQL）
```bash
# 安装MySQL客户端
# Ubuntu/Debian
sudo apt-get install default-libmysqlclient-dev

# CentOS/RHEL
sudo yum install mysql-devel

# macOS
brew install mysql-client

# 创建数据库
mysql -u root -p
CREATE DATABASE ship_schedule CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ship_user'@'localhost' IDENTIFIED BY 'ship_password';
GRANT ALL PRIVILEGES ON ship_schedule.* TO 'ship_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# 配置数据库连接
cp ship_schedule/settings.py ship_schedule/settings_local.py
# 编辑settings_local.py中的数据库配置

# 执行迁移
python manage.py migrate
```

### 5. 启动服务
```bash
# 启动开发服务器
python manage.py runserver

# 访问应用
# API: http://127.0.0.1:8000/api/
# 管理后台: http://127.0.0.1:8000/admin/
```

## 📦 详细安装步骤

### 步骤1: 环境准备

#### Ubuntu/Debian系统
```bash
# 更新系统包
sudo apt update && sudo apt upgrade -y

# 安装基础依赖
sudo apt install -y python3 python3-pip python3-venv git curl wget

# 安装编译工具
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev

# 安装MySQL客户端库
sudo apt install -y default-libmysqlclient-dev pkg-config
```

#### CentOS/RHEL系统
```bash
# 更新系统包
sudo yum update -y

# 安装基础依赖
sudo yum install -y python3 python3-pip git curl wget

# 安装开发工具
sudo yum groupinstall -y "Development Tools"
sudo yum install -y openssl-devel libffi-devel python3-devel

# 安装MySQL客户端库
sudo yum install -y mysql-devel
```

#### macOS系统
```bash
# 安装Homebrew（如果未安装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装依赖
brew install python3 git mysql-client pkg-config
```

### 步骤2: 项目配置

#### 创建项目目录
```bash
# 创建项目根目录
sudo mkdir -p /opt/ship_schedule
sudo chown $USER:$USER /opt/ship_schedule
cd /opt/ship_schedule

# 克隆项目
git clone <repository-url> .
```

#### 配置环境变量
```bash
# 创建环境变量文件
cat > .env << EOF
# Django配置
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# 数据库配置
DATABASE_URL=mysql://ship_user:ship_password@localhost:3306/ship_schedule

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 邮件配置
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=noreply@example.com
EMAIL_HOST_PASSWORD=email-password
EMAIL_USE_TLS=True

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/opt/ship_schedule/logs/django.log
EOF

# 设置文件权限
chmod 600 .env
```

### 步骤3: 数据库安装配置

#### MySQL安装
```bash
# Ubuntu/Debian
sudo apt install -y mysql-server mysql-client

# CentOS/RHEL
sudo yum install -y mysql-server mysql

# macOS
brew install mysql

# 启动MySQL服务
sudo systemctl start mysql
sudo systemctl enable mysql

# 安全配置
sudo mysql_secure_installation
```

#### Redis安装
```bash
# Ubuntu/Debian
sudo apt install -y redis-server

# CentOS/RHEL
sudo yum install -y redis

# macOS
brew install redis

# 启动Redis服务
sudo systemctl start redis
sudo systemctl enable redis

# 测试Redis连接
redis-cli ping
```

### 步骤4: 应用部署

#### 安装Python依赖
```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 验证安装
python manage.py check
```

#### 数据库初始化
```bash
# 创建数据库表
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 加载初始数据（如果有）
python manage.py loaddata fixtures/initial_data.json

# 收集静态文件
python manage.py collectstatic --noinput
```

#### 创建系统服务
```bash
# 创建systemd服务文件
sudo tee /etc/systemd/system/ship-schedule.service > /dev/null << EOF
[Unit]
Description=Ship Schedule Django Application
After=network.target mysql.service redis.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/opt/ship_schedule
Environment=PATH=/opt/ship_schedule/venv/bin
ExecStart=/opt/ship_schedule/venv/bin/gunicorn --bind 127.0.0.1:8000 ship_schedule.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# 重新加载systemd配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start ship-schedule
sudo systemctl enable ship-schedule

# 检查服务状态
sudo systemctl status ship-schedule
```

### 步骤5: Web服务器配置

#### Nginx安装配置
```bash
# 安装Nginx
sudo apt install -y nginx  # Ubuntu/Debian
sudo yum install -y nginx  # CentOS/RHEL

# 创建Nginx配置
sudo tee /etc/nginx/sites-available/ship-schedule > /dev/null << EOF
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 100M;

    location /static/ {
        alias /opt/ship_schedule/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /opt/ship_schedule/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

# 启用站点
sudo ln -s /etc/nginx/sites-available/ship-schedule /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

## 🔒 SSL证书配置

### 使用Let's Encrypt
```bash
# 安装Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加以下行
0 12 * * * /usr/bin/certbot renew --quiet
```

### 手动SSL证书
```bash
# 创建SSL目录
sudo mkdir -p /etc/nginx/ssl

# 复制证书文件
sudo cp your-cert.pem /etc/nginx/ssl/
sudo cp your-key.pem /etc/nginx/ssl/

# 设置权限
sudo chmod 600 /etc/nginx/ssl/*
sudo chown root:root /etc/nginx/ssl/*

# 更新Nginx配置
# 在server块中添加SSL配置
listen 443 ssl http2;
ssl_certificate /etc/nginx/ssl/your-cert.pem;
ssl_certificate_key /etc/nginx/ssl/your-key.pem;
```

## 🧪 安装验证

### 功能测试
```bash
# 测试API健康检查
curl http://localhost/api/

# 测试用户登录
curl -X POST http://localhost/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "your-password"}'

# 测试船期查询
curl -X GET "http://localhost/api/schedules/cabin-grouping-with-info/?polCd=CNSHA&podCd=USNYC" \
  -H "Authorization: Bearer <token>"
```

### 性能测试
```bash
# 安装Apache Bench
sudo apt install -y apache2-utils

# 并发测试
ab -n 1000 -c 10 http://localhost/api/

# 查看系统资源使用
htop
iostat -x 1
```

## 🔧 故障排除

### 常见问题

#### 1. 数据库连接失败
```bash
# 检查MySQL服务状态
sudo systemctl status mysql

# 检查数据库连接
mysql -u ship_user -p ship_schedule

# 查看Django日志
tail -f /opt/ship_schedule/logs/django.log
```

#### 2. 静态文件404错误
```bash
# 重新收集静态文件
python manage.py collectstatic --clear --noinput

# 检查Nginx配置
sudo nginx -t

# 检查文件权限
ls -la /opt/ship_schedule/staticfiles/
```

#### 3. 权限错误
```bash
# 设置正确的文件权限
sudo chown -R www-data:www-data /opt/ship_schedule
sudo chmod -R 755 /opt/ship_schedule
sudo chmod -R 644 /opt/ship_schedule/logs
```

### 日志查看
```bash
# Django应用日志
tail -f /opt/ship_schedule/logs/django.log

# Nginx访问日志
tail -f /var/log/nginx/access.log

# Nginx错误日志
tail -f /var/log/nginx/error.log

# 系统服务日志
sudo journalctl -u ship-schedule -f
```

## 📋 安装检查清单

### 安装前检查
- [ ] 系统要求满足
- [ ] 网络连接正常
- [ ] 必要端口开放
- [ ] 域名解析配置

### 安装后检查
- [ ] Python虚拟环境激活
- [ ] 依赖包安装完成
- [ ] 数据库连接正常
- [ ] 数据迁移完成
- [ ] 超级用户创建
- [ ] 静态文件收集
- [ ] 服务正常启动
- [ ] Nginx配置正确
- [ ] SSL证书配置（如需要）

### 功能验证
- [ ] API健康检查通过
- [ ] 用户登录功能正常
- [ ] 船期查询功能正常
- [ ] 管理后台可访问
- [ ] 权限控制正常

## 🔗 相关链接

- **[配置说明](configuration.md)** - 详细配置参数
- **[部署总览](README.md)** - 部署架构概述
- **[API文档](../api/README.md)** - API接口文档
- **[开发指南](../development/getting_started.md)** - 开发环境搭建
